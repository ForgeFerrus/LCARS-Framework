import sys
import os
from pathlib import Path

# Додаємо шлях до модулів проекту
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from lcars.ui.lcars_central import LCARSCentralCommand

def main():
    """Центральна точка входу в систему LCARS Framework"""
    app = QApplication(sys.argv)
    
    # Налаштування стилю додатку
    app.setStyle("Fusion")
    
    # Запуск головного вікна керування
    window = LCARSCentralCommand()
    window.show()
    
    print("🖖 LCARS Framework: Enterprise Edition")
    print(f"📂 Робоча директорія: {project_root}")
    print("🚀 Систему успішно ініціалізовано.")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
