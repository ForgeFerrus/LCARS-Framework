# LCARS SYSTEM INITIALIZATION
# Правильна послідовність завантаження системи LCARS
# 1. Ядро системи
# 2. Матриця та графічні компоненти  
# 3. Лаунчер вибору фракцій/епох
# 4. Авторизація
# 5. Перехід на містик/десктоп

import sys
import os
from pathlib import Path
import time
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont

# Додавання шляхів
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

class LCARSSystemSplash(QSplashScreen):
    """Системний сплеш-скрін завантаження LCARS"""
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.progress = 0
        self.max_progress = 100
        self.current_step = 0
        
        # Кроки завантаження
        self.boot_steps = [
            "◤ ISOLINEAR CORE INITIALIZATION",
            "◤ NEXUS DATA HUB ACTIVATION", 
            "◤ KERNEL SUBSTRATE LOADING",
            "◤ MATRIX PROTOCOL SYNCHRONIZATION",
            "◤ GRAPHICS COMPONENTS INITIALIZATION",
            "◤ LCARS INTERFACE PREPARATION",
            "◤ FACTION DATABASE LOADING",
            "◤ ERA PROTOCOLS ACTIVATION",
            "◤ AUTHORIZATION SYSTEM READY",
            "◤ SYSTEM FULLY OPERATIONAL"
        ]
        
    def drawContents(self, painter):
        painter.setPen(QColor(255, 153, 0))  # LCARS Orange
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        # Заголовок
        painter.drawText(50, 50, "LCARS SYSTEM INITIALIZATION")
        painter.drawText(50, 80, f"STARFLEET COMMAND INTERFACE")
        
        # Прогрес-бар
        painter.setPen(QColor(153, 204, 255))  # LCARS Blue
        progress_width = int((self.progress / self.max_progress) * 400)
        painter.drawRect(50, 120, 400, 20)
        
        # Заповнення прогресу
        from PyQt6.QtCore import QRect
        progress_rect = QRect(50, 120, progress_width, 20)
        painter.fillRect(progress_rect, QColor(153, 204, 255))
        
        # Текст поточного кроку
        if self.current_step < len(self.boot_steps):
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 12))
            painter.drawText(50, 160, self.boot_steps[self.current_step])
        
        # Відсоток
        painter.setPen(QColor(255, 153, 0))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(50, 200, f"LOADING: {int((self.progress / self.max_progress) * 100)}%")
        
    def update_progress(self, step, progress=None):
        """Оновлення прогресу завантаження"""
        self.current_step = min(step, len(self.boot_steps) - 1)
        if progress is not None:
            self.progress = progress
        else:
            self.progress = int((step / len(self.boot_steps)) * self.max_progress)
        self.update()
        
