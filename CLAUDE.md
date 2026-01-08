# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python music stem separation application that extracts drums, bass, vocals, and other instruments from MP3 files or Spotify tracks using AI models (Demucs). The project includes both a command-line interface (CLI) and a cross-platform desktop GUI built with PyQt6.

## Development Commands

Based on the project overview, the following UV-based commands will be used:

```bash
# Environment setup
uv init music-stem-separator
uv pip install -e .

# Testing
uv run pytest                    # Run all tests
uv run pytest tests/test_file.py # Run specific test file

# Code quality
uv run black .                   # Format code
uv run ruff check .              # Lint code

# Main application - CLI
uv run stem-separator song.mp3   # Process local MP3
uv run stem-separator https://open.spotify.com/track/... # Process Spotify track

# Main application - GUI
uv run stem-separator-gui         # Launch desktop GUI application
```

## Architecture

### Core Processing Layer

- **src/shared/process_track.py** - Shared processing logic used by both CLI and GUI
- **src/separator.py** - Core Demucs AI model wrapper for stem separation
- **src/spotify_handler.py** - Spotify track download functionality using spotdl
- **src/input_processor.py** - Input validation and routing logic
- **src/stem_processor.py** - Audio processing and enhancement
- **src/output_manager.py** - File organization and output management

### CLI Interface

- **src/cli.py** - Command-line interface using Click framework
- Entry point: `stem-separator` command

### GUI Interface (PyQt6)

The desktop GUI follows an MVC-like architecture with clear separation of concerns:

#### Entry Point
- **src/gui_main.py** - GUI application entry point, initializes QApplication and error handler

#### Main Window
- **src/gui/main_window.py** - Main application window coordinating all components

#### Models (Data Layer)
- **src/gui/models/audio_input.py** - Input validation and type detection (local file, Spotify URL, direct URL)
- **src/gui/models/processing_job.py** - Job state tracking and management
- **src/gui/models/output_bundle.py** - Output file organization metadata
- **src/gui/models/user_settings.py** - User preferences (model, output dir, enhancement, credentials)

#### Controllers (Business Logic)
- **src/gui/controllers/processing_controller.py** - Manages background processing via QThread workers
- **src/gui/controllers/settings_controller.py** - Handles settings persistence and loading

#### Widgets (UI Components)
- **src/gui/widgets/file_input.py** - Drag-and-drop file input with validation
- **src/gui/widgets/process_button.py** - Start/Cancel button with state management
- **src/gui/widgets/progress_display.py** - Real-time progress tracking with ETA
- **src/gui/widgets/result_display.py** - Results display with "Open Folder" action
- **src/gui/widgets/settings_panel.py** - Settings dialog for user preferences
- **src/gui/widgets/about_dialog.py** - About dialog with version and credits

#### Utilities
- **src/gui/utils/error_handler.py** - Global exception handling with user-friendly error dialogs
- **src/gui/utils/progress_tracker.py** - Smart ETA estimation based on file size and model
- **src/gui/utils/settings_manager.py** - JSON-based settings persistence
- **src/gui/utils/platform_utils.py** - Cross-platform file operations
- **src/gui/utils/credential_utils.py** - Spotify credential validation
- **src/gui/utils/version.py** - Version information from pyproject.toml

### GUI Architecture Principles

1. **Separation of Concerns**: Clear boundaries between UI (widgets), business logic (controllers), and data (models)
2. **Thread Safety**: Background processing via QThread to prevent UI blocking
3. **Signal/Slot Pattern**: Qt's event-driven architecture for loose coupling
4. **Platform Independence**: Uses platformdirs for cross-platform paths
5. **Settings Persistence**: JSON-based settings stored in platform-specific config directories
6. **Error Handling**: Global exception handler with logging and user-friendly dialogs
7. **CLI/GUI Independence**: GUI and CLI share core processing but maintain separate configurations

## Key Technologies

- **Demucs** - AI-powered audio source separation
- **UV** - Python package and environment management
- **librosa** - Audio processing library
- **spotdl** - Spotify track downloading
- **click** - CLI framework
- **PyQt6** - Cross-platform GUI framework
- **platformdirs** - Platform-specific directory management
- **pytest** - Testing framework

## Development Approach

- Test-driven development with 80%+ coverage requirement
- Modular design for easy extension and model swapping
- Support for multiple Demucs models (htdemucs_ft, etc.)
- Processing target: under 2 minutes per average song

## Output Structure

Separated stems will be organized in an `output/` directory with individual WAV files for each stem (drums, bass, vocals, other).

## Active Technologies
- Python 3.12+ (matching existing CLI) (001-desktop-gui)
- File-based user settings in platform-standard config directories (~/Library/Application Support on macOS, AppData on Windows) (001-desktop-gui)

## Recent Changes
- 001-desktop-gui: Added Python 3.12+ (matching existing CLI)
