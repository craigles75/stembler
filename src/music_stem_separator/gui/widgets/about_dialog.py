"""About dialog showing application information."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.version import get_version, get_description
from ..utils.theme import Theme


class AboutDialog(QDialog):
    """Dialog showing application version, credits, and license information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("About Stembler")
        self.setMinimumWidth(550)
        self.setModal(True)

        # Apply dialog background
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {Theme.BACKGROUND_PRIMARY};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_LG)
        layout.setContentsMargins(40, 40, 40, 40)

        # App icon + Name
        icon_name_layout = QHBoxLayout()
        icon_name_layout.addStretch()

        # Music note emoji as app icon
        icon_label = QLabel("🎵")
        icon_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.ICON_SIZE_XL}px;
                margin-right: {Theme.SPACING_SM}px;
            }}
            """
        )
        icon_name_layout.addWidget(icon_label)

        # App name with larger font
        name_label = QLabel("Stembler")
        name_font = QFont()
        name_font.setPointSize(32)  # Increased from 24px
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY};")
        icon_name_layout.addWidget(name_label)

        icon_name_layout.addStretch()
        layout.addLayout(icon_name_layout)

        # Version
        version = get_version()
        version_label = QLabel(f"Version {version}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
            """
        )
        layout.addWidget(version_label)

        # Description
        description = get_description()
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin: {Theme.SPACING_MD}px 0;
            }}
            """
        )
        layout.addWidget(desc_label)

        # Separator
        separator = QLabel()
        separator.setFrameStyle(QLabel.Shape.HLine | QLabel.Shadow.Sunken)
        separator.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.BORDER_LIGHT};
                margin: {Theme.SPACING_MD}px 0;
            }}
            """
        )
        layout.addWidget(separator)

        # Credits
        credits_label = QLabel("<b>Credits</b>")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        credits_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        layout.addWidget(credits_label)

        credits_text = QLabel(
            "• Built with PyQt6 for cross-platform GUI<br>"
            "• Powered by Demucs AI models for stem separation<br>"
            "• Uses spotdl for Spotify track downloads<br>"
            "• Music processing with librosa and PyTorch"
        )
        credits_text.setWordWrap(True)
        credits_text.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin-left: {Theme.SPACING_LG}px;
            }}
            """
        )
        layout.addWidget(credits_text)

        # License
        license_label = QLabel("<b>License</b>")
        license_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        license_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
                margin-top: {Theme.SPACING_MD}px;
            }}
            """
        )
        layout.addWidget(license_label)

        license_text = QLabel(
            "This software is provided as-is for educational and personal use."
        )
        license_text.setWordWrap(True)
        license_text.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin-left: {Theme.SPACING_LG}px;
            }}
            """
        )
        layout.addWidget(license_text)

        # Links with external link icons
        links_label = QLabel("<b>Links</b>")
        links_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        links_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TEXT_PRIMARY};
                margin-top: {Theme.SPACING_MD}px;
            }}
            """
        )
        layout.addWidget(links_label)

        links_text = QLabel(
            f'• 🔗 Demucs: <a href="https://github.com/facebookresearch/demucs" style="color: {Theme.PRIMARY};">github.com/facebookresearch/demucs</a><br>'
            f'• 🔗 spotdl: <a href="https://github.com/spotDL/spotify-downloader" style="color: {Theme.PRIMARY};">github.com/spotDL/spotify-downloader</a>'
        )
        links_text.setOpenExternalLinks(True)
        links_text.setWordWrap(True)
        links_text.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_SM}px;
                margin-left: {Theme.SPACING_LG}px;
            }}
            """
        )
        layout.addWidget(links_text)

        layout.addStretch()

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
