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
    QLabel, QPushButton, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt

# Import existing theme files
from lcars.themes.lcars_palette import LCARSEra, ERA_COLOR_PALETTES
from lcars.themes.theme import Theme
from lcars.themes.components import (
    StarfleetButton, StarfleetPanel, StarfleetDisplay,
    KlingonButton, KlingonPanel, KlingonDisplay,
    RomulanButton, RomulanPanel, RomulanDisplay,
    CardassianButton, CardassianPanel, CardassianDisplay
)
from lcars.themes.klingon_theme import create_klingon_interface
from lcars.themes.romulan_theme import create_romulan_interface
from lcars.themes.cardassian_theme import create_cardassian_interface


class LCARSThemeDemo(QMainWindow):
    """LCARS Theme Demo - Shows existing working themes"""
    
    def __init__(self):
        super().__init__()
        self.current_era = LCARSEra.LCARS_24TH
        self.current_faction = "starfleet"
        self.init_ui()
        self.apply_faction_styling()
        self.show_current_theme()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Theme Demo")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Central widget with main layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create centered container
        container = QWidget()
        container.setMaximumSize(1200, 800)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(20)
        
        # Header
        header = QLabel("LCARS THEME DEMO")
        header.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #FFCC66;
                padding: 20px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(header)
        
        # Faction selection - FIRST
        faction_label = QLabel("SELECT FACTION")
        faction_label.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        faction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(faction_label)
        
        faction_buttons = QWidget()
        faction_button_layout = QHBoxLayout(faction_buttons)
        faction_button_layout.setSpacing(10)
        
        self.faction_buttons = []
        factions = ["starfleet", "klingon", "romulan", "cardassian"]
        for faction in factions:
            btn = QPushButton(faction.upper())
            btn.clicked.connect(lambda checked, f=faction: self.select_faction(f))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """)
            self.faction_buttons.append(btn)
            faction_button_layout.addWidget(btn)
        
        faction_button_layout.addStretch()
        container_layout.addWidget(faction_buttons)
        
        # Era selection - SECOND (based on faction)
        self.era_label = QLabel("SELECT ERA")
        self.era_label.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        self.era_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.era_label)
        
        self.era_buttons = QWidget()
        self.era_button_layout = QHBoxLayout(self.era_buttons)
        self.era_button_layout.setSpacing(10)
        
        # Create era buttons
        self.era_button_list = []
        for era in LCARSEra:
            btn = QPushButton(era.value.replace("_", " ").title())
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """)
            self.era_button_list.append(btn)
            self.era_button_layout.addWidget(btn)
        
        self.era_button_layout.addStretch()
        container_layout.addWidget(self.era_buttons)
        
        # Theme display area
        self.display_area = QWidget()
        self.display_layout = QVBoxLayout(self.display_area)
        container_layout.addWidget(self.display_area)
        
        # Exit button
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: #FFFFFF;
                padding: 15px 30px;
                font-weight: bold;
                font-size: 16px;
                border-radius: 6px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        
        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        exit_layout.addWidget(exit_btn)
        exit_layout.addStretch()
        container_layout.addLayout(exit_layout)
        
        # Center the container
        main_layout.addStretch()
        main_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()
        
    def select_era(self, era: LCARSEra):
        self.current_era = era
        self.show_current_theme()
        
    def select_faction(self, faction: str):
        self.current_faction = faction
        self.apply_faction_styling()
        self.show_current_theme()
        
    def apply_faction_styling(self):
        """Apply authentic faction interface styling to controls"""
        if self.current_faction == "klingon":
            # Klingon styling - red/orange theme
            for btn in self.faction_buttons:
                if btn.text().lower() == "klingon":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #8B0000;
                            color: #FFD700;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #FF4500;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #330000;
                            color: #FFCCCC;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #550000;
                        }
                    """)
            for btn in self.era_button_list:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #330000;
                        color: #FFCCCC;
                        padding: 10px 15px;
                        font-weight: bold;
                        border-radius: 4px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #550000;
                    }
                """)
        elif self.current_faction == "romulan":
            # Romulan styling - green theme
            for btn in self.faction_buttons:
                if btn.text().lower() == "romulan":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #006666;
                            color: #00FF99;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #008B8B;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #003333;
                            color: #00FFAA;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #005555;
                        }
                    """)
            for btn in self.era_button_list:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #003333;
                        color: #00FFAA;
                        padding: 10px 15px;
                        font-weight: bold;
                        border-radius: 4px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #005555;
                    }
                """)
        elif self.current_faction == "cardassian":
            # Cardassian styling - orange/gray theme
            for btn in self.faction_buttons:
                if btn.text().lower() == "cardassian":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #CC3300;
                            color: #CCCCCC;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #FF3300;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #1A1A1A;
                            color: #CCCCCC;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #2A2A2A;
                        }
                    """)
            for btn in self.era_button_list:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1A1A1A;
                        color: #CCCCCC;
                        padding: 10px 15px;
                        font-weight: bold;
                        border-radius: 4px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #2A2A2A;
                    }
                """)
        else:
            # Starfleet/default styling
            for btn in self.faction_buttons:
                if btn.text().lower() == "starfleet":
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #FF9900;
                            color: #000000;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #FFCC66;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #666666;
                            color: #FFFFFF;
                            padding: 10px 15px;
                            font-weight: bold;
                            border-radius: 4px;
                            min-width: 100px;
                        }
                        QPushButton:hover {
                            background-color: #999999;
                        }
                    """)
            for btn in self.era_button_list:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #666666;
                        color: #FFFFFF;
                        padding: 10px 15px;
                        font-weight: bold;
                        border-radius: 4px;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #999999;
                    }
                """)
        for btn in self.era_button_list:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666666;
                    color: #FFFFFF;
                    padding: 10px 15px;
                    font-weight: bold;
                    border-radius: 4px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #999999;
                }
            """)
        
    def show_current_theme(self):
        """Show current theme from existing files"""
        # Clear display
        while self.display_layout.count():
            item = self.display_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Show current selection
        info = QLabel(f"ERA: {self.current_era.value.replace('_', ' ').upper()} | FACTION: {self.current_faction.upper()}")
        info.setStyleSheet("font-size: 20px; color: #FFCC66; padding: 15px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(info)
        
        # Show authentic faction interface
        if self.current_faction == "starfleet":
            # Use ready-made Starfleet components
            starfleet_panel = StarfleetPanel()
            self.display_layout.addWidget(starfleet_panel)
            
            # Add Starfleet buttons
            button_layout = QHBoxLayout()
            warp_btn = StarfleetButton("WARP DRIVE")
            shields_btn = StarfleetButton("SHIELDS")
            phasers_btn = StarfleetButton("PHASERS")
            button_layout.addWidget(warp_btn)
            button_layout.addWidget(shields_btn)
            button_layout.addWidget(phasers_btn)
            self.display_layout.addLayout(button_layout)
            
            # Add Starfleet display
            display = StarfleetDisplay("STARFLEET SYSTEMS ONLINE", "title")
            self.display_layout.addWidget(display)
            
        elif self.current_faction == "klingon":
            # Use ready-made Klingon components
            klingon_panel = KlingonPanel()
            self.display_layout.addWidget(klingon_panel)
            
            # Add Klingon buttons
            button_layout = QHBoxLayout()
            weapons_btn = KlingonButton("WEAPONS")
            shields_btn = KlingonButton("SHIELDS")
            cloak_btn = KlingonButton("CLOAK")
            button_layout.addWidget(weapons_btn)
            button_layout.addWidget(shields_btn)
            button_layout.addWidget(cloak_btn)
            self.display_layout.addLayout(button_layout)
            
            # Add Klingon display
            display = KlingonDisplay("KLINGON EMPIRE - BATTLE READY", "title")
            self.display_layout.addWidget(display)
            
        elif self.current_faction == "romulan":
            # Use ready-made Romulan components
            romulan_panel = RomulanPanel()
            self.display_layout.addWidget(romulan_panel)
            
            # Add Romulan buttons
            button_layout = QHBoxLayout()
            cloak_btn = RomulanButton("CLOAKING DEVICE")
            sensors_btn = RomulanButton("SENSORS")
            power_btn = RomulanButton("POWER")
            button_layout.addWidget(cloak_btn)
            button_layout.addWidget(sensors_btn)
            button_layout.addWidget(power_btn)
            self.display_layout.addLayout(button_layout)
            
            # Add Romulan display
            display = RomulanDisplay("ROMULAN STAR EMPIRE - STEALTH MODE", "title")
            self.display_layout.addWidget(display)
            
        elif self.current_faction == "cardassian":
            # Use ready-made Cardassian components
            cardassian_panel = CardassianPanel()
            self.display_layout.addWidget(cardassian_panel)
            
            # Add Cardassian buttons
            button_layout = QHBoxLayout()
            weapons_btn = CardassianButton("WEAPONS")
            shields_btn = CardassianButton("SHIELDS")
            tactical_btn = CardassianButton("TACTICAL")
            button_layout.addWidget(weapons_btn)
            button_layout.addWidget(shields_btn)
            button_layout.addWidget(tactical_btn)
            self.display_layout.addLayout(button_layout)
            
            # Add Cardassian display
            display = CardassianDisplay("CARDASSIAN UNION - ORDER MAINTAINED", "title")
            self.display_layout.addWidget(display)
        
        # Also show palette colors
        if self.current_faction in ["klingon", "romulan", "cardassian"]:
            # Show faction palette with era support
            faction_palette = Theme.generate_faction_palette(self.current_faction, self.current_era.value)
            if faction_palette:
                self.show_faction_palette(faction_palette)
            else:
                self.show_era_palette()
        else:
            # Show era palette for starfleet and others
            self.show_era_palette()
            
    def show_faction_palette(self, palette):
        """Show faction palette from Theme.generate_faction_palette"""
        # Apply background
        bg_color = palette[0] if palette else '#000000'
        self.setStyleSheet(f"background-color: {bg_color};")
        
        # Show palette colors
        colors_title = QLabel(f"FACTION PALETTE COLORS")
        colors_title.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        colors_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(colors_title)
        
        # Display colors directly from list
        unique_colors = palette if palette else []
        
        # Color grid
        color_grid = QWidget()
        grid_layout = QGridLayout(color_grid)
        grid_layout.setSpacing(10)
        
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
            
    def show_era_palette(self):
        """Show era palette from existing files"""
        palette = ERA_COLOR_PALETTES[self.current_era]
        
        # Apply background
        bg_color = palette.get('background', '#000000')
        self.setStyleSheet(f"background-color: {bg_color};")
        
        # Show palette colors
        colors_title = QLabel("ERA PALETTE COLORS")
        colors_title.setStyleSheet("font-size: 18px; color: #FFCC66; padding: 10px;")
        colors_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_layout.addWidget(colors_title)
        
        # Extract colors from palette
        all_colors = []
        for value in palette.values():
            if isinstance(value, list):
                all_colors.extend(value)
            elif isinstance(value, str) and value.startswith('#'):
                all_colors.append(value)
        
        # Remove duplicates and display
        seen = set()
        unique_colors = []
        for color in all_colors:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)
        
        # Color grid
        color_grid = QWidget()
        grid_layout = QGridLayout(color_grid)
        grid_layout.setSpacing(10)
        
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


def main(argv: Optional[list[str]] = None) -> int:
    app = QApplication.instance() or QApplication(sys.argv or [])
    demo = LCARSThemeDemo()
    demo.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())