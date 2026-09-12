"""
ЦЕНТРАЛЬНИЙ МОДУЛЬ КЕРУВАННЯ LCARS :: АВТОНОМНИЙ ЗАПУСК
Архітектура TITAN v5.0
ПРОТОКОЛ: ПРЯМИЙ ЗВ'ЯЗОК
"""
import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt

# Додавання кореневої папки проекту до шляхів імпорту
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.ui.panels.central import CentralPanel
from lcars.themes.lcars_palette import LCARSEra, setup_lcars_font
from lcars.core.board_computer import BoardComputer

def main():
    # Примусова підтримка UTF-8 для символів LCARS (тільки Windows)
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)

    app = QApplication(sys.argv)
    setup_lcars_font()

    # Ініціалізація ядра системи (Бортовий Комп'ютер)
    system = BoardComputer()
    system.start()

    # Створення головного вікна для відображення CentralPanel
    window = QMainWindow()
    window.setWindowTitle("LCARS :: CENTRAL COMMAND :: TITAN v5.0")
    
    # Справжній інтерфейс LCARS має бути безрамковий
    window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    # Задаємо чорний фон додатку для автентичності
    window.setStyleSheet("background-color: black;")
    
    # Ініціалізація CentralPanel з реальним ядром системи
    central = CentralPanel(system=system, era=LCARSEra.LCARS_25TH)
    
    window.setCentralWidget(central)
    
    # Максимальний масштаб для повного занурення
    window.showFullScreen()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()