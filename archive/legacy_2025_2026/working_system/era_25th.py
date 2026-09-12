"""
LCARS Working System - 25th Century Interface
Complete working holographic interface
"""

import sys
import math
import random
import time
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QHBoxLayout, QFrame, QApplication, 
                           QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                           QGraphicsLineItem)
from PyQt6.QtGui import (QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, 
                        QLinearGradient, QRadialGradient, QConicalGradient)
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF, pyqtSignal

# 25th Century Holographic Palette
HOLO_COLORS = {
    'bg': '#000008',           # Deep Space Black
    'holo_blue': '#00CCFF',    # Holographic Blue
    'holo_cyan': '#66DDFF',    # Light Cyan
    'holo_gold': '#FFCC00',    # Quantum Gold
    'holo_green': '#00FF66',   # Matrix Green
    'holo_purple': '#CC66FF',  # Subspace Purple
    'holo_white': '#FFFFFF',   # Pure White
    'text': '#E0F0FF',         # Phosphor Blue-White
    'warning': '#FF6600',      # Neural Orange
    'error': '#FF3366'         # Critical Red
}

class HolographicButton(QPushButton):
    """25th Century Holographic-style button with glow effects"""
    def __init__(self, text="", color=HOLO_COLORS['holo_blue'], parent=None):
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
        
        rect = self.rect().adjusted(8, 8, -8, -8)
        
        # Main holographic gradient
        gradient = QRadialGradient(QPointF(rect.center()), rect.width() / 2)
        if self.hovered or self.isDown():
            gradient.setColorAt(0, self.base_color.lighter(200))
            gradient.setColorAt(0.7, self.base_color)
            gradient.setColorAt(1, self.base_color.darker(150))
        else:
            gradient.setColorAt(0, self.base_color.lighter(150))
            gradient.setColorAt(0.7, self.base_color.darker(120))
            gradient.setColorAt(1, self.base_color.darker(200))
            
        # Draw button
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(self.base_color.lighter(150), 3))
        painter.drawRoundedRect(QRectF(rect), 20, 20)
        
        # Holographic text
        text_color = QColor(HOLO_COLORS['holo_white'])
        if self.hovered:
            text_color = self.base_color.lighter(200)
            
        painter.setPen(text_color)
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class HolomatrixDisplay(QWidget):
    """Central holomatrix authentication display"""
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 250)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)
        
    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Central holographic display
        center_x, center_y = 200, 125
        
        # Rotating holographic rings
        for i, radius in enumerate([40, 60, 80]):
            pen_color = QColor(HOLO_COLORS['holo_cyan'])
            pen_color.setAlpha(150 - i * 30)
            painter.setPen(QPen(pen_color, 2))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            
        # Central authentication matrix
        matrix_size = 30
        matrix_gradient = QRadialGradient(QPointF(center_x, center_y), matrix_size)
        matrix_gradient.setColorAt(0, QColor(HOLO_COLORS['holo_gold']))
        matrix_gradient.setColorAt(0.5, QColor(HOLO_COLORS['holo_blue']))
        matrix_gradient.setColorAt(1, QColor(HOLO_COLORS['holo_purple']))
        
        painter.setBrush(QBrush(matrix_gradient))
        painter.setPen(QPen(QColor(HOLO_COLORS['holo_white']), 2))
        painter.drawEllipse(center_x - matrix_size, center_y - matrix_size, 
                           matrix_size * 2, matrix_size * 2)

