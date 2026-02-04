"""Cross-platform utility functions."""

import sys
import subprocess
from pathlib import Path


def open_folder(folder_path: str | Path) -> bool:
    """
    Open a folder in the system file manager.

    Args:
        folder_path: Path to the folder to open

    Returns:
        True if successful, False otherwise
    """
    folder = Path(folder_path)

    if not folder.exists():
        return False

    if not folder.is_dir():
        return False

    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", str(folder)], check=True)
        elif sys.platform == "win32":  # Windows
            subprocess.run(["explorer", str(folder)], check=True)
        else:  # Linux/Unix
            subprocess.run(["xdg-open", str(folder)], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_platform_name() -> str:
    """
    Get a human-readable platform name.

    Returns:
        Platform name string
    """
    if sys.platform == "darwin":
        return "macOS"
    elif sys.platform == "win32":
        return "Windows"
    elif sys.platform.startswith("linux"):
        return "Linux"
    else:
        return sys.platform


def get_default_output_directory() -> Path:
    """
    Get the default output directory for the platform.

    Returns:
        Path to default output directory
    """
    try:
        from platformdirs import user_music_path

        music_dir = Path(user_music_path())
    except Exception:
        # Fallback to home directory
        music_dir = Path.home()

    output_dir = music_dir / "Stembler Output"
    return output_dir


def ensure_directory_exists(directory: str | Path) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory: Path to directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False
