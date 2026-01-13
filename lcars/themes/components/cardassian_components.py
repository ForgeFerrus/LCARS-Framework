#!/usr/bin/env python3
"""Cardassian LCARS Components - Authentic Deep Space Nine Style"""

from PyQt6.QtWidgets import (QPushButton, QFrame, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QApplication, QGridLayout, QGraphicsView, QGraphicsScene)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import (QFont, QPainter, QPainterPath, QLinearGradient, QColor, 
                        QPen, QBrush, QPolygonF)
import sys


class CardassianButton(QPushButton):
    """Authentic Cardassian LCARS button with DS9 styling"""
    
    def __init__(self, text="", button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Setup authentic Cardassian button styling"""
        self.setMinimumHeight(45)
        self.setMinimumWidth(100)
        font = QFont("Arial", 10, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8B0000, stop:0.3 #CC3300, stop:0.7 #FF4400, stop:1 #8B0000);
                    color: #FFFF00;
                    border: 2px solid #FFAA00;
                    border-radius: 1px;
                    padding: 6px 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 10px;
                    font-family: 'Courier New', monospace;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #AA0000, stop:0.3 #FF5500, stop:0.7 #FF6600, stop:1 #AA0000);
                    border-color: #FFFF00;
                    color: #000000;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #660000, stop:0.3 #990000, stop:0.7 #CC0000, stop:1 #660000);
                    border-color: #CC6600;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1A1A1A, stop:0.5 #2A2A2A, stop:1 #1A1A1A);
                    color: #FFAA00;
                    border: 1px solid #666666;
                    border-radius: 1px;
                    padding: 5px 10px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 9px;
                    font-family: 'Courier New', monospace;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2A2A2A, stop:0.5 #3A3A3A, stop:1 #2A2A2A);
                    border-color: #CC3300;
                    color: #FFFF00;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #0A0A0A, stop:0.5 #1A1A1A, stop:1 #0A0A0A);
                    border-color: #444444;
                }
            """)
        elif self.button_type == "command":
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF6600, stop:0.3 #CC3300, stop:0.7 #990000, stop:1 #660000);
                    color: #000000;
                    border: 3px solid #FFAA00;
                    border-radius: 0px;
                    padding: 8px 16px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 11px;
                    font-family: 'Courier New', monospace;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF8800, stop:0.3 #FF4400, stop:0.7 #CC0000, stop:1 #880000);
                    border-color: #FFFF00;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #CC4400, stop:0.3 #990000, stop:0.7 #660000, stop:1 #440000);
                    border-color: #CC6600;
                }
            """)


class CardassianAngledPanel(QFrame):
    """Cardassian panel with authentic angled design"""
    
    def __init__(self, panel_type="standard", parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.setup_style()
        
    def setup_style(self):
        """Setup authentic Cardassian angled panel styling"""
        if self.panel_type == "command":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:0.2 #1A0A0A, stop:0.4 #CC3300,
                        stop:0.6 #1A0A0A, stop:0.8 #000000, stop:1 #1A1A1A);
                    border: 3px solid #FF6600;
                    border-radius: 0px;
                    padding: 8px;
                }
            """)
        elif self.panel_type == "system":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #000000, stop:0.15 #1A1A1A, stop:0.3 #000000,
                        stop:0.45 #1A1A1A, stop:0.6 #000000, stop:0.75 #1A1A1A, stop:1 #000000);
                    border: 2px solid #CC3300;
                    border-radius: 1px;
                    padding: 6px;
                }
            """)
        elif self.panel_type == "alert":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #FF0000, stop:0.3 #CC3300, stop:0.7 #FF4400, stop:1 #AA0000);
                    border: 2px solid #FFFF00;
                    border-radius: 0px;
                    padding: 4px;
                }
            """)


