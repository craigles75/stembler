#!/bin/bash
# Create macOS .app bundle from PyInstaller dist output
# This script works around the PyQt6 framework symlink issue

set -e

APP_NAME="Stembler"
BUNDLE_ID="com.stembler.app"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Read version from pyproject.toml
VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('$PROJECT_ROOT/pyproject.toml', 'rb'))['project']['version'])")
DIST_DIR="$PROJECT_ROOT/dist"

echo "========================================"
echo "  Creating $APP_NAME.app Bundle"
echo "========================================"
echo

# Check if dist/Stembler exists
if [ ! -d "$DIST_DIR/$APP_NAME" ]; then
    echo "Error: $DIST_DIR/$APP_NAME not found!"
    echo "Run PyInstaller first: pyinstaller packaging/macos/stembler.spec"
    exit 1
fi

# Create .app bundle structure
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
echo "[1/5] Creating .app bundle structure..."
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"
mkdir -p "$APP_BUNDLE/Contents/Frameworks"

# Copy application files
echo "[2/5] Copying application files..."
cp -R "$DIST_DIR/$APP_NAME/"* "$APP_BUNDLE/Contents/MacOS/"

# Copy icon
if [ -f "$SCRIPT_DIR/icon.icns" ]; then
    echo "[3/5] Copying icon..."
    cp "$SCRIPT_DIR/icon.icns" "$APP_BUNDLE/Contents/Resources/"
else
    echo "[3/5] Warning: icon.icns not found, skipping..."
fi

# Create Info.plist
echo "[4/5] Creating Info.plist..."
cat > "$APP_BUNDLE/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>$APP_NAME</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>$VERSION</string>
    <key>CFBundleVersion</key>
    <string>$VERSION</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2026</string>
    <key>CFBundleGetInfoString</key>
    <string>AI-powered music stem separation</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>Audio File</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSHandlerRank</key>
            <string>Alternate</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>public.mp3</string>
                <string>public.mpeg-4-audio</string>
                <string>com.microsoft.waveform-audio</string>
                <string>public.audio</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
PLIST

# Make executable executable
echo "[5/5] Setting permissions..."
chmod +x "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

echo
echo "✓ .app bundle created successfully!"
echo
echo "Location: $APP_BUNDLE"
echo
echo "To test:"
echo "  open \"$APP_BUNDLE\""
echo
echo "To create DMG:"
echo "  ./packaging/macos/build_dmg.sh"
echo
