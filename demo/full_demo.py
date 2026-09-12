#!/usr/bin/env python3
"""
Full LCARS Demo — uses project's theme system and widgets to present
an integrated launcher + desktop in the LCARS style.
"""
import sys
from pathlib import Path

# ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QPushButton, QMainWindow
)
from PyQt6.QtCore import Qt, QTimer

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar, StatBar
from lcars.themes.theme import FactionEra, get_faction_palette, get_available_factions
from lcars.themes.lcars_palette import get_theme, LCARSEra

class FullLauncher(QWidget):
    """Launcher that demonstrates theme integration and opens a demo desktop."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS Full Demo - Launcher')
        self.setGeometry(80, 80, 1200, 900)
        self.current_faction_era = None
        self.current_era = LCARSEra.LCARS_25TH
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)

        header = QLabel('LCARS FRAMEWORK - FULL DEMO')
        header.setStyleSheet('color: #4BBEBF; font-size: 28px; font-weight: bold;')
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        top_el = QHBoxLayout()
        top_el.addWidget(LCARSElbow('top-left', color='#4BBEBF'))
        top_el.addStretch(1)
        top_el.addWidget(LCARSElbow('top-right', color='#FF9900'))
        layout.addLayout(top_el)

        # Faction selection grid
        grid = QGridLayout()
        grid.setSpacing(18)

        # Choose a small curated list (but uses real palettes)
        options = [FactionEra.STARFLEET_25TH, FactionEra.KLINGON_24TH, FactionEra.ROMULAN_24TH, FactionEra.CARDASSIAN_24TH]
        for i, fe in enumerate(options):
            pal = get_faction_palette(fe)
            main = pal.get('button_colors', ['#4BBEBF'])[0]
            name = fe.name.split('_')[0]
            btn = LCARSButton(name, color=main, shape='rect')
            btn.setFixedSize(320, 120)
            btn.clicked.connect(lambda _, f=fe: self.select_faction(f))
            grid.addWidget(btn, i//2, i%2)

            desc = QLabel(f"{name} — {len(pal.get('button_colors', []))} colors")
            desc.setStyleSheet(f"color: {main}; font-size:12px;")
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(desc, i//2+2, i%2)

        layout.addLayout(grid)

        # Integration status
        status_frame = QFrame(); status_frame.setStyleSheet('background:#111; border:1px solid #333; border-radius:6px;')
        sf_l = QVBoxLayout(status_frame)
        title = QLabel('INTEGRATION STATUS'); title.setStyleSheet('color:#FFCC33; font-weight:bold;')
        sf_l.addWidget(title)
        self.status_label = QLabel('Theme: LOADED — select a faction to preview')
        self.status_label.setStyleSheet('color:#CCCCCC;')
        sf_l.addWidget(self.status_label)
        layout.addWidget(status_frame)

        # Footer controls
        footer = QHBoxLayout()
        footer.addStretch()
        self.launch_btn = LCARSButton('OPEN DEMO', color='#4BBEBF', shape='rect')
        self.launch_btn.clicked.connect(self.launch_demo)
        footer.addWidget(self.launch_btn)
        close_btn = LCARSButton('CLOSE', color='#666666', shape='rect')
        close_btn.clicked.connect(self.close)
        footer.addWidget(close_btn)
        layout.addLayout(footer)

    def select_faction(self, faction_era):
        self.current_faction_era = faction_era
        pal = get_faction_palette(faction_era)
        name = faction_era.name.split('_')[0]
        self.status_label.setText(f'SELECTED: {name} — {len(pal.get("button_colors", []))} colors')

    def launch_demo(self):
        if not self.current_faction_era:
            self.status_label.setText('ERROR: select a faction first')
            return
        theme = get_theme(self.current_era, self.current_faction_era)
        demo = DemoDesktop(theme, title=f"LCARS Demo - {self.current_faction_era.name}")
        demo.show()

class DemoDesktop(QMainWindow):
    def __init__(self, theme: dict, title: str = 'LCARS Demo'):
        super().__init__()
        self.theme = theme
        self.setWindowTitle(title)
        self.setGeometry(120, 120, 1400, 900)
        self.setup_ui()

    def setup_ui(self):
        w = QWidget(); self.setCentralWidget(w)
        self.setStyleSheet(f"background-color: {self.theme.get('bg', '#000')};")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8,8,8,8)

        # header
        h = QHBoxLayout()
        h.addWidget(LCARSElbow('top-left', color=self.theme.get('accent')))
        title_panel = QFrame(); title_panel.setFixedHeight(70)
        title_panel.setStyleSheet(f"background:{self.theme.get('secondary')}; border-radius:6px;")
        tl = QHBoxLayout(title_panel)
        lbl = QLabel('LCARS DEMO DESKTOP'); lbl.setStyleSheet(f"color:{self.theme.get('text')}; font-size:20px; font-weight:bold;")
        tl.addWidget(lbl)
        h.addWidget(title_panel,1)
        h.addWidget(LCARSElbow('top-right', color=self.theme.get('accent')))
        layout.addLayout(h)

        # content
        content = QHBoxLayout()
        left = QVBoxLayout()
        for name in ['DASHBOARD','TACTICAL','SCIENCE','ENGINEERING','COMMUNICATIONS']:
            b = LCARSButton(name, color=self.theme.get('palette')[0], shape='left')
            b.setFixedHeight(64)
            left.addWidget(b)
        left.addStretch()
        content.addLayout(left)

        # center panels
        center = QVBoxLayout()
        main_panel = QFrame(); main_panel.setStyleSheet(f"background:{self.theme.get('palette')[2]}; border-radius:6px;")
        main_panel.setFixedHeight(260)
        mp = QVBoxLayout(main_panel)
        t = QLabel('MAIN SYSTEMS STATUS'); t.setStyleSheet(f"color:{self.theme.get('text')}; font-weight:bold;")
        mp.addWidget(t)
        mp.addWidget(QLabel('ALL SYSTEMS OPERATIONAL — DEMO'))
        center.addWidget(main_panel)

        # statbars
        sb = StatBar('CPU', self.theme.get('accent'))
        sb.setValue(37)
        center.addWidget(sb)

        content.addLayout(center,1)
        layout.addLayout(content)

        # bottom bar
        bottom = QHBoxLayout()
        bottom.addWidget(LCARSElbow('bottom-left', color=self.theme.get('accent')))
        status_text = QLabel('STARDATE: 58432.7 — DEMO READY')
        status_text.setStyleSheet(f"color:{self.theme.get('text')};")
        bottom.addWidget(status_text,1)
        bottom.addWidget(LCARSElbow('bottom-right', color=self.theme.get('accent')))
        layout.addLayout(bottom)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    launcher = FullLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
