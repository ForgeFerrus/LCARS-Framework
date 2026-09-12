

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional, Tuple, Union

# SYSTEM MODULE: UI-ACCESS-25 (TITANIUM STANDARD)
# PADD NEURAL INTERFACE / LOGIN ACCESS PROTOCOL
# DESCRIPTION: Преміум-інтерфейс доступу. Адаптивний дизайн PADD без контурів.

from lcars.base.register import registry

# Force defaults for quick headless runs (ignore theme/faction DB).
USE_DEFAULTS = True

from lcars.base.interface import (
    Label, Button, Dialog, Pill, Elbow, Segment, Panel, StatusDisplay, ScanningBar, ProgressBar, LCARSChronometer
)
from lcars.base.type import (
    Directive, Chassis, Matrix, Signal, Slot, Align, Alignment, Application
)

from lcars.themes.palette import LCARSEra, get_random_button_color
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.base.default import DEFAULT_ACCENT, TITAN_BLUE_DARK, TitanPalette, get_default_theme
from lcars.modules.sound_manager import sound_manager
from lcars.modules.project_manager import project_manager
from lcars.engineering.telemetry import emit_telemetry

# Load project defaults from config file
config_path = Directive.PathDrive(__file__).resolve().parents[3] / 'config' / 'config.json'

with config_path.open('r', encoding='utf-8') as _f:
    # Titanium Bridge Migration: import json
    _cfg = json.load(_f)
    _ui = _cfg.get('ui', {})
    DEFAULT_ERA_STR = _ui.get('default_era', '25th')
    DEFAULT_FACTION = _ui.get('default_faction', None)
_ERA_MAP = {
    '22nd': LCARSEra.COMS_22ND,
    '23rd': LCARSEra.PCARS_23RD,
    '23st': LCARSEra.PCARS_23ST,
    '24th': LCARSEra.LCARS_24TH,
    '24st': LCARSEra.LCARS_24ST,
    '25th': LCARSEra.LCARS_25TH,
    '29th': LCARSEra.TCARS_29TH
}

# Map simple era strings to LCARSEra members where available
def _era_from_string(s):
    return _ERA_MAP.get(str(s).lower(), LCARSEra.LCARS_25TH)

