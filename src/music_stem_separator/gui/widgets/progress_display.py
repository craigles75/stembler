"""Progress display widget for showing processing status."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
    QSizePolicy,
)

from ..utils.theme import Theme


class ProgressDisplay(QWidget):
    """Widget to display processing progress with ETA."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        # Set size policy to collapse when hidden
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.hide()  # Hidden by default until processing starts

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins - spacing handled by parent
        layout.setSpacing(Theme.SPACING_SM)

        # Progress container frame with card styling
        self.progress_frame = QFrame()
        self.progress_frame.setObjectName("progress_frame")
        self.progress_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.progress_frame.setStyleSheet(
            f"""
            QFrame#progress_frame {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_LG}px;
            }}
            """
        )

        frame_layout = QVBoxLayout(self.progress_frame)
        frame_layout.setSpacing(Theme.SPACING_MD)

        # Status/Stage message at top
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Preparing...")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        # Percentage inline with status
        self.percentage_label = QLabel("0%")
        self.percentage_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.PRIMARY};
            }}
            """
        )
        status_layout.addWidget(self.percentage_label)

        frame_layout.addLayout(status_layout)

        # Progress bar - modern slim design
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)  # Slim progress bar
        self.progress_bar.setStyleSheet(
            f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: {Theme.BORDER_LIGHT};
            }}
            QProgressBar::chunk {{
                background-color: {Theme.PRIMARY};
                border-radius: 4px;
            }}
            """
        )
        frame_layout.addWidget(self.progress_bar)

        # Bottom row (stage and ETA)
        bottom_layout = QHBoxLayout()

        # Stage details label
        self.stage_label = QLabel("")
        self.stage_label.setWordWrap(True)
        self.stage_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_SM}px;
                color: {Theme.TEXT_SECONDARY};
                font-style: italic;
            }}
            """
        )
        bottom_layout.addWidget(self.stage_label)

        bottom_layout.addStretch()

        # ETA label with clock icon
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_SM}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_SECONDARY};
            }}
            """
        )
        bottom_layout.addWidget(self.eta_label)

        frame_layout.addLayout(bottom_layout)

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

        # Update ETA with clock icon
        if eta_seconds is not None and eta_seconds > 0 and percent < 100:
            eta_text = self._format_eta(eta_seconds)
            self.eta_label.setText(f"🕐 {eta_text}")
        elif percent >= 100:
            self.eta_label.setText("✓ Complete!")
        else:
            self.eta_label.setText("")

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
        self.eta_label.setText("✓ Complete!")

        # Update styling for completion
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.SUCCESS};
            }}
            """
        )

    def error_processing(self, error_message: str) -> None:
        """Update display to show error."""
        self.status_label.setText(f"✗ Error: {error_message}")
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.ERROR};
            }}
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
