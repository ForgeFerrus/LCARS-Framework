# LCARS: ГОЛОВНИЙ ІНТЕРФЕЙС ДЕСКТОПА
# Система: 25.04.02 (TITAN ARCHITECTURE / CLEAN RESTORATION)
# Авторизація: Рівень 10 (ADMIRAL) // U.S.S. TITAN-A / ODYSSEY
# Протокол безпеки: EPSILON-9-THETA
# Опис: Головний інтерфейс LCARS для управління заголовком, бічною навігацією,
#       динамічними вікнами перегляду та телеметрією. Файл містить основне
#       вікно-десктоп, вбудовані панелі та логіку реакції на глобальні події.
import importlib
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

from lcars.themes.palette import LCARSEra, FactionEra, GetRandomButtonColor
from lcars.themes.theme import GetTheme, GetLcarsFontStyle, setup_lcars_font
from lcars.base.component import (LCARSButton, ScanningBar, StatBar,
    DataBlock, LCARSElbow,
)

# expose board computer accessor at module level for testing and convenience
from lcars.core.board_computer import get_computer
# Імпорти для десктопу (loading_screen видалено - тепер в system/initialization.py)
from lcars.ui.panels.console_panel import ConsolePanel as ConsoleView
from programs.engineering_view import EngineeringView
from programs.project_explorer import ProjectExplorerView
from lcars.ui.panels.programs import ProgramsPanel as ProgramsView
from lcars.ui.views.system_access import AccessMenu
# from lcars.ui.views.copilot import CopilotView # TODO: Verify path
# Оновлено: вказано на новий повний інтерфейс SystemControlCenter (псевдонім SystemMenu)
from lcars.ui.system import SystemControlCenter
from lcars.system.bios import BIOSDialog
from lcars.ui.panels.storage import StoragePanel
from lcars.ui.onboard import OnboardComputerDrawer
from lcars.ui.panel_manager import PanelManager
from lcars.modules.sound_manager import GetSoundManager
from lcars.system.alert import alert_system, AlertLevel
from lcars.modules.config_manager import config_manager
from lcars.system import hotkeys

logger = logging.getLogger("lcars.ui.desktop")

# Клас LockScreen — екран блокування поверх десктопа.
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

        lbl = QLabel("SECURITY LOCK")
        lbl.setStyleSheet(f"color: {alerts[1] if len(alerts) > 1 else '#FF3333'}; {GetLcarsFontStyle(36, 'normal')}")
        layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        btn = LCARSButton("RESTORE ACCESS", accent, shape="pill")
        btn.setFixedSize(260, 60)
        btn.clicked.connect(self.hide)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    # Показати екран блокування поверх батьківського вікна
    def ShowLock(self):
        if self.parent_obj:
            self.setGeometry(self.parent_obj.rect())
        self.raise_()
        self.setVisible(True)


