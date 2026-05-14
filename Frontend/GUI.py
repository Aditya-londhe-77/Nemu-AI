from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
    QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, 
    QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtGui import (QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, 
    QPixmap, QTextBlockFormat, QLinearGradient, QBrush, QPen, QRadialGradient,
    QPainterPath, QFontDatabase)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, pyqtProperty, QPoint
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Nemu")
current_dir = os.getcwd()

old_chat_message = ""

TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirpath = rf"{current_dir}\Frontend\Graphics"

# ── Color Palette ──
COLORS = {
    "bg_dark": "#0a0a12",
    "bg_card": "#12121f",
    "bg_glass": "rgba(18, 18, 35, 0.7)",
    "accent_cyan": "#00d4ff",
    "accent_purple": "#7b2ff7",
    "accent_pink": "#ff2d95",
    "text_primary": "#e8eaf0",
    "text_secondary": "#8890a4",
    "text_dim": "#4a5068",
    "border_subtle": "#1e1e3a",
    "user_bubble": "#1a2a4a",
    "bot_bubble": "#1a1a30",
    "danger": "#ff4757",
    "success": "#00e676",
}

STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLORS['bg_dark']};
    }}
    QWidget#centralContainer {{
        background-color: {COLORS['bg_dark']};
    }}
