"""Progress display widget for showing processing status."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
)
from PyQt6.QtCore import Qt


class ProgressDisplay(QWidget):
    """Widget to display processing progress with ETA."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.hide()  # Hidden by default until processing starts

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Progress container frame
        self.progress_frame = QFrame()
        self.progress_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.progress_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 20px;
            }
            """
        )

        frame_layout = QVBoxLayout(self.progress_frame)
        frame_layout.setSpacing(12)

        # Status message label
        self.status_label = QLabel("Preparing...")
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
            }
            """
        )
        frame_layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMinimumHeight(25)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #fff;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            """
        )
        frame_layout.addWidget(self.progress_bar)

        # Info row (percentage and ETA)
        info_layout = QHBoxLayout()

        # Percentage label
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #4CAF50;
            }
            """
        )
        info_layout.addWidget(self.percentage_label)

        info_layout.addStretch()

        # ETA label
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #666;
            }
            """
        )
        info_layout.addWidget(self.eta_label)

        frame_layout.addLayout(info_layout)

        # Stage details label
        self.stage_label = QLabel("")
        self.stage_label.setWordWrap(True)
        self.stage_label.setStyleSheet(
            """
            QLabel {
                font-size: 11px;
                color: #888;
                font-style: italic;
            }
            """
        )
        frame_layout.addWidget(self.stage_label)

        layout.addWidget(self.progress_frame)

    def update_progress(
        self, percent: int, message: str, stage: str = "", eta_seconds: int = None
    ) -> None:
        """
        Update the progress display.

        Args:
            percent: Progress percentage (0-100)
            message: Status message to display
            stage: Current processing stage
            eta_seconds: Estimated time remaining in seconds
        """
        self.progress_bar.setValue(percent)
        self.percentage_label.setText(f"{percent}%")
        self.status_label.setText(message)

        # Update stage label
        if stage:
            stage_text = self._format_stage(stage)
            self.stage_label.setText(f"Stage: {stage_text}")
        else:
            self.stage_label.setText("")

        # Update ETA
        if eta_seconds is not None and eta_seconds > 0 and percent < 100:
            eta_text = self._format_eta(eta_seconds)
            self.eta_label.setText(f"ETA: {eta_text}")
        elif percent >= 100:
            self.eta_label.setText("Complete!")
        else:
            self.eta_label.setText("")

        # Change colors based on progress
        if percent >= 100:
            self.percentage_label.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                    font-weight: bold;
                    color: #2e7d32;
                }
                """
            )
        elif percent >= 80:
            self.percentage_label.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                    font-weight: bold;
                    color: #689F38;
                }
                """
            )

    def _format_stage(self, stage: str) -> str:
        """Format stage name for display."""
        # Convert snake_case to Title Case
        return stage.replace("_", " ").title()

    def _format_eta(self, seconds: int) -> str:
        """Format ETA in human-readable format."""
        if seconds < 60:
            return f"{seconds}s remaining"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            if secs == 0:
                return f"{minutes}m remaining"
            return f"{minutes}m {secs}s remaining"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m remaining"

    def start_processing(self, is_download: bool = False) -> None:
        """
        Show progress display and reset to initial state.

        Args:
            is_download: If True, show downloading message
        """
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        if is_download:
            self.status_label.setText("Downloading from Spotify...")
            self.stage_label.setText("This may take a moment")
        else:
            self.status_label.setText("Starting...")
            self.stage_label.setText("")
        self.eta_label.setText("")
        self.show()

    def complete_processing(self) -> None:
        """Update display to show completion."""
        self.progress_bar.setValue(100)
        self.percentage_label.setText("100%")
        self.status_label.setText("✓ Processing Complete!")
        self.stage_label.setText("")
        self.eta_label.setText("Complete!")

        # Update styling for completion
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2e7d32;
            }
            """
        )

    def error_processing(self, error_message: str) -> None:
        """Update display to show error."""
        self.status_label.setText(f"✗ Error: {error_message}")
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #c62828;
            }
            """
        )
        self.stage_label.setText("")
        self.eta_label.setText("")

    def reset(self) -> None:
        """Reset and hide the progress display."""
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        self.status_label.setText("Preparing...")
        self.stage_label.setText("")
        self.eta_label.setText("")
        self.hide()
