#!/usr/bin/env python3
"""
QML демо фракційних LCARS інтерфейсів з ShapePath кнопками
"""

import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, QUrl
from PySide6.QtCore import QDir

# Імпортуємо палітри
try:
    from lcars.themes.theme import get_faction_palette, FactionEra
    print("✅ Імпорт палітр успішний!")
except ImportError as e:
    print(f"❌ Помилка імпорту палітр: {e}")
    sys.exit(1)

class QMLBridge(QObject):
    def __init__(self):
        super().__init__()
        self.current_faction_era = FactionEra.KLINGON_24TH
        
    @Slot(str)
    def get_faction_color(self, faction_era):
        """Повертає головний колір для фракції"""
        try:
            era = FactionEra(faction_era)
            palette = get_faction_palette(era)
            return palette['button_colors'][0]  # Перший колір - головний
        except:
            return "#660000"  # Клінгонський червоний за замовчуванням
    
    @Slot(str)
    def get_accent_color(self, faction_era):
        """Повертає акцентний колір для фракції"""
        try:
            era = FactionEra(faction_era)
            palette = get_faction_palette(era)
            return palette['button_colors'][1] if len(palette['button_colors']) > 1 else palette['button_colors'][0]
        except:
            return "#FFD700"  # Золотий за замовчуванням
    
    @Slot()
    def exit_system(self):
        sys.exit(0)
    
    @Slot(str)
    def button_clicked(self, button_name):
        print(f"Button clicked: {button_name}")

def main():
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    bridge = QMLBridge()
    
    # Додаємо шлях до QML компонентів
    engine.addImportPath(QDir.currentPath() + "/lcars/qml")
    
    # Передаємо об'єкт bridge у QML
    engine.rootContext().setContextProperty("bridge", bridge)
    
    # Завантажуємо QML файл
    engine.load(QUrl.fromLocalFile("qml_faction_demo.qml"))
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
