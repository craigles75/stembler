# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python music stem separation application that extracts drums, bass, vocals, and other instruments from MP3 files or Spotify tracks using AI models (Demucs). The core pipeline (input handling, Demucs separation, stem enhancement, output organization) and CLI are implemented, with a pytest test suite.

## Development Commands

UV-based commands:

```bash
# Environment setup (installs runtime + dev dependencies)
uv sync --extra dev

# Testing
uv run pytest                              # Run all tests
uv run pytest tests/test_separator.py      # Run specific test file
uv run pytest --cov=music_stem_separator   # Run with coverage

# Code quality
uv run black src/ tests/         # Format code
uv run ruff check src/ tests/    # Lint code

# Main application
uv run stem-separator song.mp3                            # Process local MP3
uv run stem-separator "https://open.spotify.com/track/..."  # Process Spotify track
uv run stem-separator "https://example.com/audio.mp3"     # Process a direct audio URL
```

## Architecture

The application lives under `src/music_stem_separator/` and is wired together by
`cli.py:process_track`, which runs the pipeline: input → separate → enhance →
organize → report, then cleans up temp directories.

- **cli.py** - Click CLI entry point and the `process_track` pipeline orchestrator
- **input_processor.py** - Detects/validates input type (local file, Spotify URL, direct audio URL) and routes accordingly
- **separator.py** - Demucs wrapper; shells out to `python -m demucs.separate` (with a timeout) and discovers the stems Demucs actually produced
- **spotify_handler.py** - Spotify track download via spotdl; also exposes module-level `is_spotify_url` / `extract_track_id` helpers reused by the input processor
- **url_downloader.py** - Downloads direct audio URLs with an SSRF guard (blocks non-public hosts) and a max-size cap
- **stem_processor.py** - Audio enhancement, normalization, and fades (brightening is skipped for bass/drums)
- **output_manager.py** - Output directory structure, file organization, metadata, and summary report

The console entry point is `stem-separator` (defined in `pyproject.toml`).

## Key Technologies

- **Demucs** - AI-powered audio source separation
- **UV** - Python package and environment management
- **librosa** - Audio processing library
- **spotdl** - Spotify track downloading
- **click** - CLI framework
- **python-dotenv** - Loads Spotify credentials from a local `.env` at CLI startup
- **pytest** - Testing framework

## Development Approach

- pytest test suite (currently ~65% coverage; aiming higher)
- Modular design for easy extension and model swapping
- Supports multiple Demucs models, including those with non-standard stem counts
  (e.g. `htdemucs_6s` produces 6 stems) — stems are discovered dynamically rather
  than assumed to be drums/bass/vocals/other
- Processing target: under 2 minutes per average song (the separation step is
  bounded by a configurable `--timeout`, default 1800s)

## Output Structure

Stems are written to `output/<track_name>/stems/` as individual WAV files (one per
separated stem), with a `metadata.json` in the track directory. Intermediate working
directories (`temp`, `temp_stems`, `temp_processed`) are created during a run and
removed afterward.

## Notes for Future Changes

- Spotify credentials are read lazily at download time from `SPOTIFY_CLIENT_ID` /
  `SPOTIFY_CLIENT_SECRET` (auto-loaded from `.env`); never commit `.env`.
- `URLDownloader` intentionally blocks private/loopback/link-local hosts. Pass
  `allow_private_hosts=True` only for trusted/local testing.
- Spotify downloads go through spotdl → yt-dlp (YouTube Music / YouTube). The
  SoundCloud provider is deliberately excluded (its client_id scrape is broken).
  Audio providers can be overridden with `STEMBLER_AUDIO_PROVIDERS`. If downloads
  start failing with "YT-DLP download error", bump yt-dlp
  (`uv lock --upgrade-package yt-dlp && uv sync`) — it is pinned directly in
  `pyproject.toml` for this reason.