"""Tests for the output manager module."""

import tempfile
import json
from pathlib import Path

from music_stem_separator.output_manager import OutputManager


class TestOutputManager:
    """Test cases for the OutputManager class."""

    def test_output_manager_initialization(self):
        """Test OutputManager initialization."""
        manager = OutputManager("/tmp/output")
        assert manager.base_output_dir == Path("/tmp/output")
        assert manager.create_subdirs is True

    def test_output_manager_custom_initialization(self):
        """Test OutputManager with custom settings."""
        manager = OutputManager(
            "/tmp/custom", create_subdirs=False, organize_by_date=True
        )
        assert manager.base_output_dir == Path("/tmp/custom")
        assert manager.create_subdirs is False
        assert manager.organize_by_date is True

    def test_create_output_structure_default(self):
        """Test default output directory structure creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)
            track_name = "test_song"

            structure = manager.create_output_structure(track_name)

            assert structure["success"] is True
            assert structure["track_dir"].exists()
            assert structure["stems_dir"].exists()
            assert "test_song" in str(structure["track_dir"])

    def test_create_output_structure_no_subdirs(self):
        """Test output structure without subdirectories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir, create_subdirs=False)
            track_name = "test_song"

            structure = manager.create_output_structure(track_name)

            assert structure["success"] is True
            assert structure["track_dir"] == manager.base_output_dir

    def test_organize_stem_files(self):
        """Test stem file organization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            # Create test stem files
            stem_files = {}
            for stem in ["drums", "bass", "vocals", "other"]:
                test_file = Path(temp_dir) / f"{stem}.wav"
                test_file.touch()
                stem_files[stem] = str(test_file)

            track_name = "test_song"
            result = manager.organize_stem_files(stem_files, track_name)

            assert result["success"] is True
            assert len(result["organized_files"]) == 4

    def test_generate_metadata(self):
        """Test metadata generation."""
        manager = OutputManager("/tmp/output")

        separation_result = {
            "audio_file": "/tmp/input.mp3",
            "model_used": "htdemucs",
            "device_used": "cpu",
        }

        processing_results = {
            "processed_stems": {
                "drums": {"metrics": {"peak_amplitude": 0.8}},
                "vocals": {"metrics": {"peak_amplitude": 0.9}},
            }
        }

        metadata = manager.generate_metadata(
            "test_song", separation_result, processing_results
        )

        assert metadata["track_name"] == "test_song"
        assert metadata["source_file"] == "/tmp/input.mp3"
        assert metadata["model_used"] == "htdemucs"
        assert "timestamp" in metadata
        assert "stems" in metadata

    def test_save_metadata(self):
        """Test metadata saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            metadata = {"track_name": "test_song", "timestamp": "2023-01-01T00:00:00"}

            output_dir = Path(temp_dir) / "test_song"
            result = manager.save_metadata(metadata, output_dir)

            assert result["success"] is True
            metadata_file = output_dir / "metadata.json"
            assert metadata_file.exists()

            # Verify content
            with open(metadata_file) as f:
                saved_metadata = json.load(f)
            assert saved_metadata["track_name"] == "test_song"

    def test_create_summary_report(self):
        """Test summary report creation."""
        manager = OutputManager("/tmp/output")

        separation_result = {
            "success": True,
            "model_used": "htdemucs",
            "stems": {"drums": "/tmp/drums.wav"},
        }

        processing_results = {
            "success": True,
            "processed_stems": {"drums": {"metrics": {"duration_seconds": 180}}},
        }

        output_paths = {
            "track_dir": Path("/tmp/output/test_song"),
            "stems_dir": Path("/tmp/output/test_song/stems"),
        }

        report = manager.create_summary_report(
            "test_song", separation_result, processing_results, output_paths
        )

        assert "Track Name" in report
        assert "test_song" in report
        assert "Model Used" in report
        assert "htdemucs" in report

    def test_cleanup_temp_files(self):
        """Test temporary file cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            # Create test files
            temp_files = []
            for i in range(3):
                test_file = Path(temp_dir) / f"temp_{i}.wav"
                test_file.touch()
                temp_files.append(str(test_file))

            # Verify files exist
            for file_path in temp_files:
                assert Path(file_path).exists()

            # Clean up
            manager.cleanup_temp_files(temp_files)

            # Verify files are removed
            for file_path in temp_files:
                assert not Path(file_path).exists()

    def test_get_output_summary(self):
        """Test output summary generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            # Create test output structure
            track_dir = Path(temp_dir) / "test_song"
            stems_dir = track_dir / "stems"
            stems_dir.mkdir(parents=True)

            # Create test stem files
            for stem in ["drums", "bass", "vocals", "other"]:
                (stems_dir / f"{stem}.wav").touch()

            output_paths = {"track_dir": track_dir, "stems_dir": stems_dir}

            summary = manager.get_output_summary(output_paths)

            assert summary["track_directory"] == str(track_dir)
            assert summary["stems_directory"] == str(stems_dir)
            assert len(summary["stem_files"]) == 4

    def test_validate_output_files(self):
        """Test output file validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            # Create test files
            stem_files = []
            for stem in ["drums", "bass", "vocals", "other"]:
                test_file = Path(temp_dir) / f"{stem}.wav"
                test_file.touch()
                stem_files.append(str(test_file))

            validation = manager.validate_output_files(stem_files)

            assert validation["all_exist"] is True
            assert len(validation["existing_files"]) == 4
            assert len(validation["missing_files"]) == 0

    def test_validate_output_files_missing(self):
        """Test output file validation with missing files."""
        manager = OutputManager("/tmp/output")

        stem_files = ["/tmp/nonexistent1.wav", "/tmp/nonexistent2.wav"]
        validation = manager.validate_output_files(stem_files)

        assert validation["all_exist"] is False
        assert len(validation["existing_files"]) == 0
        assert len(validation["missing_files"]) == 2

    def test_get_file_size_info(self):
        """Test file size information gathering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = OutputManager(temp_dir)

            # Create test file with known content
            test_file = Path(temp_dir) / "test.wav"
            test_content = b"test audio data" * 1000
            test_file.write_bytes(test_content)

            size_info = manager.get_file_size_info([str(test_file)])

            assert size_info["total_size_bytes"] == len(test_content)
            assert size_info["total_size_mb"] > 0
            assert len(size_info["file_sizes"]) == 1
