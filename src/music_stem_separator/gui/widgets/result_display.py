"""Result display widget showing processing outcome."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSizePolicy,
    QStyle,
)
from PyQt6.QtCore import pyqtSignal

from ..models import OutputBundle
from ..utils.theme import Theme


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
        layout.setContentsMargins(0, 0, 0, 0)  # No margins - spacing handled by parent
        layout.setSpacing(Theme.SPACING_SM)

        # Result container frame - card design
        self.result_frame = QFrame()
        self.result_frame.setObjectName("result_frame")
        self.result_frame.setFrameShape(QFrame.Shape.NoFrame)
        self.result_frame.setStyleSheet(
            f"""
            QFrame#result_frame {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_LG}px;
            }}
            """
        )

        frame_layout = QVBoxLayout(self.result_frame)
        frame_layout.setSpacing(Theme.SPACING_MD)

        # Icon + Title row
        header_layout = QHBoxLayout()

        # Icon label (will be set based on success/error)
        self.icon_label = QLabel("")
        self.icon_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.ICON_SIZE_XL}px;
            }}
            """
        )
        header_layout.addWidget(self.icon_label)

        # Title label
        self.title_label = QLabel("")
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_LG}px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        frame_layout.addLayout(header_layout)

        # Details label
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin-top: {Theme.SPACING_SM}px;
            }}
            """
        )
        frame_layout.addWidget(self.details_label)

        # Button row
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Open folder button with icon
        self.open_folder_button = QPushButton("  Open Output Folder")
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        self.open_folder_button.setIcon(folder_icon)
        self.open_folder_button.clicked.connect(self._on_open_folder_clicked)
        self.open_folder_button.setStyleSheet(
            Theme.button_style(
                Theme.SECONDARY,
                Theme.SECONDARY_HOVER,
                Theme.SECONDARY_PRESSED,
                height=40,
            )
        )
        button_layout.addWidget(self.open_folder_button)

        frame_layout.addLayout(button_layout)

        layout.addWidget(self.result_frame)

    def show_success(self, output_bundle: OutputBundle) -> None:
        """Show successful processing result."""
        self._output_bundle = output_bundle

        # Large checkmark icon
        self.icon_label.setText("✅")
        self.icon_label.show()

        self.title_label.setText("Stem Separation Complete!")
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_LG}px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.SUCCESS};
            }}
            """
        )

        # Build details text
        details = []
        details.append(f"📂 Location: {output_bundle.track_directory.name}")
        details.append(f"🎵 Stems separated: {output_bundle.stem_count}")

        if output_bundle.stem_names:
            stems_list = ", ".join(output_bundle.stem_names)
            details.append(f"📄 Files: {stems_list}")

        details.append(f"💾 Total size: {output_bundle.total_size_mb:.1f} MB")

        if output_bundle.processing_time_seconds:
            minutes = int(output_bundle.processing_time_seconds // 60)
            seconds = int(output_bundle.processing_time_seconds % 60)
            details.append(f"⏱️ Processing time: {minutes}m {seconds}s")

        self.details_label.setText("\n".join(details))
        self.open_folder_button.show()

        # Add subtle green accent background
        self.result_frame.setStyleSheet(
            f"""
            QFrame#result_frame {{
                background-color: {Theme.SUCCESS_LIGHT};
                border: 1px solid {Theme.SUCCESS};
                border-left: 4px solid {Theme.SUCCESS};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_LG}px;
            }}
            """
        )

        self.show()

    def show_error(self, error_message: str) -> None:
        """Show processing error."""
        self._output_bundle = None

        # Large error icon
        self.icon_label.setText("❌")
        self.icon_label.show()

        self.title_label.setText("Processing Failed")
        self.title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_LG}px;
                font-weight: {Theme.FONT_WEIGHT_BOLD};
                color: {Theme.ERROR};
            }}
            """
        )

        self.details_label.setText(f"{error_message}\n\n💡 Tip: Check the log file for more details")
        self.open_folder_button.hide()

        # Add subtle red accent background
        self.result_frame.setStyleSheet(
            f"""
            QFrame#result_frame {{
                background-color: {Theme.ERROR_LIGHT};
                border: 1px solid {Theme.ERROR};
                border-left: 4px solid {Theme.ERROR};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_LG}px;
            }}
            """
        )

        self.show()

    def clear(self) -> None:
        """Clear the result display."""
        self._output_bundle = None
        self.icon_label.setText("")
        self.icon_label.hide()
        self.title_label.setText("")
        self.details_label.setText("")
        self.open_folder_button.show()

        # Reset to default frame styling
        self.result_frame.setStyleSheet(
            f"""
            QFrame#result_frame {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: {Theme.RADIUS_LG}px;
                padding: {Theme.SPACING_LG}px;
            }}
            """
        )

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
