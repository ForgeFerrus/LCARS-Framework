"""
LCARS Integrated Launcher - Екран вибору фракції та ери.
Дозволяє користувачу налаштувати візуальне середовище системи.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style, LCARSColorGenerator, 
    FactionEra, get_random_button_color
)
from lcars.themes.theme_simple import get_simple_palette
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour, ScanningBar
from lcars.modules.sound_manager import get_sound_manager

class SelectorView(QWidget):
    """Configuration selector for Faction and Era with full architectural framing."""
    selected = pyqtSignal(str, str) # faction, era
    preview_changed = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_faction = "FEDERATION"
        self.selected_era = "25th"
        self.setup_ui()
        # Початкова синхронізація кольорів згідно з алгоритмом рандомізації
        self._refresh_interface()

    def setup_ui(self):
        """Побудова сітки вибору з архітектурним обрамленням."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- TOP HEADER STRUCTURE ---
        header_lay = QHBoxLayout()
        header_lay.setSpacing(5)
        
        self.elbow_tl = LCARSElbow("top-left", color="#3366CC")
        self.elbow_tl.setFixedSize(140, 60)
        header_lay.addWidget(self.elbow_tl)
        
        self.top_title_bar = LCARSContour(direction="horizontal")
        self.top_title_bar.setFixedHeight(30)
        t_lay = QHBoxLayout(self.top_title_bar)
        t_lay.setContentsMargins(20, 0, 20, 0)
        
        self.title_lbl = QLabel("◢ CONFIGURATION SELECTION")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}; border: none;")
        t_lay.addWidget(self.title_lbl)
        t_lay.addStretch()
        
        header_lay.addWidget(self.top_title_bar, 1)
        self.main_layout.addLayout(header_lay)

        # --- BODY CORE ---
        body = QHBoxLayout()
        body.setSpacing(5)
        
        # Left Scanning Bar
        self.side_scan = ScanningBar("#3366CC", orientation="vertical")
        self.side_scan.setFixedWidth(50)
        body.addWidget(self.side_scan)

        # Central Area
        content_vbox = QVBoxLayout()
        content_vbox.setContentsMargins(20, 10, 20, 10)
        content_vbox.setSpacing(20)

        grid = QHBoxLayout()
        
        # --- Фракції (Alignments) ---
        faction_vbox = QVBoxLayout()
        f_title = QLabel("SELECT ALIGNMENT")
        f_title.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(14, 'normal')}")
        faction_vbox.addWidget(f_title)
        
        self.f_btn_group = []
        factions = [
            ("FEDERATION", "#9999FF"),
            ("KLINGON", "#CC3333"),
            ("ROMULAN", "#339966"),
            ("CARDASSIAN", "#CC9966")
        ]
        for name, color in factions:
            btn = LCARSButton(name, color, shape="right", auto_cycle=True)
            btn.setFixedSize(240, 50)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            if name == "FEDERATION": btn.setChecked(True)
            btn.clicked.connect(lambda ch, n=name: self._set_faction(n))
            faction_vbox.addWidget(btn)
            self.f_btn_group.append(btn)
        
        faction_vbox.addStretch()
        grid.addLayout(faction_vbox)
        
        grid.addSpacing(30)

        # --- Ери (Temporal Periods) ---
        era_vbox = QVBoxLayout()
        e_title = QLabel("SELECT TEMPORAL PERIOD")
        e_title.setStyleSheet(f"color: #3399CC; {get_lcars_font_style(14, 'normal')}")
        era_vbox.addWidget(e_title)
        
        eras_grid = QGridLayout()
        eras = [
            ("22nd Century (ENT)", "22nd"), ("23rd Century (TOS)", "23rd"),
            ("23rd Alt (TMP)", "23st"), ("24th Century (TNG)", "24th"),
            ("24th ALT (FC)", "24st"), ("25th Century (PIC)", "25th"),
            ("29th Century (VOY)", "29th")
        ]
        for i, (label, val) in enumerate(eras):
            btn = LCARSButton(label, era=LCARSEra.LCARS_24TH, shape="rect", auto_cycle=True)
            btn.setFixedSize(230, 45)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            if val == "25th": btn.setChecked(True)
            btn.clicked.connect(lambda ch, v=val: self._set_era(v))
            eras_grid.addWidget(btn, i // 2, i % 2)
        
        era_vbox.addLayout(eras_grid)
        era_vbox.addStretch()
        grid.addLayout(era_vbox)
        
        content_vbox.addLayout(grid, 1)

        # --- Launch Control ---
        launch_hbox = QHBoxLayout()
        launch_hbox.addStretch()
        
        v_confirm = QVBoxLayout()
        self.preview_lbl = QLabel("CONFIG: FEDERATION // 25th")
        self.preview_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}")
        v_confirm.addWidget(self.preview_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        self.btn_launch = LCARSButton("INITIALIZE INTERFACE", "#4BBEBF", shape="pill")
        self.btn_launch.setFixedSize(400, 80)
        self.btn_launch.clicked.connect(self._launch)
        v_confirm.addWidget(self.btn_launch)
        
        launch_hbox.addLayout(v_confirm)
        content_vbox.addLayout(launch_hbox)

        body.addLayout(content_vbox, 1)

        # Right decorative bar
        self.right_bar = LCARSContour(direction="vertical")
        self.right_bar.setFixedWidth(20)
        body.addWidget(self.right_bar)
        
        self.main_layout.addLayout(body, 1)

        # --- FOOTER ---
        footer_lay = QHBoxLayout()
        footer_lay.setSpacing(5)
        
        self.bottom_cap = LCARSContour(direction="horizontal")
        self.bottom_cap.setFixedHeight(30)
        footer_lay.addWidget(self.bottom_cap, 1)
        
        self.elbow_br = LCARSElbow("bottom-right", color="#3366CC")
        self.elbow_br.setFixedSize(140, 60)
        footer_lay.addWidget(self.elbow_br)
        
        self.main_layout.addLayout(footer_lay)

    def _set_faction(self, name):
        self.selected_faction = name
        self._refresh_interface()
        get_sound_manager().play("click")

    def _set_era(self, era):
        self.selected_era = era
        self._refresh_interface()
        get_sound_manager().play("click")

    def _get_current_enums(self):
        """Helper to resolve current era and faction enums."""
        from lcars.themes.lcars_palette import LCARSEra, FactionEra
        
        era_map = {
            "22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD,
            "23st": LCARSEra.PCARS_23ST, "24th": LCARSEra.LCARS_24TH,
            "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH,
            "29th": LCARSEra.TCARS_29TH
        }
        f_map = {
            "FEDERATION": None,
            "KLINGON": FactionEra.KLINGON,
            "ROMULAN": FactionEra.ROMULAN,
            "CARDASSIAN": FactionEra.CARDASSIAN
        }
        
        target_era = era_map.get(self.selected_era, LCARSEra.LCARS_25TH)
        target_faction = f_map.get(self.selected_faction.upper())
        return target_era, target_faction

    def _refresh_interface(self):
        """Повне оновлення інтерфейсу згідно з обраною палітрою (Living UI)."""
        target_era, target_faction = self._get_current_enums()
        
        from lcars.themes.lcars_palette import get_theme
        theme = get_theme(target_era, target_faction)
        primary = theme.get('primary', '#4BBEBF')
        secondary = theme.get('secondary', '#3366CC')
        
        self.preview_lbl.setText(f"CONFIG: {self.selected_faction} // {self.selected_era}")
        self.preview_lbl.setStyleSheet(f"color: {primary}; {get_lcars_font_style(20, 'normal')}")
        
        # Generator for structured randomization (The algorithm the user refers to)
        gen = LCARSColorGenerator(target_era, target_faction)
        
        # 1. Update architectural framing
        self.elbow_tl.update_color(secondary)
        self.top_title_bar.update_color(secondary)
        self.side_scan.update_color(primary)
        self.bottom_cap.update_color(secondary)
        self.elbow_br.update_color(primary)
        self.right_bar.update_color(primary)
        
        # 2. Update ALL buttons within the view
        for btn in self.findChildren(LCARSButton):
            btn.era = target_era
            btn.faction = target_faction
            
            # Using the generator to pick colors from the NEW palette
            # This ensures they look like "one palette" as requested.
            new_color = gen.get_next_color()
            btn.current_color = new_color
            btn.apply_style()
            
        # 3. Special case for launch button
        self.btn_launch.update_color(primary)
        
        # Notify launcher
        self.preview_changed.emit(self.selected_faction, self.selected_era)

    def _launch(self):
        print(f"[SELECTOR] Initializing {self.selected_faction} ({self.selected_era})...")
        get_sound_manager().play("acknowledge")
        self.selected.emit(self.selected_faction, self.selected_era)