# Клас LCARSDesktop — головне вікно десктопа LCARS.
class LCARSDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        # get_computer is imported at module level now
        self.computer = get_computer()
        self.event_bus = self.computer.event_bus
        # Register this desktop with the BoardComputer so created panels can be embedded
        self.computer.register_desktop(self, add_widget_callback=self.DesktopAddWidget)

        # Load initial theme from config, with fallback to defaults
        initial_era_str = config_manager.get('app', 'era', '25th')
        initial_faction_str = config_manager.get('app', 'faction', 'FEDERATION')

        f_map = {"FEDERATION": None, "KLINGON": FactionEra.KLINGON, "ROMULAN": FactionEra.ROMULAN, "CARDASSIAN": FactionEra.CARDASSIAN}
        era_map = {"22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST,
                   "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}

        self.era = era_map.get(initial_era_str.lower(), LCARSEra.LCARS_25TH)
        self.faction = f_map.get(initial_faction_str.upper())
        self.theme = GetTheme(self.era, self.faction)

        from lcars.system.color import COLOR_MANAGER
        COLOR_MANAGER.set_context(self.era, self.faction)
        self.accent = COLOR_MANAGER.next_color()
        self.secondary = COLOR_MANAGER.next_color()
        # legacy generator removed, use central COLOR_MANAGER
        self.color_gen = COLOR_MANAGER
        # Відстеження стану тривоги (alert) явно
        self.alert_state = False
        # Listen to central alert system to update UI elements
        alert_system.alert_changed.connect(self.OnAlertChanged)

        # Watch for theme changes in config
        config_manager.watch('app', 'era', lambda n, k, o, nv: self.OnThemeConfigChanged(n, k, o, nv))
        config_manager.watch('app', 'faction', lambda n, k, o, nv: self.OnThemeConfigChanged(n, k, o, nv))
        # Watch for language changes so desktop can retranslate
        config_manager.watch('app', 'language', lambda n, k, o, nv: self.OnLanguageConfigChanged(n, k, o, nv))

        # initialize language from config as early as possible
        from lcars.system.localization import LOCALIZATION as Language
        initial_lang = config_manager.get('app', 'language', 'en')
        Language.SetLanguage(initial_lang)
        # register for future updates in case any desktop labels need changing
        Language.RegisterCallback(self.RetranslateDesktop)

        self.setWindowTitle("LCARS PRIMARY OPERATING SYSTEM")
        # Робимо десктоп єдиним повноекранним хостом без рамки
        # — усі панелі вбудовані в цей віконний контейнер (без системного заголовку).
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        from lcars.system.hotkeys import HotkeyManager
        self.hotkeys = HotkeyManager(self)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background-color: black;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.SetupUiContainers()
        self.StartTimers()
        # Prepare periodic color timer (started after full UI init)
        self.ColorTimer = QTimer(self)
        self.ColorTimer.timeout.connect(GetRandomButtonColor)
        # Ensure desktop occupies the full screen as the host canvas.
        self.showFullScreen()

    # Побудова базової скелетної структури десктопа: header/body/footer
    def SetupUiContainers(self):
        # Контейнер заголовку
        self.header_layout_container = QHBoxLayout()
        self.main_layout.addLayout(self.header_layout_container)

        # Контейнер вмісту (тіло)
        self.body_layout_container = QHBoxLayout()
        self.body_layout_container.setSpacing(5)
        self.main_layout.addLayout(self.body_layout_container, 1)

        # Контейнер підвалу (footer)
        self.footer_layout_container = QHBoxLayout()
        self.main_layout.addLayout(self.footer_layout_container)

        # Оверлеї
        # Panel manager: host for embedded slide-out panels (Onboard, tools, etc.)
        self.panel_manager = PanelManager(self, width=420)
        # ensure panel manager is part of layout (added later in InitUi alongside viewport)
        self.lock_screen = LockScreen(self.theme, self)
        self.start_menu = None
        # Subscribe to global alert system updates
        alert_system.alert_changed.connect(self.OnAlertChanged)
        # initialize current alert state immediately
        self.OnAlertChanged(int(alert_system.level))

    # ПРИМІТКА: оновлення тривог обробляються в єдиному консолідованому хендлері нижче

    # Обробник глобальних змін тривоги (alert): оновлює вигляд кнопок та контурів
    # відповідно до поточного рівня тривоги. Фон десктопа не змінюється тут.
    def OnAlertChanged(self, level_val: int):
        # Ensure the provided value maps to a known AlertLevel; let unexpected values be ignored
        if not any(member.value == level_val for member in AlertLevel):
            return
        lev = AlertLevel(level_val)

        # Відобразити AlertLevel у прості імена, які очікують віджети
        # (мапування відомих членів AlertLevel до дружніх назв).
        name_map = {
            AlertLevel.NORMAL: "NORMAL",
            AlertLevel.YELLOW: "YELLOW",
            AlertLevel.RED: "RED",
        }
        level_name = name_map.get(lev, "NORMAL")

        # Оновити всі віджети типу LCARSButton, які підтримують update_alert_level,
        # і застосувати окрему палітру для кожного рівня тривоги для кращої видимості.
        # allow overrides from configuration
        from lcars.modules.config_manager import config_manager
        cfg_colors = config_manager.get('ui', 'colors', {}) or {}
        color_map = {
            AlertLevel.NORMAL: cfg_colors.get('alert_normal', self.theme.get('secondary', self.accent)),
            AlertLevel.YELLOW: cfg_colors.get('alert_yellow', '#FFCC33'),
            AlertLevel.RED: cfg_colors.get('alert_red', '#CC0000'),
        }
        color = color_map.get(lev, self.theme.get('secondary', self.accent))

        for btn in self.findChildren(LCARSButton):
            if hasattr(btn, 'update_alert_level'):
                btn.update_alert_level(level_name)
            if hasattr(btn, 'setStyleSheet'):
                btn.setStyleSheet(f"background: {color};")

        for w in self.findChildren(LCARSElbow):
            if hasattr(w, 'update_alert_level'):
                w.update_alert_level(level_name)
            if hasattr(w, 'setStyleSheet'):
                w.setStyleSheet(f"background: {color};")

        # show lock screen when red alert, hide otherwise
        if lev == AlertLevel.RED and hasattr(self, 'lock_screen'):
            self.lock_screen.ShowLock()
        elif lev != AlertLevel.RED and hasattr(self, 'lock_screen') and self.lock_screen.isVisible():
            self.lock_screen.hide()

        # apply any desktop-level palette changes
        self.ApplyAlertPalette(lev)

    # Ініціалізація теми та повного інтерфейсу для заданої фракції/епохи.
    def SetupDesktop(self, faction_name: str, era_name: str):
        f_map = {"FEDERATION": None, "KLINGON": FactionEra.KLINGON, "ROMULAN": FactionEra.ROMULAN, "CARDASSIAN": FactionEra.CARDASSIAN}
        era_map = {"22nd": LCARSEra.COMS_22ND, "23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST,
                   "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}
        self.era = era_map.get(era_name.lower(), LCARSEra.LCARS_25TH)
        self.faction = f_map.get(faction_name.upper())
        self.theme = GetTheme(self.era, self.faction)

        from lcars.system.color import COLOR_MANAGER
        COLOR_MANAGER.set_context(self.era, self.faction)
        self.accent = COLOR_MANAGER.next_color()
        self.secondary = COLOR_MANAGER.next_color()
        # Skip splash - ініціалізація тепер в system/initialization.py
        # Пряма ініціалізація інтерфейсу
        self.InitUi()
        self.computer.sounds.play("ready")

    # Альтернативна розкладка інтерфейсу: стиль 22-го сторіччя (NX-01).
    def InitUi22nd(self):
        def ClearLayout(layout):
            if not layout: return
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()
                elif item.layout(): ClearLayout(item.layout())

        ClearLayout(self.header_layout_container)
        ClearLayout(self.body_layout_container)
        ClearLayout(self.footer_layout_container)

        # --- HEADER 22nd ---
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(60)
        self.header_frame.setStyleSheet("background: #5C5C5C; border-bottom: 3px solid #CCCCCC;")
        h_lay = QHBoxLayout(self.header_frame)
        h_lay.setContentsMargins(20, 0, 20, 0)

        lbl_head = QLabel(f"NX-01 PRIMARY SYSTEMS // {self.era.value.upper()} CENTURY")
        lbl_head.setStyleSheet(f"color: white; {GetLcarsFontStyle(20, 'normal')}")
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
            ("CONSOLE", 0, self.ShowConsole),
            ("BROWSER", 2, self.ShowBrowser),
            ("HEALTH", 3, self.ShowHealthcheck),
            ("SYSTEM", 4, self.ShowSystemControl),
            ("SETTINGS", 5, self.ShowSettings),
        ]
        for text, idx, func in apps:
            btn = LCARSButton(text, p[idx % len(p)], era=self.era, shape="rect")
            btn.setFixedSize(180, 55)
            btn.clicked.connect(func)
            sidebar_lay.addWidget(btn)
        sidebar_lay.addStretch()

        self.btn_access_22 = LCARSButton("SYSTEM ACCESS", "#269EEE", era=self.era, shape="rect")
        self.btn_access_22.setFixedSize(180, 45)
        self.btn_access_22.clicked.connect(self.OpenStartMenu)
        sidebar_lay.addWidget(self.btn_access_22)

        self.body_layout_container.addLayout(sidebar_lay)

    # Побудова основного інтерфейсу для поточної era/faction.
    def InitUi(self):
        if self.era == LCARSEra.COMS_22ND:
            return self.InitUi22nd()

        def ClearLayout(layout):
            if not layout: return
            while layout.count():
                item = layout.takeAt(0)
                if item.widget(): item.widget().deleteLater()
                elif item.layout(): ClearLayout(item.layout())

        ClearLayout(self.header_layout_container)
        ClearLayout(self.body_layout_container)
        ClearLayout(self.footer_layout_container)

        # create panel manager container if not present
        if not hasattr(self, 'panel_manager') or self.panel_manager is None:
            self.panel_manager = PanelManager(self, width=420)

        p = self.theme.get("palette", ["#3366CC"] * 10)

        header_bar = QFrame()
        header_bar.setMinimumHeight(60)
        header_bar.setStyleSheet(f"background: #111; border-bottom: 2px solid {self.accent}; padding:6px 8px;")
        h_outer_lay = QHBoxLayout(header_bar)
        h_outer_lay.setContentsMargins(10, 5, 10, 5)

        # Ініціалізація бортового комп'ютера та оверлеїв
        if hasattr(self, 'lock_screen') and self.lock_screen: self.lock_screen.deleteLater()

        # Instantiate Onboard drawer in embedded mode and register it
        self.onboard_drawer = OnboardComputerDrawer(self, era=self.era, faction=self.faction, width=420, mode='embedded')
        # register onboard drawer
        self.panel_manager.register_panel('onboard', self.onboard_drawer)
        # Register System Utilities panel (embed tools/system_utilities) if available
        # Перевірка наявності модуля SystemUtilitiesPanel перед імпортом
        _su_spec = importlib.util.find_spec('lcars.system.system_utilities')
        if _su_spec is not None:
            from lcars.system.system_utilities import SystemUtilitiesPanel
            utils_panel = SystemUtilitiesPanel(parent=self.panel_manager.container)
            self.panel_manager.register_panel('system_utils', utils_panel)
            # add a header button to open the panel
            btn_utils = LCARSButton("UTILS", self.accent, shape="rect")
            btn_utils.setMinimumSize(120, 40)
            btn_utils.clicked.connect(lambda: self.panel_manager.show_panel('system_utils'))
            h_outer_lay.addWidget(btn_utils)
        # Add panel manager container to the body layout (right side)
        self.body_layout_container.addWidget(self.panel_manager.container)
        self.lock_screen = LockScreen(self.theme, self)

        self.lbl_title = QLabel(f"LCARS PRIMARY CONSOLE // {self.era.value.upper()}")
        self.lbl_title.setStyleSheet(f"color: {p[1]}; {GetLcarsFontStyle(20, 'bold')}")
        h_outer_lay.addWidget(self.lbl_title)
        h_outer_lay.addStretch()

        self.btn_nav_toggle = LCARSButton("NAV", self.secondary, shape="pill")
        self.btn_nav_toggle.setMinimumSize(90, 24)

        self.btn_nav_toggle.clicked.connect(self.ToggleSidebar)
        h_outer_lay.addWidget(self.btn_nav_toggle)

        # BUTTON 1: BRIDGE (shows Welcome/Bridge interface)
        self.btn_sys = LCARSButton("BRIDGE", p[2], shape="rect")
        self.btn_sys.setMinimumSize(120, 40)
        self.btn_sys.clicked.connect(self.ShowBridge)
        h_outer_lay.addWidget(self.btn_sys)

        # BUTTON: SYSTEM (open integrated System Control Center inside the viewport)
        self.btn_system = LCARSButton("SYSTEM", p[3] if len(p) > 3 else self.secondary, shape="rect")
        self.btn_system.setMinimumSize(120, 40)
        self.btn_system.clicked.connect(self.ShowSystemControl)
        h_outer_lay.addWidget(self.btn_system)

        # BUTTON 2: ALERT (header alert indicator) — toggles alert state
        self.btn_alert = LCARSButton("ALERT", p[2], shape="rect")
        self.btn_alert.setMinimumSize(80, 40)
        self.btn_alert.clicked.connect(self.ToggleAlert)
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
            ("CONSOLE", 0, self.ShowConsole),
            ("PROGRAMS", 1, self.ShowPrograms),
            ("BROWSER", 2, self.ShowBrowser),
            ("EXPLORER", 3, self.ShowExplorer),
            ("HEALTH", 4, self.ShowHealthcheck),
            ("SYSTEM", 5, self.ShowSystemControl),
            ("SCANNER", 6, self.ShowScanner),
        ]
        # Extend standard apps with registered embeddable widgets from tools/widget_registry
        from scripts.widget_registry import get_registered_widgets
        regs = get_registered_widgets()
        # append each registered widget as an app entry; handler will instantiate on demand
        for i, info in enumerate(regs, start=len(apps)):
            apps.append((info.get('name', f'WIDGET_{i}'), i, (lambda *args, _info=info: self.ShowRegisteredWidget(_info))))
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

        # Nav Widgets (Calendar & Weather) — перевірка наявності модулів перед імпортом
        _cal_spec = importlib.util.find_spec('lcars.ui.widgets.calendar')
        if _cal_spec is not None:
            from lcars.ui.widgets.calendar import CalendarNavWidget
            self.cal_nav = CalendarNavWidget(self, era=self.era, faction=self.faction)
            nav_box.addWidget(self.cal_nav)

        _weather_spec = importlib.util.find_spec('lcars.ui.widgets.weather')
        if _weather_spec is not None:
            from lcars.ui.widgets.weather import WeatherNavWidget
            self.weather_nav = WeatherNavWidget(self, era=self.era, faction=self.faction)
            nav_box.addWidget(self.weather_nav)

        sb_inner.addLayout(nav_box)
        sidebar_lay.addLayout(sb_inner)

        spacer = QWidget()
        spacer.setMinimumHeight(10)
        sidebar_lay.addWidget(spacer)

        self.body_layout_container.addWidget(self.sidebar_frame)

        # Viewport
        self.viewport = QFrame()
        self.viewport.setStyleSheet(f"background: #000; border-left: 1px solid {self.accent}22; border-radius:6px; padding:8px;")
        v_lay = QVBoxLayout(self.viewport)
        v_lay.setContentsMargins(12, 12, 12, 12)

        self.stack = QStackedWidget()

        # Тільки базові компоненти для лаунчера
        self.console_view = ConsoleView(self, self.event_bus, self.era, self.faction)
        self.engineering_view = EngineeringView(self.computer, self.era, self.faction, self)

        # Bridge - основний екран
        from lcars.ui.panels.bridge import BridgePanel
        self.bridge_view = BridgePanel(self, era=self.era, faction=self.faction)

        # Додаємо тільки необхідні компоненти
        self.stack.addWidget(self.bridge_view)
        self.stack.addWidget(self.console_view)
        self.stack.addWidget(self.engineering_view)

        # Start with Bridge; console remains available via button
        self.stack.setCurrentWidget(self.bridge_view)

        v_lay.addWidget(self.stack)
        self.body_layout_container.addWidget(self.viewport, 1)

        # After building the main UI, ensure dynamic color bindings are attached
        if hasattr(self, 'ColorTimer'):
            self.ColorTimer.start(3000)

    # Відкрити комплексний інтерфейс System Control Center як embedded widget.
    def ShowSystemControl(self):
        from lcars.ui.system import SystemControlCenter
        # Create and add to the stack
        sys_ctrl = SystemControlCenter(self, self.era, self.faction)
        self.stack.addWidget(sys_ctrl)
        self.stack.setCurrentWidget(sys_ctrl)

    # Вбудовування CentralPanel (контрольна поверхня) у головний viewport stack.
    # Утримує весь UI в одному віконному контейнері (без додаткових вікон).
    def OpenCentralPanel(self):
        from lcars.ui.panels.central import CentralPanel
        if not hasattr(self, 'central_panel') or self.central_panel is None:
            self.central_panel = CentralPanel(system=self.computer, parent=self)
            self.stack.addWidget(self.central_panel)
        self.stack.setCurrentWidget(self.central_panel)
        return True

    # Обробник зміни конфігурації теми в реальному часі (епоха або фракція).
    def OnThemeConfigChanged(self, config_name, key, old_value, new_value):
        logger.info(f"Theme config changed: {key} = {new_value}. Re-initializing UI.")
        era_str = config_manager.get('app', 'era', '25th')
        faction_str = config_manager.get('app', 'faction', 'FEDERATION')

        # Clear cached views so they are rebuilt with the new theme
        for attr in ['programs_view', 'explorer_view', 'browser_view', 'health_inst']:
            if hasattr(self, attr):
                setattr(self, attr, None)

        self.SetupDesktop(faction_str, era_str)

    # Обробник викликається при зміні мови в конфігурації.
    def OnLanguageConfigChanged(self, config_name, key, old_value, new_value):
        from lcars.system.localization import LOCALIZATION as Language
        Language.SetLanguage(new_value)
        # update font/theme in case language-specific font loaded
        from lcars.themes.theme import setup_lcars_font
        setup_lcars_font()

    # Callback зареєстрований у LocalizationService для оновлення міток десктопа.
    def RetranslateDesktop(self, lang_code: str):
        if hasattr(self, 'lbl_title'):
            self.lbl_title.setText(
                Language.translate("LCARS PRIMARY CONSOLE // {era}", era=self.era.value.upper())
            )

    # Оновлення палітри/стильового аркуша десктопа для заданого рівня тривоги.
    def ApplyAlertPalette(self, level: AlertLevel) -> None:
        cfg_colors = config_manager.get("ui", "colors", {}) or {}
        color_map = {
            AlertLevel.NORMAL: cfg_colors.get(
                "alert_normal", self.theme.get("secondary", self.accent)
            ),
            AlertLevel.YELLOW: cfg_colors.get("alert_yellow", "#FFCC33"),
            AlertLevel.RED: cfg_colors.get("alert_red", "#CC0000"),
        }
        color = color_map.get(level, self.theme.get("secondary", self.accent))
        self.setStyleSheet(f"background: {color};")

    # Інстанціювати та вбудувати зареєстрований віджет у головний стек.
    # reg_info — це словник з widget_registry з ключами 'name' та 'cls'.
    def ShowRegisteredWidget(self, reg_info):
        cls = reg_info.get('cls')
        if not cls:
            return

        # If we've already instantiated this widget, switch to it
        if not hasattr(self, 'RegisteredInstances'):
            self.RegisteredInstances = {}
        name = reg_info.get('name') or getattr(cls, '__name__', None)
        if name in self.RegisteredInstances:
            inst = self.RegisteredInstances[name]
            if self.stack.indexOf(inst) != -1:
                self.stack.setCurrentWidget(inst)
                return

        # Try sensible constructor signatures
        inst = None

        inst = cls(self, self.era, self.faction)
        if inst is None:
            return
        self.stack.addWidget(inst)
        self.RegisteredInstances[name] = inst
        self.stack.setCurrentWidget(inst)

    # Переключити viewport на інтегрований екран Bridge
    def ShowBridge(self):
        if hasattr(self, 'bridge_view'):
            self.stack.setCurrentWidget(self.bridge_view)
            self.computer.sounds.play('acknowledge')

    # Відобразити вбудовану консольну панель у viewport stack.
    def ShowConsole(self):
        if hasattr(self, 'console_view') and self.console_view is not None:
            self.stack.setCurrentWidget(self.console_view)
            self.computer.sounds.play('acknowledge')

    def ShowPowerMenu(self):
        self.ShowSystemControl()

    # Перемкнути видимість бічної навігаційної панелі та оновити текст кнопки.
    def ToggleSidebar(self):
        visible = self.sidebar_frame.isVisible()
        self.sidebar_frame.setVisible(not visible)
        self.btn_nav_toggle.setText("NAV ○" if visible else "NAV ●")
        self.computer.sounds.play("acknowledge")

    # Запустити внутрішні таймери: годинник і періодичне оновлення UI.
    def StartTimers(self):
        self.t_clock = QTimer(self)
        self.t_clock.timeout.connect(self.UpdateUi)
        self.t_clock.start(1000)

    # Placeholder для періодичного оновлення UI (годинник, телеметрія тощо).
    def UpdateUi(self):
        pass

    # Callback використовується BoardComputer для вбудовування віджетів у стек десктопа.
    def DesktopAddWidget(self, widget, **meta):
        if hasattr(self, 'stack') and widget is not None:
            self.stack.addWidget(widget)
            self.stack.setCurrentWidget(widget)
            return True
        return False

    # Отримати або створити екземпляр віджета за атрибутом та класом.
    def GetOrCreate(self, attr_name, cls):
        if not hasattr(self, attr_name) or getattr(self, attr_name) is None:
            # attempt primary constructor signature
            inst = cls(self, self.era, self.faction)
            setattr(self, attr_name, inst)
            self.stack.addWidget(inst)
        return getattr(self, attr_name)

    def ShowExplorer(self):
        if v := self.GetOrCreate('explorer_view', ProjectExplorerView):
            self.stack.setCurrentWidget(v)

    def ShowPrograms(self):
        if v := self.GetOrCreate('programs_view', ProgramsView):
            self.stack.setCurrentWidget(v)

    # Вбудовування LCARS веб-браузера у стек десктопа.
    def ShowBrowser(self):
        if not hasattr(self, 'browser_view') or self.browser_view is None:
            from programs.lcars_web_browser import LCARSBrowserProgram
            self.browser_view = LCARSBrowserProgram(era=self.era, faction=self.faction, parent=self)
            self.stack.addWidget(self.browser_view)
        self.stack.setCurrentWidget(self.browser_view)

    # Вбудовування LCARS Scanner Widget у стек десктопа.
    def ShowScanner(self):
        if not hasattr(self, 'scanner_view') or self.scanner_view is None:
            from lcars.ui.widgets.scanner import ScannerWidget
            self.scanner_view = ScannerWidget(era=self.era, faction=self.faction, parent=self)
            self.stack.addWidget(self.scanner_view)
        self.stack.setCurrentWidget(self.scanner_view)

    # Вбудовування повної LCARS Weather Application у стек десктопа.
    def ShowWeather(self):
        if not hasattr(self, 'weather_app_view') or self.weather_app_view is None:
            from programs.weather.app import FullWeatherView
            # Share the engine from the nav widget if possible to save API calls
            engine = getattr(self, "weather_nav", None)
            engine = engine.engine if engine else None
            self.weather_app_view = FullWeatherView(era=self.era, faction=self.faction, parent=self, engine=engine)
            self.stack.addWidget(self.weather_app_view)
        self.stack.setCurrentWidget(self.weather_app_view)

    # Вбудовування archive HealthCheck у стек десктопа (центральний віджет).
    def ShowHealthcheck(self):
        if not hasattr(self, 'health_inst') or self.health_inst is None:
            from tools.health_check import HealthCheck
            self.health_inst = HealthCheck()
            widget = getattr(self.health_inst, 'central', None)
            # Some versions expose centralWidget(); support both
            if widget is None and hasattr(self.health_inst, 'centralWidget'):
                widget = self.health_inst.centralWidget()
            if widget is None:
                widget = self.health_inst
            self.stack.addWidget(widget)
        # prefer the embedded central widget if available
        current_widget = getattr(self.health_inst, 'central', None) or self.health_inst
        self.stack.setCurrentWidget(current_widget)

    # Відкрити головний System Control Center для керування налаштуваннями.
    def ShowSettings(self):
        self.ShowSystemControl()

    # Делегувати циклічне перемикання тривоги до центральної системи тривог.
    def ToggleAlert(self):
        alert_system.next_level()

    # Створити стартове меню якщо потрібно
    def OpenStartMenu(self):
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
        GetSoundManager().play("acknowledge")

    def keyPressEvent(self, a0):
        if a0 and a0.key() == Qt.Key.Key_F1: self.OpenStartMenu()
        super().keyPressEvent(a0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    GetRandomButtonColor()  # initialize color generator
    setup_lcars_font()

    # Allow direct desktop start when script is invoked with --direct
    # or when env var LCARS_DIRECT_DESKTOP=1 is set. Otherwise fall back to
    # the launcher flow to require user confirmation.
    direct = "--direct" in sys.argv or os.environ.get("LCARS_DIRECT_DESKTOP") == "1"
    if direct:
        desktop = LCARSDesktop()
        # Default to Federation/25th when run directly
        desktop.SetupDesktop('Federation', '25th')
        desktop.show()
        sys.exit(app.exec())
