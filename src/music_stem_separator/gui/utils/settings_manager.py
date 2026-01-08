"""Settings manager for persisting user settings to JSON file."""

import json
from pathlib import Path
from typing import Optional

from ..models.user_settings import UserSettings


class JSONSettingsManager:
    """Manages loading and saving UserSettings to a JSON file."""

    def __init__(self, settings_file: Optional[Path] = None):
        """Initialize settings manager.

        Args:
            settings_file: Path to settings JSON file. If None, uses platform-specific default.
        """
        if settings_file:
            self.settings_file = settings_file
        else:
            self.settings_file = self._get_default_settings_path()

        # Ensure settings directory exists
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

    def _get_default_settings_path(self) -> Path:
        """Get platform-specific settings file path."""
        try:
            from platformdirs import user_config_path

            config_dir = Path(user_config_path("Stembler", appauthor=False))
        except Exception:
            # Fallback to home directory
            config_dir = Path.home() / ".stembler"

        return config_dir / "settings.json"

    def load(self) -> UserSettings:
        """Load settings from JSON file.

        Returns:
            UserSettings object (default settings if file doesn't exist)
        """
        if not self.settings_file.exists():
            # First run - return default settings
            return UserSettings.get_default()

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserSettings.from_dict(data)
        except (json.JSONDecodeError, OSError, KeyError) as e:
            # If settings file is corrupted, log error and return defaults
            print(f"Warning: Failed to load settings from {self.settings_file}: {e}")
            print("Using default settings instead.")
            return UserSettings.get_default()

    def save(self, settings: UserSettings) -> bool:
        """Save settings to JSON file.

        Args:
            settings: UserSettings object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)

            # Write settings to file with pretty formatting
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings.to_dict(), f, indent=2, ensure_ascii=False)

            return True
        except (OSError, TypeError) as e:
            print(f"Error: Failed to save settings to {self.settings_file}: {e}")
            return False

    def reset_to_defaults(self) -> UserSettings:
        """Reset settings to defaults and save.

        Returns:
            Default UserSettings object
        """
        default_settings = UserSettings.get_default()
        self.save(default_settings)
        return default_settings

    def get_settings_file_path(self) -> Path:
        """Get the path to the settings file.

        Returns:
            Path to settings JSON file
        """
        return self.settings_file

    def settings_exist(self) -> bool:
        """Check if settings file exists.

        Returns:
            True if settings file exists, False otherwise
        """
        return self.settings_file.exists()
