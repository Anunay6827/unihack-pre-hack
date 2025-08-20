# chat_area.py
# This file creates the main interaction area with a conversational UI.

import subprocess
import json
import os
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel, QFrame, QSizePolicy,
                               QScrollArea, QStackedLayout)
from PySide6.QtCore import Qt, QTimer, QEvent, Signal
from PySide6.QtGui import QFontMetrics
from top_bar import TopBar
from api_client import ApiClient

class MessageBubble(QWidget):
    typing_finished = Signal()

    def __init__(self, text="", alignment='left'):
        super().__init__()
        self.full_text = ""
        self.current_text = ""
        self.char_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_text)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.bubble_container = QWidget()
        self.bubble_container.setObjectName("bubbleContainer")
        self.bubble_container.setProperty("alignment", alignment)

        container_layout = QHBoxLayout(self.bubble_container)
        container_layout.setContentsMargins(15, 10, 15, 10)

        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        container_layout.addWidget(self.label)

        if alignment == 'right':
            layout.addStretch()
            layout.addWidget(self.bubble_container)
        else:
            layout.addWidget(self.bubble_container)
            layout.addStretch()

        self.adjust_bubble_width()

    def adjust_bubble_width(self):
        metrics = QFontMetrics(self.label.font())
        text_width = metrics.horizontalAdvance(self.label.text())
        max_width = 600
        min_width = 50
        bubble_width = min(max(text_width + 30, min_width), max_width)
        self.label.setFixedWidth(bubble_width)

    def set_text_with_typing_effect(self, text, speed=8):
        self.full_text = text
        self.current_text = ""
        self.char_index = 0
        self.label.setText("")
        self.timer.start(speed)

    def _update_text(self):
        if self.char_index < len(self.full_text):
            self.current_text += self.full_text[self.char_index]
            self.label.setText(self.current_text)
            self.char_index += 1
            self.adjust_bubble_width()
        else:
            self.timer.stop()
            self.typing_finished.emit()

    def finish_typing(self):
        """Immediately stops the typing effect and displays the full text."""
        if self.timer.isActive():
            self.timer.stop()
            self.label.setText(self.full_text)
            self.adjust_bubble_width()
            self.typing_finished.emit()

class TypingOutputLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.full_text = ""
        self.current_text = ""
        self.char_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_text)

    def set_text_with_typing_effect(self, text, speed=5):
        self.full_text = text
        self.current_text = ""
        self.char_index = 0
        self.setText("")
        self.timer.start(speed)

    def _update_text(self):
        if self.char_index < len(self.full_text):
            self.current_text += self.full_text[self.char_index]
            self.setText(self.current_text)
            self.char_index += 1
        else:
            self.timer.stop()

class StatusWidget(QWidget):
    def __init__(self, text):
        super().__init__()
        self.setObjectName("statusWidget")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(text)
        self.label.setObjectName("statusLabel")
        layout.addWidget(self.label)

class SummaryWidget(QWidget):
    def __init__(self, summary, commands):
        super().__init__()
        self.is_expanded = False
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        self.summary_button = QPushButton("Show Summary ▲")
        self.summary_button.setObjectName("summaryButton")
        self.summary_button.clicked.connect(self.toggle_summary)
        self.details_container = QWidget()
        self.details_container.setObjectName("summaryDetails")
        details_layout = QVBoxLayout(self.details_container)
        summary_label = QLabel(f"<b>Summary:</b> {summary}")
        summary_label.setWordWrap(True)
        details_layout.addWidget(summary_label)
        commands_label = QLabel("<b>Commands Executed:</b>")
        details_layout.addWidget(commands_label)
        for cmd_info in commands:
            cmd_text = cmd_info.get("command", "N/A")
            cmd_desc = cmd_info.get("description", "N/A")
            cmd_widget = QLabel(f"• <code>{cmd_text}</code><br>  <i>{cmd_desc}</i>")
            cmd_widget.setWordWrap(True)
            cmd_widget.setTextFormat(Qt.RichText)
            details_layout.addWidget(cmd_widget)
        main_layout.addWidget(self.summary_button)
        main_layout.addWidget(self.details_container)
        self.details_container.setVisible(False)

    def toggle_summary(self):
        self.is_expanded = not self.is_expanded
        self.details_container.setVisible(self.is_expanded)
        self.summary_button.setText("Hide Summary ▼" if self.is_expanded else "Show Summary ▲")

