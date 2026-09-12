
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QLinearGradient

# --- CONSTANTS ---
KLINGON_FONT = "Impact"   # Bold and aggressive
KLINGON_RED_DARK = "#440000"
KLINGON_RED_MAIN = "#990000"
KLINGON_RED_BRIGHT = "#FF0000"
KLINGON_GREY = "#333333"
KLINGON_METAL = "#666666"
KLINGON_GOLD = "#CC9900"
KLINGON_BLACK = "#110505"

class KlingonFrame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {KLINGON_BLACK};
                border: 2px solid {KLINGON_RED_MAIN};
                color: {KLINGON_RED_BRIGHT};
            }}
        """)

class KlingonHeader(QWidget):

    def __init__(self, title="IKS ROTARRAN", parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.title = title
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Gradient Background (Blood Red to Black)
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor(KLINGON_RED_MAIN))
        gradient.setColorAt(1, QColor(KLINGON_RED_DARK))
        
        path = QPainterPath()
        
        # Klingon Blade Shape
        # Start top left
        path.moveTo(0, 0)
        # Sharp inner cut
        path.lineTo(w * 0.2, 0)
        path.lineTo(w * 0.25, h * 0.6) # Down spike
        path.lineTo(w * 0.75, h * 0.6) # Flat middle
        path.lineTo(w * 0.8, 0) # Up spike
        path.lineTo(w, 0)
        
        # Bottom edge
        path.lineTo(w, h * 0.8)
        # Sharp serrations
        path.lineTo(w * 0.9, h)
        path.lineTo(w * 0.1, h)
        path.lineTo(0, h * 0.8)
        
        path.closeSubpath()
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(KLINGON_RED_BRIGHT), 2))
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(KLINGON_BLACK))
        font = QFont(KLINGON_FONT, 28, QFont.Weight.Bold)
        painter.setFont(font)
        # Draw text in the middle gap
        painter.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, self.title)

class KlingonButton(QPushButton):

    def __init__(self, text, parent=None, is_alert=False):
        super().__init__(text, parent)
        self.is_alert = is_alert
        self.setMinimumHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Color Logic
        base_col = KLINGON_RED_MAIN if not self.is_alert else KLINGON_GOLD
        
        if self.isDown():
            bg_color = QColor(base_col).lighter(150)
        elif self.underMouse():
            bg_color = QColor(base_col).lighter(120)
        else:
            bg_color = QColor(base_col)
            
        rect = self.rect()
        path = QPainterPath()
        
        w = rect.width()
        h = rect.height()
        
        # Shape: Trapezoid / Angular Blade
        #   /----\
        #  |      |
        #   \____/
        
        offset = 15
        
        path.moveTo(offset, 0)
        path.lineTo(w - offset, 0)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.closeSubpath()
        
        painter.setBrush(bg_color)
        pen = QPen(QColor(KLINGON_BLACK), 2)
        if self.is_alert:
            pen = QPen(QColor("#FFFFFF"), 2)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(KLINGON_BLACK))
        if self.is_alert:
             painter.setPen(QColor(KLINGON_RED_DARK))
             
        painter.setFont(QFont(KLINGON_FONT, 14, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class KlingonDisplay(QWidget):

    def __init__(self, title, content="...", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5,5,5,5)
        
        self.lbl = QLabel(title)
        self.lbl.setStyleSheet(f"color: {KLINGON_RED_BRIGHT}; font-weight: bold; font-family: {KLINGON_FONT};")
        layout.addWidget(self.lbl)
        
        self.field = QLabel(content)
        self.field.setWordWrap(True)
        self.field.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.field.setStyleSheet(f"""
            background-color: {KLINGON_RED_DARK};
            color: {KLINGON_GOLD};
            border: 2px solid {KLINGON_RED_MAIN};
            padding: 10px;
            font-family: Consolas;
            font-weight: bold;
        """)
        layout.addWidget(self.field)
        
    def paintEvent(self, event):
        # Draw tactical overlay?
        pass

class KlingonDaggerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(60)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        w = self.width()
        h = self.height()
        
        # Tri-blade pattern repeated
        gap = 40
        for y in range(0, h, gap):
             path.moveTo(0, y)
             path.lineTo(w, y + (gap/2))
             path.lineTo(0, y + gap)
        
        painter.setBrush(QColor(KLINGON_METAL))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

class KlingonSystem(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("KLINGON DEFENSE FORCE TACTICAL")
        self.resize(1024, 768)
        self.setStyleSheet(f"background-color: {KLINGON_BLACK};")
        
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 1. Header
        self.header = KlingonHeader("TACTICAL DISPLAY - BOP HEGH'TA")
        main_layout.addWidget(self.header)
        
        # 2. Body Area
        body_layout = QHBoxLayout()
        
        # Left Dagger Decoration
        body_layout.addWidget(KlingonDaggerPanel())
        
        # Center Console
        center_widget = QWidget()
        center_grid = QGridLayout(center_widget)
        center_grid.setSpacing(15)
        
        # Tactical Screens
        self.screen_shields = KlingonDisplay("SHIELD STATUS", "FORWARD: 100%\nAFT: 100%\nPORT: 100%\nSTARBOARD: 100%")
        self.screen_weapons = KlingonDisplay("WEAPONS ARRAY", "DISRUPTORS: CHARGED\nTORPEDOES: 20\nCLOAK: STANDBY")
        self.screen_log = KlingonDisplay("BATTLE LOG", "NO TARGETS.\nPATROLLING SECTOR 001.\nWAITING FOR ORDERS.")
        
        center_grid.addWidget(self.screen_shields, 0, 0)
        center_grid.addWidget(self.screen_weapons, 0, 1)
        center_grid.addWidget(self.screen_log, 1, 0, 1, 2)
        
        body_layout.addWidget(center_widget)
        
        # Right Controls
        controls = QVBoxLayout()
        btn_fire = KlingonButton("FIRE DISRUPTORS", is_alert=True)
        btn_torp = KlingonButton("FIRE TORPEDO", is_alert=True)
        btn_cloak = KlingonButton("ENGAGE CLOAK")
        btn_scan = KlingonButton("SENSOR SWEEP")
        btn_hail = KlingonButton("HAIL TARGET")
        
        controls.addWidget(btn_fire)
        controls.addWidget(btn_torp)
        controls.addSpacing(20)
        controls.addWidget(btn_cloak)
        controls.addWidget(btn_scan)
        controls.addWidget(btn_hail)
        controls.addStretch()
        
        body_layout.addLayout(controls)
        
        main_layout.addLayout(body_layout)
        
        # Footer
        footer = QLabel("QAPLA'!")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {KLINGON_RED_BRIGHT}; font-size: 24px; font-weight: bold; font-family: {KLINGON_FONT};")
        main_layout.addWidget(footer)

def main():
    app = QApplication(sys.argv)
    window = KlingonSystem()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
