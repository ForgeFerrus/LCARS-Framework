# LCARS Framework :: Ship's Logbook v1.0.0
# Бортовий журнал системи
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

import os
import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from hashlib import md5
import threading
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Ship's Logbook v{version}")  # Вимкнено для UI

class Logbook:
    # Бортовий журнал LCARS
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / '.lcars_logbook.db')
        
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        # Ініціалізація бази даних
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS logbook (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    action TEXT NOT NULL,
                    hash_before TEXT,
                    hash_after TEXT,
                    size_before INTEGER,
                    size_after INTEGER,
                    metadata TEXT,
                    reported INTEGER DEFAULT 0
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    content_size INTEGER,
                    metadata TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_file_path ON logbook(file_path)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON logbook(timestamp)
            ''')
    
    def _calculate_hash(self, file_path: str) -> Optional[str]:
        # Розрахувати хеш файлу
        if not Path(file_path).exists():
            return None
        
        with open(file_path, 'rb') as f:
            return md5(f.read()).hexdigest()
    
    def _get_file_size(self, file_path: str) -> Optional[int]:
        # Розмір файлу
        if not Path(file_path).exists():
            return None
        
        return Path(file_path).stat().st_size
    
    def log_change(self, file_path: str, action: str, metadata: Optional[Dict] = None):
        # Записати зміну файлу
        with self.lock:
            file_path = str(Path(file_path).resolve())
            timestamp = datetime.now().isoformat()
            
            hash_before = self._calculate_hash(file_path)
            size_before = self._get_file_size(file_path)
            
            # Записуємо зміну
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO logbook 
                    (timestamp, file_path, action, hash_before, size_before, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (timestamp, file_path, action, hash_before, size_before, 
                      json.dumps(metadata) if metadata else None))
            
            # Створюємо снепшот файлу
            self._create_snapshot(file_path, timestamp)
    
    def _create_snapshot(self, file_path: str, timestamp: str):
        # Створити снепшот файлу
        if not Path(file_path).exists():
            return
        
        content_hash = self._calculate_hash(file_path)
        content_size = self._get_file_size(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO file_snapshots 
                (file_path, timestamp, content_hash, content_size)
                VALUES (?, ?, ?, ?)
            ''', (file_path, timestamp, content_hash, content_size))
    
    def monitor_file(self, file_path: str):
        # Почати моніторинг файлу
        file_path = str(Path(file_path).resolve())
        
        if not Path(file_path).exists():
            self.log_change(file_path, 'MONITOR_STARTED', {'status': 'file_not_found'})
            return
        
        # Записуємо початковий стан
        self.log_change(file_path, 'MONITOR_STARTED', {
            'initial_hash': self._calculate_hash(file_path),
            'initial_size': self._get_file_size(file_path)
        })
    
    def check_changes(self, file_path: str) -> Dict:
        # Перевірити зміни файлу
        file_path = str(Path(file_path).resolve())
        
        if not Path(file_path).exists():
            return {'changed': False, 'status': 'file_not_found'}
        
        current_hash = self._calculate_hash(file_path)
        current_size = self._get_file_size(file_path)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT hash_before, size_before FROM logbook 
                WHERE file_path = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (file_path,))
            
            last_record = cursor.fetchone()
            
            if last_record:
                last_hash, last_size = last_record
                changed = (last_hash != current_hash or last_size != current_size)
                
                if changed:
                    self.log_change(file_path, 'CHANGED', {
                        'previous_hash': last_hash,
                        'current_hash': current_hash,
                        'size_change': current_size - last_size if last_size and current_size else None
                    })
                
                return {
                    'changed': changed,
                    'current_hash': current_hash,
                    'current_size': current_size,
                    'last_hash': last_hash,
                    'last_size': last_size
                }
        
        return {'changed': True, 'status': 'first_check'}
    
    def get_file_history(self, file_path: str, limit: int = 50) -> List[Dict]:
        # Історія змін файлу
        file_path = str(Path(file_path).resolve())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, action, hash_before, hash_after, 
                       size_before, size_after, metadata
                FROM logbook 
                WHERE file_path = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (file_path, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'timestamp': row[0],
                    'action': row[1],
                    'hash_before': row[2],
                    'hash_after': row[3],
                    'size_before': row[4],
                    'size_after': row[5],
                    'metadata': json.loads(row[6]) if row[6] else None
                })
            
            return history
    
    def get_all_changes(self, limit: int = 100) -> List[Dict]:
        # Всі зміни в системі
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, file_path, action, hash_before, hash_after,
                       size_before, size_after, metadata
                FROM logbook 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            changes = []
            for row in cursor.fetchall():
                changes.append({
                    'timestamp': row[0],
                    'file_path': row[1],
                    'action': row[2],
                    'hash_before': row[3],
                    'hash_after': row[4],
                    'size_before': row[5],
                    'size_after': row[6],
                    'metadata': json.loads(row[7]) if row[7] else None
                })
            
            return changes
    
    def mark_reported(self, log_id: int):
        # Позначити як звітоване
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE logbook SET reported = 1 WHERE id = ?', (log_id,))
    
    def get_unreported_changes(self) -> List[Dict]:
        # Отримати незвітовані зміни
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT id, timestamp, file_path, action, metadata
                FROM logbook 
                WHERE reported = 0 
                ORDER BY timestamp ASC
            ''')
            
            unreported = []
            for row in cursor.fetchall():
                unreported.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'file_path': row[2],
                    'action': row[3],
                    'metadata': json.loads(row[4]) if row[4] else None
                })
            
            return unreported
    
    def generate_report(self, file_path: Optional[str] = None) -> Dict:
        # Згенерувати звіт
        if file_path:
            history = self.get_file_history(file_path)
            title = f"Logbook Report: {file_path}"
        else:
            history = self.get_all_changes()
            title = "Logbook Report: All Changes"
        
        report = {
            'title': title,
            'generated_at': datetime.now().isoformat(),
            'total_changes': len(history),
            'changes': history
        }
        
        return report
    
    def cleanup_old_records(self, days: int = 30):
        # Очистити старі записи
        cutoff_date = (datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM logbook WHERE timestamp < ?', (cutoff_date,))
            conn.execute('DELETE FROM file_snapshots WHERE timestamp < ?', (cutoff_date,))
    
    def get_statistics(self) -> Dict:
        # Статистика журналу
        with sqlite3.connect(self.db_path) as conn:
            # Загальна кількість записів
            cursor = conn.execute('SELECT COUNT(*) FROM logbook')
            total_records = cursor.fetchone()[0]
            
            # Кількість унікальних файлів
            cursor = conn.execute('SELECT COUNT(DISTINCT file_path) FROM logbook')
            unique_files = cursor.fetchone()[0]
            
            # Найактивніші файли
            cursor = conn.execute('''
                SELECT file_path, COUNT(*) as changes 
                FROM logbook 
                GROUP BY file_path 
                ORDER BY changes DESC 
                LIMIT 10
            ''')
            most_active = [{'file': row[0], 'changes': row[1]} for row in cursor.fetchall()]
            
            return {
                'total_records': total_records,
                'unique_files': unique_files,
                'most_active_files': most_active,
                'database_size': Path(self.db_path).stat().st_size if Path(self.db_path).exists() else 0
            }

class FileWatcher:
    # Спостерігач за файлами
    
    def __init__(self, logbook: Logbook):
        self.logbook = logbook
        self.watched_files = {}
        self.running = False
        self.thread = None
    
    def add_file(self, file_path: str):
        # Додати файл для спостереження
        file_path = str(Path(file_path).resolve())
        self.watched_files[file_path] = {
            'last_hash': self.logbook._calculate_hash(file_path),
            'last_size': self.logbook._get_file_size(file_path)
        }
        self.logbook.monitor_file(file_path)
    
    def remove_file(self, file_path: str):
        # Видалити файл зі спостереження
        file_path = str(Path(file_path).resolve())
        if file_path in self.watched_files:
            del self.watched_files[file_path]
    
    def start_watching(self, interval: int = 5):
        # Почати спостереження
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._watch_loop, args=(interval,))
            self.thread.daemon = True
            self.thread.start()
    
    def stop_watching(self):
        # Зупинити спостереження
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _watch_loop(self, interval: int):
        # Цикл спостереження
        import time as time_module
        
        while self.running:
            for file_path, last_state in list(self.watched_files.items()):
                current_hash = self.logbook._calculate_hash(file_path)
                current_size = self.logbook._get_file_size(file_path)
                
                if (current_hash != last_state['last_hash'] or 
                    current_size != last_state['last_size']):
                    
                    self.logbook.log_change(file_path, 'AUTO_DETECTED', {
                        'previous_hash': last_state['last_hash'],
                        'current_hash': current_hash,
                        'size_change': current_size - last_state['last_size'] if last_state['last_size'] and current_size else None
                    })
                    
                    self.watched_files[file_path] = {
                        'last_hash': current_hash,
                        'last_size': current_size
                    }
            
            time_module.sleep(interval)

# Глобальний екземпляр
logbook = Logbook()
watcher = FileWatcher(logbook)

# Швидкі функції
def log_file_change(file_path: str, action: str, metadata: Optional[Dict] = None):
    logbook.log_change(file_path, action, metadata)

def monitor_file(file_path: str):
    logbook.monitor_file(file_path)

def get_file_log(file_path: str) -> List[Dict]:
    return logbook.get_file_history(file_path)

def generate_log_report(file_path: Optional[str] = None) -> Dict:
    return logbook.generate_report(file_path)
