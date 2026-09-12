# LCARS :: MINIMAL OS :: ENGINEERING SANDBOX
# ===============================================
# Ця система забезпечує чисте середовище для розробки та експериментів ШІ.
# Дизайн: Блек-фон з периферичною рамкою LCARS.
# ===============================================
import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSplitter, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent

# Додавання кореневої папки проєкту
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.core.board_computer import BoardComputer, get_computer
from lcars.core.kernel import EventType
from lcars.ui.tools.terminal import LCARSTerminal
from lcars.ui.onboard import AIConfigPanel, SystemStatusPanel
from lcars.ui.base.portable import PortablePADD
from lcars.ui.base.widgets import LCARSButton, StatBar, DataBlock
from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_theme, setup_lcars_font
import importlib
import importlib.util

# Load journal module only if it exists (no try/except)
_spec = importlib.util.find_spec('lcars.system.journal')
if _spec is not None:
    system_journal = importlib.import_module('lcars.system.journal')
else:
    system_journal = None


def load_era_from_config(default=LCARSEra.LCARS_25TH):
    """Load era from config file, return an `LCARSEra` enum value.

    Keeps config-read logic in one place to avoid duplication.
    """
    config_path = Path(__file__).parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        era_str = config.get('era', '25th').upper()
        return getattr(LCARSEra, era_str, default)
    return default
import plugins

class Workspace(QWidget):
    """
    Central workspace that manages floating LCARS panels (PADDs).
    """
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.panels = []
        self.setStyleSheet("background-color: black;")
        
    def spawn_padd(self, title, widget, x=50, y=50, w=None, h=None):
        """Create and show a new floating PADD.

        If width/height not supplied, use a percentage of workspace size
        so layouts remain adaptive instead of hard-fixed pixels.
        """
        padd = PortablePADD(title=title, era=self.era, faction=self.faction, parent=self)
        padd.set_content(widget)
        # adaptive sizing
        ww = self.width() or 800
        hh = self.height() or 600
        if w is None:
            w = max(300, int(ww * 0.4))
        if h is None:
            h = max(200, int(hh * 0.35))
        padd.resize(w, h)
        padd.setMinimumSize(200, 150)
        padd.setMaximumSize(int(ww * 0.9), int(hh * 0.9))
        padd.move(x, y)
        padd.show()
        self.panels.append(padd)
        return padd

    def resizeEvent(self, a0):
        """Adaptive rearrangement on resize."""
        super().resizeEvent(a0)
        self.auto_arrange()

    def auto_arrange(self):
        """Simple logic to ensure panels don't go off-screen."""
        w, h = self.width(), self.height()
        if w < 100 or h < 100: return
        
        for padd in self.panels:
            px, py = padd.x(), padd.y()
            pw, ph = padd.width(), padd.height()
            
            # Constrain to workspace
            nx = max(10, min(px, w - pw - 10))
            ny = max(10, min(py, h - ph - 10))
            
            if nx != px or ny != py:
                padd.move(nx, ny)

