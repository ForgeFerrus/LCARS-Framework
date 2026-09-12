"""
PCARS 22nd Century Constructor - Full Featured Version
Відновлений конструктор з повним функціоналом для LCARS Framework
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QToolBar, QDockWidget, 
                            QListWidget, QListWidgetItem, QLabel, QMenuBar, QMenu)
from PyQt6.QtGui import QAction, QFont, QPainter, QColor, QPen, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QTimer

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from lcars.core.edit_mode import EditMode
from lcars.themes.eras.primitives import Rect, Square, Circle, Triangle, Line, LCARSButton, TextLabel
from lcars.themes.eras.PCARSPanel import PCARS22Panel
from lcars.themes.eras.pcars22_components import PCARS22Button, PCARS22MiniButton
from lcars.themes.lcars_palette import get_palette_by_name


class Indicator22(QLabel):
    """PCARS 22nd Century indicator"""
    
    def __init__(self, color="#FF6600", text="INDICATOR", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {self.color};
                color: #000;
                padding: 8px;
                font-weight: bold;
                border: 2px solid #000;
                font-size: 14px;
            }}
        """)


class VerticalScale22(QWidget):
    """Вертикальна шкала для 22nd Century"""
    
    def __init__(self, label="SCALE", color="#FF6600", parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.setFixedSize(60, 200)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor("#111"))
        
        # Шкала
        painter.setPen(QPen(QColor(self.color), 2))
        painter.drawRect(10, 20, 40, 160)
        
        # Поділки
        for i in range(5):
            y = 20 + i * 40
            painter.drawLine(10, y, 50, y)
            
        # Назва
        painter.setPen(QColor(self.color))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.label)


class Radar22(QWidget):
    """Radar display для 22nd Century"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_radar)
        self.timer.start(100)
        
    def update_radar(self):
        self.angle = (self.angle + 6) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor("#001100"))
        
        # Кола радара
        painter.setPen(QPen(QColor("#00FF00"), 1))
        center = self.width() // 2
        for radius in [40, 80, 120]:
            painter.drawEllipse(center - radius//2, center - radius//2, radius, radius)
            
        # Лінії
        painter.drawLine(center, 20, center, 180)
        painter.drawLine(20, center, 180, center)
        
        # Сканована лінія
        painter.setPen(QPen(QColor("#00FF00"), 2))
        # Titanium Bridge Migration: import math
        x = center + 80 * math.cos(math.radians(self.angle))
        y = center + 80 * math.sin(math.radians(self.angle))
        painter.drawLine(center, center, int(x), int(y))


class LogBlock22(QWidget):
    """Log block для 22nd Century"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 100)
        self.logs = ["SYSTEM READY", "LCARS ONLINE", "NX-01 STANDBY"]
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor("#111"))
        
        # Рамка
        painter.setPen(QPen(QColor("#FF6600"), 2))
        painter.drawRect(0, 0, self.width(), self.height())
        
        # Текст логів
        painter.setPen(QColor("#FF6600"))
        painter.setFont(QFont("Courier", 10))
        y = 20
        for log in self.logs[-3:]:
            painter.drawText(10, y, log)
            y += 25


