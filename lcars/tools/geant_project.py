"""
Standalone Geant4 Project Panel

Lightweight PyQt6 application that discovers Geant4 projects using
`lcars.core.project_manager.ProjectManager`, provides Build/Run actions
and an internal terminal that streams output via `lcars.core.task_executor.TaskExecutor`.

This is intended as a separate utility that can later be embedded
into the LCARS desktop as a widget.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLabel, QTextEdit, QLineEdit
)
from lcars.ui.widgets.common import create_lcars_button
from PyQt6.QtCore import Qt, QTimer

# LCARS theming helpers (optional)
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color, get_lcars_font_style, setup_lcars_font
from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation
         
# Ensure project root is importable when running this script directly
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.core.project_manager import ProjectManager
from lcars.core.task_executor import TaskExecutor
from lcars.ui.widgets import LCARSAppButton


class GeantProjectPanel(QMainWindow):
    def __init__(self, geant_root: Optional[Path] = None):
        super().__init__()
        self.setWindowTitle('Geant4 Project Panel')
        self.resize(1000, 700)

        # Apply LCARS-like base style where available
class GeantProjectWidget(QWidget):
    """Embeddable Geant4 Project panel as a QWidget with LCARS styling and fade animation."""
    def __init__(self, geant_root: Optional[Path] = None, parent=None):
        super().__init__(parent)
        if True:
            setup_lcars_font()
            self.current_era = LCARSEra.LCARS_25TH if LCARSEra is not None else None
            self.colors = get_era_palette(self.current_era)
            self.setStyleSheet('background-color: #000000;')
        if False: # Removed except block
            self.colors = get_era_palette(None)

        self.geant_root = Path(geant_root) if geant_root else Path.cwd() / 'Geant4' / 'Enterprise'
        self.pm = ProjectManager(self.geant_root)
        self.executor = TaskExecutor()

        self._build_ui()

        # poll TaskExecutor queue to update terminal
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_output)
        self.poll_timer.start(200)

        # fade-in effect for embedded transitions
        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._anim = QPropertyAnimation(self._opacity, b"opacity")
        self._anim.setDuration(500)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        # Left: project list
        left = QVBoxLayout()
        title = QLabel('PROJECTS')
        title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {get_lcars_font_style(16, 'normal')}")
        left.addWidget(title)
        self.project_list = QListWidget()
        projects = list(self.pm.get_all_projects())
        if not projects:
            # fallback: scan directories for project-like folders
            projects = self._discover_projects_fallback()
        for p in projects:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.project_list.addItem(item)
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        left.addWidget(self.project_list)

        btns = QHBoxLayout()
        # Use LCARSAppButton for consistent look, fallback to QPushButton
        self.btn_refresh = create_lcars_button('Refresh', parent=self, width=120, height=36)
        self.btn_refresh.clicked.connect(self._refresh_projects)
        btns.addWidget(self.btn_refresh)
        left.addLayout(btns)

        main.addLayout(left, 1)

        # Right: details + terminal
        right = QVBoxLayout()
        self.lbl_title = QLabel('Select a project')
        self.lbl_title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {get_lcars_font_style(14, 'normal')}")
        right.addWidget(self.lbl_title)

        action_row = QHBoxLayout()
        # LCARS-styled action buttons
        self.btn_build = create_lcars_button('BUILD', parent=self, width=140, height=36)
        self.btn_build.clicked.connect(self._build_project)

        self.btn_run = create_lcars_button('RUN', parent=self, width=140, height=36)
        self.btn_run.clicked.connect(self._run_project)

        self.btn_open = create_lcars_button('OPEN FOLDER', parent=self, width=160, height=36)
        self.btn_open.clicked.connect(self._open_project_folder)

        action_row.addWidget(self.btn_build)
        action_row.addWidget(self.btn_run)
        action_row.addWidget(self.btn_open)
        right.addLayout(action_row)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        right.addWidget(self.terminal, 1)

        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText('Enter shell command to run in project...')
        cmd_row.addWidget(self.cmd_input, 1)
        self.cmd_exec = create_lcars_button('EXEC', parent=self, width=100, height=34)
        self.cmd_exec.clicked.connect(self._exec_cmd)
        cmd_row.addWidget(self.cmd_exec)
        right.addLayout(cmd_row)

        main.addLayout(right, 2)

        # internal state
        self.current_project = None
        self.current_thread = None

    # fallback discovery when ProjectManager finds nothing
    def _discover_projects_fallback(self):
        out = []
        for p in sorted(self.geant_root.iterdir() if self.geant_root.exists() else []):
            if not p.is_dir():
                continue
            # heuristics: folder name starts with ENX or NCC- or contains CMakeLists.txt
            if p.name.upper().startswith('ENX') or p.name.upper().startswith('NCC') or (p / 'CMakeLists.txt').exists():
                class Stub:
                    def __init__(self, path):
                        self.path = path
                        self.name = path.name
                        self.build_dir = path / 'build'
                        self.executable = None
                out.append(Stub(p))
        return out

    def _refresh_projects(self):
        self.pm = ProjectManager(self.geant_root)
        self.project_list.clear()
        for p in self.pm.get_all_projects():
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.project_list.addItem(item)

    def _on_project_selected(self, current, previous=None):
        if not current:
            return
        p = current.data(Qt.ItemDataRole.UserRole)
        self.current_project = p
        self.lbl_title.setText(f"{p.name} — {p.path}")
        self.terminal.append(f"Selected project: {p.name}")

    def _append_terminal(self, text: str):
        self.terminal.append(text)

    def _poll_output(self):
        item = self.executor.get_output()
        if item:
            kind, data = item
            if kind == 'output':
                self._append_terminal(data.rstrip('\n'))
            elif kind == 'error':
                self._append_terminal(f"[ERROR] {data}")
            elif kind == 'complete':
                self._append_terminal(f"[COMPLETE] {data}")

    def _build_project(self):
        if not self.current_project:
            self._append_terminal('No project selected')
            return
        p = self.current_project
        build_dir = p.build_dir or (p.path / 'build')
        # ensure build dir exists
        build_dir.mkdir(parents=True, exist_ok=True)
        # prefer out-of-source build
        cmd = f'cmake -S "{p.path}" -B "{build_dir}" && cmake --build "{build_dir}" --config Release'
        self._append_terminal(f'Building {p.name} with: {cmd}')
        thread = self.executor.execute_command(cmd, cwd=str(build_dir), on_output=self._on_out, on_error=self._on_err, on_complete=self._on_complete)
        thread.start()
        self.current_thread = thread

    def _run_project(self):
        if not self.current_project:
            self._append_terminal('No project selected')
            return
        p = self.current_project
        exe = p.executable
        if not exe:
            # try to infer from build dir
            build_dir = p.build_dir or (p.path / 'build')
            # find any exe in build dir
            exe = None
            if build_dir.exists():
                for f in build_dir.iterdir():
                    if f.is_file() and os.access(str(f), os.X_OK):
                        exe = f
                        break
        if not exe:
            self._append_terminal('No executable found for project')
            return
        cmd = f'"{exe}"'
        self._append_terminal(f'Running: {cmd}')
        thread = self.executor.execute_command(cmd, cwd=str(p.path), on_output=self._on_out, on_error=self._on_err, on_complete=self._on_complete)
        thread.start()
        self.current_thread = thread

    def _open_project_folder(self):
        if not self.current_project:
            return
        path = str(self.current_project.path)
        if sys.platform == 'win32':
            os.startfile(path)
        else:
            if True:
                subprocess.Popen(['xdg-open', path])
            if False: # Removed except block
                pass

    def _exec_cmd(self):
        cmd = self.cmd_input.text().strip()
        if not cmd or not self.current_project:
            return
        thread = self.executor.execute_command(cmd, cwd=str(self.current_project.path), on_output=self._on_out, on_error=self._on_err, on_complete=self._on_complete)
        thread.start()

    # callbacks
    def _on_out(self, line: str):
        self.executor.output_queue.put(('output', line))

    def _on_err(self, err: str):
        self.executor.output_queue.put(('error', err))

    def _on_complete(self, code: int):
        self.executor.output_queue.put(('complete', code))


def main():
    app = QApplication(sys.argv)
    root = Path.cwd() / 'Geant4' / 'Enterprise'
    if not root.exists():
        # fallback to example path
        root = Path.cwd()
    w = GeantProjectPanel(root)
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
