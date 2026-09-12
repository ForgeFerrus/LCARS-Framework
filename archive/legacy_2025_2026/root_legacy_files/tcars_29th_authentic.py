#!/usr/bin/env python3
"""
TCARS 29th Century - Справжній LCARS стиль з SVG елементами
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout)
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_random_button_color

class LCARSWidget(QWidget):
    """Базовий LCARS віджет з правильними кутами"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.color = QColor(100, 200, 255)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо LCARS кути
        self.draw_lcars_corners(painter)
        
    def draw_lcars_corners(self, painter):
        """Малювання характерних LCARS кутів"""
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(self.color))
        
        w, h = self.width(), self.height()
        corner_size = 40
        
        # Верхній лівий кут (класичний LCARS)
        path = QPainterPath()
        path.moveTo(0, corner_size)
        path.quadTo(0, 0, corner_size, 0)
        path.lineTo(0, corner_size)
        painter.drawPath(path)
        
        # Верхній правий кут
        path = QPainterPath()
        path.moveTo(w - corner_size, 0)
        path.quadTo(w, 0, w, corner_size)
        path.lineTo(w - corner_size, 0)
        painter.drawPath(path)
        
        # Нижній лівий кут
        path = QPainterPath()
        path.moveTo(0, h - corner_size)
        path.quadTo(0, h, corner_size, h)
        path.lineTo(0, h - corner_size)
        painter.drawPath(path)
        
        # Нижній правий кут
        path = QPainterPath()
        path.moveTo(w - corner_size, h)
        path.quadTo(w, h, w, h - corner_size)
        path.lineTo(w - corner_size, h)
        painter.drawPath(path)

