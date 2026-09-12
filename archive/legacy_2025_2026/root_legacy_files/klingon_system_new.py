#!/usr/bin/env python3
"""
Klingon System - Характерний LCARS стиль з вибором епох
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout,
                           QComboBox, QGridLayout)
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_random_button_color

class KlingonBlade(QWidget):
    """Klingon blade element - агресивний трикутний дизайн"""
    def __init__(self, blade_type="left", color="#CC0000", size=80, parent=None):
        super().__init__(parent)
        self.blade_type = blade_type
        self.color = QColor(color)
        self.size = size
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#FF0000"), 3)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        
        # Create triangular blade shape
        if self.blade_type == "left":
            # Left-pointing blade
            points = [
                QPointF(0, self.size // 2),
                QPointF(self.size, 0),
                QPointF(self.size, self.size)
            ]
        elif self.blade_type == "right":
            # Right-pointing blade
            points = [
                QPointF(self.size, self.size // 2),
                QPointF(0, 0),
                QPointF(0, self.size)
            ]
        elif self.blade_type == "top":
            # Up-pointing blade
            points = [
                QPointF(self.size // 2, 0),
                QPointF(0, self.size),
                QPointF(self.size, self.size)
            ]
        else:  # bottom
            # Down-pointing blade
            points = [
                QPointF(self.size // 2, self.size),
                QPointF(0, 0),
                QPointF(self.size, 0)
            ]
            
        # Draw the blade
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.closeSubpath()
        
        painter.drawPath(path)

class KlingonButton(QPushButton):
    """Klingon button with aggressive styling"""
    def __init__(self, text, button_type="primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setFixedHeight(40)
        self.setup_klingon_style()
        
    def setup_klingon_style(self):
        colors = {
            "primary": "#CC0000",
            "honor": "#990000", 
            "secondary": "#660000",
            "alert": "#FF3300"
        }
        
        base_color = colors.get(self.button_type, "#CC0000")
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {base_color}, 
                    stop:0.5 {base_color}CC, 
                    stop:1 {base_color});
                color: #FFFFFF;
                border: 2px solid #FF0000;
                font-weight: bold;
                font-size: 12px;
                text-transform: uppercase;
                padding: 8px 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF0000, 
                    stop:0.5 #FF6666, 
                    stop:1 #FF0000);
                border: 2px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background: #990000;
                border: 2px solid #FFFF00;
            }}
        """)

