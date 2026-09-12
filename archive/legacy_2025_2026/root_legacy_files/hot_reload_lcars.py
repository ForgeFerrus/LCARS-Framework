#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hot Reload System for LCARS Desktop
Автоматично перезапускає LCARS при зміні коду
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LCARSReloadHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_reload = time.time()
        
    def on_modified(self, event):
        # Ігноруємо зміни в тимчасових файлах та __pycache__
        if '__pycache__' in event.src_path or event.src_path.endswith('.tmp'):
            return
            
        # Перезапуск тільки якщо зміни в .py файлах
        if event.src_path.endswith('.py'):
            # Запобігаємо частим перезапускам
            current_time = time.time()
            if current_time - self.last_reload < 2:
                return
            self.last_reload = current_time
            
            print(f"Hot reload: Змінено {event.src_path}")
            self.restart_callback()

def start_lcars_with_hot_reload():
    """Запустити LCARS з hot reload"""
    project_root = Path(__file__).parent
    
    def restart_lcars():
        """Перезапустити LCARS"""
        print("Перезапуск LCARS...")
        
        # Закриваємо попередній процес
        if hasattr(restart_lcars, 'lcars_process'):
            try:
                restart_lcars.lcars_process.terminate()
                restart_lcars.lcars_process.wait(timeout=5)
            except:
                pass
        
        # Запускаємо новий процес
        try:
            # Використовуємо simple_loader.py
            script_path = project_root / "lcars" / "ui" / "simple_loader.py"
            restart_lcars.lcars_process = subprocess.Popen([
                sys.executable, str(script_path)
            ], cwd=project_root / "lcars" / "ui")
            print("LCARS перезапущено")
        except Exception as e:
            print(f"Помилка перезапуску: {e}")
    
    # Запускаємо спостерігач за файлами
    event_handler = LCARSReloadHandler(restart_lcars)
    observer = Observer()
    
    # Спостерігаємо за папками з кодом
    paths_to_watch = [
        project_root / "lcars" / "ui",
        project_root / "lcars" / "themes",
        project_root / "lcars" / "core"
    ]
    
    for path in paths_to_watch:
        if path.exists():
            observer.schedule(event_handler, str(path), recursive=True)
            print(f"Спостерігаємо за: {path}")
    
    observer.start()
    
    # Перший запуск
    restart_lcars()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗупинка hot reload...")
        observer.stop()
        
        # Закриваємо LCARS
        if hasattr(restart_lcars, 'lcars_process'):
            try:
                restart_lcars.lcars_process.terminate()
            except:
                pass
    
    observer.join()

if __name__ == "__main__":
    print("LCARS Hot Reload System v1.0")
    print("Зміни в .py файлах автоматично перезапустять систему")
    print("Натисніть Ctrl+C для виходу")
    
    start_lcars_with_hot_reload()
