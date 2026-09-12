
"""
LCARS Interface - Classic 23rd Century (TOS)
The Original Series Style (2260s)
"""

import sys
import random
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                           QFrame, QGridLayout, QPushButton, QStackedWidget)
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QPainterPath, QBrush, QFontDatabase
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty, QRectF

# --- PATH SETUP ---
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- TOS PALETTE (AUTHENTIC 1960s COLORS) ---
TOS_COLORS = {
    "bg": "#000000",
    "primary_orange": "#FF4400",  # Engineering / Safety
    "primary_red": "#CC0000",     # Alert
    "primary_blue": "#6688CC",    # Science / Spock
    "secondary_blue": "#88AAFF",
    "indicator_green": "#66CC66",
    "indicator_yellow": "#FFCC00",
    "monitor_bg": "#111111",      # Dark grey for screens
    "text": "#FFD700"             # Gold text often used in displays
}

class TOSButton(QPushButton):
    """
    Classic 'Jelly Bean' or 'Chiclet' rocker button.
    """
    def __init__(self, text, color="blue", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(60)
        self.setCheckable(True)
        
        # Color mapping
        self.base_color_code = TOS_COLORS.get(f"primary_{color}", TOS_COLORS["primary_blue"])
        self._color = QColor(self.base_color_code)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Determine color state
        if self.isDown() or self.isChecked():
            # Glowing / Lit state
            fill_color = self._color.lighter(130)
        else:
            # Standard Resin state
            fill_color = self._color
            
        # Draw Beveled Rect (The 'Jelly Bean' look)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 15, 15)
        
        # Main Fill
        painter.setBrush(fill_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Highlights (Topshine to simulate plastic)
        highlight_rect = QRectF(rect.x() + 5, rect.y() + 5, rect.width() - 10, rect.height() / 2 - 5)
        grad = QBrush(QColor(255, 255, 255, 60))
        painter.setBrush(grad)
        painter.drawRoundedRect(highlight_rect, 10, 10)
        
        # Text
        painter.setPen(QColor("black"))
        painter.setFont(QFont("Arial Black", 10, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())


class MedicalBar(QWidget):
    """
    Vertical Slider Bar (McCoy Style)
    Animates up and down randomly to simulate 'Bio-Readings'
    """
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.label = label
        self.value = 50.0 # 0-100
        self.target = 50.0
        self.setFixedWidth(60)
        self.setFixedHeight(250)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_reading)
        self.timer.start(100) # 10 FPS animation
        
    def update_reading(self):
        # Move value towards target
        diff = self.target - self.value
        self.value += diff * 0.1
        
        # Randomly change target occasionally
        if random.random() < 0.05:
            self.target = random.uniform(10, 90)
            
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Track line
        mid_x = self.width() // 2
        painter.setPen(QPen(QColor("white"), 2))
        painter.drawLine(mid_x, 10, mid_x, self.height() - 30)
        
        # Ticks
        for y in range(10, self.height() - 30, 20):
            painter.drawLine(mid_x - 5, y, mid_x + 5, y)
             
        # The Bar Indicator (Color changes based on height)
        bar_y = int(self.height() - 30 - ((self.height() - 40) * (self.value / 100)))
        
        # Color Logic (TOS colors: Red High, Green Mid, Yellow Low)
        c = QColor(TOS_COLORS["indicator_green"])
        if self.value > 80: c = QColor(TOS_COLORS["primary_red"])
        elif self.value < 20: c = QColor(TOS_COLORS["indicator_yellow"])
        
        painter.setBrush(c)
        painter.setPen(Qt.PenStyle.NoPen)
        # Draw triangular pointer or bar
        rect_w = 40
        painter.drawRect(mid_x - rect_w//2, bar_y, rect_w, 10)
        
        # Label
        painter.setPen(QColor(TOS_COLORS["text"]))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(0, self.height()-20, self.width(), 20, Qt.AlignmentFlag.AlignCenter, self.label)


class ViewerScreen(QFrame):
    """
    Main Viewscreen with rounded border
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            background-color: {TOS_COLORS['monitor_bg']}; 
            border: 4px solid {TOS_COLORS['primary_blue']};
            border-radius: 20px;
        """)
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(TOS_COLORS["secondary_blue"]))
        
        # Draw simple star field
        w, h = self.width(), self.height()
        import random
        painter.setPen(QColor("white"))
        for _ in range(20):
             x = random.randint(0, w)
             y = random.randint(0, h)
             painter.drawPoint(x, y)
             
        # Grid overlay (Tactical)
        painter.setPen(QPen(QColor(TOS_COLORS["text"]), 1, Qt.PenStyle.DotLine))
        painter.drawLine(w//2, 0, w//2, h)
        painter.drawLine(0, h//2, w, h//2)


class PCARS23Early(QMainWindow):
    """
    Classic TOS Interface (2265-2270)
    Based on the Enterprise Bridge control stations and Medical displays.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NCC-1701 BRIDGE STATION")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {TOS_COLORS['bg']};")
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main Layout: 3 Columns
        # Left: Systems Status (Buttons)
        # Center: Main Viewer / Readouts
        # Right: Medical / Bio Sensors (McCoy style)
        layout = QHBoxLayout(central)
        layout.setSpacing(20)
        
        # LEFT COL
        left_panel = QVBoxLayout()
        lbl_sys = QLabel("SYSTEMS CONTROL")
        lbl_sys.setStyleSheet("color: white; font-family: 'Arial Black'; font-size: 14pt;")
        left_panel.addWidget(lbl_sys)
        
        systems = ["TURBOLIFT", "TRANSPORTER", "COMMUNICATIONS", "GRAVITY", "SHIELDS", "PHASERS"]
        for s in systems:
            color = "orange" if s in ["PHASERS", "SHIELDS"] else "blue"
            if s == "COMMUNICATIONS": color = "red"
            
            btn = TOSButton(s, color=color)
            left_panel.addWidget(btn)
            
        left_panel.addStretch()
        
        # Return Button
        btn_exit = TOSButton("SYSTEM EXIT", color="primary_red")
        btn_exit.clicked.connect(self.close)
        left_panel.addWidget(btn_exit)
        
        layout.addLayout(left_panel, 1)
        
        # CENTER COL
        center_panel = QVBoxLayout()
        
        # Viewer
        self.viewer = ViewerScreen()
        center_panel.addWidget(self.viewer, 3)
        
        # Data Readout Area
        data_title = QLabel("SENSOR RECORDINGS")
        data_title.setStyleSheet("background-color: #CC4400; color: black; font-weight: bold; padding: 5px;")
        center_panel.addWidget(data_title)
        
        # Simulated Code Grid
        grid_frame = QFrame()
        grid = QGridLayout(grid_frame)
        for r in range(4):
            for c in range(4):
                val = random.randint(100, 999)
                lbl = QLabel(str(val))
                lbl.setStyleSheet(f"color: {TOS_COLORS['text']}; font-family: Courier; font-size: 12pt;")
                grid.addWidget(lbl, r, c)
        center_panel.addWidget(grid_frame, 2)
        
        layout.addLayout(center_panel, 3)
        
        # RIGHT COL (McCoy Style Biobed)
        right_panel = QVBoxLayout()
        lbl_bio = QLabel("LIFE SCIENCES")
        lbl_bio.setStyleSheet("color: white; font-family: 'Arial Black'; font-size: 14pt;")
        right_panel.addWidget(lbl_bio)
        
        # Big Red Circle Indicator
        monitor_frame = QFrame()
        monitor_frame.setFixedHeight(150)
        monitor_layout = QHBoxLayout(monitor_frame)
        
        self.pulse_light = QLabel() 
        self.pulse_light.setFixedSize(80, 80)
        self.pulse_light.setStyleSheet("background-color: #CC0000; border-radius: 40px;")
        monitor_layout.addWidget(self.pulse_light)
        
        right_panel.addWidget(monitor_frame)
        
        # Sliders
        sliders_layout = QHBoxLayout()
        sliders = ["PULSE", "RESP", "BRAIN", "CELL"]
        for sl in sliders:
            bar = MedicalBar(sl)
            sliders_layout.addWidget(bar)
            
        right_panel.addLayout(sliders_layout)
        right_panel.addStretch()
        
        layout.addLayout(right_panel, 2)


if __name__ == "__main__":
    app = sys.modules.get("PyQt6.QtWidgets").QApplication(sys.argv)
    window = PCARS23Early()
    window.show()
    sys.exit(app.exec())


