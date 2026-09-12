"""
LCARS BIOS - System Configuration Interface
Styled as LCARS, functions like BIOS
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QStackedWidget, QSlider, QComboBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QKeyEvent
# Titanium Bridge Migration: from typing import Optional

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color


class LCARSSection(QFrame):
    """LCARS settings section"""
    def __init__(self, title, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                border-radius: 20px;
            }}
        """)
        
        section_layout = QVBoxLayout(self)
        section_layout.setContentsMargins(20, 15, 20, 15)
        section_layout.setSpacing(12)
        self.section_layout = section_layout
        
        # Title
        title_label = QLabel(f"◢ {title}")
        title_label.setStyleSheet("color: #000; font-size: 16px; font-weight: bold; background: transparent; border: none;")
        section_layout.addWidget(title_label)
    
    def add_option(self, label, widget, color):
        """Add option row"""
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 5, 0, 5)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {color}; font-size: 13px; background: transparent;")
        row_layout.addWidget(label_widget)
        
        row_layout.addStretch()
        row_layout.addWidget(widget)
        
        self.section_layout.addWidget(row)


class DynamicSelector(QComboBox):
    """LCARS-styled dropdown with dynamic colors"""
    def __init__(self, era, button_index=0):
        super().__init__()
        self.era = era
        self.button_index = button_index
        self.setFixedWidth(200)
        
        # Dynamic color cycling
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer.setInterval(2500)
        
        self.update_style()
    
    def cycle_color(self):
        self.update_style()
    
    def update_style(self):
        color = get_random_button_color(self.era)
        self.setStyleSheet(f"""
            QComboBox {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 12px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 12px;
            }}
            QComboBox:hover {{
                background-color: {self.brighten(color)};
            }}
        """)
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()


