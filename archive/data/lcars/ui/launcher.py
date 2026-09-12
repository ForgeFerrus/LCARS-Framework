"""
LCARS UI Launcher - Faction and Era Selection Dialog
"""
from __future__ import annotations

import datetime
from typing import Optional, Sequence
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedLayout, QWidget, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from lcars.themes.palette import ( LCARSColorGenerator,
    LCARSEra, get_lcars_font_style, setup_lcars_font,
    get_random_button_color, get_alert_color, get_era_palette, FactionEra
)
# Default factions and eras
DEFAULT_FACTIONS = ["Federation", "Klingon", "Romulan", "Cardassian"]
DEFAULT_ERAS = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

class FactionDialog(QDialog):

    def __init__(self, factions: Sequence[str], eras: Sequence[str], parent=None):
        super().__init__(parent)
        setup_lcars_font()
        self.era_enum = LCARSEra.LCARS_25TH
        self.color_gen = LCARSColorGenerator(self.era_enum)
        self.factions = factions
        self.eras = eras
        self.current_faction = None
        
        self.selected_faction = factions[0]
        self.selected_era = eras[0]
        self.alert_mode = False
        self._bar_index = 0
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: none;")
        self._selection: Optional[tuple] = None

        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setFixedSize(1100, 780)
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(4) # Tighter connections

        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.elbow = QFrame()
        self.elbow.setFixedSize(180, 70)
        self.elbow.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(0)}; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
        header.addWidget(self.elbow)
        
        self.title_fr = QFrame()
        self.title_fr.setFixedHeight(70)
        self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(1)}; border-radius: 4px; color: black;")
        tf_l = QHBoxLayout(self.title_fr)
        tl = QLabel("SYSTEM ACCESS - TEMPORAL & POLITICAL ALIGNMENT PROTOCOL")
        tl.setStyleSheet(get_lcars_font_style(28, 'normal')) 
        tf_l.addWidget(tl)
        header.addWidget(self.title_fr, 1)
        self.cc_end = QFrame()
        self.cc_end.setFixedSize(40, 70)
        self.cc_end.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(2)}; border-top-right-radius: 35px; border-bottom-right-radius: 4px;")
        header.addWidget(self.cc_end)
        
        c_layout.addLayout(header)

        # --- CONTENT ---
        content = QHBoxLayout()
        content.setSpacing(4)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(4)
        
        self.sb_main = QFrame()
        self.sb_main.setFixedWidth(180)
        self.sb_main.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(3)}; border-bottom-left-radius: 80px; border-top-left-radius: 4px;")
        sidebar.addWidget(self.sb_main, 1) 
        
        # Sidebar "Running Bars" (Professional Version)
        self._sidebar_bars = []
        for i in range(8):
            f = QPushButton(f"NODE 0{i+1}")
            f.setFixedSize(180, 42)
            initial_color = self.color_gen.get_color_at_index(10 + i)
            # Use specific colors for some nodes to look authentic
            if i == 0: initial_color = "#99CCFF" # Cyan node
            if i == 7: initial_color = "#CC99FF" # Violet node
            
            f.setStyleSheet(f"background-color: {initial_color}; border-radius: 4px; color: black; {get_lcars_font_style(16, 'normal')}; text-align: right; padding-right: 15px; border: none;")
            
            # Make the first node toggle Alert Level!
            if i == 0:
                from lcars.system.alert import alert_system
                f.clicked.connect(alert_system.next_level)
                f.setText("STATUS")
                
            sidebar.addWidget(f)
            self._sidebar_bars.append(f)
        
        sidebar.addStretch(1) 
        
        # Bottom sidebar connector (elbow-ish)
        self.sb_bottom = QFrame()
        self.sb_bottom.setFixedSize(180, 60)
        self.sb_bottom.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(4)}; border-bottom-left-radius: 40px; border-top-left-radius: 6px;")
        sidebar.addWidget(self.sb_bottom)
        
        content.addLayout(sidebar)

        # Stack
        self.stack = QStackedLayout()
        
        # P1: Factions
        p1 = QWidget()
        p1_l = QVBoxLayout(p1)
        p1_l.setContentsMargins(30, 0, 30, 0)
        p1_l.setSpacing(20)
        
        p1_l.addStretch(1) # Top stretch for vertical centering

        import datetime
        stardate = datetime.datetime.now().strftime("%y%m.%d")
        
        # Section Header with Background
        self.p1_header = QFrame()
        self.p1_header.setFixedHeight(60)
        self.p1_header.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(2)}; border-radius: 4px;")
        p1_h_layout = QHBoxLayout(self.p1_header)
        
        self.info_lbl = QLabel(f"SD {stardate} - SELECT OPERATIONAL ALIGNMENT")
        self.info_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(32, 'normal')}") 
        self.info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        p1_h_layout.addWidget(self.info_lbl)
        p1_l.addWidget(self.p1_header)
        
        # Grid block for Faction Bricks
        f_grid = QGridLayout()
        f_grid.setSpacing(40) # Maximum Breathing Room
        
        from lcars.themes.theme import FactionEra
        f_mapping = {
            "Federation": None, 
            "Klingon": FactionEra.KLINGON, 
            "Romulan": FactionEra.ROMULAN, 
            "Cardassian": FactionEra.CARDASSIAN
        }
        
        self.faction_btns = {}
        for i, faction in enumerate(self.factions):
            btn = QPushButton(faction.upper())
            btn.setFixedSize(280, 180) # Larger, better proportions
            
            # Use faction-specific random colors!
            f_enum = f_mapping.get(faction)
            btn_color = get_random_button_color(self.era_enum, f_enum)
            btn.setStyleSheet(self._get_btn_style(btn_color, size=26))
            
            btn.clicked.connect(lambda ch, f=faction: self._select_faction(f))
            f_grid.addWidget(btn, i // 2, i % 2) 
            self.faction_btns[faction] = btn
        
        # Horizontal centering for the grid
        grid_container = QHBoxLayout()
        grid_container.addStretch(1)
        grid_container.addLayout(f_grid)
        grid_container.addStretch(1)
        p1_l.addLayout(grid_container)
        
        p1_l.addStretch(1) # Bottom stretch for vertical centering
        self.stack.addWidget(p1)
        
        # P2: Eras
        p2 = QWidget()
        p2_l = QVBoxLayout(p2)
        p2_l.setContentsMargins(30, 0, 30, 0)
        p2_l.setSpacing(15)

        p2_l.addStretch(1)

        self.p2_header = QFrame()
        self.p2_header.setFixedHeight(60)
        self.p2_header.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(2)}; border-radius: 4px;")
        p2_h_layout = QHBoxLayout(self.p2_header)

        lbl2 = QLabel("TEMPORAL GRID - SELECT OPERATING ERA")
        lbl2.setStyleSheet(f"color: black; {get_lcars_font_style(32, 'normal')}")
        lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        p2_h_layout.addWidget(lbl2)
        p2_l.addWidget(self.p2_header)
        
        e_grid = QGridLayout()
        e_grid.setSpacing(40) # Maximum Breathing Room
        self.era_btns = {}
        for i, era in enumerate(eras):
            btn = QPushButton(era.upper())
            btn.setFixedSize(220, 110)
            btn.setStyleSheet(self._get_btn_style(self.color_gen.get_color_at_index(20+i), size=22))
            btn.clicked.connect(lambda ch, e=era: self._select_era(e))
            e_grid.addWidget(btn, i // 3, i % 3)
            self.era_btns[era] = btn
        
        e_container = QHBoxLayout()
        e_container.addStretch(1)
        e_container.addLayout(e_grid)
        e_container.addStretch(1)
        p2_l.addLayout(e_container)
        
        p2_l.addStretch(1)
        self.stack.addWidget(p2)
        
        content.addLayout(self.stack, 1)
        c_layout.addLayout(content, 1)

        # --- NAVIGATION BAR (FIXED AT BOTTOM) ---
        nav = QHBoxLayout()
        nav.setContentsMargins(188, 5, 8, 5) 
        nav.setSpacing(15)

        self.back_btn = QPushButton("RETURN")
        self.back_btn.setFixedSize(220, 56) 
        self.back_btn.setStyleSheet(self._get_btn_style("#FF9900", size=20))
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.back_btn.setVisible(False)
        self.stack.currentChanged.connect(lambda idx: self.back_btn.setVisible(idx > 0))
        nav.addWidget(self.back_btn)
        
        c_layout.addLayout(nav)
 
        # --- FOOTER ---
        self.footer_fr = QFrame()
        self.footer_fr.setFixedHeight(48)
        self.footer_fr.setStyleSheet(f"""
            background-color: {self.color_gen.get_color_at_index(4)}; 
            border-bottom-right-radius: 40px; 
            border-top-right-radius: 4px;
            margin-left: 188px;
        """)
        c_layout.addWidget(self.footer_fr)

        # Center on screen
        main_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(container)
        h_center.addStretch()
        main_layout.addLayout(h_center)
        main_layout.addStretch()

        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self._cycle_atmosphere_colors)
        self.color_timer.start(5000)

        # "������ �������" � ������� (�������� - 600��)
        self.running_timer = QTimer(self)
        self.running_timer.timeout.connect(self._cycle_running_bars)
        self.running_timer.start(400)

        self.showFullScreen()

    def _get_btn_style(self, color, size=24):
        """Clean, professional LCARS Brick Style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border: none;
                border-radius: 4px;
                {get_lcars_font_style(size, 'normal')}
                text-align: right;
                padding-right: 15px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                color: black;
            }}
            QPushButton:pressed {{ 
                background-color: #666666; 
            }}
        """
    def _cycle_running_bars(self):
        """Logic for the 8 NODE segments + pulse endcaps (Professional Look)"""
        if not hasattr(self, '_sidebar_bars') or not self._sidebar_bars:
            return
            
        self._bar_index += 1
        
        # Shift sidebar colors
        for i in range(len(self._sidebar_bars)-1, 0, -1):
            self._sidebar_bars[i].setStyleSheet(self._sidebar_bars[i-1].styleSheet())
            
        new_color = self.color_gen.get_color_at_index(10 + (self._bar_index % 10))
        btn_style = f"background-color: {new_color}; border-radius: 4px; color: black; {get_lcars_font_style(16, 'normal')}; text-align: right; padding-right: 15px; border: none;"
        self._sidebar_bars[0].setStyleSheet(btn_style)

        # Subtle pulse for the end-cap (70px height radii)
        if self._bar_index % 4 == 0:
            pulse_color = self.color_gen.get_color_at_index(5 + (self._bar_index % 5))
            self.cc_end.setStyleSheet(f"background-color: {pulse_color}; border-top-right-radius: 35px; border-bottom-right-radius: 4px;")
            self.sb_bottom.setStyleSheet(f"background-color: {pulse_color}; border-bottom-left-radius: 40px; border-top-left-radius: 4px;")

    def _cycle_atmosphere_colors(self):
        """Randomly cycles colors for that authentic LCARS panel flicker."""
        from lcars.system.alert import alert_system
        level_val = int(alert_system.level)
        
        # Use randomness for main panels as well
        self.elbow.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-top-left-radius: 50px; border-bottom-left-radius: 4px;")
        self.title_fr.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-radius: 4px; color: black;")
        self.sb_main.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-bottom-left-radius: 80px; border-top-left-radius: 4px;")
        self.sb_bottom.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-bottom-left-radius: 40px; border-top-left-radius: 6px;")
        
        # Update section headers
        if hasattr(self, 'p1_header'):
            self.p1_header.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-radius: 4px; color: black;")
        if hasattr(self, 'p2_header'):
            self.p2_header.setStyleSheet(f"background-color: {get_random_button_color(self.era_enum, self.current_faction, alert_level=level_val)}; border-radius: 4px; color: black;")
        
      
    def _select_faction(self, faction):
        self.selected_faction = faction
        f_map = {"Klingon": FactionEra.KLINGON, "Romulan": FactionEra.ROMULAN, "Cardassian": FactionEra.CARDASSIAN, "Federation": None}
        self.current_faction = f_map.get(faction)
        self.color_gen = LCARSColorGenerator(self.era_enum, self.current_faction)
        
        # Immediate UI Update 
        self._cycle_atmosphere_colors()

        # Dim others
        for btn in self.faction_btns.values():
            if btn.text() == faction.upper():
                btn.setStyleSheet(self._get_btn_style("#00CC00", size=26)) 
            else:
                btn.setStyleSheet(self._get_btn_style("#222222", size=26))
        
        QTimer.singleShot(300, lambda: self.stack.setCurrentIndex(1))

    def _select_era(self, era):
        self.selected_era = era
        era_map = {"22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST, "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}
        self.era_enum = era_map.get(era, LCARSEra.LCARS_24TH)

        for btn in self.era_btns.values():
            if btn.text() == era.upper():
                btn.setStyleSheet(self._get_btn_style("#00CC00", size=22))
            else:
                btn.setStyleSheet(self._get_btn_style("#222222", size=22))
        
        # Auto-accept after a short delay for smoothness
        QTimer.singleShot(300, self._on_ok)

    def _on_ok(self):
        from lcars.system.alert import alert_system
        self._selection = (self.selected_faction, self.selected_era, int(alert_system.level))
        self.accept()

    def selection(self) -> Optional[tuple]:
        return self._selection
