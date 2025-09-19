"""Tests for the CLI module."""

from unittest.mock import Mock, patch
from click.testing import CliRunner

from music_stem_separator.cli import main, process_track


class TestCLI:
    """Test cases for the CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Music Stem Separator" in result.output
        assert "INPUT" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    @patch("music_stem_separator.cli.InputProcessor")
    @patch("music_stem_separator.cli.StemSeparator")
    @patch("music_stem_separator.cli.StemProcessor")
    @patch("music_stem_separator.cli.OutputManager")
    def test_cli_local_file_basic(
        self,
        mock_output_manager,
        mock_stem_processor,
        mock_separator,
        mock_input_processor,
    ):
        """Test CLI with local file input."""
        runner = CliRunner()

        # Mock the processors
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
            "stems": {"drums": "/tmp/drums.wav", "vocals": "/tmp/vocals.wav"},
        }

        mock_proc = Mock()
        mock_stem_processor.return_value = mock_proc
        mock_proc.process_stem_files.return_value = {"success": True}

        mock_output = Mock()
        mock_output_manager.return_value = mock_output
        mock_output.organize_stem_files.return_value = {"success": True}

        result = runner.invoke(main, ["/tmp/test.mp3"])

        assert result.exit_code == 0

    @patch("music_stem_separator.cli.InputProcessor")
    def test_cli_spotify_url(self, mock_input_processor):
        """Test CLI with Spotify URL."""
        runner = CliRunner()

        mock_input = Mock()
        mock_input_processor.return_value = mock_input
        mock_input.process_input.return_value = {
            "success": True,
            "input_type": "spotify_url",
            "audio_file": "/tmp/downloaded.mp3",
        }

        # Mock other components
        with (
            patch("music_stem_separator.cli.StemSeparator") as mock_sep,
            patch("music_stem_separator.cli.StemProcessor") as mock_proc,
            patch("music_stem_separator.cli.OutputManager") as mock_output,
        ):

            mock_sep.return_value.separate_stems.return_value = {
                "success": True,
                "stems": {},
            }
            mock_proc.return_value.process_stem_files.return_value = {"success": True}
            mock_output.return_value.organize_stem_files.return_value = {
                "success": True
            }

            result = runner.invoke(main, ["https://open.spotify.com/track/123"])

            assert result.exit_code == 0

    def test_cli_invalid_input(self):
        """Test CLI with invalid input."""
        runner = CliRunner()

        with patch("music_stem_separator.cli.InputProcessor") as mock_input_processor:
            mock_input = Mock()
            mock_input_processor.return_value = mock_input
            mock_input.process_input.return_value = {
                "success": False,
                "error": "Invalid input",
            }

            result = runner.invoke(main, ["invalid_input"])

            assert result.exit_code == 1
            assert "Invalid input" in result.output

    def test_cli_with_model_option(self):
        """Test CLI with custom model option."""
        runner = CliRunner()

        with (
            patch("music_stem_separator.cli.InputProcessor") as mock_input_processor,
            patch("music_stem_separator.cli.StemSeparator") as mock_separator,
        ):

            mock_input = Mock()
            mock_input_processor.return_value = mock_input
            mock_input.process_input.return_value = {
                "success": True,
                "audio_file": "/tmp/test.mp3",
            }

            mock_sep = Mock()
            mock_separator.return_value = mock_sep
            mock_sep.separate_stems.return_value = {"success": True, "stems": {}}

            with (
                patch("music_stem_separator.cli.StemProcessor") as mock_proc,
                patch("music_stem_separator.cli.OutputManager") as mock_output,
            ):

                mock_proc.return_value.process_stem_files.return_value = {
                    "success": True
                }
                mock_output.return_value.organize_stem_files.return_value = {
                    "success": True
                }

                result = runner.invoke(
                    main, ["/tmp/test.mp3", "--model", "htdemucs_ft"]
                )

                assert result.exit_code == 0
                mock_separator.assert_called_with(model_name="htdemucs_ft", device=None)

    def test_cli_with_output_option(self):
        """Test CLI with custom output directory."""
        runner = CliRunner()

        with (
            patch("music_stem_separator.cli.InputProcessor") as mock_input_processor,
            patch("music_stem_separator.cli.OutputManager") as mock_output_manager,
        ):

            mock_input = Mock()
            mock_input_processor.return_value = mock_input
            mock_input.process_input.return_value = {
                "success": True,
                "audio_file": "/tmp/test.mp3",
            }

            mock_output = Mock()
            mock_output_manager.return_value = mock_output

            with (
                patch("music_stem_separator.cli.StemSeparator") as mock_sep,
                patch("music_stem_separator.cli.StemProcessor") as mock_proc,
            ):

                mock_sep.return_value.separate_stems.return_value = {
                    "success": True,
                    "stems": {},
                }
                mock_proc.return_value.process_stem_files.return_value = {
                    "success": True
                }
                mock_output.organize_stem_files.return_value = {"success": True}

                result = runner.invoke(
                    main, ["/tmp/test.mp3", "--output", "/custom/output"]
                )

                assert result.exit_code == 0
                mock_output_manager.assert_called_with("/custom/output")

    def test_cli_no_enhancement(self):
        """Test CLI with enhancement disabled."""
        runner = CliRunner()

        with patch("music_stem_separator.cli.StemProcessor") as mock_stem_processor:
            mock_proc = Mock()
            mock_stem_processor.return_value = mock_proc

            with (
                patch(
                    "music_stem_separator.cli.InputProcessor"
                ) as mock_input_processor,
                patch("music_stem_separator.cli.StemSeparator") as mock_sep,
                patch("music_stem_separator.cli.OutputManager") as mock_output,
            ):

                mock_input_processor.return_value.process_input.return_value = {
                    "success": True,
                    "audio_file": "/tmp/test.mp3",
                }
                mock_sep.return_value.separate_stems.return_value = {
                    "success": True,
                    "stems": {},
                }
                mock_proc.process_stem_files.return_value = {"success": True}
                mock_output.return_value.organize_stem_files.return_value = {
                    "success": True
                }

                result = runner.invoke(main, ["/tmp/test.mp3", "--no-enhance"])

                assert result.exit_code == 0
                mock_stem_processor.assert_called_with(enable_enhancement=False)

    def test_cli_verbose_mode(self):
        """Test CLI verbose mode."""
        runner = CliRunner()

        with patch("music_stem_separator.cli.InputProcessor") as mock_input_processor:
            mock_input_processor.return_value.process_input.return_value = {
                "success": False,
                "error": "Test error",
            }

            result = runner.invoke(main, ["/tmp/test.mp3", "--verbose"])

            assert result.exit_code == 1
            # In verbose mode, more detailed output should be shown

    @patch("music_stem_separator.cli.InputProcessor")
    @patch("music_stem_separator.cli.StemSeparator")
    @patch("music_stem_separator.cli.StemProcessor")
    @patch("music_stem_separator.cli.OutputManager")
    def test_process_track_function(
        self,
        mock_output_manager,
        mock_stem_processor,
        mock_separator,
        mock_input_processor,
    ):
        """Test the process_track function directly."""
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
            "track_name": "test_song",
        }

        mock_proc = Mock()
        mock_stem_processor.return_value = mock_proc
        mock_proc.process_stem_files.return_value = {"success": True}

        mock_output = Mock()
        mock_output_manager.return_value = mock_output
        mock_output.organize_stem_files.return_value = {"success": True}
        mock_output.create_summary_report.return_value = "Test report"

        # Test the function
        result = process_track(
            input_path="/tmp/test.mp3",
            output_dir="/tmp/output",
            model_name="htdemucs",
            device=None,
            enable_enhancement=True,
            verbose=False,
        )

        assert result["success"] is True
