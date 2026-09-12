#!/usr/bin/env python3
"""Fixed LCARS Launcher - Working Version"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Try to import interfaces
INTERFACES = {}
if True:
    from lcars.ui.LCARS_24th import LCARS24thCentury
    INTERFACES['LCARS_24th'] = LCARS24thCentury
if False: # Removed except block
    pass

if True:
    from lcars.ui.LCARS_25th import LCARS25thCentury
    INTERFACES['LCARS_25th'] = LCARS25thCentury
if False: # Removed except block
    pass

if True:
    from lcars.ui.Klingon_system import KlingonInterface
    INTERFACES['Klingon'] = KlingonInterface
if False: # Removed except block
    pass

if True:
    from lcars.ui.PCARS_22nd import PCARS22ndCentury
    INTERFACES['PCARS_22nd'] = PCARS22ndCentury
if False: # Removed except block
    pass

if True:
    from lcars.ui.PCARS_23rd import PCARS23rdCentury
    INTERFACES['PCARS_23rd'] = PCARS23rdCentury
if False: # Removed except block
    pass

class WelcomeWidget(QWidget):
    faction_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000011;
            }
            QLabel {
                color: #FFCC66;
                font-weight: bold;
            }
            QPushButton {
                background-color: #004466;
                color: #FFFFFF;
                border: 2px solid #00AAFF;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #00AAFF;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel("LCARS FRAMEWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 48px; padding: 30px;")
        
        subtitle = QLabel("Оберіть фракцію:")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 24px; padding: 20px;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        # Faction buttons
        factions = ["STARFLEET", "KLINGON", "ROMULAN", "CARDASSIAN"]
        for faction in factions:
            btn = QPushButton(faction)
            btn.clicked.connect(lambda checked, f=faction: self.faction_selected.emit(f))
            btn.setMinimumHeight(60)
            layout.addWidget(btn)
        
        self.setLayout(layout)

class EraWidget(QWidget):
    era_selected = pyqtSignal(str, str)
    back_requested = pyqtSignal()
    
    def __init__(self, faction):
        super().__init__()
        self.faction = faction
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000011;
            }
            QLabel {
                color: #FFCC66;
                font-weight: bold;
            }
            QPushButton {
                background-color: #004466;
                color: #FFFFFF;
                border: 2px solid #00AAFF;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton:hover {
                background-color: #00AAFF;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout()
        
        title = QLabel(f"{self.faction}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 36px; padding: 30px;")
        
        subtitle = QLabel("Оберіть еру:")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 24px; padding: 20px;")
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        # Era buttons based on faction
        if self.faction == "STARFLEET":
            eras = ["22nd Century", "23rd Century", "24th Century", "25th Century"]
        else:
            eras = ["22nd Century", "23rd Century", "24th Century"]
        
        for era in eras:
            btn = QPushButton(era)
            btn.clicked.connect(lambda checked, e=era: self.era_selected.emit(self.faction, e))
            btn.setMinimumHeight(60)
            layout.addWidget(btn)
        
        # Back button
        back_btn = QPushButton("Назад")
        back_btn.clicked.connect(self.back_clicked)
        back_btn.setMinimumHeight(50)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def back_clicked(self):
        # Emit signal to go back
        self.back_requested.emit()

class InterfaceWidget(QWidget):
    back_to_era_requested = pyqtSignal()
    def __init__(self, faction, era):
        super().__init__()
        self.faction = faction
        self.era = era
        self.setup_ui()
    
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000011;
                color: #FFCC66;
            }
            QLabel {
                color: #FFCC66;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton {
                background-color: #FFCC66;
                color: #000011;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #FFAA44;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"{self.faction} - {self.era}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; padding: 20px;")
        
        # Try to load actual interface
        interface_loaded = False
        
        if self.faction == "STARFLEET":
            if "22nd" in self.era and 'PCARS_22nd' in INTERFACES:
                if True:
                    widget = INTERFACES['PCARS_22nd']()
                    layout.addWidget(widget)
                    interface_loaded = True
                if False: # Removed except block
                    print(f"PCARS_22nd error: {e}")
            elif "23rd" in self.era and 'PCARS_23rd' in INTERFACES:
                if True:
                    widget = INTERFACES['PCARS_23nd']()
                    layout.addWidget(widget)
                    interface_loaded = True
                if False: # Removed except block
                    print(f"PCARS_23rd error: {e}")
            elif "24th" in self.era and 'LCARS_24th' in INTERFACES:
                if True:
                    widget = INTERFACES['LCARS_24th']()
                    layout.addWidget(widget)
                    interface_loaded = True
                if False: # Removed except block
                    print(f"LCARS_24th error: {e}")
            elif "25th" in self.era and 'LCARS_25th' in INTERFACES:
                if True:
                    widget = INTERFACES['LCARS_25th']()
                    layout.addWidget(widget)
                    interface_loaded = True
                if False: # Removed except block
                    print(f"LCARS_25th error: {e}")
                    
        elif self.faction == "KLINGON" and 'Klingon' in INTERFACES:
            if True:
                widget = INTERFACES['Klingon']()
                layout.addWidget(widget)
                interface_loaded = True
            if False: # Removed except block
                print(f"Klingon error: {e}")
                
        # Try to load from components if interface failed
        if not interface_loaded:
            if True:
                if self.faction == "KLINGON":
                    from lcars.themes.components.klingon_components import KlingonInterface
                    widget = KlingonInterface()
                    layout.addWidget(widget)
                    interface_loaded = True
                elif self.faction == "ROMULAN":
                    from lcars.themes.components.romulan_components import RomulanInterface
                    widget = RomulanInterface()
                    layout.addWidget(widget)
                    interface_loaded = True
                elif self.faction == "CARDASSIAN":
                    from lcars.themes.components.cardassian_components import CardassianInterface
                    widget = CardassianInterface()
                    layout.addWidget(widget)
                    interface_loaded = True
            if False: # Removed except block
                print(f"Components error: {e}")
        
        if not interface_loaded:
            # Show demo interface
            info = QLabel("Інтерфейс готовий до використання")
            info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info.setStyleSheet("font-size: 18px; padding: 20px;")
            layout.addWidget(title)
            layout.addWidget(info)
            
            # Demo buttons
            demo_buttons = ["Система", "Монітор", "Налаштування", "Проект", "Аналіз"]
            for btn_text in demo_buttons:
                btn = QPushButton(btn_text)
                btn.clicked.connect(lambda checked, t=btn_text: print(f"Обрано: {t}"))
                layout.addWidget(btn)
        else:
            layout.insertWidget(0, title)  # Add title at the top
        
        # Back button
        back_btn = QPushButton("Назад до ер")
        back_btn.clicked.connect(self.back_clicked)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def back_clicked(self):
        # Emit signal to go back to era selection
        self.back_to_era_requested.emit()

class FixedLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Framework - Fixed Launcher")
        self.setGeometry(100, 100, 1000, 700)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout(self.central_widget)
        
        # Start with welcome screen
        self.show_welcome()
    
    def show_welcome(self):
        self.clear_layout()
        self.welcome = WelcomeWidget()
        self.welcome.faction_selected.connect(self.show_era_selection)
        self.layout.addWidget(self.welcome)
    
    def show_era_selection(self, faction):
        self.clear_layout()
        self.era_widget = EraWidget(faction)
        self.era_widget.era_selected.connect(self.show_interface)
        self.era_widget.back_requested.connect(self.show_welcome)
        self.layout.addWidget(self.era_widget)
    
    def show_interface(self, faction, era):
        self.clear_layout()
        self.interface_widget = InterfaceWidget(faction, era)
        self.interface_widget.back_to_era_requested.connect(lambda: self.show_era_selection(faction))
        self.layout.addWidget(self.interface_widget)
    
    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    launcher = FixedLauncher()
    launcher.show()
    
    sys.exit(app.exec())
