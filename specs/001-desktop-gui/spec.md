# Feature Specification: Cross-Platform Desktop GUI

**Feature Branch**: `001-desktop-gui`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "turn the existing command line application into a desktop application that works on both Apple and Windows machines. I still should be able to use the command line, however for non-technical people, it would be great to have a basic user interface"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simple Drag-and-Drop Processing (Priority: P1)

A non-technical music enthusiast wants to extract vocals from a song without learning command-line tools. They simply drag their MP3 file into the application window, click a button, and receive the separated stems in an easy-to-find location.

**Why this priority**: This is the core value proposition for non-technical users. It must work flawlessly to justify the desktop application's existence. Without this, there's no reason for users to prefer the GUI over the CLI.

**Independent Test**: Can be fully tested by dragging a sample audio file into the GUI, clicking "Separate Stems", and verifying that output files are created in the expected location. Delivers immediate value by making stem separation accessible to non-technical users.

**Acceptance Scenarios**:

1. **Given** the application is running, **When** a user drags an MP3 file onto the application window, **Then** the file path appears in the input field and is validated
2. **Given** a valid audio file is selected, **When** the user clicks "Separate Stems", **Then** the processing starts and shows real-time progress
3. **Given** processing is complete, **When** stems are generated, **Then** the user sees a success message with a clickable link to open the output folder
4. **Given** an invalid file is selected, **When** the user attempts to start processing, **Then** a clear error message explains what file types are supported

---

### User Story 2 - Visual Progress Feedback (Priority: P2)

A user processing a long audio file wants to know how much time remains and whether the application is still working. They see a progress bar, percentage complete, estimated time remaining, and which processing step is currently running.

**Why this priority**: Stem separation can take 1-3 minutes per song. Without feedback, users will assume the application has frozen. This prevents support requests and user frustration.

**Independent Test**: Can be tested by processing a 5-minute audio file and verifying that progress updates appear at regular intervals, showing percentage, time remaining, and current step. Delivers value by reducing user anxiety during processing.

**Acceptance Scenarios**:

1. **Given** processing has started, **When** the AI model loads, **Then** the status shows "Loading AI model..." with a spinner
2. **Given** stem separation is in progress, **When** processing advances, **Then** the progress bar updates to show percentage complete
3. **Given** 50% of processing is complete, **When** the user looks at the interface, **Then** they see an estimated time remaining (e.g., "1 minute 30 seconds remaining")
4. **Given** processing is in the enhancement phase, **When** stems are being enhanced, **Then** the status shows "Enhancing audio quality..." with current stem being processed

---

### User Story 3 - Spotify URL Processing (Priority: P3)

A user discovers a song on Spotify and wants to extract its stems. They copy the Spotify share link, paste it into the desktop application, and the application downloads and processes the track automatically.

**Why this priority**: This is a key differentiator from simple audio tools, but it requires the user to set up Spotify API credentials first. It's valuable but not essential for the MVP.

**Independent Test**: Can be tested by pasting a Spotify track URL into the input field (with valid credentials configured) and verifying that the track is downloaded and processed. Delivers value by eliminating the need for users to download tracks manually.

**Acceptance Scenarios**:

1. **Given** Spotify credentials are not configured, **When** a user pastes a Spotify URL, **Then** the application shows a settings dialog explaining how to obtain and configure Spotify API credentials
2. **Given** valid Spotify credentials are configured, **When** a user pastes a Spotify track URL, **Then** the application validates the URL and shows the track name and artist
3. **Given** a valid Spotify URL is entered, **When** the user clicks "Separate Stems", **Then** the application downloads the track first (showing download progress) before starting stem separation
4. **Given** Spotify credentials are invalid or expired, **When** download is attempted, **Then** the user sees a clear error message and is prompted to update their credentials

---

### User Story 4 - Settings and Model Selection (Priority: P4)

An advanced user wants to customize their stem separation experience by choosing different AI models, specifying output locations, and enabling/disabling audio enhancement. They access a settings panel where these options are clearly explained.

**Why this priority**: Power users need customization options, but sensible defaults work for most users. This can be added after core functionality is stable.

