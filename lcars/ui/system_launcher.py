# -*- coding: utf-8 -*-
"""
LCARS System Launcher/Coordinator
Головний координатор системи - керує boot -> faction selection -> lock screen
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject, pyqtSignal

# Додаємо шлях до проекту
if True:
    project_root = str(Path(__file__).parent.parent.parent)
if False: # Removed except block
    project_root = os.path.abspath(os.path.join(os.getcwd()))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Імпорти компонентів
from lcars.ui.loading import LCARSBoot 
from lcars.ui.lock_screen import setup_lcars_font, LCARSLockScreen
from lcars.ui.desktop import LCARSDesktop

class LCARSSystemCoordinator(QObject):
    """Координатор системи LCARS"""
    
    def __init__(self):
        super().__init__()
        self.current_screen = None
        self.selected_faction = None
        self.selected_faction_data = None
    
    def start_system(self):
        """Запуск системи - єдина система з завантаженням"""
        print("Starting LCARS System...")
        
        # 1. Налаштування шрифтів (ДО показу UI)
        setup_lcars_font()
        print("Fonts configured")
        
        # 2. Ініціалізація системи тем (ДО показу UI)  
        from lcars.themes.lcars_palette import get_era_palette, LCARSEra
        test_palette = get_era_palette(LCARSEra.LCARS_25TH)
        print(f"Theme system ready - {len(test_palette['button_colors'])} colors loaded")
        
        # 3. Запустити завантаження системи (boot) - вхід в систему
        self.show_boot_screen_with_faction_selection()
    
    def show_unified_lcars_system(self):
        """Показати єдину систему LCARS з завантаженням → лок скрін → десктоп"""
        print("Starting Unified LCARS System...")
        
        if self.current_screen:
            self.current_screen.close()
        
        # Створити єдиний екран системи
        from lcars.ui.loading import LCARSBoot
        self.current_screen = LCARSBoot()
        
        # Підключити сигнали для переходів
        self.current_screen.system_ready.connect(self.show_faction_lock_screen_direct)
        
        self.current_screen.show()
        print("Unified LCARS System started!")
    
    def show_lock_screen_direct(self):
        """Показати lock screen напряму з вибором фракцій"""
        print("Showing LCARS Lock Screen with faction selection...")
        
        if self.current_screen:
            self.current_screen.close()
        
        # Завантажити lock screen
        self.current_screen = LCARSLockScreen()
        # Підключити сигнал успішної автентифікації
        self.current_screen.authentication_success.connect(self.show_desktop)
        self.current_screen.show()
    
    def show_boot_screen_with_faction_selection(self):
        """Показати ОДИН boot screen (всі налаштування вже зроблені)"""
        print("Showing Unified Boot Screen...")
        
        if self.current_screen:
            self.current_screen.close()
        
        if True:
            self.current_screen = LCARSBoot()
            # Тепер слухаємо system_ready замість faction_selected
            self.current_screen.system_ready.connect(self.show_faction_lock_screen_direct)
            self.current_screen.show()
            print("Boot screen started successfully!")
        if False: # Removed except block
            print(f"Error starting boot screen: {e}")
            # Якщо завантаження не працює, переходимо напряму до лок скріну
            self.show_lock_screen_direct()
    
    def show_faction_lock_screen_direct(self, faction_key, era_value):
        """Показати автентичний lock screen для обраної фракції та ери"""
        print(f"Loading {faction_key} {era_value} Lock Screen...")
        
        if self.current_screen:
            self.current_screen.close()
        
        # Завантажити автентичний lock screen
        from lcars.ui.lock_screen import LCARSLockScreen
        self.current_screen = LCARSLockScreen()
        # Підключити сигнал успішної автентифікації
        self.current_screen.authentication_success.connect(self.show_desktop)
        
        print(f"Authentic {faction_key} {era_value} interface ready!")
        self.current_screen.show()
    
    def show_faction_lock_screen(self, faction_key, faction_data):
        """Показати автентичний lock screen для обраної фракції"""
        print(f"Loading {faction_data['name']} Lock Screen...")
        
        self.selected_faction = faction_key
        self.selected_faction_data = faction_data
        
        if self.current_screen:
            self.current_screen.close()
        
        # В залежності від фракції завантажуємо відповідний lock screen
        if faction_key == 'federation':
            self.show_federation_lock_screen()
        elif faction_key == 'klingon':
            self.show_klingon_lock_screen()
        elif faction_key == 'romulan':
            self.show_romulan_lock_screen()
        else:
            print(f"Unknown faction: {faction_key}")
    
    def show_federation_lock_screen(self):
        """Показати Federation lock screen"""
        print("Loading Federation Lock Screen...")
        
        # Поки що використовуємо загальний lock screen
        # Потім замінимо на специфічний Federation screen
        from lcars.ui.lock_screen import LCARSLockScreen
        
        self.current_screen = LCARSLockScreen()
        # Встановлюємо Federation faction
        from lcars.ui.lock_screen import StarTrekFaction
        self.current_screen.current_faction = StarTrekFaction.FEDERATION
        self.current_screen.current_era = StarTrekFaction.FEDERATION['era']
        
        # Перебудувати інтерфейс з правильною фракцією
        self.current_screen.rebuild_interface()
    
    def show_klingon_lock_screen(self):
        """Показати Klingon lock screen"""
        print("Loading Klingon Lock Screen...")
        
        # Поки що заглушка - буде створений окремий Klingon screen
        print("Klingon Lock Screen - Coming Soon!")
        print("For now, showing general lock screen...")
        self.show_federation_lock_screen()  # Тимчасово
    
    def show_romulan_lock_screen(self):
        """Показати Romulan lock screen"""
        print("Loading Romulan Lock Screen...")
        
        # Поки що заглушка - буде створений окремий Romulan screen
        print("Romulan Lock Screen - Coming Soon!")
        print("For now, showing general lock screen...")
        self.show_federation_lock_screen()  # Тимчасово
    
    def show_desktop(self):
        """Показати десктоп після успішної автентифікації"""
        print("Authentication successful - Loading desktop...")
        
        if self.current_screen:
            self.current_screen.close()
        
        # Завантажити десктоп
        self.current_screen = LCARSDesktop()
        self.current_screen.show()
        print("LCARS Desktop loaded successfully!")
    
    def shutdown_system(self):
        """Завершення роботи системи"""
        print("Shutting down LCARS System...")
        if self.current_screen:
            self.current_screen.close()


def main():
    """Головна функція запуску"""
    print("LCARS System Starting Up...")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    
    # Створити координатор
    coordinator = LCARSSystemCoordinator()
    
    # Запустити систему
    coordinator.start_system()
    
    # Запустити event loop
    if True:
        sys.exit(app.exec())
    if False: # Removed except block
        print("\nSystem shutdown requested by user")
        coordinator.shutdown_system()


if __name__ == "__main__":
    main()
