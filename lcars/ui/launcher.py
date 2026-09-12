# LCARS Launcher - Unified entry point for all eras/factions. Adaptive & Resizable.
# Provides a splash screen for access confirmation, then routes to era-specific boot/login flows.
from __future__ import annotations

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys

# Ensure project root is in path for imports (adjust as needed)
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if root not in sys.path:
    sys.path.insert(0, root)
# Переконайтесь, що корінь проєкту в sys.path для імпортів (за потреби скоригуйте)
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Titanium Bridge Migration: from typing import Optional, Sequence
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedLayout, QWidget, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style, setup_lcars_font,
    get_random_button_color, FactionEra
)
# Використовуємо нові модульні компоненти з папок епох
from lcars.ui.views.titan.boot import BootView
from lcars.ui.views.titan.login import LoginView
from lcars.ui.views.titan.odyssey_login import OdysseyLoginView
from lcars.ui.views.titan.selector import SelectorView

# NX-01 Style Views (22nd Century)
from lcars.ui.views.nx01.selector import NX01SelectorView
from lcars.ui.views.nx01.boot import BootViewNX01
from lcars.ui.views.nx01.login import LoginViewNX01

# Фракції та ери за замовчуванням (25-те сторіччя — стандарт)
DEFAULT_FACTIONS = ["Federation", "Klingon", "Romulan", "Cardassian"]
DEFAULT_ERAS = ["22nd", "23rd", "24th", "25th", "29th"]

