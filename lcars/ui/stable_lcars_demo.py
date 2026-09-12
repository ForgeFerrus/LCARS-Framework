"""
Стабільний LCARS Demo - не залежить від імпортів
Простий, надійний інтерфейс що працює завжди
"""

# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

# Створюємо власні кольори - не залежимо від палітр
LCARS_COLORS = {
    'background': '#000000',
    'text': '#FFFFFF',
    'accent_orange': '#FF9900',
    'accent_blue': '#3399FF',
    'accent_green': '#00CC66',
    'accent_red': '#CC3333',
    'accent_yellow': '#FFCC66',
    'border': '#664466'
}

class LCARSButton(QPushButton):
    """Стабільна LCARS кнопка - не залежить від зовнішніх файлів"""
    
    def __init__(self, text, color_key='accent_orange', parent=None):
        super().__init__(text, parent)
        self.color_key = color_key
        self.apply_style()
        
    def apply_style(self):
        color = LCARS_COLORS.get(self.color_key, '#FF9900')
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #FFFFFF;
                border: 2px solid {LCARS_COLORS['border']};
                border-radius: 25px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """)

class LCARSLabel(QLabel):
    """Стабільний LCARS текст"""
    
    def __init__(self, text, size=16, color_key='text', parent=None):
        super().__init__(text, parent)
        color = LCARS_COLORS.get(color_key, '#FFFFFF')
        self.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {size}px;
                font-weight: bold;
                background: transparent;
                letter-spacing: 2px;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class LCARSPanel(QWidget):
    """Стабільна LCARS панель"""
    
    def __init__(self, color_key='background', parent=None):
        super().__init__(parent)
        color = LCARS_COLORS.get(color_key, '#000000')
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid {LCARS_COLORS['border']};
                border-radius: 15px;
            }}
        """)

class StableLCARSDemo(QMainWindow):
    """Стабільний LCARS демо-інтерфейс"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("STABLE LCARS DEMO")
        self.setGeometry(100, 100, 1200, 800)
        self.setup_ui()
        
    def setup_ui(self):
        # Фон
        self.setStyleSheet(f"background-color: {LCARS_COLORS['background']};")
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        header = LCARSLabel("LCARS INTERFACE", 24, 'accent_orange')
        main_layout.addWidget(header)
        
        # Панель з кнопками
        button_panel = LCARSPanel('background')
        button_layout = QVBoxLayout(button_panel)
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(20, 20, 20, 20)
        
        # Кнопки з різними кольорами
        buttons_data = [
            ("STARFLEET COMMAND", 'accent_blue'),
            ("TACTICAL SYSTEMS", 'accent_red'),
            ("SCIENCE LABORATORY", 'accent_green'),
            ("ENGINEERING CORE", 'accent_yellow'),
            ("MEDICAL BAY", 'accent_orange'),
            ("COMMUNICATIONS", 'accent_blue'),
            ("SECURITY DECK", 'accent_red'),
            ("HOLODECK", 'accent_green')
        ]
        
        for text, color in buttons_data:
            btn = LCARSButton(text, color)
            btn.setMinimumHeight(50)
            button_layout.addWidget(btn)
        
        button_layout.addStretch()
        main_layout.addWidget(button_panel)
        
        # Статус панель
        status_panel = LCARSPanel('background')
        status_layout = QHBoxLayout(status_panel)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        status_label = LCARSLabel("SYSTEM ONLINE", 14, 'accent_green')
        status_layout.addWidget(status_label)
        status_layout.addStretch()
        
        time_label = LCARSLabel("STARDATE 43210.5", 14, 'text')
        status_layout.addWidget(time_label)
        
        main_layout.addWidget(status_panel)
        
        # Таймер для анімації
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(2000)
        
    def update_status(self):
        # Проста анімація статусу
        import random
        statuses = ["SYSTEM ONLINE", "SCANNING", "ANALYZING", "STANDBY"]
        colors = ['accent_green', 'accent_blue', 'accent_yellow', 'accent_orange']
        
        status = random.choice(statuses)
        color = random.choice(colors)
        
        # Оновлюємо статус
        labels = self.findChildren(QLabel)
        for label in labels:
            if "SYSTEM" in label.text() or "SCANNING" in label.text():
                label.setText(status)
                label.setStyleSheet(f"""
                    QLabel {{
                        color: {LCARS_COLORS[color]};
                        font-size: 14px;
                        font-weight: bold;
                        background: transparent;
                        letter-spacing: 2px;
                    }}
                """)
                break

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо шрифт
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = StableLCARSDemo()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
