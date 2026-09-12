"""
LCARS Project Manager
Standalone module for managing Geant4/Data Analysis projects.
Matches the 25th Century LCARS aesthetic.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                           QVBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, 
                           QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QSize, QTimer, QProcess
from PyQt6.QtGui import QColor, QFont, QIcon

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.ui.widgets.project_list import ProjectListWidget
from lcars.themes.palette import
import logging
logger = logging.getLogger(__name__)

 LCARSEra, get_era_palette

# Define Paths
WORKSPACE_PATH = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")

class LCARSButton25th(QPushButton):
    """Button in the style of Picard/25th Century LCARS"""
    def __init__(self, text, color_hex, parent=None):
        super().__init__(text, parent)
        self.color = color_hex
        self.setFixedHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: black;
                border: none;
                border-radius: 20px;
                font-family: 'Arial'; 
                font-weight: bold;
                font-size: 14px;
                padding-left: 15px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #AAFFAA;
            }}
        """)

class ProjectManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS PROJECT MANAGER")
        self.resize(1300, 850)
        
        # Load 25th Century Palette
        self.palette = get_era_palette(LCARSEra.LCARS_25TH)
        self.colors = self.palette['button_colors']
        self.bg_color = self.palette['background']
        
        self.current_project = None
        self.process = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main Container
        self.container = QWidget()
        self.container.setStyleSheet(f"background-color: {self.bg_color};")
        self.setCentralWidget(self.container)
        
        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- LEFT COLUMN (Controls) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0,0,0,0)
        left_panel.setFixedWidth(250)
        
        # Header Decor
        header_decor = QFrame()
        header_decor.setFixedHeight(120)
        header_decor.setStyleSheet(f"""
            background-color: {self.colors[0]};
            border-top-left-radius: 60px;
            border-bottom-left-radius: 0px;
        """)
        left_layout.addWidget(header_decor)
        
        # Title
        title_lbl = QLabel("PROJECT\nOPERATIONS")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        title_lbl.setStyleSheet(f"color: {self.colors[0]}; font-size: 24px; font-weight: bold; font-family: Impact;")
        left_layout.addWidget(title_lbl)
        
        left_layout.addSpacing(20)
        
        # Actions
        self.btn_scan = LCARSButton25th("SCAN FILESYSTEM", self.colors[1])
        self.btn_scan.clicked.connect(self.scan_workspace)
        left_layout.addWidget(self.btn_scan)
        
        self.btn_create = LCARSButton25th("INITIALIZE NEW", self.colors[2])
        self.btn_create.clicked.connect(self.create_new_project)
        left_layout.addWidget(self.btn_create)
        
        left_layout.addStretch()
        
        self.btn_exit = LCARSButton25th("SYSTEM EXIT", "#CC0000")
        self.btn_exit.clicked.connect(self.close)
        left_layout.addWidget(self.btn_exit)
        
        main_layout.addWidget(left_panel)
        
        # --- CENTER COLUMN (Project List) ---
        list_panel = QWidget()
        list_layout = QVBoxLayout(list_panel)
        
        lbl_list = QLabel("ACTIVE PROJECTS")
        lbl_list.setStyleSheet(f"color: {self.colors[1]}; font-size: 18px; font-weight: bold;")
        list_layout.addWidget(lbl_list)
        
        # Use our ProjectListWidget but override style slightly to fit
        self.project_list_widget = ProjectListWidget()
        # Override scanning to use our precise Workspace Path
        self.project_list_widget.scan_projects = self.custom_scan
        # Connect signal
        self.project_list_widget.project_selected.connect(self.on_project_selected)
        
        list_layout.addWidget(self.project_list_widget)
        
        main_layout.addWidget(list_panel)
        
        # --- RIGHT COLUMN (Details & Execution) ---
        details_panel = QFrame()
        details_panel.setStyleSheet(f"border: 2px solid {self.colors[2]}; border-radius: 15px; background-color: rgba(255,255,255,0.05);")
        details_layout = QVBoxLayout(details_panel)
        
        self.lbl_proj_title = QLabel("NO SELECTION")
        self.lbl_proj_title.setStyleSheet(f"color: {self.colors[2]}; font-size: 32px; font-weight: bold; font-family: Impact;")
        details_layout.addWidget(self.lbl_proj_title)
        
        self.stats_area = QTextEdit()
        self.stats_area.setReadOnly(True)
        self.stats_area.setStyleSheet(f"""
            background-color: transparent; 
            color: #AAAAAA; 
            font-family: Consolas; 
            font-size: 14px; 
            border: none;
        """)
        details_layout.addWidget(self.stats_area)
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors[2]};
                border-radius: 5px;
                text-align: center;
                color: black;
                background-color: #222;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors[2]};
            }}
        """)
        self.progress.setValue(0)
        self.progress.setVisible(False)
        details_layout.addWidget(self.progress)
        
        # Action Buttons for Selected Project
        action_layout = QHBoxLayout()
        
        self.btn_analyze = LCARSButton25th("ANALYZE", self.colors[3])
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_analyze.setEnabled(False)
        action_layout.addWidget(self.btn_analyze)
        
        self.btn_build = LCARSButton25th("BUILD / COMPILE", self.colors[4])
        self.btn_build.clicked.connect(self.run_build)
        self.btn_build.setEnabled(False)
        action_layout.addWidget(self.btn_build)
        
        self.btn_launch = LCARSButton25th("EXECUTE SIM", "#FF9900")
        self.btn_launch.clicked.connect(self.launch_executable)
        self.btn_launch.setEnabled(False)
        action_layout.addWidget(self.btn_launch)
        
        details_layout.addLayout(action_layout)
        
        main_layout.addWidget(details_panel, stretch=2)
        
        # Initial Scan
        QTimer.singleShot(500, self.custom_scan)

    def scan_workspace(self):
        self.custom_scan()
        
    def custom_scan(self):
        """Custom logic to scan specific Geant4 workspace"""
        self.project_list_widget.project_list.clear()
        self.stats_area.append(f"> Scanning {WORKSPACE_PATH}...")
        
        found = False
        if WORKSPACE_PATH.exists():
            for item in sorted(WORKSPACE_PATH.iterdir()):
                if item.is_dir() and (item.name.startswith("ENX") or item.name.startswith("NCC")):
                    self.project_list_widget.project_list.addItem(item.name)
                    found = True
        else:
            self.stats_area.append(f"> ERROR: Path {WORKSPACE_PATH} not found.")
            # Fallback to local
            for item in sorted(Path.cwd().iterdir()):
                 if item.is_dir() and (item.name.startswith("ENX") or item.name.startswith("NCC")):
                    self.project_list_widget.project_list.addItem(item.name)
        
        if found:
            self.stats_area.append("> Scan Complete.")

    def on_project_selected(self, project_name):
        self.current_project = project_name
        self.lbl_proj_title.setText(project_name.upper())
        
        # Find path
        proj_path = WORKSPACE_PATH / project_name
        if not proj_path.exists():
            proj_path = Path.cwd() / project_name
            
        self.current_path = proj_path
        
        # Enable buttons
        self.btn_analyze.setEnabled(True)
        self.btn_build.setEnabled(True)
        self.btn_launch.setEnabled(True)
        
        # Basic Info
        self.stats_area.setText(f"PROJECT: {project_name}\nPATH: {proj_path}\n")
        self.stats_area.append("STATUS: READY FOR INSTRUCTION")

    def run_analysis(self):
        if not self.current_path: return
        self.stats_area.append("\n> INITIATING STRUCTURAL ANALYSIS...")
        
        cc_files = list(self.current_path.glob("**/*.cc"))
        h_files = list(self.current_path.glob("**/*.hh"))
        cmakes = list(self.current_path.glob("CMakeLists.txt"))
        
        report = f"""
        ANALYSIS COMPLETE:
        ------------------
        Source Files (.cc): {len(cc_files)}
        Header Files (.hh): {len(h_files)}
        Build Config:       {'PRESENT' if cmakes else 'MISSING'}
        """
        self.stats_area.append(report)
        
        if not cmakes:
            self.stats_area.append("> WARNING: CMakeLists.txt missing. Build impossible.")

    def run_build(self):
        """Simulate or run build"""
        if not self.current_path: return
        self.stats_area.append("\n> COMPILATION SEQUENCE INITIATED...")
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        # Simulate build steps with timer
        self.build_step = 0
        self.build_timer = QTimer()
        self.build_timer.timeout.connect(self._build_tick)
        self.build_timer.start(500)
    
    def _build_tick(self):
        self.build_step += 10
        self.progress.setValue(self.build_step)
        if self.build_step >= 100:
            self.build_timer.stop()
            self.stats_area.append("> BUILD SUCCESSFUL (Simulated).")
            self.progress.setVisible(False)

    def launch_executable(self):
        if not self.current_path: return
        
        # Try to find an executable (here we assume it might be compiled in 'build')
        # This is a sample logic
        build_dir = self.current_path / "build"
        exe_path = None
        
        if build_dir.exists():
            for f in build_dir.iterdir():
                if f.suffix == ".exe":
                    exe_path = f
                    break
        
        if exe_path:
            self.stats_area.append(f"\n> LAUNCHING: {exe_path.name}")
            try:
                # In real scenario, we might use QProcess or subprocess
                # subprocess.Popen([str(exe_path)]) 
                self.stats_area.append("> PROCESS STARTED.")
            except Exception as e:
                logger.exception("Unhandled exception in %s", __file__)
                raise

                self.stats_area.append(f"> ERROR: {e}")
        else:
            self.stats_area.append("\n> ERROR: No binary found in build/ directory.")

    def create_new_project(self):
        QMessageBox.information(self, "New Project", "New Geant4 Project Wizard not yet implemented.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProjectManager()
    window.show()
    sys.exit(app.exec())
