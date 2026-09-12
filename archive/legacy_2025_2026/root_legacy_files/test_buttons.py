#!/usr/bin/env python3
"""
Простий тест кнопок
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt

try:
    from lcars.themes.theme import (
        KlingonTriangleButton,
        RomulanTrapezoidButton,
        RomulanTrapezoidButton2,
        CardassianHexagonButton
    )
    print("✅ Імпорт кнопок успішний!")
except ImportError as e:
    print(f"❌ Помилка імпорту: {e}")
    sys.exit(1)

class TestButtons(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Тест Фракційних Кнопок")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Клінгонські кнопки
        klingon_layout = QHBoxLayout()
        klingon_layout.addWidget(KlingonTriangleButton("КОМАНДА", "black_circle"))
        klingon_layout.addWidget(KlingonTriangleButton("1", "text_in_circle"))
        klingon_layout.addWidget(KlingonTriangleButton("ЗБРОЯ", "black_circle"))
        main_layout.addWidget(QWidget().setLayout(klingon_layout))
        
        # Ромуланські кнопки
        romulan_layout = QHBoxLayout()
        romulan_layout.addWidget(RomulanTrapezoidButton("ТАЛ ШИАР"))
        romulan_layout.addWidget(RomulanTrapezoidButton2("ПЛАЗМА"))
        main_layout.addWidget(QWidget().setLayout(romulan_layout))
        
        # Кардасіанські кнопки
        cardassian_layout = QHBoxLayout()
        cardassian_layout.addWidget(CardassianHexagonButton("ОБСЛУГА"))
        cardassian_layout.addWidget(CardassianHexagonButton("БАЗА"))
        main_layout.addWidget(QWidget().setLayout(cardassian_layout))
        
        self.setStyleSheet("background-color: #000000;")

def main():
    app = QApplication(sys.argv)
    window = TestButtons()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
