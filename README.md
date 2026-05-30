# Music Stem Separator 🎵

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI-powered music stem separation tool that extracts drums, bass, vocals, and other instruments from audio files using state-of-the-art machine learning models.

## ✨ Features

- **🎯 Stem Separation**: Extract drums, bass, vocals, and other instruments (6-stem models such as `htdemucs_6s` are supported too)
- **📱 Flexible Input**: Process local audio files, Spotify tracks, or direct audio URLs
- **🤖 Multiple AI Models**: Support for various Demucs models for optimal results
- **🎛️ Audio Enhancement**: Optional post-processing for improved quality (bass/drums are left unbrightened)
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
2. Create a `.env` file in the project root:
   ```
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   ```
3. Run using one of the options below

📖 **Detailed setup instructions**: See [SETUP.md](SETUP.md)

### Basic Usage

```bash
# Separate a local MP3 file
uv run stem-separator song.mp3

# Process a Spotify track.
# A .env file in the project root is loaded automatically:
uv run stem-separator "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

# Alternatively, pass the credentials explicitly with inline env vars:
SPOTIFY_CLIENT_ID=xxx SPOTIFY_CLIENT_SECRET=yyy uv run stem-separator "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

# Process a direct audio URL
uv run stem-separator "https://example.com/audio.mp3"

# Use a specific model with custom output directory
uv run stem-separator song.mp3 --model htdemucs_ft --output ./my_stems

# Disable audio enhancement for faster processing
uv run stem-separator song.mp3 --no-enhance

# Cap the separation step at 10 minutes
uv run stem-separator song.mp3 --timeout 600

# Enable verbose output
uv run stem-separator song.mp3 --verbose

# Process different audio formats
uv run stem-separator song.wav
uv run stem-separator song.flac
uv run stem-separator song.m4a
```

## 📖 Detailed Usage

### Command Line Options

```bash
uv run stem-separator [OPTIONS] INPUT_PATH

Arguments:
  INPUT_PATH    Path to audio file or Spotify URL

Options:
  -o, --output TEXT     Output directory (default: ./output)
  -m, --model TEXT      Demucs model to use (default: htdemucs)
  -d, --device TEXT     Device to use (cpu, cuda, or auto-detect)
  --no-enhance          Disable audio enhancement processing
  --timeout INTEGER     Max seconds for the separation step (default: 1800)
  -v, --verbose         Enable verbose output
  --version             Show version and exit
  --help                Show help message
```

### Supported Input Formats

- **Local Files**: MP3, WAV, FLAC, M4A, AAC, OGG ✅
- **Spotify URLs**: Direct track links and URIs ✅
  - `https://open.spotify.com/track/...`
  - `spotify:track:...`
- **Direct Audio URLs**: `https://.../audio.mp3` ✅
  (only public hosts are allowed; private/loopback addresses are blocked)

### Available Models

- `htdemucs` (default) - High-quality general purpose model (4 stems)
- `htdemucs_ft` - Fine-tuned version for better quality (4 stems)
- `htdemucs_6s` - 6-stem model (adds piano and guitar)
- `hdemucs_mmi` - Hybrid Demucs trained on the MMI dataset
- `mdx_extra` - Alternative model with different characteristics

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
uv sync --extra dev

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
│   ├── url_downloader.py   # Direct audio URL downloads (with SSRF guard)
│   ├── stem_processor.py   # Audio enhancement
│   └── output_manager.py   # File organization
├── tests/                  # Test suite
├── samples/               # Sample audio files (gitignored)
├── output/                # Generated stems (gitignored)
└── pyproject.toml         # Project configuration
```

## 🧪 Testing

The project uses pytest for testing (currently ~65% coverage):

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
- `requests` - Direct audio URL downloads
- `python-dotenv` - Loads Spotify credentials from `.env`

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
- **Output Quality**: High-fidelity 32-bit float WAV files

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
