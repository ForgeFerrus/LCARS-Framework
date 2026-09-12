#!/usr/bin/env python3
"""LCARS Theme Selector - Simple working version"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt

from lcars.themes.lcars_palette import LCARSEra, ERA_COLOR_PALETTES

class ThemeSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_era = LCARSEra.LCARS_24TH
        self.current_faction = "starfleet"
        self.init_ui()
        self.apply_current_palette()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Theme Selector")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("LCARS THEME SELECTOR")
        header.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #FFCC66;
            padding: 20px;
            text-align: center;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Control panel
        controls = QWidget()
        control_layout = QVBoxLayout(controls)
        control_layout.setSpacing(15)
        
        # Era buttons
        era_label = QLabel("SELECT ERA")
        era_label.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        control_layout.addWidget(era_label)
        
        era_buttons = QWidget()
        era_button_layout = QHBoxLayout(era_buttons)
        era_button_layout.setSpacing(10)
        
        for era in LCARSEra:
            btn = QPushButton(era.value.replace("_", " ").title())
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    border: none;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """)
            era_button_layout.addWidget(btn)
        
        era_button_layout.addStretch()
        control_layout.addWidget(era_buttons)
        
        # Faction buttons
        faction_label = QLabel("SELECT FACTION")
        faction_label.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        control_layout.addWidget(faction_label)
        
        faction_buttons = QWidget()
        faction_button_layout = QHBoxLayout(faction_buttons)
        faction_button_layout.setSpacing(10)
        
        factions = ["starfleet", "klingon", "romulan", "cardassian"]
        for faction in factions:
            btn = QPushButton(faction.upper())
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    border: none;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """)
            faction_button_layout.addWidget(btn)
        
        faction_button_layout.addStretch()
        control_layout.addWidget(faction_buttons)
        
        layout.addWidget(controls)
        
        # Palette display
        self.display_area = QWidget()
        self.display_layout = QVBoxLayout(self.display_area)
        layout.addWidget(self.display_area)
        
        # Exit button
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: #FFFFFF;
                border: none;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        exit_btn_layout = QHBoxLayout()
        exit_btn_layout.addStretch()
        exit_btn_layout.addWidget(exit_btn)
        exit_btn_layout.addStretch()
        layout.addLayout(exit_btn_layout)
        
    def select_era(self, era: LCARSEra):
        self.current_era = era
        self.current_faction = "starfleet"
        self.apply_current_palette()
        
    def select_faction(self, faction: str):
        self.current_faction = faction
        self.apply_current_palette()
        
    def get_current_palette(self):
        # Try faction-specific palette            
        # Use era palette
        return ERA_COLOR_PALETTES[self.current_era]
        
    def apply_current_palette(self):
        # Clear display
        while self.display_layout.count():
            item = self.display_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get palette
        palette = self.get_current_palette()
        
        # Apply background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {list(palette.values())[0] if palette.values() else '#000000'};
            }}
        """)
        
        # Show current selection
        info = QLabel(f"ERA: {self.current_era.value.replace('_', ' ').upper()} | FACTION: {self.current_faction.upper()}")
        info.setStyleSheet("font-size: 20px; color: #FFCC66; padding: 15px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(info)
        
        # Show colors
        colors_title = QLabel("COLOR PALETTE")
        colors_title.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        colors_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(colors_title)
        
        # Color grid
        color_grid = QWidget()
        grid_layout = QGridLayout(color_grid)
        grid_layout.setSpacing(10)
        
        # Extract colors
        colors = []
        for value in palette.values():
            if isinstance(value, str) and value.startswith('#'):
                colors.append(value)
        
        # Remove duplicates
        unique_colors = []
        seen = set()
        for color in colors:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)
        
        # Display colors
        for i, color in enumerate(unique_colors[:24]):
            color_frame = QFrame()
            color_frame.setFixedSize(60, 60)
            color_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: 2px solid #FFFFFF;
                    border-radius: 6px;
                }}
            """)
            grid_layout.addWidget(color_frame, i // 8, i % 8)
        
        self.display_layout.addWidget(color_grid)


def main():
    app = QApplication.instance() or QApplication(sys.argv)
    selector = ThemeSelector()
    selector.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
