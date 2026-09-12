"""LCARS BIOS - System Configuration Interface."""

from __future__ import annotations

import json
import platform
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import lcars.base.default as lcars_default
from lcars.base.default import ContrastColor
from lcars.themes.lcars_palette import (
    LCARSEra,
    get_era_palette,
    get_random_button_color,
    setup_lcars_font,
)

ROOT = Path(__file__).resolve().parent
SETTINGS_PATH = ROOT / "bios_settings.json"
FONTS_DIR = ROOT / "lcars" / "fonts"

ERA_OPTIONS: List[Tuple[str, str]] = [
    ("default", "Default"),
    ("22nd", "22nd Century"),
    ("23rd", "23rd Century"),
    ("23st", "23st Century"),
    ("24th", "24th Century"),
    ("24st", "24st Century"),
    ("25th", "25th Century"),
    ("29th", "29th Century"),
]

ERA_MAP = {
    "22nd": LCARSEra.COMS_22ND,
    "23rd": LCARSEra.PCARS_23RD,
    "23st": LCARSEra.PCARS_23ST,
    "24th": LCARSEra.LCARS_24TH,
    "24st": LCARSEra.LCARS_24ST,
    "25th": LCARSEra.LCARS_25TH,
    "29th": LCARSEra.TCARS_29TH,
}


def load_bios_font_family() -> str:
    """Load bundled LCARS fonts and return the best available family name."""
    preferred = [
        "LCARS",
        "FederationWide",
        "FederationWide Regular",
        "LCARS Regular",
    ]
    found: List[str] = []
    if FONTS_DIR.exists():
        for font_file in sorted(FONTS_DIR.glob("*.ttf")) + sorted(FONTS_DIR.glob("*.otf")):
            fid = QFontDatabase.addApplicationFont(str(font_file))
            if fid == -1:
                continue
            found.extend(QFontDatabase.applicationFontFamilies(fid))
    for name in preferred:
        for family in found:
            if family.lower().replace(" ", "") == name.lower().replace(" ", ""):
                return family
    if "LCARS" in found:
        return "LCARS"
    return found[0] if found else "LCARS"


