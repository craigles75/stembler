#!/usr/bin/env python3
"""Generate platform-specific application icons from SVG source.

This script converts the icon.svg file to:
- macOS .icns format (via PNG intermediates)
- Windows .ico format

Requirements:
    pip install Pillow cairosvg
"""

import subprocess
from pathlib import Path


def generate_icons():
    """Generate application icons for all platforms."""
    packaging_dir = Path(__file__).parent
    svg_path = packaging_dir / "icon.svg"

    if not svg_path.exists():
        print(f"Error: {svg_path} not found!")
        return False

    print(f"Generating icons from {svg_path}...")

    # Check for dependencies
    try:
        import cairosvg
        from PIL import Image

        has_python_libs = True
    except ImportError:
        print("Warning: cairosvg or Pillow not installed.")
        print("Install with: pip install Pillow cairosvg")
        has_python_libs = False

    # Generate PNG sizes needed for both platforms
    sizes = [16, 32, 48, 64, 128, 256, 512]
    png_dir = packaging_dir / "temp_pngs"
    png_dir.mkdir(exist_ok=True)

    if has_python_libs:
        print("\nGenerating PNG files...")
        for size in sizes:
            png_path = png_dir / f"icon_{size}x{size}.png"
            print(f"  {size}x{size}...")
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(png_path),
                output_width=size,
                output_height=size,
            )

        # Generate Windows .ico (multiple sizes in one file)
        print("\nGenerating Windows .ico...")
        ico_path = packaging_dir / "windows" / "icon.ico"
        ico_images = []
        for size in [16, 32, 48, 64, 128, 256]:
            png_path = png_dir / f"icon_{size}x{size}.png"
            ico_images.append(Image.open(png_path))

        # Save as .ico with all sizes
        ico_images[0].save(
            ico_path,
            format="ICO",
            sizes=[(img.width, img.height) for img in ico_images],
            append_images=ico_images[1:],
        )
        print(f"  Created: {ico_path}")

        # Generate macOS .icns (requires iconutil on macOS)
        print("\nGenerating macOS .icns...")
        if _generate_icns(packaging_dir, png_dir):
            print("  Created: packaging/macos/icon.icns")
        else:
            print("  Note: Run this script on macOS to generate .icns with iconutil")
            print("  Alternative: Use an online converter for icon.svg → .icns")

        # Cleanup temp PNGs
        print("\nCleaning up temporary files...")
        for png_path in png_dir.glob("*.png"):
            png_path.unlink()
        png_dir.rmdir()

        print("\n✓ Icon generation complete!")
        return True
    else:
        print("\nAlternative: Use online converters")
        print("  macOS: https://cloudconvert.com/svg-to-icns")
        print("  Windows: https://cloudconvert.com/svg-to-ico")
        return False


def _generate_icns(packaging_dir: Path, png_dir: Path) -> bool:
    """Generate .icns file using macOS iconutil.

    Returns:
        True if successful, False if not on macOS or iconutil not available
    """
    import platform

    if platform.system() != "Darwin":
        return False

    # Check if iconutil is available
    try:
        subprocess.run(["iconutil", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    # Create iconset directory structure
    iconset_dir = packaging_dir / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    # Copy PNGs with proper naming for iconutil
    size_map = {
        16: ["icon_16x16.png"],
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: ["icon_32x32@2x.png"],
        128: ["icon_128x128.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
    }

    for size, filenames in size_map.items():
        src = png_dir / f"icon_{size}x{size}.png"
        if src.exists():
            for filename in filenames:
                dst = iconset_dir / filename
                dst.write_bytes(src.read_bytes())

    # Convert to .icns
    icns_path = packaging_dir / "macos" / "icon.icns"
    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(icns_path)], check=True
    )

    # Cleanup iconset directory
    for file in iconset_dir.glob("*.png"):
        file.unlink()
    iconset_dir.rmdir()

    return True


if __name__ == "__main__":
    generate_icons()
