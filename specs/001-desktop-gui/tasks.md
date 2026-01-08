# Implementation Tasks: Cross-Platform Desktop GUI

**Feature**: 001-desktop-gui | **Branch**: `001-desktop-gui` | **Date**: 2026-01-07

## Overview

This document provides actionable implementation tasks for adding a cross-platform desktop GUI to the music stem separator. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 47
**MVP Scope**: Phase 3 (User Story 1 - Drag-and-Drop Processing) + Phase 4 (User Story 5 - CLI Compatibility)
**Estimated Parallel Opportunities**: 25 parallelizable tasks

## Implementation Strategy

### MVP-First Approach
1. **Phase 3 (US1)**: Minimal drag-and-drop GUI - proves value immediately
2. **Phase 4 (US5)**: CLI compatibility verification - ensures no regressions
3. **Phases 5-7**: Add remaining user stories incrementally

### Independent Testing
Each user story phase can be tested independently without requiring other phases to be complete. This enables:
- Parallel development of different stories
- Early user feedback on individual features
- Incremental delivery and validation

---

## Phase 1: Setup & Project Initialization

**Goal**: Set up development environment and install GUI dependencies.

### Tasks

- [X] T001 Add PyQt6 and platformdirs to project dependencies in pyproject.toml
- [X] T002 [P] Install GUI dependencies with uv sync --extra gui
- [X] T003 [P] Create src/music_stem_separator/gui/ directory structure per plan.md
- [X] T004 [P] Create src/music_stem_separator/shared/ directory for shared processing logic
- [X] T005 [P] Create tests/test_gui/ directory structure per plan.md
- [X] T006 [P] Create packaging/ directory structure with macos/ and windows/ subdirectories
- [X] T007 Verify existing CLI tests pass with pytest to establish baseline

---

## Phase 2: Foundational - Shared Processing Logic

**Goal**: Extract shared processing logic from CLI to enable reuse by both CLI and GUI without breaking existing functionality.

**Why Foundational**: Both CLI (US5) and GUI (US1) depend on this shared logic. Must complete before any user story implementation.

**Independent Test**: Run all existing CLI tests - they must pass without modification.

### Tasks

- [X] T008 Extract process_track() function from src/music_stem_separator/cli.py to src/music_stem_separator/shared/process_track.py
- [X] T009 Add optional progress_callback parameter to process_track() function
- [X] T010 Update src/music_stem_separator/cli.py to import process_track from shared module
- [X] T011 Verify CLI functionality unchanged by running existing CLI tests
- [X] T012 [P] Create test_shared_process_track.py to test callback mechanism

---

## Phase 3: User Story 1 - Simple Drag-and-Drop Processing (P1)

**Story Goal**: Non-technical users can drag an MP3 file into the GUI and get separated stems.

**Why P1**: Core value proposition - without this, there's no reason for the GUI to exist.

**Independent Test**:
1. Launch GUI application
2. Drag sample.mp3 onto window
3. Click "Separate Stems" button
4. Verify stems appear in output directory
5. Click "Open Output Folder" button
6. Verify folder opens in system file browser

### Data Models (US1)

- [X] T013 [P] [US1] Create ProcessingJob model in src/music_stem_separator/gui/models/processing_job.py
- [X] T014 [P] [US1] Create AudioInput model in src/music_stem_separator/gui/models/audio_input.py
- [X] T015 [P] [US1] Create OutputBundle model in src/music_stem_separator/gui/models/output_bundle.py

### UI Widgets (US1)

- [X] T016 [P] [US1] Create FileInputWidget with drag-drop support in src/music_stem_separator/gui/widgets/file_input.py
- [X] T017 [P] [US1] Create ProcessButton widget in src/music_stem_separator/gui/widgets/process_button.py
- [X] T018 [P] [US1] Create ResultDisplay widget with "Open Folder" button in src/music_stem_separator/gui/widgets/result_display.py

### Controllers (US1)

- [X] T019 [US1] Create ProcessingController in src/music_stem_separator/gui/controllers/processing_controller.py
- [X] T020 [US1] Implement ProcessingWorker (QThread) for background processing in processing_controller.py
- [X] T021 [US1] Connect process_track() callback to Qt signals for thread-safe UI updates
- [X] T022 [US1] Implement file validation logic using AudioInput model

