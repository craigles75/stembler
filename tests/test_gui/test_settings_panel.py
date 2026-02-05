"""Tests for SettingsPanel UX fixes.

All tests instantiate a real SettingsPanel against the offscreen Qt platform
(see conftest.py).  No widget internals are mocked; assertions target the
concrete layout structure and stylesheet content produced by each fix.

Note on visibility assertions
------------------------------
Same convention as test_file_input.py: use isHidden() rather than isVisible()
because the offscreen platform never fully maps the widget hierarchy.
"""

import pytest
from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QHBoxLayout

from music_stem_separator.gui.widgets.settings_panel import SettingsPanel
from music_stem_separator.gui.models.user_settings import UserSettings
from music_stem_separator.gui.utils.theme import Theme


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def settings():
    """Default UserSettings instance."""
    return UserSettings.get_default()


@pytest.fixture()
def panel(qt_app, settings):
    """Fresh SettingsPanel, destroyed after each test."""
    p = SettingsPanel(settings)
    yield p
    p.deleteLater()
    qt_app.processEvents()


@pytest.fixture()
def panel_with_creds(qt_app):
    """SettingsPanel pre-loaded with plausible (>=10 char) credentials."""
    s = UserSettings(
        spotify_client_id="abcdef1234567890",
        spotify_client_secret="secret1234567890",
    )
    p = SettingsPanel(s)
    yield p
    p.deleteLater()
    qt_app.processEvents()


# ---------------------------------------------------------------------------
# 1. QGroupBox title visibility -- color and background-color present
# ---------------------------------------------------------------------------


class TestGroupBoxTitleStylesheet:
    """Both group boxes must have explicit color/background on their ::title."""

    def _get_groupbox_stylesheet(self, panel: SettingsPanel, title: str) -> str:
        """Walk the top-level layout to find a QGroupBox by title text."""
        layout = panel.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget and widget.title() == title:
                return widget.styleSheet()
        pytest.fail(f"QGroupBox titled '{title}' not found")

    def test_processing_settings_title_has_color(self, panel):
        ss = self._get_groupbox_stylesheet(panel, "Processing Settings")
        assert Theme.TEXT_PRIMARY in ss
        # Specifically inside the ::title block
        assert "QGroupBox::title" in ss
        title_block = ss.split("QGroupBox::title")[1]
        assert f"color: {Theme.TEXT_PRIMARY}" in title_block

    def test_processing_settings_title_has_background(self, panel):
        ss = self._get_groupbox_stylesheet(panel, "Processing Settings")
        title_block = ss.split("QGroupBox::title")[1]
        assert f"background-color: {Theme.BACKGROUND_PRIMARY}" in title_block

    def test_spotify_integration_title_has_color(self, panel):
        ss = self._get_groupbox_stylesheet(panel, "Spotify Integration")
        title_block = ss.split("QGroupBox::title")[1]
        assert f"color: {Theme.TEXT_PRIMARY}" in title_block

    def test_spotify_integration_title_has_background(self, panel):
        ss = self._get_groupbox_stylesheet(panel, "Spotify Integration")
        title_block = ss.split("QGroupBox::title")[1]
        assert f"background-color: {Theme.BACKGROUND_PRIMARY}" in title_block


# ---------------------------------------------------------------------------
# 2. Form labels are explicit QLabel widgets with styled color
# ---------------------------------------------------------------------------


