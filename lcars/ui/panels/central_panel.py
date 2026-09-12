from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget, QFrame, QSizePolicy, QSplitter
)
from PyQt6.QtCore import Qt

from lcars.ui.base.widgets import LCARSButton
from lcars.ui.terminal import TerminalDrawer
from lcars.ui.onboard_computer import OnboardComputerView
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme
from lcars.engineering.architect import IsolinearArchitect

# Import New Panels
from lcars.ui.panels.bridge_panel import BridgePanel
from lcars.ui.panels.navigation_panel import NavigationPanel
from lcars.ui.panels.communication_panel import CommunicationPanel
from lcars.ui.panels.medical_panel import MedicalPanel
from lcars.ui.panels.database_panel import DatabasePanel
from lcars.ui.panels.programs_panel import ProgramsPanel

class CentralPanel(QWidget):
    """
    Unified central panel (TITAN V4.0): 
    Integrated modes for Bridge, Engineering, Navigation, Comms, Med, DB and Programs.
    """
    def __init__(self, system=None, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.system = system
        self.era = era
        self.faction = faction
        self.theme = get_theme(self.era, self.faction)
        self._build_ui()

    def _build_ui(self):
        # КРОК 1: Базове налаштування фону та головного макета (TITAN CORE)
        bg = self.theme.get("bg", "#000000")
        p = self.theme.get("palette", ["#3366CC"] * 10)
        accent = self.theme.get("accent", "#FFCC00")
        
        self.setStyleSheet(f"background-color: {bg};")
        self.main = QVBoxLayout(self)
        self.main.setContentsMargins(0, 0, 0, 0)
        self.main.setSpacing(0)

        # Header: Mode Selector (ADMIRAL LEVEL 10 AUTHORIZATION)
        header = QFrame()
        header.setMinimumHeight(64)
        header.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        h = QHBoxLayout(header)
        h.setContentsMargins(15, 8, 15, 8)
        h.setSpacing(8)

        # КРОК 2: Побудова кнопок перемикання режимів (BRIDGE, ENGIN, NAV...)
        modes = [
            ("BRIDGE", 0, p[3] if len(p) > 3 else p[0]),   # Командний місток
            ("ENGINEERING", 1, p[4] if len(p) > 4 else p[1]), # Інженерія (Архітектор)
            ("CONSTRUCT", 2, p[5] if len(p) > 5 else p[2]), # Конструктор інтерфейсів
            ("NAVIGATION", 3, p[0]), # Навігація
            ("COMMS", 4, p[6] if len(p) > 6 else p[0]),      # Зв'язок
            ("MEDICAL", 5, p[7] if len(p) > 7 else p[0]),    # Медицина
            ("DATABASE", 6, p[8] if len(p) > 8 else p[0]),   # База даних
            ("PROGRAMS", 7, p[9] if len(p) > 9 else p[0])    # Програми
        ]
        
        self.mode_btns = []
        for text, idx, col in modes:
            btn = LCARSButton(text, col, era=self.era, faction=self.faction)
            btn.setMinimumHeight(35)
            btn.clicked.connect(lambda checked, i=idx: self.mode_stack.setCurrentIndex(i))
            h.addWidget(btn)
            self.mode_btns.append(btn)

        h.addStretch()

        # КРОК 3: Додавання системних перемикачів консолі та AI
        self.terminal_btn = LCARSButton("CONSOLE", p[1] if len(p) > 1 else "#2288AA", era=self.era)
        self.terminal_btn.setMinimumHeight(35)
        self.terminal_btn.clicked.connect(self._toggle_terminal)
        h.addWidget(self.terminal_btn)

        self.onboard_btn = LCARSButton("AI TERMINAL", p[2] if len(p) > 2 else '#AA66FF', era=self.era)
        self.onboard_btn.setMinimumHeight(35)
        self.onboard_btn.clicked.connect(self._toggle_onboard)
        h.addWidget(self.onboard_btn)

        self.main.addWidget(header)

        # КРОК 4: Ініціалізація стек-віджета для перемикання між панелями
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(5)

        self.mode_stack = QStackedWidget()
        
        # Режим 0: Командний місток
        self.bridge_view = BridgePanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.bridge_view)

        # Режим 1: Ізолінійна архітектура (Інженерія)
        self.architect = IsolinearArchitect(parent=self)
        self.mode_stack.addWidget(self.architect)

        # Режим 2: Конструктор інтерфейсів
        from lcars.engineering.constructor import InterfaceConstructor
        self.constructor = InterfaceConstructor(self.system, parent=self)
        self.mode_stack.addWidget(self.constructor)

        # Режим 3: Навігація
        self.nav_view = NavigationPanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.nav_view)

        # Режим 4: Комунікації (Мовна матриця)
        self.comms_view = CommunicationPanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.comms_view)

        # Режим 5: Медицина (Біо-сканери)
        self.med_view = MedicalPanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.med_view)

        # Режим 6: База даних (Бібліотека)
        self.db_view = DatabasePanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.db_view)

        # Режим 7: Програмний менеджер
        self.prog_view = ProgramsPanel(self, self.era, self.faction)
        self.mode_stack.addWidget(self.prog_view)

        # Режим 8: Бортовий комп'ютер (AI)
        self.onboard = OnboardComputerView(parent=self)
        self.mode_stack.addWidget(self.onboard)

        splitter.addWidget(self.mode_stack)

        # КРОК 5: Права панель діагностичного фіду (Diag Feed)
        border_col = self.theme.get("border", "#333")
        diag = QFrame()
        diag.setMinimumWidth(220)
        diag.setStyleSheet(f"border-left: 1px solid {border_col}; background: #050505;")
        dlay = QVBoxLayout(diag)
        lbl_diag = QLabel("◤ DIAGNOSTIC FEED")
        lbl_diag.setStyleSheet(f"color: {p[4] if len(p) > 4 else '#4BBEBF'}; {get_lcars_font_style(12, 'normal')}")
        dlay.addWidget(lbl_diag)
        
        self.feed = QLabel("◤ SYSTEM: TITAN ACTIVE\n◤ NEURAL LINK: STABLE\n◤ CORE: OPTIMAL\n◤ ACCESS: AUTHORIZED")
        self.feed.setStyleSheet(f"color: {p[5] if len(p) > 5 else '#66FF66'}; {get_lcars_font_style(10, 'normal')}")
        dlay.addWidget(self.feed)
        dlay.addStretch()
        
        splitter.addWidget(diag)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        self.main.addWidget(splitter, 1)

        # КРОК 6: Нижній висувний термінал (Console Drawer)
        self.terminal = TerminalDrawer(parent=self, width=900)
        self.terminal.setMaximumHeight(0)
        self.terminal.setVisible(False)
        self.main.addWidget(self.terminal)

        # Footer Status
        footer = QFrame()
        footer.setFixedHeight(28)
        flay = QHBoxLayout(footer)
        flay.setContentsMargins(15, 0, 15, 0)
        lbl_foot = QLabel("◢ LCARS TITAN COMMAND // SYSTEM: ODYSSEY v4.0 // STATUS: NOMINAL")
        lbl_foot.setStyleSheet(f"color: white; {get_lcars_font_style(11, 'normal')}")
        flay.addWidget(lbl_foot)
        flay.addStretch()
        self.main.addWidget(footer)

    def _toggle_terminal(self):
        visible = self.terminal.isVisible()
        self.terminal.setVisible(not visible)
        self.terminal.setMaximumHeight(300 if not visible else 0)
        self.terminal_btn.setChecked(not visible)

    def _toggle_onboard(self):
        # AI toggle: move to index 8 in stack
        if self.mode_stack.currentIndex() == 8:
            self.mode_stack.setCurrentIndex(0)
        else:
            self.mode_stack.setCurrentIndex(8)
        self.onboard_btn.setChecked(self.mode_stack.currentIndex() == 8)

