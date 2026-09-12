# LCARS Framework :: System Environment Manager v1.0.0
# Управління системним оточенням та шляхами
# Автор: LCARS Development Team
# Ліцензія: MIT

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Environment Manager v{version}")  # Вимкнено для UI

class Environment:
    # Менеджер системного оточення
    
    def __init__(self):
        self.backup_file = Path.home() / '.lcars_env_backup.json'
        self.current_paths = list(sys.path)
        self.original_paths = list(sys.path)
    
    def view_all(self) -> Dict[str, str]:
        # Переглянути всі змінні оточення
        return dict(os.environ)
    
    def view_path(self) -> List[str]:
        # Переглянути PATH змінну
        return os.environ.get('PATH', '').split(os.pathsep) if os.environ.get('PATH') else []
    
    def view_python_path(self) -> List[str]:
        # Переглянути Python sys.path
        return list(sys.path)
    
    def get_var(self, name: str) -> Optional[str]:
        # Отримати змінну оточення
        return os.environ.get(name)
    
    def set_var(self, name: str, value: str):
        # Встановити змінну оточення
        os.environ[name] = value
    
    def remove_var(self, name: str) -> bool:
        # Видалити змінну оточення
        if name in os.environ:
            del os.environ[name]
            return True
        return False
    
    def add_to_path(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до PATH
        path = str(Path(path).resolve())
        
        if not Path(path).exists():
            return False
        
        current_path = os.environ.get('PATH', '')
        paths = current_path.split(os.pathsep)
        
        if path in paths:
            return False
        
        if position == 'start':
            paths.insert(0, path)
        else:
            paths.append(path)
        
        os.environ['PATH'] = os.pathsep.join(paths)
        return True
    
    def remove_from_path(self, path: str) -> bool:
        # Видалити шлях з PATH
        path = str(Path(path).resolve())
        current_path = os.environ.get('PATH', '')
        paths = current_path.split(os.pathsep)
        
        if path in paths:
            paths.remove(path)
            os.environ['PATH'] = os.pathsep.join(paths)
            return True
        return False
    
    def add_to_python_path(self, path: str, position: str = 'end') -> bool:
        # Додати шлях до Python sys.path
        path = str(Path(path).resolve())
        
        if not Path(path).exists():
            return False
        
        if path in sys.path:
            return False
        
        if position == 'start':
            sys.path.insert(0, path)
        else:
            sys.path.append(path)
        
        self.current_paths = list(sys.path)
        return True
    
    def remove_from_python_path(self, path: str) -> bool:
        # Видалити шлях з Python sys.path
        path = str(Path(path).resolve())
        
        if path in sys.path:
            sys.path.remove(path)
            self.current_paths = list(sys.path)
            return True
        return False
    
    def auto_add_paths(self, directory: str, recursive: bool = True) -> int:
        # Автоматично додати всі піддиректорії до шляхів
        directory = Path(directory).resolve()
        
        if not directory.exists():
            return 0
        
        added_count = 0
        
        if recursive:
            # Рекурсивно додати всі піддиректорії
            for path in directory.rglob('*'):
                if path.is_dir() and str(path) not in sys.path:
                    self.add_to_python_path(str(path))
                    added_count += 1
        else:
            # Тільки прямі піддиректорії
            for path in directory.iterdir():
                if path.is_dir() and str(path) not in sys.path:
                    self.add_to_python_path(str(path))
                    added_count += 1
        
        return added_count
    
    def auto_add_python_packages(self, directory: str) -> int:
        # Автоматично додати шляхи до Python пакетів
        directory = Path(directory).resolve()
        added_count = 0
        
        # Шукаємо директорії з __init__.py
        for path in directory.rglob('__init__.py'):
            package_dir = path.parent
            if str(package_dir) not in sys.path:
                self.add_to_python_path(str(package_dir.parent))
                added_count += 1
        
        return added_count
    
    def patch_environment(self, patches: Dict[str, str]) -> int:
        # Патч змінних оточення
        patched_count = 0
        
        for name, value in patches.items():
            if name.upper() == 'PATH':
                # Спеціальна обробка для PATH
                paths = value.split(os.pathsep)
                for path in paths:
                    if self.add_to_path(path):
                        patched_count += 1
            else:
                # Звичайні змінні
                old_value = os.environ.get(name)
                if old_value != value:
                    self.set_var(name, value)
                    patched_count += 1
        
        return patched_count
    
    def patch_python_path(self, paths: List[str], position: str = 'end') -> int:
        # Патч Python sys.path
        patched_count = 0
        
        for path in paths:
            if self.add_to_python_path(path, position):
                patched_count += 1
        
        return patched_count
    
    def backup_environment(self) -> bool:
        # Зберегти бекап поточного оточення
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'environment': dict(os.environ),
            'python_path': list(sys.path),
            'original_python_path': self.original_paths
        }
        
        try:
            with open(self.backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            return True
        except:
            return False
    
    def restore_environment(self) -> bool:
        # Відновити оточення з бекапу
        if not self.backup_file.exists():
            return False
        
        try:
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)
            
            # Відновлюємо змінні оточення
            os.environ.clear()
            os.environ.update(backup_data['environment'])
            
            # Відновлюємо Python path
            sys.path.clear()
            sys.path.extend(backup_data['python_path'])
            
            self.current_paths = list(sys.path)
            return True
        except:
            return False
    
    def reset_to_original(self):
        # Скинути до оригінальних шляхів
        sys.path.clear()
        sys.path.extend(self.original_paths)
        self.current_paths = list(sys.path)
    
    def get_environment_diff(self) -> Dict[str, Dict]:
        # Показати різницю між поточним та оригінальним оточенням
        current_env = dict(os.environ)
        
        # Завантажуємо оригінальне оточення
        original_env = {}
        if self.backup_file.exists():
            try:
                with open(self.backup_file, 'r') as f:
                    backup_data = json.load(f)
                original_env = backup_data['environment']
            except:
                pass
        
        # Знаходимо різниці
        added = {}
        removed = {}
        changed = {}
        
        all_keys = set(current_env.keys()) | set(original_env.keys())
        
        for key in all_keys:
            current_val = current_env.get(key)
            original_val = original_env.get(key)
            
            if original_val is None:
                added[key] = current_val
            elif current_val is None:
                removed[key] = original_val
            elif current_val != original_val:
                changed[key] = {'old': original_val, 'new': current_val}
        
        return {
            'added': added,
            'removed': removed,
            'changed': changed,
            'path_diff': {
                'original': self.original_paths,
                'current': self.current_paths,
                'added': [p for p in self.current_paths if p not in self.original_paths],
                'removed': [p for p in self.original_paths if p not in self.current_paths]
            }
        }
    
    def scan_for_modules(self, directory: str) -> List[str]:
        # Сканувати директорію на наявність Python модулів
        directory = Path(directory).resolve()
        modules = []
        
        for path in directory.rglob('*.py'):
            if path.name != '__init__.py':
                relative_path = path.relative_to(directory)
                module_name = str(relative_path.with_suffix('')).replace(os.sep, '.')
                modules.append(module_name)
        
        return modules
    
    def validate_path(self, path: str) -> Dict[str, Union[bool, str]]:
        # Перевірити валідність шляху
        path_obj = Path(path)
        
        return {
            'exists': path_obj.exists(),
            'is_file': path_obj.is_file(),
            'is_dir': path_obj.is_dir(),
            'is_readable': os.access(path, os.R_OK),
            'is_writable': os.access(path, os.W_OK),
            'is_executable': os.access(path, os.X_OK),
            'absolute_path': str(path_obj.resolve()),
            'parent_exists': path_obj.parent.exists()
        }

# Глобальний екземпляр
env = Environment()

# Швидкі функції
def add_path(path: str) -> bool:
    return env.add_to_path(path)

def add_python_path(path: str) -> bool:
    return env.add_to_python_path(path)

def auto_add(directory: str, recursive: bool = True) -> int:
    return env.auto_add_paths(directory, recursive)

def backup_env() -> bool:
    return env.backup_environment()

def restore_env() -> bool:
    return env.restore_environment()

def show_env_diff() -> Dict[str, Dict]:
    return env.get_environment_diff()
