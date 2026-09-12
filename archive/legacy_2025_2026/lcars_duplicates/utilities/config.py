# LCARS Framework :: Config Utils v1.0.0
# Утиліти роботи з конфігурацією
# Автор: LCARS Development Team
# Ліцензія: MIT

import json
from pathlib import Path
from typing import Any, Dict, Optional

# Проста версія без getVersion
version = "1.0.0"
# print(f"LCARS Config Utils v{version}")  # Вимкнено для UI


def load_json_config(filepath: str) -> Optional[Dict[str, Any]]:
    # Завантажити JSON конфігурацію
    path = Path(filepath)
    if not path.exists():
        return None
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_config(data: Dict[str, Any], filepath: str, pretty: bool = True) -> bool:
    # Зберегти JSON конфігурацію
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    return True


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    # Об'єднати конфігурації
    result = base.copy()
    result.update(override)
    return result


def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    # Отримати значення з конфігурації по ключу
    keys = key.split('.')
    current = config
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current


def set_config_value(config: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    # Встановити значення в конфігурації
    keys = key.split('.')
    current = config
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    current[keys[-1]] = value
    return config


def load_or_create_config(filepath: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    # Завантажити конфігурацію або створити з defaults
    config = load_json_config(filepath)
    
    if config is None:
        config = defaults.copy()
        save_json_config(config, filepath)
    
    return config


def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    # Валідувати конфігурацію по схемі
    for key, expected_type in schema.items():
        value = get_config_value(config, key)
        if value is None:
            return False
        if not isinstance(value, expected_type):
            return False
    return True


def backup_config(filepath: str) -> str:
    # Створити бекап конфігурації
    path = Path(filepath)
    if not path.exists():
        return ""
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.parent / f"{path.stem}_{timestamp}{path.suffix}"
    
    if save_json_config(load_json_config(filepath), str(backup_path)):
        return str(backup_path)
    
    return ""


def restore_config(backup_path: str, target_path: str) -> bool:
    # Відновити конфігурацію з бекапу
    backup_data = load_json_config(backup_path)
    if backup_data:
        return save_json_config(backup_data, target_path)
    return False


def compare_configs(config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
    # Порівняти дві конфігурації
    keys1 = set(get_all_keys(config1))
    keys2 = set(get_all_keys(config2))
    
    common_keys = keys1 & keys2
    only_in_config1 = keys1 - keys2
    only_in_config2 = keys2 - keys1
    
    differences = {}
    for key in common_keys:
        val1 = get_config_value(config1, key)
        val2 = get_config_value(config2, key)
        if val1 != val2:
            differences[key] = {'old': val1, 'new': val2}
    
    return {
        'differences': differences,
        'only_in_config1': list(only_in_config1),
        'only_in_config2': list(only_in_config2),
        'identical': len(differences) == 0 and len(only_in_config1) == 0 and len(only_in_config2) == 0
    }


def get_all_keys(config: Dict[str, Any], prefix: str = "") -> list:
    # Отримати всі ключі конфігурації
    keys = []
    
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.append(full_key)
        
        if isinstance(value, dict):
            keys.extend(get_all_keys(value, full_key))
    
    return keys


def flatten_config(config: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    # Сплющити конфігурацію
    result = {}
    
    for key, value in config.items():
        full_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            result.update(flatten_config(value, full_key))
        else:
            result[full_key] = value
    
    return result


def unflatten_config(flat_config: Dict[str, Any]) -> Dict[str, Any]:
    # Розплющити конфігурацію
    result = {}
    
    for key, value in flat_config.items():
        set_config_value(result, key, value)
    
    return result


def filter_config(config: Dict[str, Any], keys: list) -> Dict[str, Any]:
    # Відфільтрувати конфігурацію по ключах
    result = {}
    
    for key in keys:
        value = get_config_value(config, key)
        if value is not None:
            set_config_value(result, key, value)
    
    return result


def update_config_from_file(config: Dict[str, Any], filepath: str) -> Dict[str, Any]:
    # Оновити конфігурацію з файлу
    file_config = load_json_config(filepath)
    if file_config:
        return merge_configs(config, file_config)
    return config


def save_config_section(config: Dict[str, Any], section: str, filepath: str) -> bool:
    # Зберегти секцію конфігурації
    section_data = get_config_value(config, section)
    if section_data:
        return save_json_config(section_data, filepath)
    return False


def load_config_section(filepath: str, section: str) -> Optional[Dict[str, Any]]:
    # Завантажити секцію конфігурації
    section_data = load_json_config(filepath)
    if section_data:
        return {section: section_data}
    return None


def get_config_summary(config: Dict[str, Any]) -> Dict[str, Any]:
    # Отримати підсумок конфігурації
    flat_config = flatten_config(config)
    
    summary = {
        'total_keys': len(flat_config),
        'key_types': {},
        'sections': {}
    }
    
    for key, value in flat_config.items():
        value_type = type(value).__name__
        summary['key_types'][value_type] = summary['key_types'].get(value_type, 0) + 1
        
        section = key.split('.')[0]
        if section not in summary['sections']:
            summary['sections'][section] = 0
        summary['sections'][section] += 1
    
    return summary


def sanitize_config(config: Dict[str, Any]) -> Dict[str, Any]:
    # Очистити конфігурацію
    def clean_value(value):
        if isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items() if v is not None}
        elif isinstance(value, list):
            return [clean_value(item) for item in value if item is not None]
        else:
            return value
    
    return clean_value(config)


# Швидкі функції
def load(filepath: str) -> Optional[Dict[str, Any]]:
    return load_json_config(filepath)

def save(data: Dict[str, Any], filepath: str) -> bool:
    return save_json_config(data, filepath)

def get(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    return get_config_value(config, key, default)

def set(config: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    return set_config_value(config, key, value)

def create(filepath: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    return load_or_create_config(filepath, defaults)


# Константи
DEFAULT_CONFIG_NAME = "config.json"
BACKUP_SUFFIX = "_backup"
CONFIG_EXTENSIONS = ['.json', '.yaml', '.yml', '.conf', '.ini']

# Популярні формати конфігурації
SUPPORTED_FORMATS = {
    'json': {'load': load_json_config, 'save': save_json_config},
}

# Стандартні схеми валідації
COMMON_SCHEMAS = {
    'database': {'host': str, 'port': int, 'name': str, 'user': str},
    'api': {'url': str, 'key': str, 'timeout': int},
    'logging': {'level': str, 'file': str, 'format': str}
}
