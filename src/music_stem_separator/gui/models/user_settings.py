"""User settings model for GUI application."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class UserSettings:
    """User-configurable settings for the GUI application."""

    # Processing settings
    model_name: str = "htdemucs"
    enable_enhancement: bool = True
    output_directory: str = ""  # Empty means use default (Music/Stembler Output)
    device: Optional[str] = None  # None means auto-detect (GPU if available, else CPU)

    # Spotify credentials
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    @property
    def has_spotify_credentials(self) -> bool:
        """Check if Spotify credentials are configured."""
        return bool(
            self.spotify_client_id.strip() and self.spotify_client_secret.strip()
        )

    def get_output_directory(self) -> Path:
        """Get the output directory path, using default if not set."""
        if self.output_directory:
            return Path(self.output_directory)

        # Default to Music/Stembler Output
        try:
            from platformdirs import user_music_path

            music_dir = Path(user_music_path())
        except Exception:
            music_dir = Path.home()

        return music_dir / "Stembler Output"

    def to_dict(self) -> dict:
        """Convert settings to dictionary for JSON serialization."""
        return {
            "model_name": self.model_name,
            "enable_enhancement": self.enable_enhancement,
            "output_directory": self.output_directory,
            "device": self.device,
            "spotify_client_id": self.spotify_client_id,
            "spotify_client_secret": self.spotify_client_secret,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserSettings":
        """Create UserSettings from dictionary (JSON deserialization)."""
        return cls(
            model_name=data.get("model_name", "htdemucs"),
            enable_enhancement=data.get("enable_enhancement", True),
            output_directory=data.get("output_directory", ""),
            device=data.get("device"),
            spotify_client_id=data.get("spotify_client_id", ""),
            spotify_client_secret=data.get("spotify_client_secret", ""),
        )

    @classmethod
    def get_default(cls) -> "UserSettings":
        """Get default settings for first run."""
        return cls()

    @classmethod
    def get_available_models(cls) -> list[tuple[str, str]]:
        """Get list of available models with descriptions.

        Returns:
            List of (model_id, description) tuples
        """
        return [
            ("htdemucs", "HTDemucs - Balanced quality and speed (default)"),
            ("htdemucs_ft", "HTDemucs Fine-Tuned - Highest quality, slower"),
            ("mdx_extra", "MDX Extra - Alternative high quality"),
            ("mdx_q", "MDX Quantized - Fastest, lower quality"),
        ]

    def get_model_description(self) -> str:
        """Get description for the current model."""
        models = dict(self.get_available_models())
        return models.get(self.model_name, "Unknown model")
