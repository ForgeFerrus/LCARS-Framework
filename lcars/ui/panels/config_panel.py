"""
Configuration Panel - Slide-out panel for selecting faction and era
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame,
    QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QPoint, QTimer
from PyQt6.QtGui import QFont

from lcars.themes.lcars_palette import LCARSEra, get_lcars_font_style
from lcars.themes.theme import FactionEra
from lcars.ui.base.widgets import LCARSButton
from lcars.modules.sound_manager import get_sound_manager


class ConfigurationPanel(QFrame):
    """Slide-out configuration panel for faction/era selection"""
    
    configuration_changed = pyqtSignal(str, str)  # faction, era
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_open = False
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border-left: 2px solid #4BBEBF;
                border-top: 2px solid #4BBEBF;
            }
            QLabel {
                color: #FF9900;
                font-weight: normal;
            }
        """)
        
        self.selected_faction = "Federation"
        self.selected_era = "25th"
        
        self.factions = [
            ("Federation", FactionEra.STARFLEET_25TH),
            ("Klingon", FactionEra.KLINGON_25TH),
            ("Romulan", FactionEra.ROMULAN_25TH),
            ("Cardassian", FactionEra.CARDASSIAN_25TH),
        ]
        
        self.eras = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]
        
        self.setup_ui()
        self.move_out()  # Start hidden
        
    def setup_ui(self):
        """Build the configuration UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("▌ CONFIGURATION")
        title.setStyleSheet(f"color: #4BBEBF; {get_lcars_font_style(18, 'normal')}")
        layout.addWidget(title)
        
        # Faction selection
        faction_label = QLabel("SELECT ALIGNMENT:")
        faction_label.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(14, 'normal')}")
        layout.addWidget(faction_label)
        
        faction_grid = QGridLayout()
        faction_grid.setSpacing(10)
        
        self.faction_buttons = {}
        for i, (faction_name, _) in enumerate(self.factions):
            btn = LCARSButton(faction_name)
            btn.clicked.connect(lambda checked, f=faction_name: self.select_faction(f))
            faction_grid.addWidget(btn, i // 2, i % 2)
            self.faction_buttons[faction_name] = btn
        
        layout.addLayout(faction_grid)
        
        # Era selection
        era_label = QLabel("SELECT ERA:")
        era_label.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(14, 'normal')}")
        layout.addWidget(era_label)
        
        era_grid = QGridLayout()
        era_grid.setSpacing(10)
        
        self.era_buttons = {}
        for i, era in enumerate(self.eras):
            btn = LCARSButton(f"{era} Century")
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
            era_grid.addWidget(btn, i // 3, i % 3)
            self.era_buttons[era] = btn
        
        layout.addLayout(era_grid)
        
        # Apply button
        apply_btn = LCARSButton("APPLY")
        apply_btn.clicked.connect(self.on_apply)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
    def select_faction(self, faction: str):
        """Select a faction"""
        self.selected_faction = faction
        for name, btn in self.faction_buttons.items():
            if name == faction:
                btn.setStyleSheet(f"{btn.styleSheet()}; border: 2px solid #FF9900;")
            else:
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid #FF9900;", ""))
        get_sound_manager().play("click")
        
    def select_era(self, era: str):
        """Select an era"""
        self.selected_era = era
        for e, btn in self.era_buttons.items():
            if e == era:
                btn.setStyleSheet(f"{btn.styleSheet()}; border: 2px solid #FF9900;")
            else:
                btn.setStyleSheet(btn.styleSheet().replace("border: 2px solid #FF9900;", ""))
        get_sound_manager().play("click")
        
    def on_apply(self):
        """Apply selected configuration"""
        get_sound_manager().play("acknowledge")
        self.configuration_changed.emit(self.selected_faction, self.selected_era)
        self.toggle()
        
    def toggle(self):
        """Toggle panel visibility"""
        if self.is_open:
            self.move_out()
        else:
            self.move_in()
    
    def move_in(self):
        """Slide panel in from right"""
        if self.is_open:
            return
        p = self.parentWidget()
        if not p:
            return
        
        self.setFixedWidth(350)
        self.setFixedHeight(p.height() - 150)
        
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(300)
        start_x = p.width()
        end_x = p.width() - 350
        self.anim.setStartValue(QPoint(start_x, 50))
        self.anim.setEndValue(QPoint(end_x, 50))
        self.anim.start()
        self.is_open = True
        self.raise_()
        get_sound_manager().play("acknowledge")
        
    def move_out(self):
        """Slide panel out to right"""
        if not self.is_open:
            return
        p = self.parentWidget()
        if not p:
            p_width = 1400
        else:
            p_width = p.width()
        
        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(300)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(QPoint(p_width, 50))
        self.anim.start()
        self.is_open = False
        get_sound_manager().play("click")
