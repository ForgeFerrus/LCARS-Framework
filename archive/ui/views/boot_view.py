"""
LCARS Boot View - Екран ініціалізації системи.
Відповідає за початкове завантаження та візуалізацію протоколів.
"""
import random
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from lcars.themes.lcars_palette import LCARSEra, get_lcars_font_style, LCARSColorGenerator
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
        self.timer.start(40) # Висока швидкість для плавності
        get_sound_manager().play("acknowledge")

    def setup_ui(self):
        """Ініціалізація графічного інтерфейсу з дотриманням стандартів LCARS."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget()
        container.setFixedSize(900, 500)
        c_lay = QVBoxLayout(container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- ВЕРХНЯ ЧАСТИНА (Header) ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = QFrame()
        self.h_elb.setFixedSize(180, 60)
        # Динамічний колір від генератора
        self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
        header.addWidget(self.h_elb)
        
        self.title_fr = QFrame()
        self.title_fr.setFixedHeight(60)
        self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        tl_lay = QHBoxLayout(self.title_fr)
        lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl_lay.addWidget(lbl)
        header.addWidget(self.title_fr, 1)
        
        self.h_cap = QFrame()
        self.h_cap.setFixedSize(40, 60)
        self.h_cap.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-right-radius: 30px; border-bottom-right-radius: 4px;")
        header.addWidget(self.h_cap)
        c_lay.addLayout(header)

        # --- ЦЕНТРАЛЬНА ЧАСТИНА (Mid) ---
        mid = QHBoxLayout()
        mid.setSpacing(4)
        
        self.sb = QFrame()
        self.sb.setFixedWidth(180)
        self.sb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 60px;")
        mid.addWidget(self.sb)
        
        term = QVBoxLayout()
        term.setContentsMargins(20, 10, 10, 10)
        self.step_lbl = QLabel("INITIALIZING...")
        self.step_lbl.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(24, 'normal')}")
        term.addWidget(self.step_lbl)
        
        self.log = QLabel("> BOOT_MODE: NOMINAL")
        self.log.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}")
        self.log.setWordWrap(True)
        term.addWidget(self.log)
        term.addStretch()
        
        mid.addLayout(term, 1)
        c_lay.addLayout(mid, 1)

        # --- ФУТЕР (Footer) ---
        self.footer = QFrame()
        self.footer.setFixedHeight(30)
        self.footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        c_lay.addWidget(self.footer)

        # Центрування всього віджета
        self.layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(container)
        h_center.addStretch()
        self.layout.addLayout(h_center)
        self.layout.addStretch()

    def update_boot(self):
        """Оновлення прогресу завантаження з ефектом 'живої' консолі."""
        self.progress += 1
        
        if self.progress % 10 == 0:
            step_idx = min(self.progress // 20, len(self.steps)-1)
            current_step = self.steps[step_idx]
            self.step_lbl.setText(current_step)
            # Додаємо рандомні дані в консоль (ефект активності)
            self.log.setText(f"{self.log.text()}\n0x{random.randint(1000, 9999):X} :: DATA_LINK_STABLE")
            get_sound_manager().play("click")
            
            # Рандомні коливання кольорів панелей (ефект пульсації)
            self.h_elb.update_color(self.color_gen.get_next_color()) if hasattr(self.h_elb, "update_color") else self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
            self.title_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")

        if self.progress >= 100:
            self.timer.stop()
            get_sound_manager().play("ready")
            QTimer.singleShot(1000, self.finished.emit)
