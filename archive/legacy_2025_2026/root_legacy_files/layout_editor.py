"""
LCARS Layout Editor - простий редактор макетів
Інтегрований в основну систему LCARS Framework
"""
import json
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, 
                            QVBoxLayout, QLabel, QMainWindow, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QMouseEvent

class LCARSButton(QPushButton):
    """LCARS кнопка з можливістю перетягування"""
    
    def __init__(self, number='00-0000', label='BUTTON', color='#3399FF', 
                 bar_color='#CCCCCC', parent=None):
        super().__init__(parent)
        self._number = number
        self._label = label
        self._color = color
        self._bar_color = bar_color
        self._border_color = '#222222'
        
        self.setMinimumSize(150, 70)
        self.setStyleSheet("background: transparent; border: none;")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Початок перетягування"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position()
            self._original_pos = self.pos()
            self.raise_()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Перетягування"""
        if hasattr(self, '_drag_start') and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._drag_start
            new_pos = self._original_pos + delta.toPoint()
            self.move(new_pos)
            if self.parent():
                self.parent().update_positions()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Кінець перетягування"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Малювання LCARS кнопки"""
        w, h = self.width(), self.height()
        bar_h = int(h * 0.3)
        square_size = int(h * 0.4)
        circle_d = int(square_size * 0.6)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Основний прямокутник
        pen_width = 2
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._color))
        painter.drawRect(0, 0, w, h - bar_h)
        
        # Сіра смуга знизу
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(0, h - bar_h, w, bar_h)
        
        # Квадрат у правому верхньому куті
        sq_x = w - square_size - pen_width
        sq_y = pen_width
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(sq_x, sq_y, square_size, square_size)
        
        # Білий круг у квадраті
        circ_x = sq_x + (square_size - circle_d) // 2
        circ_y = sq_y + (square_size - circle_d) // 2
        painter.setBrush(QColor('#FFFFFF'))
        painter.drawEllipse(circ_x, circ_y, circle_d, circle_d)
        
        # Номер
        painter.setPen(QPen(QColor('#111111'), 2))
        font = QFont('Arial', max(10, int((h - bar_h) * 0.3)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int((h - bar_h) * 0.2), w, int((h - bar_h) * 0.3), 
                        Qt.AlignmentFlag.AlignCenter, self._number)
        
        # Підпис
        font.setPointSize(max(8, int(bar_h * 0.5)))
        painter.setFont(font)
        painter.drawText(0, h - bar_h, w, bar_h, 
                        Qt.AlignmentFlag.AlignCenter, self._label)

class LCARSPanel(QWidget):
    """LCARS панель з можливістю перетягування"""
    
    def __init__(self, label='PANEL', circle_color='#1A3AFF', parent=None):
        super().__init__(parent)
        self.label = label
        self.circle_color = circle_color
        
        self.setMinimumSize(250, 180)
        self.setStyleSheet("background: transparent;")
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_MouseTracking)
        
    def mousePressEvent(self, event: QMouseEvent):
        """Початок перетягування"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position()
            self._original_pos = self.pos()
            self.raise_()
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event: QMouseEvent):
        """Перетягування"""
        if hasattr(self, '_drag_start') and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.position() - self._drag_start
            new_pos = self._original_pos + delta.toPoint()
            self.move(new_pos)
            if self.parent():
                self.parent().update_positions()
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Кінець перетягування"""
        if hasattr(self, '_drag_start'):
            delattr(self, '_drag_start')
        super().mouseReleaseEvent(event)
        
    def paintEvent(self, event):
        """Малювання LCARS панелі"""
        w, h = self.width(), self.height()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Основна панель
        painter.setPen(QPen(QColor('#BFC2C4'), 6))
        painter.setBrush(QColor('#000000'))
        painter.drawRect(0, 0, w, h)
        
        # Круговий індикатор
        circle_size = min(w, h) * 0.25
        painter.setPen(QPen(QColor(self.circle_color), 4))
        painter.setBrush(QColor(self.circle_color))
        painter.drawEllipse(int(w * 0.1), int(h * 0.1), int(circle_size), int(circle_size))
        
        # Назва панелі
        painter.setPen(QPen(QColor('#FFFFFF'), 2))
        font = QFont('Arial', max(14, int(h * 0.15)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int(h * 0.6), w, int(h * 0.3), 
                        Qt.AlignmentFlag.AlignCenter, self.label)

class LCARSLayoutEditor(QMainWindow):
    """Головний редактор макетів"""
    
    def __init__(self):
        super().__init__()
        self.elements = []
        self.init_ui()
        
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle("LCARS Layout Editor")
        self.setGeometry(100, 100, 1400, 900)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QHBoxLayout(central_widget)
        
        # Область для роботи
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background-color: #000000;")
        self.canvas.setMinimumSize(1000, 700)
        main_layout.addWidget(self.canvas, 4)
        
        # Панель керування
        control_panel = QWidget()
        control_panel.setMaximumWidth(350)
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, 1)
        
        # Заголовок
        title = QLabel("LCARS EDITOR")
        title.setStyleSheet("color: #FFCC33; font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(title)
        
        # Кнопки додавання
        btn_style = """
        QPushButton {
            background-color: #3399FF;
            color: white;
            border: 2px solid #222222;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            padding: 12px;
        }
        QPushButton:hover {
            background-color: #55AAFF;
        }
        """
        
        self.add_btn = QPushButton("Додати Кнопку")
        self.add_btn.setStyleSheet(btn_style)
        self.add_btn.clicked.connect(self.add_button)
        control_layout.addWidget(self.add_btn)
        
        self.add_panel_btn = QPushButton("Додати Панель")
        self.add_panel_btn.setStyleSheet(btn_style)
        self.add_panel_btn.clicked.connect(self.add_panel)
        control_layout.addWidget(self.add_panel_btn)
        
        # Розділювач
        separator = QLabel()
        separator.setStyleSheet("background-color: #444444; height: 2px; margin: 10px;")
        control_layout.addWidget(separator)
        
        # Кнопки управління
        save_style = """
        QPushButton {
            background-color: #00AA66;
            color: white;
            border: 2px solid #222222;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            padding: 12px;
        }
        QPushButton:hover {
            background-color: #00CC88;
        }
        """
        
        self.save_btn = QPushButton("Зберегти Макет")
        self.save_btn.setStyleSheet(save_style)
        self.save_btn.clicked.connect(self.save_layout)
        control_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("Завантажити Макет")
        self.load_btn.setStyleSheet(save_style)
        self.load_btn.clicked.connect(self.load_layout)
        control_layout.addWidget(self.load_btn)
        
        clear_style = """
        QPushButton {
            background-color: #CC3333;
            color: white;
            border: 2px solid #222222;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            padding: 12px;
        }
        QPushButton:hover {
            background-color: #FF5555;
        }
        """
        
        self.clear_btn = QPushButton("Очистити Все")
        self.clear_btn.setStyleSheet(clear_style)
        self.clear_btn.clicked.connect(self.clear_layout)
        control_layout.addWidget(self.clear_btn)
        
        # Статус
        control_layout.addStretch()
        self.status_label = QLabel("Готовий до роботи")
        self.status_label.setStyleSheet("color: #CCCCCC; font-size: 14px; padding: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.status_label)
        
    def add_button(self):
        """Додати кнопку"""
        button = LCARSButton(
            number=f"00-{len(self.elements)+1:04d}",
            label=f"BUTTON {len(self.elements)+1}",
            color="#3399FF",
            bar_color="#CCCCCC",
            parent=self.canvas
        )
        button.setGeometry(100 + (len(self.elements) * 40), 100 + (len(self.elements) * 30), 200, 80)
        button.show()
        
        self.elements.append({
            'type': 'button',
            'widget': button,
            'number': button._number,
            'label': button._label,
            'color': button._color,
            'bar_color': button._bar_color
        })
        
        self.status_label.setText(f"Додано кнопку: {len(self.elements)}")
        
    def add_panel(self):
        """Додати панель"""
        panel = LCARSPanel(
            label=f"PANEL {len(self.elements)+1}",
            circle_color="#1A3AFF",
            parent=self.canvas
        )
        panel.setGeometry(150 + (len(self.elements) * 50), 150 + (len(self.elements) * 40), 300, 200)
        panel.show()
        
        self.elements.append({
            'type': 'panel',
            'widget': panel,
            'label': panel.label,
            'circle_color': panel.circle_color
        })
        
        self.status_label.setText(f"Додано панель: {len(self.elements)}")
        
    def update_positions(self):
        """Оновити позиції елементів"""
        for element in self.elements:
            widget = element['widget']
            element['x'] = widget.x()
            element['y'] = widget.y()
            element['width'] = widget.width()
            element['height'] = widget.height()
            
    def save_layout(self):
        """Зберегти макет"""
        self.update_positions()
        
        layout_data = []
        for element in self.elements:
            if element['type'] == 'button':
                data = {
                    'type': 'button',
                    'x': element['x'],
                    'y': element['y'],
                    'width': element['width'],
                    'height': element['height'],
                    'number': element['number'],
                    'label': element['label'],
                    'color': element['color'],
                    'bar_color': element['bar_color']
                }
            else:  # panel
                data = {
                    'type': 'panel',
                    'x': element['x'],
                    'y': element['y'],
                    'width': element['width'],
                    'height': element['height'],
                    'label': element['label'],
                    'circle_color': element['circle_color']
                }
            layout_data.append(data)
        
        try:
            with open('lcars_layout.json', 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, ensure_ascii=False, indent=2)
            self.status_label.setText(f"Збережено: {len(layout_data)} елементів")
            QMessageBox.information(self, "Успіх", "Макет збережено!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося зберегти: {str(e)}")
            
    def load_layout(self):
        """Завантажити макет"""
        try:
            with open('lcars_layout.json', 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
            
            # Очистити існуючі елементи
            self.clear_layout()
            
            # Створити елементи з файлу
            for item in layout_data:
                if item['type'] == 'button':
                    widget = LCARSButton(
                        number=item.get('number', '00-0000'),
                        label=item.get('label', 'BUTTON'),
                        color=item.get('color', '#3399FF'),
                        bar_color=item.get('bar_color', '#CCCCCC'),
                        parent=self.canvas
                    )
                    widget.setGeometry(item['x'], item['y'], item['width'], item['height'])
                    widget.show()
                    
                    self.elements.append({
                        'type': 'button',
                        'widget': widget,
                        'number': widget._number,
                        'label': widget._label,
                        'color': widget._color,
                        'bar_color': widget._bar_color
                    })
                    
                elif item['type'] == 'panel':
                    widget = LCARSPanel(
                        label=item.get('label', 'PANEL'),
                        circle_color=item.get('circle_color', '#1A3AFF'),
                        parent=self.canvas
                    )
                    widget.setGeometry(item['x'], item['y'], item['width'], item['height'])
                    widget.show()
                    
                    self.elements.append({
                        'type': 'panel',
                        'widget': widget,
                        'label': widget.label,
                        'circle_color': widget.circle_color
                    })
            
            self.status_label.setText(f"Завантажено: {len(layout_data)} елементів")
            QMessageBox.information(self, "Успіх", "Макет завантажено!")
            
        except FileNotFoundError:
            QMessageBox.warning(self, "Попередження", "Файл макету не знайдено!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити: {str(e)}")
            
    def clear_layout(self):
        """Очистити все"""
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.status_label.setText("Очищено")

def main():
    """Запуск редактора"""
    app = QApplication(sys.argv)
    editor = LCARSLayoutEditor()
    editor.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
