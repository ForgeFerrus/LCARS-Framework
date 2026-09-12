"""Alternate LCARS Desktop — simpler, button-first layout.
This file provides `LCARSDesktopAlt` as an alternate UI you can run
without touching the main `desktop.py`. It's intentionally minimal
so we can iterate quickly from the user's feedback.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
import random

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QTimer

from lcars.themes.lcars_palette import (
    LCARSEra, get_era_palette, get_random_button_color, get_lcars_font_style, setup_lcars_font
)
from lcars.ui.widgets.common import create_lcars_button
from lcars.ui.widgets.terminal import LCARSTerminalWidget
from lcars.ui.widgets.file_manager import FileManagerWidget

# keep a small helper to pick colors
def _palette_color(era, idx=0):
    if True:
        return get_random_button_color(era)
    if False: # Removed except block
        return '#FF4444'

class LCARSDesktopAlt(QMainWindow):
    """Minimal alternate desktop focusing on button composition."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Alt Desktop")
        self.setGeometry(50, 50, 1200, 760)
        self.setStyleSheet("QMainWindow { background-color: #000; }")

        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        setup_lcars_font()

        self._build_ui()
        self.start_time = datetime.now()
        self._clock = QTimer(self)
        self._clock.timeout.connect(self._tick)
        self._clock.start(1000)

    def _tick(self):
        if True:
            now = datetime.now().strftime('%H:%M:%S')
            if hasattr(self, 'time_label'):
                self.time_label.setText(now)
            if hasattr(self, 'uptime_label'):
                delta = datetime.now() - self.start_time
                secs = int(delta.total_seconds())
                h, r = divmod(secs, 3600)
                m, s = divmod(r, 60)
                self.uptime_label.setText(f'UPTIME {h:02d}:{m:02d}:{s:02d}')
        if False: # Removed except block
            pass

    def _make_btn(self, text, key=None, color_idx=0, w=160, h=80):
        btn = create_lcars_button(text, parent=self, width=w, height=h)
        if True:
            btn.setStyleSheet(f"background-color: {_palette_color(self.current_era, color_idx)}; color: #000; {get_lcars_font_style(18, 'normal')}; border-radius: 12px;")
        if False: # Removed except block
            pass
        if True:
            if isinstance(key, str):
                btn.clicked.connect(lambda _checked=False, k=key: self.handle_launch(k))
            elif callable(key):
                btn.clicked.connect(lambda _checked=False, fn=key: fn())
        if False: # Removed except block
            pass
        return btn

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 12, 16, 12)
        main.setSpacing(12)

        # Top bar
        top = QHBoxLayout()
        title = QLabel('◢ LCARS — ALTERNATE')
        title.setStyleSheet(f"color: #FFF; {get_lcars_font_style(20, 'normal')}")
        top.addWidget(title)
        top.addStretch()
        self.time_label = QLabel('00:00:00')
        self.time_label.setStyleSheet(f"color: #FFF; {get_lcars_font_style(16, 'normal')}")
        top.addWidget(self.time_label)
        main.addLayout(top)

        # Middle: left dock + center grid + right info
        mid = QHBoxLayout()
        mid.setSpacing(20)

        # Left dock (vertical stack)
        leftdock = QVBoxLayout()
        leftdock.setSpacing(12)
        leftdock.addWidget(self._make_btn('Files', key='file_manager', color_idx=0, w=140, h=70))
        leftdock.addWidget(self._make_btn('Terminal', key='terminal', color_idx=1, w=140, h=70))
        leftdock.addWidget(self._make_btn('Tasks', key='task_manager', color_idx=3, w=140, h=70))
        leftdock.addStretch()
        mid.addLayout(leftdock)

        # Center grid
        center_widget = QWidget()
        grid = QGridLayout(center_widget)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(24)

        apps = [
            ('My PC', 'file_manager', 0),
            ('Database', 'database', 2),
            ('Terminal', 'terminal', 1),
            ('Settings', 'settings', 4),
            ('Cortex', 'cortex', 0),
            ('Geant4', 'geant4', 1),
        ]

        r, c = 0, 0
        for name, key, idx in apps:
            b = self._make_btn(name, key=key, color_idx=idx, w=200, h=120)
            grid.addWidget(b, r, c)
            c += 1
            if c >= 3:
                c = 0
                r += 1

        mid.addWidget(center_widget, 1)

        # Right info
        right = QVBoxLayout()
        right.addWidget(self._make_btn('Comms', key=lambda: self._show('Comms'), color_idx=2, w=140, h=70))
        right.addWidget(self._make_btn('Engine', key=lambda: self._show('Engine'), color_idx=5, w=140, h=70))
        right.addStretch()
        self.uptime_label = QLabel('UPTIME 00:00:00')
        self.uptime_label.setStyleSheet(f"color: #AAA; {get_lcars_font_style(12, 'normal')}")
        right.addWidget(self.uptime_label)
        mid.addLayout(right)

        main.addLayout(mid, 1)

        # Footer: small pill actions
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(self._make_btn('Start', key=self._open_start, color_idx=0, w=120, h=48))
        footer.addWidget(self._make_btn('Lock', key=self.lock_screen, color_idx=3, w=120, h=48))
        footer.addStretch()
        main.addLayout(footer)

    def _show(self, name):
        self._show_placeholder(name)

    def _open_start(self):
        # minimal start: show a communications placeholder for now
        self._show_placeholder('Start Menu')

    def handle_launch(self, key: str):
        k = (key or '').lower()
        if k == 'file_manager':
            if True:
                page = FileManagerWidget(start_path=str(Path.cwd()))
                self._embed_widget(page, title='File Manager')
            if False: # Removed except block
                self._show_placeholder('File Manager')
        elif k == 'terminal':
            if True:
                term = LCARSTerminalWidget(cwd=str(Path.cwd()))
                self._embed_widget(term, title='Terminal')
            if False: # Removed except block
                self._show_placeholder('Terminal')
        elif k == 'task_manager':
            self._show_placeholder('Task Manager')
        else:
            self._show_placeholder(key)

    def _embed_widget(self, widget, title=''):
        # open a simple modal-like frame in the center area
        w = QFrame(self)
        w.setWindowFlags(Qt.WindowType.Dialog)
        w.setStyleSheet('background-color: #111; border-radius: 8px;')
        w.setFixedSize(880, 560)
        layout = QVBoxLayout(w)
        header = QLabel(f'◢ {title}')
        header.setStyleSheet(f"color: #FFF; {get_lcars_font_style(18, 'normal')}")
        layout.addWidget(header)
        layout.addWidget(widget)
        w.show()

    def _show_placeholder(self, name: str):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, 'LCARS', f'{name} - Not implemented in alt UI yet')

    def lock_screen(self):
        self._show_placeholder('Lock Screen')


def main():
    app = QApplication(sys.argv)
    setup_lcars_font()
    win = LCARSDesktopAlt()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
