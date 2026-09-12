"""
ПРОСТИЙ РОБОЧИЙ КОНСТРУКТОР - БЕЗ ХЕРНІ
"""
# Titanium Bridge Migration: import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor

# Імпорт ваших компонентів
if True:
    from lcars_palette import get_palette_by_name
    from primitives import get_universal_primitives
    from pcars23_components import get_23rd_components
if False: # Removed except block
    # Fallback
    def get_palette_by_name(name): 
        return {'button_colors': ['#ff9900', '#0099ff', '#00ff00', '#ff0000']}
    def get_universal_primitives(): 
        return {'rect': lambda parent: QPushButton(parent)}
    def get_23rd_components(): 
        return {}

class WorkingConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS CONSTRUCTOR - РОБОЧИЙ ВАРІАНТ")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("background-color: black; color: white;")
        
        # Палітра
        self.palette = get_palette_by_name("24th")
        self.components = {**get_universal_primitives(), **get_23rd_components()}
        
        # Canvas
        self.canvas = QFrame()
        self.canvas.setStyleSheet("background-color: #0a0a0a; border: 2px solid #333;")
        self.setCentralWidget(self.canvas)
        
        # Елементи
        self.elements = []
        self.selected = None
        
        # UI
        self.setup_ui()
        
        # Events
        self.canvas.mousePressEvent = self.mouse_press
        self.canvas.mouseMoveEvent = self.mouse_move
        self.canvas.mouseReleaseEvent = self.mouse_release
        
        print(f"✅ ГОТОВО! Компонентів: {len(self.components)}")
    
    def setup_ui(self):
        # Ліва панель - компоненти
        left_panel = QWidget(self.canvas)
        left_panel.setGeometry(10, 10, 180, 880)
        left_panel.setStyleSheet("background-color: #1a1a1a; border: 1px solid #444;")
        
        left_layout = QVBoxLayout(left_panel)
        
        title = QLabel("КОМПОНЕНТИ")
        title.setStyleSheet("color: #ff9900; font-size: 16px; font-weight: bold; padding: 10px;")
        left_layout.addWidget(title)
        
        for name in self.components.keys():
            btn = QPushButton(name.upper())
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #222; color: #99ccff; 
                    border-left: 4px solid #99ccff; padding: 8px; margin: 2px;
                    text-align: left;
                }}
                QPushButton:hover {{ background-color: #333; }}
            """)
            btn.clicked.connect(lambda checked=False, n=name: self.add_element(n))
            left_layout.addWidget(btn)
        
        # Права панель - властивості
        right_panel = QWidget(self.canvas)
        right_panel.setGeometry(1300, 10, 90, 880)
        right_panel.setStyleSheet("background-color: #1a1a1a; border: 1px solid #444;")
        
        right_layout = QVBoxLayout(right_panel)
        
        props_title = QLabel("ВЛАСТИВОСТІ")
        props_title.setStyleSheet("color: #ff9900; font-size: 14px; font-weight: bold; padding: 10px;")
        right_layout.addWidget(props_title)
        
        # Кнопки дій
        delete_btn = QPushButton("ВИДАЛИТИ")
        delete_btn.setStyleSheet("background-color: #ff0000; color: white; padding: 8px; margin: 2px;")
        delete_btn.clicked.connect(self.delete_selected)
        right_layout.addWidget(delete_btn)
        
        clear_btn = QPushButton("ОЧИСТИТИ")
        clear_btn.setStyleSheet("background-color: #ff6600; color: white; padding: 8px; margin: 2px;")
        clear_btn.clicked.connect(self.clear_all)
        right_layout.addWidget(clear_btn)
        
        # Інфо
        self.info_label = QLabel("Елемент: 0")
        self.info_label.setStyleSheet("color: #99ccff; font-size: 12px; padding: 10px;")
        right_layout.addWidget(self.info_label)
    
    def add_element(self, element_type):
        if True:
            # Створюємо компонент
            widget = self.components[element_type](self.canvas)
            
            # Випадковий колір
            color = random.choice(self.palette['button_colors'])
            
            # Стиль
            if hasattr(widget, 'setColor'):
                widget.setColor(color)
            else:
                widget.setStyleSheet(f"background-color: {color}; border: 1px solid #666;")
            
            # Розмір і позиція
            widget.setGeometry(250 + random.randint(0, 200), 100 + random.randint(0, 200), 120, 60)
            widget.show()
            
            # Додаємо до списку
            element = {
                'widget': widget,
                'type': element_type,
                'color': color,
                'selected': False
            }
            self.elements.append(element)
            
            self.update_info()
            print(f"✅ Додано: {element_type}")
            
        if False: # Removed except block
            print(f"❌ Помилка: {e}")
    
    def delete_selected(self):
        if self.selected:
            self.selected['widget'].deleteLater()
            self.elements.remove(self.selected)
            self.selected = None
            self.update_info()
            print("✅ Видалено")
    
    def clear_all(self):
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.selected = None
        self.update_info()
        print("🧹 Очищено")
    
    def update_info(self):
        self.info_label.setText(f"Елементів: {len(self.elements)}")
    
    def mouse_press(self, event):
        pos = event.position().toPoint()
        
        # Шукаємо елемент
        for element in reversed(self.elements):
            rect = element['widget'].geometry()
            if rect.contains(pos):
                self.select_element(element)
                
                if event.button() == Qt.MouseButton.LeftButton:
                    # Перевіряємо чи клік на кут для ресайзу
                    if abs(pos.x() - rect.right()) < 10 and abs(pos.y() - rect.bottom()) < 10:
                        element['resizing'] = True
                        element['resize_start'] = pos
                        element['original_size'] = rect.size()
                        self.canvas.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                    else:
                        element['dragging'] = True
                        element['drag_start'] = pos - rect.topLeft()
                        self.canvas.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                return
        
        # Клік на пусто
        self.deselect_all()
    
    def mouse_move(self, event):
        pos = event.position().toPoint()
        
        # Оновлення курсора
        for element in self.elements:
            rect = element['widget'].geometry()
            if abs(pos.x() - rect.right()) < 10 and abs(pos.y() - rect.bottom()) < 10:
                self.canvas.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                break
        else:
            self.canvas.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
        # Перетягування і ресайз
        for element in self.elements:
            if element.get('dragging', False):
                new_pos = pos - element['drag_start']
                element['widget'].move(new_pos)
                return
            elif element.get('resizing', False):
                rect = element['widget'].geometry()
                new_size = element['original_size'] + (pos - element['resize_start'])
                if new_size.width() > 20 and new_size.height() > 20:
                    element['widget'].resize(new_size)
                return
    
    def mouse_release(self, event):
        for element in self.elements:
            element['dragging'] = False
        self.canvas.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def select_element(self, element):
        self.deselect_all()
        element['selected'] = True
        self.selected = element
        
        # Зелена рамка
        style = element['widget'].styleSheet()
        element['widget'].setStyleSheet(style + "; border: 3px solid #00ff00;")
    
    def deselect_all(self):
        for element in self.elements:
            if element['selected']:
                element['selected'] = False
                # Прибираємо зелену рамку
                style = element['widget'].styleSheet()
                style = style.replace("; border: 3px solid #00ff00;", "")
                element['widget'].setStyleSheet(style)
        self.selected = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkingConstructor()
    window.show()
    sys.exit(app.exec())
