"""Data models for the GUI application."""

from .audio_input import AudioInput, InputType
from .output_bundle import OutputBundle
from .processing_job import ProcessingJob, JobStatus

__all__ = [
    "AudioInput",
    "InputType",
    "OutputBundle",
    "ProcessingJob",
    "JobStatus",
]
