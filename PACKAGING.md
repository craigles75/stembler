# Stembler Packaging Guide

This guide explains how to build distributable packages of Stembler for macOS and Windows.

## Overview

Stembler uses **PyInstaller** to create standalone executables that bundle Python, all dependencies, and the application code into a single distributable package.

**Supported Platforms:**
- macOS: `.app` bundle → `.dmg` installer
- Windows: `.exe` executable → `.msi` installer

---

## Quick Start

### macOS

```bash
# 1. Build the application
./packaging/macos/build.sh

# Output: dist/Stembler/ (742MB directory containing executable)
# Executable: dist/Stembler/Stembler (54MB)

# 2. Create DMG installer
./packaging/macos/build_dmg.sh

# Output: dist/Stembler-{version}-macOS.dmg (268MB compressed)
```

**Note**: Due to a PyQt6 framework symlink incompatibility with PyInstaller, the build creates a working `dist/Stembler/` directory instead of a traditional `.app` bundle. The application works perfectly and is distributed via DMG.

### Windows

```batch
REM 1. Build the .exe
.\packaging\windows\build.bat

REM 2. Create MSI installer
python packaging\windows\build_msi.py

REM Output: dist\Stembler-{version}-win64.msi
```

---

## Prerequisites

### All Platforms

1. **Python 3.12+**
   ```bash
   python --version
   ```

2. **UV Package Manager**
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
   # Or: pip install uv
   ```

3. **Project Dependencies**
   ```bash
   # Install all dependencies including GUI
   uv sync --extra gui
   ```

4. **PyInstaller**
   ```bash
   # Installed automatically by build scripts
   # Or manually: uv pip install pyinstaller
   ```

### macOS Specific

- **Xcode Command Line Tools** (usually pre-installed)
  ```bash
  xcode-select --install
  ```

- **create-dmg** (optional, for prettier DMG)
  ```bash
  brew install create-dmg
  ```

### Windows Specific

- **Microsoft Visual C++ Build Tools** (for some dependencies)
  - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

- **cx_Freeze** (optional, for MSI creation)
  ```bash
  pip install cx_Freeze
  ```

---

## Application Icons

### Generating Icons from SVG

The project includes `packaging/icon.svg` as the source. Generate platform-specific icons:

```bash
# Install dependencies
uv pip install Pillow cairosvg

# Generate icons
python packaging/generate_icons.py
```

**Output:**
- `packaging/macos/icon.icns` - macOS icon
- `packaging/windows/icon.ico` - Windows icon

### Manual Icon Creation

If the script doesn't work on your platform:

1. **macOS .icns:**
   - Upload `packaging/icon.svg` to https://cloudconvert.com/svg-to-icns
   - Download and save to `packaging/macos/icon.icns`

2. **Windows .ico:**
   - Upload `packaging/icon.svg` to https://cloudconvert.com/svg-to-ico
   - Download and save to `packaging/windows/icon.ico`

See `packaging/ICON-README.md` for detailed instructions.

---

## macOS Packaging

### Step 1: Build the .app Bundle

```bash
./packaging/macos/build.sh
```

**What it does:**
1. Installs PyInstaller
2. Cleans previous builds
3. Runs PyInstaller with `packaging/macos/stembler.spec`
4. Creates `dist/Stembler.app`

**Build options (in `stembler.spec`):**
- Bundles all Python dependencies
- Includes PyQt6, torch, demucs, spotdl
- Excludes unnecessary packages (tkinter, matplotlib, etc.)
- Creates macOS app bundle with proper Info.plist

**Output:**
- `dist/Stembler/` - Directory containing standalone application (742MB)
- `dist/Stembler/Stembler` - Main executable (54MB)

**Testing:**
```bash
# Run the executable directly
./dist/Stembler/Stembler

# Or if .app bundle was created:
open dist/Stembler.app
```

**What Actually Happens:**
PyInstaller successfully completes:
- ✅ Analysis phase (dependency detection)
- ✅ PYZ phase (Python archive)
- ✅ EXE phase (executable creation)
- ⚠️  COLLECT phase (fails with PyQt6 framework symlink error)

Despite the COLLECT error, `dist/Stembler/` is created with everything needed to run.

### Step 2: Create DMG Installer

```bash
./packaging/macos/build_dmg.sh
```

**What it does:**
1. Checks for `dist/Stembler.app`
2. Creates DMG with Applications symlink
3. Optionally uses `create-dmg` for fancy layout
4. Outputs `dist/Stembler-{version}-macOS.dmg`

**DMG Options:**

**Method 1: Fancy DMG (requires create-dmg)**
- Custom background image
- Positioned icons
- Drag-to-Applications visual

**Method 2: Simple DMG (built-in hdiutil)**
- Basic disk image
- Applications symlink
- No custom layout

**Output:**
- `dist/Stembler-{version}-macOS.dmg` - Distributable installer

**Testing:**
```bash
# Mount and test the DMG
open dist/Stembler-*.dmg

