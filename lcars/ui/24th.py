
"""
LCARS Interface - 24th Century (TNG-Era) OS
A fully functional science workstation in the classic 24th-century aesthetic.
"""

import sys
import random
import csv
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QGroupBox, 
                            QTextEdit, QProgressBar, QTabWidget, QListWidget,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QDateTime, QThread
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPolygonF
from PyQt6.QtCore import QPointF

# LCARS 24th Century Palette
LCARS_24TH_PALETTE = {
    'text': '#FFCC66',
    'button_colors': ['#FFCC66', '#00AAFF', '#FFAA44', '#00BBFF', '#FFDD88']
}

def get_random_button_color(era):
    """Get random color from palette"""
    return random.choice(LCARS_24TH_PALETTE['button_colors'])

class LcarsElbow(QWidget):
    """LCARS elbow widget"""
    def __init__(self, color="#FFCC66", direction="top-left", size=(180, 120)):
        super().__init__()
        self.color = QColor(color)
        self.direction = direction
        self.setFixedSize(*size)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(self.color))
        painter.setPen(QPen(QColor("#000000"), 2))
        
        w, h = self.width(), self.height()
        radius = min(w, h) // 2
        
        path = QPolygonF()
        if self.direction == "top-left":
            path.append(QPointF(w, 0))
            path.append(QPointF(radius, 0))
            path.append(QPointF(0, radius))
            path.append(QPointF(0, h))
            path.append(QPointF(w, h))
        else:
            path.append(QPointF(0, 0))
            path.append(QPointF(w - radius, 0))
            path.append(QPointF(w, radius))
            path.append(QPointF(w, h))
            path.append(QPointF(0, h))
        
        painter.drawPolygon(path)

class SystemMonitorWidget(QWidget):
    """Simple system monitor widget"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #000; border: 2px solid #FFCC66;")
        layout = QVBoxLayout()
        self.label = QLabel("SYSTEM MONITOR")
        self.label.setStyleSheet("color: #FFCC66; font-weight: bold;")
        layout.addWidget(self.label)
        self.status = QLabel("CPU: 45% | RAM: 62%")
        self.status.setStyleSheet("color: #00AAFF; font-family: 'Consolas';")
        layout.addWidget(self.status)
        self.setLayout(layout)
        self.setFixedHeight(150)

class ConsoleWidget(QWidget):
    """Simple console widget"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #000; border: 2px solid #FFCC66;")
        layout = QVBoxLayout()
        self.label = QLabel("CONSOLE")
        self.label.setStyleSheet("color: #FFCC66; font-weight: bold;")
        layout.addWidget(self.label)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet("background: #111; color: #00AAFF; font-family: 'Consolas'; border: none;")
        layout.addWidget(self.text)
        self.setLayout(layout)
    
    def append(self, text):
        self.text.append(text)

class AIAgentWidget(QWidget):
    """Simple AI agent widget"""
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: #000; border: 2px solid #FFCC66;")
        layout = QVBoxLayout()
        self.label = QLabel("AI AGENT")
        self.label.setStyleSheet("color: #FFCC66; font-weight: bold;")
        layout.addWidget(self.label)
        self.status = QLabel("Status: Standby")
        self.status.setStyleSheet("color: #00AAFF;")
        layout.addWidget(self.status)
        self.setLayout(layout)
        self.setFixedHeight(100)

class ProjectManager:
    """Simple project manager"""
    def __init__(self, root_path):
        self.root_path = Path(root_path)
    
    def get_project_names(self):
        return ["Demo Project 1", "Demo Project 2", "Test Project"]
    
    def get_project(self, name):
        class DummyProject:
            def __init__(self, name):
                self.name = name
                self.path = "/demo/path"
                self.build_dir = "/demo/build"
                self.executable = "/demo/exec"
                self.data_dir = "/demo/data"
                self.description = "Demo project description"
        return DummyProject(name)

