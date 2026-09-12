
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, QTimer, QObject, pyqtSlot
from PyQt6.QtGui import QIcon

# Контролер для взаємодії з QML
class LCARSController(QObject):  
    def __init__(self):
        super().__init__()
    
    @pyqtSlot(str)
    def button_clicked(self, button_name):
        print(f"◤ BUTTON PRESSED: {button_name}")
        
    @pyqtSlot()
    def exit_system(self):
        print("◤ SYSTEM SHUTDOWN INITIATED")
        QApplication.quit()

def main():
    # Створення QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("LCARS System")
    app.setOrganizationName("Starfleet Command")
    
    # Контролер для QML
    controller = LCARSController()
    
    # Створення QML движка
    engine = QQmlApplicationEngine()
    
    # Встановлення контексту
    engine.rootContext().setContextProperty("con", controller)
    
    # Шлях до QML файлу
    qml_file = Path(__file__).parent / "tools" / "main.qml"
    
    if not qml_file.exists():
        print(f"◤ ERROR: QML file not found: {qml_file}")
        return 1
    
    # Завантаження QML
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    if not engine.rootObjects():
        print("◤ ERROR: Failed to load QML")
        return 1
    
    print("◤ LCARS SYSTEM INITIALIZED")
    print("◤ ALL SYSTEMS ONLINE")
    print("◤ BRIDGE INTERFACE READY")
    
    # Запуск додатку
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
