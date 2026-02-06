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
import tomllib
with open(str(project_root / "pyproject.toml"), "rb") as _f:
    app_version = tomllib.load(_f)["project"]["version"]

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
    binaries=[],
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
