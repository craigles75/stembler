"""Input validation and routing for local files and Spotify URLs."""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .spotify_handler import SpotifyHandler
from .url_downloader import URLDownloader


logger = logging.getLogger(__name__)


class InputProcessor:
    """Processor for validating and routing different input types."""

    SUPPORTED_FORMATS = [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"]

    def __init__(self):
        """Initialize the input processor."""
        self.spotify_handler = None  # Lazy initialization
        self.url_downloader = None  # Lazy initialization
        logger.info("Initialized InputProcessor")

    def determine_input_type(self, input_path: str) -> str:
        """
        Determine the type of input (local file, Spotify URL, etc.).

        Args:
            input_path: Input string to analyze

        Returns:
            Input type: 'local_file', 'spotify_url', 'audio_url', or 'invalid'
        """
        if not input_path or not isinstance(input_path, str):
            return "invalid"

        cleaned_input = self.clean_input_path(input_path)

        # Check if it's a Spotify URL
        if self._is_spotify_url(cleaned_input):
            return "spotify_url"

        # Check if it's a local file
        if self._is_local_file(cleaned_input):
            return "local_file"

        # Check if it's a URL
        if self._is_url(cleaned_input):
            return "audio_url"

        return "invalid"

    def _is_spotify_url(self, input_str: str) -> bool:
        """Check if input is a Spotify URL."""
        spotify_patterns = [
            r"https://open\.spotify\.com/track/[a-zA-Z0-9]+",
            r"spotify:track:[a-zA-Z0-9]+",
        ]
        return any(re.match(pattern, input_str.strip()) for pattern in spotify_patterns)

    def _is_local_file(self, input_str: str) -> bool:
        """Check if input is a local file path."""
        try:
            path = Path(input_str)
            return path.exists() and path.is_file()
        except (OSError, ValueError):
            return False

    def _is_url(self, input_str: str) -> bool:
        """Check if input is a URL."""
        try:
            from urllib.parse import urlparse

            result = urlparse(input_str)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def validate_local_file(self, file_path: str) -> Dict:
        """
        Validate a local audio file.

        Args:
            file_path: Path to the local file

        Returns:
            Validation result dictionary
        """
        try:
            file_path = self.clean_input_path(file_path)
            path = Path(file_path)

            if not path.exists():
                return {"valid": False, "error": f"File not found: {file_path}"}

            if not path.is_file():
                return {"valid": False, "error": f"Path is not a file: {file_path}"}

            file_format = path.suffix.lower()
            if file_format not in self.SUPPORTED_FORMATS:
                return {
                    "valid": False,
                    "error": f"Unsupported format: {file_format}. Supported: {', '.join(self.SUPPORTED_FORMATS)}",
                }

            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return {"valid": False, "error": f"File is not readable: {file_path}"}

            return {
                "valid": True,
                "file_path": str(path.absolute()),
                "format": file_format,
                "size_bytes": path.stat().st_size,
            }

        except Exception as e:
            return {"valid": False, "error": f"Validation error: {str(e)}"}

    def validate_spotify_url(self, url: str) -> Dict:
        """
        Validate a Spotify URL.

        Args:
            url: Spotify URL to validate

        Returns:
            Validation result dictionary
        """
        try:
            if not self._is_spotify_url(url):
                return {"valid": False, "error": "Invalid Spotify URL format"}

            # Extract track ID
            track_id = self._extract_spotify_track_id(url)
            if not track_id:
                return {
                    "valid": False,
                    "error": "Could not extract track ID from Spotify URL",
                }

            return {
                "valid": True,
                "url": url,
                "track_id": track_id,
                "type": "spotify_track",
            }

        except Exception as e:
            return {"valid": False, "error": f"Spotify URL validation error: {str(e)}"}

    def validate_audio_url(self, url: str) -> Dict:
        """
        Validate an audio URL.

        Args:
            url: URL to validate

        Returns:
            Validation result dictionary
        """
        try:
            if not self._is_url(url):
                return {"valid": False, "error": "Invalid URL format"}

            # Initialize URL downloader if needed
            if not self.url_downloader:
                self.url_downloader = URLDownloader()

            # Check if it's an audio URL
            if not self.url_downloader.is_audio_url(url):
                return {
                    "valid": False,
                    "error": "URL does not appear to be an audio file",
                }

            # Get file info
            file_info = self.url_downloader.get_file_info(url)
            if not file_info["valid"]:
                return {
                    "valid": False,
                    "error": f"Could not access URL: {file_info.get('error', 'Unknown error')}",
                }

            return {
                "valid": True,
                "url": url,
                "file_size_mb": file_info.get("file_size_mb", 0),
                "content_type": file_info.get("content_type", ""),
                "type": "audio_url",
            }

        except Exception as e:
            return {"valid": False, "error": f"URL validation error: {str(e)}"}

    def _extract_spotify_track_id(self, url: str) -> Optional[str]:
        """Extract track ID from Spotify URL."""
        # Handle Spotify URI format
        if url.startswith("spotify:track:"):
            return url.split(":")[-1]

        # Handle HTTP URL format
        track_id_match = re.search(r"/track/([a-zA-Z0-9]+)", url)
        if track_id_match:
            return track_id_match.group(1)

        return None

    def process_input(self, input_path: str, temp_dir: Optional[str] = None) -> Dict:
        """
        Process input and return audio file path ready for stem separation.

        Args:
            input_path: Input file path or Spotify URL
            temp_dir: Temporary directory for downloads (required for Spotify URLs)

        Returns:
            Processing result dictionary with audio file path
        """
        try:
            input_type = self.determine_input_type(input_path)

            if input_type == "local_file":
                return self._process_local_file(input_path)
            elif input_type == "spotify_url":
                if not temp_dir:
                    temp_dir = "/tmp/music_stem_separator"
                return self._process_spotify_url(input_path, temp_dir)
            elif input_type == "audio_url":
                if not temp_dir:
                    temp_dir = "/tmp/music_stem_separator"
                return self._process_audio_url(input_path, temp_dir)
            else:
                return {
                    "success": False,
                    "error": f"Invalid or unsupported input: {input_path}",
                }

        except Exception as e:
            logger.error(f"Input processing failed: {str(e)}")
            return {"success": False, "error": f"Processing error: {str(e)}"}

    def _process_local_file(self, file_path: str) -> Dict:
        """Process local audio file."""
        validation = self.validate_local_file(file_path)

        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        return {
            "success": True,
            "input_type": "local_file",
            "audio_file": validation["file_path"],
            "format": validation["format"],
            "size_bytes": validation["size_bytes"],
        }

    def _process_spotify_url(self, url: str, temp_dir: str) -> Dict:
        """Process Spotify URL by downloading the track."""
        validation = self.validate_spotify_url(url)

        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        # Initialize Spotify handler if needed
        if not self.spotify_handler:
            self.spotify_handler = SpotifyHandler()

        # Download the track
        download_result = self.spotify_handler.download_track(url, temp_dir)

        if not download_result["success"]:
            return {
                "success": False,
                "error": f"Spotify download failed: {download_result.get('error', 'Unknown error')}",
            }

        return {
            "success": True,
            "input_type": "spotify_url",
            "audio_file": download_result["file_path"],
            "track_id": validation["track_id"],
            "original_url": url,
            "temp_file": True,  # Mark as temporary for cleanup
        }

    def _process_audio_url(self, url: str, temp_dir: str) -> Dict:
        """Process audio URL by downloading the file."""
        validation = self.validate_audio_url(url)

        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        # Initialize URL downloader if needed
        if not self.url_downloader:
            self.url_downloader = URLDownloader()

        # Download the file
        download_result = self.url_downloader.download_file(url, temp_dir)

        if not download_result["success"]:
            return {
                "success": False,
                "error": f"URL download failed: {download_result.get('error', 'Unknown error')}",
            }

        return {
            "success": True,
            "input_type": "audio_url",
            "audio_file": download_result["file_path"],
            "url": url,
            "file_size_mb": download_result.get("file_size_mb", 0),
            "temp_file": True,
        }

    def clean_input_path(self, input_path: str) -> str:
        """
        Clean and normalize input path string.

        Args:
            input_path: Raw input path

        Returns:
            Cleaned path string
        """
        if not input_path:
            return ""

        # Strip whitespace
        cleaned = input_path.strip()

        # Remove surrounding quotes
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (
            cleaned.startswith("'") and cleaned.endswith("'")
        ):
            cleaned = cleaned[1:-1]

        return cleaned

    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported audio formats.

        Returns:
            List of supported file extensions
        """
        return self.SUPPORTED_FORMATS.copy()

    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files.

        Args:
            file_paths: List of file paths to remove
        """
        if self.spotify_handler:
            self.spotify_handler.cleanup_temp_files(file_paths)

        if self.url_downloader:
            self.url_downloader.cleanup_temp_files(file_paths)