class MinimalSandbox(QMainWindow):
    """
    25th Century Adaptive Workspace: Floating PADDs, No Fixed Contours.
    """
    def __init__(self, system, era=None):
        super().__init__()
        self.system = system
        # Використовуємо еру з конфігурації або передану
        if era is None:
            self.era = load_era_from_config()
        else:
            self.era = era

        self.theme = get_theme(self.era)
        self.current_mode = "standard"  # standard, engineering, tactical, science

        # Initialize workspace for floating PADDs
        self.workspace = Workspace(era=self.era, parent=self)

        self.setWindowTitle("LCARS :: ADAPTIVE WORKSPACE")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        self._init_ui()

        # Connect to Event Bus for dynamic UI updates
        computer = get_computer()
        if computer and hasattr(computer, 'event_bus'):
            computer.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self.on_ui_event)

    def set_mode(self, mode):
        """Перемикання режимів роботи системи"""
        self.current_mode = mode
        # Оновлюємо еру відповідно до режиму
        if mode == "tactical":
            self.era = LCARSEra.LCARS_24ST
        elif mode == "engineering":
            self.era = LCARSEra.LCARS_24TH
        elif mode == "science":
            self.era = LCARSEra.TCARS_29TH
        elif mode == "ai":
            # AI режим використовує 25th еру за замовчуванням
            self.era = LCARSEra.LCARS_25TH
            # Перебудовуємо інтерфейс для AI режиму
            self._rebuild_for_ai_mode()
            return
        else:
            # Повертаємо еру з конфігурації для standard режиму
            self.era = load_era_from_config()
            # Повертаємо до стандартного layout
            self._rebuild_standard_layout()
        
        self.theme = get_theme(self.era)
        self._update_ui_theme()

    def _rebuild_for_ai_mode(self):
        """Перебудовує інтерфейс для AI режиму"""
        # Очищуємо основний layout
        central_widget = self.centralWidget()
        if isinstance(central_widget, QWidget):
            layout = central_widget.layout()
            if layout is not None:
                while layout.count():
                    child = layout.takeAt(0)
                    widget = child.widget()
                    if widget is not None:
                        widget.deleteLater()
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = central_widget.layout()
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
        
        # Створюємо AI layout
        from lcars.ui.onboard import OnboardComputerView as OnboardComputer
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Панель режимів
        mode_panel = QHBoxLayout()
        mode_label = QLabel("MODE:")
        mode_label.setStyleSheet(f"color: {self.theme.get('text', '#FFFFFF')}; font-weight: bold;")
        mode_panel.addWidget(mode_label)
        
        modes = [("STANDARD", "standard"), ("ENGINEERING", "engineering"), 
                ("TACTICAL", "tactical"), ("SCIENCE", "science"), ("AI", "ai")]
        
        for name, mode_id in modes:
            btn = LCARSButton(name, self.theme['accent'] if mode_id == self.current_mode else "#333333", shape="rect")
            btn.clicked.connect(lambda checked, m=mode_id: self.set_mode(m))
            mode_panel.addWidget(btn)
        
        mode_panel.addStretch()
        main_layout.addLayout(mode_panel)
        
        # AI спліттер
        ai_splitter = QSplitter(Qt.Orientation.Vertical)
        ai_splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.theme['palette'][1]}; }}")
        
        # AI компонент
        from lcars.ui.onboard_real import RealAIInterface, CommandInterface
        
        # Створюємо AI інтерфейс
        ai_interface = RealAIInterface()
        
        # Створюємо контейнер для AI
        ai_container = QWidget()
        ai_layout = QVBoxLayout(ai_container)
        
        # Додаємо командний інтерфейс
        command_interface = CommandInterface(ai_interface)
        ai_layout.addWidget(command_interface)
        
        ai_splitter.addWidget(ai_container)
        
        # Термінал
        term_widget = LCARSTerminal(parent=self, era=self.era)
        ai_splitter.addWidget(term_widget)
        
        main_layout.addWidget(ai_splitter)
        self.theme = get_theme(self.era)
        self._update_ui_theme()

    def _rebuild_standard_layout(self):
        """Повертає до стандартного layout"""
        # Перебудовуємо стандартний інтерфейс
        self._init_ui()

    def _update_ui_theme(self):
        """Оновлює тему всього інтерфейсу"""
        accent_color = self.theme.get('accent', '#FF9900')
        
        # Оновлюємо спліттери
        if hasattr(self, 'main_splitter'):
            self.main_splitter.setStyleSheet(f"""
                QSplitter::handle {{
                    background-color: {accent_color};
                    width: 2px;
                }}
                QSplitter::handle:vertical {{
                    height: 2px;
                }}
            """)
        
        if hasattr(self, 'right_splitter'):
            self.right_splitter.setStyleSheet(f"""
                QSplitter::handle:vertical {{
                    background-color: {accent_color};
                    height: 2px;
                }}
            """)

    def on_ui_event(self, event):
        """Handle incoming UI events, like spawning new panels."""
        if event.source == 'workspace' and isinstance(event.data, dict):
            action = event.data.get('action')
            if action == 'spawn_padd':
                title = event.data.get('title', '◤ AI GENERATED')
                components = event.data.get('components', [])
                self._handle_ui_builder(title, components)

    def _handle_ui_builder(self, title, components):
        """Build a widget from components and spawn it."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        for comp in components:
            c_type = comp.get('type')
            label = comp.get('label', '')
            color = comp.get('color')
            value = comp.get('value', '')

            if c_type == 'button':
                btn = LCARSButton(label, color=color, era=self.era)
                layout.addWidget(btn)
            elif c_type == 'stat':
                stat = StatBar(label, color or self.theme.get('accent', '#3366CC'))
                stat.setValue(int(value) if value.isdigit() else 0)
                layout.addWidget(stat)
            elif c_type == 'data':
                data = DataBlock(label, value, color or self.theme.get('accent', '#3366CC'))
                layout.addWidget(data)
            elif c_type == 'label':
                lbl = QLabel(label.upper())
                lbl.setStyleSheet(f"color: {color or 'white'}; font-family: 'LCARS'; font-size: 16px;")
                layout.addWidget(lbl)

        layout.addStretch()
        # Spawn in a reasonable location (cascading or random)
        import random
        rx = random.randint(100, 400)
        ry = random.randint(100, 400)
        # Ensure workspace is visible and parented
        if not self.workspace.isVisible():
            self.workspace.setParent(self)
            self.workspace.setGeometry(self.geometry())
            self.workspace.show()
        self.workspace.spawn_padd(title, container, x=rx, y=ry, w=300, h=len(components)*50 + 60)

    def _init_ui(self):
        # Створюємо головний layout
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Панель режимів
        mode_panel = QHBoxLayout()
        mode_label = QLabel("MODE:")
        mode_label.setStyleSheet(f"color: {self.theme.get('text', '#FFFFFF')}; font-weight: bold;")
        mode_panel.addWidget(mode_label)
        
        modes = [
            ("STANDARD", "standard"),
            ("ENGINEERING", "engineering"), 
            ("TACTICAL", "tactical"),
            ("SCIENCE", "science"),
            ("AI", "ai")
        ]
        
        for name, mode_id in modes:
            btn = LCARSButton(name, self.theme['accent'] if mode_id == self.current_mode else "#333333", shape="rect")
            btn.clicked.connect(lambda checked, m=mode_id: self.set_mode(m))
            mode_panel.addWidget(btn)
        
        mode_panel.addStretch()
        main_layout.addLayout(mode_panel)
        
        # Створюємо спліттер для адаптивного розміщення панелей
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setSizes([1, 1])  # Рівні пропорції для адаптивності
        
        # Ліва панель - термінал (більший)
        from lcars.ui.tools.terminal import LCARSTerminal
        term_widget = LCARSTerminal(parent=self, era=self.era)
        term_widget.setStyleSheet("background: transparent; border: none;")
        
        # Обгортаємо термінал у контейнер для кращого вигляду
        term_container = QWidget()
        term_layout = QVBoxLayout(term_container)
        term_layout.setContentsMargins(5, 5, 5, 5)
        term_layout.addWidget(term_widget)
        
        # Права панель - спліттер для AI та систем монітору
        self.right_splitter = QSplitter(Qt.Orientation.Vertical)
        self.right_splitter.setChildrenCollapsible(False)
        
        # AI Configuration
        ai_cfg = AIConfigPanel(era=self.era)
        ai_container = QWidget()
        ai_layout = QVBoxLayout(ai_container)
        ai_layout.setContentsMargins(5, 5, 5, 5)
        ai_layout.addWidget(ai_cfg)
        
        # System Monitor
        sys_mon = SystemStatusPanel(era=self.era)
        sys_container = QWidget()
        sys_layout = QVBoxLayout(sys_container)
        sys_layout.setContentsMargins(5, 5, 5, 5)
        sys_layout.addWidget(sys_mon)
        
        # Додаємо панелі до спліттерів
        self.right_splitter.addWidget(ai_container)
        self.right_splitter.addWidget(sys_container)
        self.right_splitter.setSizes([1, 1])  # Рівні пропорції для адаптивності
        
        self.main_splitter.addWidget(term_container)
        self.main_splitter.addWidget(self.right_splitter)
        self.main_splitter.setSizes([2, 1])  # Термінал трохи більший
        
        # Додаємо спліттер до головного layout
        main_layout.addWidget(self.main_splitter)
        
        # Стилізуємо спліттери відповідно до системної теми
        accent_color = self.theme.get('accent', '#FF9900')
        self.main_splitter.setStyleSheet(f"""
            QSplitter::handle {{
                background-color: {accent_color};
                width: 2px;
            }}
            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """)
        
        self.right_splitter.setStyleSheet(f"""
            QSplitter::handle:vertical {{
                background-color: {accent_color};
                height: 2px;
            }}
        """)
        
        # Стилізуємо контейнери - мінімалістичний стиль без контурів
        for container in [term_container, ai_container, sys_container]:
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: rgba(5, 5, 8, 245);
                    border: none;
                    border-radius: 4px;
                }}
            """)

    def keyPressEvent(self, a0):
        if isinstance(a0, QKeyEvent) and a0.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(a0)

