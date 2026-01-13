#!/usr/bin/env python3
"""Cardassian DS9 Interface - Image Integration Template"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QGridLayout, QLabel, QFrame, QPushButton, QScrollArea)
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QRectF

class CardassianImagePanel(QFrame):
    """Cardassian panel with image support"""
    
    def __init__(self, panel_type="main", image_path=None, parent=None):
        super().__init__(parent)
        self.panel_type = panel_type
        self.image_path = image_path
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(2)
        
        # Create panels based on type
        if self.panel_type == "header":
            self.create_header_panel(layout)
        elif self.panel_type == "left_main":
            self.create_left_main_panel(layout)
        elif self.panel_type == "left_systems":
            self.create_left_systems_panel(layout)
        elif self.panel_type == "center_display":
            self.create_center_display_panel(layout)
        elif self.panel_type == "center_controls":
            self.create_center_controls_panel(layout)
        elif self.panel_type == "right_status":
            self.create_right_status_panel(layout)
        elif self.panel_type == "right_tactical":
            self.create_right_tactical_panel(layout)
        elif self.panel_type == "bottom_grid":
            self.create_bottom_grid_panel(layout)
            
    def create_image_label(self, fallback_text, size=None):
        """Create label with image or fallback text"""
        label = QLabel()
        
        if self.image_path and os.path.exists(self.image_path):
            # Load and scale image
            pixmap = QPixmap(self.image_path)
            if size:
                pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            # Fallback text styling
            label.setText(fallback_text)
            label.setStyleSheet("""
                QLabel {
                    color: #FFAA00;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #000000, stop:0.3 #1A1A1A, stop:0.7 #000000, stop:1 #1A1A1A);
                    border: 2px solid #CC3300;
                    padding: 10px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        return label
        
    def create_header_panel(self, layout):
        """Create header panel"""
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #000000, stop:0.1 #1A0A0A, stop:0.2 #CC3300,
                    stop:0.3 #FF6600, stop:0.4 #CC3300, stop:0.5 #1A0A0A,
                    stop:0.6 #000000, stop:0.7 #1A0A0A, stop:0.8 #CC3300,
                    stop:0.9 #FF6600, stop:1 #CC3300);
                border: 2px solid #FFAA00;
                border-radius: 2px;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Left section - can be replaced with image
        left_section = self.create_image_label("CARDASSIAN UNION", (200, 50))
        header_layout.addWidget(left_section)
        
        header_layout.addStretch()
        
        # Center section
        center_section = QLabel("DEEP SPACE NINE")
        center_section.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                background: transparent;
                font-size: 14px;
                font-weight: bold;
                text-transform: uppercase;
                font-family: 'Courier New', monospace;
            }
        """)
        header_layout.addWidget(center_section)
        
        header_layout.addStretch()
        
        # Right section
        right_section = QLabel("STARDATE: 51879.2")
        right_section.setStyleSheet("""
            QLabel {
                color: #FFAA00;
                background: transparent;
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                font-family: 'Courier New', monospace;
            }
        """)
        header_layout.addWidget(right_section)
        
        layout.addWidget(header_widget)
        
    def create_left_main_panel(self, layout):
        """Create left main panel"""
        main_widget = QWidget()
        main_widget.setFixedHeight(150)
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.2 #1A0A0A, stop:0.4 #000000,
                    stop:0.6 #1A0A0A, stop:0.8 #000000, stop:1 #1A1A1A);
                border: 2px solid #CC3300;
                border-radius: 2px;
            }
        """)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 6, 8, 6)
        main_layout.setSpacing(3)
        
        # Main image area (replace with your graphic)
        main_image = self.create_image_label("CENTRAL COMMAND", (180, 80))
        main_layout.addWidget(main_image)
        
        # Status displays
        status_layout = QHBoxLayout()
        status_layout.setSpacing(2)
        
        statuses = ["ORDER", "SECURE", "ONLINE"]
        for status in statuses:
            status_label = QLabel(status)
            status_label.setStyleSheet("""
                QLabel {
                    color: #FFFF00;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #330000, stop:0.5 #660000, stop:1 #330000);
                    padding: 4px 8px;
                    font-size: 9px;
                    font-weight: bold;
                    border: 1px solid #CC3300;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_layout.addWidget(status_label)
            
        main_layout.addLayout(status_layout)
        layout.addWidget(main_widget)
        
    def create_left_systems_panel(self, layout):
        """Create left systems panel"""
        systems_widget = QWidget()
        systems_widget.setFixedHeight(120)
        systems_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.15 #1A1A1A, stop:0.3 #000000,
                    stop:0.45 #1A1A1A, stop:0.6 #000000, stop:0.75 #1A1A1A, stop:1 #000000);
                border: 2px solid #666666;
                border-radius: 2px;
            }
        """)
        
        systems_layout = QGridLayout(systems_widget)
        systems_layout.setContentsMargins(6, 6, 6, 6)
        systems_layout.setSpacing(2)
        
        # System grid - can be replaced with images
        system_items = [
            ("SYS", "normal"), ("PWR", "normal"), ("SHD", "normal"),
            ("WEP", "active"), ("NAV", "normal"), ("COM", "normal"),
            ("ENG", "normal"), ("MED", "normal"), ("SCI", "normal")
        ]
        
        for i, (text, status) in enumerate(system_items):
            item = QLabel(text)
            if status == "active":
                item.setStyleSheet("""
                    QLabel {
                        color: #FFFF00;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #CC3300, stop:0.5 #FF6600, stop:1 #CC3300);
                        border: 1px solid #FFAA00;
                        padding: 3px 6px;
                        font-size: 8px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-family: 'Courier New', monospace;
                    }
                """)
            else:
                item.setStyleSheet("""
                    QLabel {
                        color: #FFAA00;
                        background: transparent;
                        border: 1px solid #333333;
                        padding: 3px 6px;
                        font-size: 8px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-family: 'Courier New', monospace;
                    }
                """)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            systems_layout.addWidget(item, i // 3, i % 3)
            
        layout.addWidget(systems_widget)
        
    def create_center_display_panel(self, layout):
        """Create center display panel"""
        display_widget = QWidget()
        display_widget.setFixedHeight(200)
        display_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.2 #1A0A0A, stop:0.4 #000000,
                    stop:0.6 #1A0A0A, stop:0.8 #000000, stop:1 #1A1A1A);
                border: 2px solid #CC3300;
                border-radius: 2px;
            }
        """)
        
        display_layout = QVBoxLayout(display_widget)
        display_layout.setContentsMargins(10, 8, 10, 8)
        display_layout.setSpacing(4)
        
        # Main display area - replace with your main graphic
        main_display = self.create_image_label("MAIN DISPLAY AREA", (350, 120))
        display_layout.addWidget(main_display)
        
        # Sub displays
        sub_layout = QHBoxLayout()
        sub_layout.setSpacing(3)
        
        sub_displays = ["DOCKING", "POWER", "SHIELDS"]
        for text in sub_displays:
            sub = QLabel(text)
            sub.setStyleSheet("""
                QLabel {
                    color: #FFFF00;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #330000, stop:0.5 #660000, stop:1 #330000);
                    padding: 6px 12px;
                    font-size: 9px;
                    font-weight: bold;
                    border: 1px solid #CC3300;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_layout.addWidget(sub)
            
        display_layout.addLayout(sub_layout)
        layout.addWidget(display_widget)
        
    def create_center_controls_panel(self, layout):
        """Create center controls panel"""
        controls_widget = QWidget()
        controls_widget.setFixedHeight(80)
        controls_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.2 #1A0A0A, stop:0.4 #000000,
                    stop:0.6 #1A0A0A, stop:0.8 #000000, stop:1 #1A1A1A);
                border: 2px solid #666666;
                border-radius: 2px;
            }
        """)
        
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(8, 6, 8, 6)
        controls_layout.setSpacing(3)
        
        control_buttons = [
            ("WEAPONS", "primary"),
            ("SHIELDS", "secondary"),
            ("TACTICAL", "primary"),
            ("SENSORS", "secondary"),
            ("POWER", "primary"),
            ("COMMS", "secondary")
        ]
        
        for text, btn_type in control_buttons:
            btn = QPushButton(text)
            if btn_type == "primary":
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #8B0000, stop:0.3 #CC3300, stop:0.7 #FF4400, stop:1 #8B0000);
                        color: #FFFF00;
                        border: 2px solid #FFAA00;
                        border-radius: 1px;
                        padding: 8px 16px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-size: 9px;
                        font-family: 'Courier New', monospace;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #AA0000, stop:0.3 #FF5500, stop:0.7 #FF6600, stop:1 #AA0000);
                        border-color: #FFFF00;
                        color: #000000;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #1A1A1A, stop:0.5 #2A2A2A, stop:1 #1A1A1A);
                        color: #FFAA00;
                        border: 1px solid #666666;
                        border-radius: 1px;
                        padding: 6px 12px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-size: 8px;
                        font-family: 'Courier New', monospace;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #2A2A2A, stop:0.5 #3A3A3A, stop:1 #2A2A2A);
                        border-color: #CC3300;
                        color: #FFFF00;
                    }
                """)
            controls_layout.addWidget(btn)
            
        layout.addWidget(controls_widget)
        
    def create_right_status_panel(self, layout):
        """Create right status panel"""
        status_widget = QWidget()
        status_widget.setFixedHeight(150)
        status_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.2 #1A0A0A, stop:0.4 #000000,
                    stop:0.6 #1A0A0A, stop:0.8 #000000, stop:1 #1A1A1A);
                border: 2px solid #CC3300;
                border-radius: 2px;
            }
        """)
        
        status_layout = QVBoxLayout(status_widget)
        status_layout.setContentsMargins(8, 6, 8, 6)
        status_layout.setSpacing(3)
        
        # Alert panel - can be replaced with image
        alert_panel = self.create_image_label("ALERT: GREEN", (150, 40))
        status_layout.addWidget(alert_panel)
        
        # Power displays
        power_displays = [
            ("POWER: 100%", "power"),
            ("SHIELDS: MAX", "shield"),
            ("WEAPONS: READY", "weapon")
        ]
        
        for text, display_type in power_displays:
            display = QLabel(text)
            if display_type == "power":
                display.setStyleSheet("""
                    QLabel {
                        color: #FFFF00;
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #CC3300, stop:0.5 #FF6600, stop:1 #CC3300);
                        padding: 6px 12px;
                        font-size: 9px;
                        font-weight: bold;
                        border: 1px solid #FFAA00;
                        text-transform: uppercase;
                        font-family: 'Courier New', monospace;
                    }
                """)
            else:
                display.setStyleSheet("""
                    QLabel {
                        color: #FFAA00;
                        background: transparent;
                        border: 1px solid #333333;
                        padding: 6px 12px;
                        font-size: 9px;
                        font-weight: bold;
                        text-transform: uppercase;
                        font-family: 'Courier New', monospace;
                    }
                """)
            display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            status_layout.addWidget(display)
            
        layout.addWidget(status_widget)
        
    def create_right_tactical_panel(self, layout):
        """Create right tactical panel"""
        tactical_widget = QWidget()
        tactical_widget.setFixedHeight(120)
        tactical_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.15 #1A1A1A, stop:0.3 #000000,
                    stop:0.45 #1A1A1A, stop:0.6 #000000, stop:0.75 #1A1A1A, stop:1 #000000);
                border: 2px solid #666666;
                border-radius: 2px;
            }
        """)
        
        tactical_layout = QVBoxLayout(tactical_widget)
        tactical_layout.setContentsMargins(8, 6, 8, 6)
        tactical_layout.setSpacing(3)
        
        # Tactical title
        tac_title = QLabel("TACTICAL")
        tac_title.setStyleSheet("""
            QLabel {
                color: #000000;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFAA00, stop:0.3 #CC3300, stop:0.7 #FF6600, stop:1 #FFAA00);
                padding: 6px 12px;
                font-size: 10px;
                font-weight: bold;
                border: 1px solid #FFFF00;
                border-radius: 1px;
                text-transform: uppercase;
                font-family: 'Courier New', monospace;
            }
        """)
        tac_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tactical_layout.addWidget(tac_title)
        
        # Tactical items - can be replaced with images
        tactical_items = ["TARGETING", "LOCKED", "FIRING"]
        for text in tactical_items:
            item = QLabel(text)
            item.setStyleSheet("""
                QLabel {
                    color: #FFAA00;
                    background: transparent;
                    border: 1px solid #333333;
                    padding: 4px 8px;
                    font-size: 8px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tactical_layout.addWidget(item)
            
        layout.addWidget(tactical_widget)
        
    def create_bottom_grid_panel(self, layout):
        """Create bottom grid panel"""
        grid_widget = QWidget()
        grid_widget.setFixedHeight(100)
        grid_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.15 #1A1A1A, stop:0.3 #000000,
                    stop:0.45 #1A1A1A, stop:0.6 #000000, stop:0.75 #1A1A1A, stop:1 #000000);
                border: 2px solid #CC3300;
                border-radius: 2px;
            }
        """)
        
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(6, 6, 6, 6)
        grid_layout.setSpacing(2)
        
        grid_items = [
            "SECT-001", "SECT-002", "SECT-003", "SECT-004", "SECT-005",
            "DOCK-A", "DOCK-B", "DOCK-C", "DOCK-D", "DOCK-E",
            "CORE-1", "CORE-2", "CORE-3", "CORE-4", "CORE-5",
            "ENG-01", "MED-01", "SCI-01", "SEC-01", "COM-01"
        ]
        
        for i, text in enumerate(grid_items):
            item = QLabel(text)
            item.setStyleSheet("""
                QLabel {
                    color: #FFAA00;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #000000, stop:0.5 #1A1A1A, stop:1 #000000);
                    border: 1px solid #333333;
                    padding: 3px 6px;
                    font-size: 7px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-family: 'Courier New', monospace;
                }
            """)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_layout.addWidget(item, i // 5, i % 5)
            
        layout.addWidget(grid_widget)


class CardassianImageInterface(QWidget):
    """Cardassian interface with image support"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CARDASSIAN UNION - DEEP SPACE NINE - IMAGE TEMPLATE")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup interface with image support"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(3)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header = CardassianImagePanel("header")
        main_layout.addWidget(header)
        
        # Main content
        main_content = QHBoxLayout()
        main_content.setSpacing(3)
        
        # Left column
        left_column = QVBoxLayout()
        left_column.setSpacing(3)
        
        left_main = CardassianImagePanel("left_main")
        left_column.addWidget(left_main)
        
        left_systems = CardassianImagePanel("left_systems")
        left_column.addWidget(left_systems)
        
        main_content.addLayout(left_column)
        
        # Center column
        center_column = QVBoxLayout()
        center_column.setSpacing(3)
        
        center_display = CardassianImagePanel("center_display")
        center_column.addWidget(center_display)
        
        center_controls = CardassianImagePanel("center_controls")
        center_column.addWidget(center_controls)
        
        main_content.addLayout(center_column)
        
        # Right column
        right_column = QVBoxLayout()
        right_column.setSpacing(3)
        
        right_status = CardassianImagePanel("right_status")
        right_column.addWidget(right_status)
        
        right_tactical = CardassianImagePanel("right_tactical")
        right_column.addWidget(right_tactical)
        
        main_content.addLayout(right_column)
        
        main_layout.addLayout(main_content)
        
        # Bottom grid
        bottom_grid = CardassianImagePanel("bottom_grid")
        main_layout.addWidget(bottom_grid)
        
        # Apply background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000000, stop:0.3 #0A0A0A, stop:0.7 #000000, stop:1 #0A0A0A);
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the interface
    interface = CardassianImageInterface()
    interface.show()
    
    sys.exit(app.exec())
