# LCARS Framework :: Formatters v1.0.0
# Утиліти форматування даних
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

from datetime import datetime, timedelta
from typing import Union, Dict, Any
import json
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Formatters v{version}")  # Вимкнено для UI


def format_bytes(bytes_value: Union[int, float], precision: int = 2) -> str:
    # Форматувати байти в читальний розмір
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    size = float(bytes_value)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.{precision}f} {units[unit_index]}"


def format_time(seconds: Union[int, float], include_ms: bool = False) -> str:
    # Форматувати секунди в час
    if not include_ms:
        seconds = int(seconds)
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_duration(start_time: datetime, end_time: datetime = None) -> str:
    # Форматувати тривалість
    if end_time is None:
        end_time = datetime.now()
    
    duration = end_time - start_time
    return format_time(duration.total_seconds())


def format_timestamp(timestamp: Union[datetime, float, str], format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    # Форматувати timestamp
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_str)
    elif isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).strftime(format_str)
    elif isinstance(timestamp, str):
        return timestamp
    else:
        return str(timestamp)


def format_number(number: Union[int, float], precision: int = 2) -> str:
    # Форматувати число з роздільниками
    if isinstance(number, int):
        return f"{number:,}"
    else:
        return f"{number:,.{precision}f}"


def format_percentage(value: Union[int, float], precision: int = 1) -> str:
    # Форматувати відсотки
    return f"{value:.{precision}f}%"


def format_file_size(file_path: str) -> str:
    # Форматувати розмір файлу
    from pathlib import Path
    size = Path(file_path).stat().st_size
    return format_bytes(size)


def format_memory_info(memory_info: Dict[str, Any]) -> str:
    # Форматувати інформацію про пам'ять
    total = format_bytes(memory_info.get('total', 0))
    available = format_bytes(memory_info.get('available', 0))
    used = format_bytes(memory_info.get('used', 0))
    percent = format_percentage(memory_info.get('percent', 0))
    
    return f"Total: {total} | Used: {used} | Available: {available} ({percent})"


def format_cpu_info(cpu_info: Dict[str, Any]) -> str:
    # Форматувати інформацію про CPU
    percent = format_percentage(cpu_info.get('percent', 0))
    freq = cpu_info.get('freq', {})
    
    if freq:
        current = freq.get('current', 0)
        max_freq = freq.get('max', 0)
        return f"CPU: {percent} | Freq: {current:.0f}/{max_freq:.0f} MHz"
    else:
        return f"CPU: {percent}"


def format_disk_info(disk_info: Dict[str, Any]) -> str:
    # Форматувати інформацію про диск
    total = format_bytes(disk_info.get('total', 0))
    used = format_bytes(disk_info.get('used', 0))
    free = format_bytes(disk_info.get('free', 0))
    percent = format_percentage(disk_info.get('percent', 0))
    
    return f"Disk: {total} | Used: {used} | Free: {free} ({percent})"


def format_network_info(network_info: Dict[str, Any]) -> str:
    # Форматувати інформацію про мережу
    bytes_sent = format_bytes(network_info.get('bytes_sent', 0))
    bytes_recv = format_bytes(network_info.get('bytes_recv', 0))
    
    return f"Network: Sent {bytes_sent} | Received {bytes_recv}"


def format_process_info(process_info: Dict[str, Any]) -> str:
    # Форматувати інформацію про процес
    pid = process_info.get('pid', 'Unknown')
    name = process_info.get('name', 'Unknown')
    cpu = format_percentage(process_info.get('cpu_percent', 0))
    memory = format_bytes(process_info.get('memory_info', {}).get('rss', 0))
    
    return f"PID: {pid} | {name} | CPU: {cpu} | Memory: {memory}"


def format_system_info(system_info: Dict[str, Any]) -> str:
    # Форматувати системну інформацію
    lines = []
    
    # OS інформація
    os_info = system_info.get('system', {})
    lines.append(f"OS: {os_info.get('platform', 'Unknown')} {os_info.get('platform_release', '')}")
    
    # CPU інформація
    cpu_info = system_info.get('cpu', {})
    lines.append(format_cpu_info(cpu_info))
    
    # Пам'ять
    memory_info = system_info.get('memory', {})
    lines.append(format_memory_info(memory_info))
    
    # Диск
    disk_info = system_info.get('disk', {})
    if disk_info:
        lines.append(format_disk_info(disk_info))
    
    # Мережа
    network_info = system_info.get('network', {})
    if network_info:
        lines.append(format_network_info(network_info))
    
    return '\n'.join(lines)


