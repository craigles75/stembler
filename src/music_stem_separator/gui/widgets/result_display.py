"""Result display widget showing processing outcome."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ..models import OutputBundle


class ResultDisplay(QWidget):
    """Widget to display processing results and provide folder access."""

    # Signal emitted when user clicks to open output folder
    open_folder_requested = pyqtSignal(str)  # folder_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self._output_bundle: OutputBundle | None = None
        self._setup_ui()
        # Set size policy to collapse when hidden
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.hide()  # Hidden by default until there are results

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Result container frame
        self.result_frame = QFrame()
        self.result_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.result_frame.setStyleSheet(
            """
            QFrame {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 15px;
            }
            """
        )

        frame_layout = QVBoxLayout(self.result_frame)

        # Title label
        self.title_label = QLabel("")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        frame_layout.addWidget(self.title_label)

        # Details label
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet("color: #666; margin-top: 5px;")
        frame_layout.addWidget(self.details_label)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self._on_open_folder_clicked)
        self.open_folder_button.setMinimumHeight(35)
        self.open_folder_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
            """
        )
        button_layout.addWidget(self.open_folder_button)

        frame_layout.addLayout(button_layout)

        layout.addWidget(self.result_frame)

    def show_success(self, output_bundle: OutputBundle) -> None:
        """Show successful processing result."""
        self._output_bundle = output_bundle

        self.title_label.setText("✅ Stem Separation Complete!")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2e7d32;")

        # Build details text
        details = []
        details.append(f"Location: {output_bundle.track_directory.name}")
        details.append(f"Stems separated: {output_bundle.stem_count}")

        if output_bundle.stem_names:
            stems_list = ", ".join(output_bundle.stem_names)
            details.append(f"Files: {stems_list}")

        details.append(f"Total size: {output_bundle.total_size_mb:.1f} MB")

        if output_bundle.processing_time_seconds:
            minutes = int(output_bundle.processing_time_seconds // 60)
            seconds = int(output_bundle.processing_time_seconds % 60)
            details.append(f"Processing time: {minutes}m {seconds}s")

        self.details_label.setText("\n".join(details))

        self.show()

    def show_error(self, error_message: str) -> None:
        """Show processing error."""
        self._output_bundle = None

        self.title_label.setText("❌ Processing Failed")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #c62828;")

        self.details_label.setText(error_message)
        self.open_folder_button.hide()

        self.show()

    def clear(self) -> None:
        """Clear the result display."""
        self._output_bundle = None
        self.title_label.setText("")
        self.details_label.setText("")
        self.open_folder_button.show()
        self.hide()

    def _on_open_folder_clicked(self) -> None:
        """Handle open folder button click."""
        if self._output_bundle and self._output_bundle.exists:
            folder_path = str(self._output_bundle.track_directory)
            self.open_folder_requested.emit(folder_path)

            # Also try to open directly
            if not self._output_bundle.open_in_file_manager():
                # If opening failed, show error
                self.details_label.setText(
                    self.details_label.text()
                    + "\n\n⚠️ Could not open folder automatically. "
                    + f"Please navigate to: {folder_path}"
                )
