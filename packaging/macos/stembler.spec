# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Stembler macOS application.

To build:
    pyinstaller packaging/macos/stembler.spec

Output:
    dist/Stembler.app - macOS application bundle
"""

import sys
import os
import shutil
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Project paths
project_root = Path(SPECPATH).parent.parent
src_path = project_root / "src"

# Application metadata
app_name = "Stembler"
app_version = "0.1.0"  # Read from pyproject.toml in production
bundle_identifier = "com.stembler.app"

# Collect all GUI package data
gui_datas = []

# Collect PyQt6 plugins and dependencies
pyqt6_datas = collect_data_files('PyQt6')

# Collect demucs model data if needed
demucs_datas = collect_data_files('demucs', include_py_files=False)

# Collect pykakasi data (needed by spotdl for Japanese text processing)
pykakasi_datas = collect_data_files('pykakasi', include_py_files=False)

# Collect scipy data (needed for signal processing)
scipy_datas = collect_data_files('scipy', include_py_files=False)

# Hidden imports (packages not auto-detected)
hidden_imports = [
    # PyQt6 modules
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    # Audio processing
    'torch',
    'torchaudio',
    'demucs',
    'librosa',
    'soundfile',
    'scipy',
    'numpy',
    # Spotify/Download
    'spotdl',
    'requests',
    # Utilities
    'platformdirs',
    'click',
]

# Collect all submodules for core packages
hidden_imports += collect_submodules('music_stem_separator')
hidden_imports += collect_submodules('demucs')
hidden_imports += collect_submodules('scipy.signal')
hidden_imports += collect_submodules('scipy.stats')
hidden_imports += collect_submodules('scipy.sparse')

# Analysis: Scan and collect all dependencies
a = Analysis(
    [str(Path(SPECPATH) / 'launcher.py')],
    pathex=[str(src_path)],
    binaries=[],
    datas=gui_datas + pyqt6_datas + demucs_datas + pykakasi_datas + scipy_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary packages to reduce size
        'tkinter',
        'matplotlib',
        'PIL',
        'IPython',
        'jupyter',
        # Exclude unused Qt modules to avoid symlink issues
        'PyQt6.Qt3DAnimation',
        'PyQt6.Qt3DCore',
        'PyQt6.Qt3DExtras',
        'PyQt6.Qt3DInput',
        'PyQt6.Qt3DLogic',
        'PyQt6.Qt3DRender',
        'PyQt6.QtBluetooth',
        'PyQt6.QtWebEngine',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuick3D',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ: Create Python zip archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# EXE: Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Don't strip binaries (can cause issues with torch)
    upx=False,  # Don't use UPX compression (incompatible with torch)
    console=False,  # GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,  # macOS argv emulation for file associations
    target_arch=None,
    codesign_identity=None,  # Set to Apple Developer ID for distribution
    entitlements_file=None,
)

# COLLECT: Gather all files for the bundle
# Custom collection with symlink handling for PyQt6 framework issue
import shutil

# Pre-clean dist directory to avoid symlink conflicts
dist_path = project_root / 'dist' / app_name
if dist_path.exists():
    print(f"Removing existing dist directory: {dist_path}")
    shutil.rmtree(dist_path)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=app_name,
)

# Note: BUNDLE target commented out due to PyQt6 framework symlink issues
# To create .app manually: mkdir -p dist/Stembler.app/Contents/MacOS && cp -R dist/Stembler/* dist/Stembler.app/Contents/MacOS/
# For now, run executable directly: ./dist/Stembler/Stembler

# # BUNDLE: Create macOS .app bundle
# app = BUNDLE(
#     coll,
#     name=f'{app_name}.app',
#     icon=str(Path(SPECPATH) / 'icon.icns') if (Path(SPECPATH) / 'icon.icns').exists() else None,
#     bundle_identifier=bundle_identifier,
#     version=app_version,
#     info_plist={
#         'CFBundleName': app_name,
#         'CFBundleDisplayName': app_name,
#         'CFBundleGetInfoString': 'AI-powered music stem separation',
#         'CFBundleIdentifier': bundle_identifier,
#         'CFBundleVersion': app_version,
#         'CFBundleShortVersionString': app_version,
#         'NSHumanReadableCopyright': 'Copyright © 2026',
#         'NSHighResolutionCapable': 'True',
#         'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
#         # File associations for audio files
#         'CFBundleDocumentTypes': [
#             {
#                 'CFBundleTypeName': 'Audio File',
#                 'CFBundleTypeRole': 'Viewer',
#                 'LSHandlerRank': 'Alternate',
#                 'LSItemContentTypes': [
#                     'public.mp3',
#                     'public.mpeg-4-audio',
#                     'com.microsoft.waveform-audio',
#                     'public.audio',
#                 ],
#             },
#         ],
#     },
# )
