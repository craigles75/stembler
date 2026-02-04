"""Tests for the Spotify handler module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from music_stem_separator.spotify_handler import SpotifyHandler

_TEST_ENV = {"SPOTIFY_CLIENT_ID": "test_client_id", "SPOTIFY_CLIENT_SECRET": "test_client_secret"}


@patch.dict(os.environ, _TEST_ENV)
class TestSpotifyHandler:
    """Test cases for the SpotifyHandler class."""

    def test_spotify_handler_initialization(self):
        """Test that SpotifyHandler initializes correctly."""
        handler = SpotifyHandler()
        assert handler.output_format == "mp3"
        assert handler.quality == "best"

    def test_spotify_handler_custom_initialization(self):
        """Test SpotifyHandler with custom settings."""
        handler = SpotifyHandler(output_format="wav", quality="320k")
        assert handler.output_format == "wav"
        assert handler.quality == "320k"

    def test_is_spotify_url_valid(self):
        """Test Spotify URL validation."""
        handler = SpotifyHandler()

        valid_urls = [
            "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC",
            "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC?si=abc123",
            "spotify:track:4uLU6hMCjMI75M1A2tKUQC",
        ]

        for url in valid_urls:
            assert handler.is_spotify_url(url)

    def test_is_spotify_url_invalid(self):
        """Test invalid URL rejection."""
        handler = SpotifyHandler()

        invalid_urls = [
            "https://youtube.com/watch?v=abc123",
            "https://soundcloud.com/artist/track",
            "not_a_url",
            "",
            "https://open.spotify.com/playlist/abc123",  # Playlist, not track
        ]

        for url in invalid_urls:
            assert not handler.is_spotify_url(url)

    def test_extract_track_id(self):
        """Test track ID extraction from Spotify URLs."""
        handler = SpotifyHandler()

        test_cases = [
            (
                "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC",
                "4uLU6hMCjMI75M1A2tKUQC",
            ),
            (
                "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC?si=abc123",
                "4uLU6hMCjMI75M1A2tKUQC",
            ),
            ("spotify:track:4uLU6hMCjMI75M1A2tKUQC", "4uLU6hMCjMI75M1A2tKUQC"),
        ]

        for url, expected_id in test_cases:
            assert handler.extract_track_id(url) == expected_id

    @patch("os.path.exists", return_value=True)
    @patch("music_stem_separator.spotify_handler.Spotdl")
    def test_download_track_success(self, mock_spotdl_class, mock_exists):
        """Test successful track download."""
        handler = SpotifyHandler()

        mock_song = Mock()
        mock_spotdl = Mock()
        mock_spotdl_class.return_value = mock_spotdl
        mock_spotdl.search.return_value = [mock_song]
        mock_spotdl.download.return_value = (mock_song, "/tmp/downloaded_song.mp3")

        url = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
        output_dir = "/tmp/downloads"

        result = handler.download_track(url, output_dir)

        assert result["success"] is True
        assert result["file_path"] == "/tmp/downloaded_song.mp3"
        assert result["track_id"] == "4uLU6hMCjMI75M1A2tKUQC"

    @patch("music_stem_separator.spotify_handler.Spotdl")
    def test_download_track_failure(self, mock_spotdl_class):
        """Test download failure handling."""
        handler = SpotifyHandler()

        mock_song = Mock()
        mock_spotdl = Mock()
        mock_spotdl_class.return_value = mock_spotdl
        mock_spotdl.search.return_value = [mock_song]
        mock_spotdl.download.side_effect = Exception("Download failed")

        url = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
        output_dir = "/tmp/downloads"

        result = handler.download_track(url, output_dir)

        assert result["success"] is False
        assert "error" in result
        assert "Download failed" in result["error"]

    def test_get_download_path(self):
        """Test download path generation."""
        handler = SpotifyHandler()

        output_dir = "/tmp/downloads"
        track_id = "4uLU6hMCjMI75M1A2tKUQC"

        path = handler.get_download_path(output_dir, track_id)

        assert str(path).startswith(output_dir)
        assert track_id in str(path)
        assert str(path).endswith(".mp3")

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        handler = SpotifyHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.mp3"
            test_file.touch()

            assert test_file.exists()
            handler.cleanup_temp_files([str(test_file)])
            assert not test_file.exists()
