"""File input widget with drag-and-drop support."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QStyle,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from ..models import AudioInput
from ..utils.theme import Theme


class FileInputWidget(QWidget):
    """Widget for file input with drag-and-drop and browse button."""

    # Signal emitted when a valid file is selected
    file_selected = pyqtSignal(str)  # file_path

    # Signal emitted when input validation changes
    validation_changed = pyqtSignal(bool, str)  # is_valid, error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_input: AudioInput | None = None
        self._setup_ui()
        self._setup_drag_drop()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins - spacing handled by parent
        layout.setSpacing(Theme.SPACING_MD)

        # Drag-drop area with icon and text
        self.drop_label = QLabel(
            "📁\n\nDrag and drop an audio file here\n"
            f"<small><font color='{Theme.TEXT_TERTIARY}'>or paste a Spotify URL</font></small>"
        )
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setTextFormat(Qt.TextFormat.RichText)
        self.drop_label.setMinimumHeight(180)
        self.drop_label.setStyleSheet(
            f"""
            QLabel {{
                border: 2px dashed {Theme.BORDER_MEDIUM};
                border-radius: 12px;
                background-color: #FAFBFC;
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_MD}px;
                padding: {Theme.SPACING_LG}px;
                qproperty-alignment: AlignCenter;
            }}
            QLabel:hover {{
                border-color: {Theme.BORDER_DARK};
                background-color: #F5F7FA;
            }}
            """
        )
        layout.addWidget(self.drop_label)

        # OR separator
        separator_label = QLabel("— OR —")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_TERTIARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin: {Theme.SPACING_MD}px 0;
            }}
            """
        )
        layout.addWidget(separator_label)

        # File path input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(Theme.SPACING_SM)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter file path or URL...")
        self.path_input.textChanged.connect(self._on_path_changed)
        self.path_input.setStyleSheet(Theme.input_style())
        input_layout.addWidget(self.path_input, stretch=1)

        # Browse button with folder icon
        self.browse_button = QPushButton("  Browse...")
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.browse_button.setIcon(folder_icon)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.browse_button.setStyleSheet(
            Theme.button_style(
                Theme.SECONDARY,
                Theme.SECONDARY_HOVER,
                Theme.SECONDARY_PRESSED,
                height=Theme.INPUT_HEIGHT,
            )
        )
        input_layout.addWidget(self.browse_button)

        layout.addLayout(input_layout)

        # Validation message label
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.ERROR};
                font-size: {Theme.FONT_SIZE_SM}px;
                padding: {Theme.SPACING_SM}px;
                margin-top: {Theme.SPACING_SM}px;
            }}
            """
        )
        self.validation_label.hide()
        layout.addWidget(self.validation_label)

        # File info label (shows when valid)
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.SUCCESS};
                font-size: {Theme.FONT_SIZE_SM}px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                padding: {Theme.SPACING_SM}px;
                margin-top: {Theme.SPACING_SM}px;
            }}
            """
        )
        self.info_label.hide()
        layout.addWidget(self.info_label)

        layout.addStretch()

    def _setup_drag_drop(self) -> None:
        """Enable drag and drop functionality."""
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Active/dragging state with thicker border and green tint
            self.drop_label.setStyleSheet(
                f"""
                QLabel {{
                    border: 3px solid {Theme.PRIMARY};
                    border-radius: 12px;
                    background-color: #F0F9F4;
                    color: {Theme.PRIMARY};
                    font-size: {Theme.FONT_SIZE_MD}px;
                    font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                    padding: {Theme.SPACING_LG}px;
                }}
                """
            )

    def dragLeaveEvent(self, event) -> None:
        """Handle drag leave event."""
        self._reset_drop_label_style()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event."""
        self._reset_drop_label_style()

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if file_path:
                    self.set_path(file_path)
                    event.acceptProposedAction()

    def _reset_drop_label_style(self) -> None:
        """Reset drop label to default style."""
        self.drop_label.setStyleSheet(
            f"""
            QLabel {{
                border: 2px dashed {Theme.BORDER_MEDIUM};
                border-radius: 12px;
                background-color: #FAFBFC;
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_MD}px;
                padding: {Theme.SPACING_LG}px;
            }}
            QLabel:hover {{
                border-color: {Theme.BORDER_DARK};
                background-color: #F5F7FA;
            }}
            """
        )

    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        file_filter = AudioInput.get_file_filter()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "", file_filter
        )
        if file_path:
            self.set_path(file_path)

    def _on_path_changed(self, path: str) -> None:
        """Handle path text field changes."""
        if path.strip():
            self._validate_input(path)
        else:
            self._clear_validation()

    def set_path(self, path: str) -> None:
        """Set the file path and validate it."""
        self.path_input.setText(path)
        self._validate_input(path)

    def _validate_input(self, path: str) -> None:
        """Validate the input path."""
        self._current_input = AudioInput(path)

        if self._current_input.is_valid:
            self._show_valid_input()
            self.file_selected.emit(path)
            self.validation_changed.emit(True, "")
        else:
            self._show_invalid_input()
            self.validation_changed.emit(
                False, self._current_input.error_message or "Invalid input"
            )

    def _show_valid_input(self) -> None:
        """Show valid input state."""
        self.validation_label.hide()

        input_type = self._current_input.input_type.value.replace("_", " ").title()
        display_name = self._current_input.display_name

        # Special handling for Spotify URLs
        if self._current_input.input_type.value == "spotify_url":
            track_info = self._current_input.get_spotify_preview_info()
            if track_info:
                track_name, artist = track_info
                info_text = f"✓ Spotify Track: {track_name} by {artist}"
                drop_text = f"🎵  {track_name}\n<small><font color='{Theme.SUCCESS}'>by {artist}</font></small>"
            else:
                info_text = f"✓ Valid {input_type}"
                drop_text = "🎵 Spotify Track"
        else:
            info_text = f"✓ Valid {input_type}: {display_name}"
            drop_text = f"✓  {display_name}"

        self.info_label.setText(info_text)
        self.info_label.show()

        self.drop_label.setText(drop_text)
        # Valid input state with card appearance and left border accent
        # Maintain minimum height to prevent layout shift
        self.drop_label.setStyleSheet(
            f"""
            QLabel {{
                border: 1px solid {Theme.BORDER_LIGHT};
                border-left: 4px solid {Theme.SUCCESS};
                border-radius: 10px;
                background-color: {Theme.SUCCESS_LIGHT};
                color: {Theme.SUCCESS};
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                padding: {Theme.SPACING_LG}px;
                min-height: 180px;
            }}
            """
        )

    def _show_invalid_input(self) -> None:
        """Show invalid input state."""
        self.info_label.hide()
        self.validation_label.setText(
            f"✗ {self._current_input.error_message or 'Invalid input'}"
        )
        self.validation_label.show()
        self._reset_drop_label_style()
        self.drop_label.setText(
            "📁\n\nDrag and drop an audio file here\n"
            f"<small><font color='{Theme.TEXT_TERTIARY}'>or paste a Spotify URL</font></small>"
        )

    def _clear_validation(self) -> None:
        """Clear validation state."""
        self.validation_label.hide()
        self.info_label.hide()
        self._reset_drop_label_style()
        self.drop_label.setText(
            "📁\n\nDrag and drop an audio file here\n"
            f"<small><font color='{Theme.TEXT_TERTIARY}'>or paste a Spotify URL</font></small>"
        )
        self._current_input = None

    def get_path(self) -> str:
        """Get the current file path."""
        return self.path_input.text().strip()

    def get_audio_input(self) -> AudioInput | None:
        """Get the validated AudioInput object."""
        return self._current_input

    def is_valid(self) -> bool:
        """Check if current input is valid."""
        return self._current_input is not None and self._current_input.is_valid

    def clear(self) -> None:
        """Clear the input field."""
        self.path_input.clear()
        self._clear_validation()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the widget."""
        self.path_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.setAcceptDrops(enabled)
