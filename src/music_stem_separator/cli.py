"""Command-line interface for the music stem separator."""

import logging
import sys
from typing import Optional

import click

from . import __version__
from .shared.process_track import process_track

# Keep these imports for backward compatibility with existing tests
from .input_processor import InputProcessor  # noqa: F401
from .separator import StemSeparator  # noqa: F401
from .stem_processor import StemProcessor  # noqa: F401
from .output_manager import OutputManager  # noqa: F401


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
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.version_option(version=__version__, prog_name="Music Stem Separator")
def main(
    input_path: str,
    output: str,
    model: str,
    device: Optional[str],
    no_enhance: bool,
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
            verbose=verbose,
            progress_callback=_cli_progress_callback,
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


def _cli_progress_callback(progress_data: dict) -> None:
    """Progress callback for CLI that outputs to console."""
    message = progress_data.get("message", "")
    percent = progress_data.get("percent", 0)
    stage = progress_data.get("stage", "")

    # Only show key milestones to avoid cluttering CLI output
    if percent in [0, 10, 20, 80, 90, 100] or stage == "error":
        if stage == "error":
            click.echo(f"❌ {message}")
        elif percent == 0:
            click.echo(f"🔍 {message}")
        elif percent == 10:
            click.echo(f"✅ {message}")
        elif percent == 20:
            click.echo(f"🤖 {message}")
        elif percent == 80:
            click.echo(f"✅ {message}")
        elif percent == 90:
            click.echo(f"🎛️  {message}")
        elif percent == 100:
            click.echo(f"📁 {message}")


if __name__ == "__main__":
    main()
