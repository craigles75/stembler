"""PyInstaller entry point for the Stembler macOS application.

Adds src/ to sys.path when running from source (development).
In a frozen PyInstaller bundle the package is already importable.
All application initialisation (icon, error handler, window) lives
in gui_main.main().
"""

import multiprocessing
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Required for PyInstaller: prevents child processes from re-executing main
    multiprocessing.freeze_support()

    # In frozen bundle, add bundled bin directory to PATH for ffmpeg/ffprobe
    # Note: TORCHDYNAMO_DISABLE is set in runtime_hook.py (runs before imports)
    if getattr(sys, "frozen", False):
        bundle_bin = Path(sys._MEIPASS) / "bin"  # noqa: SLF001
        if bundle_bin.exists():
            os.environ["PATH"] = (
                str(bundle_bin) + os.pathsep + os.environ.get("PATH", "")
            )
    else:
        src_path = Path(__file__).parent.parent.parent / "src"
        sys.path.insert(0, str(src_path))

    from music_stem_separator.gui_main import main

    main()
