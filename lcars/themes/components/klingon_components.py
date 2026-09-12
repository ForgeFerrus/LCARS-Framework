#!/usr/bin/env python3
"""Klingon LCARS Components - 22nd Century Style"""

from PyQt6.QtWidgets import QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPainterPath, QLinearGradient, QColor


class KlingonButton(QPushButton):
    """Authentic Klingon LCARS button with 22nd century styling"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Klingon button styling"""
        self.setMinimumHeight(40)
        font = QFont("Arial", 12, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #8B0000;
                    color: #FFD700;
                    border: 2px solid #FFD700;
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FF4500;
                    border-color: #FFFFFF;
                    color: #000000;
                }
                QPushButton:pressed {
                    background-color: #A00000;
                    border-color: #FFAA00;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #330000;
                    color: #FFCCCC;
                    border: 2px solid #666666;
                    border-radius: 3px;
                    padding: 8px 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #550000;
                    border-color: #FFCCCC;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #440000;
                    border-color: #999999;
                }
            """)
        elif self.button_type == "weapon":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FF0000;
                    color: #FFFF00;
                    border: 2px solid #FF6600;
                    border-radius: 4px;
                    padding: 10px 18px;
                    font-weight: bold;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FF3300;
                    border-color: #FFAA00;
                    color: #000000;
                }
                QPushButton:pressed {
                    background-color: #CC0000;
                    border-color: #FF4400;
                }
            """)


class KlingonPanel(QFrame):
    """Klingon LCARS panel with characteristic design"""
    
    def __init__(self, panel_type="standard", parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Klingon panel styling"""
        if self.panel_type == "standard":
            self.setStyleSheet("""
                QFrame {
                    background-color: #1A0000;
                    border: 3px solid #FFD700;
                    border-radius: 5px;
                    padding: 10px;
                }
            """)
        elif self.panel_type == "weapon":
            self.setStyleSheet("""
                QFrame {
                    background-color: #330000;
                    border: 2px solid #FF0000;
                    border-radius: 3px;
                    padding: 8px;
                }
            """)
        elif self.panel_type == "tactical":
            self.setStyleSheet("""
                QFrame {
                    background-color: #000000;
                    border: 2px solid #8B0000;
                    border-radius: 4px;
                    padding: 12px;
                }
            """)


class KlingonDisplay(QLabel):
    """Klingon LCARS display with authentic styling"""
    
    def __init__(self, text="", display_type="standard", parent=None):
        super().__init__(text, parent)
        self.display_type = display_type
        self.setup_style()
        
    def setup_style(self):
        """Setup Klingon display styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Arial", 14, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.display_type == "standard":
            self.setStyleSheet("""
                QLabel {
                    color: #FFD700;
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
                    background-color: #FFD700;
                    padding: 12px 20px;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 5px;
                    text-transform: uppercase;
                }
            """)
        elif self.display_type == "tactical":
            self.setStyleSheet("""
                QLabel {
                    color: #FF6600;
                    background-color: #000000;
                    padding: 8px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    border: 1px solid #8B0000;
                }
            """)
        elif self.display_type == "alert":
            self.setStyleSheet("""
                QLabel {
                    color: #FFFF00;
                    background-color: #FF0000;
                    padding: 10px;
                    font-size: 16px;
                    font-weight: bold;
                    border: 2px solid #FF6600;
                    text-transform: uppercase;
                }
            """)


class KlingonInterface(QWidget):
    """Complete Klingon interface with 22nd century styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup complete Klingon interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header panel
        header_panel = KlingonPanel("standard")
        header_layout = QHBoxLayout(header_panel)
        
        title = KlingonDisplay("KLINGON EMPIRE", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        status = KlingonDisplay("BATTLE READY", "standard")
        header_layout.addWidget(status)
        
        layout.addWidget(header_panel)
        
        # Tactical panel
        tactical_panel = KlingonPanel("tactical")
        tactical_layout = QHBoxLayout(tactical_panel)
        
        self.weapon_btn = KlingonButton("WEAPONS", "weapon")
        tactical_layout.addWidget(self.weapon_btn)
        
        self.shields_btn = KlingonButton("SHIELDS", "primary")
        tactical_layout.addWidget(self.shields_btn)
        
        self.cloak_btn = KlingonButton("CLOAK", "secondary")
        tactical_layout.addWidget(self.cloak_btn)
        
        tactical_layout.addStretch()
        
        layout.addWidget(tactical_panel)
        
        # Display panel
        display_panel = KlingonPanel("weapon")
        display_layout = QVBoxLayout(display_panel)
        
        self.tactical_display = KlingonDisplay("TACTICAL STATUS: ALL SYSTEMS ARMED", "tactical")
        display_layout.addWidget(self.tactical_display)
        
        self.alert_display = KlingonDisplay("", "alert")
        self.alert_display.hide()
        display_layout.addWidget(self.alert_display)
        
        layout.addWidget(display_panel)
        
        # Apply background
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
