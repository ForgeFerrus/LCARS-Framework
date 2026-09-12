"""
Простий LCARS Constructor з drag & drop
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QDrag

class DraggableButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(100, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #000000;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #FF6B6B;
            }
        """)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.text())
            drag.setMimeData(mime)
            drag.exec()

class CanvasWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: #000000; border: 2px solid #FF6B6B;")
        self.buttons = []
    
    def dragEnterEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        text = event.mimeData().text()
        
        btn = QPushButton(text, self)
        btn.setFixedSize(100, 40)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #269EEE;
                color: #000000;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #000000;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #269EEE;
            }
        """)
        
        pos = event.position().toPoint()
        btn.move(pos - QPoint(50, 20))
        btn.show()
        
        self.buttons.append(btn)
        print(f"Додано кнопку: {text} на позиції {pos}")

class SimpleConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Constructor")
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("background-color: #000000; color: #FF6B6B;")
        
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QHBoxLayout(central)
        
        # Ліва панель
        left = QFrame()
        left.setFixedWidth(200)
        left.setStyleSheet("background-color: #111111; border: 2px solid #FF6B6B;")
        left_layout = QVBoxLayout(left)
        
        left_layout.addWidget(QLabel("ЕЛЕМЕНТИ:"))
        
        elements = ["Кнопка", "Панель", "Дисплей", "Консоль"]
        for elem in elements:
            btn = DraggableWidget(elem)
            left_layout.addWidget(btn)
        
        clear_btn = QPushButton("ОЧИСТИТИ")
        clear_btn.clicked.connect(self.clear_canvas)
        left_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("ЗБЕРЕГТИ")
        save_btn.clicked.connect(self.save_layout)
        left_layout.addWidget(save_btn)
        
        left_layout.addStretch()
        layout.addWidget(left)
        
        # Права панель - полотно
        self.canvas = CanvasWidget()
        layout.addWidget(self.canvas)
    
    def clear_canvas(self):
        for btn in self.canvas.buttons:
            btn.deleteLater()
        self.canvas.buttons.clear()
        print("Полотно очищено")
    
    def save_layout(self):
        data = []
        for btn in self.canvas.buttons:
            data.append({
                'text': btn.text(),
                'x': btn.x(),
                'y': btn.y()
            })
        
        filename = f"layout_{len(data)}_elements.json"
        with open(filename, 'w') as f:
            json.dump(data, f)
        print(f"Збережено {len(data)} елементів")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleConstructor()
    window.show()
    
    print('🎨 Простий LCARS конструктор запущено!')
    print('🔧 Перетягуйте елементи на полотно')
    
    sys.exit(app.exec())
