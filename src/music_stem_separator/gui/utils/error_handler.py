"""Global error handler for GUI application."""

import sys
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import QMessageBox, QWidget


class ErrorHandler:
    """Handles uncaught exceptions and provides user-friendly error reporting."""

    def __init__(self, log_file: Optional[Path] = None):
        """Initialize error handler.

        Args:
            log_file: Path to log file. If None, uses platform-specific default.
        """
        self.log_file = log_file or self._get_default_log_path()
        self._setup_logging()

    def _get_default_log_path(self) -> Path:
        """Get platform-specific log file path."""
        try:
            from platformdirs import user_log_path

            log_dir = Path(user_log_path("Stembler", appauthor=False))
        except Exception:
            # Fallback to home directory
            log_dir = Path.home() / ".stembler" / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"stembler_{timestamp}.log"

        return log_file

    def _setup_logging(self) -> None:
        """Set up file logging."""
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout),
            ],
        )

        logging.info(f"Logging initialized. Log file: {self.log_file}")

    def handle_exception(
        self, exc_type, exc_value, exc_traceback, parent: Optional[QWidget] = None
    ) -> None:
        """Handle uncaught exception.

        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
            parent: Parent widget for error dialog
        """
        # Ignore KeyboardInterrupt (Ctrl+C)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Log the full exception
        error_msg = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )
        logging.error(f"Uncaught exception:\n{error_msg}")

        # Show user-friendly error dialog
        self.show_error_dialog(exc_value, exc_type.__name__, parent)

    def show_error_dialog(
        self,
        exception: Exception,
        error_type: str = "Error",
        parent: Optional[QWidget] = None,
    ) -> None:
        """Show user-friendly error dialog.

        Args:
            exception: The exception that occurred
            error_type: Type of error (for title)
            parent: Parent widget for dialog
        """
        # Create user-friendly error message
        user_message = self._get_user_friendly_message(exception)

        # Create detailed technical message for "Show Details"
        technical_details = f"{error_type}: {str(exception)}\n\n"
        technical_details += f"Log file: {self.log_file}\n\n"
        technical_details += "Please check the log file for full details."

        # Show error dialog
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("An Error Occurred")
        msg_box.setText(user_message)
        msg_box.setInformativeText(
            "The error has been logged. If the problem persists, "
            "please report this issue with the log file."
        )
        msg_box.setDetailedText(technical_details)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _get_user_friendly_message(self, exception: Exception) -> str:
        """Convert technical exception to user-friendly message.

        Args:
            exception: The exception to convert

        Returns:
            User-friendly error message
        """
        error_str = str(exception).lower()

        # File/path errors
        if isinstance(exception, FileNotFoundError):
            return (
                "A required file could not be found.\n\n"
                "Please check that all necessary files are present and try again."
            )

        if isinstance(exception, PermissionError):
            return (
                "Permission denied when accessing a file or directory.\n\n"
                "Please check file permissions and try again."
            )

        # Network errors
        if "connection" in error_str or "network" in error_str:
            return (
                "A network connection error occurred.\n\n"
                "Please check your internet connection and try again."
            )

        # Spotify errors
        if "spotify" in error_str:
            if "credentials" in error_str or "client_id" in error_str:
                return (
                    "Spotify credentials are invalid or missing.\n\n"
                    "Please check your Spotify API credentials in Settings."
                )
            return (
                "An error occurred while downloading from Spotify.\n\n"
                "Please try again or use a different track."
            )

        # Memory errors
        if isinstance(exception, MemoryError) or "memory" in error_str:
            return (
                "The application ran out of memory.\n\n"
                "Please close other applications and try processing a smaller file."
            )

        # GPU/CUDA errors
        if "cuda" in error_str or "gpu" in error_str:
            return (
                "A GPU processing error occurred.\n\n"
                "The application will try to use CPU instead. Processing may be slower."
            )

        # Model errors
        if "model" in error_str or "demucs" in error_str:
            return (
                "An error occurred while loading or running the AI model.\n\n"
                "Please try restarting the application or selecting a different model."
            )

        # Generic error with exception type
        exception_name = type(exception).__name__
        return (
            f"An unexpected error occurred: {exception_name}\n\n"
            f"{str(exception)}\n\n"
            "Please try again or report this issue if it persists."
        )

    def install_global_handler(self, parent: Optional[QWidget] = None) -> None:
        """Install this as the global exception handler.

        Args:
            parent: Parent widget for error dialogs
        """

        def exception_hook(exc_type, exc_value, exc_traceback):
            self.handle_exception(exc_type, exc_value, exc_traceback, parent)

        sys.excepthook = exception_hook
        logging.info("Global exception handler installed")


# Singleton instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get or create the global error handler instance.

    Returns:
        ErrorHandler instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def install_error_handler(parent: Optional[QWidget] = None) -> ErrorHandler:
    """Install global error handler.

    Args:
        parent: Parent widget for error dialogs

    Returns:
        ErrorHandler instance
    """
    handler = get_error_handler()
    handler.install_global_handler(parent)
    return handler


def log_error(message: str, exception: Optional[Exception] = None) -> None:
    """Log an error message.

    Args:
        message: Error message to log
        exception: Optional exception to include
    """
    if exception:
        logging.error(f"{message}: {exception}", exc_info=True)
    else:
        logging.error(message)


def log_warning(message: str) -> None:
    """Log a warning message.

    Args:
        message: Warning message to log
    """
    logging.warning(message)


def log_info(message: str) -> None:
    """Log an info message.

    Args:
        message: Info message to log
    """
    logging.info(message)
