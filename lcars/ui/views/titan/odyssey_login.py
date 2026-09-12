"""
LCARS SECURE ACCESS - ODYSSEY LOGIN
SYSTEM MODULE: AUTH-SEC-1071
PROTOCOL: NEURAL INTERFACE AUTHENTICATION
DESCRIPTION: High-security authentication interface for Enterprise-F class vessels.
             Features procedural UFP iconography and secure credential verification.
"""
import logging
import random
# Titanium Bridge Migration: import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QRadialGradient, QPolygonF

from lcars.themes.theme import get_lcars_font_style
from lcars.themes.palette import (get_random_button_color,
    LCARSEra,  FactionEra
)
from lcars.ui.base.widgets import LCARSButton
from lcars.modules.sound_manager import get_sound_manager

logger = logging.getLogger("lcars.ui.odyssey_login")

class UFPLogo(QWidget):
    """Векторний логотип Федерації. Контури зірки можуть бути вимкнені для чистого вигляду."""
    def _draw_star(self, painter, center, radius, points=5, inner_radius_ratio=0.4):
        star = QPolygonF()
        for i in range(2 * points):
            r = radius if i % 2 == 0 else radius * inner_radius_ratio
            angle = (i * math.pi) / points - math.pi / 2
            star.append(QPointF(center.x() + r * math.cos(angle), center.y() + r * math.sin(angle)))
        painter.drawPolygon(star)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20

        # Зовнішній декоративний шар (тепер без видимого контуру)
        painter.setBrush(QBrush(QColor(0, 50, 150, 40)))
        painter.setPen(Qt.PenStyle.NoPen)
        self._draw_star(painter, center, radius + 25, points=8, inner_radius_ratio=0.7)

        # Основна зірка — без товстої обвідки (контур вимкнений за запитом)
        painter.setBrush(QBrush(QColor(0, 40, 120, 200)))
        painter.setPen(Qt.PenStyle.NoPen)
        self._draw_star(painter, center, radius, points=6, inner_radius_ratio=0.5)

        # Маленькі зірки (без товстих обвідок)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        random.seed(42)
        for _ in range(40):
            x = center.x() + random.randint(-radius+10, radius-10)
            y = center.y() + random.randint(-radius+10, radius-10)
            if (x - center.x())**2 + (y - center.y())**2 < (radius-20)**2:
                self._draw_star(painter, QPointF(x, y), 5, points=5)

        # Великі символічні зірки — також без контурів
        painter.setPen(Qt.PenStyle.NoPen)
        self._draw_star(painter, QPointF(center.x(), center.y() - 30), 12, points=5)
        self._draw_star(painter, QPointF(center.x() - 40, center.y() + 30), 12, points=5)
        self._draw_star(painter, QPointF(center.x() + 40, center.y() + 30), 12, points=5)


