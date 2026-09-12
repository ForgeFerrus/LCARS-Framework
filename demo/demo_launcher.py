# Цей модуль реалізує демонстраційний лаунчер у стилі LCARS з поетапним завантаженням: Boot → Login → Launcher → Desktop. Всі стилі й кольори
# витягуються з палітри теми проекту (`get_theme`, `get_random_button_color`).

import sys
import time
from pathlib import Path
import subprocess

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
# Ensure repository root is on sys.path so imports like `lcars.*` resolve
repo_root = project_root.parent
sys.path.insert(0, str(repo_root))
# Примітка: Ми додаємо корінь репозиторію в `sys.path`, щоб можна було
# імпортувати локальний пакет `lcars` коли скрипт запускається з папки demo/

from PyQt6.QtWidgets import (QApplication, QDialog, QMainWindow, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QPushButton, QFrame, QProgressBar, QStackedWidget, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette

# Import existing LCARS components - widgets first to avoid circular imports
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar
# Stub for sound_manager to avoid circular import
def get_sound_manager():
    class DummySoundManager:
        def PlayAudioClip(self, name): pass
        def PlayAlertSignal(self, severity): pass
    return DummySoundManager()
from lcars.themes.palette import (
    LCARSEra, get_theme, get_random_button_color,
    get_lcars_font_style, LCARSColorGenerator, get_alert_color
)
from lcars.themes.lcars_palette import setup_lcars_font
from lcars.themes.theme import FactionEra

# Головний діалог LCARS з послідовністю фаз завантаження.
class UnifiedLCARSSystem(QDialog):

    
    def __init__(self):
        super().__init__()
        # Поточна епоха/тема — визначає палітру та стилі
        self.era = LCARSEra.LCARS_25TH
        # Поточна фракція (рядок або FactionEra enum). None означає, що
        # користувач ще не зробив вибору — показуємо екран вибору.
        self.faction = None
        # If an enum is available, keep it separately to avoid printing enum reprs
        self.faction_enum = None
        # Генератор кольорів для послідовності віджетів
        self.color_gen = LCARSColorGenerator(self.era)
        # Поточна тема (словар палітри/налаштувань)
        self.theme = get_theme(self.era)
        # Автоматичний режим для демонстрації (опція --auto)
        self.auto_mode = False
        # Опціональні значення для авто-режиму (faction, era)
        self._auto_faction = None
        self._auto_era = None
        # Флаги, які означають, що користувач ОРІГІНАЛЬНО обрав фракцію/епоху
        # (контролюють доступність кнопки LAUNCH)
        self._selected_faction = False
        self._selected_era = False
        # Прапорець авторизації (після Login)
        self._authorized = False
        # Mapping which eras are appropriate for each faction label.
        # This controls which era buttons are shown after a faction is chosen.
        self.allowed_eras_by_faction = {
            "FEDERATION": [LCARSEra.COMS_22ND, LCARSEra.PCARS_23RD, LCARSEra.LCARS_24TH, LCARSEra.LCARS_25TH, LCARSEra.TCARS_29TH],
            "KLINGON": [LCARSEra.PCARS_23RD, LCARSEra.LCARS_24TH, LCARSEra.LCARS_25TH],
            "ROMULAN": [LCARSEra.PCARS_23RD, LCARSEra.LCARS_24TH, LCARSEra.LCARS_25TH],
            "CARDASSIAN": [LCARSEra.LCARS_24TH, LCARSEra.LCARS_25TH]
        }
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(0, 0, QApplication.primaryScreen().size().width(), 
                        QApplication.primaryScreen().size().height())
        
        self.current_phase = "boot"
        # node_phase used by cycle_nodes() — initialize to a safe default
        self.node_phase = 0
        self.setup_ui()
        self.start_unified_sequence()
        
    def setup_ui(self):
        # Базовий фон діалогу та структура контейнерів
        self.setStyleSheet("background-color: black;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main container — фіксований прямокутник, всередині якого ми будуємо сцени
        self.container = QWidget()
        # Make container size relative to the primary screen for responsiveness
        # Use a smaller overall panel so the UI appears scaled down uniformly.
        screen = QApplication.primaryScreen()
        if screen:
            s = screen.size()
            # Make launcher panel smaller (compact preview) per user request
            cw = int(s.width() * 0.60)
            ch = int(s.height() * 0.55)
        else:
            cw, ch = 1200, 700
        self.container.setFixedSize(cw, ch)
        layout.addWidget(self.container)
        
        # Center container
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(self.container)
        h_center.addStretch()
        layout.addLayout(h_center)
        
        # Використовуємо QStackedWidget для перемикання між фазами boot/login/launcher/desktop
        self.stack = QStackedWidget()
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.stack)
        
        # Phase 1: Boot Screen — перша сторінка стеку
        self.boot_widget = self.create_boot_screen()
        self.stack.addWidget(self.boot_widget)
        
        # Phase 2: Login Screen — після завершення boot
        self.login_widget = self.create_login_screen()
        self.stack.addWidget(self.login_widget)
        
        # Phase 3: Launcher Screen — тут відбувається вибір фракції й епохи
        self.launcher_widget = self.create_launcher_screen()
        self.stack.addWidget(self.launcher_widget)
        
        # Phase 4: Desktop Screen — фінальна сторінка демо
        self.desktop_widget = self.create_desktop_screen()
        self.stack.addWidget(self.desktop_widget)

        # Ensure launcher central content reflects the current faction at startup
        # Let `update_launcher_for_faction` handle only import-time errors;
        # avoid broad exception swallowing here so failures are visible.
        self.update_launcher_for_faction()

    # Helper factory methods used by external launcher builders
    def _create_faction_button(self, label, color):
        btn = LCARSButton(label, color, era=self.era, shape="rect", auto_cycle=True)
        btn.setFixedSize(220, 100)
        btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 8px; {get_lcars_font_style(16, 'bold')}")
        btn.clicked.connect(lambda checked, f=label: self.select_faction(f))
        return btn

    def _create_era_button(self, display):
        # Map display to an era enum if possible
        era_map = {e.name.split('_')[-1]: e for e in LCARSEra}
        era = era_map.get(display, None)
        color = self.color_gen.get_next_color()
        btn = LCARSButton(display, color, era=era or self.era, shape='rect', auto_cycle=True)
        btn.setFixedSize(140, 56)
        btn.setStyleSheet(f"background-color: {color}; color: white; border-radius: 6px; {get_lcars_font_style(14, 'normal')}")
        if era is not None:
            btn.clicked.connect(lambda checked, e=era: self.select_era(e))
        return btn
        
    def create_boot_screen(self):
        """Створити екран завантаження (Boot).

        Компоненти стилізуються через палітру теми; тут також використовується
        генератор кольорів `self.color_gen` для послідовної палітри.
        """
        widget = QWidget()
        accent = self.theme.get('accent') or get_random_button_color(self.era)
        secondary = self.theme.get('secondary') or get_random_button_color(self.era)
        # Do not use alert palette by default; use theme accent instead
        alert_col = self.theme.get('accent') or self.color_gen.get_next_color()
        # Отримуємо значення радіусів з теми для узгодженого вигляду
        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        # derive radius values from theme for consistent styling
        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'
        
        # Header (верхня частина екрану): кут, заголовок і кап)
        header = QHBoxLayout()
        header.setSpacing(12)
        
        self.boot_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.boot_elb.setFixedSize(200, 70)
        header.addWidget(self.boot_elb)
        
        self.boot_title = QFrame()
        self.boot_title.setFixedHeight(70)
        self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius};")
        title_layout = QHBoxLayout(self.boot_title)
        title_lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        title_layout.addWidget(title_lbl)
        header.addWidget(self.boot_title, 1)
        
        self.boot_cap = QFrame()
        self.boot_cap.setFixedSize(60, 70)
        self.boot_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: {elbow}; border-bottom-right-radius: {small_radius};")
        header.addWidget(self.boot_cap)
        layout.addLayout(header)
        
        # Main boot area
        main = QHBoxLayout()
        main.setSpacing(12)
        
        boot_sidebar = QFrame()
        boot_sidebar.setFixedWidth(200)
        boot_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius}; border-bottom-left-radius: {elbow};")
        main.addWidget(boot_sidebar)
        
        boot_content = QVBoxLayout()
        boot_content.setContentsMargins(20, 10, 10, 10)
        
        self.boot_step = QLabel("INITIALIZING...")
        self.boot_step.setStyleSheet(f"color: {alert_col}; {get_lcars_font_style(24, 'normal')}")
        boot_content.addWidget(self.boot_step)
        
        self.boot_log = QLabel("> BOOT_MODE: NOMINAL")
        self.boot_log.setStyleSheet(f"color: {secondary}; {get_lcars_font_style(16, 'normal')}")
        self.boot_log.setWordWrap(True)
        boot_content.addWidget(self.boot_log)
        boot_content.addStretch()
        
        main.addLayout(boot_content, 1)
        layout.addLayout(main, 1)
        
        # Footer
        self.boot_footer = QFrame()
        self.boot_footer.setFixedHeight(40)
        self.boot_footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: {small_radius}; border-top-right-radius: {small_radius};")
        layout.addWidget(self.boot_footer)
        
        return widget
        
    def create_login_screen(self):
        """Створити екран авторизації (Login).

        Показує індикатор сканування й кнопку авторизації. При підтвердженні
        переходить до вибору фракції/епохи перед лаунчером.
        """
        widget = QWidget()
        # Отримуємо значення радіусів з теми для узгодженого вигляду
        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(12)
        
        self.login_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.login_elb.setFixedSize(180, 60)
        header.addWidget(self.login_elb)
        
        self.login_title = QFrame()
        self.login_title.setFixedHeight(60)
        self.login_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius};")
        title_layout = QHBoxLayout(self.login_title)
        title_layout.setContentsMargins(20, 0, 0, 0)
        title_lbl = QLabel("◢ AUTHORIZATION PROTOCOL - SECURE ACCESS")
        title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        title_layout.addWidget(title_lbl)
        header.addWidget(self.login_title, 1)
        
        self.login_cap = QFrame()
        self.login_cap.setFixedSize(40, 60)
        self.login_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: {elbow}; border-bottom-right-radius: {small_radius};")
        header.addWidget(self.login_cap)
        layout.addLayout(header)
        
        # Main login area
        main = QHBoxLayout()
        main.setSpacing(16)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(4)
        self.login_sidebar = QFrame()
        self.login_sidebar.setFixedSize(180, 200)
        self.login_sidebar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius}; border-bottom-left-radius: {elbow};")
        sidebar.addWidget(self.login_sidebar)
        sidebar.addStretch()
        main.addLayout(sidebar)
        
        # Content
        content = QVBoxLayout()
        content.setContentsMargins(30, 20, 30, 20)
        content.setSpacing(15)
        
        # Use theme accent for login status (no alert palette)
        login_alert = self.theme.get('accent') or self.color_gen.get_next_color()
        self.login_status = QLabel("PROTOCOL :: IDENTIFYING NEURAL PATTERN...")
        self.login_status.setStyleSheet(f"color: {login_alert}; {get_lcars_font_style(18, 'normal')}")
        content.addWidget(self.login_status)
        
        self.login_progress = ScanningBar(self.color_gen.get_next_color(), self)
        self.login_progress.setFixedHeight(25)
        content.addWidget(self.login_progress)
        
        content.addStretch()
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        self.login_btn = LCARSButton("AUTHORIZE", self.theme.get('accent') or self.color_gen.get_next_color(), era=self.era, shape="rect", auto_cycle=True)
        self.login_btn.setFixedSize(180, 50)
        self.login_btn.clicked.connect(self.complete_login)
        btn_box.addWidget(self.login_btn)
        content.addLayout(btn_box)
        
        main.addLayout(content, 1)
        layout.addLayout(main, 1)
        
        # Footer
        self.login_footer = QFrame()
        self.login_footer.setFixedHeight(30)
        self.login_footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: {small_radius}; border-top-right-radius: {small_radius};")
        layout.addWidget(self.login_footer)
        
        return widget

    def complete_login(self):
        """Завершити авторизацію: оновити статус і перейти до вибору фракції.

        Викликається при натисканні кнопки AUTHORIZE на екрані логіну.
        """
        get_sound_manager().play("ready")
        self._authorized = True
        if hasattr(self, 'login_status'):
            self.login_status.setText("PROTOCOL :: AUTHORIZED")
        # Невелика затримка щоб показати оновлення статусу, потім перехід
        QTimer.singleShot(800, self.transition_to_selection)
        
    def create_launcher_screen(self):
        """Створити екран лаунчера (Launcher).

        Екран показує вибір фракції та епохи, а також кнопки запуску. Всі
        кольори беруться з функцій `get_random_button_color` або `get_theme`.
        """
        widget = QWidget()
        # Отримуємо значення радіусів з теми для узгодженого вигляду
        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Header
        header = QHBoxLayout()
        header.setSpacing(16)
        
        self.launcher_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        self.launcher_elb.setFixedSize(220, 80)
        header.addWidget(self.launcher_elb)
        
        self.launcher_title = QFrame()
        self.launcher_title.setFixedHeight(80)
        title_color = self.theme.get('accent') or get_random_button_color(self.era)
        self.launcher_title.setStyleSheet(f"background-color: {title_color}; border-radius: {radius};")
        title_layout = QHBoxLayout(self.launcher_title)
        title_layout.setContentsMargins(25, 0, 0, 0)
        # Expose launcher title label so faction-specific designs can modify it
        self.launcher_title_label = QLabel("◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        self.launcher_title_label.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        title_layout.addWidget(self.launcher_title_label)
        header.addWidget(self.launcher_title, 1)
        
        self.launcher_cap = QFrame()
        self.launcher_cap.setFixedSize(80, 80)
        cap_color = self.theme.get('secondary') or get_random_button_color(self.era)
        self.launcher_cap.setStyleSheet(f"background-color: {cap_color}; border-top-right-radius: {elbow}; border-bottom-right-radius: {small_radius};")
        header.addWidget(self.launcher_cap)
        layout.addLayout(header)
        
        # Main launcher area
        main = QHBoxLayout()
        main.setSpacing(20)
        
        # Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(16)
        
        self.launcher_sidebar = QFrame()
        # smaller sidebar to match compact launcher
        self.launcher_sidebar.setFixedSize(180, 360)
        sidebar_color = self.theme.get('secondary') or self.color_gen.get_next_color()
        self.launcher_sidebar.setStyleSheet(f"background-color: {sidebar_color}; border-radius: {radius}; border-bottom-left-radius: {elbow};")
        sidebar.addWidget(self.launcher_sidebar)
        
        sidebar.addStretch()
        
        # Animated nodes
        # Create launcher nodes using the current theme palette in order
        self.launcher_nodes = []
        palette = self.theme.get('palette', [self.color_gen.get_next_color()])
        for i in range(6):
            n = QFrame()
            n.setFixedSize(180, 20)
            color = palette[i % len(palette)]
            n.setStyleSheet(f"background-color: {color}; border-radius: {small_radius};")
            sidebar.addWidget(n)
            self.launcher_nodes.append(n)
            
        # RED ALERT Button (hidden by default; do not use alert palette here)
        alert_color = self.theme.get('secondary') or self.color_gen.get_next_color()
        self.alert_btn = LCARSButton("RED ALERT", alert_color, era=self.era, shape="rect", auto_cycle=False)
        self.alert_btn.setFixedSize(180, 48)
        self.alert_btn.setVisible(False)
        sidebar.addWidget(self.alert_btn)
        
        main.addLayout(sidebar)
        
        # Content area container: this will be replaced with faction-specific
        # launcher UIs via `update_launcher_for_faction`.
        self.launcher_content_container = QWidget()
        self.launcher_content_container.setObjectName('launcher_content_container')
        content_layout = QVBoxLayout(self.launcher_content_container)
        # increase inner margins so central content breathes
        content_layout.setContentsMargins(60, 40, 40, 40)
        content_layout.setSpacing(36)
        # Ensure central content is horizontally centered within the container
        content_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        # Build default content initially
        default_content = self.build_default_launcher_content()
        content_layout.addWidget(default_content)
        # Debug: report how many faction/era buttons were created
        try:
            fb = getattr(self, 'faction_buttons', None)
            eb_map = getattr(self, 'era_buttons_map', None)
            print(f"[launcher-debug] faction_buttons={len(fb) if fb is not None else 0}, era_buttons={len(eb_map) if eb_map is not None else 0}")
        except Exception:
            pass
        
        # Add the content container to the main layout
        main.addWidget(self.launcher_content_container, 1)

        # Launch button (static area below the content) so it remains available
        # regardless of which faction content is shown.
        # Restore original launch button sizing/color (compact launcher)
        launch_btn_color = self.theme.get('accent') or self.color_gen.get_next_color()
        self.launch_btn = LCARSButton("LAUNCH SYSTEM", launch_btn_color, era=self.era, shape="rect", auto_cycle=False)
        # smaller launch button for compact launcher
        self.launch_btn.setFixedSize(240, 48)
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self.launch_desktop)

        # Add main area first, then place the static launch button below it
        layout.addLayout(main)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.launch_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Footer
        self.launcher_footer = QFrame()
        self.launcher_footer.setFixedHeight(40)
        footer_color = self.theme.get('secondary') or get_random_button_color(self.era)
        self.launcher_footer.setStyleSheet(f"background-color: {footer_color}; border-bottom-right-radius: {small_radius}; border-top-right-radius: {small_radius};")
        layout.addWidget(self.launcher_footer)
        
        # Node animation timer (start when launcher becomes visible)
        self.node_timer = QTimer()
        self.node_timer.timeout.connect(self.cycle_nodes)
        
        return widget
        
    def create_desktop_screen(self):
        """Create the desktop container and populate per-current-faction content.

        The desktop page is a wrapper whose inner content is rebuilt when the
        user selects a faction. This allows each faction to have its own
        interface while keeping the stacked page reference stable.
        """
        widget = QWidget()
        self.desktop_container_layout = QVBoxLayout(widget)
        self.desktop_container_layout.setContentsMargins(0, 0, 0, 0)
        self.desktop_container_layout.setSpacing(0)

        # Build initial content according to currently selected faction
        self.desktop_content = self.build_desktop_content()
        self.desktop_container_layout.addWidget(self.desktop_content)

        return widget

    # --- Launcher content builders ---------------------------------
    def build_default_launcher_content(self):
        """Build the default (Federation-style) launcher central content."""
        # Prefer new centralized builders (cleaner, easier to iterate)
        try:
            from demo.launcher_central import build_default_launcher_content as central_default
            return central_default(self)
        except Exception as e:
            print(f"[launcher-debug] central_default builder failed: {e}")
            # fallback minimal implementation to avoid empty UI
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(12)
            stardate = time.strftime("%Y.%m.%d")
            faction_display = self.faction if self.faction else 'UNASSIGNED'
            self.launcher_info = QLabel(f"STARDATE: {stardate} // {faction_display} SECTOR")
            self.launcher_info.setStyleSheet(f"color: {self.theme.get('accent') or '#FFCC33'}; {get_lcars_font_style(20, 'normal')}")
            layout.addWidget(self.launcher_info)
            return widget

    def build_klingon_launcher_content(self):
        """Build a distinct Klingon launcher central content (different layout/feel)."""
        try:
            from demo.launcher_central import build_klingon_launcher_content as central_klingon
            return central_klingon(self)
        except Exception as e:
            print(f"[launcher-debug] central_klingon builder failed: {e}")
            w = QWidget()
            layout = QHBoxLayout(w)
            layout.addWidget(QLabel("KLINGON - (fallback UI)"))
            return w

    def update_launcher_for_faction(self):
        """Replace the central launcher content according to `self.faction`."""
        # remove old content widget(s)
        if not hasattr(self, 'launcher_content_container'):
            print("[launcher-debug] no launcher_content_container available")
            return
        for i in reversed(range(self.launcher_content_container.layout().count())):
            item = self.launcher_content_container.layout().itemAt(i)
            w = item.widget()
            if w:
                self.launcher_content_container.layout().removeWidget(w)
                w.setParent(None)

        # determine faction key
        fk = None
        if isinstance(self.faction_enum, FactionEra):
            fk = self.faction_enum.name.split('_')[0].upper()
        else:
            fk = str(self.faction).upper()
        print(f"[launcher-debug] updating launcher for faction '{fk}'")

        # Try modular faction UI first
        new = None
        try:
            from demo.faction_ui import get_faction_module
            mod = get_faction_module(fk)
            print(f"[launcher-debug] modular module found: {mod}")
            if mod and hasattr(mod, 'build_launcher_content'):
                new = mod.build_launcher_content(self)
                print("[launcher-debug] used modular build_launcher_content")
        except Exception as e:
            print(f"[launcher-debug] modular loader error: {e}")

        # fallbacks
        if new is None:
            if fk == 'KLINGON':
                print("[launcher-debug] falling back to build_klingon_launcher_content")
                new = self.build_klingon_launcher_content()
            else:
                print("[launcher-debug] falling back to build_default_launcher_content")
                new = self.build_default_launcher_content()

        # ensure we have a widget
        if new is None:
            print("[launcher-debug] ERROR: builder returned None, adding empty placeholder")
            new = QWidget()

        self.launcher_content_container.layout().addWidget(new)

        # By default, hide era buttons until a faction is chosen to enforce
        # selection order: Faction -> Era -> Launch. Builders may expose
        # `era_buttons_map` but we ensure they remain hidden until selection.
        eb_map = getattr(self, 'era_buttons_map', None)
        if eb_map:
            for era, eb in list(eb_map.items()):
                try:
                    if getattr(eb, 'setVisible', None):
                        eb.setVisible(False)
                        eb.setEnabled(False)
                except RuntimeError:
                    continue

    def build_desktop_content(self):
        """Return a QWidget for the current faction's desktop UI."""
        # Try to load faction desktop from modular UI package first
        try:
            from demo.faction_ui import get_faction_module
            fk = None
            if isinstance(self.faction_enum, FactionEra):
                fk = self.faction_enum.name.split('_')[0].upper()
            else:
                fk = str(self.faction).upper()
            mod = get_faction_module(fk)
            if mod and hasattr(mod, 'build_desktop_content'):
                return mod.build_desktop_content(self)
        except Exception:
            pass

        # Fallback to existing internal builders
        if isinstance(self.faction_enum, FactionEra):
            faction_key = self.faction_enum.name.split('_')[0].upper()
        else:
            faction_key = str(self.faction).upper()
        if faction_key == 'KLINGON':
            return self.build_klingon_desktop()
        else:
            return self.build_default_desktop()

    def update_desktop_for_faction(self):
        """Rebuild desktop inner content for the current faction."""
        try:
            if hasattr(self, 'desktop_content') and self.desktop_content is not None:
                # Remove old content widget
                self.desktop_container_layout.removeWidget(self.desktop_content)
                self.desktop_content.setParent(None)
            # Build and add new content
            self.desktop_content = self.build_desktop_content()
            self.desktop_container_layout.addWidget(self.desktop_content)
        except Exception:
            pass

    def build_default_desktop(self):
        """Existing default desktop UI (keeps previous look)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'

        # Header
        header = QHBoxLayout()
        header.setSpacing(4)
        desktop_elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        desktop_elb.setFixedSize(250, 80)
        header.addWidget(desktop_elb)

        title_panel = QFrame()
        title_panel.setFixedHeight(80)
        t_color = self.theme.get('accent') or self.color_gen.get_next_color()
        title_panel.setStyleSheet(f"background-color: {t_color}; border-radius: {radius};")
        title_layout = QHBoxLayout(title_panel)
        title = QLabel(f"USS ENTERPRISE - {self.faction} {self.era.value}")
        title.setStyleSheet(f"color: black; {get_lcars_font_style(28, 'normal')}")
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)

        right_cap = QFrame()
        right_cap.setFixedSize(100, 80)
        cap_color = self.theme.get('secondary') or get_random_button_color(self.era)
        right_cap.setStyleSheet(f"background-color: {cap_color}; border-top-right-radius: {elbow}; border-bottom-right-radius: {small_radius};")
        header.addWidget(right_cap)

        layout.addLayout(header)

        # Main interface (simple)
        interface = QHBoxLayout()
        interface.setSpacing(6)
        left_panel = QVBoxLayout()
        left_panel.setSpacing(6)
        main_left = QFrame()
        main_left.setFixedWidth(250)
        main_left_color = self.theme.get('secondary') or self.color_gen.get_next_color()
        main_left.setStyleSheet(f"background-color: {main_left_color}; border-radius: {radius}; border-bottom-left-radius: {elbow};")
        left_panel.addWidget(main_left, 1)

        controls = [
            ("DASHBOARD", self.color_gen.get_next_color()),
            ("TACTICAL", get_alert_color(self.era, alert_level=2)),
            ("SCIENCE", self.color_gen.get_next_color()),
            ("ENGINEERING", self.color_gen.get_next_color()),
            ("COMMUNICATIONS", self.color_gen.get_next_color())
        ]
        for control, color in controls:
            btn = LCARSButton(control, color, era=self.era, shape="rect", auto_cycle=True)
            btn.setFixedSize(250, 60)
            left_panel.addWidget(btn)
        left_panel.addStretch(1)
        bottom_elbow = LCARSElbow("bottom-left", era=self.era, auto_cycle=False)
        bottom_elbow.setFixedSize(250, 80)
        left_panel.addWidget(bottom_elbow)
        interface.addLayout(left_panel)

        # Center display (status panels)
        center = QVBoxLayout()
        center.setContentsMargins(20, 20, 20, 20)
        center.setSpacing(15)
        status_panel = QFrame()
        status_panel.setFixedHeight(120)
        status_panel_color = self.theme.get('accent') or get_random_button_color(self.era)
        status_panel.setStyleSheet(f"background-color: {status_panel_color}; border-radius: {radius};")
        status_layout = QVBoxLayout(status_panel)
        status_title = QLabel("MAIN SYSTEMS STATUS")
        status_title.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        status_info = QLabel("ALL SYSTEMS OPERATIONAL - GREEN ALERT")
        status_info.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        status_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_info)
        center.addWidget(status_panel)

        # Simple systems grid
        systems_grid = QGridLayout()
        systems_grid.setSpacing(15)
        systems = [
            ("SHIELDS", "ONLINE - 100%"),
            ("WEAPONS", "STANDBY"),
            ("ENGINES", "WARP 9.0"),
            ("SENSORS", "LONG RANGE"),
            ("COMM", "SUBSPACE OPEN"),
            ("LIFE SUPPORT", "OPTIMAL")
        ]
        for i, (system, status) in enumerate(systems):
            panel = QFrame()
            panel.setFixedSize(200, 80)
            panel.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius};")
            panel_layout = QVBoxLayout(panel)
            system_label = QLabel(system)
            system_label.setStyleSheet(f"color: black; {get_lcars_font_style(16, 'normal')}")
            system_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(system_label)
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(status_label)
            systems_grid.addWidget(panel, i // 2, i % 2)
        center.addLayout(systems_grid)
        center.addStretch()
        interface.addLayout(center, 1)
        layout.addLayout(interface)

        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(4)
        left_status = LCARSElbow("bottom-left", era=self.era, auto_cycle=False)
        left_status.setFixedSize(300, 50)
        footer.addWidget(left_status)
        center_status = QFrame()
        center_status.setFixedHeight(50)
        center_status_color = self.theme.get('secondary') or self.color_gen.get_next_color()
        center_status.setStyleSheet(f"background-color: {center_status_color}; border-radius: {radius};")
        center_layout = QHBoxLayout(center_status)
        status_text = QLabel(f"STARDATE: {int(time.time()) % 100000} - SYSTEM READY")
        status_text.setStyleSheet(f"color: {self.theme.get('text') or '#FFFFFF'}; {get_lcars_font_style(16, 'normal')}")
        center_layout.addWidget(status_text)
        footer.addWidget(center_status, 1)
        right_status = QFrame()
        right_status.setFixedSize(150, 50)
        right_status_color = self.theme.get('secondary') or self.color_gen.get_next_color()
        right_status.setStyleSheet(f"background-color: {right_status_color}; border-bottom-right-radius: {small_radius}; border-top-right-radius: {small_radius};")
        footer.addWidget(right_status)
        layout.addLayout(footer)

        return widget

    def build_klingon_desktop(self):
        """Construct a Klingon-styled desktop interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        radius = self.theme.get('radius', '4px')
        elbow = self.theme.get('elbow', '40px')
        small_radius = '4px'

        # Bold header with Klingon accent
        header = QHBoxLayout()
        header.setSpacing(4)
        elb = LCARSElbow("top-left", era=self.era, auto_cycle=False)
        elb.setFixedSize(250, 80)
        header.addWidget(elb)

        title_panel = QFrame()
        title_panel.setFixedHeight(80)
        klingon_accent = get_random_button_color(self.era, self.faction) or '#A82828'
        title_panel.setStyleSheet(f"background-color: {klingon_accent}; border-radius: {radius};")
        title_layout = QHBoxLayout(title_panel)
        title = QLabel(f"K" + "'" + "ara Command - KLINGON EMPIRE")
        title.setStyleSheet(f"color: black; {get_lcars_font_style(26, 'bold')}")
        title_layout.addWidget(title)
        header.addWidget(title_panel, 1)

        right_cap = QFrame()
        right_cap.setFixedSize(100, 80)
        right_cap.setStyleSheet(f"background-color: #2B0B0B; border-top-right-radius: {elbow}; border-bottom-right-radius: {small_radius};")
        header.addWidget(right_cap)
        layout.addLayout(header)

        # Main interface: emphasis on tactical/warfare panels
        interface = QHBoxLayout()
        interface.setSpacing(8)

        # Klingon control column
        left_col = QVBoxLayout()
        left_col.setSpacing(8)
        panel = QFrame()
        panel.setFixedWidth(300)
        panel.setStyleSheet(f"background-color: #2E1A1A; border-radius: {radius};")
        p_layout = QVBoxLayout(panel)
        p_layout.setContentsMargins(12, 12, 12, 12)
        p_title = QLabel("WAR COUNCIL")
        p_title.setStyleSheet(f"color: #FFD8C0; {get_lcars_font_style(18,'bold')}")
        p_layout.addWidget(p_title)
        for name in ("TACTICAL", "BATTLE MAP", "TARGETING", "BORDER FLEETS"):
            b = LCARSButton(name, '#8A1F1F', era=self.era, shape="rect", auto_cycle=True)
            b.setFixedSize(260, 60)
            p_layout.addWidget(b)
        p_layout.addStretch()
        left_col.addWidget(panel)
        interface.addLayout(left_col)

        # Center: status and weapons
        center_col = QVBoxLayout()
        center_col.setContentsMargins(10,10,10,10)
        status_panel = QFrame()
        status_panel.setFixedHeight(140)
        status_panel.setStyleSheet(f"background-color: {klingon_accent}; border-radius: {radius};")
        s_layout = QVBoxLayout(status_panel)
        s_title = QLabel("MAIN WAR STATUS")
        s_title.setStyleSheet(f"color: black; {get_lcars_font_style(20)}")
        s_layout.addWidget(s_title)
        s_info = QLabel("SHIELDS: 78%  |  ARMOR: 64%  |  PHOTON TORPEDOES: 120")
        s_info.setStyleSheet(f"color: black; {get_lcars_font_style(14)}")
        s_layout.addWidget(s_info)
        center_col.addWidget(status_panel)

        weapons_grid = QGridLayout()
        for i, (n, st) in enumerate([("TORPEDO", "READY"), ("PLASMA", "CHARGING"), ("PULSAR", "STANDBY"), ("DRONES", "DEPLOYED")]):
            w = QFrame()
            w.setFixedSize(260, 90)
            w.setStyleSheet(f"background-color: #5A1A1A; border-radius: {radius};")
            wl = QVBoxLayout(w)
            wl.addWidget(QLabel(n))
            wl.addWidget(QLabel(st))
            weapons_grid.addWidget(w, i // 2, i % 2)
        center_col.addLayout(weapons_grid)
        center_col.addStretch()
        interface.addLayout(center_col, 1)

        # Right: sensors/comm
        right_col = QVBoxLayout()
        right_col.setSpacing(8)
        r_panel = QFrame()
        r_panel.setFixedWidth(220)
        r_panel.setStyleSheet(f"background-color: #3B1212; border-radius: {radius};")
        rp_l = QVBoxLayout(r_panel)
        rp_l.addWidget(QLabel("SENSORS"))
        rp_l.addWidget(QLabel("LONG RANGE: ACTIVE"))
        rp_l.addStretch()
        right_col.addWidget(r_panel)
        interface.addLayout(right_col)

        layout.addLayout(interface)

        # Footer
        footer = QHBoxLayout()
        footer.addStretch()
        f_label = QLabel("KHAN'IL SYSTEM - HONOR ABOVE ALL")
        f_label.setStyleSheet(f"color: #FFCFCF; {get_lcars_font_style(14)}")
        footer.addWidget(f_label)
        layout.addLayout(footer)

        return widget
        
    def start_unified_sequence(self):
        """Запустити послідовність завантаження (починає з Boot)."""
        self.current_phase = "boot"
        self.stack.setCurrentIndex(0)  # Show boot screen
        self.start_boot_sequence()

    def apply_theme(self):
        """Apply current `self.theme` to visible UI elements.

        This updates key frames and headers so the launcher preview
        accurately reflects the selected faction/era palette.
        """
        theme = get_theme(self.era, self.faction_enum)
        self.theme = theme

        # helper to set stylesheet (let exceptions surface)
        def ss(widget, style):
            if widget is not None:
                widget.setStyleSheet(style)

        accent = theme.get('accent') if theme else '#444444'
        secondary = theme.get('secondary') if theme else '#666666'
        radius = theme.get('radius', '6px') if theme else '6px'

        # Update boot elements
        ss(getattr(self, 'boot_title', None), f"background-color: {accent}; border-radius: {radius};")
        ss(getattr(self, 'boot_cap', None), f"background-color: {secondary}; border-top-right-radius: {theme.get('elbow','40px')}; border-bottom-right-radius: 4px;")
        ss(getattr(self, 'boot_footer', None), f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 4px;")

        # Update login elements
        ss(getattr(self, 'login_title', None), f"background-color: {accent}; border-radius: {radius};")
        ss(getattr(self, 'login_cap', None), f"background-color: {secondary}; border-top-right-radius: {theme.get('elbow','40px')}; border-bottom-right-radius: 4px;")

        # Update launcher elements
        ss(getattr(self, 'launcher_title', None), f"background-color: {accent}; border-radius: {radius};")
        ss(getattr(self, 'launcher_cap', None), f"background-color: {secondary}; border-top-right-radius: {theme.get('elbow','40px')}; border-bottom-right-radius: 4px;")
        ss(getattr(self, 'launcher_sidebar', None), f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius};")
        ss(getattr(self, 'launcher_footer', None), f"background-color: {secondary}; border-bottom-right-radius: 4px;")

        # Update desktop/title if present
        ss(getattr(self, 'boot_step', None), f"color: {theme.get('accent') if theme else '#FFFFFF'}; {get_lcars_font_style(18)}")
        
    def apply_faction_design(self):
        """Apply small, opinionated design adjustments per faction.

        This function adjusts header/footer/sidebar colors and node
        palettes to give each faction a distinct look. It's intentionally
        lightweight — main palettes still come from `get_theme`.
        """
        # determine faction key as upper-case string
        if isinstance(self.faction_enum, FactionEra):
            faction_key = self.faction_enum.name.split('_')[0].upper()
        else:
            faction_key = str(self.faction).upper()

        # default colors from theme
        accent = self.theme.get('accent') or self.color_gen.get_next_color()
        secondary = self.theme.get('secondary') or self.color_gen.get_next_color()

        # Per-faction adjustments (fallback to theme values)
        if faction_key == 'KLINGON':
            # stronger reds (but do not alter the main container panel)
            accent = get_random_button_color(self.era, self.faction) or '#C03030'
            secondary = '#3A1F1F'
        elif faction_key == 'ROMULAN':
            accent = get_random_button_color(self.era, self.faction) or '#33AA66'
            secondary = '#0F2F1F'
        elif faction_key == 'CARDASSIAN':
            accent = get_random_button_color(self.era, self.faction) or '#6B2F2F'
            secondary = '#2E2B2A'
        else:
            # Federation / default — keep theme defaults
            accent = accent
            secondary = secondary

        # Only update non-structural, textual indicators for faction —
        # do NOT modify core panel styling here. This preserves the
        # main launcher appearance and confines visual changes to
        # faction-specific UI modules.
        if hasattr(self, 'launcher_title_label'):
            self.launcher_title_label.setText(f"◢ SYSTEM ACCESS // {faction_key} // TEMPORAL ALIGNMENT")

    def start_boot_sequence(self):
        """Запустити фази boot із послідовними кроками та таймером."""
        self.boot_steps = [
            "◤ ISOLINEAR CORE: INITIALIZING...",
            "◤ NEXUS DATA HUB: CONNECTING...", 
            "◤ NEURAL PROCESSOR: CALIBRATING...",
            "◤ SUBSPACE COMMUNICATIONS: ESTABLISHING LINK...",
            "◤ TACTICAL SYSTEMS: LOADING...",
            "◤ SHIELD GENERATORS: POWERING UP...",
            "◤ WARP CORE: IGNITION SEQUENCE...",
            "◤ LIFE SUPPORT: ONLINE",
            "◤ LCARS INTERFACE: READY"
        ]
        
        self.boot_progress = 0
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.update_boot)
        self.boot_timer.start(800)
        get_sound_manager().play("acknowledge")
        
    def update_boot(self):
        """Оновити прогрес boot: показати наступний крок і змінити колірні елементи."""
        if self.boot_progress < len(self.boot_steps):
            step_text = self.boot_steps[self.boot_progress]
            self.boot_step.setText(step_text)
            self.boot_log.setText(f"{self.boot_log.text()}\n> {step_text.split(':')[0]} :: ONLINE")
            get_sound_manager().play("click")
            
            # Update colors: оновлюємо декоративні елементи палітрою наступного кольору
            # (дає відчуття процесу завантаження — кольори «мигають» послідовно)
            elbow = self.theme.get('elbow', '40px')
            small_radius = '4px'
            self.boot_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: {elbow}; border-bottom-left-radius: {small_radius};")
            radius = self.theme.get('radius', '4px')
            self.boot_title.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: {radius};")
            
            self.boot_progress += 1
        else:
            self.boot_timer.stop()
            get_sound_manager().play("ready")
            # After boot, move to selection phase (Faction -> Era) before login
            QTimer.singleShot(1500, self.transition_to_selection)
    def transition_to_selection(self):
        """Показати екран вибору фракції/епохи після завершення
boot-послідовності."""
        # After boot, show the launcher selection (faction buttons) directly.
        self.current_phase = "selection"
        # Show launcher page (index 2) so faction buttons are visible immediately
        self.stack.setCurrentIndex(2)
        get_sound_manager().play("acknowledge")
        # mark authorized since we skip the login step in this simplified flow
        self._authorized = True
        # Ensure launcher reflects current state
        self.update_launcher_for_faction()
        self.apply_theme()
        # start node animation when launcher is visible
        if hasattr(self, 'node_timer'):
            self.node_timer.start(4000)
                
    def transition_to_launcher(self):
        """Показати екран лаунчера (після того, як вибір фракції/епохи і логін завершені)."""
        self.current_phase = "launcher"
        get_sound_manager().play("ready")
        # Show the launcher page and start node animation
        self.stack.setCurrentIndex(2)
        # Ensure the launcher content matches the currently selected faction
        self.update_launcher_for_faction()
        self.apply_theme()

        print("[launcher] warning: update_launcher_for_faction failed during transition")
        # start node animation when launcher is visible
        if hasattr(self, 'node_timer'):
            self.node_timer.start(4000)

        # Enable LAUNCH only when faction, era and authorization are present
            if hasattr(self, 'launch_btn'):
                self.launch_btn.setEnabled(bool(self._selected_faction and self._selected_era and self._authorized))

    def select_faction(self, faction_label, faction_enum: FactionEra = None):
        """Обробити вибір фракції та оновити інфо-рядок лаунчера.

        Параметри:
        - faction_label: текстова мітка (наприклад 'FEDERATION')
        - faction_enum: опціональний `FactionEra` enum для точнішої палітри
        """
        get_sound_manager().play("acknowledge")
        # Зберігаємо рядкове ім'я для відображення і enum окремо для палітри
        self.faction = faction_label
        self.faction_enum = faction_enum if isinstance(faction_enum, FactionEra) else None
        # Відзначаємо, що користувач зробив вибір фракції
        self._selected_faction = True
        # Оновлюємо видимий рядок інформації
        stardate = time.strftime("%Y.%m.%d")
        self.launcher_info.setText(f"STARDATE: {stardate} // {faction_label} SECTOR")
        # Оновлюємо генератор/тему (передаємо enum якщо він є)
        self.color_gen = LCARSColorGenerator(self.era, self.faction_enum)
        self.theme = get_theme(self.era, self.faction_enum)
        print(f"[launcher] faction selected -> {self.faction} ({self.faction_enum})")
        # apply theme preview immediately so launcher reflects choice
        fk = str(faction_label).upper()
        if fk == 'KLINGON':
            self.setWindowTitle('Klingon Empire - Launcher')
            if hasattr(self, 'launcher_title_label'):
                self.launcher_title_label.setText("◢ KLINGON COMMAND - K'ARA")
        elif fk == 'ROMULAN':
            self.setWindowTitle('Romulan Directorate - Launcher')
            if hasattr(self, 'launcher_title_label'):
                self.launcher_title_label.setText('◢ ROMULAN DIRECTORATE - SYSTEM')
        elif fk == 'CARDASSIAN':
            self.setWindowTitle('Cardassian Union - Launcher')
            if hasattr(self, 'launcher_title_label'):
                self.launcher_title_label.setText('◢ CARDASSIAN UNION - INTERFACE')
        else:
            self.setWindowTitle('Federation - LCARS Launcher')
            if hasattr(self, 'launcher_title_label'):
                self.launcher_title_label.setText('◢ SYSTEM ACCESS // TEMPORAL ALIGNMENT')

        self.apply_theme()
        # apply lightweight faction-specific design adjustments
        self.apply_faction_design()
        # rebuild desktop content for the chosen faction
        self.update_desktop_for_faction()
        # Rebuild launcher central content per-faction so the launcher UI
        # itself changes (not just labels).
        self.update_launcher_for_faction()
        # Mark the faction as selected and lock the faction buttons
        # so the interface is fixed to this faction before era selection.
        self._selected_faction = True
        if hasattr(self, 'faction_buttons'):
            # iterate over a snapshot and skip any deleted widgets safely
            for b in list(getattr(self, 'faction_buttons', [])):
                if not getattr(b, 'setEnabled', None):
                    continue
                try:
                    b.setEnabled(False)
                    # visually indicate selected faction vs others
                    if getattr(b, 'text', None) and b.text().upper() == str(faction_label).upper():
                        sel_color = self.theme.get('accent') or self.color_gen.get_next_color()
                        b.setStyleSheet(f"background-color: {sel_color};")
                    else:
                        muted = self.theme.get('secondary') or '#333333'
                        b.setStyleSheet(f"background-color: {muted};")
                except RuntimeError:
                    # widget was deleted by another part of the UI; skip it
                    continue

        # enable era buttons now that faction is fixed
        if hasattr(self, 'era_buttons'):
            # Show only the eras that are allowed for the chosen faction
            faction_key = str(faction_label).upper()
            allowed = self.allowed_eras_by_faction.get(faction_key, [])
            # iterate over a snapshot to avoid touching deleted widgets
            for era, eb in list(getattr(self, 'era_buttons_map', {}).items()):
                if not getattr(eb, 'setVisible', None):
                    continue
                try:
                    if era in allowed:
                        # compute an era-specific color influenced by faction
                        era_color = get_random_button_color(era, faction_enum)
                        era_color = self.color_gen.get_next_color()
                        eb.setStyleSheet(f"background-color: {era_color}; border-radius: 4px;")
                        eb.setVisible(True)
                        eb.setEnabled(True)
                    else:
                        eb.setVisible(False)
                except RuntimeError:
                    # widget was deleted elsewhere; skip
                    continue

        # Ensure launch remains disabled until era is chosen and login completes
        self.launch_btn.setEnabled(self._selected_faction and self._selected_era)
        # If Klingon selected, visually indicate the system is different
        if faction_key == 'KLINGON':
            if hasattr(self, 'launch_btn'):
                self.launch_btn.setText('LAUNCH KLINGON SYSTEM')
                # stronger red accent for Klingon launch
                self.launch_btn.setStyleSheet(f"background-color: #8A1F1F; color: black; border-radius: 6px;")
        else:
            if hasattr(self, 'launch_btn'):
                self.launch_btn.setText('LAUNCH SYSTEM')
                # restore theme-driven color
                lcolor = self.theme.get('accent') or self.color_gen.get_next_color()
                self.launch_btn.setStyleSheet(f"background-color: {lcolor}; border-radius: 6px;")
        
    def select_era(self, era):
        """Обробити вибір епохи: оновити генератор кольорів і тему.

        Встановлює `self._selected_era = True` і активує LAUNCH коли є обидва вибори.
        """
        get_sound_manager().play("acknowledge")
        self.era = era
        # Якщо вже обрана фракція і вона має enum-значення — передамо його
        faction_enum = self.faction_enum
        self.color_gen = LCARSColorGenerator(era, faction_enum)
        self.theme = get_theme(era, faction_enum)
        self._selected_era = True
        print(f"[launcher] era selected -> {self.era}")
        # apply theme preview immediately so launcher reflects epoch choice
        self.apply_theme()

        # After era selection, move user to the login screen to authorize
        # (login will then transition back to launcher and allow LAUNCH).
        self.stack.setCurrentIndex(1)

        # LAUNCH will be enabled once both selections are set and login completes
        try:
            if hasattr(self, 'launch_btn'):
                self.launch_btn.setEnabled(bool(self._selected_faction and self._selected_era and self._authorized))
        except Exception:
            pass

    def launch_desktop(self):
        """Перейти до екрану Desktop і запустити канонічний demo/lcars_demo.py у відокремленому процесі.

        Запускає новий процес з тим же інтерпретатором (`sys.executable`) щоб демон не блокував
        поточний лаунчер. Якщо користувач обрав фракцію й епоху, передаємо їх як `--auto`.
        """
        # Show desktop screen in this launcher
        self.stack.setCurrentIndex(3)

        # Disable the launch button to avoid repeated clicks
        self.launch_btn.setEnabled(False)

        # Play confirmation sound
        get_sound_manager().play('acknowledge')

        # Build command to spawn a faction-specific demo entrypoint.
        # Klingon should launch its own system; others default to canonical demo.
        faction_label = None
        if isinstance(self.faction_enum, FactionEra):
            faction_label = self.faction_enum.name.split('_')[0].upper()
        else:
            faction_label = str(self.faction).upper()

        if faction_label == 'KLINGON':
            demo_path = repo_root / 'demo' / 'lcars_klingon.py'
        else:
            demo_path = repo_root / 'demo' / 'lcars_demo.py'

        cmd = [sys.executable, str(demo_path)]

        # If we have selected faction and era, pass auto payload
        if getattr(self, '_selected_faction', False) and getattr(self, '_selected_era', False):
            # normalize faction label
            if isinstance(self.faction_enum, FactionEra):
                faction_label = self.faction_enum.name.split('_')[0].upper()
            else:
                faction_label = str(self.faction).upper()

            # era key like '25th'
            era_key = self.era.name.split('_')[-1].lower()

            # pass explicit flags so the demo can pick the correct theme
            cmd.append(f"--faction={faction_label}")
            cmd.append(f"--era={era_key}")

        # Spawn detached process so launcher remains interactive
        subprocess.Popen(cmd, cwd=str(repo_root))
        
    def cycle_nodes(self):
        """Анімація вузлів у бічній панелі лаунчера (циклічне оновлення кольору)."""
        self.current_phase = "launcher"
        get_sound_manager().play("ready")
        # Node color cycling only — do not force stack index here
        # Якщо режим --auto: застосовуємо програмні вибори (якщо задані)
        if getattr(self, 'auto_mode', False):
            if self._auto_faction:
                # спробуємо знайти enum у FactionEra, інакше передаємо рядок
                if self._auto_faction in FactionEra.__members__:
                    af = FactionEra[self._auto_faction]
                else:
                    af = None
                # викликаємо select_faction з наданими значеннями
                self.select_faction(self._auto_faction, af)
            if self._auto_era:
                self.select_era(self._auto_era)

    def transition_to_selection(self):
        """Показати на екрані лаунчера (фракції/епохи як кнопки).

        Простий, прямий перехід без надмірних перевірок — кнопки вже є
        на сторінці Launcher і використовують `get_random_button_color`.
        Якщо `auto_mode` увімкнено — застосовуємо програмні вибори.
        """
        get_sound_manager().play("ready")
        print("[launcher] presenting on-screen Faction/Era buttons")
        self.current_phase = "launcher"
        self.stack.setCurrentIndex(2)

        # Простий авто-режим: якщо задано, застосуємо вибори.
        if self.auto_mode:
            if self._auto_faction:
                if self._auto_faction in FactionEra.__members__:
                    af = FactionEra[self._auto_faction]
                else:
                    af = None
                self.select_faction(self._auto_faction, af)
            if self._auto_era:
                self.select_era(self._auto_era)
    def show(self):
        """Центрувати вікно на екрані й показати його."""
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)
        super().show()

