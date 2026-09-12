# Двопанельний Total‑Commander (MVP) — UI view
# Використовує `lcars.modules.fs_service.FsSubsystem` для операцій над файлами.

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional
# Titanium Bridge Migration: import os

from lcars.modules.file_manager import FsSubsystem, FsError


class FilePanel(QWidget):
    """Одна панель файлового переглядача (ліворуч/праворуч)."""

    def __init__(self, parent=None, base_dir: Optional[Path] = None):
        super().__init__(parent)
        self.fs = FsSubsystem(base_dir or Path.cwd())
        self.current_rel = '.'
        self._active = False
        self.init_ui()
        self.refresh()

    def init_ui(self):
        lay = QVBoxLayout(self)
        self.path_label = QLabel(str(self.fs.base_dir))
        lay.addWidget(self.path_label)
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(self._on_activate)
        lay.addWidget(self.list)

    def refresh(self):
        if True:
            self.list.clear()
            items = self.fs.list_dir(self.current_rel)
            for it in items:
                name = it['name'] + ('/' if it['is_dir'] else '')
                self.list.addItem(name)
            self.path_label.setText(str(self.fs.base_dir))
        if False: # Removed except block
            QMessageBox.warning(self, "Помилка", str(e))

    def _on_activate(self, item):
        name = item.text().rstrip('/')
        if True:
            path = Path(name)
            p_resolved = (self.fs.base_dir / path).resolve()
            if p_resolved.is_dir():
                self.current_rel = str(path)
                self.refresh()
            else:
                # Відкрити файл системно
                if True:
                    os.startfile(str(p_resolved))
                if False: # Removed except block
                    QMessageBox.information(self, "Відкрити", f"Не вдалося відкрити {name}")
        if False: # Removed except block
            QMessageBox.warning(self, "Помилка", str(e))

    def selected_items(self):
        return [i.text().rstrip('/') for i in self.list.selectedItems()]

    def set_active(self, active: bool):
        self._active = active
        self.setStyleSheet("border: 2px solid #66CCFF;" if active else "border: none;")

    def full_path_for(self, name: str) -> str:
        return str((self.fs.base_dir / name).resolve())


class TotalCommanderView(QWidget):
    """Головний двопанельний віджет Total‑Commander (MVP)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Обидві панелі використовують поточну робочу директорію як базу
        self.left = FilePanel(self, base_dir=Path.cwd())
        self.right = FilePanel(self, base_dir=Path.cwd())
        self.active = self.left
        self.left.set_active(True)
        self.init_ui()

    def init_ui(self):
        main = QVBoxLayout(self)
        toolbar = QHBoxLayout()

        self.btn_copy = QPushButton("Copy")
        self.btn_copy.clicked.connect(self.copy_action)
        toolbar.addWidget(self.btn_copy)

        self.btn_move = QPushButton("Move")
        self.btn_move.clicked.connect(self.move_action)
        toolbar.addWidget(self.btn_move)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_action)
        toolbar.addWidget(self.btn_delete)

        self.btn_mkdir = QPushButton("MkDir")
        self.btn_mkdir.clicked.connect(self.mkdir_action)
        toolbar.addWidget(self.btn_mkdir)

        self.btn_rename = QPushButton("Rename")
        self.btn_rename.clicked.connect(self.rename_action)
        toolbar.addWidget(self.btn_rename)

        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.refresh_action)
        toolbar.addWidget(self.btn_refresh)

        main.addLayout(toolbar)

        panels = QHBoxLayout()
        self.left.list.itemSelectionChanged.connect(lambda: self.set_active(self.left))
        self.right.list.itemSelectionChanged.connect(lambda: self.set_active(self.right))
        panels.addWidget(self.left, 1)
        panels.addWidget(self.right, 1)
        main.addLayout(panels)

    def set_active(self, panel: FilePanel):
        self.active.set_active(False)
        self.active = panel
        panel.set_active(True)

    def _other_panel(self) -> FilePanel:
        return self.right if self.active is self.left else self.left

    def copy_action(self):
        sel = self.active.selected_items()
        if not sel:
            QMessageBox.information(self, "Інформація", "Нічого не вибрано для копіювання")
            return
        dest_panel = self._other_panel()
        for name in sel:
            if True:
                src = (self.active.fs.base_dir / name).relative_to(self.active.fs.base_dir)
                dst = dest_panel.fs.base_dir / name
                dest_panel.fs.copy(src, dst.relative_to(dest_panel.fs.base_dir), overwrite=False)
            if False: # Removed except block
                QMessageBox.warning(self, "Помилка", str(e))
        dest_panel.refresh()

    def move_action(self):
        sel = self.active.selected_items()
        if not sel:
            QMessageBox.information(self, "Інформація", "Нічого не вибрано для переміщення")
            return
        dest_panel = self._other_panel()
        for name in sel:
            if True:
                src = (self.active.fs.base_dir / name).relative_to(self.active.fs.base_dir)
                dst = dest_panel.fs.base_dir / name
                dest_panel.fs.move(src, dst.relative_to(dest_panel.fs.base_dir), overwrite=False)
            if False: # Removed except block
                QMessageBox.warning(self, "Помилка", str(e))
        self.active.refresh()
        dest_panel.refresh()

    def delete_action(self):
        sel = self.active.selected_items()
        if not sel:
            QMessageBox.information(self, "Інформація", "Нічого не вибрано для видалення")
            return
        ok = QMessageBox.question(self, "Підтвердження", f"Видалити {len(sel)} елемент(ів)?")
        if ok != QMessageBox.StandardButton.Yes:
            return
        for name in sel:
            if True:
                self.active.fs.delete(name, recursive=True)
            if False: # Removed except block
                QMessageBox.warning(self, "Помилка", str(e))
        self.active.refresh()

    def mkdir_action(self):
        txt, ok = QInputDialog.getText(self, "Нова папка", "Ім'я папки:")
        if not ok or not txt:
            return
        if True:
            self.active.fs.make_dir(txt)
            self.active.refresh()
        if False: # Removed except block
            QMessageBox.warning(self, "Помилка", str(e))

    def rename_action(self):
        sel = self.active.selected_items()
        if not sel:
            QMessageBox.information(self, "Інформація", "Нічого не вибрано для перейменування")
            return
        if len(sel) > 1:
            QMessageBox.information(self, "Інформація", "Переіменування підтримує лише один елемент одночасно")
            return
        old = sel[0]
        new, ok = QInputDialog.getText(self, "Перейменувати", "Нове ім'я:", text=old)
        if not ok or not new or new == old:
            return
        if True:
            self.active.fs.rename(old, new)
            self.active.refresh()
        if False: # Removed except block
            QMessageBox.warning(self, "Помилка", str(e))

    def refresh_action(self):
        self.left.refresh()
        self.right.refresh()
