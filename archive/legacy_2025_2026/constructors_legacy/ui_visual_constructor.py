"""
LCARS Visual Constructor - Робочий drag & drop редактор
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QComboBox, 
                            QFileDialog, QMessageBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QPoint, QMimeData
from PyQt6.QtGui import QDrag, QPixmap, QPainter
# Titanium Bridge Migration: import json

class DraggableWidget(QPushButton):
    """Віджет, який можна перетягувати"""
    
    def __init__(self, widget_type, text="", parent=None):
        super().__init__(text, parent)
        self.widget_type = widget_type
        self.text = text
        self.setFixedSize(120, 40)
        self.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                padding: 8px;
                border-radius: 20px;
                border: 2px solid #000000;
                font-size: 11px;
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
        mime_data.setText(f"{self.widget_type}:{self.text}")
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
            print("Drag enter accepted")
    
    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        if event.mimeData().hasText():
            data = event.mimeData().text().split(":")
            if len(data) >= 2:
                widget_type = data[0]
                text = data[1]
                
                print(f"Creating widget: {widget_type} - {text}")
                
                # Створити нову кнопку на полотні
                button = QPushButton(text, self)
                button.setFixedSize(120, 40)
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #269EEE;
                        color: #000000;
                        font-weight: bold;
                        padding: 8px;
                        border-radius: 20px;
                        border: 2px solid #000000;
                        font-size: 11px;
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
                
                print(f"Widget created at position: {drop_pos}")
                event.acceptProposedAction()
            else:
                print("Invalid mime data format")
                event.ignore()
        else:
            print("No text in mime data")
            event.ignore()
    
    def clear_canvas(self):
        """Очистити полотно"""
        for item in self.widgets:
            item['widget'].deleteLater()
        self.widgets.clear()
        print("Canvas cleared")
    
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
            button.setFixedSize(120, 40)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #269EEE;
                    color: #000000;
                    font-weight: bold;
                    padding: 8px;
                    border-radius: 20px;
                    border: 2px solid #000000;
                    font-size: 11px;
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
        print(f"Loaded {len(layout_data)} widgets")

class LCARSConstructor(QMainWindow):
    """Головне вікно конструктора"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS Visual Constructor')
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
            QFrame {
                background-color: rgba(255, 107, 107, 0.1);
                border: 2px solid #FF6B6B;
                border-radius: 10px;
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
            ("Сенсор", "sensor"),
            ("Контролер", "controller"),
            ("Модуль", "module")
        ]
        
        for text, widget_type in elements:
            btn = DraggableWidget(widget_type, text)
            left_layout.addWidget(btn)
        
        # Кнопки управління
        left_layout.addSpacing(20)
        
        clear_btn = QPushButton("ОЧИСТИТИ ПОЛОТНО")
        clear_btn.clicked.connect(self.clear_canvas)
        left_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("ЗБЕРЕГТИ РОЗМІТКУ")
        save_btn.clicked.connect(self.save_layout)
        left_layout.addWidget(save_btn)
        
        load_btn = QPushButton("ЗАВАНТАЖИТИ РОЗМІТКУ")
        load_btn.clicked.connect(self.load_layout)
        left_layout.addWidget(load_btn)
        
        export_btn = QPushButton("ЕКСПОРТ В КОД")
        export_btn.clicked.connect(self.export_code)
        left_layout.addWidget(export_btn)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Права панель - полотно
        right_panel = QFrame()
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
            QMessageBox.information(self, "Готово", f"Розмітку збережено!\nЕлементів: {len(layout_data)}")
    
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
                QMessageBox.information(self, "Готово", f"Розмітку завантажено!\nЕлементів: {len(layout_data)}")
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
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
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
                padding: 8px;
                border-radius: 20px;
                border: 2px solid #000000;
                font-size: 11px;
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
            code += f'''        # {item['text']} {i+1}
        self.btn_{i+1} = QPushButton("{item['text']}", central_widget)
        self.btn_{i+1}.setFixedSize(120, 40)
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
            QMessageBox.information(self, "Готово", f"Код експортовано!\nЕлементів: {len(layout_data)}")

def main():
    app = QApplication(sys.argv)
    constructor = LCARSConstructor()
    constructor.show()
    
    print('🎨 LCARS Visual Constructor запущено!')
    print('🔧 Перетягуйте елементи на полотно')
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())

class DraggableWidget(QFrame):
    """Віджет, який можна перетягувати"""
    
    def __init__(self, widget_type, text="", parent=None):
        super().__init__(parent)
        self.widget_type = widget_type
        self.text = text
        self.current_faction = "starfleet"
        self.setMouseTracking(True)
        self.drag_start_pos = None
        self.is_dragging = False
        self.is_on_canvas = False  # Чи віджет на полотні
        
        # Стиль для конструктора
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #FF6B6B;
                background-color: rgba(255, 107, 107, 0.1);
                border-radius: 5px;
            }
            QFrame:hover {
                border: 2px solid #FF6B6B;
                background-color: rgba(255, 107, 107, 0.2);
            }
        """)
        
        # Створити реальний віджет
        self.create_real_widget()
    
    def create_real_widget(self):
        """Створити реальний LCARS віджет"""
        if True:
            if hasattr(self, 'real_widget') and self.real_widget:
                self.real_widget.deleteLater()
            
            self.real_widget = create_widget(
                self.widget_type, 
                self.text, 
                self.current_faction, 
                parent=self
            )
            
            if self.real_widget:
                # Розмістити реальний віджет всередині
                layout = QVBoxLayout(self)
                layout.setContentsMargins(5, 5, 5, 5)
                layout.addWidget(self.real_widget)
                
                # Встановити розмір
                if self.real_widget.width() > 0:
                    self.resize(self.real_widget.size())
                else:
                    self.resize(200, 60)
                
        if False: # Removed except block
            print(f"Error creating widget: {e}")
            # Якщо не вдалося, створити просту кнопку
            self.real_widget = QPushButton(self.text or self.widget_type.upper())
            self.real_widget.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: #000000;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
            layout = QVBoxLayout(self)
            layout.addWidget(self.real_widget)
            self.resize(200, 60)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Початок перетягування"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.position().toPoint()
            self.is_dragging = True
            self.raise_()  # Підняти на передній план
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Перетягування"""
        if self.is_dragging and self.drag_start_pos:
            if (event.position().toPoint() - self.drag_start_pos).manhattanLength() > 10:
                # Почати drag & drop
                drag = QDrag(self)
                pixmap = QPixmap(self.size())
                self.render(pixmap)
                drag.setPixmap(pixmap)
                
                mime_data = QMimeData()
                mime_data.setText(f"{self.widget_type}:{self.text}:{self.current_faction}")
                drag.setMimeData(mime_data)
                
                # Виконати drag
                drop_action = drag.exec()
                
                # Якщо це копія з палітри, не видаляти оригінал
                if drop_action == Qt.DropAction.MoveAction and self.is_on_canvas:
                    self.deleteLater()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Кінець перетягування"""
        self.is_dragging = False
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)
    
    def update_faction(self, faction):
        """Оновити фракцію віджета"""
        self.current_faction = faction
        self.create_real_widget()

class ConstructorCanvas(QFrame):
    """Полотно для розміщення віджетів"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 2px solid #FF6B6B;
                border-radius: 10px;
            }
        """)
        self.setAcceptDrops(True)
        self.widgets = []
        
        # Layout для віджетів
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
    
    def dragEnterEvent(self, event):
        """Дозволити drop"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
            print("Drag enter event accepted")
    
    def dragMoveEvent(self, event):
        """Дозволити move"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """Обробити drop"""
        print("Drop event received")
        mime_data = event.mimeData().text()
        print(f"Mime data: {mime_data}")
        
        if ":" in mime_data:
            if True:
                widget_type, text, faction = mime_data.split(":", 2)
                print(f"Creating widget: {widget_type}, {text}, {faction}")
                
                # Створити новий віджет
                widget = DraggableWidget(widget_type, text, self)
                widget.is_on_canvas = True  # Позначити що віджет на полотні
                
                # Розмістити в позиції drop
                drop_pos = event.position().toPoint()
                widget.move(drop_pos)
                widget.show()
                
                self.widgets.append(widget)
                event.acceptProposedAction()
                print(f"Widget created and placed at {drop_pos}")
                
            if False: # Removed except block
                print(f"Error processing drop: {e}")
                event.ignore()
        else:
            event.ignore()
    
    def clear_canvas(self):
        """Очистити полотно"""
        for widget in self.widgets:
            widget.deleteLater()
        self.widgets.clear()
    
    def save_layout(self):
        """Зберегти розмітку"""
        layout_data = []
        for widget in self.widgets:
            layout_data.append({
                'type': widget.widget_type,
                'text': widget.text,
                'faction': widget.current_faction,
                'position': [widget.x(), widget.y()],
                'size': [widget.width(), widget.height()]
            })
        return layout_data
    
    def load_layout(self, layout_data):
        """Завантажити розмітку"""
        self.clear_canvas()
        for item in layout_data:
            widget = DraggableWidget(item['type'], item['text'], self)
            widget.is_on_canvas = True
            widget.move(item['position'][0], item['position'][1])
            widget.resize(item['size'][0], item['size'][1])
            widget.show()
            self.widgets.append(widget)

class LCARSConstructor(QMainWindow):
    """Головне вікно конструктора"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS Visual Constructor')
        self.setGeometry(100, 100, 1200, 800)
        
        # Стиль вікна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
            QLabel {
                color: #FF6B6B;
                font-weight: bold;
            }
            QPushButton {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
                border: 2px solid #000000;
            }
            QPushButton:hover {
                background-color: #000000;
                color: #FF6B6B;
            }
            QComboBox {
                background-color: #FF6B6B;
                color: #000000;
                font-weight: bold;
                padding: 5px;
                border-radius: 5px;
                border: 2px solid #000000;
            }
            QGroupBox {
                color: #FF6B6B;
                font-weight: bold;
                border: 2px solid #FF6B6B;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Налаштування інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Ліва панель - інструменти
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Налаштування
        settings_group = QGroupBox("Налаштування")
        settings_layout = QVBoxLayout()
        
        # Вибір фракції
        faction_label = QLabel("Фракція:")
        self.faction_combo = QComboBox()
        self.faction_combo.addItems(["starfleet", "klingon", "romulan", "cardassian"])
        self.faction_combo.currentTextChanged.connect(self.update_widgets_faction)
        
        settings_layout.addWidget(faction_label)
        settings_layout.addWidget(self.faction_combo)
        
        # Текст для кнопок
        text_label = QLabel("Текст кнопки:")
        self.text_input = QPushButton("BUTTON")
        self.text_input.clicked.connect(self.change_button_text)
        
        settings_layout.addWidget(text_label)
        settings_layout.addWidget(self.text_input)
        
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # Палітра віджетів
        widgets_group = QGroupBox("Палітра віджетів")
        widgets_layout = QVBoxLayout()
        
        # Створюємо віджети для drag & drop
        widget_types = [
            ("panel", "Панель"),
            ("button", "Кнопка"),
            ("mini", "Міні-кнопка"),
            ("display", "Дисплей"),
            ("console", "Консоль")
        ]
        
        for widget_type, label in widget_types:
            widget = DraggableWidget(widget_type, label, self)
            widget.setFixedSize(250, 60)
            widgets_layout.addWidget(widget)
        
        widgets_group.setLayout(widgets_layout)
        left_layout.addWidget(widgets_group)
        
        # Кнопки управління
        controls_group = QGroupBox("Управління")
        controls_layout = QVBoxLayout()
        
        clear_btn = QPushButton("Очистити полотно")
        clear_btn.clicked.connect(self.clear_canvas)
        controls_layout.addWidget(clear_btn)
        
        save_btn = QPushButton("Зберегти розмітку")
        save_btn.clicked.connect(self.save_layout)
        controls_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Завантажити розмітку")
        load_btn.clicked.connect(self.load_layout)
        controls_layout.addWidget(load_btn)
        
        export_btn = QPushButton("Експортувати в код")
        export_btn.clicked.connect(self.export_code)
        controls_layout.addWidget(export_btn)
        
        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        
        # Права панель - полотно
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        
        canvas_label = QLabel("Полотно конструктора:")
        right_layout.addWidget(canvas_label)
        
        # Полотно з прокруткою
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.canvas = ConstructorCanvas()
        self.canvas.setMinimumSize(800, 600)
        scroll_area.setWidget(self.canvas)
        right_layout.addWidget(scroll_area)
        
        main_layout.addWidget(right_panel)
    
    def update_widgets_faction(self, faction):
        """Оновити фракцію для всіх віджетів"""
        for widget in self.canvas.widgets:
            widget.update_faction(faction)
    
    def change_button_text(self):
        """Змінити текст для кнопок"""
        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Текст кнопки", "Введіть текст:")
        if ok and text:
            self.text_input.setText(text)
    
    def clear_canvas(self):
        """Очистити полотно"""
        self.canvas.clear_canvas()
    
    def save_layout(self):
        """Зберегти розмітку"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Зберегти розмітку", "", "JSON Files (*.json)"
        )
        if filename:
            layout_data = self.canvas.save_layout()
            with open(filename, 'w') as f:
                json.dump(layout_data, f, indent=2)
            QMessageBox.information(self, "Успіх", "Розмітку збережено!")
    
    def load_layout(self):
        """Завантажити розмітку"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Завантажити розмітку", "", "JSON Files (*.json)"
        )
        if filename:
            if True:
                with open(filename, 'r') as f:
                    layout_data = json.load(f)
                self.canvas.load_layout(layout_data)
                QMessageBox.information(self, "Успіх", "Розмітку завантажено!")
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
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout

# Додати шлях до проєкту
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if True:
    from lcars.themes.eras.Constructor import create_widget
if False: # Removed except block
    print("Cannot import LCARS modules")
    sys.exit(1)

class GeneratedInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generated LCARS Interface")
        self.setGeometry(100, 100, 1200, 800)
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Створити віджети
'''
        
        for i, item in enumerate(layout_data):
            code += f'''
        # Віджет {i+1}
        widget_{i+1} = create_widget(
            "{item['type']}", 
            "{item['text']}", 
            "{item['faction']}", 
            parent=central_widget
        )
        widget_{i+1}.move({item['position'][0]}, {item['position'][1]})
        widget_{i+1}.show()
'''
        
        code += '''

def main():
    app = QApplication(sys.argv)
    window = GeneratedInterface()
    window.show()
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
'''
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Експортувати код", "", "Python Files (*.py)"
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(code)
            QMessageBox.information(self, "Успіх", "Код експортовано!")

def main():
    app = QApplication(sys.argv)
    constructor = LCARSConstructor()
    constructor.show()
    
    print('🎨 LCARS Visual Constructor Started')
    print('🔧 Drag & Drop interface builder')
    
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