class LCARSSystemInitializer:
    """Ініціалізатор системи LCARS"""
    
    def __init__(self):
        self.splash = LCARSSystemSplash()
        self.app = None
        self.system = None
        
    def initialize_core_system(self):
        """Крок 1: Ініціалізація ядра системи"""
        print("◤ Initializing Core System...")
        self.splash.update_progress(0)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Ініціалізація ядра
            from lcars.core.kernel import Kernel
            from plugins import boot_full_system, set_system
            
            self.system, _, _ = boot_full_system(headless=False)
            set_system(self.system)
            
            self.splash.update_progress(1)
            print("✓ Core System Initialized")
            return True
            
        except Exception as e:
            print(f"✗ Core System Error: {e}")
            return False
            
    def initialize_matrix(self):
        """Крок 2: Ініціалізація матриці та протоколів"""
        print("◤ Initializing Matrix Protocols...")
        self.splash.update_progress(2)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Лінгвістична матриця
            from lcars.modules.linguistic_matrix import LinguisticMatrix
            matrix = LinguisticMatrix()
            
            # Проста перевірка роботи матриці
            if hasattr(matrix, 'initialize'):
                matrix.initialize()
            
            self.splash.update_progress(3)
            print("✓ Matrix Protocols Active")
            return True
            
        except Exception as e:
            print(f"✗ Matrix Error: {e}")
            # Матриця не є критичною для продовження
            self.splash.update_progress(3)
            print("⚠ Matrix Protocols Bypassed")
            return True
            
    def initialize_graphics(self):
        """Крок 3: Ініціалізація графічних компонентів"""
        print("◤ Initializing Graphics Components...")
        self.splash.update_progress(4)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Налаштування теми та шрифтів
            from lcars.themes.theme import setup_lcars_font, get_theme
            from lcars.themes.palette import LCARSEra
            
            setup_lcars_font()
            theme = get_theme(LCARSEra.LCARS_25TH)
            
            # Ініціалізація кольорового менеджера
            from lcars.system.color import COLOR_MANAGER
            COLOR_MANAGER.set_context(LCARSEra.LCARS_25TH, None)
            
            self.splash.update_progress(5)
            print("✓ Graphics Components Ready")
            return True
            
        except Exception as e:
            print(f"✗ Graphics Error: {e}")
            return False
            
    def initialize_launcher(self):
        """Крок 4: Підготовка лаунчера"""
        print("◤ Initializing Faction/Era Launcher...")
        self.splash.update_progress(6)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Завантаження баз даних фракцій та епох
            from lcars.themes.palette import get_faction_palette, get_era_palette
            
            # Перевірка доступних фракцій
            factions = ["Federation", "Klingon", "Romulan", "Borg"]
            eras = ["22nd", "23rd", "24th", "25th"]
            
            self.splash.update_progress(7)
            print("✓ Launcher Database Loaded")
            return True
            
        except Exception as e:
            print(f"✗ Launcher Error: {e}")
            return False
            
    def initialize_authorization(self):
        """Крок 5: Ініціалізація системи авторизації"""
        print("◤ Initializing Authorization System...")
        self.splash.update_progress(8)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Система авторизації
            from lcars.ui.views.titan.login import LoginView
            
            # Підготовка до авторизації
            self.splash.update_progress(9)
            print("✓ Authorization System Ready")
            return True
            
        except Exception as e:
            print(f"✗ Authorization Error: {e}")
            return False
            
    def launch_interface(self):
        """Крок 6: Запуск інтерфейсу"""
        print("◤ Launching LCARS Interface...")
        self.splash.update_progress(10, 100)
        QApplication.processEvents()
        time.sleep(0.5)
        
        try:
            # Запуск лаунчера з повною авторизацією
            from lcars.ui.launcher import LCARSLauncher
            
            # Закриття сплеш-скріна
            self.splash.finish(self.splash)
            
            # Створення та показ лаунчера
            launcher = LCARSLauncher(require_auth=True)
            
            # Повноекранний режим
            screen = QApplication.primaryScreen()
            if screen:
                geometry = screen.availableGeometry()
                launcher.setGeometry(geometry)
            
            launcher.show()
            launcher.raise_()
            launcher.activateWindow()
            
            # Запуск системи після авторизації
            self.system.start()
            
            print("✓ LCARS Interface Launched")
            return True
            
        except Exception as e:
            print(f"✗ Interface Launch Error: {e}")
            return False
            
    def run_initialization(self):
        """Повна послідовність ініціалізації"""
        print("=" * 60)
        print("◤ LCARS SYSTEM INITIALIZATION SEQUENCE")
        print("=" * 60)
        
        # Показати сплеш-скрін
        self.splash.show()
        QApplication.processEvents()
        
        # Послідовність завантаження
        steps = [
            ("Core System", self.initialize_core_system),
            ("Matrix Protocols", self.initialize_matrix),
            ("Graphics Components", self.initialize_graphics),
            ("Launcher Database", self.initialize_launcher),
            ("Authorization System", self.initialize_authorization),
            ("Interface Launch", self.launch_interface)
        ]
        
        for step_name, step_func in steps:
            print(f"[{time.strftime('%H:%M:%S')}] Starting {step_name}...")
            if not step_func():
                print(f"[{time.strftime('%H:%M:%S')}] ✗ Failed at {step_name}")
                return False
            print(f"[{time.strftime('%H:%M:%S')}] ✓ {step_name} Complete")
            
        print("=" * 60)
        print("◤ LCARS SYSTEM FULLY OPERATIONAL")
        print("=" * 60)
        return True

def main():
    """Головна функція запуску системи"""
    # Налаштування кодування для Windows
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except:
            pass
    
    # Створення QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Ініціалізація системи
    initializer = LCARSSystemInitializer()
    
    if initializer.run_initialization():
        # Запуск головного циклу подій
        app.exec()
    else:
        print("System initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
