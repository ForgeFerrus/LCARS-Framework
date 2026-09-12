#!/usr/bin/env python3
"""Authentic Faction Interfaces - Complete UI Systems"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QGridLayout, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import (QFont, QPainter, QColor, QPen, QBrush, 
                        QLinearGradient, QPainterPath, QPolygonF)


class Starfleet24thInterface(QWidget):
    """Authentic Starfleet 24th Century Interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_starfleet_ui()
        
    def setup_starfleet_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #000000;
                color: #FFCC66;
                font-family: 'Swiss 911', 'Arial', sans-serif;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top header bar
        header = self.create_header_bar("STARFLEET COMMAND")
        layout.addWidget(header)
        
        # Main content area
        main_content = QHBoxLayout()
        
        # Left side panel
        left_panel = self.create_side_panel()
        main_content.addWidget(left_panel)
        
        # Center display
        center_display = self.create_center_display()
        main_content.addWidget(center_display)
        
        # Right side panel  
        right_panel = self.create_side_panel()
        main_content.addWidget(right_panel)
        
        layout.addLayout(main_content)
        
        # Bottom status bar
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
        
    def create_header_bar(self, title):
        """Create Starfleet header bar"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFCC66, stop:0.3 #FFAA33, stop:0.7 #FFCC66, stop:1 #FFAA33);
                border: none;
                border-bottom-left-radius: 30px;
                border-bottom-right-radius: 30px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 5, 20, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #000000;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        layout.addStretch()
        
        return header
        
    def create_side_panel(self):
        """Create Starfleet side panel"""
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFAA33, stop:1 #000000);
                border: none;
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        buttons = ["SYSTEMS", "WEAPONS", "SHIELDS", "ENGINES", "COMMS", "TACTICAL"]
        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFCC66;
                    color: #000000;
                    border: 2px solid #FFAA33;
                    border-radius: 25px;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #FFAA33;
                    color: #000000;
                    border: 2px solid #FFCC66;
                }
                QPushButton:pressed {
                    background-color: #FF9900;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return panel
        
    def create_center_display(self):
        """Create Starfleet center display"""
        display = QFrame()
        display.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 3px solid #FFCC66;
                border-radius: 20px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(display)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Display title
        title = QLabel("MAIN DISPLAY")
        title.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-size: 22px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFCC66, stop:1 #FFAA33);
                border-radius: 15px;
                padding: 10px;
                text-transform: uppercase;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Content area
        content = QLabel("SYSTEM STATUS: ALL GREEN\n\nWARP CORE: ONLINE\nSHIELDS: 100%\nWEAPONS: STANDBY\n\nUSS ENTERPRISE-D\nNCC-1701-D")
        content.setStyleSheet("""
            QLabel {
                color: #FFCC66;
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #001144, stop:0.5 #002266, stop:1 #001144);
                border: 2px solid #FFAA33;
                border-radius: 15px;
                padding: 20px;
                text-transform: uppercase;
            }
        """)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        layout.addStretch()
        return display
        
    def create_status_bar(self):
        """Create Starfleet status bar"""
        status = QFrame()
        status.setFixedHeight(40)
        status.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFAA33, stop:0.5 #FFCC66, stop:1 #FFAA33);
                border: none;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
            }
        """)
        
        layout = QHBoxLayout(status)
        layout.setContentsMargins(20, 5, 20, 5)
        
        status_items = [
            ("STATUS", "ONLINE", "#00FF00"),
            ("POWER", "100%", "#00FF00"), 
            ("SHIELDS", "UP", "#00FF00")
        ]
        
        for label_text, value_text, color in status_items:
            widget = QWidget()
            widget.setFixedSize(120, 30)
            widget.setStyleSheet(f"""
                QWidget {{
                    background-color: #000000;
                    border: 2px solid #FFCC66;
                    border-radius: 10px;
                }}
            """)
            
            widget_layout = QHBoxLayout(widget)
            widget_layout.setContentsMargins(5, 2, 5, 2)
            
            label = QLabel(label_text)
            label.setStyleSheet("""
                font-size: 10px;
                color: #FFCC66;
                font-weight: bold;
                background: transparent;
            """)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                font-size: 12px;
                color: {color};
                font-weight: bold;
                background: transparent;
            """)
            
            widget_layout.addWidget(label)
            widget_layout.addWidget(value)
            layout.addWidget(widget)
            
        layout.addStretch()
        return status


class KlingonInterface(QWidget):
    """Authentic Klingon Interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_klingon_ui()
        
    def setup_klingon_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #1A0000;
                color: #CC0000;
                font-family: 'Arial', sans-serif;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Klingon header with blade design
        header = self.create_klingon_header()
        layout.addWidget(header)
        
        # Main content with aggressive layout
        main_content = QHBoxLayout()
        
        # Weapons panel
        weapons_panel = self.create_weapons_panel()
        main_content.addWidget(weapons_panel)
        
        # Tactical display
        tactical_display = self.create_tactical_display()
        main_content.addWidget(tactical_display)
        
        # Status panel
        status_panel = self.create_klingon_status()
        main_content.addWidget(status_panel)
        
        layout.addLayout(main_content)
        
    def create_klingon_header(self):
        """Create Klingon header with blade motif"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #660000, stop:0.3 #CC0000, stop:0.7 #660000, stop:1 #CC0000);
                border: 3px solid #FF0000;
                border-bottom-left-radius: 40px;
                border-bottom-right-radius: 40px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        title = QLabel("KLINGON HIGH COMMAND")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 28px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 3px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        return header
        
    def create_weapons_panel(self):
        """Create Klingon weapons panel"""
        panel = QFrame()
        panel.setFixedWidth(250)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #CC0000, stop:1 #330000);
                border: 3px solid #FF0000;
                border-top-right-radius: 30px;
                border-bottom-right-radius: 30px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Weapons title
        title = QLabel("WEAPONS")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 20px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                text-align: center;
                padding: 10px;
                border-bottom: 2px solid #FF0000;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Weapon controls
        weapons = ["DISRUPTORS", "PHOTON", "PLASMA", "TORPEDOES"]
        for weapon in weapons:
            btn = QPushButton(weapon)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #990000, stop:0.5 #CC0000, stop:1 #990000);
                    color: #FFFF00;
                    border: 2px solid #FF0000;
                    border-radius: 5px;
                    padding: 10px 15px;
                    font-weight: bold;
                    font-size: 14px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background: #FF0000;
                    color: #000000;
                    border: 2px solid #FFFF00;
                }
                QPushButton:pressed {
                    background: #660000;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return panel
        
    def create_tactical_display(self):
        """Create Klingon tactical display"""
        display = QFrame()
        display.setStyleSheet("""
            QFrame {
                background: #000000;
                border: 3px solid #CC0000;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(display)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tactical title
        title = QLabel("TACTICAL DISPLAY")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 22px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #CC0000, stop:1 #990000);
                border-radius: 10px;
                padding: 10px;
                text-transform: uppercase;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Target display
        target_info = QLabel("TARGET LOCKED\n\nFEDERATION VESSEL\nSHIELDS: 75%\nHULL: 90%\n\nFIRE AT WILL!")
        target_info.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 18px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #330000, stop:0.5 #660000, stop:1 #330000);
                border: 2px solid #CC0000;
                border-radius: 10px;
                padding: 20px;
                text-transform: uppercase;
            }
        """)
        target_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(target_info)
        
        layout.addStretch()
        return display
        
    def create_klingon_status(self):
        """Create Klingon status panel"""
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #330000, stop:1 #CC0000);
                border: 3px solid #FF0000;
                border-top-left-radius: 30px;
                border-bottom-left-radius: 30px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # Status title
        title = QLabel("SHIP STATUS")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                text-align: center;
                padding: 8px;
                border-bottom: 2px solid #FF0000;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status items
        status_items = [
            ("SHIELDS", "85%"),
            ("WEAPONS", "READY"),
            ("ENGINES", "FULL"),
            ("CLOAK", "OFFLINE")
        ]
        
        for label, value in status_items:
            item = QLabel(f"{label}: {value}")
            item.setStyleSheet("""
                QLabel {
                    color: #FF0000;
                    font-size: 12px;
                    font-weight: bold;
                    background: transparent;
                    padding: 5px;
                    text-transform: uppercase;
                    border-bottom: 1px solid #660000;
                }
            """)
            layout.addWidget(item)
            
        layout.addStretch()
        return panel


class RomulanQuantumInterface(QWidget):
    """Authentic Romulan Quantum Interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_romulan_ui()
        
    def setup_romulan_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.3 #001144, stop:0.7 #000822, stop:1 #001144);
                color: #00FFAA;
                font-family: 'Arial', sans-serif;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Romulan header with quantum design
        header = self.create_romulan_header()
        layout.addWidget(header)
        
        # Main quantum content
        main_content = QHBoxLayout()
        
        # Quantum core
        quantum_core = self.create_quantum_core()
        main_content.addWidget(quantum_core)
        
        # Cloak systems
        cloak_systems = self.create_cloak_systems()
        main_content.addWidget(cloak_systems)
        
        # Weapon systems
        weapon_systems = self.create_weapon_systems()
        main_content.addWidget(weapon_systems)
        
        layout.addLayout(main_content)
        
        # Bottom quantum grid
        quantum_grid = self.create_quantum_grid()
        layout.addWidget(quantum_grid)
        
    def create_romulan_header(self):
        """Create Romulan header with quantum elements"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                border: 3px solid #00FFAA;
                border-radius: 15px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        title = QLabel("ROMULAN QUANTUM COMMAND")
        title.setStyleSheet("""
            QLabel {
                color: #001144;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 3px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        return header
        
    def create_quantum_core(self):
        """Create Romulan quantum core display"""
        core = QFrame()
        core.setFixedWidth(300)
        core.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.2 #001144, stop:0.4 #000822,
                    stop:0.6 #001144, stop:0.8 #000822, stop:1 #001144);
                border: 2px solid #00FFAA;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(core)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Core title
        title = QLabel("QUANTUM CORE")
        title.setStyleSheet("""
            QLabel {
                color: #001144;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                padding: 8px 15px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #00FFAA;
                border-radius: 8px;
                text-transform: uppercase;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Energy display
        energy = QLabel("QUANTUM ENERGY: 98.7%")
        energy.setStyleSheet("""
            QLabel {
                color: #00FFCC;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #001144, stop:0.2 #002266, stop:0.4 #001144,
                    stop:0.6 #002266, stop:0.8 #001144, stop:1 #002266);
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #00AA88;
                border-radius: 6px;
                text-transform: uppercase;
            }
        """)
        energy.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(energy)
        
        # Quantum states
        states_layout = QHBoxLayout()
        states_layout.setSpacing(5)
        
        states = ["STABLE", "ENTANGLED", "SUPERPOSED"]
        for state in states:
            state_label = QLabel(state)
            state_label.setStyleSheet("""
                QLabel {
                    color: #00FFAA;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #004433, stop:0.5 #006655, stop:1 #004433);
                    padding: 6px 10px;
                    font-size: 9px;
                    font-weight: bold;
                    border: 1px solid #00AA88;
                    text-transform: uppercase;
                    border-radius: 4px;
                }
            """)
            state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            states_layout.addWidget(state_label)
            
        layout.addLayout(states_layout)
        layout.addStretch()
        return core
        
    def create_cloak_systems(self):
        """Create Romulan cloak systems panel"""
        cloak = QFrame()
        cloak.setFixedWidth(250)
        cloak.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.15 #001144, stop:0.3 #000822,
                    stop:0.45 #001144, stop:0.6 #000822, stop:0.75 #001144, stop:1 #000822);
                border: 2px solid #00FFAA;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(cloak)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Cloak title
        title = QLabel("CLOAK SYSTEMS")
        title.setStyleSheet("""
            QLabel {
                color: #001144;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #00FFAA;
                border-radius: 8px;
                text-transform: uppercase;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Cloak status
        status = QLabel("CLOAK: ENGAGED")
        status.setStyleSheet("""
            QLabel {
                color: #001144;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.5 #00FFCC, stop:1 #00FFAA);
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #00FFAA;
                border-radius: 6px;
                text-transform: uppercase;
            }
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status)
        
        # Cloak controls
        controls = ["STEALTH MODE", "POWER LEVEL", "DECOY"]
        for control in controls:
            btn = QPushButton(control)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #004433, stop:0.3 #006655, stop:0.7 #008877, stop:1 #004433);
                    color: #00FFAA;
                    border: 1px solid #00AA88;
                    border-radius: 5px;
                    padding: 8px 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #006655, stop:0.3 #008877, stop:0.7 #00AA99, stop:1 #006655);
                    color: #001144;
                    border-color: #00FFCC;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return cloak
        
    def create_weapon_systems(self):
        """Create Romulan weapon systems panel"""
        weapons = QFrame()
        weapons.setFixedWidth(250)
        weapons.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.2 #001144, stop:0.4 #000822,
                    stop:0.6 #001144, stop:0.8 #000822, stop:1 #001144);
                border: 2px solid #00FFAA;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(weapons)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Weapons title
        title = QLabel("WEAPON SYSTEMS")
        title.setStyleSheet("""
            QLabel {
                color: #001144;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFAA, stop:0.3 #00FFCC, stop:0.7 #00FFAA, stop:1 #00FFCC);
                padding: 8px 15px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #00FFAA;
                border-radius: 8px;
                text-transform: uppercase;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Weapon controls
        weapon_controls = ["DISRUPTORS", "PLASMA", "QUANTUM", "TORPEDOES"]
        for weapon in weapon_controls:
            btn = QPushButton(weapon)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #004433, stop:0.3 #006655, stop:0.7 #008877, stop:1 #004433);
                    color: #00FFAA;
                    border: 2px solid #00FFAA;
                    border-radius: 6px;
                    padding: 10px 15px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #006655, stop:0.3 #008877, stop:0.7 #00AA99, stop:1 #006655);
                    color: #001144;
                    border-color: #00FFCC;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return weapons
        
    def create_quantum_grid(self):
        """Create Romulan quantum grid display"""
        grid = QFrame()
        grid.setFixedHeight(100)
        grid.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #000822, stop:0.15 #001144, stop:0.3 #000822,
                    stop:0.45 #001144, stop:0.6 #000822, stop:0.75 #001144, stop:1 #000822);
                border: 2px solid #00FFAA;
                border-radius: 10px;
            }
        """)
        
        grid_layout = QGridLayout(grid)
        grid_layout.setContentsMargins(10, 10, 10, 10)
        grid_layout.setSpacing(3)
        
        # Quantum grid items
        grid_items = [
            "QUANT-1", "QUANT-2", "QUANT-3", "QUANT-4", "QUANT-5",
            "NODE-A", "NODE-B", "NODE-C", "NODE-D", "NODE-E",
            "CORE-X", "CORE-Y", "CORE-Z", "SUB-1", "SUB-2"
        ]
        
        for i, text in enumerate(grid_items):
            item = QLabel(text)
            item.setStyleSheet("""
                QLabel {
                    color: #00FFAA;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #002244, stop:0.5 #003366, stop:1 #002244);
                    border: 1px solid #006644;
                    padding: 4px 6px;
                    font-size: 8px;
                    font-weight: bold;
                    text-transform: uppercase;
                    border-radius: 3px;
                }
            """)
            item.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid_layout.addWidget(item, i // 5, i % 5)
            
        return grid


class CardassianInterface(QWidget):
    """Authentic Cardassian Interface"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_cardassian_ui()
        
    def setup_cardassian_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: #2A1810;
                color: #CC6600;
                font-family: 'Arial', sans-serif;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Cardassian header
        header = self.create_cardassian_header()
        layout.addWidget(header)
        
        # Main content
        main_content = QHBoxLayout()
        
        # Command panel
        command_panel = self.create_command_panel()
        main_content.addWidget(command_panel)
        
        # Central display
        central_display = self.create_central_display()
        main_content.addWidget(central_display)
        
        # Systems panel
        systems_panel = self.create_systems_panel()
        main_content.addWidget(systems_panel)
        
        layout.addLayout(main_content)
        
    def create_cardassian_header(self):
        """Create Cardassian header"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B0000, stop:0.3 #CC3300, stop:0.7 #8B0000, stop:1 #CC3300);
                border: 3px solid #FFAA00;
                border-radius: 12px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 10, 30, 10)
        
        title = QLabel("CARDASSIAN UNION COMMAND")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        return header
        
    def create_command_panel(self):
        """Create Cardassian command panel"""
        panel = QFrame()
        panel.setFixedWidth(220)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A0A05, stop:1 #8B0000);
                border: 2px solid #CC6600;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        # Command title
        title = QLabel("COMMAND")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                text-align: center;
                padding: 8px;
                border-bottom: 2px solid #CC6600;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Command buttons
        commands = ["AUTHORITY", "JUSTICE", "ORDER", "SECURITY"]
        for cmd in commands:
            btn = QPushButton(cmd)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #8B0000, stop:0.3 #CC3300, stop:0.7 #FF4400, stop:1 #8B0000);
                    color: #FFFF00;
                    border: 2px solid #FFAA00;
                    border-radius: 8px;
                    padding: 10px 15px;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #AA0000, stop:0.3 #FF5500, stop:0.7 #FF6600, stop:1 #AA0000);
                    color: #000000;
                    border-color: #FFFF00;
                }
            """)
            layout.addWidget(btn)
            
        layout.addStretch()
        return panel
        
    def create_central_display(self):
        """Create Cardassian central display"""
        display = QFrame()
        display.setStyleSheet("""
            QFrame {
                background: #1A0A05;
                border: 3px solid #CC6600;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
        layout = QVBoxLayout(display)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Display title
        title = QLabel("CENTRAL COMMAND")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 20px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8B0000, stop:0.3 #CC3300, stop:0.7 #FF4400, stop:1 #8B0000);
                border-radius: 10px;
                padding: 10px;
                text-transform: uppercase;
                text-align: center;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Content area
        content = QLabel("GALOR CLASS CRUISER\n\nSYSTEMS: OPERATIONAL\nCREW: 600\nWEAPONS: READY\nSHIELDS: MAXIMUM\n\nCARDASSIAN PRIME\nSECTOR 7")
        content.setStyleSheet("""
            QLabel {
                color: #CC6600;
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2A1810, stop:0.5 #4A2818, stop:1 #2A1810);
                border: 2px solid #CC6600;
                border-radius: 10px;
                padding: 20px;
                text-transform: uppercase;
            }
        """)
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content)
        
        layout.addStretch()
        return display
        
    def create_systems_panel(self):
        """Create Cardassian systems panel"""
        panel = QFrame()
        panel.setFixedWidth(200)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A0A05, stop:1 #8B0000);
                border: 2px solid #CC6600;
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # Systems title
        title = QLabel("SYSTEMS")
        title.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
                text-transform: uppercase;
                text-align: center;
                padding: 8px;
                border-bottom: 2px solid #CC6600;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # System status
        systems = [
            ("POWER", "ONLINE"),
            ("WEAPONS", "ARMED"),
            ("SHIELDS", "ACTIVE"),
            ("COMMS", "OPEN")
        ]
        
        for system, status in systems:
            item = QLabel(f"{system}: {status}")
            item.setStyleSheet("""
                QLabel {
                    color: #CC6600;
                    font-size: 11px;
                    font-weight: bold;
                    background: transparent;
                    padding: 6px;
                    text-transform: uppercase;
                    border-bottom: 1px solid #8B0000;
                }
            """)
            layout.addWidget(item)
            
        layout.addStretch()
        return panel


# Export all interfaces
__all__ = [
    'Starfleet24thInterface',
    'KlingonInterface', 
    'RomulanQuantumInterface',
    'CardassianInterface'
]