class TestFormLabelVisibility:
    """Form row labels must be QLabel instances with TEXT_PRIMARY colour."""

    def _find_labels_by_text(self, panel: SettingsPanel, text: str) -> list[QLabel]:
        """Recursively find all QLabel children whose text matches."""
        return [w for w in panel.findChildren(QLabel) if w.text() == text]

    def _assert_label_styled(self, label: QLabel) -> None:
        ss = label.styleSheet()
        assert f"color: {Theme.TEXT_PRIMARY}" in ss, (
            f"Label '{label.text()}' stylesheet missing TEXT_PRIMARY color. "
            f"Got: {ss}"
        )

    def test_model_label_is_styled_qlabel(self, panel):
        labels = self._find_labels_by_text(panel, "Model:")
        assert len(labels) == 1, "Expected exactly one 'Model:' QLabel"
        self._assert_label_styled(labels[0])

    def test_output_directory_label_is_styled_qlabel(self, panel):
        labels = self._find_labels_by_text(panel, "Output Directory:")
        assert len(labels) == 1
        self._assert_label_styled(labels[0])

    def test_enhancement_label_is_styled_qlabel(self, panel):
        labels = self._find_labels_by_text(panel, "Enhancement:")
        assert len(labels) == 1
        self._assert_label_styled(labels[0])

    def test_client_id_label_is_styled_qlabel(self, panel):
        labels = self._find_labels_by_text(panel, "Client ID:")
        assert len(labels) == 1
        self._assert_label_styled(labels[0])

    def test_client_secret_label_is_styled_qlabel(self, panel):
        labels = self._find_labels_by_text(panel, "Client Secret:")
        assert len(labels) == 1
        self._assert_label_styled(labels[0])


# ---------------------------------------------------------------------------
# 3. Show buttons are inline (same QHBoxLayout) as credential fields
# ---------------------------------------------------------------------------


class TestShowButtonsInline:
    """Each credential field and its Show button must share a QHBoxLayout row."""

    def _find_show_buttons(self, panel: SettingsPanel) -> list[QPushButton]:
        return [
            w
            for w in panel.findChildren(QPushButton)
            if w.text() in ("Show", "Hide") and w.isCheckable()
        ]

    def _get_parent_layout(self, widget) -> object:
        """Return the layout that directly contains widget, or None."""
        parent = widget.parent()
        if parent is None:
            return None
        layout = parent.layout()
        if layout is None:
            return None
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget() is widget:
                return layout
            # Check sub-layouts
            sub = item.layout()
            if sub:
                for j in range(sub.count()):
                    sub_item = sub.itemAt(j)
                    if sub_item.widget() is widget:
                        return sub
                    # One more level for QFormLayout -> QHBoxLayout nesting
                    sub2 = sub_item.layout()
                    if sub2:
                        for k in range(sub2.count()):
                            if sub2.itemAt(k).widget() is widget:
                                return sub2
        return None

    def test_two_show_buttons_exist(self, panel):
        btns = self._find_show_buttons(panel)
        assert len(btns) == 2, f"Expected 2 Show/Hide buttons, found {len(btns)}"

    def test_client_id_show_button_shares_layout_with_input(self, panel):
        """The Client ID input and its Show button must be in the same layout."""
        input_widget = panel.spotify_client_id_input
        # Find the Show button that shares a parent layout with this input
        btns = self._find_show_buttons(panel)
        input_layout = self._get_parent_layout(input_widget)
        assert (
            input_layout is not None
        ), "Could not find layout containing client_id input"
        assert isinstance(
            input_layout, QHBoxLayout
        ), f"Expected QHBoxLayout for credential row, got {type(input_layout)}"

        # At least one Show button must be in the same layout
        found = False
        for btn in btns:
            btn_layout = self._get_parent_layout(btn)
            if btn_layout is input_layout:
                found = True
                break
        assert found, "No Show button shares a layout with the Client ID input"

    def test_client_secret_show_button_shares_layout_with_input(self, panel):
        input_widget = panel.spotify_client_secret_input
        btns = self._find_show_buttons(panel)
        input_layout = self._get_parent_layout(input_widget)
        assert input_layout is not None
        assert isinstance(input_layout, QHBoxLayout)

        found = False
        for btn in btns:
            btn_layout = self._get_parent_layout(btn)
            if btn_layout is input_layout:
                found = True
                break
        assert found, "No Show button shares a layout with the Client Secret input"


