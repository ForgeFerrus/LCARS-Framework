"""
Federation 29th Century Login Screen
Based on USS Relativity TCARS Interface
Temporal Operations Command
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import random
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Relativity Palette
REL_COLORS = {
    'bg': '#000000',           # Space Black
    'teal_bright': '#00FFFF',  # Active Cyan
    'teal_mid': '#0099CC',     # Standard Teal
    'teal_dark': '#004C66',    # Deep Teal
    'grey_light': '#A0A0A0',   # Metallic Grey
    'grey_dark': '#404040',    # Structural Grey
    'alert': '#FFCC00',        # Temporal Alert
    'text': '#E0FFFF'          # Pale Cyan Text
}

class RelativityButton(QPushButton):
    """29th Century Relativity-style button"""
    def __init__(self, text="", color=REL_COLORS['teal_mid'], parent=None):
        super().__init__(text, parent)
        self.base_color = QColor(color)
        self.hovered = False
        self.setFixedHeight(35)
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
        
        # Gradient effect for 29th century
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(150))
            gradient.setColorAt(1, self.base_color)
        else:
            gradient.setColorAt(0, self.base_color)
            gradient.setColorAt(1, self.base_color.darker(120))
            
        # Draw rounded pill shape
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(REL_COLORS['teal_bright']), 1))
        painter.drawRoundedRect(QRectF(rect), 15, 15)
        
        # Draw text
        painter.setPen(QColor("#000000" if not self.hovered else "#FFFFFF"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class Federation29thLogin(QMainWindow):
    """29th Century Federation Login Screen - USS Relativity Style"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_relativity_interface()
        
        # Temporal color update timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_temporal_colors)
        self.color_timer.start(2000)  # Every 2 seconds for temporal feel
        
    def setup_relativity_interface(self):
        """Setup USS Relativity temporal interface"""
        self.setWindowTitle("USS Relativity - Temporal Operations Command")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Apply Relativity styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {REL_COLORS['bg']};
                border: 3px solid {REL_COLORS['teal_bright']};
            }}
            QLabel {{
                color: {REL_COLORS['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: {REL_COLORS['grey_dark']};
                border: 2px solid {REL_COLORS['teal_mid']};
                color: {REL_COLORS['text']};
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                padding: 10px;
                border-radius: 8px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Temporal Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {REL_COLORS['teal_dark']}, 
                    stop:1 {REL_COLORS['grey_dark']});
                border: 2px solid {REL_COLORS['teal_bright']};
                border-radius: 10px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("TEMPORAL OPERATIONS COMMAND")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            padding: 20px;
        """)
        
        subtitle_label = QLabel("USS RELATIVITY - 29TH CENTURY AUTHORIZATION")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {REL_COLORS['alert']};
            font-style: italic;
            padding: 5px;
        """)
        
        temporal_label = QLabel("◊ TEMPORAL MECHANICS DIVISION ◊")
        temporal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temporal_label.setStyleSheet(f"""
            font-size: 14px;
            color: {REL_COLORS['grey_light']};
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(temporal_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(25)
        auth_layout.setContentsMargins(120, 40, 120, 40)
        
        # Temporal authorization field
        auth_label = QLabel("TEMPORAL AUTHORIZATION MATRIX:")
        auth_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            margin-bottom: 15px;
        """)
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.auth_field = QLineEdit()
        self.auth_field.setPlaceholderText("Enter temporal access codes...")
        self.auth_field.setFixedHeight(45)
        
        # Relativity-style buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(20)
        
        self.relativity_buttons = []
        temporal_commands = [
            ("TEMPORAL OPS", REL_COLORS['teal_bright']),
            ("CHRONOTON SCAN", REL_COLORS['teal_mid']),
            ("TIME STREAM", REL_COLORS['alert']),
            ("COMMAND AUTH", REL_COLORS['grey_light'])
        ]
        
        for text, color in temporal_commands:
            btn = RelativityButton(text, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(200, 50)
            self.relativity_buttons.append(btn)
            button_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_field)
        auth_layout.addWidget(button_frame)
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def update_temporal_colors(self):
        """Update temporal color fluctuations"""
        temporal_colors = [
            REL_COLORS['teal_bright'],
            REL_COLORS['teal_mid'],
            REL_COLORS['teal_dark'],
            REL_COLORS['alert'],
            REL_COLORS['grey_light']
        ]
        
        for btn in self.relativity_buttons:
            btn.base_color = QColor(random.choice(temporal_colors))
            btn.update()
            
    def authenticate(self):
        """Handle temporal authentication"""
        print("✅ USS Relativity temporal authentication successful!")
        self.authentication_success.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation29thLogin()
    login.show()
    sys.exit(app.exec())
