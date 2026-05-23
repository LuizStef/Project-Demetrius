import glob
import profile
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QFrame, QSizePolicy, QMenu, QColorDialog,
    QDialog, QFormLayout, QComboBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPainter, QPixmap, QAction
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import QByteArray
from sympy import sec

from security import Security, logger
from smart_memory import SmartMemory
from demetrius import Demetrius
from automation import Automation
from exceptions import DemetriusOfflineError


# ─── THEME ────────────────────────────────────────────────────────────────────

THEME = {
    "bg":        "#111111",
    "bg2":       "#1a1a1a",
    "bg3":       "#222222",
    "border":    "#2a2a2a",
    "text":      "#e0e0e0",
    "text_dim":  "#666666",
    "accent":    "#ffffff",
    "user":      "#e0e0e0",
    "assistant": "#909090",
    "system":    "#555555",
    "error":     "#e06c75",
    "font":      "Inter, Segoe UI, Arial",
    "font_size": 13,
}

# ─── ICONS ────────────────────────────────────────────────────────────────────

def svg_icon(svg_str, size=16):
    data = QByteArray(svg_str.encode())
    px = QPixmap(size, size)
    px.fill(Qt.GlobalColor.transparent)
    from PyQt6.QtSvg import QSvgRenderer
    renderer = QSvgRenderer(data)
    painter = QPainter(px)
    renderer.render(painter)
    painter.end()
    return QIcon(px)

ICONS = {
    "send": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M22 2L11 13M22 2L15 22L11 13M22 2L2 9L11 13" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>''',
    "menu": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
    "clear": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 6H21M8 6V4H16V6M19 6L18 20H6L5 6" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>''',
    "settings": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="3" stroke="#e0e0e0" stroke-width="1.5"/>
        <path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
    "cpu": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="16" height="16" rx="2" stroke="#e0e0e0" stroke-width="1.5"/>
        <rect x="9" y="9" width="6" height="6" stroke="#e0e0e0" stroke-width="1.5"/>
        <path d="M9 2v2M15 2v2M9 20v2M15 20v2M2 9h2M2 15h2M20 9h2M20 15h2" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
    "mic": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2a3 3 0 0 1 3 3v6a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" stroke="#e0e0e0" stroke-width="1.5"/>
        <path d="M19 10a7 7 0 0 1-14 0M12 19v3M8 22h8" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',

    "mic_off": '''<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M15 9.34V5a3 3 0 0 0-5.68-1.33M12 19v3M8 22h8M19 10a7 7 0 0 1-1.2 3.9M5 10a7 7 0 0 0 9.9 6.5M3 3l18 18" stroke="#e0e0e0" stroke-width="1.5" stroke-linecap="round"/>
    </svg>''',
}

# ─── WORKER ───────────────────────────────────────────────────────────────────

class WorkerThread(QThread):
    response_ready = pyqtSignal(str)
    error_ready    = pyqtSignal(str)

    def __init__(self, demetrius, message):
        super().__init__()
        self._demetrius = demetrius
        self._message   = message

    def run(self):
        try:
            from smart_memory import SmartMemory
            from core import Core
            from semantic_memory import SemanticMemory

            mem  = SmartMemory()
            core = Core()
            sem  = SemanticMemory()

            mem.save_memory("user", self._message)
            history = list(mem.stream_history())
            sem.add(self._message)
            context  = sem.search(self._message)
            response = core.think(self._message, history, context)
            mem.save_memory("jarvis", response)
            self.response_ready.emit(response)
        except DemetriusOfflineError:
            self.error_ready.emit("Offline — start Ollama and try again.")
        except Exception as e:
            self.error_ready.emit(str(e))

# ─── SETTINGS DIALOG ──────────────────────────────────────────────────────────

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(340)
        self.setStyleSheet(parent._css() if parent else "")

        layout = QFormLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Font size
        self.font_size = QComboBox()
        self.font_size.addItems(["11", "12", "13", "14", "15", "16"])
        self.font_size.setCurrentText(str(THEME["font_size"]))
        layout.addRow("Font size", self.font_size)

        # Mood
        self.mood = QComboBox()
        self.mood.addItems(["neutral", "excited", "tired"])
        if parent:
            self.mood.setCurrentText(parent.demetrius.get_mood())
        layout.addRow("Mood", self.mood)

        # Accent color
        self.accent_btn = QPushButton("Choose accent color")
        self.accent_btn.clicked.connect(self._pick_color)
        self._accent = THEME["accent"]
        layout.addRow("Accent", self.accent_btn)

        # Buttons
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._accent), self)
        if color.isValid():
            self._accent = color.name()
            self.accent_btn.setStyleSheet(f"background:{self._accent};color:#111;")

