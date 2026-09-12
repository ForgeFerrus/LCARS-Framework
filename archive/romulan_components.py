#!/usr/bin/env python3
"""
Romulan Interface Components
Authentic Romulan Star Empire styling for LCARS Framework.
Designed to meet the "one chance to redo it" standard.
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QLinearGradient

# --- CONSTANTS ---
ROMULAN_FONT = "Impact" # Or "Arial Black" as a fallback for blocky look
ROMULAN_GREEN_DARK = "#003300"
ROMULAN_GREEN_MID = "#006633"
ROMULAN_GREEN_LIGHT = "#33CC66"
ROMULAN_TEAL = "#008080"
ROMULAN_GREY = "#2F4F4F" 
ROMULAN_TEXT_COLOR = "#99FF99"

class RomulanFrame(QFrame):
    """
    Base container with Romulan-styled borders (angular, no rounded corners).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {ROMULAN_GREEN_DARK};
                border: 2px solid {ROMULAN_GREEN_MID};
                color: {ROMULAN_TEXT_COLOR};
            }}
        """)

class RomulanHeader(QWidget):
    """
    Top header bar with the Romulan emblem shape (Trapezoidal feel).
    """
    def __init__(self, title="IMPERIAL ACCESS", parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.title = title
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background: Dark Green Gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(ROMULAN_GREEN_MID))
        gradient.setColorAt(1, QColor(ROMULAN_GREEN_DARK))
        
        # Complex Shape
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(width, 0)
        path.lineTo(width, height)
        path.lineTo(width - 40, height) # Notch right
        path.lineTo(width - 60, height - 20) # Angle up
        path.lineTo(60, height - 20) # Flat mid
        path.lineTo(40, height) # Angle down
        path.lineTo(0, height)
        path.closeSubpath()
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Text
        painter.setPen(QColor(ROMULAN_TEXT_COLOR))
        font = QFont(ROMULAN_FONT, 24, QFont.Weight.Bold)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop, self.title)

class RomulanButton(QPushButton):
    """
    Hexagonal/Angled button.
    """
    def __init__(self, text, parent=None, color=ROMULAN_GREEN_MID):
        super().__init__(text, parent)
        self.color_base = color
        self.setMinimumHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_pressed = self.isDown()
        is_hover = self.underMouse()
        
        # Color Logic
        bg_color = QColor(self.color_base)
        if is_pressed:
            bg_color = bg_color.lighter(150)
        elif is_hover:
            bg_color = bg_color.lighter(120)
            
        width = self.width()
        height = self.height()
        offset = 15 # Angle depth
        
        # Shape: Cut corners (Octagon-ish / Hex-ish)
        path = QPainterPath()
        path.moveTo(offset, 0)
        path.lineTo(width, 0)
        path.lineTo(width, height - offset)
        path.lineTo(width - offset, height)
        path.lineTo(0, height)
        path.lineTo(0, offset)
        path.closeSubpath()
        
        # Draw Fill
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(QColor(ROMULAN_TEXT_COLOR), 1))
        painter.drawPath(path)
        
        # Draw Text
        painter.setPen(QColor("black") if is_pressed else QColor(ROMULAN_TEXT_COLOR))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class RomulanDisplay(QFrame):
    """
    Line graph / status display area.
    """
    def __init__(self, text="STATUS", parent=None):
        super().__init__(parent)
        self.text = text
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: black; border: 1px solid #336633;")
        
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(ROMULAN_GREEN_LIGHT))
        font = QFont("Consolas", 10)
        painter.setFont(font)
        
        # Grid lines
        painter.setPen(QPen(QColor(ROMULAN_GREEN_DARK), 1, Qt.PenStyle.DotLine))
        for i in range(0, self.width(), 20):
            painter.drawLine(i, 0, i, self.height())
        for i in range(0, self.height(), 20):
            painter.drawLine(0, i, self.width(), i)
            
        # Random data line
        painter.setPen(QPen(QColor(ROMULAN_GREEN_LIGHT), 2))
        path = QPainterPath()
        path.moveTo(0, self.height()/2)
        import random
        for i in range(0, self.width(), 10):
            path.lineTo(i, self.height()/2 + random.randint(-40, 40))
        painter.drawPath(path)
        
        # Label
        painter.setPen(QColor(ROMULAN_TEXT_COLOR))
        painter.drawText(10, 20, self.text)

class RomulanComponentsDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Romulan Imperial Interface")
        self.setStyleSheet("background-color: #050505;")
        self.resize(1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 1. Header
        header = RomulanHeader("D'DERIDEX TACTICAL CONTROL")
        main_layout.addWidget(header)
        
        # 2. Main Body: 3 Columns
        body_layout = QHBoxLayout()
        
        # -- Left Column (Navigation) --
        left_col = QVBoxLayout()
        for label in ["NAV-01", "NAV-02", "SENSORS", "COMMS"]:
            btn = RomulanButton(label)
            left_col.addWidget(btn)
        left_col.addStretch()
        body_layout.addLayout(left_col, 1)
        
        # -- Center Column (Main View) --
        center_col = QVBoxLayout()
        center_col.setSpacing(10)
        
        # Large Display
        display = RomulanDisplay("CLOAKING FIELD STATUS: ENGAGED")
        center_col.addWidget(display, 2)
        
        # Status Bars
        status_grid = QGridLayout()
        labels = ["WARP CORE", "SINGULARITY", "SHIELDS", "WEAPONS"]
        for i, lab in enumerate(labels):
            frame = QFrame()
            frame.setStyleSheet(f"background-color: {ROMULAN_GREEN_DARK}; border-left: 5px solid {ROMULAN_GREEN_LIGHT};")
            frame.setFixedHeight(40)
            l = QLabel(lab)
            l.setStyleSheet(f"color: {ROMULAN_TEXT_COLOR}; padding-left: 10px; font-weight: bold;")
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(0,0,0,0)
            fl.addWidget(l)
            status_grid.addWidget(frame, i // 2, i % 2)
            
        center_col.addLayout(status_grid, 1)
        body_layout.addLayout(center_col, 3)
        
        # -- Right Column (Tactical) --
        right_col = QVBoxLayout()
        alert_btn = RomulanButton("RED ALERT", color="#800000") # Red for alert
        right_col.addWidget(alert_btn)
        
        cloak_btn = RomulanButton("DISENGAGE CLOAK")
        right_col.addWidget(cloak_btn)
        
        fire_btn = RomulanButton("FIRE DISRUPTORS", color="#CC6600") # Orange
        right_col.addWidget(fire_btn)
        
        right_col.addStretch()
        body_layout.addLayout(right_col, 1)
        
        main_layout.addLayout(body_layout)
        
        # 3. Footer
        footer = QLabel("IMPERIAL ROMULAN WARBIRD HAAKONA")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {ROMULAN_GREEN_MID}; font-size: 12px; letter-spacing: 5px;")
        main_layout.addWidget(footer)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RomulanComponentsDemo()
    window.show()
    sys.exit(app.exec())
        
    def setup_grid(self):
        """Setup Romulan grid display"""
        layout = QGridLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(2)
        
        for i, (text, status) in enumerate(self.grid_data):
            item = RomulanDisplay(text, "data")
            if status == "active":
                item.setStyleSheet("""
                    QLabel {
                        color: #001144;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #00FFAA, stop:0.5 #00FFCC, stop:1 #00FFAA);
                        border: 1px solid #00FFAA;
                        padding: 3px 6px;
                        font-size: 7px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-family: 'Arial', sans-serif;
                        border-radius: 3px;
                    }
                """)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(item, i // 5, i % 5)


class RomulanStatusPanel(QFrame):
    """Individual Romulan status panel component"""
    
    def __init__(self, status_items=None, parent=None):
        super().__init__(parent)
        self.status_items = status_items or []
        self.setup_status_panel()
        
    def setup_status_panel(self):
        """Setup Romulan status panel"""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.15 #001144, stop:0.3 #000822,
                    stop:0.45 #001144, stop:0.6 #000822, stop:0.75 #001144, stop:1 #000822);
                border: 1px solid #00AA88;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(3)
        
        for text, item_type in self.status_items:
            item = RomulanDisplay(text, item_type)
            layout.addWidget(item)


class RomulanControlPanel(QFrame):
    """Individual Romulan control panel component"""
    
    def __init__(self, controls=None, parent=None):
        super().__init__(parent)
        self.controls = controls or []
        self.setup_control_panel()
        
    def setup_control_panel(self):
        """Setup Romulan control panel"""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.2 #001144, stop:0.4 #000822,
                    stop:0.6 #001144, stop:0.8 #000822, stop:1 #001144);
                border: 2px solid #00FFAA;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        for text, btn_type in self.controls:
            btn = RomulanButton(text, btn_type)
            layout.addWidget(btn)


class RomulanMainDisplay(QFrame):
    """Individual Romulan main display component"""
    
    def __init__(self, title="MAIN DISPLAY", content="", parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.setup_main_display()
        
    def setup_main_display(self):
        """Setup Romulan main display"""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.1 #001144, stop:0.2 #000822,
                    stop:0.3 #001144, stop:0.4 #000822, stop:0.5 #001144,
                    stop:0.6 #000822, stop:0.7 #001144, stop:0.8 #000822,
                    stop:0.9 #001144, stop:1 #000822);
                border: 3px solid #00FFAA;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)
        
        # Title
        title_label = RomulanDisplay(self.title, "title")
        layout.addWidget(title_label)
        
        # Content area
        content_area = QLabel(self.content)
        content_area.setStyleSheet("""
            QLabel {
                color: #00FFCC;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #001144, stop:0.2 #002266, stop:0.4 #001144,
                    stop:0.6 #002266, stop:0.8 #001144, stop:1 #002266);
                padding: 20px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #00AA88;
                border-radius: 6px;
                text-transform: uppercase;
                font-family: 'Arial', sans-serif;
            }
        """)
        content_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content_area)


# Demonstration of individual components
class RomulanComponentDemo(QWidget):
    """Demonstration of individual Romulan components"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Romulan Components Demo")
        self.setGeometry(100, 100, 800, 600)
        self.setup_demo()
        
    def setup_demo(self):
        """Setup component demonstration"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = RomulanDisplay("ROMULAN COMPONENTS", "title")
        main_layout.addWidget(title)
        
        # Button types
        button_section = QHBoxLayout()
        button_section.addWidget(QLabel("Buttons:"))
        button_section.addWidget(RomulanButton("PRIMARY", "primary"))
        button_section.addWidget(RomulanButton("SECONDARY", "secondary"))
        button_section.addWidget(RomulanButton("TACTICAL", "tactical"))
        main_layout.addLayout(button_section)
        
        # Display types
        display_section = QHBoxLayout()
        display_section.addWidget(QLabel("Displays:"))
        display_section.addWidget(RomulanDisplay("STATUS", "status"))
        display_section.addWidget(RomulanDisplay("DATA", "data"))
        display_section.addWidget(RomulanDisplay("ALERT", "alert"))
        main_layout.addLayout(display_section)
        
        # Panel types
        panel_section = QHBoxLayout()
        panel_section.addWidget(QLabel("Panels:"))
        
        main_panel = RomulanPanel("main")
        main_panel.setFixedSize(100, 60)
        panel_section.addWidget(main_panel)
        
        secondary_panel = RomulanPanel("secondary")
        secondary_panel.setFixedSize(100, 60)
        panel_section.addWidget(secondary_panel)
        
        minor_panel = RomulanPanel("minor")
        minor_panel.setFixedSize(100, 60)
        panel_section.addWidget(minor_panel)
        
        main_layout.addLayout(panel_section)
        
        # Grid display
        grid_data = [
            ("SYS-1", "normal"), ("SYS-2", "active"), ("SYS-3", "normal"),
            ("SYS-4", "normal"), ("SYS-5", "normal"), ("SYS-6", "normal"),
            ("SYS-7", "normal"), ("SYS-8", "normal"), ("SYS-9", "normal")
        ]
        grid_display = RomulanGridDisplay(grid_data)
        main_layout.addWidget(grid_display)
        
        # Status panel
        status_items = [
            ("SHIELDS: 100%", "status"),
            ("WEAPONS: READY", "status"),
            ("CLOAK: ENGAGED", "alert"),
            ("WARP: STANDBY", "data")
        ]
        status_panel = RomulanStatusPanel(status_items)
        main_layout.addWidget(status_panel)
        
        # Control panel
        controls = [
            ("WEAPONS", "primary"),
            ("SHIELDS", "secondary"),
            ("CLOAK", "tactical")
        ]
        control_panel = RomulanControlPanel(controls)
        main_layout.addWidget(control_panel)
        
        # Main display
        main_display = RomulanMainDisplay("QUANTUM CORE", "ENERGY LEVEL: 98.7%")
        main_layout.addWidget(main_display)
        
        # Apply background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.3 #001144, stop:0.7 #000822, stop:1 #001144);
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the component demo
    demo = RomulanComponentDemo()
    demo.show()
    
    sys.exit(app.exec())
