"""Tests for the input processor module."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from music_stem_separator.input_processor import InputProcessor


class TestInputProcessor:
    """Test cases for the InputProcessor class."""

    def test_input_processor_initialization(self):
        """Test InputProcessor initialization."""
        processor = InputProcessor()
        assert processor is not None

    def test_determine_input_type_local_file(self):
        """Test input type detection for local files."""
        processor = InputProcessor()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            input_type = processor.determine_input_type(temp_path)
            assert input_type == "local_file"
        finally:
            Path(temp_path).unlink()

    def test_determine_input_type_spotify_url(self):
        """Test input type detection for Spotify URLs."""
        processor = InputProcessor()

        spotify_urls = [
            "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC",
            "spotify:track:4uLU6hMCjMI75M1A2tKUQC",
        ]

        for url in spotify_urls:
            input_type = processor.determine_input_type(url)
            assert input_type == "spotify_url"

    def test_determine_input_type_audio_url(self):
        """Test input type detection for generic audio URLs."""
        processor = InputProcessor()

        audio_urls = [
            "https://youtube.com/watch?v=abc123",
            "https://example.com/song.mp3",
        ]

        for url in audio_urls:
            input_type = processor.determine_input_type(url)
            assert input_type == "audio_url"

    def test_determine_input_type_invalid(self):
        """Test input type detection for invalid inputs."""
        processor = InputProcessor()

        invalid_inputs = [
            "nonexistent_file.mp3",
            "invalid_input",
            "",
        ]

        for invalid_input in invalid_inputs:
            input_type = processor.determine_input_type(invalid_input)
            assert input_type == "invalid"

    def test_validate_local_file_valid(self):
        """Test local file validation for valid files."""
        processor = InputProcessor()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = processor.validate_local_file(temp_path)
            assert result["valid"] is True
            assert result["file_path"] == temp_path
            assert result["format"] == ".mp3"
        finally:
            Path(temp_path).unlink()

    def test_validate_local_file_nonexistent(self):
        """Test local file validation for nonexistent files."""
        processor = InputProcessor()

        result = processor.validate_local_file("nonexistent.mp3")
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    def test_validate_local_file_unsupported_format(self):
        """Test local file validation for unsupported formats."""
        processor = InputProcessor()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = processor.validate_local_file(temp_path)
            assert result["valid"] is False
            assert "unsupported format" in result["error"].lower()
        finally:
            Path(temp_path).unlink()

    def test_validate_spotify_url_valid(self):
        """Test Spotify URL validation for valid URLs."""
        processor = InputProcessor()

        valid_urls = [
            "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC",
            "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC?si=abc123",
        ]

        for url in valid_urls:
            result = processor.validate_spotify_url(url)
            assert result["valid"] is True
            assert result["url"] == url
            assert result["track_id"] == "4uLU6hMCjMI75M1A2tKUQC"

    def test_validate_spotify_url_invalid(self):
        """Test Spotify URL validation for invalid URLs."""
        processor = InputProcessor()

        invalid_urls = [
            "https://youtube.com/watch?v=abc123",
            "invalid_url",
            "https://open.spotify.com/playlist/abc123",
        ]

        for url in invalid_urls:
            result = processor.validate_spotify_url(url)
            assert result["valid"] is False
            assert "error" in result

    @patch("music_stem_separator.input_processor.SpotifyHandler")
    def test_process_input_local_file(self, mock_spotify_handler):
        """Test input processing for local files."""
        processor = InputProcessor()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            result = processor.process_input(temp_path)
            assert result["success"] is True
            assert result["input_type"] == "local_file"
            assert result["audio_file"] == temp_path
        finally:
            Path(temp_path).unlink()

    @patch("music_stem_separator.input_processor.SpotifyHandler")
    def test_process_input_spotify_url(self, mock_spotify_handler_class):
        """Test input processing for Spotify URLs."""
        processor = InputProcessor()

        mock_handler = Mock()
        mock_spotify_handler_class.return_value = mock_handler
        mock_handler.download_track.return_value = {
            "success": True,
            "file_path": "/tmp/downloaded.mp3",
        }

        url = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"
        result = processor.process_input(url, "/tmp/downloads")

        assert result["success"] is True
        assert result["input_type"] == "spotify_url"
        assert result["audio_file"] == "/tmp/downloaded.mp3"

    def test_process_input_invalid(self):
        """Test input processing for invalid inputs."""
        processor = InputProcessor()

        result = processor.process_input("invalid_input")
        assert result["success"] is False
        assert "error" in result

    def test_get_supported_formats(self):
        """Test supported formats retrieval."""
        processor = InputProcessor()
        formats = processor.get_supported_formats()

        expected_formats = [".mp3", ".wav", ".flac", ".m4a"]
        assert all(fmt in formats for fmt in expected_formats)

    def test_clean_input_path(self):
        """Test input path cleaning."""
        processor = InputProcessor()

        test_cases = [
            ("  /path/to/file.mp3  ", "/path/to/file.mp3"),
            ("'file.mp3'", "file.mp3"),
            ('"file.mp3"', "file.mp3"),
            ("file.mp3", "file.mp3"),
        ]

        for input_path, expected in test_cases:
            cleaned = processor.clean_input_path(input_path)
            assert cleaned == expected
