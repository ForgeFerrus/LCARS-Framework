"""Simple IDE-like panel for Geant4 workstation.

Combines a file browser, a text editor and a console.  This is not a full
VSCode clone but gives basic file editing and execution capabilities.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton, QPlainTextEdit, QLabel
)
from PyQt6.QtCore import Qt
from pathlib import Path
import subprocess, sys

from lcars.modules.file_manager import FileManager
from lcars.ui.views.console import ConsoleView


class IDEWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # file manager on left
        # disable auto-open so we can intercept activation ourselves
        self.fm = FileManager(self, base_dir=Path.cwd(), auto_open=False)
        # connect double-click to load into editor (FileManager won't launch external app)
        if hasattr(self.fm, 'file_list'):
            self.fm.file_list.itemDoubleClicked.connect(self._on_file_selected)
        splitter.addWidget(self.fm)

        # right side: editor + console
        right_split = QSplitter(Qt.Orientation.Vertical)
        # editor
        self.editor = QPlainTextEdit()
        self.editor.setPlainText("# write Python code here\n")
        right_split.addWidget(self.editor)

        # run button
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.run_code)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addStretch()
        container = QWidget()
        container.setLayout(btn_layout)
        right_split.addWidget(container)

        # console view
        self.console = ConsoleView(event_bus=None)
        right_split.addWidget(self.console)

        splitter.addWidget(right_split)
        layout.addWidget(splitter)

    def run_code(self):
        text = self.editor.toPlainText()
        # execute in subprocess so output appears in console
        try:
            proc = subprocess.Popen([sys.executable, "-c", text],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True)
            out, _ = proc.communicate(timeout=5)
            self.console.on_output(out)
        except Exception as e:
            self.console.on_output(f"[error] {e}")

    def _on_file_selected(self, item):
        # load file contents into editor if it's a file
        name = item.text().rstrip("/")
        target = self.fm.base_dir / name
        if target.is_file():
            try:
                self.editor.setPlainText(target.read_text())
            except Exception as e:
                self.console.on_output(f"[error] cannot read {target}: {e}")