class LCARSButton(QPushButton):
    """LCARS кнопка з правильним стилем"""
    def __init__(self, text, color, parent=None):
        super().__init__(text, parent)
        self.base_color = QColor(color)
        self.setFixedHeight(50)
        self.setup_lcars_style()
        
    def setup_lcars_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color.name()};
                color: #000000;
                border: none;
                font-weight: bold;
                font-size: 14px;
                text-transform: uppercase;
                padding-left: 15px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {self.base_color.name()};
            }}
            QPushButton:pressed {{
                background-color: {self.base_color.darker(120).name()};
            }}
        """)

class LCARSPanel(QWidget):
    """LCARS панель з кутами"""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedWidth(120)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(self.color))
        
        w, h = self.width(), self.height()
        
        # Верхній кутовий елемент
        path = QPainterPath()
        path.moveTo(0, 60)
        path.quadTo(0, 0, 90, 0)
        path.lineTo(120, 0)
        path.lineTo(120, 60)
        path.lineTo(0, 60)
        painter.drawPath(path)
        
        # Основна панель
        painter.drawRect(0, 60, w, h - 140)
        
        # Нижній кутовий елемент
        path = QPainterPath()
        path.moveTo(0, h - 80)
        path.lineTo(120, h - 80)
        path.lineTo(120, h)
        path.lineTo(0, h)
        path.lineTo(0, h - 80)
        painter.drawPath(path)

class TCARS29thCentury(QMainWindow):
    """
    29th Century TCARS - справжній LCARS стиль
    """
    
    temporal_alert = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCARS 29th CENTURY")
        
        # Підключаємо палітру 29го століття
        self.colors = get_era_palette(LCARSEra.TCARS_29TH)
        self.era = LCARSEra.TCARS_29TH
        
        # Налаштовуємо алгоритм
        self.setup_color_algorithm()
        
        # Створюємо LCARS інтерфейс
        self.setup_lcars_interface()
        
        # Запускаємо моніторинг
        self.start_monitoring()
        
    def setup_color_algorithm(self):
        """Алгоритм динамічних кольорів"""
        self.color_index = 0
        
        # Таймер для зміни кольорів
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(2000)
        
    def update_colors(self):
        """Оновлює кольори за алгоритмом"""
        # Оновлюємо основний стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QLabel {{
                color: {get_random_button_color(self.era)};
                background-color: transparent;
                font-family: 'Arial', sans-serif;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QTabWidget::pane {{
                border: 2px solid {self.colors['panel_border']};
                background-color: {self.colors['background']};
            }}
            QTabBar::tab {{
                background-color: {get_random_button_color(self.era)};
                color: {self.colors['background']};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['panel_border']};
            }}
            QLineEdit {{
                background-color: {self.colors['background']};
                color: {get_random_button_color(self.era)};
                border: 1px solid {self.colors['panel_border']};
                border-radius: 3px;
                padding: 5px;
                font-weight: bold;
            }}
        """)
        
        # Оновлюємо кольори кнопок
        self.update_button_colors()
        
        print(f"🔄 LCARS кольори оновлено")
        
    def setup_lcars_interface(self):
        """Створення справжнього LCARS інтерфейсу"""
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Основний layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Ліва панель - LCARS стиль
        left_panel = self.create_lcars_left_panel()
        main_layout.addWidget(left_panel)
        
        # Центральна область
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхня панель з кутами
        top_panel = self.create_lcars_top_panel()
        center_layout.addWidget(top_panel)
        
        # Основний контент
        content = self.create_main_content()
        center_layout.addWidget(content)
        
        # Нижня панель з кутами
        bottom_panel = self.create_lcars_bottom_panel()
        center_layout.addWidget(bottom_panel)
        
        main_layout.addWidget(center_area)
        
        # Права панель - LCARS стиль
        right_panel = self.create_lcars_right_panel()
        main_layout.addWidget(right_panel)
        
    def create_lcars_left_panel(self):
        """Створення лівої LCARS панелі"""
        left_panel = QWidget()
        left_panel.setFixedWidth(120)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Верхній кутовий елемент
        corner_top = LCARSWidget()
        corner_top.setFixedHeight(60)
        corner_top.color = QColor(get_random_button_color(self.era))
        left_layout.addWidget(corner_top)
        
        # Кнопки управління
        buttons = ["PRIME", "ALTERNATE", "NEXUS", "SHIELDS", "ALERT", "RESET"]
        for text in buttons:
            btn = LCARSButton(text, get_random_button_color(self.era))
            
            if text == "SHIELDS":
                btn.clicked.connect(self.toggle_shields)
            elif text == "ALERT":
                btn.clicked.connect(lambda: self.temporal_alert.emit("Temporal anomaly!"))
            elif text == "RESET":
                btn.clicked.connect(self.return_to_main)
                
            left_layout.addWidget(btn)
            
        # Нижній кутовий елемент
        corner_bottom = LCARSWidget()
        corner_bottom.setFixedHeight(80)
        corner_bottom.color = QColor(self.colors['background'])
        left_layout.addWidget(corner_bottom)
        
        left_layout.addStretch()
        
        return left_panel
        
    def create_lcars_right_panel(self):
        """Створення правої LCARS панелі"""
        right_panel = QWidget()
        right_panel.setFixedWidth(100)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # Верхній кутовий елемент
        corner_top = LCARSWidget()
        corner_top.setFixedHeight(40)
        corner_top.color = QColor(get_random_button_color(self.era))
        right_layout.addWidget(corner_top)
        
        # Статусні індикатори
        status_colors = [get_random_button_color(self.era) for _ in range(5)]
        for i, color in enumerate(status_colors):
            indicator = LCARSWidget()
            indicator.setFixedHeight(30)
            indicator.color = QColor(color)
            right_layout.addWidget(indicator)
            
        # Нижній кутовий елемент
        corner_bottom = LCARSWidget()
        corner_bottom.setFixedHeight(60)
        corner_bottom.color = QColor(self.colors['background'])
        right_layout.addWidget(corner_bottom)
        
        right_layout.addStretch()
        
        return right_panel
        
    def create_lcars_top_panel(self):
        """Створення верхньої LCARS панелі"""
        top_panel = QWidget()
        top_panel.setFixedHeight(80)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Лівий кут
        left_corner = LCARSWidget()
        left_corner.setFixedWidth(100)
        left_corner.color = QColor(get_random_button_color(self.era))
        top_layout.addWidget(left_corner)
        
        # Заголовок
        title = QLabel("TCARS 29th CENTURY")
        title.setStyleSheet(f"""
            QLabel {{
                color: #000000;
                font-size: 32px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 4px;
                padding: 20px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Фон заголовка
        title_bg = QWidget()
        title_bg.setStyleSheet(f"background-color: {get_random_button_color(self.era)};")
        title_layout = QVBoxLayout(title_bg)
        title_layout.addWidget(title)
        top_layout.addWidget(title_bg)
        
        # Правий кут
        right_corner = LCARSWidget()
        right_corner.setFixedWidth(100)
        right_corner.color = QColor(get_random_button_color(self.era))
        top_layout.addWidget(right_corner)
        
        return top_panel
        
    def create_lcars_bottom_panel(self):
        """Створення нижньої LCARS панелі"""
        bottom_panel = QWidget()
        bottom_panel.setFixedHeight(60)
        bottom_layout = QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        # Лівий кут
        left_corner = LCARSWidget()
        left_corner.setFixedWidth(80)
        left_corner.color = QColor(get_random_button_color(self.era))
        bottom_layout.addWidget(left_corner)
        
        # Статусна інформація
        status = QLabel("TEMPORAL CORE: STABLE")
        status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 18px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 2px;
                padding: 15px;
            }}
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_layout.addWidget(status)
        
        # Правий кут
        right_corner = LCARSWidget()
        right_corner.setFixedWidth(80)
        right_corner.color = QColor(get_random_button_color(self.era))
        bottom_layout.addWidget(right_corner)
        
        return bottom_panel
        
    def create_main_content(self):
        """Створення основного контенту"""
        content = QWidget()
        content.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['panel_border']};
                border-radius: 10px;
            }}
        """)
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Статус
        self.temporal_status = QLabel("TEMPORAL CORE: STABLE")
        self.temporal_status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border: 2px solid {self.colors['panel_border']};
                border-radius: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
        """)
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.temporal_status)
        
        # Вкладки
        self.timeline_monitor = QTabWidget()
        self.setup_timeline_tabs()
        content_layout.addWidget(self.timeline_monitor)
        
        # Панель управління
        control_panel = QWidget()
        control_layout = QFormLayout()
        self.add_controls(control_layout)
        control_panel.setLayout(control_layout)
        content_layout.addWidget(control_panel)
        
        return content
        
    def setup_timeline_tabs(self):
        """Налаштування вкладок"""
        tabs_data = [
            ("PRIME", "PRIME TIMELINE INTEGRITY: 100%", 
             "No temporal incursions detected\nAll timelines stable\nQuantum coherence: 99.8%"),
            ("ALTERNATE", "ALTERNATE TIMELINES: SCANNING", 
             "0 alternate timelines detected\nParadox level: 0.0%\nTemporal stability: OPTIMAL"),
            ("NEXUS", "TEMPORAL NEXUS: STABLE", 
             "Nexus stability: OPTIMAL\nChroniton flow: NORMAL\nTime displacement: 0.00ms")
        ]
        
        for tab_name, status_text, info_text in tabs_data:
            tab = QWidget()
            layout = QVBoxLayout()
            
            status = QLabel(status_text)
            status.setStyleSheet(f"""
                QLabel {{
                    color: {get_random_button_color(self.era)};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    text-transform: uppercase;
                }}
            """)
            layout.addWidget(status)
            
            info = QLabel(info_text)
            info.setStyleSheet(f"""
                QLabel {{
                    color: {get_random_button_color(self.era)};
                    font-size: 14px;
                    padding: 10px;
                    border: 1px solid {self.colors['panel_border']};
                    border-radius: 5px;
                }}
            """)
            layout.addWidget(info)
            
            tab.setLayout(layout)
            self.timeline_monitor.addTab(tab, tab_name)
            
    def add_controls(self, layout):
        """Додавання елементів управління"""
        controls = [
            ("Chronometric:", "Quantum Chronometric Reading"),
            ("Stability:", "100%"),
            ("Coefficient:", "1.0000"),
            ("Paradox:", "0.00%")
        ]
        
        for label_text, placeholder in controls:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if placeholder in ["100%", "1.0000", "0.00%"]:
                field.setReadOnly(True)
            layout.addRow(QLabel(label_text), field)
            
    def update_button_colors(self):
        """Оновлення кольорів кнопок"""
        for btn in self.findChildren(LCARSButton):
            new_color = QColor(get_random_button_color(self.era))
            btn.base_color = new_color
            btn.setup_lcars_style()
            
        # Оновлення кольорів LCARS віджетів
        for widget in self.findChildren(LCARSWidget):
            if widget.color.name() != self.colors['background']:
                widget.color = QColor(get_random_button_color(self.era))
                widget.update()
                
    def toggle_shields(self):
        """Перемикання щитів"""
        self.temporal_status.setText("TEMPORAL CORE: SHIELDS ACTIVE")
        
    def return_to_main(self):
        """Повернення"""
        self.close()
        
    def start_monitoring(self):
        """Запуск моніторингу"""
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_status)
        self.monitor_timer.start(1000)
        
        # Підключення сигналів
        self.temporal_alert.connect(self.alert_handler)
        
    def update_status(self):
        """Оновлення статусу"""
        pass
        
    def alert_handler(self, message):
        """Обробка alert"""
        self.temporal_status.setText(f"TEMPORAL ALERT: {message}")
        self.temporal_status.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['alert_colors'][0]};
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                border: 2px solid {self.colors['alert_colors'][0]};
                border-radius: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
        """)

def main():
    app = QApplication(sys.argv)
    window = TCARS29thCentury()
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
