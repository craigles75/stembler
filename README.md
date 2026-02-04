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
- **🖥️ Desktop GUI**: User-friendly drag-and-drop interface with:
  - Visual progress tracking with ETA
  - Persistent settings (model selection, output directory, Spotify credentials)
  - Error logging and user-friendly error messages
  - Cancellation support during processing
- **🔧 CLI Interface**: Powerful command-line tool for automation and scripting
- **🔀 Dual Interface**: GUI and CLI work independently - use whichever suits your workflow

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

#### Loading credentials from .env file

If you have a `.env` file with your credentials:

```bash
# Option 1: One-liner using env command (recommended)
env $(cat .env | xargs) uv run stem-separator "https://open.spotify.com/track/..."

# Option 2: Export variables first, then run
export $(cat .env | xargs)
uv run stem-separator "https://open.spotify.com/track/..."

# Option 3: Set variables directly (no .env file needed)
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
uv run stem-separator "https://open.spotify.com/track/..."
```

Note: Credentials remain active only for the current shell session.

### Basic Usage

#### GUI Application (Recommended for most users)

**macOS** — run from your existing clone:
```bash
uv sync --extra gui          # Install GUI dependencies (PyQt6)
uv run stem-separator-gui    # Launch the application
```

**Windows** — clone the repo on your Windows machine, then:
```bash
# Install uv if not already installed: https://docs.astral.sh/uv/
git clone https://github.com/craigles75/stembler.git
cd stembler
uv sync --extra gui          # Install GUI dependencies (PyQt6)
uv run stem-separator-gui    # Launch the application
```

Then simply:
1. **Drag and drop** an audio file onto the window, or click "Browse" to select one
2. **Optional**: Configure settings via File → Settings (model, output directory, Spotify credentials)
3. Click **"Separate Stems"** to start processing
4. Watch real-time progress with ETA and stage information
5. Click **"Open Output Folder"** to view your separated stems

**GUI Features**:
- **Settings Panel** (File → Settings): Configure model, output directory, enhancement, and Spotify credentials
- **About Dialog** (Help → About): View version info and credits
- **Error Logging**: Automatic error logging to `~/.config/Stembler/logs/` (or platform equivalent)
- **Cancel Processing**: Click "Cancel" during processing to safely stop

#### Command Line Interface (For automation & scripting)

```bash
# Separate a local MP3 file
uv run stem-separator song.mp3

# Process a Spotify track
uv run stem-separator "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

# Use a specific model with custom output directory
uv run stem-separator song.mp3 --model htdemucs_ft --output ./my_stems

# Disable audio enhancement for faster processing
uv run stem-separator song.mp3 --no-enhance

# Enable verbose output
uv run stem-separator song.mp3 --verbose

# Process different audio formats
uv run stem-separator song.wav
uv run stem-separator song.flac
uv run stem-separator song.m4a
```

## 📖 Detailed Usage

### GUI vs CLI: Choose Your Interface

Both interfaces provide the same core functionality, but work **completely independently**:

| Feature | GUI (`stem-separator-gui`) | CLI (`stem-separator`) |
|---------|---------------------------|------------------------|
| **Best For** | Non-technical users, visual feedback | Automation, scripting, batch processing |
| **Input Method** | Drag-and-drop or Browse button | Command-line arguments |
| **Progress Display** | Visual progress bar with ETA | Optional verbose output |
| **Settings** | Persistent settings panel (model, output dir, credentials) | Command-line flags only |
| **Output Location** | `~/Music/Stembler Output` (default, customizable) | `./output` or custom via `--output` |
| **Model Selection** | Via Settings panel (File → Settings) | Via `--model` flag |
| **Processing** | Background thread with cancel support | Foreground (blocks terminal) |
| **Error Handling** | User-friendly dialogs + log files | Stack traces to console |

**Key Point**: GUI and CLI use **separate, independent configurations**. Your CLI command-line preferences never affect GUI behavior, and vice versa. Both can be used on the same system without conflicts.

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
│   ├── cli.py                      # Command-line interface
│   ├── gui_main.py                 # GUI application entry point
│   ├── shared/
│   │   └── process_track.py        # Shared processing logic (CLI + GUI)
│   ├── gui/
│   │   ├── main_window.py          # Main GUI window
│   │   ├── models/                 # Data models
│   │   │   ├── audio_input.py      # Input validation
│   │   │   ├── processing_job.py   # Job tracking
│   │   │   ├── output_bundle.py    # Output management
│   │   │   └── user_settings.py    # User preferences
│   │   ├── widgets/                # UI components
│   │   │   ├── file_input.py       # Drag-drop input
│   │   │   ├── process_button.py   # Action button
│   │   │   ├── progress_display.py # Progress tracking
│   │   │   ├── result_display.py   # Results view
│   │   │   ├── settings_panel.py   # Settings dialog
│   │   │   └── about_dialog.py     # About dialog
│   │   ├── controllers/            # Business logic
│   │   │   ├── processing_controller.py
│   │   │   └── settings_controller.py
│   │   └── utils/                  # Helper functions
│   │       ├── platform_utils.py   # Cross-platform utilities
│   │       ├── error_handler.py    # Global error handling
│   │       ├── progress_tracker.py # ETA estimation
│   │       ├── settings_manager.py # Settings persistence
│   │       └── version.py          # Version utilities
│   ├── input_processor.py          # Input validation & routing
│   ├── separator.py                # Core Demucs wrapper
│   ├── spotify_handler.py          # Spotify download
│   ├── stem_processor.py           # Audio enhancement
│   └── output_manager.py           # File organization
├── tests/                          # Test suite
│   ├── test_cli.py                 # CLI tests
│   ├── test_shared_process_track.py # Shared logic tests
│   └── test_gui/                   # GUI tests (future)
├── specs/                          # Feature specifications
├── samples/                        # Sample audio files (gitignored)
├── output/                         # Generated stems (gitignored)
└── pyproject.toml                  # Project configuration
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

### GUI Dependencies (Optional)
- `PyQt6` - Cross-platform GUI framework
- `platformdirs` - Platform-specific directories

Install GUI dependencies with:
```bash
uv sync --extra gui
```

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