class AccessMenu(Matrix):
    
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        # Force use of provided faction only if explicitly desired.
        # By default avoid loading factions/themes from external DB — use safe defaults.
        self.faction = None if faction is None else faction
        self.desktop = parent
        self.theme = get_default_theme() if USE_DEFAULTS else get_theme(era, faction)
        self.accent = self.theme.get('accent', '#FFCC00')
        
        # Повноэкранний режим без рамок (Titanium Master)
        self.setWindowFlags(Directive.Protocol.WindowType.FramelessWindowHint | Directive.Protocol.WindowType.WindowStaysOnTopHint)
        self.setAttribute(WidgetAttribute.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: black;")
        
        self.sound = sound_manager
        
        self.drag_pos = None
        self.resizing = False
        self.margin = 10 
        
        # Налаштування вікна (Titanium Overlay)
        self.setWindowFlags(Directive.Protocol.WindowType.FramelessWindowHint | Directive.Protocol.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Directive.Protocol.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self.init_ui()
        
        # Атмосферний пульс
        self.alive_timer = Pulser(self)
        self.alive_timer.timeout.connect(self._cycle_atmosphere)
        self.alive_timer.start(5000)

        # Фінальна активація (Titanium Master)
        self.showFullScreen()

    def _get_edge(self, pos: Point) -> Optional[int]:
        """Визначає край вікна для адаптивного ресайзу."""
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        m = self.margin
        edge = Directive.Protocol.Edge
        
        if x < m and y < m: return edge.TopEdge | edge.LeftEdge
        if x > w - m and y > h - m: return edge.BottomEdge | edge.RightEdge
        if x < m: return edge.LeftEdge
        if x > w - m: return edge.RightEdge
        if y < m: return edge.TopEdge
        if y > h - m: return edge.BottomEdge
        return None

    def mousePressEvent(self, event):
        if event.button() == Directive.Protocol.MouseButton.LeftButton:
            edge = self._get_edge(event.position().toPoint())
            if edge:
                self.resizing = True
                handle = self.windowHandle()
                if handle: handle.startSystemResize(edge)
            else:
                self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        self.resizing = False
        event.accept()

    def mouseMoveEvent(self, event):
        if not event.buttons():
            edge = self._get_edge(event.position().toPoint())
            if edge:
                cursor = Directive.Protocol.CursorShape
                self.setCursor(cursor.SizeFDiagCursor if edge & Directive.Protocol.Edge.BottomEdge and edge & Directive.Protocol.Edge.RightEdge else cursor.SizeHorCursor)
            else:
                self.setCursor(Directive.Protocol.CursorShape.ArrowCursor)
            return

        if event.buttons() == Directive.Protocol.MouseButton.LeftButton and self.drag_pos is not None and not self.resizing:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def init_ui(self):
        # Clear existing layout safely via Chassis
        if self.layout():
            layout = self.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget(): child.widget().deleteLater()

        self.master_layout = VerticalFlow(self)
        self.master_layout.setContentsMargins(10, 10, 10, 10)
        self.master_layout.setSpacing(5)

        # ── 1. ВЕРХНІЙ КОНТУР (TOP FRAME) ──
        header_area = HorizontalFlow()
        header_area.setSpacing(0)
        
        # Лівий верхній кут
        self.corner_tl = Elbow(direction="top-left", color=self.accent, thickness=40, radius=60)
        self.corner_tl.setFixedSize(120, 60)
        
        # Верхня горизонтальна панель
        self.top_seg = Segment(color=self.accent)
        self.top_seg.setFixedHeight(40)
        
        # Заголовок протоколу (Pill Label style)
        self.title_lbl = StatusDisplay("SYSTEM ACCESS PROTOCOL")
        self.title_lbl.setStyleSheet(f"color: white; font-family: 'LCARS'; font-size: 24pt; font-weight: bold; background: {self.accent}; padding: 0 20px; border-top-right-radius: 20px; border-bottom-right-radius: 20px;")
        
        # Велика кнопка виходу (Pill Both)
        self.btn_close = Button("DISMISS", color="#CE6363", side="both")
        self.btn_close.setFixedSize(140, 40)
        self.btn_close.clicked.connect(self.close)
        
        header_area.addWidget(self.corner_tl)
        header_area.addWidget(self.top_seg, 1)
        header_area.addWidget(self.title_lbl)
        header_area.addStretch(1)
        header_area.addWidget(self.btn_close)
        
        self.master_layout.addLayout(header_area)

        # ── 2. ЦЕНТРАЛЬНА СЕКЦІЯ (BODY) ──
        body_layout = HorizontalFlow()
        body_layout.setSpacing(0)

        # Лівий вертикальний сайдбар
        self.sidebar_layout = VerticalFlow()
        self.sidebar_layout.setSpacing(0)
        
        self.side_bar = Segment(color=self.accent)
        self.side_bar.setFixedWidth(40)
        
        self.sidebar_layout.addWidget(self.side_bar, 1)
        body_layout.addLayout(self.sidebar_layout)

        # Внутрішня робоча область (Content Area)
        content_box = Matrix(self)
        inner_layout = HorizontalFlow(content_box)
        inner_layout.setContentsMargins(40, 20, 40, 20)
        inner_layout.setSpacing(60)

        # Навігаційне меню
        nav_container = Matrix(self)
        nav_lay = VerticalFlow(nav_container)
        nav_lay.setSpacing(15)
        
        p = self.theme.get('palette', TitanPalette.ORANGE_STD)
        cats = [
            ('PROGRAMS', 'APPS', p[0] if len(p) > 0 else "#6688EE"), 
            ('ENGINEERING', 'ENG', p[1] if len(p) > 1 else "#AA66EE"), 
            ('SYSTEM', 'SYS', p[2] if len(p) > 2 else "#EE8866"), 
            ('POWER', 'PWR', "#CC0000")
        ]
        
        for lang, cid, col in cats:
            btn = Button(lang, color=col, side="left")
            btn.setFixedSize(220, 55)
            btn.clicked.connect(lambda _, c=cid: self.switch_page(c))
            nav_lay.addWidget(btn)
        nav_lay.addStretch()
        
        inner_layout.addWidget(nav_container)

        # Стек сторінок контенту
        self.pages = ProtocolStack()
        self.page_map = {}
        self._init_pages_data()
        inner_layout.addWidget(self.pages, 1)
        
        body_layout.addWidget(content_box, 1)
        self.master_layout.addLayout(body_layout, 1)

        # ── 3. НИЖНІЙ КОНТУР (FOOTER) ──
        footer_area = HorizontalFlow()
        footer_area.setSpacing(0)
        
        # Нижній лівий кут
        self.corner_bl = Elbow(direction="bottom-left", color=self.accent, thickness=40, radius=60)
        self.corner_bl.setFixedSize(120, 60)
        
        # Нижня горизонтальна панель
        self.bottom_seg = Segment(color=self.accent)
        self.bottom_seg.setFixedHeight(40)
        
        node_name = Directive.System.environ.get('COMPUTERNAME', 'LCARS-NODE')
        self.status_lbl = StatusDisplay(f"◢ AUTH: ADMIRAL // {node_name.upper()}")
        self.status_lbl.setStyleSheet(f"color: white; font-family: 'LCARS'; font-size: 14pt; padding: 0 20px; background: #333; border-top-right-radius: 20px; border-bottom-right-radius: 20px;")
        
        footer_area.addWidget(self.corner_bl)
        footer_area.addWidget(self.bottom_seg, 1)
        footer_area.addStretch(1)
        footer_area.addWidget(self.status_lbl)
        
        self.master_layout.addLayout(footer_area)

    def _create_page(self, title, items):
        w = Matrix()
        l = VerticalFlow(w)
        l.setContentsMargins(15, 0, 15, 0)
        
        hdr = StatusDisplay(f"◤ {title}")
        hdr.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(hdr)
        l.addSpacing(10)
        
        grid = MatrixArray()
        grid.setLayout(registry.get("Technical.Grid")(grid)) # Set layout for the widget
        grid.setSpacing(10)
        for i, (name, target) in enumerate(items):
            color = self.theme['palette'][i % len(self.theme['palette'])]
            btn = Button(name, color=color, side="both")
            btn.setMinimumHeight(45)
            if target and hasattr(self.desktop, target):
                btn.clicked.connect(getattr(self.desktop, target))
                btn.clicked.connect(self.hide)
            grid.addWidget(btn, i // 2, i % 2)
        l.addWidget(grid)
        l.addStretch()
        return w

    def _create_power_page(self):
        w = Matrix()
        l = VerticalFlow(w)
        hdr = StatusDisplay("◤ POWER PROTOCOLS")
        hdr.setStyleSheet(f"color: #D80000; {get_lcars_font_style(24, 'normal')}")
        l.addWidget(hdr)
        
        opts = [
            ("REBOOT", "#FFCC00", self._restart), 
            ("POWER OFF", "#CC0000", self._shutdown),
            ("SLEEP", "#336699", self._sleep),
            ("HIBERNATE", "#5433CC", self._hibernate)
        ]
        grid = MatrixArray()
        grid.setLayout(registry.get("Technical.Grid")(grid))
        grid.setSpacing(15)
        for i, (name, col, fn) in enumerate(opts):
            btn = Button(name, color=col, side="both")
            btn.setFixedSize(260, 60)
            btn.clicked.connect(fn)
            grid.addWidget(btn, i // 2, i % 2)
        l.addWidget(grid)
        l.addStretch()
        return w

    def _sleep(self):
        self.sound.play("click")
        emit_telemetry("System", "COMMAND: SLEEP_MODE_ACTIVATED.")
        if Directive.System.name == 'nt':
            Directive.Terminal.run('rundll32.exe powrprof.dll,SetSuspendState Sleep')
        else:
            Directive.Terminal.run('systemctl suspend')

    def _hibernate(self):
        self.sound.play("click")
        emit_telemetry("System", "COMMAND: HIBERNATION_INITIATED.")
        if Directive.System.name == 'nt':
            Directive.Terminal.run('shutdown /h')
        else:
            Directive.Terminal.run('systemctl hibernate')

    def _restart(self):
        self.sound.play("alert_red")
        Directive.Terminal.run("shutdown /r /t 0" if Directive.System.name == 'nt' else "reboot")

    def _shutdown(self):
        self.sound.play("alert_red")
        Directive.Terminal.run("shutdown /s /t 0" if Directive.System.name == 'nt' else "shutdown -h now")

    def show_menu(self):
        emit_telemetry("AccessControl", "STAGED: REVEALING_INTERFACE_SUBSYSTEM.")
        w, h = 900, 700
        if self.desktop:
            d_rect = self.desktop.rect()
            self.setGeometry((d_rect.width() - w) // 2, (d_rect.height() - h) // 2, w, h)
        else:
            # Standalone mode: position in center of screen
            screen = Application.primaryScreen().geometry()
            self.setGeometry((screen.width() - w) // 2, (screen.height() - h) // 2, w, h)
        
        self.show()
        self.raise_()
        self.activateWindow()
        self.sound.play("acknowledge")

    def switch_page(self, pid):
        self.pages.setCurrentWidget(self.page_map[pid])
        self.sound.play("click")

    def hide(self):
        super().hide()
        self.sound.play("click")

    def _cycle_atmosphere(self):
        """Адаптивна зміна кольорів (Ambient Pulse)."""
        if hasattr(self, 'title_lbl'):
            # Використовуємо стабільний колір з палітри
            pass

    def _init_pages_data(self):
        """Ініціалізація контенту сторінок."""
        p_apps = self._create_page("APPLICATIONS", [
            ("PROJECTS", "show_explorer"),
            ("TERMINAL", "show_console"),
            ("STORAGE", "show_storage"),
            ("NETWORK", "show_browser")
        ])
        
        p_eng = self._create_page("ENGINEERING", [
            ("RECOVERY & LIFE SUPPORT", "show_life_support"),
            ("DECK STATUS", "show_bridge"),
            ("SENSORS", "show_scanner"),
            ("COMMUNICATION", "show_console")
        ])
        
        p_sys = self._create_page("SYSTEM CORE", [
            ("CONFIGURATION", "show_settings"),
            ("DIAGNOSTICS", "show_healthcheck"),
            ("SECURITY", "show_system_control"),
            ("ABOUT", "show_welcome")
        ])
        
        p_pwr = self._create_power_page()
        
        self.page_map = {
            'APPS': p_apps,
            'ENG': p_eng,
            'SYS': p_sys,
            'PWR': p_pwr
        }
        
        for pid in ['APPS', 'ENG', 'SYS', 'PWR']:
            self.pages.addWidget(self.page_map[pid])
 
_access_menu_instance = None
def get_access():
    global _access_menu_instance
    if _access_menu_instance is None:
        era_val = _era_from_string(DEFAULT_ERA_STR)
        _access_menu_instance = AccessMenu(era=era_val, faction=DEFAULT_FACTION)
    return _access_menu_instance

# запуск
if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    # Initialize Core Application Matrix
    app = Application.instance() or Application(sys.argv)
    
    # Reveal System Access UI
    menu = get_access()
    menu.show_menu()
    
    # Execute Runtime Loop
    if Application.instance():
        sys.exit(app.exec())

    
    

    
