"""Audio processing and enhancement for separated stems."""

import logging
import numpy as np
from pathlib import Path
from typing import Dict, Union, Tuple

try:
    import librosa
    import soundfile as sf
    from scipy import signal
except ImportError as e:
    raise ImportError(f"Required audio processing dependencies not installed: {e}")


logger = logging.getLogger(__name__)


class StemProcessor:
    """Processor for enhancing and manipulating separated audio stems."""

    def __init__(self, sample_rate: int = 44100, enable_enhancement: bool = True):
        """
        Initialize the stem processor.

        Args:
            sample_rate: Target sample rate for processing
            enable_enhancement: Whether to apply audio enhancement
        """
        self.sample_rate = sample_rate
        self.enable_enhancement = enable_enhancement

        logger.info(
            f"Initialized StemProcessor with sample_rate: {sample_rate}, enhancement: {enable_enhancement}"
        )

    def load_audio_file(self, file_path: Union[str, Path]) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return audio data and sample rate.

        Args:
            file_path: Path to audio file

        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio_data, sr = librosa.load(str(file_path), sr=self.sample_rate)
            logger.debug(
                f"Loaded audio file: {file_path}, duration: {len(audio_data)/sr:.2f}s"
            )
            return audio_data, sr

        except Exception as e:
            logger.error(f"Failed to load audio file {file_path}: {e}")
            raise

    def save_audio_file(
        self, audio_data: np.ndarray, output_path: Union[str, Path], sample_rate: int
    ) -> Dict:
        """
        Save audio data to file.

        Args:
            audio_data: Audio data array
            output_path: Output file path
            sample_rate: Sample rate for the audio

        Returns:
            Save operation result
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Ensure audio data is in valid range
            if not self.validate_audio_data(audio_data):
                raise ValueError("Invalid audio data")

            # Save as 32-bit float WAV for best quality
            sf.write(str(output_path), audio_data, sample_rate, subtype="FLOAT")

            logger.debug(f"Saved audio file: {output_path}")
            return {
                "success": True,
                "file_path": str(output_path),
                "duration_seconds": len(audio_data) / sample_rate,
                "sample_rate": sample_rate,
            }

        except Exception as e:
            logger.error(f"Failed to save audio file {output_path}: {e}")
            return {"success": False, "error": str(e)}

    def normalize_audio(
        self, audio_data: np.ndarray, max_db: float = -0.1
    ) -> np.ndarray:
        """
        Normalize audio to prevent clipping and achieve target peak level.

        Args:
            audio_data: Input audio data
            max_db: Target peak level in dB

        Returns:
            Normalized audio data
        """
        if len(audio_data) == 0:
            return audio_data

        # Find peak amplitude
        peak = np.max(np.abs(audio_data))

        if peak == 0:
            return audio_data

        # Calculate target amplitude from dB
        target_amplitude = 10 ** (max_db / 20.0)

        # Normalize to target level
        normalized = audio_data * (target_amplitude / peak)

        logger.debug(
            f"Normalized audio: peak {peak:.4f} -> {np.max(np.abs(normalized)):.4f}"
        )
        return normalized

    def apply_fade_in_out(
        self, audio_data: np.ndarray, fade_duration: float = 0.05
    ) -> np.ndarray:
        """
        Apply fade in and fade out to prevent clicks.

        Args:
            audio_data: Input audio data
            fade_duration: Fade duration in seconds

        Returns:
            Audio data with fades applied
        """
        if len(audio_data) == 0:
            return audio_data

        fade_samples = int(fade_duration * self.sample_rate)
        fade_samples = min(
            fade_samples, len(audio_data) // 4
        )  # Max 25% of total length

        if fade_samples <= 0:
            return audio_data

        # Create fade curves
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)

        # Apply fades
        faded_audio = audio_data.copy()
        faded_audio[:fade_samples] *= fade_in
        faded_audio[-fade_samples:] *= fade_out

        return faded_audio

    def enhance_audio_quality(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply audio enhancement techniques.

        Args:
            audio_data: Input audio data

        Returns:
            Enhanced audio data
        """
        if not self.enable_enhancement or len(audio_data) == 0:
            return audio_data

        try:
            enhanced = audio_data.copy()

            # Apply pre-emphasis filter to brighten the sound
            enhanced = librosa.effects.preemphasis(enhanced, coef=0.97)

            # Apply gentle high-frequency boost
            # Design a subtle high-shelf filter
            sos = signal.butter(
                2, 8000, btype="highpass", fs=self.sample_rate, output="sos"
            )
            high_freq = signal.sosfilt(sos, enhanced)

            # Mix original with high-frequency boosted version
            enhanced = 0.85 * enhanced + 0.15 * high_freq

            logger.debug("Applied audio enhancement")
            return enhanced

        except Exception as e:
            logger.warning(f"Audio enhancement failed, returning original: {e}")
            return audio_data

    def process_single_stem(
        self, input_file: Union[str, Path], output_file: Union[str, Path]
    ) -> Dict:
        """
        Process a single stem file with enhancement.

        Args:
            input_file: Input stem file path
            output_file: Output processed file path

        Returns:
            Processing result dictionary
        """
        try:
            # Load audio
            audio_data, sr = self.load_audio_file(input_file)

            # Validate audio data
            if not self.validate_audio_data(audio_data):
                raise ValueError("Invalid audio data loaded")

            # Apply processing steps
            if self.enable_enhancement:
                audio_data = self.enhance_audio_quality(audio_data)

            # Apply fade in/out
            audio_data = self.apply_fade_in_out(audio_data)

            # Normalize
            audio_data = self.normalize_audio(audio_data)

            # Save processed audio
            save_result = self.save_audio_file(audio_data, output_file, sr)

            if not save_result["success"]:
                return save_result

            return {
                "success": True,
                "input_file": str(input_file),
                "output_file": str(output_file),
                "processing_applied": self.enable_enhancement,
                "metrics": self.calculate_audio_metrics(audio_data),
            }

        except Exception as e:
            logger.error(f"Failed to process stem {input_file}: {e}")
            return {"success": False, "input_file": str(input_file), "error": str(e)}

    def process_stem_files(
        self, stem_files: Dict[str, Union[str, Path]], output_dir: Union[str, Path]
    ) -> Dict:
        """
        Process multiple stem files.

        Args:
            stem_files: Dictionary mapping stem names to file paths
            output_dir: Output directory for processed files

        Returns:
            Processing results for all stems
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {"success": True, "processed_stems": {}, "failed_stems": {}}

        for stem_name, input_file in stem_files.items():
            try:
                # Generate output filename
                input_path = Path(input_file)
                output_file = output_dir / f"{stem_name}_processed{input_path.suffix}"

                # Process the stem
                result = self.process_single_stem(input_file, output_file)

                if result["success"]:
                    results["processed_stems"][stem_name] = result
                else:
                    results["failed_stems"][stem_name] = result
                    results["success"] = False

            except Exception as e:
                logger.error(f"Failed to process stem {stem_name}: {e}")
                results["failed_stems"][stem_name] = {"error": str(e)}
                results["success"] = False

        logger.info(
            f"Processed {len(results['processed_stems'])}/{len(stem_files)} stems successfully"
        )
        return results

    def validate_audio_data(self, audio_data) -> bool:
        """
        Validate audio data array.

        Args:
            audio_data: Audio data to validate

        Returns:
            True if valid, False otherwise
        """
        if audio_data is None:
            return False

        if not isinstance(audio_data, np.ndarray):
            return False

        if len(audio_data) == 0:
            return False

        if not np.isfinite(audio_data).all():
            return False

        return True

    def calculate_audio_metrics(self, audio_data: np.ndarray) -> Dict:
        """
        Calculate metrics for audio data.

        Args:
            audio_data: Audio data array

        Returns:
            Dictionary of audio metrics
        """
        if not self.validate_audio_data(audio_data):
            return {"error": "Invalid audio data"}

        try:
            metrics = {
                "peak_amplitude": float(np.max(np.abs(audio_data))),
                "rms_level": float(np.sqrt(np.mean(audio_data**2))),
                "duration_seconds": len(audio_data) / self.sample_rate,
                "zero_crossings": int(librosa.zero_crossings(audio_data).sum()),
                "spectral_centroid": float(
                    np.mean(
                        librosa.feature.spectral_centroid(
                            y=audio_data, sr=self.sample_rate
                        )
                    )
                ),
            }

            # Calculate peak level in dB
            if metrics["peak_amplitude"] > 0:
                metrics["peak_db"] = 20 * np.log10(metrics["peak_amplitude"])
            else:
                metrics["peak_db"] = -np.inf

            return metrics

        except Exception as e:
            logger.warning(f"Failed to calculate audio metrics: {e}")
            return {"error": str(e)}

    def get_processing_settings(self) -> Dict:
        """
        Get current processing settings.

        Returns:
            Dictionary of current settings
        """
        return {
            "sample_rate": self.sample_rate,
            "enable_enhancement": self.enable_enhancement,
            "supported_formats": [".wav", ".flac", ".mp3", ".m4a"],
        }
