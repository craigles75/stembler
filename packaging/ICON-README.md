# Application Icon

This directory contains the application icon source and platform-specific builds.

## Source

- `icon.svg` - Vector source file (512x512) with Spotify green gradient and music note design

## Platform-Specific Formats

### macOS (.icns)

To generate the macOS icon:

```bash
# Method 1: Using iconutil (macOS only)
# 1. Create iconset directory
mkdir icon.iconset

# 2. Generate multiple sizes using ImageMagick or similar
# (requires svg2png or similar tool)
for size in 16 32 64 128 256 512; do
  rsvg-convert -w $size -h $size icon.svg > icon.iconset/icon_${size}x${size}.png
  rsvg-convert -w $((size*2)) -h $((size*2)) icon.svg > icon.iconset/icon_${size}x${size}@2x.png
done

# 3. Convert to .icns
iconutil -c icns icon.iconset -o macos/icon.icns

# Method 2: Using png2icns (if available)
# Install: brew install libicns
# png2icns icon.icns icon_512x512.png

# Method 3: Using online converter
# Upload icon.svg to https://cloudconvert.com/svg-to-icns
# Download and save to macos/icon.icns
```

### Windows (.ico)

To generate the Windows icon:

```bash
# Method 1: Using ImageMagick
# Install: brew install imagemagick (macOS) or choco install imagemagick (Windows)
magick convert icon.svg -define icon:auto-resize=256,128,64,48,32,16 windows/icon.ico

# Method 2: Using online converter
# Upload icon.svg to https://cloudconvert.com/svg-to-ico
# Download and save to windows/icon.ico
```

## Quick Setup (Using Online Converter)

If you don't have the command-line tools installed:

1. Go to https://cloudconvert.com/svg-to-icns
2. Upload `icon.svg`
3. Download the generated `icon.icns`
4. Save to `packaging/macos/icon.icns`

5. Go to https://cloudconvert.com/svg-to-ico
6. Upload `icon.svg`
7. Download the generated `icon.ico`
8. Save to `packaging/windows/icon.ico`

## Dependencies

For local conversion:
- **macOS**: `iconutil` (built-in), `librsvg` (brew install librsvg)
- **Windows**: ImageMagick (choco install imagemagick)
- **Cross-platform**: Python Pillow + cairosvg

## Current Status

- [x] SVG source created
- [x] macOS .icns generated (134KB, full iconset)
- [x] Windows .ico generated (22KB, 6 sizes: 16/32/48/64/128/256)
- [x] Qt runtime icon set via `gui_main.py` (512x512 PNG in gui/resources/)
- [x] PyInstaller specs updated to bundle gui/resources/
