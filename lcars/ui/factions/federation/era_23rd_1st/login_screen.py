"""
23rd Century First Half Login Interface (2200-2250)
Early PCARS Design - Cold Blue Palette
Based on early Federation computer systems
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import math
import random
import time
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QHBoxLayout, QFrame, QApplication, 
                           QGridLayout)
from PyQt6.QtGui import (QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, 
                        QLinearGradient, QRadialGradient)
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF, pyqtSignal

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 23rd Century First Half Cold Blue Palette
PCARS_EARLY_COLORS = {
    'bg': '#0A0A12',           # Deep Space Black
    'primary': '#00AAFF',      # Science Blue
    'secondary': '#4A9EFF',    # Function Blue
    'accent1': '#0088CC',      # Command Dark Blue
    'accent2': '#66BBFF',      # Highlight Blue
    'text': '#E0F0FF',         # Phosphor White
    'success': '#00FF88',      # Isolinear Green
    'warning': '#FFAA00',      # Alert Orange
    'danger': '#FF4444',       # Red Alert
    'info': '#88CCFF'          # Data Blue
}

class PCARSEarlyButton(QPushButton):
    """23rd Century early PCARS-style button with cold blue design"""
    def __init__(self, text="", color=PCARS_EARLY_COLORS['primary'], parent=None):
        super().__init__(text, parent)
        self.base_color = QColor(color)
        self.hovered = False
        self.setMinimumHeight(45)
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
        
        rect = self.rect().adjusted(4, 4, -4, -4)
        
        # Cold blue gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(160))
            gradient.setColorAt(0.5, self.base_color)
            gradient.setColorAt(1, self.base_color.darker(130))
        else:
            gradient.setColorAt(0, self.base_color.lighter(120))
            gradient.setColorAt(0.8, self.base_color.darker(110))
            gradient.setColorAt(1, self.base_color.darker(140))
            
        # Draw rectangular PCARS button
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.base_color.lighter(140), 2))
        painter.drawRoundedRect(QRectF(rect), 8, 8)
        
        # Draw text
        painter.setPen(QColor("#000000" if not self.hovered else "#FFFFFF"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class Federation23rdFirstLogin(QMainWindow):
    """23rd Century First Half Federation Login Screen - Early PCARS"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_early_pcars_interface()
        
        # Early system color timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_early_colors)
        self.color_timer.start(4000)  # Every 4 seconds for stability
        
        self.pcars_buttons = []
        
    def setup_early_pcars_interface(self):
        """Setup 23rd century early PCARS interface"""
        self.setWindowTitle("Federation - 23rd Century Early Systems (2200-2250)")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Apply early PCARS styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {PCARS_EARLY_COLORS['bg']}, 
                    stop:1 {PCARS_EARLY_COLORS['accent1']});
                color: {PCARS_EARLY_COLORS['text']};
            }}
            QLabel {{
                color: {PCARS_EARLY_COLORS['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 170, 255, 0.2), 
                    stop:1 rgba(10, 10, 18, 0.8));
                border: 2px solid {PCARS_EARLY_COLORS['secondary']};
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: {PCARS_EARLY_COLORS['text']};
                min-height: 25px;
            }}
            QLineEdit:focus {{
                border: 3px solid {PCARS_EARLY_COLORS['accent2']};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(102, 187, 255, 0.3), 
                    stop:1 rgba(0, 170, 255, 0.2));
            }}
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # EARLY PCARS HEADER
        header_frame = QFrame()
        header_frame.setFixedHeight(180)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 170, 255, 0.4), 
                    stop:1 rgba(10, 10, 18, 0.9));
                border: 3px solid {PCARS_EARLY_COLORS['primary']};
                border-radius: 10px;
                margin: 15px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(25, 25, 25, 25)
        
        # Early Federation title
        title_label = QLabel("FEDERATION COMPUTER SYSTEM")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {PCARS_EARLY_COLORS['primary']};
            padding: 10px;
        """)
        
        subtitle_label = QLabel("23RD CENTURY EARLY SYSTEMS • 2200-2250")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 18px;
            color: {PCARS_EARLY_COLORS['secondary']};
            padding: 5px;
        """)
        
        era_label = QLabel("PCARS PROTOCOL INITIALIZATION")
        era_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        era_label.setStyleSheet(f"""
            font-size: 16px;
            color: {PCARS_EARLY_COLORS['info']};
            font-style: italic;
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(era_label)
        
        # AUTHENTICATION AREA
        auth_frame = QFrame()
        auth_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(74, 158, 255, 0.2), 
                    stop:1 rgba(10, 10, 18, 0.8));
                border: 2px solid {PCARS_EARLY_COLORS['secondary']};
                border-radius: 15px;
                margin: 15px;
            }}
        """)
        
        auth_layout = QHBoxLayout(auth_frame)
        auth_layout.setContentsMargins(30, 30, 30, 30)
        auth_layout.setSpacing(25)
        
        # Left: Computer System Info
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setSpacing(15)
        
        info_title = QLabel("SYSTEM SPECIFICATIONS")
        info_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {PCARS_EARLY_COLORS['accent2']};
            padding: 12px;
            border: 2px solid {PCARS_EARLY_COLORS['accent2']};
            border-radius: 8px;
            background: rgba(102, 187, 255, 0.1);
        """)
        
        # System info
        system_info = QLabel("""
