"""
LCARS ENGINEERING STATION - DIAGNOSTIC CORE
SYSTEM MODULE: UI-ENG-15
PROTOCOL: ISOLINEAR / NEURAL LINK INTERFACE
DESCRIPTION: Primary engineering interface for managing system cores and neural links.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QMenu
from PyQt6.QtCore import Qt, QPoint

from lcars.ui.base.widgets import LCARSButton, DataBlock, StatBar
from lcars.ui.panels.central import CentralPanel
from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.portable import PortablePADD

import logging
logger = logging.getLogger("lcars.ui.engineering")

class EngineeringView(QWidget):
    """
    Інженерна панель для управління ізолінійними чіпами та нейронним зв'язком.
    Використовує CentralPanel як основний компонент.
    Тепер віджет можна від'єднувати у портативний ПАДД.
    """
    def __init__(self, system=None, era=LCARSEra.LCARS_25TH, faction=None, parent=None, is_standalone=False):
        super().__init__(parent)
        # КРОК 1: Ініціалізація системи та параметрів ери
        self.system = system
        self.era = era
        self.faction = faction
        self.is_standalone = is_standalone
        self.theme = get_theme(era, faction)
        
        self.init_ui()

    def init_ui(self):
        # КРОК 2: Налаштування головного макета
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # --- HEADER CONTROL (Тільки якщо не портативний режим) ---
        if not self.is_standalone:
            header = QHBoxLayout()
            
            # ЧИСТИЙ заголовок без контурів
            self.title_lbl = QLabel("◤ MAIN ENGINEERING // CORE MONITORING")
            primary_color = self.theme.get('button_colors', ['#FF9900'])[0] if isinstance(self.theme.get('button_colors'), list) else self.theme.get('button_colors', '#FF9900')
            self.title_lbl.setStyleSheet(f"color: {primary_color}; {get_lcars_font_style(20, 'normal')}")
            header.addWidget(self.title_lbl, 1)
            
            # Кнопка для від'єднання модуля (Портативність)
            button_color = self.theme.get('button_colors', ['#FFAA00'])[1] if isinstance(self.theme.get('button_colors'), list) and len(self.theme.get('button_colors', [])) > 1 else self.theme.get('button_colors', '#FFAA00')
            self.btn_pop = LCARSButton("EXPORT PADD", button_color, shape="pill")
            self.btn_pop.setMinimumSize(140, 26)
            self.btn_pop.clicked.connect(self.pop_out)
            header.addWidget(self.btn_pop)
            
            layout.addLayout(header)
            
            # Тонка лінія-розділювач замість масивного контуру
            sep = QFrame()
            sep.setMinimumHeight(1)
            sep.setStyleSheet(f"background: {primary_color}55;")
            layout.addWidget(sep)
        
        # КРОК 3: Додавання центральної інженерної панелі (CentralPanel)
        self.central = CentralPanel(system=self.system, parent=self)
        layout.addWidget(self.central, 1)
        
        # КРОК 4: Додатковий опис статусу інженерних систем
        status_lbl = QLabel("ENGINEERING STATUS: NOMINAL // CORE STABILITY: 99.8%")
        status_lbl.setStyleSheet(f"color: {primary_color}; {get_lcars_font_style(14, 'normal')}")
        layout.addWidget(status_lbl, alignment=Qt.AlignmentFlag.AlignRight)

    def pop_out(self):
        """Перенесення інженерного віджета у портативний ПАДД (Адаптивність)."""
        from lcars.ui.base.portable import PortablePADD
        
        # Створюємо ПАДД як незалежне вікно
        padd = PortablePADD(
            title="◤ PORTABLE ENGINEERING MONITOR", 
            era=self.era, 
            faction=self.faction, 
            parent=None # Робимо top-level для справжньої портативності
        )
        
        # Створюємо контент
        cloned_view = EngineeringView(
            system=self.system, 
            era=self.era, 
            faction=self.faction, 
            is_standalone=True
        )
        
        padd.set_content(cloned_view)
        padd.resize(950, 650)
        padd.show()
        
        from lcars.modules.sound_manager import get_sound_manager
        get_sound_manager().play("acknowledge")