### Main Window (US1)

- [X] T023 [US1] Create MainWindow class in src/music_stem_separator/gui/main_window.py
- [X] T024 [US1] Add FileInputWidget to MainWindow layout
- [X] T025 [US1] Add ProcessButton to MainWindow layout
- [X] T026 [US1] Add ResultDisplay to MainWindow layout
- [X] T027 [US1] Connect widgets to ProcessingController
- [X] T028 [US1] Implement error handling for invalid files with user-friendly messages

### Application Entry Point (US1)

- [X] T029 [US1] Create gui_main.py entry point with QApplication initialization
- [X] T030 [US1] Add stem-separator-gui script to pyproject.toml [project.scripts]
- [X] T031 [US1] Test GUI launches and displays main window

### Platform Integration (US1)

- [X] T032 [P] [US1] Implement open_folder() in src/music_stem_separator/gui/utils/platform_utils.py
- [X] T033 [P] [US1] Test "Open Output Folder" on macOS and Windows

---

## Phase 4: User Story 5 - CLI Compatibility Maintained (P1)

**Story Goal**: Existing CLI users can continue using their scripts without modification.

**Why P1**: Breaking existing workflows would alienate power users. Non-negotiable.

**Independent Test**:
1. Run `stem-separator sample.mp3` (existing CLI command)
2. Verify it works exactly as before GUI was added
3. Run `stem-separator --help` and verify all options still work
4. Verify GUI settings don't affect CLI behavior

### Tasks

- [X] T034 [P] [US5] Run full CLI test suite (pytest tests/test_cli.py) and verify 100% pass
- [X] T035 [P] [US5] Test CLI with all input types (local file, Spotify URL, direct URL)
- [X] T036 [P] [US5] Test CLI with all models (htdemucs, htdemucs_ft, mdx_extra, mdx_q)
- [X] T037 [P] [US5] Verify CLI and GUI use separate settings (no cross-contamination)
- [X] T038 [US5] Document CLI/GUI independence in README.md

---

## Phase 5: User Story 2 - Visual Progress Feedback (P2)

**Story Goal**: Users see real-time progress during processing to avoid thinking app has frozen.

**Why P2**: Processing takes 1-3 minutes. Without feedback, users will force-quit the app.

**Dependencies**: Requires US1 (basic GUI) to be complete.

**Independent Test**:
1. Process a 5-minute audio file
2. Verify progress bar updates every 2 seconds
3. Verify percentage changes from 0% to 100%
4. Verify estimated time remaining updates
5. Verify stage messages ("Loading model...", "Separating stems...")

### Tasks

- [X] T039 [P] [US2] Create ProgressDisplay widget in src/music_stem_separator/gui/widgets/progress_display.py
- [X] T040 [P] [US2] Add progress bar, percentage label, and ETA label to ProgressDisplay
- [X] T041 [P] [US2] Add status label for current stage message
- [X] T042 [US2] Create ProgressTracker utility in src/music_stem_separator/gui/utils/progress_tracker.py
- [X] T043 [US2] Implement time estimation logic based on file size and model
- [X] T044 [US2] Connect process_track() progress callbacks to ProgressDisplay via signals
- [X] T045 [US2] Add ProgressDisplay to MainWindow layout
- [X] T046 [US2] Test progress updates with 5-minute audio file

---

## Phase 6: User Story 3 - Spotify URL Processing (P3)

**Story Goal**: Users can paste Spotify URLs and download+process tracks automatically.

**Why P3**: Differentiating feature, but requires Spotify API setup first.

**Dependencies**: Requires US1 (basic GUI) and US4 (settings panel for credentials).

**Independent Test**:
1. Open settings and enter Spotify credentials
2. Paste https://open.spotify.com/track/... into input field
3. Click "Separate Stems"
4. Verify track downloads and processes
5. Test with invalid credentials (should show clear error)

### Tasks

- [X] T047 [P] [US3] Add Spotify URL detection to FileInputWidget validation
- [X] T048 [P] [US3] Display track name and artist when Spotify URL is validated
- [X] T049 [US3] Add download progress display before processing starts
- [X] T050 [US3] Implement credential validation in SettingsController
- [X] T051 [US3] Show "Configure Spotify Credentials" dialog when URL pasted without credentials
- [X] T052 [US3] Test Spotify URL processing end-to-end with valid credentials

