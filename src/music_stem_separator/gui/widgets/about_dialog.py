"""About dialog showing application information."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.version import get_version, get_description


class AboutDialog(QDialog):
    """Dialog showing application version, credits, and license information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("About Stembler")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # App name
        name_label = QLabel("Stembler")
        name_font = QFont()
        name_font.setPointSize(24)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Version
        version = get_version()
        version_label = QLabel(f"Version {version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(version_label)

        # Description
        description = get_description()
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("margin: 10px 0; font-size: 13px;")
        layout.addWidget(desc_label)

        # Separator
        separator = QLabel()
        separator.setFrameStyle(QLabel.Shape.HLine | QLabel.Shadow.Sunken)
        separator.setStyleSheet("margin: 10px 0;")
        layout.addWidget(separator)

        # Credits
        credits_label = QLabel("<b>Credits</b>")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(credits_label)

        credits_text = QLabel(
            "• Built with PyQt6 for cross-platform GUI<br>"
            "• Powered by Demucs AI models for stem separation<br>"
            "• Uses spotdl for Spotify track downloads<br>"
            "• Music processing with librosa and PyTorch"
        )
        credits_text.setWordWrap(True)
        credits_text.setStyleSheet("font-size: 12px; margin-left: 20px;")
        layout.addWidget(credits_text)

        # License
        license_label = QLabel("<b>License</b>")
        license_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        license_label.setStyleSheet("margin-top: 15px;")
        layout.addWidget(license_label)

        license_text = QLabel(
            "This software is provided as-is for educational and personal use."
        )
        license_text.setWordWrap(True)
        license_text.setStyleSheet("font-size: 12px; margin-left: 20px;")
        layout.addWidget(license_text)

        # Links
        links_label = QLabel("<b>Links</b>")
        links_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        links_label.setStyleSheet("margin-top: 15px;")
        layout.addWidget(links_label)

        links_text = QLabel(
            '• Demucs: <a href="https://github.com/facebookresearch/demucs">github.com/facebookresearch/demucs</a><br>'
            '• spotdl: <a href="https://github.com/spotDL/spotify-downloader">github.com/spotDL/spotify-downloader</a>'
        )
        links_text.setOpenExternalLinks(True)
        links_text.setWordWrap(True)
        links_text.setStyleSheet("font-size: 12px; margin-left: 20px;")
        layout.addWidget(links_text)

        layout.addStretch()

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
