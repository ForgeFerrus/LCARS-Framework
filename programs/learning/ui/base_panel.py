"""
Base panel module for learning UI station panels.
Provides LearningStation base class with common functionality.
"""
from lcars.base.components import SystemComponent
from lcars.base.type import Chassis, Label, Frame
from lcars.base.default import FontStyle


class LearningStation(SystemComponent):
    """
    Базовий клас для всіх навчальних панелей (Learning Station).
    
    Наслідує SystemComponent - базовий віджет LCARS з підтримкою:
    - Тем (кольори, шрифти)
    - Фракцій (FEDERATION, etc.)
    - Спільних методів типу createHeader()
    
    Всі панелі (Dashboard, Grammar, Tenses) наслідують цей клас
    для отримання спільного функціоналу.
    """
    def __init__(self, theme, faction, parent=None):
        super().__init__(parent)
        self.theme = theme  # dict з palette, accent, alert кольорами
        self.faction = faction  # "FEDERATION" або інші фракції

    def createHeader(self, title, layout, colorIdx=0):
        """
        Створює заголовок панелі з LCARS-стилем.
        
        Args:
            title: Текст заголовку
            layout: Layout для додавання заголовка
            colorIdx: Індекс кольору з палітри теми
        """
        # Використовуємо колір з палітри теми за індексом
        colors = self.theme.get('palette', ['#FF9900'] * 8)
        color = colors[colorIdx % len(colors)]
        hdr = Frame()
        hdr.setFixedHeight(88)
        hdr.setStyleSheet(f"background-color: {color}; border-radius: 44px;")
        # Використовуємо Chassis.Horizontal замість HBoxLayout
        hLay = Chassis.Horizontal(hdr)
        hLay.setContentsMargins(50, 0, 50, 0)
        lbl = Label(title)
        lbl.setStyleSheet(f"color: #000000; {FontStyle(32, 'normal')}; letter-spacing: 1px;")
        hLay.addWidget(lbl)
        layout.addWidget(hdr)