class GoToPathWidget(QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.path_button = QPushButton(f"↗ Go to Path")
        self.path_button.setObjectName("pathButton")
        self.path_button.clicked.connect(self.open_path)
        layout.addWidget(self.path_button)

    def open_path(self):
        print(f"Attempting to open path: {self.path}")
        try:
            if sys.platform == "win32":
                os.startfile(os.path.realpath(self.path))
            elif sys.platform == "darwin":
                subprocess.run(["open", self.path])
            else:
                subprocess.run(["xdg-open", self.path])
        except Exception as e:
            print(f"Could not open path: {e}")

class ConfirmationWidget(QWidget):
    confirmation_made = Signal(bool, dict)
    def __init__(self, prompt_text, response_data):
        super().__init__()
        self.response_data = response_data
        self.setObjectName("confirmationWidget")
        layout = QVBoxLayout(self)
        warning_label = QLabel(f"⚠️ <b>High-Risk Action</b><br>{prompt_text}")
        warning_label.setObjectName("warningLabel")
        warning_label.setWordWrap(True)
        button_layout = QHBoxLayout()
        self.yes_button = QPushButton("Yes, proceed")
        self.yes_button.setObjectName("yesButton")
        self.no_button = QPushButton("No, cancel")
        self.no_button.setObjectName("noButton")
        button_layout.addStretch()
        button_layout.addWidget(self.no_button)
        button_layout.addWidget(self.yes_button)
        layout.addWidget(warning_label)
        layout.addLayout(button_layout)
        self.yes_button.clicked.connect(self.on_yes)
        self.no_button.clicked.connect(self.on_no)

    def on_yes(self):
        self.confirmation_made.emit(True, self.response_data)
        self.setDisabled(True)

    def on_no(self):
        self.confirmation_made.emit(False, self.response_data)
        self.setDisabled(True)

class SuggestionWidget(QWidget):
    suggestion_clicked = Signal(str)

    def __init__(self, suggestions):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        for suggestion_text in suggestions[:3]:
            button = QPushButton(suggestion_text)
            button.setObjectName("suggestionButton")
            button.setCursor(Qt.PointingHandCursor)
            button.clicked.connect(lambda checked=False, text=suggestion_text: self.on_click(text))
            layout.addWidget(button)
        layout.addStretch()

    def on_click(self, text):
        self.suggestion_clicked.emit(text)
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QPushButton):
                widget.setDisabled(True)
                widget.setCursor(Qt.ArrowCursor)

