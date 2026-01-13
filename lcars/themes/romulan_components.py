#!/usr/bin/env python3
"""Romulan LCARS Components - Individual Elements"""

import sys
from PyQt6.QtWidgets import (QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QGridLayout, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QLinearGradient, QColor, QPen

class RomulanButton(QPushButton):
    """Individual Romulan button component"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan button styling"""
        self.setMinimumHeight(35)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #004433, stop:0.3 #006655, stop:0.7 #008877, stop:1 #004433);
                    color: #00FFAA;
                    border: 2px solid #00FFAA;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 10px;
                    font-family: 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #006655, stop:0.3 #008877, stop:0.7 #00AA99, stop:1 #006655);
                    color: #001144;
                    border-color: #00FFCC;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #002233, stop:0.3 #004455, stop:0.7 #006677, stop:1 #002233);
                    color: #00FFAA;
                    border-color: #006644;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #002244, stop:0.5 #003366, stop:1 #002244);
                    color: #00FFAA;
                    border: 1px solid #006644;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 9px;
                    font-family: 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #003366, stop:0.5 #004477, stop:1 #003366);
                    color: #00FFCC;
                    border-color: #008866;
                }
            """)
        elif self.button_type == "tactical":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                    color: #001144;
                    border: 3px solid #00FFAA;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 11px;
                    font-family: 'Arial', sans-serif;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FFCC, stop:0.3 #FFFFFF, stop:0.7 #00FFCC, stop:1 #FFFFFF);
                    color: #001144;
                    border-color: #FFFFFF;
                }
            """)


class RomulanPanel(QFrame):
    """Individual Romulan panel component"""
    
    def __init__(self, panel_type="standard", parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan panel styling"""
        if self.panel_type == "main":
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
        elif self.panel_type == "secondary":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000822, stop:0.2 #001144, stop:0.4 #000822,
                        stop:0.6 #001144, stop:0.8 #000822, stop:1 #001144);
                    border: 2px solid #00FFAA;
                    border-radius: 10px;
                }
            """)
        elif self.panel_type == "minor":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000822, stop:0.15 #001144, stop:0.3 #000822,
                        stop:0.45 #001144, stop:0.6 #000822, stop:0.75 #001144, stop:1 #000822);
                    border: 1px solid #00AA88;
                    border-radius: 8px;
                }
            """)


class RomulanDisplay(QLabel):
    """Individual Romulan display component"""
    
    def __init__(self, text="", display_type="standard", parent=None):
        super().__init__(text, parent)
        self.display_type = display_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan display styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.display_type == "title":
            self.setStyleSheet("""
                QLabel {
                    color: #001144;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                    padding: 8px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #00FFAA;
                    border-radius: 8px;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                }
            """)
        elif self.display_type == "status":
            self.setStyleSheet("""
                QLabel {
                    color: #00FFCC;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #004433, stop:0.5 #006655, stop:1 #004433);
                    padding: 6px 12px;
                    font-size: 10px;
                    font-weight: bold;
                    border: 1px solid #00AA88;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                    border-radius: 4px;
                }
            """)
        elif self.display_type == "data":
            self.setStyleSheet("""
                QLabel {
                    color: #00FFAA;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #002244, stop:0.5 #003366, stop:1 #002244);
                    padding: 4px 8px;
                    font-size: 8px;
                    font-weight: bold;
                    border: 1px solid #006644;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                    border-radius: 3px;
                }
            """)
        elif self.display_type == "alert":
            self.setStyleSheet("""
                QLabel {
                    color: #001144;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FFAA, stop:0.5 #00FFCC, stop:1 #00FFAA);
                    padding: 6px 12px;
                    font-size: 9px;
                    font-weight: bold;
                    border: 2px solid #00FFAA;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                    border-radius: 5px;
                }
            """)


class RomulanGridDisplay(QWidget):
    """Individual Romulan grid display component"""
    
    def __init__(self, grid_data=None, parent=None):
        super().__init__(parent)
        self.grid_data = grid_data or []
        self.setup_grid()
        
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
