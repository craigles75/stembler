"""Shared fixtures for GUI widget tests.

All GUI tests run under the offscreen Qt platform so they require no display.
The QApplication instance is created once per session; Qt does not permit more
than one QApplication to exist simultaneously.
"""

import os
import sys

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session", autouse=True)
def qt_app():
    """Create a single QApplication for the entire test session.

    Sets QT_QPA_PLATFORM=offscreen so the tests work in CI / headless
    environments without a display server.
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
