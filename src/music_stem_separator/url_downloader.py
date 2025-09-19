"""URL download functionality for audio files."""

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class URLDownloader:
    """Handler for downloading audio files from URLs."""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        """
        Initialize the URL downloader.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Set up session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set user agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        logger.info(f"Initialized URLDownloader with timeout: {timeout}s, max_retries: {max_retries}")

    def is_valid_url(self, url: str) -> bool:
        """
        Check if the provided string is a valid URL.

        Args:
            url: URL to validate

        Returns:
            True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def is_audio_url(self, url: str) -> bool:
        """
        Check if the URL points to an audio file.

        Args:
            url: URL to check

        Returns:
            True if URL appears to be an audio file, False otherwise
        """
        if not self.is_valid_url(url):
            return False

        # Check file extension
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}
        parsed_url = urlparse(url)
        path = Path(parsed_url.path)
        
        if path.suffix.lower() in audio_extensions:
            return True

        # Check content type by making a HEAD request
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            
            audio_types = {
                'audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/flac',
                'audio/mp4', 'audio/aac', 'audio/ogg', 'audio/x-wav',
                'audio/wave', 'audio/x-m4a'
            }
            
            return any(audio_type in content_type for audio_type in audio_types)
        except Exception as e:
            logger.debug(f"Could not check content type for {url}: {e}")
            return False

    def download_file(self, url: str, output_dir: str, filename: Optional[str] = None) -> Dict:
        """
        Download an audio file from a URL.

        Args:
            url: URL to download from
            output_dir: Directory to save the file
            filename: Optional custom filename (if None, will be derived from URL)

        Returns:
            Dictionary with download results and metadata
        """
        try:
            if not self.is_valid_url(url):
                raise ValueError(f"Invalid URL: {url}")

            if not self.is_audio_url(url):
                raise ValueError(f"URL does not appear to be an audio file: {url}")

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename if not provided
            if not filename:
                parsed_url = urlparse(url)
                path = Path(parsed_url.path)
                if path.suffix:
                    filename = f"downloaded_audio{path.suffix}"
                else:
                    filename = "downloaded_audio.mp3"

            output_path = output_dir / filename

            logger.info(f"Downloading audio file from: {url}")
            logger.info(f"Saving to: {output_path}")

            # Download the file
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()

            # Get file size if available
            file_size = int(response.headers.get('content-length', 0))
            if file_size > 0:
                logger.info(f"File size: {file_size / (1024*1024):.1f} MB")

            # Download with progress
            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if file_size > 0:
                            progress = (downloaded / file_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Log every MB
                                logger.debug(f"Downloaded: {downloaded / (1024*1024):.1f} MB ({progress:.1f}%)")

            # Verify file was downloaded
            if not output_path.exists() or output_path.stat().st_size == 0:
                raise Exception("Download failed or file is empty")

            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Download completed: {file_size_mb:.1f} MB")

            return {
                "success": True,
                "url": url,
                "file_path": str(output_path),
                "filename": filename,
                "file_size_mb": file_size_mb,
                "output_dir": str(output_dir),
            }

        except Exception as e:
            logger.error(f"URL download failed: {str(e)}")
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }

    def get_file_info(self, url: str) -> Dict:
        """
        Get information about a file at a URL without downloading it.

        Args:
            url: URL to check

        Returns:
            Dictionary with file information
        """
        try:
            if not self.is_valid_url(url):
                return {"valid": False, "error": "Invalid URL"}

            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length')
            file_size = int(content_length) if content_length else 0

            return {
                "valid": True,
                "url": url,
                "content_type": content_type,
                "file_size": file_size,
                "file_size_mb": file_size / (1024 * 1024) if file_size > 0 else 0,
                "is_audio": self.is_audio_url(url)
            }

        except Exception as e:
            logger.error(f"Failed to get file info for {url}: {e}")
            return {"valid": False, "url": url, "error": str(e)}

    def cleanup_temp_files(self, file_paths: list) -> None:
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