# ─── MAIN WINDOW ──────────────────────────────────────────────────────────────

class DemetriusUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Demetrius")
        self.resize(1000, 700)
        self.setMinimumSize(700, 500)
        sec = Security()
        if not sec.authenticate():
            sys.exit(1)

        self.security = sec
        # Boot
        self.memory   = SmartMemory()
        username      = self.memory.load_user() or "Luiz"
        self.memory.save_user(username)
        self.demetrius = Demetrius(username)
        self.auto      = Automation()
        self.username  = username

        self._apply_theme()
        self._build()
        self._post("Demetrius", f"Hello, {username}.", "assistant")
        self._post("System", "Type a message or use the menu.", "system")
    
    def _feedback_good(self):
        if hasattr(self, '_DemetriusUI__last_response'):
            self.demetrius.personality.add_feedback("", self.__last_response, 1)
            self._post("System", "Feedback saved — good response.", "system")

    def _feedback_bad(self):
        if hasattr(self, '_DemetriusUI__last_response'):
            self.demetrius.personality.add_feedback("", self.__last_response, -1)
            self._post("System", "Feedback saved — bad response.", "system")

    # ── BUILD ─────────────────────────────────────────────────────────────────

    def _build(self):
        root = QWidget()
        self.setCentralWidget(root)
        v = QVBoxLayout(root)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        v.addWidget(self._make_topbar())
        v.addWidget(self._make_chat(), stretch=1)
        v.addWidget(self._make_input())

    def _make_topbar(self):
        bar = QFrame()
        bar.setFixedHeight(52)
        bar.setObjectName("topbar")
        h = QHBoxLayout(bar)
        h.setContentsMargins(20, 0, 12, 0)
        h.setSpacing(8)

        # Title
        title = QLabel("Demetrius")
        title.setObjectName("title")
        title.setFont(QFont(THEME["font"], 14, QFont.Weight.Medium))
        h.addWidget(title)

        # Status dot
        self.status_dot = QLabel("·")
        self.status_dot.setObjectName("dot_online")
        self.status_dot.setFont(QFont(THEME["font"], 22))
        h.addWidget(self.status_dot)

        h.addStretch()

        # Mood label
        self.mood_label = QLabel("neutral")
        self.mood_label.setObjectName("dim")
        h.addWidget(self.mood_label)

        # Sysinfo button
        si_btn = self._icon_btn(ICONS["cpu"], self._sysinfo)
        h.addWidget(si_btn)

        # Clear button
        cl_btn = self._icon_btn(ICONS["clear"], self._clear)
        h.addWidget(cl_btn)

        # Settings / menu
        st_btn = self._icon_btn(ICONS["settings"], self._open_settings)
        h.addWidget(st_btn)

        # Hamburger menu
        mn_btn = self._icon_btn(ICONS["menu"], self._open_menu)
        h.addWidget(mn_btn)

        return bar

    def _make_chat(self):
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setObjectName("chat")
        self.chat.setFont(QFont(THEME["font"], THEME["font_size"]))
        self.chat.document().setDocumentMargin(28)
        return self.chat

    def _make_input(self):
        frame = QFrame()
        frame.setObjectName("inputbar")
        frame.setFixedHeight(64)
        h = QHBoxLayout(frame)
        h.setContentsMargins(20, 12, 12, 12)
        h.setSpacing(10)

        self.input = QLineEdit()
        self.input.setObjectName("input")
        self.input.setPlaceholderText("Message Demetrius...")
        self.input.setFont(QFont(THEME["font"], THEME["font_size"]))
        self.input.returnPressed.connect(self._send)
        h.addWidget(self.input)

        # Mic button
        self.mic_btn = QPushButton()
        self.mic_btn.setObjectName("iconbtn")
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.setIcon(svg_icon(ICONS["mic"], 18))
        self.mic_btn.setIconSize(QSize(18, 18))
        self.mic_btn.setCheckable(True)
        self.mic_btn.clicked.connect(self._toggle_listen)
        h.addWidget(self.mic_btn)

        # Send button
        send = QPushButton()
        send.setObjectName("send")
        send.setFixedSize(40, 40)
        send.setIcon(svg_icon(ICONS["send"], 18))
        send.setIconSize(QSize(18, 18))
        send.clicked.connect(self._send)
        h.addWidget(send)

        return frame

    def _icon_btn(self, svg, callback):
        btn = QPushButton()
        btn.setObjectName("iconbtn")
        btn.setFixedSize(36, 36)
        btn.setIcon(svg_icon(svg, 16))
        btn.setIconSize(QSize(16, 16))
        btn.clicked.connect(callback)
        return btn

    # ── ACTIONS ───────────────────────────────────────────────────────────────
    
    def _view_logs(self):
        import glob
        logs = glob.glob("logs/*.log")
        if logs:
            with open(logs[-1]) as f:
                content = f.read()[-2000:]
            self._post("System", content, "system")
        else:
            self._post("System", "No logs found.", "system")
    
    def _toggle_listen(self):
        self._post("System", "Listening... (5 seconds)", "system")

        def _listen_thread():
            text = self.demetrius.voice.listen(duration=5)
            if text:
                self.input.setText(text)
                self._send()
            else:
                self._post("System", "Could not hear anything.", "system")
            self.mic_btn.setChecked(False)

        from PyQt6.QtCore import QThread, pyqtSignal

        class ListenThread(QThread):
            done = pyqtSignal(str)
            def run(self):
                text = self.parent().demetrius.voice.listen(duration=5)
                self.done.emit(text or "")

        self.listen_thread = ListenThread(self)
        self.listen_thread.done.connect(self._on_listen_done)
        self.listen_thread.start()

    def _on_listen_done(self, text):
        self.mic_btn.setChecked(False)
        if text:
            self.input.setText(text)
            self._send()
        else:
            self._post("System", "Could not hear anything.", "system")

    def _send(self):
        msg = self.input.text().strip()
        if not msg:
            return
        self.input.clear()
        self._post(self.username, msg, "user")
        self._handle(msg)

    def _handle(self, msg):
        m = msg.lower().strip()

        if m == "!clear":
            self._clear()
        elif m == "!history":
            rows = self.demetrius.memory.load_history()
            for role, content, ts in reversed(rows):
                self._post(role.capitalize(), content, role)
        elif m == "!stats":
            u = len(self.demetrius.memory.load_user_messages())
            d = len(self.demetrius.memory.load_jarvis_messages())
            self._post("System", f"{u} messages from you · {d} replies from Demetrius", "system")
        elif m == "!sysinfo":
            self._sysinfo()
        elif m == "!backup":
            self._post("System", self.auto.backup(), "system")
        elif m.startswith("!ls"):
            path = msg[3:].strip() or "."
            self._post("System", self.auto.list_files(path), "system")
        elif m.startswith("!mkdir "):
            self._post("System", self.auto.make_dir(msg[7:].strip()), "system")
        elif m.startswith("!find "):
            self._post("System", self.auto.find_file(msg[6:].strip()), "system")
        elif m.startswith("!open "):
            self._post("System", self.auto.open_app(msg[6:].strip()), "system")
        elif m.startswith("!run "):
            self._post("System", self.auto.run_script(msg[5:].strip()), "system")
        elif m.startswith("!mood "):
            mood = msg.split(" ")[1]
            try:
                self.demetrius.set_mood(mood)
                self.mood_label.setText(mood)
                self._post("System", f"Mood → {mood}", "system")
            except Exception as e:
                self._post("System", str(e), "error")
        elif m == "!help":
            self._post("System", self._help_text(), "system")
        
        elif m == "!good":
            self._feedback_good()
        elif m == "!bad":
            self._feedback_bad()
        elif m == "!profile":
            profile = self.demetrius.personality.get_profile()
            interests = ", ".join(profile["interests"]) or "none yet"
            vocab     = ", ".join(profile["vocabulary"]) or "none yet"
            self._post("System", f"Interests: {interests}\nVocabulary: {vocab}", "system")
            
        elif m == "!emails":
            if not hasattr(self, "google"):
                from integrations import GoogleIntegration
                self.google = GoogleIntegration()
            emails = self.google.get_emails()
            if not emails:
                self._post("System", "No unread emails.", "system")
            else:
                for e in emails:
                    self._post("System", f"From: {e['from']}\nSubject: {e['subject']}\n{e['snippet']}", "system")

        elif m == "!events":
            if not hasattr(self, "google"):
                from integrations import GoogleIntegration
                self.google = GoogleIntegration()
            events = self.google.get_events()
            if not events:
                self._post("System", "No upcoming events.", "system")
            else:
                for e in events:
                    start = e["start"].get("dateTime", e["start"].get("date"))
                    self._post("System", f"{e['summary']} — {start}", "system")

        elif m == "!tasks":
            if not hasattr(self, "google"):
                from integrations import GoogleIntegration
                self.google = GoogleIntegration()
            tasks = self.google.get_tasks()
            if not tasks:
                self._post("System", "No pending tasks.", "system")
            else:
                for t in tasks:
                    self._post("System", f"[ ] {t['title']} — {t['due']}", "system")

        elif m == "!drive":
            if not hasattr(self, "google"):
                from integrations import GoogleIntegration
                self.google = GoogleIntegration()
            files = self.google.list_drive_files()
            if not files:
                self._post("System", "No files found.", "system")
            else:
                for f in files:
                    self._post("System", f"{f['name']} — {f['mimeType']}", "system")
            
        else:
            self._post("System", "...", "system")
            self.worker = WorkerThread(self.demetrius, msg)
            self.worker.response_ready.connect(lambda r: self._post("Demetrius", r, "assistant"))
            self.worker.error_ready.connect(lambda e: self._post("Error", e, "error"))
            self.worker.start()

    def _clear(self):
        self.demetrius.memory.clear_history()
        self.chat.clear()
        self._post("System", "Memory cleared.", "system")

    def _sysinfo(self):
        self._post("System", self.auto.sysinfo(), "system")

    def _open_settings(self):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QComboBox, QDialogButtonBox, QLineEdit, QLabel
        from model_manager import ModelManager

        mgr = ModelManager()
        cfg = mgr.load_config()

        dlg = QDialog(self)
        dlg.setWindowTitle("Settings")
        dlg.setMinimumWidth(380)
        dlg.setStyleSheet(self._css())

        layout = QFormLayout(dlg)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Provider
        provider_box = QComboBox()
        provider_box.addItems(["ollama", "openai", "anthropic", "groq"])
        provider_box.setCurrentText(cfg["provider"])
        layout.addRow("Provider", provider_box)

        # Model
        model_box = QComboBox()
        def update_models():
            model_box.clear()
            p = provider_box.currentText()
            if p == "ollama":
                model_box.addItems(mgr.list_ollama_models())
            else:
                model_box.addItems(mgr.list_api_models(p))
            model_box.setCurrentText(cfg["model"])
        provider_box.currentTextChanged.connect(update_models)
        update_models()
        layout.addRow("Model", model_box)

        # API Key
        key_field = QLineEdit()
        key_field.setEchoMode(QLineEdit.EchoMode.Password)
        key_field.setPlaceholderText("Leave empty for Ollama")
        key_field.setText(cfg["api_key"])
        layout.addRow("API Key", key_field)

        # Font size
        font_box = QComboBox()
        font_box.addItems(["11", "12", "13", "14", "15", "16"])
        font_box.setCurrentText(str(THEME["font_size"]))
        layout.addRow("Font size", font_box)

        # Mood
        mood_box = QComboBox()
        mood_box.addItems(["neutral", "excited", "tired"])
        mood_box.setCurrentText(self.demetrius.get_mood())
        layout.addRow("Mood", mood_box)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addRow(btns)

        if dlg.exec():
            provider = provider_box.currentText()
            model    = model_box.currentText()
            api_key  = key_field.text()

            mgr.save_config(provider, model, api_key)

            from core import Core
            self.demetrius.core = Core(provider=provider, model=model, api_key=api_key)

            THEME["font_size"] = int(font_box.currentText())
            try:
                self.demetrius.set_mood(mood_box.currentText())
                self.mood_label.setText(mood_box.currentText())
            except:
                pass

            self._apply_theme()
            self._post("System", f"Model → {provider} / {model}", "system")

    def _open_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(self._css())
        menu.addAction("System Info",     self._sysinfo)
        menu.addAction("Clear Memory",    self._clear)
        menu.addAction("Backup Database", lambda: self._post("System", self.auto.backup(), "system"))
        menu.addAction("Stats",           lambda: self._handle("!stats"))
        menu.addAction("History",         lambda: self._handle("!history"))
        menu.addSeparator()
        menu.addAction("Settings",        self._open_settings)
        menu.exec(self.mapToGlobal(self.rect().topRight()))
        menu.addAction("Encrypted Backup", lambda: self._post("System", str(self.security.backup(encrypt=True)), "system"))
        menu.addAction("View Logs",        self._view_logs)
        
    def _help_text(self):
        return (
            "!clear · !history · !stats · !backup · !sysinfo · !logs\n"
            "!open [app] · !run [script] · !ls [path]\n"
            "!mkdir [name] · !find [file] · !mood [neutral|excited|tired]\n"
            "!good · !bad · !profile\n"
            "!emails · !events · !tasks · !drive"
    )
    # ── POSTS ─────────────────────────────────────────────────────────────────

    def _post(self, sender, text, role):
        colors = {
            "user":      THEME["user"],
            "assistant": THEME["assistant"],
            "system":    THEME["system"],
            "error":     THEME["error"],
            "jarvis":    THEME["assistant"],
        }
        c    = colors.get(role, THEME["text"])
        safe = (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace("\n", "<br>"))

        if role == "user":
            html = (f'<p style="margin:14px 0 2px 0;color:{THEME["text_dim"]};font-size:11px;">{sender}</p>'
                    f'<p style="margin:0 0 14px 0;color:{c};">{safe}</p>')
        elif role in ("assistant", "jarvis"):
            html = (f'<p style="margin:14px 0 2px 0;color:{THEME["text_dim"]};font-size:11px;">Demetrius '
                    f'<span style="color:#333;cursor:pointer;" title="Good response" '
                    f'onclick="void(0)">+</span> '
                    f'<span style="color:#333;cursor:pointer;" title="Bad response" '
                    f'onclick="void(0)">−</span></p>'
                    f'<p style="margin:0 0 14px 0;color:{c};">{safe}</p>')
            self.__last_response = text
        else:
            html = f'<p style="margin:6px 0;color:{c};font-size:11px;">{safe}</p>'

        self.chat.append(html)
        sb = self.chat.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ── THEME ─────────────────────────────────────────────────────────────────

    def _apply_theme(self):
        self.setStyleSheet(self._css())

    def _css(self):
        t = THEME
        return f"""
        QMainWindow, QWidget {{
            background: {t['bg']};
            color: {t['text']};
            font-family: {t['font']};
        }}
        #topbar {{
            background: {t['bg2']};
            border-bottom: 1px solid {t['border']};
        }}
        #title {{
            color: {t['text']};
            letter-spacing: 0.5px;
        }}
        #dot_online {{
            color: #4caf50;
        }}
        #dim {{
            color: {t['text_dim']};
            font-size: 11px;
        }}
        #chat {{
            background: {t['bg']};
            border: none;
            color: {t['text']};
            selection-background-color: {t['border']};
        }}
        #inputbar {{
            background: {t['bg2']};
            border-top: 1px solid {t['border']};
        }}
        #input {{
            background: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 8px;
            padding: 8px 14px;
            font-size: {t['font_size']}px;
        }}
        #input:focus {{
            border: 1px solid #444;
        }}
        #send {{
            background: {t['bg3']};
            border: 1px solid {t['border']};
            border-radius: 8px;
        }}
        #send:hover {{
            background: #2a2a2a;
            border: 1px solid #444;
        }}
        #iconbtn {{
            background: transparent;
            border: none;
            border-radius: 6px;
        }}
        #iconbtn:hover {{
            background: {t['bg3']};
        }}
        QMenu {{
            background: {t['bg2']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 8px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background: {t['bg3']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {t['border']};
            margin: 4px 8px;
        }}
        QDialog {{
            background: {t['bg2']};
        }}
        QComboBox {{
            background: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 6px 10px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background: {t['bg2']};
            color: {t['text']};
            border: 1px solid {t['border']};
            selection-background-color: {t['bg3']};
        }}
        QPushButton {{
            background: {t['bg3']};
            color: {t['text']};
            border: 1px solid {t['border']};
            border-radius: 6px;
            padding: 8px 16px;
        }}
        QPushButton:hover {{
            background: #2a2a2a;
        }}
        QScrollBar:vertical {{
            background: {t['bg']};
            width: 4px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background: {t['border']};
            border-radius: 2px;
        }}
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        QLabel {{
            color: {t['text']};
        }}
        """

# ─── RUN ──────────────────────────────────────────────────────────────────────

def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = DemetriusUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()