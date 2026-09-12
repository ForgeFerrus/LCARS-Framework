"""System utilities for LCARS Framework"""

import os
import sys
import platform
import logging
import shutil
try:
    import psutil
except Exception:
    psutil = None
from typing import Dict, Any, Optional


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with system details
    """
    logger = logging.getLogger(__name__)
    try:
        cpu_count = os.cpu_count() or 1
        info: Dict[str, Any] = {
            'os': sys.platform,
            'os_name': platform.system(),
            'os_version': platform.release(),
            'python_version': sys.version,
            'python_executable': sys.executable,
            'cpu_count': cpu_count,
            'processor': platform.processor(),
            'machine': platform.machine(),
        }

        if psutil:
            try:
                vm = psutil.virtual_memory()
                info.update({
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory_total_gb': vm.total / (1024**3),
                    'memory_available_gb': vm.available / (1024**3),
                    'memory_percent': vm.percent,
                })
            except Exception as e:
                logger.debug("psutil metrics failed: %s", e)
                info.update({
                    'cpu_percent': None,
                    'memory_total_gb': None,
                    'memory_available_gb': None,
                    'memory_percent': None,
                })
        else:
            info.update({
                'cpu_percent': None,
                'memory_total_gb': None,
                'memory_available_gb': None,
                'memory_percent': None,
            })

        return info
    except Exception as e:
        logging.getLogger(__name__).exception("Error getting system info: %s", e)
        return {}


def check_dependencies(packages: list) -> Dict[str, bool]:
    """
    Check if Python packages are installed.
    
    Args:
        packages: List of package names to check
        
    Returns:
        Dictionary mapping package name to installed status
    """
    results = {}
    
    for package in packages:
        try:
            __import__(package)
            results[package] = True
        except ImportError:
            results[package] = False
    
    return results


def get_free_space(path: str = '/') -> Dict[str, float]:
    """
    Get free disk space information.
    
    Args:
        path: Path to check (default is root)
        
    Returns:
        Dictionary with space info in GB
    """
    logger = logging.getLogger(__name__)
    try:
        if psutil:
            usage = psutil.disk_usage(path)
            return {
                'total_gb': usage.total / (1024**3),
                'used_gb': usage.used / (1024**3),
                'free_gb': usage.free / (1024**3),
                'percent_used': usage.percent,
            }
        else:
            usage = shutil.disk_usage(path)
            total, used, free = usage
            percent_used = (used / total) * 100 if total else 0.0
            return {
                'total_gb': total / (1024**3),
                'used_gb': used / (1024**3),
                'free_gb': free / (1024**3),
                'percent_used': percent_used,
            }
    except Exception as e:
        logger.exception("Error getting disk space for %s: %s", path, e)
        return {}


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    logger = logging.getLogger(__name__)
    try:
        if psutil:
            return psutil.cpu_percent(interval=0.1)
        logger.debug("psutil not available for CPU usage query")
        return -1.0
    except Exception as e:
        logger.exception("Error getting CPU usage: %s", e)
        return -1.0


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage information."""
    logger = logging.getLogger(__name__)
    try:
        if not psutil:
            logger.debug("psutil not available for memory usage query")
            return {}
        vm = psutil.virtual_memory()
        return {
            'total_gb': vm.total / (1024**3),
            'available_gb': vm.available / (1024**3),
            'used_gb': vm.used / (1024**3),
            'percent': vm.percent,
        }
    except Exception as e:
        logger.exception("Error getting memory usage: %s", e)
        return {}


def get_process_info() -> Dict[str, Any]:
    """Get current process information."""
    logger = logging.getLogger(__name__)
    try:
        if not psutil:
            logger.debug("psutil not available for process info")
            return {'pid': os.getpid()}
        process = psutil.Process()
        return {
            'pid': process.pid,
            'memory_mb': process.memory_info().rss / (1024**2),
            'cpu_percent': process.cpu_percent(),
            'num_threads': process.num_threads(),
            'create_time': process.create_time(),
        }
    except Exception as e:
        logger.exception("Error getting process info: %s", e)
        return {}


def is_admin() -> bool:
    """Check if running with admin privileges."""
    logger = logging.getLogger(__name__)
    try:
        return os.geteuid() == 0  # Unix/Linux
    except AttributeError:
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())  # Windows
        except Exception as e:
            logger.debug("is_admin Windows check failed: %s", e)
            return False


def get_screen_resolution() -> Optional[Dict[str, int]]:
    """
    Get screen resolution (requires PyQt6 or similar).
    
    Returns:
        Dictionary with width and height, or None
    """
    logger = logging.getLogger(__name__)
    try:
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            return {
                'width': screen.geometry().width(),
                'height': screen.geometry().height(),
            }
    except Exception as e:
        logger.debug("get_screen_resolution failed: %s", e)

    return None
