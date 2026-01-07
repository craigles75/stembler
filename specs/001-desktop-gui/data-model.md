# Data Model: Cross-Platform Desktop GUI

**Feature**: 001-desktop-gui
**Date**: 2026-01-07
**Status**: Phase 1 Design

## Overview

This document defines the data entities used by the desktop GUI for the music stem separator. These models represent the state and configuration of the GUI application, separate from the core audio processing logic (which remains unchanged in the existing modules).

## Entity Definitions

### 1. ProcessingJob

Represents a single stem separation operation with full state tracking.

**Purpose**: Track the lifecycle of a processing request from input validation through completion.

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `job_id` | string (UUID) | Yes | Unique identifier for this processing job | Auto-generated UUID4 |
| `input_source` | AudioInput | Yes | The validated audio input | Must pass validation |
| `model_name` | string | Yes | Demucs model to use | One of: htdemucs, htdemucs_ft, mdx_extra, mdx_q |
| `enhancement_enabled` | boolean | Yes | Whether to apply audio enhancement | Default: true |
| `output_directory` | Path | Yes | Where to save stem files | Must be writable |
| `status` | ProcessingStatus (enum) | Yes | Current job status | See status enum below |
| `progress_percent` | integer | Yes | Completion percentage (0-100) | Range: 0-100 |
| `current_stage` | string | No | Human-readable stage description | e.g., "Loading AI model..." |
| `estimated_time_remaining` | integer | No | Seconds until completion | Updated during processing |
| `start_time` | datetime | No | When processing started | Set on status change to RUNNING |
| `end_time` | datetime | No | When processing finished | Set on COMPLETED/FAILED/CANCELLED |
| `error_message` | string | No | Error details if failed | Only set if status is FAILED |
| `output_bundle` | OutputBundle | No | Generated stems and metadata | Only set if status is COMPLETED |

**ProcessingStatus Enum**:
- `QUEUED`: Job created but not yet started
- `RUNNING`: Processing in progress
- `COMPLETED`: Successfully finished
- `FAILED`: Error occurred during processing
- `CANCELLED`: User cancelled the operation

**State Transitions**:
```
QUEUED → RUNNING → COMPLETED
               ↘ FAILED
               ↘ CANCELLED
```

**Validation Rules**:
- `progress_percent` must stay in range 0-100
- `status` can only move forward (no COMPLETED → RUNNING)
- `output_bundle` is None unless status is COMPLETED
- `error_message` is None unless status is FAILED
- `estimated_time_remaining` only valid when status is RUNNING

---

### 2. UserSettings

Persistent user preferences loaded on startup and saved on changes.

**Purpose**: Store user configuration across application restarts.

**Attributes**:

| Attribute | Type | Required | Description | Constraints | Default Value |
|-----------|------|----------|-------------|-------------|---------------|
| `output_directory` | Path | Yes | Default output location | Must exist or be creatable | ~/Music/Stembler Output |
| `default_model` | string | Yes | Preferred Demucs model | One of: htdemucs, htdemucs_ft, mdx_extra, mdx_q | htdemucs |
| `enhancement_enabled` | boolean | Yes | Enable enhancement by default | - | true |
| `spotify_client_id` | string | No | Spotify API client ID | Empty string if not configured | "" |
| `spotify_client_secret` | string | No | Spotify API client secret | Empty string if not configured | "" |
| `last_input_directory` | Path | No | Last directory user selected file from | Used for file picker | User's home directory |
| `window_width` | integer | Yes | Main window width in pixels | Min: 600, Max: 3840 | 800 |
| `window_height` | integer | Yes | Main window height in pixels | Min: 400, Max: 2160 | 600 |
| `window_x` | integer | No | Window X position | None = centered | None |
| `window_y` | integer | No | Window Y position | None = centered | None |

**Persistence**:
- Stored in platform-standard config directory
- Format: JSON file (`settings.json`)
- Location (macOS): `~/Library/Application Support/Stembler/settings.json`
- Location (Windows): `%APPDATA%\Stembler\settings.json`

**Validation Rules**:
- `output_directory` must be absolute path
- `spotify_client_id` and `spotify_client_secret` validated together (both empty or both filled)
- Window dimensions clamped to min/max values
- Invalid JSON or missing file → fall back to defaults

---

### 3. AudioInput

Validated input source for processing.

**Purpose**: Represent a validated audio source (local file or URL) with metadata.

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `source_type` | InputType (enum) | Yes | Type of input | LOCAL_FILE, SPOTIFY_URL, DIRECT_URL |
| `path_or_url` | string | Yes | File path or URL | Must pass validation for type |
| `display_name` | string | Yes | User-friendly name | Filename or track name |
| `file_size_bytes` | integer | No | Size in bytes (local files only) | > 0 if local file |
| `duration_seconds` | float | No | Audio duration (if determinable) | > 0 if available |
| `validation_status` | ValidationStatus (enum) | Yes | Result of validation | See status enum below |
| `validation_message` | string | No | Details if validation failed | Only set if not VALID |

