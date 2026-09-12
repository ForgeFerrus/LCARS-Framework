# LCARS Framework :: File Utils v1.0.0
# Утиліти роботи з файловою системою
# Автор: LCARS Development Team
# Ліцензія: MIT

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Проста версія без getVersion
version = "1.0.0"
# print(f"LCARS File Utils v{version}")  # Вимкнено для UI


def find_files(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
    # Знайти файли за шаблоном
    path = Path(directory)
    if not path.exists():
        return []
    
    if recursive:
        matches = list(path.glob(f"**/{pattern}"))
    else:
        matches = list(path.glob(pattern))
    
    return [str(m) for m in matches if m.is_file()]


def find_directories(directory: str, pattern: str = "*", recursive: bool = True) -> List[str]:
    # Знайти директорії за шаблоном
    path = Path(directory)
    if not path.exists():
        return []
    
    if recursive:
        matches = list(path.glob(f"**/{pattern}"))
    else:
        matches = list(path.glob(pattern))
    
    return [str(m) for m in matches if m.is_dir()]


def get_file_info(file_path: str) -> Dict[str, Any]:
    # Отримати інформацію про файл
    path = Path(file_path)
    if not path.exists():
        return {}
    
    stat = path.stat()
    
    return {
        'path': str(path),
        'name': path.name,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'created': datetime.fromtimestamp(stat.st_ctime),
        'modified': datetime.fromtimestamp(stat.st_mtime),
        'accessed': datetime.fromtimestamp(stat.st_atime),
        'is_file': path.is_file(),
        'is_dir': path.is_dir(),
        'extension': path.suffix.lower(),
        'parent': str(path.parent)
    }


def list_directory(directory: str, show_hidden: bool = False) -> List[Dict[str, Any]]:
    # Список файлів і директорій
    path = Path(directory)
    if not path.exists():
        return []
    
    items = []
    for item in path.iterdir():
        if not show_hidden and item.name.startswith('.'):
            continue
        
        items.append(get_file_info(str(item)))
    
    return sorted(items, key=lambda x: (not x['is_dir'], x['name'].lower()))


def copy_file(source: str, destination: str, overwrite: bool = False) -> bool:
    # Копіювати файл
    src = Path(source)
    dst = Path(destination)
    
    if not src.exists():
        return False
    
    if dst.exists() and not overwrite:
        return False
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def move_file(source: str, destination: str, overwrite: bool = False) -> bool:
    # Перемістити файл
    src = Path(source)
    dst = Path(destination)
    
    if not src.exists():
        return False
    
    if dst.exists() and not overwrite:
        return False
    
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return True


def delete_file(file_path: str) -> bool:
    # Видалити файл
    path = Path(file_path)
    if not path.exists():
        return False
    
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(str(path))
    
    return True


def create_directory(directory: str, parents: bool = True) -> bool:
    # Створити директорію
    path = Path(directory)
    path.mkdir(parents=parents, exist_ok=True)
    return path.exists()


def get_directory_size(directory: str) -> int:
    # Отримати розмір директорії
    path = Path(directory)
    if not path.exists():
        return 0
    
    total_size = 0
    for item in path.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
    
    return total_size


def format_file_size(size_bytes: int) -> str:
    # Форматувати розмір файлу
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.2f} {units[unit_index]}"


def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    # Обчислити хеш файлу
    path = Path(file_path)
    if not path.exists():
        return ""
    
    hash_func = hashlib.new(algorithm)
    
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    
    return hash_func.hexdigest()


def compare_files(file1: str, file2: str) -> bool:
    # Порівняти файли
    path1 = Path(file1)
    path2 = Path(file2)
    
    if not path1.exists() or not path2.exists():
        return False
    
    if path1.stat().st_size != path2.stat().st_size:
        return False
    
    return calculate_file_hash(file1) == calculate_file_hash(file2)


def find_duplicate_files(directory: str) -> Dict[str, List[str]]:
    # Знайти дублікати файлів
    path = Path(directory)
    if not path.exists():
        return {}
    
    file_hashes = {}
    
    for file_path in path.rglob('*'):
        if file_path.is_file():
            file_hash = calculate_file_hash(str(file_path))
            if file_hash not in file_hashes:
                file_hashes[file_hash] = []
            file_hashes[file_hash].append(str(file_path))
    
    # Повернути тільки дублікати
    duplicates = {hash_val: files for hash_val, files in file_hashes.items() if len(files) > 1}
    return duplicates