class PCARSConstructor(QMainWindow):
    """Повнофункціональний конструктор PCARS 22nd Century"""
    
    def __init__(self, faction="22nd"):
        super().__init__()
        self.faction = faction
        self.setWindowTitle(f"LCARS Framework Constructor - {faction.upper()} Century")
        self.setGeometry(100, 100, 1400, 900)
        
        # Налаштування кольорів
        self.colors = get_palette_by_name(faction)
        
        # Центральний віджет для роботи
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Основний layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Створюємо toolbar
        self.create_toolbar()
        
        # Створюємо робочу область
        self.create_work_area()
        
        # Створюємо EditMode
        self.edit_mode = EditMode(self.work_area)
        
        # Налаштовуємо component palette для EditMode
        self.setup_component_palette()
        
        # Створюємо UI для EditMode
        self.edit_mode.create_edit_ui()
        
        # Стиль головного вікна
        self.setup_faction_style()
        
        # Створюємо меню
        self.create_menus()
        
        # Додаємо демонстраційні елементи
        QTimer.singleShot(1000, self.add_demo_elements)
    
    def create_toolbar(self):
        """Створює панель інструментів"""
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet(f"""
            QToolBar {{
                background: {self.colors.get('panel_color', '#222')};
                border: 2px solid {self.colors.get('accent1', '#FF6600')};
                spacing: 5px;
                padding: 5px;
            }}
            QPushButton {{
                background: {self.colors.get('accent1', '#FF6600')};
                color: #000;
                border: 1px solid #000;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background: {self.colors.get('accent2', '#01B9E6')};
            }}
            QPushButton:checked {{
                background: {self.colors.get('accent3', '#0798C9')};
            }}
        """)
        self.main_layout.addWidget(self.toolbar)
        
        # Кнопка режиму редагування
        self.edit_btn = QPushButton("EDIT MODE")
        self.edit_btn.setCheckable(True)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.toolbar.addWidget(self.edit_btn)
        
        # Розділювач
        self.toolbar.addSeparator()
        
        # Кнопки компонентів
        self.component_buttons = {}
        components = [
            ("PANEL", "panel"),
            ("BUTTON", "button"), 
            ("MINI", "mini"),
            ("TEXT", "text"),
            ("RECT", "rect"),
            ("CIRCLE", "circle"),
            ("LINE H", "line_h"),
            ("LINE V", "line_v")
        ]
        
        for label, comp_type in components:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, t=comp_type: self.add_component(t))
            self.toolbar.addWidget(btn)
            self.component_buttons[comp_type] = btn
        
        # Розділювач
        self.toolbar.addSeparator()
        
        # Декоративні елементи
        self.toolbar.addWidget(Indicator22(color=self.colors.get('accent1', '#FF6600'), text="LCARS"))
        self.toolbar.addWidget(VerticalScale22("POWER", color=self.colors.get('accent2', '#01B9E6')))
    
    def create_work_area(self):
        """Створює робочу область"""
        work_container = QWidget()
        work_layout = QHBoxLayout(work_container)
        work_layout.setContentsMargins(0, 0, 0, 0)
        
        # Ліва панель з компонентами
        self.left_panel = PCARS22Panel()
        self.left_panel.setFixedWidth(200)
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок панелі
        title = QLabel("COMPONENTS")
        title.setStyleSheet(f"color: {self.colors.get('accent1', '#FF6600')}; font-size: 16px; font-weight: bold;")
        self.left_layout.addWidget(title)
        
        # Список компонентів
        self.component_list = QListWidget()
        self.component_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.colors.get('panel_color', '#111')};
                color: {self.colors.get('accent1', '#FF6600')};
                border: 1px solid {self.colors.get('accent2', '#01B9E6')};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #333;
            }}
            QListWidget::item:selected {{
                background: {self.colors.get('accent2', '#01B9E6')};
                color: #000;
            }}
        """)
        
        components = ["Panel", "Button", "Mini Button", "Text Label", "Rectangle", "Square", "Circle", "Triangle", "Line H", "Line V"]
        for comp in components:
            self.component_list.addItem(comp)
        
        self.component_list.itemDoubleClicked.connect(self.add_component_from_list)
        self.left_layout.addWidget(self.component_list)
        
        # Права робоча область
        self.work_area = QWidget()
        self.work_area.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        
        work_layout.addWidget(self.left_panel)
        work_layout.addWidget(self.work_area, 1)
        
        self.main_layout.addWidget(work_container, 1)
    
    def setup_component_palette(self):
        """Налаштовує палітру компонентів для EditMode"""
        self.edit_mode.component_palette = {
            'panel': lambda parent=None: PCARS22Panel(parent=parent),
            'button': lambda parent=None: PCARS22Button("01-BTN", "BUTTON", color=self.colors.get('accent1', '#FF6600'), parent=parent),
            'mini': lambda parent=None: PCARS22MiniButton("MINI", color_index=0, parent=parent),
            'text': lambda parent=None: TextLabel("TEXT", color=self.colors.get('accent1', '#FF6600'), parent=parent),
            'rect': lambda parent=None: Rect(100, 40, self.colors.get('accent1', '#FF6600'), "#000", 2, parent=parent),
            'square': lambda parent=None: Square(40, self.colors.get('accent2', '#01B9E6'), "#000", 2, parent=parent),
            'circle': lambda parent=None: Circle(40, self.colors.get('accent3', '#0798C9'), "#000", 2, parent=parent),
            'triangle': lambda parent=None: Triangle(50, 50, self.colors.get('accent1', '#FF6600'), "#000", 2, parent=parent),
            'line_h': lambda parent=None: Line(100, 4, self.colors.get('accent2', '#01B9E6'), "h", parent=parent),
            'line_v': lambda parent=None: Line(100, 4, self.colors.get('accent3', '#0798C9'), "v", parent=parent),
        }
    
    def toggle_edit_mode(self):
        """Перемикає режим редагування"""
        self.edit_mode.enabled = self.edit_btn.isChecked()
        if self.edit_mode.enabled:
            self.work_area.setStyleSheet(f"background: {self.colors.get('background', '#000')}; border: 2px solid {self.colors.get('accent1', '#FF6600')};")
        else:
            self.work_area.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.work_area.update()
    
    def add_component(self, comp_type):
        """Додає компонент через toolbar"""
        if not self.edit_mode.enabled:
            self.edit_btn.setChecked(True)
            self.toggle_edit_mode()
        self.edit_mode.add_element(comp_type)
    
    def add_component_from_list(self, item):
        """Додає компонент через список"""
        comp_map = {
            "Panel": "panel",
            "Button": "button", 
            "Mini Button": "mini",
            "Text Label": "text",
            "Rectangle": "rect",
            "Square": "square",
            "Circle": "circle",
            "Triangle": "triangle",
            "Line H": "line_h",
            "Line V": "line_v"
        }
        
        comp_type = comp_map.get(item.text(), "panel")
        self.add_component(comp_type)
    
    def setup_faction_style(self):
        """Налаштовує стиль залежно від фракції"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('background', '#000')};
            }}
            QWidget {{
                background-color: {self.colors.get('background', '#000')};
                color: {self.colors.get('accent1', '#FF6600')};
            }}
        """)
    
    def create_menus(self):
        """Створює меню"""
        menubar = self.menuBar()
        
        # Меню фракцій
        faction_menu = menubar.addMenu('Faction')
        
        factions = ["22nd", "23rd", "24th", "25th"]
        for faction in factions:
            action = QAction(f"{faction.upper()} Century", self)
            action.triggered.connect(lambda checked, f=faction: self.change_faction(f))
            faction_menu.addAction(action)
        
        # Меню компонентів
        comp_menu = menubar.addMenu('Components')
        
        add_panel_action = QAction("Add Panel", self)
        add_panel_action.triggered.connect(lambda: self.add_component("panel"))
        comp_menu.addAction(add_panel_action)
        
        add_button_action = QAction("Add Button", self)
        add_button_action.triggered.connect(lambda: self.add_component("button"))
        comp_menu.addAction(add_button_action)
        
        # Меню допомоги
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def change_faction(self, new_faction):
        """Змінює фракцію"""
        if new_faction != self.faction:
            self.faction = new_faction
            self.colors = get_palette_by_name(new_faction)
            self.setWindowTitle(f"LCARS Framework Constructor - {new_faction.upper()} Century")
            self.setup_faction_style()
            self.setup_component_palette()
            # Оновлюємо існуючі елементи
            self.update_existing_elements()
    
    def update_existing_elements(self):
        """Оновлює існуючі елементи при зміні фракції"""
        for el in self.edit_mode.elements:
            if hasattr(el['widget'], 'setColor'):
                # Оновлюємо кольори для примітивів
                if el['type'] in ['rect', 'square', 'circle', 'triangle']:
                    el['widget'].setColor(self.colors.get('accent1', '#FF6600'))
                elif el['type'] in ['line_h', 'line_v']:
                    el['widget'].color = self.colors.get('accent2', '#01B9E6')
        self.work_area.update()
    
    def show_about(self):
        """Показує інформацію про програму"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About LCARS Constructor", 
                         "LCARS Framework Constructor\nFull Featured Version\n"
                         f"Faction: {self.faction.upper()} Century\n"
                         "Built with PyQt6")
    
    def add_demo_elements(self):
        """Додає демонстраційні елементи"""
        if not self.edit_mode.enabled:
            self.edit_btn.setChecked(True)
            self.toggle_edit_mode()
        
        demo_elements = [
            ('panel', 50, 50, 200, 150),
            ('button', 300, 50, 120, 40),
            ('mini', 450, 50, 80, 30),
            ('text', 50, 250, 200, 30),
            ('rect', 300, 250, 100, 60),
            ('circle', 450, 250, 60, 60),
            ('triangle', 50, 350, 80, 80),
            ('line_h', 200, 380, 200, 4),
            ('line_v', 450, 350, 4, 100),
        ]
        
        for elem_type, x, y, w, h in demo_elements:
            widget = self.edit_mode.component_palette[elem_type](parent=self.work_area)
            element = {
                'type': elem_type,
                'widget': widget,
                'geom': [x, y, w, h]
            }
            self.edit_mode.elements.append(element)
            widget.setGeometry(x, y, w, h)
            widget.show()
        
        print(f"Додано {len(demo_elements)} демонстраційних елементів для фракції {self.faction}")


def main():
    """Головна функція запуску"""
    app = QApplication(sys.argv)
    
    # Створюємо конструктор з вибором фракції
    constructor = PCARSConstructor("22nd")
    constructor.show()
    
    # Запускаємо додаток
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
