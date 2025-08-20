# main.py
# This is the entry point of our application.

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from main_window import MainWindow
# styles.py is now imported and managed by MainWindow

if __name__ == "__main__":
    # Create the application instance
    app = QApplication(sys.argv)

    # --- Font Configuration ---
    font_families = ["Inter", "Segoe UI", "Roboto", "Helvetica Neue", "sans-serif"]
    font = QFont()
    font.setFamilies(font_families)
    app.setFont(font)

    # Create and show the main window
    # The window itself will now handle applying the theme
    window = MainWindow()
    window.show()

    # Start the application's event loop
    sys.exit(app.exec())