---

## Phase 7: User Story 4 - Settings and Model Selection (P4)

**Story Goal**: Advanced users can customize model, output directory, and enhancement settings.

**Why P4**: Power users need control, but defaults work for most. Can be added last.

**Dependencies**: None (independent of other stories).

**Independent Test**:
1. Open settings panel
2. Change model to "htdemucs_ft"
3. Change output directory to custom location
4. Disable enhancement
5. Process a file
6. Verify custom settings were applied
7. Restart app and verify settings persisted

### Data Models (US4)

- [X] T053 [P] [US4] Create UserSettings model in src/music_stem_separator/gui/models/user_settings.py
- [X] T054 [P] [US4] Create JSONSettingsManager in src/music_stem_separator/gui/utils/settings_manager.py

### Settings Panel UI (US4)

- [X] T055 [P] [US4] Create SettingsPanel widget in src/music_stem_separator/gui/widgets/settings_panel.py
- [X] T056 [P] [US4] Add model selection dropdown with descriptions
- [X] T057 [P] [US4] Add output directory picker with "Browse" button
- [X] T058 [P] [US4] Add enhancement enable/disable checkbox
- [X] T059 [P] [US4] Add Spotify credentials input fields (client ID and secret)

### Settings Controller (US4)

- [X] T060 [US4] Create SettingsController in src/music_stem_separator/gui/controllers/settings_controller.py
- [X] T061 [US4] Implement settings load on app startup
- [X] T062 [US4] Implement settings save when user changes values
- [X] T063 [US4] Apply default settings on first run (Music/Stembler Output, htdemucs, enhancement on)
- [X] T064 [US4] Validate Spotify credentials when user clicks "Test Credentials" button

### Integration (US4)

- [X] T065 [US4] Add "Settings" menu item to MainWindow
- [X] T066 [US4] Open SettingsPanel dialog when menu item clicked
- [X] T067 [US4] Load settings on app startup and apply to ProcessingController
- [X] T068 [US4] Test settings persistence across app restarts

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Production-ready polish, packaging, and documentation.

### Error Handling

- [ ] T069 [P] Implement global exception handler for uncaught errors
- [ ] T070 [P] Add error logging to file in platform-specific log directory
- [ ] T071 [P] Replace technical stack traces with user-friendly error dialogs

### Cancellation Support

- [ ] T072 [P] Add "Cancel" button to MainWindow during processing
- [ ] T073 [P] Implement CancellationToken in processing_controller.py
- [ ] T074 [P] Test cancellation mid-processing (cleanup temp files, return to ready state)

### Application Metadata

- [ ] T075 [P] Add "About" dialog with version, license, and credits
- [ ] T076 [P] Set application icon for macOS (.icns) and Windows (.ico)
- [ ] T077 [P] Set window title to "Stembler v{version}"

### Packaging - macOS

- [ ] T078 Create PyInstaller spec file in packaging/macos/stembler.spec
- [ ] T079 Test PyInstaller build on macOS (generates .app bundle)
- [ ] T080 Create DMG installer script in packaging/macos/build_dmg.sh
- [ ] T081 Test DMG installation on clean macOS system

### Packaging - Windows

- [ ] T082 Create PyInstaller spec file in packaging/windows/stembler.spec
- [ ] T083 Test PyInstaller build on Windows (generates .exe)
- [ ] T084 Create MSI installer script in packaging/windows/build_msi.py
- [ ] T085 Test MSI installation on clean Windows system

### Documentation

- [ ] T086 [P] Update README.md with GUI installation and usage instructions
- [ ] T087 [P] Add GUI screenshots to README.md
- [ ] T088 [P] Update CLAUDE.md with GUI architecture details
- [ ] T089 [P] Create PACKAGING.md with build instructions for both platforms

---

## Task Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1** → **Phase 2** (Setup before shared logic)
2. **Phase 2** → **Phase 3** (Shared logic before GUI)
3. **Phase 2** → **Phase 4** (Shared logic before CLI verification)

### Independent Phases (Can Execute in Parallel)

