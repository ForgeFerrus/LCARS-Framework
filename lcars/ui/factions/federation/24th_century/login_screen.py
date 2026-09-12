"""
Federation 24th Century Login Screen
Classic LCARS Interface - TNG/DS9/VOY Era
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import random
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class LCARSButton(QPushButton):
    """Classic LCARS rounded button"""
    def __init__(self, text="", color="#FFCC66", parent=None):
        super().__init__(text, parent)
        self.lcars_color = color
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)
        
        # LCARS color
        bg_color = QColor(self.lcars_color)
        if self.underMouse():
            bg_color = bg_color.lighter(110)
        if self.isDown():
            bg_color = bg_color.darker(110)
            
        # Draw classic LCARS pill shape
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(rect), 20, 20)
        
        # Draw text
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Antonio", 14, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class Federation24thLogin(QMainWindow):
    """24th Century Federation Login Screen - Classic LCARS Style"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_lcars_interface()
        
        # LCARS color update timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_lcars_colors)
        self.color_timer.start(2500)  # Every 2.5 seconds
        
    def setup_lcars_interface(self):
        """Setup Classic LCARS interface"""
        self.setWindowTitle("LCARS Interface - 24th Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Classic LCARS colors
        self.lcars_colors = {
            'background': '#000000',    # Black
            'text': '#FFFFFF',          # White
            'primary': '#FFCC66',       # Classic LCARS Orange
            'secondary': '#FF9900',     # Darker Orange
            'tertiary': '#CC6666',      # Red
            'quaternary': '#664466',    # Purple
            'accent': '#66CCFF',        # Blue
            'panel': '#333333',         # Dark Grey
        }
        
        # Apply Classic LCARS styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.lcars_colors['background']};
                border: none;
            }}
            QLabel {{
                color: {self.lcars_colors['text']};
                font-family: 'Antonio', 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: rgba(0, 0, 0, 0.8);
                border: 3px solid {self.lcars_colors['primary']};
                color: {self.lcars_colors['text']};
                font-family: 'Antonio', 'Arial', sans-serif;
                font-size: 18px;
                padding: 12px;
                border-radius: 10px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # LCARS Header with classic layout
        header_frame = QFrame()
        header_frame.setFixedHeight(140)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.lcars_colors['background']};
                border-bottom: 5px solid {self.lcars_colors['primary']};
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Classic LCARS title
        title_label = QLabel("LCARS ACCESS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {self.lcars_colors['primary']};
            padding: 25px;
        """)
        
        subtitle_label = QLabel("STARFLEET COMMAND INTERFACE")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.lcars_colors['secondary']};
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(30)
        auth_layout.setContentsMargins(150, 50, 150, 50)
        
        # Authorization field
        auth_label = QLabel("AUTHORIZATION REQUIRED:")
        auth_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {self.lcars_colors['primary']};
            margin-bottom: 15px;
        """)
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.auth_field = QLineEdit()
        self.auth_field.setPlaceholderText("Enter Starfleet credentials...")
        self.auth_field.setFixedHeight(50)
        
        # Classic LCARS buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(25)
        
        self.lcars_buttons = []
        lcars_commands = [
            ("ACCESS MAIN", "#FFCC66"),
            ("SECURITY", "#FF9900"),
            ("EMERGENCY", "#CC6666"),
            ("COMMAND", "#66CCFF")
        ]
        
        for text, color in lcars_commands:
            btn = LCARSButton(text, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(220, 60)
            self.lcars_buttons.append(btn)
            button_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_field)
        auth_layout.addWidget(button_frame)
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def update_lcars_colors(self):
        """Update classic LCARS button colors"""
        classic_colors = ["#FFCC66", "#FF9900", "#CC6666", "#664466", "#66CCFF", "#99CC99"]
        
        for btn in self.lcars_buttons:
            btn.lcars_color = random.choice(classic_colors)
            btn.update()
            
    def authenticate(self):
        """Handle LCARS authentication"""
        print("✅ LCARS 24th Century authentication successful!")
        self.authentication_success.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation24thLogin()
    login.show()
    sys.exit(app.exec())
