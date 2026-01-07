"""Data model for audio input validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from enum import Enum


class InputType(Enum):
    """Type of audio input."""

    LOCAL_FILE = "local_file"
    SPOTIFY_URL = "spotify_url"
    DIRECT_URL = "direct_url"
    INVALID = "invalid"


@dataclass
class AudioInput:
    """Represents and validates an audio input."""

    path: str
    input_type: InputType = InputType.INVALID
    error_message: Optional[str] = None

    # Supported audio formats
    SUPPORTED_AUDIO_FORMATS = {
        ".mp3",
        ".wav",
        ".flac",
        ".ogg",
        ".m4a",
        ".aac",
        ".wma",
    }

    def __post_init__(self):
        """Validate input after initialization."""
        self.input_type, self.error_message = self._determine_input_type()

    def _determine_input_type(self) -> tuple[InputType, Optional[str]]:
        """Determine the type of input and validate it."""
        if not self.path or not self.path.strip():
            return InputType.INVALID, "Input path is empty"

        path_str = self.path.strip()

        # Check for Spotify URL
        if self._is_spotify_url(path_str):
            return InputType.SPOTIFY_URL, None

        # Check for direct URL
        if self._is_direct_url(path_str):
            return InputType.DIRECT_URL, None

        # Check for local file
        return self._validate_local_file(path_str)

    def _is_spotify_url(self, path: str) -> bool:
        """Check if input is a Spotify URL."""
        spotify_patterns = [
            "open.spotify.com/track/",
            "spotify:track:",
        ]
        return any(pattern in path for pattern in spotify_patterns)

    def _is_direct_url(self, path: str) -> bool:
        """Check if input is a direct URL to an audio file."""
        url_prefixes = ["http://", "https://"]
        if not any(path.startswith(prefix) for prefix in url_prefixes):
            return False

        # Check if URL ends with a supported audio format
        path_lower = path.lower()
        return any(path_lower.endswith(ext) for ext in self.SUPPORTED_AUDIO_FORMATS)

    def _validate_local_file(self, path: str) -> tuple[InputType, Optional[str]]:
        """Validate a local file path."""
        file_path = Path(path)

        # Check if file exists
        if not file_path.exists():
            return InputType.INVALID, f"File does not exist: {path}"

        # Check if it's a file (not a directory)
        if not file_path.is_file():
            return InputType.INVALID, f"Path is not a file: {path}"

        # Check file extension
        if file_path.suffix.lower() not in self.SUPPORTED_AUDIO_FORMATS:
            supported = ", ".join(sorted(self.SUPPORTED_AUDIO_FORMATS))
            return (
                InputType.INVALID,
                f"Unsupported file format: {file_path.suffix}. "
                f"Supported formats: {supported}",
            )

        return InputType.LOCAL_FILE, None

    @property
    def is_valid(self) -> bool:
        """Check if input is valid."""
        return self.input_type != InputType.INVALID

    @property
    def requires_download(self) -> bool:
        """Check if input requires downloading before processing."""
        return self.input_type in (InputType.SPOTIFY_URL, InputType.DIRECT_URL)

    @property
    def display_name(self) -> str:
        """Get a user-friendly display name for the input."""
        if self.input_type == InputType.LOCAL_FILE:
            return Path(self.path).name
        elif self.input_type == InputType.SPOTIFY_URL:
            return "Spotify Track"
        elif self.input_type == InputType.DIRECT_URL:
            return Path(self.path).name or "Remote Audio File"
        else:
            return "Invalid Input"

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported audio formats."""
        return sorted(cls.SUPPORTED_AUDIO_FORMATS)

    @classmethod
    def get_file_filter(cls) -> str:
        """Get file filter string for file dialogs."""
        formats = " ".join(f"*{ext}" for ext in sorted(cls.SUPPORTED_AUDIO_FORMATS))
        return f"Audio Files ({formats})"

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "path": self.path,
            "input_type": self.input_type.value,
            "is_valid": self.is_valid,
            "requires_download": self.requires_download,
            "display_name": self.display_name,
            "error_message": self.error_message,
        }
