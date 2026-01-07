# Technology Research: Cross-Platform Desktop GUI

**Feature**: Cross-Platform Desktop GUI for Music Stem Separator
**Date**: 2026-01-07
**Status**: Complete

## Executive Summary

This document presents the research findings and technology decisions for implementing a cross-platform desktop GUI for the music stem separator application. The key decisions are:

1. **GUI Framework**: **PyQt6** (with fallback to Tkinter if licensing is a concern)
2. **Packaging**: **PyInstaller** for both platforms
3. **Settings Storage**: **platformdirs** + **JSON**
4. **Progress Communication**: **Threading with Queue** + **Qt Signals/Slots**

## 1. GUI Framework Selection

### Requirements Recap
- Cross-platform (macOS 11+ and Windows 10+)
- Modern, native appearance
- File drag-and-drop support
- Progress bar and status widgets
- Bundle into standalone executables
- Python 3.12+ compatible
- Active maintenance

### Frameworks Evaluated

| Framework | Bundle Size | Platform Integration | Packaging Ease | Licensing | Maintenance | Learning Curve | Drag-Drop |
|-----------|-------------|---------------------|----------------|-----------|-------------|----------------|-----------|
| **PyQt6** | 80-150MB | Excellent (native widgets) | Easy (PyInstaller) | GPL/Commercial | Active (Qt Company) | Medium | Built-in |
| **PySide6** | 80-150MB | Excellent (native widgets) | Easy (PyInstaller) | LGPL (free) | Active (Qt Company) | Medium | Built-in |
| **Tkinter** | 20-40MB | Basic (dated look) | Easy (built-in) | PSF License | Python core | Low | Custom needed |
| **wxPython** | 60-100MB | Good (native) | Medium | wxWindows | Active | Medium | Built-in |
| **Flet** | 100-200MB | Web-based (Flutter) | Easy | MIT | Active (2024+) | Low | Built-in |
| **NiceGUI** | 50-100MB | Web-based | Easy | MIT | Active (2024+) | Low | Built-in |

### Decision: PyQt6 (Primary) / PySide6 (Alternative)

**Rationale**:
1. **Native appearance**: Uses native OS widgets, not web-based rendering
2. **Rich widget library**: Progress bars, file dialogs, drag-drop all built-in
3. **Excellent documentation**: Extensive docs and community resources
4. **Proven track record**: Used by many professional desktop apps
5. **Python 3.12+ support**: Fully compatible
6. **Packaging support**: Well-tested with PyInstaller

**Why not others**:
- **Tkinter**: Dated appearance, would require significant custom styling
- **Flet/NiceGUI**: Web-based UI feels less native, larger bundle sizes
- **wxPython**: Smaller community, less modern documentation

**Licensing consideration**:
- PyQt6 requires GPL or commercial license for distribution
- PySide6 (LGPL) is a drop-in replacement if licensing is a concern
- For this open-source project, either works fine

### Alternative Path
If PyQt6/PySide6 proves too complex:
- **Fallback to CustomTkinter**: Modern-styled Tkinter library
- Bundle size: ~30-50MB
- Easier learning curve
- Acceptable appearance for v1

## 2. Application Packaging

### Requirements Recap
- Bundle Python runtime
- Support macOS 11+ and Windows 10+
- Handle PyTorch and AI models
- Create DMG (macOS) and MSI/EXE (Windows)
- Target <500MB bundle (excluding models)

### Packaging Tools Evaluated

| Tool | Bundle Size | Reliability | Platform Support | Installer Creation | ML/PyTorch Support | Active Dev |
|------|-------------|-------------|------------------|-------------------|-------------------|------------|
| **PyInstaller** | 100-300MB | High | macOS + Windows | Via scripts | Good (tested) | Active |
| **py2app** | 100-250MB | High | macOS only | DMG via tools | Good | Active |
| **cx_Freeze** | 100-300MB | Medium | macOS + Windows | MSI support | Medium | Active |
| **Briefcase** | 150-400MB | Medium | All platforms | DMG + MSI | Medium | Active (BeeWare) |
| **Nuitka** | 50-150MB | Medium | All platforms | Via scripts | Growing | Active |

