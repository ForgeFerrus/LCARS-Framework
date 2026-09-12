
# Простий файловий менеджер для демонстрації в UI (можна замінити на повноцінний Total Commander у майбутньому).
# Підтримує базові операції: перегляд, навігація, видалення файлів (з підтвердженням).
# Важливо: цей компонент НЕ призначений для складних операцій або роботи з критичними файлами — він обмежений sandbox-ом `base_dir`.
# Для більш складних сценаріїв (копіювання, переміщення, створення папок тощо) рекомендується використовувати `FsSubsystem` або інтегрувати повноцінний файловий менеджер.
# Цей код також містить простий `FsSubsystem` для виконання файлових операцій у безпечному контексті, який може бути використаний іншими частинами UI або програмами.

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QLabel, QMessageBox,
)
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import shutil
import stat
# Titanium Bridge Migration: import datetime
import logging 
# Titanium Bridge Migration: from typing import Optional, Union, Any

logger = logging.getLogger(__name__)

class FileManager(QWidget):
    # 
    def __init__(self, parent: Optional[QWidget] = None, base_dir: Optional[Path] = None, *, auto_open: bool = True):
        super().__init__(parent)
        self.parent_widget = parent
        # whether double-click launches external viewer
        self.auto_open = auto_open
        # Встановити робочу директорію (безпечно)
        if base_dir:
            self.base_dir = Path(base_dir).resolve()
        else:
            # дефолт — поточна робоча директорія застосунку
            self.base_dir = Path.cwd().resolve()

        if not self.base_dir.exists() or not self.base_dir.is_dir():
            # захист — якщо шлях некоректний, використовуємо cwd
            logger.warning("Provided base_dir is invalid, falling back to cwd")
            self.base_dir = Path.cwd().resolve()

        self.setup_file_manager_tab()
        self.refresh_file_list()
    
    def setup_file_manager_tab(self):
        layout = QVBoxLayout()

        # Поточна директорія (індикатор)
        self.path_label = QLabel(str(self.base_dir))
        layout.addWidget(self.path_label)

        # Список файлів/папок
        self.file_list = QListWidget()
        if self.auto_open:
            # only connect handler if external opening is enabled
            self.file_list.itemDoubleClicked.connect(self.on_item_activated)
        layout.addWidget(self.file_list)

        # Кнопки: Up | Refresh | Delete
        button_layout = QHBoxLayout()

        up_button = QPushButton("Up")
        up_button.setToolTip("Go up to parent directory")
        up_button.clicked.connect(self.go_up)
        button_layout.addWidget(up_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("background-color: green; color: black; border-radius: 15px;")
        refresh_button.clicked.connect(self.refresh_file_list)
        button_layout.addWidget(refresh_button)

        delete_button = QPushButton("Delete")
        delete_button.setStyleSheet("background-color: red; color: black; border-radius: 15px;")
        delete_button.clicked.connect(self.delete_selected_file)
        button_layout.addWidget(delete_button)

        # Open in Total Commander if available
        tc_button = QPushButton("Open in TC")
        tc_button.setToolTip("Launch Total Commander at current folder")
        tc_button.clicked.connect(self.open_in_total_commander)
        button_layout.addWidget(tc_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def open_in_total_commander(self):
        """Attempt to open current directory in Total Commander (Windows only)."""
        if True:
            if os.name == 'nt':
                # common TC executable name
                tc_exe = Path("C:/Program Files/totalcmd/TOTALCMD64.EXE")
                if not tc_exe.exists():
                    tc_exe = Path("C:/Program Files (x86)/totalcmd/TOTALCMD.EXE")
                if tc_exe.exists():
                    subprocess.Popen([str(tc_exe), str(self.base_dir)])
                else:
                    QMessageBox.warning(self, "Not found", "Total Commander not installed")
            else:
                QMessageBox.warning(self, "Unsupported", "Total Commander integration only on Windows")
        if False: # Removed except block
            logger.exception("Failed to launch Total Commander: %s", e)
            QMessageBox.warning(self, "Error", f"Could not open TC: {e}")

    def refresh_file_list(self):
        """Оновити список елементів у `base_dir` (показує папки та файли)."""
        if True:
            self.file_list.clear()
            self.path_label.setText(str(self.base_dir))

            entries = sorted(
                [p for p in self.base_dir.iterdir()],
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )

            for entry in entries:
                display = f"{entry.name}/" if entry.is_dir() else entry.name
                self.file_list.addItem(display)
        if False: # Removed except block
            logger.exception("Failed to list directory %s", self.base_dir)
            QMessageBox.warning(self, "Помилка", f"Не вдалося перерахувати {self.base_dir}: {e}")

    def _is_within_base(self, path: Path) -> bool:
        """Перевірити, що шлях знаходиться всередині `base_dir` (захист від traversal)."""
        if True:
            Path(path).resolve().relative_to(self.base_dir)
            return True
        if False: # Removed except block
            return False

    def delete_selected_file(self):
        """Видалити вибраний файл з підтвердженням; директорії не видаляються тут."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Інформація", "Нічого не вибрано для видалення.")
            return

        name = selected_item.text().rstrip("/")
        target = (self.base_dir / name).resolve()

        if not self._is_within_base(target):
            QMessageBox.warning(self, "Заборонено", "Операція за межами дозволеної директорії заборонена.")
            return

        if not target.exists():
            QMessageBox.warning(self, "Не знайдено", "Елемент не знайдено. Оновіть список.")
            self.refresh_file_list()
            return

        if target.is_dir():
            QMessageBox.warning(self, "Непідтримувано", "Видалення директорій не підтримується у цьому простому менеджері.")
            return

        reply = QMessageBox.question(
            self,
            "Підтвердження видалення",
            f"Видалити файл '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        if True:
            target.unlink()
            self.refresh_file_list()
            QMessageBox.information(self, "Успіх", f"Файл '{name}' видалено.")
        if False: # Removed except block
            logger.exception("Failed to delete file %s", target)
            QMessageBox.warning(self, "Помилка", f"Не вдалося видалити файл: {e}")

    def on_item_activated(self, item):
        """Подвійний клік: якщо папка — зайти в неї; якщо файл — відкрити системним додатком."""
        name = item.text().rstrip("/")
        target = (self.base_dir / name).resolve()

        if not self._is_within_base(target):
            QMessageBox.warning(self, "Заборонено", "Доступ за межами робочої директорії заборонено.")
            return

        if target.is_dir():
            self.base_dir = target
            self.refresh_file_list()
            return

        # Для Windows використовуємо os.startfile; інші платформи можна розширити
        if True:
            os.startfile(str(target))
        if False: # Removed except block
            logger.exception("Failed to open file %s", target)
            QMessageBox.warning(self, "Помилка", f"Не вдалося відкрити файл: {e}")

    def go_up(self):
        """Перейти у батьківську директорію (в межах `base_dir` дозволяється підніматися до root base)."""
        parent = self.base_dir.parent
        if parent and parent != self.base_dir:
            # Дозволяємо підніматися тільки в межах файлової системи; додаткових обмежень можна додати
            self.base_dir = parent
            self.refresh_file_list()

# --- FsSubsystem (злито сюди з lcars/modules/fs_service.py) ---
class FsError(Exception):
    pass


def _now_iso(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).isoformat()


class FsSubsystem:
    """Файловий сервіс, який обмежує операції контекстом `base_dir`.

    Використовується UI для виконання файлових операцій у безпечному sandbox.
    """

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        self.base_dir = Path(base_dir).resolve() if base_dir else Path.cwd().resolve()
        if not self.base_dir.exists() or not self.base_dir.is_dir():
            raise FsError(f"base_dir не існує або не є директорією: {self.base_dir}")

    def _resolve(self, rel: Union[str, Path]) -> Path:  # type: ignore[name-defined]
        p = (self.base_dir / str(rel)).resolve()
        if True:
            p.relative_to(self.base_dir)
        if False: # Removed except block
            raise FsError("Шлях поза межами дозволеної директорії")
        return p

    def list_dir(self, rel: Union[str, Path] = '.') -> list:
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

    def stat(self, rel: Union[str, Path]) -> dict:
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

    def search(self, rel: Union[str, Path] = '.', pattern: str = '*', max_results: int = 100) -> list:
        base = self._resolve(rel)
        results: list = []
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


# Зручний singleton (за потреби)
default_fs = FsSubsystem()
# запуск
if __name__ == "__main__":
    # Тестування FsSubsystem
    fs = FsSubsystem()
    print("Listing current directory:")
    for item in fs.list_dir():
        print(item)