class OdysseyLoginView(QWidget):
    """Преміальний екран авторизації 'Odyssey/Enterprise-F'.

    Параметр `show_contours` керує декоративними лініями/контуром у верхній та нижній частинах.
    """
    finished = pyqtSignal()

    def __init__(self, show_contours: bool = False):
        super().__init__()
        self.show_contours = bool(show_contours)
        self.setup_ui()

    def setup_ui(self):
        # КРОК 1: Базове налаштування фону та головного контейнера
        self.setStyleSheet("background-color: black;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 40, 0, 40)
        layout.setSpacing(0)

        # --- TOP BORDER (ВЕРХНЯ МЕЖА) ---
        # Декоративні лінії включаються лише якщо show_contours=True
        top_border = QVBoxLayout()
        top_border.setSpacing(8)
        if self.show_contours:
            line1 = QFrame()
            line1.setMinimumHeight(6)
            line1.setStyleSheet("background-color: #CC4422;") # LCARS ORANGE-RED
            top_border.addWidget(line1)

            line2 = QFrame()
            line2.setMinimumHeight(6)
            line2.setStyleSheet("background-color: #CC4422;")
            top_border.addWidget(line2)
        else:
            # keep spacing consistent when contours are hidden
            spacer = QFrame()
            spacer.setMinimumHeight(12)
            top_border.addWidget(spacer)
        
        # Інформація про корабель (Зверху справа)
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        ship_info = QVBoxLayout()
        ship_info.setSpacing(2)
        
        uss_lbl = QLabel('U.S.S. "ODYSSEY"')
        uss_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(14, 'normal')};")
        ship_info.addWidget(uss_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        ncc_lbl = QLabel("NCC-1071 ENTERPRISE-F")
        ncc_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(14, 'normal')};")
        ship_info.addWidget(ncc_lbl, alignment=Qt.AlignmentFlag.AlignRight)
        
        info_layout.addLayout(ship_info)
        info_layout.addSpacing(30)
        
        layout.addLayout(top_border)
        layout.addLayout(info_layout)
        
        layout.addStretch(1)

        # --- CENTER CONTENT (ЦЕНТРАЛЬНА ЧАСТИНА) ---
        # КРОК 3: Візуалізація логотипу Федерації через QPainter
        center_layout = QVBoxLayout()
        center_layout.setSpacing(30)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # UFP Logo - Високоякісна векторна графіка (ЗІРКИ ЗА ЗАПИТОМ КОРИСТУВАЧА)
        self.logo_container = QFrame()
        self.logo_container.setMinimumSize(400, 300)
        self.logo_layout = QVBoxLayout(self.logo_container)
        
        self.logo_widget = UFPLogo()
        self.logo_layout.addWidget(self.logo_widget)
        center_layout.addWidget(self.logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title_lbl = QLabel("THE LCARS COMPUTER NETWORK")
        title_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(42, 'normal')}; letter-spacing: 2px;")
        center_layout.addWidget(title_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.status_lbl = QLabel("AUTHORIZED ACCESS ONLY - SYSTEM READY")
        self.status_lbl.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(22, 'normal')};")
        center_layout.addWidget(self.status_lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # КРОК 4: Налаштування поля вводу пароля та кнопки доступу
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setSpacing(15)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("........")
        self.pwd_input.setMinimumSize(350, 60)
        # Стиль: темний фон, червоний текст, жирна помаранчева межа зліва
        self.pwd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #1A1A1A;
                border-left: 12px solid #CC4422;
                border-top: 1px solid #333;
                border-bottom: 1px solid #333;
                border-right: 1px solid #333;
                color: #FF3333;
                padding-left: 15px;
                {get_lcars_font_style(32, 'normal')}
                border-radius: 2px;
            }}
        """)
        input_layout.addWidget(self.pwd_input)
        
        self.btn_access = LCARSButton("ACCESS", "#9EA5BA", shape="pill")
        self.btn_access.setMinimumSize(160, 60)
        self.btn_access.clicked.connect(self.attempt_login)
        input_layout.addWidget(self.btn_access)
        
        center_layout.addWidget(input_container)
        layout.addLayout(center_layout)
        
        layout.addStretch(1)

        # --- BOTTOM BORDER (НИЖНЯ МЕЖА) ---
        # КРОК 5: Завершення симетрії кадру нижніми лініями
        bottom_border = QVBoxLayout()
        bottom_border.setSpacing(8)
        
        line3 = QFrame()
        line3.setMinimumHeight(6)
        line3.setStyleSheet("background-color: #CC4422;")
        bottom_border.addWidget(line3)
        
        line4 = QFrame()
        line4 = QFrame()
        line4.setMinimumHeight(6)
        line4.setStyleSheet("background-color: #CC4422;")
        bottom_border.addWidget(line4)
        
        layout.addLayout(bottom_border)

    def start_auto_login(self):
        """Анімація автоматичного вводу (для --default режиму)."""
        password = "********"
        self.pwd_input.setText("")
        for i in range(len(password)):
            QTimer.singleShot(i * 120, lambda val=password[:i+1]: self.pwd_input.setText(val))
        QTimer.singleShot(len(password) * 120 + 600, self.attempt_login)

    def attempt_login(self):
        """Імітація перевірки пароля."""
        from lcars.modules.sound_manager import get_sound_manager
        get_sound_manager().play("acknowledge")
        self.status_lbl.setText("AUTHENTICATING NEURAL INTERFACE...")
        self.status_lbl.setStyleSheet(f"color: #CC4422; {get_lcars_font_style(22, 'normal')}")
        QTimer.singleShot(1500, self.confirm_access)

    def confirm_access(self):
        """Завершення авторизації."""
        self.status_lbl.setText("ACCESS GRANTED. WELCOME ADMIRAL.")
        self.status_lbl.setStyleSheet(f"color: #44CC44; {get_lcars_font_style(22, 'normal')}")
        from lcars.modules.sound_manager import get_sound_manager
        get_sound_manager().play("ready")
        QTimer.singleShot(1000, self.finished.emit)

    def focus_input(self):
        self.pwd_input.setFocus()
