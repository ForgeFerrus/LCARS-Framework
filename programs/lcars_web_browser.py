#!/usr/bin/env python3
"""
LCARS Web Browser Program
Повноцінний веб-браузер з підтримкою сучасних сайтів та Star Trek закладками
"""

import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QKeySequence, QShortcut

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage
    _WEB_AVAILABLE = True
except ImportError:
    _WEB_AVAILABLE = False
    QWebEngineView = None

from lcars.ui.base.widgets import LCARSButton, LCARSInput, LCARSElbow
from lcars.themes.theme import get_theme, get_lcars_font_style, setup_lcars_font
from lcars.themes.palette import LCARSEra, FactionEra, get_random_button_color
from lcars.system.localization import LOCALIZATION as Language

# Star Trek themed bookmarks
_BOOKMARKS = [
    ("★ START PAGE",  "https://www.startpage.com"),
    ("WIKIPEDIA",     "https://en.wikipedia.org"),
    ("GITHUB",        "https://github.com"),
    ("PYTHON DOCS",   "https://docs.python.org/3/"),
    ("PYQT6 DOCS",    "https://www.riverbankcomputing.com/static/Docs/PyQt6/"),
    ("OPENAI",        "https://platform.openai.com"),
    ("★ ME WHO TREK", "https://www.mewho.com/trek/"),
    ("★ ME WHO TITAN", "https://www.mewho.com/titan/"),
    ("★ ME WHO APOD", "https://www.mewho.com/apod/"),
    ("★ ME WHO STARFIELD47", "https://www.mewho.com/starfield47/"),
    ("★ ME WHO TURBOLIFT1", "https://www.mewho.com/turbolift1/"),
    ("MEMORY ALPHA",  "https://memory-alpha.fandom.com"),
    ("STARTREK.COM",  "https://www.startrek.com"),
    ("TREKCORE",      "https://trekcore.com"),
    ("STARBASE 400 LCARS", "https://www.starbase400.org/lcars.html"),
    ("LCARS DB",      "https://www.lcarsdatabase.com"),
]

_HOME = "https://www.mewho.com/trek/"  # Start with Star Trek site

