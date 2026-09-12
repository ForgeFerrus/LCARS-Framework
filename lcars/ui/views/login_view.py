"""
LCARS Login View - Екран авторизації користувача.
Забезпечує безпечний доступ до системних ресурсів.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal

from lcars.themes.lcars_palette import LCARSEra, get_lcars_font_style, LCARSColorGenerator
from lcars.ui.base.widgets import LCARSButton
from lcars.modules.sound_manager import get_sound_manager

logger = logging.getLogger("lcars.ui.login")

class LoginView(QWidget):
    """Автентичний протокол авторизації LCARS."""
    finished = pyqtSignal()

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.era = era
        self.faction = faction
        # Алгоритмічний вибір кольорів
        self.color_gen = LCARSColorGenerator(era)
        self.setup_ui()

    def setup_ui(self):
        """Побудова інтерфейсу авторизації з використанням фірмових форм LCARS."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Контейнер діалогу
        self.container = QFrame()
        self.container.setFixedSize(800, 450)
        self.container.setStyleSheet("background: black;")
        c_lay = QVBoxLayout(self.container)
        c_lay.setContentsMargins(0, 0, 0, 0)
        c_lay.setSpacing(4)
        
        # --- ЗАГОЛОВОК ---
        header = QHBoxLayout()
        header.setSpacing(4)
        
        self.h_elb = QFrame()
        self.h_elb.setFixedSize(160, 50)
        self.h_elb.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-top-left-radius: 30px; border-bottom-left-radius: 4px;")
        header.addWidget(self.h_elb)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px;")
        tb_lay = QHBoxLayout(self.title_bar)
        lbl = QLabel("◢ AUTHORIZATION PROTOCOL 2501")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        tb_lay.addWidget(lbl)
        header.addWidget(self.title_bar, 1)
        c_lay.addLayout(header)

        # --- ОСНОВНА ЧАСТИНА ---
        content = QHBoxLayout()
        content.setSpacing(4)
        
        # Бічна панель
        self.sb_block = QFrame()
        self.sb_block.setFixedWidth(160)
        self.sb_block.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-radius: 4px; border-bottom-left-radius: 40px;")
        content.addWidget(self.sb_block)
        
        # Форма логіну
        form = QVBoxLayout()
        form.setContentsMargins(40, 40, 40, 40)
        form.setSpacing(20)
        
        login_lbl = QLabel("ENTER ACCESS CODE")
        login_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}")
        form.addWidget(login_lbl)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("********")
        self.pwd_input.setFixedSize(400, 50)
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #111;
                border: 2px solid {self.color_gen.get_next_color()};
                color: white;
                padding-left: 10px;
                {get_lcars_font_style(24, 'normal')}
            }}
        """)
        self.pwd_input.returnPressed.connect(self.attempt_login)
        form.addWidget(self.pwd_input)
        
        self.status_lbl = QLabel("READY FOR INPUT")
        self.status_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(14, 'normal')}")
        form.addWidget(self.status_lbl)
        
        # Кнопка входу
        btn_login = LCARSButton("AUTHORIZE", self.color_gen.get_next_color(), shape="rect")
        btn_login.setFixedSize(200, 60)
        btn_login.clicked.connect(self.attempt_login)
        form.addWidget(btn_login)
        
        form.addStretch()
        content.addLayout(form, 1)
        c_lay.addLayout(content, 1)
        
        # --- ФУТЕР ---
        self.footer = QFrame()
        self.footer.setFixedHeight(25)
        self.footer.setStyleSheet(f"background-color: {self.color_gen.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 4px;")
        c_lay.addWidget(self.footer)

        # Центрування
        self.layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(self.container)
        h_center.addStretch()
        self.layout.addLayout(h_center)
        self.layout.addStretch()

    def attempt_login(self):
        """Імітація процесу перевірки коду доступу."""
        # У реальній системі тут буде перевірка через SessionManager
        get_sound_manager().play("acknowledge")
        self.status_lbl.setText("AUTHENTICATING...")
        self.status_lbl.setStyleSheet("color: #FFCC33;")
        
        # Затримка для ефекту "роботи" системи
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, self.confirm_access)

    def confirm_access(self):
        """Підтвердження доступу та перехід до робочого столу."""
        self.status_lbl.setText("ACCESS GRANTED")
        self.status_lbl.setStyleSheet("color: #4BBEBF;")
        get_sound_manager().play("ready")
        QTimer.singleShot(1000, self.finished.emit)
