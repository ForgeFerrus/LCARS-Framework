"""Validation utilities for LCARS Framework"""

import json
import os
from pathlib import Path
from typing import Any, Optional


def validate_path(path: str, must_exist: bool = True) -> bool:
    """
    Validate file or directory path.
    
    Args:
        path: Path to validate
        must_exist: Require path to exist
        
    Returns:
        True if valid
    """
    p = Path(path)
    if must_exist:
        return p.exists()
    return True


def validate_json(data: str) -> bool:
    """
    Validate JSON string.
    
    Args:
        data: JSON string to validate
        
    Returns:
        True if valid JSON
    """
    json.loads(data)
    return True


def validate_json_schema(data: dict, schema_keys: list) -> bool:
    """
    Validate dictionary has required keys.
    
    Args:
        data: Dictionary to validate
        schema_keys: Required keys
        
    Returns:
        True if all keys present
    """
    if not isinstance(data, dict):
        return False
    return all(key in data for key in schema_keys)


def is_geant4_project(path: str) -> bool:
    """
    Check if directory is a Geant4 project.
    
    Args:
        path: Directory path
        
    Returns:
        True if appears to be Geant4 project
    """
    p = Path(path)
    if not p.is_dir():
        return False
    
    # Check for typical Geant4 project structure
    required = ['CMakeLists.txt', 'src', 'include']
    return all((p / req).exists() for req in required)


def is_valid_filename(filename: str) -> bool:
    """
    Check if string is valid filename.
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if valid
    """
    invalid_chars = '<>:"|?*\\'
    return not any(char in filename for char in invalid_chars) and filename.strip()


def validate_file_extension(path: str, allowed_extensions: list) -> bool:
    """
    Check if file has allowed extension.
    
    Args:
        path: File path
        allowed_extensions: List of allowed extensions (e.g., ['.py', '.txt'])
        
    Returns:
        True if extension is allowed
    """
    ext = Path(path).suffix.lower()
    return ext in [e.lower() for e in allowed_extensions]


def validate_directory_structure(root: str, required_dirs: list) -> bool:
    """
    Check if directory has required subdirectories.
    
    Args:
        root: Root directory path
        required_dirs: List of required subdirectory names
        
    Returns:
        True if all required dirs exist
    """
    root_path = Path(root)
    return all((root_path / d).is_dir() for d in required_dirs)


def is_readable_file(path: str) -> bool:
    """
    Check if file is readable.
    
    Args:
        path: File path
        
    Returns:
        True if readable
    """
    return os.access(path, os.R_OK)


def is_writable_directory(path: str) -> bool:
    """
    Check if directory is writable.
    
    Args:
        path: Directory path
        
    Returns:
        True if writable
    """
    return os.access(path, os.W_OK)


def validate_url(url: str) -> bool:
    """
    Basic URL validation.
    
    Args:
        url: URL string
        
    Returns:
        True if appears to be valid URL
    """
    return url.startswith(('http://', 'https://', 'ftp://'))
