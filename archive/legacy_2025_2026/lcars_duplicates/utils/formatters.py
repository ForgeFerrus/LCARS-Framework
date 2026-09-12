"""Formatting utilities for LCARS Framework"""

from datetime import datetime, timedelta
from typing import Union


def format_bytes(bytes_value: Union[int, float], precision: int = 2) -> str:
    """
    Format bytes to human-readable size.
    
    Args:
        bytes_value: Size in bytes
        precision: Decimal places
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    size = float(bytes_value)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.{precision}f} {units[unit_index]}"


def format_time(seconds: Union[int, float], include_ms: bool = False) -> str:
    """
    Format seconds to human-readable time.
    
    Args:
        seconds: Duration in seconds
        include_ms: Include milliseconds
        
    Returns:
        Formatted time string (e.g., "1h 30m 45s")
    """
    try:
        total_seconds = int(seconds)
        ms = int((seconds - total_seconds) * 1000)
        
        hours = total_seconds // 3600
        remaining = total_seconds % 3600
        minutes = remaining // 60
        secs = remaining % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")
        
        result = " ".join(parts)
        
        if include_ms and ms > 0:
            result += f" {ms}ms"
        
        return result
    except Exception as e:
        return str(seconds)


def format_number(value: Union[int, float], precision: int = 2, use_comma: bool = True) -> str:
    """
    Format number with thousands separator.
    
    Args:
        value: Number to format
        precision: Decimal places
        use_comma: Use comma as thousands separator
        
    Returns:
        Formatted number string
    """
    if precision > 0:
        formatted = f"{value:.{precision}f}"
    else:
        formatted = str(int(value))
    
    if use_comma:
        parts = formatted.split('.')
        parts[0] = '{:,}'.format(int(parts[0]))
        return '.'.join(parts)
    
    return formatted


def format_percentage(value: Union[int, float], precision: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value: Value between 0-100
        precision: Decimal places
        
    Returns:
        Formatted percentage string (e.g., "45.5%")
    """
    return f"{value:.{precision}f}%"


def format_datetime(dt: datetime, include_time: bool = True) -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        include_time: Include time component
        
    Returns:
        Formatted datetime string
    """
    if include_time:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.strftime("%Y-%m-%d")


def format_duration(start: datetime, end: datetime) -> str:
    """
    Format duration between two datetimes.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Formatted duration string
    """
    delta = end - start
    return format_time(delta.total_seconds())


def format_hex_color(r: int, g: int, b: int) -> str:
    """
    Format RGB to hex color.
    
    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)
        
    Returns:
        Hex color string (e.g., "#FF5733")
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def format_status(status: str) -> str:
    """
    Format status string for display.
    
    Args:
        status: Status string
        
    Returns:
        Formatted status with emoji indicator
    """
    status_lower = status.lower()
    
    indicators = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'running': '⏳',
        'stopped': '⏹️',
        'pending': '⏳',
    }
    
    indicator = indicators.get(status_lower, '•')
    return f"{indicator} {status}"


def format_table_row(values: list, widths: list = None) -> str:
    """
    Format values as table row.
    
    Args:
        values: List of values to format
        widths: Optional column widths
        
    Returns:
        Formatted table row
    """
    if widths is None:
        widths = [15] * len(values)
    
    formatted = []
    for value, width in zip(values, widths):
        str_val = str(value)
        if len(str_val) > width:
            str_val = str_val[:width-3] + "..."
        formatted.append(str_val.ljust(width))
    
    return " | ".join(formatted)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix for truncated text
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
