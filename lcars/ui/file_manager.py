"""Simple File Manager UI placeholder.

UKR: Плейсхолдер для файлового менеджера. Пізніше підключимо повний
ProjectManager для роботи з реальними проєктами та шляхами.
"""
from __future__ import annotations

# Titanium Bridge Migration: from typing import List
# Titanium Bridge Migration: from pathlib import Path


class FileManager:
    """Надає базові операції над файлами для UI.

    Методи:
      - `list_files(path)` -> List[Path]
      - `read_text(path)` -> str
    """

    def list_files(self, path: str) -> List[Path]:
        p = Path(path)
        if not p.exists():
            return []
        return [x for x in p.iterdir() if x.is_file()]

    def read_text(self, path: str) -> str:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(path)
        return p.read_text(encoding='utf-8')