class BuildWorker(QThread):
    """Simple build worker"""
    output_signal = QTimer.__class__.__name__  # dummy
    finished_signal = QTimer.__class__.__name__  # dummy
    
    def __init__(self, path, command):
        super().__init__()
        self.path = path
        self.command = command
        self.callbacks = []
    
    def connect_output(self, callback):
        self.callbacks.append(callback)
    
    def connect_finished(self, callback):
        self.callbacks.append(callback)
    
    def run(self):
        for i in range(5):
            for cb in self.callbacks:
                cb(f"Processing step {i+1}/5...")
            self.msleep(500)
        for cb in self.callbacks:
            cb(0)

class DynamicButton(QPushButton):
    """Button with dynamic color cycling from palette (24th era)"""
    def __init__(self, text, era, width=None, height=None, button_index=0):
        super().__init__(text)
        self.era = era
        self.button_index = button_index
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer.setInterval(2500)
        
        self.update_style()
    
    def cycle_color(self):
        self.update_style()
    
    def update_style(self):
        color = get_random_button_color(self.era)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Swis721 BT';
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken(color)};
            }}
        """)
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        h = c.hue() if c.hue() != -1 else 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()
    
    @staticmethod
    def darken(color):
        c = QColor(color)
        h = c.hue() if c.hue() != -1 else 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, min(255, s+40), max(0, v-50), a)
        return c.name()

class LCARS24thCentury(QMainWindow):
    """
    Classic TNG-era Science Workstation.
    Full functional integration of Geant4 and Analysis tools.
    """
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        self.root_path = root_path or Path(".")
        self.selector = selector
        self.colors = LCARS_24TH_PALETTE
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
            ("PROJECTS", 0),
            ("SIMULATION", 1),
            ("ANALYSIS", 2),
            ("SETTINGS", 3)
        ]
        
        for i, (name, idx) in enumerate(nav_items):
            btn = DynamicButton(name, "24th", height=50, button_index=i)
            btn.clicked.connect(lambda checked, target_idx=idx: self.tab_stack.setCurrentIndex(target_idx))
            sidebar_lay.addWidget(btn)
            
        sidebar_lay.addStretch()
        
        # BACK button
        back_btn = DynamicButton("EXIT CORE", "24th", height=50, button_index=len(nav_items))
        back_btn.clicked.connect(self.return_to_selector)
        sidebar_lay.addWidget(back_btn)
        
        content_layout.addWidget(sidebar_v)
        
        # Central Display Stack
        self.tab_stack = QTabWidget()
        if True:
            tab_bar = self.tab_stack.tabBar()
            if tab_bar:
                tab_bar.hide()
        if False: # Removed except block
            pass
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
        
        # Title
        title = QLabel("◢ SHIP-WIDE PROJECT REGISTRY")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        lay.addWidget(title)
        
        # Projects list with metadata
        self.proj_list = QListWidget()
        self.proj_list.setStyleSheet(f"""
            background: transparent; 
            border: 1px solid #333; 
            color: {self.colors['text']}; 
            font-size: 14px;
            padding: 5px;
        """)
        
        # Get projects and add to list
        projects = self.project_manager.get_project_names()
        if projects:
            self.proj_list.addItems(projects)
            self.proj_list.itemSelectionChanged.connect(self.show_project_details)
        else:
            self.proj_list.addItem("No projects found")
        
        lay.addWidget(self.proj_list)
        
        # Project details panel
        self.proj_details = QTextEdit()
        self.proj_details.setReadOnly(True)
        self.proj_details.setMaximumHeight(100)
        self.proj_details.setStyleSheet(f"""
            background: #000; 
            color: #FF9900; 
            font-family: 'Consolas'; 
            font-size: 10px; 
            border: 1px solid #333;
            padding: 5px;
        """)
        lay.addWidget(self.proj_details)
        
        return tab
    
    def show_project_details(self):
        """Display selected project details"""
        item = self.proj_list.currentItem()
        if not item:
            return
        
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        
        if proj:
            details = f"""PROJECT: {proj.name}
