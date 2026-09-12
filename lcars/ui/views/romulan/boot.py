"""
LCARS Romulan Boot View - Екран ініціалізації Ромуланської імперії.
Тайний і елегантний дизайн з зеленими відтінками.
"""
import random
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from lcars.themes.palette import LCARSEra, LCARSColorGenerator
from lcars.themes.theme import get_lcars_font_style
from lcars.modules.sound_manager import get_sound_manager

logger = logging.getLogger("lcars.ui.romulan.boot")

class RomulanBootView(QWidget):
    """Ромуланська послідовність завантаження з таємничою зеленою темою."""
    finished = pyqtSignal()
    selection_made = pyqtSignal(str, str)

    def __init__(self, era=LCARSEra.PCARS_23RD):
        super().__init__()
        self.era = era
        # Ромуланський генератор кольорів (зелені відтінки)
        self.color_gen = LCARSColorGenerator(era)
        self.progress = 0
        
        # Кроки ініціалізації ромуланською мовою
        self.steps = [
            "SCANNING SHADOW CORE...",
            "INITIALIZING CLOAKING SYSTEMS...",
            "CALIBRATING DECEPTION PROTOCOLS...",
            "ESTABLISHING TAL SHAR NETWORK...",
            "READY FOR STEALTH OPERATIONS.",
            "ACCESS GRANTED. WELCOME OFFICER."
        ]
        
        self.setup_ui()
        # Лог область буде створена в setup_ui
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_boot)
        get_sound_manager().play("acknowledge")

    def apply_theme(self):
        """Зовнішній метод для синхронізації теми."""
        self.color_gen = LCARSColorGenerator(self.era, getattr(self, 'faction', None))
        self.setup_ui()

    def start_boot(self):
        """Запуск бут-секвенції з реальною ініціалізацією."""
        self.apply_theme()
        self.progress = 0
        get_sound_manager().play("acknowledge")
        
        # Реальна ініціалізація компонентів системи
        self.initialize_system_components()
        
        self.timer.start(150)  # Спокійний темп для таємничості

    def initialize_system_components(self):
        """Реальна ініціалізація компонентів системи в ромуланському стилі."""
        if True:
            # Ініціалізація ядра системи
            if True:
                from plugins import get_system
                system = get_system()
                if system and not system.is_running:
                    system.start()
                    print("[ROMULAN BOOT] Shadow core system initialized")
            if False: # Removed except block
                print("[ROMULAN BOOT] Plugins system not available, continuing...")
            
            # Ініціалізація графічних компонентів
            from lcars.themes.theme import setup_lcars_font
            setup_lcars_font()
            print("[ROMULAN BOOT] Stealth graphics initialized")
            
            # Ініціалізація кольорового менеджера
            from lcars.system.color import COLOR_MANAGER
            from lcars.themes.palette import LCARSEra
            COLOR_MANAGER.set_context(LCARSEra.PCARS_23RD, None)
            print("[ROMULAN BOOT] Shadow color scheme initialized")
            
            # Ініціалізація звукової системи
            from lcars.modules.sound_manager import get_sound_manager
            sound_manager = get_sound_manager()
            print("[ROMULAN BOOT] Stealth sounds initialized")
            
        if False: # Removed except block
            print(f"[ROMULAN BOOT] Component initialization error: {e}")

    def setup_ui(self):
        """Ініціалізація інтерфейсу в ромуланському стилі."""
        if not self.layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(5)
        else:
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())
            clear_layout(self.main_layout)

        c_lay = self.main_layout
        
        # Ромуланські кольори - таємничі зелені
        primary = self.color_gen.get_next_color()
        secondary = self.color_gen.get_next_color()
        
        # --- ROMULAN HEADER ---
        header = QHBoxLayout()
        header.setSpacing(5)
        
        # Ромуланський елемент заголовка
        self.elbow = QFrame()
        self.elbow.setMinimumSize(200, 60)
        self.elbow.setStyleSheet(f"background-color: {primary}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        header.addWidget(self.elbow)
        
        # Заголовок
        self.title_fr = QFrame()
        self.title_fr.setMinimumSize(600, 60)
        self.title_fr.setStyleSheet(f"background-color: {secondary}; border-radius: 6px;")
        tl_layout = QHBoxLayout(self.title_fr)
        self.title_lbl = QLabel("ROMULAN EMPIRE // SHADOW SYSTEM")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl_layout.addWidget(self.title_lbl)
        header.addWidget(self.title_fr)
        
        header.addStretch()
        c_lay.addLayout(header)
        
        # --- MAIN TERMINAL ---
        terminal = QVBoxLayout()
        terminal.setContentsMargins(30, 20, 20, 20)
        terminal.setSpacing(15)
        
        # Дисплей статусу
        self.step_display = QLabel("INITIALIZING...")
        self.step_display.setStyleSheet(f"color: #33FF33; {get_lcars_font_style(24, 'normal')}")
        terminal.addWidget(self.step_display)
        
        # Прогрес-бар
        self.pbar_layout = QHBoxLayout()
        self.pbar_layout.setSpacing(4)
        self.chunks = []
        for _ in range(40):  # Більше чанків для плавності
            chunk = QFrame()
            chunk.setMinimumSize(12, 25)
            chunk.setStyleSheet("background-color: #003300; border-radius: 4px;")
            self.chunks.append(chunk)
            self.pbar_layout.addWidget(chunk)
        terminal.addLayout(self.pbar_layout)
        
        # Лог область
        self.log_area = QVBoxLayout()
        self.log_area.setSpacing(5)
        self.log_lines = []
        for _ in range(5):
            line = QLabel("> ...")
            line.setStyleSheet(f"color: #66CC66; {get_lcars_font_style(16, 'normal')}")
            self.log_lines.append(line)
            self.log_area.addWidget(line)
        terminal.addLayout(self.log_area)
        
        terminal.addStretch()
        c_lay.addLayout(terminal, 1)
        
        # --- ROMULAN FOOTER ---
        footer = QFrame()
        footer.setMinimumHeight(30)
        footer.setStyleSheet(f"background-color: {primary}; border-bottom-right-radius: 20px;")
        c_lay.addWidget(footer)

    def update_boot(self):
        """Оновлення прогресу завантаження."""
        self.progress += 1
        
        # Оновлення чанків прогресу
        chunk_idx = int((self.progress / 100) * 40)
        for i, chunk in enumerate(self.chunks):
            if i < chunk_idx:
                if i == chunk_idx - 1:
                    chunk.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
                elif "#003300" in chunk.styleSheet():
                    chunk.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
            else:
                chunk.setStyleSheet("background-color: #003300; border-radius: 4px;")
        
        # Оновлення кроків
        step_idx = int((self.progress / 100) * len(self.steps))
        if step_idx < len(self.steps):
            new_step = self.steps[step_idx]
            if new_step != self.step_display.text():
                self.step_display.setText(new_step)
                for i in range(len(self.log_lines) - 1, 0, -1):
                    self.log_lines[i].setText(self.log_lines[i - 1].text())
                self.log_lines[0].setText(f"> {new_step} [STEALTH]")
        
        if self.progress >= 100:
            self.timer.stop()
            self.finished.emit()

    def closeEvent(self, event):
        """Очищення при закритті."""
        if self.timer.isActive():
            self.timer.stop()
        event.accept()
