#!/usr/bin/env python3
"""
QML демо клінгонської кнопки з ShapePath - без залежностей від PyQt6
"""

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot

class QMLBridge(QObject):
    def __init__(self):
        super().__init__()
        
    @Slot()
    def exit_system(self):
        sys.exit(0)
    
    @Slot(str)
    def button_clicked(self, button_name):
        print(f"Button clicked: {button_name}")
    
    @Slot(str)
    def get_klingon_color(self, era):
        """Повертає колір для клінгонської ери"""
        colors = {
            "klingon_22nd": "#8B0000",  # Темно-червоний
            "klingon_23rd": "#660000",  # Клінгонський червоний
            "klingon_24th": "#990000",  # Яскраво-червоний
            "klingon_25th": "#CC0000"   # Світло-червоний
        }
        return colors.get(era, "#660000")

def main():
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    bridge = QMLBridge()
    
    # Додаємо шлях до QML компонентів
    engine.addImportPath(".")
    
    # Передаємо об'єкт bridge у QML
    engine.rootContext().setContextProperty("bridge", bridge)
    
    # Завантажуємо QML файл
    engine.load("klingon_demo.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