# Drag Stembler.app to Applications
# Launch from Applications folder
```

### Code Signing (Optional)

For distribution outside the App Store, sign the app:

```bash
# Sign the .app
codesign --force --deep --sign "Developer ID Application: Your Name" dist/Stembler.app

# Verify
codesign --verify --verbose dist/Stembler.app

# Notarize for Gatekeeper
xcrun notarytool submit dist/Stembler-*.dmg --apple-id YOUR_EMAIL --wait

# Staple the notarization
xcrun stapler staple dist/Stembler.app
```

---

## Windows Packaging

### Step 1: Build the .exe

```batch
.\packaging\windows\build.bat
```

**What it does:**
1. Installs PyInstaller
2. Cleans previous builds
3. Runs PyInstaller with `packaging/windows/stembler.spec`
4. Creates `dist/Stembler/Stembler.exe` and dependencies

**Build options (in `stembler.spec`):**
- Uses `packaging/windows/launcher.py` (absolute imports, PyInstaller-compatible)
- Bundles all Python dependencies
- Includes PyQt6, torch, demucs, spotdl
- No console window (GUI mode)
- Includes icon if available

**Output:**
- `dist/Stembler/` - Folder with .exe and dependencies

**Testing:**
```batch
REM Run the executable
dist\Stembler\Stembler.exe

REM Or double-click dist\Stembler\Stembler.exe in Explorer
```

### Step 2: Create MSI Installer

```bash
python packaging/windows/build_msi.py
```

**What it does:**
1. Checks for `dist/Stembler/Stembler.exe`
2. Uses cx_Freeze or WiX to create MSI
3. Outputs `dist/Stembler-{version}-win64.msi`

**MSI Creation Options:**

**Option 1: cx_Freeze (Recommended)**
```bash
pip install cx_Freeze
python packaging/windows/build_msi.py
```

**Option 2: WiX Toolset (More Control)**
- Download from https://wixtoolset.org/
- Create `stembler.wxs` file (see WiX docs)
- More complex but more customizable

**Option 3: Inno Setup (Free Alternative)**
- Download from https://jrsoftware.org/isdl.php
- Create `.iss` script
- Popular for Windows installers

**Output:**
- `dist/Stembler-{version}-win64.msi` - Windows installer

**Testing:**
```batch
REM Install from MSI
dist\Stembler-{version}-win64.msi

REM Check: C:\Program Files\Stembler\Stembler.exe
REM Start Menu shortcut should appear
```

---

## Known Issues

### macOS: PyQt6 Framework Symlink Error (PyInstaller)

**Error:**
```
FileExistsError: [Errno 17] File exists: 'Versions/Current/Resources' ->
'.../PyQt6/Qt6/lib/QtBluetooth.framework/Resources'
```

**Root Cause:**
PyInstaller 6.x attempts to preserve macOS framework structures and create symlinks, but PyQt6 6.x frameworks already contain these symlinks. When COLLECT tries to create them again, it fails with FileExistsError.

**Status:** This is a known incompatibility between PyInstaller 6.x and PyQt6 6.x on macOS.

**Workaround Option 1: Use py2app (Recommended for macOS)**
py2app is the macOS-native packaging tool and handles frameworks correctly:
```bash
# Install py2app
uv pip install py2app

# Build (if compatible with your project structure)
python setup.py py2app
```

**Workaround Option 2: Manual .app creation**
If PyInstaller's COLLECT stage fails, the EXE is still built successfully:
```bash
# Run PyInstaller (will fail at COLLECT, but EXE exists)
pyinstaller packaging/macos/stembler.spec

# The executable exists at: build/stembler/Stembler
# Run it directly for testing:
./build/stembler/Stembler

