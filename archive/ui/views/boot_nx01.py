"""
NX-01 STYLE BOOT SEQUENCE
ARCHITECT: TITAN V5.0
DESCRIPTION: Implementation of the 22nd Century NX-01 System Initialization.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style
)
from lcars.ui.views.selector_nx01 import NX01Frame

class BootViewNX01(QWidget):
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.start_boot()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = NX01Frame()
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(100, 100, 100, 100)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_head = QLabel("SYSTEM INITIALIZATION")
        self.lbl_head.setStyleSheet(f"color: white; {get_lcars_font_style(32, 'normal')}")
        self.lbl_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.lbl_head)
        
        self.lbl_status = QLabel("◢ SYNCING NEURAL PROCESSORS...")
        self.lbl_status.setStyleSheet(f"color: #CCCCCC; {get_lcars_font_style(16, 'normal')}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.lbl_status)
        
        self.progress = QProgressBar()
        self.progress.setFixedSize(600, 20)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #5C5C5C;
                background-color: black;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #269EEE;
            }
        """)
        self.progress.setRange(0, 100)
        frame_layout.addWidget(self.progress)
        
        layout.addWidget(self.frame)

    def start_boot(self):
        self.step = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._timer_tick)
        self.timer.start(50)

    def _timer_tick(self):
        self.step += 1
        self.progress.setValue(self.step)
        
        msgs = [
            "◢ ПЕРЕВІРКА КОРПУСУ КОРАБЛЯ...",
            "◢ ЗАВАНТАЖЕННЯ БІОС-СЕКТОРІВ...",
            "◢ ІНІЦІАЛІЗАЦІЯ EPS-КОНТУРІВ...",
            "◢ СИНХРОНІЗАЦІЯ КОМУНІКАЦІЙ...",
            "◢ КАЛІБРУВАННЯ СЕНСОРІВ...",
            "◢ СИСТЕМА ГОТОВА."
        ]
        
        if self.step == 1:
            self.lbl_head.setText("ІНІЦІАЛІЗАЦІЯ СИСТЕМИ")
            
        if self.step % 20 == 0:
            idx = (self.step // 20) - 1
            if 0 <= idx < len(msgs):
                self.lbl_status.setText(msgs[idx])
            
        if self.step >= 100:
            self.timer.stop()
            self.finished.emit()
