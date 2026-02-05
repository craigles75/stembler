"""Controller for managing processing jobs and background workers."""

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Optional

from ...shared.process_track import process_track
from ..models import ProcessingJob, AudioInput, OutputBundle


class ProcessingWorker(QThread):
    """Background worker thread for processing audio files."""

    # Signals for communication with main thread
    progress_updated = pyqtSignal(int, str, str)  # percent, message, stage
    processing_completed = pyqtSignal(dict)  # result dictionary
    processing_failed = pyqtSignal(str)  # error message

    def __init__(self, job: ProcessingJob):
        super().__init__()
        self.job = job
        self._is_cancelled = False

    def run(self) -> None:
        """Execute the processing job in background thread."""
        try:
            # Call the shared process_track function with progress callback
            result = process_track(
                input_path=self.job.input_path,
                output_dir=self.job.output_dir,
                model_name=self.job.model_name,
                device=self.job.device,
                enable_enhancement=self.job.enable_enhancement,
                verbose=False,
                progress_callback=self._progress_callback,
            )

            # Check if cancelled during processing
            if self._is_cancelled:
                return

            # Emit result
            if result.get("success"):
                self.processing_completed.emit(result)
            else:
                error = result.get("error", "Unknown error occurred")
                self.processing_failed.emit(error)

        except Exception as e:
            if not self._is_cancelled:
                self.processing_failed.emit(str(e))

    def _progress_callback(self, progress_data: dict) -> None:
        """Handle progress updates from process_track."""
        if self._is_cancelled:
            return

        stage = progress_data.get("stage", "")
        percent = progress_data.get("percent", 0)
        message = progress_data.get("message", "")

        self.progress_updated.emit(percent, message, stage)

    def cancel(self) -> None:
        """Request cancellation of the processing job."""
        self._is_cancelled = True


class ProcessingController(QObject):
    """Controller for managing audio processing jobs."""

    # Signals
    progress_updated = pyqtSignal(int, str, str)  # percent, message, stage
    processing_started = pyqtSignal()
    processing_completed = pyqtSignal(OutputBundle)  # output bundle
    processing_failed = pyqtSignal(str)  # error message
    processing_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_job: Optional[ProcessingJob] = None
        self._worker: Optional[ProcessingWorker] = None

    def start_processing(
        self,
        audio_input: AudioInput,
        output_dir: str,
        model_name: str = "htdemucs",
        device: Optional[str] = None,
        enable_enhancement: bool = True,
    ) -> bool:
        """
        Start processing an audio input.

        Args:
            audio_input: Validated audio input
            output_dir: Output directory path
            model_name: Demucs model name
            device: Device to use (None for auto-detect)
            enable_enhancement: Whether to apply audio enhancement

        Returns:
            True if processing started, False if already processing or invalid input
        """
        # Validate input
        if not self._validate_input(audio_input):
            return False

        # Check if already processing
        if self.is_processing():
            return False

        # Create processing job
        self._current_job = ProcessingJob(
            input_path=audio_input.path,
            output_dir=output_dir,
            model_name=model_name,
            device=device,
            enable_enhancement=enable_enhancement,
        )

        # Mark job as started
        self._current_job.start()

        # Create and start worker thread
        self._worker = ProcessingWorker(self._current_job)
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.processing_completed.connect(self._on_processing_completed)
        self._worker.processing_failed.connect(self._on_processing_failed)
        self._worker.finished.connect(self._on_worker_finished)

        self._worker.start()
        self.processing_started.emit()

        return True

    def cancel_processing(self) -> None:
        """Cancel the current processing job."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.quit()

            # Wait for thread to finish, up to 5 seconds
            if not self._worker.wait(5000):
                # Thread didn't finish in time - force terminate
                self._worker.terminate()
                self._worker.wait()  # Wait for termination

            # Now cleanup safely - thread is guaranteed to be stopped
            if self._worker:
                self._worker.deleteLater()
                self._worker = None

            if self._current_job:
                self._current_job.cancel()

            self.processing_cancelled.emit()

    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self._worker is not None and self._worker.isRunning()

    def get_current_job(self) -> Optional[ProcessingJob]:
        """Get the current processing job."""
        return self._current_job

    def _validate_input(self, audio_input: AudioInput) -> bool:
        """
        Validate audio input.

        Args:
            audio_input: AudioInput to validate

        Returns:
            True if valid, False otherwise
        """
        if not audio_input or not audio_input.is_valid:
            self.processing_failed.emit(
                audio_input.error_message if audio_input else "Invalid input"
            )
            return False

        return True

    def _on_progress_updated(self, percent: int, message: str, stage: str) -> None:
        """Handle progress update from worker."""
        if self._current_job:
            self._current_job.update_progress(percent, message, stage)

        self.progress_updated.emit(percent, message, stage)

    def _on_processing_completed(self, result: dict) -> None:
        """Handle successful processing completion."""
        if self._current_job:
            self._current_job.complete(result)

            # Create output bundle from result
            try:
                output_bundle = OutputBundle.from_result(result)

                # Add processing time from job
                if self._current_job.duration_seconds:
                    output_bundle.processing_time_seconds = (
                        self._current_job.duration_seconds
                    )

                self.processing_completed.emit(output_bundle)
            except Exception as e:
                self.processing_failed.emit(f"Failed to create output bundle: {e}")

    def _on_processing_failed(self, error: str) -> None:
        """Handle processing failure."""
        if self._current_job:
            self._current_job.fail(error)

        self.processing_failed.emit(error)

    def _on_worker_finished(self) -> None:
        """Handle worker thread completion."""
        # Cleanup worker
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
