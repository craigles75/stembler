# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Stembler Windows application.

To build:
    pyinstaller packaging\windows\stembler.spec

Output:
    dist\Stembler.exe - Windows executable
    dist\Stembler\ - Distribution folder with all dependencies
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Project paths
project_root = Path(SPECPATH).parent.parent
src_path = project_root / "src"

# Application metadata
app_name = "Stembler"
app_version = "0.1.0"  # Read from pyproject.toml in production

# Collect all GUI package data
gui_datas = []

# Collect PyQt6 plugins and dependencies
pyqt6_datas = collect_data_files('PyQt6')

# Collect demucs model data if needed
demucs_datas = collect_data_files('demucs', include_py_files=False)

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

# Analysis: Scan and collect all dependencies
a = Analysis(
    [str(src_path / 'music_stem_separator' / 'gui_main.py')],
    pathex=[str(src_path)],
    binaries=[],
    datas=gui_datas + pyqt6_datas + demucs_datas,
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

# EXE: Create Windows executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Don't use UPX compression (incompatible with torch)
    console=False,  # GUI app (no console window)
    disable_windowed_traceback=False,
    icon=str(Path(SPECPATH) / 'icon.ico') if (Path(SPECPATH) / 'icon.ico').exists() else None,
    version_file=None,  # Can add Windows version resource file
    uac_admin=False,  # Don't require admin privileges
    uac_uiaccess=False,
)

# COLLECT: Gather all files for distribution
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
