"""
Simple LCARS Editor - повний контроль над елементами
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, QDialog, 
                            QLineEdit, QColorDialog, QMenu)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

# Додаємо шлях
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from lcars.themes.eras.primitives import Rect, Square, Circle, Triangle, Line, TextLabel

class LCARSElement(QWidget):
    """Базовий елемент LCARS"""
    
    def __init__(self, element_type="rect", parent=None):
        super().__init__(parent)
        self.element_type = element_type
        self.color = QColor("#FF9900")  # LCARS orange
        self.text = ""
        self.selected = False
        self.setFixedSize(100, 60)
        
    def set_color(self, color):
        """Змінити колір елемента"""
        self.color = color
        self.update()
        
    def set_text(self, text):
        """Змінити текст елемента"""
        self.text = text
        self.update()
        
    def paintEvent(self, event):
        """Малювання елемента"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Колір залежно від виділення
        if self.selected:
            painter.setPen(QPen(QColor("#FFFFFF"), 2))
        else:
            painter.setPen(QPen(QColor("#666666"), 1))
            
        painter.setBrush(self.color)
        
        # Малювання залежно від типу
        if self.element_type == "rect":
            painter.drawRect(10, 10, 80, 40)
        elif self.element_type == "circle":
            painter.drawEllipse(20, 5, 60, 50)
        elif self.element_type == "triangle":
            points = [QPoint(50, 10), QPoint(20, 50), QPoint(80, 50)]
            painter.drawPolygon(points)
            
        # Малювання тексту
        if self.text:
            painter.setPen(QPen(QColor("#000000"), 1))
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

