"""Tests for the FileInputWidget clear button behaviour.

Every test instantiates a real FileInputWidget against the offscreen Qt
platform (see conftest.py).  No widget internals are mocked; the only
boundary mock is a temporary .mp3 file on disk for the local-file path,
because AudioInput checks Path.exists().

Note on visibility assertions
-----------------------------
Qt's QWidget.isVisible() returns True only when the entire ancestor chain
has been mapped to a window.  In offscreen / headless tests the top-level
widget is never shown, so isVisible() is always False even after show() is
called.  We use isHidden() instead: it reflects only the widget's *own*
explicit visibility flag, which is what show()/hide() toggle.
"""

import tempfile
from pathlib import Path

import pytest

from music_stem_separator.gui.widgets.file_input import FileInputWidget

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A valid Spotify track URL that AudioInput recognises without filesystem I/O.
SPOTIFY_URL = "https://open.spotify.com/track/4uLU6hMCjMI75M1A2tKUQC"

# The default drop-zone placeholder text fragment (used to verify reset).
DROP_PLACEHOLDER_FRAGMENT = "Drag and drop"


@pytest.fixture()
def widget(qt_app):
    """Fresh FileInputWidget, destroyed after each test."""
    w = FileInputWidget()
    yield w
    w.deleteLater()
    qt_app.processEvents()


@pytest.fixture()
def mp3_file():
    """A real (empty) .mp3 file on disk so AudioInput.is_valid returns True."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        path = f.name
    yield path
    Path(path).unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Clear button visibility
# ---------------------------------------------------------------------------


class TestClearButtonVisibility:
    """The clear button must appear only in the valid-input (success) state."""

    def test_hidden_on_construction(self, widget):
        """Button is not visible when the widget is first created."""
        assert widget.clear_button.isHidden()

    def test_shown_after_valid_spotify_url(self, widget):
        """Button appears after a valid Spotify URL is entered."""
        widget.set_path(SPOTIFY_URL)
        assert not widget.clear_button.isHidden()

    def test_shown_after_valid_local_file(self, widget, mp3_file):
        """Button appears after a valid local audio file path is entered."""
        widget.set_path(mp3_file)
        assert not widget.clear_button.isHidden()

    def test_hidden_after_invalid_input(self, widget):
        """Button stays hidden when an invalid path is entered."""
        widget.set_path("this-file-does-not-exist.mp3")
        assert widget.clear_button.isHidden()

    def test_hidden_after_empty_input(self, widget):
        """Button stays hidden when the path field is cleared to empty."""
        widget.set_path(SPOTIFY_URL)
        assert not widget.clear_button.isHidden()  # precondition

        widget.path_input.clear()  # triggers _on_path_changed -> _clear_validation
        assert widget.clear_button.isHidden()


# ---------------------------------------------------------------------------
# Clear button action
# ---------------------------------------------------------------------------


class TestClearButtonAction:
    """Clicking the clear button must fully reset the widget to its initial state."""

    def test_clear_resets_path_input(self, widget):
        """path_input text is empty after clear."""
        widget.set_path(SPOTIFY_URL)
        widget.clear()
        assert widget.path_input.text() == ""

    def test_clear_resets_current_input(self, widget):
        """_current_input is None after clear."""
        widget.set_path(SPOTIFY_URL)
        assert widget.is_valid()  # precondition

        widget.clear()
        assert widget._current_input is None
        assert not widget.is_valid()

    def test_clear_hides_button(self, widget):
        """The clear button itself is hidden after it is clicked."""
        widget.set_path(SPOTIFY_URL)
        assert not widget.clear_button.isHidden()  # precondition

        widget.clear()
        assert widget.clear_button.isHidden()

    def test_clear_restores_drop_label_placeholder(self, widget):
        """The drop label text reverts to the default drag-and-drop prompt."""
        widget.set_path(SPOTIFY_URL)
        widget.clear()
        assert DROP_PLACEHOLDER_FRAGMENT in widget.drop_label.text()

    def test_clear_restores_separator_visibility(self, widget):
        """The '— OR —' separator is shown again after clear."""
        widget.set_path(SPOTIFY_URL)
        assert widget.separator_label.isHidden()  # hidden in valid state

        widget.clear()
        assert not widget.separator_label.isHidden()

    def test_clear_restores_drop_label_min_height(self, widget):
        """The drop label minimum height is restored to the full 180px zone."""
        widget.set_path(SPOTIFY_URL)
        assert widget.drop_label.minimumHeight() == 0  # collapsed in valid state

        widget.clear()
        assert widget.drop_label.minimumHeight() == 180

    def test_clear_via_clicked_signal(self, widget):
        """Simulating a button click (not calling clear() directly) works."""
        widget.set_path(SPOTIFY_URL)
        widget.clear_button.click()  # triggers the connected slot

        assert widget.path_input.text() == ""
        assert widget.clear_button.isHidden()
        assert widget._current_input is None


# ---------------------------------------------------------------------------
# Enabled / disabled state
# ---------------------------------------------------------------------------


class TestClearButtonEnabled:
    """The clear button participates in the widget-wide enable/disable cycle."""

    def test_button_disabled_when_widget_disabled(self, widget):
        """set_enabled(False) disables the clear button."""
        widget.set_path(SPOTIFY_URL)
        assert widget.clear_button.isEnabled()  # precondition

        widget.set_enabled(False)
        assert not widget.clear_button.isEnabled()

    def test_button_re_enabled_when_widget_enabled(self, widget):
        """set_enabled(True) re-enables the clear button."""
        widget.set_path(SPOTIFY_URL)
        widget.set_enabled(False)
        widget.set_enabled(True)
        assert widget.clear_button.isEnabled()