class Federation25thDesktop(QMainWindow):
    """25th Century Federation Desktop - Simplified"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Federation - 25th Century Neural Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:1.5,
                    stop:0 {HOLO_COLORS['bg']}, 
                    stop:1 rgba(0, 204, 255, 0.1));
                color: {HOLO_COLORS['text']};
            }}
        """)
        
        # Main interface
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)
        
        # Header
        header = QLabel("◊ 25TH CENTURY NEURAL INTERFACE ◊")
        header.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_blue']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Content area
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(30)
        
        # Left panel
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: rgba(0, 204, 255, 0.1);
                border: 2px solid {HOLO_COLORS['holo_cyan']};
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        nav_buttons = [
            ("NEURAL MATRIX", HOLO_COLORS['holo_blue']),
            ("HOLOGRAPHIC PROJ", HOLO_COLORS['holo_cyan']),
            ("QUANTUM INTERFACE", HOLO_COLORS['holo_purple']),
            ("BIONEURAL NET", HOLO_COLORS['holo_green'])
        ]
        
        for label, color in nav_buttons:
            btn = HolographicButton(label, color)
            btn.setMinimumHeight(50)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        logout_btn = HolographicButton("NEURAL DISCONNECT", "#FF6600")
        logout_btn.clicked.connect(self.logout)
        left_layout.addWidget(logout_btn)
        
        content_layout.addWidget(left_panel)
        
        # Center display
        center_panel = QFrame()
        center_panel.setStyleSheet(f"""
            QFrame {{
                background: rgba(102, 221, 255, 0.05);
                border: 3px solid {HOLO_COLORS['holo_blue']};
                border-radius: 20px;
            }}
        """)
        
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(40, 40, 40, 40)
        
        center_title = QLabel("HOLOGRAPHIC INTERFACE ACTIVE")
        center_title.setStyleSheet(f"""
            font-size: 36px;
            color: {HOLO_COLORS['holo_cyan']};
            text-align: center;
            padding: 30px;
        """)
        center_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(center_title)
        
        center_layout.addStretch()
        content_layout.addWidget(center_panel)
        
        layout.addWidget(content_container)
        
        # Footer
        footer = QLabel("UNITED FEDERATION OF PLANETS • 25TH CENTURY TECHNOLOGY")
        footer.setStyleSheet(f"""
            font-size: 16px;
            color: {HOLO_COLORS['text']};
            text-align: center;
            padding: 15px;
        """)
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)
        
    def logout(self):
        """Return to launcher"""
        self.authentication_success.emit()
        self.close()

class Federation25thLogin(QMainWindow):
    """25th Century Federation Login Screen"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Federation - 25th Century Holographic Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.holographic_buttons = []
        self.setup_interface()
        
    def setup_interface(self):
        """Setup holographic login interface"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                    stop:0 {HOLO_COLORS['bg']}, 
                    stop:1 {HOLO_COLORS['holo_blue']});
                color: {HOLO_COLORS['text']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(40)
        
        # Header
        header = QLabel("◊ FEDERATION COMMAND - 25TH CENTURY ◊")
        header.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_blue']};
            text-align: center;
            padding: 20px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        subtitle = QLabel("HOLOGRAPHIC INTERFACE PROTOCOLS")
        subtitle.setStyleSheet(f"""
            font-size: 24px;
            color: {HOLO_COLORS['holo_gold']};
            text-align: center;
            padding: 10px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Main content
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setSpacing(50)
        
        # Left: Holomatrix
        self.holomatrix = HolomatrixDisplay()
        content_layout.addWidget(self.holomatrix)
        
        # Center: Auth form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(25)
        
        auth_label = QLabel("◊ HOLOGRAPHIC AUTHENTICATION ◊")
        auth_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_cyan']};
            text-align: center;
            padding: 15px;
            border: 2px solid {HOLO_COLORS['holo_cyan']};
            border-radius: 10px;
        """)
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.addWidget(auth_label)
        
        form_layout.addSpacing(30)
        
        # Right: Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(20)
        
        controls_title = QLabel("◊ NEURAL INTERFACES ◊")
        controls_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_gold']};
            text-align: center;
            padding: 10px;
            border: 2px solid {HOLO_COLORS['holo_gold']};
            border-radius: 8px;
        """)
        controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(controls_title)
        
        holo_interfaces = [
            ("NEURAL LINK", HOLO_COLORS['holo_blue']),
            ("BIOMETRIC SCAN", HOLO_COLORS['holo_green']),
            ("QUANTUM AUTH", HOLO_COLORS['holo_purple']),
            ("HOLO ACCESS", HOLO_COLORS['holo_gold'])
        ]
        
        for interface, color in holo_interfaces:
            btn = HolographicButton(interface, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(220, 60)
            self.holographic_buttons.append(btn)
            controls_layout.addWidget(btn)
            
        controls_layout.addStretch()
        
        content_layout.addWidget(form_widget)
        content_layout.addWidget(controls_widget)
        
        layout.addWidget(content_container)
        layout.addStretch()
        
    def authenticate(self):
        """Launch 25th century desktop"""
        print("✅ 25th Century holographic authentication successful!")
        QTimer.singleShot(1000, self.launch_desktop)
        
    def launch_desktop(self):
        """Launch holographic desktop"""
        print("🚀 Launching 25th Century Desktop...")
        self.desktop = Federation25thDesktop()
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
    login = Federation25thLogin()
    login.show()
    sys.exit(app.exec())