# ---------------------------------------------------------------------------
# 4. Show buttons: ghost stylesheet + Show/Hide text toggle
# ---------------------------------------------------------------------------


class TestShowButtonGhostStyle:
    """Show buttons must use transparent/ghost style and toggle their label."""

    def _find_show_buttons(self, panel: SettingsPanel) -> list[QPushButton]:
        return [
            w
            for w in panel.findChildren(QPushButton)
            if w.text() in ("Show", "Hide") and w.isCheckable()
        ]

    def test_show_buttons_have_transparent_background(self, panel):
        for btn in self._find_show_buttons(panel):
            assert (
                "background-color: transparent" in btn.styleSheet()
            ), f"Show button stylesheet lacks transparent background: {btn.styleSheet()}"

    def test_show_buttons_have_border(self, panel):
        for btn in self._find_show_buttons(panel):
            assert f"border: 1px solid {Theme.BORDER_MEDIUM}" in btn.styleSheet()

    def test_show_buttons_have_checked_state_style(self, panel):
        for btn in self._find_show_buttons(panel):
            assert "QPushButton:checked" in btn.styleSheet()

    def test_client_id_show_toggles_echo_mode(self, panel):
        """Clicking the Show button for Client ID switches to Normal echo mode."""
        panel.spotify_client_id_input.setText("test_value")
        assert panel.spotify_client_id_input.echoMode() == QLineEdit.EchoMode.Password

        # Find the Show button that is in the same layout as the client_id input
        btns = self._find_show_buttons(panel)
        # Toggle each; the one that changes client_id's echo mode is ours
        for btn in btns:
            btn.setChecked(True)
            if panel.spotify_client_id_input.echoMode() == QLineEdit.EchoMode.Normal:
                assert btn.text() == "Hide"
                # Toggle back
                btn.setChecked(False)
                assert (
                    panel.spotify_client_id_input.echoMode()
                    == QLineEdit.EchoMode.Password
                )
                assert btn.text() == "Show"
                return
            btn.setChecked(False)  # reset if it wasn't the right one
        pytest.fail("No Show button controls Client ID echo mode")

    def test_client_secret_show_toggles_echo_mode(self, panel):
        panel.spotify_client_secret_input.setText("test_secret")
        assert (
            panel.spotify_client_secret_input.echoMode() == QLineEdit.EchoMode.Password
        )

        btns = self._find_show_buttons(panel)
        for btn in btns:
            btn.setChecked(True)
            if (
                panel.spotify_client_secret_input.echoMode()
                == QLineEdit.EchoMode.Normal
            ):
                assert btn.text() == "Hide"
                btn.setChecked(False)
                assert (
                    panel.spotify_client_secret_input.echoMode()
                    == QLineEdit.EchoMode.Password
                )
                assert btn.text() == "Show"
                return
            btn.setChecked(False)
        pytest.fail("No Show button controls Client Secret echo mode")


# ---------------------------------------------------------------------------
# 5. Save and Cancel buttons have explicit stylesheets
# ---------------------------------------------------------------------------


class TestDialogButtonStyles:
    """Save and Cancel must have non-empty, distinct stylesheets."""

    def _get_button_box(self, panel: SettingsPanel):
        from PyQt6.QtWidgets import QDialogButtonBox

        boxes = panel.findChildren(QDialogButtonBox)
        assert len(boxes) == 1, "Expected exactly one QDialogButtonBox"
        return boxes[0]

    def test_save_button_has_primary_style(self, panel):
        from PyQt6.QtWidgets import QDialogButtonBox

        bb = self._get_button_box(panel)
        save = bb.button(QDialogButtonBox.StandardButton.Save)
        assert save is not None
        ss = save.styleSheet()
        assert (
            Theme.PRIMARY in ss
        ), f"Save button stylesheet missing PRIMARY color. Got: {ss}"

    def test_cancel_button_has_ghost_style(self, panel):
        from PyQt6.QtWidgets import QDialogButtonBox

        bb = self._get_button_box(panel)
        cancel = bb.button(QDialogButtonBox.StandardButton.Cancel)
        assert cancel is not None
        ss = cancel.styleSheet()
        assert "background-color: transparent" in ss
        assert f"border: 1px solid {Theme.BORDER_MEDIUM}" in ss
        assert f"color: {Theme.TEXT_SECONDARY}" in ss

    def test_save_and_cancel_stylesheets_differ(self, panel):
        from PyQt6.QtWidgets import QDialogButtonBox

        bb = self._get_button_box(panel)
        save_ss = bb.button(QDialogButtonBox.StandardButton.Save).styleSheet()
        cancel_ss = bb.button(QDialogButtonBox.StandardButton.Cancel).styleSheet()
        assert save_ss != cancel_ss


