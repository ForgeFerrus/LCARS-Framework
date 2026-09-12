# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QTextEdit
)
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_random_button_color, get_lcars_font_style, LCARSEra


class DatabaseInterface(QWidget):
    def __init__(self, project_root=None, parent=None):
        super().__init__(parent)
        self.project_root = Path(project_root) if project_root else Path(__file__).resolve().parent.parent
        self.setStyleSheet("color: #FFF;")

        main = QVBoxLayout(self)
        header = QLabel("◢ LCARS DATABASE")
        header.setStyleSheet(f"{get_lcars_font_style(20, 'normal')}; color: #DDD;")
        main.addWidget(header)

        # Search
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search projects...")
        self.search.textChanged.connect(self.filter_projects)
        search_row.addWidget(self.search)
        main.addLayout(search_row)

        body = QHBoxLayout()
        self.list = QListWidget()
        self.list.itemSelectionChanged.connect(self._show_selected)
        body.addWidget(self.list, 1)

        right = QVBoxLayout()
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        right.addWidget(self.details)

        btn_row = QHBoxLayout()
        from lcars.ui.widgets.common import create_lcars_button
        self.build_btn = create_lcars_button("Build", parent=self, width=120, height=44, action="build")
        self.build_btn.clicked.connect(self._build_project)

        self.run_btn = create_lcars_button("Run", parent=self, width=120, height=44, action="run")
        self.run_btn.clicked.connect(self._run_project)

        btn_row.addWidget(self.build_btn)
        btn_row.addWidget(self.run_btn)
        right.addLayout(btn_row)

        body.addLayout(right, 2)
        main.addLayout(body, 1)

        self.load_projects()

    def load_projects(self):
        self._projects = []
        root = Path(self.project_root)
        # search depth 2 for likely projects
        for p in root.iterdir():
            if p.is_dir() and (p.name.startswith('ENX') or p.name.startswith('NCC-') or 'geant' in p.name.lower() or 'project' in p.name.lower()):
                self._projects.append(p)
        # Fallback: include any top-level directories
        if not self._projects:
            for p in root.iterdir():
                if p.is_dir():
                    self._projects.append(p)

        self._projects.sort(key=lambda p: p.name.lower())
        self.populate_list()

    def populate_list(self):
        self.list.clear()
        for p in self._projects:
            it = QListWidgetItem(p.name)
            it.setData(Qt.ItemDataRole.UserRole, str(p))
            self.list.addItem(it)

    def filter_projects(self, text: str):
        t = text.lower() if text else ''
        for i in range(self.list.count()):
            it = self.list.item(i)
            show = t in it.text().lower() # type: ignore
            self.list.setRowHidden(i, not show)

    def _show_selected(self):
        items = self.list.selectedItems()
        if not items:
            self.details.setText('')
            return
        path = items[0].data(Qt.ItemDataRole.UserRole)
        p = Path(path)
        info = f"Name: {p.name}\nPath: {p}\n"
        if True:
            files = list(p.iterdir())[:20]
            info += "\nContents:\n"
            for f in files:
                info += f" - {f.name}\n"
        if False: # Removed except block
            info += f"\nFailed to list contents: {e}\n"
        self.details.setText(info)

    def _build_project(self):
        items = self.list.selectedItems()
        if not items:
            self.details.append('\nSelect a project first')
            return
        path = items[0].data(Qt.ItemDataRole.UserRole)
        self.details.append(f"\n[BUILD] Starting build for {path} (placeholder)")

    def _run_project(self):
        items = self.list.selectedItems()
        if not items:
            self.details.append('\nSelect a project first')
            return
        path = items[0].data(Qt.ItemDataRole.UserRole)
        self.details.append(f"\n[RUN] Launching project {path} (placeholder)")

# запуск
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    # шлях до проекту
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    app = QApplication(sys.argv)
    win = DatabaseInterface(project_root=project_root)
    win.resize(800, 600)
    win.show()
    app.exec()
