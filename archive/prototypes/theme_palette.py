#!/usr/bin/env python3
"""LCARS Theme Demo - Simple demo of existing theme files"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor

# Import existing theme files
from lcars.themes.lcars_palette import LCARSEra, ERA_COLOR_PALETTES
from lcars.themes.theme import get_faction_colors

class LCARSThemeDemo(QMainWindow):
    """LCARS Theme Demo - Shows existing working themes with Premium Design"""
    
    def __init__(self):
        super().__init__()
        self.current_era = LCARSEra.LCARS_24TH
        self.current_faction = "starfleet"
        
        self.colors = {
            'background': '#000000',
            'primary': '#FF9900', 
            'secondary': '#99CCFF',
            'tertiary': '#CC6600',
            'text': '#FF9900',
            'border': '#FF9900'
        }
        
        self.init_ui()
        self.update_local_styles()
        self.show_current_theme()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Theme Demo (Premium)")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Central widget
        central = QWidget()
        central.setStyleSheet("background-color: #000000;")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- Header ---
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-top: 4px solid {self.colors['primary']};
                border-bottom: 2px solid {self.colors['primary']};
            }}
        """)
        header_layout = QHBoxLayout(header)
        
        title = QLabel("LCARS THEME PALETTE VIEWER")
        title.setStyleSheet(f"""
            font-size: 32px; 
            font-weight: bold; 
            color: {self.colors['primary']};
            background: transparent;
            border: none;
            font-family: 'Swiss 911', 'Arial';
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Exit Button
        exit_btn = QPushButton("TERMINATE")
        exit_btn.setFixedSize(150, 40)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #CC0000;
                color: #FFFFFF;
                border: none;
                font-weight: bold;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: #FF0000;
            }}
        """)
        header_layout.addWidget(exit_btn)
        main_layout.addWidget(header)
        
        # --- Controls Area ---
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                border: 1px solid {self.colors['secondary']};
                border-radius: 10px;
                background-color: #050505;
            }}
        """)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Faction Selector
        lbl_faction = QLabel("SELECT FACTION IDENTITY")
        lbl_faction.setStyleSheet(f"color: {self.colors['secondary']}; font-weight: bold; border: none;")
        controls_layout.addWidget(lbl_faction)
        
        faction_layout = QHBoxLayout()
        self.faction_buttons = []
        for f in ["starfleet", "klingon", "romulan", "cardassian"]:
            btn = QPushButton(f.upper())
            btn.setCheckable(True)
            btn.clicked.connect(lambda c, x=f: self.select_faction(x))
            btn.setFixedSize(140, 45)
            faction_layout.addWidget(btn)
            self.faction_buttons.append(btn)
        faction_layout.addStretch()
        controls_layout.addLayout(faction_layout)
        
        # Era Selector
        lbl_era = QLabel("SELECT TEMPORAL ERA")
        lbl_era.setStyleSheet(f"color: {self.colors['secondary']}; font-weight: bold; border: none; margin-top: 10px;")
        controls_layout.addWidget(lbl_era)
        
        era_scroll = QScrollArea()
        era_scroll.setWidgetResizable(True)
        era_scroll.setFixedHeight(70)
        era_scroll.setStyleSheet("background: transparent; border: none;")
        era_widget = QWidget()
        era_layout = QHBoxLayout(era_widget)
        
        self.era_buttons = []
        for era in LCARSEra:
            btn = QPushButton(era.value.replace("_", " ").title())
            btn.setCheckable(True)
            btn.clicked.connect(lambda c, x=era: self.select_era(x))
            btn.setFixedSize(120, 40)
            era_layout.addWidget(btn)
            self.era_buttons.append(btn)
        era_layout.addStretch()
        era_scroll.setWidget(era_widget)
        controls_layout.addWidget(era_scroll)
        
        main_layout.addWidget(controls_frame)
        
        # --- Display Area ---
        self.display_area = QFrame()
        self.display_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.display_layout = QGridLayout(self.display_area)
        self.display_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(self.display_area)
        
    def update_local_styles(self):
        """Update buttons styling based on selection"""
        # Reset all
        base_style = """
            QPushButton {
                background-color: #222222;
                color: #888888;
                border: 1px solid #444444;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
                color: #FFFFFF;
            }
        """
        active_style = f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: #000000;
                border: 1px solid {self.colors['primary']};
                border-radius: 6px;
                font-weight: bold;
            }}
        """
        
        # Color logic based on faction
        if self.current_faction == 'romulan':
            self.colors['primary'] = '#00CC99' # Green
            self.colors['secondary'] = '#006666'
        elif self.current_faction == 'klingon':
            self.colors['primary'] = '#CC0000' # Red
            self.colors['secondary'] = '#CC6600'
        elif self.current_faction == 'cardassian':
            self.colors['primary'] = '#CC9900' # Gold/Brown
            self.colors['secondary'] = '#996600'
        else: # Starfleet
            self.colors['primary'] = '#FF9900' # Orange
            self.colors['secondary'] = '#99CCFF'
            
        # Re-apply header title style
        title = self.findChild(QLabel) # First label is title
        if title:
             title.setStyleSheet(f"""
                font-size: 32px; 
                font-weight: bold; 
                color: {self.colors['primary']};
                background: transparent;
                border: none;
                font-family: 'Swiss 911', 'Arial';
            """)

        # Apply styles to buttons
        for btn in self.faction_buttons:
            if btn.text().lower() == self.current_faction:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(base_style)
                
        for btn in self.era_buttons:
            # Match era text
            if btn.text().lower().replace(" ", "_") == self.current_era.value:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(base_style)
                
    def select_faction(self, faction):
        self.current_faction = faction
        self.update_local_styles()
        self.show_current_theme()
        
    def select_era(self, era):
        self.current_era = era
        self.update_local_styles()
        self.show_current_theme()
        
    def show_current_theme(self):
        # Clear grid
        while self.display_layout.count():
            item = self.display_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Get colors
        palette = []
        colors_dict = {}
        
        try:
            if self.current_faction != 'starfleet':
                colors_dict = get_faction_colors(self.current_faction, self.current_era.value)
            else:
                colors_dict = ERA_COLOR_PALETTES.get(self.current_era, {})
                
            # Flatten dictionary to list of color strings
            if isinstance(colors_dict, dict):
                for val in colors_dict.values():
                    if isinstance(val, list):
                        palette.extend([c for c in val if isinstance(c, str)])
                    elif isinstance(val, str) and val.startswith('#'):
                        palette.append(val)
        except Exception as e:
            print(f"Error fetching colors: {e}")
            
        unique_colors = sorted(list(set(palette)))
        
        # Display
        if not unique_colors:
            lbl = QLabel("NO COLOR DATA AVAILABLE FOR THIS CONFIGURATION")
            lbl.setStyleSheet("color: #666; font-size: 24px;")
            self.display_layout.addWidget(lbl, 0, 0)
            return
            
        # Create Grid
        row, col = 0, 0
        max_cols = 8
        
        for color_code in unique_colors:
            # Color Box
            box = QFrame()
            box.setFixedSize(100, 100)
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color_code};
                    border: 1px solid #333;
                    border-radius: 8px;
                }}
            """)
            
            # Label inside
            lbl = QLabel(color_code)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # Calculate contrast text color
            c = QColor(color_code)
            text_col = "#000000" if (c.red()*0.299 + c.green()*0.587 + c.blue()*0.114) > 150 else "#FFFFFF"
            
            lbl.setStyleSheet(f"color: {text_col}; font-weight: bold; background: transparent; border: none;")
            
            layout = QVBoxLayout(box)
            layout.addWidget(lbl)
            
            self.display_layout.addWidget(box, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

def main(argv: Optional[list[str]] = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv or [])
    demo = LCARSThemeDemo()
    demo.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())