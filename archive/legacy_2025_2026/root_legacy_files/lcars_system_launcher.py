"""
LCARS System Launcher
Керує всім потоком: вхід → блокування → робочий стіл
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtCore import pyqtSignal, QObject

# Додаємо шлях до проекту
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.ui.loading import LCARSBootScreen
from lcars.ui.lock_screen import LCARSLockScreen

class LCARSSystemLauncher(QMainWindow):
    """Головний системний лаунчер - керує всім потоком"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS System")
        self.setGeometry(0, 0, 1200, 800)
        
        # Стек екранів
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Дані поточної сесії
        self.current_faction = None
        self.current_era = None
        
        # Створюємо екрани
        self.setup_screens()
        
        # Показуємо стартовий екран
        self.show_boot_screen()
        
    def setup_screens(self):
        """Створити всі екрани системи"""
        # 1. Екран завантаження з вибором фракції/епохи
        self.boot_screen = LCARSBootScreen()
        self.boot_screen.system_ready.connect(self.on_faction_selected)
        self.stack.addWidget(self.boot_screen)
        
        # 2. Екран блокування (створюється динамічно)
        self.lock_screen = None
        
        # 3. Робочий стіл (створюється динамічно)
        self.desktop_screen = None
        
    def show_boot_screen(self):
        """Показати екран завантаження"""
        print("🚀 Starting LCARS Boot Sequence...")
        self.stack.setCurrentWidget(self.boot_screen)
        
    def on_faction_selected(self, faction, era):
        """Обробити вибір фракції та епохи"""
        print(f"✅ Selected: {faction} {era}")
        self.current_faction = faction
        self.current_era = era
        
        # Показати екран блокування
        self.show_lock_screen(faction, era)
        
    def show_lock_screen(self, faction, era):
        """Показати екран блокування для вибраної епохи"""
        print(f"🔒 Loading lock screen for {faction} {era}")
        
        try:
            # Видаляємо попередній екран блокування якщо є
            if self.lock_screen:
                self.stack.removeWidget(self.lock_screen)
                self.lock_screen.deleteLater()
                
            # Створюємо новий екран блокування
            self.lock_screen = LCARSLockScreen(faction, era)
            self.lock_screen.access_granted.connect(self.on_access_granted)
            self.lock_screen.back_requested.connect(self.show_boot_screen)
            
            self.stack.addWidget(self.lock_screen)
            self.stack.setCurrentWidget(self.lock_screen)
            
        except Exception as e:
            print(f"❌ Error creating lock screen: {e}")
            self.show_boot_screen()
            
    def on_access_granted(self):
        """Обробити успішний вхід в систему"""
        print(f"✅ Access granted to {self.current_faction} {self.current_era}")
        
        # Показати робочий стіл
        self.show_desktop(self.current_faction, self.current_era)
        
    def show_desktop(self, faction, era):
        """Показати робочий стіл для вибраної епохи"""
        print(f"🖥️ Loading desktop for {faction} {era}")
        
        try:
            # Видаляємо попередній робочий стіл якщо є
            if self.desktop_screen:
                self.stack.removeWidget(self.desktop_screen)
                self.desktop_screen.deleteLater()
                
            # Створюємо робочий стіл
            self.desktop_screen = self.create_desktop(faction, era)
            
            if self.desktop_screen:
                self.stack.addWidget(self.desktop_screen)
                self.stack.setCurrentWidget(self.desktop_screen)
            else:
                print(f"❌ No desktop available for {faction} {era}")
                self.show_boot_screen()
                
        except Exception as e:
            print(f"❌ Error creating desktop: {e}")
            self.show_boot_screen()
            
    def create_desktop(self, faction, era):
        """Створити робочий стіл для конкретної фракції/епохи"""
        # Тут буде логіка створення відповідного робочого столу
        # Наприклад, імпорт з lcars.ui.desktop або lcars.ui.factions.federation.era_22nd.desktop
        
        try:
            if faction == "federation":
                if era == "22nd":
                    from lcars.ui.factions.federation.era_22nd.desktop import Desktop22nd
                    return Desktop22nd()
                elif era == "24th":
                    from lcars.ui.desktop import LCARSDesktop  # Загальний робочий стіл
                    return LCARSDesktop(faction, era)
                elif era == "25th":
                    from lcars.ui.desktop import LCARSDesktop
                    return LCARSDesktop(faction, era)
                # Додати інші епохи...
                
            # Fallback - загальний робочий стіл
            from lcars.ui.desktop import LCARSDesktop
            return LCARSDesktop(faction, era)
            
        except ImportError as e:
            print(f"❌ Desktop import error: {e}")
            return None
            
    def logout(self):
        """Вийти з системи - повернутися на екран завантаження"""
        print("🔄 Logging out...")
        self.current_faction = None
        self.current_era = None
        self.show_boot_screen()


def main():
    """Запуск LCARS системи"""
    app = QApplication(sys.argv)
    app.setApplicationName("LCARS System")
    
    # Створюємо головне вікно системи
    launcher = LCARSSystemLauncher()
    launcher.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()