• DUOTRONIC COMPUTER SYSTEM
• ISOLINEAR OPTICAL CHIPS
• SUBSPACE COMMUNICATION
• FEDERATION DATABASE ACCESS
• STARFLEET COMMAND LINK
• SECURITY PROTOCOL ALPHA
        """)
        system_info.setStyleSheet(f"""
            font-size: 14px;
            color: {PCARS_EARLY_COLORS['text']};
            padding: 15px;
            border: 1px solid {PCARS_EARLY_COLORS['info']};
            border-radius: 6px;
            background: rgba(136, 204, 255, 0.05);
        """)
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(system_info)
        info_layout.addStretch()
        
        # Center: Authentication Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        auth_label = QLabel("DUOTRONIC AUTHENTICATION")
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_label.setStyleSheet(f"""
            font-size: 22px;
            font-weight: bold;
            color: {PCARS_EARLY_COLORS['primary']};
            padding: 12px;
            border: 2px solid {PCARS_EARLY_COLORS['primary']};
            border-radius: 8px;
            background: rgba(0, 170, 255, 0.1);
        """)
        
        # Username field
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Officer Identification Code")
        
        # Password field
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Security Clearance Key")
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            min-height: 20px;
        """)
        
        form_layout.addWidget(auth_label)
        form_layout.addWidget(self.username_field)
        form_layout.addWidget(self.password_field)
        form_layout.addWidget(self.status_label)
        form_layout.addStretch()
        
        # Right: System Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(12)
        
        controls_title = QLabel("SYSTEM ACCESS")
        controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {PCARS_EARLY_COLORS['success']};
            padding: 10px;
            border: 2px solid {PCARS_EARLY_COLORS['success']};
            border-radius: 8px;
        """)
        controls_layout.addWidget(controls_title)
        
        # PCARS interface buttons
        pcars_interfaces = [
            ("COMPUTER CORE", PCARS_EARLY_COLORS['primary']),
            ("DATA BANK", PCARS_EARLY_COLORS['secondary']),
            ("COMMUNICATION", PCARS_EARLY_COLORS['info']),
            ("SECURITY", PCARS_EARLY_COLORS['warning'])
        ]
        
        for interface, color in pcars_interfaces:
            btn = PCARSEarlyButton(interface, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(180, 55)
            self.pcars_buttons.append(btn)
            controls_layout.addWidget(btn)
            
        controls_layout.addStretch()
        
        # Assembly
        auth_layout.addWidget(info_widget)
        auth_layout.addWidget(form_widget)
        auth_layout.addWidget(controls_widget)
        
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def update_early_colors(self):
        """Update early PCARS system colors"""
        early_colors = [
            PCARS_EARLY_COLORS['primary'],
            PCARS_EARLY_COLORS['secondary'],
            PCARS_EARLY_COLORS['accent1'],
            PCARS_EARLY_COLORS['accent2']
        ]
        
        for btn in self.pcars_buttons:
            btn.base_color = QColor(random.choice(early_colors))
            btn.update()
            
    def authenticate(self):
        """Handle early PCARS authentication and launch desktop"""
        print("✅ 23rd Century early PCARS authentication successful!")
        
        # Launch early PCARS desktop
        QTimer.singleShot(1000, self.launch_early_desktop)
        
    def launch_early_desktop(self):
        """Launch 23rd century early desktop interface"""
        print("🚀 Launching Early 23rd Century Desktop...")
        from .desktop import Federation23rdFirstDesktop
        
        self.early_desktop = Federation23rdFirstDesktop()
        
        # Connect desktop logout to return to boot system
        self.early_desktop.authentication_success.connect(self.on_desktop_logout)
        
        # Hide login and show desktop
        self.hide()
        self.early_desktop.show()
        
    def on_desktop_logout(self):
        """Handle desktop logout - return to boot system"""
        self.early_desktop = None
        self.authentication_success.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation23rdFirstLogin()
    login.show()
    sys.exit(app.exec())
