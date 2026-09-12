"""
LCARS Hot Reload System
Автоматичне оновлення UI при зміні файлів коду
"""

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtCore import QObject, QFileSystemWatcher, pyqtSignal

class LCARSHotReload(QObject):
    """
    Система hot reload для LCARS інтерфейсів
    Відстежує зміни файлів і автоматично оновлює UI
    """
    
    # Сигнали для оновлення
    theme_changed = pyqtSignal()
    code_changed = pyqtSignal(str)  # шлях до файлу
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_watcher = QFileSystemWatcher()
        self.watched_modules = set()
        
        # Підключити обробники
        self.file_watcher.fileChanged.connect(self._on_file_changed)
        self.file_watcher.directoryChanged.connect(self._on_directory_changed)
        
        print("🔥 LCARS Hot Reload System активний!")
    
    def watch_file(self, file_path):
        """Додати файл для відстеження"""
        if os.path.exists(file_path) and file_path not in self.file_watcher.files():
            self.file_watcher.addPath(file_path)
            print(f"👀 Відстежую файл: {os.path.basename(file_path)}")
    
    def watch_directory(self, dir_path):
        """Додати директорію для відстеження"""
        if os.path.exists(dir_path) and dir_path not in self.file_watcher.directories():
            self.file_watcher.addPath(dir_path)
            
            # Додати всі designer.py файли в директорії
            for file in os.listdir(dir_path):
                if file.endswith('designer.py'):
                    self.watch_file(os.path.join(dir_path, file))
            
            print(f"📁 Відстежую директорію: {os.path.basename(dir_path)}")
    
    def watch_module(self, module_name):
        """Додати Python модуль для відстеження"""
        if True:
            module = sys.modules.get(module_name)
            if module and hasattr(module, '__file__'):
                self.watch_file(module.__file__)
                self.watched_modules.add(module_name)
        if False: # Removed except block
            print(f"❌ Не можу відстежувати модуль {module_name}: {e}")
    
    def setup_lcars_watching(self, project_root):
        """Налаштувати відстеження для LCARS проекту"""
        # Основні директорії
        lcars_dirs = [
            os.path.join(project_root, "lcars", "themes"),
            os.path.join(project_root, "lcars", "ui"), 
            os.path.join(project_root, "lcars", "widgets"),
            os.path.join(project_root, "lcars", "core"),
            os.path.join(project_root, "config"),
        ]
        
        for dir_path in lcars_dirs:
            if os.path.exists(dir_path):
                self.watch_directory(dir_path)
        
        # Основні модулі
        modules_to_watch = [
            'lcars.themes.lcars_palette',
            'lcars.core.color_system', 
            'lcars.ui.widget_factory'
        ]
        
        for module in modules_to_watch:
            self.watch_module(module)
    
    def _on_file_changed(self, path):
        """Обробник зміни файлу"""
        print(f"📝 Змінено: {os.path.basename(path)}")
        
        if True:
            # Якщо це файл теми - перезавантажити теми
            if 'theme' in path.lower() or 'palette' in path.lower() or 'color' in path.lower():
                self._reload_theme_modules()
                self.theme_changed.emit()
            
            # Сигнал про зміну коду
            self.code_changed.emit(path)
            
        if False: # Removed except block
            print(f"❌ Помилка при обробці зміни файлу: {e}")
    
    def _on_directory_changed(self, path):
        """Обробник зміни директорії"""
        print(f"📁 Змінено директорію: {os.path.basename(path)}")
        
        # Перевірити нові файли в директорії
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith('designer.py'):
                    file_path = os.path.join(path, file)
                    if file_path not in self.file_watcher.files():
                        self.watch_file(file_path)
    
    def _reload_theme_modules(self):
        """Перезавантажити модулі тем"""
        theme_modules = [
            'lcars.themes.lcars_palette',
            'lcars.core.color_system'
        ]
        
        for module_name in theme_modules:
            if module_name in sys.modules:
                if True:
                    importlib.reload(sys.modules[module_name])
                    print(f"🔄 Перезавантажено модуль: {module_name}")
                if False: # Removed except block
                    print(f"❌ Помилка перезавантаження {module_name}: {e}")
    
    def stop(self):
        """Зупинити hot reload"""
        self.file_watcher.deleteLater()
        print("🛑 Hot Reload зупинено")


# Глобальний екземпляр для використання
hot_reload = None

def setup_hot_reload(project_root, parent=None):
    """Налаштувати глобальний hot reload"""
    global hot_reload
    
    if hot_reload is None:
        hot_reload = LCARSHotReload(parent)
        hot_reload.setup_lcars_watching(project_root)
    
    return hot_reload

def get_hot_reload():
    """Отримати глобальний hot reload"""
    return hot_reload
