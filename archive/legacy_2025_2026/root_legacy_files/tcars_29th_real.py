#!/usr/bin/env python3
"""
TCARS 29th Century - Справжній LCARS інтерфейс
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout,
                           QGridLayout)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_random_button_color

class TCARS29thCentury(QMainWindow):
    """
    29th Century LCARS Interface - справжній стиль
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
        # Оновлюємо кольори кнопок
        self.update_button_colors()
        
        # Оновлюємо основний стиль
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QLabel {{
                color: {get_random_button_color(self.era)};
                background-color: transparent;
                font-family: 'Arial', sans-serif;
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
            }}
        """)
        
        print(f"🔄 Кольори оновлено")
        
    def setup_lcars_interface(self):
        """Створення справжнього LCARS інтерфейсу"""
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Основний layout
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Ліва панель - характерний LCARS елемент
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Центральна область
        center_area = QWidget()
        center_layout = QVBoxLayout(center_area)
        center_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок
        header = self.create_header()
        center_layout.addWidget(header)
        
        # Основний контент
        content = self.create_main_content()
        center_layout.addWidget(content)
        
        main_layout.addWidget(center_area)
        
    def create_left_panel(self):
        """Створення лівої панелі в стилі LCARS"""
        left_panel = QWidget()
        left_panel.setFixedWidth(120)
        left_panel.setStyleSheet(f"""
            QWidget {{
                background-color: {get_random_button_color(self.era)};
                border: none;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Верхній кутовий елемент
        corner_top = QWidget()
        corner_top.setFixedHeight(60)
        corner_top.setStyleSheet(f"""
            QWidget {{
                background-color: {get_random_button_color(self.era)};
                border: none;
            }}
        """)
        left_layout.addWidget(corner_top)
        
        # Кнопки управління
        self.create_lcars_buttons(left_layout)
        
        # Нижній кутовий елемент
        corner_bottom = QWidget()
        corner_bottom.setFixedHeight(80)
        corner_bottom.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors['background']};
                border: none;
            }}
        """)
        left_layout.addWidget(corner_bottom)
        
        left_layout.addStretch()
        
        return left_panel
        
    def create_lcars_buttons(self, layout):
        """Створення LCARS кнопок"""
        buttons_data = [
            ("PRIME", 0),
            ("ALTERNATE", 1), 
            ("NEXUS", 2),
            ("SHIELDS", 3),
            ("ALERT", 4),
            ("RESET", 5)
        ]
        
        for text, index in buttons_data:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['background']};
                    color: {get_random_button_color(self.era)};
                    border: 2px solid {get_random_button_color(self.era)};
                    border-radius: 0px;
                    font-weight: bold;
                    font-size: 12px;
                    text-align: left;
                    padding-left: 10px;
                }}
                QPushButton:hover {{
                    background-color: {get_random_button_color(self.era)};
                    color: {self.colors['background']};
                }}
                QPushButton:pressed {{
                    background-color: {get_random_button_color(self.era)};
                }}
            """)
            
            # Підключаємо обробники
            if index == 3:  # SHIELDS
                btn.clicked.connect(self.toggle_shields)
            elif index == 4:  # ALERT
                btn.clicked.connect(lambda: self.temporal_alert.emit("Temporal anomaly!"))
            elif index == 5:  # RESET
                btn.clicked.connect(self.return_to_main)
                
            layout.addWidget(btn)
            
    def create_header(self):
        """Створення заголовка"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QWidget {{
                background-color: {get_random_button_color(self.era)};
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("TCARS 29th CENTURY")
        title.setStyleSheet(f"""
            QLabel {{
                color: {self.colors['background']};
                font-size: 28px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 3px;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        return header
        
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
        # Prime Timeline
        prime_tab = QWidget()
        prime_layout = QVBoxLayout()
        
        prime_status = QLabel("PRIME TIMELINE INTEGRITY: 100%")
        prime_status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                text-transform: uppercase;
            }}
        """)
        prime_layout.addWidget(prime_status)
        
        prime_info = QLabel("No temporal incursions detected\nAll timelines stable\nQuantum coherence: 99.8%")
        prime_info.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 14px;
                padding: 10px;
                border: 1px solid {self.colors['panel_border']};
                border-radius: 5px;
            }}
        """)
        prime_layout.addWidget(prime_info)
        
        prime_tab.setLayout(prime_layout)
        self.timeline_monitor.addTab(prime_tab, "PRIME")
        
        # Alternate Timelines
        alt_tab = QWidget()
        alt_layout = QVBoxLayout()
        
        alt_status = QLabel("ALTERNATE TIMELINES: SCANNING")
        alt_status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                text-transform: uppercase;
            }}
        """)
        alt_layout.addWidget(alt_status)
        
        alt_info = QLabel("0 alternate timelines detected\nParadox level: 0.0%\nTemporal stability: OPTIMAL")
        alt_info.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 14px;
                padding: 10px;
                border: 1px solid {self.colors['panel_border']};
                border-radius: 5px;
            }}
        """)
        alt_layout.addWidget(alt_info)
        
        alt_tab.setLayout(alt_layout)
        self.timeline_monitor.addTab(alt_tab, "ALTERNATE")
        
        # Temporal Nexus
        nexus_tab = QWidget()
        nexus_layout = QVBoxLayout()
        
        nexus_status = QLabel("TEMPORAL NEXUS: STABLE")
        nexus_status.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                text-transform: uppercase;
            }}
        """)
        nexus_layout.addWidget(nexus_status)
        
        nexus_info = QLabel("Nexus stability: OPTIMAL\nChroniton flow: NORMAL\nTime displacement: 0.00ms")
        nexus_info.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color(self.era)};
                font-size: 14px;
                padding: 10px;
                border: 1px solid {self.colors['panel_border']};
                border-radius: 5px;
            }}
        """)
        nexus_layout.addWidget(nexus_info)
        
        nexus_tab.setLayout(nexus_layout)
        self.timeline_monitor.addTab(nexus_tab, "NEXUS")
        
    def add_controls(self, layout):
        """Додавання елементів управління"""
        # Chronometric Sensor
        chronometric = QLineEdit()
        chronometric.setPlaceholderText("Quantum Chronometric Reading")
        layout.addRow("Chronometric:", chronometric)
        
        # Timeline Stability
        stability = QLineEdit()
        stability.setPlaceholderText("100%")
        stability.setReadOnly(True)
        layout.addRow("Stability:", stability)
        
        # Temporal Coefficient
        coefficient = QLineEdit()
        coefficient.setPlaceholderText("1.0000")
        coefficient.setReadOnly(True)
        layout.addRow("Coefficient:", coefficient)
        
    def update_button_colors(self):
        """Оновлення кольорів кнопок"""
        # Оновлюємо кольори всіх кнопок
        for btn in self.findChildren(QPushButton):
            if btn.text() in ["PRIME", "ALTERNATE", "NEXUS", "SHIELDS", "ALERT", "RESET"]:
                new_color = get_random_button_color(self.era)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.colors['background']};
                        color: {new_color};
                        border: 2px solid {new_color};
                        border-radius: 0px;
                        font-weight: bold;
                        font-size: 12px;
                        text-align: left;
                        padding-left: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {new_color};
                        color: {self.colors['background']};
                    }}
                """)
                
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
