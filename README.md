# Music Stem Separator 🎵

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI-powered music stem separation tool that extracts drums, bass, vocals, and other instruments from audio files using state-of-the-art machine learning models.

## ✨ Features

- **🎯 4-Stem Separation**: Extract drums, bass, vocals, and other instruments
- **📱 Dual Input Support**: Process local audio files or Spotify tracks
- **🤖 Multiple AI Models**: Support for various Demucs models for optimal results
- **🎛️ Audio Enhancement**: Optional post-processing for improved quality
- **📁 Smart Output Organization**: Automatically organizes stems with metadata
- **⚡ High Performance**: GPU acceleration support for faster processing
- **🔧 CLI Interface**: Simple command-line usage for automation and scripting

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/craigles75/stembler.git
cd stembler

# Install with UV (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Spotify Setup

To use Spotify track downloading, you need Spotify API credentials:

1. Get Spotify API credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Set environment variables: `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`

📖 **Detailed setup instructions**: See [SETUP.md](SETUP.md)

### Basic Usage

```bash
# Separate a local MP3 file
stem-separator song.mp3

# Process a Spotify track
stem-separator "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

# Use a specific model with custom output directory
stem-separator song.mp3 --model htdemucs_ft --output ./my_stems

# Disable audio enhancement for faster processing
stem-separator song.mp3 --no-enhance

# Enable verbose output
stem-separator song.mp3 --verbose

# Process different audio formats
stem-separator song.wav
stem-separator song.flac
stem-separator song.m4a
```

## 📖 Detailed Usage

### Command Line Options

```bash
stem-separator [OPTIONS] INPUT_PATH

Arguments:
  INPUT_PATH    Path to audio file or Spotify URL

Options:
  -o, --output TEXT     Output directory (default: ./output)
  -m, --model TEXT      Demucs model to use (default: htdemucs)
  -d, --device TEXT     Device to use (cpu, cuda, or auto-detect)
  --no-enhance          Disable audio enhancement processing
  -v, --verbose         Enable verbose output
  --version             Show version and exit
  --help                Show help message
```

### Supported Input Formats

- **Local Files**: MP3, WAV, FLAC, M4A, and other common audio formats ✅
- **Spotify URLs**: Direct track links and URIs ✅
  - `https://open.spotify.com/track/...`
  - `spotify:track:...`

### Available Models

- `htdemucs` (default) - High-quality general purpose model
- `htdemucs_ft` - Fine-tuned version for better quality
- `mdx_extra` - Alternative model with different characteristics
- `mdx_q` - Quantized model for faster processing

### Output Structure

```
output/
└── [Track Name]/
    ├── stems/
    │   ├── [Track Name]_drums.wav
    │   ├── [Track Name]_bass.wav
    │   ├── [Track Name]_vocals.wav
    │   └── [Track Name]_other.wav
    └── metadata.json
```

## 🛠️ Development

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip
- CUDA-compatible GPU (optional, for faster processing)

### Development Setup

```bash
# Clone and setup
git clone https://github.com/craigles75/stembler.git
cd stembler

# Install development dependencies
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/music_stem_separator

# Format code
uv run black src/ tests/

# Lint code
uv run ruff check src/ tests/
```

### Project Structure

```
stembler/
├── src/music_stem_separator/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── input_processor.py  # Input validation & routing
│   ├── separator.py        # Core Demucs wrapper
│   ├── spotify_handler.py  # Spotify download functionality
│   ├── stem_processor.py   # Audio enhancement
│   └── output_manager.py   # File organization
├── tests/                  # Test suite
├── samples/               # Sample audio files (gitignored)
├── output/                # Generated stems (gitignored)
└── pyproject.toml         # Project configuration
```

## 🧪 Testing

The project uses pytest for testing with comprehensive coverage:

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_separator.py

# Run with coverage report
uv run pytest --cov=src/music_stem_separator --cov-report=html
```

## 📦 Dependencies

### Core Dependencies
- `demucs` - AI stem separation engine
- `librosa` - Audio processing and analysis
- `spotdl` - Spotify track downloading
- `click` - Command-line interface framework
- `torch` & `torchaudio` - PyTorch for ML models
- `numpy` & `scipy` - Numerical computing
- `soundfile` - Audio file I/O

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `ruff` - Fast Python linter

## 🎯 Use Cases

- **Music Production**: Create stems for remixing and sampling
- **Karaoke**: Extract vocal tracks for karaoke creation
- **Learning**: Study individual instrument parts
- **Remixing**: Isolate specific instruments for creative projects
- **Audio Analysis**: Analyze individual components of mixed audio

## ⚡ Performance

- **Processing Time**: 1-3 minutes per song (depending on model and hardware)
- **GPU Acceleration**: Significantly faster with CUDA-compatible GPU
- **Memory Usage**: ~2-4GB RAM for typical songs
- **Output Quality**: High-fidelity 24-bit WAV files

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Demucs](https://github.com/facebookresearch/demucs) - The amazing AI model for stem separation
- [SpotDL](https://github.com/spotDL/spotify-downloader) - Spotify track downloading
- [Librosa](https://librosa.org/) - Audio processing library

## 📞 Support

If you encounter any issues or have questions, please:

1. Check the [Issues](https://github.com/craigles75/stembler/issues) page
2. Create a new issue with detailed information
3. Include your system information and error messages

---

**Made with ❤️ by [Craig Penfold](https://github.com/craigles75)**
