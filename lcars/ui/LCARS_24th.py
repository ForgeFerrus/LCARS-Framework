
"""
LCARS Interface - 24th Century (TNG-Era) OS
A fully functional science workstation in the classic 24th-century aesthetic.
"""

import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QGroupBox, 
                            QTextEdit, QProgressBar, QTabWidget, QListWidget,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QDateTime, QThread
from PyQt6.QtGui import QFont, QColor

# Add project root to path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette
from lcars.ui.dashboard_widgets import SystemMonitorWidget, ConsoleWidget, AIAgentWidget
from lcars.ui.lcars_widgets import LcarsElbow, AnimatedButton
from lcars.core.project_manager import ProjectManager
from lcars.core.geant4_build import BuildWorker

class LCARS24thCentury(QMainWindow):
    """
    Classic TNG-era Science Workstation.
    Full functional integration of Geant4 and Analysis tools.
    """
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        self.root_path = root_path or Path(project_root)
        self.selector = selector
        self.colors = get_era_palette(LCARSEra.LCARS_24TH)
        self.project_manager = ProjectManager(self.root_path)
        
        self.setup_window()
        self.setup_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def setup_window(self):
        self.setWindowTitle("LCARS 24TH - SCIENCE TERMINAL")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: black; font-family: 'Swis721 BT', 'Arial';")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. TNG HEADER (Continuous frame with elbow)
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)
        
        elbow_color = self.colors['button_colors'][1]
        self.elbow = LcarsElbow(color=elbow_color, direction="top-left", size=(180, 120))
        header_layout.addWidget(self.elbow)
        
        self.title_label = QLabel("LCARS CENTRAL COMMAND")
        self.title_label.setStyleSheet(f"font-size: 42px; color: {self.colors['text']}; font-weight: bold; background-color: transparent; padding-left: 20px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"font-size: 32px; color: black; background-color: {elbow_color}; padding: 10px 40px; font-weight: bold;")
        header_layout.addWidget(self.time_label)
        
        self.main_layout.addWidget(header_frame)

        # 2. MAIN WORK AREA (Sidebar + Content + Widgets)
        content_box = QWidget()
        content_layout = QHBoxLayout(content_box)
        content_layout.setContentsMargins(0, 0, 10, 10)
        content_layout.setSpacing(10)
        
        # Sidebar with geometric nav
        sidebar_v = QFrame()
        sidebar_v.setFixedWidth(180)
        sidebar_v.setStyleSheet(f"background-color: {elbow_color}; margin-top: -1px;")
        sidebar_lay = QVBoxLayout(sidebar_v)
        sidebar_lay.setContentsMargins(5, 5, 5, 5)
        sidebar_lay.setSpacing(5)
        
        nav_items = [
            ("PROJECTS", 0, self.colors['button_colors'][0]),
            ("SIMULATION", 1, self.colors['button_colors'][2]),
            ("ANALYSIS", 2, self.colors['button_colors'][3]),
            ("SETTINGS", 3, self.colors['button_colors'][4])
        ]
        
        for name, idx, clr in nav_items:
            btn = QPushButton(name)
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, i=idx: self.tab_stack.setCurrentIndex(i))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {clr};
                    border: none;
                    border-top-left-radius: 25px;
                    border-bottom-left-radius: 25px;
                    color: black;
                    font-weight: bold;
                    font-size: 16px;
                    text-align: right;
                    padding-right: 15px;
                }}
                QPushButton:hover {{ background-color: white; }}
            """)
            sidebar_lay.addWidget(btn)
            
        sidebar_lay.addStretch()
        
        # BACK button
        back_btn = QPushButton("EXIT CORE")
        back_btn.setFixedHeight(50)
        back_btn.clicked.connect(self.return_to_selector)
        back_btn.setStyleSheet(f"background-color: #CC3333; color: white; border-radius: 25px; font-weight: bold;")
        sidebar_lay.addWidget(back_btn)
        
        content_layout.addWidget(sidebar_v)
        
        # Central Display Stack
        self.tab_stack = QTabWidget()
        self.tab_stack.tabBar().hide()
        self.tab_stack.setStyleSheet(f"""
            QTabWidget::pane {{ border: 4px solid {elbow_color}; border-top-right-radius: 30px; background: black; }}
        """)
        
        self.tab_stack.addTab(self.create_projects_tab(), "PROJECTS")
        self.tab_stack.addTab(self.create_simulation_tab(), "SIMULATION")
        self.tab_stack.addTab(self.create_analysis_tab(), "ANALYSIS")
        self.tab_stack.addTab(QLabel("SYSTEM SETTINGS STANDBY"), "SETTINGS")
        
        content_layout.addWidget(self.tab_stack, 4)
        
        # Right Side Widgets
        right_v = QVBoxLayout()
        right_v.setSpacing(10)
        right_v.addWidget(SystemMonitorWidget())
        right_v.addWidget(AIAgentWidget())
        self.console = ConsoleWidget()
        right_v.addWidget(self.console, 1)
        
        content_layout.addLayout(right_v, 2)
        
        self.main_layout.addWidget(content_box, 1)

    def create_projects_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.addWidget(QLabel("◢ SHIP-WIDE PROJECT REGISTRY"))
        
        self.proj_list = QListWidget()
        self.proj_list.setStyleSheet(f"background: transparent; border: 1px solid #333; color: {self.colors['text']}; font-size: 16px;")
        projects = self.project_manager.get_project_names()
        self.proj_list.addItems(projects)
        lay.addWidget(self.proj_list)
        
        return tab

    def create_simulation_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.addWidget(QLabel("◢ GEANT4 BATTLE-BRIDGE SIMULATION TERMINAL"))
        
        ctrls = QHBoxLayout()
        for name, cmd, clr in [("INITIATE BUILD", self.exec_build, self.colors['button_colors'][0]),
                               ("ENGAGE SIM", self.exec_run, self.colors['button_colors'][2])]:
            btn = AnimatedButton(name)
            btn.setFixedHeight(40)
            btn.set_color(QColor(clr))
            btn.clicked.connect(cmd)
            ctrls.addWidget(btn)
        lay.addLayout(ctrls)
        
        self.sim_log = QTextEdit()
        self.sim_log.setReadOnly(True)
        self.sim_log.setStyleSheet("background: #000; color: #FF9900; font-family: 'Consolas'; font-size: 11px; border: 1px solid #333;")
        lay.addWidget(self.sim_log)
        
        return tab

    def create_analysis_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.addWidget(QLabel("◢ SPECTROMETRIC DATA ANALYSIS"))
        
        self.analysis_table = QTableWidget(0, 3)
        self.analysis_table.setHorizontalHeaderLabels(["ENERGY", "COUNTS", "PARTICLE"])
        self.analysis_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.analysis_table.setStyleSheet(f"background: transparent; color: white; border: 1px solid #333;")
        lay.addWidget(self.analysis_table)
        
        btn = AnimatedButton("ANALYZE SENSORS")
        btn.clicked.connect(self.simulate_analysis)
        lay.addWidget(btn)
        
        return tab

    def update_time(self):
        self.time_label.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))

    def exec_build(self):
        item = self.proj_list.currentItem()
        if not item: return
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        self.worker = BuildWorker(proj.path, "build")
        self.worker.output_signal.connect(lambda m: self.sim_log.append(m))
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def exec_run(self):
        item = self.proj_list.currentItem()
        if not item: return
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        self.worker = BuildWorker(proj.path, "run")
        self.worker.output_signal.connect(lambda m: self.sim_log.append(m))
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def simulate_analysis(self):
        self.analysis_table.setRowCount(0)
        for i in range(8):
            self.analysis_table.insertRow(i)
            self.analysis_table.setItem(i, 0, QTableWidgetItem(f"{random.uniform(10, 500):.2f} MeV"))
            self.analysis_table.setItem(i, 1, QTableWidgetItem(f"{random.randint(50, 1000)}"))
            self.analysis_table.setItem(i, 2, QTableWidgetItem("NEUTRON"))

    def return_to_selector(self):
        if self.selector: self.selector.restore_selector()
        else: self.close()

def main():
    app = QApplication(sys.argv)
    window = LCARS24thCentury()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
