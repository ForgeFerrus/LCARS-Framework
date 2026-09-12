from __future__ import annotations

import shutil
import time
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
Ignored = {".git", ".venv", ".idea", ".vscode", "node_modules"}


def FindCacheNodes():
    # Знайти всі каталоги __pycache__ у проєкті, пропускаючи служби та налаштування.
    return [
        PathItem for PathItem in ProjectRoot.rglob("__pycache__")
        if PathItem.is_dir() and not any(Part in Ignored for Part in PathItem.parts)
    ]


def PurgeCaches():
    Removed = []
    for PathItem in FindCacheNodes():
        shutil.rmtree(PathItem)
        Removed.append(str(PathItem.relative_to(ProjectRoot)))
    return Removed


def Main(poll_seconds: float = 0.5):
    print(f"◤ CACHE SENTINEL :: WATCHING {ProjectRoot}")
    print(f"◤ CACHE SENTINEL :: INTERVAL = {poll_seconds} sec")
    print("◤ CACHE SENTINEL :: STARTED")
    while True:
        Removed = PurgeCaches()
        if Removed:
            for Item in Removed:
                print(f"◤ CACHE SENTINEL :: PURGED {Item}")
        time.sleep(poll_seconds)


if __name__ == "__main__":
    Main()