### Decision: PyInstaller (Primary)

**Rationale**:
1. **Proven reliability**: Most widely used Python packager
2. **ML support**: Well-tested with PyTorch, NumPy, etc.
3. **Cross-platform**: Single tool for both macOS and Windows
4. **Community support**: Large community, many examples
5. **Hook system**: Handles complex dependencies automatically

**Platform-specific packaging**:
- **macOS**: PyInstaller → .app bundle → `create-dmg` tool for DMG
- **Windows**: PyInstaller → .exe → Inno Setup or NSIS for installer

**Bundle size strategy**:
- Exclude AI models from bundle (download on-demand, same as CLI)
- Use `--onefile` for single executable OR `--onedir` for faster startup
- Optimize with `--exclude-module` for unused dependencies
- Expected final bundle: 150-300MB (without models)

**Alternative**: Nuitka for smaller bundles if PyInstaller proves too large

## 3. Settings Persistence

### Requirements Recap
- Platform-standard locations (~/Library/Application Support on macOS, %APPDATA% on Windows)
- Simple key-value storage
- No external database
- Human-readable format

### Decision: platformdirs + JSON

**Components**:
1. **Path resolution**: `platformdirs` library (actively maintained fork of `appdirs`)
2. **Storage format**: JSON files
3. **Structure**: Single `settings.json` file

**Example structure**:
```python
from platformdirs import user_config_dir
import json
from pathlib import Path

class SettingsManager:
    def __init__(self, app_name="Stembler"):
        config_dir = Path(user_config_dir(app_name))
        config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = config_dir / "settings.json"
        self.defaults = {
            "output_directory": str(Path.home() / "Music" / "Stembler Output"),
            "model": "htdemucs",
            "enhancement_enabled": True,
            "spotify_client_id": "",
            "spotify_client_secret": "",
        }

    def load(self):
        if not self.settings_file.exists():
            return self.defaults.copy()
        try:
            with open(self.settings_file) as f:
                return {**self.defaults, **json.load(f)}
        except Exception:
            return self.defaults.copy()

    def save(self, settings):
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
```

**Rationale**:
- **platformdirs**: Modern, maintained, cross-platform
- **JSON**: Human-readable, built-in to Python, simple
- **Single file**: Easy to backup, debug, reset