class CardassianDisplay(QLabel):
    """Cardassian display with authentic DS9 styling"""
    
    def __init__(self, text="", display_type="standard", parent=None):
        super().__init__(text, parent)
        self.display_type = display_type
        self.setup_style()
        
    def setup_style(self):
        """Setup authentic Cardassian display styling"""
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Courier New", 10, QFont.Weight.Bold)
        self.setFont(font)
        
        if self.display_type == "title":
            self.setStyleSheet("""
                QLabel {
                    color: #000000;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FFAA00, stop:0.3 #CC3300, stop:0.7 #FF6600, stop:1 #FFAA00);
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #FFFF00;
                    border-radius: 1px;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
        elif self.display_type == "system":
            self.setStyleSheet("""
                QLabel {
                    color: #FFAA00;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #000000, stop:0.5 #1A0A0A, stop:1 #000000);
                    padding: 4px 8px;
                    font-size: 9px;
                    font-weight: bold;
                    border: 1px solid #666666;
                    border-radius: 1px;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
        elif self.display_type == "status":
            self.setStyleSheet("""
                QLabel {
                    color: #FFFF00;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #330000, stop:0.5 #660000, stop:1 #330000);
                    padding: 6px 12px;
                    font-size: 10px;
                    font-weight: bold;
                    border: 1px solid #CC3300;
                    border-radius: 0px;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
        elif self.display_type == "alert":
            self.setStyleSheet("""
                QLabel {
                    color: #000000;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #FFFF00, stop:0.3 #FF6600, stop:0.7 #FF0000, stop:1 #FFFF00);
                    padding: 4px 8px;
                    font-size: 11px;
                    font-weight: bold;
                    border: 2px solid #FF0000;
                    border-radius: 0px;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)


class CardassianGridPanel(QFrame):
    """Complex Cardassian grid panel with authentic layout"""
    
    def __init__(self, grid_type="system", parent=None):
        super().__init__(parent)
        self.grid_type = grid_type
        self.setup_ui()
        
    def setup_ui(self):
        """Setup complex grid layout"""
        layout = QGridLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(4, 4, 4, 4)
        
        if self.grid_type == "command":
            # Command center grid
            grid_data = [
                ("CMD", "system"), ("CTRL", "system"), ("EXEC", "system"),
                ("SEC", "status"), ("OPS", "status"), ("TAC", "status"),
                ("LOG", "system"), ("DATA", "system"), ("COMM", "system")
            ]
        elif self.grid_type == "station":
            # Station systems grid
            grid_data = [
                ("SECT-1", "system"), ("SECT-2", "system"), ("SECT-3", "system"),
                ("DOCK-A", "status"), ("DOCK-B", "status"), ("DOCK-C", "status"),
                ("CORE-1", "system"), ("CORE-2", "system"), ("CORE-3", "system")
            ]
        else:
            # Standard grid
            grid_data = [
                ("SYS", "system"), ("PWR", "system"), ("SHD", "system"),
                ("WEP", "status"), ("NAV", "status"), ("COM", "status"),
                ("ENG", "system"), ("MED", "system"), ("SCI", "system")
            ]
        
        for i, (text, cell_type) in enumerate(grid_data):
            cell = CardassianDisplay(text, cell_type)
            layout.addWidget(cell, i // 3, i % 3)
        
        # Apply grid styling
        if self.grid_type == "command":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:0.2 #1A1A1A, stop:0.4 #000000,
                        stop:0.6 #1A1A1A, stop:0.8 #000000, stop:1 #1A1A1A);
                    border: 3px solid #CC3300;
                    border-radius: 2px;
                    padding: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #000000, stop:0.2 #1A1A1A, stop:0.4 #000000,
                        stop:0.6 #1A1A1A, stop:0.8 #000000, stop:1 #1A1A1A);
                    border: 2px solid #666666;
                    border-radius: 1px;
                    padding: 6px;
                }
            """)


class CardassianInterface(QWidget):
    """Complete authentic Cardassian DS9 interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup authentic Cardassian interface layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Top command section
        top_section = QHBoxLayout()
        top_section.setSpacing(4)
        
        # Left command panel
        left_cmd = CardassianAngledPanel("command")
        left_cmd.setFixedSize(200, 100)
        left_layout = QVBoxLayout(left_cmd)
        left_layout.setSpacing(3)
        
        cmd_title = CardassianDisplay("CENTRAL COMMAND", "title")
        left_layout.addWidget(cmd_title)
        
        cmd_status = CardassianDisplay("ORDER MAINTAINED", "status")
        left_layout.addWidget(cmd_status)
        
        top_section.addWidget(left_cmd)
        
        # Center main display
        center_main = CardassianAngledPanel("system")
        center_main.setFixedSize(350, 100)
        center_layout = QVBoxLayout(center_main)
        center_layout.setSpacing(4)
        
        main_title = CardassianDisplay("CARDASSIAN UNION - DS9", "title")
        center_layout.addWidget(main_title)
        
        subtitle = CardassianDisplay("DEEP SPACE NINE OPERATIONS", "status")
        center_layout.addWidget(subtitle)
        
        top_section.addWidget(center_main)
        
        # Right command grid
        right_grid = CardassianGridPanel("command")
        right_grid.setFixedSize(200, 100)
        top_section.addWidget(right_grid)
        
        main_layout.addLayout(top_section)
        
        # Middle control section
        middle_section = QHBoxLayout()
        middle_section.setSpacing(6)
        
        # Left controls
        left_controls = CardassianAngledPanel("system")
        left_controls.setFixedSize(250, 150)
        left_control_layout = QVBoxLayout(left_controls)
        left_control_layout.setSpacing(4)
        
        self.weapons_btn = CardassianButton("WEAPONS SYSTEMS", "command")
        left_control_layout.addWidget(self.weapons_btn)
        
        self.shields_btn = CardassianButton("SHIELD GRID", "primary")
        left_control_layout.addWidget(self.shields_btn)
        
        self.tactical_btn = CardassianButton("TACTICAL SENSORS", "secondary")
        left_control_layout.addWidget(self.tactical_btn)
        
        middle_section.addWidget(left_controls)
        
        # Center status panels
        center_status = CardassianAngledPanel("system")
        center_status.setFixedSize(300, 150)
        status_layout = QVBoxLayout(center_status)
        status_layout.setSpacing(6)
        
        obsidian_display = CardassianDisplay("OBSIDIAN ORDER: ACTIVE", "status")
        status_layout.addWidget(obsidian_display)
        
        military_display = CardassianDisplay("MILITARY: BATTLE READY", "status")
        status_layout.addWidget(military_display)
        
        station_display = CardassianDisplay("STATION: ALL SECTORS SECURE", "system")
        status_layout.addWidget(station_display)
        
        middle_section.addWidget(center_status)
        
        # Right alert panel
        right_alert = CardassianAngledPanel("alert")
        right_alert.setFixedSize(200, 150)
        alert_layout = QVBoxLayout(right_alert)
        alert_layout.setSpacing(4)
        
        alert_title = CardassianDisplay("ALERT STATUS", "alert")
        alert_layout.addWidget(alert_title)
        
        alert_status = CardassianDisplay("CONDITION GREEN", "alert")
        alert_layout.addWidget(alert_status)
        
        power_display = CardassianDisplay("POWER: 100%", "system")
        alert_layout.addWidget(power_display)
        
        middle_section.addWidget(right_alert)
        main_layout.addLayout(middle_section)
        
        # Bottom station grid
        bottom_station = CardassianGridPanel("station")
        bottom_station.setFixedHeight(120)
        main_layout.addWidget(bottom_station)
        
        # Apply authentic background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.3 #0A0A0A, stop:0.7 #000000, stop:1 #0A0A0A);
            }
        """)


# Demo component for launcher
class CardassianComponentDemo(QWidget):
    """Cardassian component demo for launcher"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_demo()
        
    def setup_demo(self):
        layout = QVBoxLayout(self)
        
        # Create Cardassian interface
        interface = CardassianInterface()
        layout.addWidget(interface)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create main window
    window = QWidget()
    window.setWindowTitle("Authentic Cardassian DS9 Interface")
    window.setGeometry(100, 100, 800, 600)
    
    # Create Cardassian interface
    interface = CardassianInterface()
    
    # Setup main layout
    main_layout = QVBoxLayout(window)
    main_layout.addWidget(interface)
    
    window.show()
    sys.exit(app.exec())
