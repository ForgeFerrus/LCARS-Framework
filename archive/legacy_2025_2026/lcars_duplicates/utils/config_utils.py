"""Configuration utilities for LCARS Framework"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


def load_json_config(filepath: str) -> Optional[Dict[str, Any]]:
    """
    Load JSON configuration file.
    
    Args:
        filepath: Path to JSON config file
        
    Returns:
        Dictionary with config data, or None if error
    """
    logger = logging.getLogger(__name__)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("Config file not found: %s", filepath)
        return None
    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON in %s: %s", filepath, e)
        return None
    except Exception as e:
        logger.exception("Error loading config from %s: %s", filepath, e)
        return None


def save_json_config(data: Dict[str, Any], filepath: str, pretty: bool = True) -> bool:
    """
    Save configuration to JSON file.
    
    Args:
        data: Configuration dictionary
        filepath: Path to save to
        pretty: Use pretty formatting (indent=2)
        
    Returns:
        True if successful
    """
    logger = logging.getLogger(__name__)
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            indent = 2 if pretty else None
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.exception("Error saving config to %s: %s", filepath, e)
        return False


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    Override values take precedence.
    
    Args:
        base: Base configuration
        override: Configuration to override with
        
    Returns:
        Merged configuration dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    return result


def get_config_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get nested config value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Path to value (e.g., "database.host")
        default: Default value if key not found
        
    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


def set_config_value(config: Dict[str, Any], key_path: str, value: Any) -> Dict[str, Any]:
    """
    Set nested config value using dot notation.
    
    Args:
        config: Configuration dictionary
        key_path: Path to value (e.g., "database.host")
        value: Value to set
        
    Returns:
        Modified configuration dictionary
    """
    keys = key_path.split('.')
    current = config
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return config


def load_or_create_config(filepath: str, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load config from file or create with defaults.
    
    Args:
        filepath: Path to config file
        defaults: Default configuration if file doesn't exist
        
    Returns:
        Configuration dictionary
    """
    config = load_json_config(filepath)
    
    if config is None:
        config = defaults.copy()
        save_json_config(config, filepath)
    
    return config
