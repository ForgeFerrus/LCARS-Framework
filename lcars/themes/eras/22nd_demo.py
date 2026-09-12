#!/usr/bin/env python3
"""
LCARS 22nd Century Demo (Enterprise NX-01 Style)
Демонстрація стилю 22-го століття на основі JSON конфігурації
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import json
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

class LCARS22Button(QPushButton):
    """Кнопка у стилі 22-го століття"""
    
    def __init__(self, text="", button_type="standard", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю кнопки"""
        styles = {
            "standard": """
                QPushButton {
                    background-color: #1E3A8A;
                    color: #E0E0FF;
                    border: 2px solid #4C4C7A;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #2C4B9E;
                    border-color: #6C6C9A;
                }
                QPushButton:pressed {
                    background-color: #3B5DB8;
                }
            """,
            "alert": """
                QPushButton {
                    background-color: #8A1E1E;
                    color: #FFE0E0;
                    border: 2px solid #A04C4C;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #9E2C2C;
                    border-color: #B06C6C;
                }
                QPushButton:pressed {
                    background-color: #B83B3B;
                }
            """,
            "primary": """
                QPushButton {
                    background-color: #1E4A8A;
                    color: #E0E0FF;
                    border: 2px solid #4C7A7A;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                QPushButton:hover {
                    background-color: #2C5E9E;
                    border-color: #6C9A9A;
                }
                QPushButton:pressed {
                    background-color: #3B7AB8;
                }
            """
        }
        
        self.setStyleSheet(styles.get(self.button_type, styles["standard"]))
        self.setMinimumWidth(120)

class LCARS22Panel(QFrame):
    """Панель у стилі 22-го століття"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю панелі"""
        self.setStyleSheet("""
            QFrame {
                background-color: #0A0A1E;
                border: 2px solid #4C4C7A;
                border-radius: 4px;
            }
        """)
        self.setMinimumHeight(120)

class LCARS22Display(QFrame):
    """Дисплей у стилі 22-го століття"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_style()
        
    def setup_style(self):
        """Налаштування стилю дисплея"""
        self.setStyleSheet("""
            QFrame {
                background-color: #0A0A14;
                border: 1px solid #2A2A3E;
                border-radius: 2px;
            }
        """)
        self.setMinimumHeight(80)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Створення головного вікна
    window = QWidget()
    window.setWindowTitle("LCARS 22nd Century Demo - Enterprise NX-01")
    window.setStyleSheet("background-color: #050510;")
    window.resize(900, 700)
    
    # Головний layout
    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    
    # Заголовок
    title_label = QLabel("ENTERPRISE NX-01 - LCARS SYSTEM")
    title_label.setStyleSheet("""
        QLabel {
            color: #E0E0FF;
            background-color: #1E3A8A;
            border: 2px solid #4C4C7A;
            border-radius: 4px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
        }
    """)
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(title_label)
    
    # Верхня панель керування
    top_panel = LCARS22Panel("COMMAND INTERFACE")
    top_layout = QHBoxLayout(top_panel)
    top_layout.setContentsMargins(10, 10, 10, 10)
    
    # Кнопки керування
    btn_helm = LCARS22Button("HELM", "primary")
    btn_tactical = LCARS22Button("TACTICAL", "alert")
    btn_sensors = LCARS22Button("SENSORS", "standard")
    btn_comms = LCARS22Button("COMMUNICATIONS", "standard")
    
    top_layout.addWidget(btn_helm)
    top_layout.addWidget(btn_tactical)
    top_layout.addWidget(btn_sensors)
    top_layout.addWidget(btn_comms)
    top_layout.addStretch()
    
    main_layout.addWidget(top_panel)
    
    # Основний дисплей
    main_display = LCARS22Display("MAIN DISPLAY")
    display_layout = QVBoxLayout(main_display)
    display_layout.setContentsMargins(15, 15, 15, 15)
    
    display_label = QLabel("STATUS: ALL SYSTEMS OPERATIONAL")
    display_label.setStyleSheet("""
        QLabel {
            color: #00FF00;
            background-color: transparent;
            font-weight: bold;
            font-size: 14px;
            font-family: 'Courier New', monospace;
        }
    """)
    display_layout.addWidget(display_label)
    
    main_layout.addWidget(main_display)
    
    # Нижня панель статусу
    status_panel = LCARS22Panel("SYSTEM STATUS")
    status_layout = QHBoxLayout(status_panel)
    status_layout.setContentsMargins(10, 10, 10, 10)
    
    # Індикатори статусу
    status_reactor = QLabel("REACTOR: ONLINE")
    status_reactor.setStyleSheet("""
        QLabel {
            color: #00FF00;
            background-color: transparent;
            font-weight: bold;
            font-size: 11px;
        }
    """)
    
    status_shields = QLabel("SHIELDS: 100%")
    status_shields.setStyleSheet("""
        QLabel {
            color: #00FF00;
            background-color: transparent;
            font-weight: bold;
            font-size: 11px;
        }
    """)
    
    status_weapons = QLabel("WEAPONS: STANDBY")
    status_weapons.setStyleSheet("""
        QLabel {
            color: #FFFF00;
            background-color: transparent;
            font-weight: bold;
            font-size: 11px;
        }
    """)
    
    status_layout.addWidget(status_reactor)
    status_layout.addStretch()
    status_layout.addWidget(status_shields)
    status_layout.addStretch()
    status_layout.addWidget(status_weapons)
    status_layout.addStretch()
    
    main_layout.addWidget(status_panel)
    
    # Кнопка виходу
    exit_btn = LCARS22Button("EXIT", "alert")
    exit_btn.clicked.connect(app.quit)
    main_layout.addWidget(exit_btn)
    
    window.show()
    sys.exit(app.exec())
