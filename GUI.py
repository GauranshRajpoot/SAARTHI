# ✅ Updated GUI Code with Fixes

import os
import sys
from dotenv import dotenv_values
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QVBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QHBoxLayout
)
from PyQt5.QtGui import (
    QIcon, QPainter, QMovie, QColor, QTextCharFormat,
    QFont, QPixmap, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QSize, QTimer

# ========== ENVIRONMENT SETUP ==========
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

# ========== PATH SETUP ==========
current_dir = os.getcwd()
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

def GraphicsDirectoryPath(filename):
    return os.path.join(GraphicsDirPath, filename)

def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)

# ========== TEXT MODIFIERS ==========
def AnswerModifier(answer: str) -> str:
    lines = answer.split("\n")
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query: str) -> str:
    query = query.strip().lower()
    question_words = [
        "how", "what", "who", "where", "when", "why",
        "which", "whose", "whom", "can you", "what's", "where's", "how's"
    ]
    if any(word + " " in query for word in question_words):
        query = query.rstrip('.?!') + "?"
    else:
        query = query.rstrip('.?!') + "."
    return query.capitalize()

# ========== FILE OPERATIONS ==========
def write_to_file(path: str, text: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def read_from_file(path: str, default="") -> str:
    if not os.path.exists(path):
        write_to_file(path, default)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

# ========== MIC & ASSISTANT STATUS ==========
def SetMicrophoneStatus(command: str):
    write_to_file(TempDirectoryPath("Mic.data"), command)

def GetMicrophoneStatus() -> str:
    return read_from_file(TempDirectoryPath("Mic.data"), "False")

def SetAssistantStatus(status: str):
    write_to_file(TempDirectoryPath("Status.data"), status)

def GetAssistantStatus() -> str:
    return read_from_file(TempDirectoryPath("Status.data"), "Ready")

def MicButtonInitialed():
    SetMicrophoneStatus("True")  # ON

def MicButtonClosed():
    SetMicrophoneStatus("False")  # OFF

# ========== OUTPUT DISPLAY ==========
def ShowTextToScreen(text: str):
    write_to_file(TempDirectoryPath("Responses.data"), text)

# ========== CHAT SECTION ==========
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        self.old_chat_message = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(10)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        self.chat_text_edit.setFont(QFont("", 13))

        self.gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        self.gif_label.setStyleSheet("border: none; background-color: black;")
        layout.addWidget(self.gif_label)

        self.lable = QLabel("")
        self.lable.setStyleSheet("color:white;font-size:16px;margin-right:195px;border:none;margin-top:-30px; background-color: black;")
        self.lable.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lable)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadmessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(1000)  # ✅ Increased interval

    def loadmessages(self):
        file_path = TempDirectoryPath("Responses.data")
        if not os.path.exists(file_path): return
        with open(file_path, "r", encoding='utf-8') as file:
            messages = file.read()
            if messages and self.old_chat_message != messages:
                self.addMessage(messages, 'white')
                self.old_chat_message = messages

    def SpeechRecogText(self):
        file_path = TempDirectoryPath("Status.data")
        if os.path.exists(file_path):
            new_status = read_from_file(file_path)
            if self.lable.text() != new_status:
                self.lable.setText(new_status)

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

# ========== OTHER UI COMPONENTS ==========
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        screen_width = rect.width()
        screen_height = rect.height()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 150)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        movie.setScaledSize(QSize(screen_width, int(screen_width / 21 * 9.5)))
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setStyleSheet("background-color: black;")

        self.label = QLabel(" ")
        self.label.setStyleSheet("color: white; font-size: 16px; background-color: black;")

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath("Mic_on.png"))
        self.icon_label.setPixmap(pixmap.scaled(60, 60))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(150, 150)
        self.toggled = False  # Start with OFF
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        layout.addWidget(gif_label)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(1000)

    def SpeechRecogText(self):
        file_path = TempDirectoryPath("Status.data")
        if os.path.exists(file_path):
            new_status = read_from_file(file_path)
            if self.label.text() != new_status:
                self.label.setText(new_status)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_off.png")).scaled(60, 60))
            MicButtonClosed()
        else:
            self.icon_label.setPixmap(QPixmap(GraphicsDirectoryPath("Mic_on.png")).scaled(60, 60))
            MicButtonInitialed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))  # Spacer
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.maximized = False
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        title_label = QLabel(f"{Assistantname} AI")
        title_label.setStyleSheet("color: white; font-size: 18px; background-color: black")

        def add_btn(icon_name, callback):
            btn = QPushButton()
            btn.setIcon(QIcon(GraphicsDirectoryPath(icon_name)))
            btn.clicked.connect(callback)
            btn.setStyleSheet("background-color: #222; color: white; border: none;")
            btn.setFixedSize(35, 35)
            return btn

        home_btn = QPushButton(" Home")
        home_btn.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        home_btn.setStyleSheet("color: white; background-color: #222; border: none;")

        msg_btn = QPushButton(" Chat")
        msg_btn.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        msg_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        msg_btn.setStyleSheet("color: white; background-color: #222; border: none;")

        minimize_btn = add_btn("Minimize2.png", self.parent().showMinimized)
        self.maximize_btn = add_btn("Maximize.png", self.toggleMaximize)
        close_btn = add_btn("Close.png", self.parent().close)

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_btn)
        layout.addWidget(msg_btn)
        layout.addWidget(minimize_btn)
        layout.addWidget(self.maximize_btn)
        layout.addWidget(close_btn)

        self.setStyleSheet("background-color: black;")

    def toggleMaximize(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black; color: white;")

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(InitialScreen())
        self.stacked_widget.addWidget(MessageScreen())
        self.setCentralWidget(self.stacked_widget)
        self.setMenuWidget(CustomTopBar(self, self.stacked_widget))

        screen = QApplication.primaryScreen()
        rect = screen.availableGeometry()
        self.setGeometry(0, 0, rect.width(), rect.height())

    def closeEvent(self, event):
        SetAssistantStatus("Terminated")
        SetMicrophoneStatus("False")
        event.accept()

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { background-color: black; color: white; }")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()


