# TODO - Known Issues & Future Work

## Resolved Issues

### ✅ Spotify Downloads Fixed (2025-10-31)

**Issue:** Spotify track downloads were failing with "The downloaded file is empty" error.

**Root Cause:**
- `spotdl 4.2.9` required `yt-dlp < 2025.0.0`
- YouTube API changes broke `yt-dlp 2024.12.23`
- Project was locked to incompatible versions

**Resolution:**
- spotdl released v4.3.0+ which removed the `< 2025.0.0` constraint
- Upgraded to `spotdl 4.4.3` and `yt-dlp 2025.10.22`
- Spotify downloads now working as expected

**How it was fixed:**
```bash
uv lock --upgrade-package spotdl
uv sync
```

**Resolved:** 2025-10-31

## High Priority

None currently!

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
