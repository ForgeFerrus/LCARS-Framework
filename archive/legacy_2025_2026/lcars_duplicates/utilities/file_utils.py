"""File system utilities for LCARS Framework"""

import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional


def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
    """
    Find files matching pattern in directory.
    
    Args:
        directory: Path to search in
        pattern: File name pattern (e.g., "*designer.py", "test_*")
        recursive: Search subdirectories
        
    Returns:
        List of absolute file paths
    """
    logger = logging.getLogger(__name__)
    try:
        path = Path(directory)
        if not path.exists():
            return []
        
        if recursive:
            matches = list(path.glob(f"**/{pattern}"))
        else:
            matches = list(path.glob(pattern))
        
        return [str(m) for m in matches if m.is_file()]
    except Exception as e:
        logger.exception("Error finding files in %s: %s", directory, e)
        return []


def safe_copy(source: str, destination: str, overwrite: bool = False) -> bool:
    """
    Safely copy file with error handling.
    
    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Allow overwriting existing file
        
    Returns:
        True if successful
    """
    logger = logging.getLogger(__name__)
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            logger.warning("Source file not found: %s", source)
            return False
        
        if dest_path.exists() and not overwrite:
            logger.warning("Destination exists and overwrite=False: %s", destination)
            return False
        
        # Create parent directories if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source, destination)
        return True
    except Exception as e:
        logger.exception("Error copying %s to %s: %s", source, destination, e)
        return False


def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes, or -1 if error
    """
    logger = logging.getLogger(__name__)
    try:
        return os.path.getsize(filepath)
    except Exception as e:
        logger.exception("Error getting file size for %s: %s", filepath, e)
        return -1


def ensure_directory(directory: str) -> bool:
    """
    Create directory if it doesn't exist.
    
    Args:
        directory: Directory path
        
    Returns:
        True if successful
    """
    logger = logging.getLogger(__name__)
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.exception("Error creating directory %s: %s", directory, e)
        return False


def remove_file(filepath: str, safe: bool = True) -> bool:
    """
    Remove file with optional safety check.
    
    Args:
        filepath: Path to file
        safe: Check if file exists first
        
    Returns:
        True if successful
    """
    logger = logging.getLogger(__name__)
    try:
        path = Path(filepath)
        if safe and not path.exists():
            logger.warning("File not found: %s", filepath)
            return False
        path.unlink()
        return True
    except Exception as e:
        logger.exception("Error removing %s: %s", filepath, e)
        return False


def list_directory(directory: str, filter_extension: Optional[str] = None) -> List[str]:
    """
    List files in directory.
    
    Args:
        directory: Directory path
        filter_extension: Filter by extension (e.g., "designer.py")
        
    Returns:
        List of file names
    """
    logger = logging.getLogger(__name__)
    try:
        path = Path(directory)
        if not path.exists():
            return []
        
        files = [f.name for f in path.iterdir() if f.is_file()]
        
        if filter_extension:
            files = [f for f in files if f.endswith(filter_extension)]
        
        return sorted(files)
    except Exception as e:
        logger.exception("Error listing directory %s: %s", directory, e)
        return []
