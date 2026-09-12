# =============================================================================
# LCARS UI DESIGNER - STANDALONE VERSION
# =============================================================================
# Цей файл є повністю незалежним UI дизайнером для створення інтерфейсів LCARS.
# Всі компоненти LCARS вбудовані безпосередньо в цей файл.
# Для запуску потрібно тільки: pip install PyQt6
# =============================================================================

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import List, Dict, Optional, Callable, Any
# Titanium Bridge Migration: from enum import Enum, auto

# ------------------------------------------------------------------------------
# Спроба імпорту PyQt6 - бібліотека для створення графічного інтерфейсу
# ------------------------------------------------------------------------------
if True:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
        QWidget, QLabel, QFrame, QSplitter, QMenuBar, QStatusBar,
        QMessageBox, QFileDialog, QPushButton, QGraphicsDropShadowEffect,
        QScrollArea, QGridLayout, QLineEdit, QComboBox, QSpinBox,
        QTextEdit, QDialog, QDialogButtonBox, QFormLayout, QCheckBox,
        QTabWidget, QGroupBox, QSlider, QProgressBar, QListWidget,
        QListWidgetItem, QTreeWidget, QTreeWidgetItem, QInputDialog,
        QFileDialog, QColorDialog, QFontDialog, QMenu, QToolBar,
        QDockWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
        QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsItem,
        QGraphicsProxyWidget, QGraphicsObject, QGraphicsWidget
    )
    from PyQt6.QtCore import (
        Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, 
        QPoint, QRect, QSize, QPointF, QRectF, QThread,
        QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup,
        QVariantAnimation, QByteArray, QDataStream, QIODevice
    )
    from PyQt6.QtGui import (
        QAction, QFont, QIcon, QColor, QPainter, QPen, QBrush,
        QPainterPath, QLinearGradient, QRadialGradient, QFontMetrics,
        QKeySequence, QCursor, QPixmap, QImage, QTransform, QPolygonF,
        QFontDatabase, QPalette
    )
    
if False: # Removed except block
    print("=" * 60)
    print("❌ ПОМИЛКА ІМПОРТУ: PyQt6 не встановлено")
    print("=" * 60)
    print(f"Деталі: {import_error}")
    print()
    print("Для встановлення виконайте команду:")
    print("  pip install PyQt6")
    print()
    input("Натисніть Enter для виходу...")
    sys.exit(1)


# =============================================================================
# LCARS КОНСТАНТИ ТА ТЕМИ
# =============================================================================

class LCARSEra(Enum):
    """Епохи LCARS інтерфейсу з різних часових періодів Star Trek"""
    COMS_22ND = auto()      # 22 століття - ранні дні Зоряного флоту
    PCARS_23RD = auto()     # 23 століття - класична ера TOS
    LCARS_24TH = auto()     # 24 століття - ера TNG/DS9/VOY
    LCARS_25TH = auto()     # 25 століття - сучасна ера
    KELVIN = auto()         # Альтернативна реальність Кельвіна
    DISCOVERY = auto()      # Ера Discovery
    PICARD = auto()         # Ера Picard
    LOWER_DECKS = auto()    # Стилізована ера Lower Decks
    PRODIGY = auto()        # Ера Prodigy для молодої аудиторії


class FactionEra(Enum):
    """Фракції всесвіту Star Trek з різними стилями інтерфейсу"""
    FEDERATION = auto()     # Об'єднана Федерація Планет
    KLINGON = auto()        # Клінгонська Імперія
    ROMULAN = auto()        # Ромулянський Старий Орден
    CARDASSIAN = auto()     # Кардасіанський Союз
    BORG = auto()           # Колектив Боргів
    DOMINION = auto()       # Домініон
    BREEN = auto()          # Брін Конфедерація
    FERENGI = auto()        # Ференгі Альянс
    VULCAN = auto()         # Вулканська Директорат
    ANDORIAN = auto()       # Андоріанська Імперія


# Кольорові палітри для різних епох та фракцій
LCARS_COLORS = {
    # Стандартні LCARS кольори 24-го століття (TNG)
    "standard": {
        "orange": "#FF9900",      # Головний помаранчевий
        "orange_light": "#FFBB66", # Світлий помаранчевий
        "orange_dark": "#CC7A00",  # Темний помаранчевий
        "blue": "#00CCFF",        # Головний блакитний
        "blue_light": "#66DDFF",   # Світлий блакитний
        "blue_dark": "#0099CC",    # Темний блакитний
        "green": "#66FF66",        # Головний зелений
        "green_light": "#99FF99",  # Світлий зелений
        "green_dark": "#33CC33",   # Темний зелений
        "red": "#FF6666",          # Червоний для критичних попереджень
        "red_dark": "#CC3333",     # Темний червоний
        "purple": "#CC99FF",       # Фіолетовий
        "tan": "#CC9966",          # Тановий
        "black": "#000000",        # Чорний фон
        "dark_gray": "#1a1a1a",    # Темно-сірий
        "medium_gray": "#333333",  # Середньо-сірий
        "light_gray": "#666666",   # Світло-сірий
        "white": "#FFFFFF",        # Білий текст
        "text_orange": "#FFCC99",  # Текстовий помаранчевий
    },
    # 22 століття (Enterprise)
    "coms_22nd": {
        "orange": "#CC7A33",
        "blue": "#5599AA",
        "green": "#77AA77",
        "black": "#0a0a0a",
        "dark_gray": "#151515",
    },
    # 23 століття (TOS)
    "pcars_23rd": {
        "orange": "#FFCC00",
        "blue": "#00AAFF",
        "green": "#55FF55",
        "red": "#FF4444",
        "black": "#111111",
    },
    # 25 століття (сучасна)
    "lcars_25th": {
        "orange": "#FF8800",
        "orange_light": "#FFAA44",
        "blue": "#00DDFF",
        "green": "#44FF88",
        "purple": "#AA66FF",
        "black": "#050505",
    },
    # Клінгонська Імперія
    "klingon": {
        "primary": "#CC3333",      # Клінгонський червоний
        "secondary": "#993333",   # Темний червоний
        "accent": "#FF6666",      # Світлий червоний
        "black": "#0a0000",       # Темний фон
        "metal": "#444444",       # Металевий
    },
    # Ромулянський Старий Орден
    "romulan": {
        "primary": "#339966",     # Ромулянський зелений
        "secondary": "#226644",
        "accent": "#66CC99",
        "black": "#000a05",
    },
    # Кардасіанський Союз
    "cardassian": {
        "primary": "#AA8833",     # Кардасіанський бурштиновий
        "secondary": "#775522",
        "accent": "#CCAA55",
        "black": "#0a0805",
    },
    # Борг
    "borg": {
        "primary": "#88AA88",     # Борг зелений
        "secondary": "#556655",
        "accent": "#AADDAA",
        "black": "#050805",
    },
}