**Independent Test**: Can be tested by opening the settings panel, changing the AI model and output directory, processing a file, and verifying that the chosen settings are applied. Delivers value by giving advanced users control without overwhelming beginners.

**Acceptance Scenarios**:

1. **Given** the user opens settings, **When** they view available AI models, **Then** they see a list of models with descriptions (e.g., "htdemucs - High quality, balanced speed" vs "htdemucs_ft - Highest quality, slower")
2. **Given** the user changes the output directory, **When** they click "Browse" and select a folder, **Then** the new path is saved and used for all future processing
3. **Given** the user disables audio enhancement, **When** they process a file, **Then** processing completes faster and the output reflects raw stem separation without enhancement
4. **Given** default settings are applied, **When** a first-time user starts the application, **Then** the default model (htdemucs) and output location (Music/Stembler Output) are pre-selected

---

### User Story 5 - CLI Compatibility Maintained (Priority: P1)

An existing power user who relies on the command-line interface for batch processing and automation wants to continue using their existing scripts without modification. The desktop GUI is installed alongside the CLI, and both work independently.

**Why this priority**: Breaking existing workflows would alienate current users. The CLI must remain fully functional and unchanged.

**Independent Test**: Can be tested by running existing CLI commands (e.g., `stem-separator song.mp3 --model htdemucs_ft`) after the desktop application is installed, and verifying that all CLI functionality works exactly as before. Delivers value by ensuring backward compatibility.

**Acceptance Scenarios**:

1. **Given** the desktop application is installed, **When** a user runs `stem-separator song.mp3` in the terminal, **Then** the CLI processes the file exactly as it did before the GUI was added
2. **Given** a user has CLI automation scripts, **When** they run their scripts after installing the GUI, **Then** all scripts execute without errors or behavior changes
3. **Given** both CLI and GUI are available, **When** a user sets preferences in the GUI, **Then** those preferences do not affect CLI default behavior (they remain independent)

---

### Edge Cases

- What happens when a user tries to process a file while another file is already being processed?
- How does the application handle extremely large audio files (>100MB or >30 minutes)?
- What happens if the user closes the application window while processing is in progress?
- How does the application behave on systems without a GPU (CPU-only processing)?
- What happens if the output directory becomes unavailable during processing (disk full, network drive disconnected)?
- How does the application handle corrupt or unsupported audio file formats?
- What happens if Spotify credentials are revoked or rate-limited during download?
- How does the application respond on first launch without any user configuration?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a desktop application that runs natively on macOS and Windows
- **FR-002**: System MUST allow users to select audio files through drag-and-drop or file picker dialog
- **FR-003**: System MUST display real-time progress during stem separation, including percentage complete and estimated time remaining
- **FR-004**: System MUST maintain full CLI functionality unchanged (existing command-line interface remains available)
- **FR-005**: System MUST support the same input types as CLI: local audio files (MP3, WAV, FLAC, M4A), Spotify URLs, and direct audio URLs
- **FR-006**: System MUST provide visual feedback for all processing stages: input validation, AI model loading, stem separation, audio enhancement, and file organization
- **FR-007**: System MUST allow users to open the output folder directly from the application after processing completes
- **FR-008**: System MUST handle errors gracefully with user-friendly error messages (not technical stack traces)
- **FR-009**: System MUST allow cancellation of in-progress processing operations
- **FR-010**: System MUST prevent users from starting new processing while another operation is in progress
- **FR-011**: System MUST persist user settings across application restarts (output directory, preferred model, enhancement enabled/disabled)
- **FR-012**: System MUST provide a settings panel for configuring Spotify API credentials, output directory, AI model selection, and audio enhancement options
- **FR-013**: System MUST validate Spotify credentials and provide clear feedback if they are missing or invalid
- **FR-014**: System MUST show file validation feedback immediately upon file selection (before processing starts)
- **FR-015**: System MUST provide default settings that work for first-time users without configuration
- **FR-016**: System MUST display application version and provide an "About" section with project information
- **FR-017**: System MUST log all errors and processing details to a file for troubleshooting purposes

