# GUI Internal API Contract

**Feature**: 001-desktop-gui
**Date**: 2026-01-07
**Version**: 1.0.0

## Overview

This document defines the internal API contracts between GUI components and the shared processing logic. These are Python interfaces (Protocols), not REST APIs.

## 1. Processing Interface

### `process_track_async()`

Asynchronous wrapper for stem separation that provides progress updates without blocking the UI.

**Signature**:
```python
async def process_track_async(
    input_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: Optional[str] = None,
    enable_enhancement: bool = True,
    progress_callback: Optional[Callable[[ProgressUpdate], None]] = None,
    cancellation_token: Optional[CancellationToken] = None
) -> ProcessingResult:
    """
    Process audio track with progress reporting.

    Args:
        input_path: Path to audio file or URL
        output_dir: Output directory for stems
        model_name: Demucs model to use
        device: Device for processing (cpu, cuda, or auto-detect)
        enable_enhancement: Apply audio enhancement after separation
        progress_callback: Optional callback for progress updates
        cancellation_token: Optional token to cancel processing

    Returns:
        ProcessingResult with success status and output details

    Raises:
        ProcessingError: If processing fails
        CancellationError: If cancelled via cancellation_token
    """
```

**ProgressUpdate Structure**:
```python
@dataclass
class ProgressUpdate:
    stage: str              # e.g., "input_processing", "loading_model", "separating_stems"
    percent: int            # 0-100
    message: str            # Human-readable message
    time_elapsed: float     # Seconds since start
    time_remaining: Optional[float]  # Estimated seconds remaining
```

**ProcessingResult Structure**:
```python
@dataclass
class ProcessingResult:
    success: bool
    track_name: str
    input_type: str
    stems_separated: List[str]  # ["drums", "bass", "vocals", "other"]
    enhancement_applied: bool
    output_structure: OutputStructure
    processing_time: float
    error: Optional[str] = None
```

**Progress Stages** (in order):
1. `input_processing` (0-10%): Validating and preparing input
2. `loading_model` (10-20%): Loading Demucs AI model
3. `separating_stems` (20-80%): Core stem separation
4. `enhancing_audio` (80-90%): Audio enhancement (if enabled)
5. `organizing_output` (90-100%): Saving and organizing files

**Example Usage**:
```python
def on_progress(update: ProgressUpdate):
    print(f"{update.percent}% - {update.message}")
    if update.time_remaining:
        print(f"  ETA: {update.time_remaining:.0f} seconds")

result = await process_track_async(
    input_path="song.mp3",
    output_dir="./output",
    progress_callback=on_progress
)

if result.success:
    print(f"Stems saved to: {result.output_structure.track_dir}")
else:
    print(f"Error: {result.error}")
```

---

## 2. Settings Management Interface

### `SettingsManager` Protocol

Interface for loading and persisting user settings.

**Methods**:

```python
class SettingsManager(Protocol):
    """Protocol for settings persistence"""

    def load(self) -> UserSettings:
        """
        Load settings from persistent storage.

        Returns:
            UserSettings object (returns defaults if file doesn't exist or is corrupted)

        Raises:
            Never raises (falls back to defaults on any error)
        """

    def save(self, settings: UserSettings) -> None:
        """
        Save settings to persistent storage.

        Args:
            settings: UserSettings object to persist

        Raises:
            SettingsError: If unable to write to storage (disk full, permissions, etc.)
        """

    def reset_to_defaults(self) -> UserSettings:
        """
        Reset settings to factory defaults and save.

        Returns:
            UserSettings with default values

        Raises:
            SettingsError: If unable to write defaults
        """

    def get_settings_file_path(self) -> Path:
        """
        Get the path to the settings file for debugging.

        Returns:
            Absolute path to settings.json
        """
```

**Implementation Note**:
The concrete implementation (`JSONSettingsManager`) uses:
- `platformdirs.user_config_dir("Stembler")` for location
- `settings.json` filename
- Atomic writes (write to temp file, then rename) for safety

