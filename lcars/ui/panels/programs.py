# LCARS PROGRAMS PANEL - SYSTEM APPLICATION LAUNCHER
# SYSTEM MODULE: UI-PRG-25

# Titanium Bridge Migration: import subprocess
import random
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt

from lcars.base.component import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style, get_theme, LCARSEra
from lcars.modules.sound import ActiveAudio

class ProgramsPanel(QWidget):
    def __init__(self, parent=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__(parent)
        self.era = era if era else LCARSEra.LCARS_25TH
        self.faction = faction
        self.theme = get_theme(self.era, faction)
        self.buttons = []
        self._build_ui()

    def update_theme(self, era, faction=None):
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        self.header_block.setStyleSheet(f"background: {self.theme['palette'][1]}; border-radius: 4px;")
        self.lbl_prg.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        self.launch_head.setStyleSheet(f"background: {self.theme['palette'][4]}; border-radius: 4px;")
        
        for idx, btn in enumerate(self.actions_btns):
            col = self.theme['palette'][idx % len(self.theme['palette'])]
            btn._base_color = col
            btn._current_color = col
            btn.setStyleSheet(f"background-color: {col}; color: black; border-radius: 20px;")
            
        self.btn_off._base_color = self.theme['palette'][0]
        self.btn_off._current_color = self.theme['palette'][0]
        self.btn_off.setStyleSheet(f"background-color: {self.theme['palette'][0]}; color: black; border-radius: 20px;")
        
        progs_colors = [self.theme['palette'][0], self.theme['palette'][5], self.theme['palette'][2], self.theme['palette'][0], self.theme['palette'][2], self.theme['palette'][7 % len(self.theme['palette'])], self.theme['palette'][3 % len(self.theme['palette'])], self.theme['palette'][4]]
        
        for idx, btn in enumerate(self.buttons):
            btn._base_color = progs_colors[idx % len(progs_colors)]
            btn._current_color = btn._base_color
            btn.setStyleSheet(f"background-color: {btn._base_color}; color: black; border-radius: 20px;")

    def _build_ui(self):
        from lcars.base.component import LCARSElbow, LCARSButton
        from lcars.base.interface import Segment as LCARSSegment
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- TITAN PROGRAMS HEADER ---
        header_frame = QFrame()
        header_frame.setMinimumHeight(120)
        header_lay = QHBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 5, 20, 0)
        header_lay.setSpacing(20)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        self.header_elbow = LCARSElbow("top-left", palette[1], era=self.era)
        self.header_elbow.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow)
        
        title_lay = QVBoxLayout()
        self.title_lbl = QLabel("PROGRAM LIBRARY // ACCESS AUTHORIZED")
        self.title_lbl.setStyleSheet(f"color: {palette[0]}; {get_lcars_font_style(32, 'bold')}; letter-spacing: 2px;")
        title_lay.addWidget(self.title_lbl)
        
        self.launch_info = QLabel("VERSION: 5.0.TITAN // SECTOR: 001")
        self.launch_info.setStyleSheet(f"color: {palette[2]}; {get_lcars_font_style(18, 'normal')};")
        title_lay.addWidget(self.launch_info)
        header_lay.addLayout(title_lay, 1)
        
        header_lay.addWidget(LCARSSegment(palette[3], direction="horizontal", era=self.era), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        body_hbox = QHBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(30)
        
        # LEFT: CATEGORIES
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        
        cats = ["SCIENTIFIC", "ENGINEERING", "COMMS", "OPERATIONS", "MEDICAL"]
        for i, cat in enumerate(cats):
            btn = LCARSButton(cat, palette[i % len(palette)], era=self.era, shape="rect")
            btn.setFixedSize(200, 45)
            left_col.addWidget(btn)
            
        left_col.addWidget(LCARSSegment(palette[1], direction="vertical", era=self.era), 1)
        
        self.left_elbow_bot = LCARSElbow("bottom-left", palette[0], era=self.era)
        self.left_elbow_bot.setMinimumHeight(120)
        left_col.addWidget(self.left_elbow_bot)
        
        body_hbox.addLayout(left_col)
        
        # CENTER: APP GRID
        center_col = QVBoxLayout()
        center_col.setSpacing(15)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(20)
        self.grid.setContentsMargins(10, 10, 10, 10)
        
        self._setup_launcher()
        
        scroll.setWidget(container)
        center_col.addWidget(scroll, 1)
        body_hbox.addLayout(center_col, 1)
        
        layout.addLayout(body_hbox, 1)

    def _setup_launcher(self):
        """Build the program grid"""
        # Note: UI Designer is moved to System Control Center -> Utilities Hub
        
        # Get current era and faction as strings to pass to subprocesses
        era_str = self.era.name if hasattr(self.era, 'name') else "LCARS_25TH"
        faction_str = str(self.faction) if self.faction else "FEDERATION"
        
        progs = [
            ("TOTAL COMMANDER", "STORAGE",   self.theme['palette'][0], True),
            ("TERMINAL",        "TERMINAL",  self.theme['palette'][5], True),
            ("BROWSER",         "BROWSER",   self.theme['palette'][2], True),
            ("WORKSPACE",       "WORKSPACE", self.theme['palette'][0], True),
            ("ENGLISH",         "ENGLISH",   self.theme['palette'][2], True),
            ("MEDIA ARCHIVE",   "MEDIA",     self.theme['palette'][7 % len(self.theme['palette'])], True),
            ("DIAGNOSTICS",     f"{sys.executable} programs/diagnostics.py", self.theme['palette'][3 % len(self.theme['palette'])], False),
            ("SYSTEM CONTROL",  "SETTINGS",  self.theme['palette'][4], True),
        ]
        
        for name, cmd, col, internal in progs:
            self.add_program(name, cmd, col, internal)
            
    def add_program(self, name, command, color, internal=False):
        btn = LCARSButton(name, color, era=self.era, faction=self.faction, shape="pill")
        btn.setMinimumHeight(100)
        btn.setMinimumWidth(220)
        
        self.buttons.append(btn)
        
        def make_run_prog(cmd=command, is_internal=internal):
            def run_prog():
                get_sound_manager().play("click")
                if is_internal:
                    if cmd == "STORAGE" and hasattr(self.parent(), 'mode_stack'):
                        self.parent().mode_stack.setCurrentIndex(1)
                        return
                    
                    # Unified Station Navigation
                    if hasattr(self.parent(), '_go'):
                        self.parent()._go(cmd)
                        return

                    if cmd == "TERMINAL":
                        if True:
                            from tools.terminal import launch as _launch_terminal
                            _launch_terminal(parent=self.parent(), era=self.era, faction=self.faction)
                        if False: # Removed except block
                            print(f"terminal.launch failed: {e}")
                        return
                    if cmd == "BROWSER":
                        if True:
                            from programs.browser import launch as _launch_browser
                            _launch_browser(parent=self.parent(), era=self.era, faction=self.faction)
                        if False: # Removed except block
                            print(f"browser.launch failed: {e}")
                        return
                    if cmd == "SETTINGS" and hasattr(self.parent(), 'show_settings'):
                        self.parent().show_settings()
                        return
                else:
                    subprocess.Popen(cmd, shell=True)
            return run_prog

        btn.clicked.connect(make_run_prog())
        count = self.grid.count()
        # 3 columns for better use of space
        self.grid.addWidget(btn, count // 3, count % 3)