def main():
    print("=== UNIFIED LCARS SYSTEM INITIALIZATION ===")
    print("[info] Sequence: Boot -> Selection (Faction->Era) -> Login -> Launcher -> Desktop")
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Register LCARS fonts
    setup_lcars_font()

    # Initialize sound manager
    sound_mgr = get_sound_manager()

    # Create and show unified system
    system = UnifiedLCARSSystem()
    system.show()

    # Support an automatic demo mode: `--auto` will auto-select a faction/era
    # Підтримка автоматичного демонстраційного режиму:
    # Виклик `python demo/demo_launcher.py --auto` автоматично обирає
    # фракцію/епоху (корисно для скринкастів або автоматизованих перевірок).
    if '--auto' in sys.argv:
        # Enable auto-mode on the system so it triggers selection once launcher appears
        system.auto_mode = True
        # allow optional args like `--auto=faction:era` (not required)
        for a in sys.argv:
            if a.startswith('--auto='):
                payload = a.split('=', 1)[1]
                parts = payload.split(':')
                if len(parts) >= 1 and parts[0]:
                    system._auto_faction = parts[0].upper()
                if len(parts) == 2 and parts[1]:
                    # map era string to enum if possible
                    era_key = parts[1].lower()
                    era_enum = None
                    for e in LCARSEra:
                        if e.value == era_key or e.name.lower().endswith(era_key):
                            era_enum = e
                            break
                    if era_enum:
                        system._auto_era = era_enum
    # Запускаємо головний цикл подій Qt та повертаємо код виходу
    return_code = app.exec()
    sys.exit(return_code)


if __name__ == "__main__":
    main()