---

## 3. Input Validation Interface

### `InputValidator` Protocol

Interface for validating audio inputs before processing.

**Methods**:

```python
class InputValidator(Protocol):
    """Protocol for input validation"""

    def validate(self, path_or_url: str) -> AudioInput:
        """
        Validate an input source and return AudioInput object.

        Args:
            path_or_url: File path, Spotify URL, or direct audio URL

        Returns:
            AudioInput object with validation_status set

        Note:
            This method NEVER raises exceptions. Invalid inputs return
            AudioInput with validation_status != VALID and a message.
        """

    def validate_spotify_credentials(
        self,
        client_id: str,
        client_secret: str
    ) -> tuple[bool, str]:
        """
        Validate Spotify API credentials.

        Args:
            client_id: Spotify client ID
            client_secret: Spotify client secret

        Returns:
            Tuple of (valid: bool, message: str)
            - (True, "Credentials valid") if successful
            - (False, error message) if invalid

        Note:
            This makes a test API call to verify credentials work.
        """
```

**AudioInput Validation Flow**:
```python
validator = InputValidator()
audio_input = validator.validate("song.mp3")

if audio_input.validation_status == ValidationStatus.VALID:
    # Proceed with processing
    result = await process_track_async(audio_input.path_or_url, ...)
else:
    # Show error to user
    show_error(audio_input.validation_message)
```

---

## 4. Cancellation Interface

### `CancellationToken` Protocol

Interface for cancelling in-progress operations.

**Methods**:

```python
class CancellationToken(Protocol):
    """Protocol for operation cancellation"""

    def is_cancelled(self) -> bool:
        """Check if cancellation has been requested"""

    def cancel(self) -> None:
        """Request cancellation of the operation"""

    def reset(self) -> None:
        """Reset token for reuse"""
```

**Usage Pattern**:
```python
# In GUI controller:
token = CancellationToken()

async def process_with_cancel():
    try:
        result = await process_track_async(
            input_path="song.mp3",
            output_dir="./output",
            cancellation_token=token
        )
    except CancellationError:
        print("User cancelled processing")

# When user clicks "Cancel" button:
def on_cancel_clicked():
    token.cancel()
```

**Implementation in process_track_async**:
```python
async def process_track_async(..., cancellation_token=None):
    # Check cancellation at each stage
    if cancellation_token and cancellation_token.is_cancelled():
        raise CancellationError("Processing cancelled by user")

    # ... do work ...

    if cancellation_token and cancellation_token.is_cancelled():
        raise CancellationError("Processing cancelled by user")
```

---

## 5. Platform Utilities Interface

### `PlatformUtils` Module

Cross-platform utilities for platform-specific operations.

**Functions**:

```python
def open_folder(path: Path) -> None:
    """
    Open folder in system file explorer.

    - macOS: Uses 'open' command
    - Windows: Uses 'explorer' command

    Args:
        path: Path to folder to open

    Raises:
        FileNotFoundError: If path doesn't exist
        OSError: If unable to open folder
    """

def get_default_music_folder() -> Path:
    """
    Get platform-standard music folder.

    Returns:
        - macOS: ~/Music
        - Windows: %USERPROFILE%\\Music

    Returns:
        Path to music folder (creates if doesn't exist)
    """

def get_config_directory(app_name: str) -> Path:
    """
    Get platform-standard config directory.

    Args:
        app_name: Name of application (e.g., "Stembler")

    Returns:
        - macOS: ~/Library/Application Support/{app_name}
        - Windows: %APPDATA%\\{app_name}

    Note:
        Creates directory if it doesn't exist
    """

def get_log_directory(app_name: str) -> Path:
    """
    Get platform-standard log directory.

    Args:
        app_name: Name of application

    Returns:
        - macOS: ~/Library/Logs/{app_name}
        - Windows: %APPDATA%\\{app_name}\\logs

    Note:
        Creates directory if it doesn't exist
    """
```

