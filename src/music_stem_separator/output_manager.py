"""Output file organization and management."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class OutputManager:
    """Manager for organizing and handling output files and directories."""

    def __init__(
        self,
        base_output_dir: Union[str, Path],
        create_subdirs: bool = True,
        organize_by_date: bool = False,
    ):
        """
        Initialize the output manager.

        Args:
            base_output_dir: Base directory for all outputs
            create_subdirs: Whether to create subdirectories for each track
            organize_by_date: Whether to organize outputs by date
        """
        self.base_output_dir = Path(base_output_dir)
        self.create_subdirs = create_subdirs
        self.organize_by_date = organize_by_date

        # Ensure base directory exists
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized OutputManager with base_dir: {self.base_output_dir}")

    def create_output_structure(self, track_name: str) -> Dict:
        """
        Create the output directory structure for a track.

        Args:
            track_name: Name of the track

        Returns:
            Dictionary with created directory paths
        """
        try:
            # Clean track name for filesystem
            safe_track_name = self._sanitize_filename(track_name)

            # Determine base directory
            if self.organize_by_date:
                date_str = datetime.now().strftime("%Y-%m-%d")
                base_dir = self.base_output_dir / date_str
            else:
                base_dir = self.base_output_dir

            # Create track-specific directory if enabled
            if self.create_subdirs:
                track_dir = base_dir / safe_track_name
                stems_dir = track_dir / "stems"
            else:
                track_dir = base_dir
                stems_dir = base_dir

            # Create directories
            track_dir.mkdir(parents=True, exist_ok=True)
            stems_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Created output structure for track: {track_name}")

            return {
                "success": True,
                "track_dir": track_dir,
                "stems_dir": stems_dir,
                "track_name": safe_track_name,
            }

        except Exception as e:
            logger.error(f"Failed to create output structure for {track_name}: {e}")
            return {"success": False, "error": str(e)}

    def organize_stem_files(
        self, stem_files: Dict[str, Union[str, Path]], track_name: str
    ) -> Dict:
        """
        Organize stem files into the output structure.

        Args:
            stem_files: Dictionary mapping stem names to file paths
            track_name: Name of the track

        Returns:
            Organization result with new file paths
        """
        try:
            # Create output structure
            structure = self.create_output_structure(track_name)
            if not structure["success"]:
                return structure

            stems_dir = structure["stems_dir"]
            organized_files = {}

            # Move/copy each stem file
            for stem_name, source_path in stem_files.items():
                source_path = Path(source_path)

                if not source_path.exists():
                    logger.warning(f"Source stem file not found: {source_path}")
                    continue

                # Generate target filename
                target_filename = f"{structure['track_name']}_{stem_name}.wav"
                target_path = stems_dir / target_filename

                # Copy/move file
                try:
                    # Use copy for safety (can change to move if needed)
                    import shutil

                    shutil.copy2(source_path, target_path)
                    organized_files[stem_name] = target_path
                    logger.debug(
                        f"Organized {stem_name}: {source_path} -> {target_path}"
                    )

                except Exception as e:
                    logger.error(f"Failed to organize {stem_name} file: {e}")
                    continue

            return {
                "success": True,
                "organized_files": organized_files,
                "output_structure": structure,
            }

        except Exception as e:
            logger.error(f"Failed to organize stem files for {track_name}: {e}")
            return {"success": False, "error": str(e)}

    def generate_metadata(
        self,
        track_name: str,
        separation_result: Dict,
        processing_results: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate metadata for the separation session.

        Args:
            track_name: Name of the track
            separation_result: Results from stem separation
            processing_results: Results from audio processing

        Returns:
            Metadata dictionary
        """
        metadata = {
            "track_name": track_name,
            "timestamp": datetime.now().isoformat(),
            "source_file": separation_result.get("audio_file"),
            "model_used": separation_result.get("model_used"),
            "device_used": separation_result.get("device_used"),
            "separation_success": separation_result.get("success", False),
            "stems": {},
        }

        # Add stem information
        if "stems" in separation_result:
            for stem_name, stem_path in separation_result["stems"].items():
                stem_info = {"file_path": str(stem_path)}

                # Add processing metrics if available
                if (
                    processing_results
                    and "processed_stems" in processing_results
                    and stem_name in processing_results["processed_stems"]
                ):

                    stem_processing = processing_results["processed_stems"][stem_name]
                    if "metrics" in stem_processing:
                        stem_info["metrics"] = stem_processing["metrics"]

                metadata["stems"][stem_name] = stem_info

        # Add processing information
        if processing_results:
            metadata["processing_applied"] = processing_results.get("success", False)
            metadata["processing_settings"] = processing_results.get("settings", {})

        return metadata

    def save_metadata(self, metadata: Dict, output_dir: Union[str, Path]) -> Dict:
        """
        Save metadata to JSON file.

        Args:
            metadata: Metadata dictionary
            output_dir: Directory to save metadata file

        Returns:
            Save operation result
        """
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            metadata_file = output_dir / "metadata.json"

            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2, default=str)

            logger.info(f"Saved metadata: {metadata_file}")

            return {"success": True, "metadata_file": str(metadata_file)}

        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return {"success": False, "error": str(e)}

    def create_summary_report(
        self,
        track_name: str,
        separation_result: Dict,
        processing_results: Optional[Dict],
        output_paths: Dict,
    ) -> str:
        """
        Create a human-readable summary report.

        Args:
            track_name: Name of the track
            separation_result: Results from separation
            processing_results: Results from processing
            output_paths: Output directory paths

        Returns:
            Summary report as string
        """
        report_lines = [
            "=" * 60,
            "MUSIC STEM SEPARATION REPORT",
            "=" * 60,
            f"Track Name: {track_name}",
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SEPARATION DETAILS:",
            f"  Source File: {separation_result.get('audio_file', 'Unknown')}",
            f"  Model Used: {separation_result.get('model_used', 'Unknown')}",
            f"  Device: {separation_result.get('device_used', 'Unknown')}",
            f"  Success: {'Yes' if separation_result.get('success') else 'No'}",
            "",
        ]

        # Add stem information
        if separation_result.get("stems"):
            report_lines.extend(["SEPARATED STEMS:", ""])

            for stem_name, stem_path in separation_result["stems"].items():
                report_lines.append(f"  {stem_name.title()}: {stem_path}")

                # Add processing metrics if available
                if (
                    processing_results
                    and "processed_stems" in processing_results
                    and stem_name in processing_results["processed_stems"]
                ):

                    metrics = processing_results["processed_stems"][stem_name].get(
                        "metrics", {}
                    )
                    if metrics:
                        duration = metrics.get("duration_seconds", 0)
                        peak_db = metrics.get("peak_db")
                        peak_str = (
                            f"{peak_db:.1f}dB"
                            if isinstance(peak_db, (int, float))
                            else "N/A"
                        )
                        report_lines.append(
                            f"    Duration: {duration:.1f}s, Peak: {peak_str}"
                        )

            report_lines.append("")

        # Add output information
        if output_paths:
            report_lines.extend(
                [
                    "OUTPUT LOCATIONS:",
                    f"  Track Directory: {output_paths.get('track_dir', '')}",
                    f"  Stems Directory: {output_paths.get('stems_dir', '')}",
                    "",
                ]
            )

        # Add processing information
        if processing_results:
            processing_success = processing_results.get("success", False)
            report_lines.extend(
                [
                    "PROCESSING:",
                    f"  Enhancement Applied: {'Yes' if processing_success else 'No'}",
                    "",
                ]
            )

        report_lines.append("=" * 60)

        return "\n".join(report_lines)

    def cleanup_temp_files(self, temp_files: List[str]) -> None:
        """
        Clean up temporary files.

        Args:
            temp_files: List of temporary file paths to remove
        """
        for file_path in temp_files:
            try:
                path = Path(file_path)
                if path.exists():
                    path.unlink()
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")

    def get_output_summary(self, output_paths: Dict) -> Dict:
        """
        Get summary of output files and directories.

        Args:
            output_paths: Dictionary of output paths

        Returns:
            Summary information
        """
        summary = {
            "track_directory": str(output_paths.get("track_dir", "")),
            "stems_directory": str(output_paths.get("stems_dir", "")),
            "stem_files": [],
            "total_files": 0,
            "total_size_bytes": 0,
        }

        try:
            stems_dir = Path(output_paths.get("stems_dir", ""))
            if stems_dir.exists():
                stem_files = list(stems_dir.glob("*.wav"))
                summary["stem_files"] = [str(f) for f in stem_files]
                summary["total_files"] = len(stem_files)

                # Calculate total size
                total_size = sum(f.stat().st_size for f in stem_files if f.exists())
                summary["total_size_bytes"] = total_size
                summary["total_size_mb"] = round(total_size / (1024 * 1024), 2)

        except Exception as e:
            logger.warning(f"Failed to generate output summary: {e}")

        return summary

    def validate_output_files(self, expected_files: List[str]) -> Dict:
        """
        Validate that expected output files exist.

        Args:
            expected_files: List of expected file paths

        Returns:
            Validation results
        """
        existing_files = []
        missing_files = []

        for file_path in expected_files:
            if Path(file_path).exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)

        return {
            "all_exist": len(missing_files) == 0,
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_expected": len(expected_files),
        }

    def get_file_size_info(self, file_paths: List[str]) -> Dict:
        """
        Get file size information for a list of files.

        Args:
            file_paths: List of file paths

        Returns:
            Size information dictionary
        """
        file_sizes = {}
        total_size = 0

        for file_path in file_paths:
            try:
                path = Path(file_path)
                if path.exists():
                    size = path.stat().st_size
                    file_sizes[file_path] = size
                    total_size += size
            except Exception as e:
                logger.warning(f"Failed to get size for {file_path}: {e}")
                file_sizes[file_path] = 0

        return {
            "file_sizes": file_sizes,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        sanitized = filename

        for char in invalid_chars:
            sanitized = sanitized.replace(char, "_")

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip(". ")

        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        # Ensure it's not empty
        if not sanitized:
            sanitized = "unknown_track"

        return sanitized
