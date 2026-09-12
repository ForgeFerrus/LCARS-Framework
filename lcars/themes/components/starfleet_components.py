#!/usr/bin/env python3
"""Starfleet LCARS Components - 22nd Century Style"""

from PyQt6.QtWidgets import QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QLinearGradient, QColor


class StarfleetButton(QPushButton):
    """Authentic Starfleet LCARS button with 22nd century styling"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Starfleet button styling"""
        self.setMinimumHeight(40)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF9900;
                    color: #000000;
                    border: 2px solid #FFCC66;
                    border-radius: 20px;
                    padding: 8px 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FFCC66;
                    border-color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #FFB84D;
                    border-color: #FF9900;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    border: 2px solid #999999;
                    border-radius: 15px;
                    padding: 6px 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #999999;
                    border-color: #FFCC66;
                }
                QPushButton:pressed {
                    background-color: #808080;
                    border-color: #CCCCCC;
                }
            """)
        elif self.button_type == "warning":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF6600;
                    color: #FFFFFF;
                    border: 2px solid #FF9900;
                    border-radius: 18px;
                    padding: 8px 18px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FF9900;
                    border-color: #FFCC66;
                }
                QPushButton:pressed {
                    background-color: #FF8C4D;
                    border-color: #FF6600;
                }
            """)


class StarfleetPanel(QFrame):
    """Starfleet LCARS panel with characteristic design"""
    
    def __init__(self, panel_type="standard", parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Starfleet panel styling"""
        if self.panel_type == "standard":
            self.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: 3px solid #FF9900;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
        elif self.panel_type == "display":
            self.setStyleSheet("""
                QFrame {
                    background-color: #001A33;
                    border: 2px solid #0066CC;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
        elif self.panel_type == "control":
            self.setStyleSheet("""
                QFrame {
                    background-color: #1A1A1A;
                    border: 2px solid #666666;
                    border-radius: 12px;
                    padding: 8px;
                }
            """)


class StarfleetDisplay(QLabel):
    """Starfleet LCARS display with authentic styling"""
    
    def __init__(self, text="", display_type="standard", parent=None):
        super().__init__(text, parent)
        self.display_type = display_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Starfleet display styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.display_type == "standard":
            self.setStyleSheet("""
                QLabel {
                    color: #FFCC66;
                    background-color: transparent;
                    padding: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
            """)
        elif self.display_type == "title":
            self.setStyleSheet("""
                QLabel {
                    color: #FFFFFF;
                    background-color: #FF9900;
                    padding: 12px 20px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-transform: uppercase;
                }
            """)
        elif self.display_type == "data":
            self.setStyleSheet("""
                QLabel {
                    color: #00FF00;
                    background-color: #000000;
                    padding: 8px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    border: 1px solid #006600;
                }
            """)


class StarfleetInterface(QWidget):
    """Complete Starfleet interface with 22nd century styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup complete Starfleet interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header panel
        header_panel = StarfleetPanel("standard")
        header_layout = QHBoxLayout(header_panel)
        
        title = StarfleetDisplay("STARFLEET COMMAND", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        status = StarfleetDisplay("SYSTEMS ONLINE", "standard")
        header_layout.addWidget(status)
        
        layout.addWidget(header_panel)
        
        # Control panel
        control_panel = StarfleetPanel("control")
        control_layout = QHBoxLayout(control_panel)
        
        self.primary_btn = StarfleetButton("PRIMARY", "primary")
        control_layout.addWidget(self.primary_btn)
        
        self.secondary_btn = StarfleetButton("SECONDARY", "secondary")
        control_layout.addWidget(self.secondary_btn)
        
        self.warning_btn = StarfleetButton("ALERT", "warning")
        control_layout.addWidget(self.warning_btn)
        
        control_layout.addStretch()
        
        layout.addWidget(control_panel)
        
        # Display panel
        display_panel = StarfleetPanel("display")
        display_layout = QVBoxLayout(display_panel)
        
        self.data_display = StarfleetDisplay("SYSTEM STATUS: ALL SYSTEMS NOMINAL", "data")
        display_layout.addWidget(self.data_display)
        
        layout.addWidget(display_panel)
        
        # Apply background
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
