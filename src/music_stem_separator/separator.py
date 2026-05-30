"""Core audio stem separation module using Demucs."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import torch
except ImportError as e:
    raise ImportError(f"Required dependencies not installed: {e}")


logger = logging.getLogger(__name__)


class StemSeparator:
    """Core class for separating audio into stems using Demucs."""

    SUPPORTED_FORMATS = [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"]
    STEM_NAMES = ["drums", "bass", "vocals", "other"]
    # Default ceiling for a single Demucs run. Generous enough for CPU runs of a
    # full song, but bounded so a hung subprocess can't block forever.
    DEFAULT_TIMEOUT_SECONDS = 1800

    def __init__(
        self,
        model_name: str = "htdemucs",
        device: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        """
        Initialize the stem separator.

        Args:
            model_name: Demucs model to use (default: htdemucs)
            device: Device to run on ('cpu', 'cuda', or None for auto-detect)
            timeout: Max seconds to allow the Demucs subprocess to run
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.timeout = timeout
        self.supported_formats = self.SUPPORTED_FORMATS

        logger.info(
            f"Initialized StemSeparator with model: {model_name}, device: {self.device}"
        )

    def is_supported_format(self, file_path: Union[str, Path]) -> bool:
        """
        Check if the file format is supported.

        Args:
            file_path: Path to the audio file

        Returns:
            True if format is supported, False otherwise
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.supported_formats

    def separate_stems(
        self, audio_file: Union[str, Path], output_dir: Union[str, Path]
    ) -> Dict:
        """
        Separate audio file into stems.

        Args:
            audio_file: Path to input audio file
            output_dir: Directory to save separated stems

        Returns:
            Dictionary with separation results and metadata
        """
        try:
            audio_file = Path(audio_file)
            output_dir = Path(output_dir)

            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

            if not self.is_supported_format(audio_file):
                raise ValueError(f"Unsupported audio format: {audio_file.suffix}")

            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Separating stems for: {audio_file}")
            logger.info(f"Using model: {self.model_name}, device: {self.device}")

            # Use Demucs for separation (using CLI-style approach)
            import subprocess
            import sys

            cmd = [
                sys.executable,
                "-m",
                "demucs.separate",
                "--name",
                self.model_name,
                "--device",
                self.device,
                "--out",
                str(output_dir),
                str(audio_file),
            ]

            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=self.timeout
                )
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError(
                    f"Demucs separation timed out after {self.timeout}s"
                ) from exc

            if result.returncode != 0:
                raise RuntimeError(f"Demucs separation failed: {result.stderr}")

            # Discover the stems Demucs actually produced (count/names vary by
            # model, e.g. htdemucs_6s adds piano/guitar) and confirm they exist.
            track_name = audio_file.stem
            stem_paths = self.discover_stems(output_dir, track_name)
            if not stem_paths:
                raise RuntimeError(
                    "Demucs reported success but no stem files were found in "
                    f"{output_dir / self.model_name / track_name}"
                )

            return {
                "success": True,
                "audio_file": str(audio_file),
                "output_dir": str(output_dir),
                "model_used": self.model_name,
                "device_used": self.device,
                "stems": stem_paths,
                "track_name": track_name,
            }

        except Exception as e:
            logger.error(f"Stem separation failed: {str(e)}")
            return {"success": False, "audio_file": str(audio_file), "error": str(e)}

    def get_stem_paths(
        self, output_dir: Union[str, Path], track_name: str
    ) -> Dict[str, Path]:
        """
        Generate expected paths for separated stem files.

        Args:
            output_dir: Output directory
            track_name: Name of the track (without extension)

        Returns:
            Dictionary mapping stem names to their file paths
        """
        output_dir = Path(output_dir)

        # Demucs creates a subdirectory with the model name
        model_output_dir = output_dir / self.model_name / track_name

        stem_paths = {}
        for stem_name in self.STEM_NAMES:
            stem_file = model_output_dir / f"{stem_name}.wav"
            stem_paths[stem_name] = stem_file

        return stem_paths

    def discover_stems(
        self, output_dir: Union[str, Path], track_name: str
    ) -> Dict[str, Path]:
        """
        Discover the stem files Demucs actually wrote for a track.

        Unlike get_stem_paths (which predicts the standard 4 stems), this inspects
        the output directory so models with a different number of stems are handled
        correctly.

        Args:
            output_dir: Output directory passed to Demucs
            track_name: Name of the track (without extension)

        Returns:
            Dictionary mapping stem names (file stem) to existing file paths
        """
        model_output_dir = Path(output_dir) / self.model_name / track_name

        if not model_output_dir.is_dir():
            return {}

        return {
            stem_file.stem: stem_file
            for stem_file in sorted(model_output_dir.glob("*.wav"))
        }

    def verify_stems_exist(self, stem_paths: Dict[str, Path]) -> Dict[str, bool]:
        """
        Verify that all expected stem files were created.

        Args:
            stem_paths: Dictionary of stem names to file paths

        Returns:
            Dictionary mapping stem names to existence status
        """
        return {stem: path.exists() for stem, path in stem_paths.items()}

    def get_available_models(self) -> List[str]:
        """
        Get list of available Demucs models.

        Returns:
            List of available model names
        """
        try:
            # Common Demucs models
            return [
                "htdemucs",
                "htdemucs_ft",
                "htdemucs_6s",
                "hdemucs_mmi",
                "mdx_extra",
            ]
        except Exception as e:
            logger.warning(f"Could not retrieve model list: {e}")
            return ["htdemucs"]  # Default fallback
