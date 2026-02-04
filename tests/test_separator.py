"""Tests for the core separator module."""

from unittest.mock import patch

from music_stem_separator.separator import StemSeparator


class TestStemSeparator:
    """Test cases for the StemSeparator class."""

    def test_separator_initialization(self):
        """Test that StemSeparator initializes with default model."""
        separator = StemSeparator()
        assert separator.model_name == "htdemucs"
        assert separator.device == "cpu"

    def test_separator_initialization_with_custom_model(self):
        """Test StemSeparator initialization with custom model."""
        separator = StemSeparator(model_name="htdemucs_ft", device="cuda")
        assert separator.model_name == "htdemucs_ft"
        assert separator.device == "cuda"

    def test_supported_formats(self):
        """Test that separator supports expected audio formats."""
        separator = StemSeparator()
        expected_formats = [".mp3", ".wav", ".flac", ".m4a"]
        assert all(fmt in separator.supported_formats for fmt in expected_formats)

    def test_is_supported_format(self):
        """Test format validation."""
        separator = StemSeparator()
        assert separator.is_supported_format("test.mp3")
        assert separator.is_supported_format("test.wav")
        assert not separator.is_supported_format("test.txt")
        assert not separator.is_supported_format("test")

    @patch("subprocess.run")
    def test_separate_stems_success(self, mock_run):
        """Test successful stem separation."""
        import tempfile
        from unittest.mock import MagicMock

        separator = StemSeparator()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            test_file = f.name

        output_dir = "/tmp/output"

        mock_run.return_value = MagicMock(returncode=0, stderr="")

        result = separator.separate_stems(test_file, output_dir)

        mock_run.assert_called_once()
        assert result["success"] is True
        assert result["output_dir"] == output_dir
        assert "stems" in result

        import os
        os.unlink(test_file)

    def test_separate_stems_failure(self):
        """Test stem separation with error handling."""
        separator = StemSeparator()
        test_file = "nonexistent.mp3"
        output_dir = "/tmp/output"

        result = separator.separate_stems(test_file, output_dir)

        assert result["success"] is False
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_get_stem_paths(self):
        """Test stem file path generation."""
        separator = StemSeparator()
        output_dir = "/tmp/output"
        track_name = "test_song"

        paths = separator.get_stem_paths(output_dir, track_name)

        expected_stems = ["drums", "bass", "vocals", "other"]
        assert all(stem in paths for stem in expected_stems)
        assert all(track_name in str(path) for path in paths.values())
        assert all(str(path).endswith(".wav") for path in paths.values())
