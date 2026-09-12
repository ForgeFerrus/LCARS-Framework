#!/usr/bin/env python3
"""Romulan LCARS Components - 22nd Century Style"""

from PyQt6.QtWidgets import QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QLinearGradient, QColor


class RomulanButton(QPushButton):
    """Authentic Romulan LCARS button with 22nd century styling"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan button styling"""
        self.setMinimumHeight(40)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #006666;
                    color: #00FF99;
                    border: 2px solid #00FF99;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #008B8B;
                    border-color: #FFFFFF;
                    color: #000000;
                }
                QPushButton:pressed {
                    background-color: #005555;
                    border-color: #00CC66;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #003333;
                    color: #00FFAA;
                    border: 2px solid #006666;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #005555;
                    border-color: #00FF99;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #004444;
                    border-color: #008888;
                }
            """)
        elif self.button_type == "stealth":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #001A1A;
                    color: #00FF66;
                    border: 2px solid #004444;
                    border-radius: 7px;
                    padding: 10px 18px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #002222;
                    border-color: #00FF99;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #001111;
                    border-color: #003333;
                }
            """)


class RomulanPanel(QFrame):
    """Romulan LCARS panel with characteristic design"""
    
    def __init__(self, panel_type="standard", parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan panel styling"""
        if self.panel_type == "standard":
            self.setStyleSheet("""
                QFrame {
                    background-color: #0A1A1A;
                    border: 3px solid #00FF99;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
        elif self.panel_type == "stealth":
            self.setStyleSheet("""
                QFrame {
                    background-color: #001A1A;
                    border: 2px solid #004444;
                    border-radius: 6px;
                    padding: 8px;
                }
            """)
        elif self.panel_type == "tactical":
            self.setStyleSheet("""
                QFrame {
                    background-color: #003333;
                    border: 2px solid #008B8B;
                    border-radius: 7px;
                    padding: 12px;
                }
            """)


class RomulanDisplay(QLabel):
    """Romulan LCARS display with authentic styling"""
    
    def __init__(self, text="", display_type="standard", parent=None):
        super().__init__(text, parent)
        self.display_type = display_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Romulan display styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.display_type == "standard":
            self.setStyleSheet("""
                QLabel {
                    color: #00FF99;
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
                    color: #000000;
                    background-color: #00FF99;
                    padding: 12px 20px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-transform: uppercase;
                }
            """)
        elif self.display_type == "stealth":
            self.setStyleSheet("""
                QLabel {
                    color: #00FF66;
                    background-color: #001A1A;
                    padding: 8px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    border: 1px solid #004444;
                }
            """)
        elif self.display_type == "tactical":
            self.setStyleSheet("""
                QLabel {
                    color: #00CCFF;
                    background-color: #003333;
                    padding: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #008B8B;
                    text-transform: uppercase;
                }
            """)


class RomulanInterface(QWidget):
    """Complete Romulan interface with 22nd century styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup complete Romulan interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header panel
        header_panel = RomulanPanel("standard")
        header_layout = QHBoxLayout(header_panel)
        
        title = RomulanDisplay("ROMULAN STAR EMPIRE", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        status = RomulanDisplay("STEALTH MODE ACTIVE", "standard")
        header_layout.addWidget(status)
        
        layout.addWidget(header_panel)
        
        # Stealth panel
        stealth_panel = RomulanPanel("stealth")
        stealth_layout = QHBoxLayout(stealth_panel)
        
        self.cloak_btn = RomulanButton("CLOAKING DEVICE", "stealth")
        stealth_layout.addWidget(self.cloak_btn)
        
        self.sensors_btn = RomulanButton("SENSORS", "secondary")
        stealth_layout.addWidget(self.sensors_btn)
        
        self.power_btn = RomulanButton("POWER", "primary")
        stealth_layout.addWidget(self.power_btn)
        
        stealth_layout.addStretch()
        
        layout.addWidget(stealth_panel)
        
        # Display panel
        display_panel = RomulanPanel("tactical")
        display_layout = QVBoxLayout(display_panel)
        
        self.stealth_display = RomulanDisplay("STEALTH SYSTEMS: OPERATIONAL", "stealth")
        display_layout.addWidget(self.stealth_display)
        
        self.tactical_display = RomulanDisplay("TACTICAL STATUS: ALL SYSTEMS NOMINAL", "tactical")
        display_layout.addWidget(self.tactical_display)
        
        layout.addWidget(display_panel)
        
        # Apply background
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
