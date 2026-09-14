# ◤ SENTINEL :: LCARS АВТОНОМНИЙ СЕНТІНЕЛ-ОЧИЩУВАЧ ТА ВАРТОВИЙ 🖖
# =============================================================================
# ПРИЗНАЧЕННЯ: Автоматичне фонове знищення будь-яких кешів (__pycache__, *.pyc)
# ПРИНЦИП: Titanium Standard (Zero-Except, Strict PascalCase, Pure LCARS)
# =============================================================================
import os
import sys
import time
import shutil
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
IgnoredDirectories = {".git", ".venv", ".idea", ".vscode", "node_modules", "archive", "data"}

# Пошук усіх директорій кешу
def FindCacheDirectories(RootNode: Path):
    CacheDirs = []
    if not RootNode.exists() or not RootNode.is_dir():
        return CacheDirs

    for DirPath, DirNames, _ in os.walk(str(RootNode)):
        PathSegments = Path(DirPath).parts
        if any(Ignored in PathSegments for Ignored in IgnoredDirectories):
            continue

        for Item in list(DirNames):
            if Item in ("__pycache__", ".pytest_cache", ".cache"):
                Target = Path(DirPath) / Item
                if Target.exists() and Target.is_dir():
                    CacheDirs.append(Target)
                DirNames.remove(Item)
    return CacheDirs

# Очищення конкретної папки кешу
def PurgeDirectory(Target: Path):
    if not Target.exists() or not Target.is_dir():
        return None
    PathStr = str(Target)
    shutil.rmtree(PathStr, ignore_errors=True)
    if Target.exists():
        os.system(f'rmdir /s /q "{PathStr}" >nul 2>&1')
    return str(Target.relative_to(ProjectRoot)) if not Target.exists() else None

# Видалення файлів .pyc
def PurgeOrphanFiles(RootNode: Path):
    Count = 0
    if not RootNode.exists() or not RootNode.is_dir():
        return 0

    for DirPath, _, FileNames in os.walk(str(RootNode)):
        PathSegments = Path(DirPath).parts
        if any(Ignored in PathSegments for Ignored in IgnoredDirectories):
            continue

        for File in FileNames:
            if File.endswith(".pyc") or File.endswith(".pyo"):
                Target = Path(DirPath) / File
                if Target.exists() and Target.is_file():
                    try:
                        Target.unlink()
                        Count += 1
                    except Exception:
                        pass
    return Count

# Миттєве повне очищення кешу проекту
def PurgeNow():
    Purged = []
    for CacheDir in FindCacheDirectories(ProjectRoot):
        Result = PurgeDirectory(CacheDir)
        if Result:
            Purged.append(Result)
    Orphans = PurgeOrphanFiles(ProjectRoot)
    if Orphans > 0:
        Purged.append(f"{Orphans} orphan .pyc files")
    return Purged

# Фоновий сторожовий демон
def RunSentinelSubsystem(PollInterval: float = 1.0):
    import threading

    def Worker():
        while True:
            PurgeNow()
            time.sleep(PollInterval)

    Thread = threading.Thread(target=Worker, daemon=True, name="LCARSSentinelDaemon")
    Thread.start()
    return Thread

if __name__ == "__main__":
    Results = PurgeNow()
    if Results:
        for Item in Results:
            print(f"[SENTINEL PURGED] {Item}")
    else:
        print("[SENTINEL] Project clean. No caches detected.")
