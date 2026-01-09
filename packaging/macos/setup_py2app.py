#!/usr/bin/env python3
"""
py2app setup file for Stembler macOS application.

py2app is the recommended tool for packaging Python apps on macOS and handles
PyQt6 frameworks natively without the symlink issues that PyInstaller has.

To build:
    python packaging/macos/setup_py2app.py py2app

Output:
    dist/Stembler.app - macOS application bundle
"""

from setuptools import setup
from pathlib import Path
import sys

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Application metadata
APP_NAME = "Stembler"
APP_VERSION = "0.1.0"
BUNDLE_ID = "com.stembler.app"

# Main script
APP = [str(src_path / "music_stem_separator" / "gui_main.py")]

# Options for py2app
OPTIONS = {
    "py2app": {
        # Icon
        "iconfile": str(Path(__file__).parent / "icon.icns"),
        # Include all packages
        "packages": [
            "PyQt6",
            "torch",
            "torchaudio",
            "demucs",
            "librosa",
            "soundfile",
            "scipy",
            "numpy",
            "spotdl",
            "requests",
            "platformdirs",
            "click",
            "music_stem_separator",
        ],
        # Exclude unnecessary packages to reduce size
        "excludes": [
            "tkinter",
            "matplotlib",
            "PIL",
            "IPython",
            "jupyter",
            "PyQt6.Qt3DAnimation",
            "PyQt6.Qt3DCore",
            "PyQt6.Qt3DExtras",
            "PyQt6.QtBluetooth",
            "PyQt6.QtWebEngine",
            "PyQt6.QtQml",
        ],
        # Build settings
        "argv_emulation": False,  # Disable argv emulation
        "strip": False,  # Don't strip binaries (can cause issues with torch)
        "optimize": 0,  # No optimization
        # Info.plist settings
        "plist": {
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "CFBundleGetInfoString": "AI-powered music stem separation",
            "CFBundleIdentifier": BUNDLE_ID,
            "CFBundleVersion": APP_VERSION,
            "CFBundleShortVersionString": APP_VERSION,
            "NSHumanReadableCopyright": "Copyright © 2026",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.13.0",  # macOS High Sierra
            # File associations for audio files
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeName": "Audio File",
                    "CFBundleTypeRole": "Viewer",
                    "LSHandlerRank": "Alternate",
                    "LSItemContentTypes": [
                        "public.mp3",
                        "public.mpeg-4-audio",
                        "com.microsoft.waveform-audio",
                        "public.audio",
                    ],
                },
            ],
        },
    },
}

# Data files (if any)
DATA_FILES = []

setup(
    app=APP,
    data_files=DATA_FILES,
    options=OPTIONS,
    setup_requires=["py2app"],
)
