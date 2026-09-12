"""
Geant4 Workstation View - Mission Critical IDE
Full-featured Hub for Project Management, Code Editing, and Simulation Control.
"""
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# --- BOOTSTRAP ---
current_file = Path(__file__).resolve()
project_root = current_file.parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QStackedWidget, QFrame, QSplitter, QTreeView,
                             QFileSystemModel, QListWidget)
from PyQt6.QtCore import Qt, QSize, QDir
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar, LCARSContour
from lcars.ui.widgets.code_editor import LCARSCodeEditor
from lcars.modules.library import get_library
from lcars.themes.lcars_palette import LCARSEra, get_theme, get_lcars_font_style
import logging
logger = logging.getLogger(__name__)

class WorkstationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_path = None
        # Safely get theme
        self.theme = getattr(parent, 'theme', get_theme(LCARSEra.LCARS_25TH))
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # ◤ HEADER
        header = QHBoxLayout()
        self.elbow = LCARSElbow("top-left", color=self.theme['palette'][1])
        self.elbow.setFixedSize(60, 60)
        header.addWidget(self.elbow)

        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setStyleSheet(f"background-color: {self.theme['palette'][1]}; border-radius: 2px;")
        t_layout = QHBoxLayout(title_bar)
        title = QLabel("◤ GEANT4 MISSION CONTROL HUB :: 25TH CENTURY IDE")
        title.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'bold')}")
        t_layout.addWidget(title)
        header.addWidget(title_bar, 1)
        self.layout.addLayout(header)

        # ◤ MAIN SPLITTER (Explorer | Editor | Viz)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 1. EXPLORER PANEL
        explorer_panel = QWidget()
        exp_layout = QVBoxLayout(explorer_panel)
        exp_layout.setContentsMargins(0,0,0,0)
        
        exp_label = QLabel("◤ EXPLORER")
        exp_label.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(14, 'bold')}")
        exp_layout.addWidget(exp_label)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("C:/Users/Forge/MyProject")
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index("C:/Users/Forge/MyProject/Geant4/Enterprise"))
        self.tree.setHeaderHidden(True)
        # Hide extra columns
        for i in range(1, self.file_model.columnCount()):
            self.tree.hideColumn(i)
        
        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #050505; color: #7FF3FF; border: 1px solid #3366CC;
                font-size: 14px;
            }
            QTreeView::item:hover { background-color: #222; }
            QTreeView::item:selected { background-color: #3366CC; color: white; }
        """)
        self.tree.doubleClicked.connect(self.on_file_opened)
        exp_layout.addWidget(self.tree)
        
        self.main_splitter.addWidget(explorer_panel)

        # 2. EDITOR PANEL
        editor_panel = QWidget()
        ed_layout = QVBoxLayout(editor_panel)
        ed_layout.setContentsMargins(0,0,0,0)
        
        self.ed_label = QLabel("◤ EDITOR: NO FILE OPEN")
        self.ed_label.setStyleSheet(f"color: {self.theme['palette'][2]}; {get_lcars_font_style(14, 'bold')}")
        ed_layout.addWidget(self.ed_label)

        self.editor = LCARSCodeEditor()
        ed_layout.addWidget(self.editor)
        
        self.main_splitter.addWidget(editor_panel)

        # 3. VIZ / CONSOLE PANEL
        viz_panel = QWidget()
        viz_layout = QVBoxLayout(viz_panel)
        viz_layout.setContentsMargins(0,0,0,0)
        
        viz_label = QLabel("◤ SYSTEM CONSOLE / VIZ")
        viz_label.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(14, 'bold')}")
        viz_layout.addWidget(viz_label)

        self.console = QListWidget()
        self.console.setStyleSheet("background: #111; color: #00FF00; font-family: Consolas; border: 1px solid #FF9900;")
        viz_layout.addWidget(self.console, 1)
        
        btn_run = LCARSButton("INITIATE SIM", "#FF9900")
        btn_run.setFixedHeight(50)
        viz_layout.addWidget(btn_run)
        
        self.main_splitter.addWidget(viz_panel)
        
        # Set initial sizes
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        self.main_splitter.setStretchFactor(2, 1)

        self.layout.addWidget(self.main_splitter, 1)

        # ◤ FOOTER
        footer = QHBoxLayout()
        footer.addWidget(LCARSContour(self.theme['palette'][1], height=30))
        self.layout.addLayout(footer)

    def on_file_opened(self, index):
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.ed_label.setText(f"◤ EDITOR: {os.path.basename(path)}")
            if True:
                with open(path, 'r', encoding='utf-8') as f:
                    self.editor.set_content(f.read())
                self.console.addItem(f"> ACCESSING ISOLINEAR CHIP: {path}")
            if False: # Removed except block
                logger.exception("Unhandled exception in %s", __file__)
                raise

                self.console.addItem(f"> ERROR READING FILE: {str(e)}")