---

## 6. Error Handling Contracts

### Custom Exceptions

```python
class ProcessingError(Exception):
    """Raised when stem separation fails"""
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

class CancellationError(Exception):
    """Raised when processing is cancelled by user"""
    pass

class SettingsError(Exception):
    """Raised when settings operations fail"""
    pass

class ValidationError(Exception):
    """Raised when input validation fails critically"""
    pass
```

### Error Recovery Strategy

| Exception | GUI Response | User Message | Recovery Action |
|-----------|-------------|--------------|-----------------|
| `ProcessingError` | Show error dialog | "Unable to process file: {message}" | Allow retry with different file |
| `CancellationError` | Show brief notification | "Processing cancelled" | Return to ready state |
| `SettingsError` | Show error dialog | "Unable to save settings: {message}" | Continue with in-memory settings |
| `ValidationError` | Show inline error | "Invalid input: {message}" | Allow user to fix input |

---

## 7. Threading Contract

### Thread Safety Requirements

**Main/UI Thread**:
- All Qt widget interactions
- Progress callback invocations (Qt signals handle thread safety)
- Settings load/save operations

**Worker Thread**:
- `process_track_async()` execution
- File I/O operations
- AI model loading and inference
- Audio processing

**Thread Communication**:
- **GUI → Worker**: Via method parameters (input_path, settings, etc.)
- **Worker → GUI**: Via progress callbacks using Qt signals
- **Shared state**: None (immutable data passed between threads)

**Example with PyQt6**:
```python
from PyQt6.QtCore import QThread, pyqtSignal

class ProcessingWorker(QThread):
    progress_update = pyqtSignal(dict)  # Thread-safe signal
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, input_path, output_dir, settings):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.settings = settings

    def run(self):
        """Runs in worker thread"""
        try:
            def on_progress(update: ProgressUpdate):
                # Emit signal (thread-safe)
                self.progress_update.emit({
                    "percent": update.percent,
                    "message": update.message,
                })

            result = process_track_sync(  # Synchronous version
                self.input_path,
                self.output_dir,
                progress_callback=on_progress
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# In GUI controller:
worker = ProcessingWorker(input_path, output_dir, settings)
worker.progress_update.connect(self.on_progress)  # Slot in main thread
worker.finished.connect(self.on_finished)
worker.error.connect(self.on_error)
worker.start()
```

---

## 8. Testing Contracts

### Mock Implementations

For testing GUI components without running actual processing:

```python
class MockProcessingService:
    """Mock for testing UI without real processing"""

    async def process_track_async(
        self,
        input_path: str,
        output_dir: str,
        progress_callback: Optional[Callable] = None,
        **kwargs
    ) -> ProcessingResult:
        """Simulates processing with fake progress updates"""

        # Simulate stages
        for stage, percent in [
            ("input_processing", 10),
            ("loading_model", 20),
            ("separating_stems", 50),
            ("separating_stems", 80),
            ("organizing_output", 100),
        ]:
            if progress_callback:
                progress_callback(ProgressUpdate(
                    stage=stage,
                    percent=percent,
                    message=f"Mock {stage}",
                    time_elapsed=percent / 10,
                    time_remaining=(100 - percent) / 10 if percent < 100 else None
                ))
            await asyncio.sleep(0.5)  # Simulate work

        return ProcessingResult(
            success=True,
            track_name="Test Song",
            input_type="local_file",
            stems_separated=["drums", "bass", "vocals", "other"],
            enhancement_applied=True,
            output_structure=mock_output_structure(),
            processing_time=5.0,
        )
```

---

## Contract Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-07 | Initial contract definition |

## Notes

- All interfaces use type hints for clarity
- Async functions return coroutines (use `await`)
- Callbacks are synchronous but invoked via Qt signals for thread safety
- No global state - all state passed explicitly
- Errors handled via exceptions, not return codes

---

**Contracts complete**: Ready for quickstart guide generation