def format_lcars_status(status: str, level: str = "INFO") -> str:
    # Форматувати статус в LCARS стилі
    level_colors = {
        "INFO": "#99FF99",
        "WARNING": "#FF9966", 
        "ERROR": "#FF6666",
        "SUCCESS": "#66FF66",
        "CRITICAL": "#FF0000"
    }
    
    color = level_colors.get(level.upper(), "#FFFFFF")
    timestamp = format_timestamp(datetime.now(), "%H:%M:%S")
    
    return f"<font color='{color}'>[{timestamp}] {level.upper()}: {status}</font>"


def format_json_pretty(data: Any, indent: int = 2) -> str:
    # Форматувати JSON красиво
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)


def format_table(data: list, headers: list = None) -> str:
    # Форматувати дані в таблицю
    if not data:
        return "No data"
    
    if headers is None:
        headers = list(data[0].keys()) if isinstance(data[0], dict) else []
    
    # Визначити ширину колонок
    col_widths = {}
    for header in headers:
        col_widths[header] = len(header)
    
    for row in data:
        if isinstance(row, dict):
            for header in headers:
                value = str(row.get(header, ''))
                col_widths[header] = max(col_widths[header], len(value))
    
    # Створити таблицю
    lines = []
    
    # Заголовки
    header_line = " | ".join(f"{header:<{col_widths[header]}}" for header in headers)
    lines.append(header_line)
    lines.append("-" * len(header_line))
    
    # Дані
    for row in data:
        if isinstance(row, dict):
            row_line = " | ".join(f"{str(row.get(header, '')):<{col_widths[header]}}" for header in headers)
            lines.append(row_line)
    
    return '\n'.join(lines)


def format_hex(data: bytes, width: int = 16) -> str:
    # Форматувати байти в hex
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{byte:02x}' for byte in chunk)
        ascii_part = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in chunk)
        lines.append(f"{i:08x}  {hex_part:<{width*3-1}}  {ascii_part}")
    
    return '\n'.join(lines)


def format_binary(data: bytes, width: int = 8) -> str:
    # Форматувати байти в бінарний вигляд
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        binary_part = ' '.join(f'{byte:08b}' for byte in chunk)
        lines.append(f"{i:08x}  {binary_part}")
    
    return '\n'.join(lines)


def defragment_text(text: str, max_line_length: int = 80) -> str:
    # Дефрагментація тексту - перенесення довгих рядків
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line) + len(word) + 1 <= max_line_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return '\n'.join(lines)


def defragment_json(json_str: str) -> str:
    # Дефрагментація JSON - красиве форматування
    data = json.loads(json_str)
    return format_json_pretty(data)


def defragment_code(code: str, language: str = "python") -> str:
    # Дефрагментація коду - базове форматування
    lines = code.split('\n')
    formatted_lines = []
    
    for line in lines:
        stripped = line.strip()
        if stripped:
            formatted_lines.append(stripped)
    
    return '\n'.join(formatted_lines)


# Швидкі функції
def fmt_size(bytes_value: Union[int, float]) -> str:
    return format_bytes(bytes_value)

def fmt_time(seconds: Union[int, float]) -> str:
    return format_time(seconds)

def fmt_percent(value: Union[int, float]) -> str:
    return format_percentage(value)

def fmt_timestamp(timestamp: Union[datetime, float, str]) -> str:
    return format_timestamp(timestamp)


# Константи форматування
LCARS_TIME_FORMAT = "%H:%M:%S"
LCARS_DATE_FORMAT = "%Y-%m-%d"
LCARS_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Кольори для статусів
LCARS_COLORS = {
    "INFO": "#99FF99",
    "WARNING": "#FF9966",
    "ERROR": "#FF6666", 
    "SUCCESS": "#66FF66",
    "CRITICAL": "#FF0000",
    "PRIMARY": "#3366CC",
    "SECONDARY": "#00CCCC",
    "ACCENT": "#FFCC99"
}
