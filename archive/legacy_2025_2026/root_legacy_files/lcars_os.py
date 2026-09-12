"""
LCARS Auto-Launcher - Використовує існуючий lock screen
Запускає lock_screen.py автоматично
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow

project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class LCARSSystem(QMainWindow):
    """Main LCARS System Launcher"""
    
    def __init__(self):
        super().__init__()
        # Одразу запускаємо lock screen, без проміжних екранів
        self.start_boot()
    
    def start_boot(self):
        """Start with existing lock screen"""
        from lcars.ui.lock_screen import LCARSLockScreen
        self.boot_screen = LCARSLockScreen()
        # Lock screen вже має логіку переходу на desktop після авторизації
        self.boot_screen.show()
        # Ховаємо launcher одразу
        self.hide()


def main():
    app = QApplication(sys.argv)
    
    # Запускаємо LCARS через lock screen
    launcher = LCARSSystem()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


def main():
    app = QApplication(sys.argv)
    
    # Start with boot sequence
    launcher = LCARSSystem()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()