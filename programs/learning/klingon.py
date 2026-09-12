#!/usr/bin/env python3
# Minimal Klingon mini-application for LCARS — single-file app
from __future__ import annotations
import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parents[2]
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lcars.base.type import Application, Label, Frame, Chassis
from lcars.base.default import RandomButtonColor, FontSetup
from lcars.base.interface import LCARSButton
from lcars.modules.sound_manager import GetSoundManager

class KlingonApp(Chassis.Window):
    """A tiny, single-file Klingon mini-app modeled after the English app.

    - Loads `resources/fonts/klingon.ttf` when available
    - Exposes `start_klingon()` for non-blocking embedding
    - `run_klingon()` is provided for standalone execution
    """

    def __init__(self, palette: list | None = None):
        super().__init__()
        self.setWindowTitle("Klingon Language Lab")
        self.setStyleSheet("background: #000; color: #FFF;")
        self.setMinimumSize(1000, 700)

        self.palette = palette or self.BuildDefaultPalette()
        self._maybe_register_klingon_font()

        self.BuildUI()

    def _maybe_register_klingon_font(self):
        try:
            font_path = Path(__file__).resolve().parents[2] / 'resources' / 'fonts' / 'klingon.ttf'
            if font_path.exists():
                fid = QFontDatabase.addApplicationFont(str(font_path))
                families = QFontDatabase.applicationFontFamilies(fid) if fid != -1 else []
                self.klingon_family = families[0] if families else 'LCARS'
            else:
                self.klingon_family = 'LCARS'
        except Exception:
            self.klingon_family = 'LCARS'

    def BuildDefaultPalette(self) -> list:
        # Klingon-ish palette: deep reds and dark accents
        return [
            '#6A0000',  # primary
            '#CC1111',  # vivid
            '#AA3300',  # accent
            '#222222',  # panels
            '#FFCC99',  # highlight
        ]

    def BuildUI(self):
        root = Chassis.Horizontal(self)
        # Left sidebar
        sidebar = Frame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet('background: #080808;')
        sidebar_layout = Chassis.Vertical(sidebar)
        sidebar_layout.setContentsMargins(8, 16, 8, 16)

        btn_phr = LCARSButton('PHRASES', ColorHexStr=self.palette[0])
        btn_vocab = LCARSButton('VOCAB', ColorHexStr=self.palette[1])
        btn_tests = LCARSButton('TESTS', ColorHexStr=self.palette[2])
        btn_settings = LCARSButton('SETTINGS', ColorHexStr=self.palette[3])

        btn_phr.setFixedHeight(50)
        btn_vocab.setFixedHeight(50)
        btn_tests.setFixedHeight(50)
        btn_settings.setFixedHeight(50)

        btn_phr.clicked.connect(lambda: self.Switch('phrases'))
        btn_vocab.clicked.connect(lambda: self.Switch('vocab'))
        btn_tests.clicked.connect(lambda: self.Switch('tests'))
        btn_settings.clicked.connect(lambda: self.Switch('settings'))

        sidebar_layout.addWidget(btn_phr)
        sidebar_layout.addWidget(btn_vocab)
        sidebar_layout.addWidget(btn_tests)
        sidebar_layout.addWidget(btn_settings)
        sidebar_layout.addStretch()

        root.addWidget(sidebar)

        # Content area (very small, informative placeholders)
        self.content = Frame()
        self.content.setStyleSheet('background: #000;')
        content_layout = Chassis.Vertical(self.content)
        content_layout.setContentsMargins(16, 16, 16, 16)

        self.title = Label('◤ KLINGON LANGUAGE LAB')
        self.title.setStyleSheet(f'color: {self.palette[4]}; font-family: "{self.klingon_family}"; font-size: 20pt;')
        content_layout.addWidget(self.title)

        self.body = Label('Qapla\' — Mini Klingon interface placeholder')
        self.body.setStyleSheet('color: #DDD; font-size: 12pt;')
        content_layout.addWidget(self.body)

        root.addWidget(self.content, 1)

        GetSoundManager().PlayAudioClip('acknowledge')

    def Switch(self, key: str):
        texts = {
            'phrases': 'Useful Klingon phrases:\n\nnuqneH!  — Hello\nQapla\'! — Success',
            'vocab': 'Vocabulary: tlhIngan Hol core words (placeholder)',
            'tests': 'Practice tests: not implemented in mini app',
            'settings': 'Settings: choose palette or font',
        }
        self.body.setText(texts.get(key, '...'))


def start_klingon():
    """Non-blocking start (for embedding into LCARS)."""
    app = Application.instance() or Application(sys.argv)
    FontSetup()
    ui = KlingonApp()
    ui.show()
    return ui


def run_klingon() -> int:
    app = Application.instance() or Application(sys.argv)
    FontSetup()
    ui = KlingonApp()
    ui.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(run_klingon())