# ---------------------------------------------------------------------------
# 6. Credential validation: inline status label, no QMessageBox
# ---------------------------------------------------------------------------


class TestCredentialValidationInline:
    """_on_test_credentials must update the inline status label, not show a dialog."""

    def test_status_label_hidden_on_construction(self, panel):
        assert panel.credentials_status_label.isHidden()

    def test_empty_credentials_show_error_label(self, panel):
        # Both fields empty by default
        panel.spotify_client_id_input.setText("")
        panel.spotify_client_secret_input.setText("")
        panel._on_test_credentials()

        assert not panel.credentials_status_label.isHidden()
        assert "\u2717" in panel.credentials_status_label.text()
        assert Theme.ERROR in panel.credentials_status_label.styleSheet()

    def test_missing_secret_shows_error_label(self, panel):
        panel.spotify_client_id_input.setText("valid_id_1234567890")
        panel.spotify_client_secret_input.setText("")
        panel._on_test_credentials()

        assert not panel.credentials_status_label.isHidden()
        assert "\u2717" in panel.credentials_status_label.text()

    def test_short_credentials_show_error_label(self, panel):
        panel.spotify_client_id_input.setText("short")
        panel.spotify_client_secret_input.setText("also")
        panel._on_test_credentials()

        assert not panel.credentials_status_label.isHidden()
        assert "\u2717" in panel.credentials_status_label.text()
        assert "too short" in panel.credentials_status_label.text()
        assert Theme.ERROR in panel.credentials_status_label.styleSheet()

    def test_valid_credentials_show_success_label(self, panel_with_creds):
        panel_with_creds._on_test_credentials()

        label = panel_with_creds.credentials_status_label
        assert not label.isHidden()
        assert "\u2713" in label.text()
        assert Theme.SUCCESS in label.styleSheet()
        assert Theme.SUCCESS_LIGHT in label.styleSheet()

    def test_error_label_replaced_by_success_on_fix(self, panel):
        """Error shown first, then valid input replaces it with success."""
        # Trigger error
        panel.spotify_client_id_input.setText("")
        panel.spotify_client_secret_input.setText("")
        panel._on_test_credentials()
        assert "\u2717" in panel.credentials_status_label.text()

        # Fix inputs and re-test
        panel.spotify_client_id_input.setText("valid_client_id_1234")
        panel.spotify_client_secret_input.setText("valid_secret_1234567")
        panel._on_test_credentials()
        assert "\u2713" in panel.credentials_status_label.text()
        assert Theme.SUCCESS in panel.credentials_status_label.styleSheet()

    def test_success_label_replaced_by_error_on_clear(self, panel_with_creds):
        """Success shown first, then cleared inputs replace it with error."""
        panel_with_creds._on_test_credentials()
        assert "\u2713" in panel_with_creds.credentials_status_label.text()

        panel_with_creds.spotify_client_id_input.setText("")
        panel_with_creds._on_test_credentials()
        assert "\u2717" in panel_with_creds.credentials_status_label.text()
        assert Theme.ERROR in panel_with_creds.credentials_status_label.styleSheet()
