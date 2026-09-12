"""
LCARS Constructor - Все в одному файлі
"""

# Titanium Bridge Migration: import json
import random
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QPolygonF

# Базовий клас для всіх LCARS-елементів
class LcarsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = "#FF9900"
        self.setFixedSize(100, 40)

    def setColor(self, color):
        self.color = color
        self.update()

# Геометричні примітиви
class Rect(LcarsWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRect(0, 0, self.width(), self.height())

class Square(Rect):
    def __init__(self, size=40, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

class Circle(LcarsWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(0, 0, self.width(), self.height())

class Triangle(LcarsWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        points = [QPoint(0, self.height()), QPoint(self.width()/2, 0), QPoint(self.width(), self.height())]
        p.drawPolygon(QPolygonF(points))

class Line(LcarsWidget):
    def __init__(self, orientation="h", parent=None):
        super().__init__(parent)
        self.orientation = orientation

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(QColor(self.color), 4))
        if self.orientation == "h":
            p.drawLine(0, self.height()//2, self.width(), self.height()//2)
        else:
            p.drawLine(self.width()//2, 0, self.width()//2, self.height())

class LCARSButton(QPushButton):
    def __init__(self, text="BUTTON", parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF9900; color: black;
                border-radius: 15px; font-weight: bold; font-family: 'Arial';
            }
            QPushButton:hover { background-color: white; }
        """)

# EditMode для drag & drop
class EditMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.enabled = True
        self.elements = []
        self.selected_element = None
        self.drag_start = None
        
        # Встановлюємо event filter на canvas
        self.canvas.mousePressEvent = self.mousePressEvent
        self.canvas.mouseMoveEvent = self.mouseMoveEvent
        self.canvas.mouseReleaseEvent = self.mouseReleaseEvent
    
    def set_elements(self, elements):
        self.elements = elements
    
    def add_element(self, element_data):
        self.elements.append(element_data)
    
    def mousePressEvent(self, event):
        if self.enabled and event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # Шукаємо елемент під курсором
            for element in reversed(self.elements):
                widget = element['widget']
                if widget.geometry().contains(pos):
                    self.selected_element = element
                    self.drag_start = pos - widget.pos()
                    widget.raise_()
                    break
    
    def mouseMoveEvent(self, event):
        if self.selected_element and self.drag_start:
            pos = event.position().toPoint()
            new_pos = pos - self.drag_start
            self.selected_element['widget'].move(new_pos)
            self.selected_element['geom'] = [new_pos.x(), new_pos.y(), 
                                            self.selected_element['geom'][2], 
                                            self.selected_element['geom'][3]]
    
    def mouseReleaseEvent(self, event):
        self.selected_element = None
        self.drag_start = None

# Палітра кольорів
def get_palette_by_name(name):
    """Проста палітра для всіх ер"""
    return {
        'button_colors': [
            '#FFCC66', '#FF9900', '#9999FF', '#B1957A',
            '#EEC222', '#3399FF', '#CD6363', '#646DCC',
            '#99CCFF', '#FFFF9C'
        ]
    }

# Фабрика компонентів
def get_universal_primitives():
    """Повертає повний набір для тулбару"""
    return {
        'Прямокутник': lambda parent=None: Rect(parent=parent),
        'Квадрат': lambda parent=None: Square(parent=parent),
        'Коло': lambda parent=None: Circle(parent=parent),
        'Трикутник': lambda parent=None: Triangle(parent=parent),
        'Гориз. Лінія': lambda parent=None: Line(orientation="h", parent=parent),
        'Верт. Лінія': lambda parent=None: Line(orientation="v", parent=parent),
        'Кнопка': lambda parent=None: LCARSButton("DATA", parent=parent),
        'Панель': lambda parent=None: Rect(parent=parent),
        'Текст': lambda parent=None: LCARSButton("TEXT", parent=parent),
        'Міні-Кнопка': lambda parent=None: LCARSButton("MINI", parent=parent),
        'Індикатор': lambda parent=None: LCARSButton("STATUS", parent=parent),
        'Дисплей': lambda parent=None: LCARSButton("DISPLAY", parent=parent)
    }

# Головний конструктор
class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()  
        self.setWindowTitle("LCARS FRAMEWORK - CONSTRUCTOR")
        self.setFixedSize(1300, 900)
        self.setStyleSheet("background-color: black; color: white;")

        # Завантаження палітри та примітивів
        self.faction = "24th"
        self.palette = get_palette_by_name(self.faction)
        
        # Об'єднуємо всі фабрики в один реєстр
        self.component_palette = get_universal_primitives()
        
        print(f"Завантажено компонентів: {len(self.component_palette)}")
        print(f"Список компонентів: {list(self.component_palette.keys())}")

        # Основний інтерфейс
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Область для малювання (Canvas)
        self.canvas = QFrame(self.central_widget)
        self.canvas.setGeometry(180, 60, 1100, 820)
        self.canvas.setStyleSheet("border: 1px dashed #333; background-color: #050505;")

        # Ініціалізація EditMode
        self.elements = []
        self.edit_mode = EditMode(self.canvas)
        self.edit_mode.set_elements(self.elements)

        # Створення панелей керування
        self.setup_ui_panels()

        # Системний таймер
        self.logic_timer = QTimer()
        self.logic_timer.timeout.connect(self.execute_logic)
        self.logic_timer.start(500)

    def setup_ui_panels(self):
        # Верхня панель (Керування режимами)
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setGeometry(0, 0, 1300, 50)
        layout = QHBoxLayout(self.top_bar)
        
        self.mode_btn = QPushButton("MODE: DESIGN")
        self.mode_btn.setFixedSize(200, 35)
        self.mode_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold; border-radius: 5px;")
        self.mode_btn.clicked.connect(self.toggle_mode)
        
        save_btn = QPushButton("SAVE JSON")
        save_btn.clicked.connect(self.save_layout)
        
        layout.addWidget(self.mode_btn)
        layout.addStretch()
        layout.addWidget(save_btn)

        # Ліва панель (Toolbar)
        self.setup_sidebar()

    def setup_sidebar(self):
        scroll = QScrollArea(self.central_widget)
        scroll.setGeometry(10, 60, 160, 820)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        title = QLabel("COMPONENTS")
        title.setStyleSheet("color: #ff9900; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Динамічно створюємо кнопки для кожного примітива
        for name in self.component_palette.keys():
            btn = QPushButton(name.upper())
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #222; color: #99ccff; 
                    border-left: 4px solid #99ccff; padding: 8px; margin-bottom: 2px;
                }
                QPushButton:hover { background-color: #333; color: white; }
            """)
            btn.clicked.connect(lambda ch=False, n=name: self.spawn_primitive(n))
            layout.addWidget(btn)
        
        layout.addStretch()
        scroll.setWidget(container)

    def spawn_primitive(self, type_name):
        """Створює об'єкт на основі палітри примітивів"""
        if type_name in self.component_palette:
            # Створюємо віджет через лямбду
            widget = self.component_palette[type_name](parent=self.canvas)
            
            # Випадковий колір з палітри
            color = random.choice(self.palette['button_colors'])
            
            # Налаштування вигляду
            if hasattr(widget, 'setColor'):
                widget.setColor(color)
            else:
                widget.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            
            # Рандомна позиція щоб не накладалися
            x = random.randint(50, 600)
            y = random.randint(50, 400)
            geom = [x, y, 150, 60]
            widget.setGeometry(*geom)
            widget.show()
            
            # Реєстрація в системі
            element_data = {
                'type': type_name,
                'widget': widget,
                'geom': geom,
                'color': color,
                'logic': "",
                'text': "DATA"
            }
            self.elements.append(element_data)
            self.edit_mode.add_element(element_data)
            
            print(f"Створено {type_name} на позиції ({x}, {y})")

    def toggle_mode(self):
        self.edit_mode.enabled = not self.edit_mode.enabled
        state = "DESIGN" if self.edit_mode.enabled else "RUNTIME"
        color = "#00ff00" if self.edit_mode.enabled else "#ff9900"
        self.mode_btn.setText(f"MODE: {state}")
        self.mode_btn.setStyleSheet(f"background-color: {color}; color: black; font-weight: bold; border-radius: 5px;")
        print(f"Режим змінено на: {state}")

    def save_layout(self):
        """Зберегти розмітку в JSON"""
        layout_data = []
        for element in self.elements:
            layout_data.append({
                'type': element['type'],
                'position': [element['geom'][0], element['geom'][1]],
                'size': [element['geom'][2], element['geom'][3]],
                'color': element['color']
            })
        
        filename = f"layout_{len(self.elements)}_elements.json"
        with open(filename, 'w') as f:
            json.dump(layout_data, f, indent=2)
        print(f"Розмітку збережено в {filename}")

    def execute_logic(self):
        """Оживляє примітиви"""
        if self.edit_mode.enabled:
            return # У режимі DESIGN алгоритми стоять на паузі
        
        # Тут можна додати логіку для RUNTIME режиму
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    
    print('🎨 LCARS Constructor запущено!')
    print('🔧 Натискайте на компоненти для створення')
    print('🖱️ Перетягуйте елементи в режимі DESIGN')
    
    sys.exit(app.exec())
