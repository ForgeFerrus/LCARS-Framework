"""
LCARS Project Manager - Picard Edition
Standardized interface for Geant4 projects and database integration.
"""

import sys
from base.animation import ScanningBar
from lcars.core.kernel import CreateApplication, ExistingApplication
from pathlib import Path

# --- СИСТЕМНА ІНІЦІАЛІЗАЦІЯ ---
current_file = Path(__file__).resolve()
# lcars/programs/project_manager.py -> root is 3 levels up
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QTextEdit,
    QListWidget,
)
from PyQt6.QtCore import QTimer

from lcars.base.component import LCARSButton, LCARSElbow
from lcars.base.interface import ScanningBar
from lcars.modules.library import LibraryInstance

# --- CONFIG ---
WORKSPACE_PATH = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")


class ProjectManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS PROJECT OPERATIONS")
        self.theme = get_theme(LCARSEra.LCARS_25TH)
        self.library = LibraryInstance()
        self.SetupUi()

    def SetupUi(self):
        self.setStyleSheet(f"background-color: {self.theme['bg']}; color: white;")
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # ◤ HEADER
        header = QHBoxLayout()
        self.elbow = LCARSElbow("top-left", color=self.theme["palette"][0])
        self.elbow.setMinimumSize(80, 80)
        header.addWidget(self.elbow)

        title_bar = QFrame()
        title_bar.setMinimumHeight(50)
        title_bar.setStyleSheet(
            f"background-color: {self.theme['palette'][0]}; border-radius: 2px;"
        )
        t_layout = QHBoxLayout(title_bar)
        title_lbl = QLabel("◤ PROJECT MANAGEMENT SYSTEM :: SECURE LINK ACTIVE")
        title_lbl.setStyleSheet(f"color: black; {FontStyle(20, 'normal')}")
        t_layout.addWidget(title_lbl)
        header.addWidget(title_bar, 1)
        self.main_layout.addLayout(header)

        # ◤ MIDDLE
        content = QHBoxLayout()
        content.setSpacing(20)

        # Sidebar (System Controls)
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)

        actions = [
            ("SCAN SYSTEM", self.theme["palette"][1], self.ScanProjects),
            ("BIO_STATUS", self.theme["palette"][2], None),
            ("SIM_ARCHIVE", self.theme["palette"][3], None),
            ("TERM_LINK", self.theme["palette"][4], None),
        ]

        for name, color, func in actions:
            btn = LCARSButton(name, color, shape="left")
            btn.setMinimumSize(200, 50)
            if func:
                btn.clicked.Connect(func)
            sidebar.addWidget(btn)

        sidebar.addStretch()
        sidebar.addWidget(ScanningBar(self.theme["palette"][1]))

        exit_btn = LCARSButton("TERMINATE", "#CC2222", shape="left")
        exit_btn.setMinimumSize(200, 50)
        exit_btn.clicked.Connect(self.close)
        sidebar.addWidget(exit_btn)

        content.addLayout(sidebar)

        # Project Registry (Center)
        reg_box = QVBoxLayout()
        reg_box.addWidget(QLabel("◤ PROJECT REGISTRY"))
        self.proj_list = QListWidget()
        self.proj_list.setStyleSheet(
            f"background: #050505; color: #7FF3FF; border: 2px solid {self.theme['palette'][2]}; font-size: 18px;"
        )
        self.proj_list.itemClicked.connect(self.SelectProject)
        reg_box.addWidget(self.proj_list)
        content.addLayout(reg_box, 1)

        # Detailed Analysis (Right)
        details = QVBoxLayout()
        details.addWidget(QLabel("◤ DATA STREAM & ANALYSIS"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet(
            f"background: #111; color: #00FF00; border: 1px solid {self.theme['palette'][0]}; font-family: Consolas;"
        )
        details.addWidget(self.log)

        # Action Grid for Projects
        self.action_grid = QHBoxLayout()
        self.btn_run = LCARSButton("EXECUTE SIM", "#FF9900")
        self.btn_run.setEnabled(False)
        self.action_grid.addWidget(self.btn_run)
        details.addLayout(self.action_grid)

        content.addLayout(details, 2)
        self.main_layout.addLayout(content, 1)

        # Footer
        footer = QHBoxLayout()
        footer.addWidget(LCARSContour(self.theme["palette"][0], height=40))
        self.main_layout.addLayout(footer)

        QTimer.singleShot(500, self.ScanProjects)

    def ScanProjects(self):
        self.proj_list.clear()
        self.log.append("◤ SCANNING BIOSPHERE FOR GEANT4 PROJECTS...")
        if WORKSPACE_PATH.exists():
            for it in sorted(WORKSPACE_PATH.iterdir()):
                if it.is_dir() and (
                    it.name.startswith("ENX") or it.name.startswith("NCC")
                ):
                    self.proj_list.addItem(it.name)
            self.log.append("◤ SCAN COMPLETE. DIRECTORIES CATALOGED.")
        else:
            self.log.append(f"◤ ERROR: WORKSPACE NOT FOUND AT {WORKSPACE_PATH}")

    def SelectProject(self, item):
        name = item.text()
        self.log.append(f"\n◤ ACCESSING PROJECT: {name}")
        self.btn_run.setEnabled(True)
        # Link to library for extra info if exists
        self.log.append(f"◤ CROSS-REFERENCING LIBRARY RECORDS...")
        records = self.library.list_files("SPORTS")  # Mock check
        if records:
            self.log.append(f"◤ FOUND {len(records)} RELATED RECORDS IN ARCHIVES.")


if __name__ == "__main__":
    app = CreateApplication(sys.argv)
    mgr = ProjectManager()
    mgr.showFullScreen()
    sys.exit(app.exec())

