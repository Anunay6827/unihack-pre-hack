# styles.py
# This file contains all the QSS (Qt Style Sheets) for the application.

def get_stylesheet(theme='dark'):
    
    # --- Base Styles (common to both themes) ---
    base_style = """
        * { font-family: "Inter", "Segoe UI", "Roboto", "Helvetica Neue", sans-serif; }
        #iconBarButton { background-color: transparent; border: none; border-radius: 8px; padding: 12px; }
        #windowControlButton, #closeButton { background-color: transparent; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; width: 40px; height: 30px; }
        #closeButton:hover { background-color: #e81123; color: white; }
        #scrollArea { border: none; }
        QScrollBar:vertical { border: none; width: 8px; margin: 0px; border-radius: 4px; }
        #summaryDetails code { border-radius: 4px; padding: 2px 4px; font-family: "Courier New", monospace; }
    """

    # --- Dark Theme Palette ---
    dark_theme = """
        #centralWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1e1f22, stop:1 #131314); border-radius: 10px; }
        #settingsDialog, #iconBar, #historyPanel { background-color: #1e1f22; color: #e8eaed; }
        #initialPage { background-color: transparent; }
        #chatPage, #chatScrollWidget { background-color: #1e1f22; }   /* <-- ADDED */
        #iconBar { border-top-left-radius: 10px; border-bottom-left-radius: 10px; }
        #historyPanel { border-right: 1px solid #3c4043; }
        #iconBarButton:hover { background-color: #2a2b2e; }
        #windowControlButton:hover { background-color: #3c4043; }
        #recentLabel { color: #9aa0a6; }
        #historyButton { background-color: transparent; color: #bdc1c6; }
        #historyButton:hover { background-color: #2a2b2e; }
        #activeHistoryButton { background-color: #3c4043; color: #e8eaed; }
        #titleLabel, #userButton { color: #e8eaed; }
        #versionButton, #proButton { background-color: transparent; color: #bdc1c6; }
        #versionButton:hover, #proButton:hover { background-color: #2a2b2e; border-radius: 8px; }
        #userButton { background-color: #8ab4f8; color: #202124; }
        #welcomeLabel { color: #8ab4f8; }
        #bubbleContainer[alignment="left"] { background-color: #2a2b2e; color: #e8eaed; }
        #bubbleContainer[alignment="right"] { background-color: #3c4043; color: #e8eaed; }
        #statusLabel { color: #9aa0a6; }
        #commandLabel { color: #8ab4f8; }
        #outputLabel, #errorLabel, #summaryDetails, #summaryDetails QLabel { color: #bdc1c6; }
        #errorLabel { color: #f28b82; }
        #summaryButton, #pathButton { background-color: transparent; color: #bdc1c6; }
        #summaryButton:hover, #pathButton:hover { color: #e8eaed; }
        #summaryDetails { background-color: #2a2b2e; }
        #summaryDetails code { background-color: #1e1f22; }
        #inputFrame { background-color: #1e1f22; border: 1px solid #5f6368; }
        #promptInput { background-color: transparent; color: #e8eaed; }
        #sendButton { background-color: #8ab4f8; color: #202124; }
        #sendButton:hover { background-color: #9ac1f9; }
        QScrollBar:vertical { background: #2a2b2e; }
        QScrollBar::handle:vertical { background-color: #5f6368; }
        #confirmationWidget { background-color: #3c3223; border: 1px solid #f29900; }
        #warningLabel { color: #e8eaed; }
        #noButton { background-color: #5f6368; color: #e8eaed; }
        #noButton:hover { background-color: #70757a; }
        #yesButton { background-color: #e84135; color: #e8eaed; }
        #yesButton:hover { background-color: #f28b82; }
    """

    # --- Light Theme Palette ---
    light_theme = """
        #centralWidget { background-color: #ffffff; border-radius: 10px; border: 1px solid #dfe1e5; }
        #settingsDialog, #iconBar, #historyPanel { background-color: #f1f3f4; color: #202124; }
        #initialPage { background-color: #ffffff; }
        #chatPage, #chatScrollWidget { background-color: #ffffff; }   /* <-- ADDED */
        #iconBar { border-top-left-radius: 10px; border-bottom-left-radius: 10px; }
        #windowControlButton:hover { background-color: #dfe1e5; }
        #recentLabel { color: #5f6368; }
        #historyButton { background-color: transparent; color: #3c4043; }
        #historyButton:hover { background-color: #e8eaed; }
        #activeHistoryButton { background-color: #dfe1e5; color: #202124; }
        #titleLabel, #userButton { color: #202124; }
        #versionButton, #proButton { background-color: transparent; color: #5f6368; }
        #versionButton:hover, #proButton:hover { background-color: #e8eaed; border-radius: 8px; }
        #userButton { background-color: #4285f4; color: #ffffff; }
        #welcomeLabel { color: #4285f4; }
        #bubbleContainer[alignment="left"]  { background-color: #d6d9dc; }
        #bubbleContainer[alignment="right"] { background-color: #c9cccf; }
        #bubbleContainer QLabel { color: #000000; }   /* force black text */

        #statusLabel { color: #5f6368; }
        #commandLabel { color: #1a73e8; }
        #outputLabel, #errorLabel, #summaryDetails, #summaryDetails QLabel { color: #3c4043; }
        #errorLabel { color: #d93025; }
        #summaryButton, #pathButton { background-color: transparent; color: #5f6368; }
        #summaryButton:hover, #pathButton:hover { color: #202124; }
        #summaryDetails { background-color: #f1f3f4; }
        #summaryDetails code { background-color: #e8eaed; }
        #inputFrame { background-color: #f1f3f4; border: 1px solid #dfe1e5; }
        #promptInput { background-color: transparent; color: #202124; }
        #sendButton { background-color: #4285f4; color: #ffffff; }
        #sendButton:hover { background-color: #5a95f5; }
        QScrollBar:vertical { background: #e8eaed; }
        QScrollBar::handle:vertical { background-color: #bdc1c6; }
        #confirmationWidget { background-color: #feefc3; border: 1px solid #f9ab00; }
        #warningLabel { color: #202124; }
        #noButton { background-color: #bdc1c6; color: #202124; }
        #noButton:hover { background-color: #dfe1e5; }
        #yesButton { background-color: #d93025; color: #ffffff; }
        #yesButton:hover { background-color: #ea4335; }
    """
    
    # --- Common Styles for both themes ---
    common_styles = """
        #historyButton, #activeHistoryButton { border: none; padding: 12px; text-align: left; border-radius: 8px; font-size: 13px; }
        #titleLabel { font-size: 20px; font-weight: 500; }
        #versionButton, #proButton { padding: 8px; font-size: 14px; }
        #userButton { border: none; border-radius: 16px; font-size: 16px; font-weight: bold; min-width: 32px; max-width: 32px; min-height: 32px; max-height: 32px; }
        #welcomeLabel { font-size: 48px; font-weight: bold; }
        #bubbleContainer { border-radius: 18px; font-size: 14px; }
        #statusLabel { font-style: italic; font-size: 13px; }
        #commandLabel, #outputLabel, #errorLabel { font-family: "Courier New", monospace; }
        #commandLabel { font-size: 14px; padding: 5px 0 5px 5px; }
        #outputLabel, #errorLabel { font-size: 13px; padding-left: 5px; margin-bottom: 10px; }
        #summaryButton, #pathButton { border: none; padding: 4px; text-align: left; font-size: 14px; font-weight: 500; }
        #summaryDetails { border-radius: 8px; padding: 15px; margin-left: 5px; }
        #inputFrame { border-radius: 20px; }
        #promptInput { border: none; font-size: 15px; padding: 5px; }
        #sendButton { border: none; border-radius: 14px; font-size: 16px; min-width: 28px; max-width: 28px; min-height: 28px; max-height: 28px; }
    """


    if theme == 'light':
        return base_style + light_theme + common_styles
    else: # Default to dark
        return base_style + dark_theme + common_styles
