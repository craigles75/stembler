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
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path

from ..models.user_settings import UserSettings


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
        self.setMinimumWidth(600)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Processing Settings Group
        processing_group = self._create_processing_settings_group()
        layout.addWidget(processing_group)

        # Spotify Credentials Group
        spotify_group = self._create_spotify_credentials_group()
        layout.addWidget(spotify_group)

        # Dialog buttons (Save/Cancel)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._on_save_clicked)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _create_processing_settings_group(self) -> QGroupBox:
        """Create processing settings group box."""
        group = QGroupBox("Processing Settings")
        form_layout = QFormLayout()
        form_layout.setSpacing(15)

        # Model selection dropdown
        self.model_combo = QComboBox()
        models = UserSettings.get_available_models()
        for model_id, description in models:
            self.model_combo.addItem(description, model_id)
        self.model_combo.setToolTip("Select the AI model to use for stem separation")
        form_layout.addRow("Model:", self.model_combo)

        # Model info label
        model_info = QLabel(
            "HTDemucs is recommended for most users (balanced quality and speed)."
        )
        model_info.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        model_info.setWordWrap(True)
        form_layout.addRow("", model_info)

        # Output directory picker
        output_layout = QHBoxLayout()
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Default: ~/Music/Stembler Output")
        self.output_dir_input.setToolTip("Directory where separated stems will be saved")
        output_layout.addWidget(self.output_dir_input, stretch=1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_output_dir)
        output_layout.addWidget(self.browse_button)

        form_layout.addRow("Output Directory:", output_layout)

        # Enhancement checkbox
        self.enhancement_checkbox = QCheckBox("Enable audio enhancement (recommended)")
        self.enhancement_checkbox.setChecked(True)
        self.enhancement_checkbox.setToolTip(
            "Applies post-processing to improve audio quality"
        )
        form_layout.addRow("Enhancement:", self.enhancement_checkbox)

        group.setLayout(form_layout)
        return group

    def _create_spotify_credentials_group(self) -> QGroupBox:
        """Create Spotify credentials group box."""
        group = QGroupBox("Spotify Integration")
        layout = QVBoxLayout()

        # Instructions label
        instructions = QLabel(
            "To download tracks from Spotify URLs, you need API credentials. "
            "Get them from the Spotify Developer Dashboard."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-size: 11px; margin-bottom: 10px;")
        layout.addWidget(instructions)

        # Form for credentials
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Client ID
        self.spotify_client_id_input = QLineEdit()
        self.spotify_client_id_input.setPlaceholderText("Enter your Spotify Client ID")
        self.spotify_client_id_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Client ID:", self.spotify_client_id_input)

        # Show/Hide Client ID button
        show_client_id_btn = QPushButton("Show")
        show_client_id_btn.setMaximumWidth(60)
        show_client_id_btn.setCheckable(True)
        show_client_id_btn.toggled.connect(
            lambda checked: self.spotify_client_id_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        form_layout.addRow("", show_client_id_btn)

        # Client Secret
        self.spotify_client_secret_input = QLineEdit()
        self.spotify_client_secret_input.setPlaceholderText(
            "Enter your Spotify Client Secret"
        )
        self.spotify_client_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Client Secret:", self.spotify_client_secret_input)

        # Show/Hide Client Secret button
        show_secret_btn = QPushButton("Show")
        show_secret_btn.setMaximumWidth(60)
        show_secret_btn.setCheckable(True)
        show_secret_btn.toggled.connect(
            lambda checked: self.spotify_client_secret_input.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        form_layout.addRow("", show_secret_btn)

        layout.addLayout(form_layout)

        # Test credentials button
        test_button_layout = QHBoxLayout()
        test_button_layout.addStretch()
        self.test_credentials_button = QPushButton("Test Credentials")
        self.test_credentials_button.clicked.connect(self._on_test_credentials)
        test_button_layout.addWidget(self.test_credentials_button)
        layout.addLayout(test_button_layout)

        # Link to Spotify Developer Dashboard
        link_layout = QHBoxLayout()
        link_label = QLabel(
            '<a href="https://developer.spotify.com/dashboard">Open Spotify Developer Dashboard</a>'
        )
        link_label.setOpenExternalLinks(True)
        link_label.setStyleSheet("margin-top: 10px;")
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
        """Test Spotify credentials."""
        client_id = self.spotify_client_id_input.text().strip()
        client_secret = self.spotify_client_secret_input.text().strip()

        if not client_id or not client_secret:
            QMessageBox.warning(
                self,
                "Missing Credentials",
                "Please enter both Client ID and Client Secret before testing.",
            )
            return

        # Basic validation (check they're not empty and look like valid IDs)
        if len(client_id) < 10 or len(client_secret) < 10:
            QMessageBox.warning(
                self,
                "Invalid Credentials",
                "Client ID and Client Secret seem too short. Please check your credentials.",
            )
            return

        # Show success message (actual API validation would require network call)
        QMessageBox.information(
            self,
            "Credentials Valid",
            "Credentials format looks valid!\n\n"
            "Note: Full validation will occur when you first download a Spotify track.",
        )

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