def get_theme_colors(era: LCARSEra = LCARSEra.LCARS_24TH, 
                     faction: FactionEra = FactionEra.FEDERATION) -> Dict[str, str]:
    """
    Отримати кольорову палітру для вказаної епохи та фракції.
    
    Параметри:
        era: Епоха LCARS інтерфейсу
        faction: Фракція всесвіту Star Trek
    
    Повертає:
        Словник з кольоровими кодами HEX
    """
    if faction == FactionEra.KLINGON:
        return LCARS_COLORS["klingon"]
    elif faction == FactionEra.ROMULAN:
        return LCARS_COLORS["romulan"]
    elif faction == FactionEra.CARDASSIAN:
        return LCARS_COLORS["cardassian"]
    elif faction == FactionEra.BORG:
        return LCARS_COLORS["borg"]
    
    if era == LCARSEra.COMS_22ND:
        return {**LCARS_COLORS["standard"], **LCARS_COLORS["coms_22nd"]}
    elif era == LCARSEra.PCARS_23RD:
        return {**LCARS_COLORS["standard"], **LCARS_COLORS["pcars_23rd"]}
    elif era == LCARSEra.LCARS_25TH:
        return {**LCARS_COLORS["standard"], **LCARS_COLORS["lcars_25th"]}
    
    return LCARS_COLORS["standard"]


# =============================================================================
# БАЗОВІ LCARS ВІДЖЕТИ (ВБУДОВАНІ)
# =============================================================================

class LCARSBaseWidget(QFrame):
    """
    Базовий клас для всіх LCARS віджетів.
    Надає спільну функціональність для стилізації та анімації.
    """
    
    clicked = pyqtSignal()  # Сигнал натискання
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        # Параметри анімації
        self.animation_duration = 300  # мілісекунди
        self.hover_animation = None
        self.is_hovered = False
        
        # Встановити відстеження миші
        self.setMouseTracking(True)
    
    def enterEvent(self, event):
        """Подія наведення миші - запускає анімацію наведення"""
        self.is_hovered = True
        self._animate_hover(True)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Подія відведення миші - запускає анімацію відведення"""
        self.is_hovered = False
        self._animate_hover(False)
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Подія натискання миші - емітує сигнал clicked"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def _animate_hover(self, entering: bool):
        """
        Анімація наведення/відведення миші.
        
        Параметри:
            entering: True якщо миша входить, False якщо виходить
        """
        pass  # Реалізація в підкласах


class LCARSButton(LCARSBaseWidget):
    """
    Кнопка у стилі LCARS з характерною формою та анімацією.
    Підтримує різні форми: прямокутник, закруглений, капсула.
    """
    
    def __init__(self, text: str = "BUTTON", color: str = "#FF9900",
                 shape: str = "rect", width: int = 150, height: int = 40,
                 font_size: int = 11, parent=None):
        """
        Ініціалізація кнопки LCARS.
        
        Параметри:
            text: Текст на кнопці
            color: HEX колір кнопки
            shape: Форма кнопки ("rect", "rounded", "capsule", "left", "right")
            width: Ширина кнопки в пікселях
            height: Висота кнопки в пікселях
            font_size: Розмір шрифту в точках
            parent: Батьківський віджет
        """
        super().__init__(parent)
        
        self.button_text = text
        self.base_color = QColor(color)
        self.button_shape = shape
        self.button_width = width
        self.button_height = height
        self.font_size = font_size
        
        self.setFixedSize(width, height)
        self._update_style()
    
    def _update_style(self):
        """Оновити стилі кнопки відповідно до поточних параметрів"""
        border_radius = self._get_border_radius()
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.base_color.name()};
                border-radius: {border_radius}px;
                border: none;
            }}
            QFrame:hover {{
                background-color: {self.base_color.lighter(120).name()};
            }}
        """)
    
    def _get_border_radius(self) -> int:
        """Отримати радіус закруглення кутів залежно від форми"""
        if self.button_shape == "capsule":
            return self.button_height // 2
        elif self.button_shape == "rounded":
            return 8
        elif self.button_shape in ["left", "right"]:
            return 0  # Спеціальна форма малюється вручну
        else:  # rect
            return 0
    
    def paintEvent(self, event):
        """Малювання кастомної кнопки з текстом"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Створити шлях для кнопки залежно від форми
        path = self._create_button_path()
        
        # Малювати фон
        painter.fillPath(path, QBrush(self.base_color))
        
        # Малювати текст
        painter.setPen(QPen(QColor("#000000")))
        font = QFont("Swiss 911 BT", self.font_size)
        font.setBold(True)
        painter.setFont(font)
        
        rect = self.rect()
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.button_text)
    
    def _create_button_path(self) -> QPainterPath:
        """Створити графічний шлях для кнопки залежно від форми"""
        path = QPainterPath()
        width = self.width()
        height = self.height()
        
        if self.button_shape == "capsule":
            radius = height / 2
            path.addRoundedRect(0, 0, width, height, radius, radius)
        elif self.button_shape == "left":
            # Закруглена тільки ліва сторона
            radius = height / 2
            path.moveTo(radius, 0)
            path.lineTo(width, 0)
            path.lineTo(width, height)
            path.lineTo(radius, height)
            path.arcTo(0, 0, height, height, 180, 180)
        elif self.button_shape == "right":
            # Закруглена тільки права сторона
            radius = height / 2
            path.moveTo(0, 0)
            path.lineTo(width - radius, 0)
            path.arcTo(width - height, 0, height, height, 90, -180)
            path.lineTo(0, height)
        else:
            # Прямокутник або закруглений
            radius = 8 if self.button_shape == "rounded" else 0
            path.addRoundedRect(0, 0, width, height, radius, radius)
        
        return path


class LCARSElbow(LCARSBaseWidget):
    """
    Ліктєвий елемент LCARS - характерна закруглена панель.
    Використовується для створення фірмового вигляду LCARS інтерфейсу.
    """
    
    def __init__(self, color: str = "#FF9900", orientation: str = "top-left",
                 width: int = 200, height: int = 150, thickness: int = 40,
                 parent=None):
        """
        Ініціалізація ліктєвого елемента.
        
        Параметри:
            color: HEX колір елемента
            orientation: Орієнтація ("top-left", "top-right", "bottom-left", "bottom-right")
            width: Загальна ширина елемента
            height: Загальна висота елемента
            thickness: Товщина ліктя
            parent: Батьківський віджет
        """
        super().__init__(parent)
        
        self.elbow_color = QColor(color)
        self.orientation = orientation
        self.elbow_width = width
        self.elbow_height = height
        self.thickness = thickness
        
        self.setFixedSize(width, height)
    
    def paintEvent(self, event):
        """Малювання ліктєвого елемента"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = self._create_elbow_path()
        painter.fillPath(path, QBrush(self.elbow_color))
    
    def _create_elbow_path(self) -> QPainterPath:
        """Створити шлях для ліктєвого елемента"""
        path = QPainterPath()
        w = self.elbow_width
        h = self.elbow_height
        t = self.thickness
        
        if self.orientation == "top-left":
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, t)
            path.lineTo(t, t)
            path.lineTo(t, h)
            path.lineTo(0, h)
            path.closeSubpath()
        elif self.orientation == "top-right":
            path.moveTo(0, 0)
            path.lineTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(w - t, h)
            path.lineTo(w - t, t)
            path.lineTo(0, t)
            path.closeSubpath()
        elif self.orientation == "bottom-left":
            path.moveTo(0, 0)
            path.lineTo(t, 0)
            path.lineTo(t, h - t)
            path.lineTo(w, h - t)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.closeSubpath()
        elif self.orientation == "bottom-right":
            path.moveTo(0, 0)
            path.lineTo(w - t, 0)
            path.lineTo(w - t, h - t)
            path.lineTo(0, h - t)
            path.closeSubpath()
            path.moveTo(w, 0)
            path.lineTo(w, h)
            path.lineTo(0, h)
            path.lineTo(0, h - t)
        
        return path


