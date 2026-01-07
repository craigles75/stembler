"""Main window for the Stembler GUI application."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from pathlib import Path

from .widgets.file_input import FileInputWidget
from .widgets.process_button import ProcessButton
from .widgets.progress_display import ProgressDisplay
from .widgets.result_display import ResultDisplay
from .controllers.processing_controller import ProcessingController
from .utils.progress_tracker import ProgressTracker
from .utils.credential_utils import (
    check_spotify_credentials,
    get_credential_setup_instructions,
)
from .models import AudioInput, InputType


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._controller = ProcessingController()
        self._current_audio_input: AudioInput | None = None
        self._progress_tracker: ProgressTracker | None = None

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Stembler - Music Stem Separator")
        self.setMinimumSize(700, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header_label = QLabel("Music Stem Separator")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #333;
                padding: 10px;
            }
            """
        )
        layout.addWidget(header_label)

        subtitle_label = QLabel("Separate your audio into drums, bass, vocals, and other instruments")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("color: #666; font-size: 13px; padding-bottom: 10px;")
        layout.addWidget(subtitle_label)

        # File input widget
        self.file_input = FileInputWidget()
        layout.addWidget(self.file_input)

        # Process button
        self.process_button = ProcessButton()
        layout.addWidget(self.process_button)

        # Progress display
        self.progress_display = ProgressDisplay()
        layout.addWidget(self.progress_display)

        # Result display
        self.result_display = ResultDisplay()
        layout.addWidget(self.result_display)

        layout.addStretch()

    def _connect_signals(self) -> None:
        """Connect signals and slots."""
        # File input signals
        self.file_input.file_selected.connect(self._on_file_selected)
        self.file_input.validation_changed.connect(self._on_validation_changed)

        # Process button signals
        self.process_button.process_requested.connect(self._on_process_requested)
        self.process_button.cancel_requested.connect(self._on_cancel_requested)

        # Result display signals
        self.result_display.open_folder_requested.connect(self._on_open_folder_requested)

        # Controller signals
        self._controller.processing_started.connect(self._on_processing_started)
        self._controller.progress_updated.connect(self._on_progress_updated)
        self._controller.processing_completed.connect(self._on_processing_completed)
        self._controller.processing_failed.connect(self._on_processing_failed)
        self._controller.processing_cancelled.connect(self._on_processing_cancelled)

    def _on_file_selected(self, file_path: str) -> None:
        """Handle file selection."""
        self._current_audio_input = self.file_input.get_audio_input()

    def _on_validation_changed(self, is_valid: bool, error_message: str) -> None:
        """Handle validation state change."""
        self.process_button.set_ready_to_process(is_valid)

        if not is_valid and error_message:
            # Could show error in status bar if we add one
            pass

    def _on_process_requested(self) -> None:
        """Handle process button click."""
        if not self._current_audio_input or not self._current_audio_input.is_valid:
            self._show_error("Please select a valid audio file first")
            return

        # Check Spotify credentials if processing a Spotify URL
        if self._current_audio_input.input_type == InputType.SPOTIFY_URL:
            credentials_valid, error_msg = check_spotify_credentials()
            if not credentials_valid:
                self._show_spotify_setup_dialog(error_msg)
                return

        # Get default output directory (user's Music folder / Stembler Output)
        output_dir = self._get_default_output_dir()

        # Start processing
        success = self._controller.start_processing(
            audio_input=self._current_audio_input,
            output_dir=str(output_dir),
            model_name="htdemucs",
            device=None,
            enable_enhancement=True,
        )

        if not success:
            self._show_error("Failed to start processing. Please try again.")

    def _on_cancel_requested(self) -> None:
        """Handle cancel button click."""
        reply = QMessageBox.question(
            self,
            "Cancel Processing",
            "Are you sure you want to cancel the current processing job?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self._controller.cancel_processing()

    def _on_open_folder_requested(self, folder_path: str) -> None:
        """Handle open folder request."""
        # The ResultDisplay widget already handles opening the folder
        # This is just for logging or additional actions if needed
        pass

    def _on_processing_started(self) -> None:
        """Handle processing start."""
        self.process_button.set_processing(True)
        self.file_input.set_enabled(False)
        self.result_display.clear()

        # Create progress tracker for ETA estimation
        input_path = self._current_audio_input.path if self._current_audio_input else None
        self._progress_tracker = ProgressTracker(model_name="htdemucs", file_path=input_path)
        self._progress_tracker.start()

        # Show progress display (with download message for Spotify/URLs)
        is_download = (
            self._current_audio_input
            and self._current_audio_input.requires_download
        )
        self.progress_display.start_processing(is_download=is_download)

    def _on_progress_updated(self, percent: int, message: str, stage: str) -> None:
        """Handle progress update."""
        # Update window title with progress
        self.setWindowTitle(f"Stembler - Processing: {percent}%")

        # Update progress tracker
        if self._progress_tracker:
            self._progress_tracker.update(percent)
            eta_seconds = self._progress_tracker.estimate_remaining_seconds(percent)
        else:
            eta_seconds = None

        # Update progress display
        self.progress_display.update_progress(percent, message, stage, eta_seconds)

    def _on_processing_completed(self, output_bundle) -> None:
        """Handle successful processing completion."""
        self.process_button.set_processing(False)
        self.process_button.set_ready_to_process(True)
        self.file_input.set_enabled(True)
        self.setWindowTitle("Stembler - Music Stem Separator")

        # Update progress display to show completion
        self.progress_display.complete_processing()

        # Show result
        self.result_display.show_success(output_bundle)

        # Show success message
        elapsed_time = (
            self._progress_tracker.format_elapsed_time()
            if self._progress_tracker
            else "unknown"
        )
        QMessageBox.information(
            self,
            "Success",
            f"Stem separation completed successfully!\n\n"
            f"Time taken: {elapsed_time}\n"
            f"Output saved to:\n{output_bundle.track_directory}",
        )

    def _on_processing_failed(self, error_message: str) -> None:
        """Handle processing failure."""
        self.process_button.set_processing(False)
        self.process_button.set_ready_to_process(True)
        self.file_input.set_enabled(True)
        self.setWindowTitle("Stembler - Music Stem Separator")

        # Update progress display to show error
        self.progress_display.error_processing(error_message)

        self.result_display.show_error(error_message)

        self._show_error(f"Processing failed:\n\n{error_message}")

    def _on_processing_cancelled(self) -> None:
        """Handle processing cancellation."""
        self.process_button.set_processing(False)
        self.process_button.set_ready_to_process(True)
        self.file_input.set_enabled(True)
        self.setWindowTitle("Stembler - Music Stem Separator")

        # Reset progress display
        self.progress_display.reset()

        QMessageBox.information(
            self,
            "Cancelled",
            "Processing has been cancelled.",
        )

    def _get_default_output_dir(self) -> Path:
        """Get the default output directory."""
        # Use platformdirs to get user's Music directory
        try:
            from platformdirs import user_music_path

            music_dir = Path(user_music_path())
        except Exception:
            # Fallback to home directory
            music_dir = Path.home()

        output_dir = music_dir / "Stembler Output"
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir

    def _show_error(self, message: str) -> None:
        """Show error message dialog."""
        QMessageBox.critical(
            self,
            "Error",
            message,
        )

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if self._controller.is_processing():
            reply = QMessageBox.question(
                self,
                "Processing in Progress",
                "Processing is currently in progress. Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._controller.cancel_processing()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
