"""
LCARS Interface - 29th Century Edition (TCARS)
Authentic "Relativity" Bridge Console Implementation
Based on reference visual logs (Teal/Cyan/Grey Palette)
"""

import sys
import math
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsView, QGraphicsScene,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPoint, QPointF, QRectF, QSize
from PyQt6.QtGui import (
    QColor, QPainter, QPainterPath, QPen, QBrush, 
    QLinearGradient, QRadialGradient, QPolygonF, QFont, QFontDatabase,
    QConicalGradient
)

# --- RELATIVITY PALETTE (Derived from Artifacts) ---
REL_COLORS = {
    'bg': '#000000',           # Space Black
    'teal_bright': '#00FFFF',  # Active Cyan
    'teal_mid': '#0099CC',     # Standard Teal
    'teal_dark': '#004C66',    # Deep Teal
    'grey_light': '#A0A0A0',   # Metallic Grey
    'grey_dark': '#404040',    # Structural Grey
    'alert': '#FFCC00',        # Temporal Alert (Yellow/Gold)
    'text': '#E0FFFF'          # Pale Cyan Text
}

class RelativityButton(QPushButton):
    """
    Small vertical pill or horizontal bar button often seen in rows
    """
    def __init__(self, text="", color=REL_COLORS['teal_mid']):
        super().__init__(text)
        self.base_color = QColor(color)
        self.hovered = False
        self.setFixedHeight(25)
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
        
        c = self.base_color.lighter(130) if self.hovered else self.base_color
        
        # Pill shape
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 10, 10)
        
        # Gradient
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, c.darker(120))
        grad.setColorAt(0.5, c)
        grad.setColorAt(1, c.darker(120))
        
        painter.setBrush(grad)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Text
        if self.text():
            painter.setPen(QColor(REL_COLORS['bg']))
            painter.setFont(QFont("Impact", 8))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class TemporalRadar(QWidget):
    """
    The central complex circular display seen in the reference
    """
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 200)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
        
    def animate(self):
        self.angle = (self.angle + 2) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        cx, cy = self.width() // 2, self.height()
        # Draw half-circle dome
        radius = 180
        
        # Clip to half circle
        painter.setClipRect(0, 0, self.width(), self.height())
        
        # Background Grid
        grid_pen = QPen(QColor(REL_COLORS['teal_dark']), 1)
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)
        
        # Radial lines
        for i in range(0, 180, 15):
            rad = math.radians(i + 180)
            px = cx + math.cos(rad) * radius
            py = cy + math.sin(rad) * radius
            painter.drawLine(cx, cy, int(px), int(py))
            
        # Arcs
        for r in range(40, radius, 40):
            painter.drawArc(cx - r, cy - r, r*2, r*2, 0, 180 * 16)
            
        # Sweep
        sweep_pen = QPen(QColor(REL_COLORS['teal_bright']), 2)
        painter.setPen(sweep_pen)
        rad_sweep = math.radians(self.angle + 180) # +180 to start from left
        # Ping pong sweep between 0 and 180? Or generic rotation.
        # Let's do a constrained radar sweep
        sweep_angle = 180 + abs(180 - (self.angle % 360)) # Simple oscillation
        
        sx = cx + math.cos(math.radians(sweep_angle)) * radius
        sy = cy + math.sin(math.radians(sweep_angle)) * radius
        painter.drawLine(cx, cy, int(sx), int(sy))
        
        # Anomalies
        painter.setBrush(QBrush(QColor(REL_COLORS['alert'])))
        painter.setPen(Qt.PenStyle.NoPen)
        anomanies = [(60, 100), (120, 150), (90, 80)]
        for a_ang, a_dist in anomanies:
             ax = cx + math.cos(math.radians(a_ang + 180)) * a_dist
             ay = cy + math.sin(math.radians(a_ang + 180)) * a_dist
             painter.drawEllipse(QPointF(ax, ay), 3, 3)

