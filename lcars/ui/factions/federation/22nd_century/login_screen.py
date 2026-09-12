"""
Federation 22nd Century Login Screen
Based on NX-01 Enterprise Master Systems Display
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class NXButton(QPushButton):
    """NX-style rectangular button with corner indicator"""
    def __init__(self, text, color="#269EEE", parent=None):
        super().__init__(text, parent)
        self.btn_color = color
        self.setMinimumHeight(35)
        self.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(1, 1, -1, -1)
        
        # Hover effect
        bg_color = QColor(self.btn_color)
        if self.underMouse():
            bg_color = bg_color.lighter(120)
        if self.isDown():
            bg_color = bg_color.darker(120)
            
        # Draw main button
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawRect(rect)
        
        # Draw text
        painter.setPen(QColor("#000000"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class Federation22ndLogin(QMainWindow):
    """22nd Century Federation Login Screen - NX-01 Style"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_nx_interface()
        
        # Color update timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(3000)  # Every 3 seconds
        
    def setup_nx_interface(self):
        """Setup NX-01 Enterprise interface"""
        self.setWindowTitle("NX-01 Enterprise Master Systems Display")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # NX-01 color scheme
        self.colors = {
            'background': '#1A1A1A',    # Dark grey
            'text': '#E0E0E0',          # Light grey
            'primary': '#269EEE',       # NX Blue
            'secondary': '#4A90E2',     # Lighter blue
            'accent': '#FF6B35',        # Orange accent
            'panel': '#2A2A2A',         # Panel grey
        }
        
        # Apply NX-01 styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                color: {self.colors['text']};
                font-family: 'Arial', sans-serif;
                font-size: 16px;
                padding: 8px;
            }}
        """)
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # NX-01 Header
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['primary']};
                border-radius: 5px;
            }}
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("NX-01 ENTERPRISE")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {self.colors['primary']};
            padding: 15px;
        """)
        
        subtitle_label = QLabel("STARFLEET COMMAND AUTHORIZATION")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['secondary']};
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Authentication area
        auth_frame = QFrame()
        auth_layout = QVBoxLayout(auth_frame)
        auth_layout.setSpacing(20)
        auth_layout.setContentsMargins(100, 30, 100, 30)
        
        # Authorization field
        auth_label = QLabel("AUTHORIZATION CODE:")
        auth_label.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        
        self.auth_field = QLineEdit()
        self.auth_field.setPlaceholderText("Enter Starfleet authorization...")
        self.auth_field.setFixedHeight(40)
        
        # NX-style buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        self.nx_buttons = []
        nx_commands = [
            ("MAIN SYSTEMS", "#269EEE"),
            ("NAVIGATION", "#4A90E2"),
            ("ENGINEERING", "#FF6B35"),
            ("COMMAND AUTH", "#7B68EE")
        ]
        
        for text, color in nx_commands:
            btn = NXButton(text, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(200, 50)
            self.nx_buttons.append(btn)
            button_layout.addWidget(btn)
            
        # Assembly
        auth_layout.addWidget(auth_label)
        auth_layout.addWidget(self.auth_field)
        auth_layout.addWidget(button_frame)
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def update_colors(self):
        """Update NX-01 button colors"""
        nx_colors = ["#269EEE", "#4A90E2", "#FF6B35", "#7B68EE", "#20B2AA", "#FF69B4"]
        import random
        
        for btn in self.nx_buttons:
            btn.btn_color = random.choice(nx_colors)
            btn.update()
            
    def authenticate(self):
        """Handle authentication"""
        print("✅ NX-01 Enterprise authentication successful!")
        self.authentication_success.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation22ndLogin()
    login.show()
    sys.exit(app.exec())
