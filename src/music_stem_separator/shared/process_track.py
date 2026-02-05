"""Shared processing logic for both CLI and GUI."""

import logging
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from ..input_processor import InputProcessor
from ..separator import StemSeparator
from ..stem_processor import StemProcessor
from ..output_manager import OutputManager


def process_track(
    input_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: Optional[str] = None,
    enable_enhancement: bool = True,
    verbose: bool = False,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> dict:
    """
    Process a single track through the complete stem separation pipeline.

    Args:
        input_path: Input file path or Spotify URL
        output_dir: Output directory
        model_name: Demucs model name
        device: Device to use for processing
        enable_enhancement: Whether to apply audio enhancement
        verbose: Enable verbose logging
        progress_callback: Optional callback for progress updates.
                          Called with dict containing: stage, percent, message

    Returns:
        Processing result dictionary

    Progress callback format:
        {
            "stage": str,  # e.g., "input_processing", "separating_stems"
            "percent": int,  # 0-100
            "message": str,  # Human-readable message
        }
    """
    logger = logging.getLogger(__name__)

    def _report_progress(stage: str, percent: int, message: str):
        """Helper to report progress if callback provided."""
        if progress_callback:
            progress_callback(
                {
                    "stage": stage,
                    "percent": percent,
                    "message": message,
                }
            )

    try:
        # Step 1: Process input (0-10%)
        _report_progress("input_processing", 0, "Processing input...")

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

        _report_progress("input_processing", 10, f"Input processed: {input_type}")

        # Step 2: Separate stems (10-80%)
        _report_progress("loading_model", 15, f"Loading AI model ({model_name})...")

        separator = StemSeparator(model_name=model_name, device=device)

        _report_progress("separating_stems", 20, "Separating stems...")

        separation_result = separator.separate_stems(
            audio_file, f"{output_dir}/temp_stems"
        )

        if not separation_result["success"]:
            return {
                "success": False,
                "error": f"Stem separation failed: {separation_result.get('error', 'Unknown error')}",
            }

        stems = separation_result.get("stems", {})
        _report_progress("separating_stems", 80, f"Separated {len(stems)} stems")

        # Step 3: Process stems (enhancement) (80-90%)
        processing_results = None
        if enable_enhancement:
            _report_progress("enhancing_audio", 82, "Enhancing audio quality...")

            stem_processor = StemProcessor(enable_enhancement=True)
            processing_results = stem_processor.process_stem_files(
                separation_result["stems"], f"{output_dir}/temp_processed"
            )

            if processing_results["success"]:
                # Update stem paths to processed versions
                for stem_name, result in processing_results["processed_stems"].items():
                    separation_result["stems"][stem_name] = result["output_file"]
                _report_progress("enhancing_audio", 90, "Audio enhancement completed")
            else:
                _report_progress(
                    "enhancing_audio",
                    90,
                    "Audio enhancement failed, using original stems",
                )
        else:
            _report_progress("enhancing_audio", 90, "Skipping audio enhancement")

        # Step 4: Organize output (90-100%)
        _report_progress("organizing_output", 92, "Organizing output files...")

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

        # Step 5: Generate metadata and reports
        _report_progress("organizing_output", 95, "Generating metadata...")

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

        # Step 6: Cleanup temporary files
        _report_progress("organizing_output", 98, "Cleaning up temporary files...")

        temp_files = []
        if input_result.get("temp_file"):
            temp_files.append(audio_file)

        if temp_files:
            output_manager.cleanup_temp_files(temp_files)

        _report_progress("organizing_output", 100, "Processing complete!")

        return {
            "success": True,
            "track_name": track_name,
            "input_type": input_type,
            "stems_separated": list(separation_result["stems"].keys()),
            "enhancement_applied": enable_enhancement
            and processing_results
            and processing_results["success"],
            "output_structure": output_structure,
            "metadata_saved": metadata_result["success"] if metadata_result else False,
            "summary_report": summary_report,
            "output_summary": output_summary,
        }

    except Exception as e:
        logger.error(f"Processing failed: {e}")
        _report_progress("error", 0, f"Error: {str(e)}")
        return {"success": False, "error": str(e)}