class LCARSContour(LCARSBaseWidget):
    """
    Контурна панель LCARS - рамка з характерними закругленнями.
    """
    
    def __init__(self, title: str = "", color: str = "#FF9900",
                 width: int = 300, height: int = 200, parent=None):
        super().__init__(parent)
        
        self.panel_title = title
        self.contour_color = QColor(color)
        self.panel_width = width
        self.panel_height = height
        
        self.setFixedSize(width, height)
        
        # Внутрішній layout
        self.inner_layout = QVBoxLayout(self)
        self.inner_layout.setContentsMargins(20, 30, 20, 20)
        self.inner_layout.setSpacing(10)
        
        # Заголовок
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet(f"""
                color: {color};
                font-size: 14px;
                font-weight: bold;
                font-family: "Swiss 911 BT", "Arial", sans-serif;
            """)
            self.inner_layout.addWidget(self.title_label)
    
    def paintEvent(self, event):
        """Малювання контуру панелі"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(self.contour_color, 3)
        painter.setPen(pen)
        
        # Малювати рамку з закругленими кутами
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRoundedRect(rect, 15, 15)


class LCARSBar(LCARSBaseWidget):
    """Горизонтальна або вертикальна панель LCARS"""
    
    def __init__(self, color: str = "#FF9900", orientation: str = "horizontal",
                 size: int = 40, length: int = 200, parent=None):
        super().__init__(parent)
        
        self.bar_color = QColor(color)
        self.orientation = orientation
        
        if orientation == "horizontal":
            self.setFixedSize(length, size)
        else:
            self.setFixedSize(size, length)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        radius = min(self.width(), self.height()) // 2
        painter.fillRect(self.rect(), self.bar_color)


class LCARSLabel(QLabel):
    """Мітка у стилі LCARS з характерним шрифтом"""
    
    def __init__(self, text: str = "", color: str = "#FF9900", 
                 font_size: int = 12, parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet(f"""
            color: {color};
            font-size: {font_size}px;
            font-family: "Swiss 911 BT", "Arial", sans-serif;
            font-weight: bold;
            background: transparent;
        """)
        
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)


class LCARSHeader(LCARSLabel):
    """Заголовкова мітка LCARS"""
    
    def __init__(self, text: str = "", color: str = "#FF9900", parent=None):
        super().__init__(text, color, 18, parent)
        self.setStyleSheet(f"""
            color: {color};
            font-size: 18px;
            font-family: "Swiss 911 BT", "Arial", sans-serif;
            font-weight: bold;
            background: transparent;
            padding: 10px;
            border-bottom: 2px solid {color};
        """)


class LCARSText(QTextEdit):
    """Текстова область у стилі LCARS"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #FFCC99;
                border: 2px solid #FF9900;
                border-radius: 8px;
                font-family: "Swiss 911 BT", "Courier New", monospace;
                font-size: 12px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #FFCC00;
            }
        """)
        
        self.setReadOnly(False)


# =============================================================================
# КОНСТРУКТОР ІНТЕРФЕЙСУ (ВБУДОВАНИЙ)
# =============================================================================

@dataclass
class ComponentData:
    """Дані про компонент інтерфейсу для серіалізації"""
    component_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    size: Dict[str, int] = field(default_factory=lambda: {"width": 100, "height": 50})


class InterfaceConstructor(QFrame):
    """
    Конструктор інтерфейсу - головна робоча область дизайнера.
    Дозволяє розміщувати та редагувати LCARS компоненти.
    """
    
    component_selected = pyqtSignal(object)  # Сигнал вибору компоненту
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        self.setStyleSheet("""
            QFrame {
                background-color: #050505;
                border: 2px solid #333333;
                border-radius: 0px;
            }
        """)
        
        # Список всіх компонентів на полотні
        self.components: List[LCARSBaseWidget] = []
        self.selected_component = None
        
        # Layout для розміщення компонентів
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)
        
        # Область для перетягування компонентів
        self.canvas = QFrame()
        self.canvas.setStyleSheet("""
            QFrame {
                background-color: #0a0a0a;
                border: 1px dashed #333333;
            }
        """)
        self.canvas_layout = QVBoxLayout(self.canvas)
        self.canvas_layout.setContentsMargins(10, 10, 10, 10)
        
        self.main_layout.addWidget(self.canvas)
        
        # Інформаційна панель
        self.info_label = QLabel("◤ WORKSPACE - Ready for components")
        self.info_label.setStyleSheet("""
            color: #666666;
            font-size: 11px;
            font-family: "Swiss 911 BT", "Arial", sans-serif;
            padding: 5px;
        """)
        self.main_layout.addWidget(self.info_label)
    
    def add_component(self, component: LCARSBaseWidget, row: int = -1):
        """
        Додати компонент на полотно конструктора.
        
        Параметри:
            component: LCARS віджет для додавання
            row: Позиція рядка (-1 для додавання в кінець)
        """
        # Встановити з'єднання для сигналу вибору
        component.clicked.connect(lambda: self._select_component(component))
        
        # Додати до списку та layout
        self.components.append(component)
        
        if row >= 0:
            self.canvas_layout.insertWidget(row, component)
        else:
            self.canvas_layout.addWidget(component)
        
        self._update_info()
        
        # Автоматично вибрати новий компонент
        self._select_component(component)
    
    def remove_component(self, component: LCARSBaseWidget):
        """Видалити компонент з полотна"""
        if component in self.components:
            self.components.remove(component)
            component.deleteLater()
            
            if self.selected_component == component:
                self.selected_component = None
                self.component_selected.emit(None)
            
            self._update_info()
    
    def clear_all(self):
        """Очистити все полотно"""
        for component in self.components[:]:
            self.remove_component(component)
    
    def _select_component(self, component: LCARSBaseWidget):
        """Вибрати компонент для редагування"""
        # Зняти виділення з попереднього
        if self.selected_component:
            self._set_component_highlight(self.selected_component, False)
        
        self.selected_component = component
        self._set_component_highlight(component, True)
        self.component_selected.emit(component)
    
    def _set_component_highlight(self, component: LCARSBaseWidget, highlight: bool):
        """Встановити підсвічування компоненту"""
        if highlight:
            component.setStyleSheet(component.styleSheet() + """
                QFrame {
                    border: 2px solid #00CCFF !important;
                }
            """)
        else:
            # Прибрати підсвічування - перезастосувати базові стилі
            component.setStyleSheet("")
            if isinstance(component, LCARSButton):
                component._update_style()
    
    def _update_info(self):
        """Оновити інформаційну панель"""
        count = len(self.components)
        self.info_label.setText(f"◤ WORKSPACE - {count} component(s) active")
    
    def get_selected_properties(self) -> Dict[str, Any]:
        """Отримати властивості вибраного компоненту"""
        if not self.selected_component:
            return {}
        
        component = self.selected_component
        properties = {
            "type": type(component).__name__,
            "width": component.width(),
            "height": component.height(),
        }
        
        if isinstance(component, LCARSButton):
            properties["text"] = component.button_text
            properties["color"] = component.base_color.name()
            properties["shape"] = component.button_shape
        elif isinstance(component, LCARSElbow):
            properties["color"] = component.elbow_color.name()
            properties["orientation"] = component.orientation
            properties["thickness"] = component.thickness
        elif isinstance(component, LCARSContour):
            properties["title"] = component.panel_title
            properties["color"] = component.contour_color.name()
        
        return properties
    
    def export_layout(self) -> List[ComponentData]:
        """Експортувати розкладку для збереження"""
        data = []
        for component in self.components:
            pos = component.pos()
            size = component.size()
            
            comp_data = ComponentData(
                component_type=type(component).__name__,
                position={"x": pos.x(), "y": pos.y()},
                size={"width": size.width(), "height": size.height()}
            )
            
            # Додати специфічні властивості
            if isinstance(component, LCARSButton):
                comp_data.properties = {
                    "text": component.button_text,
                    "color": component.base_color.name(),
                    "shape": component.button_shape,
                }
            elif isinstance(component, LCARSElbow):
                comp_data.properties = {
                    "color": component.elbow_color.name(),
                    "orientation": component.orientation,
                    "thickness": component.thickness,
                }
            
            data.append(comp_data)
        
        return data
    
    def import_layout(self, data: List[ComponentData]):
        """Імпортувати розкладку з даних"""
        self.clear_all()
        
        for comp_data in data:
            component = None
            
            if comp_data.component_type == "LCARSButton":
                props = comp_data.properties
                component = LCARSButton(
                    text=props.get("text", "BUTTON"),
                    color=props.get("color", "#FF9900"),
                    shape=props.get("shape", "rect"),
                    width=comp_data.size.get("width", 150),
                    height=comp_data.size.get("height", 40)
                )
            elif comp_data.component_type == "LCARSElbow":
                props = comp_data.properties
                component = LCARSElbow(
                    color=props.get("color", "#FF9900"),
                    orientation=props.get("orientation", "top-left"),
                    width=comp_data.size.get("width", 200),
                    height=comp_data.size.get("height", 150),
                    thickness=props.get("thickness", 40)
                )
            
            if component:
                self.add_component(component)


# =============================================================================
# ГОЛОВНЕ ВІКНО ДИЗАЙНЕРА
# =============================================================================

class LCARSDesignerWindow(QMainWindow):
    """
    Головне вікно дизайнера LCARS інтерфейсів.
    Має три панелі: інструменти зліва, конструктор по центру, властивості справа.
    """
    
    def __init__(self):
        super().__init__()
        
        # Встановити заголовок та розміри вікна
        self.setWindowTitle("◤ LCARS ARCHITECT - UI DESIGNER v3.0 [STANDALONE]")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Поточна тема
        self.current_era = LCARSEra.LCARS_24TH
        self.current_faction = FactionEra.FEDERATION
        self.colors = get_theme_colors(self.current_era, self.current_faction)
        
        # Застосувати LCARS стилізацію
        self.setup_lcars_style()
        self.setup_menu()
        self.setup_ui()
        
        # Таймер для оновлення статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Оновлювати кожну секунду
        
        # Шлях до поточного проекту
        self.current_project_path = None
        
        print("◤ [ARCHITECT] Система ініціалізована")
    
    def setup_lcars_style(self):
        """
        Застосувати LCARS стилізацію до головного вікна.
        Встановлює кольори, шрифти та рамки для всіх елементів інтерфейсу.
        """
        orange = self.colors.get("orange", "#FF9900")
        black = self.colors.get("black", "#000000")
        dark_gray = self.colors.get("dark_gray", "#1a1a1a")
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {black};
                color: {orange};
                font-family: "Swiss 911 BT", "Arial", sans-serif;
            }}
            QMenuBar {{
                background-color: {dark_gray};
                border-bottom: 2px solid {orange};
                color: {orange};
                font-size: 12px;
                font-weight: bold;
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 8px 16px;
                spacing: 3px;
            }}
            QMenuBar::item:selected {{
                background-color: {orange};
                color: {black};
            }}
            QMenu {{
                background-color: {dark_gray};
                border: 2px solid {orange};
                color: {orange};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {orange};
                color: {black};
            }}
            QStatusBar {{
                background-color: {dark_gray};
                border-top: 2px solid {orange};
                color: {orange};
                font-size: 12px;
            }}
            QFrame {{
                background-color: transparent;
            }}
            QLabel {{
                color: {orange};
                font-family: "Swiss 911 BT", "Arial", sans-serif;
            }}
        """)
    
    def setup_menu(self):
        """
        Налаштувати рядок меню програми.
        Додає меню File, View, Tools, Help з відповідними діями.
        """
        menubar = self.menuBar()
        
        # Меню FILE - операції з файлами
        file_menu = menubar.addMenu("◤ FILE")
        
        new_action = QAction("NEW PROJECT", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("OPEN PROJECT", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("SAVE PROJECT", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("SAVE AS...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("EXPORT PYTHON CODE", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_code)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("EXIT", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню VIEW - налаштування відображення
        view_menu = menubar.addMenu("◤ VIEW")
        
        # Підменю вибору епохи
        era_menu = view_menu.addMenu("ERA THEME")
        
        for era in LCARSEra:
            era_action = QAction(f"ERA: {era.name.replace('_', ' ')}", self)
            era_action.triggered.connect(lambda checked, era_value=era: self.change_era(era_value))
            era_menu.addAction(era_action)
        
        # Підменю вибору фракції
        faction_menu = view_menu.addMenu("FACTION THEME")
        
        for faction in FactionEra:
            faction_action = QAction(f"FACTION: {faction.name.replace('_', ' ')}", self)
            faction_action.triggered.connect(lambda checked, faction_value=faction: self.change_faction(faction_value))
            faction_menu.addAction(faction_action)
        
        view_menu.addSeparator()
        
        # Меню TOOLS - інструменти дизайнера
        tools_menu = menubar.addMenu("◤ TOOLS")
        
        preview_action = QAction("PREVIEW UI", self)
        preview_action.setShortcut("F5")
        preview_action.triggered.connect(self.preview_ui)
        tools_menu.addAction(preview_action)
        
        clear_action = QAction("CLEAR WORKSPACE", self)
        clear_action.triggered.connect(self.clear_workspace)
        tools_menu.addAction(clear_action)
        
        # Меню HELP - довідка
        help_menu = menubar.addMenu("◤ HELP")
        
        about_action = QAction("ABOUT", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_ui(self):
        """
        Налаштувати головний інтерфейс програми.
        Створює трипанельний layout: інструменти, конструктор, властивості.
        """
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний горизонтальний layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Ліва панель - інструменти та компоненти
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Центральна панель - конструктор інтерфейсу
        self.constructor = InterfaceConstructor()
        self.constructor.component_selected.connect(self.on_component_selected)
        main_layout.addWidget(self.constructor, 4)
        
        # Права панель - властивості компонентів
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # Рядок статусу
        self.statusBar().showMessage("◤ LCARS ARCHITECT v3.0 - Ready")
    
    def create_left_panel(self) -> QFrame:
        """
        Створити ліву панель з інструментами та компонентами.
        
        Повертає:
            QFrame з панеллю інструментів
        """
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: #0a0a0a;
                border-right: 3px solid {self.colors.get("orange", "#FF9900")};
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Заголовок панелі
        header = LCARSHeader("◤ COMPONENTS", self.colors.get("orange", "#FF9900"))
        layout.addWidget(header)
        
        # Роздільник
        separator = LCARSBar(self.colors.get("orange", "#FF9900"), "horizontal", 3, 250)
        layout.addWidget(separator)
        
        # Кнопки компонентів
        layout.addWidget(LCARSLabel("Basic Components:", self.colors.get("blue", "#00CCFF"), 11))
        
        btn_panel = LCARSButton("ADD PANEL", self.colors.get("orange", "#FF9900"), "rect", 250, 45, 12)
        btn_panel.clicked.connect(self.add_panel)
        layout.addWidget(btn_panel)
        
        btn_elbow = LCARSButton("ADD ELBOW", self.colors.get("blue", "#00CCFF"), "rect", 250, 45, 12)
        btn_elbow.clicked.connect(self.add_elbow)
        layout.addWidget(btn_elbow)
        
        btn_button = LCARSButton("ADD BUTTON", self.colors.get("green", "#66FF66"), "rect", 250, 45, 12)
        btn_button.clicked.connect(self.add_button)
        layout.addWidget(btn_button)
        
        btn_contour = LCARSButton("ADD CONTOUR", self.colors.get("purple", "#CC99FF"), "rect", 250, 45, 12)
        btn_contour.clicked.connect(self.add_contour)
        layout.addWidget(btn_contour)
        
        layout.addSpacing(20)
        
        # Спеціальні форми
        layout.addWidget(LCARSLabel("Special Shapes:", self.colors.get("blue", "#00CCFF"), 11))
        
        btn_capsule = LCARSButton("CAPSULE BTN", self.colors.get("orange_light", "#FFBB66"), "capsule", 250, 45, 12)
        btn_capsule.clicked.connect(self.add_capsule_button)
        layout.addWidget(btn_capsule)
        
        btn_rounded = LCARSButton("ROUNDED BTN", self.colors.get("tan", "#CC9966"), "rounded", 250, 45, 12)
        btn_rounded.clicked.connect(self.add_rounded_button)
        layout.addWidget(btn_rounded)
        
        # Розтягнути залишок простору
        layout.addStretch()
        
        # Версія внизу
        version_label = LCARSLabel("v3.0 STANDALONE", self.colors.get("light_gray", "#666666"), 9)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        return panel
    
    def create_right_panel(self) -> QFrame:
        """
        Створити праву панель з властивостями компонентів.
        
        Повертає:
            QFrame з панеллю властивостей
        """
        panel = QFrame()
        panel.setFixedWidth(280)
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: #0a0a0a;
                border-left: 3px solid {self.colors.get("orange", "#FF9900")};
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Заголовок панелі
        header = LCARSHeader("◤ PROPERTIES", self.colors.get("orange", "#FF9900"))
        layout.addWidget(header)
        
        # Роздільник
        separator = LCARSBar(self.colors.get("orange", "#FF9900"), "horizontal", 3, 250)
        layout.addWidget(separator)
        
        # Область властивостей
        self.properties_area = LCARSLabel("Select component to view properties", "#888888", 11)
        self.properties_area.setWordWrap(True)
        self.properties_area.setMinimumHeight(200)
        layout.addWidget(self.properties_area)
        
        # Кнопка видалення
        layout.addStretch()
        
        btn_delete = LCARSButton("DELETE SELECTED", self.colors.get("red", "#FF6666"), "rect", 250, 45, 12)
        btn_delete.clicked.connect(self.delete_selected)
        layout.addWidget(btn_delete)
        
        btn_clear = LCARSButton("CLEAR ALL", self.colors.get("red_dark", "#CC3333"), "rect", 250, 45, 12)
        btn_clear.clicked.connect(self.clear_workspace)
        layout.addWidget(btn_clear)
        
        return panel
    
    def update_status(self):
        """Оновити рядок статусу з поточним часом"""
        # Titanium Bridge Migration: from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        component_count = len(self.constructor.components)
        
        self.statusBar().showMessage(
            f"◤ LCARS ARCHITECT v3.0 - {current_time} UTC - Components: {component_count}"
        )
    
    # --------------------------------------------------------------------------
    # Обробники дій меню FILE
    # --------------------------------------------------------------------------
    
    def new_project(self):
        """Створити новий проект - очистити робочу область"""
        reply = QMessageBox.question(
            self, "NEW PROJECT",
            "Create new project? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.constructor.clear_all()
            self.current_project_path = None
            self.statusBar().showMessage("◤ New project created")
    
    def open_project(self):
        """Відкрити проект з файлу"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open LCARS Project", "",
            "LCARS Project Files (*.lcars.json);;All Files (*)"
        )
        
        if file_path:
            if True:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    # Конвертувати словники назад в ComponentData
                    components_data = []
                    for item in data.get("components", []):
                        comp_data = ComponentData(
                            component_type=item["component_type"],
                            properties=item.get("properties", {}),
                            position=item.get("position", {"x": 0, "y": 0}),
                            size=item.get("size", {"width": 100, "height": 50})
                        )
                        components_data.append(comp_data)
                    
                    self.constructor.import_layout(components_data)
                    self.current_project_path = file_path
                    self.statusBar().showMessage(f"◤ Opened: {file_path}")
                    
            if False: # Removed except block
                QMessageBox.critical(
                    self, "ERROR",
                    f"Failed to open project:\n{str(error)}"
                )
    
    def save_project(self):
        """Зберегти проект в поточний файл"""
        if self.current_project_path:
            self._save_to_file(self.current_project_path)
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Зберегти проект з вибором шляху"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save LCARS Project", "",
            "LCARS Project Files (*.lcars.json);;All Files (*)"
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_project_path = file_path
    
    def _save_to_file(self, file_path: str):
        """Зберегти дані проекту у файл"""
        if True:
            components_data = self.constructor.export_layout()
            
            # Конвертувати ComponentData в словники для JSON
            data = {
                "version": "3.0",
                "era": self.current_era.name,
                "faction": self.current_faction.name,
                "components": []
            }
            
            for comp in components_data:
                data["components"].append({
                    "component_type": comp.component_type,
                    "properties": comp.properties,
                    "position": comp.position,
                    "size": comp.size
                })
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            self.statusBar().showMessage(f"◤ Saved: {file_path}")
            
        if False: # Removed except block
            QMessageBox.critical(
                self, "ERROR",
                f"Failed to save project:\n{str(error)}"
            )
    
    def export_code(self):
        """Експортувати Python код для поточного інтерфейсу"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Python Code", "lcars_interface.py",
            "Python Files (*.py);;All Files (*)"
        )
        
        if file_path:
            if True:
                code = self._generate_python_code()
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(code)
                
                self.statusBar().showMessage(f"◤ Exported code to: {file_path}")
                
                QMessageBox.information(
                    self, "EXPORT SUCCESSFUL",
                    f"Python code exported to:\n{file_path}"
                )
                
            if False: # Removed except block
                QMessageBox.critical(
                    self, "EXPORT ERROR",
                    f"Failed to export code:\n{str(error)}"
                )
    
    def _generate_python_code(self) -> str:
        """Згенерувати Python код для поточного інтерфейсу"""
        code_lines = [
            "# =============================================================================",
            "# LCARS INTERFACE - AUTO GENERATED",
            "# =============================================================================",
            "# This code was generated by LCARS Architect v3.0",
            "# =============================================================================",
            "",
            "import sys",
            "from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout",
            "from PyQt6.QtCore import Qt",
            "",
            "# Додайте імпорт LCARS компонентів з вашого проекту",
            "# from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour",
            "",
            "class LCARSInterface(QWidget):",
            '    """Автоматично згенерований LCARS інтерфейс"""',
            "",
            "    def __init__(self):",
            "        super().__init__()",
            f'        self.setWindowTitle("LCARS Interface")',
            f'        self.setGeometry(100, 100, 800, 600)',
            "        self.setup_ui()",
            "",
            "    def setup_ui(self):",
            "        layout = QVBoxLayout(self)",
            "        layout.setSpacing(10)",
            "        layout.setContentsMargins(20, 20, 20, 20)",
            "",
        ]
        
        # Додати компоненти
        for i, component in enumerate(self.constructor.components):
            if isinstance(component, LCARSButton):
                code_lines.append(
                    f'        # Button {i+1}'
                )
                code_lines.append(
                    f'        button_{i+1} = LCARSButton("{component.button_text}", "{component.base_color.name()}")'
                )
                code_lines.append(
                    f'        layout.addWidget(button_{i+1})'
                )
                code_lines.append("")
            elif isinstance(component, LCARSElbow):
                code_lines.append(
                    f'        # Elbow {i+1}'
                )
                code_lines.append(
                    f'        elbow_{i+1} = LCARSElbow("{component.elbow_color.name()}", "{component.orientation}")'
                )
                code_lines.append(
                    f'        layout.addWidget(elbow_{i+1})'
                )
                code_lines.append("")
        
        code_lines.extend([
            "",
            "if __name__ == \"__main__\":",
            "    app = QApplication(sys.argv)",
            "    window = LCARSInterface()",
            "    window.show()",
            "    sys.exit(app.exec())",
            "",
        ])
        
        return "\n".join(code_lines)
    
    # --------------------------------------------------------------------------
    # Обробники дій меню VIEW
    # --------------------------------------------------------------------------
    
    def change_era(self, era: LCARSEra):
        """Змінити епоху теми інтерфейсу"""
        self.current_era = era
        self.colors = get_theme_colors(self.current_era, self.current_faction)
        self._refresh_theme()
        
        QMessageBox.information(
            self, "ERA CHANGED",
            f"Theme changed to {era.name.replace('_', ' ')}"
        )
    
    def change_faction(self, faction: FactionEra):
        """Змінити фракційну тему інтерфейсу"""
        self.current_faction = faction
        self.colors = get_theme_colors(self.current_era, self.current_faction)
        self._refresh_theme()
        
        QMessageBox.information(
            self, "FACTION CHANGED",
            f"Theme changed to {faction.name.replace('_', ' ')}"
        )
    
    def _refresh_theme(self):
        """Оновити тему інтерфейсу"""
        self.setup_lcars_style()
        # Перестворити UI щоб застосувати нові кольори
        self.setup_ui()
    
    # --------------------------------------------------------------------------
    # Обробники дій меню TOOLS
    # --------------------------------------------------------------------------
    
    def preview_ui(self):
        """Відкрити попередній перегляд UI"""
        if not self.constructor.components:
            QMessageBox.information(
                self, "PREVIEW",
                "No components to preview. Add some components first!"
            )
            return
        
        # Створити діалог попереднього перегляду
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("◤ LCARS PREVIEW")
        preview_dialog.setGeometry(200, 200, 600, 400)
        preview_dialog.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
        """)
        
        layout = QVBoxLayout(preview_dialog)
        
        label = LCARSLabel("UI Preview Mode", self.colors.get("orange", "#FF9900"), 16)
        layout.addWidget(label)
        
        info = LCARSLabel(
            f"Components: {len(self.constructor.components)}",
            self.colors.get("light_gray", "#666666"), 12
        )
        layout.addWidget(info)
        
        # Показати список компонентів
        component_list = QListWidget()
        component_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #0a0a0a;
                color: {self.colors.get("orange", "#FF9900")};
                border: 2px solid {self.colors.get("orange", "#FF9900")};
                font-family: "Swiss 911 BT", "Courier New", monospace;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #333333;
            }}
        """)
        
        for component in self.constructor.components:
            comp_type = type(component).__name__
            item_text = f"◤ {comp_type}"
            if isinstance(component, LCARSButton):
                item_text += f' - "{component.button_text}"'
            elif isinstance(component, LCARSElbow):
                item_text += f' - {component.orientation}'
            
            QListWidgetItem(item_text, component_list)
        
        layout.addWidget(component_list)
        
        # Кнопка закриття
        btn_ok = LCARSButton("CLOSE PREVIEW", self.colors.get("orange", "#FF9900"), "rect", 200, 40)
        btn_ok.clicked.connect(preview_dialog.accept)
        layout.addWidget(btn_ok, alignment=Qt.AlignmentFlag.AlignCenter)
        
        preview_dialog.exec()
    
    def clear_workspace(self):
        """Очистити робочу область"""
        reply = QMessageBox.question(
            self, "CLEAR WORKSPACE",
            "Remove all components? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.constructor.clear_all()
            self.properties_area.setText("Select component to view properties")
            self.statusBar().showMessage("◤ Workspace cleared")
    
    def delete_selected(self):
        """Видалити вибраний компонент"""
        if self.constructor.selected_component:
            self.constructor.remove_component(self.constructor.selected_component)
            self.properties_area.setText("Select component to view properties")
            self.statusBar().showMessage("◤ Component deleted")
        else:
            QMessageBox.information(
                self, "NO SELECTION",
                "No component selected. Click on a component first."
            )
    
    # --------------------------------------------------------------------------
    # Обробники додавання компонентів
    # --------------------------------------------------------------------------
    
    def add_panel(self):
        """Додати панель до конструктора"""
        panel = LCARSContour(
            title="PANEL",
            color=self.colors.get("orange", "#FF9900"),
            width=300,
            height=200
        )
        self.constructor.add_component(panel)
        self.statusBar().showMessage("◤ Panel added")
    
    def add_elbow(self):
        """Додати ліктєвий елемент до конструктора"""
        elbow = LCARSElbow(
            color=self.colors.get("blue", "#00CCFF"),
            orientation="top-left",
            width=200,
            height=150,
            thickness=40
        )
        self.constructor.add_component(elbow)
        self.statusBar().showMessage("◤ Elbow added")
    
    def add_button(self):
        """Додати кнопку до конструктора"""
        button = LCARSButton(
            text="LCARS BUTTON",
            color=self.colors.get("green", "#66FF66"),
            shape="rect",
            width=200,
            height=45,
            font_size=12
        )
        self.constructor.add_component(button)
        self.statusBar().showMessage("◤ Button added")
    
    def add_contour(self):
        """Додати контурну рамку до конструктора"""
        contour = LCARSContour(
            title="CONTOUR",
            color=self.colors.get("purple", "#CC99FF"),
            width=300,
            height=200
        )
        self.constructor.add_component(contour)
        self.statusBar().showMessage("◤ Contour added")
    
    def add_capsule_button(self):
        """Додати капсульну кнопку"""
        button = LCARSButton(
            text="CAPSULE",
            color=self.colors.get("orange_light", "#FFBB66"),
            shape="capsule",
            width=200,
            height=45,
            font_size=12
        )
        self.constructor.add_component(button)
        self.statusBar().showMessage("◤ Capsule button added")
    
    def add_rounded_button(self):
        """Додати закруглену кнопку"""
        button = LCARSButton(
            text="ROUNDED",
            color=self.colors.get("tan", "#CC9966"),
            shape="rounded",
            width=200,
            height=45,
            font_size=12
        )
        self.constructor.add_component(button)
        self.statusBar().showMessage("◤ Rounded button added")
    
    def on_component_selected(self, component):
        """Обробник вибору компоненту"""
        if component is None:
            self.properties_area.setText("Select component to view properties")
            return
        
        # Отримати властивості компоненту
        properties = self.constructor.get_selected_properties()
        
        # Сформувати текст для відображення
        text_lines = [f"◤ {properties.get('type', 'Unknown')}", ""]
        
        for key, value in properties.items():
            if key != "type":
                text_lines.append(f"{key.upper()}: {value}")
        
        self.properties_area.setText("\n".join(text_lines))
    
    def show_about(self):
        """Показати діалог About"""
        QMessageBox.about(
            self,
            "◤ ABOUT LCARS ARCHITECT",
            """<h2>LCARS ARCHITECT v3.0</h2>
            <p><b>Standalone UI Designer for LCARS Interfaces</b></p>
            <p>This is a fully self-contained application for designing
            LCARS (Library Computer Access/Retrieval System) interfaces
            inspired by Star Trek.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Visual component designer</li>
                <li>Multiple era themes (22nd-25th century)</li>
                <li>Faction themes (Federation, Klingon, Romulan, etc.)</li>
                <li>Project save/load</li>
                <li>Python code export</li>
            </ul>
            <p><i>Requires: PyQt6</i></p>
            <p>Version 3.0 - Standalone Edition</p>"""
        )


# =============================================================================
# ТОЧКА ВХОДУ В ПРОГРАМУ
# =============================================================================

def main():
    """
    Головна точка входу в програму LCARS Architect.
    Ініціалізує QApplication та запускає головне вікно.
    """
    print("=" * 60)
    print("◤ LCARS ARCHITECT v3.0 - STANDALONE")
    print("◤ Library Computer Access/Retrieval System")
    print("◤ UI Designer & Interface Constructor")
    print("=" * 60)
    print()
    print("◤ [INIT] Initializing Isolinear Substrate...")
    print("◤ [INIT] Loading LCARS Component Library...")
    print("◤ [INIT] Preparing Constructor Interface...")
    print()
    
    if True:
        # Створити застосунок Qt
        application = QApplication(sys.argv)
        
        # Встановити шрифт за замовчуванням
        available_families = QFontDatabase.families()
        if "Swiss 911 BT" in available_families:
            default_font = QFont("Swiss 911 BT", 10)
        else:
            # Використати резервний шрифт якщо Swiss 911 BT недоступний
            default_font = QFont("Arial Black", 10)
        
        application.setFont(default_font)
        
        print("◤ [LAUNCH] Creating Architect Window...")
        
        # Створити та показати головне вікно
        window = LCARSDesignerWindow()
        window.show()
        
        print("◤ [LAUNCH] System online. Ready for input.")
        print()
        
        # Запустити головний цикл подій
        return application.exec()
        
    if False: # Removed except block
        print()
        print("=" * 60)
        print("◤ [CRITICAL] System crash detected!")
        print("=" * 60)
        print(f"Error: {error}")
        print()
        traceback.print_exc()
        print()
        input("Press Enter to exit...")
        return 1


if __name__ == "__main__":
    # Вихід з кодом повернення з головної функції
    sys.exit(main())
