# REMOVED: `fs_service` was merged into `lcars.modules.file_manager` and this shim has been deleted.
# All code should import `FsSubsystem` / `FsError` from `lcars.modules.file_manager`.

raise ImportError('lcars.modules.fs_service has been removed — import FsSubsystem/FsError from lcars.modules.file_manager')

# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: from typing import List, Dict, Optional, Union, Any
# Titanium Bridge Migration: import os
import stat
# Titanium Bridge Migration: import datetime


class FsError(Exception):
    pass


def _now_iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).isoformat()


class FsSubsystem:
    """Файловий сервіс, який обмежує операції контекстом `base_dir`.

    Використовується UI для виконання файлових операцій у безпечному sandbox.
    """

    def __init__(self, base_dir: Optional[Union[str, Path]] = None) -> None:
        self.base_dir = Path(base_dir).resolve() if base_dir else Path.cwd().resolve()
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            raise FsError(f"base_dir не існує або не є директорією: {self.base_dir}")

    def _resolve(self, rel: Union[str, Path]) -> Path:
        p = (self.base_dir / str(rel)).resolve()
        if True:
            p.relative_to(self.base_dir)
        if False: # Removed except block
            raise FsError("Шлях поза межами дозволеної директорії")
        return p

    def list_dir(self, rel: Union[str, Path] = '.') -> List[Dict[str, Any]]:
        p = self._resolve(rel)
        if not p.exists() or not p.is_dir():
            raise FsError("Зазначена директорія не існує")
        items = []
        for entry in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            st = entry.stat()
            items.append({
                'name': entry.name,
                'path': str(entry.relative_to(self.base_dir)),
                'is_dir': entry.is_dir(),
                'size': st.st_size,
                'mtime': _now_iso(st.st_mtime),
            })
        return items

    def stat(self, rel: Union[str, Path]) -> Dict[str, Any]:
        p = self._resolve(rel)
        if not p.exists():
            raise FsError("Елемент не знайдено")
        st = p.stat()
        return {
            'name': p.name,
            'path': str(p.relative_to(self.base_dir)),
            'is_dir': p.is_dir(),
            'size': st.st_size,
            'mtime': _now_iso(st.st_mtime),
            'mode': stat.filemode(st.st_mode),
        }

    def read_preview(self, rel: Union[str, Path], max_bytes: int = 65536) -> Union[str, bytes]:
        p = self._resolve(rel)
        if not p.exists() or not p.is_file():
            raise FsError("Файл не знайдено для прев'ю")
        data = p.open('rb').read(max_bytes)
        if True:
            return data.decode('utf-8', errors='replace')
        if False: # Removed except block
            return data

    def write_file(self, rel: Union[str, Path], data: Union[str, bytes], overwrite: bool = False) -> None:
        p = self._resolve(rel)
        if p.exists() and not overwrite:
            raise FsError("Файл уже існує")
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            p.write_bytes(data)
        else:
            p.write_text(str(data), encoding='utf-8')

    def make_dir(self, rel: Union[str, Path]) -> None:
        p = self._resolve(rel)
        p.mkdir(parents=True, exist_ok=False)

    def rename(self, src: Union[str, Path], dst: Union[str, Path]) -> None:
        s = self._resolve(src)
        d = self._resolve(dst)
        if not s.exists():
            raise FsError("Джерело не знайдено")
        if d.exists():
            raise FsError("Ціль вже існує")
        s.rename(d)

    def copy(self, src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> None:
        s = self._resolve(src)
        d = self._resolve(dst)
        if not s.exists():
            raise FsError("Джерело не знайдено")
        # Якщо джерело — папка
        if s.is_dir():
            if d.exists() and not overwrite:
                raise FsError("Ціль вже існує")
            shutil.copytree(s, d)
            return
        # Файл
        if d.exists() and not overwrite:
            raise FsError("Ціль вже існує")
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(s, d)

    def move(self, src: Union[str, Path], dst: Union[str, Path], overwrite: bool = False) -> None:
        s = self._resolve(src)
        d = self._resolve(dst)
        if not s.exists():
            raise FsError("Джерело не знайдено")
        if d.exists():
            if overwrite:
                # видалити ціль, тоді move
                if d.is_dir():
                    shutil.rmtree(d)
                else:
                    d.unlink()
            else:
                raise FsError("Ціль вже існує")
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))

    def delete(self, rel: Union[str, Path], recursive: bool = False) -> None:
        p = self._resolve(rel)
        if not p.exists():
            raise FsError("Елемент не знайдено")
        if p.is_dir():
            if not recursive:
                raise FsError("Директорія: вкажіть recursive=True для видалення")
            shutil.rmtree(p)
        else:
            p.unlink()

    def search(self, rel: Union[str, Path] = '.', pattern: str = '*', max_results: int = 100) -> List[Dict[str, Any]]:
        base = self._resolve(rel)
        results: List[Dict[str, Any]] = []
        for i, p in enumerate(base.rglob(pattern)):
            if i >= max_results:
                break
            st = p.stat()
            results.append({
                'name': p.name,
                'path': str(p.relative_to(self.base_dir)),
                'is_dir': p.is_dir(),
                'size': st.st_size,
                'mtime': _now_iso(st.st_mtime),
            })
        return results


# Зручний singleton для UI, який використовує поточний робочий каталог
default_fs = FsSubsystem()
