"""
LCARS Login Screen - Minimal full-screen background environment
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSettings, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
# Titanium Bridge Migration: from pathlib import Path
from lcars.themes.lcars_palette import ( LCARSColorGenerator, LCARSEra,
    get_era_palette, get_lcars_font_style, setup_lcars_font, 
    get_random_button_color
)
from lcars.system.alert import alert_system


class LCARSLoginScreen(QWidget):
    """Справжній екран входу LCARS: центрований, повноекранний, автентичний."""
    login_successful = pyqtSignal()
    # Ініціалізація екрану входу
    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH, parent=None):
        super().__init__(parent)
        setup_lcars_font()
        self.era = era
        self.lcars_palette = get_era_palette(self.era)
        self.color_gen = LCARSColorGenerator(self.era)
        # Налаштування вікна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: none;")
        # Встановлення геометрії екрану
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

        # --- HEADER --- (з елементами, що змінюють колір)
        header = QHBoxLayout()
        header.setSpacing(10)
        self.elbow = QFrame()
        self.elbow.setFixedSize(180, 60)
        self.elbow.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(0)}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        header.addWidget(self.elbow)
        
        self.header_fr = QFrame()
        self.header_fr.setFixedHeight(60)
        self.header_fr.setFixedWidth(600) # Обмежуємо ширину, щоб не було розтягнуто
        self.header_fr.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(1)}; border-radius: 6px;")
        tb_layout = QHBoxLayout(self.header_fr)
        self.title_lbl = QLabel("SYSTEM LOGON PROTOCOL")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(20, 'normal')}")
        tb_layout.addWidget(self.title_lbl)
        header.addWidget(self.header_fr)
        
        # Додаємо декоративні блоки замість розтягування
        self.header_deco = QFrame()
        self.header_deco.setFixedSize(140, 60)
        self.header_deco.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(2)}; border-radius: 6px;")
        header.addWidget(self.header_deco)
        
        header.addStretch() # Або додаємо порожнечу в кінці, а не розтягуємо кнопки
        cf_layout.addLayout(header)

        # -- CONTENT --
        content = QHBoxLayout()
        content.setSpacing(10)
        
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        self.sb_main = QFrame()
        self.sb_main.setFixedWidth(180)
        self.sb_main.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(3)}; border-bottom-left-radius: 60px; border-top-left-radius: 6px;")
        sidebar.addWidget(self.sb_main, 1)
        
        self.side_decos = []
        for i in range(5):
            dec = QFrame()
            dec.setFixedSize(180, 45)
            dec.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(10+i)}; border-radius: 6px;")
            sidebar.addWidget(dec)
            self.side_decos.append(dec)
        content.addLayout(sidebar)
        
        auth_area = QVBoxLayout()
        auth_area.setContentsMargins(20, 20, 20, 20)
        auth_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        auth_area.setSpacing(30)
        
        self.status = QLabel("LCARS SYSTEM READY")
        self.status.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(56, 'normal')}")
        auth_area.addWidget(self.status, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.info = QLabel("WELCOME TO FEDERATION MAIN CONTROL NODE")
        self.info.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(24, 'normal')}")
        auth_area.addWidget(self.info, 0, Qt.AlignmentFlag.AlignCenter)
        
        auth_area.addStretch(1)
        
        # Grid block for authentication buttons (bricks)
        auth_grid = QHBoxLayout()
        auth_grid.setSpacing(20)
        auth_grid.addStretch()
        
        self.auth_btn = QPushButton("ACCESS SYSTEM")
        self.auth_btn.setFixedSize(280, 110) # Premium Monitor size matching Launcher
        self.auth_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color_gen.get_color_at_index(6)};
                color: black; border-radius: 8px;
                {get_lcars_font_style(28, 'normal')}
                padding-right: 25px; text-align: right;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                margin: -2px;
                border: 2px solid {self.color_gen.get_color_at_index(6)};
            }}
        """)
        self.auth_btn.clicked.connect(self.on_authorize_clicked)
        auth_grid.addWidget(self.auth_btn)
        
        # Decorative brick next to it
        self.deco_brick = QFrame()
        self.deco_brick.setFixedSize(80, 110) 
        self.deco_brick.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(7)}; border-radius: 8px;")
        auth_grid.addWidget(self.deco_brick)
        
        auth_grid.addStretch()
        auth_area.addLayout(auth_grid)
        
        auth_area.addStretch(1)
        
        content.addLayout(auth_area, 1)
        cf_layout.addLayout(content, 1)

        # FOOTER
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setSpacing(10)
        self.footer_layout.setContentsMargins(190, 0, 0, 0) # Align with content
        
        # Справжні LCARS бріки: 220*60
        self.alert_toggle = QPushButton("STATUS: NOMINAL")
        self.alert_toggle.setFixedSize(240, 60)
        self.alert_toggle.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(5)}; color: black; border-radius: 6px; {get_lcars_font_style(20, 'normal')}")
        self.alert_toggle.clicked.connect(self._toggle_system_alert)
        self.footer_layout.addWidget(self.alert_toggle)

        self.footer_block = QFrame()
        self.footer_block.setFixedHeight(60) # Відповідно до бріків
        self.footer_block.setFixedWidth(300)
        self.footer_block.setStyleSheet(f"background-color: {self.color_gen.get_color_at_index(5)}; border-radius: 6px;")
        self.footer_layout.addWidget(self.footer_block)
        
        self.exit_btn = QPushButton("TERMINATE")
        self.exit_btn.setFixedSize(220, 60)
        self.exit_btn.setStyleSheet(f"background-color: #CC6666; color: black; border-radius: 6px; {get_lcars_font_style(20, 'normal')}")
        self.exit_btn.clicked.connect(self.close)
        self.footer_layout.addWidget(self.exit_btn)
        
        self.footer_layout.addStretch()
        cf_layout.addLayout(self.footer_layout)

        # Таймер атмосферного циклу (ДУЖЕ ПОВІЛЬНО - 6 сек)
        # Це той самий канонічний "алгоритм LCARS", що змінює кольори панелей
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_interface_cycle)
        self.color_timer.start(5000) 

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
        self.update_interface_cycle()

    def get_next_color(self):
        return self.color_gen.get_next_color(int(alert_system.level))

    def update_interface_cycle(self):
        """
        Subtle update of static components using random colors for that authentic LCARS flicker.
        """
        level_val = int(alert_system.level)
        
        # Using the requested randomness
        self.elbow.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-top-left-radius: 40px; border-bottom-left-radius: 6px;")
        self.header_fr.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 6px;")
        self.header_deco.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 6px;")
        self.sb_main.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-bottom-left-radius: 60px; border-top-left-radius: 6px;")
        
        for dec in self.side_decos:
            dec.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 6px;")
            
        self.footer_block.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 6px;")
        
        # Main access button - also flickers
        btn_color = get_random_button_color(self.era)
        self.auth_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                color: black; border-radius: 8px;
                {get_lcars_font_style(28, 'normal')}
                padding-right: 25px; text-align: right;
            }}
            QPushButton:hover {{ 
                background-color: white; 
                margin: -2px;
                border: 2px solid {btn_color};
            }}
        """)
        self.deco_brick.setStyleSheet(f"background-color: {get_random_button_color(self.era)}; border-radius: 8px;")
        
        # Status text update
        status_texts = ["SYSTEM NOMINAL", "CAUTION ADVISED", "CRITICAL ALERT"]
        info_texts = ["WELCOME TO FEDERATION MAIN CONTROL NODE", "SECURITY OVERRIDE - CODES REQUIRED", "IMPERIAL ATTACK - ALL STATIONS TO BATTLE"]
        colors = ["#9EA5BA", "#FFCC33", "#D80000"]
        
        self.status.setText(status_texts[level_val])
        self.status.setStyleSheet(f"color: {colors[level_val]}; {get_lcars_font_style(56, 'normal')}")
        self.info.setText(info_texts[level_val])
        self.info.setStyleSheet(f"color: {colors[level_val]}; {get_lcars_font_style(24, 'normal')}")
        
        # Update alert button text
        status_lbls = ["NOMINAL", "CAUTION", "CRITICAL"]
        self.alert_toggle.setText(f"STATUS: {status_lbls[level_val]}")
        from lcars.themes.lcars_palette import get_alert_color
        alert_btn_color = get_alert_color(self.era, level_val)
        self.alert_toggle.setStyleSheet(f"background-color: {alert_btn_color}; color: black; border-radius: 6px; {get_lcars_font_style(20, 'normal')}")

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
