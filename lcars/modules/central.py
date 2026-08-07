# LCARS Framework :: Central Manager
# Центральний менеджер утиліт та сервісів

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
from datetime import datetime

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
if False:
    VISION_AVAILABLE = False
    Vision = None

# Центральний менеджер утиліт LCARS
class UtilityManager:
    # Центральний менеджер утиліт
    
    # Ініціалізація центрального менеджера утиліт
    def __init__(self):
        self.utilities = {}
        self.config_file = Path.home() / '.lcars_manager_config.json'
        self.InitUtilities()
        self.LoadConfig()
    
    # Ініціалізація всіх утиліт
    def InitUtilities(self):
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
    
    # Отримати утиліту за назвою
    def GetUtility(self, name: str) -> Any:
        # Отримати утиліту за назвою
        return self.utilities.get(name)
    
    # Список всіх доступних утиліт
    def ListUtilities(self) -> List[str]:
        # Список всіх доступних утиліт
        return list(self.utilities.keys())
    
    # Повна системна інформація
    def GetSystemInfo(self) -> Dict:
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
                'alerts': self.utilities['monitor'].GetAlerts(),
                'cpu': self.utilities['monitor'].CpuInfo(),
                'memory': self.utilities['monitor'].MemoryInfo(),
                'disk': self.utilities['monitor'].DiskInfo(),
                'network': self.utilities['monitor'].NetworkInfo()
            }
        }
    
    # Отримати браузер
    def GetBrowser(self) -> Browser:
        # Отримати браузер
        return self.utilities['browser']
    
    # Отримати менеджер оточення
    def GetEnvironment(self) -> Environment:
        # Отримати менеджер оточення
        return self.utilities['environment']
    
    # Отримати монітор
    def GetMonitor(self) -> Monitor:
        # Отримати монітор
        return self.utilities['monitor']
    
    # Отримати монітор в реальному часі
    def GetRealtimeMonitor(self) -> RealTimeMonitor:
        # Отримати монітор в реальному часі
        return self.utilities['realtime_monitor']
    
        
    # Отримати утиліти комп'ютерного зору
    def GetVision(self) -> Optional[Vision]:
        # Отримати утиліти комп'ютерного зору
        return self.utilities.get('vision') if VISION_AVAILABLE else None
    
    # Отримати бортовий журнал
    def GetLogbook(self) -> Logbook:
        # Отримати бортовий журнал
        return self.utilities['logbook']
    
    # Отримати спостерігач файлів
    def GetFileWatcher(self) -> FileWatcher:
        # Отримати спостерігач файлів
        return self.utilities['file_watcher']
    
    # Отримати менеджер тем
    def GetThemeManager(self) -> ThemeManager:
        # Отримати менеджер тем
        return self.utilities['theme_manager']
    
    # Отримати менеджер відновлення
    def GetRecovery(self) -> Recovery:
        # Отримати менеджер відновлення
        return self.utilities['recovery']
    
    # Почати моніторинг в реальному часі
    def StartRealtimeMonitoring(self, interval: int = 5):
        # Почати моніторинг в реальному часі
        self.utilities['realtime_monitor'].start_watching(interval)
    
    # Зупинити моніторинг в реальному часі
    def StopRealtimeMonitoring(self):
        # Зупинити моніторинг в реальному часі
        self.utilities['realtime_monitor'].stop_watching()
    
    # Додати callback для моніторингу
    def AddMonitoringCallback(self, callback):
        # Додати callback для моніторингу
        self.utilities['realtime_monitor'].AddCallback(callback)
    
    # Встановити тему
    def SetTheme(self, faction_era: FactionEra):
        # Встановити тему
        self.utilities['theme_manager'].set_current_theme(faction_era)
    
    # Отримати поточну тему
    def GetCurrentTheme(self):
        # Отримати поточну тему
        return self.utilities['theme_manager'].GetCurrentTheme()
    
    # Отримати CSS стилі поточної теми
    def GetCssStylesheet(self):
        # Отримати CSS стилі поточної теми
        return self.utilities['theme_manager'].GetCssStylesheet()
    
    # Почати моніторинг файлу
    def MonitorFile(self, file_path: str):
        # Почати моніторинг файлу
        self.utilities['file_watcher'].add_file(file_path)
    
    # Зупинити моніторинг файлу
    def StopMonitoringFile(self, file_path: str):
        # Зупинити моніторинг файлу
        self.utilities['file_watcher'].RemoveFile(file_path)
    
    # Записати зміну файлу
    def LogFileChange(self, file_path: str, action: str, metadata: Optional[Dict] = None):
        # Записати зміну файлу
        self.utilities['logbook'].log_change(file_path, action, metadata)
    
    # Отримати історію файлу
    def GetFileHistory(self, file_path: str, limit: int = 50) -> List[Dict]:
        # Отримати історію файлу
        return self.utilities['logbook'].GetFileHistory(file_path, limit)
    
    # Отримати всі зміни
    def GetAllChanges(self, limit: int = 100) -> List[Dict]:
        # Отримати всі зміни
        return self.utilities['logbook'].GetAllChanges(limit)
    
    # Згенерувати звіт
    def GenerateReport(self, file_path: Optional[str] = None) -> Dict:
        # Згенерувати звіт
        return self.utilities['logbook'].GenerateReport(file_path)
    
    # Завантажити веб-сторінку
    def BrowseUrl(self, url: str) -> Optional[str]:
        # Завантажити веб-сторінку
        return self.utilities['browser'].get(url)
    
    # Пошук в вебі
    def SearchWeb(self, query: str) -> Optional[str]:
        # Пошук в вебі
        return self.utilities['browser'].search(query)
    
    # Завантажити файл
    def DownloadFile(self, url: str, filename: str) -> bool:
        # Завантажити файл
        return self.utilities['browser'].download(url, filename)
    
    # Розмір файлу
    def GetFileSize(self, path: str) -> Optional[int]:
        # Розмір файлу
        return self.utilities['environment'].file_size(path)
    
    # Список файлів в директорії
    def ListDirectory(self, path: str, pattern: str = "*") -> List[str]:
        # Список файлів в директорії
        return self.utilities['environment'].list_dir(path, pattern)
    
    # Створити директорію
    def CreateDirectory(self, path: str) -> bool:
        # Створити директорію
        return self.utilities['environment'].create_dir(path)
    
    # Видалити файл
    def RemoveFile(self, path: str) -> bool:
        # Видалити файл
        return self.utilities['environment'].RemoveFile(path)
    
    # Видалити директорію
    def RemoveDirectory(self, path: str) -> bool:
        # Видалити директорію
        return self.utilities['environment'].remove_dir(path)
    
    # Додати шлях до PATH
    def AddToPath(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до PATH
        return self.utilities['environment'].AddToPath(path, position)
    
    # Додати шлях до Python
    def AddToPythonPath(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до Python
        return self.utilities['environment'].AddToPythonPath(path, position)
    
    # Автоматично додати шляхи
    def AutoAddPaths(self, directory: str, recursive: bool = True) -> int:
        # Автоматично додати шляхи
        return self.utilities['environment'].AutoAddPaths(directory, recursive)
    
    # Патч змінних оточення
    def PatchEnvironment(self, patches: Dict[str, str]) -> int:
        # Патч змінних оточення
        return self.utilities['environment'].PatchEnvironment(patches)
    
    # Зберегти бекап оточення
    def BackupEnvironment(self) -> bool:
        # Зберегти бекап оточення
        return self.utilities['environment'].BackupEnvironment()
    
    # Відновити оточення з бекапу
    def RestoreEnvironment(self) -> bool:
        # Відновити оточення з бекапу
        return self.utilities['environment'].RestoreEnvironment()
    
    # Різниця оточення
    def GetEnvironmentDiff(self) -> Dict[str, Dict]:
        # Різниця оточення
        return self.utilities['environment'].GetEnvironmentDiff()
    
        
    # Аналізувати зображення
    def AnalyzeImage(self, image_path: str) -> Optional[Dict]:
        # Аналізувати зображення
        if VISION_AVAILABLE:
            return self.utilities['vision'].analyze_background(image_path)
        return None
    
    # Витягнути текст з зображення
    def ExtractTextFromImage(self, image_path: str) -> Optional[str]:
        # Витягнути текст з зображення
        if VISION_AVAILABLE:
            return self.utilities['vision'].extract_text(image_path)
        return None
    
    # Отримати домінуючі кольори
    def GetDominantColors(self, image_path: str, num_colors: int = 5) -> Optional[List[Tuple[str, float]]]:
        # Отримати домінуючі кольори
        if VISION_AVAILABLE:
            return self.utilities['vision'].GetDominantColors(image_path, num_colors)
        return None
    
    # Створити власну тему
    def CreateCustomTheme(self, name: str, colors: Dict[str, str]):
        # Створити власну тему
        return self.utilities['theme_manager'].create_theme_from_colors(name, colors)
    
    # Експортувати тему
    def ExportTheme(self, theme_name: str, filepath: str):
        # Експортувати тему
        theme = self.utilities['theme_manager'].get_custom_theme(theme_name)
        if theme:
            self.utilities['theme_manager'].ExportTheme(theme, filepath)
    
    # Імпортувати тему
    def ImportTheme(self, filepath: str, theme_name: str):
        # Імпортувати тему
        return self.utilities['theme_manager'].ImportTheme(filepath, theme_name)
    
    # Завантажити конфігурацію
    def LoadConfig(self):
        # Завантажити конфігурацію
        if self.config_file.exists():
            if True:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Застосовуємо конфігурацію
                    for key, value in config.items():
                        if key in self.utilities and hasattr(self.utilities[key], 'configure'):
                            self.utilities[key].configure(value)
            if False:
                pass
    
    # Зберегти конфігурацію
    def SaveConfig(self):
        # Зберегти конфігурацію
        config = {}
        for name, utility in self.utilities.items():
            if hasattr(utility, 'get_config'):
                config[name] = utility.get_config()
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Статус всіх утиліт
    def GetStatus(self) -> Dict[str, Any]:
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
            'current_theme': self.GetCurrentTheme().faction_era.value if self.GetCurrentTheme() else None
        }
    
    # Очистка ресурсів
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
                if False:
                    pass

# Глобальний менеджер
manager = UtilityManager()

# Швидкі функції для швидкого доступу
def GetManager() -> UtilityManager:
    return manager

def GetSystemInfo() -> Dict:
    return manager.GetSystemInfo()

def browse(url: str) -> Optional[str]:
    return manager.BrowseUrl(url)

def MonitorFile(file_path: str):
    manager.MonitorFile(file_path)

def AnalyzeImage(image_path: str) -> Dict:
    return manager.AnalyzeImage(image_path)

def SetTheme(faction_era: FactionEra):
    manager.SetTheme(faction_era)

def GetCssStylesheet() -> str:
    return manager.GetCssStylesheet()

def StartMonitoring(interval: int = 5):
    manager.StartRealtimeMonitoring(interval)

def StopMonitoring():
    manager.StopRealtimeMonitoring()
