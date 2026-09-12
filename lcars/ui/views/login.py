"""
LCARS Login View - Екран авторизації користувача.
Забезпечує безпечний доступ до системних ресурсів.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

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
        self.color_gen = LCARSColorGenerator(era, faction)
        self.setup_ui()

    def apply_theme(self):
        """Re-apply styling based on current era and faction."""
        self.color_gen = LCARSColorGenerator(self.era, self.faction)
        self.setup_ui()

    def setup_ui(self):
        """Побудова інтерфейсу авторизації з використанням алгоритмічного оформлення."""
        if not self.layout():
            self.main_layout = QVBoxLayout(self)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(5)
        else:
            # Очищення існуючого макету (разом з вкладеними елементами)
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())
            clear_layout(self.main_layout)

        c_lay = self.main_layout
        
        # Використовуємо кольори за алгоритмом
        primary = self.color_gen.get_next_color()
        secondary = self.color_gen.get_next_color()
        accent = self.color_gen.get_next_color()
        
        # --- TOP HEADER ---
        header = QHBoxLayout()
        elb_tl = QFrame()
        elb_tl.setFixedSize(140, 50)
        elb_tl.setStyleSheet(f"background: {primary}; border-top-left-radius: 30px; border-bottom-left-radius: 4px;")
        header.addWidget(elb_tl)
        
        title_bar = QFrame()
        title_bar.setFixedHeight(30)
        title_bar.setStyleSheet(f"background: {primary}; border-radius: 2px;")
        tb_lay = QHBoxLayout(title_bar)
        tb_lay.setContentsMargins(20, 0, 20, 0)
        
        f_name = str(self.faction).split('.')[-1] if hasattr(self.faction, 'name') else str(self.faction or 'SYSTEM')
        lbl = QLabel(f"◢ AUTHORIZATION PROTOCOL :: {f_name.upper()}")
        lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}; border: none;")
        tb_lay.addWidget(lbl)
        header.addWidget(title_bar, 1)
        c_lay.addLayout(header)

        # --- CONTENT AREA ---
        content = QHBoxLayout()
        content.setSpacing(10)
        
        # Side Bar
        side_strip = QFrame()
        side_strip.setFixedWidth(50)
        side_strip.setStyleSheet(f"background: {secondary}; border-radius: 4px; border-bottom-left-radius: 40px;")
        content.addWidget(side_strip)
        
        # Form
        form = QVBoxLayout()
        form.setContentsMargins(40, 40, 40, 40)
        form.setSpacing(20)
        
        login_lbl = QLabel(f"ACCESS CODE FOR {f_name.upper()}")
        login_lbl.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}; border: none;")
        form.addWidget(login_lbl)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("********")
        self.pwd_input.setFixedSize(450, 60)
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #050505;
                border: 2px solid {accent};
                border-radius: 5px;
                color: {accent};
                padding-left: 15px;
                {get_lcars_font_style(32, 'normal')};
            }}
        """)
        form.addWidget(self.pwd_input)
        
        self.status_lbl = QLabel("◤ AWAITING NEURAL LINK...")
        self.status_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(16, 'normal')}; border: none;")
        form.addWidget(self.status_lbl)
        
        # Кнопка входу
        self.btn_auth = LCARSButton("AUTHORIZE", accent, shape="pill")
        self.btn_auth.setFixedSize(240, 70)
        form.addWidget(self.btn_auth)
        
        form.addStretch()
        content.addLayout(form, 1)
        c_lay.addLayout(content, 1)
        
        # --- FOOTER ---
        footer_lay = QHBoxLayout()
        footer_bar = QFrame()
        footer_bar.setFixedHeight(30)
        footer_bar.setStyleSheet(f"background: {primary}; border-radius: 2px;")
        footer_lay.addWidget(footer_bar, 1)
        
        elb_br = QFrame()
        elb_br.setFixedSize(140, 50)
        elb_br.setStyleSheet(f"background: {primary}; border-bottom-right-radius: 30px; border-top-right-radius: 4px;")
        footer_lay.addWidget(elb_br)
        c_lay.addLayout(footer_lay)

    def start_auto_login(self):
        """Симуляція автоматичного вводу пароля системою."""
        print("[LOGIN] Starting auto-login sequence (typing password animation)")
        password = "********"
        self.pwd_input.setText("")
        
        # Ефект друку символів * - уповільнено (200ms)
        for i in range(len(password)):
            QTimer.singleShot(i * 200, lambda val=password[:i+1]: self.pwd_input.setText(val))
            
        # Запуск авторизації після закінчення "друку"
        QTimer.singleShot(len(password) * 200 + 800, self.attempt_login)
    
    def focus_input(self):
        """Фокус на полі вводу для ручної авторизації."""
        self.pwd_input.setFocus()
        self.pwd_input.selectAll()
        self.status_lbl.setText("◤ ENTER AUTHORIZATION CODE")
        self.status_lbl.setStyleSheet("color: #FF9900;")

    def attempt_login(self):
        """Імітація процесу перевірки коду доступу."""
        get_sound_manager().play("acknowledge")
        self.status_lbl.setText("◤ AUTHENTICATING NEURAL PATHWAYS...")
        self.status_lbl.setStyleSheet("color: #FFCC33;")
        
        QTimer.singleShot(1500, self.confirm_access)

    def confirm_access(self):
        """Підтвердження доступу та передача керування далі."""
        print("[LOGIN] Access granted, emitting finished signal in 800ms")
        self.status_lbl.setText("◤ ACCESS GRANTED. SYSTEM READY.")
        self.status_lbl.setStyleSheet("color: #4BBEBF;")
        get_sound_manager().play("ready")
        QTimer.singleShot(800, self.finished.emit)
