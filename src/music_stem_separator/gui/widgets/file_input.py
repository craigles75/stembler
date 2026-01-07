"""File input widget with drag-and-drop support."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from ..models import AudioInput


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

        # Drag-drop area
        self.drop_label = QLabel("Drag and drop an audio file here")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setMinimumHeight(150)
        self.drop_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 14px;
                padding: 20px;
            }
            QLabel:hover {
                border-color: #666;
                background-color: #f0f0f0;
            }
            """
        )
        layout.addWidget(self.drop_label)

        # OR separator
        separator_label = QLabel("— OR —")
        separator_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator_label.setStyleSheet("color: #999; margin: 10px 0;")
        layout.addWidget(separator_label)

        # File path input row
        input_layout = QHBoxLayout()

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter file path or URL...")
        self.path_input.textChanged.connect(self._on_path_changed)
        input_layout.addWidget(self.path_input, stretch=1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        input_layout.addWidget(self.browse_button)

        layout.addLayout(input_layout)

        # Validation message label
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: #c00; margin-top: 5px;")
        self.validation_label.hide()
        layout.addWidget(self.validation_label)

        # File info label (shows when valid)
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #060; margin-top: 5px;")
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
            self.drop_label.setStyleSheet(
                """
                QLabel {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    background-color: #e8f5e9;
                    color: #2e7d32;
                    font-size: 14px;
                    padding: 20px;
                }
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
            """
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 14px;
                padding: 20px;
            }
            QLabel:hover {
                border-color: #666;
                background-color: #f0f0f0;
            }
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

        self.info_label.setText(f"✓ Valid {input_type}: {display_name}")
        self.info_label.show()

        self.drop_label.setText(f"Selected: {display_name}")
        self.drop_label.setStyleSheet(
            """
            QLabel {
                border: 2px solid #4CAF50;
                border-radius: 8px;
                background-color: #e8f5e9;
                color: #2e7d32;
                font-size: 14px;
                padding: 20px;
            }
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
        self.drop_label.setText("Drag and drop an audio file here")

    def _clear_validation(self) -> None:
        """Clear validation state."""
        self.validation_label.hide()
        self.info_label.hide()
        self._reset_drop_label_style()
        self.drop_label.setText("Drag and drop an audio file here")
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
