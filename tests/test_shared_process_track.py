"""Tests for the shared process_track module."""

from unittest.mock import Mock, patch

from music_stem_separator.shared.process_track import process_track


class TestSharedProcessTrack:
    """Test cases for the shared process_track function."""

    @patch("music_stem_separator.shared.process_track.InputProcessor")
    @patch("music_stem_separator.shared.process_track.StemSeparator")
    @patch("music_stem_separator.shared.process_track.StemProcessor")
    @patch("music_stem_separator.shared.process_track.OutputManager")
    def test_process_track_with_progress_callback(
        self,
        mock_output_manager,
        mock_stem_processor,
        mock_separator,
        mock_input_processor,
    ):
        """Test process_track with progress callback."""
        # Setup mocks
        mock_input = Mock()
        mock_input_processor.return_value = mock_input
        mock_input.process_input.return_value = {
            "success": True,
            "input_type": "local_file",
            "audio_file": "/tmp/test.mp3",
        }

        mock_sep = Mock()
        mock_separator.return_value = mock_sep
        mock_sep.separate_stems.return_value = {
            "success": True,
            "stems": {"drums": "/tmp/drums.wav"},
        }

        mock_proc = Mock()
        mock_stem_processor.return_value = mock_proc
        mock_proc.process_stem_files.return_value = {
            "success": True,
            "processed_stems": {
                "drums": {"output_file": "/tmp/drums_processed.wav"},
            },
        }

        mock_output = Mock()
        mock_output_manager.return_value = mock_output
        mock_output.organize_stem_files.return_value = {
            "success": True,
            "output_structure": {"track_dir": "/tmp/output/test"},
        }
        mock_output.generate_metadata.return_value = {"test": "metadata"}
        mock_output.save_metadata.return_value = {"success": True}
        mock_output.create_summary_report.return_value = "Test report"
        mock_output.get_output_summary.return_value = {
            "track_directory": "/tmp/output/test",
            "total_files": 4,
            "total_size_mb": 10.5,
        }

        # Track progress callbacks
        progress_calls = []

        def progress_callback(progress_data):
            progress_calls.append(progress_data)

        # Test the function with progress callback
        result = process_track(
            input_path="/tmp/test.mp3",
            output_dir="/tmp/output",
            model_name="htdemucs",
            device=None,
            enable_enhancement=True,
            verbose=False,
            progress_callback=progress_callback,
        )

        # Verify success
        assert result["success"] is True

        # Verify progress callbacks were made
        assert len(progress_calls) > 0

        # Verify progress callback structure
        for call in progress_calls:
            assert "stage" in call
            assert "percent" in call
            assert "message" in call
            assert isinstance(call["percent"], int)
            assert 0 <= call["percent"] <= 100

        # Verify key stages were reported
        stages = [call["stage"] for call in progress_calls]
        assert "input_processing" in stages
        assert "loading_model" in stages
        assert "separating_stems" in stages
        assert "organizing_output" in stages

        # Verify progress starts at 0 and ends at 100
        assert progress_calls[0]["percent"] == 0
        assert progress_calls[-1]["percent"] == 100

    @patch("music_stem_separator.shared.process_track.InputProcessor")
    @patch("music_stem_separator.shared.process_track.StemSeparator")
    @patch("music_stem_separator.shared.process_track.StemProcessor")
    @patch("music_stem_separator.shared.process_track.OutputManager")
    def test_process_track_without_callback(
        self,
        mock_output_manager,
        mock_stem_processor,
        mock_separator,
        mock_input_processor,
    ):
        """Test process_track works without progress callback."""
        # Setup mocks
        mock_input = Mock()
        mock_input_processor.return_value = mock_input
        mock_input.process_input.return_value = {
            "success": True,
            "input_type": "local_file",
            "audio_file": "/tmp/test.mp3",
        }

        mock_sep = Mock()
        mock_separator.return_value = mock_sep
        mock_sep.separate_stems.return_value = {
            "success": True,
            "stems": {"drums": "/tmp/drums.wav"},
        }

        mock_proc = Mock()
        mock_stem_processor.return_value = mock_proc
        mock_proc.process_stem_files.return_value = {
            "success": True,
            "processed_stems": {
                "drums": {"output_file": "/tmp/drums_processed.wav"},
            },
        }

        mock_output = Mock()
        mock_output_manager.return_value = mock_output
        mock_output.organize_stem_files.return_value = {
            "success": True,
            "output_structure": {"track_dir": "/tmp/output/test"},
        }
        mock_output.generate_metadata.return_value = {"test": "metadata"}
        mock_output.save_metadata.return_value = {"success": True}
        mock_output.create_summary_report.return_value = "Test report"
        mock_output.get_output_summary.return_value = {
            "track_directory": "/tmp/output/test",
            "total_files": 4,
            "total_size_mb": 10.5,
        }

        # Test without callback (should not crash)
        result = process_track(
            input_path="/tmp/test.mp3",
            output_dir="/tmp/output",
            model_name="htdemucs",
            device=None,
            enable_enhancement=True,
            verbose=False,
            progress_callback=None,
        )

        # Verify success
        assert result["success"] is True

    @patch("music_stem_separator.shared.process_track.InputProcessor")
    def test_process_track_input_failure(self, mock_input_processor):
        """Test process_track handles input processing failure."""
        mock_input = Mock()
        mock_input_processor.return_value = mock_input
        mock_input.process_input.return_value = {
            "success": False,
            "error": "Invalid input",
        }

        progress_calls = []

        def progress_callback(progress_data):
            progress_calls.append(progress_data)

        result = process_track(
            input_path="/invalid/path",
            output_dir="/tmp/output",
            model_name="htdemucs",
            device=None,
            enable_enhancement=True,
            verbose=False,
            progress_callback=progress_callback,
        )

        # Verify failure
        assert result["success"] is False
        assert "Invalid input" in result["error"]

        # Verify progress callback was called at start
        assert len(progress_calls) >= 1
        assert progress_calls[0]["stage"] == "input_processing"
        assert progress_calls[0]["percent"] == 0

    @patch("music_stem_separator.shared.process_track.InputProcessor")
    @patch("music_stem_separator.shared.process_track.StemSeparator")
    @patch("music_stem_separator.shared.process_track.OutputManager")
    def test_process_track_without_enhancement(
        self,
        mock_output_manager,
        mock_separator,
        mock_input_processor,
    ):
        """Test process_track skips enhancement when disabled."""
        mock_input = Mock()
        mock_input_processor.return_value = mock_input
        mock_input.process_input.return_value = {
            "success": True,
            "input_type": "local_file",
            "audio_file": "/tmp/test.mp3",
        }

        mock_sep = Mock()
        mock_separator.return_value = mock_sep
        mock_sep.separate_stems.return_value = {
            "success": True,
            "stems": {"drums": "/tmp/drums.wav"},
        }

        mock_output = Mock()
        mock_output_manager.return_value = mock_output
        mock_output.organize_stem_files.return_value = {
            "success": True,
            "output_structure": {"track_dir": "/tmp/output/test"},
        }
        mock_output.generate_metadata.return_value = {"test": "metadata"}
        mock_output.save_metadata.return_value = {"success": True}
        mock_output.create_summary_report.return_value = "Test report"
        mock_output.get_output_summary.return_value = {
            "track_directory": "/tmp/output/test",
            "total_files": 4,
            "total_size_mb": 10.5,
        }

        progress_calls = []

        def progress_callback(progress_data):
            progress_calls.append(progress_data)

        result = process_track(
            input_path="/tmp/test.mp3",
            output_dir="/tmp/output",
            model_name="htdemucs",
            device=None,
            enable_enhancement=False,
            verbose=False,
            progress_callback=progress_callback,
        )

        # Verify success
        assert result["success"] is True
        assert result["enhancement_applied"] is False

        # Verify enhancement was skipped in progress messages
        messages = [call["message"] for call in progress_calls]
        assert any("Skipping audio enhancement" in msg for msg in messages)
