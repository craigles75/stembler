# Music Stem Separator - Project Overview

## What It Does
A Python application that takes an MP3 file or Spotify link and separates it into four individual audio stems: drums, bass, vocals, and other instruments. This enables remixing, sampling, karaoke creation, and music production workflows.

## Core Features
- **Dual Input Support**: Accept local MP3 files or Spotify track URLs
- **4-Stem Separation**: Extract drums, bass, vocals, and other instruments
- **High Quality Output**: Export individual WAV files for each stem
- **Multiple AI Models**: Support for various Demucs models for optimal results
- **CLI Interface**: Simple command-line usage for automation

## Technical Approach
- **Demucs** for AI-powered stem separation (same approach as bassline_transcription project)
- **UV** for Python package management and environment handling
- **Test-Driven Development** throughout the build process
- **Modular architecture** for easy extension and maintenance

## Project Structure
```
music_stem_separator/
├── src/
│   ├── separator.py          # Core Demucs wrapper
│   ├── spotify_handler.py    # Spotify download functionality
│   ├── input_processor.py    # Input validation & routing
│   ├── stem_processor.py     # Audio enhancement
│   └── output_manager.py     # File organization
├── tests/                     # Test files for each module
├── output/                    # Separated stems output
└── stem_separator_cli.py      # Main CLI entry point
```

## Usage Examples
```bash
# Install with UV
uv init music-stem-separator
uv pip install -e .

# Separate local MP3
uv run stem-separator song.mp3

# Process Spotify track
uv run stem-separator https://open.spotify.com/track/...

# Specify model and enhance output
uv run stem-separator song.mp3 --model htdemucs_ft --enhance
```

## Development Workflow
1. **Write Test First**: Define expected behavior with pytest
2. **Implement Feature**: Code to make tests pass
3. **Run Tests**: `uv run pytest` for continuous validation
4. **Check Coverage**: Maintain 80%+ test coverage
5. **Format & Lint**: `uv run black` and `uv run ruff`

## Key Dependencies
- `demucs` - AI stem separation
- `librosa` - Audio processing
- `spotdl` - Spotify downloading
- `click` - CLI framework
- `pytest` - Testing framework

## Implementation Timeline
- **Week 1**: Core separation module with tests
- **Week 2**: Spotify integration with TDD
- **Week 3**: Enhancement and output management
- **Week 4**: CLI and integration testing

## Success Metrics
- Clean separation of all 4 stems
- Support for both MP3 files and Spotify links
- Processing time under 2 minutes for average song
- Test coverage above 80%
- Modular design allowing easy model swapping

## Next Steps
1. Set up UV and Python environment
2. Create project structure
3. Write first test for stem separation
4. Implement core separator module
5. Add Spotify support
6. Build CLI interface
7. Package for distribution
