
"""
LCARS Interface - 25th Century "Boarding Computer" OS
The primary functional hub for Geant4 simulations and ship systems.
"""

# Titanium Bridge Migration: import sys
import random
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QGridLayout, QGroupBox, 
                            QTextEdit, QProgressBar, QTabWidget, QListWidget,
                            QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                            QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, QProcess, pyqtSlot, QDateTime, QSize, QThread
from PyQt6.QtGui import QFont, QColor

# Add project root to path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color
from lcars.widgets.dashboard_widgets import SystemMonitorWidget, ConsoleWidget, AIAgentWidget
from lcars.widgets.widgets import LcarsElbow
from lcars.core.project_manager import ProjectManager
from lcars.core.geant4_build import BuildWorker


class DynamicButton(QPushButton):
    """Button with dynamic color cycling from palette"""
    def __init__(self, text, era, width=None, height=None, button_index=0):
        super().__init__(text)
        self.era = era
        self.button_index = button_index
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        # Асинхронна змінювання кольорів
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer.setInterval(2500)
        
        self.update_style()
    
    def cycle_color(self):
        """Get random color from palette"""
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
                border: 2px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {self.darken(color)};
            }}
        """)
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()
    
    @staticmethod
    def darken(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, min(255, s+40), max(0, v-50), a)
        return c.name()


class LCARS25thCentury(QMainWindow):
    """
    Advanced 25th Century OS Interface.
    Integrates Dashboard, Geant4 Workstation, and Analysis into one unified shell.
    """
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        self.root_path = root_path or Path(project_root)
        self.selector = selector
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        self.project_manager = ProjectManager(self.root_path)
        self.running_processes = {}
        
        self.setup_window()
        self.setup_ui()
        
        # System Update Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_system_time)
        self.timer.start(1000)

    def setup_window(self):
        self.setWindowTitle("LCARS OS - 25TH CENTURY NODE")
        self.showFullScreen()
        self.setStyleSheet(f"background-color: {self.colors['background']}; font-family: 'Swis721 BT', 'Arial';")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # 1. HEADER AREA
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        # Left Elbow Curve
        elbow_color = self.colors['button_colors'][0]
        self.header_elbow = LcarsElbow(color=elbow_color, direction="top-left", size=(200, 60))
        header_layout.addWidget(self.header_elbow)
        
        # Title Plate
        self.title_plate = QLabel("◢ ENTERPRISE SYSTEMS // QUANTUM CORE v5.2")
        self.title_plate.setStyleSheet(f"""
            background-color: {elbow_color};
            color: black;
            font-size: 24px;
            font-weight: bold;
            padding: 0 30px;
            margin-left: -1px;
            border-bottom-right-radius: 20px;
        """)
        self.title_plate.setFixedHeight(60)
        header_layout.addWidget(self.title_plate)
        
        header_layout.addStretch()
        
        # Stardate/Time display
        self.time_display = QLabel()
        self.time_display.setStyleSheet(f"color: {self.colors['text']}; font-size: 20px; font-weight: bold; padding-right: 20px;")
        header_layout.addWidget(self.time_display)
        
        self.main_layout.addLayout(header_layout)

        # 2. MIDDLE CONTENT (Sidebar + Main View + Widgets)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # --- SIDEBAR (Navigation & Controls) ---
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(200)
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(8)
        
        nav_buttons = [
            ("DASHBOARD", 0),
            ("SCIENCE", 1),
            ("ANALYSIS", 2),
            ("SYSTEMS", 3)
        ]
        
        for idx, (name, page_idx) in enumerate(nav_buttons):
            btn = DynamicButton(name, LCARSEra.LCARS_25TH, height=50, button_index=idx)
            btn.clicked.connect(lambda checked, i=page_idx: self.display_stack.setCurrentIndex(i))
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addStretch()
        
        # Authorization Disconnect
        exit_btn = DynamicButton("DISCONNECT", LCARSEra.LCARS_25TH, height=50, button_index=4)
        exit_btn.clicked.connect(self.return_to_main)
        sidebar_layout.addWidget(exit_btn)
        
        content_layout.addWidget(sidebar_frame)
        
        # --- CENTRAL DISPLAY STACK ---
        self.display_stack = QTabWidget()
        if True:
                tab_bar = self.display_stack.tabBar()
                if tab_bar:
                    tab_bar.hide()
        if False: # Removed except block
                pass
        self.display_stack.setStyleSheet(f"""
            QTabWidget::pane {{ 
                border: 2px solid {self.colors['panel_border']}; 
                border-radius: 25px; 
                background: rgba(0,0,0,0.4); 
            }}
        """)
        
        self.display_stack.addTab(self.create_dashboard_tab(), "DASHBOARD")
        self.display_stack.addTab(self.create_science_tab(), "SCIENCE")
        self.display_stack.addTab(self.create_analysis_tab(), "ANALYSIS")
        self.display_stack.addTab(self.create_systems_tab(), "SYSTEMS")
        
        content_layout.addWidget(self.display_stack, 5)
        
        # --- RIGHT PANEL (Telemetry & Logs) ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        self.sys_monitor = SystemMonitorWidget()
        self.ai_agent = AIAgentWidget()
        self.console = ConsoleWidget()
        
        right_panel.addWidget(self.sys_monitor)
        right_panel.addWidget(self.ai_agent)
        right_panel.addWidget(self.console, 1)
        
        content_layout.addLayout(right_panel, 2)
        
        self.main_layout.addLayout(content_layout, 1)

    # --- TAB CREATION METHODS ---

    def create_dashboard_tab(self):
        """OS Desktop view with Application Grid"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("◢ OPERATING SYSTEM CORE // ACTIVE NODE"))
        
        # Application Grid
        app_grid_box = QGroupBox("PRIMARY APPLICATIONS")
        app_grid_box.setStyleSheet(f"color: {self.colors['text']}; font-weight: bold; border: 1px solid {self.colors['panel_border']};")
        grid_layout = QGridLayout(app_grid_box)
        
        apps = [
            ("CONSTRUCTOR", "Interface Designer"),
            ("GEANT4 STATION", "Simulation Core"),
            ("SPECTRA VIEW", "Data Analysis"),
            ("HEALTH CHECK", "System Diagnostics"),
            ("CMD SHELL", "Terminal Access"),
            ("DB MANAGER", "Project Storage")
        ]
        
        for i, (name, desc) in enumerate(apps):
            btn_frame = QFrame()
            btn_lay = QVBoxLayout(btn_frame)
            btn = DynamicButton(name, LCARSEra.LCARS_25TH, height=40, button_index=i)
            btn.clicked.connect(lambda checked, n=name: self.log_to_console(f"Requesting Launch: {n}"))
            
            btn_lay.addWidget(btn)
            btn_lay.addWidget(QLabel(desc))
            grid_layout.addWidget(btn_frame, i // 3, i % 3)
            
        layout.addWidget(app_grid_box)
        
        # System Info Pane
        info_pane = QFrame()
        info_pane.setStyleSheet(f"background: rgba(255,255,255,0.05); border-radius: 15px; border: 1px solid {self.colors['panel_border']};")
        info_lay = QVBoxLayout(info_pane)
        info_lay.addWidget(QLabel("◢ KERNEL STATUS: NOMINAL"))
        info_lay.addWidget(QLabel("◢ ENCRYPTION: LEVEL 9 ACTIVE"))
        info_lay.addWidget(QLabel("◢ SUBSYSTEMS: ONLINE"))
        layout.addWidget(info_pane)
        
        return widget

    def create_science_tab(self):
        """Integrated Geant4 Workstation"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Project Selector
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("◤ PROJECT DISCOVERY:"))
        self.proj_selector = QListWidget()
        self.proj_selector.setFixedHeight(100)
        self.proj_selector.setStyleSheet(f"background: #050505; color: {self.colors['text']}; border: 1px solid {self.colors['panel_border']};")
        
        # Populate projects
        projects = self.project_manager.get_project_names()
        self.proj_selector.addItems(projects)
        top_bar.addWidget(self.proj_selector)
        layout.addLayout(top_bar)
        
        # Build/Run Controls
        ctrl_bar = QHBoxLayout()
        controls = [("BUILD", self.exec_build), 
                    ("RUN", self.exec_run),
                    ("STOP", self.stop_process)]
        for idx, (name, cmd) in enumerate(controls):
            btn = DynamicButton(name, LCARSEra.LCARS_25TH, height=40, button_index=idx)
            btn.clicked.connect(cmd)
            ctrl_bar.addWidget(btn)
        layout.addLayout(ctrl_bar)
        
        # Simulation Log (Active)
        layout.addWidget(QLabel("◢ GEANT4 OUTPUT LOG:"))
        self.science_log = QTextEdit()
        self.science_log.setReadOnly(True)
        self.science_log.setStyleSheet("background: #000; color: #0F0; font-family: 'Consolas'; font-size: 10px; border: 1px solid #333;")
        layout.addWidget(self.science_log)
        
        return widget

    def create_analysis_tab(self):
        """Integrated Spectra Analysis"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("◢ SPECTROMETRY ANALYSIS ENGINE"))
        
        self.analysis_table = QTableWidget(0, 3)
        self.analysis_table.setHorizontalHeaderLabels(["ENERGY (keV)", "INTENSITY", "PROBABILITY"])
        if True:
            header = self.analysis_table.horizontalHeader()
            if header:
                header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if False: # Removed except block
            pass
        self.analysis_table.setStyleSheet(f"""
            QTableWidget {{ background: transparent; color: white; border: 1px solid {self.colors['panel_border']}; }}
            QHeaderView::section {{ background: {self.colors['button_colors'][0]}; color: black; font-weight: bold; }}
        """)
        layout.addWidget(self.analysis_table)
        layout.addWidget(self.analysis_table)
        
        # Action Buttons
        btn_lay = QHBoxLayout()
        scan_btn = DynamicButton("SCAN DATA", LCARSEra.LCARS_25TH, button_index=0)
        scan_btn.clicked.connect(self.simulate_analysis)
        btn_lay.addWidget(scan_btn)
        
        plot_btn = DynamicButton("GENERATE PLOT", LCARSEra.LCARS_25TH, button_index=1)
        btn_lay.addWidget(plot_btn)
        layout.addLayout(btn_lay)
        
        return widget

    def create_systems_tab(self):
        """Ship-wide Diagnostic & Settings"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("◢ SHIP-WIDE DIAGNOSTIC SYSTEMS"))
        
        # Dummy progress bars for diagnostics
        for sys_name in ["WARP CORE", "IMPULSE", "SHIELDS", "SENSORS"]:
            lay = QHBoxLayout()
            lay.addWidget(QLabel(f"{sys_name}:"))
            bar = QProgressBar()
            bar.setValue(random.randint(85, 100))
            bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {self.colors['button_colors'][1]}; }}")
            lay.addWidget(bar)
            layout.addLayout(lay)
            
        layout.addStretch()
        return widget

    # --- FUNCTIONAL LOGIC ---

    def update_system_time(self):
        self.time_display.setText(QDateTime.currentDateTime().toString("HH:mm:ss"))

    def log_to_console(self, msg):
        if hasattr(self, 'console'):
            self.console.output.append(f"> {msg}")

    def exec_build(self):
        item = self.proj_selector.currentItem()
        if not item:
            return

        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        if proj is None or not hasattr(proj, "path"):
            QMessageBox.warning(self, "SYSTEM", f"Project '{proj_name}' not found or invalid.")
            self.log_to_console(f"Error: Project '{proj_name}' not found or invalid.")
            return
        self.log_to_console(f"Starting Build: {proj_name}")

        self.worker = BuildWorker(proj.path, "build")
        self.worker.output_signal.connect(lambda m: self.science_log.append(m))
        self.worker.finished_signal.connect(lambda c: self.log_to_console(f"Build Finished: Code {c}"))

        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished_signal.connect(self.worker_thread.quit)
        self.worker_thread.start()

    def exec_run(self):
        item = self.proj_selector.currentItem()
        if not item: return
        
        proj_name = item.text()
        proj = self.project_manager.get_project(proj_name)
        if proj is None or not hasattr(proj, "path"):
            QMessageBox.warning(self, "SYSTEM", f"Project '{proj_name}' not found or invalid.")
            self.log_to_console(f"Error: Project '{proj_name}' not found or invalid.")
            return
        self.log_to_console(f"Running Simulation: {proj_name}")
        
        self.worker = BuildWorker(proj.path, "run")
        self.worker.output_signal.connect(lambda m: self.science_log.append(m))
        self.worker.finished_signal.connect(lambda c: self.log_to_console(f"Simulation Ended: Code {c}"))
        
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished_signal.connect(self.worker_thread.quit)
        self.worker_thread.start()

    def stop_process(self):
        if hasattr(self, 'worker'):
            self.worker.terminate()
            self.log_to_console("Process Interrupted.")

    def simulate_analysis(self):
        """Fills the analysis table with dummy data for verification"""
        self.analysis_table.setRowCount(0)
        for i in range(10):
            self.analysis_table.insertRow(i)
            self.analysis_table.setItem(i, 0, QTableWidgetItem(f"{random.uniform(10, 2000):.2f}"))
            self.analysis_table.setItem(i, 1, QTableWidgetItem(f"{random.randint(100, 5000)}"))
            self.analysis_table.setItem(i, 2, QTableWidgetItem(f"{random.uniform(0.1, 0.99):.4f}"))

    def return_to_main(self):
        if self.selector:
            self.selector.restore_selector()
        else:
            self.close()

def main():
    app = QApplication(sys.argv)
    window = LCARS25thCentury()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
