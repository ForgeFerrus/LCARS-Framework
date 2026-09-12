#!/usr/bin/env python3
"""
LCARS Full Demo - Comprehensive demonstration of all themes, palettes, and factions
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QTabWidget, QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Ensure the project root is in the Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

# Ensure the lcars_theme module is in the Python path
lcars_ui_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(lcars_ui_dir))

# Ensure the lcars/themes module is in the Python path
lcars_themes_dir = project_root / 'lcars' / 'themes'
if str(lcars_themes_dir) not in sys.path:
    sys.path.insert(0, str(lcars_themes_dir))

from lcars.themes.lcars_palette import ERA_THEMES, SHIP_CLASS_PALETTES

class LCARSFullDemo(QMainWindow):
    """Comprehensive LCARS demonstration window"""

    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()

    def setup_window(self):
        """Configure the main window"""
        self.setWindowTitle("LCARS FULL DEMONSTRATION")
        self.setGeometry(100, 100, 1400, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

    def setup_ui(self):
        """Create the user interface"""
        # Header
        self.title = QLabel("LCARS FULL DEMONSTRATION")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.main_layout.addWidget(self.title)

        # Tabbed interface
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Add tabs
        self.create_palette_tab()
        self.create_elements_tab()
        self.create_faction_tab()

    def create_palette_tab(self):
        """Create a tab to demonstrate color palettes"""
        palette_tab = QWidget()
        layout = QVBoxLayout(palette_tab)

        # Color swatches
        self.color_swatches = {}
        for era, palette in ERA_THEMES.items():
            group = QGroupBox(f"{era.name} Palette")
            group_layout = QGridLayout(group)

            for key, color in palette.items():
                swatch = QFrame()
                swatch.setFixedSize(80, 50)
                swatch.setStyleSheet(f"background-color: {color};")

                label = QLabel(key)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.addWidget(swatch)
                container_layout.addWidget(label)

                group_layout.addWidget(container)

            layout.addWidget(group)

        self.tabs.addTab(palette_tab, "Color Palettes")

    def create_elements_tab(self):
        """Create a tab to demonstrate UI elements"""
        elements_tab = QWidget()
        layout = QVBoxLayout(elements_tab)

        # Example buttons
        button_group = QGroupBox("Buttons")
        button_layout = QVBoxLayout(button_group)

        for era in FederationEra:
            theme = get_faction_era_theme(era)
            button = QPushButton(f"{era.name} Button")
            button.setStyleSheet(get_lcars_stylesheet(theme))
            button_layout.addWidget(button)

        layout.addWidget(button_group)
        self.tabs.addTab(elements_tab, "UI Elements")

    def create_faction_tab(self):
        """Create a tab to demonstrate factions"""
        faction_tab = QWidget()
        layout = QVBoxLayout(faction_tab)

        for faction in ["Federation", "Klingon", "Romulan"]:
            group = QGroupBox(f"{faction} Themes")
            group_layout = QVBoxLayout(group)

            for era in ["22nd", "23rd", "24th", "25th", "29th"]:
                theme = get_theme_by_name(faction, era)
                label = QLabel(f"{faction} {era} Theme")
                label.setStyleSheet(get_title_stylesheet(f"{faction} {era} Theme", theme))
                group_layout.addWidget(label)

            layout.addWidget(group)

        self.tabs.addTab(faction_tab, "Factions")

    def update_console_content(self):
        """Update console content based on current theme"""
        pass


def main():
    """Run the LCARS full demonstration"""
    app = QApplication(sys.argv)
    demo = LCARSFullDemo()
    demo.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