"""

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(query):
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?']:
            new_query = new_query[:-1]
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf"{TempDirPath}\Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf"{TempDirPath}\Mic.data", "r", encoding="utf-8") as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as file:
        return file.read()

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return rf"{GraphicsDirpath}\{Filename}"

def TempDirectoryPath(Filename):
    return rf"{TempDirPath}\{Filename}"

def ShowTextToScreen(Text):
    with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as file:
        file.write(Text)


class GlowingMicButton(QWidget):
    """Circular mic button with pulsing glow animation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)
        self.setCursor(Qt.PointingHandCursor)
        self.toggled = True
        self._glow_radius = 0
        self._is_active = False
        
        self.glow_anim = QPropertyAnimation(self, b"glowRadius")
        self.glow_anim.setDuration(1200)
        self.glow_anim.setStartValue(0)
        self.glow_anim.setEndValue(20)
        self.glow_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.glow_anim.setLoopCount(-1)
        self.glow_anim.finished.connect(lambda: None)
        
        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse_toggle)
        
    def _pulse_toggle(self):
        if self.glow_anim.direction() == QPropertyAnimation.Forward:
            self.glow_anim.setDirection(QPropertyAnimation.Backward)
        else:
            self.glow_anim.setDirection(QPropertyAnimation.Forward)
        self.glow_anim.start()

    @pyqtProperty(int)
    def glowRadius(self):
        return self._glow_radius
    
    @glowRadius.setter
    def glowRadius(self, value):
        self._glow_radius = value
        self.update()

    def mousePressEvent(self, event):
        if self.toggled:
            MicButtonInitialed()
            self._is_active = False
            self.glow_anim.stop()
            self._glow_radius = 0
            self.pulse_timer.stop()
        else:
            MicButtonClosed()
            self._is_active = True
            self.glow_anim.setDirection(QPropertyAnimation.Forward)
            self.glow_anim.start()
            self.pulse_timer.start(2400)
        self.toggled = not self.toggled
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center = self.rect().center()
        radius = 38
        
        # Outer glow
        if self._is_active:
            glow_color = QColor(COLORS["danger"])
            for i in range(self._glow_radius, 0, -2):
                glow_color.setAlpha(max(0, 40 - i * 2))
                painter.setPen(Qt.NoPen)
                painter.setBrush(glow_color)
                painter.drawEllipse(center, radius + i, radius + i)
        
        # Main circle with gradient
        grad = QRadialGradient(center.x(), center.y() - 10, radius)
        if self._is_active:
            grad.setColorAt(0, QColor("#ff4757"))
            grad.setColorAt(1, QColor("#c0392b"))
        else:
            grad.setColorAt(0, QColor("#00d4ff"))
            grad.setColorAt(1, QColor("#0099cc"))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(grad))
        painter.drawEllipse(center, radius, radius)
        
        # Inner highlight
        highlight = QRadialGradient(center.x() - 8, center.y() - 12, radius // 2)
        highlight.setColorAt(0, QColor(255, 255, 255, 60))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(center, radius - 2, radius - 2)
        
        # Mic icon (draw simple mic shape)
        painter.setPen(QPen(QColor("white"), 2.5))
        painter.setBrush(Qt.NoBrush)
        mic_x = center.x()
        mic_y = center.y()
        
        # Mic body
        mic_rect = QRect(mic_x - 6, mic_y - 14, 12, 20)
        painter.drawRoundedRect(mic_rect, 6, 6)
        
        # Mic arc
        arc_rect = QRect(mic_x - 12, mic_y - 10, 24, 24)
        painter.drawArc(arc_rect, -30 * 16, -120 * 16)
        
        # Mic stand
        painter.drawLine(mic_x, mic_y + 12, mic_x, mic_y + 18)
        painter.drawLine(mic_x - 6, mic_y + 18, mic_x + 6, mic_y + 18)
        
        painter.end()


class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setFont(QFont("Segoe UI", 11))
        
        self.chat_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                color: {COLORS['text_primary']};
                border: none;
                padding: 10px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['bg_dark']};
                width: 6px;
                margin: 0;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 {COLORS['accent_cyan']}, stop:1 {COLORS['accent_purple']});
                min-height: 30px;
                border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """)
        
        layout.addWidget(self.chat_text_edit)
        
        # Bottom section: GIF + status
        bottom = QVBoxLayout()
        bottom.setSpacing(8)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; background: transparent;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(360, 200))
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setMovie(movie)
        movie.start()
        bottom.addWidget(self.gif_label, alignment=Qt.AlignCenter)
        
        self.label = QLabel("")
        self.label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']}; 
            font-size: 14px; 
            font-weight: 500;
            font-family: 'Segoe UI';
            background: transparent;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        bottom.addWidget(self.label)
        
        layout.addLayout(bottom)
        
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            if not messages or len(messages) < 1 or str(old_chat_message) == str(messages):
                pass
            else:
                self.addMessage(message=messages, color=COLORS['text_primary'])
                old_chat_message = messages
        except:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            self.label.setText(messages)
        except:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(8)
        block_fmt.setLeftMargin(15)
        fmt.setForeground(QColor(color))
        fmt.setFont(QFont("Segoe UI", 11))
        cursor.setCharFormat(fmt)
        cursor.setBlockFormat(block_fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Spacer top
        layout.addStretch(1)
        
        # Title
        title = QLabel(f"{Assistantname.upper()} AI")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28px;
            font-weight: 700;
            font-family: 'Segoe UI';
            letter-spacing: 8px;
            background: transparent;
            padding: 10px;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Your Intelligent Desktop Assistant")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 13px;
            font-family: 'Segoe UI';
            letter-spacing: 3px;
            background: transparent;
            margin-bottom: 20px;
        """)
        layout.addWidget(subtitle)
        
        # GIF container with glow
        gif_container = QWidget()
        gif_container.setStyleSheet("background: transparent;")
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setAlignment(Qt.AlignCenter)
        
        gif_label = QLabel()
        gif_label.setStyleSheet(f"""
            border: 2px solid {COLORS['border_subtle']};
            border-radius: 20px;
            background: transparent;
            padding: 5px;
        """)
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        
        desktop = QApplication.desktop()
        sw = desktop.screenGeometry().width()
        gif_w = min(int(sw * 0.5), 700)
        gif_h = int(gif_w * 9 / 16)
        movie.setScaledSize(QSize(gif_w, gif_h))
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setMovie(movie)
        movie.start()
        
        # Glow effect on GIF
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(40)
        glow.setColor(QColor(COLORS['accent_cyan']))
        glow.setOffset(0, 0)
        gif_label.setGraphicsEffect(glow)
        
        gif_layout.addWidget(gif_label)
        layout.addWidget(gif_container)
        
        layout.addStretch(1)
        
        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            font-size: 15px;
            font-family: 'Segoe UI';
            font-weight: 500;
            background: transparent;
            padding: 5px;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        # Mic button
        self.mic_button = GlowingMicButton()
        layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        # Bottom hint
        hint = QLabel("Tap the mic to start speaking")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"""
            color: {COLORS['text_dim']};
            font-size: 11px;
            font-family: 'Segoe UI';
            background: transparent;
            margin-top: 8px;
            margin-bottom: 40px;
        """)
        layout.addWidget(hint)
        
        layout.addStretch(1)
        
        # Status timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            self.label.setText(messages)
        except:
            pass


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Gradient accent line at top
        accent_line = QFrame()
        accent_line.setFixedHeight(2)
        accent_line.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {COLORS['accent_cyan']}, 
                stop:0.5 {COLORS['accent_purple']}, 
                stop:1 {COLORS['accent_pink']});
        """)
        layout.addWidget(accent_line)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.parent_window = parent
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(52)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        # Title with gradient-like appearance
        title_label = QLabel(f"  {str(Assistantname).capitalize()} AI")
        title_label.setStyleSheet(f"""
            color: {COLORS['accent_cyan']};
            font-size: 16px;
            font-weight: 700;
            font-family: 'Segoe UI';
            letter-spacing: 2px;
            background: transparent;
        """)
        layout.addWidget(title_label)
        layout.addStretch(1)

        # Nav buttons
        nav_style = f"""
            QPushButton {{
                height: 34px;
                padding: 0 18px;
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border_subtle']};
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border_subtle']};
                border-color: {COLORS['accent_cyan']};
                color: {COLORS['accent_cyan']};
            }}
        """

        home_button = QPushButton("⌂  HOME")
        home_button.setStyleSheet(nav_style)
        home_button.setCursor(Qt.PointingHandCursor)
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        chat_button = QPushButton("💬  CHAT")
        chat_button.setStyleSheet(nav_style)
        chat_button.setCursor(Qt.PointingHandCursor)
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(home_button)
        layout.addWidget(chat_button)
        layout.addStretch(1)

        # Window controls
        ctrl_style = f"""
            QPushButton {{
                width: 36px;
                height: 36px;
                background-color: transparent;
                border: none;
                border-radius: 18px;
                font-size: 14px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['border_subtle']};
            }}
        """
        close_hover = f"""
            QPushButton {{
                width: 36px; height: 36px;
                background-color: transparent;
                border: none; border-radius: 18px;
                font-size: 14px;
                color: {COLORS['text_secondary']};
            }}
            QPushButton:hover {{
                background-color: {COLORS['danger']};
                color: white;
            }}
        """

        min_btn = QPushButton("─")
        min_btn.setStyleSheet(ctrl_style)
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.clicked.connect(self.minimizeWindow)

        max_btn = QPushButton("□")
        max_btn.setStyleSheet(ctrl_style)
        max_btn.setCursor(Qt.PointingHandCursor)
        max_btn.clicked.connect(self.maximizeWindow)

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet(close_hover)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.closeWindow)

        layout.addWidget(min_btn)
        layout.addWidget(max_btn)
        layout.addWidget(close_btn)

        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Glassmorphism top bar background
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor(15, 15, 30, 230))
        grad.setColorAt(1, QColor(20, 20, 40, 230))
        painter.fillRect(self.rect(), QBrush(grad))
        
        # Bottom accent line
        accent_grad = QLinearGradient(0, 0, self.width(), 0)
        accent_grad.setColorAt(0, QColor(COLORS['accent_cyan']))
        accent_grad.setColorAt(0.5, QColor(COLORS['accent_purple']))
        accent_grad.setColorAt(1, QColor(COLORS['accent_pink']))
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(accent_grad))
        painter.drawRect(0, self.height() - 2, self.width(), 2)
        
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent_window.showMinimized()

    def maximizeWindow(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def closeWindow(self):
        self.parent_window.close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent_window.move(new_pos)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(STYLESHEET)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        stacked_widget.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
