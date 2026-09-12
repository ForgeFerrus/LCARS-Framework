#!/usr/bin/env python3
"""
Сучасний LCARS інтерфейс з правильною архітектурою
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette

class LCARSButton(QPushButton):
    """Спеціалізована кнопка LCARS"""
    def __init__(self, text, color="#ff9c00", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: white;
                color: {color};
            }}
            QPushButton:pressed {{
                background-color: #cccccc;
            }}
        """)
        self.setFixedSize(100, 35)

class LCARSElbow(QFrame):
    """Елемент 'лікоть' LCARS"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 30)
        self.setStyleSheet("""
            QFrame {
                background-color: #ff9c00;
                border: none;
            }
        """)

class LCARSSidePanel(QFrame):
    """Бічна панель LCARS"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(100)
        self.setStyleSheet("""
            QFrame {
                background-color: #ff9c00;
                border: none;
            }
        """)

class LCARSMainWindow(QMainWindow):
    """Головне вікно LCARS"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS System 47")
        self.setGeometry(100, 100, 1024, 768)
        
        # Прибираємо рамку вікна
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Встановлюємо темну тему
        self.setStyleSheet("background-color: black;")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Налаштування інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Ліва частина з "ліктем" та бічною панеллю
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(10, 10, 0, 10)
        left_layout.setSpacing(0)
        
        # Елемент "лікоть"
        elbow = LCARSElbow()
        left_layout.addWidget(elbow)
        
        # Бічна панель з кнопками
        side_panel = LCARSSidePanel()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(10, 40, 10, 10)
        side_layout.setSpacing(5)
        
        # Кнопки меню
        buttons_data = [
            ("Library", "#cc99cc"),
            ("Tactical", "#cc6666"),
            ("Sensors", "#ff9c00"),
            ("", None),  # Розділювач
            ("Exit", "#cc6666")
        ]
        
        for text, color in buttons_data:
            if text:
                btn = LCARSButton(text, color)
                if text == "Exit":
                    btn.clicked.connect(self.close)
                else:
                    btn.clicked.connect(lambda checked, t=text: self.button_clicked(t))
                side_layout.addWidget(btn)
            else:
                # Розділювач
                separator = QWidget()
                separator.setFixedHeight(20)
                side_layout.addWidget(separator)
        
        left_layout.addWidget(side_panel)
        main_layout.addWidget(left_widget)
        
        # Права частина - контентна область
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Заголовок
        title = QLabel("LCARS SYSTEM 47")
        title.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        title.setStyleSheet("color: #ff9c00;")
        content_layout.addWidget(title)
        
        # Контентна область
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                border: 2px solid #cc99cc;
                background-color: transparent;
            }
        """)
        content_layout.addWidget(content_area)
        
        # Текст в контентній області
        content_text = QLabel("SYSTEM ONLINE\nAWAITING INPUT...")
        content_text.setFont(QFont("Arial", 24))
        content_text.setStyleSheet("color: #ff9c00;")
        content_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Розміщуємо текст в центрі контентної області
        content_layout.addWidget(content_text)
        
        main_layout.addWidget(content_widget)
        
    def button_clicked(self, button_name):
        """Обробка натискання кнопки"""
        print(f"Button clicked: {button_name}")
        # Тут можна додати логіку для кожної кнопки

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо темну палітру
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    window = LCARSMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
