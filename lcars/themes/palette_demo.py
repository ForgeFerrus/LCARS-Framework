#!/usr/bin/env python3
"""LCARS Palette Demo - Shows all available palettes, factions, eras and themes"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFrame, QComboBox, QGridLayout, QScrollArea,
    QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt

# Import LCARS theme system
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, ERA_COLOR_PALETTES, get_palette_by_name


class PaletteDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.show_all_palettes()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Palette Demo - All Themes & Factions")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Main content with tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
    def create_header(self):
        """Create demo header"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #FFCC66;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(header)
        
        title = QLabel("LCARS PALETTE DEMO")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #000000;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        info = QLabel("All Eras • All Factions • All Themes")
        info.setStyleSheet("""
            font-size: 14px;
            color: #000000;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        layout.addWidget(info)
        
        return header
        
    def show_all_palettes(self):
        """Create tabs for different palette views"""
        
        # Tab 1: All Eras
        self.create_eras_tab()
        
        # Tab 2: All Factions
        self.create_factions_tab()
        
        # Tab 3: Combined Themes
        self.create_combined_tab()
        
        # Tab 4: Color Grid
        self.create_color_grid_tab()
        
    def create_eras_tab(self):
        """Create tab showing all eras"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("ALL LCARS ERAS")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #FFCC66;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 10px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
            QScrollBar:vertical {
                background-color: #333333;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #FFCC66;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Era list
        eras = [
            ("22nd Century", LCARSEra.PCARS_22ND, "Pre-Federation Era"),
            ("23st Century", LCARSEra.PCARS_23ST, "Early Federation"),
            ("23rd Century", LCARSEra.PCARS_23RD, "Original Series"),
            ("24th Century", LCARSEra.LCARS_24TH, "Next Generation"),
            ("25th Century", LCARSEra.LCARS_25TH, "Post-Nemesis"),
            ("29th Century", LCARSEra.TCARS_29TH, "Temporal Era")
        ]
        
        for era_name, era_enum, description in eras:
            era_widget = self.create_era_widget(era_name, era_enum, description)
            content_layout.addWidget(era_widget)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "Eras")
        
    def create_factions_tab(self):
        """Create tab showing all factions"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("ALL FACTIONS")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #FFCC66;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 10px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Factions
        factions = [
            ("Starfleet", "#FFCC66", "United Federation of Planets"),
            ("Klingon", "#CC0000", "Klingon Empire"),
            ("Romulan", "#003366", "Romulan Star Empire"),
            ("Borg", "#00FF00", "The Borg Collective"),
            ("Cardassian", "#8B4513", "Cardassian Union"),
            ("Dominion", "#4B0082", "Dominion")
        ]
        
        for faction_name, color, description in factions:
            faction_widget = self.create_faction_widget(faction_name, color, description)
            content_layout.addWidget(faction_widget)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "Factions")
        
    def create_combined_tab(self):
        """Create tab showing combined era+faction themes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("COMBINED THEMES (Era + Faction)")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #FFCC66;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 10px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #000000;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Create combinations
        eras = ["22nd", "23st", "23rd", "24th", "25th", "29th"]
        factions = ["Starfleet", "Klingon", "Romulan", "Borg", "Cardassian", "Dominion"]
        
        for era in eras:
            for faction in factions:
                combo_widget = self.create_combo_widget(era, faction)
                content_layout.addWidget(combo_widget)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "Combined")
        
    def create_color_grid_tab(self):
        """Create tab showing color grid"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Title
        title = QLabel("COLOR PALETTE GRID")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #FFCC66;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 10px;
            background: transparent;
        """)
        layout.addWidget(title)
        
        # Grid layout
        grid = QGridLayout()
        
        # Show all available palettes
        row = 0
        for era_name, palette in ERA_COLOR_PALETTES.items():
            # Era name - convert LCARSEra enum to string
            era_str = str(era_name).replace('LCARSEra.', '')
            era_label = QLabel(era_str.replace('_', ' ').title())
            era_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
                padding: 5px;
            """)
            grid.addWidget(era_label, row, 0)
            
            # Color boxes
            colors = palette.get('button_colors', [])
            for i, color in enumerate(colors[:6]):  # Show first 6 colors
                color_box = QFrame()
                color_box.setStyleSheet(f"""
                    QFrame {{
                        background-color: {color};
                        border: 1px solid #333333;
                        border-radius: 5px;
                        min-width: 40px;
                        min-height: 40px;
                    }}
                """)
                grid.addWidget(color_box, row, i + 1)
            
            row += 1
        
        layout.addLayout(grid)
        self.tabs.addTab(tab, "Color Grid")
        
    def create_era_widget(self, era_name, era_enum, description):
        """Create widget for era display"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #111111;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        
        # Left side - Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(era_name)
        name_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #FFCC66;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        info_layout.addWidget(name_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #CCCCCC;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Right side - Colors
        palette = get_era_palette(era_enum)
        colors = palette.get('button_colors', [])
        
        color_layout = QHBoxLayout()
        for color in colors[:6]:
            color_box = QFrame()
            color_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: none;
                    border-radius: 5px;
                    width: 30px;
                    height: 30px;
                }}
            """)
            color_layout.addWidget(color_box)
        
        layout.addLayout(color_layout)
        
        return widget
        
    def create_faction_widget(self, faction_name, color, description):
        """Create widget for faction display"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        # Left side - Color indicator
        color_indicator = QFrame()
        color_indicator.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 5px;
                width: 40px;
                height: 40px;
            }}
        """)
        layout.addWidget(color_indicator)
        
        # Middle - Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(faction_name)
        name_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {color};
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        info_layout.addWidget(name_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            font-size: 12px;
            color: #CCCCCC;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        info_layout.addWidget(desc_label)
        
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Right side - Theme colors
        faction_colors = self.get_faction_colors(faction_name)
        color_layout = QHBoxLayout()
        for color in faction_colors[:6]:
            color_box = QFrame()
            color_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: none;
                    border-radius: 5px;
                    width: 30px;
                    height: 30px;
                }}
            """)
            color_layout.addWidget(color_box)
        
        layout.addLayout(color_layout)
        
        return widget
        
    def create_combo_widget(self, era, faction):
        """Create widget for era+faction combination"""
        widget = QFrame()
        
        era_mapping = {
            "22nd": LCARSEra.PCARS_22ND,
            "23st": LCARSEra.PCARS_23ST,
            "23rd": LCARSEra.PCARS_23RD,
            "24th": LCARSEra.LCARS_24TH,
            "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH
        }
        
        era_enum = era_mapping.get(era, LCARSEra.LCARS_24TH)
        base_palette = get_era_palette(era_enum)
        
        # Apply faction theme
        palette = self.apply_faction_theme(base_palette, faction)
        
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {palette.get('button_colors', ['#FFCC66'])[0]};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout(widget)
        
        # Info
        info_layout = QVBoxLayout()
        
        combo_label = QLabel(f"{era} Century - {faction}")
        combo_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {palette.get('button_colors', ['#FFCC66'])[0]};
            font-family: 'Swiss 911', 'Arial', sans-serif;
            background: transparent;
        """)
        info_layout.addWidget(combo_label)
        
        layout.addLayout(info_layout)
        
        layout.addStretch()
        
        # Colors
        colors = palette.get('button_colors', [])
        color_layout = QHBoxLayout()
        for color in colors[:6]:
            color_box = QFrame()
            color_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color};
                    border: none;
                    border-radius: 5px;
                    width: 25px;
                    height: 25px;
                }}
            """)
            color_layout.addWidget(color_box)
        
        layout.addLayout(color_layout)
        
        return widget
        
    def get_faction_colors(self, faction):
        """Get faction-specific colors"""
        faction_themes = {
            "Starfleet": ['#FFCC66', '#FF9900', '#9999FF', '#664466', '#FF6666', '#66FF66'],
            "Klingon": ['#CC0000', '#8B0000', '#FF6B6B', '#4B0000', '#FF4444', '#990000'],
            "Romulan": ['#003366', '#001144', '#336699', '#002244', '#4488BB', '#005577'],
            "Borg": ['#006600', '#004400', '#008800', '#003300', '#00AA00', '#005500'],
            "Cardassian": ['#8B4513', '#654321', '#A0522D', '#4B2F1A', '#CD853F', '#704214'],
            "Dominion": ['#4B0082', '#663399', '#8B008B', '#3D1475', '#9932CC', '#6A0DAD']
        }
        return faction_themes.get(faction, ['#FFCC66', '#FF9900', '#9999FF'])
        
    def apply_faction_theme(self, base_palette, faction):
        """Apply faction-specific modifications"""
        palette = base_palette.copy()
        
        faction_themes = {
            "Starfleet": {},
            "Klingon": {
                'button_colors': ['#CC0000', '#8B0000', '#FF6B6B', '#4B0000', '#FF4444', '#990000']
            },
            "Romulan": {
                'button_colors': ['#003366', '#001144', '#336699', '#002244', '#4488BB', '#005577']
            },
            "Borg": {
                'button_colors': ['#006600', '#004400', '#008800', '#003300', '#00AA00', '#005500'],
                'text': '#00FF00'
            },
            "Cardassian": {
                'button_colors': ['#8B4513', '#654321', '#A0522D', '#4B2F1A', '#CD853F', '#704214']
            },
            "Dominion": {
                'button_colors': ['#4B0082', '#663399', '#8B008B', '#3D1475', '#9932CC', '#6A0DAD']
            }
        }
        
        if faction in faction_themes:
            faction_mods = faction_themes[faction]
            for key, value in faction_mods.items():
                palette[key] = value
        
        return palette


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set dark theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #000000;
        }
        QTabWidget::pane {
            border: 2px solid #FFCC66;
            background-color: #000000;
            border-radius: 10px;
        }
        QTabBar::tab {
            background-color: #333333;
            color: #FFCC66;
            padding: 8px 15px;
            margin-right: 2px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            font-weight: bold;
        }
        QTabBar::tab:selected {
            background-color: #FFCC66;
            color: #000000;
        }
        QTabBar::tab:hover {
            background-color: #FF9933;
        }
    """)
    
    demo = PaletteDemo()
    demo.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