**Security note**:
- Spotify credentials stored in plain JSON (same as CLI currently)
- For v2, consider using `keyring` library for secure credential storage
- Current approach acceptable for v1 (user's local machine only)

## 4. Progress Communication Architecture

### Requirements Recap
- Real-time updates during processing
- Non-blocking UI
- Integrates with existing processing logic
- Thread-safe

### Decision: Threading + Queue + Qt Signals

**Architecture**:
```python
# Worker thread runs processing
class ProcessingWorker(QThread):
    progress_update = pyqtSignal(dict)  # Emits progress data
    finished = pyqtSignal(dict)         # Emits final result
    error = pyqtSignal(str)             # Emits error message

    def run(self):
        # Run process_track() in background thread
        # Emit signals for progress updates
```

**Progress callback approach**:
```python
def process_track_with_progress(input_path, callback=None):
    """Modified process_track that accepts progress callback"""
    if callback:
        callback({"stage": "input_processing", "percent": 10})

    # ... existing processing logic ...

    if callback:
        callback({"stage": "separating_stems", "percent": 50})
```

**Rationale**:
- **Qt threading**: Built-in, safe, well-documented
- **Signals/Slots**: Thread-safe communication to UI
- **Minimal changes**: Existing `process_track()` gets optional callback parameter
- **CLI compatibility**: Callback is optional, CLI passes `None`

**Alternative considered**:
- asyncio: More complex, would require rewriting processing logic
- multiprocessing: Overkill for this use case, harder to debug

## 5. CLI/GUI Code Sharing

### Decision: Extract Shared Processing Logic

**Refactoring approach**:
1. Move `process_track()` from `cli.py` to `shared/process_track.py`
2. Add optional `progress_callback` parameter
3. Both CLI and GUI import and use the shared function

**Structure**:
```python
# src/music_stem_separator/shared/process_track.py
def process_track(input_path, output_dir, model_name="htdemucs",
                  device=None, enable_enhancement=True,
                  progress_callback=None):
    """
    Shared processing logic for both CLI and GUI.

    Args:
        progress_callback: Optional function(dict) for progress updates
                          Format: {"stage": str, "percent": int, "message": str}
    """
    # Existing processing logic with progress callbacks added
    if progress_callback:
        progress_callback({"stage": "starting", "percent": 0, "message": "Initializing..."})
    # ... rest of implementation ...
```

**CLI usage** (unchanged behavior):
```python
# cli.py
from .shared.process_track import process_track

def main():
    result = process_track(input_path, output_dir, model_name)  # No callback
```

**GUI usage**:
```python
# gui/controllers/processing_controller.py
from ...shared.process_track import process_track

def on_progress(progress_data):
    # Update UI with progress
    self.progress_bar.setValue(progress_data["percent"])

result = process_track(input_path, output_dir, model_name,
                      progress_callback=on_progress)
```

**Rationale**:
- **No CLI changes**: Default behavior preserved (callback=None)
- **Code reuse**: Both interfaces use identical processing logic
- **Easy testing**: Shared function can be unit tested once

## Implementation Recommendations

### Phase 1: Proof of Concept
1. Build minimal PyQt6 app with file picker and button
2. Test PyInstaller packaging on both platforms
3. Verify bundle size and startup time
4. Confirm drag-drop works

### Phase 2: Core Functionality
1. Extract `process_track()` to shared module
2. Add progress callbacks to processing pipeline
3. Build main window with progress display
4. Test end-to-end processing

### Phase 3: Settings & Polish
1. Implement settings manager with platformdirs
2. Build settings panel UI
3. Add Spotify credential validation
4. Implement "Open Output Folder" button

### Phase 4: Packaging & Distribution
1. Create PyInstaller spec files for each platform
2. Build DMG installer for macOS (using `create-dmg`)
3. Build Windows installer (using Inno Setup or NSIS)
4. Test installers on clean VMs

## Open Questions Resolved

1. **Auto-update functionality**: Out of scope for v1 (confirmed)
2. **GPU detection**: Automatic (same as CLI) (confirmed)
3. **First-run tutorial**: Not needed if defaults work out of box (confirmed)
4. **Log file separation**: Yes, separate `gui.log` and `cli.log` (decided)

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PyQt6 bundle too large | High | Fall back to Tkinter/CustomTkinter |
| PyInstaller reliability issues | High | Test early, consider Nuitka alternative |
| Progress updates too slow | Medium | Optimize callback frequency |
| Settings corruption | Low | Always fall back to defaults |
| Platform-specific bugs | Medium | Test on multiple machines per platform |

## Technology Stack Summary

**Final Stack**:
- **GUI**: PyQt6 (or PySide6 if licensing concern)
- **Packaging**: PyInstaller
- **Settings**: platformdirs + JSON
- **Progress**: Threading + Qt Signals
- **Installers**: create-dmg (macOS), Inno Setup (Windows)

**Dependencies to add** (to pyproject.toml):
```toml
[project.optional-dependencies]
gui = [
    "PyQt6>=6.6.0",
    "platformdirs>=4.0.0",
]
```

**Entry point to add**:
```toml
[project.scripts]
stem-separator-gui = "music_stem_separator.gui_main:main"
```

---

**Research completed**: 2026-01-07
**Approved for Phase 1**: Ready to proceed with data model and contracts
