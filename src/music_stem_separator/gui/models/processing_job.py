"""Data model for processing jobs."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum


class JobStatus(Enum):
    """Status of a processing job."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingJob:
    """Represents a single audio processing job."""

    input_path: str
    output_dir: str
    job_id: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    status: JobStatus = JobStatus.PENDING
    model_name: str = "htdemucs"
    device: Optional[str] = None
    enable_enhancement: bool = True
    progress_percent: int = 0
    progress_message: str = ""
    progress_stage: str = ""
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self) -> None:
        """Mark job as started."""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.now()

    def complete(self, result: Dict[str, Any]) -> None:
        """Mark job as completed with result."""
        self.status = JobStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
        self.progress_percent = 100
        self.progress_message = "Processing complete"

    def fail(self, error: str) -> None:
        """Mark job as failed with error message."""
        self.status = JobStatus.FAILED
        self.error_message = error
        self.completed_at = datetime.now()
        self.progress_message = f"Failed: {error}"

    def cancel(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
        self.progress_message = "Cancelled by user"

    def update_progress(self, percent: int, message: str, stage: str = "") -> None:
        """Update job progress."""
        self.progress_percent = percent
        self.progress_message = message
        if stage:
            self.progress_stage = stage

    @property
    def is_active(self) -> bool:
        """Check if job is currently active (pending or processing)."""
        return self.status in (JobStatus.PENDING, JobStatus.PROCESSING)

    @property
    def is_complete(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in (
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        )

    @property
    def duration_seconds(self) -> Optional[float]:
        """Get job duration in seconds, if started."""
        if not self.started_at:
            return None
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()

    @property
    def input_filename(self) -> str:
        """Get the input filename."""
        return Path(self.input_path).name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "job_id": self.job_id,
            "input_path": self.input_path,
            "input_filename": self.input_filename,
            "output_dir": self.output_dir,
            "status": self.status.value,
            "model_name": self.model_name,
            "device": self.device,
            "enable_enhancement": self.enable_enhancement,
            "progress_percent": self.progress_percent,
            "progress_message": self.progress_message,
            "progress_stage": self.progress_stage,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
        }