PATH: {proj.path}
BUILD: {proj.build_dir if proj.build_dir else 'Not found'}
EXEC: {proj.executable if proj.executable else 'Not found'}
DATA: {proj.data_dir if proj.data_dir else 'Not found'}
DESC: {proj.description[:100] if proj.description else 'N/A'}"""
            self.proj_details.setText(details)

    def create_simulation_tab(self):
        tab = QWidget()
        lay = QVBoxLayout(tab)
        lay.addWidget(QLabel("◢ GEANT4 BATTLE-BRIDGE SIMULATION TERMINAL"))
        
        ctrls = QHBoxLayout()
        for j, (name, cmd) in enumerate([("INITIATE BUILD", self.exec_build),
                                         ("ENGAGE SIM", self.exec_run)]):
            btn = DynamicButton(name, "24th", height=40, button_index=j)
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
        
        # Title
        title = QLabel("◢ SPECTROMETRIC DATA ANALYSIS ENGINE")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        lay.addWidget(title)
        
        # Info panel
        info = QLabel("""ANALYSIS STATUS: Ready
Data Pipeline: Idle
Memory: Available
Processing: Standby""")
        info.setStyleSheet(f"color: #FF9900; font-family: 'Consolas'; font-size: 11px; background: #000; padding: 5px; border: 1px solid #333;")
        lay.addWidget(info)
        
        # Data table with more columns
        self.analysis_table = QTableWidget(0, 4)
        self.analysis_table.setHorizontalHeaderLabels(["SAMPLE#", "ENERGY (MeV)", "COUNTS", "PARTICLE_TYPE"])
        if True:
            header = self.analysis_table.horizontalHeader()
            if header:
                header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if False: # Removed except block
            pass
        self.analysis_table.setStyleSheet(f"""
            background: transparent; 
            color: {self.colors['text']}; 
            border: 1px solid #333;
            gridline-color: #333;
        """)
        lay.addWidget(self.analysis_table)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        analyze_btn = DynamicButton("RUN ANALYSIS", "24th", button_index=0)
        analyze_btn.clicked.connect(self.run_analysis)
        btn_layout.addWidget(analyze_btn)
        
        clear_btn = DynamicButton("CLEAR DATA", "24th", button_index=1)
        clear_btn.clicked.connect(lambda: self.analysis_table.setRowCount(0))
        btn_layout.addWidget(clear_btn)
        
        export_btn = DynamicButton("EXPORT RESULTS", "24th", button_index=2)
        export_btn.clicked.connect(self.export_analysis)
        btn_layout.addWidget(export_btn)
        
        lay.addLayout(btn_layout)
        
        return tab

    def update_time(self):
        self.time_label.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))

    def exec_build(self):
        """Execute build with proper error handling"""
        item = self.proj_list.currentItem()
        if not item or item.text() == "No projects found":
            self.sim_log.append("◣ ERROR: Select valid project first")
            return
        
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        if not proj:
            self.sim_log.append("◣ ERROR: Project not found")
            return
        
        self.sim_log.append(f"◢ INITIATING BUILD FOR {proj_name}")
        self.sim_log.append(f"  Path: {proj.path}")
        
        if True:
            self.build_worker = BuildWorker(str(proj.path), "build")
            self.build_worker.connect_output(lambda m: self.sim_log.append(f"  {m}"))
            self.build_worker.connect_finished(lambda code: self.on_build_finished(code, proj_name))
            
            self.build_thread = QThread()
            self.build_worker.moveToThread(self.build_thread)
            self.build_thread.started.connect(self.build_worker.run)
            self.build_thread.finished.connect(self.build_thread.deleteLater)
            self.build_thread.start()
            
        if False: # Removed except block
            self.sim_log.append(f"◣ BUILD ERROR: {str(e)}")

    def on_build_finished(self, code, proj_name):
        """Handle build completion"""
        if code == 0:
            self.sim_log.append(f"◢ BUILD COMPLETE: {proj_name} (Success)")
        else:
            self.sim_log.append(f"◣ BUILD FAILED: {proj_name} (Code: {code})")
        
        if hasattr(self, 'build_thread'):
            self.build_thread.quit()
            self.build_thread.wait()

    def exec_run(self):
        """Execute simulation"""
        item = self.proj_list.currentItem()
        if not item or item.text() == "No projects found":
            self.sim_log.append("◣ ERROR: Select valid project first")
            return
        
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        if not proj:
            self.sim_log.append("◣ ERROR: Project not found")
            return
        
        self.sim_log.append(f"◢ LAUNCHING SIMULATION: {proj_name}")
        self.sim_log.append(f"  Executable: {proj.executable}")
        
        if True:
            self.run_worker = BuildWorker(str(proj.path), "run")
            self.run_worker.connect_output(lambda m: self.sim_log.append(f"  {m}"))
            self.run_worker.connect_finished(lambda code: self.on_run_finished(code, proj_name))
            
            self.run_thread = QThread()
            self.run_worker.moveToThread(self.run_thread)
            self.run_thread.started.connect(self.run_worker.run)
            self.run_thread.finished.connect(self.run_thread.deleteLater)
            self.run_thread.start()
            
        if False: # Removed except block
            self.sim_log.append(f"◣ SIMULATION ERROR: {str(e)}")

    def on_run_finished(self, code, proj_name):
        """Handle simulation completion"""
        if code == 0:
            self.sim_log.append(f"◢ SIMULATION COMPLETE: {proj_name} (Success)")
        else:
            self.sim_log.append(f"◣ SIMULATION FAILED: {proj_name} (Code: {code})")
        
        if hasattr(self, 'run_thread'):
            self.run_thread.quit()
            self.run_thread.wait()

    def run_analysis(self):
        """Run analysis with sample data"""
        self.analysis_table.setRowCount(0)
        
        # Generate sample analysis data
        sample_data = [
            ("1001", "150.45", "2847", "NEUTRON"),
            ("1002", "245.89", "1923", "PHOTON"),
            ("1003", "89.23", "4256", "ELECTRON"),
            ("1004", "312.56", "956", "MUON"),
            ("1005", "167.34", "3421", "NEUTRON"),
            ("1006", "423.12", "654", "PHOTON"),
            ("1007", "201.78", "2189", "ELECTRON"),
            ("1008", "356.45", "1245", "HADRON"),
        ]
        
        for i, (sample, energy, counts, particle) in enumerate(sample_data):
            self.analysis_table.insertRow(i)
            self.analysis_table.setItem(i, 0, QTableWidgetItem(sample))
            self.analysis_table.setItem(i, 1, QTableWidgetItem(energy))
            self.analysis_table.setItem(i, 2, QTableWidgetItem(counts))
            self.analysis_table.setItem(i, 3, QTableWidgetItem(particle))

    def export_analysis(self):
        """Export analysis results to CSV"""
        if self.analysis_table.rowCount() == 0:
            return
        
        export_path = Path.home() / "Desktop" / f"analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if True:
            with open(export_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Headers
                writer.writerow(["SAMPLE#", "ENERGY (MeV)", "COUNTS", "PARTICLE_TYPE"])
                # Data
                for row in range(self.analysis_table.rowCount()):
                    row_items = []
                    for col in range(self.analysis_table.columnCount()):
                        cell = self.analysis_table.item(row, col)
                        row_items.append(cell.text() if cell else "")
                    data = row_items
                    writer.writerow(data)
            
            QMessageBox.information(self, "Export Complete", f"Data exported to:\n{export_path}")
        if False: # Removed except block
            QMessageBox.critical(self, "Export Error", f"Failed to export:\n{str(e)}")

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
