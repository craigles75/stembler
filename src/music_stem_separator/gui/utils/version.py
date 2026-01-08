"""Version utility for retrieving application version."""

import tomllib
from pathlib import Path
from typing import Optional


def get_version() -> str:
    """Get application version from pyproject.toml.

    Returns:
        Version string (e.g., "0.1.0"), or "unknown" if not found
    """
    try:
        # Find pyproject.toml (go up from this file to project root)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return "unknown"

        # Parse pyproject.toml
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        # Get version from [project] section
        version = pyproject_data.get("project", {}).get("version", "unknown")
        return version

    except Exception:
        return "unknown"


def get_app_name() -> str:
    """Get application name from pyproject.toml.

    Returns:
        Application name string
    """
    try:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return "Stembler"

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        return pyproject_data.get("project", {}).get("name", "Stembler")

    except Exception:
        return "Stembler"


def get_description() -> str:
    """Get application description from pyproject.toml.

    Returns:
        Description string
    """
    try:
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if not pyproject_path.exists():
            return "Music Stem Separator"

        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)

        return pyproject_data.get("project", {}).get("description", "Music Stem Separator")

    except Exception:
        return "Music Stem Separator"
