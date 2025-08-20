# main_window.py
# This file defines the main window, which now manages multiple chat sessions and themes.

import configparser
from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedLayout
from PySide6.QtGui import QMouseEvent

from icon_bar import IconBar
from chat_history_panel import ChatHistoryPanel
from chat_area import ChatArea
from settings_dialog import SettingsDialog
import styles # Import the styles module

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Command Prompt")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.chats = []
        self.current_chat_index = -1
        self.current_theme = self.load_theme_preference()

        self.icon_bar = IconBar(self.current_theme)
        self.history_panel = ChatHistoryPanel()
        self.chat_area_container = QStackedLayout()

        self.layout.addWidget(self.icon_bar)
        self.layout.addWidget(self.history_panel)
        self.layout.addLayout(self.chat_area_container, 1)

        # --- Connect Signals ---
        self.icon_bar.toggle_history_signal.connect(self.history_panel.toggle_panel)
        self.icon_bar.open_settings_signal.connect(self.open_settings)
        self.icon_bar.new_chat_signal.connect(self.create_new_chat)
        self.icon_bar.toggle_theme_signal.connect(self.toggle_theme)
        self.history_panel.chat_selected.connect(self.switch_chat)

        self.create_new_chat()
        self.apply_theme() # Apply theme on startup
        self._old_pos = None

    def load_theme_preference(self):
        config = configparser.ConfigParser()
        if config.read('config.ini'):
            return config.get('Theme', 'mode', fallback='dark')
        return 'dark'

    def save_theme_preference(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        if not config.has_section('Theme'):
            config.add_section('Theme')
        config.set('Theme', 'mode', self.current_theme)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    def apply_theme(self):
        """Applies the current theme to the application and its components."""
        stylesheet = styles.get_stylesheet(self.current_theme)
        QApplication.instance().setStyleSheet(stylesheet)
        self.icon_bar.update_icons(self.current_theme)
        
        # --- FIX --- Force style polish on all necessary widgets
        self.style().polish(self)
        self.style().polish(self.icon_bar)
        self.style().polish(self.history_panel)
        
        # This loop ensures every chat area and its internal pages are updated
        for i in range(self.chat_area_container.count()):
            chat_widget = self.chat_area_container.widget(i)
            self.style().polish(chat_widget)
            self.style().polish(chat_widget.initial_page)
            self.style().polish(chat_widget.chat_page)


    def toggle_theme(self):
        """Switches the theme and applies the changes."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self.save_theme_preference()
        self.apply_theme()

    def create_new_chat(self):
        new_chat_area = ChatArea(parent_window=self)
        new_chat_index = self.chat_area_container.addWidget(new_chat_area)
        new_chat_area.first_message_sent.connect(
            lambda title, index=new_chat_index: self.update_chat_title(index, title)
        )
        self.chats.append({"title": f"New Chat {len(self.chats) + 1}", "widget": new_chat_area})
        self.switch_chat(0); self.update_history_panel()

    def switch_chat(self, reversed_index):
        correct_index = len(self.chats) - 1 - reversed_index
        if 0 <= correct_index < len(self.chats):
            self.chat_area_container.setCurrentIndex(correct_index)
            self.current_chat_index = correct_index
            self.history_panel.select_chat_by_index(reversed_index)

    def update_chat_title(self, index, title):
        if 0 <= index < len(self.chats):
            short_title = (title[:30] + '...') if len(title) > 30 else title
            self.chats[index]['title'] = short_title
            self.update_history_panel()

    def update_history_panel(self):
        titles = [chat['title'] for chat in self.chats]; titles.reverse()
        self.history_panel.update_history(titles)
        if self.current_chat_index != -1:
            reversed_index = len(self.chats) - 1 - self.current_chat_index
            self.history_panel.select_chat_by_index(reversed_index)

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            current_chat_widget = self.chat_area_container.currentWidget()
            if current_chat_widget: current_chat_widget.api_client.configure()

    def mousePressEvent(self, event: QMouseEvent):
        current_chat_widget = self.chat_area_container.currentWidget()
        if current_chat_widget and current_chat_widget.top_bar and event.button() == Qt.MouseButton.LeftButton and event.position().y() < current_chat_widget.top_bar.height():
            self._old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y()); self._old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._old_pos = None
