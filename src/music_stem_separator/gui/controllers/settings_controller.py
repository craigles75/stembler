"""Controller for managing application settings."""

import os
from pathlib import Path
from typing import Optional

from ..models.user_settings import UserSettings
from ..utils.settings_manager import JSONSettingsManager


class SettingsController:
    """Controller for loading, saving, and applying user settings."""

    def __init__(self, settings_file: Optional[Path] = None):
        """Initialize settings controller.

        Args:
            settings_file: Path to settings JSON file. If None, uses platform-specific default.
        """
        self._settings_manager = JSONSettingsManager(settings_file)
        self._current_settings: Optional[UserSettings] = None

    def load_settings(self) -> UserSettings:
        """Load settings from file.

        If settings file doesn't exist (first run), default settings are returned.

        Returns:
            UserSettings object
        """
        self._current_settings = self._settings_manager.load()

        # Apply Spotify credentials to environment if present
        self._apply_spotify_credentials_to_env()

        return self._current_settings

    def save_settings(self, settings: UserSettings) -> bool:
        """Save settings to file.

        Args:
            settings: UserSettings object to save

        Returns:
            True if successful, False otherwise
        """
        success = self._settings_manager.save(settings)
        if success:
            self._current_settings = settings
            # Apply Spotify credentials to environment
            self._apply_spotify_credentials_to_env()

        return success

    def get_current_settings(self) -> UserSettings:
        """Get current settings.

        Returns:
            Current UserSettings object (loads from file if not loaded yet)
        """
        if self._current_settings is None:
            return self.load_settings()
        return self._current_settings

    def reset_to_defaults(self) -> UserSettings:
        """Reset settings to defaults and save.

        Returns:
            Default UserSettings object
        """
        self._current_settings = self._settings_manager.reset_to_defaults()
        # Clear Spotify credentials from environment
        self._apply_spotify_credentials_to_env()
        return self._current_settings

    def is_first_run(self) -> bool:
        """Check if this is the first run (settings file doesn't exist).

        Returns:
            True if first run, False otherwise
        """
        return not self._settings_manager.settings_exist()

    def get_settings_file_path(self) -> Path:
        """Get path to settings file.

        Returns:
            Path to settings JSON file
        """
        return self._settings_manager.get_settings_file_path()

    def _apply_spotify_credentials_to_env(self) -> None:
        """Apply Spotify credentials from settings to environment variables.

        This allows the underlying spotdl library to use the credentials.
        """
        if self._current_settings is None:
            return

        # Set or clear SPOTIFY_CLIENT_ID
        if self._current_settings.spotify_client_id:
            os.environ["SPOTIFY_CLIENT_ID"] = self._current_settings.spotify_client_id
        elif "SPOTIFY_CLIENT_ID" in os.environ:
            del os.environ["SPOTIFY_CLIENT_ID"]

        # Set or clear SPOTIFY_CLIENT_SECRET
        if self._current_settings.spotify_client_secret:
            os.environ["SPOTIFY_CLIENT_SECRET"] = (
                self._current_settings.spotify_client_secret
            )
        elif "SPOTIFY_CLIENT_SECRET" in os.environ:
            del os.environ["SPOTIFY_CLIENT_SECRET"]

    def get_output_directory(self) -> Path:
        """Get the output directory from current settings.

        Returns:
            Path to output directory
        """
        if self._current_settings is None:
            self.load_settings()

        return self._current_settings.get_output_directory()

    def get_model_name(self) -> str:
        """Get the model name from current settings.

        Returns:
            Model name string
        """
        if self._current_settings is None:
            self.load_settings()

        return self._current_settings.model_name

    def get_enhancement_enabled(self) -> bool:
        """Get enhancement setting from current settings.

        Returns:
            True if enhancement is enabled
        """
        if self._current_settings is None:
            self.load_settings()

        return self._current_settings.enable_enhancement

    def get_device(self) -> Optional[str]:
        """Get device setting from current settings.

        Returns:
            Device string (e.g., 'cuda', 'cpu') or None for auto-detect
        """
        if self._current_settings is None:
            self.load_settings()

        return self._current_settings.device
