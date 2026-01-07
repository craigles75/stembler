"""Process button widget for initiating stem separation."""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import pyqtSignal


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
        self.setMinimumHeight(40)
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
            self.setText("Cancel")
            self.setEnabled(True)
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #d32f2f;
                }
                QPushButton:pressed {
                    background-color: #b71c1c;
                }
                """
            )
        elif self._is_enabled_for_processing:
            self.setText("Separate Stems")
            self.setEnabled(True)
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
                """
            )
        else:
            self.setText("Separate Stems")
            self.setEnabled(False)
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #ccc;
                    color: #666;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 10px;
                }
                """
            )
