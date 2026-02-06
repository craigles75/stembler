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
import tomllib
with open(str(project_root / "pyproject.toml"), "rb") as _f:
    app_version = tomllib.load(_f)["project"]["version"]
bundle_identifier = "com.stembler.app"

# Collect all GUI package data
gui_resources = str(project_root / "src" / "music_stem_separator" / "gui" / "resources")
gui_datas = [(gui_resources, "gui/resources")]

# Collect PyQt6 plugins and dependencies
pyqt6_datas = collect_data_files('PyQt6')

# Collect demucs model data if needed
demucs_datas = collect_data_files('demucs', include_py_files=False)

# Collect pykakasi data (needed by spotdl for Japanese text processing)
pykakasi_datas = collect_data_files('pykakasi', include_py_files=False)

# Collect scipy data (needed for signal processing)
scipy_datas = collect_data_files('scipy', include_py_files=False)

# Bundle ffmpeg/ffprobe (required by torchaudio/demucs for audio loading)
# Use static builds from packaging/macos/bin/ (no external dependencies)
ffmpeg_binaries = []
ffmpeg_bin_dir = Path(SPECPATH) / 'bin'
for binary_name in ['ffmpeg', 'ffprobe']:
    binary_path = ffmpeg_bin_dir / binary_name
    if binary_path.exists():
        ffmpeg_binaries.append((str(binary_path), 'bin'))
        print(f"Bundling {binary_name} from: {binary_path}")
    else:
        print(f"WARNING: {binary_name} not found at {binary_path}")

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
# Additional demucs dependencies
hidden_imports += collect_submodules('einops')
hidden_imports += collect_submodules('openunmix')
hidden_imports += collect_submodules('dora')
hidden_imports += collect_submodules('torch')
hidden_imports += collect_submodules('torchaudio')

# Analysis: Scan and collect all dependencies
a = Analysis(
    [str(Path(SPECPATH) / 'launcher.py')],
    pathex=[str(src_path)],
    binaries=ffmpeg_binaries,
    datas=gui_datas + pyqt6_datas + demucs_datas + pykakasi_datas + scipy_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[str(Path(SPECPATH) / 'runtime_hook.py')],
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
        # Layer 3: Exclude torch._numpy (stubs provided by runtime_hook.py).
        # These modules contain vars()[name] loops that crash under PyInstaller
        # bytecode compilation. Excluding them removes the crash source entirely.
        'torch._numpy',
        'torch._numpy._binary_ufuncs_impl',
        'torch._numpy._casting_dicts',
        'torch._numpy._dtypes',
        'torch._numpy._dtypes_impl',
        'torch._numpy._funcs',
        'torch._numpy._funcs_impl',
        'torch._numpy._getlimits',
        'torch._numpy._ndarray',
        'torch._numpy._normalizations',
        'torch._numpy._reductions_impl',
        'torch._numpy._ufuncs',
        'torch._numpy._unary_ufuncs_impl',
        'torch._numpy._util',
        'torch._numpy.fft',
        'torch._numpy.linalg',
        'torch._numpy.random',
        'torch._numpy.testing',
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

# Pre-clean dist directories to avoid symlink conflicts
for dist_name in [app_name, f'{app_name}.app']:
    dist_path = project_root / 'dist' / dist_name
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

# BUNDLE: Create macOS .app bundle
app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    icon=str(Path(SPECPATH) / 'icon.icns') if (Path(SPECPATH) / 'icon.icns').exists() else None,
    bundle_identifier=bundle_identifier,
    version=app_version,
    info_plist={
        'CFBundleName': app_name,
        'CFBundleDisplayName': app_name,
        'CFBundleGetInfoString': 'AI-powered music stem separation',
        'CFBundleIdentifier': bundle_identifier,
        'CFBundleVersion': app_version,
        'CFBundleShortVersionString': app_version,
        'NSHumanReadableCopyright': 'Copyright © 2026',
        'NSHighResolutionCapable': 'True',
        'LSMinimumSystemVersion': '10.13.0',  # macOS High Sierra
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Audio File',
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': [
                    'public.mp3',
                    'public.mpeg-4-audio',
                    'com.microsoft.waveform-audio',
                    'public.audio',
                ],
            },
        ],
    },
)
