"""Settings panel dialog for configuring application preferences."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QMessageBox,
    QDialogButtonBox,
    QStyle,
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path

from ..models.user_settings import UserSettings
from ..utils.theme import Theme


class SettingsPanel(QDialog):
    """Dialog for editing application settings."""

    # Signal emitted when settings are saved
    settings_changed = pyqtSignal(UserSettings)

    def __init__(self, current_settings: UserSettings, parent=None):
        super().__init__(parent)
        self._current_settings = current_settings
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Stembler Settings")
        self.setMinimumWidth(650)
        self.setModal(True)

        # Apply dialog background styling
        self.setStyleSheet(
            f"""
            QDialog {{
                background-color: {Theme.BACKGROUND_SECONDARY};
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_LG)

        # Processing Settings Group
        processing_group = self._create_processing_settings_group()
        layout.addWidget(processing_group)

        # Spotify Credentials Group
        spotify_group = self._create_spotify_credentials_group()
        layout.addWidget(spotify_group)

        # Dialog buttons (Save/Cancel)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_save_clicked)
        button_box.rejected.connect(self.reject)

        # Style Save and Cancel buttons explicitly
        save_btn = button_box.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(
            Theme.button_style(
                Theme.PRIMARY, Theme.PRIMARY_HOVER, Theme.PRIMARY_PRESSED
            )
        )

        cancel_btn = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER_MEDIUM};
                border-radius: {Theme.RADIUS_MD}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                padding: 0 16px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BACKGROUND_HOVER};
                border-color: {Theme.BORDER_DARK};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )

        layout.addWidget(button_box)

    def _create_processing_settings_group(self) -> QGroupBox:
        """Create processing settings group box."""
        group = QGroupBox("Processing Settings")
        # Card-style container with white background
        group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: 12px;
                padding: {Theme.SPACING_LG}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                margin-top: {Theme.SPACING_MD}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Theme.SPACING_MD}px;
                padding: 0 {Theme.SPACING_SM}px;
                color: {Theme.TEXT_PRIMARY};
                background-color: {Theme.BACKGROUND_PRIMARY};
            }}
            """
        )

        form_layout = QFormLayout()
        form_layout.setSpacing(Theme.SPACING_MD)
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # Model selection dropdown with custom styling
        self.model_combo = QComboBox()
        models = UserSettings.get_available_models()
        for model_id, description in models:
            self.model_combo.addItem(description, model_id)
        self.model_combo.setToolTip("Select the AI model to use for stem separation")
        self.model_combo.setStyleSheet(Theme.input_style())

        model_label = QLabel("Model:")
        model_label.setStyleSheet(
            f"QLabel {{ color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_SM}px; }}"
        )
        form_layout.addRow(model_label, self.model_combo)

        # Model info label
        model_info = QLabel(
            "HTDemucs is recommended for most users (balanced quality and speed)."
        )
        model_info.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_TERTIARY};
                font-size: {Theme.FONT_SIZE_XS}px;
                font-style: italic;
            }}
            """
        )
        model_info.setWordWrap(True)
        form_layout.addRow("", model_info)

        # Output directory picker
        output_layout = QHBoxLayout()
        output_layout.setSpacing(Theme.SPACING_SM)

        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Default: ~/Music/Stembler Output")
        self.output_dir_input.setToolTip(
            "Directory where separated stems will be saved"
        )
        self.output_dir_input.setStyleSheet(Theme.input_style())
        output_layout.addWidget(self.output_dir_input, stretch=1)

        # Browse button with folder icon
        self.browse_button = QPushButton("  Browse...")
        folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        self.browse_button.setIcon(folder_icon)
        self.browse_button.clicked.connect(self._on_browse_output_dir)
        self.browse_button.setStyleSheet(
            Theme.button_style(
                Theme.SECONDARY,
                Theme.SECONDARY_HOVER,
                Theme.SECONDARY_PRESSED,
                height=Theme.INPUT_HEIGHT,
            )
        )
        output_layout.addWidget(self.browse_button)

        output_dir_label = QLabel("Output Directory:")
        output_dir_label.setStyleSheet(
            f"QLabel {{ color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_SM}px; }}"
        )
        form_layout.addRow(output_dir_label, output_layout)

        # Enhancement checkbox
        self.enhancement_checkbox = QCheckBox("Enable audio enhancement (recommended)")
        self.enhancement_checkbox.setChecked(True)
        self.enhancement_checkbox.setToolTip(
            "Applies post-processing to improve audio quality"
        )
        self.enhancement_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: {Theme.FONT_SIZE_SM}px;
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        enhancement_label = QLabel("Enhancement:")
        enhancement_label.setStyleSheet(
            f"QLabel {{ color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_SM}px; }}"
        )
        form_layout.addRow(enhancement_label, self.enhancement_checkbox)

        group.setLayout(form_layout)
        return group

    def _create_spotify_credentials_group(self) -> QGroupBox:
        """Create Spotify credentials group box."""
        group = QGroupBox("Spotify Integration")
        # Card-style container with white background
        group.setStyleSheet(
            f"""
            QGroupBox {{
                background-color: {Theme.BACKGROUND_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: 12px;
                padding: {Theme.SPACING_LG}px;
                font-size: {Theme.FONT_SIZE_MD}px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                margin-top: {Theme.SPACING_MD}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {Theme.SPACING_MD}px;
                padding: 0 {Theme.SPACING_SM}px;
                color: {Theme.TEXT_PRIMARY};
                background-color: {Theme.BACKGROUND_PRIMARY};
            }}
            """
        )

        layout = QVBoxLayout()
        layout.setSpacing(Theme.SPACING_MD)

        # Instructions label
        instructions = QLabel(
            "To download tracks from Spotify URLs, you need API credentials. "
            "Get them from the Spotify Developer Dashboard."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {Theme.FONT_SIZE_XS}px;
                margin-bottom: {Theme.SPACING_SM}px;
            }}
            """
        )
        layout.addWidget(instructions)

        # Form for credentials
        form_layout = QFormLayout()
        form_layout.setSpacing(Theme.SPACING_SM)
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # Client ID row: label + (input + ghost Show button)
        client_id_label = QLabel("Client ID:")
        client_id_label.setStyleSheet(
            f"QLabel {{ color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_SM}px; }}"
        )

        client_id_row = QHBoxLayout()
        client_id_row.setSpacing(Theme.SPACING_SM)

        self.spotify_client_id_input = QLineEdit()
        self.spotify_client_id_input.setPlaceholderText("Enter your Spotify Client ID")
        self.spotify_client_id_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.spotify_client_id_input.setStyleSheet(Theme.input_style())
        client_id_row.addWidget(self.spotify_client_id_input, stretch=1)

        show_client_id_btn = QPushButton("Show")
        show_client_id_btn.setFixedWidth(60)
        show_client_id_btn.setCheckable(True)
        show_client_id_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER_MEDIUM};
                border-radius: {Theme.RADIUS_SM}px;
                font-size: {Theme.FONT_SIZE_SM}px;
                padding: 4px 8px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BACKGROUND_HOVER};
                border-color: {Theme.BORDER_DARK};
            }}
            QPushButton:checked {{
                background-color: {Theme.BACKGROUND_TERTIARY};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        show_client_id_btn.toggled.connect(
            lambda checked: (
                self.spotify_client_id_input.setEchoMode(
                    QLineEdit.EchoMode.Normal
                    if checked
                    else QLineEdit.EchoMode.Password
                ),
                show_client_id_btn.setText("Hide" if checked else "Show"),
            )
        )
        client_id_row.addWidget(show_client_id_btn)

        form_layout.addRow(client_id_label, client_id_row)

        # Client Secret row: label + (input + ghost Show button)
        client_secret_label = QLabel("Client Secret:")
        client_secret_label.setStyleSheet(
            f"QLabel {{ color: {Theme.TEXT_PRIMARY}; font-size: {Theme.FONT_SIZE_SM}px; }}"
        )

        client_secret_row = QHBoxLayout()
        client_secret_row.setSpacing(Theme.SPACING_SM)

        self.spotify_client_secret_input = QLineEdit()
        self.spotify_client_secret_input.setPlaceholderText(
            "Enter your Spotify Client Secret"
        )
        self.spotify_client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.spotify_client_secret_input.setStyleSheet(Theme.input_style())
        client_secret_row.addWidget(self.spotify_client_secret_input, stretch=1)

        show_secret_btn = QPushButton("Show")
        show_secret_btn.setFixedWidth(60)
        show_secret_btn.setCheckable(True)
        show_secret_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_SECONDARY};
                border: 1px solid {Theme.BORDER_MEDIUM};
                border-radius: {Theme.RADIUS_SM}px;
                font-size: {Theme.FONT_SIZE_SM}px;
                padding: 4px 8px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BACKGROUND_HOVER};
                border-color: {Theme.BORDER_DARK};
            }}
            QPushButton:checked {{
                background-color: {Theme.BACKGROUND_TERTIARY};
                color: {Theme.TEXT_PRIMARY};
            }}
            """
        )
        show_secret_btn.toggled.connect(
            lambda checked: (
                self.spotify_client_secret_input.setEchoMode(
                    QLineEdit.EchoMode.Normal
                    if checked
                    else QLineEdit.EchoMode.Password
                ),
                show_secret_btn.setText("Hide" if checked else "Show"),
            )
        )
        client_secret_row.addWidget(show_secret_btn)

        form_layout.addRow(client_secret_label, client_secret_row)

        layout.addLayout(form_layout)

        # Test credentials button with secondary styling
        test_button_layout = QHBoxLayout()
        test_button_layout.addStretch()
        self.test_credentials_button = QPushButton("  Test Credentials")
        # Add a checkmark icon
        check_icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogApplyButton
        )
        self.test_credentials_button.setIcon(check_icon)
        self.test_credentials_button.clicked.connect(self._on_test_credentials)
        self.test_credentials_button.setStyleSheet(
            Theme.button_style(
                Theme.SECONDARY,
                Theme.SECONDARY_HOVER,
                Theme.SECONDARY_PRESSED,
                height=40,
            )
        )
        test_button_layout.addWidget(self.test_credentials_button)
        layout.addLayout(test_button_layout)

        # Inline credential validation status label (hidden until first test)
        self.credentials_status_label = QLabel("")
        self.credentials_status_label.setWordWrap(True)
        self.credentials_status_label.hide()
        layout.addWidget(self.credentials_status_label)

        # Link to Spotify Developer Dashboard
        link_layout = QHBoxLayout()
        link_label = QLabel(
            '<a href="https://developer.spotify.com/dashboard" style="color: '
            + Theme.PRIMARY
            + ';">🔗 Open Spotify Developer Dashboard</a>'
        )
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: {Theme.FONT_SIZE_SM}px;
                margin-top: {Theme.SPACING_SM}px;
            }}
            """
        )
        link_layout.addWidget(link_label)
        link_layout.addStretch()
        layout.addLayout(link_layout)

        group.setLayout(layout)
        return group

    def _load_current_settings(self) -> None:
        """Load current settings into the UI."""
        # Set model
        model_index = self.model_combo.findData(self._current_settings.model_name)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)

        # Set output directory
        if self._current_settings.output_directory:
            self.output_dir_input.setText(self._current_settings.output_directory)

        # Set enhancement
        self.enhancement_checkbox.setChecked(self._current_settings.enable_enhancement)

        # Set Spotify credentials
        self.spotify_client_id_input.setText(self._current_settings.spotify_client_id)
        self.spotify_client_secret_input.setText(
            self._current_settings.spotify_client_secret
        )

    def _on_browse_output_dir(self) -> None:
        """Handle browse button click for output directory."""
        current_dir = self.output_dir_input.text() or str(Path.home())
        selected_dir = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", current_dir
        )
        if selected_dir:
            self.output_dir_input.setText(selected_dir)

    def _on_test_credentials(self) -> None:
        """Test Spotify credentials using inline status feedback."""
        client_id = self.spotify_client_id_input.text().strip()
        client_secret = self.spotify_client_secret_input.text().strip()

        if not client_id or not client_secret:
            self._show_credentials_error(
                "Please enter both Client ID and Client Secret before testing."
            )
            return

        # Basic validation (check they're not empty and look like valid IDs)
        if len(client_id) < 10 or len(client_secret) < 10:
            self._show_credentials_error(
                "Client ID and Client Secret seem too short. "
                "Please check your credentials."
            )
            return

        # Show success message (actual API validation would require network call)
        self._show_credentials_success(
            "Credentials format looks valid! "
            "Full validation will occur when you first download a Spotify track."
        )

    def _show_credentials_error(self, message: str) -> None:
        """Display an inline error message below the Test Credentials button."""
        self.credentials_status_label.setText(f"\u2717 {message}")
        self.credentials_status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.ERROR};
                background-color: {Theme.ERROR_LIGHT};
                font-size: {Theme.FONT_SIZE_SM}px;
                padding: 8px 12px;
                border-radius: {Theme.RADIUS_SM}px;
            }}
            """
        )
        self.credentials_status_label.show()

    def _show_credentials_success(self, message: str) -> None:
        """Display an inline success message below the Test Credentials button."""
        self.credentials_status_label.setText(f"\u2713 {message}")
        self.credentials_status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {Theme.SUCCESS};
                background-color: {Theme.SUCCESS_LIGHT};
                font-size: {Theme.FONT_SIZE_SM}px;
                padding: 8px 12px;
                border-radius: {Theme.RADIUS_SM}px;
            }}
            """
        )
        self.credentials_status_label.show()

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        # Get values from UI
        model_id = self.model_combo.currentData()
        output_dir = self.output_dir_input.text().strip()
        enhancement = self.enhancement_checkbox.isChecked()
        spotify_id = self.spotify_client_id_input.text().strip()
        spotify_secret = self.spotify_client_secret_input.text().strip()

        # Validate output directory if provided
        if output_dir:
            output_path = Path(output_dir)
            if not output_path.is_absolute():
                QMessageBox.warning(
                    self,
                    "Invalid Directory",
                    "Please provide an absolute path for the output directory.",
                )
                return

        # Create updated settings
        updated_settings = UserSettings(
            model_name=model_id,
            enable_enhancement=enhancement,
            output_directory=output_dir,
            device=self._current_settings.device,  # Preserve device setting
            spotify_client_id=spotify_id,
            spotify_client_secret=spotify_secret,
        )

        # Emit signal and close
        self.settings_changed.emit(updated_settings)
        self.accept()

    def get_settings(self) -> UserSettings:
        """Get the current settings from the dialog.

        Returns:
            UserSettings object with current values
        """
        model_id = self.model_combo.currentData()
        output_dir = self.output_dir_input.text().strip()
        enhancement = self.enhancement_checkbox.isChecked()
        spotify_id = self.spotify_client_id_input.text().strip()
        spotify_secret = self.spotify_client_secret_input.text().strip()

        return UserSettings(
            model_name=model_id,
            enable_enhancement=enhancement,
            output_directory=output_dir,
            device=self._current_settings.device,
            spotify_client_id=spotify_id,
            spotify_client_secret=spotify_secret,
        )
