"""
LCARS Working System - 29th Century USS Relativity
Temporal Operations Interface
"""

import sys
import math
import random
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal

# USS Relativity TCARS Palette
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
        
        rect = self.rect().adjusted(3, 3, -3, -3)
        
        # Temporal gradient effect
        gradient = QLinearGradient(0, 0, 0, rect.height())
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(150))
            gradient.setColorAt(0.5, self.base_color)
            gradient.setColorAt(1, self.base_color.darker(120))
        else:
            gradient.setColorAt(0, self.base_color.lighter(120))
            gradient.setColorAt(1, self.base_color.darker(130))
            
        # Draw temporal pill shape
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(REL_COLORS['teal_bright']), 2))
        painter.drawRoundedRect(QRectF(rect), 15, 15)
        
        # Text
        painter.setPen(QColor("#000000" if not self.hovered else "#FFFFFF"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class TemporalRadar(QWidget):
    """Simple temporal radar display"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 200)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)
        
    def animate(self):
        self.angle = (self.angle + 3) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() // 2, self.height()
        radius = 140
        
        # Background circles
        for r in range(40, radius, 30):
            painter.setPen(QPen(QColor(REL_COLORS['teal_dark']), 1))
            painter.drawArc(cx-r, cy-r, r*2, r*2, 0, 180*16)
            
        # Sweep line
        sweep_angle = self.angle
        rad = math.radians(sweep_angle + 180)
        sx = cx + math.cos(rad) * radius
        sy = cy + math.sin(rad) * radius
        
        painter.setPen(QPen(QColor(REL_COLORS['teal_bright']), 3))
        painter.drawLine(cx, cy, int(sx), int(sy))

class Relativity29thDesktop(QMainWindow):
    """USS Relativity Temporal Operations Desktop"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("USS Relativity - Temporal Operations Command")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {REL_COLORS['bg']};
                color: {REL_COLORS['text']};
            }}
        """)
        
        # Main interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("TEMPORAL OPERATIONS COMMAND")
        header.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Main content
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(25)
        
        # Left temporal navigation
        left_panel = QFrame()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {REL_COLORS['teal_dark']}, 
                    stop:1 {REL_COLORS['grey_dark']});
                border: 2px solid {REL_COLORS['teal_mid']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        
        nav_title = QLabel("TEMPORAL NAVIGATION")
        nav_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            padding: 8px;
        """)
        nav_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(nav_title)
        
        temporal_systems = [
            ("TEMPORAL SCAN", REL_COLORS['teal_bright']),
            ("CHRONOTON ANALYSIS", REL_COLORS['teal_mid']),
            ("TIME STREAM", REL_COLORS['alert']),
            ("TEMPORAL SHIELDS", REL_COLORS['grey_light']),
            ("QUANTUM DATING", REL_COLORS['teal_dark']),
            ("PARADOX DETECTION", REL_COLORS['alert'])
        ]
        
        for system, color in temporal_systems:
            btn = RelativityButton(system, color)
            btn.setMinimumHeight(45)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        logout_btn = RelativityButton("TEMPORAL LOGOUT", "#CE6363")
        logout_btn.clicked.connect(self.logout)
        left_layout.addWidget(logout_btn)
        
        content_layout.addWidget(left_panel)
        
        # Center display
        center_panel = QFrame()
        center_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {REL_COLORS['bg']}, 
                    stop:1 {REL_COLORS['grey_dark']});
                border: 3px solid {REL_COLORS['teal_bright']};
                border-radius: 12px;
            }}
        """)
        
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(40, 40, 40, 40)
        
        center_title = QLabel("USS RELATIVITY NCV-474439-G")
        center_title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            padding: 30px;
        """)
        center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(center_title)
        
        status_label = QLabel("TEMPORAL TIMELINE STABLE")
        status_label.setStyleSheet(f"""
            font-size: 24px;
            color: {REL_COLORS['alert']};
            text-align: center;
            padding: 20px;
        """)
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(status_label)
        
        center_layout.addStretch()
        content_layout.addWidget(center_panel)
        
        # Right temporal radar
        right_panel = QFrame()
        right_panel.setFixedWidth(250)
        right_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:1, y1:0, x2:0, y2:0,
                    stop:0 {REL_COLORS['teal_dark']}, 
                    stop:1 {REL_COLORS['grey_dark']});
                border: 2px solid {REL_COLORS['teal_mid']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        radar_title = QLabel("TEMPORAL RADAR")
        radar_title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            padding: 8px;
        """)
        radar_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(radar_title)
        
        self.temporal_radar = TemporalRadar()
        right_layout.addWidget(self.temporal_radar)
        
        right_layout.addStretch()
        content_layout.addWidget(right_panel)
        
        layout.addWidget(content_container)
        
        # Footer
        footer = QLabel("WELLS CLASS TEMPORAL VESSEL • 29TH CENTURY")
        footer.setStyleSheet(f"""
            font-size: 16px;
            color: {REL_COLORS['text']};
            text-align: center;
            padding: 15px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
    def logout(self):
        """Return to launcher"""
        self.authentication_success.emit()
        self.close()

class Federation29thLogin(QMainWindow):
    """29th Century USS Relativity Login"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("USS Relativity - Temporal Operations Command")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setup_interface()
        
    def setup_interface(self):
        """Setup Relativity temporal interface"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {REL_COLORS['bg']};
                color: {REL_COLORS['text']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Header
        header = QLabel("USS RELATIVITY")
        header.setStyleSheet(f"""
            font-size: 54px;
            font-weight: bold;
            color: {REL_COLORS['teal_bright']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("29TH CENTURY TEMPORAL OPERATIONS")
        subtitle.setStyleSheet(f"""
            font-size: 22px;
            color: {REL_COLORS['alert']};
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
        
        temporal_systems = [
            ("TEMPORAL COMMAND ACCESS", REL_COLORS['teal_bright']),
            ("CHRONOTON SYSTEMS", REL_COLORS['teal_mid']),
            ("TIME STREAM MONITOR", REL_COLORS['alert']),
            ("PARADOX PROTOCOLS", REL_COLORS['grey_light'])
        ]
        
        for system, color in temporal_systems:
            btn = RelativityButton(system, color)
            btn.setMinimumSize(500, 80)
            btn.clicked.connect(self.authenticate)
            button_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            
        layout.addWidget(button_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
    def authenticate(self):
        """Launch Relativity desktop"""
        print("✅ USS Relativity temporal authentication successful!")
        QTimer.singleShot(1000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch temporal desktop"""
        print("🚀 Launching USS Relativity Desktop...")
        self.desktop = Relativity29thDesktop()
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
    login = Federation29thLogin()
    login.show()
    sys.exit(app.exec())