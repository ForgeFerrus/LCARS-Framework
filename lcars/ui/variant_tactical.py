"""
Variant: TACTICAL GRID
Layout: Circular Elements + High Contrast Bricks + Tactical Indicators
"""
from __future__ import annotations
# Titanium Bridge Migration: from typing import Optional, Sequence
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QStackedLayout, QWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.lcars_palette import (LCARSColorGenerator, LCARSEra, 
                                       get_lcars_font_style, setup_lcars_font)

class TacticalLauncher(QDialog):
    def __init__(self, factions: Sequence[str], eras: Sequence[str], parent=None):
        super().__init__(parent)
        setup_lcars_font()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.factions = factions
        self.eras = eras
        self._selection = None
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        main = QVBoxLayout(self)
        main.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. HEADER BRICK
        header = QLabel("TACTICAL MISSION SELECTION")
        header.setFixedSize(800, 50)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"background-color: #CC6633; color: black; {get_lcars_font_style(28, 'normal')} border-radius: 5px;")
        main.addWidget(header)

        # 2. GRID
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(20)
        
        self._show_factions()
        main.addWidget(self.grid_widget)

    def _show_factions(self):
        self._clear_grid()
        for i, f in enumerate(self.factions):
            btn = QPushButton(f.upper())
            btn.setFixedSize(180, 180)
            btn.setStyleSheet(f"background-color: #336699; color: white; border: 4px solid #99CCFF; border-radius: 90px; {get_lcars_font_style(18, 'normal')}")
            btn.clicked.connect(lambda ch, faction=f: self._on_f(faction))
            self.grid.addWidget(btn, i // 2, i % 2)

    def _on_f(self, f):
        self.sel_f = f
        self._show_eras()

    def _show_eras(self):
        self._clear_grid()
        for i, e in enumerate(self.eras):
            btn = QPushButton(e.upper())
            btn.setFixedSize(180, 50)
            btn.setStyleSheet(f"background-color: #664422; color: white; border: 1px solid #CC9933; {get_lcars_font_style(16, 'normal')}")
            btn.clicked.connect(lambda ch, era=e: self._on_e(era))
            self.grid.addWidget(btn, i // 3, i % 3)

    def _on_e(self, e):
        self._selection = (self.sel_f, e, 0)
        self.accept()

    def _clear_grid(self):
        while self.grid.count():
            self.grid.takeAt(0).widget().deleteLater()

    def selection(self): return self._selection
