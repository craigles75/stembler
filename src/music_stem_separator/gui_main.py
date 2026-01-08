"""Entry point for the GUI application."""

import sys
from PyQt6.QtWidgets import QApplication

from .gui.main_window import MainWindow
from .gui.utils.error_handler import install_error_handler


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Stembler")
    app.setOrganizationName("Stembler")
    app.setApplicationDisplayName("Music Stem Separator")

    # Create and show main window
    window = MainWindow()

    # Install global error handler (with main window as parent for dialogs)
    install_error_handler(parent=window)

    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
