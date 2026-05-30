"""Command-line interface for the music stem separator."""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional

import click
from dotenv import load_dotenv

from . import __version__
from .input_processor import InputProcessor
from .separator import StemSeparator
from .stem_processor import StemProcessor
from .output_manager import OutputManager


def setup_logging(verbose: bool = False) -> None:
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    format_str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        if verbose
        else "%(message)s"
    )

    logging.basicConfig(
        level=level, format=format_str, handlers=[logging.StreamHandler(sys.stdout)]
    )


@click.command()
@click.argument("input_path", type=str)
@click.option(
    "--output",
    "-o",
    default="./output",
    help="Output directory for separated stems (default: ./output)",
)
@click.option(
    "--model", "-m", default="htdemucs", help="Demucs model to use (default: htdemucs)"
)
@click.option(
    "--device", "-d", default=None, help="Device to use (cpu, cuda, or auto-detect)"
)
@click.option("--no-enhance", is_flag=True, help="Disable audio enhancement processing")
@click.option(
    "--timeout",
    type=int,
    default=StemSeparator.DEFAULT_TIMEOUT_SECONDS,
    show_default=True,
    help="Max seconds to allow the separation step to run",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.version_option(version=__version__, prog_name="Music Stem Separator")
def main(
    input_path: str,
    output: str,
    model: str,
    device: Optional[str],
    no_enhance: bool,
    timeout: int,
    verbose: bool,
) -> None:
    """
    Music Stem Separator - AI-powered audio stem separation tool.

    Separates audio files or Spotify tracks into drums, bass, vocals, and other instruments.

    INPUT_PATH can be:
    - Path to a local audio file (MP3, WAV, FLAC, etc.)
    - Spotify track URL (https://open.spotify.com/track/...)
    - Spotify URI (spotify:track:...)
    - Direct URL to audio file (MP3, WAV, FLAC, etc.)

    Examples:
    \b
        stem-separator song.mp3
        stem-separator song.mp3 --model htdemucs_ft --output ./my_stems
        stem-separator "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
        stem-separator "https://example.com/audio.mp3"
    """
    # Load Spotify (and any other) credentials from a local .env file if present.
    load_dotenv()

    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    click.echo("🎵 Music Stem Separator v{} 🎵".format(__version__))
    click.echo("=" * 50)

    try:
        result = process_track(
            input_path=input_path,
            output_dir=output,
            model_name=model,
            device=device,
            enable_enhancement=not no_enhance,
            timeout=timeout,
            verbose=verbose,
        )

        if result["success"]:
            click.echo("\n✅ Stem separation completed successfully!")

            if "summary_report" in result:
                click.echo("\n" + result["summary_report"])

            if "output_summary" in result:
                summary = result["output_summary"]
                click.echo(f"\n📁 Output Location: {summary['track_directory']}")
                click.echo(f"📊 Total Files: {summary['total_files']}")
                click.echo(f"💾 Total Size: {summary.get('total_size_mb', 0):.1f} MB")

        else:
            click.echo(f"\n❌ Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        click.echo("\n\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"\n💥 Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def process_track(
    input_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: Optional[str] = None,
    enable_enhancement: bool = True,
    timeout: int = StemSeparator.DEFAULT_TIMEOUT_SECONDS,
    verbose: bool = False,
) -> dict:
    """
    Process a single track through the complete stem separation pipeline.

    Args:
        input_path: Input file path or Spotify URL
        output_dir: Output directory
        model_name: Demucs model name
        device: Device to use for processing
        enable_enhancement: Whether to apply audio enhancement
        timeout: Max seconds to allow the separation step to run
        verbose: Enable verbose logging

    Returns:
        Processing result dictionary
    """
    logger = logging.getLogger(__name__)

    # Intermediate working directories, removed in the finally block below.
    temp_dirs = [
        f"{output_dir}/temp",
        f"{output_dir}/temp_stems",
        f"{output_dir}/temp_processed",
    ]

    try:
        # Step 1: Process input
        click.echo("🔍 Processing input...")
        input_processor = InputProcessor()
        input_result = input_processor.process_input(
            input_path, temp_dir=f"{output_dir}/temp"
        )

        if not input_result["success"]:
            return {
                "success": False,
                "error": f"Input processing failed: {input_result.get('error', 'Unknown error')}",
            }

        audio_file = input_result["audio_file"]
        input_type = input_result["input_type"]

        click.echo(f"✅ Input processed: {input_type}")
        if verbose:
            click.echo(f"   Audio file: {audio_file}")

        # Step 2: Separate stems
        click.echo(f"🤖 Separating stems using {model_name}...")
        separator = StemSeparator(model_name=model_name, device=device, timeout=timeout)
        separation_result = separator.separate_stems(
            audio_file, f"{output_dir}/temp_stems"
        )

        if not separation_result["success"]:
            return {
                "success": False,
                "error": f"Stem separation failed: {separation_result.get('error', 'Unknown error')}",
            }

        click.echo("✅ Stem separation completed")
        if verbose:
            stems = separation_result.get("stems", {})
            click.echo(f"   Separated {len(stems)} stems: {list(stems.keys())}")

        # Step 3: Process stems (enhancement)
        processing_results = None
        if enable_enhancement:
            click.echo("🎛️  Enhancing audio quality...")
            stem_processor = StemProcessor(enable_enhancement=True)
            processing_results = stem_processor.process_stem_files(
                separation_result["stems"], f"{output_dir}/temp_processed"
            )

            if processing_results["success"]:
                click.echo("✅ Audio enhancement completed")
                # Update stem paths to processed versions
                for stem_name, result in processing_results["processed_stems"].items():
                    separation_result["stems"][stem_name] = result["output_file"]
            else:
                click.echo("⚠️  Audio enhancement failed, using original stems")
        else:
            click.echo("⏭️  Skipping audio enhancement")

        # Step 4: Organize output
        click.echo("📁 Organizing output files...")
        track_name = Path(audio_file).stem
        output_manager = OutputManager(output_dir)

        organization_result = output_manager.organize_stem_files(
            separation_result["stems"], track_name
        )

        if not organization_result["success"]:
            return {
                "success": False,
                "error": f"Output organization failed: {organization_result.get('error', 'Unknown error')}",
            }

        # Point downstream reporting at the final organized files rather than the
        # soon-to-be-deleted temp copies.
        if organization_result.get("organized_files"):
            separation_result["stems"] = organization_result["organized_files"]

        # Step 5: Generate metadata and reports
        metadata = output_manager.generate_metadata(
            track_name, separation_result, processing_results
        )

        output_structure = organization_result["output_structure"]
        metadata_result = output_manager.save_metadata(
            metadata, output_structure["track_dir"]
        )

        summary_report = output_manager.create_summary_report(
            track_name, separation_result, processing_results, output_structure
        )

        output_summary = output_manager.get_output_summary(output_structure)

        return {
            "success": True,
            "track_name": track_name,
            "input_type": input_type,
            "stems_separated": list(separation_result["stems"].keys()),
            "enhancement_applied": bool(
                enable_enhancement
                and processing_results
                and processing_results["success"]
            ),
            "output_structure": output_structure,
            "metadata_saved": metadata_result["success"] if metadata_result else False,
            "summary_report": summary_report,
            "output_summary": output_summary,
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        # Always remove intermediate working directories (downloaded input,
        # raw stems, enhanced stems), regardless of success or failure.
        if verbose:
            click.echo("🧹 Cleaning up temporary files...")
        for temp_dir in temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
