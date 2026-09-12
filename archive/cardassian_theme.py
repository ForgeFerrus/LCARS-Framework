#!/usr/bin/env python3
"""
Cardassian Interface Components
Authentic Cardassian Union styling for LCARS Framework (DS9 Era).
Designed to match the "standalone component" standard used in Romulan module.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QLinearGradient

# --- CONSTANTS ---
CARDASSIAN_FONT = "Impact"  # Strong, authoritarian font
CARDASSIAN_OCHRE = "#B8860B"     # DarkGoldenrod
CARDASSIAN_ORANGE = "#D2691E"    # Chocolate
CARDASSIAN_RUST = "#8B4513"      # SaddleBrown
CARDASSIAN_DARK = "#2F2F2F"      # Dark Grey background
CARDASSIAN_TEAL = "#008B8B"      # DarkCyan (secondary accents)
CARDASSIAN_TEXT = "#FFD700"      # Gold text

class CardassianFrame(QFrame):
    """
    Base container with Cardassian styling (Union colors).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {CARDASSIAN_DARK};
                border: 2px solid {CARDASSIAN_RUST};
                color: {CARDASSIAN_TEXT};
            }}
        """)

class CardassianHeader(QWidget):
    """
    Top header bar with the Cardassian "Fish Head" / Elliptical shape.
    """
    def __init__(self, title="CENTRAL COMMAND", parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self.title = title
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Gradient Background
        gradient = QLinearGradient(0, 0, 0, h)
        gradient.setColorAt(0, QColor(CARDASSIAN_OCHRE).darker(120))
        gradient.setColorAt(1, QColor(CARDASSIAN_RUST))
        
        path = QPainterPath()
        # Cardassian "Spoon" / "Fish Head" motif
        # Start bottom left
        path.moveTo(0, h)
        path.lineTo(0, h-40)
        # Curve up to top center
        path.quadTo(w * 0.25, 0, w * 0.5, 10)
        # Curve down to right
        path.quadTo(w * 0.75, 0, w, h-40)
        path.lineTo(w, h)
        path.closeSubpath()
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(CARDASSIAN_ORANGE), 2))
        painter.drawPath(path)
        
        # Decorative "Eye" in center
        eye_rect = QPoint(int(w/2), 40)
        painter.setBrush(QColor(CARDASSIAN_TEAL))
        painter.drawEllipse(eye_rect, 15, 15)
        
        # Text
        painter.setPen(QColor(CARDASSIAN_DARK))
        font = QFont(CARDASSIAN_FONT, 20, QFont.Weight.Bold)
        painter.setFont(font)
        # Draw text below eye
        painter.drawText(0, 55, w, 40, Qt.AlignmentFlag.AlignCenter, self.title)

class CardassianButton(QPushButton):
    """
    Curved segmented button (Cardassian control panel style).
    """
    def __init__(self, text, parent=None, color=CARDASSIAN_OCHRE):
        super().__init__(text, parent)
        self.color_base = color
        self.setMinimumHeight(55)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bg = QColor(self.color_base)
        if self.isDown():
            bg = bg.darker(130)
        elif self.underMouse():
            bg = bg.lighter(120)
            
        rect = self.rect()
        path = QPainterPath()
        
        # Unique Shape: Rect with one curved side or angled cut
        # Simple Cardassian Pill: Flat top/bottom, curved sides inward
        w = rect.width()
        h = rect.height()
        
        path.moveTo(10, 0)
        path.lineTo(w-10, 0)
        path.lineTo(w, h/2) # Point out
        path.lineTo(w-10, h)
        path.lineTo(10, h)
        path.lineTo(0, h/2) # Point out
        path.closeSubpath()
        
        painter.setBrush(bg)
        painter.setPen(QPen(QColor(CARDASSIAN_DARK), 2))
        painter.drawPath(path)
        
        painter.setPen(QColor(CARDASSIAN_DARK))
        painter.setFont(QFont(CARDASSIAN_FONT, 12, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

class CardassianDisplay(QWidget):
    """
    Data display field with ribbed border.
    """
    def __init__(self, title, content="...", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Header Label
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: {CARDASSIAN_ORANGE}; font-weight: bold; font-family: {CARDASSIAN_FONT};")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.lbl_title)
        
        # Content Box
        self.text_content = QTextEdit()
        self.text_content.setPlainText(content)
        self.text_content.setReadOnly(True)
        self.text_content.setStyleSheet(f"""
            background-color: #1a1a1a;
            color: {CARDASSIAN_TEAL};
            border: 1px solid {CARDASSIAN_RUST};
            font-family: Consolas;
        """)
        self.layout.addWidget(self.text_content)
        
    def paintEvent(self, event):
        # Optional: draw ribbed sidebar if needed
        pass

class CardassianSystem(QMainWindow):
    """
    Main Window demonstrating Cardassian components.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CARDASSIAN UNION TERMINAL")
        self.resize(1024, 768)
        self.setStyleSheet(f"background-color: {CARDASSIAN_DARK};")
        
        container = QWidget()
        self.setCentralWidget(container)
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0,0,0,0)
        
        # 1. Header
        self.header = CardassianHeader("OBSIDIAN ORDER DATABANK")
        main_layout.addWidget(self.header)
        
        # 2. Body Area with Sidebar
        body_widget = QWidget()
        body_layout = QHBoxLayout(body_widget)
        
        # Left Sidebar (Controls)
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet(f"background-color: {CARDASSIAN_RUST}; border-right: 4px solid {CARDASSIAN_OCHRE};")
        side_layout = QVBoxLayout(sidebar)
        
        btn_labels = ["SYSTEM STATUS", "SURVEILLANCE", "PRISONER LOGS", "INTERROGATION", "SECURITY LOCK"]
        colors = [CARDASSIAN_OCHRE, CARDASSIAN_ORANGE, CARDASSIAN_OCHRE, CARDASSIAN_ORANGE, "#AA0000"]
        
        for i, lbl in enumerate(btn_labels):
            btn = CardassianButton(lbl, color=colors[i])
            side_layout.addWidget(btn)
            
        side_layout.addStretch()
        body_layout.addWidget(sidebar)
        
        # Main Display Area
        display_area = QWidget()
        disp_layout = QGridLayout(display_area)
        
        self.screen_1 = CardassianDisplay("SECTOR SCAN", "No anomalies detected in the Demilitarized Zone.\nBajoran traffic normal.")
        self.screen_2 = CardassianDisplay("RESOURCE ALLOCATION", "Energy Grid: 98%\nReplicator Rations: RESTRICTED")
        self.screen_3 = CardassianDisplay("ALERTS", "STATUS: YELLOW\nPotential Maquis activity in sector 4.")
        
        disp_layout.addWidget(self.screen_1, 0, 0)
        disp_layout.addWidget(self.screen_2, 0, 1)
        disp_layout.addWidget(self.screen_3, 1, 0, 1, 2)
        
        body_layout.addWidget(display_area)
        
        main_layout.addWidget(body_widget)
        
        # Footer
        footer = QLabel("FOR THE STATE")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"background-color: {CARDASSIAN_RUST}; color: {CARDASSIAN_DARK}; font-weight: bold; padding: 5px;")
        main_layout.addWidget(footer)

def main():
    app = QApplication(sys.argv)
    window = CardassianSystem()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
