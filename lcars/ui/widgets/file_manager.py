from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from pathlib import Path


class FileManagerWidget(QWidget):
    """Simple FileManager widget listing files in a directory (placeholder)."""
    def __init__(self, start_path: Path | str | None = None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.title = QLabel(f"File Manager: {start_path}")
        layout.addWidget(self.title)
        self.list = QListWidget()
        layout.addWidget(self.list)
        if start_path:
            p = Path(start_path)
            if p.exists() and p.is_dir():
                for f in sorted(p.iterdir()):
                    self.list.addItem(str(f.name))
