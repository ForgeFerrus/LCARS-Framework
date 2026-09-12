from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.themes.palette import (
    get_era_palette, LCARSEra, get_lcars_font_style, 
    LCARSColorGenerator, setup_lcars_font
)

class LCARSLoadingScreen(QWidget):
    """
    LCARS System Boot Sequence
    Справжнє повноекранне завантаження з центрованими блоками даних.
    """
    loading_finished = pyqtSignal()

    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__()
        setup_lcars_font()
        self.era = era
        self.lcars_palette = get_era_palette(self.era)
        self.color_cycle_index = 0
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(f"background-color: {self.lcars_palette['background']}; border: none;")
        
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        
        self.steps = [
            "SCANNING CORE BUFFER...",
            "INITIALIZING NEURAL NETS...",
            "CALIBRATING OPTICAL DATA...",
            "ESTABLISHING SECURE PROTOCOLS...",
            "SYNCHRONIZING TEMPORAL DATA...",
            "RECOGNIZING SYSTEM AUTHORITY...",
            "READY FOR INTERFACE."
        ]
        self.progress = 0
        
        self.init_ui()
        self.showFullScreen()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(10) # 10мс для швидкого старту

    def init_ui(self):
        screen_layout = QVBoxLayout(self)
        screen_layout.setContentsMargins(0, 0, 0, 0)
        
        container = QWidget()
        container.setFixedSize(900, 500)
        self.c_layout = QVBoxLayout(container)
        self.c_layout.setContentsMargins(0, 0, 0, 0)
        self.c_layout.setSpacing(8)
        
        # --- HEADER ---
        header = QHBoxLayout()
        header.setSpacing(8)
        
        self.elbow_l = QFrame()
        self.elbow_l.setFixedSize(180, 60)
        self.elbow_l.setStyleSheet(f"background-color: {self.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        header.addWidget(self.elbow_l)
        
        self.title_fr = QFrame()
        self.title_fr.setFixedSize(600, 60)
        self.title_fr.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px;")
        tl_layout = QHBoxLayout(self.title_fr)
        self.title_lbl = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tl_layout.addWidget(self.title_lbl)
        header.addWidget(self.title_fr)
        
        header.addStretch() 

        self.elbow_r = QFrame()
        self.elbow_r.setFixedSize(40, 60)
        self.elbow_r.setStyleSheet(f"background-color: {self.get_next_color()}; border-top-right-radius: 30px; border-bottom-right-radius: 6px;")
        header.addWidget(self.elbow_r)
        self.c_layout.addLayout(header)

        # --- MID ---
        mid = QHBoxLayout()
        mid.setSpacing(8)
        
        sidebar = QVBoxLayout()
        sidebar.setSpacing(8)
        self.sb_main = QFrame()
        self.sb_main.setFixedWidth(180)
        self.sb_main.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px; border-bottom-left-radius: 60px;")
        sidebar.addWidget(self.sb_main, 1)
        mid.addLayout(sidebar)
        
        terminal = QVBoxLayout()
        terminal.setContentsMargins(20, 10, 10, 10)
        terminal.setSpacing(15)
        
        self.step_display = QLabel("INITIALIZING...")
        self.step_display.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(24, 'normal')}")
        terminal.addWidget(self.step_display)
        
        self.pbar_layout = QHBoxLayout()
        self.pbar_layout.setSpacing(4)
        self.chunks = []
        for _ in range(40): # Більше чанків, але меншого розміру
            chunk = QFrame()
            chunk.setFixedSize(12, 25)
            chunk.setStyleSheet("background-color: #222222; border-radius: 4px;")
            self.chunks.append(chunk)
            self.pbar_layout.addWidget(chunk)
        terminal.addLayout(self.pbar_layout)
        
        self.log_area = QVBoxLayout()
        self.log_area.setSpacing(5)
        self.log_lines = []
        for _ in range(5):
            line = QLabel("> ...")
            line.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(18, 'normal')}")
            self.log_lines.append(line)
            self.log_area.addWidget(line)
        terminal.addLayout(self.log_area) 
        
        terminal.addStretch()
        mid.addLayout(terminal, 1)
        self.c_layout.addLayout(mid, 1)

        # --- FOOTER ---
        footer = QFrame()
        footer.setFixedHeight(30)
        footer.setStyleSheet(f"background-color: {self.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 6px;")
        self.c_layout.addWidget(footer)

        screen_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(container)
        h_center.addStretch()
        screen_layout.addLayout(h_center)
        screen_layout.addStretch()

        self.showFullScreen()

    def get_next_color(self):
        """Викликає централізований генератор кольорів."""
        color = LCARSColorGenerator(self.era, self.color_cycle_index)
        self.color_cycle_index = (self.color_cycle_index + 1) % 8
        return color

    def refresh_colors(self):
        """Динамічне оновлення кольорів під час завантаження за циклічним алгоритмом."""
        # Скидаємо індекс для передбачуваності циклу при кожному кроку оновлення
        # або залишаємо для безперервного циклу. Залишимо безперервним.
        self.elbow_l.setStyleSheet(f"background-color: {self.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        self.title_fr.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px;")
        self.elbow_r.setStyleSheet(f"background-color: {self.get_next_color()}; border-top-right-radius: 30px; border-bottom-right-radius: 6px;")
        self.sb_main.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px; border-bottom-left-radius: 60px;")

    def update_progress(self):
        self.progress += 1
        if self.progress % 8 == 0: 
            self.color_cycle_index = (self.color_cycle_index + 1) % 8 # Оновлюємо індекс кольору кожні 8%
        
        # Update chunks (теж циклічно)
        chunk_idx = int((self.progress / 100) * 40)
        for i, chunk in enumerate(self.chunks):
            if i < chunk_idx:
                if i == chunk_idx - 1: # Останній активний чанк завжди наступний за циклом
                    chunk.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 4px;")
                elif "background-color: #222222" in chunk.styleSheet():
                    chunk.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 4px;")
            else:
                chunk.setStyleSheet("background-color: #222222; border-radius: 4px;")

        # Update steps
        step_idx = int((self.progress / 100) * len(self.steps))
        if step_idx < len(self.steps):
            new_step = self.steps[step_idx]
            if new_step != self.step_display.text():
                self.step_display.setText(new_step)
                for i in range(len(self.log_lines)-1, 0, -1):
                    self.log_lines[i].setText(self.log_lines[i-1].text())
                self.log_lines[0].setText(f"> {new_step} [OK]")

        if self.progress >= 100:
            self.timer.stop()
            self.loading_finished.emit()
            self.close()