class SplashView(QWidget):
    # Екран підтвердження доступу (splash). Запобігає мимовільному запуску системи без санкції користувача.
    confirmed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Використання векторного логотипу Федерації
        from lcars.ui.views.titan.odyssey_login import UFPLogo
        self.logo = UFPLogo()
        self.logo.setMinimumSize(400, 400)
        layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_id = QLabel("LCARS PRIMARY OPERATING SYSTEM // AUTHORIZATION REQUIRED")
        self.lbl_id.setStyleSheet(f"color: #CC4422; {get_lcars_font_style(24, 'normal')}")
        layout.addWidget(self.lbl_id, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(40)
        
        # Кнопка підтвердження входу (Manual initialization)
        from lcars.ui.base.widgets import LCARSButton
        self.btn_confirm = LCARSButton("CONFIRM ACCESS", "#9EA5BA", shape="pill")
        self.btn_confirm.setMinimumSize(300, 80)
        self.btn_confirm.clicked.connect(self.confirmed.emit)
        layout.addWidget(self.btn_confirm, alignment=Qt.AlignmentFlag.AlignCenter)

class LCARSLauncher(QDialog):
    # Уніфікований лаунчер LCARS — маршрутизація до епох/фракцій, адаптивний інтерфейс.
    
    def __init__(self, factions: Sequence[str] = DEFAULT_FACTIONS, eras: Sequence[str] = DEFAULT_ERAS, parent=None, require_auth: bool = True):
        super().__init__(parent)
        setup_lcars_font()
        
        self.factions = factions
        self.eras = eras
        # load defaults from config if present
        from lcars.modules.config_manager import config_manager
        self.selected_faction = config_manager.get('ui','default_faction', 'Federation')
        self.selected_era = config_manager.get('ui','default_era', '25th')
        # also allow overriding lists via config
        self.factions = config_manager.get('ui','factions', factions)
        self.eras = config_manager.get('ui','eras', eras)
        # register hotkeys for launcher too
        if True:
            from lcars.system.hotkeys import HotkeyManager
            self.hotkeys = HotkeyManager(self)
        if False: # Removed except block
            pass
        self.require_auth = require_auth
        self._nx01_mode = False
        
        # Режим адаптивності (Resize)
        self.drag_pos = None
        self.margin = 10 

        # Window Setup - БЕЗ рамок, але з підтримкою ресайзу
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.resize(1400, 900)

        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.move((geometry.width() - self.width()) // 2, (geometry.height() - self.height()) // 2)

        # Main Layout
        self.master_layout = QVBoxLayout(self)
        self.master_layout.setContentsMargins(5, 5, 5, 5)

        self.main_container = QFrame()
        # launcher uses flat container (no border contour)
        self.main_container.setStyleSheet("background-color: black; border: none; border-radius: 10px;")
        mc_lay = QVBoxLayout(self.main_container)
        mc_lay.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        mc_lay.addWidget(self.stack)
        self.master_layout.addWidget(self.main_container)

        # Ініціалізуємо поки лише Splash view — створення інших view відкладено
        # until the core has started to ensure correct initialization order.
        self.splash_view = SplashView()
        self.splash_view.confirmed.connect(self.switchToStandard)
        self.stack.addWidget(self.splash_view)

        # СТАРТ: показати спочатку splash (інші view створяться після авторизації/запуску ядра)
        self.stack.setCurrentWidget(self.splash_view)

    def _get_edge(self, pos):
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        m = self.margin
        if x > w - m and y > h - m: return Qt.Edge.BottomEdge | Qt.Edge.RightEdge
        if x > w - m: return Qt.Edge.RightEdge
        if y > h - m: return Qt.Edge.BottomEdge
        return None

    def mousePressEvent(self, a0):
        if a0 is None: return
        if a0.button() == Qt.MouseButton.LeftButton:
            edge = self._get_edge(a0.position().toPoint())
            if edge:
                handle = self.windowHandle()
                if handle:
                    handle.startSystemResize(edge)
            else:
                self.drag_pos = a0.globalPosition().toPoint() - self.frameGeometry().topLeft()
            a0.accept()

    def mouseMoveEvent(self, a0):
        if a0 is None: return
        if not a0.buttons():
            edge = self._get_edge(a0.position().toPoint())
            if edge:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor if edge & Qt.Edge.BottomEdge and edge & Qt.Edge.RightEdge else Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        if a0.buttons() == Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(a0.globalPosition().toPoint() - self.drag_pos)
            a0.accept()

    def _init_all_views(self):
        # Prevent double initialization
        if hasattr(self, 'selector_view'):
            return

        # Splash View (already created during ctor)
        if not hasattr(self, 'splash_view'):
            self.splash_view = SplashView()
            self.splash_view.confirmed.connect(self.switchToStandard)
            self.stack.addWidget(self.splash_view)

        # 25th CENTURY (TITAN) - DEFAULT
        self.selector_view = SelectorView()
        self.selector_view.selected.connect(self.start_initialization)

        self.boot_view = BootView()
        self.boot_view.finished.connect(self.show_login)

        self.login_view = LoginView()
        self.login_view.finished.connect(self.launch_final)

        # 22nd CENTURY (NX-01) - OPTIONAL
        self.nx_selector_view = NX01SelectorView()
        self.nx_selector_view.selected.connect(self.start_initialization)

        self.nx_boot_view = BootViewNX01()
        self.nx_boot_view.finished.connect(self.show_login)

        self.nx_login_view = LoginViewNX01()
        self.nx_login_view.finished.connect(self.launch_final)

        # Register the rest in stack (splash already present)
        for v in [self.selector_view, self.boot_view, self.login_view, self.nx_selector_view, self.nx_boot_view, self.nx_login_view]:
            self.stack.addWidget(v)

    def switchToStandard(self):
        # Стандартний режим TITAN. Перехід після підтвердження доступу.
        # Переконайтесь, що ядро (BoardComputer) запущено перед ініціалізацією
        # view-елементів, що залежать від нього (event_bus, батьківські зв'язки).
        self._nx01_mode = False

        # Спочатку запустити ядро (якщо ще не запущено)
        from plugins import get_system
        system = get_system()
        if system and not system.is_running:
            print("[LAUNCHER] Access confirmed. Initializing core subsystems...")
            system.start()

        # Initialize all remaining views (after core is available)
        self._init_all_views()

        # Якщо лаунчер в режимі require_auth (звичайний запуск),
        # після підтвердження доступу користувач очікує потрапити на десктоп.
        # У цьому випадку запускаємо фінальний старт десктопа негайно.
        if getattr(self, 'require_auth', False):
            if True:
                self.launch_final()
                return
            if False: # Removed except block
                # Якщо фінальний запуск не вдався, повертаємося до селектора
                logger = __import__('logging').getLogger('lcars.ui.launcher')
                logger.exception('Immediate launch_final failed; falling back to selector')

        # За замовчуванням переходимо до екрану вибору (selector)
        self.stack.setCurrentWidget(self.selector_view)

    def switchToNX01(self):
        # Переключити інтерфейс у стиль NX-01 (режим для відладки/опцій).
        self._nx01_mode = True
        self.stack.setCurrentWidget(self.nx_selector_view)

    def start_initialization(self, faction, era):
        # Запуск процесу ініціалізації з обраними фракцією та епохою.
        self.selected_faction = faction
        self.selected_era = era
        
        if era == "22nd":
            self._nx01_mode = True
            self.stack.setCurrentWidget(self.nx_boot_view)
            self.nx_boot_view.start_boot()
        else:
            self._nx01_mode = False
            self.stack.setCurrentWidget(self.boot_view)
            # Прив'язка теми до BootView
            from lcars.themes.lcars_palette import LCARSEra, FactionEra
            era_map = {"23rd": LCARSEra.PCARS_23RD, "23st": LCARSEra.PCARS_23ST, 
                       "24th": LCARSEra.LCARS_24TH, "24st": LCARSEra.LCARS_24ST, 
                       "25th": LCARSEra.LCARS_25TH, "29th": LCARSEra.TCARS_29TH}
            self.boot_view.era = era_map.get(era, LCARSEra.LCARS_25TH)
            self.boot_view.apply_theme()
            self.boot_view.start_boot()

    def show_login(self):
        # Відображення екрану входу (автоматичний логін для стандартного режиму).
        if self._nx01_mode:
            self.stack.setCurrentWidget(self.nx_login_view)
        else:
            self.stack.setCurrentWidget(self.login_view)
            self.login_view.start_auto_login()

    def update_launcher_theme(self, faction, era): 
        # Оновлює тему лаунчера при зміні ери.
        pass 

    def selection(self): 
        # Повертає обрані параметри (faction, era, reserved_flag).
        return (self.selected_faction, self.selected_era, 0)

    def launch_final(self):
        # Фінальний запуск десктопа з обраною конфігурацією.
        print(f"[LAUNCHER] Authorization successful. Launching {self.selected_faction} Desktop...")
        from lcars.ui.desktop import LCARSDesktop
        
        # Створюємо десктоп
        self.desktop = LCARSDesktop()
        self.desktop.setup_desktop(self.selected_faction, self.selected_era)
        self.desktop.showFullScreen()
        
        # Приймаємо діалог (це закриє лаунчер і поверне результат у start_lcars.py)
        self.accept()

