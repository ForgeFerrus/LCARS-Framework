import sys
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot

# Цей клас буде мостом між Python і QML
class Bridge(QObject):
    @Slot()
    def exit_system(self):
        sys.exit(0)
    
    @Slot(str)
    def button_clicked(self, button_name):
        print(f"Button clicked: {button_name}")
        # Тут можна додати логіку для кожної кнопки

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    
    engine = QQmlApplicationEngine()
    bridge = Bridge()
    
    # Передаємо об'єкт bridge у QML, щоб викликати функції Python з інтерфейсу
    engine.rootContext().setContextProperty("con", bridge)
    
    engine.load("main.qml")
    
    if not engine.rootObjects():
        sys.exit(-1)
        
    sys.exit(app.exec())
