# LCARS TERMINAL INTERFACE - DESKTOP CORE
# Система: 25.04.02 (TITAN ARCHITECTURE / CLEAN RESTORATION)
# Авторизація: Рівень 10 (ADMIRAL) // U.S.S. TITAN-A / ODYSSEY
# Протокол безпеки: EPSILON-9-THETA
# Опис: Головний інтерфейс LCARS для управління заголовком, бічною навігацією,
#       динамічними вікнами перегляду та телеметрією. Файл містить основне
#       вікно-десктоп, вбудовані панелі та логіку реакції на глобальні події.
import logging
import psutil
import random
from datetime import datetime
import os, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if root not in sys.path:
    sys.path.insert(0, root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.themes.palette import (LCARSEra, FactionEra, get_random_button_color 
)
from lcars.ui.base.widgets import (LCARSButton, ScanningBar, StatBar,
    DataBlock, ConfirmationOverlay, StasisPanel, LCARSElbow, LCARSContour,
)
from lcars.ui.loading_screen import LCARSLoadingScreen
from lcars.ui.views.console import ConsoleView
from lcars.ui.views.engineering import EngineeringView
from lcars.ui.views.project_explorer import ProjectExplorerView
from lcars.ui.views.programs import ProgramsView
from lcars.ui.views.system_access import AccessMenu
# Оновлено: вказано на новий повний інтерфейс SystemControlCenter (псевдонім SystemMenu)
from lcars.ui.system import SystemMenu
from lcars.ui.views.bios_dialog import BIOSDialog
from lcars.ui.panels.storage import StoragePanel
from lcars.ui.onboard import OnboardComputerDrawer
from lcars.modules.sound_manager import get_sound_manager
from lcars.system.alert import alert_system, AlertLevel
from lcars.ui.panels.bridge import WelcomeScreen

logger = logging.getLogger("lcars.ui.desktop")
# Клас `LockScreen` — екран блокування поверх десктопа.
# Відповідає за відображення затемнення, тексту безпеки та кнопки відновлення доступу.
class LockScreen(QWidget):
    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.parent_obj = parent
        self.setStyleSheet("background-color: rgba(0, 0, 0, 240);")
        self.setVisible(False)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        alerts = self.theme.get("alerts", ["#FFCC33", "#D80000"])
        accent = self.theme.get("accent", "#FFCC33")
        
        lbl = QLabel("◢ SECURITY LOCK")
        lbl.setStyleSheet(f"color: {alerts[1] if len(alerts) > 1 else '#FF3333'}; {get_lcars_font_style(36, 'normal')}")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn = LCARSButton("RESTORE ACCESS", accent, shape="pill")
        btn.setFixedSize(260, 60)
        btn.clicked.connect(self.hide)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def show_lock(self):
        if self.parent_obj:
            self.setGeometry(self.parent_obj.rect())
        self.raise_()
        self.setVisible(True)

class RandomDynamicPanel(QFrame):
    # Динамічна анімована панель з блоками даних.
    # Використовується для демонстрації змінних телеметричних значень,
    # таймер випадково оновлює один з блоків.
    def __init__(self, theme, era, faction, parent=None, vertical=True):
        super().__init__(parent)
        self.theme = theme
        self.lcars_palette = theme.get("palette", ["#3366CC"] * 10)
        self.era = era
        self.faction = faction
        layout = QVBoxLayout(self) if vertical else QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(8)
        
        self.blocks = []
        for i in range(4):
            color = random.choice(self.lcars_palette)
            db = DataBlock(f"LINK-{random.randint(10, 99)}", "STABLE", color)
            db.setFixedHeight(35)
            layout.addWidget(db)
            self.blocks.append(db)
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._randomize)
        self.timer.start(3000)

    def _randomize(self):
        if self.blocks and random.random() > 0.5:
            block = random.choice(self.blocks)
            block.set_value(f"0x{random.randint(1000, 9999):X}")

class LCARSDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        from lcars.core.board_computer import get_computer
        self.computer = get_computer()
        self.event_bus = self.computer.event_bus
        
        self.era = LCARSEra.LCARS_25TH
        self.faction = None
        self.theme = get_theme(self.era)
        self.accent = self.theme.get("accent", "#FFCC66")
        self.secondary = self.theme.get("secondary", self.accent)
        # Track alert state explicitly
        self.alert_state = False
        # Listen to central alert system to update UI elements
        alert_system.alert_changed.connect(self._on_alert_changed)
        
        self.setWindowTitle("LCARS PRIMARY OPERATING SYSTEM")
        # Make the desktop a single fullscreen, frameless host window
        # so all panels are embedded within it (no OS titlebar).
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: black;")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.setup_ui_containers()
        self._start_timers()
        # Ensure desktop occupies the full screen as the host canvas.
        self.showFullScreen()

    def setup_ui_containers(self):
        # Побудова базової скелетної структури десктопа: header/body/footer
        # Контейнери створюються як layout-об'єкти; конкретні віджети додаються пізніше.
        # Header Container
        self.header_layout_container = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout_container)
        
        # Body Container
        self.body_layout_container = QHBoxLayout()
        self.body_layout_container.setSpacing(5)
        self.main_layout.addLayout(self.body_layout_container, 1)
        
        # Footer Container
        self.footer_layout_container = QHBoxLayout()
        self.main_layout.addLayout(self.footer_layout_container)
        
        # Overlays
        # Use our new Onboard Computer Drawer
        self.drawer = OnboardComputerDrawer(self, self.era, self.faction)
        self.lock_screen = LockScreen(self.theme, self)
        self.start_menu = None
        # Subscribe to global alert system updates
        alert_system.alert_changed.connect(self._on_alert_changed)
        # initialize current alert state immediately
        self._on_alert_changed(int(alert_system.level))

    # NOTE: alert updates handled in single consolidated handler below

    def _on_alert_changed(self, level_val: int):
        # Обробник глобальних змін тривоги (alert): оновлює кнопки та контури
        # для відображення поточного рівня тривоги. Не змінює фон десктопа.
        # Ensure the provided value maps to a known AlertLevel; let unexpected values be ignored
        if not any(member.value == level_val for member in AlertLevel):
            return
        lev = AlertLevel(level_val)

        # Map AlertLevel to simple names expected by widgets
        # Map known AlertLevel members to widget-friendly names.
        name_map = {
            AlertLevel.NORMAL: "NORMAL",
            AlertLevel.YELLOW: "YELLOW",
            AlertLevel.RED: "RED",
        }
        level_name = name_map.get(lev, "NORMAL")

        # Update all LCARSButton-like widgets that support update_alert_level
        # (Assume LCARSButton/LCARSElbow/LCARSContour are available via top-level imports)
        for btn in self.findChildren(LCARSButton):
            btn.update_alert_level(level_name)

        for w in self.findChildren(LCARSElbow):
            w.update_alert_level(level_name)
    def setup_desktop(self, faction_name: str, era_name: str):
        # Ініціалізація теми та повного інтерфейсу для заданої фракції/епохи.
        # Встановлює `self.era`, `self.faction`, підвантажує тему та запуск
        # опціонального екрану завантаження (splash). Після завантаження викликає `init_ui()`.
        f_map = {"FEDERATION": None, "KLINGON": FactionEra.KLINGON, "ROMULAN": FactionEra.ROMULAN, "CARDASSIAN": FactionEra.CARDASSIAN}
        era_map = {"22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST, 
                   "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}
        
        self.era = era_map.get(era_name.lower(), LCARSEra.LCARS_25TH)
        self.faction = f_map.get(faction_name.upper())
        self.theme = get_theme(self.era, self.faction)
        self.accent = self.theme.get("accent", "#FFCC66")
        self.secondary = self.theme.get("secondary", self.accent)
        
        # Optional boot splash: show a brief loading screen unless explicitly skipped
        skip_splash = os.environ.get("LCARS_SKIP_SPLASH") == "1"
        if not skip_splash:       
                self._loading = LCARSLoadingScreen(self.era)
                # When loading finishes, initialize the main UI
                self._loading.loading_finished.connect(lambda: (self.init_ui(), self.computer.sounds.play("ready")))
                self._loading.show()
                # Fallback to direct init if loading screen fails
                logger.exception("Loading screen failed, falling back to direct UI init")
                self.init_ui()
                self.computer.sounds.play("ready")
        else:
            self.init_ui()
            self.computer.sounds.play("ready")

    def init_ui_22nd(self):
        # Альтернативна розкладка інтерфейсу: стиль 22-го сторіччя (NX-01).
        # Тут побудовано заголовок, бічну панель та viewport з наборами віджетів,
        # специфічними для цього режиму.
        def clear_layout(layout):
            if not layout: return
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()
                elif item.layout(): clear_layout(item.layout())
        
        clear_layout(self.header_layout_container)
        clear_layout(self.body_layout_container)
        clear_layout(self.footer_layout_container)
        
        # --- HEADER 22nd ---
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(60)
        self.header_frame.setStyleSheet("background: #5C5C5C; border-bottom: 3px solid #CCCCCC;")
        h_lay = QHBoxLayout(self.header_frame)
        h_lay.setContentsMargins(20, 0, 20, 0)
        
        lbl_head = QLabel(f"◢ NX-01 PRIMARY SYSTEMS // {self.era.value.upper()} CENTURY")
        lbl_head.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}")
        h_lay.addWidget(lbl_head)
        h_lay.addStretch()
        
        btn_exit = LCARSButton("EXIT", "#CE6363", era=self.era)
        btn_exit.setFixedSize(120, 40)
        btn_exit.clicked.connect(self.close)
        h_lay.addWidget(btn_exit)
        self.header_layout_container.addWidget(self.header_frame, 1)

        # --- BODY 22nd (Sidebar + Viewport) ---
        sidebar_lay = QVBoxLayout()
        sidebar_lay.setContentsMargins(10, 20, 10, 20)
        sidebar_lay.setSpacing(10)
        
        p = self.theme.get("palette", ["#CCCCCC"] * 10)
        apps = [
            ("CONSOLE", 0, self.show_console), 
            ("PROJECTS", 1, self.show_explorer), 
            ("STORAGE", 2, self.show_storage),
            ("MONITOR", 3, self.show_monitor), 
            ("ENGINEERING", 4, self.show_engineering)
        ]
        for text, idx, func in apps:
            btn = LCARSButton(text, p[idx % len(p)], era=self.era, shape="rect")
            btn.setFixedSize(180, 55)
            btn.clicked.connect(func)
            sidebar_lay.addWidget(btn)
        sidebar_lay.addStretch()
        
        self.btn_access_22 = LCARSButton("SYSTEM ACCESS", "#269EEE", era=self.era, shape="rect")
        self.btn_access_22.setFixedSize(180, 45)
        self.btn_access_22.clicked.connect(self.open_start_menu)
        sidebar_lay.addWidget(self.btn_access_22)
        
        self.body_layout_container.addLayout(sidebar_lay)

        # Content 22nd
        self.viewport = QFrame()
        self.viewport.setStyleSheet("background: black; border: 2px solid #5C5C5C;")
        v_lay = QVBoxLayout(self.viewport)
        self.stack = QStackedWidget()
        self.console_view = ConsoleView(self.event_bus, self.era, self.faction)
        self.project_view = ProjectExplorerView(self.era, self.faction, self)
        self.storage_view = StoragePanel(self.computer, self.era, self.faction)
        self.programs_view = ProgramsView(self, self.era, self.faction)
        self.stack.addWidget(self.console_view)
        self.stack.addWidget(self.engineering_view)
        self.stack.addWidget(self.project_view)
        self.stack.addWidget(self.storage_view)
        self.stack.addWidget(self.programs_view)
        self.body_layout_container.addWidget(self.viewport, 1)
        self.footer_frame = QFrame()
        self.footer_frame.setFixedHeight(40)
        self.footer_frame.setStyleSheet("background: #333333; border-top: 2px solid #5C5C5C;")
        f_lay = QHBoxLayout(self.footer_frame)
        f_lay.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet(f"color: white; {get_lcars_font_style(16, 'normal')}")
        f_lay.addWidget(self.lbl_clock)
        f_lay.addStretch()
        
        self.footer_layout_container.addWidget(self.footer_frame, 1)

    def init_ui(self):
        # Побудова основного інтерфейсу для поточної `era`/`faction`.
        # Очищує попередні layout-и та створює header, sidebar, viewport,
        # стеки віджетів (views) та інтегрує WelcomeScreen у стек.
        if self.era == LCARSEra.COMS_22ND:
            return self.init_ui_22nd()
            
        def clear_layout(layout):
            if not layout: return
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()
                elif item.layout(): clear_layout(item.layout())
        
        clear_layout(self.header_layout_container)
        clear_layout(self.body_layout_container)
        clear_layout(self.footer_layout_container)
        
        # Re-init overlays with new theme
        if hasattr(self, 'drawer') and self.drawer: self.drawer.deleteLater()
        if hasattr(self, 'lock_screen') and self.lock_screen: self.lock_screen.deleteLater()
        self.drawer = OnboardComputerDrawer(self, self.era, self.faction)
        self.lock_screen = LockScreen(self.theme, self)
        p = self.theme.get("palette", ["#3366CC"] * 10)
        
        # --- HEADER (Clean Industrial Style) ---
        header_bar = QFrame()
        header_bar.setMinimumHeight(60)
        header_bar.setStyleSheet(f"background: #111; border-bottom: 2px solid {self.accent}; padding:6px 8px;")
        h_outer_lay = QHBoxLayout(header_bar)
        h_outer_lay.setContentsMargins(10, 5, 10, 5)
        
        self.lbl_title = QLabel(f"◢ LCARS PRIMARY CONSOLE // {self.era.value.upper()}")
        self.lbl_title.setStyleSheet(f"color: {p[1]}; {get_lcars_font_style(20, 'bold')}")
        h_outer_lay.addWidget(self.lbl_title)
        h_outer_lay.addStretch()
        
        self.btn_nav_toggle = LCARSButton("NAV", self.secondary, shape="pill")
        self.btn_nav_toggle.setMinimumSize(90, 24)

        self.btn_nav_toggle.clicked.connect(self.toggle_sidebar)
        h_outer_lay.addWidget(self.btn_nav_toggle)

        # BUTTON 1: BRIDGE (shows Welcome/Bridge interface)
        self.btn_sys = LCARSButton("BRIDGE", p[2], shape="rect")
        self.btn_sys.setMinimumSize(120, 40)
        self.btn_sys.clicked.connect(self.show_bridge)
        h_outer_lay.addWidget(self.btn_sys)

        # BUTTON 2: ALERT (header alert indicator) — toggles alert state
        self.btn_alert = LCARSButton("ALERT", p[2], shape="rect")
        self.btn_alert.setMinimumSize(120, 40)
        self.btn_alert.clicked.connect(self.toggle_alert)
        h_outer_lay.addWidget(self.btn_alert)
        
        self.header_layout_container.addWidget(header_bar, 1)
        # --- DEFAULT SIDEBAR + VIEWPORT ---
        # Create a standard sidebar and viewport so the desktop is not empty by default
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setMinimumWidth(200)
        self.sidebar_frame.setStyleSheet(f"background: transparent; border-right: 1px solid {self.accent}44; padding:6px;")
        sidebar_lay = QVBoxLayout(self.sidebar_frame)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(5)

        self.scan_bar = ScanningBar(self.accent, faction=self.faction)
        self.scan_bar.setMinimumWidth(40)
        sb_inner = QHBoxLayout()
        sb_inner.addWidget(self.scan_bar)

        nav_box = QVBoxLayout()
        apps = [
            ("CONSOLE", 0, self.show_console),
            ("PROJECTS", 1, self.show_explorer),
            ("STORAGE", 2, self.show_storage),
            ("MONITOR", 3, self.show_monitor),
            ("ENGINEERING", 4, self.show_engineering),
        ]
        for text, idx, func in apps:
            btn = LCARSButton(text, p[idx % len(p)], era=self.era, faction=self.faction, shape="right")
            btn.setMinimumHeight(45)
            btn.clicked.connect(func)
            nav_box.addWidget(btn)
        nav_box.addStretch()

        # CPU/MEM Meters
        self.cpu_meter = StatBar("CPU", p[0], faction=self.faction)
        self.mem_meter = StatBar("MEM", p[1], faction=self.faction)
        nav_box.addWidget(self.cpu_meter)
        nav_box.addWidget(self.mem_meter)

        sb_inner.addLayout(nav_box)
        sidebar_lay.addLayout(sb_inner)

        spacer = QWidget()
        spacer.setMinimumHeight(20)
        sidebar_lay.addWidget(spacer)

        self.body_layout_container.addWidget(self.sidebar_frame)

        # Viewport
        self.viewport = QFrame()
        self.viewport.setStyleSheet(f"background: #000; border-left: 1px solid {self.accent}22; border-radius:6px; padding:8px;")
        v_lay = QVBoxLayout(self.viewport)
        v_lay.setContentsMargins(12, 12, 12, 12)

        self.stack = QStackedWidget()
        self.console_view = ConsoleView(self.event_bus, self.era, self.faction)
        self.engineering_view = EngineeringView(self.computer, self.era, self.faction, self)
        # Welcome screen (integrated Bridge welcome) — shown on startup instead of console
        self.welcome_view = WelcomeScreen(self.event_bus, self.era, self.faction, parent=self)
        self.project_view = ProjectExplorerView(self.era, self.faction, self)
        self.storage_view = StoragePanel(self.computer, self.era, self.faction)
        self.programs_view = ProgramsView(self, self.era, self.faction)

        self.stack.addWidget(self.console_view)
        self.stack.addWidget(self.engineering_view)
        self.stack.addWidget(self.welcome_view)
        self.stack.addWidget(self.project_view)
        self.stack.addWidget(self.storage_view)
        self.stack.addWidget(self.programs_view)

        # Start with WelcomeScreen; console remains available via button
        self.stack.setCurrentWidget(self.welcome_view)

        v_lay.addWidget(self.stack)
        self.body_layout_container.addWidget(self.viewport, 1)

    def show_system_control(self):
        # Відкрити комплексний інтерфейс System Control Center як fullscreen QWidget.
        from lcars.ui.system import SystemControlCenter
        self.sys_ctrl = SystemControlCenter(self, self.era, self.faction)
        self.sys_ctrl.show() # Changed from exec() to show() because it's now a fullscreen QWidget

    def show_bridge(self):
        # Переключити viewport на інтегрований екран Bridge/Welcome.
        if hasattr(self, 'welcome_view'):
            self.stack.setCurrentWidget(self.welcome_view)
            self.computer.sounds.play('acknowledge')

    def show_power_menu(self):
        # Відкрити меню живлення/системні параметри через `SystemMenu`.
        from lcars.ui.system import SystemMenu
        self.pwr_menu = SystemMenu(self, self.era, self.faction)
        self.pwr_menu.exec()
        p = self.theme.get("palette", ["#3366CC"] * 10)
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(200)
        self.sidebar_frame.setStyleSheet(f"background: transparent; border-right: 1px solid {self.accent}44;")
        sidebar_lay = QVBoxLayout(self.sidebar_frame)
        sidebar_lay.setContentsMargins(0, 0, 0, 0)
        sidebar_lay.setSpacing(5)
        
        self.scan_bar = ScanningBar(self.accent, faction=self.faction)
        self.scan_bar.setFixedWidth(40)
        sb_inner = QHBoxLayout()
        sb_inner.addWidget(self.scan_bar)
        
        nav_box = QVBoxLayout()
        apps = [
            ("CONSOLE", 0, self.show_console), 
            ("PROJECTS", 1, self.show_explorer), 
            ("STORAGE", 2, self.show_storage),
            ("MONITOR", 3, self.show_monitor), 
            ("ENGINEERING", 4, self.show_engineering)
        ]
        for text, idx, func in apps:
            btn = LCARSButton(text, p[idx % len(p)], era=self.era, faction=self.faction, shape="right")
            btn.setMinimumHeight(45)
            btn.clicked.connect(func)
            nav_box.addWidget(btn)
        
        nav_box.addStretch()
        
        # CPU/MEM Meters
        self.cpu_meter = StatBar("CPU", p[0], faction=self.faction)
        self.mem_meter = StatBar("MEM", p[1], faction=self.faction)
        nav_box.addWidget(self.cpu_meter)
        nav_box.addWidget(self.mem_meter)
        
        sb_inner.addLayout(nav_box)
        sidebar_lay.addLayout(sb_inner)
        
        # NO ELBOWS in industrial mode
        spacer = QWidget()
        spacer.setFixedHeight(20)
        sidebar_lay.addWidget(spacer)
        
        self.body_layout_container.addWidget(self.sidebar_frame)
        
        # Viewport
        self.viewport = QFrame()
        self.viewport.setStyleSheet(f"background: black; border-left: 1px solid {self.accent}22;")
        v_lay = QVBoxLayout(self.viewport)
        v_lay.setContentsMargins(10, 10, 10, 10)
        
        self.stack = QStackedWidget()
        self.console_view = ConsoleView(self.event_bus, self.era, self.faction)
        self.engineering_view = EngineeringView(self.computer, self.era, self.faction, self)
        self.project_view = ProjectExplorerView(self.era, self.faction, self)
        self.storage_view = StoragePanel(self.computer, self.era, self.faction)
        self.programs_view = ProgramsView(self, self.era, self.faction)
        
        self.stack.addWidget(self.console_view)
        self.stack.addWidget(self.engineering_view)
        self.stack.addWidget(self.project_view)
        self.stack.addWidget(self.storage_view)
        self.stack.addWidget(self.programs_view)
        
        v_lay.addWidget(self.stack)
        self.body_layout_container.addWidget(self.viewport, 1)

        # --- FOOTER (Clean Style) ---
        footer_bar = QFrame()
        footer_bar.setMinimumHeight(45)
        footer_bar.setStyleSheet(f"background: #0b0b0b; border-top: 2px solid {self.secondary}; padding:6px 10px;")
        f_inner = QHBoxLayout(footer_bar)
        f_inner.setContentsMargins(20, 0, 20, 0)
        
        self.btn_access = LCARSButton("SYSTEM ACCESS", p[0], shape="rect")
        self.btn_access.setFixedSize(160, 30)
        self.btn_access.clicked.connect(self.open_start_menu)
        f_inner.addWidget(self.btn_access)
        
        status_lbl = QLabel("◢ STATUS: NOMINAL")
        status_lbl.setStyleSheet(f"color: {self.secondary}; {get_lcars_font_style(14, 'normal')}")
        f_inner.addWidget(status_lbl)
        
        f_inner.addStretch()
        
        self.lbl_clock = QLabel("00:00:00")
        self.lbl_clock.setStyleSheet(f"color: {p[1]}; {get_lcars_font_style(20, 'normal')}")
        f_inner.addWidget(self.lbl_clock)
        
        self.footer_layout_container.addWidget(footer_bar, 1)
        
    def toggle_sidebar(self):
        # Перемкнути видимість бічної навігаційної панелі та оновити текст кнопки.
        visible = self.sidebar_frame.isVisible()
        self.sidebar_frame.setVisible(not visible)
        self.btn_nav_toggle.setText("NAV ○" if visible else "NAV ●")
        self.computer.sounds.play("acknowledge")

    def _start_timers(self):
        # Запустити внутрішні таймери: годинник і періодичне оновлення UI.
        self.t_clock = QTimer(self)
        self.t_clock.timeout.connect(self._update_ui)
        self.t_clock.start(1000)

    def _update_ui(self):
        # Поточне оновлення UI: оновлення годинника, метрів CPU/MEM тощо.
        if hasattr(self, 'lbl_clock'): self.lbl_clock.setText(datetime.now().strftime("%H:%M:%S"))
        cpu = psutil.cpu_percent()
        if isinstance(cpu, (list, tuple)): cpu = cpu[0]
        mem = psutil.virtual_memory().percent
        if hasattr(self, 'cpu_meter'): self.cpu_meter.setValue(int(cpu))
        if hasattr(self, 'mem_meter'): self.mem_meter.setValue(int(mem))
        # self.drawer does not have cpu_stat/mem_stat attributes; skip these lines
    def show_console(self): self.stack.setCurrentWidget(self.console_view)
    def show_explorer(self): self.stack.setCurrentWidget(self.project_view)
    def show_storage(self): self.stack.setCurrentWidget(self.storage_view)
    def show_programs(self): self.stack.setCurrentWidget(self.programs_view)
    def show_monitor(self): self.drawer.toggle()
    def show_engineering(self): self.stack.setCurrentWidget(self.engineering_view)
    
    def show_security_override(self):
        """Invoke critical system command menu."""
        self.sec_menu = SystemMenu(self, era=self.era, faction=self.faction)
        self.sec_menu.exec()

    def show_bios(self):
        """Open BIOS/System parameters configuration."""
        self.bios = BIOSDialog(self)
        self.bios.exec()

    def show_settings(self):
        """Open settings interface (Restricted level 10)."""
        get_sound_manager().play("deny")
        logger.info("◤ CONFIG_INTERFACE: ACCESS RESTRICTED")

    def toggle_alert(self):
        # Delegate alert cycling to central alert system which will emit changes
        alert_system.next_level()

    def open_start_menu(self):
        # Create start menu if needed
        if not self.start_menu:
            self.start_menu = AccessMenu(era=self.era, faction=self.faction, parent=self)

        # Prefer bottom-left placement (user request): offset from left and bottom edges
        d_rect = self.rect()
        w = 700
        h = 420
        x = 20
        y = d_rect.height() - h - 20
        if y < 20: y = 20
        self.start_menu.setGeometry(x, y, w, h)
        self.start_menu.show()
        self.start_menu.raise_()
        get_sound_manager().play("acknowledge")

    def keyPressEvent(self, a0):
        if a0 and a0.key() == Qt.Key.Key_F1: self.open_start_menu()
        super().keyPressEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Allow direct desktop start when script is invoked with --direct
    # or when env var LCARS_DIRECT_DESKTOP=1 is set. Otherwise fall back to
    # the launcher flow to require user confirmation.
    direct = "--direct" in sys.argv or os.environ.get("LCARS_DIRECT_DESKTOP") == "1"
    if direct:
        desktop = LCARSDesktop()
        # Default to Federation/25th when run directly
        desktop.setup_desktop('Federation', '25th')
        desktop.show()
        sys.exit(app.exec())
    else:
        from lcars.ui.launcher import LCARSLauncher
        launcher = LCARSLauncher()
        launcher.show()
        sys.exit(app.exec())
