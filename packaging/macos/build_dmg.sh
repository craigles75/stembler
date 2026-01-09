#!/bin/bash
# DMG installer creation script for Stembler
#
# This script creates a macOS DMG installer with custom background and layout.
#
# Requirements:
#   - dist/Stembler.app must exist (run build.sh first)
#   - Optional: create-dmg (for fancier DMG with background image)
#     Install with: brew install create-dmg
#
# Usage:
#   ./packaging/macos/build_dmg.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Stembler DMG Installer Builder${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$PROJECT_ROOT"

# Check if application exists (either .app bundle or directory)
APP_PATH=""
if [ -d "dist/Stembler.app" ] && [ -x "dist/Stembler.app/Contents/MacOS/Stembler" ]; then
    APP_PATH="dist/Stembler.app"
    echo "Found: Stembler.app bundle"
elif [ -d "dist/Stembler" ] && [ -x "dist/Stembler/Stembler" ]; then
    APP_PATH="dist/Stembler"
    echo "Found: Stembler directory"
else
    echo -e "${RED}Error: dist/Stembler or dist/Stembler.app not found${NC}"
    echo "Run ./packaging/macos/build.sh first"
    exit 1
fi

# Get version from pyproject.toml
VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
DMG_NAME="Stembler-${VERSION}-macOS"

echo -e "${GREEN}[1/3]${NC} Creating DMG installer..."
echo "Version: ${VERSION}"
echo

# Use hdiutil for simple, reliable DMG creation
echo "Creating DMG installer..."

# Create temporary directory for DMG contents
DMG_TEMP="dist/dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# Copy application
echo -e "${GREEN}[2/3]${NC} Copying application files..."
cp -R "$APP_PATH" "$DMG_TEMP/"

# Create Applications symlink
ln -s /Applications "$DMG_TEMP/Applications"

# Add README if distributing as directory
if [ "$APP_PATH" = "dist/Stembler" ]; then
    cat > "$DMG_TEMP/README.txt" << 'EOF'
Stembler - AI-Powered Music Stem Separation

Installation:
1. Drag the "Stembler" folder to Applications
2. Open Applications folder
3. Double-click "Stembler/Stembler" to run

Or run directly from this disk image.

Visit: https://github.com/yourusername/stembler
EOF
fi

echo -e "${GREEN}[2/3]${NC} Creating disk image..."

# Create DMG
hdiutil create \
    -volname "Stembler" \
    -srcfolder "$DMG_TEMP" \
    -ov \
    -format UDZO \
    -fs HFS+ \
    "dist/${DMG_NAME}.dmg"

# Cleanup
rm -rf "$DMG_TEMP"

echo
echo -e "${GREEN}[3/3]${NC} DMG creation complete!"
echo
echo -e "${GREEN}✓${NC} DMG installer created:"
echo -e "  ${BLUE}dist/${DMG_NAME}.dmg${NC}"
echo

# Get file size
DMG_SIZE=$(du -h "dist/${DMG_NAME}.dmg" | cut -f1)
echo "File size: ${DMG_SIZE}"
echo

echo "To test the installer:"
echo -e "  ${BLUE}open dist/${DMG_NAME}.dmg${NC}"
echo
echo "Distribution ready!"
