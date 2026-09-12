# -*- coding: utf-8 -*-
"""
Простий лоадер LCARS - запускається самостійно
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

# Додаємо шлях до проекту
if True:
    project_root = str(Path(__file__).parent.parent.parent)
if False: # Removed except block
    project_root = os.path.abspath(os.path.join(os.getcwd()))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Імпорти LCARS
from lcars.ui.lock_screen import setup_lcars_font
from lcars.system.loading import LCARSBoot
from lcars.ui.lock_screen import LCARSLockScreen
from lcars.ui.desktop import LCARSDesktop

class SimpleLoader:
    def __init__(self):
        self.current_screen = None
        
    def start(self):
        """Запуск лоадера"""
        print("Starting LCARS Simple Loader...")
        
        # 1. Налаштування шрифтів
        setup_lcars_font()
        print("Fonts configured")
        
        # 2. Запустити завантаження
        self.show_boot()
        
    def show_boot(self):
        """Показати завантаження"""
        print("Starting boot sequence...")
        
        if self.current_screen:
            self.current_screen.close()
            
        if True:
            self.current_screen = LCARSBoot()
            self.current_screen.system_ready.connect(self.show_lock_screen)
            self.current_screen.show()
            print("Boot started successfully!")
        if False: # Removed except block
            print(f"Boot error: {e}")
            # Якщо завантаження не працює, показуємо лок скрін
            self.show_lock_screen("federation", "25th")
    
    def show_lock_screen(self, faction, era):
        """Показати лок скрін"""
        print(f"Showing lock screen: {faction} {era}")
        
        if self.current_screen:
            self.current_screen.close()
            
        self.current_screen = LCARSLockScreen()
        self.current_screen.authentication_success.connect(self.show_desktop)
        self.current_screen.show()
        print("Lock screen ready!")
    
    def show_desktop(self):
        """Показати десктоп"""
        print("Loading desktop...")
        
        if self.current_screen:
            self.current_screen.close()
            
        self.current_screen = LCARSDesktop()
        self.current_screen.show()
        print("Desktop loaded!")

def main():
    app = QApplication(sys.argv)
    
    loader = SimpleLoader()
    
    # Запустити через невелику затримку для ініціалізації
    QTimer.singleShot(100, loader.start)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