class LCARSBrowserProgram(QWidget):
    """
    Full-featured LCARS-themed web browser program.
    - Navigation bar (back, forward, reload, address bar)
    - Star Trek themed bookmarks
    - Status bar
    - Keyboard shortcuts
    """

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self._build_ui()

    def _build_ui(self):
        p = self.theme.get("palette", ["#3366CC", "#FF9900", "#CC66FF"])
        accent = self.theme.get("accent", p[0])

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ──────────────────────────────
        hdr = QHBoxLayout()
        hdr.setContentsMargins(4, 4, 4, 4)
        hdr.setSpacing(4)

        cap = QFrame()
        cap.setMinimumSize(22, 32)
        cap.setStyleSheet(
            f"background:{accent}; border-top-left-radius:16px; border-bottom-left-radius:16px;"
        )
        hdr.addWidget(cap)

        self.title_lbl = QLabel("◤ LCARS NETWORK BROWSER")
        self.title_lbl.setStyleSheet(
            f"background:{accent}; color:black; padding-left:10px; {get_lcars_font_style(15,'bold')}"
        )
        self.title_lbl.setMinimumHeight(32)
        hdr.addWidget(self.title_lbl, 1)

        root.addLayout(hdr)

        # ── NAV BAR ─────────────────────────────
        nav = QHBoxLayout()
        nav.setContentsMargins(6, 4, 6, 4)
        nav.setSpacing(6)

        self.btn_back    = LCARSButton("◂", p[0], era=self.era, shape="rect")
        self.btn_forward = LCARSButton("▸", p[0], era=self.era, shape="rect")
        self.btn_reload  = LCARSButton("↺", p[1], era=self.era, shape="rect")
        self.btn_home    = LCARSButton("⌂", accent, era=self.era, shape="rect")

        for btn in (self.btn_back, self.btn_forward, self.btn_reload, self.btn_home):
            btn.setMinimumSize(36, 28)
            nav.addWidget(btn)

        self.addr_bar = LCARSInput(p[1])
        self.addr_bar.setPlaceholderText("ENTER URL OR SEARCH QUERY...")
        self.addr_bar.returnPressed.connect(self._on_navigate)
        nav.addWidget(self.addr_bar, 1)

        self.btn_go = LCARSButton("ENGAGE", p[2], era=self.era, shape="pill")
        self.btn_go.setMinimumSize(90, 28)
        self.btn_go.clicked.connect(self._on_navigate)
        nav.addWidget(self.btn_go)

        root.addLayout(nav)

        # ── BOOKMARKS ───────────────────────────
        bm_row = QHBoxLayout()
        bm_row.setContentsMargins(6, 0, 6, 4)
        bm_row.setSpacing(4)

        for i, (label, url) in enumerate(_BOOKMARKS):
            btn = LCARSButton(label, p[i % len(p)], era=self.era, shape="pill")
            btn.setMinimumHeight(22)
            btn.clicked.connect(lambda checked, u=url: self._load(u))
            bm_row.addWidget(btn)

        bm_row.addStretch()
        root.addLayout(bm_row)

        # ── WEB VIEW ────────────────────────────
        if _WEB_AVAILABLE:
            self.webview = QWebEngineView(self)
            self.webview.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            # Connect signals
            self.webview.urlChanged.connect(self._on_url_changed)
            self.webview.titleChanged.connect(self._on_title_changed)
            self.webview.loadProgress.connect(self._on_load_progress)
            self.webview.loadFinished.connect(self._on_load_finished)
            root.addWidget(self.webview, 1)
            self._load(_HOME)
        else:
            fallback = QLabel(
                "◤ QWebEngineView NOT AVAILABLE\n"
                "Install: pip install PyQt6-WebEngine\n"
                "Or: pip install PyQtWebEngine"
            )
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback.setStyleSheet(
                f"color: #FF9900; background: #050505; {get_lcars_font_style(16, 'normal')}"
            )
            root.addWidget(fallback, 1)
            self.webview = None

        # ── STATUS BAR ──────────────────────────
        self.status_bar = QLabel("◤ READY")
        self.status_bar.setMinimumHeight(18)
        self.status_bar.setStyleSheet(
            f"background:#050505; color:#444; padding-left:8px; {get_lcars_font_style(10,'normal')}"
        )
        root.addWidget(self.status_bar)

        # ── Footer cap ──────────────────────────
        foot = QFrame()
        foot.setMinimumHeight(12)
        foot.setStyleSheet(f"background:{accent}; border-bottom-left-radius:12px; border-bottom-right-radius:12px;")
        root.addWidget(foot)

        # ── WIRE BUTTONS ────────────────────────
        self.btn_back.clicked.connect(self._go_back)
        self.btn_forward.clicked.connect(self._go_forward)
        self.btn_reload.clicked.connect(self._reload)
        self.btn_home.clicked.connect(lambda: self._load(_HOME))

        # ── KEYBOARD SHORTCUTS ──────────────────
        QShortcut(QKeySequence("Alt+Left"),  self).activated.connect(self._go_back)
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(self._go_forward)
        QShortcut(QKeySequence("F5"),        self).activated.connect(self._reload)
        QShortcut(QKeySequence("Ctrl+L"),    self).activated.connect(
            lambda: (self.addr_bar.selectAll(), self.addr_bar.setFocus())
        )

    # ──────────────────────────────────────────────
    #  NAVIGATION ACTIONS
    # ──────────────────────────────────────────────

    def _load(self, url: str):
        if not self.webview:
            return
        if not url.startswith(("http://", "https://", "file://", "about:")):
            # treat as search query
            url = f"https://www.startpage.com/search?q={url.replace(' ', '+')}"
        self.webview.setUrl(QUrl(url))
        self.addr_bar.setText(url)
        self._set_status(f"◤ LOADING: {url[:80]}...")

    def _on_navigate(self):
        text = self.addr_bar.text().strip()
        if text:
            self._load(text)

    def _go_back(self):
        if self.webview:
            self.webview.back()

    def _go_forward(self):
        if self.webview:
            self.webview.forward()

    def _reload(self):
        if self.webview:
            self.webview.reload()

    # ──────────────────────────────────────────────
    #  SIGNAL HANDLERS
    # ──────────────────────────────────────────────

    def _on_url_changed(self, url: QUrl):
        self.addr_bar.setText(url.toString())

    def _on_title_changed(self, title: str):
        if title:
            self.title_lbl.setText(f"◤ {title.upper()}")

    def _on_load_progress(self, pct: int):
        if pct < 100:
            self._set_status(f"◤ LOADING... {pct}%")

    def _on_load_finished(self, ok: bool):
        if ok:
            self._set_status("◤ UPLINK ESTABLISHED")
        else:
            self._set_status("◤ SIGNAL DEGRADED — PAGE FAILED TO LOAD")
        # clear status after 3 s
        QTimer.singleShot(3000, lambda: self._set_status("◤ STANDBY"))

    def _set_status(self, msg: str):
        self.status_bar.setText(msg)


def launch():
    """Запустити програму веб-браузера"""
    app = QApplication(sys.argv)
    from lcars.themes.theme import setup_lcars_font
    setup_lcars_font()
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("LCARS WEB BROWSER")
    window.setStyleSheet("background: black;")
    window.resize(1400, 900)
    
    # Create browser widget
    browser = LCARSBrowserProgram()
    window.setCentralWidget(browser)
    
    # Show and run
    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(launch())
