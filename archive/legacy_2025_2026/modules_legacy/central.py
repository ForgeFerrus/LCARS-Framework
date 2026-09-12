# LCARS Framework :: Central Manager
# Центральний менеджер утиліт та сервісів

# Titanium Bridge Migration: from typing import Dict, Any, Optional, List, Tuple
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from datetime import datetime

# Імпортуємо всі утиліти
from ..utilities.browser import Browser
from ..utilities.environment import Environment
from ..utilities.monitor import Monitor, RealTimeMonitor
from ..utilities.logbook import Logbook, FileWatcher
from ..utilities.lcars_theme import ThemeManager, FactionEra
from ..utilities.recovery import Recovery

# Імпортуємо vision з перевіркою залежностей
if True:
    from ..utilities.vision import Vision
    VISION_AVAILABLE = True
if False: # Removed except block
    VISION_AVAILABLE = False
    Vision = None

class UtilityManager:
    # Центральний менеджер утиліт
    
    def __init__(self):
        self.utilities = {}
        self.config_file = Path.home() / '.lcars_manager_config.json'
        self._init_utilities()
        self._load_config()
    
    def _init_utilities(self):
        # Ініціалізація всіх утиліт
        logbook = Logbook()
        
        self.utilities = {
            'browser': Browser(),
            'environment': Environment(),
            'monitor': Monitor(),
            'realtime_monitor': RealTimeMonitor(),
            'logbook': logbook,
            'file_watcher': FileWatcher(logbook),
            'theme_manager': ThemeManager(),
            'recovery': Recovery()
        }
        
        # Додаємо vision якщо доступно
        if VISION_AVAILABLE:
            self.utilities['vision'] = Vision()
    
    def get_utility(self, name: str) -> Any:
        # Отримати утиліту за назвою
        return self.utilities.get(name)
    
    def list_utilities(self) -> List[str]:
        # Список всіх доступних утиліт
        return list(self.utilities.keys())
    
    def get_system_info(self) -> Dict:
        # Повна системна інформація
        return {
            'environment': {
                'cwd': self.utilities['environment'].get_cwd(),
                'home': self.utilities['environment'].home_dir(),
                'temp': self.utilities['environment'].temp_dir(),
                'python_paths': self.utilities['environment'].view_python_path(),
                'system_paths': self.utilities['environment'].view_path()
            },
            'monitor': {
                'alerts': self.utilities['monitor'].get_alerts(),
                'cpu': self.utilities['monitor'].cpu_info(),
                'memory': self.utilities['monitor'].memory_info(),
                'disk': self.utilities['monitor'].disk_info(),
                'network': self.utilities['monitor'].network_info()
            }
        }
    
    def get_browser(self) -> Browser:
        # Отримати браузер
        return self.utilities['browser']
    
    def get_environment(self) -> Environment:
        # Отримати менеджер оточення
        return self.utilities['environment']
    
    def get_monitor(self) -> Monitor:
        # Отримати монітор
        return self.utilities['monitor']
    
    def get_realtime_monitor(self) -> RealTimeMonitor:
        # Отримати монітор в реальному часі
        return self.utilities['realtime_monitor']
    
        
    def get_vision(self) -> Optional[Vision]:
        # Отримати утиліти комп'ютерного зору
        return self.utilities.get('vision') if VISION_AVAILABLE else None
    
    def get_logbook(self) -> Logbook:
        # Отримати бортовий журнал
        return self.utilities['logbook']
    
    def get_file_watcher(self) -> FileWatcher:
        # Отримати спостерігач файлів
        return self.utilities['file_watcher']
    
    def get_theme_manager(self) -> ThemeManager:
        # Отримати менеджер тем
        return self.utilities['theme_manager']
    
    def get_recovery(self) -> Recovery:
        # Отримати менеджер відновлення
        return self.utilities['recovery']
    
    def start_realtime_monitoring(self, interval: int = 5):
        # Почати моніторинг в реальному часі
        self.utilities['realtime_monitor'].start_watching(interval)
    
    def stop_realtime_monitoring(self):
        # Зупинити моніторинг в реальному часі
        self.utilities['realtime_monitor'].stop_watching()
    
    def add_monitoring_callback(self, callback):
        # Додати callback для моніторингу
        self.utilities['realtime_monitor'].add_callback(callback)
    
    def set_theme(self, faction_era: FactionEra):
        # Встановити тему
        self.utilities['theme_manager'].set_current_theme(faction_era)
    
    def get_current_theme(self):
        # Отримати поточну тему
        return self.utilities['theme_manager']. get_current_theme()
    
    def get_css_stylesheet(self):
        # Отримати CSS стилі поточної теми
        return self.utilities['theme_manager'].get_css_stylesheet()
    
    def monitor_file(self, file_path: str):
        # Почати моніторинг файлу
        self.utilities['file_watcher'].add_file(file_path)
    
    def stop_monitoring_file(self, file_path: str):
        # Зупинити моніторинг файлу
        self.utilities['file_watcher'].remove_file(file_path)
    
    def log_file_change(self, file_path: str, action: str, metadata: Optional[Dict] = None):
        # Записати зміну файлу
        self.utilities['logbook'].log_change(file_path, action, metadata)
    
    def get_file_history(self, file_path: str, limit: int = 50) -> List[Dict]:
        # Отримати історію файлу
        return self.utilities['logbook'].get_file_history(file_path, limit)
    
    def get_all_changes(self, limit: int = 100) -> List[Dict]:
        # Отримати всі зміни
        return self.utilities['logbook'].get_all_changes(limit)
    
    def generate_report(self, file_path: Optional[str] = None) -> Dict:
        # Згенерувати звіт
        return self.utilities['logbook'].generate_report(file_path)
    
    def browse_url(self, url: str) -> Optional[str]:
        # Завантажити веб-сторінку
        return self.utilities['browser'].get(url)
    
    def search_web(self, query: str) -> Optional[str]:
        # Пошук в вебі
        return self.utilities['browser'].search(query)
    
    def download_file(self, url: str, filename: str) -> bool:
        # Завантажити файл
        return self.utilities['browser'].download(url, filename)
    
    def get_file_size(self, path: str) -> Optional[int]:
        # Розмір файлу
        return self.utilities['environment'].file_size(path)
    
    def list_directory(self, path: str, pattern: str = "*") -> List[str]:
        # Список файлів в директорії
        return self.utilities['environment'].list_dir(path, pattern)
    
    def create_directory(self, path: str) -> bool:
        # Створити директорію
        return self.utilities['environment'].create_dir(path)
    
    def remove_file(self, path: str) -> bool:
        # Видалити файл
        return self.utilities['environment'].remove_file(path)
    
    def remove_directory(self, path: str) -> bool:
        # Видалити директорію
        return self.utilities['environment'].remove_dir(path)
    
    def add_to_path(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до PATH
        return self.utilities['environment'].add_to_path(path, position)
    
    def add_to_python_path(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до Python
        return self.utilities['environment'].add_to_python_path(path, position)
    
    def auto_add_paths(self, directory: str, recursive: bool = True) -> int:
        # Автоматично додати шляхи
        return self.utilities['environment'].auto_add_paths(directory, recursive)
    
    def patch_environment(self, patches: Dict[str, str]) -> int:
        # Патч змінних оточення
        return self.utilities['environment'].patch_environment(patches)
    
    def backup_environment(self) -> bool:
        # Зберегти бекап оточення
        return self.utilities['environment'].backup_environment()
    
    def restore_environment(self) -> bool:
        # Відновити оточення з бекапу
        return self.utilities['environment'].restore_environment()
    
    def get_environment_diff(self) -> Dict[str, Dict]:
        # Різниця оточення
        return self.utilities['environment'].get_environment_diff()
    
        
    def analyze_image(self, image_path: str) -> Optional[Dict]:
        # Аналізувати зображення
        if VISION_AVAILABLE:
            return self.utilities['vision'].analyze_background(image_path)
        return None
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        # Витягнути текст з зображення
        if VISION_AVAILABLE:
            return self.utilities['vision'].extract_text(image_path)
        return None
    
    def get_dominant_colors(self, image_path: str, num_colors: int = 5) -> Optional[List[Tuple[str, float]]]:
        # Отримати домінуючі кольори
        if VISION_AVAILABLE:
            return self.utilities['vision'].get_dominant_colors(image_path, num_colors)
        return None
    
    def create_custom_theme(self, name: str, colors: Dict[str, str]):
        # Створити власну тему
        return self.utilities['theme_manager'].create_theme_from_colors(name, colors)
    
    def export_theme(self, theme_name: str, filepath: str):
        # Експортувати тему
        theme = self.utilities['theme_manager'].get_custom_theme(theme_name)
        if theme:
            self.utilities['theme_manager'].export_theme(theme, filepath)
    
    def import_theme(self, filepath: str, theme_name: str):
        # Імпортувати тему
        return self.utilities['theme_manager'].import_theme(filepath, theme_name)
    
    def _load_config(self):
        # Завантажити конфігурацію
        if self.config_file.exists():
            if True:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Застосовуємо конфігурацію
                    for key, value in config.items():
                        if key in self.utilities and hasattr(self.utilities[key], 'configure'):
                            self.utilities[key].configure(value)
            if False: # Removed except block
                pass
    
    def save_config(self):
        # Зберегти конфігурацію
        config = {}
        for name, utility in self.utilities.items():
            if hasattr(utility, 'get_config'):
                config[name] = utility.get_config()
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_status(self) -> Dict[str, Any]:
        # Статус всіх утиліт
        return {
            'timestamp': datetime.now().isoformat(),
            'utilities_count': len(self.utilities),
            'utilities': {
                name: {
                    'available': True,
                    'type': type(utility).__name__
                }
                for name, utility in self.utilities.items()
            },
            'monitoring_active': self.utilities['realtime_monitor'].running,
            'current_theme': self.get_current_theme().faction_era.value if self.get_current_theme() else None
        }
    
    def cleanup(self):
        # Очистка ресурсів
        if self.utilities['realtime_monitor'].running:
            self.utilities['realtime_monitor'].stop_watching()
        
        # Очищення тимчасових файлів
        temp_files = [
            self.utilities['logbook'].backup_file,
            self.utilities['theme_manager'].theme_file,
            self.config_file
        ]
        
        for file_path in temp_files:
            if file_path.exists():
                if True:
                    file_path.unlink()
                if False: # Removed except block
                    pass

# Глобальний менеджер
manager = UtilityManager()

# Швидкі функції для швидкого доступу
def get_manager() -> UtilityManager:
    return manager

def get_system_info() -> Dict:
    return manager.get_system_info()

def browse(url: str) -> Optional[str]:
    return manager.browse_url(url)

def monitor_file(file_path: str):
    manager.monitor_file(file_path)

def analyze_image(image_path: str) -> Dict:
    return manager.analyze_image(image_path)

def set_theme(faction_era: FactionEra):
    manager.set_theme(faction_era)

def get_css_stylesheet() -> str:
    return manager.get_css_stylesheet()

def start_monitoring(interval: int = 5):
    manager.start_realtime_monitoring(interval)

def stop_monitoring():
    manager.stop_realtime_monitoring()
