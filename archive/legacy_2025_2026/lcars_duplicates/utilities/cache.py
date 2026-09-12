# LCARS Framework :: Auto Cache v1.0.0
# Просте кешування результатів
# Автор: LCARS Development Team
# Ліцензія: MIT

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict, Callable
from functools import wraps

# Проста версія без getVersion
version = "1.0.0"
# print(f"LCARS Auto Cache v{version}")  # Вимкнено для UI

class SimpleCache:
    # Простий кеш  
    def __init__(self, cache_dir: str = None):
        self.cache_dir = Path(cache_dir or Path.home() / '.lcars_cache')
        self.cache_dir.mkdir(exist_ok=True)
        self.cache = {}
        self.ttl = {}
    
    def _get_cache_file(self, key: str) -> Path:
        # Файл кешу
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Any]:
        # Отримати з кешу
        # Спочатку в пам'яті
        if key in self.cache:
            if time.time() < self.ttl[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.ttl[key]
        
        # Потім в файлі
        cache_file = self._get_cache_file(key)
        if not cache_file.exists():
            return None
        
        with open(cache_file, 'r') as f:
            data = json.load(f)
            if time.time() < data.get('expires', 0):
                return data.get('value')
            else:
                cache_file.unlink()
                return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        # Зберегти в кеш
        self.cache[key] = value
        self.ttl[key] = time.time() + ttl
        
        cache_file = self._get_cache_file(key)
        data = {
            'value': value,
            'expires': time.time() + ttl
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    
    def clear(self):
        # Очистити кеш
        self.cache.clear()
        self.ttl.clear()
        
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()

# Глобальний кеш
_cache = SimpleCache()

def cache(ttl: int = 3600):
    # Декоратор кешування
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
            
            result = _cache.get(key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator

def cache_file(ttl: int = 3600):
    # Кешування файлів
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(file_path: str, *args, **kwargs):
            path = Path(file_path)
            if not path.exists():
                return func(file_path, *args, **kwargs)
            
            key = f"file_{func.__name__}_{path.stat().st_mtime}_{path.stat().st_size}"
            result = _cache.get(key)
            if result is not None:
                return result
            
            result = func(file_path, *args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator

def cache_network(ttl: int = 300):
    # Кешування мережі
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str, *args, **kwargs):
            key = f"network_{func.__name__}_{hashlib.md5(url.encode()).hexdigest()}"
            result = _cache.get(key)
            if result is not None:
                return result
            
            result = func(url, *args, **kwargs)
            _cache.set(key, result, ttl)
            return result
        
        return wrapper
    return decorator

# Швидкі функції
def get_cache() -> SimpleCache:
    return _cache

def clear_cache():
    _cache.clear()

# Приклади
@cache(ttl=60)
def slow_calculation(x: int) -> int:
    # Кешується на 1 хвилину
    return sum(i * i for i in range(x))

@cache_file(ttl=300)
def read_json(file_path: str) -> dict:
    # Кешується на 5 хвилин
    with open(file_path, 'r') as f:
        return json.load(f)

@cache_network(ttl=600)
def fetch_url(url: str) -> str:
    # Кешується на 10 хвилин
    import requests
    response = requests.get(url)
    return response.text
