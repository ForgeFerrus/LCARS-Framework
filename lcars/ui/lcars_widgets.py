# LCARS Generic Widgets
# Повторно використовувані текстові компоненти, кнопки та контейнери для LCARS фреймворку.
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen

# Анімована кнопка LCARS зі зміною кольору
class AnimatedButton(QPushButton):
    # Ініціалізація кнопки з базовим кольором
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.Color = QColor("#000000")
        
    # Властивість кольору для анімації через Qt
    @pyqtProperty(QColor)
    def color(self):
        return self.Color
        
    # Встановлення кольору та оновлення стилю
    @color.setter
    def color(self, color):
        self.Color = color
        self.setStyleSheet(f"background-color: {color.name()}; border: none; border-radius: 2px; color: black; font-weight: normal;")
        
    # Публічний метод встановлення кольору
    def SetColor(self, color):
        self.color = color
        
    # Запуск анімації переходу до нового кольору
    def AnimateToColor(self, target_color, duration=1000):
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.Color)
        self.animation.setEndValue(QColor(target_color))
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.animation.start()

# Розширений віджет тайлу LCARS із заголовком та описом
class LcarsTile(QFrame):
    # Сигнал натискання на тайл
    clicked = pyqtSignal(bool)

    # Ініціалізація тайлу з текстом та базовим кольором
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.Color = QColor("#37A6D1")
        
        # Внутрішній макет
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 10, 15, 10)
        self.layout.setSpacing(5)
        
        # Декоративна лінія (технічний елемент)
        self.line = QFrame()
        self.line.setFixedHeight(4)
        self.line.setStyleSheet("background-color: rgba(0,0,0, 0.3); border-radius: 2px;")
        self.layout.addWidget(self.line)
        
        self.title_label = QLabel()
        self.title_label.setStyleSheet("background: transparent; border: none; color: black; font-weight: normal; font-size: 18px; font-family: 'Swis721 BT'; text-transform: uppercase;")
        
        self.desc_label = QLabel()
        self.desc_label.setStyleSheet("background: transparent; border: none; color: black; font-weight: normal; font-size: 12px; font-family: 'Swis721 BT';")
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.desc_label)
        
        # Технічний номер у підвалі
        self.number_label = QLabel(str(id(self))[-4:]) 
        self.number_label.setStyleSheet("color: rgba(0,0,0, 0.5); font-size: 10px; font-weight: normal; font-family: 'Swis721 BT';")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.number_label)
        
        self.setText(text)
        
    # Встановлення тексту з розбиттям на заголовок та опис
    def setText(self, text):
        if "\n" in text:
            parts = text.split("\n", 1)
            self.title_label.setText(parts[0])
            self.desc_label.setText(parts[1])
        else:
            self.title_label.setText(text)
            self.desc_label.setText("")
            
    # Обробка натискання миші
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(True)
            
    # Властивість кольору тайлу
    @pyqtProperty(QColor)
    def color(self):
        return self.Color
        
    # Встановлення кольору та оновлення стилю тайлу
    @color.setter
    def color(self, color):
        self.Color = color
        self.setStyleSheet(f"""
            LcarsTile {{
                background-color: {color.name()};
                border-radius: 2px;
                border-bottom-right-radius: 0px; 
            }}
            QLabel {{
                background: transparent;
                border: none;
                color: black;
                font-weight: normal;
                text-transform: uppercase;
            }}
        """)
        
    # Публічний метод встановлення кольору тайлу
    def SetColor(self, color):
        self.color = color


# Іконічний LCARS L-подібний (Elbow) конектор - Стиль 25-го Століття
class LcarsElbow(QWidget):
    # Ініціалізація elbow конектора з кольором, напрямом та розміром
    def __init__(self, color="#37A6D1", direction="top-left", size=(150, 80), parent=None):
        super().__init__(parent)
        self.color = color
        self.direction = direction
        self.setFixedSize(QSize(*size))

    # Оновлення кольору та перемальовування
    def SetColor(self, color):
        self.color = color
        self.update()

    # Малювання L-подібної форми elbow
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        w, h = self.width(), self.height()
        bar_height = 40  # Стандартна висота смуги
        curve_radius = 40
        
        path = QPainterPath()
        
        # Малювання залежно від напрямку
        if self.direction == "top-left":
            # Горизонтальна верхня частина
            path.moveTo(w, 0)
            path.lineTo(curve_radius + 20, 0)
            # Зовнішня крива
            path.cubicTo(curve_radius, 0, 0, 0, 0, curve_radius)
            # Вертикальна нижня частина
            path.lineTo(0, h)
            path.lineTo(bar_height, h) 
            path.lineTo(bar_height, curve_radius + 20)
            # Внутрішня крива
            path.cubicTo(bar_height, bar_height, bar_height, bar_height, w, bar_height)
            
        p.drawPath(path)

# Контейнер з користувацьким стилем LCARS із заголовковим elbow
class LcarsFrame(QFrame):
    # Ініціалізація контейнера з заголовком та кольором
    def __init__(self, title, color="#37A6D1", parent=None):
        super().__init__(parent)
        self.title = title.upper()
        self.color = color
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 45, 10, 10)
        
    # Малювання заголовкової панелі з elbow та текстом
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        w, h = rect.width(), rect.height()
        
        # Заголовкова смуга
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        # Elbow
        thickness = 30
        path = QPainterPath()
        path.moveTo(thickness + 10, 0)
        path.lineTo(w - 20, 0)
        path.arcTo(w - 20, 0, 20, 20, 90, -90)
        path.lineTo(w, thickness)
        path.lineTo(thickness, thickness)
        path.arcTo(0, 0, thickness*2, thickness*2, 90, 90)
        path.lineTo(0, h)
        path.lineTo(10, h)
        path.lineTo(10, thickness)
        path.arcTo(10, thickness, 2, 2, 180, -90)
        path.lineTo(thickness + 10, thickness)
        path.closeSubpath()
        
        p.drawPath(path)
        
        # Текст заголовка
        p.setPen(QPen(QColor("#000000"), 2))
        font = QFont("Swis721 BT", 12, QFont.Weight.Normal)
        p.setFont(font)
        p.drawText(QRect(thickness + 20, 5, w - thickness - 40, thickness - 10), 
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.title)