def clean_directory(directory: str, keep_patterns: List[str] = None) -> int:
    # Очистити директорію
    path = Path(directory)
    if not path.exists():
        return 0
    
    keep_patterns = keep_patterns or []
    deleted_count = 0
    
    for item in path.iterdir():
        should_keep = False
        for pattern in keep_patterns:
            if item.match(pattern):
                should_keep = True
                break
        
        if not should_keep:
            if delete_file(str(item)):
                deleted_count += 1
    
    return deleted_count


def backup_file(file_path: str, backup_dir: str = None) -> str:
    # Створити бекап файлу
    path = Path(file_path)
    if not path.exists():
        return ""
    
    if backup_dir is None:
        backup_dir = path.parent / "backups"
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.stem}_{timestamp}{path.suffix}"
    backup_file_path = backup_path / backup_name
    
    if copy_file(str(path), str(backup_file_path)):
        return str(backup_file_path)
    
    return ""


def restore_file(backup_path: str, original_path: str) -> bool:
    # Відновити файл з бекапу
    return copy_file(backup_path, original_path, overwrite=True)


def compress_files(file_paths: List[str], archive_path: str) -> bool:
    # Створити архів
    import zipfile
    
    archive_path = Path(archive_path)
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in file_paths:
            path = Path(file_path)
            if path.exists():
                zipf.write(path, path.name)
    
    return archive_path.exists()


def extract_files(archive_path: str, extract_dir: str) -> bool:
    # Розпакувати архів
    import zipfile
    
    archive_path = Path(archive_path)
    extract_dir = Path(extract_dir)
    
    if not archive_path.exists():
        return False
    
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        zipf.extractall(extract_dir)
    
    return True


def sync_directories(source: str, destination: str) -> Dict[str, Any]:
    # Синхронізувати директорії
    src = Path(source)
    dst = Path(destination)
    
    if not src.exists():
        return {'success': False, 'message': 'Source directory does not exist'}
    
    dst.mkdir(parents=True, exist_ok=True)
    
    copied = 0
    updated = 0
    deleted = 0
    
    # Копіювати нові файли
    for src_file in src.rglob('*'):
        if src_file.is_file():
            dst_file = dst / src_file.relative_to(src)
            
            if not dst_file.exists():
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if copy_file(str(src_file), str(dst_file)):
                    copied += 1
            elif src_file.stat().st_mtime > dst_file.stat().st_mtime:
                if copy_file(str(src_file), str(dst_file), overwrite=True):
                    updated += 1
    
    return {
        'success': True,
        'copied': copied,
        'updated': updated,
        'deleted': deleted
    }


def get_file_type(file_path: str) -> str:
    # Визначити тип файлу
    path = Path(file_path)
    if not path.exists():
        return "unknown"
    
    if path.is_dir():
        return "directory"
    
    extension = path.suffix.lower()
    
    type_mapping = {
        '.txt': 'text',
        '.py': 'python',
        '.js': 'javascript',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.xml': 'xml',
        '.csv': 'csv',
        '.pdf': 'pdf',
        '.doc': 'document',
        '.docx': 'document',
        '.xls': 'spreadsheet',
        '.xlsx': 'spreadsheet',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.mp3': 'audio',
        '.wav': 'audio',
        '.mp4': 'video',
        '.avi': 'video',
        '.mkv': 'video',
        '.zip': 'archive',
        '.rar': 'archive',
        '.tar': 'archive',
        '.gz': 'archive'
    }
    
    return type_mapping.get(extension, 'unknown')


# Швидкі функції
def find(file_path: str, pattern: str = "*") -> List[str]:
    return find_files(file_path, pattern)

def info(file_path: str) -> Dict[str, Any]:
    return get_file_info(file_path)

def ls(directory: str) -> List[Dict[str, Any]]:
    return list_directory(directory)

def cp(source: str, destination: str) -> bool:
    return copy_file(source, destination)

def mv(source: str, destination: str) -> bool:
    return move_file(source, destination)

def rm(file_path: str) -> bool:
    return delete_file(file_path)

def mkdir(directory: str) -> bool:
    return create_directory(directory)

def size(directory: str) -> int:
    return get_directory_size(directory)

def create_file_hash(file_path: str) -> str:
    # Створити хеш файлу
    path = Path(file_path)
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

# Константи
FILE_TYPES = {
    'text': ['.txt', '.md', '.rst'],
    'code': ['.py', '.js', '.java', '.cpp', '.c', '.h'],
    'web': ['.html', '.css', '.js', '.php'],
    'data': ['.json', '.xml', '.csv', '.yaml', '.yml'],
    'document': ['.pdf', '.doc', '.docx', '.odt'],
    'spreadsheet': ['.xls', '.xlsx', '.ods', '.csv'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
    'archive': ['.zip', '.rar', '.tar', '.gz', '.7z']
}
