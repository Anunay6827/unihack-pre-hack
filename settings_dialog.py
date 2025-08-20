# settings_dialog.py
# This file creates the dialog for entering the Google API Key.

import configparser
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.setObjectName("settingsDialog")

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)

        # --- API Key Input ---
        self.api_key_label = QLabel("Google AI API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your API key here")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        # --- Buttons ---
        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.save_button)

        # --- Layout ---
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_input)
        self.layout.addLayout(self.button_layout)

        # --- Connections ---
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.reject)

        self.load_settings()

    def load_settings(self):
        """Loads the API key from the config file."""
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            self.api_key_input.setText(config.get('API', 'key', fallback=''))

    def save_settings(self):
        """Saves the API key to the config file."""
        config = configparser.ConfigParser()
        config['API'] = {'key': self.api_key_input.text()}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        self.accept()