class KlingonPanel(QWidget):
    """Klingon panel with aggressive design"""
    def __init__(self, title, color="#990000", has_blades=True, parent=None):
        super().__init__(parent)
        self.title = title
        self.color = QColor(color)
        self.has_blades = has_blades
        self.setup_panel()
        
    def setup_panel(self):
        layout = QVBoxLayout()
        
        # Title with blade decoration
        title_layout = QHBoxLayout()
        
        if self.has_blades:
            left_blade = KlingonBlade("left", self.color.name(), 30)
            title_layout.addWidget(left_blade)
            
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                background-color: {self.color.name()};
                font-size: 14px;
                font-weight: bold;
                padding: 8px 15px;
                text-transform: uppercase;
            }}
        """)
        title_layout.addWidget(title_label)
        
        if self.has_blades:
            right_blade = KlingonBlade("right", self.color.name(), 30)
            title_layout.addWidget(right_blade)
            
        layout.addLayout(title_layout)
        
        # Content area
        self.content_area = QWidget()
        content_layout = QVBoxLayout(self.content_area)
        self.content_area.setStyleSheet(f"""
            QWidget {{
                background-color: #1A0000;
                border: 2px solid {self.color.name()};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        
        layout.addWidget(self.content_area)
        self.setLayout(layout)
        
    def add_widget(self, widget):
        """Add widget to content area"""
        self.content_area.layout().addWidget(widget)

class KlingonInterface(QMainWindow):
    """Klingon Interface with era selection"""
    
    temporal_alert = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KLINGON EMPIRE - TEMPORAL COMMAND")
        
        # Поточна епоха
        self.current_era = LCARSEra.LCARS_24TH
        
        # Підключаємо палітру
        self.load_era_palette()
        
        # Налаштовуємо алгоритм
        self.setup_color_algorithm()
        
        # Створюємо Klingon інтерфейс
        self.setup_klingon_interface()
        
        # Запускаємо моніторинг
        self.start_monitoring()
        
    def load_era_palette(self):
        """Завантаження палітри поточної епохи"""
        self.colors = get_era_palette(self.current_era)
        print(f"⚔️ Завантажено палітру: {self.current_era.value}")
        
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A0000, 
                    stop:0.5 #330000, 
                    stop:1 #1A0000);
            }}
            QLabel {{
                color: {get_random_button_color(self.current_era)};
                background-color: transparent;
                font-family: 'Arial Black', sans-serif;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QTabWidget::pane {{
                border: 3px solid {self.colors['panel_border']};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A0000, 
                    stop:0.5 #330000, 
                    stop:1 #1A0000);
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {get_random_button_color(self.current_era)}, 
                    stop:0.5 {get_random_button_color(self.current_era)}CC, 
                    stop:1 {get_random_button_color(self.current_era)});
                color: #FFFFFF;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                font-weight: bold;
                font-size: 14px;
                text-transform: uppercase;
                border: 2px solid #FF0000;
            }}
            QTabBar::tab:selected {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF0000, 
                    stop:0.5 #CC0000, 
                    stop:1 #990000);
                color: #FFFFFF;
                border: 2px solid #FFFF00;
            }}
            QLineEdit {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A0000, 
                    stop:0.5 #330000, 
                    stop:1 #1A0000);
                color: {get_random_button_color(self.current_era)};
                border: 2px solid #FF0000;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }}
            QComboBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #990000, 
                    stop:0.5 #CC0000, 
                    stop:1 #990000);
                color: #FFFFFF;
                border: 2px solid #FF0000;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        
        # Оновлюємо кольори кнопок
        self.update_button_colors()
        
        print(f"🔄 Кольори оновлено для епохи: {self.current_era.value}")
        
    def setup_klingon_interface(self):
        """Створення Klingon інтерфейсу"""
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Основний layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Ліва панель - Klingon стиль
        left_panel = self.create_klingon_left_panel()
        main_layout.addWidget(left_panel)
        
        # Центральна область
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(10, 10, 10, 10)
        
        # Верхня панель з blade елементами
        top_panel = self.create_klingon_top_panel()
        center_layout.addWidget(top_panel)
        
        # Основний контент
        content = self.create_main_content()
        center_layout.addWidget(content)
        
        main_layout.addWidget(center_area)
        
        # Права панель - Klingon стиль
        right_panel = self.create_klingon_right_panel()
        main_layout.addWidget(right_panel)
        
    def create_klingon_left_panel(self):
        """Створення лівої Klingon панелі"""
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Верхній blade елемент
        top_blade = KlingonBlade("top", get_random_button_color(self.current_era), 60)
        left_layout.addWidget(top_blade)
        
        # Вибір епохи
        era_panel = KlingonPanel("ERA SELECT", "#990000", True)
        self.era_combo = QComboBox()
        self.era_combo.addItems([era.value for era in LCARSEra])
        current_index = list(LCARSEra).index(self.current_era)
        self.era_combo.setCurrentIndex(current_index)
        self.era_combo.currentTextChanged.connect(self.change_era)
        era_panel.add_widget(self.era_combo)
        left_layout.addWidget(era_panel)
        
        # Кнопки управління
        buttons_panel = KlingonPanel("TACTICAL COMMAND", "#CC0000", True)
        buttons = [
            ("PRIME TARGET", "primary"),
            ("ALTERNATE VECTOR", "honor"),
            ("NEXUS POINT", "secondary"),
            ("ENGAGE SHIELDS", "primary"),
            ("RED ALERT", "alert"),
            ("RESET SYSTEM", "honor")
        ]
        
        for text, btn_type in buttons:
            btn = KlingonButton(text, btn_type)
            
            if text == "ENGAGE SHIELDS":
                btn.clicked.connect(self.toggle_shields)
            elif text == "RED ALERT":
                btn.clicked.connect(lambda: self.temporal_alert.emit("Klingon alert!"))
            elif text == "RESET SYSTEM":
                btn.clicked.connect(self.return_to_main)
                
            buttons_panel.add_widget(btn)
            
        left_layout.addWidget(buttons_panel)
        
        # Нижній blade елемент
        bottom_blade = KlingonBlade("bottom", get_random_button_color(self.current_era), 60)
        left_layout.addWidget(bottom_blade)
        
        left_layout.addStretch()
        
        return left_panel
        
    def create_klingon_right_panel(self):
        """Створення правої Klingon панелі"""
        right_panel = QWidget()
        right_panel.setFixedWidth(200)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Верхній blade елемент
        top_blade = KlingonBlade("top", get_random_button_color(self.current_era), 40)
        right_layout.addWidget(top_blade)
        
        # Статусна панель
        status_panel = KlingonPanel("BATTLE STATUS", "#660000", True)
        
        status_items = [
            "WEAPONS READY",
            "SHIELDS UP", 
            "ENGINES HOT",
            "CREW ALERT",
            "TARGET LOCKED"
        ]
        
        for status in status_items:
            status_label = QLabel(status)
            status_label.setStyleSheet(f"""
                QLabel {{
                    color: {get_random_button_color(self.current_era)};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 5px;
                    border-bottom: 1px solid #FF0000;
                    text-transform: uppercase;
                }}
            """)
            status_panel.add_widget(status_label)
            
        right_layout.addWidget(status_panel)
        
        # Нижній blade елемент
        bottom_blade = KlingonBlade("bottom", get_random_button_color(self.current_era), 40)
        right_layout.addWidget(bottom_blade)
        
        right_layout.addStretch()
        
        return right_panel
        
    def create_klingon_top_panel(self):
        """Створення верхньої Klingon панелі"""
        top_panel = QWidget()
        top_panel.setFixedHeight(100)
        top_layout = QHBoxLayout(top_panel)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Лівий blade
        left_blade = KlingonBlade("left", get_random_button_color(self.current_era), 80)
        top_layout.addWidget(left_blade)
        
        # Заголовок
        title = QLabel(f"KLINGON EMPIRE - {self.current_era.value}")
        title.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #CC0000, 
                    stop:0.5 #FF0000, 
                    stop:1 #CC0000);
                font-size: 28px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 4px;
                padding: 20px;
                border: 3px solid #FF0000;
                border-radius: 10px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(title)
        
        # Правий blade
        right_blade = KlingonBlade("right", get_random_button_color(self.current_era), 80)
        top_layout.addWidget(right_blade)
        
        return top_panel
        
    def create_main_content(self):
        """Створення основного контенту"""
        content = QWidget()
        content.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1A0000, 
                    stop:0.5 #330000, 
                    stop:1 #1A0000);
                border: 3px solid #FF0000;
                border-radius: 15px;
            }}
        """)
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Статус
        self.temporal_status = QLabel("TEMPORAL CORE: BATTLE READY")
        self.temporal_status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.current_era)};
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                border: 3px solid #FF0000;
                border-radius: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #330000, 
                    stop:0.5 #660000, 
                    stop:1 #330000);
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
            ("PRIME", "PRIME TARGET ACQUIRED", 
             "Target locked\nWeapons charged\nVictory imminent"),
            ("ALTERNATE", "ALTERNATE VECTORS", 
             "Scanning alternate timelines\n0 threats detected\nAll systems optimal"),
            ("NEXUS", "NEXUS COORDINATES", 
             "Nexus stability: OPTIMAL\nTemporal coordinates locked\nReady for battle")
        ]
        
        for tab_name, status_text, info_text in tabs_data:
            tab = QWidget()
            layout = QVBoxLayout()
            
            status = QLabel(status_text)
            status.setStyleSheet(f"""
                QLabel {{
                    color: {get_random_button_color(self.current_era)};
                    font-size: 16px;
                    font-weight: bold;
                    padding: 10px;
                    text-transform: uppercase;
                    border: 2px solid #FF0000;
                    border-radius: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #330000, 
                        stop:0.5 #660000, 
                        stop:1 #330000);
                }}
            """)
            layout.addWidget(status)
            
            info = QLabel(info_text)
            info.setStyleSheet(f"""
                QLabel {{
                    color: {get_random_button_color(self.current_era)};
                    font-size: 14px;
                    padding: 15px;
                    border: 1px solid #FF0000;
                    border-radius: 8px;
                    background-color: #1A0000;
                }}
            """)
            layout.addWidget(info)
            
            tab.setLayout(layout)
            self.timeline_monitor.addTab(tab, tab_name)
            
    def add_controls(self, layout):
        """Додавання елементів управління"""
        controls = [
            ("Target:", "PRIME TARGET LOCKED"),
            ("Shields:", "100%"),
            ("Weapons:", "CHARGED"),
            ("Engine:", "WARP FACTOR 9")
        ]
        
        for label_text, placeholder in controls:
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            if placeholder in ["100%", "CHARGED", "WARP FACTOR 9"]:
                field.setReadOnly(True)
            layout.addRow(QLabel(label_text), field)
            
    def change_era(self, era_name):
        """Змінити епоху"""
        # Знаходимо епоху за назвою
        for era in LCARSEra:
            if era.value == era_name:
                self.current_era = era
                self.load_era_palette()
                self.update_colors()
                break
                
    def update_button_colors(self):
        """Оновлення кольорів кнопок"""
        for btn in self.findChildren(KlingonButton):
            btn.setup_klingon_style()
            
        # Оновлення кольорів blade елементів
        for blade in self.findChildren(KlingonBlade):
            blade.color = QColor(get_random_button_color(self.current_era))
            blade.update()
            
    def toggle_shields(self):
        """Перемикання щитів"""
        self.temporal_status.setText("TEMPORAL CORE: SHIELDS ENGAGED")
        
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
        self.temporal_status.setText(f"KLINGON ALERT: {message}")
        self.temporal_status.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                border: 3px solid #FFFF00;
                border-radius: 20px;
                text-transform: uppercase;
                letter-spacing: 2px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FF0000, 
                    stop:0.5 #CC0000, 
                    stop:1 #FF0000);
            }
        """)

def main():
    app = QApplication(sys.argv)
    window = KlingonInterface()
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
