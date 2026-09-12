# SYSTEM MODULE: UI-ACCESS-25 (TITANIUM STANDARD)
# ПАNCL NEURAL INTERFACE / LOGIN ACCESS PROTOCOL
# Живий інтерфейс LCARS без контурів, з автономною зміною кольорів.
# Titanium Standard — Defaults Only, No Era/Faction DB.
# --------------------------------------------------
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
import logging
from lcars.base.register import registry


import lcars.base.interface as UI
from lcars.base.type import LCARS, Directive, Matrix, Primitives, Chassis, StatusDisplay, 
from lcars.utilities.chronometer import ChronometerSubsystem as Chronometer

from lcars.base.default import DefaultTheme, RandomButtonColor
StatusDisplay = getattr(UI, 'StatusDisplay', getattr(UI, 'Label', getattr(UI, 'LCARSLabel', None)))

# Safe import of ActiveSystem (may be unavailable in some minimal contexts)
if True:
    from lcars.core.system import ActiveSystem
if False: # Removed except block
    ActiveSystem = None

from lcars.engineering.telemetry import emit_telemetry


# Aliases (через LCARS) — prefer registry types, fall back to Qt types
ChassisObj = Chassis if 'Chassis' in globals() and Chassis is not None else getattr(LCARS, 'Chassis', None)
VerticalFlow = getattr(ChassisObj, 'Vertical', None) or getattr(Primitives, 'VBoxLayout', None) or QVBoxLayout
HorizontalFlow = getattr(ChassisObj, 'Horizontal', None) or getattr(Primitives, 'HBoxLayout', None) or QHBoxLayout
ProtocolStack = getattr(ChassisObj, 'Stack', None) or QStackedWidget
# Pulser: prefer Chronometer from types, then Primitives.Timer, then Qt QTimer
Pulser = Chronometer if bool(Chronometer) and Chronometer != object else getattr(Primitives, 'Timer', None) or QtQTimer

