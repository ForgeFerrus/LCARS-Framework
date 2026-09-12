"""
LCARS Login Screen - Minimal full-screen background environment
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSettings, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from pathlib import Path
from lcars.themes.palette import ( LCARSColorGenerator, LCARSEra,
    get_era_palette, get_lcars_font_style, setup_lcars_font, 
    get_random_button_color
)
from lcars.system.alert import alert_system


class LCARSLoginScreen(QWidget):
    """Справжній екран входу LCARS: центрований, повноекранний, автентичний."""
    
    login_successful = pyqtSignal()
    
    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH, parent=None):
        super().__init__(parent)
        setup_lcars_font()
        self.era = era
        self.lcars_palette = get_era_palette(self.era)
        self.color_gen = LCARSColorGenerator(self.era)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: none;")
        
        primary_screen = QApplication.primaryScreen()
        screen_geo = primary_screen.geometry() if primary_screen else QRect(0, 0, 1920, 1080)
        self.setGeometry(screen_geo)
        self.showFullScreen()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Центрувальний контейнер
        center_frame = QWidget()
        center_frame.setFixedSize(950, 650) # Трохи вище щоб влізла кнопка нижче
        cf_layout = QVBoxLayout(center_frame)
        cf_layout.setContentsMargins(0, 0, 0, 0)
        cf_layout.setSpacing(10)

        # -- HEADER --
        header = QHBoxLayout()
        header.setSpacing(10)
        self.elbow = QFrame()
        self.elbow.setFixedSize(180, 60)
        self.elbow.setStyleSheet(f"background-color: {self.get_next_color()}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        header.addWidget(self.elbow)
        
        self.header_fr = QFrame()
        self.header_fr.setFixedHeight(60)
        self.header_fr.setFixedWidth(600) # Обмежуємо ширину, щоб не було розтягнуто
        self.header_fr.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px;")
        tb_layout = QHBoxLayout(self.header_fr)
        self.title_lbl = QLabel("TERMINAL ACCESS RESTRICTED")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        tb_layout.addWidget(self.title_lbl)
        header.addWidget(self.header_fr)
        
        # Додаємо декоративні блоки замість розтягування
        self.header_deco = QFrame()
        self.header_deco.setFixedSize(140, 60)
        self.header_deco.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px;")
        header.addWidget(self.header_deco)
        
        header.addStretch() # Або додаємо порожнечу в кінці, а не розтягуємо кнопки
        cf_layout.addLayout(header)

        # -- CONTENT --
        content = QHBoxLayout()
        content.setSpacing(10)
        
        sidebar = QVBoxLayout()
        sidebar.setSpacing(5)
        self.sb_main = QFrame()
        self.sb_main.setFixedWidth(180)
        self.sb_main.setStyleSheet(f"background-color: {self.get_next_color()}; border-bottom-left-radius: 60px; border-top-left-radius: 6px;")
        sidebar.addWidget(self.sb_main, 1)
        
        self.side_decos = []
        for _ in range(5):
            dec = QFrame()
            dec.setFixedSize(180, 25)
            dec.setStyleSheet(f"background-color: {self.get_next_color()}; border-radius: 6px;")
            sidebar.addWidget(dec)
            self.side_decos.append(dec)
        content.addLayout(sidebar)
        
        auth_area = QVBoxLayout()
        auth_area.setContentsMargins(40, 40, 40, 40)
        auth_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status = QLabel("ACCESS DENIED")
        self.status.setStyleSheet(f"color: #EE4444; {get_lcars_font_style(56, 'normal')}")
        auth_area.addWidget(self.status, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.info = QLabel("INPUT AUTHORIZATION CODE VIA VOICE OR CONSOLE")
        self.info.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(24, 'normal')}")
        auth_area.addWidget(self.info, 0, Qt.AlignmentFlag.AlignCenter)
        
        auth_area.addStretch(1)
        
        self.auth_btn = QPushButton("AUTHORIZE")
        self.auth_btn.setFixedSize(280, 110) 
        self.auth_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.get_next_color()};
                color: black; border-radius: 8px;
                {get_lcars_font_style(28, 'normal')}
                padding-right: 25px; text-align: right;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                margin: -2px;
                border: 2px solid #FFFFFF;
            }}
        """)
        self.auth_btn.clicked.connect(self.on_authorize_clicked)
        auth_area.addWidget(self.auth_btn, 0, Qt.AlignmentFlag.AlignCenter)
        auth_area.addStretch(1) # Кнопка нижче
        
        content.addLayout(auth_area, 1)
        cf_layout.addLayout(content, 1)

        # FOOTER - замість однієї розтягнутої смуги робимо блоки
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setSpacing(10)
        
        self.footer_block = QFrame()
        self.footer_block.setFixedSize(600, 30)
        self.footer_block.setStyleSheet(f"background-color: {self.get_next_color()}; border-bottom-right-radius: 20px; border-top-right-radius: 6px;")
        self.footer_layout.addWidget(self.footer_block)
        
        self.alert_toggle = QPushButton("TOGGLE ALERT")
        self.alert_toggle.setFixedSize(180, 50)
        self.alert_toggle.setStyleSheet(f"background-color: #336699; color: white; border-radius: 6px; {get_lcars_font_style(18, 'normal')}")
        self.alert_toggle.clicked.connect(self._toggle_system_alert)
        self.footer_layout.addWidget(self.alert_toggle)
        
        self.footer_layout.addStretch()
        cf_layout.addLayout(self.footer_layout)

        # Таймер динамічних кольорів
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.refresh_colors)
        self.color_timer.start(3000)

        main_layout.addStretch()
        h_center = QHBoxLayout()
        h_center.addStretch()
        h_center.addWidget(center_frame)
        h_center.addStretch()
        main_layout.addLayout(h_center)
        main_layout.addStretch()

        self.showFullScreen()

    def _toggle_system_alert(self):
        """Перемикання тривоги для тестування прямо з екрану входу."""
        alert_system.next_level()
        self.refresh_colors()

    def get_next_color(self):
        return self.color_gen.get_next_color(int(alert_system.level))

    def refresh_colors(self):
        """Оновлення кольорів інтерфейсу за циклічним алгоритмом з урахуванням 3 рівнів тривоги."""
        self.color_gen.reset()
        level_val = int(alert_system.level)
        
        # Оновлення графічних елементів
        self.elbow.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        self.header_fr.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-radius: 6px;")
        self.header_deco.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-radius: 6px;")
        self.sb_main.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-bottom-left-radius: 60px; border-top-left-radius: 6px;")
        
        btn_color = self.color_gen.get_next_color(level_val)
        self.auth_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                color: black; border-radius: 6px;
                {get_lcars_font_style(22, 'normal')}
                padding-right: 20px; text-align: right;
            }}
            QPushButton:hover {{ background-color: white; }}
        """)
        
        self.footer_block.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-bottom-right-radius: 20px; border-top-right-radius: 6px;")
        for dec in self.side_decos:
            dec.setStyleSheet(f"background-color: {self.color_gen.get_next_color(level_val)}; border-radius: 6px;")
        
        # Оновлення тексту та кольору статусу залежно від рівня
        if level_val == 0: # NORMAL
            self.status.setText("ACCESS DENIED")
            self.status.setStyleSheet(f"color: #EE4444; {get_lcars_font_style(48, 'normal')}")
            self.info.setText("INPUT AUTHORIZATION CODE VIA VOICE OR CONSOLE")
        elif level_val == 1: # YELLOW
            self.status.setText("YELLOW ALERT")
            self.status.setStyleSheet(f"color: #FFCC33; {get_lcars_font_style(48, 'normal')}")
            self.info.setText("NON-ESSENTIAL SYSTEMS SUSPENDED")
        else: # RED
            self.status.setText("RED ALERT")
            self.status.setStyleSheet(f"color: #D80000; {get_lcars_font_style(48, 'normal')}")
            self.info.setText("BATTLE STATIONS - ALL PERSONNEL TO STATIONS")

    def on_authorize_clicked(self):
        """Авторзиація успішна"""
        print("⚠ ACCESS GRANTED")
        self.login_successful.emit()
        self.close()

    def keyPressEvent(self, a0):
        if a0 is None:
            return
        if a0.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.on_authorize_clicked()
        elif a0.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(a0)
