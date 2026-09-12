import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QCursor

class SimpleElement:
    def __init__(self, widget, element_type):
        self.widget = widget
        self.type = element_type
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.drag_start = QPoint()
        self.resize_start = QPoint()
        self.original_size = None

class SimpleConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIMPLE LCARS CONSTRUCTOR")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: black; color: white;")
        
        # Canvas
        self.canvas = QFrame()
        self.canvas.setStyleSheet("background-color: #111; border: 2px solid #333;")
        self.setCentralWidget(self.canvas)
        
        # Elements
        self.elements = []
        self.selected_element = None
        
        # Toolbar
        self.setup_toolbar()
        
        # Event handling
        self.canvas.mousePressEvent = self.mouse_press
        self.canvas.mouseMoveEvent = self.mouse_move
        self.canvas.mouseReleaseEvent = self.mouse_release
        
        print("✅ Простий конструктор готовий!")
    
    def setup_toolbar(self):
        toolbar = QWidget(self)
        toolbar.setGeometry(10, 10, 200, 780)
        toolbar.setStyleSheet("background-color: #222;")
        
        layout = QVBoxLayout(toolbar)
        
        # Add elements
        btn_rect = QPushButton("ПРЯМОКУТНИК")
        btn_rect.clicked.connect(lambda: self.add_element("rect"))
        btn_rect.setStyleSheet("background-color: #ff9900; color: black; padding: 10px;")
        layout.addWidget(btn_rect)
        
        btn_circle = QPushButton("КОЛО")
        btn_circle.clicked.connect(lambda: self.add_element("circle"))
        btn_circle.setStyleSheet("background-color: #0099ff; color: white; padding: 10px;")
        layout.addWidget(btn_circle)
        
        btn_text = QPushButton("ТЕКСТ")
        btn_text.clicked.connect(lambda: self.add_element("text"))
        btn_text.setStyleSheet("background-color: #00ff00; color: black; padding: 10px;")
        layout.addWidget(btn_text)
        
        # Delete button
        btn_delete = QPushButton("ВИДАЛИТИ")
        btn_delete.clicked.connect(self.delete_selected)
        btn_delete.setStyleSheet("background-color: #ff0000; color: white; padding: 10px; margin-top: 20px;")
        layout.addWidget(btn_delete)
    
    def add_element(self, element_type):
        if element_type == "rect":
            widget = QPushButton("", self.canvas)
            widget.setGeometry(300, 200, 150, 80)
            widget.setStyleSheet("background-color: #ff9900; border: 2px solid #ffcc00;")
        elif element_type == "circle":
            widget = QPushButton("", self.canvas)
            widget.setGeometry(300, 200, 80, 80)
            widget.setStyleSheet("background-color: #0099ff; border: 2px solid #00ccff; border-radius: 40px;")
        else:  # text
            widget = QPushButton("TEXT", self.canvas)
            widget.setGeometry(300, 200, 120, 40)
            widget.setStyleSheet("background-color: #00ff00; color: black; border: 2px solid #00cc00;")
        
        widget.show()
        
        element = SimpleElement(widget, element_type)
        self.elements.append(element)
        
        print(f"✅ Додано {element_type}")
    
    def delete_selected(self):
        if self.selected_element:
            self.selected_element.widget.deleteLater()
            self.elements.remove(self.selected_element)
            self.selected_element = None
            print("✅ Елемент видалено")
    
    def mouse_press(self, event):
        pos = event.position().toPoint()
        
        # Check elements (reverse order for top-most)
        for element in reversed(self.elements):
            if element.widget.geometry().contains(pos):
                self.select_element(element)
                
                if event.button() == Qt.MouseButton.LeftButton:
                    # Check for resize (corners)
                    rect = element.widget.geometry()
                    if abs(pos.x() - rect.right()) < 10 and abs(pos.y() - rect.bottom()) < 10:
                        element.resizing = True
                        element.resize_start = pos
                        element.original_size = rect.size()
                        self.canvas.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                    else:
                        element.dragging = True
                        element.drag_start = pos - rect.topLeft()
                        self.canvas.setCursor(QCursor(Qt.CursorShape.SizeAllCursor))
                return
        
        # Click on empty space
        self.deselect_all()
    
    def mouse_move(self, event):
        pos = event.position().toPoint()
        
        # Update cursor
        for element in self.elements:
            rect = element.widget.geometry()
            if abs(pos.x() - rect.right()) < 10 and abs(pos.y() - rect.bottom()) < 10:
                self.canvas.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
                return
        
        self.canvas.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        
        # Handle dragging/resizing
        for element in self.elements:
            if element.dragging:
                new_pos = pos - element.drag_start
                element.widget.move(new_pos)
                return
            elif element.resizing:
                rect = element.widget.geometry()
                new_size = element.original_size + (pos - element.resize_start)
                if new_size.width() > 20 and new_size.height() > 20:
                    element.widget.resize(new_size)
                return
    
    def mouse_release(self, event):
        for element in self.elements:
            element.dragging = False
            element.resizing = False
        self.canvas.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def select_element(self, element):
        self.deselect_all()
        element.selected = True
        self.selected_element = element
        element.widget.setStyleSheet(element.widget.styleSheet() + "; border: 3px solid #00ff00;")
    
    def deselect_all(self):
        for element in self.elements:
            if element.selected:
                element.selected = False
                # Remove green border
                style = element.widget.styleSheet()
                style = style.replace("; border: 3px solid #00ff00;", "")
                element.widget.setStyleSheet(style)
        self.selected_element = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleConstructor()
    window.show()
    sys.exit(app.exec())
