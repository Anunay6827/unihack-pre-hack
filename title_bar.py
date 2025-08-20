# title_bar.py
# This file creates the custom title bar below the window controls.

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QSize, QPropertyAnimation, QEasingCurve, QMargins

class TitleBar(QWidget):
    toggle_sidebar_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("titleBar")
        self.setFixedHeight(60)
        self.is_collapsed = False

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 20, 0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.layout.setSpacing(10)

        # --- Widgets ---
        self.menu_button = QPushButton("☰")
        self.menu_button.setObjectName("menuButton")
        self.menu_button.setFixedSize(QSize(40, 40))
        self.menu_button.clicked.connect(self.toggle_sidebar_signal.emit)

        self.title_label = QLabel("CmdCraft")
        self.title_label.setObjectName("titleLabel")

        self.version_button = QPushButton("1.5 Flash ▾")
        self.version_button.setObjectName("versionButton")

        # self.pro_button = QPushButton("PRO")
        # self.pro_button.setObjectName("proButton")

        # self.user_button = QPushButton("A")
        # self.user_button.setObjectName("userButton")

        # --- Layout ---
        self.layout.addWidget(self.menu_button)
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.version_button)
        self.layout.addStretch()
        # self.layout.addWidget(self.pro_button)
        # self.layout.addWidget(self.user_button)
        
        # --- Animation for menu button margin ---
        self.animation = QPropertyAnimation(self, b"layoutMargins")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(300)

    # This is a custom property for the animation to target
    def getLayoutMargins(self):
        return self.layout.contentsMargins()

    def setLayoutMargins(self, margins):
        self.layout.setContentsMargins(margins)

    layoutMargins = property(getLayoutMargins, setLayoutMargins)

    def animate_menu_button(self):
        """Animates the left margin to align with collapsed sidebar."""
        self.is_collapsed = not self.is_collapsed
        start_margin = self.layout.contentsMargins()
        
        if self.is_collapsed:
            end_margin = QMargins(-40, start_margin.top(), start_margin.right(), start_margin.bottom())
        else:
            end_margin = QMargins(10, start_margin.top(), start_margin.right(), start_margin.bottom())
            
        self.animation.setStartValue(start_margin)
        self.animation.setEndValue(end_margin)
        self.animation.start()
