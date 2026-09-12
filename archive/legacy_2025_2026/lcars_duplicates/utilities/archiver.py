# LCARS Framework :: Archiver v1.0.0
# Утиліта архівації файлів та директорій
# Автор: LCARS Development Team
# Ліцензія: MIT

import shutil
from sys import version
import zipfile
import tarfile
import gzip
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from dataclasses import dataclass
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Archiver v{version}")  # Вимкнено для UI
@dataclass
class ArchiveInfo:
    # Інформація про архів
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name
        self.size = path.stat().st_size if path.exists() else 0
        self.created = datetime.fromtimestamp(path.stat().st_ctime) if path.exists() else None
        self.modified = datetime.fromtimestamp(path.stat().st_mtime) if path.exists() else None
        self.format = self._detect_format()
        self.compressed = self._is_compressed()
        self.files_count = 0
        self.total_size = 0
        
        if path.exists():
            self._analyze_archive()
    
    def _detect_format(self) -> str:
        # Виявити формат архіву
        suffix = self.path.suffix.lower()
        
        if suffix == '.zip':
            return 'zip'
        elif suffix in ['.tar', '.tar.gz', '.tgz']:
            return 'tar'
        elif suffix == '.gz':
            return 'gzip'
        elif suffix in ['.bz2', '.tbz2']:
            return 'bzip2'
        elif suffix in ['.xz', '.txz']:
            return 'xz'
        else:
            return 'unknown'
    
    def _is_compressed(self) -> bool:
        # Перевірити чи архів стиснутий
        return self.format in ['zip', 'gzip', 'bzip2', 'xz', 'tar']
    
    def _analyze_archive(self):
        # Проаналізувати архів
        try:
            if self.format == 'zip':
                with zipfile.ZipFile(self.path, 'r') as zf:
                    self.files_count = len(zf.namelist())
                    self.total_size = sum(info.file_size for info in zf.filelist)
            elif self.format == 'tar':
                with tarfile.open(self.path, 'r:*') as tf:
                    self.files_count = len(tf.getnames())
                    self.total_size = sum(info.size for info in tf.getmembers())
        except:
            pass
    
    def get_summary(self) -> Dict[str, Any]:
        # Отримати підсумок
        return {
            'name': self.name,
            'path': str(self.path),
            'size': self.size,
            'format': self.format,
            'compressed': self.compressed,
            'files_count': self.files_count,
            'total_size': self.total_size,
            'compression_ratio': (1 - self.size / self.total_size) if self.total_size > 0 else 0,
            'created': self.created,
            'modified': self.modified
        }


