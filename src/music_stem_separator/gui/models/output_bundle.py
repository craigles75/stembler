"""Data model for processing output bundle."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import sys


@dataclass
class OutputBundle:
    """Represents the output from a completed processing job."""

    track_directory: Path
    stem_files: Dict[str, Path] = field(default_factory=dict)
    metadata_file: Optional[Path] = None
    summary_report: Optional[str] = None
    total_size_mb: float = 0.0
    processing_time_seconds: Optional[float] = None

    @classmethod
    def from_result(cls, result: Dict) -> "OutputBundle":
        """Create OutputBundle from process_track result dictionary."""
        output_structure = result.get("output_structure", {})
        output_summary = result.get("output_summary", {})

        track_dir = Path(output_summary.get("track_directory", ""))

        # Extract stem files from output structure
        stem_files = {}
        stems_dir = output_structure.get("stems_dir")
        if stems_dir:
            stems_path = Path(stems_dir)
            if stems_path.exists():
                for stem_file in stems_path.glob("*.wav"):
                    stem_name = stem_file.stem
                    stem_files[stem_name] = stem_file

        # Find metadata file
        metadata_file = None
        metadata_path = track_dir / "metadata.json"
        if metadata_path.exists():
            metadata_file = metadata_path

        return cls(
            track_directory=track_dir,
            stem_files=stem_files,
            metadata_file=metadata_file,
            summary_report=result.get("summary_report"),
            total_size_mb=output_summary.get("total_size_mb", 0.0),
        )

    @property
    def exists(self) -> bool:
        """Check if output directory exists."""
        return self.track_directory.exists()

    @property
    def stem_count(self) -> int:
        """Get number of separated stems."""
        return len(self.stem_files)

    @property
    def stem_names(self) -> List[str]:
        """Get list of stem names."""
        return list(self.stem_files.keys())

    def get_stem_path(self, stem_name: str) -> Optional[Path]:
        """Get path to a specific stem file."""
        return self.stem_files.get(stem_name)

    def open_in_file_manager(self) -> bool:
        """Open the output directory in the system file manager."""
        if not self.exists:
            return False

        try:
            if sys.platform == "darwin":  # macOS
                import subprocess

                subprocess.run(["open", str(self.track_directory)], check=True)
            elif sys.platform == "win32":  # Windows
                import os

                os.startfile(str(self.track_directory))
            else:  # Linux/Unix
                import subprocess

                subprocess.run(["xdg-open", str(self.track_directory)], check=True)
            return True
        except Exception:
            return False

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "track_directory": str(self.track_directory),
            "exists": self.exists,
            "stem_count": self.stem_count,
            "stem_names": self.stem_names,
            "stem_files": {name: str(path) for name, path in self.stem_files.items()},
            "metadata_file": str(self.metadata_file) if self.metadata_file else None,
            "total_size_mb": self.total_size_mb,
            "processing_time_seconds": self.processing_time_seconds,
        }
