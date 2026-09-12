"""
LCARS Working System - 22nd Century NX-01 Interface
Based on Enterprise NX-01 computer systems
"""

import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal

# NX-01 Enterprise Palette
NX_COLORS = {
    'bg': '#000011',           # Deep Space Navy
    'nx_orange': '#FF6600',    # NX Primary Orange
    'nx_blue': '#0066CC',      # NX Secondary Blue
    'nx_yellow': '#FFCC00',    # NX Alert Yellow
    'nx_green': '#66CC00',     # NX Systems Green
    'nx_red': '#CC3300',       # NX Warning Red
    'text': '#E0E0FF',         # Pale Blue Text
    'panel': '#1A1A33'         # Panel Background
}

class NXButton(QPushButton):
    """NX-01 Enterprise style button"""
    def __init__(self, text="", color=NX_COLORS['nx_orange'], parent=None):
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
        
        rect = self.rect().adjusted(3, 3, -3, -3)
        
        # NX-style gradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(160))
            gradient.setColorAt(0.5, self.base_color)
            gradient.setColorAt(1, self.base_color.darker(120))
        else:
            gradient.setColorAt(0, self.base_color.lighter(130))
            gradient.setColorAt(1, self.base_color.darker(110))
            
        # Draw NX pill shape
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.base_color.lighter(140), 2))
        painter.drawRoundedRect(QRectF(rect), 20, 20)
        
        # Text
        painter.setPen(QColor("#000000"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class NX01Desktop(QMainWindow):
    """NX-01 Enterprise Desktop Interface"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NX-01 Enterprise - Computer Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {NX_COLORS['bg']}, 
                    stop:1 {NX_COLORS['panel']});
                color: {NX_COLORS['text']};
            }}
        """)
        
        # Main interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Header
        header = QLabel("NX-01 ENTERPRISE COMPUTER CORE")
        header.setStyleSheet(f"""
            font-size: 38px;
            font-weight: bold;
            color: {NX_COLORS['nx_orange']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(30)
        
        # Left navigation
        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 102, 0, 0.1);
                border: 2px solid {NX_COLORS['nx_orange']};
                border-radius: 12px;
                padding: 15px;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        
        nav_title = QLabel("SHIP SYSTEMS")
        nav_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {NX_COLORS['nx_orange']};
            text-align: center;
            padding: 10px;
        """)
        nav_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(nav_title)
        
        nx_systems = [
            ("WARP CORE", NX_COLORS['nx_blue']),
            ("IMPULSE ENGINES", NX_COLORS['nx_green']),
            ("PHASE CANNONS", NX_COLORS['nx_red']),
            ("POLARIZED HULL", NX_COLORS['nx_yellow']),
            ("SENSORS", NX_COLORS['nx_blue']),
            ("COMMUNICATIONS", NX_COLORS['nx_green'])
        ]
        
        for system, color in nx_systems:
            btn = NXButton(system, color)
            btn.setMinimumHeight(45)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        logout_btn = NXButton("SYSTEM LOGOUT", NX_COLORS['nx_red'])
        logout_btn.clicked.connect(self.logout)
        left_layout.addWidget(logout_btn)
        
        content_layout.addWidget(left_panel)
        
        # Center display
        center_panel = QFrame()
        center_panel.setStyleSheet(f"""
            QFrame {{
                background: rgba(0, 102, 204, 0.1);
                border: 3px solid {NX_COLORS['nx_blue']};
                border-radius: 15px;
            }}
        """)
        
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(40, 40, 40, 40)
        
        center_title = QLabel("ENTERPRISE NX-01")
        center_title.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {NX_COLORS['nx_blue']};
            text-align: center;
            padding: 30px;
        """)
        center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(center_title)
        
        status_label = QLabel("ALL SYSTEMS OPERATIONAL")
        status_label.setStyleSheet(f"""
            font-size: 24px;
            color: {NX_COLORS['nx_green']};
            text-align: center;
            padding: 20px;
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(status_label)
        
        center_layout.addStretch()
        content_layout.addWidget(center_panel)
        
        layout.addWidget(content_container)
        
        # Footer
        footer = QLabel("UNITED EARTH STARFLEET • NX-CLASS STARSHIP • 2151-2161")
        footer.setStyleSheet(f"""
            font-size: 16px;
            color: {NX_COLORS['text']};
            text-align: center;
            padding: 15px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
    def logout(self):
        """Return to launcher"""
        self.authentication_success.emit()
        self.close()

class Federation22ndLogin(QMainWindow):
    """22nd Century NX-01 Login Screen"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NX-01 Enterprise - Computer Access")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup NX-01 login interface"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {NX_COLORS['bg']}, 
                    stop:1 {NX_COLORS['panel']});
                color: {NX_COLORS['text']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Header
        header = QLabel("ENTERPRISE NX-01 COMPUTER SYSTEM")
        header.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {NX_COLORS['nx_orange']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("UNITED EARTH STARFLEET • 22ND CENTURY")
        subtitle.setStyleSheet(f"""
            font-size: 20px;
            color: {NX_COLORS['nx_blue']};
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
        
        access_systems = [
            ("COMPUTER CORE ACCESS", NX_COLORS['nx_orange']),
            ("ENGINEERING SYSTEMS", NX_COLORS['nx_blue']),
            ("TACTICAL SYSTEMS", NX_COLORS['nx_red']),
            ("SCIENCE STATIONS", NX_COLORS['nx_green'])
        ]
        
        for system, color in access_systems:
            btn = NXButton(system, color)
            btn.setMinimumSize(400, 70)
            btn.clicked.connect(self.authenticate)
            button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
    def authenticate(self):
        """Launch NX-01 desktop"""
        print("✅ NX-01 Enterprise authentication successful!")
        QTimer.singleShot(1000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch NX-01 desktop"""
        print("🚀 Launching NX-01 Desktop...")
        self.desktop = NX01Desktop()
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
    login = Federation22ndLogin()
    login.show()
    sys.exit(app.exec())