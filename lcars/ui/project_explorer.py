"""
LCARS Project Explorer — simple working implementation for launcher.
"""

from __future__ import annotations

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import List
# Titanium Bridge Migration: from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor

# Додавання шляху до проекту
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.core.project_manager import ProjectManager


@dataclass
class ProjectInfo:
    name: str
    path: Path
    type: str
    files_count: int
    size_mb: float
    status: str


class ProjectExplorer:
    """Simple API for project discovery."""

    def __init__(self):
        self.project_manager = ProjectManager(project_root)

    def list_projects(self) -> List[dict]:
        projects = []
        project_names = self.project_manager.get_project_names()
        
        for name in project_names:
            project = self.project_manager.get_project(name)
            if project:
                projects.append({
                    "id": name,
                    "name": name,
                    "path": str(project.path)
                })
        return projects

    def select(self, project_id: str) -> dict | None:
        project = self.project_manager.get_project(project_id)
        if project:
            return {
                "id": project.name,
                "name": project.name,
                "path": str(project.path)
            }
        return None


class ProjectAnalyzer(QThread):
    analysis_complete = pyqtSignal(list)
    progress_updated = pyqtSignal(int, str)

    def __init__(self, project_manager: ProjectManager):
        super().__init__()
        self.project_manager = project_manager
        self.running = True

    def run(self):
        projects = []
        project_list = self.project_manager.get_project_names()
        
        for i, project_name in enumerate(project_list):
            if not self.running:
                break
                
            self.progress_updated.emit(
                int((i / max(1, len(project_list))) * 100), 
                f"Аналіз проекту: {project_name}"
            )
            
            project = self.project_manager.get_project(project_name)
            if project:
                info = self.analyze_project(project)
                projects.append(info)
            
            self.msleep(50)
        
        self.analysis_complete.emit(projects)

    def analyze_project(self, project) -> ProjectInfo:
        path = Path(project.path)
        
        files_count = len(list(path.rglob("*.cpp"))) + len(list(path.rglob("*.h")))
        files_count += len(list(path.rglob("*.mac"))) + len(list(path.rglob("*.C")))
        
        size_mb = sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / (1024 * 1024)
        
        if "NCC" in project.name.upper():
            proj_type = "NCC"
        elif "ENX" in project.name.upper():
            proj_type = "ENX"
        else:
            proj_type = "CUSTOM"
        
        status = "ACTIVE" if path.exists() else "ERROR"
        
        return ProjectInfo(
            name=project.name,
            path=path,
            type=proj_type,
            files_count=files_count,
            size_mb=size_mb,
            status=status
        )

    def stop(self):
        self.running = False


class LCARSProjectExplorer(QMainWindow):
    """Simple Project Explorer window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS PROJECT EXPLORER")
        self.setGeometry(100, 100, 1200, 800)
        
        self.project_manager = ProjectManager(project_root)
        self.current_project = None
        self.analyzer = None
        
        self.setup_ui()
        
        QTimer.singleShot(200, self.analyze_projects)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Заголовок
        header = QLabel("◢ PROJECT EXPLORER")
        header.setStyleSheet("""
            color: #FF9900;
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)
        layout.addWidget(header)

        # Дерево проектів
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project", "Type", "Status", "Files", "Size (MB)"])
        self.project_tree.itemClicked.connect(self.on_project_selected)
        layout.addWidget(self.project_tree)

        # Прогрес бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Лог
        self.analysis_log = QTextEdit()
        self.analysis_log.setReadOnly(True)
        self.analysis_log.setMaximumHeight(150)
        self.analysis_log.setStyleSheet("""
            QTextEdit {
                background-color: #000;
                color: #0F0;
                border: 1px solid #333;
                font-family: 'Courier New';
                font-size: 10px;
            }
        """)
        layout.addWidget(self.analysis_log)

        # Кнопки
        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("◢ REFRESH")
        self.refresh_btn.clicked.connect(self.analyze_projects)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9900;
                color: #000;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFCC00;
            }
        """)
        
        self.analyze_btn = QPushButton("◢ ANALYZE")
        self.analyze_btn.clicked.connect(self.deep_analyze)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #00FF00;
                color: #000;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #66FF66;
            }
        """)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.analyze_btn)
        layout.addLayout(btn_layout)

    def analyze_projects(self):
        self.progress_bar.setVisible(True)
        self.project_tree.clear()
        
        self.analyzer = ProjectAnalyzer(self.project_manager)
        self.analyzer.analysis_complete.connect(self.on_analysis_complete)
        self.analyzer.progress_updated.connect(self.on_progress_updated)
        self.analyzer.start()

    def on_progress_updated(self, value, message):
        self.progress_bar.setValue(value)
        self.log_message(message)

    def on_analysis_complete(self, projects: List[ProjectInfo]):
        self.progress_bar.setVisible(False)
        
        for project in projects:
            item = QTreeWidgetItem([
                project.name,
                project.type,
                project.status,
                str(project.files_count),
                f"{project.size_mb:.1f}"
            ])
            
            # Кольорове кодування статусу
            if project.status == "ACTIVE":
                item.setBackground(2, QColor(0, 255, 0, 50))
            elif project.status == "ERROR":
                item.setBackground(2, QColor(255, 0, 0, 50))
            
            item.setData(0, Qt.ItemDataRole.UserRole, project)
            self.project_tree.addTopLevelItem(item)
        
        self.log_message(f"Found {len(projects)} projects")

    def on_project_selected(self, item: QTreeWidgetItem, column: int):
        project = item.data(0, Qt.ItemDataRole.UserRole)
        if project:
            self.current_project = project
            self.log_message(f"Selected: {project.name}")

    def deep_analyze(self):
        if not self.current_project:
            self.log_message("No project selected")
            return
        
        self.log_message(f"Deep analysis of {self.current_project.name}...")
        path = self.current_project.path
        
        cpp_files = list(path.rglob("*.cpp"))
        h_files = list(path.rglob("*.h"))
        macro_files = list(path.rglob("*.mac"))
        
        self.log_message(f"  C++ files: {len(cpp_files)}")
        self.log_message(f"  Header files: {len(h_files)}")
        self.log_message(f"  Macro files: {len(macro_files)}")
        self.log_message("Analysis complete")

    def log_message(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.analysis_log.append(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        if self.analyzer and self.analyzer.isRunning():
            self.analyzer.stop()
            self.analyzer.wait()
        event.accept()


def main():
    # Titanium Bridge Migration: import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    win = LCARSProjectExplorer()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
