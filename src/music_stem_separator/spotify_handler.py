"""Spotify track download functionality using spotdl."""

import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    from spotdl import Spotdl
except ImportError as e:
    raise ImportError(f"spotdl not installed: {e}")


logger = logging.getLogger(__name__)


class SpotifyHandler:
    """Handler for downloading tracks from Spotify using spotdl."""

    def __init__(self, output_format: str = "mp3", quality: str = "best"):
        """
        Initialize the Spotify handler.

        Args:
            output_format: Audio format for downloads (mp3, wav, flac, etc.)
            quality: Audio quality (best, 320k, 256k, 192k, 128k, etc.)
        """
        self.output_format = output_format
        self.quality = quality

        # Get Spotify credentials from environment variables
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not found. Please set SPOTIFY_CLIENT_ID and "
                "SPOTIFY_CLIENT_SECRET environment variables. "
                "Get them from https://developer.spotify.com/dashboard"
            )

        # Store settings for spotdl initialization
        self.settings = {
            "output_format": output_format,
            "bitrate": quality,
            "audio_providers": ["youtube-music", "youtube"],  # YouTube Music primary, YouTube as fallback
        }

        logger.info(
            f"Initialized SpotifyHandler with format: {output_format}, quality: {quality}"
        )

    def is_spotify_url(self, url: str) -> bool:
        """
        Check if the provided URL is a valid Spotify track URL.

        Args:
            url: URL to validate

        Returns:
            True if valid Spotify track URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False

        # Support both HTTP and Spotify URI formats
        spotify_patterns = [
            r"https://open\.spotify\.com/track/[a-zA-Z0-9]+",
            r"spotify:track:[a-zA-Z0-9]+",
        ]

        return any(re.match(pattern, url.strip()) for pattern in spotify_patterns)

    def extract_track_id(self, url: str) -> Optional[str]:
        """
        Extract the Spotify track ID from a URL.

        Args:
            url: Spotify URL or URI

        Returns:
            Track ID if found, None otherwise
        """
        if not self.is_spotify_url(url):
            return None

        # Handle Spotify URI format: spotify:track:ID
        if url.startswith("spotify:track:"):
            return url.split(":")[-1]

        # Handle HTTP URL format
        track_id_match = re.search(r"/track/([a-zA-Z0-9]+)", url)
        if track_id_match:
            return track_id_match.group(1)

        return None

    def download_track(self, spotify_url: str, output_dir: Union[str, Path]) -> Dict:
        """
        Download a track from Spotify.

        Args:
            spotify_url: Spotify track URL or URI
            output_dir: Directory to save the downloaded file

        Returns:
            Dictionary with download results and metadata
        """
        try:
            if not self.is_spotify_url(spotify_url):
                raise ValueError(f"Invalid Spotify URL: {spotify_url}")

            track_id = self.extract_track_id(spotify_url)
            if not track_id:
                raise ValueError(f"Could not extract track ID from: {spotify_url}")

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Downloading Spotify track: {track_id}")

            # Initialize spotdl with credentials and settings
            # Disable strict filtering to allow more flexible matching
            # YouTube API changes have made strict filtering too aggressive
            downloader_settings = {
                "audio_providers": self.settings["audio_providers"],
                "filter_results": False,  # Allow all search results (filtering is too strict)
            }
            spotdl = Spotdl(
                client_id=self.client_id,
                client_secret=self.client_secret,
                downloader_settings=downloader_settings
            )

            # Download the track
            songs = spotdl.search([spotify_url])
            if not songs:
                raise Exception("No songs found for the given URL")

            song = songs[0]
            song, downloaded_file = spotdl.download(song)

            if not downloaded_file or not os.path.exists(downloaded_file):
                raise Exception(f"Download failed or file not found: {downloaded_file}")

            return {
                "success": True,
                "spotify_url": spotify_url,
                "track_id": track_id,
                "file_path": downloaded_file,
                "output_dir": str(output_dir),
                "format": self.output_format,
                "quality": self.quality,
            }

        except Exception as e:
            error_msg = str(e)
            if "No results found" in error_msg or "Requested format is not available" in error_msg:
                error_msg = (
                    f"Song with track ID '{track_id}' is not available for download due to copyright restrictions "
                    "or is blocked on all audio platforms. Try a different song or use a local MP3 file instead."
                )
            logger.error(f"Spotify download failed: {error_msg}")
            return {"success": False, "spotify_url": spotify_url, "error": error_msg}

    def get_download_path(self, output_dir: Union[str, Path], track_id: str) -> Path:
        """
        Generate expected download path for a track.

        Args:
            output_dir: Output directory
            track_id: Spotify track ID

        Returns:
            Expected file path
        """
        output_dir = Path(output_dir)
        filename = f"spotify_{track_id}.{self.output_format}"
        return output_dir / filename

    def batch_download(
        self, spotify_urls: List[str], output_dir: Union[str, Path]
    ) -> Dict:
        """
        Download multiple tracks from Spotify.

        Args:
            spotify_urls: List of Spotify URLs
            output_dir: Directory to save downloaded files

        Returns:
            Dictionary with batch download results
        """
        results = {
            "success": True,
            "downloaded": [],
            "failed": [],
            "total": len(spotify_urls),
        }

        for url in spotify_urls:
            result = self.download_track(url, output_dir)
            if result["success"]:
                results["downloaded"].append(result)
            else:
                results["failed"].append(result)
                results["success"] = False

        logger.info(
            f"Batch download completed: {len(results['downloaded'])}/{results['total']} successful"
        )
        return results

    def cleanup_temp_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary downloaded files.

        Args:
            file_paths: List of file paths to remove
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up {file_path}: {e}")

    def get_track_metadata(self, spotify_url: str) -> Dict:
        """
        Get metadata for a Spotify track without downloading.

        Args:
            spotify_url: Spotify track URL

        Returns:
            Track metadata dictionary
        """
        try:
            if not self.is_spotify_url(spotify_url):
                raise ValueError(f"Invalid Spotify URL: {spotify_url}")

            track_id = self.extract_track_id(spotify_url)

            # This would typically use the Spotify Web API
            # For now, return basic info
            return {"track_id": track_id, "spotify_url": spotify_url, "type": "track"}

        except Exception as e:
            logger.error(f"Failed to get track metadata: {e}")
            return {"error": str(e)}
