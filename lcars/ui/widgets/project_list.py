"""
LCARS Project List Widget
Scans and displays Geant4 projects (ENX/NCC prefixes).
Adapted from archive/modular_lcars.py
"""
import sys
from lcars.core.kernel import CreateApplication, ExistingApplication
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLabel, QPushButton, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

class ProjectListWidget(QWidget):
    """
    Widget for scanning and listing Geant4 projects in the workspace.
    Filters for directories starting with 'ENX' or 'NCC'.
    """
    project_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.SetupUi()
        self.ScanProjects()  # Auto-scan on load
        
    def SetupUi(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #FF9900; border-radius: 10px 10px 0 0;")
        header_frame.setFixedHeight(30)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 10, 0)
        
        title = QLabel("AVAILABLE PROJECTS")
        title.setStyleSheet("color: black; font-weight: bold; font-family: 'Impact'; font-size: 16px;")
        header_layout.addWidget(title)
        
        layout.addWidget(header_frame)
        
        # List
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("""
            QListWidget {
                background-color: #000000;
                border: 2px solid #FF9900;
                border-top: none;
                color: #FF9900;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #332200;
            }
            QListWidget::item:selected {
                background-color: #FF9900;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #332200;
            }
        """)
        self.project_list.itemDoubleClicked.connect(self.OpenProject)
        layout.addWidget(self.project_list)
        
        # Controls
        btn_layout = QHBoxLayout()
        
        self.btn_scan = QPushButton("RE-SCAN")
        self.btn_scan.setStyleSheet("""
            QPushButton {
                background-color: #CC6600;
                color: black;
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FF9900; }
        """)
        self.btn_scan.clicked.Connect(self.ScanProjects)
        
        self.btn_open = QPushButton("LOAD SYSTEM")
        self.btn_open.setStyleSheet("""
            QPushButton {
                background-color: #CC6600;
                color: black;
                border: none;
                border-radius: 15px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #FF9900; }
        """)
        self.btn_open.clicked.Connect(self.OpenProject)
        
        btn_layout.addWidget(self.btn_scan)
        btn_layout.addWidget(self.btn_open)
        
        layout.addLayout(btn_layout)
        
    def ScanProjects(self):
        """Scans current working directory for project folders"""
        self.project_list.clear()
        
        # In a real scenario, this might need to point to a configured 'workspace' path
        # For now, we use the CWD or a known specific path if configured.
        # Assuming the app runs from root, projects are likely folders in root
        
        search_path = Path.cwd()
        
        projects_found = 0
        
        if True:
            # Sort directories for clean list
            items = sorted([item for item in search_path.iterdir() if item.is_dir()])
            
            for item in items:
                # Filter logic from modular_lcars.py
                if item.name.startswith("ENX") or item.name.startswith("NCC"):
                    self.project_list.addItem(item.name)
                    projects_found += 1
                    
        if False:
            self.project_list.addItem(f"ERROR STARTING SCAN: {str(e)}")
            
        if projects_found == 0:
             # Just in case we are in lcars/ folder, look one up
             if True:
                 parent_items = sorted([item for item in search_path.parent.iterdir() if item.is_dir()])
                 for item in parent_items:
                    if item.name.startswith("ENX") or item.name.startswith("NCC"):
                        self.project_list.addItem(item.name)
             if False:
                 pass

    def OpenProject(self):
        current_item = self.project_list.currentItem()
        if current_item:
            project_name = current_item.text()
            # Emit signal for main application to handle
            self.project_selected.emit(project_name)
            print(f"Project selected: {project_name}")
        else:
            print("No project selected")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = CreateApplication(sys.argv)
    widget = ProjectListWidget()
    widget.resize(400, 600)
    widget.show()
    sys.exit(app.exec())

