"""
Launcher script for Stembler macOS application.

This script uses absolute imports instead of relative imports,
making it compatible with PyInstaller as an entry point.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from music_stem_separator.gui.main_window import MainWindow
from music_stem_separator.gui.utils.error_handler import install_error_handler


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Stembler")
    app.setOrganizationName("Stembler")
    app.setApplicationDisplayName("Music Stem Separator")

    # Install global error handler
    install_error_handler()

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
