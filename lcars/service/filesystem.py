# LCARS File System Service
# Файлова система як системний сервіс.

from __future__ import annotations
import shutil
from pathlib import Path
from typing import Any, List, Optional
from lcars.core.service import Service
from lcars.core.signal import ODN


class FileService(Service):
    # Системний сервіс файлових операцій.
    Name = "file"

    def __init__(self):
        super().__init__(Id="FileService")
        self.Root = Path.cwd()

    # Читання файлу
    def Read(self, PathStr: str) -> str:
        Target = self.Resolve(PathStr)
        if not Target.exists() or not Target.is_file():
            return ""
        return Target.read_text(encoding="utf-8")

    # Запис файлу
    def Write(self, PathStr: str, Data: Any) -> bool:
        Target = self.Resolve(PathStr)
        Target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(Data, (dict, list)):
            import json
            Target.write_text(json.dumps(Data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        else:
            Target.write_text(str(Data), encoding="utf-8")
        return True

    # Список файлів у директорії
    def List(self, PathStr: str) -> List[str]:
        Target = self.Resolve(PathStr)
        if not Target.exists() or not Target.is_dir():
            return []
        return [P.name for P in Target.iterdir()]

    # Перевірка існування
    def Exists(self, PathStr: str) -> bool:
        Target = self.Resolve(PathStr)
        return Target.exists()

    # Видалення файлу/директорії
    def Delete(self, PathStr: str) -> bool:
        Target = self.Resolve(PathStr)
        if not Target.exists():
            return False
        if Target.is_dir():
            shutil.rmtree(Target)
        else:
            Target.unlink()
        return True

    # Копіювання
    def Copy(self, Src: str, Dst: str) -> bool:
        Source = self.Resolve(Src)
        Dest = self.Resolve(Dst)
        if not Source.exists():
            return False
        if Source.is_dir():
            shutil.copytree(Source, Dest, dirs_exist_ok=True)
        else:
            Dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(Source, Dest)
        return True

    # Статистика (розмір, тип, час)
    def Stat(self, PathStr: str) -> Optional[dict]:
        Target = self.Resolve(PathStr)
        if not Target.exists():
            return None
        St = Target.stat()
        return {
            "size": St.st_size,
            "isDir": Target.is_dir(),
            "isFile": Target.is_file(),
            "modified": St.st_mtime,
        }

    # Нормалізація шляху відносно кореня
    def Resolve(self, PathStr: str) -> Path:
        P = Path(PathStr)
        if not P.is_absolute():
            P = self.Root / P
        return P.resolve()


__all__ = ["FileService"]