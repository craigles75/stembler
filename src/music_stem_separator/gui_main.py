"""Entry point for the GUI application."""

import sys
from PyQt6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Stembler")
    app.setOrganizationName("Stembler")
    app.setApplicationDisplayName("Music Stem Separator")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
