# icon_bar.py
# This file creates the static icon bar on the far left.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

# --- SVG Icon Data ---
MENU_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>"""
PLUS_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>"""
SETTINGS_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>"""
THEME_ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>"""

def create_icon_from_svg(svg_data, color):
    # Use string formatting to inject the color
    colored_svg = svg_data.format(color=color)
    renderer = QSvgRenderer(colored_svg.encode('utf-8'))
    pixmap = QPixmap(renderer.defaultSize())
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

class IconBar(QWidget):
    toggle_history_signal = Signal()
    open_settings_signal = Signal()
    new_chat_signal = Signal()
    toggle_theme_signal = Signal() # New signal for theme

    def __init__(self, initial_theme='dark'):
        super().__init__()
        self.setObjectName("iconBar")
        self.setFixedWidth(70)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 20)
        self.layout.setSpacing(20)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.menu_button = QPushButton()
        self.new_chat_button = QPushButton()
        self.settings_button = QPushButton()
        self.theme_button = QPushButton()

        self.update_icons(initial_theme) # Set initial icons

        for btn in [self.menu_button, self.new_chat_button, self.settings_button, self.theme_button]:
            btn.setObjectName("iconBarButton")
            btn.setIconSize(QSize(24, 24))
        
        self.menu_button.clicked.connect(self.toggle_history_signal.emit)
        self.new_chat_button.clicked.connect(self.new_chat_signal.emit)
        self.settings_button.clicked.connect(self.open_settings_signal.emit)
        self.theme_button.clicked.connect(self.toggle_theme_signal.emit)

        self.layout.addWidget(self.menu_button)
        self.layout.addWidget(self.new_chat_button)
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.theme_button)
        self.layout.addWidget(self.settings_button)

    def update_icons(self, theme):
        """Re-creates all icons with colors appropriate for the current theme."""
        icon_color = "#e8eaed" if theme == 'dark' else "#202124"
        self.menu_button.setIcon(create_icon_from_svg(MENU_ICON_SVG, icon_color))
        self.new_chat_button.setIcon(create_icon_from_svg(PLUS_ICON_SVG, icon_color))
        self.settings_button.setIcon(create_icon_from_svg(SETTINGS_ICON_SVG, icon_color))
        self.theme_button.setIcon(create_icon_from_svg(THEME_ICON_SVG, icon_color))
