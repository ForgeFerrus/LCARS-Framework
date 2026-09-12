"""
25th Century Federation Login Interface
Advanced Holographic LCARS Design
Based on future Federation technology
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import math
import random
import time
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QHBoxLayout, QFrame, QApplication, 
                           QGridLayout, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                           QGraphicsLineItem)
from PyQt6.QtGui import (QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QBrush, 
                        QLinearGradient, QRadialGradient, QConicalGradient)
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF, pyqtSignal

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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
        self.glow_intensity = 0
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        
        # Glow animation timer
        self.glow_timer = QTimer()
        self.glow_timer.timeout.connect(self.animate_glow)
        self.glow_timer.start(50)
        
    def enterEvent(self, event):
        self.hovered = True
        self.update()
        
    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        
    def animate_glow(self):
        self.glow_intensity = (self.glow_intensity + 5) % 100
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(8, 8, -8, -8)
        
        # Holographic glow effect
        glow_radius = 15 + (self.glow_intensity / 100.0) * 10
        for i in range(int(glow_radius)):
            alpha = int(255 * (1 - i / glow_radius) * 0.3)
            glow_color = QColor(self.base_color)
            glow_color.setAlpha(alpha)
            painter.setPen(QPen(glow_color, 2))
            painter.drawRoundedRect(rect.adjusted(-i, -i, i, i), 20, 20)
        
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
        
        # Holographic text with glow
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
        self.setFixedSize(500, 300)
        self.angle = 0
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)
        
        # Initialize holographic particles
        for _ in range(20):
            self.particles.append({
                'x': random.uniform(0, 500),
                'y': random.uniform(0, 300),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'size': random.uniform(2, 8),
                'color': random.choice([HOLO_COLORS['holo_blue'], HOLO_COLORS['holo_cyan'], 
                                      HOLO_COLORS['holo_purple'], HOLO_COLORS['holo_green']])
            })
        
    def animate(self):
        self.angle = (self.angle + 2) % 360
        
        # Update particles
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Wrap around edges
            if particle['x'] < 0: particle['x'] = 500
            if particle['x'] > 500: particle['x'] = 0
            if particle['y'] < 0: particle['y'] = 300
            if particle['y'] > 300: particle['y'] = 0
        
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background grid pattern
        grid_pen = QPen(QColor(HOLO_COLORS['holo_blue']), 1)
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)
        
        for x in range(0, 500, 25):
            painter.drawLine(x, 0, x, 300)
        for y in range(0, 300, 25):
            painter.drawLine(0, y, 500, y)
        
        # Central holographic display
        center_x, center_y = 250, 150
        
        # Rotating holographic rings
        for i, radius in enumerate([50, 80, 110]):
            ring_angle = self.angle + (i * 30)
            pen_color = QColor(HOLO_COLORS['holo_cyan'])
            pen_color.setAlpha(150 - i * 30)
            painter.setPen(QPen(pen_color, 2))
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
            
        # Holographic particles
        for particle in self.particles:
            color = QColor(particle['color'])
            color.setAlpha(180)
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(particle['x']), int(particle['y']), 
                              int(particle['size']), int(particle['size']))
        
        # Central authentication matrix
        matrix_size = 60
        matrix_gradient = QRadialGradient(QPointF(center_x, center_y), matrix_size)
        matrix_gradient.setColorAt(0, QColor(HOLO_COLORS['holo_gold']))
        matrix_gradient.setColorAt(0.5, QColor(HOLO_COLORS['holo_blue']))
        matrix_gradient.setColorAt(1, QColor(HOLO_COLORS['holo_purple']))
        
        painter.setBrush(QBrush(matrix_gradient))
        painter.setPen(QPen(QColor(HOLO_COLORS['holo_white']), 2))
        painter.drawEllipse(center_x - matrix_size, center_y - matrix_size, 
                           matrix_size * 2, matrix_size * 2)
        
        # Authentication text
        painter.setPen(QColor(HOLO_COLORS['holo_white']))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(QRectF(center_x - 80, center_y - 10, 160, 20), 
                        Qt.AlignmentFlag.AlignCenter, "AUTHENTICATION")

class Federation25thLogin(QMainWindow):
    """25th Century Federation Login Screen - Holographic LCARS"""
    authentication_success = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_holographic_interface()
        
        # Holographic color cycling timer
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_holographic_colors)
        self.color_timer.start(3000)  # Every 3 seconds
        
        self.holographic_buttons = []
        
    def setup_holographic_interface(self):
        """Setup 25th century holographic interface"""
        self.setWindowTitle("Federation - 25th Century Holographic Interface")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        # Initialize holographic buttons list
        self.holographic_buttons = []
        
        # Apply holographic styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                    stop:0 {HOLO_COLORS['bg']}, 
                    stop:1 {HOLO_COLORS['holo_blue']});
                color: {HOLO_COLORS['text']};
            }}
            QLabel {{
                color: {HOLO_COLORS['text']};
                font-family: 'Arial', sans-serif;
                background: transparent;
                border: none;
            }}
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 204, 255, 0.2), 
                    stop:1 rgba(0, 0, 8, 0.8));
                border: 2px solid {HOLO_COLORS['holo_cyan']};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                color: {HOLO_COLORS['text']};
                min-height: 30px;
            }}
            QLineEdit:focus {{
                border: 3px solid {HOLO_COLORS['holo_gold']};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 204, 0, 0.3), 
                    stop:1 rgba(0, 204, 255, 0.2));
            }}
        """)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # HOLOGRAPHIC HEADER
        header_frame = QFrame()
        header_frame.setFixedHeight(200)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 204, 255, 0.3), 
                    stop:1 rgba(0, 0, 8, 0.9));
                border: 3px solid {HOLO_COLORS['holo_cyan']};
                border-radius: 15px;
                margin: 20px;
            }}
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 30, 30, 30)
        
        # Holographic title
        title_label = QLabel("◊ FEDERATION COMMAND ◊")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_blue']};
            padding: 10px;
        """)
        
        subtitle_label = QLabel("25TH CENTURY HOLOGRAPHIC INTERFACE")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            font-size: 20px;
            color: {HOLO_COLORS['holo_gold']};
            padding: 5px;
        """)
        
        future_label = QLabel("◊ NEURAL INTERFACE PROTOCOLS ACTIVE ◊")
        future_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_label.setStyleSheet(f"""
            font-size: 16px;
            color: {HOLO_COLORS['holo_purple']};
            font-style: italic;
            padding: 5px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(future_label)
        
        # AUTHENTICATION AREA
        auth_frame = QFrame()
        auth_frame.setStyleSheet(f"""
            QFrame {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                    stop:0 rgba(102, 221, 255, 0.2), 
                    stop:1 rgba(0, 0, 8, 0.8));
                border: 2px solid {HOLO_COLORS['holo_blue']};
                border-radius: 20px;
                margin: 20px;
            }}
        """)
        
        auth_layout = QHBoxLayout(auth_frame)
        auth_layout.setContentsMargins(40, 40, 40, 40)
        auth_layout.setSpacing(30)
        
        # Left: Holomatrix Display
        self.holomatrix = HolomatrixDisplay()
        auth_layout.addWidget(self.holomatrix)
        
        # Center: Authentication Form
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(20)
        
        auth_label = QLabel("◊ HOLOGRAPHIC AUTHENTICATION ◊")
        auth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_label.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_cyan']};
            padding: 15px;
            border: 2px solid {HOLO_COLORS['holo_cyan']};
            border-radius: 10px;
            background: rgba(0, 204, 255, 0.1);
        """)
        
        # Username field
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Neural Pattern ID")
        
        # Password field
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Biometric Encryption Key")
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
        
        auth_layout.addWidget(form_widget)
        
        # Right: Holographic Controls
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        
        controls_title = QLabel("◊ NEURAL INTERFACES ◊")
        controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {HOLO_COLORS['holo_gold']};
            padding: 10px;
            border: 2px solid {HOLO_COLORS['holo_gold']};
            border-radius: 8px;
        """)
        controls_layout.addWidget(controls_title)
        
        # Holographic interface buttons
        holo_interfaces = [
            ("NEURAL LINK", HOLO_COLORS['holo_blue']),
            ("BIOMETRIC SCAN", HOLO_COLORS['holo_green']),
            ("QUANTUM AUTH", HOLO_COLORS['holo_purple']),
            ("HOLO ACCESS", HOLO_COLORS['holo_gold'])
        ]
        
        for interface, color in holo_interfaces:
            btn = HolographicButton(interface, color)
            btn.clicked.connect(self.authenticate)
            btn.setMinimumSize(200, 60)
            self.holographic_buttons.append(btn)
            controls_layout.addWidget(btn)
            
        controls_layout.addStretch()
        auth_layout.addWidget(controls_widget)
        
        # Assembly
        main_layout.addWidget(header_frame)
        main_layout.addWidget(auth_frame)
        main_layout.addStretch()
        
    def cycle_holographic_colors(self):
        """Cycle holographic interface colors"""
        holo_colors = [
            HOLO_COLORS['holo_blue'],
            HOLO_COLORS['holo_cyan'],
            HOLO_COLORS['holo_purple'],
            HOLO_COLORS['holo_green'],
            HOLO_COLORS['holo_gold']
        ]
        
        for btn in self.holographic_buttons:
            btn.base_color = QColor(random.choice(holo_colors))
            btn.update()
            
    def authenticate(self):
        """Handle holographic authentication and launch desktop"""
        print("✅ 25th Century holographic authentication successful!")
        
        # Launch holographic desktop
        QTimer.singleShot(1000, self.launch_holographic_desktop)
        
    def launch_holographic_desktop(self):
        """Launch 25th century holographic desktop interface"""
        print("🚀 Launching 25th Century Holographic Desktop...")
        from .desktop import Federation25thDesktop
        
        self.holographic_desktop = Federation25thDesktop()
        
        # Connect desktop logout to return to boot system
        self.holographic_desktop.authentication_success.connect(self.on_desktop_logout)
        
        # Hide login and show desktop
        self.hide()
        self.holographic_desktop.show()
        
    def on_desktop_logout(self):
        """Handle desktop logout - return to boot system"""
        self.holographic_desktop = None
        self.authentication_success.emit()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Federation25thLogin()
    login.show()
    sys.exit(app.exec())
