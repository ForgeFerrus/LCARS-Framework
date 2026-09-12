"""
NX-01 STYLE AUTHORIZATION
ARCHITECT: TITAN V5.0
DESCRIPTION: Implementation of the 22nd Century NX-01 Login Screen.
"""
import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QLineEdit, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from lcars.themes.lcars_palette import (
    LCARSEra, get_lcars_font_style
)
from lcars.ui.views.selector_nx01 import NX01Frame, NX01Button

class LoginViewNX01(QWidget):
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.frame = NX01Frame()
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(100, 100, 100, 100)
        frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.setSpacing(20)
        
        self.lbl_head = QLabel("◢ КОНТРОЛЬ ДОСТУПУ :: ПОТРІБНА АВТОРИЗАЦІЯ")
        self.lbl_head.setStyleSheet(f"color: white; {get_lcars_font_style(24, 'normal')}")
        self.lbl_head.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.lbl_head)
        
        # Access Code Input area
        self.lbl_code = QLabel("◢ ВВЕДІТЬ КОД ДОСТУПУ")
        self.lbl_code.setStyleSheet(f"color: #CCCCCC; {get_lcars_font_style(16, 'normal')}")
        self.lbl_code.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.lbl_code)
        
        self.input_code = QLineEdit()
        self.input_code.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_code.setStyleSheet("""
            QLineEdit {
                background-color: black;
                color: #269EEE;
                border: 2px solid #5C5C5C;
                font-family: 'Arial';
                font-size: 24px;
                padding: 10px;
                text-align: center;
            }
        """)
        self.input_code.setFixedSize(400, 60)
        frame_layout.addWidget(self.input_code, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Confirm Button
        self.btn_login = NX01Button("АВТОРИЗАЦІЯ", "AUTH", "#269EEE")
        self.btn_login.clicked.connect(self.start_auto_login)
        frame_layout.addWidget(self.btn_login, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_status = QLabel("◢ КОМУНІКАЦІЇ: АКТИВНО")
        self.lbl_status.setStyleSheet(f"color: #CCCCCC; {get_lcars_font_style(12, 'normal')}")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(self.lbl_status)
        
        layout.addWidget(self.frame)

    def start_auto_login(self):
        """Auto-login logic."""
        self.input_code.setText("********")
        self.lbl_status.setText("◢ СИНХРОНІЗАЦІЯ БІОМЕТРИКИ...")
        self.btn_login.update_color("#FFBB00") # Yellow/Active
        
        QTimer.singleShot(1500, self._complete_login)

    def _complete_login(self):
        self.lbl_status.setText("◢ ДОСТУП НАДАНО.")
        self.btn_login.update_color("#00FF00") # Green/Access
        QTimer.singleShot(1000, self.finished.emit)
