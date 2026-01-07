# Implementation Plan: Cross-Platform Desktop GUI

**Branch**: `001-desktop-gui` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-desktop-gui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a cross-platform desktop GUI for the music stem separator that enables non-technical users to separate audio stems through drag-and-drop file selection while maintaining full CLI backward compatibility. The GUI will provide visual progress feedback, settings management, and support for local files and Spotify URLs, targeting macOS and Windows platforms.

## Technical Context

**Language/Version**: Python 3.12+ (matching existing CLI)
**Primary Dependencies**: PyQt6 (GUI framework), platformdirs (config paths), PyInstaller (packaging)
**Storage**: File-based user settings in platform-standard config directories (~/Library/Application Support on macOS, AppData on Windows), JSON format
**Testing**: pytest (existing test infrastructure) + Qt test fixtures for GUI components
**Target Platform**: macOS 11+ and Windows 10+ desktop applications
**Project Type**: Single project (extending existing CLI codebase)
**Performance Goals**: <3s application startup, <2s UI responsiveness for progress updates, stem separation performance same as CLI (1-3 min per song)
**Constraints**: <500MB application bundle size (excluding models), must not modify existing CLI behavior, must bundle Python runtime for non-technical users
**Scale/Scope**: Single-file processing (no batch operations), 5 main UI screens (main processing, settings, progress, about, first-run setup), ~17 functional requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: No constitution violations detected (constitution template not yet populated for this project).

**Notes**:
- The project currently has no defined constitution principles
- This feature extends existing CLI functionality without replacing it
- Standard software engineering practices will be followed
- Will re-check after Phase 1 design artifacts are created

## Project Structure

### Documentation (this feature)

```text
specs/001-desktop-gui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── gui-api.md       # Internal API contract between GUI and processing logic
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/music_stem_separator/
├── __init__.py              # [EXISTING] Package initialization
├── cli.py                   # [EXISTING] CLI entry point
├── input_processor.py       # [EXISTING] Input validation and routing
├── separator.py             # [EXISTING] Core Demucs wrapper
├── spotify_handler.py       # [EXISTING] Spotify download
├── stem_processor.py        # [EXISTING] Audio enhancement
├── output_manager.py        # [EXISTING] File organization
├── url_downloader.py        # [EXISTING] URL download handler
├── gui/                     # [NEW] GUI module
│   ├── __init__.py
│   ├── main_window.py       # Main application window
│   ├── widgets/             # Custom UI widgets
│   │   ├── __init__.py
│   │   ├── file_input.py    # Drag-drop file input widget
│   │   ├── progress_display.py  # Progress bar and status
│   │   └── settings_panel.py    # Settings configuration
│   ├── controllers/         # UI controllers
│   │   ├── __init__.py
│   │   ├── processing_controller.py  # Manages processing flow
│   │   └── settings_controller.py    # Settings management
│   ├── models/              # GUI-specific data models
│   │   ├── __init__.py
│   │   ├── processing_job.py        # Processing job state
│   │   └── user_settings.py         # User preferences
│   └── utils/               # GUI utilities
│       ├── __init__.py
│       ├── platform_utils.py        # Platform-specific helpers
│       └── progress_tracker.py      # Progress estimation
├── gui_main.py              # [NEW] GUI entry point
└── shared/                  # [NEW] Shared logic between CLI and GUI
    ├── __init__.py
    └── process_track.py     # Extracted from cli.py for reuse

tests/
├── test_cli.py              # [EXISTING] CLI tests
├── test_input_processor.py  # [EXISTING]
├── test_separator.py        # [EXISTING]
├── test_spotify_handler.py  # [EXISTING]
├── test_stem_processor.py   # [EXISTING]
├── test_output_manager.py   # [EXISTING]
├── test_url_downloader.py   # [EXISTING]
└── test_gui/                # [NEW] GUI tests
    ├── __init__.py
    ├── test_main_window.py
    ├── test_processing_controller.py
    ├── test_settings_controller.py
    ├── test_processing_job.py
    └── test_user_settings.py

packaging/                   # [NEW] Distribution packaging
├── macos/
│   ├── build_dmg.sh         # macOS DMG builder
│   └── Info.plist           # macOS app metadata
└── windows/
    ├── build_msi.py         # Windows installer builder
    └── app.manifest         # Windows app manifest
```

**Structure Decision**: Single project structure (Option 1) is selected because the GUI is an extension of the existing CLI application, sharing the same core processing logic. The GUI will be implemented as a new module (`src/music_stem_separator/gui/`) alongside the existing CLI code, with shared processing logic extracted to a `shared/` module for reuse. This approach minimizes code duplication while maintaining clear separation between CLI and GUI concerns.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. Constitution template is not yet populated for this project.

## Phase 0: Research & Technology Selection

### Research Questions

The following technical decisions require research before implementation can begin:

1. **GUI Framework Selection**: Which Python GUI framework best meets our requirements?
   - **Requirements**: Cross-platform (macOS + Windows), modern appearance, file drag-drop support, progress bar widgets, ability to bundle into standalone executables, Python 3.12+ compatible, active maintenance
   - **Candidates**: PyQt6, Tkinter, Flet, NiceGUI, Electron with Python backend
   - **Research needed**: Compare bundle sizes, ease of packaging, platform integration quality, licensing concerns

