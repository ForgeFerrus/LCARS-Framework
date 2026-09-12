"""
LCARS Working System - 24th Century Classic LCARS
TNG/DS9/VOY era interface
"""

import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal

# Classic LCARS Palette
LCARS_COLORS = {
    'bg': '#000000',           # LCARS Black
    'lcars_orange': '#FF9900', # LCARS Orange
    'lcars_red': '#CC6666',    # LCARS Red
    'lcars_blue': '#9999FF',   # LCARS Blue
    'lcars_yellow': '#FFFF99', # LCARS Yellow
    'lcars_green': '#99FF99',  # LCARS Green
    'lcars_purple': '#CC99FF', # LCARS Purple
    'text': '#FFFFFF',         # LCARS White Text
    'panel': '#000033'         # Panel Background
}

class LCARSButton(QPushButton):
    """Classic LCARS style button"""
    def __init__(self, text="", color=LCARS_COLORS['lcars_orange'], parent=None):
        super().__init__(text, parent)
        self.base_color = QColor(color)
        self.hovered = False
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # Classic LCARS gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(140))
            gradient.setColorAt(1, self.base_color.darker(120))
        else:
            gradient.setColorAt(0, self.base_color.lighter(110))
            gradient.setColorAt(1, self.base_color.darker(110))
            
        # Draw LCARS rounded rectangle
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.base_color.darker(130), 1))
        painter.drawRoundedRect(QRectF(rect), 25, 25)
        
        # Text
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class LCARS24thDesktop(QMainWindow):
    """Classic 24th Century LCARS Desktop"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS - 24th Century Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LCARS_COLORS['bg']};
                color: {LCARS_COLORS['text']};
            }}
        """)
        
        # Main interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # LCARS Header
        header_panel = QFrame()
        header_panel.setFixedHeight(120)
        header_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {LCARS_COLORS['lcars_orange']}, 
                    stop:1 {LCARS_COLORS['panel']});
                border-bottom: 3px solid {LCARS_COLORS['lcars_orange']};
            }}
        """)
        
        header_layout = QHBoxLayout(header_panel)
        header_layout.setContentsMargins(30, 20, 30, 20)
        
        # LCARS title
        lcars_title = QLabel("LCARS")
        lcars_title.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {LCARS_COLORS['text']};
            background: transparent;
        """)
        header_layout.addWidget(lcars_title)
        
        header_layout.addStretch()
        
        # Stardate
        stardate = QLabel("STARDATE 48315.6")
        stardate.setStyleSheet(f"""
            font-size: 18px;
            color: {LCARS_COLORS['text']};
            background: transparent;
        """)
        header_layout.addWidget(stardate)
        
        layout.addWidget(header_panel)
        
        # Main content
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left LCARS panel
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {LCARS_COLORS['panel']};
                border: 2px solid {LCARS_COLORS['lcars_blue']};
                border-radius: 10px;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(15)
        
        nav_title = QLabel("NAVIGATION")
        nav_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {LCARS_COLORS['lcars_blue']};
            text-align: center;
            padding: 10px;
            background: transparent;
        """)
        nav_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(nav_title)
        
        lcars_functions = [
            ("HELM CONTROL", LCARS_COLORS['lcars_orange']),
            ("TACTICAL", LCARS_COLORS['lcars_red']),
            ("ENGINEERING", LCARS_COLORS['lcars_yellow']),
            ("SCIENCE", LCARS_COLORS['lcars_blue']),
            ("MEDICAL", LCARS_COLORS['lcars_green']),
            ("COMMUNICATIONS", LCARS_COLORS['lcars_purple'])
        ]
        
        for function, color in lcars_functions:
            btn = LCARSButton(function, color)
            btn.setMinimumHeight(50)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        logout_btn = LCARSButton("LCARS LOGOUT", LCARS_COLORS['lcars_red'])
        logout_btn.clicked.connect(self.logout)
        left_layout.addWidget(logout_btn)
        
        content_layout.addWidget(left_panel)
        
        # Center LCARS display
        center_panel = QFrame()
        center_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {LCARS_COLORS['panel']};
                border: 3px solid {LCARS_COLORS['lcars_orange']};
                border-radius: 15px;
            }}
        """)
        
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(50, 50, 50, 50)
        
        center_title = QLabel("LCARS COMPUTER NETWORK")
        center_title.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {LCARS_COLORS['lcars_orange']};
            text-align: center;
            padding: 40px;
        """)
        center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(center_title)
        
        status_label = QLabel("ALL SYSTEMS NOMINAL")
        status_label.setStyleSheet(f"""
            font-size: 28px;
            color: {LCARS_COLORS['lcars_green']};
            text-align: center;
            padding: 20px;
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(status_label)
        
        center_layout.addStretch()
        content_layout.addWidget(center_panel)
        
        layout.addWidget(content_container)
        
        # LCARS Footer
        footer_panel = QFrame()
        footer_panel.setFixedHeight(80)
        footer_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:1, x2:0, y2:0,
                    stop:0 {LCARS_COLORS['lcars_orange']}, 
                    stop:1 {LCARS_COLORS['panel']});
                border-top: 3px solid {LCARS_COLORS['lcars_orange']};
            }}
        """)
        
        footer_layout = QHBoxLayout(footer_panel)
        footer_layout.setContentsMargins(30, 15, 30, 15)
        
        footer_info = QLabel("UNITED FEDERATION OF PLANETS • 24TH CENTURY")
        footer_info.setStyleSheet(f"""
            font-size: 18px;
            color: {LCARS_COLORS['text']};
            background: transparent;
        """)
        footer_layout.addWidget(footer_info)
        
        footer_layout.addStretch()
        
        # Quick controls
        for control, color in [("SHIELDS", LCARS_COLORS['lcars_blue']), ("WEAPONS", LCARS_COLORS['lcars_red'])]:
            btn = LCARSButton(control, color)
            btn.setMinimumHeight(40)
            footer_layout.addWidget(btn)
            
        layout.addWidget(footer_panel)
        
    def logout(self):
        """Return to launcher"""
        self.authentication_success.emit()
        self.close()

class Federation24thLogin(QMainWindow):
    """24th Century Classic LCARS Login"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS - 24th Century Computer Network")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup classic LCARS login"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LCARS_COLORS['bg']};
                color: {LCARS_COLORS['text']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Header
        header = QLabel("THE LCARS COMPUTER NETWORK")
        header.setStyleSheet(f"""
            font-size: 52px;
            font-weight: bold;
            color: {LCARS_COLORS['lcars_orange']};
            text-align: center;
            padding: 30px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("24TH CENTURY • FEDERATION STANDARD")
        subtitle.setStyleSheet(f"""
            font-size: 24px;
            color: {LCARS_COLORS['lcars_blue']};
            text-align: center;
            padding: 10px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        # Access buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(25)
        
        lcars_systems = [
            ("MAIN COMPUTER ACCESS", LCARS_COLORS['lcars_orange']),
            ("TACTICAL SYSTEMS", LCARS_COLORS['lcars_red']),
            ("SCIENCE DATABASE", LCARS_COLORS['lcars_blue']),
            ("ENGINEERING CONTROL", LCARS_COLORS['lcars_yellow'])
        ]
        
        for system, color in lcars_systems:
            btn = LCARSButton(system, color)
            btn.setMinimumSize(450, 80)
            btn.clicked.connect(self.authenticate)
            button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
    def authenticate(self):
        """Launch LCARS desktop"""
        print("✅ LCARS 24th Century authentication successful!")
        QTimer.singleShot(1000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch LCARS desktop"""
        print("🚀 Launching LCARS Desktop...")
        self.desktop = LCARS24thDesktop()
        self.desktop.authentication_success.connect(self.on_desktop_logout)
        self.hide()
        self.desktop.show()
        
    def on_desktop_logout(self):
        """Handle desktop logout"""
        self.desktop = None
        self.authentication_success.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation24thLogin()
    login.show()
    sys.exit(app.exec())