After Phase 2 completes, these can run concurrently:
- **Phase 3** (US1: Drag-and-drop)
- **Phase 4** (US5: CLI compatibility)
- **Phase 7** (US4: Settings panel) ← No dependencies on other stories

After Phase 3 completes:
- **Phase 5** (US2: Progress feedback) ← Depends on US1
- **Phase 6** (US3: Spotify URLs) ← Depends on US1 + US4

After all user stories:
- **Phase 8** (Polish) ← Should wait for core functionality

### Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Shared Logic)
    ├─→ Phase 3 (US1: Drag-Drop) ───→ Phase 5 (US2: Progress)
    │                              ├─→ Phase 6 (US3: Spotify)*
    ├─→ Phase 4 (US5: CLI Compat)  │
    └─→ Phase 7 (US4: Settings) ───┘

    *Phase 6 requires both Phase 3 AND Phase 7

Phase 3 + Phase 4 + Phase 5 + Phase 6 + Phase 7
    ↓
Phase 8 (Polish & Packaging)
```

---

## Parallel Execution Examples

### Sprint 1: Foundation (Parallel Track)
**Goal**: Complete setup and shared logic
- T001-T007 (Setup) - Team Member A
- T008-T012 (Shared logic) - Team Member B (after setup)

### Sprint 2: MVP (Parallel Tracks)
**Goal**: Deliver minimal usable GUI + verify CLI still works
- **Track A**: T013-T033 (US1: Drag-drop GUI)
- **Track B**: T034-T038 (US5: CLI compatibility)
- **Track C**: T053-T068 (US4: Settings) - Independent, can start early

### Sprint 3: Enhanced UX (Parallel Tracks)
**Goal**: Add progress feedback and Spotify support
- **Track A**: T039-T046 (US2: Progress feedback)
- **Track B**: T047-T052 (US3: Spotify URLs)

### Sprint 4: Production Ready
**Goal**: Polish and package for distribution
- T069-T089 (Polish, packaging, docs) - Many can run in parallel

---

## Validation Checklist

Before marking feature complete, verify:

### User Story 1 (Drag-Drop)
- [ ] Can drag MP3 file onto GUI
- [ ] Processing starts and completes
- [ ] Stems appear in output directory
- [ ] "Open Folder" button works on both macOS and Windows
- [ ] Error shown for invalid file types

### User Story 5 (CLI Compat)
- [ ] All existing CLI commands work unchanged
- [ ] CLI tests pass 100%
- [ ] GUI settings don't affect CLI behavior

### User Story 2 (Progress)
- [ ] Progress bar updates during processing
- [ ] Percentage changes from 0% to 100%
- [ ] ETA updates every 2 seconds
- [ ] Stage messages appear correctly

### User Story 3 (Spotify)
- [ ] Can paste Spotify URL
- [ ] Track name displays after validation
- [ ] Download progress shows before processing
- [ ] Clear error if credentials invalid

### User Story 4 (Settings)
- [ ] Settings panel opens from menu
- [ ] Can change model, output dir, enhancement
- [ ] Settings persist across restarts
- [ ] Defaults work on first run

### Polish
- [ ] Application doesn't crash on any user action
- [ ] Errors show user-friendly messages (no stack traces)
- [ ] Can cancel processing mid-operation
- [ ] macOS DMG installs and runs on clean system
- [ ] Windows MSI installs and runs on clean system

---

## MVP Delivery Scope

**Recommended MVP** (Phases 1-4):
- Phase 1: Setup
- Phase 2: Shared logic
- Phase 3: US1 (Drag-drop processing)
- Phase 4: US5 (CLI compatibility)

**Why this is MVP**:
- Delivers core value: non-technical users can process files
- Protects existing users: CLI still works
- Independently testable: Can validate with real users immediately
- ~38 tasks (T001-T038)

**Post-MVP** (Phases 5-8):
- Phase 5: US2 (Progress feedback) - 8 tasks
- Phase 6: US3 (Spotify URLs) - 6 tasks
- Phase 7: US4 (Settings panel) - 16 tasks
- Phase 8: Polish & packaging - 21 tasks

---

**Tasks generated**: 2026-01-07
**Ready for implementation**: Yes
**Estimated total effort**: 89 tasks
**Parallel opportunities**: 25 tasks marked [P]