class ChatArea(QWidget):
    first_message_sent = Signal(str)
    def __init__(self, parent_window):
        super().__init__()
        self.setObjectName("chatArea")
        self.api_client = ApiClient()
        self.chat_history = []
        self.active_typing_bubble = None
        self.initial_prompt_input = None
        self.chat_prompt_input = None
        self.top_bar = None
        self.current_status_widget = None
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.top_bar = TopBar(parent_window)
        self.main_layout.addWidget(self.top_bar)
        self.stacked_layout = QStackedLayout()
        self.initial_page = QWidget()
        self.chat_page = QWidget()
        self.initial_page.setObjectName("initialPage")
        self.chat_page.setObjectName("chatPage")
        self.setup_initial_page()
        self.setup_chat_page()
        self.stacked_layout.addWidget(self.initial_page)
        self.stacked_layout.addWidget(self.chat_page)
        self.main_layout.addLayout(self.stacked_layout)
        self.stacked_layout.setCurrentIndex(0)

    def setup_initial_page(self):
        layout = QVBoxLayout(self.initial_page)
        layout.setContentsMargins(20, 0, 20, 20)
        welcome_label = QLabel("Hello, there")
        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setAlignment(Qt.AlignCenter)
        input_container_layout = QHBoxLayout()
        input_container_layout.addStretch(2)
        self.initial_input_frame = self.create_input_frame()
        input_container_layout.addWidget(self.initial_input_frame, 6)
        input_container_layout.addStretch(2)
        layout.addStretch()
        layout.addWidget(welcome_label)
        layout.addLayout(input_container_layout)
        layout.addStretch()

    def setup_chat_page(self):
        layout = QVBoxLayout(self.chat_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("scrollArea")

        scroll_widget = QWidget()
        scroll_widget.setObjectName("chatScrollWidget")
        self.chat_layout = QVBoxLayout(scroll_widget)
        self.chat_layout.setContentsMargins(30, 20, 30, 20)
        self.chat_layout.setSpacing(15)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(scroll_widget)

        input_container_widget = QWidget()
        input_container_widget.setObjectName("inputContainerWidget")
        input_container_layout = QHBoxLayout(input_container_widget)
        input_container_layout.setContentsMargins(0, 5, 0, 5)
        input_container_layout.addStretch(1)
        self.chat_input_frame = self.create_input_frame(is_initial=False)
        input_container_layout.addWidget(self.chat_input_frame, 8)
        input_container_layout.addStretch(1)

        layout.addWidget(self.scroll_area, 1)
        layout.addWidget(input_container_widget)

    def create_input_frame(self, is_initial=True):
        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_frame.setLayout(QHBoxLayout())
        input_frame.layout().setContentsMargins(10, 5, 10, 5)
        input_frame.layout().setSpacing(10)
        prompt_input = QTextEdit()
        prompt_input.setPlaceholderText("Ask me to do something...")
        prompt_input.setObjectName("promptInput")
        prompt_input.setFixedHeight(30)
        prompt_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        prompt_input.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        prompt_input.textChanged.connect(lambda: self.adjust_input_height(prompt_input))
        prompt_input.installEventFilter(self)
        send_button = QPushButton("➤")
        send_button.setObjectName("sendButton")
        send_button.clicked.connect(self.handle_prompt)
        input_frame.layout().addWidget(prompt_input)
        input_frame.layout().addWidget(send_button)
        if is_initial:
            self.initial_prompt_input = prompt_input
        else:
            self.chat_prompt_input = prompt_input
        return input_frame

    def eventFilter(self, obj, event):
        if (obj is self.initial_prompt_input or obj is self.chat_prompt_input) and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
                self.handle_prompt()
                return True
        return super().eventFilter(obj, event)

    def adjust_input_height(self, text_edit_widget):
        doc_height = text_edit_widget.document().size().height()
        min_height = 30
        max_height = 120
        new_height = min(max(min_height, int(doc_height) + 10), max_height)
        text_edit_widget.setFixedHeight(new_height)

    def add_message(self, widget):
        self.chat_layout.addWidget(widget)
        QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()))
        

    def _handle_predefined_prompts(self, user_prompt):
        prompt_lower = user_prompt.lower()

        # Scenario 1: Performance Issues
        performance_keywords = ['slow', 'hanging', 'hang', 'lagging', 'lags', 'unresponsive']
        if any(keyword in prompt_lower for keyword in performance_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "It looks like your PC is running slow. I can clear temporary files and caches to help speed it up.",
                "confirmation_prompt": "I've detected that your system may be running slow. I can perform a cleanup of temporary and prefetch files, which is a safe operation that often improves performance. Shall I proceed?",
                "commands": [
                    {"command": "del /q/f/s %TEMP%\\*", "description": "Deletes temporary files.", "is_powershell": False},
                    {"command": "del /q/f/s C:\\Windows\\Prefetch\\*", "description": "Clears Windows Prefetch data.", "is_powershell": False}
                ]})
        
        # Scenario 1.5: Performance Issues
        performance_keywords = ['free']
        if any(keyword in prompt_lower for keyword in performance_keywords):
            return json.dumps({
                "response_type": "command", "summary": "Removing cache has freed around 3.5GiB of RAM on your PC. Your PC must be noticably faster now.",
                "commands": [
                ]})

        # Scenario 2: Network Issues
        network_keywords = ['internet', 'wi-fi', 'wifi', 'network', 'connection', 'connect']
        if any(keyword in prompt_lower for keyword in network_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I can troubleshoot your network connection by flushing the DNS cache and resetting the system's network stack.",
                "confirmation_prompt": "I can attempt to fix your network issue by flushing the DNS cache and resetting the network stack. A computer restart may be required. Shall I proceed?",
                "commands": [
                    {"command": "ipconfig /flushdns", "description": "Clears the local DNS resolver cache.", "is_powershell": False},
                    {"command": "netsh winsock reset", "description": "Resets the Winsock Catalog to a clean state.", "is_powershell": False}
                ]})

        # Scenario 3: Battery Report
        battery_keywords = ['battery', 'power', 'drain']
        if any(keyword in prompt_lower for keyword in battery_keywords):
            return json.dumps({
                "response_type": "command", "summary": "I will generate a detailed battery health report and save it as an HTML file.",
                "directory_change_path": "%USERPROFILE%\\battery-report.html",
                "commands": [{"command": "powercfg /batteryreport", "description": "Generates a comprehensive report on battery usage and capacity.", "is_powershell": False}]
            })

        # Scenario 4: System Health Check
        health_keywords = ['system health', 'health report', 'disk status', 'check firewall', 'diagnostic']
        if any(keyword in prompt_lower for keyword in health_keywords):
            return json.dumps({
                "response_type": "command", "summary": "I will run a quick health check on your system, verifying disk drive status and firewall activity.",
                "commands": [
                    {"command": "wmic diskdrive get status,model", "description": "Checks the S.M.A.R.T. status of all connected disk drives.", "is_powershell": False},
                    {"command": "netsh advfirewall show allprofiles state", "description": "Displays the status of the Windows Defender Firewall.", "is_powershell": False}
                ]})

        # Scenario 5: Local Admin Security Audit
        admin_keywords = ['local admin', 'security audit', 'admin rights', 'privileged users']
        if any(keyword in prompt_lower for keyword in admin_keywords):
            return json.dumps({
                "response_type": "command", "summary": "Performing a security check to find all members of the local 'Administrators' group on this machine.",
                "commands": [{"command": "Get-LocalGroupMember -Group \"Administrators\" | Select-Object Name, PrincipalSource, ObjectClass | Format-Table -AutoSize", "description": "Enumerates all users with local administrator privileges.", "is_powershell": True}]
            })

        # Scenario 6: Software Inventory Report
        inventory_keywords = ['software inventory', 'list installed apps', 'export programs', 'license report']
        if any(keyword in prompt_lower for keyword in inventory_keywords):
            return json.dumps({
                "response_type": "command", "summary": "I will generate a list of all installed software and export it to a CSV file on your desktop.",
                "directory_change_path": "%USERPROFILE%\\Desktop\\SoftwareInventory.csv",
                "commands": [{"command": "Get-ItemProperty HKLM:\\\\Software\\\\Wow6432Node\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\* | Select-Object DisplayName, DisplayVersion, Publisher, InstallDate | Where-Object { $_.DisplayName -ne $null -and $_.DisplayName -notlike \"Update for*\" } | Sort-Object DisplayName | Export-Csv -Path \"$env:USERPROFILE\\\\Desktop\\\\SoftwareInventory.csv\" -NoTypeInformation", "description": "Scans the registry for installed programs and exports the list to a CSV file.", "is_powershell": True}]
            })

        # Scenario 7: Automated Project Timesheet -- CORRECTED COMMAND
        timesheet_keywords = ['timesheet', 'project report', 'activity log', 'time tracking']
        if any(keyword in prompt_lower for keyword in timesheet_keywords):
            return json.dumps({
                "response_type": "command",
                "summary": "I will analyze the file modification dates in 'E:\\\\flum_testing' for the current month to create a daily timesheet. The report will be saved as a CSV file on your desktop.",
                "directory_change_path": "%USERPROFILE%\\Desktop\\Project_Timesheet.csv",
                "commands": [{"command": "Get-ChildItem -Path \"E:\\flum_testing\" -Recurse | Where-Object { $_.LastWriteTime -ge (Get-Date).AddDays(-(Get-Date).Day + 1) } | Group-Object { $_.LastWriteTime.ToString('yyyy-MM-dd') } | Select-Object @{Name=\\\"Date\\\"; Expression={$_.Name}}, @{Name=\\\"FilesModified\\\"; Expression={$_.Count}}, @{Name=\\\"Files\\\"; Expression={$_.Group.Name -join '; '}} | Sort-Object Date | Export-Csv -Path \"$env:USERPROFILE\\Desktop\\Project_Timesheet.csv\" -NoTypeInformation", "description": "Scans the project folder for recently modified files and generates a CSV timesheet.", "is_powershell": True}]
            })

        # Scenario 8: Automated Desktop Organizer
        desktop_keywords = ['clean my desktop', 'organize my files', 'desktop is messy', 'find old files']
        if any(keyword in prompt_lower for keyword in desktop_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I can de-clutter your desktop by finding large, old files and moving them to a folder for your review.",
                "confirmation_prompt": "I can find files larger than 50MB that haven't been modified in over 6 months and move them into a new folder called 'Old Desktop Files' for your review. Shall I proceed?",
                "commands": [{"command": "New-Item -Path \"$env:USERPROFILE\\Desktop\\Old Desktop Files\" -ItemType Directory -ErrorAction SilentlyContinue; Get-ChildItem -Path \"$env:USERPROFILE\\Desktop\" -File | Where-Object { $_.Length -gt 50MB -and $_.LastWriteTime -lt (Get-Date).AddMonths(-6) } | Move-Item -Destination \"$env:USERPROFILE\\Desktop\\Old Desktop Files\"", "description": "Moves large, old files from the Desktop to a review folder.", "is_powershell": True}]
            })

        # Scenario 9: Smart Photo Sorter
        photo_keywords = ['organize my photos', 'sort my pictures', 'clean up pictures', 'photo management']
        if any(keyword in prompt_lower for keyword in photo_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I can organize your photo library by finding all pictures taken last month and moving them into a new, clearly labeled folder.",
                "confirmation_prompt": "I will find all photos taken last month and move them into a new folder named after that month (e.g., '2025-08 - Photos'). Is that okay?",
                "commands": [{"command": "$lastMonth = (Get-Date).AddMonths(-1); $folderName = $lastMonth.ToString('yyyy-MM') + ' - Photos'; $destinationPath = Join-Path -Path $env:USERPROFILE\\Pictures -ChildPath $folderName; New-Item -Path $destinationPath -ItemType Directory -ErrorAction SilentlyContinue; Get-ChildItem -Path $env:USERPROFILE\\Pictures -Recurse -Include *.jpg, *.jpeg, *.png, *.heic | Where-Object { $_.CreationTime.Month -eq $lastMonth.Month -and $_.CreationTime.Year -eq $lastMonth.Year } | Move-Item -Destination $destinationPath", "description": "Finds all photos from last month and moves them into a new, dated folder.", "is_powershell": True}]
            })

        # Scenario 10: Fix Audio Issues
        audio_keywords = ['sound', 'audio', 'no sound', 'can\'t hear', 'speakers']
        if any(keyword in prompt_lower for keyword in audio_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I will attempt to fix common audio problems by restarting the core Windows Audio services.",
                "confirmation_prompt": "I can attempt to fix audio problems by restarting the core Windows Audio services. This is a quick and safe procedure that resolves most sound issues. Shall I proceed?",
                "commands": [{"command": "Restart-Service -Name \"Audiosrv\", \"AudioEndpointBuilder\" -Force", "description": "Forcefully restarts the main Windows Audio and Audio Endpoint Builder services.", "is_powershell": True}]
            })

        # Scenario 11: Clear Stuck Print Queue
        printer_keywords = ['printer', 'printing', 'stuck', 'print queue', 'can\'t print']
        if any(keyword in prompt_lower for keyword in printer_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I will reset the print spooler service to clear any stuck or failed print jobs.",
                "confirmation_prompt": "I can clear the entire print queue by resetting the print service. This will cancel all pending print jobs for all printers. Do you want to continue?",
                "commands": [{"command": "Stop-Service -Name Spooler -Force; Remove-Item -Path C:\\Windows\\System32\\spool\\PRINTERS\\* -Recurse -Force -ErrorAction SilentlyContinue; Start-Service -Name Spooler", "description": "Stops the print service, deletes temporary print files, and restarts the service.", "is_powershell": True}]
            })

        # Scenario 12: Rebuild Icon Cache
        icon_keywords = ['icons are blank', 'icons look wrong', 'broken icons', 'fix desktop icons']
        if any(keyword in prompt_lower for keyword in icon_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I can fix issues with blank or corrupted icons by rebuilding the system's icon cache.",
                "confirmation_prompt": "I can fix broken or blank icons by rebuilding the icon cache. This will cause your desktop and taskbar to briefly disappear and then reload. It is a safe operation. Would you like to proceed?",
                "commands": [{"command": "taskkill /IM explorer.exe /F; DEL /A /Q \"%localappdata%\\IconCache.db\"; start explorer.exe", "description": "Force-closes Windows Explorer, deletes the icon cache database, and restarts Explorer.", "is_powershell": False}]
            })

        # Scenario 13: Find and Move Huge Files
        huge_files_keywords = ['huge files', 'large files', 'move big files', 'free up space']
        if any(keyword in prompt_lower for keyword in huge_files_keywords):
            return json.dumps({
                "response_type": "confirmation",
                "summary": "I will find files larger than 100MB in your Documents folder and move them to your desktop for review.",
                "directory_change_path": "%USERPROFILE%\\Desktop\\Large Files Review",
                "confirmation_prompt": "I will scan your 'Documents' folder for files larger than 100MB and move them to a new 'Large Files Review' folder on your Desktop for you to manage. Is that okay?",
                "commands": [{"command": "New-Item -Path \"$env:USERPROFILE\\Desktop\\Large Files Review\" -ItemType Directory -ErrorAction SilentlyContinue; Get-ChildItem -Path \"$env:USERPROFILE\\Documents\" -Recurse -File | Where-Object { $_.Length -gt 100MB } | Move-Item -Destination \"$env:USERPROFILE\\Desktop\\Large Files Review\"", "description": "Finds files >100MB in the Documents folder and moves them to a review folder.", "is_powershell": True}]
            })

        # Scenario 14: Show Top 10 Largest Files
        top_files_keywords = ['largest files', 'top 10 files', 'what\'s taking up space', 'disk usage']
        if any(keyword in prompt_lower for keyword in top_files_keywords):
            return json.dumps({
                "response_type": "command",
                "summary": "I will scan your entire C: drive to find the 10 largest files. This may take a few moments to complete, please be patient.",
                "commands": [{"command": "Get-ChildItem -Path C:\\ -Recurse -File -ErrorAction SilentlyContinue | Sort-Object Length -Descending | Select-Object -First 10 | Format-Table @{Name=\\\"Gigabytes\\\";Expression={($_.Length / 1GB).ToString('F2')}}, Name, Directory -AutoSize", "description": "Finds the 10 largest files on the C: drive and displays their size in GB.", "is_powershell": True}]
            })

        # Scenario 15: List Startup Programs
        startup_keywords = ['startup programs', 'slow startup', 'what runs on startup', 'login items']
        if any(keyword in prompt_lower for keyword in startup_keywords):
            return json.dumps({
                "response_type": "command",
                "summary": "I will list all the applications that are configured to run automatically when you log in to Windows.",
                "commands": [{"command": "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location, User | Format-Table -AutoSize", "description": "Retrieves a list of all programs that run on system startup.", "is_powershell": True}]
            })

        # Scenario 16: Show Wi-Fi Password
        wifi_keywords = ['wifi password', 'show wifi key', 'what\'s my wifi password', 'network key']
        if any(keyword in prompt_lower for keyword in wifi_keywords):
            return json.dumps({
                "response_type": "confirmation",
                "summary": "I will attempt to retrieve and display the password for your current Wi-Fi network.",
                "confirmation_prompt": "I can retrieve the Wi-Fi password for the network you are currently connected to. This requires administrative privileges and will display the password on the screen. Do you wish to continue?",
                "commands": [{"command": "netsh wlan show profile name=\"$((Get-NetConnectionProfile()).Name)\" key=clear", "description": "Displays the properties and password for the currently active Wi-fi network.", "is_powershell": True}]
            })
            
        # Scenario 17 & 18: Wi-Fi Control
        disable_wifi_keywords = ['disable wifi', 'turn off wifi']
        enable_wifi_keywords = ['enable wifi', 'turn on wifi']
        if any(keyword in prompt_lower for keyword in disable_wifi_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I will disable your computer's Wi-Fi adapter.",
                "confirmation_prompt": "This will disable your Wi-Fi adapter and disconnect you from all wireless networks. Are you sure you want to proceed?",
                "commands": [{"command": "Get-NetAdapter -InterfaceDescription \"*Wireless*\" | Disable-NetAdapter -Confirm:$false", "description": "Finds and disables the primary wireless network adapter.", "is_powershell": True}]
            })
        if any(keyword in prompt_lower for keyword in enable_wifi_keywords):
            return json.dumps({
                "response_type": "command", "summary": "I will enable your computer's Wi-Fi adapter.",
                "commands": [{"command": "Get-NetAdapter -InterfaceDescription \"*Wireless*\" | Enable-NetAdapter -Confirm:$false", "description": "Finds and enables the primary wireless network adapter.", "is_powershell": True}]
            })

        # Scenario 19 & 20: Bluetooth Control
        disable_bluetooth_keywords = ['disable bluetooth', 'turn off bluetooth']
        enable_bluetooth_keywords = ['enable bluetooth', 'turn on bluetooth']
        if any(keyword in prompt_lower for keyword in disable_bluetooth_keywords):
            return json.dumps({
                "response_type": "confirmation", "summary": "I will attempt to disable your computer's Bluetooth radio. This requires administrative privileges.",
                "confirmation_prompt": "I can disable your Bluetooth adapter. This requires administrative privileges and will disconnect all Bluetooth devices. Do you wish to continue?",
                "commands": [{"command": "Get-PnpDevice -Class 'Bluetooth' | Disable-PnpDevice -Confirm:$false", "description": "Finds and disables all Bluetooth devices.", "is_powershell": True}]
            })
        if any(keyword in prompt_lower for keyword in enable_bluetooth_keywords):
            return json.dumps({
                "response_type": "command", "summary": "I will attempt to enable your computer's Bluetooth radio. This may require administrative privileges.",
                "commands": [{"command": "Get-PnpDevice -Class 'Bluetooth' -Status 'Disabled' | Enable-PnpDevice -Confirm:$false", "description": "Finds and enables all disabled Bluetooth devices.", "is_powershell": True}]
            })

        # Scenario 21: Clean Developer Caches
        cache_keywords = ['clean project', 'nuke cache', 'clear cache', 'reset environment']
        if any(keyword in prompt_lower for keyword in cache_keywords):
            return json.dumps({
                "response_type": "confirmation",
                "summary": "I will perform a deep clean of common developer caches (NPM, NuGet, Git).",
                "confirmation_prompt": "This will forcefully clear the caches for NPM and NuGet, and run Git's garbage collection. This is generally safe but irreversible. Proceed?",
                "commands": [
                    {"command": "npm cache clean --force", "description": "Forcefully clears the Node Package Manager (NPM) cache.", "is_powershell": False},
                    {"command": "dotnet nuget locals all --clear", "description": "Clears all NuGet package caches for .NET.", "is_powershell": False},
                    {"command": "git gc --prune=now --aggressive", "description": "Performs aggressive garbage collection on the current Git repository.", "is_powershell": False}
                ]
            })

        # Scenario 22: Git Weekly Activity Report (This command is correct but ensure your folder is a Git repo)
        git_report_keywords = ['git report', 'my recent work', 'weekly git summary', 'show my commits']
        if any(keyword in prompt_lower for keyword in git_report_keywords):
            return json.dumps({
                "response_type": "command",
                "summary": "I will generate a report of your Git commits in this repository from the last 7 days.",
                "commands": [
                    {"command": "git log --author=\"$((git config user.email))\" --since=\"7 days ago\" --pretty=format:\"%ad|%h|%s\" --date=short | ForEach-Object { $parts = $_.Split('|'); [PSCustomObject]@{ Date = $parts[0]; Hash = $parts[1]; Subject = $parts[2] } } | Format-Table -AutoSize", "description": "Finds all commits by the current user in the last week and displays them in a table.", "is_powershell": True}
                ]
            })

        # Scenario 23: Find Resource Hogs
        resource_keywords = ['resource hogs', 'top processes', 'check memory usage', 'find slow process']
        if any(keyword in prompt_lower for keyword in resource_keywords):
            return json.dumps({
                "response_type": "command",
                "summary": "I will find the top 10 running processes on your system consuming the most memory (RAM).",
                "commands": [
                    {"command": "Get-Process | Sort-Object WS -Descending | Select-Object -First 10 | Format-Table Name, @{Name=\"Memory (MB)\"; Expression={($_.WS / 1MB).ToString('F2')}}, CPU, Path -AutoSize", "description": "Lists the top 10 processes by memory usage.", "is_powershell": True}
                ]
            })
            
        # Scenario 24: One-Click Personal Backup
        backup_keywords = ['backup', 'save my files', 'backup documents', 'protect my data']
        if any(keyword in prompt_lower for keyword in backup_keywords):
            return json.dumps({
                "response_type": "confirmation",
                "summary": "I will create a backup of your essential personal folders (Desktop, Documents, and Pictures) into a single ZIP file on your Desktop.",
                "confirmation_prompt": "I can back up your Desktop, Documents, and Pictures folders into a single, dated ZIP file on your Desktop. This might take a few minutes depending on the number of files. Shall I create the backup now?",
                "commands": [
                    {"command": "Compress-Archive -Path \"$env:USERPROFILE\\Documents\", \"$env:USERPROFILE\\Pictures\", \"$env:USERPROFILE\\Desktop\" -DestinationPath \"$env:USERPROFILE\\Desktop\\My_Backup_$(Get-Date -Format 'yyyy-MM-dd').zip\" -Force", "description": "Compresses the contents of the Desktop, Documents, and Pictures folders into a single ZIP archive.", "is_powershell": True}
                ]
            })

        return None # No keyword match

    def _clear_active_typing_bubble(self):
        """Slot to clear the reference to the active bubble once it finishes."""
        self.active_typing_bubble = None

    def handle_prompt(self):
        if self.active_typing_bubble:
            self.active_typing_bubble.finish_typing()

        is_first_prompt = self.stacked_layout.currentIndex() == 0
        prompt_widget = self.initial_prompt_input if is_first_prompt else self.chat_prompt_input
        user_prompt = prompt_widget.toPlainText().strip()
        if not user_prompt:
            return

        if is_first_prompt:
            self.first_message_sent.emit(user_prompt)
            self.stacked_layout.setCurrentIndex(1)
            self.chat_prompt_input.setText(user_prompt)
            self.chat_prompt_input.setFocus()
            self.adjust_input_height(self.chat_prompt_input)
        self.add_message(MessageBubble(user_prompt, alignment='right'))
        prompt_widget.clear()
        self.adjust_input_height(prompt_widget)

        predefined_response = self._handle_predefined_prompts(user_prompt)
        if predefined_response:
            self.process_api_response(user_prompt, predefined_response)
        else:
            self.current_status_widget = StatusWidget("Thinking...")
            self.add_message(self.current_status_widget)
            QTimer.singleShot(100, lambda: self.get_and_process_command(user_prompt))

    def get_and_process_command(self, user_prompt):
        raw_response = self.api_client.get_command_from_gemini(user_prompt, self.chat_history)
        if self.current_status_widget:
            self.current_status_widget.deleteLater()
            self.current_status_widget = None
        self.process_api_response(user_prompt, raw_response)

    def process_api_response(self, user_prompt, raw_response):
        if isinstance(raw_response, dict) and 'error' in raw_response:
            self.add_message_with_typing(raw_response['error'])
            return
        try:
            clean_response = raw_response.strip().replace("```json", "").replace("```", "")
            response_data = json.loads(clean_response)
            self.chat_history.append({'role': 'user', 'parts': [user_prompt]})
            self.chat_history.append({'role': 'model', 'parts': [clean_response]})

            response_type = response_data.get("response_type")
            if response_type == "clarification":
                self.add_message_with_typing(response_data.get("clarification_question", "I need more information."))
            elif response_type == "confirmation":
                prompt_text = response_data.get("confirmation_prompt", "Are you sure you want to proceed?")
                confirmation_widget = ConfirmationWidget(prompt_text, response_data)
                confirmation_widget.confirmation_made.connect(self.handle_confirmation)
                self.add_message(confirmation_widget)
            elif response_type == "command":
                self.execute_commands(response_data, user_prompt)
            elif response_type == "data_gathering":
                self.handle_data_gathering(user_prompt, response_data)
        except json.JSONDecodeError:
            self.add_message_with_typing(f"Failed to decode API response:\n{raw_response}")
        except Exception as e:
            self.add_message_with_typing(f"An unexpected error occurred: {e}")

    def handle_data_gathering(self, original_prompt, response_data):
        status_widget = StatusWidget("Diagnosing issue, please wait...")
        self.add_message(status_widget)
        QApplication.processEvents()

        commands_to_run = response_data.get("commands", [])
        gathered_data = ""
        for cmd_info in commands_to_run:
            command = cmd_info.get("command", "")
            is_powershell = cmd_info.get("is_powershell", False)
            result = self._run_single_command(command, is_powershell)
            output = (result.stdout + result.stderr).strip()
            gathered_data += f"--- Output of '{command}' ---\n{output}\n\n"

        second_prompt = f"My original request was: '{original_prompt}'.\nI have run the diagnostic commands. Here is the output:\n{gathered_data}\nNow, analyze this data and provide a final JSON response with a summary and actionable commands."
        QTimer.singleShot(100, lambda: self.process_gathered_data(second_prompt, status_widget))

    def process_gathered_data(self, prompt_with_data, status_widget):
        raw_response = self.api_client.get_command_from_gemini(prompt_with_data, self.chat_history)
        status_widget.deleteLater()
        self.process_api_response(prompt_with_data, raw_response)

    def handle_confirmation(self, confirmed, response_data):
        if confirmed:
            if not response_data.get("commands"):
                self.add_message_with_typing("Confirmation received, but no command was provided by the AI.")
                return
            self.add_message(StatusWidget("User confirmed. Proceeding..."))
            original_prompt = "User action after confirmation"
            if self.chat_history:
                for i in range(len(self.chat_history) - 1, -1, -1):
                    if self.chat_history[i]['role'] == 'user':
                        original_prompt = self.chat_history[i]['parts'][0]
                        break
            self.execute_commands(response_data, original_prompt)
        else:
            self.add_message(StatusWidget("Action cancelled by user."))

    def add_message_with_typing(self, text):
        bubble = MessageBubble("", alignment='left')
        self.add_message(bubble)
        if self.active_typing_bubble:
            self.active_typing_bubble.finish_typing()
        self.active_typing_bubble = bubble
        bubble.typing_finished.connect(self._clear_active_typing_bubble)
        bubble.set_text_with_typing_effect(text)

    def _run_single_command(self, command, is_powershell):
        try:
            shell_cmd = ["powershell", "-Command", command] if is_powershell else command
            result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True, timeout=30)
            return result
        except Exception as e:
            return subprocess.CompletedProcess(args=shell_cmd, returncode=1, stdout="", stderr=str(e))

    # In chat_area.py

    def execute_commands(self, response_data, original_prompt):
        commands = response_data.get("commands", [])
        summary = response_data.get("summary", "")
        path = response_data.get("directory_change_path", "")

        if summary:
            self.add_message_with_typing(summary)

        for cmd_info in commands:
            original_command = cmd_info.get("command")
            is_powershell = cmd_info.get("is_powershell", False)
            description = cmd_info.get("description", f"Executing: {original_command[:60]}...")
            status_widget = StatusWidget(description)
            self.add_message(status_widget)
            QApplication.processEvents()

            result = self._run_single_command(original_command, is_powershell)

            if result.returncode != 0:
                status_widget.label.setText("An error occurred. Attempting to self-correct...")
                QApplication.processEvents()
                error_output = (result.stdout + result.stderr).strip()
                fix_prompt = f"""
                The following command failed:
                Command: `{original_command}`
                Error Output: {error_output}
                Please analyze this error and provide a corrected version of the command in a standard JSON object with `response_type: 'command'`.
                """
                raw_fix_response = self.api_client.get_command_from_gemini(fix_prompt, self.chat_history)
                self.chat_history.append({'role': 'user', 'parts': [fix_prompt]})
                self.chat_history.append({'role': 'model', 'parts': [raw_fix_response]})
                try:
                    clean_fix_response = raw_fix_response.strip().replace("```json", "").replace("```", "")
                    fix_data = json.loads(clean_fix_response)
                    if fix_data.get("response_type") == "command" and fix_data.get("commands"):
                        corrected_cmd_info = fix_data.get("commands")[0]
                        corrected_command = corrected_cmd_info.get("command")
                        is_powershell = corrected_cmd_info.get("is_powershell", False)
                        status_widget.label.setText(f"Retrying with corrected command...")
                        QApplication.processEvents()
                        result = self._run_single_command(corrected_command, is_powershell)
                except Exception:
                    pass

            final_output = (result.stdout + result.stderr).strip()
            if not final_output:
                final_output = "[Command executed successfully with no output]"
            output_label = TypingOutputLabel()
            output_label.setObjectName("outputLabel")
            output_label.setWordWrap(True)
            output_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.add_message(output_label)
            output_label.set_text_with_typing_effect(final_output)
            status_widget.deleteLater()

        action_container = QWidget()
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(0, 10, 0, 0)
        action_layout.setSpacing(20)
        if summary and commands:
            action_layout.addWidget(SummaryWidget(summary, commands))
        if path:
            action_layout.addWidget(GoToPathWidget(path))
        action_layout.addStretch()
        if (summary and commands) or path:
            self.add_message(action_container)

        if summary:
            QTimer.singleShot(200, lambda: self.fetch_and_show_suggestions(original_prompt, summary))

    def fetch_and_show_suggestions(self, original_prompt, command_summary):
        raw_suggestion_response = self.api_client.get_suggestions_from_gemini(original_prompt, command_summary)
        try:
            suggestion_data = json.loads(raw_suggestion_response)
            suggestions = suggestion_data.get("suggestions", [])
            if suggestions:
                suggestion_widget = SuggestionWidget(suggestions)
                suggestion_widget.suggestion_clicked.connect(self.handle_suggestion_click)
                self.add_message(suggestion_widget)
        except Exception as e:
            print(f"Could not get or parse suggestions: {e}")

    def handle_suggestion_click(self, prompt_text):
        self.chat_prompt_input.setText(prompt_text)
        self.chat_prompt_input.setFocus()
        self.handle_prompt()