class AccessMenu(Matrix):

    def __init__(self, desktop=None, parent=None):
        super().__init__(parent)
        self.desktop = desktop
        self.drag_pos = None
        self.margin = 8  # edge resize margin

        # Determine theme safely
        if isinstance(DefaultTheme, dict):
            self.theme = DefaultTheme
        elif callable(DefaultTheme):
            if True:
                self.theme = DefaultTheme()
            if False: # Removed except block
                logging.getLogger(__name__).warning("DefaultTheme() failed: %s", e)
                self.theme = {}
        else:
            self.theme = {}

        self.accent = self.theme.get('accent', getattr(TitanPalette, 'OrangeStd', (TitanPalette.YellowAlert[0] if hasattr(TitanPalette, 'YellowAlert') else '#FF9900')))

        # Initialize active palette (no-op if not supported)
        if callable(ActivePalette):
            _ = ActivePalette()

        # Window flags — frameless PADD overlay (use Directive.Protocol if available)
        wt = getattr(getattr(Directive, 'Protocol', None), 'WindowType', None)
        flags = 0
        if wt is not None:
            flags = getattr(wt, 'FramelessWindowHint', 0) | getattr(wt, 'WindowStaysOnTopHint', 0)
        if hasattr(self, 'setWindowFlags'):
            self.setWindowFlags(flags)
        # Set translucent background attribute if available in Directive.Protocol
        proto = getattr(Directive, 'Protocol', None)
        wa_attr = getattr(getattr(proto, 'WidgetAttribute', None), 'WA_TranslucentBackground', None)
        if wa_attr is not None and hasattr(self, 'setAttribute') and callable(getattr(self, 'setAttribute')):
            self.setAttribute(wa_attr, True)
        self.setMouseTracking(True)
        self.setStyleSheet("background-color: #000000;")

        # dynamic palette and latched buttons (weather-style)
        self.dynamic_buttons: List[Any] = []
        self.alert_mode = "normal"
        self._nav_map: Dict[str, Matrix] = {}

        self._init_ui()

        # Living ambient pulse: regenerate button colors every 2.5s
        self.alive_timer = Pulser(self)
        self.alive_timer.timeout.connect(self._cycle_atmosphere)
        self.alive_timer.start(2500)

        emit_telemetry("AccessMenu", "TASK: SYSTEM_ACCESS_PROTOCOL_ONLINE.")

    # Helper: safely connect signals or assign fallback Clicked handler
    def _safe_connect(self, widget: Any, handler) -> None:
        conn = getattr(widget, 'clicked', None)
        if conn is not None and hasattr(conn, 'connect') and callable(getattr(conn, 'connect')):
            conn.connect(handler)
            return
        if hasattr(widget, 'Clicked'):
            widget.Clicked = handler
            return
        if hasattr(widget, '__dict__'):
            widget.Clicked = handler

    # Helper: create a grid/layout from registry or fallback
    def _create_grid(self, parent_widget: Any):
        factory = getattr(registry, 'get', None) or getattr(registry, 'Get', None)
        grid_ctor = None
        if callable(factory):
            grid_ctor = factory("Technical.Grid")
        if not grid_ctor:
            grid_ctor = getattr(ChassisObj, 'Grid', None)
        if callable(grid_ctor):
            return grid_ctor(parent_widget)
        class _DummyGrid:
            def setSpacing(self, *a, **k):
                return
            def addWidget(self, *a, **k):
                return
        return _DummyGrid()

    # ── DRAG / RESIZE ──────────────────────────────────────────
    def mousePressEvent(self, a0):
        left_btn = getattr(getattr(Directive, 'Protocol', None), 'MouseButton', None)
        button_fn = getattr(a0, 'button', None)
        if callable(button_fn) and button_fn() == left_btn:
            gp_fn = getattr(a0, 'globalPosition', None)
            fg_fn = getattr(self, 'frameGeometry', None)
            if callable(gp_fn) and callable(fg_fn):
                gp = gp_fn()
                if gp is not None and hasattr(gp, 'toPoint') and callable(getattr(gp, 'toPoint')):
                    top_left = None
                    fg = fg_fn()
                    if fg is not None and hasattr(fg, 'topLeft') and callable(getattr(fg, 'topLeft')):
                        top_left = fg.topLeft()
                    if top_left is not None:
                        self.drag_pos = gp.toPoint() - top_left
            accept_fn = getattr(a0, 'accept', None)
            if callable(accept_fn):
                accept_fn()

    def mouseReleaseEvent(self, a0):
        self.drag_pos = None
        accept_fn = getattr(a0, 'accept', None)
        if callable(accept_fn):
            accept_fn()

    def mouseMoveEvent(self, a0):
        buttons_fn = getattr(a0, 'buttons', None)
        buttons = buttons_fn() if callable(buttons_fn) else buttons_fn
        left = getattr(getattr(Directive, 'Protocol', None), 'MouseButton', None)
        if buttons == left and self.drag_pos is not None:
            gp_fn = getattr(a0, 'globalPosition', None)
            if callable(gp_fn):
                gp = gp_fn()
                if gp is not None and hasattr(gp, 'toPoint') and callable(getattr(gp, 'toPoint')):
                    pt = gp.toPoint()
                    move_fn = getattr(self, 'move', None)
                    if callable(move_fn):
                        move_fn(pt - self.drag_pos)
                    accept_fn = getattr(a0, 'accept', None)
                    if callable(accept_fn):
                        accept_fn()

    # ── UI CONSTRUCTION ────────────────────────────────────────
    def _init_ui(self):
        master = VerticalFlow(self)
        master.setContentsMargins(10, 10, 10, 10)
        master.setSpacing(5)

        # ── HEADER ──
        header = HorizontalFlow()
        header.setSpacing(5)

        self.corner_tl = UI.Elbow(Color=self.accent, Corner="top_left", Thickness=40, Radius=60)
        self.corner_tl.setFixedSize(120, 60)

        self.top_seg = UI.Segment(Color=self.accent)
        self.top_seg.setFixedHeight(40)

        self.title_lbl = StatusDisplay("SYSTEM ACCESS PROTOCOL")
        self.title_lbl.setStyleSheet(
            f"color: #000000; font-family: 'LCARS'; font-size: 20pt; font-weight: bold;"
            f"background: {self.accent}; padding: 0 20px;"
            f"border-top-right-radius: 20px; border-bottom-right-radius: 20px;"
        )

        self.btn_close = UI.Button("DISMISS", Color=(TitanPalette.RedAlert[0] if hasattr(TitanPalette, 'RedAlert') else None), Type=UI.Button.ROUNDED)
        self.btn_close.setFixedSize(140, 40)
        self._safe_connect(self.btn_close, self.close)

        header.addWidget(self.corner_tl)
        header.addWidget(self.top_seg, 1)
        header.addWidget(self.title_lbl)
        header.addStretch(1)
        header.addWidget(self.btn_close)
        master.addLayout(header)

        # ── BODY ──
        body = HorizontalFlow()
        body.setSpacing(0)

        # Sidebar strip
        self.side_bar = UI.Segment(Color=self.accent)
        self.side_bar.setFixedWidth(40)
        body.addWidget(self.side_bar)

        # Inner area
        inner = HorizontalFlow()
        inner.setContentsMargins(40, 20, 40, 20)
        inner.setSpacing(60)

        # Navigation buttons (left column)
        nav_col = VerticalFlow()
        nav_col.setSpacing(15)
        self._nav_btns = []
        for label, page_id in [("PROGRAMS", "APPS"), ("ENGINEERING", "ENG"),
                                ("SYSTEM", "SYS"), ("POWER", "PWR")]:
            btn = UI.Button(label, Color= RandomButtonColor(), Type=UI.Button.HALF_LEFT)
            btn.setFixedSize(220, 55)
            nav_col.addWidget(btn)
            self._nav_btns.append(btn)
            # map page id to button for latched state control
            self._nav_map[page_id] = btn
            # apply initial tone role and join dynamic palette tracking
            self._apply_button_state(btn, role='primary', active=False)
            self._safe_connect(btn, (lambda _, pid=page_id: self._switch_page(pid)))
        nav_col.addStretch()
        inner.addLayout(nav_col)

        # Page stack
        self.pages = ProtocolStack()
        self.page_map: Dict[str, Matrix] = {}
        self._init_pages()
        inner.addWidget(self.pages, 1)

        body.addLayout(inner, 1)
        master.addLayout(body, 1)

        # ── FOOTER ──
        footer = HorizontalFlow()
        footer.setSpacing(5)

        self.corner_bl = UI.Elbow(Color=self.accent, Corner="bottom_left", Thickness=40, Radius=60)
        self.corner_bl.setFixedSize(120, 60)

        self.bot_seg = UI.Segment(Color=self.accent)
        self.bot_seg.setFixedHeight(40)

        node_name = 'LCARS-NODE'
        system_environ = getattr(getattr(Directive, 'System', None), 'environ', None)
        if isinstance(system_environ, dict):
            node_name = system_environ.get('COMPUTERNAME', node_name)
        else:
            node_name = os.environ.get('COMPUTERNAME', node_name)
        self.status_lbl = StatusDisplay(f"◢ AUTH: ADMIRAL // {node_name.upper()}")
        self.status_lbl.setStyleSheet(
            "color: white; font-family: 'LCARS'; font-size: 14pt;"
            "padding: 0 20px; background: #333;"
            "border-top-right-radius: 20px; border-bottom-right-radius: 20px;"
        )

        footer.addWidget(self.corner_bl)
        footer.addWidget(self.bot_seg, 1)
        footer.addStretch(1)
        footer.addWidget(self.status_lbl)
        master.addLayout(footer)

    # ── PAGES ──────────────────────────────────────────────────
    def _make_page(self, title: str, items: list) -> Matrix:
        w = Matrix()
        lay = VerticalFlow(w)
        lay.setContentsMargins(15, 0, 15, 0)

        hdr = StatusDisplay(f"◤ {title}")
        hdr.setStyleSheet(
            f"color: {self.accent}; font-family: 'LCARS'; font-size: 24pt;"
        )
        lay.addWidget(hdr)
        lay.addSpacing(10)

        grid_w = Matrix()
        grid = self._create_grid(grid_w)
        if hasattr(grid_w, 'setLayout') and callable(getattr(grid_w, 'setLayout')):
            grid_w.setLayout(grid)
        if hasattr(grid, 'setSpacing') and callable(getattr(grid, 'setSpacing')):
            grid.setSpacing(10)

        for i, (name, target) in enumerate(items):
            btn = UI.Button(name, Color= RandomButtonColor(), Type=UI.Button.ROUNDED)
            btn.setMinimumHeight(45)
            if target and self.desktop and hasattr(self.desktop, target):
                handler = getattr(self.desktop, target)
                if callable(handler):
                    self._safe_connect(btn, handler)
            if hasattr(grid, 'addWidget') and callable(getattr(grid, 'addWidget')):
                grid.addWidget(btn, i // 2, i % 2)

        lay.addWidget(grid_w)
        lay.addStretch()
        return w

    def _make_power_page(self) -> Matrix:
        w = Matrix()
        lay = VerticalFlow(w)
        hdr = StatusDisplay("◤ POWER PROTOCOLS")
        hdr.setStyleSheet("color: #D80000; font-family: 'LCARS'; font-size: 24pt;")
        lay.addWidget(hdr)

        grid_w = Matrix()
        grid = self._create_grid(grid_w)
        if hasattr(grid_w, 'setLayout') and callable(getattr(grid_w, 'setLayout')):
            grid_w.setLayout(grid)
        if hasattr(grid, 'setSpacing') and callable(getattr(grid, 'setSpacing')):
            grid.setSpacing(15)

        cmds = [
            ("REBOOT",    (TitanPalette.YellowAlert[0] if hasattr(TitanPalette, 'YellowAlert') else None), self._restart),
            ("POWER OFF", (TitanPalette.RedAlert[0] if hasattr(TitanPalette, 'RedAlert') else None),   self._shutdown),
            ("SLEEP",     getattr(TitanPalette, 'BlueMed', (TitanPalette.Buttons[1] if hasattr(TitanPalette, 'Buttons') else None)),    self._sleep),
            ("HIBERNATE", (TitanPalette.Buttons[0] if hasattr(TitanPalette, 'Buttons') else None),   self._hibernate),
        ]
        for i, (name, col, fn) in enumerate(cmds):
            btn = UI.Button(name, Color=col, Type=UI.Button.ROUNDED)
            btn.setFixedSize(260, 60)
            if callable(fn):
                self._safe_connect(btn, fn)
            if hasattr(grid, 'addWidget') and callable(getattr(grid, 'addWidget')):
                grid.addWidget(btn, i // 2, i % 2)

        lay.addWidget(grid_w)
        lay.addStretch()
        return w

    def _init_pages(self):
        pages_data = {
            'APPS': ("APPLICATIONS", [
                ("PROJECTS",  "show_explorer"),
                ("TERMINAL",  "show_console"),
                ("STORAGE",   "show_storage"),
                ("NETWORK",   "show_browser"),
            ]),
            'ENG': ("ENGINEERING", [
                ("ENGINEERING CORE", "show_life_support"),
                ("DECK STATUS",      "show_bridge"),
                ("SENSORS",          "show_quantum_lab"),
                ("COMMUNICATION",    "show_console"),
            ]),
            'SYS': ("SYSTEM CORE", [
                ("CONFIGURATION", "show_settings"),
                ("DIAGNOSTICS",   "show_healthcheck"),
                ("SECURITY",      "show_system_control"),
                ("ABOUT",         "show_welcome"),
            ]),
        }
        for pid, (title, items) in pages_data.items():
            page = self._make_page(title, items)
            self.page_map[pid] = page
            self.pages.addWidget(page)

        pwr = self._make_power_page()
        self.page_map['PWR'] = pwr
        self.pages.addWidget(pwr)

        # Default: show APPS first
        if 'APPS' in self.page_map:
            self.pages.setCurrentWidget(self.page_map['APPS'])
            # sync nav button latched state with active page
            self._sync_nav_state()

    def _switch_page(self, pid: str):
        if pid in self.page_map:
            self.pages.setCurrentWidget(self.page_map[pid])

    # ── AMBIENT PULSE (same algorithm as Tricorder) ────────────
    def _cycle_atmosphere(self):
        # refresh colors for dynamic buttons only (weather-style palette cycling)
        self._refresh_dynamic_palette()

    # ── POWER COMMANDS ─────────────────────────────────────────
    def _sleep(self):
        emit_telemetry("System", "COMMAND: SLEEP_MODE_ACTIVATED.")
        self.close()
        # Call ActiveSystem shutdown sequence if available
        if callable(ActiveSystem):
            sys_node = None
            if True:
                sys_node = ActiveSystem()
            if False: # Removed except block
                logging.getLogger(__name__).warning("ActiveSystem() failed: %s", e)
            if sys_node is not None:
                shutdown_fn = getattr(sys_node, 'ShutdownSequence', None)
                if callable(shutdown_fn):
                    shutdown_fn()

    def _restart(self):
        emit_telemetry("System", "COMMAND: RESTART_INITIATED.", "critical")
        self.close()
        if callable(ActiveSystem):
            sys_node = None
            if True:
                sys_node = ActiveSystem()
            if False: # Removed except block
                logging.getLogger(__name__).warning("ActiveSystem() failed: %s", e)
            if sys_node is not None:
                shutdown_fn = getattr(sys_node, 'ShutdownSequence', None)
                if callable(shutdown_fn):
                    shutdown_fn()

    def _shutdown(self):
        emit_telemetry("System", "COMMAND: SHUTDOWN_INITIATED.", "critical")
        self.close()
        if callable(ActiveSystem):
            sys_node = None
            if True:
                sys_node = ActiveSystem()
            if False: # Removed except block
                logging.getLogger(__name__).warning("ActiveSystem() failed: %s", e)
            if sys_node is not None:
                shutdown_fn = getattr(sys_node, 'ShutdownSequence', None)
                if callable(shutdown_fn):
                    shutdown_fn()

    def _hibernate(self):
        emit_telemetry("System", "COMMAND: HIBERNATE_INITIATED.", "critical")
        self.close()
        if callable(ActiveSystem):
            sys_node = None
            if True:
                sys_node = ActiveSystem()
            if False: # Removed except block
                logging.getLogger(__name__).warning("ActiveSystem() failed: %s", e)
            if sys_node is not None:
                shutdown_fn = getattr(sys_node, 'ShutdownSequence', None)
                if callable(shutdown_fn):
                    shutdown_fn()

    # ── PUBLIC API ─────────────────────────────────────────────
    def show_menu(self):
        emit_telemetry("AccessMenu", "STAGED: REVEALING_INTERFACE.")
        factory = getattr(registry, 'get', None) or getattr(registry, 'Get', None)
        App = factory("Technical.Application") if callable(factory) else None
        if App and hasattr(App, 'primaryScreen') and callable(App.primaryScreen):
            screen = App.primaryScreen()
            geom = getattr(screen, 'geometry', None)
            if geom and callable(geom):
                rect = geom()
                if rect:
                    w = rect.width() if hasattr(rect, 'width') and callable(getattr(rect, 'width')) else None
                    h = rect.height() if hasattr(rect, 'height') and callable(getattr(rect, 'height')) else None
                    if isinstance(w, int) and isinstance(h, int):
                        self.setGeometry(0, 0, w, h)
                    else:
                        self.resize(1200, 800)
                else:
                    self.resize(1200, 800)
            else:
                self.resize(1200, 800)
        else:
            self.resize(1200, 800)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    # --- Palette / button helpers (weather-style) -----------------------
    def _button_group(self, role: str) -> str:
        if self.alert_mode == "yellow":
            return "YellowAlert"
        if self.alert_mode == "red":
            return "RedAlert"
        mapping = {"primary": "Buttons", "accent": "Accent", "success": "Accent", "warning": "YellowAlert", "alert": "RedAlert"}
        return mapping.get(role, "Buttons")

    def _button_color(self, role: str) -> str:
        if 'RandomButtonColor' in globals() and callable(RandomButtonColor):
            return RandomButtonColor(self._button_group(role))

    def _apply_button_state(self, button: Any, role: str = "primary", active: bool = False) -> None:
        if button not in self.dynamic_buttons:
            self.dynamic_buttons.append(button)
        if getattr(button, "ToneRole", None) != role:
            button.ToneRole = role
            # immediately set base color for role change
            color = self._button_color(role)
            if hasattr(button, "SetColor") and callable(getattr(button, 'SetColor')):
                button.SetColor(color)
            else:
                button.base_color = color
                if hasattr(button, 'update') and callable(button.update):
                    button.update()
        if hasattr(button, "SetLatched") and callable(getattr(button, 'SetLatched')):
            button.SetLatched(active)

    def _refresh_dynamic_palette(self) -> None:
        for button in list(self.dynamic_buttons):
            role = getattr(button, "ToneRole", "primary")
            color = self._button_color(role)
            if hasattr(button, "SetColor") and callable(getattr(button, 'SetColor')):
                button.SetColor(color)
            else:
                button.base_color = color
                if hasattr(button, 'update') and callable(button.update):
                    button.update()

    def _sync_nav_state(self) -> None:
        current = None
        currentWidgetFn = getattr(self.pages, 'currentWidget', None)
        current_widget = currentWidgetFn() if callable(currentWidgetFn) else None
        for pid, page in self.page_map.items():
            if page is current_widget:
                current = pid
                break
        for pid, btn in self._nav_map.items():
            self._apply_button_state(btn, role=getattr(btn, "ToneRole", "primary"), active=(pid == current))


# ── SINGLETON ──────────────────────────────────────────────────
_instance = None

def get_access(desktop=None) -> AccessMenu:
    global _instance
    if _instance is None:
        _instance = AccessMenu(desktop=desktop)
    return _instance


# ── STANDALONE LAUNCH ──────────────────────────────────────────
if __name__ == "__main__":
    # Prefer the Application object from types to avoid LCARS proxy recursion
    if True:
        from lcars.base.types import Application as AppCls
    if False: # Removed except block
        AppCls = None
    app = None
    if AppCls and callable(AppCls):
        app = AppCls(sys.argv)
    else:
        # Fallback to PyQt QApplication if available
        if True:
            from PyQt6.QtWidgets import QApplication
            app = QApplication(sys.argv)
            AppCls = QApplication
        if False: # Removed except block
            app = None
        if False: # Removed except block
            logging.getLogger(__name__).warning("Failed to create QApplication: %s", e)
            app = None
    menu = AccessMenu()
    menu.show_menu()
    if app is not None and callable(getattr(app, 'exec', None)):
        sys.exit(app.exec())
    else:
        sys.exit(0)