class SystemWrapper:
    def __init__(self, computer):
        self.board_computer = computer

def main():
    import time
    start_time = time.time()
    
    if sys.platform == "win32":
        import ctypes
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "kernel32") and hasattr(ctypes.windll.kernel32, "SetConsoleOutputCP"):
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)

    print("◤ LCARS INITIALIZATION SEQUENCE")
    print("=" * 50)
    
    # Крок 1: Ініціалізація QApplication (15%)
    print("[15%] Initializing Qt Application...", end="\r")
    app = QApplication(sys.argv)
    setup_lcars_font()
    if system_journal:
        system_journal.record('startup', 'Qt application initialized')
    print("[25%] Font system loaded          ", end="\r")
    
    # Крок 2: Завантаження теми (40%)
    print("[40%] Loading theme configuration...", end="\r")
    theme = get_theme(LCARSEra.LCARS_25TH)
    print("[55%] Theme system active         ", end="\r")
    
    # Крок 3: Ініціалізація бортового комп'ютера (70%)
    print("[70%] Initializing Board Computer...", end="\r")
    computer = get_computer() or BoardComputer()
    if not hasattr(computer, 'is_running') or not computer.is_running:
        computer.start()
    if system_journal:
        system_journal.record('startup', 'Board Computer online')
    print("[80%] Board Computer online        ", end="\r")
    
    # Крок 4: Плагіни та інтерфейс (90%)
    print("[90%] Finalizing initialization...", end="\r")
    system = SystemWrapper(computer)
    plugins.set_system(system)
    window = MinimalSandbox(system)
    if system_journal:
        system_journal.record('startup', 'UI components initialized')
    window.showFullScreen()
    
    # Крок 5: Застосування стилів (100%)
    print("[95%] Applying styles...", end="\r")
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {theme.get('bg', '#000000')};
            border: none;
        }}
        QWidget {{
            background-color: {theme.get('bg', '#000000')};
            color: {theme.get('text', '#FFFFFF')};
        }}
        QSplitter::handle {{
            background-color: {theme.get('accent', '#FF9900')};
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
    """)
    
    load_time = time.time() - start_time
    print(f"[100%] SYSTEM READY - Load time: {load_time:.2f}s")
    print("=" * 50)
    print("◤ LCARS :: ADAPTIVE WORKSPACE :: ONLINE")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
