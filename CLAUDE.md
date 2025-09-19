# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python music stem separation application that extracts drums, bass, vocals, and other instruments from MP3 files or Spotify tracks using AI models (Demucs). The project is currently in early planning/setup phase.

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

# Main application
uv run stem-separator song.mp3   # Process local MP3
uv run stem-separator https://open.spotify.com/track/... # Process Spotify track
```

## Architecture

The planned modular architecture includes:

- **src/separator.py** - Core Demucs AI model wrapper for stem separation
- **src/spotify_handler.py** - Spotify track download functionality using spotdl
- **src/input_processor.py** - Input validation and routing logic
- **src/stem_processor.py** - Audio processing and enhancement
- **src/output_manager.py** - File organization and output management
- **stem_separator_cli.py** - Main CLI entry point using Click framework

## Key Technologies

- **Demucs** - AI-powered audio source separation
- **UV** - Python package and environment management
- **librosa** - Audio processing library
- **spotdl** - Spotify track downloading
- **click** - CLI framework
- **pytest** - Testing framework

## Development Approach

- Test-driven development with 80%+ coverage requirement
- Modular design for easy extension and model swapping
- Support for multiple Demucs models (htdemucs_ft, etc.)
- Processing target: under 2 minutes per average song

## Output Structure

Separated stems will be organized in an `output/` directory with individual WAV files for each stem (drums, bass, vocals, other).