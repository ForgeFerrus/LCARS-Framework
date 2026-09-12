"""
Простий і робочий LCARS конструктор
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QFileDialog, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QDrag, QPixmap, QPainter
# Titanium Bridge Migration: import json

class DraggableButton(QPushButton):
    """Кнопка, яку можна перетягувати"""
    
    def __init__(self, text, widget_type, parent=None):
        super().__init__(text, parent)
        self.widget_type = widget_type
        self.setFixedSize(150, 50)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                padding: 10px;
                border-radius: 25px;
                border: 2px solid #000000;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #FF6B6B;
            }
        """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        
        if not hasattr(self, 'drag_start_position'):
            return
        
        if ((event.position().toPoint() - self.drag_start_position).manhattanLength() 
            < QApplication.startDragDistance()):
            return
        
        # Створити drag об'єкт
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"{self.widget_type}:{self.text()}")
        drag.setMimeData(mime_data)
        
        # Створити pixmap для drag
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter)
        painter.end()
        drag.setPixmap(pixmap)
        
        # Виконати drag
        drag.exec()

class CanvasWidget(QFrame):
    """Полотно для розміщення віджетів"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 3px solid #FF6B6B;
                border-radius: 15px;
            }
        """)
        self.widgets = []
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            data = event.mimeData().text().split(":")
            if len(data) >= 2:
                widget_type = data[0]
                text = data[1]
                
                # Створити нову кнопку на полотні
                button = QPushButton(text, self)
                button.setFixedSize(150, 50)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #269EEE;
                        color: #000000;
                        font-weight: bold;
                        padding: 10px;
                        border-radius: 25px;
                        border: 2px solid #000000;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #000000;
                        color: #269EEE;
                    }
                """)
                
                # Розмістити кнопку в позиції drop
                drop_pos = event.position().toPoint()
                button.move(drop_pos)
                button.show()
                
                # Зберегти віджет
                self.widgets.append({
                    'widget': button,
                    'type': widget_type,
                    'text': text,
                    'position': drop_pos
                })
                
                event.acceptProposedAction()
    
    def clear_canvas(self):
        """Очистити полотно"""
        for item in self.widgets:
            item['widget'].deleteLater()
        self.widgets.clear()
    
    def save_layout(self):
        """Зберегти розмітку"""
        layout_data = []
        for item in self.widgets:
            layout_data.append({
                'type': item['type'],
                'text': item['text'],
                'position': [item['position'].x(), item['position'].y()]
            })
        return layout_data
    
    def load_layout(self, layout_data):
        """Завантажити розмітку"""
        self.clear_canvas()
        for item in layout_data:
            button = QPushButton(item['text'], self)
            button.setFixedSize(150, 50)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #269EEE;
                    color: #000000;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 25px;
                    border: 2px solid #000000;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #000000;
                    color: #269EEE;
                }
            """)
            
            pos = QPoint(item['position'][0], item['position'][1])
            button.move(pos)
            button.show()
            
            self.widgets.append({
                'widget': button,
                'type': item['type'],
                'text': item['text'],
                'position': pos
            })

class SimpleLCARSConstructor(QMainWindow):
    """Простий конструктор LCARS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Constructor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Стиль вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QLabel {
                color: #FF6B6B;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                border: 2px solid #000000;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #FF6B6B;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Ліва панель - елементи
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 107, 107, 0.1);
                border: 2px solid #FF6B6B;
                border-radius: 10px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        
        # Заголовок
        title = QLabel("ЕЛЕМЕНТИ LCARS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #FF6B6B;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        left_layout.addWidget(title)
        
        # Елементи для drag & drop
        elements = [
            ("Кнопка", "button"),
            ("Панель", "panel"),
            ("Дисплей", "display"),
            ("Консоль", "console"),
            ("Індикатор", "indicator"),
            ("Сенсор", "sensor")
        ]
        
        for text, widget_type in elements:
            btn = DraggableButton(text, widget_type)
            left_layout.addWidget(btn)
        
        # Кнопки управління
        left_layout.addSpacing(20)
        
        clear_btn = QPushButton("ОЧИСТИТИ ПОЛОТНО")
        clear_btn.clicked.connect(self.clear_canvas)
        left_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("ЗБЕРЕГТИ")
        save_btn.clicked.connect(self.save_layout)
        left_layout.addWidget(save_btn)
        
        load_btn = QPushButton("ЗАВАНТАЖИТИ")
        load_btn.clicked.connect(self.load_layout)
        left_layout.addWidget(load_btn)
        
        export_btn = QPushButton("ЕКСПОРТ В КОД")
        export_btn.clicked.connect(self.export_code)
        left_layout.addWidget(export_btn)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Права панель - полотно
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 107, 107, 0.1);
                border: 2px solid #FF6B6B;
                border-radius: 10px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        
        # Заголовок полотна
        canvas_title = QLabel("ПОЛОТНО КОНСТРУКТОРА")
        canvas_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        canvas_title.setStyleSheet("""
            QLabel {
                color: #FF6B6B;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        right_layout.addWidget(canvas_title)
        
        # Полотно з прокруткою
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.canvas = CanvasWidget()
        self.canvas.setMinimumSize(800, 600)
        scroll_area.setWidget(self.canvas)
        
        right_layout.addWidget(scroll_area)
        main_layout.addWidget(right_panel)
    
    def clear_canvas(self):
        """Очистити полотно"""
        self.canvas.clear_canvas()
        QMessageBox.information(self, "Готово", "Полотно очищено!")
    
    def save_layout(self):
        """Зберегти розмітку"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Зберегти розмітку", "", "JSON Files (*.json)"
        )
        if filename:
            layout_data = self.canvas.save_layout()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Готово", "Розмітку збережено!")
    
    def load_layout(self):
        """Завантажити розмітку"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Завантажити розмітку", "", "JSON Files (*.json)"
        )
        if filename:
            if True:
                with open(filename, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                self.canvas.load_layout(layout_data)
                QMessageBox.information(self, "Готово", "Розмітку завантажено!")
            if False: # Removed except block
                QMessageBox.critical(self, "Помилка", f"Помилка завантаження: {e}")
    
    def export_code(self):
        """Експортувати в код"""
        layout_data = self.canvas.save_layout()
        
        code = '''"""
Згенерований LCARS інтерфейс
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class GeneratedLCARSInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generated LCARS Interface")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QPushButton {
                background-color: #269EEE;
                color: #000000;
                font-weight: bold;
                padding: 10px;
                border-radius: 25px;
                border: 2px solid #000000;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #269EEE;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
'''
        
        for i, item in enumerate(layout_data):
            x, y = item['position']
            code += f'''        # Кнопка {i+1}
        self.btn_{i+1} = QPushButton("{item['text']}", central_widget)
        self.btn_{i+1}.setFixedSize(150, 50)
        self.btn_{i+1}.move({x}, {y})
        self.btn_{i+1}.show()
        
'''
        
        code += '''
def main():
    app = QApplication(sys.argv)
    window = GeneratedLCARSInterface()
    window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
'''
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Експортувати код", "", "Python Files (*.py)"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            QMessageBox.information(self, "Готово", "Код експортовано!")

def main():
    app = QApplication(sys.argv)
    constructor = SimpleLCARSConstructor()
    constructor.show()
    
    print('🎨 Простий LCARS конструктор запущено!')
    print('🔧 Перетягуйте елементи на полотно')
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