def fmt_seconds(value: float) -> str:
    total = max(0, int(value))
    d, rem = divmod(total, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h or parts:
        parts.append(f"{h}h")
    if m or parts:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


class LCARSSection(QFrame):
    def __init__(self, title: str, accent: str, background: str, text_color: str):
        super().__init__()
        self._title = title
        self._accent = accent
        self._background = background
        self._text = text_color
        self.setObjectName("lcarsSection")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.top = QFrame()
        self.top.setFixedHeight(10)
        outer.addWidget(self.top)

        header = QHBoxLayout()
        header.setContentsMargins(18, 14, 18, 8)
        header.setSpacing(10)
        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        header.addWidget(self.title_label, 1)
        head = QWidget()
        head.setLayout(header)
        outer.addWidget(head)

        self.body = QVBoxLayout()
        self.body.setContentsMargins(18, 8, 18, 18)
        self.body.setSpacing(12)
        body = QWidget()
        body.setLayout(self.body)
        outer.addWidget(body)
        self.set_theme(accent, background, text_color)

    def set_theme(self, accent: str, background: str, text_color: str) -> None:
        self._accent = accent
        self._background = background
        self._text = text_color
        self.top.setStyleSheet(f"background-color: {accent}; border: none;")
        self.setStyleSheet(
            f"QFrame#lcarsSection {{ background-color: {background}; border: none; border-radius: 18px; }}"
        )
        self.title_label.setStyleSheet(
            f"color: {text_color}; font-size: 22px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )

    def add_row(self, label: str, widget: QWidget, width: int = 250) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)
        lab = QLabel(label)
        lab.setFixedWidth(width)
        lab.setWordWrap(True)
        lab.setStyleSheet(
            f"color: {self._text}; font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )
        row.addWidget(lab)
        row.addWidget(widget, 1)
        self.body.addLayout(row)


class ColorSwatch(QLabel):
    def __init__(self, title: str, color: str):
        super().__init__(title)
        self._title = title
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(42)
        self.set_color(color)

    def set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"""
            QLabel {{
                background-color: {color};
                color: {ContrastColor(color)};
                border: none;
                border-radius: 12px;
                padding: 8px 10px;
                font-size: 18px;
                font-family: 'LCARS';
                font-weight: normal;
            }}
            """
        )


class LCARSBios(QMainWindow):
    def __init__(self):
        super().__init__()
        setup_lcars_font()
        self.font_family = load_bios_font_family()

        self.setWindowTitle("LCARS BIOS")
        self.setMinimumSize(1500, 900)
        self.resize(1720, 980)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        self.theme_mode = "default"
        self.current_era = LCARSEra.LCARS_25TH
        self.system_state = lcars_default.SystemState
        self.start_time = time.time()
        self.dirty = False
        self.force_quit_without_save = False

        self.colors = self.resolve_palette()
        self.menu_buttons: List[QPushButton] = []
        self.dynamic_buttons: List[Tuple[QPushButton, str, str]] = []
        self.sections: List[LCARSSection] = []
        self.swatches: List[ColorSwatch] = []
        self.page_titles: Dict[int, str] = {}
        self.page_stack: Optional[QStackedWidget] = None

        self.build_ui()
        self.load_settings(silent=True)
        self.refresh_theme()
        self.update_chrome()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_tick)
        self.timer.start(1000)

        self.showFullScreen()

    # ---------- palette ----------
    def resolve_palette(self) -> Dict[str, Any]:
        if self.theme_mode == "default":
            base = lcars_default.DefaultPalette
            return {
                "mode": "default",
                "background": base.Background,
                "text": "#F6F6F6",
                "panel": "#0E0E12",
                "panel_alt": "#16161C",
                "header": base.Buttons[1],
                "button_colors": base.Buttons,
                "alert_colors": base.RedAlert,
            }

        palette = get_era_palette(ERA_MAP.get(self.theme_mode, LCARSEra.LCARS_25TH))
        button_colors = palette.get("button_colors", ["#202020"])
        return {
            "mode": self.theme_mode,
            "background": palette["background"],
            "text": palette["text"],
            "panel": "#101015",
            "panel_alt": "#18181F",
            "header": button_colors[0],
            "button_colors": button_colors,
            "alert_colors": palette.get("alert_colors", ["#FFAA00", "#CC0000"]),
        }

    def theme_label(self) -> str:
        for key, label in ERA_OPTIONS:
            if key == self.theme_mode:
                return label
        return "Default"

    def set_theme_mode(self, mode: str, refresh: bool = True) -> None:
        mode = (mode or "default").strip().lower()
        if mode not in {k for k, _ in ERA_OPTIONS}:
            mode = "default"
        self.theme_mode = mode
        if mode != "default":
            self.current_era = ERA_MAP.get(mode, LCARSEra.LCARS_25TH)
        self.colors = self.resolve_palette()
        lcars_default.SystemState = self.system_state
        if refresh:
            self.refresh_theme()
            self.mark_dirty()

    def set_system_state(self, state: str, refresh: bool = True) -> None:
        state = state.title()
        if state not in {"Green", "Yellow", "Red"}:
            state = "Green"
        self.system_state = state
        lcars_default.SystemState = state
        if refresh:
            self.refresh_button_styles()
            self.update_chrome()
            self.mark_dirty()

    def theme_color(self, index: int, group: str = "buttons") -> str:
        if self.theme_mode == "default":
            return lcars_default.RandomButtonColor(group, Seed=index)
        colors = self.colors.get("button_colors", [])
        if not colors:
            return self.colors["header"]
        phase = int(time.time() / 3)
        offset = abs(hash(f"{group}:{index}")) % len(colors)
        return colors[(phase + offset) % len(colors)]

    def dynamic_color(self, group: str, seed: str, index: int) -> str:
        if self.theme_mode == "default":
            return lcars_default.RandomButtonColor(group, Seed=seed)
        colors = self.colors.get("button_colors", [])
        if not colors:
            return self.colors["header"]
        phase = int(time.time() / 3)
        offset = abs(hash(f"{group}:{seed}")) % len(colors)
        return colors[(phase + offset) % len(colors)]

    # ---------- UI ----------
    def build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = self.build_header()
        layout.addWidget(self.header)

        body = QHBoxLayout()
        body.setContentsMargins(18, 18, 18, 18)
        body.setSpacing(16)
        body.addWidget(self.build_menu(), 0)

        self.page_stack = QStackedWidget()
        body.addWidget(self.page_stack, 1)

        self.sidebar = self.build_sidebar()
        body.addWidget(self.sidebar, 0)
        body_wrap = QWidget()
        body_wrap.setLayout(body)
        layout.addWidget(body_wrap, 1)

        self.footer = self.build_footer()
        layout.addWidget(self.footer)

        self.build_pages()

    def build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerFrame")
        frame.setFixedHeight(84)
        row = QHBoxLayout(frame)
        row.setContentsMargins(24, 16, 24, 16)
        row.setSpacing(16)
        self.header_title = QLabel("LCARS BIOS / SYSTEM CONFIGURATION")
        self.header_title.setStyleSheet(
            f"color: {self.colors['header']}; font-size: 26px; font-family: '{self.font_family}'; font-weight: normal; background: transparent;"
        )
        self.header_theme = QLabel("")
        self.header_theme.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.header_theme.setStyleSheet(
            f"color: {self.colors['text']}; font-size: 18px; font-family: '{self.font_family}'; font-weight: normal; background: transparent;"
        )
        row.addWidget(self.header_title, 1)
        row.addWidget(self.header_theme)
        return frame

    def build_menu(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("menuFrame")
        frame.setFixedWidth(242)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        items = [
            ("OVERVIEW", 0),
            ("DISPLAY", 1),
            ("ERA & THEME", 2),
            ("BOOT", 3),
            ("SECURITY", 4),
            ("LANGUAGE & INPUT", 5),
            ("NETWORK & DIAGNOSTICS", 6),
            ("ADVANCED & POWER", 7),
        ]
        for label, index in items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _=False, i=index: self.switch_page(i))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        layout.addStretch(1)
        self.exit_button = QPushButton("EXIT")
        self.exit_button.clicked.connect(self.request_exit_without_save)
        layout.addWidget(self.exit_button)
        self.dynamic_buttons.append((self.exit_button, "alert", "exit"))
        return frame

    def build_sidebar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sidebarFrame")
        frame.setFixedWidth(300)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.sidebar_time = QLabel("")
        self.sidebar_uptime = QLabel("")
        self.sidebar_theme = QLabel("")
        self.sidebar_state = QLabel("")
        self.sidebar_page = QLabel("")
        self.sidebar_dirty = QLabel("")
        self.sidebar_boot = QLabel("")
        self.sidebar_swatch = ColorSwatch("ACTIVE", self.colors["header"])

        for label in [
            self.sidebar_time,
            self.sidebar_uptime,
            self.sidebar_theme,
            self.sidebar_state,
            self.sidebar_page,
            self.sidebar_dirty,
            self.sidebar_boot,
        ]:
            label.setWordWrap(True)
            label.setStyleSheet(
                "font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
            )
            layout.addWidget(label)

        layout.addWidget(QLabel("CURRENT PALETTE"))
        layout.addWidget(self.sidebar_swatch)

        self.btn_save = QPushButton("SAVE")
        self.btn_apply = QPushButton("APPLY")
        self.btn_defaults = QPushButton("DEFAULTS")
        self.btn_help = QPushButton("HELP")
        self.btn_save.clicked.connect(self.save_and_remain)
        self.btn_apply.clicked.connect(self.apply_current_settings)
        self.btn_defaults.clicked.connect(self.restore_defaults)
        self.btn_help.clicked.connect(self.show_help)
        for btn, group in [
            (self.btn_save, "buttons"),
            (self.btn_apply, "buttons"),
            (self.btn_defaults, "buttons"),
            (self.btn_help, "accent"),
        ]:
            layout.addWidget(btn)
            self.dynamic_buttons.append((btn, group, btn.text().lower()))
        layout.addStretch(1)
        return frame

    def build_footer(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("footerFrame")
        frame.setFixedHeight(58)
        row = QHBoxLayout(frame)
        row.setContentsMargins(24, 10, 24, 10)
        self.footer_help = QLabel("F1: HELP | F5: APPLY | F10: SAVE & EXIT | ESC: EXIT WITHOUT SAVING")
        self.footer_help.setStyleSheet(
            "font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )
        self.footer_status = QLabel("")
        self.footer_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.footer_status.setStyleSheet(
            "font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )
        row.addWidget(self.footer_help, 1)
        row.addWidget(self.footer_status)
        return frame

    def build_pages(self) -> None:
        pages = [
            ("SYSTEM OVERVIEW", self.create_overview_page),
            ("DISPLAY CONTROL", self.create_display_page),
            ("ERA & THEME", self.create_era_page),
            ("BOOT SEQUENCE", self.create_boot_page),
            ("SECURITY", self.create_security_page),
            ("LANGUAGE & INPUT", self.create_language_page),
            ("NETWORK & DIAGNOSTICS", self.create_network_page),
            ("ADVANCED & POWER", self.create_advanced_page),
        ]
        self.page_titles = {i: title for i, (title, _) in enumerate(pages)}
        for _, factory in pages:
            page = factory()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(page)
            self.page_stack.addWidget(scroll)
        self.switch_page(0)

    def make_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        return page

    def add_section(self, page: QWidget, title: str, accent_index: int) -> LCARSSection:
        accent = self.theme_color(accent_index)
        section = LCARSSection(title, accent, self.colors["panel"], self.colors["text"])
        page.layout().addWidget(section)
        self.sections.append(section)
        return section

    # ---------- pages ----------
    def create_overview_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "SYSTEM SUMMARY", 0)
        self.overview_version = QLabel("BIOS v25.0")
        self.overview_build = QLabel(datetime.now().strftime("%Y-%m-%d"))
        self.overview_platform = QLabel(platform.platform())
        self.overview_theme = QLabel(self.theme_label())
        self.overview_state = QLabel(self.system_state)
        self.overview_uptime = QLabel("")
        for w in [self.overview_version, self.overview_build, self.overview_platform, self.overview_theme, self.overview_state, self.overview_uptime]:
            w.setStyleSheet(
                f"color: {self.colors['text']}; font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
            )
        sec.add_row("BIOS Version", self.overview_version)
        sec.add_row("Build Date", self.overview_build)
        sec.add_row("Platform", self.overview_platform)
        sec.add_row("Active Theme", self.overview_theme)
        sec.add_row("System State", self.overview_state)
        sec.add_row("Uptime", self.overview_uptime)

        sec2 = self.add_section(page, "QUICK ACTIONS", 1)
        self.btn_overview_apply = QPushButton("APPLY SETTINGS")
        self.btn_overview_save = QPushButton("SAVE TO BIOS")
        self.btn_overview_restore = QPushButton("RESTORE DEFAULTS")
        self.btn_overview_help = QPushButton("HELP")
        self.btn_overview_apply.clicked.connect(self.apply_current_settings)
        self.btn_overview_save.clicked.connect(self.save_and_remain)
        self.btn_overview_restore.clicked.connect(self.restore_defaults)
        self.btn_overview_help.clicked.connect(self.show_help)
        for btn, group in [
            (self.btn_overview_apply, "buttons"),
            (self.btn_overview_save, "buttons"),
            (self.btn_overview_restore, "buttons"),
            (self.btn_overview_help, "accent"),
        ]:
            sec2.body.addWidget(btn)
            self.dynamic_buttons.append((btn, group, btn.text().lower()))

        self.overview_log = QTextEdit()
        self.overview_log.setReadOnly(True)
        self.overview_log.setMinimumHeight(180)
        self.overview_log.setPlainText("BIOS ready.")
        sec2.body.addWidget(self.overview_log)
        return page

    def create_display_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "DISPLAY SETTINGS", 2)
        self.display_resolution = QComboBox()
        self.display_resolution.addItems(["1920x1080", "2560x1440", "3840x2160", "1600x900", "1280x720"])
        self.display_refresh = QComboBox()
        self.display_refresh.addItems(["60 Hz", "120 Hz", "144 Hz"])
        self.display_brightness = QSlider(Qt.Orientation.Horizontal)
        self.display_brightness.setRange(0, 100)
        self.display_brightness.setValue(80)
        self.display_scale = QSpinBox()
        self.display_scale.setRange(100, 200)
        self.display_scale.setValue(100)
        self.display_fullscreen = QCheckBox("Fullscreen on launch")
        self.display_fullscreen.setChecked(True)
        sec.add_row("Resolution", self.display_resolution)
        sec.add_row("Refresh Rate", self.display_refresh)
        sec.add_row("Brightness", self.display_brightness)
        sec.add_row("UI Scale", self.display_scale)
        sec.add_row("Fullscreen", self.display_fullscreen)
        self.display_apply = QPushButton("APPLY DISPLAY PROFILE")
        self.display_apply.clicked.connect(self.apply_current_settings)
        sec.body.addWidget(self.display_apply)
        self.dynamic_buttons.append((self.display_apply, "buttons", "display_apply"))
        return page

    def create_era_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "THEME SELECTION", 3)
        self.theme_combo = QComboBox()
        for key, label in ERA_OPTIONS:
            self.theme_combo.addItem(label, key)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        sec.add_row("Theme", self.theme_combo)
        self.theme_note = QLabel(
            "Default is the base LCARS palette. Era themes are optional overlays, not the base UI."
        )
        self.theme_note.setWordWrap(True)
        self.theme_note.setStyleSheet(
            f"color: {self.colors['text']}; font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )
        sec.body.addWidget(self.theme_note)

        preview = self.add_section(page, "PALETTE PREVIEW", 4)
        self.preview_layout = QGridLayout()
        self.preview_layout.setHorizontalSpacing(10)
        self.preview_layout.setVerticalSpacing(10)
        preview.body.addLayout(self.preview_layout)

        self.swatches = []
        entries = [
            ("Background", self.colors["background"]),
            ("Text", self.colors["text"]),
            ("Panel", self.colors["panel"]),
            ("Panel Alt", self.colors["panel_alt"]),
        ]
        entries.extend([(f"Btn {i+1}", c) for i, c in enumerate(self.colors["button_colors"])])
        entries.extend([(f"Alert {i+1}", c) for i, c in enumerate(self.colors["alert_colors"])])
        for idx, (name, color) in enumerate(entries):
            sw = ColorSwatch(name, color)
            self.swatches.append(sw)
            self.preview_layout.addWidget(sw, idx // 3, idx % 3)
        return page

    def create_boot_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "BOOT ORDER", 5)
        self.boot_list = QListWidget()
        self.boot_list.addItems(["SSD-0 / PRIMARY", "USB-1 / REMOVABLE", "NET-0 / PXE", "ROM / DIAGNOSTICS"])
        self.boot_list.setCurrentRow(0)
        sec.body.addWidget(self.boot_list)
        row = QHBoxLayout()
        self.btn_boot_up = QPushButton("UP")
        self.btn_boot_down = QPushButton("DOWN")
        self.btn_boot_top = QPushButton("TOP")
        self.btn_boot_bottom = QPushButton("BOTTOM")
        self.btn_boot_remove = QPushButton("REMOVE")
        self.btn_boot_add = QPushButton("ADD DEVICE")
        for btn in [self.btn_boot_up, self.btn_boot_down, self.btn_boot_top, self.btn_boot_bottom, self.btn_boot_remove, self.btn_boot_add]:
            row.addWidget(btn)
            self.dynamic_buttons.append((btn, "buttons", btn.text().lower()))
        sec.body.addLayout(row)
        self.btn_boot_up.clicked.connect(lambda: self.move_boot_item(-1))
        self.btn_boot_down.clicked.connect(lambda: self.move_boot_item(1))
        self.btn_boot_top.clicked.connect(lambda: self.move_boot_item_to_edge(True))
        self.btn_boot_bottom.clicked.connect(lambda: self.move_boot_item_to_edge(False))
        self.btn_boot_remove.clicked.connect(self.remove_boot_item)
        self.btn_boot_add.clicked.connect(self.add_boot_item)
        r2 = QHBoxLayout()
        self.boot_mode = QComboBox()
        self.boot_mode.addItems(["UEFI", "Legacy", "Hybrid"])
        self.boot_timeout = QSpinBox()
        self.boot_timeout.setRange(0, 120)
        self.boot_timeout.setValue(12)
        r2.addWidget(QLabel("Boot Mode"))
        r2.addWidget(self.boot_mode, 1)
        r2.addWidget(QLabel("Timeout"))
        r2.addWidget(self.boot_timeout, 1)
        sec.body.addLayout(r2)
        return page

    def create_security_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "SECURITY CONTROLS", 6)
        self.secure_boot = QCheckBox("Secure Boot")
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.tamper_lock = QCheckBox("Tamper lock")
        self.lockdown_mode = QCheckBox("Lockdown mode")
        self.audit_logging = QCheckBox("Audit logging")
        sec.add_row("Secure Boot", self.secure_boot)
        sec.add_row("Admin Password", self.admin_password)
        sec.add_row("User Password", self.user_password)
        sec.add_row("Tamper Lock", self.tamper_lock)
        sec.add_row("Lockdown", self.lockdown_mode)
        sec.add_row("Audit Log", self.audit_logging)
        self.btn_clear_passwords = QPushButton("CLEAR PASSWORDS")
        self.btn_clear_passwords.clicked.connect(self.clear_passwords)
        sec.body.addWidget(self.btn_clear_passwords)
        self.dynamic_buttons.append((self.btn_clear_passwords, "alert", "clear_passwords"))
        return page

    def create_language_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "LANGUAGE & INPUT", 7)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Ukrainian", "Klingon", "Vulcan", "Romulan"])
        self.keyboard_combo = QComboBox()
        self.keyboard_combo.addItems(["QWERTY", "QWERTZ", "AZERTY", "Dvorak"])
        self.repeat_rate = QSpinBox()
        self.repeat_rate.setRange(1, 60)
        self.repeat_rate.setValue(20)
        self.interface_beeps = QCheckBox("Interface beeps")
        self.voice_prompts = QCheckBox("Voice prompts")
        sec.add_row("Interface Language", self.language_combo)
        sec.add_row("Keyboard Layout", self.keyboard_combo)
        sec.add_row("Repeat Rate", self.repeat_rate)
        sec.add_row("Interface Beeps", self.interface_beeps)
        sec.add_row("Voice Prompts", self.voice_prompts)
        return page

    def create_network_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "NETWORK SETTINGS", 8)
        self.network_enabled = QCheckBox("Enable network")
        self.auto_connect = QCheckBox("Auto connect")
        self.subspace_encryption = QCheckBox("Subspace encryption")
        self.interface_name = QLabel(self.detect_primary_interface())
        self.interface_name.setStyleSheet(
            f"color: {self.colors['text']}; font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
        )
        sec.add_row("Interface", self.interface_name)
        sec.add_row("Network Enabled", self.network_enabled)
        sec.add_row("Auto Connect", self.auto_connect)
        sec.add_row("Encryption", self.subspace_encryption)
        self.net_progress = QProgressBar()
        self.net_progress.setRange(0, 100)
        self.net_progress.setValue(0)
        sec.body.addWidget(self.net_progress)
        self.network_output = QTextEdit()
        self.network_output.setReadOnly(True)
        self.network_output.setMinimumHeight(220)
        self.network_output.setPlainText("Diagnostics not run.")
        sec.body.addWidget(self.network_output)
        row = QHBoxLayout()
        self.btn_run_diag = QPushButton("RUN DIAGNOSTICS")
        self.btn_clear_diag = QPushButton("CLEAR")
        self.btn_run_diag.clicked.connect(self.run_diagnostics)
        self.btn_clear_diag.clicked.connect(lambda: self.network_output.setPlainText("Diagnostics cleared."))
        row.addWidget(self.btn_run_diag)
        row.addWidget(self.btn_clear_diag)
        sec.body.addLayout(row)
        self.dynamic_buttons.append((self.btn_run_diag, "buttons", "run_diagnostics"))
        self.dynamic_buttons.append((self.btn_clear_diag, "buttons", "clear_diagnostics"))
        return page

    def create_advanced_page(self) -> QWidget:
        page = self.make_page()
        sec = self.add_section(page, "POWER AND SYSTEM STATE", 9)
        self.system_state_combo = QComboBox()
        self.system_state_combo.addItems(["Green", "Yellow", "Red"])
        self.system_state_combo.currentTextChanged.connect(self.set_system_state)
        self.auto_apply_state = QCheckBox("Apply state immediately")
        self.auto_apply_state.setChecked(True)
        sec.add_row("System State", self.system_state_combo)
        sec.add_row("Immediate Apply", self.auto_apply_state)
        self.btn_restore_defaults = QPushButton("RESTORE DEFAULTS")
        self.btn_factory_reset = QPushButton("FACTORY RESET")
        self.btn_reboot = QPushButton("REBOOT")
        self.btn_shutdown = QPushButton("SHUTDOWN")
        for btn, group in [
            (self.btn_restore_defaults, "buttons"),
            (self.btn_factory_reset, "alert"),
            (self.btn_reboot, "buttons"),
            (self.btn_shutdown, "alert"),
        ]:
            sec.body.addWidget(btn)
            self.dynamic_buttons.append((btn, group, btn.text().lower()))
        self.btn_restore_defaults.clicked.connect(self.restore_defaults)
        self.btn_factory_reset.clicked.connect(self.factory_reset)
        self.btn_reboot.clicked.connect(self.reboot_system)
        self.btn_shutdown.clicked.connect(self.shutdown_system)
        return page

    # ---------- styling ----------
    def build_stylesheet(self) -> str:
        c = self.colors
        return f"""
        QMainWindow, QWidget#root {{
            background-color: {c['background']};
            color: {c['text']};
            font-family: '{self.font_family}';
            font-size: 18px;
            font-weight: normal;
        }}
        QFrame {{ border: none; }}
        QFrame#headerFrame {{
            background-color: {c['panel']};
            border: none;
        }}
        QFrame#footerFrame {{
            background-color: {c['panel_alt']};
            border: none;
        }}
        QFrame#menuFrame {{
            background-color: {c['panel']};
            border: none;
            border-radius: 18px;
            padding: 8px;
        }}
        QFrame#sidebarFrame {{
            background-color: {c['panel']};
            border: none;
            border-radius: 18px;
        }}
        QFrame#lcarsSection {{
            background-color: {c['panel']};
            border: none;
            border-radius: 18px;
        }}
        QScrollArea {{ background: transparent; border: none; }}
        QScrollArea > QWidget > QWidget {{ background: transparent; }}
        QComboBox, QLineEdit, QSpinBox, QTextEdit, QListWidget {{
            background-color: {c['panel_alt']};
            color: {c['text']};
            border: none;
            border-radius: 12px;
            padding: 8px 12px;
            font-family: '{self.font_family}';
            font-size: 18px;
            font-weight: normal;
        }}
        QComboBox::drop-down {{ border: none; width: 26px; }}
        QComboBox::down-arrow {{ image: none; width: 0px; height: 0px; }}
        QComboBox QAbstractItemView {{
            background-color: {c['panel']};
            color: {c['text']};
            border: none;
            selection-background-color: {c['header']};
            selection-color: {ContrastColor(c['header'])};
        }}
        QCheckBox {{
            color: {c['text']};
            font-family: '{self.font_family}';
            font-size: 18px;
            font-weight: normal;
            spacing: 10px;
            background: transparent;
        }}
        QCheckBox::indicator {{
            width: 22px;
            height: 22px;
            border: none;
            border-radius: 5px;
            background-color: {c['panel_alt']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {c['header']};
        }}
        QSlider::groove:horizontal {{
            height: 8px;
            background: {c['panel_alt']};
            border: none;
            border-radius: 4px;
        }}
        QSlider::handle:horizontal {{
            background: {c['header']};
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border: none;
            border-radius: 10px;
        }}
        QProgressBar {{
            background-color: {c['panel_alt']};
            color: {c['text']};
            border: none;
            border-radius: 10px;
            text-align: center;
            font-family: '{self.font_family}';
            font-size: 18px;
            font-weight: normal;
            height: 26px;
        }}
        QProgressBar::chunk {{
            background-color: {c['header']};
            border-radius: 10px;
        }}
        QPushButton {{
            border: none;
            border-radius: 16px;
            padding: 12px 16px;
            font-family: '{self.font_family}';
            font-size: 18px;
            font-weight: normal;
            text-align: left;
        }}
        QListWidget::item {{
            padding: 10px 12px;
        }}
        QListWidget::item:selected {{
            background-color: {c['header']};
            color: {ContrastColor(c['header'])};
        }}
        """

    def apply_theme(self) -> None:
        self.setStyleSheet(self.build_stylesheet())

    def refresh_theme(self) -> None:
        self.colors = self.resolve_palette()
        self.apply_theme()
        self.refresh_sections()
        self.refresh_swatches()
        self.refresh_nav_styles()
        self.refresh_button_styles()
        self.apply_window_chrome()
        self.style_text_labels()
        self.update_chrome()

    def refresh_sections(self) -> None:
        for idx, section in enumerate(self.sections):
            section.set_theme(self.theme_color(idx), self.colors["panel"], self.colors["text"])

    def refresh_swatches(self) -> None:
        entries = [self.colors["background"], self.colors["text"], self.colors["panel"], self.colors["panel_alt"]]
        entries.extend(self.colors["button_colors"])
        entries.extend(self.colors["alert_colors"])
        for swatch, color in zip(self.swatches, entries):
            swatch.set_color(color)

    def refresh_nav_styles(self) -> None:
        for idx, button in enumerate(self.menu_buttons):
            active = idx == self.page_stack.currentIndex()
            color = self.theme_color(idx)
            if active:
                color = self.brighten(color, 0.14)
            self.style_button(button, color)
            button.setChecked(active)

    def refresh_button_styles(self) -> None:
        for idx, (button, group, seed) in enumerate(self.dynamic_buttons):
            self.style_button(button, self.dynamic_color(group, seed, idx))

    def style_button(self, button: QPushButton, color: str) -> None:
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: {ContrastColor(color)};
                border: none;
                border-radius: 16px;
                padding: 12px 16px;
                font-family: '{self.font_family}';
                font-size: 18px;
                font-weight: normal;
                text-align: left;
                border-left: 10px solid {self.brighten(color, 0.18)};
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color, 0.12)};
            }}
            QPushButton:checked {{
                background-color: {self.brighten(color, 0.16)};
            }}
            """
        )

    def brighten(self, color: str, amount: float = 0.12) -> str:
        c = QColor(color)
        if not c.isValid():
            return color
        h = c.hue()
        if h < 0:
            h = 0
        s = c.saturation()
        v = c.value()
        c.setHsv(h, max(0, int(s * (1 - amount))), min(255, int(v + (255 - v) * amount)), c.alpha())
        return c.name()

    def style_text_labels(self) -> None:
        color = self.colors["text"]
        for name in [
            "header_title",
            "header_theme",
            "footer_help",
            "footer_status",
            "sidebar_time",
            "sidebar_uptime",
            "sidebar_theme",
            "sidebar_state",
            "sidebar_page",
            "sidebar_dirty",
            "sidebar_boot",
            "theme_note",
        ]:
            widget = getattr(self, name, None)
            if isinstance(widget, QLabel):
                widget.setStyleSheet(
                    f"color: {color}; font-size: 18px; font-family: 'LCARS'; font-weight: normal; background: transparent;"
                )

    def apply_window_chrome(self) -> None:
        self.header.setStyleSheet(f"background-color: {self.colors['header']}; border: none;")
        self.footer.setStyleSheet(f"background-color: {self.colors['panel_alt']}; border: none;")
        self.sidebar.setStyleSheet(f"background-color: {self.colors['panel']}; border: none; border-radius: 18px;")
        self.page_stack.setStyleSheet("background: transparent; border: none;")

    # ---------- runtime ----------
    def switch_page(self, index: int) -> None:
        if not self.page_stack:
            return
        index = max(0, min(index, self.page_stack.count() - 1))
        self.page_stack.setCurrentIndex(index)
        self.refresh_nav_styles()
        self.update_chrome()

    def update_chrome(self) -> None:
        self.header_theme.setText(f"Theme: {self.theme_label()}")
        self.footer_status.setText(f"STATE: {self.system_state.upper()}")
        self.sidebar_time.setText(datetime.now().strftime("TIME\n%Y-%m-%d %H:%M:%S"))
        self.sidebar_uptime.setText(f"UPTIME\n{fmt_seconds(time.time() - self.start_time)}")
        self.sidebar_theme.setText(f"THEME\n{self.theme_label()}")
        self.sidebar_state.setText(f"STATE\n{self.system_state.upper()}")
        current_page = self.page_titles.get(self.page_stack.currentIndex(), "")
        self.sidebar_page.setText(f"PAGE\n{current_page}")
        self.sidebar_dirty.setText(f"CHANGES\n{'DIRTY' if self.dirty else 'CLEAN'}")
        if hasattr(self, "boot_list") and self.boot_list.count():
            self.sidebar_boot.setText(f"BOOT\n{self.boot_list.item(0).text()}")
        self.sidebar_swatch.set_color(self.colors["header"])
        self.style_text_labels()
        if hasattr(self, "overview_theme"):
            self.overview_theme.setText(self.theme_label())
        if hasattr(self, "overview_state"):
            self.overview_state.setText(self.system_state)
        if hasattr(self, "overview_uptime"):
            self.overview_uptime.setText(fmt_seconds(time.time() - self.start_time))

    def on_tick(self) -> None:
        self.refresh_button_styles()
        self.update_chrome()

    def mark_dirty(self) -> None:
        self.dirty = True
        self.update_chrome()

    # ---------- settings ----------
    def default_settings(self) -> Dict[str, Any]:
        return {
            "theme_mode": "default",
            "system_state": "Green",
            "display": {
                "resolution": "1920x1080",
                "refresh_rate": "60 Hz",
                "brightness": 80,
                "ui_scale": 100,
                "fullscreen": True,
            },
            "boot": {
                "order": ["SSD-0 / PRIMARY", "USB-1 / REMOVABLE", "NET-0 / PXE", "ROM / DIAGNOSTICS"],
                "mode": "UEFI",
                "timeout": 12,
            },
            "security": {
                "secure_boot": True,
                "admin_password": "",
                "user_password": "",
                "tamper_lock": False,
                "lockdown_mode": False,
                "audit_logging": True,
            },
            "language": {
                "language": "English",
                "keyboard": "QWERTY",
                "interface_beeps": True,
                "voice_prompts": False,
                "repeat_rate": 20,
            },
            "network": {
                "enabled": True,
                "auto_connect": False,
                "encryption": True,
            },
            "advanced": {
                "system_state": "Green",
                "auto_apply_state": True,
            },
        }

    def collect_settings(self) -> Dict[str, Any]:
        return {
            "theme_mode": self.theme_mode,
            "system_state": self.system_state,
            "display": {
                "resolution": self.display_resolution.currentText(),
                "refresh_rate": self.display_refresh.currentText(),
                "brightness": self.display_brightness.value(),
                "ui_scale": self.display_scale.value(),
                "fullscreen": self.display_fullscreen.isChecked(),
            },
            "boot": {
                "order": [self.boot_list.item(i).text() for i in range(self.boot_list.count())],
                "mode": self.boot_mode.currentText(),
                "timeout": self.boot_timeout.value(),
            },
            "security": {
                "secure_boot": self.secure_boot.isChecked(),
                "admin_password": self.admin_password.text(),
                "user_password": self.user_password.text(),
                "tamper_lock": self.tamper_lock.isChecked(),
                "lockdown_mode": self.lockdown_mode.isChecked(),
                "audit_logging": self.audit_logging.isChecked(),
            },
            "language": {
                "language": self.language_combo.currentText(),
                "keyboard": self.keyboard_combo.currentText(),
                "interface_beeps": self.interface_beeps.isChecked(),
                "voice_prompts": self.voice_prompts.isChecked(),
                "repeat_rate": self.repeat_rate.value(),
            },
            "network": {
                "enabled": self.network_enabled.isChecked(),
                "auto_connect": self.auto_connect.isChecked(),
                "encryption": self.subspace_encryption.isChecked(),
            },
            "advanced": {
                "system_state": self.system_state_combo.currentText(),
                "auto_apply_state": self.auto_apply_state.isChecked(),
            },
        }

    def load_settings(self, silent: bool = False) -> None:
        if not SETTINGS_PATH.exists():
            self.apply_defaults_to_ui()
            self.dirty = False
            return
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            self.apply_settings_dict(data)
            self.dirty = False
        except Exception as exc:
            if not silent:
                QMessageBox.warning(self, "LCARS BIOS", f"Could not load settings:\n{exc}")
            self.apply_defaults_to_ui()
            self.dirty = False

    def save_settings(self) -> bool:
        try:
            SETTINGS_PATH.write_text(json.dumps(self.collect_settings(), indent=2), encoding="utf-8")
            self.dirty = False
            self.overview_log.append(f"Saved settings at {datetime.now().strftime('%H:%M:%S')}")
            self.update_chrome()
            return True
        except Exception as exc:
            QMessageBox.critical(self, "LCARS BIOS", f"Save failed:\n{exc}")
            return False

    def apply_settings_dict(self, data: Dict[str, Any]) -> None:
        self.block_controls(True)
        try:
            self.set_theme_mode(data.get("theme_mode", "default"), refresh=False)
            self.set_system_state(data.get("system_state", "Green"), refresh=False)

            display = data.get("display", {})
            self.set_combo_text(self.display_resolution, display.get("resolution", "1920x1080"))
            self.set_combo_text(self.display_refresh, display.get("refresh_rate", "60 Hz"))
            self.display_brightness.setValue(int(display.get("brightness", 80)))
            self.display_scale.setValue(int(display.get("ui_scale", 100)))
            self.display_fullscreen.setChecked(bool(display.get("fullscreen", True)))

            boot = data.get("boot", {})
            self.populate_boot_order(boot.get("order", []))
            self.set_combo_text(self.boot_mode, boot.get("mode", "UEFI"))
            self.boot_timeout.setValue(int(boot.get("timeout", 12)))

            sec = data.get("security", {})
            self.secure_boot.setChecked(bool(sec.get("secure_boot", True)))
            self.admin_password.setText(str(sec.get("admin_password", "")))
            self.user_password.setText(str(sec.get("user_password", "")))
            self.tamper_lock.setChecked(bool(sec.get("tamper_lock", False)))
            self.lockdown_mode.setChecked(bool(sec.get("lockdown_mode", False)))
            self.audit_logging.setChecked(bool(sec.get("audit_logging", True)))

            lang = data.get("language", {})
            self.set_combo_text(self.language_combo, lang.get("language", "English"))
            self.set_combo_text(self.keyboard_combo, lang.get("keyboard", "QWERTY"))
            self.interface_beeps.setChecked(bool(lang.get("interface_beeps", True)))
            self.voice_prompts.setChecked(bool(lang.get("voice_prompts", False)))
            self.repeat_rate.setValue(int(lang.get("repeat_rate", 20)))

            net = data.get("network", {})
            self.network_enabled.setChecked(bool(net.get("enabled", True)))
            self.auto_connect.setChecked(bool(net.get("auto_connect", False)))
            self.subspace_encryption.setChecked(bool(net.get("encryption", True)))

            adv = data.get("advanced", {})
            self.set_combo_text(self.system_state_combo, adv.get("system_state", "Green"))
            self.auto_apply_state.setChecked(bool(adv.get("auto_apply_state", True)))
        finally:
            self.block_controls(False)
        self.dirty = False
        self.refresh_theme()
        self.update_chrome()

    def apply_defaults_to_ui(self) -> None:
        self.apply_settings_dict(self.default_settings())

    def block_controls(self, state: bool) -> None:
        widgets = [
            getattr(self, name, None)
            for name in [
                "theme_combo",
                "system_state_combo",
                "display_resolution",
                "display_refresh",
                "display_brightness",
                "display_scale",
                "display_fullscreen",
                "boot_mode",
                "boot_timeout",
                "secure_boot",
                "admin_password",
                "user_password",
                "tamper_lock",
                "lockdown_mode",
                "audit_logging",
                "language_combo",
                "keyboard_combo",
                "interface_beeps",
                "voice_prompts",
                "repeat_rate",
                "network_enabled",
                "auto_connect",
                "subspace_encryption",
                "auto_apply_state",
            ]
        ]
        for widget in widgets:
            if widget is not None:
                widget.blockSignals(state)

    def set_combo_text(self, combo: QComboBox, value: str) -> None:
        idx = combo.findText(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    # ---------- actions ----------
    def on_theme_changed(self) -> None:
        if not hasattr(self, "theme_combo"):
            return
        self.set_theme_mode(self.theme_combo.currentData(), refresh=True)
        self.mark_dirty()

    def populate_boot_order(self, order: List[str]) -> None:
        if not hasattr(self, "boot_list"):
            return
        current = order or ["SSD-0 / PRIMARY", "USB-1 / REMOVABLE", "NET-0 / PXE", "ROM / DIAGNOSTICS"]
        self.boot_list.clear()
        self.boot_list.addItems(current)
        self.boot_list.setCurrentRow(0)

    def move_boot_item(self, delta: int) -> None:
        row = self.boot_list.currentRow()
        if row < 0:
            return
        target = row + delta
        if target < 0 or target >= self.boot_list.count():
            return
        item = self.boot_list.takeItem(row)
        self.boot_list.insertItem(target, item)
        self.boot_list.setCurrentRow(target)
        self.mark_dirty()

    def move_boot_item_to_edge(self, top: bool = True) -> None:
        row = self.boot_list.currentRow()
        if row < 0:
            return
        item = self.boot_list.takeItem(row)
        target = 0 if top else self.boot_list.count()
        self.boot_list.insertItem(target, item)
        self.boot_list.setCurrentRow(target)
        self.mark_dirty()

    def remove_boot_item(self) -> None:
        row = self.boot_list.currentRow()
        if row < 0:
            return
        self.boot_list.takeItem(row)
        self.mark_dirty()

    def add_boot_item(self) -> None:
        self.boot_list.addItem("NEW DEVICE")
        self.boot_list.setCurrentRow(self.boot_list.count() - 1)
        self.mark_dirty()

    def clear_passwords(self) -> None:
        self.admin_password.clear()
        self.user_password.clear()
        self.mark_dirty()

    def detect_primary_interface(self) -> str:
        try:
            host = socket.gethostname()
            ip = socket.gethostbyname(host)
            return f"{host} / {ip}"
        except Exception:
            return platform.node() or "UNKNOWN"

    def run_diagnostics(self) -> None:
        self.net_progress.setValue(10)
        lines = [
            f"Timestamp: {datetime.now().isoformat(timespec='seconds')}",
            f"Host: {platform.node()}",
            f"Platform: {platform.platform()}",
            f"Python: {platform.python_version()}",
            f"Theme: {self.theme_label()}",
            f"State: {self.system_state}",
        ]
        try:
            host = socket.gethostname()
            lines.append(f"Local host: {host}")
            lines.append(f"Local address: {socket.gethostbyname(host)}")
        except Exception as exc:
            lines.append(f"Local address unavailable: {exc}")
        try:
            probe = socket.create_connection(("1.1.1.1", 53), timeout=0.5)
            probe.close()
            lines.append("External network probe: OK")
        except Exception:
            lines.append("External network probe: OFFLINE")
        self.network_output.setPlainText("\n".join(lines))
        self.net_progress.setValue(100)
        self.overview_log.append("Diagnostics completed.")
        self.mark_dirty()

    def restore_defaults(self) -> None:
        self.theme_mode = "default"
        self.system_state = "Green"
        lcars_default.SystemState = "Green"
        self.apply_defaults_to_ui()
        self.refresh_theme()
        self.overview_log.append("Defaults restored.")
        self.mark_dirty()

    def factory_reset(self) -> None:
        resp = QMessageBox.question(
            self,
            "LCARS BIOS",
            "Factory reset will clear saved BIOS settings. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            if SETTINGS_PATH.exists():
                SETTINGS_PATH.unlink()
        except Exception:
            pass
        self.restore_defaults()
        self.save_settings()
        self.overview_log.append("Factory reset completed.")

    def reboot_system(self) -> None:
        QMessageBox.information(self, "LCARS BIOS", "Reboot requested. Simulation only.")
        self.overview_log.append("Reboot requested.")

    def shutdown_system(self) -> None:
        QMessageBox.information(self, "LCARS BIOS", "Shutdown requested. Simulation only.")
        self.overview_log.append("Shutdown requested.")

    def apply_current_settings(self) -> None:
        if hasattr(self, "theme_combo"):
            self.set_theme_mode(self.theme_combo.currentData(), refresh=True)
        if hasattr(self, "system_state_combo"):
            self.set_system_state(self.system_state_combo.currentText(), refresh=True)
        self.overview_log.append(f"Applied settings at {datetime.now().strftime('%H:%M:%S')}")
        self.mark_dirty()

    def save_and_remain(self) -> None:
        self.save_settings()

    def save_and_exit(self) -> None:
        if self.save_settings():
            self.force_quit_without_save = True
            self.close()

    def show_help(self) -> None:
        QMessageBox.information(
            self,
            "LCARS BIOS Help",
            "F1: help\nF5: apply current settings\nF10: save and exit\nEsc: exit without saving\n\nUse the left menu to switch BIOS pages.",
        )

    def request_exit_without_save(self) -> None:
        self.force_quit_without_save = True
        self.close()

    # ---------- events ----------
    def keyPressEvent(self, event: Optional[QKeyEvent]) -> None:
        if not event:
            return
        if event.key() == Qt.Key.Key_Escape:
            self.request_exit_without_save()
            return
        if event.key() == Qt.Key.Key_F1:
            self.show_help()
            return
        if event.key() == Qt.Key.Key_F5:
            self.apply_current_settings()
            return
        if event.key() == Qt.Key.Key_F10:
            self.save_and_exit()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        if self.force_quit_without_save:
            event.accept()
            return
        if self.dirty:
            response = QMessageBox.question(
                self,
                "LCARS BIOS",
                "Save BIOS settings before exit?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes,
            )
            if response == QMessageBox.StandardButton.Yes:
                event.accept() if self.save_settings() else event.ignore()
                return
            if response == QMessageBox.StandardButton.No:
                event.accept()
                return
            event.ignore()
            return
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setFont(QFont(load_bios_font_family(), 18))
    bios = LCARSBios()
    bios.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