class Archiver:
    # Основний клас архіватора
    def __init__(self):
        self.supported_formats = ['zip', 'tar', 'gzip', 'bzip2', 'xz']
        self.default_archive_dir = Path.cwd() / 'archives'
    
    def create_archive(self, source: Union[str, Path], 
                     destination: Union[str, Path] = None,
                     format_type: str = 'zip',
                     compression_level: int = 6,
                     exclude_patterns: List[str] = None,
                     include_hidden: bool = False) -> str:
        # Створити архів
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Визначити шлях призначення
        if destination:
            dest_path = Path(destination)
            if dest_path.is_dir():
                archive_name = f"{source_path.name}.{format_type}"
                archive_path = dest_path / archive_name
            else:
                archive_path = dest_path
        else:
            self.default_archive_dir.mkdir(exist_ok=True)
            archive_name = f"{source_path.name}.{format_type}"
            archive_path = self.default_archive_dir / archive_name
        
        # Створити архів залежно від формату
        if format_type == 'zip':
            self._create_zip(source_path, archive_path, compression_level, exclude_patterns, include_hidden)
        elif format_type == 'tar':
            self._create_tar(source_path, archive_path, exclude_patterns, include_hidden)
        elif format_type == 'gzip':
            self._create_gzip(source_path, archive_path, compression_level, exclude_patterns, include_hidden)
        elif format_type == 'bzip2':
            self._create_bzip2(source_path, archive_path, exclude_patterns, include_hidden)
        elif format_type == 'xz':
            self._create_xz(source_path, archive_path, exclude_patterns, include_hidden)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return str(archive_path)
    
    def _create_zip(self, source_path: Path, archive_path: Path, 
                   compression_level: int, exclude_patterns: List[str], include_hidden: bool):
        # Створити ZIP архів
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zf:
            for item in self._get_items_to_archive(source_path, exclude_patterns, include_hidden):
                if item.is_file():
                    zf.write(item, item.relative_to(source_path))
                elif item.is_dir():
                    for file_path in item.rglob('*'):
                        if file_path.is_file():
                            zf.write(file_path, file_path.relative_to(source_path))
    
    def _create_tar(self, source_path: Path, archive_path: Path,
                   exclude_patterns: List[str], include_hidden: bool):
        # Створити TAR архів
        with tarfile.open(archive_path, 'w') as tf:
            for item in self._get_items_to_archive(source_path, exclude_patterns, include_hidden):
                tf.add(item, arcname=item.relative_to(source_path))
    
    def _create_gzip(self, source_path: Path, archive_path: Path,
                    compression_level: int, exclude_patterns: List[str], include_hidden: bool):
        # Створити GZIP архів
        if source_path.is_file():
            with open(source_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
        else:
            # Для директорій створюємо tar.gz
            tar_path = archive_path.with_suffix('.tar')
            self._create_tar(source_path, tar_path, exclude_patterns, include_hidden)
            
            with open(tar_path, 'rb') as f_in:
                with gzip.open(archive_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            tar_path.unlink()
    
    def _create_bzip2(self, source_path: Path, archive_path: Path,
                     exclude_patterns: List[str], include_hidden: bool):
        # Створити BZIP2 архів
        if source_path.is_file():
            with open(source_path, 'rb') as f_in:
                with tarfile.open(archive_path, 'w:bz2') as tf:
                    tf.add(source_path, arcname=source_path.name)
        else:
            with tarfile.open(archive_path, 'w:bz2') as tf:
                for item in self._get_items_to_archive(source_path, exclude_patterns, include_hidden):
                    tf.add(item, arcname=item.relative_to(source_path))
    
    def _create_xz(self, source_path: Path, archive_path: Path,
                   exclude_patterns: List[str], include_hidden: bool):
        # Створити XZ архів
        if source_path.is_file():
            with open(source_path, 'rb') as f_in:
                with tarfile.open(archive_path, 'w:xz') as tf:
                    tf.add(source_path, arcname=source_path.name)
        else:
            with tarfile.open(archive_path, 'w:xz') as tf:
                for item in self._get_items_to_archive(source_path, exclude_patterns, include_hidden):
                    tf.add(item, arcname=item.relative_to(source_path))
    
    def extract_archive(self, archive_path: Union[str, Path],
                      destination: Union[str, Path] = None,
                      overwrite: bool = False) -> List[str]:
        # Розпакувати архів
        archive_file = Path(archive_path)
        if not archive_file.exists():
            raise FileNotFoundError(f"Archive not found: {archive_path}")
        
        # Визначити шлях розпакування
        if destination:
            extract_path = Path(destination)
        else:
            extract_path = archive_file.parent / archive_file.stem
        
        extract_path.mkdir(parents=True, exist_ok=True)
        
        # Розпакувати залежно від формату
        archive_info = ArchiveInfo(archive_file)
        extracted_files = []
        
        if archive_info.format == 'zip':
            extracted_files = self._extract_zip(archive_file, extract_path, overwrite)
        elif archive_info.format == 'tar':
            extracted_files = self._extract_tar(archive_file, extract_path, overwrite)
        elif archive_info.format == 'gzip':
            extracted_files = self._extract_gzip(archive_file, extract_path, overwrite)
        elif archive_info.format == 'bzip2':
            extracted_files = self._extract_bzip2(archive_file, extract_path, overwrite)
        elif archive_info.format == 'xz':
            extracted_files = self._extract_xz(archive_file, extract_path, overwrite)
        else:
            raise ValueError(f"Unsupported archive format: {archive_info.format}")
        
        return extracted_files
    
    def _extract_zip(self, archive_path: Path, extract_path: Path, overwrite: bool) -> List[str]:
        # Розпакувати ZIP
        extracted_files = []
        
        with zipfile.ZipFile(archive_path, 'r') as zf:
            for member in zf.namelist():
                file_path = extract_path / member
                
                if not overwrite and file_path.exists():
                    continue
                
                zf.extract(member, extract_path)
                extracted_files.append(str(file_path))
        
        return extracted_files
    
    def _extract_tar(self, archive_path: Path, extract_path: Path, overwrite: bool) -> List[str]:
        # Розпакувати TAR
        extracted_files = []
        
        with tarfile.open(archive_path, 'r:*') as tf:
            for member in tf.getmembers():
                file_path = extract_path / member.name
                
                if not overwrite and file_path.exists():
                    continue
                
                tf.extract(member, extract_path)
                extracted_files.append(str(file_path))
        
        return extracted_files
    
    def _extract_gzip(self, archive_path: Path, extract_path: Path, overwrite: bool) -> List[str]:
        # Розпакувати GZIP
        output_file = extract_path / archive_path.stem
        
        if not overwrite and output_file.exists():
            return []
        
        with gzip.open(archive_path, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return [str(output_file)]
    
    def _extract_bzip2(self, archive_path: Path, extract_path: Path, overwrite: bool) -> List[str]:
        # Розпакувати BZIP2
        extracted_files = []
        
        with tarfile.open(archive_path, 'r:bz2') as tf:
            for member in tf.getmembers():
                file_path = extract_path / member.name
                
                if not overwrite and file_path.exists():
                    continue
                
                tf.extract(member, extract_path)
                extracted_files.append(str(file_path))
        
        return extracted_files
    
    def _extract_xz(self, archive_path: Path, extract_path: Path, overwrite: bool) -> List[str]:
        # Розпакувати XZ
        extracted_files = []
        
        with tarfile.open(archive_path, 'r:xz') as tf:
            for member in tf.getmembers():
                file_path = extract_path / member.name
                
                if not overwrite and file_path.exists():
                    continue
                
                tf.extract(member, extract_path)
                extracted_files.append(str(file_path))
        
        return extracted_files
    
    def _get_items_to_archive(self, source_path: Path, 
                             exclude_patterns: List[str], include_hidden: bool) -> List[Path]:
        # Отримати елементи для архівації
        items = []
        exclude_patterns = exclude_patterns or []
        
        for item in source_path.rglob('*'):
            # Пропустити приховані файли
            if not include_hidden and item.name.startswith('.'):
                continue
            
            # Перевірити патерни виключення
            should_exclude = False
            for pattern in exclude_patterns:
                if item.match(pattern):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
            
            items.append(item)
        
        return items
    
    def list_archive_contents(self, archive_path: Union[str, Path]) -> List[Dict[str, Any]]:
        # Список вмісту архіву
        archive_file = Path(archive_path)
        archive_info = ArchiveInfo(archive_file)
        contents = []
        
        if archive_info.format == 'zip':
            with zipfile.ZipFile(archive_file, 'r') as zf:
                for info in zf.filelist:
                    contents.append({
                        'name': info.filename,
                        'size': info.file_size,
                        'compressed_size': info.compress_size,
                        'date': datetime(*info.date_time),
                        'is_dir': info.is_dir()
                    })
        
        elif archive_info.format == 'tar':
            with tarfile.open(archive_file, 'r:*') as tf:
                for member in tf.getmembers():
                    contents.append({
                        'name': member.name,
                        'size': member.size,
                        'date': datetime.fromtimestamp(member.mtime),
                        'is_dir': member.isdir(),
                        'mode': member.mode
                    })
        
        return contents
    
    def get_archive_info(self, archive_path: Union[str, Path]) -> ArchiveInfo:
        # Отримати інформацію про архів
        return ArchiveInfo(Path(archive_path))
    
    def verify_archive(self, archive_path: Union[str, Path]) -> bool:
        # Перевірити цілісність архіву
        archive_file = Path(archive_path)
        archive_info = ArchiveInfo(archive_file)
        
        try:
            if archive_info.format == 'zip':
                with zipfile.ZipFile(archive_file, 'r') as zf:
                    zf.testzip()
            elif archive_info.format == 'tar':
                with tarfile.open(archive_file, 'r:*') as tf:
                    tf.getmembers()
            
            return True
        except:
            return False
    
    def compress_archive(self, source_archive: Union[str, Path],
                      target_format: str = 'zip',
                      compression_level: int = 6) -> str:
        # Перестиснути архів в інший формат
        source_path = Path(source_archive)
        
        # Створити тимчасову директорію
        temp_dir = source_path.parent / 'temp_extract'
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # Розпакувати вихідний архів
            self.extract_archive(source_path, temp_dir)
            
            # Створити новий архів
            target_name = f"{source_path.stem}.{target_format}"
            target_path = source_path.parent / target_name
            
            self.create_archive(temp_dir, target_path, target_format, compression_level)
            
            return str(target_path)
        finally:
            # Очистити тимчасову директорію
            if temp_dir.exists():
                shutil.rmtree(temp_dir)


# Швидкі функції
def archive(source: Union[str, Path], 
           destination: Union[str, Path] = None,
           format_type: str = 'zip') -> str:
    archiver = Archiver()
    return archiver.create_archive(source, destination, format_type)

def extract(archive_path: Union[str, Path],
           destination: Union[str, Path] = None) -> List[str]:
    archiver = Archiver()
    return archiver.extract_archive(archive_path, destination)

def list_archive(archive_path: Union[str, Path]) -> List[Dict[str, Any]]:
    archiver = Archiver()
    return archiver.list_archive_contents(archive_path)

def verify(archive_path: Union[str, Path]) -> bool:
    archiver = Archiver()
    return archiver.verify_archive(archive_path)

def get_info(archive_path: Union[str, Path]) -> ArchiveInfo:
    archiver = Archiver()
    return archiver.get_archive_info(archive_path)

# Константи
SUPPORTED_FORMATS = ['zip', 'tar', 'gzip', 'bzip2', 'xz']
DEFAULT_COMPRESSION_LEVEL = 6
DEFAULT_ARCHIVE_DIR = 'archives'
COMMON_EXCLUDE_PATTERNS = [
    '*.pyc', '*.pyo', '__pycache__', '.git', '.svn', '.hg',
    '*.tmp', '*.log', '*.bak', '*~'
]
