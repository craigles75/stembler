"""
Minimal py2app setup for Stembler macOS application.
"""

from setuptools import setup

APP = ["src/music_stem_separator/gui_main.py"]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "packaging/macos/icon.icns",
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
    ],
    "excludes": [
        "tkinter",
        "matplotlib",
        "PIL",
        "IPython",
        "jupyter",
    ],
    "plist": {
        "CFBundleName": "Stembler",
        "CFBundleDisplayName": "Stembler",
        "CFBundleGetInfoString": "AI-powered music stem separation",
        "CFBundleIdentifier": "com.stembler.app",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "NSHumanReadableCopyright": "Copyright © 2026",
        "NSHighResolutionCapable": True,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
)
