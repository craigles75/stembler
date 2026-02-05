"""Entry point for the GUI application."""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .gui.main_window import MainWindow
from .gui.utils.error_handler import install_error_handler


def _get_icon_path() -> Path:
    """Resolve icon path for both source and PyInstaller environments."""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # noqa: SLF001
    else:
        base = Path(__file__).parent
    return base / "gui" / "resources" / "icon.png"


def main():
    """Main entry point for the GUI application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("Stembler")
    app.setOrganizationName("Stembler")
    app.setApplicationDisplayName("Music Stem Separator")

    # Set application icon
    icon_path = _get_icon_path()
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # Create and show main window
    window = MainWindow()

    # Install global error handler (with main window as parent for dialogs)
    install_error_handler(parent=window)

    window.show()

    # Run application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