2. **Application Packaging**: How to create standalone executables with bundled Python runtime?
   - **Requirements**: Non-technical users shouldn't need Python installed, <500MB bundle size, platform-standard installers (DMG for macOS, MSI for Windows)
   - **Candidates**: PyInstaller, py2app, cx_Freeze, Briefcase, Nuitka
   - **Research needed**: Compare reliability, bundle size, platform support, AI model bundling strategy

3. **Settings Persistence**: What's the best approach for cross-platform settings storage?
   - **Requirements**: Platform-standard locations, simple key-value storage, no external dependencies
   - **Candidates**: configparser, JSON files, platformdirs library for path resolution
   - **Research needed**: Best practices for each platform, migration strategy

4. **Progress Communication**: How should GUI receive progress updates from processing pipeline?
   - **Requirements**: Real-time updates during processing, doesn't block UI thread, integrates with existing processing logic
   - **Candidates**: Threading with queues, asyncio event loop, callback functions, signals/slots pattern
   - **Research needed**: Framework-specific patterns, thread safety considerations

5. **CLI/GUI Coexistence**: How to structure code for both CLI and GUI to share processing logic?
   - **Requirements**: No changes to existing CLI behavior, shared processing pipeline, minimal code duplication
   - **Approach**: Extract `process_track()` function from `cli.py` to `shared/process_track.py`, both CLI and GUI import and use it
   - **Research needed**: Verify no breaking changes to CLI, proper error handling for both contexts

### Research Tasks

- [ ] **Task 1**: Evaluate GUI frameworks (PyQt6, Tkinter, Flet, NiceGUI) for cross-platform desktop requirements
- [ ] **Task 2**: Test packaging tools (PyInstaller, py2app, Briefcase) with a simple GUI + ML model to measure bundle size and reliability
- [ ] **Task 3**: Research platform-standard settings directories and implement cross-platform path resolution
- [ ] **Task 4**: Design progress tracking architecture that works with both synchronous (CLI) and asynchronous (GUI) contexts
- [ ] **Task 5**: Prototype extraction of `process_track()` from CLI to ensure backward compatibility

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Key Entities**:
- **ProcessingJob**: Represents a stem separation operation with state, progress, and result tracking
- **UserSettings**: Persisted user preferences for output directory, model selection, and Spotify credentials
- **AudioInput**: Validated input source (file path or URL) with metadata
- **OutputBundle**: Collection of generated stem files with metadata

### API Contracts

See [contracts/gui-api.md](./contracts/gui-api.md) for complete interface definitions.

**Internal API** (between GUI and processing logic):
- `process_track_async()`: Non-blocking wrapper around existing `process_track()` function
- `ProgressCallback`: Protocol for receiving processing updates
- `SettingsManager`: Interface for loading/saving user preferences
- `InputValidator`: Interface for validating audio inputs before processing

### Quickstart

See [quickstart.md](./quickstart.md) for developer setup instructions and architecture overview.

## Phase 2: Task Breakdown

*Generated by `/speckit.tasks` command - NOT part of this plan output*

## Open Questions

1. Should we support auto-update functionality in v1, or wait for v2?
   - **Current spec**: Out of scope (manual downloads only)
   - **Consideration**: Many desktop apps expect auto-updates; manual updates may confuse users

2. Should GPU detection be automatic or require user configuration?
   - **Current assumption**: Automatic detection (same as CLI)
   - **Consideration**: May need UI to show detected GPU status

3. Should first-run experience include a tutorial or sample file?
   - **Current spec**: Default settings should work without configuration
   - **Consideration**: A 30-second sample file could help users verify installation

4. Should the GUI log files be separate from CLI log files?
   - **Current assumption**: Separate logs (gui.log vs cli.log)
   - **Consideration**: Easier troubleshooting if separate, but users may not know where to find them

## Next Steps

After this plan is approved:

1. **Phase 0 Research**: Execute research tasks and generate `research.md` with technology decisions
2. **Phase 1 Design**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Phase 2 Tasks**: Run `/speckit.tasks` to generate actionable implementation tasks
4. **Implementation**: Run `/speckit.implement` to execute tasks

## Assumptions & Constraints

**From Spec**:
- Users have disk space for stems (50-200MB per song)
- Users have internet for Spotify and model downloads
- Existing CLI architecture can be reused for GUI
- macOS 11+ and Windows 10+ target platforms
- Python runtime can be bundled
- GPU acceleration optional (CPU acceptable)

**Additional Technical Assumptions**:
- GUI framework will support dark mode (follows system preference)
- Application will require ~200-400MB installed size (excluding models)
- First launch will download AI models on-demand (same as CLI)
- Settings migration between versions is not required (v1 has no prior version)
- Crash reporting will use log files only (no telemetry)

**Constraints**:
- Must not modify existing CLI behavior
- Must follow platform UI conventions (HIG for macOS, Windows UI Guidelines)
- Must use platform-standard settings locations
- Installer must be simple (double-click, no terminal commands)
- Application bundle <500MB (excluding models)