class SimpleLCARSEditor(QMainWindow):
    """Простий редактор LCARS з повним контролем"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple LCARS Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.elements = []
        self.selected_element = None
        self.drag_offset = QPoint()
        
        self.setup_ui()
        self.add_demo_elements()
        
    def setup_ui(self):
        """Створити інтерфейс"""
        layout = QVBoxLayout(self.central_widget)
        
        # Панель інструментів
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("background: #333333;")
        
        toolbar_layout = QHBoxLayout(toolbar)
        
        # Кнопки додавання елементів
        add_rect = QPushButton("ADD RECT")
        add_rect.clicked.connect(lambda: self.add_element("rect"))
        add_rect.setStyleSheet("background: #FF9900; color: white; padding: 5px;")
        
        add_circle = QPushButton("ADD CIRCLE") 
        add_circle.clicked.connect(lambda: self.add_element("circle"))
        add_circle.setStyleSheet("background: #0099FF; color: white; padding: 5px;")
        
        add_triangle = QPushButton("ADD TRIANGLE")
        add_triangle.clicked.connect(lambda: self.add_element("triangle"))
        add_triangle.setStyleSheet("background: #00AA00; color: white; padding: 5px;")
        
        # Кнопки редагування
        edit_color = QPushButton("COLOR")
        edit_color.clicked.connect(self.edit_element_color)
        edit_color.setStyleSheet("background: #FF6600; color: white; padding: 5px;")
        
        edit_text = QPushButton("TEXT")
        edit_text.clicked.connect(self.edit_element_text)
        edit_text.setStyleSheet("background: #9900FF; color: white; padding: 5px;")
        
        delete_btn = QPushButton("DELETE")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setStyleSheet("background: #CC0000; color: white; padding: 5px;")
        
        # Додати кнопки
        toolbar_layout.addWidget(add_rect)
        toolbar_layout.addWidget(add_circle)
        toolbar_layout.addWidget(add_triangle)
        toolbar_layout.addWidget(edit_color)
        toolbar_layout.addWidget(edit_text)
        toolbar_layout.addWidget(delete_btn)
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar)
        
        # Робоча область
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background: #000000;")
        layout.addWidget(self.canvas)
        
        # Встановлюємо event filter для миші
        self.canvas.installEventFilter(self)
        
    def add_demo_elements(self):
        """Додати демонстраційні елементи"""
        rect = LCARSElement("rect", self.canvas)
        rect.move(100, 100)
        rect.set_text("RECT1")
        self.elements.append(rect)
        
        circle = LCARSElement("circle", self.canvas)
        circle.move(250, 100)
        circle.set_color(QColor("#0099FF"))
        circle.set_text("CIRCLE1")
        self.elements.append(circle)
        
        triangle = LCARSElement("triangle", self.canvas)
        triangle.move(400, 100)
        triangle.set_color(QColor("#00AA00"))
        triangle.set_text("TRIANGLE1")
        self.elements.append(triangle)
        
    def add_element(self, element_type):
        """Додати новий елемент"""
        element = LCARSElement(element_type, self.canvas)
        element.move(50, 200)
        element.set_text(f"{element_type.upper()}{len(self.elements)+1}")
        self.elements.append(element)
        self.canvas.update()
        
    def edit_element_color(self):
        """Редагувати колір виділеного елемента"""
        if self.selected_element:
            color = QColorDialog.getColor(self.selected_element.color, self)
            if color.isValid():
                self.selected_element.set_color(color)
                self.canvas.update()
                
    def edit_element_text(self):
        """Редагувати текст виділеного елемента"""
        if self.selected_element:
            from PyQt6.QtWidgets import QInputDialog
            text, ok = QInputDialog.getText(self, "Edit Text", "Enter text:", text=self.selected_element.text)
            if ok:
                self.selected_element.set_text(text)
                self.canvas.update()
                
    def delete_selected(self):
        """Видалити виділений елемент"""
        if self.selected_element:
            self.elements.remove(self.selected_element)
            self.selected_element.deleteLater()
            self.selected_element = None
            self.canvas.update()
            
    def eventFilter(self, obj, event):
        """Обробка подій миші"""
        if obj != self.canvas:
            return False
            
        if event.type() == event.Type.MouseButtonPress:
            return self.mouse_press(event)
        elif event.type() == event.Type.MouseMove:
            return self.mouse_move(event)
        elif event.type() == event.Type.MouseButtonRelease:
            return self.mouse_release(event)
        elif event.type() == event.Type.ContextMenu:
            return self.context_menu(event)
            
        return False
        
    def mouse_press(self, event):
        """Натискання миші"""
        pos = event.pos()
        
        # Перевіряємо клік на елемент
        for element in reversed(self.elements):  # Зверху вниз
            if element.geometry().contains(pos):
                self.select_element(element)
                self.drag_offset = pos - element.pos()
                return True
                
        # Клік на порожньому місці - зняти виділення
        self.select_element(None)
        return True
        
    def mouse_move(self, event):
        """Рух миші"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.selected_element:
            new_pos = event.pos() - self.drag_offset
            self.selected_element.move(new_pos)
            self.canvas.update()
            
    def mouse_release(self, event):
        """Відпускання миші"""
        return True
        
    def context_menu(self, event):
        """Контекстне меню"""
        pos = event.pos()
        
        for element in reversed(self.elements):
            if element.geometry().contains(pos):
                self.select_element(element)
                
                menu = QMenu(self)
                menu.setStyleSheet("""
                    QMenu {
                        background: #333333;
                        color: white;
                        border: 1px solid #666666;
                    }
                    QMenu::item {
                        padding: 5px 20px;
                    }
                    QMenu::item:selected {
                        background: #FF9900;
                    }
                """)
                
                color_action = menu.addAction("Change Color")
                color_action.triggered.connect(self.edit_element_color)
                
                text_action = menu.addAction("Change Text")
                text_action.triggered.connect(self.edit_element_text)
                
                delete_action = menu.addAction("Delete")
                delete_action.triggered.connect(self.delete_selected)
                
                menu.exec(event.globalPos())
                return True
                
        return True
        
    def select_element(self, element):
        """Виділити елемент"""
        # Зняти попереднє виділення
        if self.selected_element:
            self.selected_element.selected = False
            
        # Встановити нове виділення
        self.selected_element = element
        if element:
            element.selected = True
            
        self.canvas.update()

def main():
    app = QApplication(sys.argv)
    editor = SimpleLCARSEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
