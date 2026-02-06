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

echo -e "${GREEN}[4/7]${NC} Patching torch._numpy._ufuncs.py (Layer 2 defense)..."
# Replace vars()[name] loop patterns that crash under PyInstaller bytecode
# with dict-comprehension + globals().update() which survives compilation.
UFUNCS_PATH=$(uv run python -c "
import torch._numpy._ufuncs as m; print(m.__file__)
" 2>/dev/null || true)

UFUNCS_BACKUP=""
if [ -n "$UFUNCS_PATH" ] && [ -f "$UFUNCS_PATH" ]; then
    UFUNCS_BACKUP="${UFUNCS_PATH}.bak"
    cp "$UFUNCS_PATH" "$UFUNCS_BACKUP"
    echo "  Backed up: $UFUNCS_PATH"

    uv run python -c "
import re, sys

path = sys.argv[1]
with open(path) as f:
    src = f.read()

# Pattern: for name in <list>:\n    ufunc = getattr(<mod>, name)\n    vars()[name] = <wrapper>(ufunc)
pattern = (
    r'for name in (\w+):\s*\n'
    r'\s+ufunc = getattr\((\w+), name\)\s*\n'
    r'\s+vars\(\)\[name\] = (\w+)\(ufunc\)'
)

def replacer(m):
    lst, mod, wrapper = m.group(1), m.group(2), m.group(3)
    return (
        f'globals().update({{\n'
        f'    _n: {wrapper}(getattr({mod}, _n))\n'
        f'    for _n in {lst}\n'
        f'}})'
    )

new_src, count = re.subn(pattern, replacer, src)
if count == 0:
    print('WARNING: No vars()[name] patterns found to patch', file=sys.stderr)
else:
    print(f'  Patched {count} vars()[name] pattern(s)')
with open(path, 'w') as f:
    f.write(new_src)
" "$UFUNCS_PATH"
else
    echo -e "  ${BLUE}(skipped — torch._numpy._ufuncs not found)${NC}"
fi

# Ensure backup is restored on exit (success or failure)
cleanup_ufuncs() {
    if [ -n "$UFUNCS_BACKUP" ] && [ -f "$UFUNCS_BACKUP" ]; then
        mv "$UFUNCS_BACKUP" "$UFUNCS_PATH"
        echo "  Restored original: $UFUNCS_PATH"
    fi
}
trap cleanup_ufuncs EXIT

echo -e "${GREEN}[5/7]${NC} Building macOS executable..."
echo "This may take several minutes (especially on first build)..."
echo

# Run PyInstaller with the spec file
# The BUNDLE step produces dist/Stembler.app directly
uv run pyinstaller packaging/macos/stembler.spec \
    --clean \
    --noconfirm 2>&1 | grep -v "FileExistsError.*Versions/Current/Resources" || true

# Check if the .app bundle was created
if [ -d "dist/Stembler.app" ] && [ -x "dist/Stembler.app/Contents/MacOS/Stembler" ]; then
    echo
    echo -e "${GREEN}[6/7]${NC} Testing executable..."

    # Start the app and check it stays alive for 3 seconds
    dist/Stembler.app/Contents/MacOS/Stembler &
    STEM_PID=$!
    sleep 3
    if ps -p $STEM_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Executable works!"
        kill $STEM_PID 2>/dev/null
        wait $STEM_PID 2>/dev/null
    else
        echo -e "${RED}✗${NC} Executable exited immediately — check logs"
    fi

    echo -e "${GREEN}[7/7]${NC} Build successful!"
    echo
    echo -e "${GREEN}✓${NC} Application created:"
    echo -e "  ${BLUE}dist/Stembler.app${NC} (signed .app bundle)"
    echo
    echo "To test the application:"
    echo -e "  ${BLUE}open dist/Stembler.app${NC}"
    echo
    echo "To create a DMG installer:"
    echo -e "  ${BLUE}./packaging/macos/build_dmg.sh${NC}"
    echo
else
    echo
    echo -e "${RED}✗${NC} Build failed!"
    echo ".app bundle not found at dist/Stembler.app"
    echo "Check the output above for errors."
    exit 1
fi
