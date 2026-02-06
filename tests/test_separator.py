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

    @patch("demucs.audio.save_audio")
    @patch("demucs.apply.apply_model")
    @patch("demucs.audio.AudioFile")
    @patch("demucs.pretrained.get_model")
    def test_separate_stems_success(
        self, mock_get_model, mock_audio_file, mock_apply_model, mock_save_audio
    ):
        """Test successful stem separation."""
        import tempfile
        from unittest.mock import MagicMock

        import torch

        separator = StemSeparator()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            test_file = f.name

        output_dir = "/tmp/output"

        # Mock model with expected attributes
        mock_model = MagicMock()
        mock_model.samplerate = 44100
        mock_model.audio_channels = 2
        mock_model.sources = ["drums", "bass", "vocals", "other"]
        mock_get_model.return_value = mock_model

        # Mock audio loading: return a 2-channel tensor
        mock_wav = torch.randn(2, 44100)
        mock_reader = MagicMock()
        mock_reader.read.return_value = mock_wav
        mock_audio_file.return_value = mock_reader

        # Mock apply_model: return tensor shaped [1, 4_stems, 2_channels, samples]
        mock_sources = torch.randn(1, 4, 2, 44100)
        mock_apply_model.return_value = mock_sources

        result = separator.separate_stems(test_file, output_dir)

        mock_get_model.assert_called_once_with("htdemucs")
        mock_apply_model.assert_called_once()
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
