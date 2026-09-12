from pathlib import Path
import sys
import os
import subprocess

# Auto-add project root to sys.path if running standalone
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QThread

from lcars.ui.widgets.common import create_lcars_button, get_lcars_font_style, LCARSElbow
from lcars.themes.palette import get_era_palette, LCARSEra
from lcars.modules.project_manager import ProjectManager
from lcars.core.task_executor import TaskExecutor
from lcars.system.paths import get_project_root
from lcars.system.localization import LOCALIZATION as Language

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

        # Реєструємо оновлення UI при зміні мови
        Language.register_callback(lambda code: self.retranslate_ui())

        # Poll executor for terminal output
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_output)
        self.poll_timer.start(100)

    def setup_ui(self):
        # Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # --- LEFT COLUMN: Project List ---
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(5)
        
        # Elbow Header for List
        self.list_elbow = LCARSElbow("top-left", color=self.colors['button_colors'][0], era=self.era)
        self.list_elbow.setFixedSize(150, 40)
        left_layout.addWidget(self.list_elbow)
        
        self.lbl_proj_index = QLabel(Language.translate('PROJECT_INDEX'))
        self.lbl_proj_index.setStyleSheet(f"color: {self.colors['text']}; {get_lcars_font_style(18, 'normal')}")
        left_layout.addWidget(self.lbl_proj_index)
        
        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                border: none;
                border-left: 10px solid {self.colors['button_colors'][0]};
                border-radius: 0px;
                font-size: 14pt;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #333;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['button_colors'][1]};
                color: black;
            }}
        """)
        self._refresh_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        left_layout.addWidget(self.project_list)

        self.btn_refresh = create_lcars_button(Language.translate('REFRESH_INDEX'), parent=self, width=200, height=50, auto_cycle=True)
        self.btn_refresh.clicked.connect(self._refresh_projects)
        left_layout.addWidget(self.btn_refresh)
        
        main_layout.addWidget(left_container, 1)

        # --- RIGHT COLUMN: Operations ---
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # Right Header: Architectural Contour
        header_row = QHBoxLayout()
        header_row.setSpacing(0)
        
        self.ops_elbow = LCARSElbow("top-right", color=self.colors['button_colors'][1], era=self.era)
        self.ops_elbow.setMinimumHeight(60) # Adaptive height
        header_row.addWidget(self.ops_elbow)
        
        right_layout.addLayout(header_row)

        self.lbl_title = QLabel(Language.translate('NO_TARGET'))
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_title.setStyleSheet(f"color: white; {get_lcars_font_style(20, 'normal')}; padding-right: 15px;")
        right_layout.addWidget(self.lbl_title)

        # Status area at bottom
        self.status_bar = QHBoxLayout()
        self.lbl_status = QLabel(Language.translate('NO_PROJECT_SELECTED'))
        self.lbl_status.setStyleSheet(f"color: {self.colors['text']}; {get_lcars_font_style(14, 'normal')}")
        self.status_bar.addWidget(self.lbl_status)
        right_layout.addLayout(self.status_bar)
        
        # Action Buttons Row
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(10)
        
        # Use key-based buttons
        self.btn_build = create_lcars_button('BUILD_SEQUENCE', parent=self, height=60, color=self.colors['button_colors'][2])
        self.btn_run = create_lcars_button('INITIATE_RUN', parent=self, height=60, color=self.colors['button_colors'][0])
        self.btn_view = create_lcars_button('ACCESS_FILES', parent=self, height=60, color=self.colors['button_colors'][1])
        
        self.btn_build.clicked.connect(self._build_project)
        self.btn_run.clicked.connect(self._run_project)
        self.btn_view.clicked.connect(self._open_project_folder)

        self.actions_layout.addWidget(self.btn_build, 1)
        self.actions_layout.addWidget(self.btn_run, 1)
        self.actions_layout.addWidget(self.btn_view, 1)
        right_layout.addLayout(self.actions_layout)

        # Terminal Display
        self.lbl_term_log = QLabel(Language.translate('SYSTEM_OUTPUT_LOG'))
        self.lbl_term_log.setStyleSheet(f"color: {self.colors['button_colors'][2]}; font-size: 12pt; margin-top: 10px;")
        right_layout.addWidget(self.lbl_term_log)

        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet(f"background-color: #050505; color: {self.colors['text']}; font-family: Consolas; font-size: 11pt; border: none; border-right: 5px solid {self.colors['button_colors'][2]};")
        right_layout.addWidget(self.terminal, 1)

        # Command Input
        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText(Language.translate('COMMAND_OVERRIDE'))
        self.cmd_input.setStyleSheet(f"""
            background-color: {self.colors['background']}; 
            color: {self.colors['text']}; 
            border: 1px solid {self.colors['button_colors'][2]}; 
            padding: 5px; 
            font-family: Consolas;
            height: 30px;
        """)   
        self.cmd_input.returnPressed.connect(self._exec_cmd)
        cmd_row.addWidget(self.cmd_input, 1)

        self.btn_exec = create_lcars_button(Language.translate('EXEC'), parent=self, width=100, height=40)
        self.btn_exec.clicked.connect(self._exec_cmd)
        cmd_row.addWidget(self.btn_exec)

        right_layout.addLayout(cmd_row)
        
        main_layout.addWidget(right_container, 2)

    def retranslate_ui(self):
        """Self-update via widgets."""
        if hasattr(self, 'lbl_title') and not self.current_project:
            self.lbl_title.setText(Language.translate('NO_TARGET'))

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

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # Simple window to hold our widget
    window = QWidget()
    layout = QVBoxLayout(window)
    widget = OperationsWidget()
    layout.addWidget(widget)
    
    # Basic styling to simulate LCARS environment
    window.setStyleSheet("background-color: black;")
    window.resize(1024, 768)
    window.show()
    
    sys.exit(app.exec())
