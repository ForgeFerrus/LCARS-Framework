#!/usr/bin/env python3
"""
Authentic LCARS Interface
Без панелей, без рамок, без контурів - тільки справжній LCARS
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt

from lcars.themes.theme_system import get_theme, get_design_style, list_themes


class AuthenticLCARS(QMainWindow):
    """Справжній LCARS інтерфейс без панелей та рамок"""
    
    def __init__(self):
        super().__init__()
        self.current_era = "24th"
        self.current_faction = "starfleet"
        self.current_design = "modern"
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        self.setWindowTitle("LCARS")
        
        # Remove window decorations and make fullscreen
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        # Central widget - чистий без рамок
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Основний контейнер
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        layout.addWidget(self.main_container)
        
    def apply_theme(self):
        # Clear content
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get theme
        theme = get_theme(self.current_era, self.current_faction, self.current_design)
        
        # Apply background - тільки колір, без рамок
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme.background};
            }}
            QLabel {{
                color: {theme.text};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                background: transparent;
            }}
        """)
        
        # Create authentic LCARS layout
        self.create_lcars_layout(theme)
        
    def create_lcars_layout(self, theme):
        """Створити справжній LCARS лейаут"""
        
        # Верхній інформаційний рядок
        self.create_header_row(theme)
        
        # Основна кнопкова секція
        self.create_main_button_section(theme)
        
        # Бічна панель кнопок
        self.create_side_button_section(theme)
        
        # Нижній статусний рядок
        self.create_status_row(theme)
        
    def create_header_row(self, theme):
        """Верхній рядок - тільки текст, без рамок"""
        header = QWidget()
        header.setFixedHeight(40)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 5, 20, 5)
        
        # Era/Faction info
        info = QLabel(f"{self.current_era.upper()} - {self.current_faction.upper()}")
        info.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {theme.button_colors[0]};
        """)
        header_layout.addWidget(info)
        
        header_layout.addStretch()
        
        # Time/status
        status = QLabel("SYSTEM ONLINE")
        status.setStyleSheet(f"""
            font-size: 16px;
            color: {theme.button_colors[1]};
        """)
        header_layout.addWidget(status)
        
        self.main_layout.addWidget(header)
        
    def create_main_button_section(self, theme):
        """Основна секція кнопок - без рамок"""
        main_section = QWidget()
        main_layout = QVBoxLayout(main_section)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(8)
        
        # Рядок основних кнопок
        row1 = QWidget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setSpacing(5)
        
        main_buttons = ["SYSTEMS", "WEAPONS", "SHIELDS", "POWER"]
        for i, btn_text in enumerate(main_buttons):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_button_clicked(text))
            
            # Використовуємо різні кольори для кнопок
            color = theme.button_colors[i % len(theme.button_colors)]
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {theme.background};
                    border: none;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {theme.accent_colors[0]};
                }}
                QPushButton:pressed {{
                    background-color: {theme.accent_colors[1]};
                }}
            """)
            row1_layout.addWidget(btn)
        
        row1_layout.addStretch()
        main_layout.addWidget(row1)
        
        # Другий рядок кнопок
        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setSpacing(5)
        
        secondary_buttons = ["COMM", "SCAN", "NAV", "TACTICAL"]
        for i, btn_text in enumerate(secondary_buttons):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_button_clicked(text))
            
            color = theme.button_colors[(i + 2) % len(theme.button_colors)]
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {theme.background};
                    border: none;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {theme.accent_colors[0]};
                }}
                QPushButton:pressed {{
                    background-color: {theme.accent_colors[1]};
                }}
            """)
            row2_layout.addWidget(btn)
        
        row2_layout.addStretch()
        main_layout.addWidget(row2)
        
        self.main_layout.addWidget(main_section)
        
    def create_side_button_section(self, theme):
        """Бічна панель - вертикальні кнопки без рамок"""
        side_panel = QWidget()
        side_panel.setFixedWidth(200)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(5)
        
        side_buttons = ["MAIN", "DISPLAY", "CONTROL", "STATUS"]
        for btn_text in side_buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_button_clicked(text))
            
            color = theme.button_colors[side_buttons.index(btn_text) % len(theme.button_colors)]
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: {theme.background};
                    border: none;
                    padding: 15px 10px;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: 'Swiss 911', 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: {theme.accent_colors[0]};
                }}
                QPushButton:pressed {{
                    background-color: {theme.accent_colors[1]};
                }}
            """)
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        
        # Додати бічну панель до основного контейнера
        main_with_side = QWidget()
        main_with_layout = QHBoxLayout(main_with_side)
        main_with_layout.setContentsMargins(0, 0, 0, 0)
        main_with_layout.setSpacing(0)
        
        # Додати бічну панель зліва
        main_with_layout.addWidget(side_panel)
        
        # Додати вільний простір
        main_with_layout.addStretch()
        
        self.main_layout.addWidget(main_with_side)
        
    def create_status_row(self, theme):
        """Нижній статусний рядок - без рамок"""
        status_row = QWidget()
        status_row.setFixedHeight(60)
        status_layout = QVBoxLayout(status_row)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        # Alert display
        alert = QLabel("ALL SYSTEMS NOMINAL")
        alert.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {theme.success_color};
            background: transparent;
        """)
        alert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(alert)
        
        # Secondary info
        info = QLabel(f"LCARS INTERFACE - {self.current_design.upper()}")
        info.setStyleSheet(f"""
            font-size: 14px;
            color: {theme.button_colors[2]};
            background: transparent;
        """)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(info)
        
        # Exit button
        exit_btn = QPushButton("EXIT")
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {theme.error_color};
                color: {theme.text};
                border: none;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
            }}
            QPushButton:hover {{
                background-color: {theme.warning_color};
            }}
        """)
        
        # Центрувати exit кнопку
        exit_container = QWidget()
        exit_layout = QHBoxLayout(exit_container)
        exit_layout.addStretch()
        exit_layout.addWidget(exit_btn)
        exit_layout.addStretch()
        
        status_layout.addWidget(exit_container)
        self.main_layout.addWidget(status_row)
        
    def on_button_clicked(self, button_name):
        print(f"LCARS button: {button_name}")


def main():
    app = QApplication(sys.argv)
    lcars = AuthenticLCARS()
    lcars.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
