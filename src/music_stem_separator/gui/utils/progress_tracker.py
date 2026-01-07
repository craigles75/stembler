"""Progress tracking and time estimation utilities."""

import time
from pathlib import Path
from typing import Optional


class ProgressTracker:
    """Tracks processing progress and estimates time remaining."""

    # Average processing time in seconds per MB for different models
    # These are rough estimates and will vary by hardware
    MODEL_PROCESSING_RATES = {
        "htdemucs": 3.0,  # seconds per MB
        "htdemucs_ft": 3.5,  # slightly slower due to fine-tuning
        "mdx_extra": 4.0,  # more complex model
        "mdx_q": 2.0,  # quantized, faster
    }

    def __init__(self, model_name: str = "htdemucs", file_path: Optional[str] = None):
        """
        Initialize progress tracker.

        Args:
            model_name: Name of the Demucs model being used
            file_path: Path to the audio file being processed
        """
        self.model_name = model_name
        self.file_path = file_path
        self.start_time: Optional[float] = None
        self.last_update_time: Optional[float] = None
        self.last_percent: int = 0
        self.file_size_mb: float = 0.0

        # Calculate file size if provided
        if file_path:
            try:
                file_size = Path(file_path).stat().st_size
                self.file_size_mb = file_size / (1024 * 1024)  # Convert to MB
            except Exception:
                self.file_size_mb = 10.0  # Default assumption

    def start(self) -> None:
        """Mark the start of processing."""
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_percent = 0

    def update(self, percent: int) -> None:
        """
        Update progress.

        Args:
            percent: Current progress percentage (0-100)
        """
        self.last_update_time = time.time()
        self.last_percent = percent

    def estimate_remaining_seconds(self, current_percent: int) -> Optional[int]:
        """
        Estimate seconds remaining until completion.

        Args:
            current_percent: Current progress percentage (0-100)

        Returns:
            Estimated seconds remaining, or None if cannot estimate
        """
        if not self.start_time or current_percent <= 0:
            return self._estimate_from_file_size()

        if current_percent >= 100:
            return 0

        # Calculate elapsed time
        elapsed_seconds = time.time() - self.start_time

        # Calculate average time per percent
        time_per_percent = elapsed_seconds / current_percent

        # Estimate remaining time
        remaining_percent = 100 - current_percent
        estimated_remaining = int(time_per_percent * remaining_percent)

        # Add some buffer for final stages (they tend to be slower)
        if current_percent > 80:
            estimated_remaining = int(estimated_remaining * 1.2)

        return max(0, estimated_remaining)

    def _estimate_from_file_size(self) -> Optional[int]:
        """
        Estimate total time based on file size when no progress data available.

        Returns:
            Estimated total seconds, or None if cannot estimate
        """
        if self.file_size_mb <= 0:
            return None

        # Get processing rate for this model
        rate = self.MODEL_PROCESSING_RATES.get(self.model_name, 3.0)

        # Calculate estimated time
        estimated_seconds = int(self.file_size_mb * rate)

        # Add overhead for I/O and setup (20-30 seconds)
        estimated_seconds += 25

        return estimated_seconds

    def get_elapsed_seconds(self) -> int:
        """Get elapsed processing time in seconds."""
        if not self.start_time:
            return 0
        return int(time.time() - self.start_time)

    def get_processing_rate(self) -> Optional[float]:
        """
        Get current processing rate in percent per second.

        Returns:
            Processing rate, or None if not enough data
        """
        if not self.start_time or self.last_percent <= 0:
            return None

        elapsed = time.time() - self.start_time
        if elapsed <= 0:
            return None

        return self.last_percent / elapsed

    def format_elapsed_time(self) -> str:
        """
        Get formatted elapsed time string.

        Returns:
            Formatted time string like "1m 23s"
        """
        elapsed = self.get_elapsed_seconds()

        if elapsed < 60:
            return f"{elapsed}s"
        elif elapsed < 3600:
            minutes = elapsed // 60
            seconds = elapsed % 60
            return f"{minutes}m {seconds}s"
        else:
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            return f"{hours}h {minutes}m"
