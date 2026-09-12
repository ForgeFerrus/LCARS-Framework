"""
ПРОСТИЙ РОБОЧИЙ LCARS КОНСТРУКТОР
"""

# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, 
                            QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QDrag, QPixmap
# Titanium Bridge Migration: import json

class SimpleDragButton(QPushButton):
    """Проста кнопка для drag & drop"""
    
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
            
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            
            drag.exec()

class ConstructorCanvas(QFrame):
    """Полотно для віджетів"""
    
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
        btn.move(pos - QPoint(50, 20))  # Центрувати
        btn.show()
        
        self.buttons.append(btn)
        print(f"Додано кнопку: {text} на позиції {pos}")

class SimpleConstructor(QMainWindow):
    """Простий конструктор"""
    
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
        
        left_layout.addWidget(QLabel("Елементи:"))
        
        # Елементи для перетягування
        elements = ["Кнопка", "Панель", "Дисплей", "Консоль"]
        for elem in elements:
            btn = SimpleDragButton(elem)
            left_layout.addWidget(btn)
        
        # Кнопки управління
        clear = QPushButton("Очистити")
        clear.clicked.connect(self.clear_canvas)
        left_layout.addWidget(clear)
        
        save = QPushButton("Зберегти")
        save.clicked.connect(self.save)
        left_layout.addWidget(save)
        
        left_layout.addStretch()
        layout.addWidget(left)
        
        # Права панель - полотно
        self.canvas = ConstructorCanvas()
        layout.addWidget(self.canvas)
    
    def clear_canvas(self):
        for btn in self.canvas.buttons:
            btn.deleteLater()
        self.canvas.buttons.clear()
        print("Полотно очищено")
    
    def save(self):
        data = []
        for btn in self.canvas.buttons:
            data.append({
                'text': btn.text(),
                'x': btn.x(),
                'y': btn.y()
            })
        
        filename, _ = QFileDialog.getSaveFileName(self, "Зберегти", "", "JSON (*.json)")
        if filename:
            with open(filename, 'w') as f:
                json.dump(data, f)
            print(f"Збережено {len(data)} елементів")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SimpleConstructor()
    w.show()
    
    print("Конструктор запущено!")
    print("Перетягуйте елементи на полотно")
    
    sys.exit(app.exec())
