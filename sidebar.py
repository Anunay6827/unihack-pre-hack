# sidebar.py
# This file creates the left-hand navigation sidebar.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QLabel
from PySide6.QtGui import QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve

# --- SVG Icon Data ---
PLUS_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e8eaed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
"""
SETTINGS_ICON_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e8eaed" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
"""

def create_icon_from_svg(svg_data):
    renderer = QSvgRenderer(svg_data.encode('utf-8'))
    pixmap = QPixmap(renderer.defaultSize())
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        
        self.expanded_width = 260
        self.collapsed_width = 80
        self.setFixedWidth(self.expanded_width)
        self.is_collapsed = False
        self.current_active_button = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 20)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- New Chat Button ---
        self.new_chat_button = QPushButton("  New chat")
        self.new_chat_button.setIcon(create_icon_from_svg(PLUS_ICON_SVG))
        self.new_chat_button.setObjectName("sidebarButton")
        self.new_chat_button.setIconSize(QSize(20, 20))
        
        # --- Recent Label ---
        self.recent_label = QLabel("Recent")
        self.recent_label.setObjectName("recentLabel")

        # --- History/Recent Items ---
        self.history_items_texts = [
            "Python GUI Library Comparison",
            "DuckDuckGo Image Scraper",
            "Future Land Use Map Search",
            "Creating a Movable Leaflet...",
        ]
        self.history_buttons = []

        # --- Bottom Settings Button ---
        self.settings_button = QPushButton("  Settings & help")
        self.settings_button.setIcon(create_icon_from_svg(SETTINGS_ICON_SVG))
        self.settings_button.setObjectName("sidebarButton")
        self.settings_button.setIconSize(QSize(20, 20))

        # --- Add widgets to layout ---
        self.layout.addWidget(self.new_chat_button)
        self.layout.addWidget(self.recent_label)

        for item_text in self.history_items_texts:
            btn = QPushButton(item_text)
            btn.setObjectName("historyButton")
            btn.clicked.connect(lambda checked=False, b=btn: self.select_chat(b))
            self.history_buttons.append(btn)
            self.layout.addWidget(btn)

        # Spacer to push settings to the bottom
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.settings_button)
        
        # --- Animation Setup ---
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(300)

        # Set the first chat as active by default
        if self.history_buttons:
            self.select_chat(self.history_buttons[0])

    def select_chat(self, button):
        """Sets the provided button as the active chat, updating styles."""
        if self.current_active_button:
            self.current_active_button.setObjectName("historyButton") # Reset old button
            self.style().polish(self.current_active_button) # Re-apply stylesheet

        button.setObjectName("activeHistoryButton") # Set new active button
        self.style().polish(button)
        self.current_active_button = button

    def toggle_sidebar(self):
        self.is_collapsed = not self.is_collapsed
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(self.collapsed_width if self.is_collapsed else self.expanded_width)
        self.update_widget_visibility()
        self.animation.start()

    def update_widget_visibility(self):
        is_fading_out = self.is_collapsed
        
        self.recent_label.setVisible(not is_fading_out)
        self.new_chat_button.setText("" if is_fading_out else "  New Chat")
        self.settings_button.setText("" if is_fading_out else "  Settings & help")
        
        for btn, text in zip(self.history_buttons, self.history_items_texts):
            btn.setText("" if is_fading_out else text)
