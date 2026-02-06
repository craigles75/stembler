"""PyInstaller entry point for the Stembler Windows application.

Adds src/ to sys.path when running from source (development).
In a frozen PyInstaller bundle the package is already importable.
All application initialisation (icon, error handler, window) lives
in gui_main.main().
"""

import multiprocessing
import sys
from pathlib import Path

if __name__ == "__main__":
    # Required for PyInstaller: prevents child processes from re-executing main
    multiprocessing.freeze_support()

    if not getattr(sys, "frozen", False):
        src_path = Path(__file__).parent.parent.parent / "src"
        sys.path.insert(0, str(src_path))

    from music_stem_separator.gui_main import main  # noqa: E402

    main()
