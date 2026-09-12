"""
LCARS Integrated Launcher - Екран вибору фракції та ери.
Дозволяє користувачу налаштувати візуальне середовище системи.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from lcars.themes.palette import LCARSEra, get_lcars_font_style, LCARSColorGenerator
from lcars.themes.theme import FactionEra
from lcars.themes.theme_simple import get_simple_palette
from lcars.ui.base.widgets import LCARSButton
from lcars.modules.sound_manager import get_sound_manager

class IntegratedLauncherView(QWidget):
    """Інтегрований інтерфейс вибору конфігурації LCARS."""
    selected = pyqtSignal(str, str) # фракція, ера

    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        self.color_gen = LCARSColorGenerator(era)
        
        self.selected_faction = "FEDERATION"
        self.selected_era = "25th"
        
        self.setup_ui()

    def setup_ui(self):
        """Побудова сітки вибору з динамічними кольорами та стилями."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        # Заголовок
        title = QLabel("CONFIGURATION SELECTION")
        title.setStyleSheet(f"color: white; {get_lcars_font_style(32, 'normal')}")
        self.layout.addWidget(title)
        
        main_content = QHBoxLayout()
        
        # --- ЛІВА ЧАСТИНА: Фракції ---
        faction_box = QVBoxLayout()
        faction_lbl = QLabel("SELECT ALIGNMENT")
        faction_lbl.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(20, 'normal')}")
        faction_box.addWidget(faction_lbl)
        
        factions = [
            ("FEDERATION", FactionEra.STARFLEET_25TH),
            ("KLINGON", FactionEra.KLINGON_25TH),
            ("ROMULAN", FactionEra.ROMULAN_25TH),
            ("CARDASSIAN", FactionEra.CARDASSIAN_25TH)
        ]
        
        for name, f_era in factions:
            palette = get_simple_palette(f_era)
            btn = LCARSButton(name, palette['primary'], shape="pill")
            btn.setMinimumSize(300, 60)
            btn.clicked.connect(lambda checked, n=name: self._set_faction(n))
            faction_box.addWidget(btn)
        
        faction_box.addStretch()
        main_content.addLayout(faction_box)
        
        # --- ЦЕНТРАЛЬНА ЧАСТИНА: Ери ---
        era_box = QVBoxLayout()
        era_lbl = QLabel("SELECT TEMPORAL PERIOD")
        era_lbl.setStyleSheet(f"color: #3399CC; {get_lcars_font_style(20, 'normal')}")
        era_box.addWidget(era_lbl)
        
        eras = ["22nd", "23rd", "24th", "25th", "29th"]
        for e in eras:
            btn = LCARSButton(e, self.color_gen.get_next_color(), shape="rect")
            btn.setMinimumSize(200, 50)
            btn.clicked.connect(lambda checked, val=e: self._set_era(val))
            era_box.addWidget(btn)
            
        era_box.addStretch()
        main_content.addLayout(era_box)
        
        # --- ПРАВА ЧАСТИНА: Підтвердження ---
        confirm_box = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: FEDERATION // 25th")
        self.preview_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}")
        confirm_box.addStretch()
        confirm_box.addWidget(self.preview_lbl)
        
        btn_launch = LCARSButton("INITIALIZE INTERFACE", "#4BBEBF", shape="right")
        btn_launch.setMinimumSize(350, 80)
        btn_launch.clicked.connect(self._launch)
        confirm_box.addWidget(btn_launch)
        
        main_content.addLayout(confirm_box)
        
        self.layout.addLayout(main_content)

    def _set_faction(self, name):
        self.selected_faction = name
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        get_sound_manager().play("click")

    def _set_era(self, era):
        self.selected_era = era
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        get_sound_manager().play("click")

    def _launch(self):
        get_sound_manager().play("acknowledge")
        self.selected.emit(self.selected_faction, self.selected_era)
