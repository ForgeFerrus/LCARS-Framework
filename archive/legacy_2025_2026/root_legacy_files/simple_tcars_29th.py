#!/usr/bin/env python3
"""
Простий запуск TCARS 29th Century без зайвих імпортів
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_random_button_color

class TCARS29thCentury(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCARS 29th Century (Universe Class)")
        
        # Підключаємо палітру 29го століття
        self.palette = get_era_palette(LCARSEra.TCARS_29TH)
        self.era = LCARSEra.TCARS_29TH
        
        # Початковий стиль
        current_color = get_random_button_color(self.era)
        self.setStyleSheet(f"background-color: {self.palette['background']}; color: {current_color};")
        
        # Створюємо інтерфейс
        layout = QVBoxLayout()
        label = QLabel("TCARS 29th Century\nUniverse Class Interface\n(Future Era)")
        label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(label)
        
        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Таймер для зміни кольорів
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(2000)  # Зміна кожні 2 секунди
        
    def update_colors(self):
        """Оновлює кольори за алгоритмом"""
        # Генеруємо новий випадковий колір
        current_color = get_random_button_color(self.era)
        
        # Оновлюємо інтерфейс
        self.setStyleSheet(f"background-color: {self.palette['background']}; color: {current_color};")
        print(f"🔄 Колір змінено на: {current_color}")

def main():
    app = QApplication(sys.argv)
    window = TCARS29thCentury()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
