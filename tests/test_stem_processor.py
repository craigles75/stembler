"""Tests for the stem processor module."""

import pytest
import tempfile
import numpy as np
from unittest.mock import patch

from music_stem_separator.stem_processor import StemProcessor


class TestStemProcessor:
    """Test cases for the StemProcessor class."""

    def test_stem_processor_initialization(self):
        """Test StemProcessor initialization."""
        processor = StemProcessor()
        assert processor.sample_rate == 44100
        assert processor.enable_enhancement is True

    def test_stem_processor_custom_initialization(self):
        """Test StemProcessor with custom settings."""
        processor = StemProcessor(sample_rate=48000, enable_enhancement=False)
        assert processor.sample_rate == 48000
        assert processor.enable_enhancement is False

    @patch("librosa.load")
    def test_load_audio_file(self, mock_load):
        """Test audio file loading."""
        processor = StemProcessor()

        mock_audio_data = np.random.rand(44100)
        mock_load.return_value = (mock_audio_data, 44100)

        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            audio_data, sr = processor.load_audio_file(temp_file.name)

        mock_load.assert_called_once()
        assert audio_data is not None
        assert sr == 44100

    @patch("soundfile.write")
    def test_save_audio_file(self, mock_write):
        """Test audio file saving."""
        processor = StemProcessor()

        audio_data = np.random.rand(44100)
        output_path = "/tmp/test_output.wav"

        result = processor.save_audio_file(audio_data, output_path, 44100)

        mock_write.assert_called_once()
        assert result["success"] is True
        assert result["file_path"] == output_path

    def test_normalize_audio(self):
        """Test audio normalization."""
        processor = StemProcessor()

        # Create test audio with values outside [-1, 1]
        audio_data = np.array([2.0, -1.5, 0.5, -0.8, 1.2])
        normalized = processor.normalize_audio(audio_data)

        # Check that values are within [-1, 1]
        assert np.max(normalized) <= 1.0
        assert np.min(normalized) >= -1.0

    def test_normalize_audio_max_db(self):
        """Test audio normalization with max dB setting."""
        processor = StemProcessor()

        audio_data = np.random.rand(1000) * 2.0 - 1.0  # Random audio between -1 and 1
        normalized = processor.normalize_audio(audio_data, max_db=-3.0)

        # Check that peak is at approximately -3dB
        peak_db = 20 * np.log10(np.max(np.abs(normalized)))
        assert peak_db <= -2.9  # Allow small tolerance

    def test_apply_fade_in_out(self):
        """Test fade in/out application."""
        processor = StemProcessor()

        audio_data = np.ones(44100)  # 1 second of audio at 1.0
        faded = processor.apply_fade_in_out(audio_data, fade_duration=0.1)

        # Check that beginning and end are faded
        assert faded[0] < 1.0
        assert faded[-1] < 1.0
        # Check that middle is still at full volume
        assert np.max(faded) == pytest.approx(1.0, rel=1e-5)

    @patch("librosa.effects.preemphasis")
    def test_enhance_audio_quality(self, mock_preemphasis):
        """Test audio quality enhancement."""
        processor = StemProcessor()

        audio_data = np.random.rand(44100)
        mock_preemphasis.return_value = audio_data

        enhanced = processor.enhance_audio_quality(audio_data)

        # Should apply some enhancement if enabled
        assert enhanced is not None
        assert len(enhanced) == len(audio_data)

    def test_enhance_audio_quality_disabled(self):
        """Test audio enhancement when disabled."""
        processor = StemProcessor(enable_enhancement=False)

        audio_data = np.random.rand(44100)
        enhanced = processor.enhance_audio_quality(audio_data)

        # Should return original audio when enhancement is disabled
        np.testing.assert_array_equal(enhanced, audio_data)

    def test_process_stem_files(self):
        """Test processing multiple stem files."""
        processor = StemProcessor()

        # Create mock stem files
        stem_files = {
            "drums": "/tmp/drums.wav",
            "bass": "/tmp/bass.wav",
            "vocals": "/tmp/vocals.wav",
            "other": "/tmp/other.wav",
        }

        with patch.object(processor, "process_single_stem") as mock_process:
            mock_process.return_value = {
                "success": True,
                "file_path": "/tmp/processed.wav",
            }

            results = processor.process_stem_files(stem_files, "/tmp/output")

            assert results["success"] is True
            assert len(results["processed_stems"]) == 4
            assert mock_process.call_count == 4

    @patch("librosa.load")
    @patch("soundfile.write")
    def test_process_single_stem(self, mock_write, mock_load):
        """Test processing a single stem file."""
        processor = StemProcessor()

        mock_audio_data = np.random.rand(44100)
        mock_load.return_value = (mock_audio_data, 44100)

        input_file = "/tmp/input.wav"
        output_file = "/tmp/output.wav"

        result = processor.process_single_stem(input_file, output_file)

        mock_load.assert_called_once_with(input_file, sr=44100)
        mock_write.assert_called_once()
        assert result["success"] is True

    def test_get_processing_settings(self):
        """Test processing settings retrieval."""
        processor = StemProcessor()
        settings = processor.get_processing_settings()

        assert "sample_rate" in settings
        assert "enable_enhancement" in settings
        assert settings["sample_rate"] == 44100

    def test_validate_audio_data(self):
        """Test audio data validation."""
        processor = StemProcessor()

        # Valid audio data
        valid_audio = np.random.rand(1000)
        assert processor.validate_audio_data(valid_audio) is True

        # Invalid audio data
        assert processor.validate_audio_data(None) is False
        assert processor.validate_audio_data([]) is False
        assert processor.validate_audio_data(np.array([])) is False

    def test_calculate_audio_metrics(self):
        """Test audio metrics calculation."""
        processor = StemProcessor()

        audio_data = np.random.rand(44100) * 0.5  # Random audio at moderate level
        metrics = processor.calculate_audio_metrics(audio_data)

        assert "peak_amplitude" in metrics
        assert "rms_level" in metrics
        assert "duration_seconds" in metrics
        assert metrics["peak_amplitude"] <= 1.0
        assert metrics["duration_seconds"] == pytest.approx(1.0, rel=0.1)