class LCARSBios(QMainWindow):
    """LCARS BIOS Configuration System"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS BIOS v25.0")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        
        self.apply_theme()
        self.setup_ui()
        
        self.showFullScreen()
    
    def apply_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
    
    def setup_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Left menu
        menu = self.create_menu()
        content_layout.addWidget(menu)
        
        # Settings panels
        self.settings_stack = QStackedWidget()
        self.create_settings_pages()
        content_layout.addWidget(self.settings_stack, 1)
        
        main_layout.addWidget(content, 1)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self):
        """Header bar"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {self.colors['button_colors'][0]}; border-radius: 0px;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 10, 30, 10)
        
        title = QLabel("◆ LCARS SYSTEM CONFIGURATION")
        title.setStyleSheet("color: #000; font-size: 28px; font-weight: bold; font-family: 'Swis721 BT';")
        h_layout.addWidget(title)
        
        h_layout.addStretch()
        
        version = QLabel("BIOS v25.0")
        version.setStyleSheet("color: #000; font-size: 16px; font-weight: bold;")
        h_layout.addWidget(version)
        
        return header
    
    def create_menu(self):
        """Left menu"""
        menu = QFrame()
        menu.setFixedWidth(280)
        
        menu_layout = QVBoxLayout(menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(8)
        
        menu_items = [
            ("SYSTEM INFO", 0),
            ("DISPLAY", 1),
            ("ERA SELECTION", 2),
            ("FACTION", 3),
            ("LANGUAGE", 4),
            ("KEYBOARD", 5),
            ("NETWORK", 6),
            ("ADVANCED", 7),
        ]
        
        self.menu_buttons = []
        for label, index in menu_items:
            btn = QPushButton(f"◢ {label}")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda _, i=index: self.switch_page(i))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['button_colors'][index % len(self.colors['button_colors'])]};
                    color: #000;
                    border: none;
                    border-radius: 15px;
                    text-align: left;
                    padding-left: 20px;
                    font-weight: bold;
                    font-size: 13px;
                    font-family: Arial, sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {self.brighten(self.colors['button_colors'][index % len(self.colors['button_colors'])])};
                }}
            """)
            self.menu_buttons.append(btn)
            menu_layout.addWidget(btn)
        
        menu_layout.addStretch()
        
        # Exit button
        exit_btn = QPushButton("◢ EXIT")
        exit_btn.setFixedHeight(60)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['alert_colors'][0]};
                color: #000;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['alert_colors'][1]};
            }}
        """)
        menu_layout.addWidget(exit_btn)
        
        return menu
    
    def create_settings_pages(self):
        """Create all settings pages"""
        
        # System Info
        system_page = QWidget()
        system_layout = QVBoxLayout(system_page)
        system_layout.setSpacing(20)
        
        info_section = LCARSSection("SYSTEM INFORMATION", self.colors['button_colors'][0])
        info_section.add_option("BIOS Version:", QLabel("v25.0"), self.colors['text'])
        info_section.add_option("Build Date:", QLabel(datetime.now().strftime("%Y-%m-%d")), self.colors['text'])
        info_section.add_option("Platform:", QLabel("LCARS Framework"), self.colors['text'])
        system_layout.addWidget(info_section)
        system_layout.addStretch()
        
        # Display
        display_page = QWidget()
        display_layout = QVBoxLayout(display_page)
        display_layout.setSpacing(20)
        
        display_section = LCARSSection("DISPLAY SETTINGS", self.colors['button_colors'][1])
        
        resolution_combo = DynamicSelector(self.current_era, button_index=0)
        resolution_combo.addItems(["1920x1080", "2560x1440", "3840x2160"])
        display_section.add_option("Resolution:", resolution_combo, self.colors['text'])
        
        refresh_combo = DynamicSelector(self.current_era, button_index=1)
        refresh_combo.addItems(["60 Hz", "120 Hz", "144 Hz"])
        display_section.add_option("Refresh Rate:", refresh_combo, self.colors['text'])
        
        display_layout.addWidget(display_section)
        display_layout.addStretch()
        
        # Era Selection
        era_page = QWidget()
        era_layout = QVBoxLayout(era_page)
        era_layout.setSpacing(20)
        
        era_section = LCARSSection("ERA SELECTION", self.colors['button_colors'][2])
        
        era_combo = DynamicSelector(self.current_era, button_index=2)
        era_combo.addItems(["22nd Century", "23rd Century", "24th Century", "25th Century (Current)", "29th Century"])
        era_combo.setCurrentIndex(3)
        era_section.add_option("LCARS Era:", era_combo, self.colors['text'])
        
        era_layout.addWidget(era_section)
        
        era_info = QLabel("Each era features unique color palettes and design elements.\n25th Century is recommended for modern systems.")
        era_info.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px; background: transparent; padding: 20px;")
        era_info.setWordWrap(True)
        era_layout.addWidget(era_info)
        era_layout.addStretch()
        
        # Faction
        faction_page = QWidget()
        faction_layout = QVBoxLayout(faction_page)
        faction_layout.setSpacing(20)
        
        faction_section = LCARSSection("FACTION CONFIGURATION", self.colors['button_colors'][3])
        
        faction_combo = DynamicSelector(self.current_era, button_index=3)
        faction_combo.addItems([
            "United Federation of Planets",
            "Klingon Empire",
            "Romulan Star Empire",
            "Vulcan High Command",
            "Borg Collective"
        ])
        faction_section.add_option("Active Faction:", faction_combo, self.colors['text'])
        
        greeting_combo = DynamicSelector(self.current_era, button_index=4)
        greeting_combo.addItems([
            "Live Long and Prosper (Vulcan)",
            "Qa'pla! (Klingon)",
            "Make It So (Starfleet)",
            "Resistance is Futile (Borg)"
        ])
        faction_section.add_option("Boot Greeting:", greeting_combo, self.colors['text'])
        
        faction_layout.addWidget(faction_section)
        faction_layout.addStretch()
        
        # Language
        language_page = QWidget()
        language_layout = QVBoxLayout(language_page)
        language_layout.setSpacing(20)
        
        lang_section = LCARSSection("LANGUAGE SETTINGS", self.colors['button_colors'][0])
        
        lang_combo = DynamicSelector(self.current_era, button_index=5)
        lang_combo.addItems(["English", "Ukrainian (Українська)", "Klingon (tlhIngan)", "Vulcan"])
        lang_combo.setCurrentIndex(1)
        lang_section.add_option("Interface Language:", lang_combo, self.colors['text'])
        
        language_layout.addWidget(lang_section)
        language_layout.addStretch()
        
        # Keyboard
        keyboard_page = QWidget()
        keyboard_layout = QVBoxLayout(keyboard_page)
        keyboard_layout.setSpacing(20)
        
        kbd_section = LCARSSection("KEYBOARD CONFIGURATION", self.colors['button_colors'][1])
        
        kbd_layout_combo = DynamicSelector(self.current_era, button_index=6)
        kbd_layout_combo.addItems(["QWERTY", "QWERTZ", "AZERTY", "Dvorak"])
        kbd_section.add_option("Layout:", kbd_layout_combo, self.colors['text'])
        
        keyboard_layout.addWidget(kbd_section)
        keyboard_layout.addStretch()
        
        # Network
        network_page = QWidget()
        network_layout = QVBoxLayout(network_page)
        network_layout.setSpacing(20)
        
        net_section = LCARSSection("NETWORK CONFIGURATION", self.colors['button_colors'][2])
        net_section.add_option("Subspace Link:", QLabel("ACTIVE"), self.colors['button_colors'][2])
        net_section.add_option("Uplink Status:", QLabel("CONNECTED"), self.colors['button_colors'][2])
        network_layout.addWidget(net_section)
        network_layout.addStretch()
        
        # Advanced
        advanced_page = QWidget()
        advanced_layout = QVBoxLayout(advanced_page)
        advanced_layout.setSpacing(20)
        
        adv_section = LCARSSection("ADVANCED SETTINGS", self.colors['button_colors'][3])
        
        debug_combo = DynamicSelector(self.current_era, button_index=7)
        debug_combo.addItems(["Disabled", "Enabled"])
        adv_section.add_option("Debug Mode:", debug_combo, self.colors['text'])
        
        advanced_layout.addWidget(adv_section)
        advanced_layout.addStretch()
        
        # Add all pages
        self.settings_stack.addWidget(system_page)
        self.settings_stack.addWidget(display_page)
        self.settings_stack.addWidget(era_page)
        self.settings_stack.addWidget(faction_page)
        self.settings_stack.addWidget(language_page)
        self.settings_stack.addWidget(keyboard_page)
        self.settings_stack.addWidget(network_page)
        self.settings_stack.addWidget(advanced_page)
    
    def switch_page(self, index):
        """Switch settings page"""
        self.settings_stack.setCurrentIndex(index)
    
    def create_footer(self):
        """Footer"""
        footer = QFrame()
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-radius: 0px;")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(30, 10, 30, 10)
        
        help_text = QLabel("F1: HELP | F10: SAVE & EXIT | ESC: EXIT WITHOUT SAVING")
        help_text.setStyleSheet("color: #000; font-size: 12px; font-weight: bold;")
        footer_layout.addWidget(help_text)
        
        footer_layout.addStretch()
        
        status = QLabel("◢ CONFIGURATION MODE")
        status.setStyleSheet("color: #000; font-size: 14px; font-weight: bold;")
        footer_layout.addWidget(status)
        
        return footer
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()
    
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.close()
        elif a0 and a0.key() == Qt.Key.Key_F10:
            # Save and exit
            self.close()


def main():
    app = QApplication(sys.argv)
    bios = LCARSBios()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