# To create a basic .app structure manually:
mkdir -p dist/Stembler.app/Contents/MacOS
cp -R build/stembler/* dist/Stembler.app/Contents/MacOS/
cp packaging/macos/icon.icns dist/Stembler.app/Contents/Resources/
# Create Info.plist manually or copy from spec file
```

**Workaround Option 3: Wait for fix**
- Monitor PyInstaller GitHub for fixes
- Try PyInstaller 7.x when released (may resolve framework handling)

**Alternative Solutions:**
- Use Docker/VM with older PyQt5 version
- Use briefcase packaging tool
- Package as a simple executable directory (onedir mode) without .app bundle

---

## Troubleshooting

### Build Fails: Missing Modules

**Problem:** PyInstaller can't find certain modules

**Solution:** Add to `hiddenimports` in spec file:
```python
hidden_imports = [
    'your_missing_module',
]
```

### Build Succeeds but App Crashes

**Problem:** Runtime import errors

**Solution 1:** Check PyInstaller warnings
```bash
# Look for "WARNING: Hidden import not found"
```

**Solution 2:** Test with console mode
```python
# In spec file, temporarily set:
console=True  # Shows error messages
```

**Solution 3:** Add data files
```python
# In spec file:
datas=[
    ('path/to/data', 'destination_in_app'),
]
```

### ImportError: attempted relative import with no known parent package

**Problem:** Application crashes with:
```
File "gui_main.py" line 6
ImportError: attempted relative import with no known parent package
```

**Root Cause:** PyInstaller cannot handle relative imports in the entry point script.

**Solution:** The spec file has been updated to use `launcher.py` which uses absolute imports instead of `gui_main.py` with relative imports.

**If you still see this error:**
1. Make sure you're using the latest spec file:
   - macOS: `packaging/macos/stembler.spec` (uses `packaging/macos/launcher.py`)
   - Windows: `packaging/windows/stembler.spec` (uses `packaging/windows/launcher.py`)
2. Clean and rebuild:
   ```bash
   # Delete old build
   rm -rf build/ dist/

   # Rebuild
   pyinstaller packaging/macos/stembler.spec --clean
   ```

### macOS: "App is Damaged" Error

**Problem:** Gatekeeper blocks unsigned apps

**Solution 1:** Allow in System Preferences
```bash
# System Preferences > Security & Privacy > Open Anyway
```

**Solution 2:** Remove quarantine attribute
```bash
xattr -cr dist/Stembler.app
```

**Solution 3:** Code sign the app (see above)

### Windows: Antivirus False Positive

**Problem:** Antivirus flags the .exe as malware

**Solution:** This is common with PyInstaller executables

1. Submit to antivirus vendors as false positive
2. Code sign the executable with a certificate
3. Use a trusted installer (MSI instead of bare .exe)

### Large File Size

**Problem:** Executable is several hundred MB

**This is normal** because it includes:
- Python runtime (~50MB)
- PyQt6 (~100MB)
- PyTorch (~500MB)
- Demucs models (~100MB+)

**To reduce size:**
```python
# In spec file:
excludes=[
    'tkinter',
    'matplotlib',
    'IPython',
    # Add more unused packages
]
```

---

## File Structure

After successful builds:

```
dist/
├── Stembler.app/                    # macOS app bundle
│   ├── Contents/
│   │   ├── MacOS/Stembler          # Executable
│   │   ├── Resources/              # Icons, data
│   │   └── Info.plist              # App metadata
├── Stembler/                        # Windows distribution
│   ├── Stembler.exe                # Executable
│   ├── python312.dll               # Python runtime
│   └── [dependencies]              # All bundled libs
├── Stembler-0.1.0-macOS.dmg        # macOS installer
└── Stembler-0.1.0-win64.msi        # Windows installer
```

---

## Distribution Checklist

Before releasing:

### Testing
- [ ] Test on clean macOS system (no Python installed)
- [ ] Test on clean Windows system (no Python installed)
- [ ] Verify all features work (drag-drop, Spotify, settings, etc.)
- [ ] Test with various audio file formats
- [ ] Check error handling and user-friendly messages

### Packaging
- [ ] Version number updated in `pyproject.toml`
- [ ] Icons generated for both platforms
- [ ] macOS .app built and tested
- [ ] macOS DMG created
- [ ] Windows .exe built and tested
- [ ] Windows MSI created

### Optional (for public distribution)
- [ ] macOS app code signed
- [ ] macOS app notarized
- [ ] Windows executable signed with certificate
- [ ] README updated with download links
- [ ] Release notes created
- [ ] GitHub release with binaries

---

## Continuous Integration

### GitHub Actions Example

```yaml
name: Build Installers

on:
  release:
    types: [created]

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Build macOS
        run: |
          ./packaging/macos/build.sh
          ./packaging/macos/build_dmg.sh
      - name: Upload DMG
        uses: actions/upload-artifact@v3
        with:
          name: Stembler-macOS
          path: dist/*.dmg

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Build Windows
        run: |
          .\packaging\windows\build.bat
          python packaging\windows\build_msi.py
      - name: Upload MSI
        uses: actions/upload-artifact@v3
        with:
          name: Stembler-Windows
          path: dist/*.msi
```

---

## Support

For packaging issues:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Review spec file comments
3. Enable verbose mode: `pyinstaller --debug all`
4. File an issue with build logs

---

**Last Updated:** 2026-01-09
**PyInstaller Version:** 6.0+
**Python Version:** 3.12+
