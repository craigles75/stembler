# TODO - Known Issues & Future Work

## High Priority

### Spotify Downloads Currently Broken (Dependency Issue)

**Issue:** Spotify track downloads are failing with "The downloaded file is empty" error.

**Root Cause:**
- `spotdl 4.2.9` requires `yt-dlp < 2025.0.0`
- YouTube has made API changes that break `yt-dlp 2024.12.23` (the version we're locked to)
- Newer `yt-dlp >= 2025.9.0` fixes YouTube issues, but is incompatible with current spotdl

**Current Status:**
- `filter_results = False` is correctly set in `spotify_handler.py:128`
- YouTube search finds videos successfully (19 results → filters to best match)
- Download attempt fails with empty file error

**Dependency Chain:**
```
our project
  └─ spotdl >= 4.0.0
      └─ yt-dlp >= 2024.11.4, < 2025.0.0  ← Locked to old version
```

**Workaround:**
Use local MP3 files instead:
```bash
stem-separator path/to/song.mp3
```

**Resolution Path:**
1. Monitor spotdl repository: https://github.com/spotDL/spotify-downloader
2. Wait for spotdl to update yt-dlp constraint (likely version 4.3.0+)
3. When updated, run: `uv lock --upgrade-package spotdl`
4. Test Spotify downloads again

**Files Modified:**
- `src/music_stem_separator/spotify_handler.py` - Set `filter_results = False` (line 128)

**Last Updated:** 2025-10-11

---

## Future Enhancements

### Web UI
- Gradio UI was attempted but hit dependency conflicts (Pydantic 2.12 + FastAPI + Gradio 4.x)
- Consider Streamlit as alternative when needed
- Files created but not working: `src/music_stem_separator/gradio_ui.py`

### Direct URL Downloads
- Consider adding support for direct audio URLs (MP3, WAV, FLAC links)
- Already partially implemented in `url_downloader.py`

### Additional Audio Sources
- YouTube direct downloads (without Spotify metadata)
- SoundCloud integration
- Bandcamp support

---

## Notes

- This project uses `uv` for dependency management
- `uv.lock` enforces exact versions for reproducibility
- UV's strict locking is actually protecting us from broken dependency combinations