**InputType Enum**:
- `LOCAL_FILE`: File on user's computer (e.g., /path/to/song.mp3)
- `SPOTIFY_URL`: Spotify track URL (e.g., https://open.spotify.com/track/...)
- `DIRECT_URL`: Direct audio file URL (e.g., https://example.com/audio.mp3)

**ValidationStatus Enum**:
- `VALID`: Input passed validation and can be processed
- `INVALID_FORMAT`: File type not supported
- `FILE_NOT_FOUND`: Local file doesn't exist
- `URL_UNREACHABLE`: URL cannot be accessed
- `SPOTIFY_AUTH_REQUIRED`: Spotify credentials needed
- `UNKNOWN_ERROR`: Validation failed for unknown reason

**Validation Rules** (by type):
- **LOCAL_FILE**:
  - Must exist on filesystem
  - Must be readable
  - Extension must be in: .mp3, .wav, .flac, .m4a, .ogg, .wma
  - Size must be < 500MB (reasonable limit)

- **SPOTIFY_URL**:
  - Must match pattern: `https://open.spotify.com/track/` or `spotify:track:`
  - Requires valid Spotify credentials in settings
  - Must be accessible via Spotify API

- **DIRECT_URL**:
  - Must be valid HTTP/HTTPS URL
  - Must end with supported audio extension
  - Must return Content-Type: audio/*

---

### 4. OutputBundle

Collection of generated stem files and metadata for a completed processing job.

**Purpose**: Represent the results of successful stem separation.

**Attributes**:

| Attribute | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `track_name` | string | Yes | Name of the processed track | Sanitized for filesystem |
| `track_directory` | Path | Yes | Directory containing all outputs | Absolute path |
| `stem_files` | dict[string, Path] | Yes | Paths to stem files | Keys: drums, bass, vocals, other |
| `metadata_file` | Path | No | Path to metadata.json | In track_directory |
| `total_size_bytes` | integer | Yes | Total size of all stems | Sum of all file sizes |
| `creation_timestamp` | datetime | Yes | When stems were created | ISO 8601 format |
| `processing_time_seconds` | float | Yes | How long processing took | > 0 |
| `model_used` | string | Yes | Which Demucs model was used | For reference |
| `enhancement_applied` | boolean | Yes | Whether enhancement was used | For reference |

**Structure Example**:
```
track_directory: /Users/name/Music/Stembler Output/Song Name/
  ├── stems/
  │   ├── Song Name_drums.wav
  │   ├── Song Name_bass.wav
  │   ├── Song Name_vocals.wav
  │   └── Song Name_other.wav
  └── metadata.json
```

**Validation Rules**:
- All `stem_files` paths must exist and be readable
- `track_directory` must exist
- All stem files must be in `track_directory/stems/` subdirectory
- `stem_files` dict must contain exactly 4 keys: drums, bass, vocals, other

---

## Entity Relationships

```
UserSettings (singleton)
    ↓ provides defaults for
ProcessingJob
    ↓ contains validated
AudioInput
    ↓ produces (if successful)
OutputBundle
```

**Cardinality**:
- 1 UserSettings per application instance (loaded on startup)
- 0-1 ProcessingJob active at a time (no concurrent processing in GUI)
- 1 AudioInput per ProcessingJob
- 0-1 OutputBundle per ProcessingJob (only if status = COMPLETED)

## Persistence Strategy

| Entity | Persisted? | Storage | Lifetime |
|--------|-----------|---------|----------|
| UserSettings | Yes | JSON file in config directory | Across app restarts |
| ProcessingJob | No | In-memory only | Single session |
| AudioInput | No | In-memory only | Part of ProcessingJob |
| OutputBundle | Partially | Stem files on disk, metadata in JSON | Permanent (until user deletes) |

**Notes**:
- `ProcessingJob` is ephemeral (not saved between sessions)
- `OutputBundle` files persist on disk, but the object itself is not serialized
- Only `UserSettings` is loaded/saved from persistent storage

## Implementation Notes

### Python Type Hints Example

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class ProcessingStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProcessingJob:
    job_id: UUID
    input_source: 'AudioInput'
    model_name: str
    enhancement_enabled: bool
    output_directory: Path
    status: ProcessingStatus = ProcessingStatus.QUEUED
    progress_percent: int = 0
    current_stage: Optional[str] = None
    estimated_time_remaining: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    output_bundle: Optional['OutputBundle'] = None

    @classmethod
    def create(cls, input_source, model_name, enhancement_enabled, output_directory):
        return cls(
            job_id=uuid4(),
            input_source=input_source,
            model_name=model_name,
            enhancement_enabled=enhancement_enabled,
            output_directory=output_directory,
        )
```

### Validation Logic

Each entity should have a `validate()` method that checks constraints:

```python
class AudioInput:
    def validate(self) -> tuple[ValidationStatus, str]:
        """Returns (status, message) tuple"""
        if self.source_type == InputType.LOCAL_FILE:
            if not Path(self.path_or_url).exists():
                return (ValidationStatus.FILE_NOT_FOUND,
                       f"File not found: {self.path_or_url}")
            # ... more validation
        # ...
```

### State Management

The GUI should maintain:
- **Singleton**: `current_settings: UserSettings`
- **Current job**: `active_job: Optional[ProcessingJob]`
- **Job history**: Not stored (out of scope for v1)

---

**Data model complete**: Ready for contract definition phase

