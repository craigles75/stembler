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

    # Ordered pipeline stages as seen by the user.  Each entry is
    # (display_name, set_of_raw_stage_keys).  The raw keys are the strings
    # emitted by process_track via the progress callback.
    #
    # Step 1 label is swapped at runtime: "Downloading" when the input
    # requires a download, "Loading Audio" otherwise.
    _STAGES: list[tuple[str, set[str]]] = [
        ("Loading Audio", {"input_processing", "downloading"}),
        ("Separating Stems", {"loading_model", "separating_stems"}),
        ("Writing Files", {"enhancing_audio", "organizing_output"}),
        ("Complete", {"complete"}),
    ]

    # Total number of user-visible steps (cached to avoid recomputing)
    _TOTAL_STEPS: int = len(_STAGES)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Whether the current job involves a download (affects step-1 label)
        self._is_download: bool = False
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

        # Update stage label with step indicator
        if stage:
            self.stage_label.setText(self._format_stage(stage))
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
        """Return a 'Step N of M: Name' string for the given raw stage key.

        Falls back to a Title-Cased version of the raw key when the stage
        is not recognised (e.g. "error" or any future stage added to the
        pipeline without a corresponding _STAGES entry).
        """
        for step_number, (display_name, keys) in enumerate(self._STAGES, start=1):
            if stage in keys:
                # Swap step-1 label when the job is a download
                if step_number == 1 and self._is_download:
                    display_name = "Downloading"
                return f"Step {step_number} of {self._TOTAL_STEPS}: {display_name}"

        # Unrecognised stage -- render gracefully without a step number
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
        self._is_download = is_download
        self.progress_bar.setValue(0)
        self.percentage_label.setText("0%")
        if is_download:
            self.status_label.setText("Downloading from Spotify...")
            self.stage_label.setText(f"Step 1 of {self._TOTAL_STEPS}: Downloading")
        else:
            self.status_label.setText("Starting...")
            self.stage_label.setText(f"Step 1 of {self._TOTAL_STEPS}: Loading Audio")
        self.eta_label.setText("")
        self.show()

    def complete_processing(self) -> None:
        """Update display to show completion."""
        self.progress_bar.setValue(100)
        self.percentage_label.setText("100%")
        self.status_label.setText("✓ Processing Complete!")
        self.stage_label.setText(
            f"Step {self._TOTAL_STEPS} of {self._TOTAL_STEPS}: Complete"
        )
        self.eta_label.setText("✓ Complete!")

        # Re-apply explicit stylesheets to every visible label.  PyQt6 QFrame
        # background cascades can suppress child colours that were set before
        # the frame was re-styled; painting them again here guarantees they
        # are visible in the completion state.  status_label uses TEXT_PRIMARY
        # (dark) for contrast; the green accent is carried by percentage_label
        # and eta_label instead.
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        self.percentage_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.SUCCESS};
            }}
            """
        )
        self.stage_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_SM}px;
                color: {Theme.TEXT_SECONDARY};
                font-style: italic;
            }}
            """
        )
        self.eta_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_SM}px;
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
        # Restore default colour; complete_processing / error_processing mutate
        # this stylesheet to green / red respectively.
        self.status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        self.stage_label.setText("")
        self.eta_label.setText("")
        self._is_download = False
        self.hide()
