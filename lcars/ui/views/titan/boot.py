"""
LCARS Boot View - Екран ініціалізації системи.
Відповідає за початкове завантаження та візуалізацію протоколів.
"""
import random
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from lcars.themes.palette import LCARSEra, LCARSColorGenerator
from lcars.themes.theme import get_lcars_font_style
from lcars.modules.sound_manager import get_sound_manager

logger = logging.getLogger("lcars.ui.boot")

class BootView(QWidget):
    """Автентична послідовність завантаження LCARS з використанням алгоритмічних кольорів."""
    finished = pyqtSignal()
    # Сигнал вибору: (назва фракції, назва ери)
    selection_made = pyqtSignal(str, str)

    def __init__(self, era=LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        # Генератор кольорів для динамічного ефекту "живої" панелі
        self.color_gen = LCARSColorGenerator(era)
        self.progress = 0
        
        # Кроки ініціалізації
        self.steps = [
            "SCANNING CORE BUFFER...",
            "INITIALIZING NEURAL NETS...",
            "CALIBRATING OPTICAL DATA...",
            "ESTABLISHING SECURE PROTOCOLS...",
            "READY FOR INTERFACE.",
            "ACCESS GRANTED. WELCOME ABOARD."
        ]
        
        self.setup_ui()
        self.log.setText("")
        
        # Алгоритмічний таймер оновлення
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_boot)
        # Timer will be started by launcher when initializing
        get_sound_manager().play("acknowledge")

    def apply_theme(self):
        """Зовнішній метод для синхронізації теми перед початком завантаження."""
        self.color_gen = LCARSColorGenerator(self.era, getattr(self, 'faction', None))
        self.setup_ui()

    def start_boot(self):
        """Зовнішній запуск бут-секвенції з реальною ініціалізацією."""
        self.apply_theme()
        self.progress = 0
        get_sound_manager().play("acknowledge")
        
        # Реальна ініціалізація компонентів системи
        self.initialize_system_components()
        
        self.timer.start(150)

    def initialize_system_components(self):
        """Реальна ініціалізація компонентів системи."""
        if True:
            # Ініціалізація ядра системи
            if True:
                from plugins import get_system
                system = get_system()
                if system and not system.is_running:
                    system.start()
                    print("[BOOT] Core system initialized")
            if False: # Removed except block
                print("[BOOT] Plugins system not available, continuing...")
            
            # Ініціалізація графічних компонентів
            from lcars.themes.theme import setup_lcars_font
            setup_lcars_font()
            print("[BOOT] Graphics components initialized")
            
            # Ініціалізація кольорового менеджера
            from lcars.system.color import COLOR_MANAGER
            from lcars.themes.palette import LCARSEra
            COLOR_MANAGER.set_context(LCARSEra.LCARS_25TH, None)
            print("[BOOT] Color manager initialized")
            
            # Ініціалізація звукової системи
            from lcars.modules.sound_manager import get_sound_manager
            sound_manager = get_sound_manager()
            print("[BOOT] Sound system initialized")
            
        if False: # Removed except block
            print(f"[BOOT] Component initialization error: {e}")

    def setup_ui(self):
        """Ініціалізація графічного інтерфейсу з дотриманням стандартів LCARS."""
        if not self.layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(5)
        else:
            # Очищення існуючого макету
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())
            clear_layout(self.main_layout)

        c_lay = self.main_layout
        
        primary = self.color_gen.get_next_color()
        secondary = self.color_gen.get_next_color()
        
        # --- TOP HEADER (Clean Industrial Style) ---
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Left elbow (keeps update_boot reference consistent)
        self.h_elb = QFrame()
        self.h_elb.setMinimumSize(180, 60)
        self.h_elb.setStyleSheet(f"background-color: {primary}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
        header.addWidget(self.h_elb)
        
        self.title_fr = QFrame()
        self.title_fr.setMinimumHeight(60)
        self.title_fr.setStyleSheet(f"background: {primary}; border-radius: 6px;")
        tl_lay = QHBoxLayout(self.title_fr)
        tl_lay.setContentsMargins(20, 0, 20, 0)
        
        lbl = QLabel("LCARS SYSTEM - INITIALIZATION")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'bold')}; border: none;")
        tl_lay.addWidget(lbl)
        tl_lay.addStretch()
        
        # Simple Cap instead of elbow
        h_cap = QFrame()
        h_cap.setMinimumSize(60, 60)
        h_cap.setStyleSheet(f"background: {primary}88; border-radius: 6px;")
        
        header.addWidget(self.title_fr, 1)
        header.addWidget(h_cap)
        c_lay.addLayout(header)

        # --- MID AREA ---
        mid = QHBoxLayout()
        mid.setSpacing(15)
        
        # Left Info Bar (Clean)
        self.sb = QFrame()
        self.sb.setMinimumWidth(120)
        self.sb.setStyleSheet(f"background: {secondary}44; border: 1px solid {secondary}; border-radius: 6px;")
        mid.addWidget(self.sb)

        
        term_lay = QVBoxLayout()
        term_lay.setContentsMargins(20, 20, 20, 20)
        self.step_lbl = QLabel("INITIALIZING...")
        self.step_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(28, 'normal')}; border: none;")
        term_lay.addWidget(self.step_lbl)
        
        self.log = QLabel("> BOOT_MODE: NOMINAL")
        self.log.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(18, 'normal')}; border: none;")
        term_lay.addWidget(self.log)
        term_lay.addStretch()
        mid.addLayout(term_lay, 1)
        c_lay.addLayout(mid, 1)

        # --- FOOTER ---
        footer_lay = QHBoxLayout()
        footer_bar = QFrame()
        footer_bar.setMinimumHeight(30)
        footer_bar.setStyleSheet(f"background: {primary}; border-radius: 2px;")
        footer_lay.addWidget(footer_bar, 1)
        
        elb_br = QFrame()
        elb_br.setMinimumSize(140, 50)
        elb_br.setStyleSheet(f"background: {primary}; border-bottom-right-radius: 40px; border-top-right-radius: 4px;")
        footer_lay.addWidget(elb_br)
        c_lay.addLayout(footer_lay)

    def update_boot(self):
        """Оновлення прогресу завантаження з ефектом 'живої' консолі."""
        self.progress += 1
        
        if self.progress % 10 == 0:
            step_idx = min(self.progress // 20, len(self.steps)-1)
            current_step = self.steps[step_idx]
            self.step_lbl.setText(current_step)
            # Додаємо рандомні дані в консоль (ефект активності)
            self.log.setText(f"{self.log.text()}\n0x{random.randint(1000, 9999):X} :: DATA_LINK_STABLE")
            self.log.setWordWrap(True)
            get_sound_manager().play("click")
            
            # Оновлення кольорів для ефекту "живої" системи (алгоритмічна рандомізація)
            next_col = self.color_gen.get_next_color()
            self.h_elb.setStyleSheet(f"background-color: {next_col}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.sb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 80px;")

        if self.progress >= 100:
            print(f"[BOOT] Boot complete! Progress={self.progress}, stopping timer")
            self.timer.stop()
            get_sound_manager().play("ready")
            QTimer.singleShot(1000, self.finished.emit)
