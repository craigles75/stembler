"""Main window for the Stembler GUI application."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QMenuBar,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from pathlib import Path

from .widgets.file_input import FileInputWidget
from .widgets.process_button import ProcessButton
from .widgets.progress_display import ProgressDisplay
from .widgets.result_display import ResultDisplay
from .widgets.settings_panel import SettingsPanel
from .widgets.about_dialog import AboutDialog
from .controllers.processing_controller import ProcessingController
from .controllers.settings_controller import SettingsController
from .utils.progress_tracker import ProgressTracker
from .utils.credential_utils import (
    check_spotify_credentials,
    get_credential_setup_instructions,
)
from .utils.version import get_version
from .utils.theme import Theme
from .models import AudioInput, InputType, UserSettings


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self._controller = ProcessingController()
        self._settings_controller = SettingsController()
        self._current_audio_input: AudioInput | None = None
        self._progress_tracker: ProgressTracker | None = None

        # Load settings on startup
        self._current_settings = self._settings_controller.load_settings()

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        version = get_version()
        self.setWindowTitle(f"Stembler v{version} - Music Stem Separator")
        self.setMinimumSize(700, 600)

        # Apply window background color
        self.setStyleSheet(
            f"QMainWindow {{ background-color: {Theme.BACKGROUND_PRIMARY}; }}"
        )

        # Create menu bar
        self._create_menu_bar()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setSpacing(Theme.SPACING_LG)  # 24px vertical spacing
        layout.setContentsMargins(
            Theme.SPACING_XL,  # 32px left
            Theme.SPACING_XL,  # 32px top
            Theme.SPACING_XL,  # 32px right
            Theme.SPACING_XL,  # 32px bottom
        )

        # Header
        header_label = QLabel("Music Stem Separator")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 28px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.TEXT_PRIMARY};
                letter-spacing: {Theme.LETTER_SPACING_TIGHT};
                padding: {Theme.SPACING_SM}px;
            }}
            """
        )
        layout.addWidget(header_label)

        subtitle_label = QLabel(
            "Separate your audio into drums, bass, vocals, and other instruments"
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                padding-bottom: {Theme.SPACING_SM}px;
            }}
            """
        )
        layout.addWidget(subtitle_label)

        # Separator line after header
        separator1 = self._create_separator()
        layout.addWidget(separator1)

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

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._on_settings_clicked)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        # About action
        about_action = QAction("&About Stembler", self)
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)

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

        # Get output directory from settings
        output_dir = self._current_settings.get_output_directory()

        # Start processing with settings
        success = self._controller.start_processing(
            audio_input=self._current_audio_input,
            output_dir=str(output_dir),
            model_name=self._current_settings.model_name,
            device=self._current_settings.device,
            enable_enhancement=self._current_settings.enable_enhancement,
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

    def _on_settings_clicked(self) -> None:
        """Handle settings menu click."""
        # Create and show settings dialog
        settings_dialog = SettingsPanel(self._current_settings, self)
        settings_dialog.settings_changed.connect(self._on_settings_changed)

        if settings_dialog.exec():
            # Settings were saved (user clicked Save)
            pass

    def _on_settings_changed(self, new_settings: UserSettings) -> None:
        """Handle settings change."""
        # Save settings to file
        success = self._settings_controller.save_settings(new_settings)
        if success:
            self._current_settings = new_settings
            QMessageBox.information(
                self,
                "Settings Saved",
                "Your settings have been saved successfully.\n\n"
                "New settings will be applied to the next processing job.",
            )
        else:
            QMessageBox.warning(
                self,
                "Save Failed",
                "Failed to save settings. Please try again.",
            )

    def _on_about_clicked(self) -> None:
        """Handle about menu click."""
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def _on_processing_started(self) -> None:
        """Handle processing start."""
        self.process_button.set_processing(True)
        self.file_input.set_enabled(False)
        self.result_display.clear()

        # Create progress tracker for ETA estimation
        input_path = self._current_audio_input.path if self._current_audio_input else None
        self._progress_tracker = ProgressTracker(
            model_name=self._current_settings.model_name, file_path=input_path
        )
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
        version = get_version()
        self.setWindowTitle(f"Stembler v{version} - Processing: {percent}%")

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
        version = get_version()
        self.setWindowTitle(f"Stembler v{version} - Music Stem Separator")

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
        version = get_version()
        self.setWindowTitle(f"Stembler v{version} - Music Stem Separator")

        # Update progress display to show error
        self.progress_display.error_processing(error_message)

        self.result_display.show_error(error_message)

        self._show_error(f"Processing failed:\n\n{error_message}")

    def _on_processing_cancelled(self) -> None:
        """Handle processing cancellation."""
        self.process_button.set_processing(False)
        self.process_button.set_ready_to_process(True)
        self.file_input.set_enabled(True)
        version = get_version()
        self.setWindowTitle(f"Stembler v{version} - Music Stem Separator")

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

    def _show_spotify_setup_dialog(self, error_msg: str) -> None:
        """Show Spotify credential setup instructions."""
        instructions = get_credential_setup_instructions()

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Spotify Credentials Required")
        msg_box.setText(f"Cannot process Spotify URL: {error_msg}")
        msg_box.setInformativeText("Spotify URLs require API credentials to download tracks.")
        msg_box.setDetailedText(instructions)
        msg_box.exec()

    def _create_separator(self) -> QFrame:
        """Create a subtle horizontal separator line."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setLineWidth(1)
        separator.setStyleSheet(
            f"""
            QFrame {{
                color: {Theme.BORDER_LIGHT};
                margin-top: {Theme.SPACING_SM}px;
                margin-bottom: {Theme.SPACING_SM}px;
            }}
            """
        )
        return separator

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
