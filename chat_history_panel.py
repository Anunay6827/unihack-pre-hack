# chat_history_panel.py
# This is the panel that slides out to show chat history.

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal

class ChatHistoryPanel(QWidget):
    chat_selected = Signal(int) # Signal to tell the main window which chat to show

    def __init__(self):
        super().__init__()
        self.setObjectName("historyPanel")

        self.expanded_width = 240
        self.is_collapsed = True
        self.setMaximumWidth(0)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 20)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.recent_label = QLabel("Recent")
        self.recent_label.setObjectName("recentLabel")
        self.layout.addWidget(self.recent_label)
        
        self.history_buttons = []
        self.current_active_button = None

        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.setDuration(300)

    def update_history(self, history_titles):
        """Clears and rebuilds the list of chat history buttons."""
        # Clear existing buttons
        for button in self.history_buttons:
            self.layout.removeWidget(button)
            button.deleteLater()
        self.history_buttons = []

        # Create new buttons
        for i, title in enumerate(history_titles):
            btn = QPushButton(title)
            btn.setObjectName("historyButton")
            # Use a lambda to capture the correct index 'i'
            btn.clicked.connect(lambda checked=False, index=i: self.chat_selected.emit(index))
            self.history_buttons.append(btn)
            self.layout.addWidget(btn)

    def select_chat_by_index(self, index):
        """Highlights the button at the given index."""
        if self.current_active_button:
            self.current_active_button.setObjectName("historyButton")
            self.style().polish(self.current_active_button)
        
        if 0 <= index < len(self.history_buttons):
            button = self.history_buttons[index]
            button.setObjectName("activeHistoryButton")
            self.style().polish(button)
            self.current_active_button = button

    def toggle_panel(self):
        self.is_collapsed = not self.is_collapsed
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(0 if self.is_collapsed else self.expanded_width)
        self.animation.start()
