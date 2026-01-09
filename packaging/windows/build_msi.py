#!/usr/bin/env python3
"""MSI installer creation script for Stembler Windows application.

This script creates a Windows MSI installer using cx_Freeze or WiX Toolset.

Requirements:
    - dist/Stembler/ must exist (run build.bat first)
    - cx_Freeze (simpler) OR WiX Toolset (more features)
      Install cx_Freeze: pip install cx_Freeze
      Install WiX: https://wixtoolset.org/

Usage:
    python packaging/windows/build_msi.py
"""

import subprocess
import sys
from pathlib import Path
import tomllib


def main():
    """Build MSI installer for Windows."""
    print("=" * 40)
    print("  Stembler MSI Installer Builder")
    print("=" * 40)
    print()

    # Get project root
    project_root = Path(__file__).parent.parent.parent
    dist_dir = project_root / "dist" / "Stembler"

    # Check if built executable exists
    if not dist_dir.exists():
        print("Error: dist/Stembler/ not found")
        print("Run build.bat first to create the executable")
        return 1

    exe_path = dist_dir / "Stembler.exe"
    if not exe_path.exists():
        print(f"Error: {exe_path} not found")
        return 1

    # Get version from pyproject.toml
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    version = pyproject["project"]["version"]
    print(f"Version: {version}")
    print()

    # Try cx_Freeze first (simpler)
    if _try_cx_freeze(project_root, dist_dir, version):
        return 0

    # Fall back to WiX if available
    if _try_wix(project_root, dist_dir, version):
        return 0

    # No installer tool available
    print("\nError: No MSI installer tool found!")
    print()
    print("Option 1 (Recommended): Install cx_Freeze")
    print("  pip install cx_Freeze")
    print()
    print("Option 2: Install WiX Toolset")
    print("  Download from: https://wixtoolset.org/")
    print()
    print("Option 3: Use Inno Setup (free)")
    print("  Download from: https://jrsoftware.org/isdl.php")
    print()

    return 1


def _try_cx_freeze(project_root: Path, dist_dir: Path, version: str) -> bool:
    """Try to build MSI using cx_Freeze.

    Returns:
        True if successful, False if cx_Freeze not available
    """
    try:
        import cx_Freeze
        from cx_Freeze import setup, Executable
    except ImportError:
        return False

    print("[1/3] Building MSI with cx_Freeze...")

    # Create temporary setup.py for cx_Freeze
    setup_content = f'''
from cx_Freeze import setup, Executable
import sys

# Build options
build_exe_options = {{
    "packages": [],
    "excludes": [],
    "include_files": [
        ("dist/Stembler", "lib"),
    ],
}}

# MSI options
bdist_msi_options = {{
    "upgrade_code": "{{12345678-1234-1234-1234-123456789ABC}}",  # Generate unique GUID
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\\Stembler",
}}

setup(
    name="Stembler",
    version="{version}",
    description="AI-powered music stem separation tool",
    options={{
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    }},
    executables=[
        Executable(
            "dist/Stembler/Stembler.exe",
            base="Win32GUI",
            icon="packaging/windows/icon.ico" if Path("packaging/windows/icon.ico").exists() else None,
            shortcut_name="Stembler",
            shortcut_dir="DesktopFolder",
        )
    ],
)
'''

    setup_path = project_root / "setup_temp.py"
    setup_path.write_text(setup_content)

    try:
        # Run cx_Freeze
        print("[2/3] Running cx_Freeze bdist_msi...")
        subprocess.run(
            [sys.executable, "setup_temp.py", "bdist_msi"],
            cwd=project_root,
            check=True,
        )

        print("[3/3] MSI creation complete!")
        print()
        print(f"✓ MSI installer created:")
        print(f"  dist/Stembler-{version}-win64.msi")
        print()

        return True

    finally:
        # Cleanup
        if setup_path.exists():
            setup_path.unlink()

    return False


def _try_wix(project_root: Path, dist_dir: Path, version: str) -> bool:
    """Try to build MSI using WiX Toolset.

    Returns:
        True if successful, False if WiX not available
    """
    # Check if WiX is installed
    try:
        subprocess.run(
            ["candle", "-?"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    print("[1/4] Building MSI with WiX Toolset...")
    print()
    print("Note: WiX setup requires creating a .wxs file first")
    print("See packaging/windows/stembler.wxs.example for template")
    print()

    # WiX requires more setup - provide instructions
    print("To use WiX:")
    print("1. Create packaging/windows/stembler.wxs from template")
    print("2. Run: candle packaging/windows/stembler.wxs")
    print("3. Run: light -ext WixUIExtension stembler.wixobj")
    print()

    return False


if __name__ == "__main__":
    sys.exit(main())
