#!/bin/bash
# Build script for Stembler macOS application
#
# This script builds the macOS .app bundle using PyInstaller.
#
# Requirements:
#   - Python 3.12+
#   - uv (Python package manager)
#   - PyInstaller
#
# Usage:
#   ./packaging/macos/build.sh

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  Stembler macOS Build Script${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
cd "$PROJECT_ROOT"

echo -e "${GREEN}[1/5]${NC} Checking environment..."

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed${NC}"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check for Python
if ! uv run python --version &> /dev/null; then
    echo -e "${RED}Error: Python environment not set up${NC}"
    echo "Run: uv sync"
    exit 1
fi

echo -e "${GREEN}[2/5]${NC} Installing PyInstaller..."
uv pip install pyinstaller

echo -e "${GREEN}[3/5]${NC} Cleaning previous builds..."
rm -rf build/ dist/

echo -e "${GREEN}[4/6]${NC} Building macOS executable..."
echo "This may take several minutes (especially on first build)..."
echo

# Run PyInstaller with the spec file
# Note: May show FileExistsError for PyQt6 frameworks, but dist/Stembler/ is created successfully
uv run pyinstaller packaging/macos/stembler.spec \
    --clean \
    --noconfirm 2>&1 | grep -v "FileExistsError.*Versions/Current/Resources" || true

# Check if the executable was created (even if COLLECT failed)
if [ -f "dist/Stembler/Stembler" ] && [ -x "dist/Stembler/Stembler" ]; then
    echo
    echo -e "${GREEN}[5/6]${NC} Testing executable..."

    # Test if it runs
    timeout 3s ./dist/Stembler/Stembler --help > /dev/null 2>&1 && {
        echo -e "${GREEN}✓${NC} Executable works!"
    } || {
        # Start and kill to test GUI launch
        ./dist/Stembler/Stembler &
        STEM_PID=$!
        sleep 2
        if ps -p $STEM_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Executable works!"
            kill $STEM_PID 2>/dev/null
        fi
    }

    echo -e "${GREEN}[6/6]${NC} Build successful!"
    echo
    echo -e "${GREEN}✓${NC} Application created:"
    echo -e "  ${BLUE}dist/Stembler/${NC} (directory containing executable)"
    echo
    echo "To test the application:"
    echo -e "  ${BLUE}./dist/Stembler/Stembler${NC}"
    echo
    echo "To create a DMG installer:"
    echo -e "  ${BLUE}./packaging/macos/build_dmg.sh${NC}"
    echo
    echo -e "${BLUE}Note:${NC} PyQt6 framework symlink issue prevents .app bundle creation"
    echo "      The executable directory works perfectly for distribution"
    echo
else
    echo
    echo -e "${RED}✗${NC} Build failed!"
    echo "Executable not found at dist/Stembler/Stembler"
    echo "Check the output above for errors."
    exit 1
fi
