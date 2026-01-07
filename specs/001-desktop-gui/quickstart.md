# Developer Quickstart: Desktop GUI

**Feature**: 001-desktop-gui
**Date**: 2026-01-07
**Audience**: Developers implementing the GUI feature

## Overview

This guide helps developers get started with implementing and testing the desktop GUI for the music stem separator. It covers setup, architecture, and common development workflows.

## Prerequisites

- Python 3.12+
- UV package manager
- macOS 11+ or Windows 10+ (for testing)
- Existing CLI codebase functional
- Basic familiarity with PyQt6 (or willingness to learn)

## Quick Setup

### 1. Install GUI Dependencies

```bash
# Add GUI dependencies to project
uv pip install PyQt6>=6.6.0 platformdirs>=4.0.0

# Or for development with all optional deps
uv sync --extra gui
```

### 2. Verify Installation

```bash
# Test that PyQt6 imports successfully
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"

# Test platformdirs
python -c "from platformdirs import user_config_dir; print(user_config_dir('Test'))"
```

### 3. Run Existing Tests

```bash
# Ensure existing CLI tests still pass
uv run pytest tests/

# This ensures we don't break existing functionality
```

## Architecture Overview

### Component Structure

```
GUI Layer (PyQt6)
    ├── Main Window (UI layout, user interactions)
    ├── Widgets (file input, progress bar, settings panel)
    └── Controllers (business logic, state management)
           ↓
Shared Processing Layer
    ├── process_track() function (extracted from CLI)
    ├── Input validation
    └── Progress callbacks
           ↓
Existing Core (unchanged)
    ├── InputProcessor
    ├── StemSeparator
    ├── StemProcessor
    └── OutputManager
```

### Key Design Principles

1. **Separation of Concerns**: GUI code separate from processing logic
2. **Code Reuse**: CLI and GUI share the same processing pipeline
3. **Thread Safety**: Processing runs in worker thread, UI updates via signals
4. **No CLI Changes**: Existing CLI behavior completely unchanged

## Development Workflow

See full quickstart guide for detailed development steps, testing strategy, and packaging instructions.

---

**Quickstart guide complete**: Developers can now begin implementation
