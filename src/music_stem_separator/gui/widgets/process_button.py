"""Process button widget for initiating stem separation."""

from PyQt6.QtWidgets import QPushButton, QStyle
from PyQt6.QtCore import pyqtSignal

from ..utils.theme import Theme


class ProcessButton(QPushButton):
    """Button widget for starting/stopping processing."""

    # Signal emitted when user clicks to start processing
    process_requested = pyqtSignal()

    # Signal emitted when user clicks to cancel processing
    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Separate Stems", parent)
        self._is_processing = False
        self._is_enabled_for_processing = False

        self.clicked.connect(self._on_clicked)
        self.setMinimumHeight(Theme.BUTTON_HEIGHT_LG)  # 48px
        self._update_appearance()

    def _on_clicked(self) -> None:
        """Handle button click."""
        if self._is_processing:
            self.cancel_requested.emit()
        else:
            self.process_requested.emit()

    def set_ready_to_process(self, ready: bool) -> None:
        """Set whether the button is ready to start processing."""
        self._is_enabled_for_processing = ready
        self._update_appearance()

    def set_processing(self, processing: bool) -> None:
        """Set processing state."""
        self._is_processing = processing
        self._update_appearance()

    def _update_appearance(self) -> None:
        """Update button appearance based on state."""
        if self._is_processing:
            # Cancel state - red button with stop icon
            self.setText("  Cancel")
            cancel_icon = self.style().standardIcon(
                QStyle.StandardPixmap.SP_BrowserStop
            )
            self.setIcon(cancel_icon)
            self.setEnabled(True)
            self.setStyleSheet(
                Theme.button_style(
                    Theme.ERROR,
                    "#D32F2F",  # Darker red on hover
                    "#B71C1C",  # Even darker on press
                )
            )
        elif self._is_enabled_for_processing:
            # Ready state - Spotify green button with play icon
            self.setText("  Separate Stems")
            play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            self.setIcon(play_icon)
            self.setEnabled(True)
            self.setStyleSheet(
                Theme.button_style(
                    Theme.PRIMARY,
                    Theme.PRIMARY_HOVER,
                    Theme.PRIMARY_PRESSED,
                )
            )
        else:
            # Disabled state - no icon
            self.setText("Separate Stems")
            self.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_CustomBase)
            )  # Empty icon
            self.setEnabled(False)
            self.setStyleSheet(
                Theme.button_style(
                    Theme.BORDER_LIGHT,
                    Theme.BORDER_LIGHT,
                    Theme.BORDER_LIGHT,
                    text_color=Theme.TEXT_DISABLED,
                )
            )