### Key Entities

- **Audio Input**: Represents the source audio to be processed - can be a local file path, Spotify URL, or direct audio URL. Has attributes: path/URL, file type, validation status, file size, duration
- **Processing Job**: Represents a single stem separation operation. Has attributes: input source, selected model, enhancement enabled, output directory, progress percentage, current processing stage, estimated time remaining, status (queued, running, completed, failed, cancelled)
- **User Settings**: Represents persisted user preferences. Has attributes: output directory path, default AI model, enhancement enabled by default, Spotify client ID, Spotify client secret, last used settings timestamp
- **Output Bundle**: Represents the collection of generated stem files and metadata for a processed track. Has attributes: track name, output directory path, list of stem files (drums, bass, vocals, other), metadata file path, total size, creation timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Non-technical users can successfully separate stems from an audio file on their first attempt without reading documentation (80% success rate in user testing)
- **SC-002**: Processing progress updates appear within 2 seconds of each stage transition, preventing users from thinking the application has frozen
- **SC-003**: Application startup time is under 3 seconds on both macOS and Windows
- **SC-004**: Users can locate their processed stems within 10 seconds of completion (via "Open Output Folder" button)
- **SC-005**: Error messages are understandable by non-technical users (no jargon or stack traces visible in UI)
- **SC-006**: Existing CLI users can continue their workflows without modification (100% backward compatibility with all existing CLI commands and options)
- **SC-007**: Application uses less than 500MB of memory when idle (excluding AI model loading during processing)
- **SC-008**: First-time users can complete their first stem separation without configuring any settings (default settings work out of the box)
- **SC-009**: Application survives unexpected interruptions (crashes, power loss) without corrupting output files or user settings
- **SC-010**: Users can cancel a running operation and start a new one within 5 seconds

## Assumptions *(mandatory)*

- Users have sufficient disk space for stem output files (typically 50-200MB per processed song)
- Users have internet connectivity for Spotify URL processing and initial AI model downloads
- The existing CLI architecture (modules: input_processor, separator, stem_processor, output_manager) can be reused for the GUI with minimal modification
- macOS users are running macOS 11 (Big Sur) or newer
- Windows users are running Windows 10 or newer
- Users will install the application using a standard installer (DMG for macOS, MSI/EXE for Windows)
- GPU acceleration remains optional (CPU-only processing is acceptable, though slower)
- The desktop application will share the same AI models and processing logic as the CLI (no separate model training)
- Python runtime can be bundled with the application (users don't need Python installed separately)
- Settings will be stored in standard user configuration directories (~/Library/Application Support on macOS, AppData on Windows)

## Out of Scope *(mandatory)*

- Batch processing multiple files at once (users process one file at a time in the GUI)
- Advanced audio editing features (waveform visualization, stem mixing, volume adjustment)
- Cloud-based processing or server-side API
- Mobile applications (iOS, Android)
- Linux desktop application (focus on macOS and Windows only for this feature)
- Real-time preview of stems during processing
- Integration with digital audio workstations (DAWs)
- Social sharing features (posting results to social media)
- Built-in audio player for previewing stems (users can use their default audio player)
- Automatic updates or update notifications (users will manually download new versions)
- Custom theme or appearance customization
- Internationalization/localization (English only)
- User accounts or authentication (beyond Spotify API credentials)

## Dependencies & Constraints

**Dependencies**:
- Existing CLI codebase and processing pipeline must remain functional
- Same AI models (Demucs) and audio processing libraries (librosa) used by CLI
- Spotify API availability for track downloading functionality
- Cross-platform GUI framework must support both macOS and Windows with native look-and-feel

**Constraints**:
- Must not break or modify existing CLI behavior
- Application package size should remain under 500MB (excluding AI models, which download on-demand)
- GUI framework must be compatible with existing Python codebase
- Must follow platform-specific UI conventions (macOS Human Interface Guidelines, Windows UI Guidelines)
- Settings storage must use platform-standard locations
- Installation process must be straightforward for non-technical users (double-click installer, no terminal commands)