class RelativityConsole(QWidget):
    """
    Main custom widget depicting the complex curved console
    """
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        
        # 1. Top Arch "Eyebrow"
        path_arch = QPainterPath()
        path_arch.moveTo(0, 80)
        path_arch.lineTo(w*0.35, 20)
        path_arch.lineTo(w*0.65, 20)
        path_arch.lineTo(w, 80)
        path_arch.lineTo(w, 110)
        path_arch.lineTo(w*0.67, 50)
        path_arch.lineTo(w*0.33, 50)
        path_arch.lineTo(0, 110)
        path_arch.closeSubpath()
        
        grad_arch = QLinearGradient(0, 0, w, 0)
        grad_arch.setColorAt(0, QColor(REL_COLORS['teal_dark']))
        grad_arch.setColorAt(0.5, QColor(REL_COLORS['teal_bright']))
        grad_arch.setColorAt(1, QColor(REL_COLORS['teal_dark']))
        
        painter.setBrush(grad_arch)
        painter.setPen(QPen(QColor(REL_COLORS['teal_bright']), 2))
        painter.drawPath(path_arch)
        
        # 2. Side Wings
        # Left Wing
        path_l = QPainterPath()
        path_l.moveTo(0, 120)
        path_l.lineTo(w*0.2, 85)
        path_l.lineTo(w*0.25, 600)
        path_l.lineTo(0, 500)
        path_l.closeSubpath()
        
        painter.setBrush(QColor(REL_COLORS['teal_dark']))
        painter.drawPath(path_l)
        
        # Right Wing
        path_r = QPainterPath()
        path_r.moveTo(w, 120)
        path_r.lineTo(w*0.8, 85)
        path_r.lineTo(w*0.75, 600)
        path_r.lineTo(w, 500)
        path_r.closeSubpath()
        
        painter.drawPath(path_r)
        
        # 3. Connection Lines
        pen_line = QPen(QColor(REL_COLORS['grey_light']), 3)
        painter.setPen(pen_line)
        painter.drawLine(int(w*0.35), 20, int(w*0.35), 600)
        painter.drawLine(int(w*0.65), 20, int(w*0.65), 600)

class LCARS29thCentury(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USS RELATIVITY - BRIDGE STATION")
        self.setGeometry(100, 100, 1400, 800)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(f"background-color: {REL_COLORS['bg']};")
        
        self.init_ui()
        
    def init_ui(self):
        # Base container layered with console graphics
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layer 1: The drawn console shape
        self.console_bg = RelativityConsole(central)
        self.console_bg.setGeometry(0, 0, 1400, 800)
        
        # Layer 2: Widgets placed on top of the drawing
        # We'll use absolute positioning or layouts that approximate the alignment
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Top Header Area
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        title = QLabel("USS RELATIVITY - TEMPORAL OPERATIONS")
        title.setStyleSheet(f"color: {REL_COLORS['teal_bright']}; font-family: 'Impact'; font-size: 24px; letter-spacing: 4px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        main_layout.addSpacing(40)
        
        # Mid Section
        mid_layout = QHBoxLayout()
        
        # LEFT STATION
        left_station = QWidget()
        left_layout = QGridLayout(left_station)
        # Button array
        for i in range(10):
            for j in range(3):
                btn = RelativityButton()
                left_layout.addWidget(btn, i, j)
        mid_layout.addWidget(left_station)
        
        # CENTER RADAR
        center_station = QVBoxLayout()
        self.radar = TemporalRadar()
        center_station.addWidget(self.radar, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        
        # Center readout
        readout = QLabel("TEMPORAL VARIANCE DETECTED\nEPOCH: 29.7\nSTATUS: REDUNDANT")
        readout.setStyleSheet(f"color: {REL_COLORS['text']}; font-family: 'Consolas'; font-size: 14px; background: rgba(0,0,0,100); padding: 10px;")
        readout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_station.addWidget(readout)
        
        mid_layout.addLayout(center_station)
        
        # RIGHT STATION
        right_station = QWidget()
        right_layout = QVBoxLayout(right_station)
        
        # Top controls
        top_cluster = QGridLayout()
        labels = ["CHRON", "FLUX", "VORTEX", "LOCK"]
        for i, lab in enumerate(labels):
            btn = RelativityButton(lab, color=REL_COLORS['grey_light'])
            top_cluster.addWidget(btn, i // 2, i % 2)
        right_layout.addLayout(top_cluster)
        
        right_layout.addStretch()
        
        # Exit
        exit_btn = RelativityButton("TERMINATE", color=REL_COLORS['alert'])
        exit_btn.clicked.connect(self.close)
        exit_btn.setFixedHeight(40)
        right_layout.addWidget(exit_btn)
        
        mid_layout.addWidget(right_station)
        
        main_layout.addLayout(mid_layout)
        main_layout.addStretch()
        
    def resizeEvent(self, event):
        # Resize background drawing to match window
        self.console_bg.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = LCARS29thCentury()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
