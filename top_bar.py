# top_bar.py
# This file creates the bar at the very top for window controls and branding.

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class TopBar(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setObjectName("topBar")
        self.setFixedHeight(60)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 5, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.setSpacing(10)

        # --- Branding Widgets ---
        self.title_label = QLabel("CmdCraft")
        self.title_label.setObjectName("titleLabel")

        self.version_button = QPushButton("1.5 Flash ▾")
        self.version_button.setObjectName("versionButton")

        # self.pro_button = QPushButton("PRO")
        # self.pro_button.setObjectName("proButton")

        # self.user_button = QPushButton("A")
        # self.user_button.setObjectName("userButton")

        # --- Window Control Buttons ---
        self.minimize_button = QPushButton("—")
        self.minimize_button.setObjectName("windowControlButton")
        self.minimize_button.clicked.connect(self.parent_window.showMinimized)

        self.maximize_button = QPushButton("□")
        self.maximize_button.setObjectName("windowControlButton")
        self.maximize_button.clicked.connect(self.toggle_maximize)

        self.close_button = QPushButton("✕")
        self.close_button.setObjectName("closeButton")
        self.close_button.clicked.connect(self.parent_window.close)

        # --- Layout ---
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.version_button)
        self.layout.addStretch()
        # self.layout.addWidget(self.pro_button)
        # self.layout.addWidget(self.user_button)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.minimize_button)
        self.layout.addWidget(self.maximize_button)
        self.layout.addWidget(self.close_button)

    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()
