from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread
from pathlib import Path
import sys
import os
import subprocess

from lcars.ui.widgets.common import create_lcars_button, get_lcars_font_style
from lcars.themes.palette import get_era_palette, LCARSEra
from lcars.modules.project_manager import ProjectManager
from lcars.core.task_executor import TaskExecutor
from lcars.system.paths import get_project_root

class OperationsWidget(QWidget):
    """
    Simulation Operations Widget (Enhanced)
    This is the primary interface for managing Geant4 projects.
    It combines discovery, build/run automation, and file access.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.era)

        # Initialize Core Logic
        self.geant4_root = Path(get_project_root()) / "Geant4" / "Enterprise"
        self.pm = ProjectManager(self.geant4_root)
        self.executor = TaskExecutor()

        # State
        self.current_project = None
        self.current_thread = None

        self.setup_ui()

        # Poll executor for terminal output
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_output)
        self.poll_timer.start(100)

    def setup_ui(self):
        layout = QHBoxLayout(self) # Transform to horizontal layout for 2-column view
        layout.setSpacing(20)
        layout.setContentsMargins(10, 10, 10, 10)

        # --- LEFT COLUMN: Project List ---
        left_col = QVBoxLayout()

        title = QLabel("PROJECTS")
        title.setStyleSheet(f"color: {self.colors['button_colors'][1]}; {get_lcars_font_style(20, 'normal')}")        
        left_col.addWidget(title)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #050505;
                color: {self.colors['button_colors'][3]};
                border: 2px solid {self.colors['button_colors'][0]};
                border-radius: 2px;
                font-size: 14pt;
            }}
            QListWidget::item {{
                padding: 10px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['button_colors'][0]};
                color: black;
            }}
        """)
        self._refresh_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        left_col.addWidget(self.project_list)

        refresh_btn = create_lcars_button("REFRESH LIST", parent=self, width=150, height=45)
        refresh_btn.clicked.connect(self._refresh_projects)
        left_col.addWidget(refresh_btn)

        layout.addLayout(left_col, 1) # Weight 1

        # --- RIGHT COLUMN: Details & Actions ---
        right_col = QVBoxLayout()

        self.lbl_title = QLabel("SELECT A TARGET")
        self.lbl_title.setStyleSheet(f"color: #FFF; {get_lcars_font_style(24, 'normal')}")
        right_col.addWidget(self.lbl_title)

        # Actions Row
        actions = QHBoxLayout()

        self.btn_build = create_lcars_button("BUILD", parent=self, width=120, height=50)
        self.btn_build.clicked.connect(self._build_project)

        self.btn_run = create_lcars_button("RUN", parent=self, width=120, height=50)
        self.btn_run.clicked.connect(self._run_project)

        self.btn_open = create_lcars_button("OPEN FOLDER", parent=self, width=140, height=50)
        self.btn_open.clicked.connect(self._open_project_folder)

        actions.addWidget(self.btn_build)
        actions.addWidget(self.btn_run)
        actions.addWidget(self.btn_open)
        actions.addStretch()
        right_col.addLayout(actions)

        # Terminal / Log
        term_label = QLabel("SYSTEM TERMINAL")
        term_label.setStyleSheet(f"color: {self.colors['button_colors'][2]}; font-size: 12pt;")
        right_col.addWidget(term_label)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #080808; color: #BBB; font-family: Consolas; font-size: 11pt; border: none;")
        right_col.addWidget(self.terminal, 1)

        # Manual Command Input
        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter system command...")
        self.cmd_input.setStyleSheet("background-color: #222; color: #FFF; padding: 5px; font-family: Consolas;")   
        self.cmd_input.returnPressed.connect(self._exec_cmd)
        cmd_row.addWidget(self.cmd_input, 1)

        cmd_btn = create_lcars_button("EXECUTE", parent=self, width=100, height=35)
        cmd_btn.clicked.connect(self._exec_cmd)
        cmd_row.addWidget(cmd_btn)

        right_col.addLayout(cmd_row)

        layout.addLayout(right_col, 2) # Weight 2

    def _refresh_projects(self):
        self.pm = ProjectManager(self.geant4_root)
        self.project_list.clear()
        projects = self.pm.get_all_projects()

        if not projects:
            self.terminal.append("[SCAN] No projects found in " + str(self.geant4_root))

        for p in projects:
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, p)
            self.project_list.addItem(item)

    def _on_project_selected(self, current, previous=None):
        if not current:
            return
        p = current.data(Qt.ItemDataRole.UserRole)
        self.current_project = p
        self.lbl_title.setText(f"{p.name.upper()}")
        self.terminal.append(f"Target locked: {p.name}")

    def _append_terminal(self, text: str):
        self.terminal.append(text)
        # Auto-scroll
        cursor = self.terminal.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.terminal.setTextCursor(cursor)

    def _poll_output(self):
        item = self.executor.get_output()
        if item:
            kind, data = item
            if kind == 'output':
                self._append_terminal(data.rstrip('\n'))
            elif kind == 'error':
                self._append_terminal(f"[ERR] {data}")
            elif kind == 'complete':
                self._append_terminal(f"[DONE] Process finished with code {data}\n")

    def _build_project(self):
        if not self.current_project:
            self._append_terminal('[ERROR] SELECT A PROJECT FIRST')
            return
        p = self.current_project
        build_dir = p.build_dir or (p.path / 'build')
        build_dir.mkdir(parents=True, exist_ok=True)

        cmd = f'cmake -S "{p.path}" -B "{build_dir}" && cmake --build "{build_dir}" --config Release'
        self._append_terminal(f'Init sequence: BUILD {p.name}...')
        thread = self.executor.execute_command(
            cmd,
            cwd=str(build_dir),
            on_output=self._on_out,
            on_error=self._on_err,
            on_complete=self._on_complete
        )
        thread.start()
        self.current_thread = thread

    def _run_project(self):
        if not self.current_project:
            self._append_terminal('[ERROR] SELECT A PROJECT FIRST')
            return
        p = self.current_project
        exe = p.executable
        if not exe:
            # try to infer from build dir
            build_dir = p.build_dir or (p.path / 'build')
            # find any exe in build dir or Release subdir
            exe = None
            if build_dir.exists():
                candidates = list(build_dir.glob("*.exe")) + list(build_dir.glob("**/*.exe"))
                if candidates:
                    exe = candidates[0]

        if not exe:
            self._append_terminal('[ERROR] No executable found. Try building first.')
            return

        cmd = f'"{exe}"'
        self._append_terminal(f'Init sequence: RUN {p.name}...')
        thread = self.executor.execute_command(
            cmd,
            cwd=str(p.path),
            on_output=self._on_out,
            on_error=self._on_err,
            on_complete=self._on_complete
        )
        thread.start()
        self.current_thread = thread

    def _open_project_folder(self):
        if not self.current_project:
            return
        path = str(self.current_project.path)
        self._append_terminal(f"Accessing filesystem: {path}")
        if sys.platform == 'win32':
            os.startfile(path)
        else:
            subprocess.Popen(['xdg-open', path])

    def _exec_cmd(self):
        cmd = self.cmd_input.text().strip()
        if not cmd: return
        cwd = str(self.current_project.path) if self.current_project else None

        self._append_terminal(f"> {cmd}")
        thread = self.executor.execute_command(
            cmd,
            cwd=cwd,
            on_output=self._on_out,
            on_error=self._on_err,
            on_complete=self._on_complete
        )
        thread.start()
        self.cmd_input.clear()

    # Callbacks for TaskExecutor
    def _on_out(self, line: str):
        self.executor.output_queue.put(('output', line))

    def _on_err(self, err: str):
        self.executor.output_queue.put(('error', err))

    def _on_complete(self, code: int):
        self.executor.output_queue.put(('complete', code))
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class OperationsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Operations module (placeholder)"))
