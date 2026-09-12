#!/usr/bin/env python3
"""
Minimal combined LCARS demo — uses project theme system and widgets.
Shows available factions/eras, palette samples, and small in-process demo windows.
"""
import sys
from pathlib import Path

# Ensure project root is on path so `lcars` package imports work when running from demo/
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt

# Project widgets and theme helpers
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar, StatBar
from lcars.themes.theme import FactionEra, get_faction_palette, get_available_factions, get_faction_eras
from lcars.themes.lcars_palette import get_theme, LCARSEra

class PaletteShowcase(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS Minimal Demo — Palette Showcase')
        self.setGeometry(120, 120, 1000, 700)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12,12,12,12)

        header = QLabel('LCARS Framework — Combined Minimal Demo')
        header.setStyleSheet('color: #4BBEBF; font-size: 26px; font-weight: bold;')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Top elbows
        row = QHBoxLayout()
        row.addWidget(LCARSElbow('top-left', color='#4BBEBF', auto_cycle=False))
        spacer = QFrame(); spacer.setStyleSheet('background: transparent'); row.addWidget(spacer, 1)
        row.addWidget(LCARSElbow('top-right', color='#FF9900', auto_cycle=False))
        layout.addLayout(row)

        # Faction buttons and counts
        grid = QGridLayout()
        factions = [f for f in FactionEra]
        # Show conservative subset of base factions
        shown = [FactionEra.STARFLEET_25TH, FactionEra.KLINGON_24TH, FactionEra.ROMULAN_24TH, FactionEra.CARDASSIAN_24TH]
        for i, f in enumerate(shown):
            name = f.name.split('_')[0]
            pal = get_faction_palette(f)
            btn_color = pal.get('button_colors', ['#4BBEBF'])[0]
            btn = LCARSButton(name, color=btn_color, shape='rect', auto_cycle=False)
            btn.setFixedSize(260, 110)
            grid.addWidget(btn, i // 2 * 2, i % 2)

            desc = QLabel(f"{name} — {len(pal.get('button_colors', []))} colors")
            desc.setStyleSheet(f"color: {btn_color}; font-size: 12px;")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(desc, i // 2 * 2 + 1, i % 2)

        layout.addLayout(grid)

        # Palette samples for a selected era (LCARS 25th)
        era_label = QLabel('LCARS 25TH ERA SAMPLE PALETTE')
        era_label.setStyleSheet('color: #FFCC33; font-size: 18px; font-weight: bold;')
        era_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(era_label)

        theme = get_theme(LCARSEra.LCARS_25TH)
        pal_row = QHBoxLayout()
        for c in theme['palette'][:8]:
            sw = QFrame(); sw.setFixedSize(90,60); sw.setStyleSheet(f'background: {c}; border-radius:4px;')
            pal_row.addWidget(sw)
        layout.addLayout(pal_row)

        # Scanning bar and a stat bar example
        layout.addWidget(ScanningBar(theme['accent']))
        sb = StatBar('SYSTEM LOAD', theme['accent'])
        sb.setValue(42)
        layout.addWidget(sb)

        # Footer buttons (launch small internal windows)
        footer = QHBoxLayout()
        demo_btn = LCARSButton('SYSTEM DEMO', color=theme['accent'], shape='rect')
        demo_btn.clicked.connect(self.open_system_demo)
        footer.addWidget(demo_btn)

        showcase_btn = LCARSButton('PALETTE SHOWCASE', color=theme['secondary'], shape='rect')
        showcase_btn.clicked.connect(self.open_palette_window)
        footer.addWidget(showcase_btn)

        close_btn = LCARSButton('CLOSE', color='#666666', shape='rect')
        close_btn.clicked.connect(self.close)
        footer.addWidget(close_btn)

        footer.addStretch()
        layout.addLayout(footer)

    def open_system_demo(self):
        w = QWidget()
        w.setWindowTitle('LCARS — System Demo')
        w.setGeometry(200,200,800,500)
        l = QVBoxLayout(w)
        l.addWidget(QLabel('Mini system demo — uses same widgets and theme'))
        w.show()

    def open_palette_window(self):
        w = QWidget()
        w.setWindowTitle('Palette Details')
        w.setGeometry(220,220,600,400)
        l = QVBoxLayout(w)
        # show all faction-era combinations count
        factions = list(FactionEra)
        l.addWidget(QLabel(f'Available FactionEra combinations: {len(factions)}'))
        # list a few names
        for f in factions[:8]:
            l.addWidget(QLabel(f.name))
        w.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    demo = PaletteShowcase()
    demo.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
