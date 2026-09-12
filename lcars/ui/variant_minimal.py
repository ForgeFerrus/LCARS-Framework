"""
Variant: MINIMALIST TERMINAL
Layout: Vertical Sidebar + Clean Typeface + Animated Data Stream
"""
from __future__ import annotations
# Titanium Bridge Migration: from typing import Optional, Sequence
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QStackedLayout, QWidget, QFrame)
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.lcars_palette import (LCARSColorGenerator, LCARSEra, 
                                       get_lcars_font_style, setup_lcars_font, FactionEra)

class MinimalistLauncher(QDialog):
    def __init__(self, factions: Sequence[str], eras: Sequence[str], parent=None):
        super().__init__(parent)
        setup_lcars_font()
        self.era_enum = LCARSEra.LCARS_25TH
        self.color_gen = LCARSColorGenerator(self.era_enum)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black;")
        self._selection = None
        self.selected_faction = factions[0]
        
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # 1. SIDEBAR ELBOW
        sidebar = QVBoxLayout()
        self.top_elbow = QFrame()
        self.top_elbow.setFixedSize(140, 200)
        self.top_elbow.setStyleSheet("background-color: #99CCFF; border-top-left-radius: 60px; border-bottom-left-radius: 10px;")
        sidebar.addWidget(self.top_elbow)
        
        self.bottom_bar = QFrame()
        self.bottom_bar.setFixedWidth(140)
        self.bottom_bar.setStyleSheet("background-color: #336699; border-bottom-left-radius: 60px; border-top-left-radius: 10px;")
        sidebar.addWidget(self.bottom_bar, 1)
        layout.addLayout(sidebar)

        # 2. SELECTION AREA
        content = QVBoxLayout()
        content.setContentsMargins(30, 0, 0, 0)
        self.title = QLabel("ACCESS PROTOCOL: SELECT ALIGNMENT")
        self.title.setStyleSheet(f"color: #99CCFF; {get_lcars_font_style(38, 'normal')}")
        content.addWidget(self.title)

        self.stack = QStackedLayout()
        
        # Factions
        p1 = QWidget()
        p1_l = QVBoxLayout(p1)
        p1_l.setSpacing(10)
        for faction in factions:
            btn = QPushButton(faction.upper())
            btn.setFixedSize(400, 50)
            btn.setStyleSheet(self._style("#778899"))
            btn.clicked.connect(lambda ch, f=faction: self._on_faction(f))
            p1_l.addWidget(btn)
        p1_l.addStretch()
        self.stack.addWidget(p1)

        # Eras
        p2 = QWidget()
        p2_l = QVBoxLayout(p2)
        p2_l.setSpacing(10)
        for era in eras:
            btn = QPushButton(era.upper())
            btn.setFixedSize(400, 45)
            btn.setStyleSheet(self._style("#99AACC"))
            btn.clicked.connect(lambda ch, e=era: self._on_era(e))
            p2_l.addWidget(btn)
        self.stack.addWidget(p2)

        content.addLayout(self.stack)
        layout.addLayout(content, 1)

    def _style(self, color):
        return f"QPushButton {{ background-color: {color}; color: black; border-radius: 2px; {get_lcars_font_style(20, 'normal')} text-align: left; padding-left: 20px; border: none; }} QPushButton:hover {{ background-color: white; }}"

    def _on_faction(self, f):
        self.selected_faction = f
        self.title.setText(f"ALIGNMENT SET: {f.upper()}")
        QTimer.singleShot(300, lambda: self.stack.setCurrentIndex(1))

    def _on_era(self, e):
        self._selection = (self.selected_faction, e, 0)
        self.accept()

    def selection(self): return self._selection
