"""
LCARS 25th Century Geant4 Science Workstation 🔬
Advanced Research Terminal for nuclear physics simulations.
"""
import sys
import os
import random
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QTextEdit, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPoint, QRect, QSize
from PyQt6.QtGui import QPainter, QColor, QTransform, QFont, QPainterPath
from PyQt6.QtCharts import QChart, QChartView, QLineSeries

# --- 1. SYSTEM INTEGRATION ---
project_root = Path(__file__).parent.parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.lcars_palette import get_palette_by_name
from lcars.core.project_manager import ProjectManager
from lcars.core.geant4_build import BuildWorker

# --- 2. AUTHENTIC UI PRIMITIVES ---

class LcarsElbow(QWidget):
    """Iconic LCARS L-bend (Elbow) connector"""
    def __init__(self, parent=None, color="#37A6D1", direction="top-left", size=(120, 40)):
        super().__init__(parent)
        self.color = color
        self.direction = direction
        self.setFixedSize(QSize(*size))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self.color))
        p.setPen(Qt.PenStyle.NoPen)
        
        w, h = self.width(), self.height()
        thickness = h // 2
        path = QPainterPath()
        
        if self.direction == "top-left":
            path.moveTo(w, 0)
            path.lineTo(thickness, 0)
            path.arcTo(0, 0, thickness*2, thickness*2, 90, 90)
            path.lineTo(0, h)
            path.lineTo(thickness, h)
            path.lineTo(thickness, thickness)
            path.arcTo(thickness, thickness, 2, 2, 180, -90)
            path.lineTo(w, thickness)
        elif self.direction == "top-right":
            path.moveTo(0, 0)
            path.lineTo(w - thickness, 0)
            path.arcTo(w - thickness*2, 0, thickness*2, thickness*2, 90, -90)
            path.lineTo(w, h)
            path.lineTo(w - thickness, h)
            path.lineTo(w - thickness, thickness)
            path.lineTo(0, thickness)
            
        p.drawPath(path)

# --- 3. MAIN WORKSTATION ---

class Geant4Workstation(QMainWindow):
    def __init__(self):
        super().__init__()
        self.palette = get_palette_by_name("25th")
        self.project_manager = ProjectManager(project_root)
        self.build_thread = None
        
        self.setWindowTitle("LCARS GEANT4 SCIENCE STATION")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet(f"background: #000000; color: #9EA5BA; font-family: 'Swis721 BT';")

        self.root = QWidget()
        self.setCentralWidget(self.root)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self.root)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # ◥ TOP BAR (Header)
        self.top = QFrame()
        self.top.setFixedHeight(80)
        tl = QHBoxLayout(self.top)
        
        elbow = LcarsElbow(self.top, self.palette['button_colors'][0], "top-left", (150, 40))
        tl.addWidget(elbow)
        
        self.title_lbl = QLabel("◢ SCIENCE INTERFACE // GEANT4_ANALYSIS_NODE_02")
        self.title_lbl.setStyleSheet(f"color: {self.palette['button_colors'][0]}; font-weight: bold; font-size: 22px; padding-left: 15px;")
        tl.addWidget(self.title_lbl)
        tl.addStretch()
        
        # System buttons
        for n, c, clr in [("BUILD", self.exec_build, self.palette['button_colors'][2]),
                          ("RUN", self.exec_run, self.palette['button_colors'][1]),
                          ("✕", self.close, self.palette['button_colors'][3])]:
            btn = self.make_pill(n, c, clr)
            tl.addWidget(btn)
            
        layout.addWidget(self.top)

        # ◥ MAIN RESEARCH AREA
        main_area = QHBoxLayout()
        
        # Left Panel: Project & Params
        left_p = QFrame()
        left_p.setFixedWidth(350)
        left_p.setStyleSheet("background: rgba(15, 22, 32, 0.95); border-radius: 20px; padding: 10px;")
        lv = QVBoxLayout(left_p)
        
        lv.addWidget(QLabel("◤ PROJECT DISCOVERY"))
        self.proj_selector = QComboBox()
        self.proj_selector.setStyleSheet("background: #0A0E1A; color: #37A6D1; border-radius: 12px; padding: 8px;")
        self.proj_selector.addItems(self.project_manager.get_project_names())
        lv.addWidget(self.proj_selector)
        
        lv.addSpacing(20)
        lv.addWidget(QLabel("◤ SIM_PARAMETERS"))
        self.params_grid = QGridLayout()
        self.params = {}
        for i, p in enumerate(["ENERGY (MeV)", "EVENTS", "THETA", "PHI"]):
            lv.addWidget(QLabel(p))
            inp = QLineEdit("0.0")
            inp.setStyleSheet("background: #050505; color: #FFFFFF; border-radius: 8px; border: 1px solid #2F3749; padding: 5px;")
            lv.addWidget(inp)
            self.params[p] = inp
            
        lv.addStretch()
        lv.addWidget(self.make_pill("INJECT MACRO", self.inject_macro, self.palette['button_colors'][0]))
        main_area.addWidget(left_p)

        # Center: Telemetry & Log
        center_v = QVBoxLayout()
        
        self.telemetry_p = QFrame()
        self.telemetry_p.setFixedHeight(250)
        self.telemetry_p.setStyleSheet("background: #050505; border-radius: 20px; border: 1px solid #1A2332;")
        tv = QVBoxLayout(self.telemetry_p)
        tv.addWidget(QLabel("◢ SYSTEM_TELEMETRY"))
        self.log_out = QTextEdit()
        self.log_out.setReadOnly(True)
        self.log_out.setStyleSheet("background: transparent; color: #9EA5BA; border: none; font-family: 'Courier New'; font-size: 11px;")
        tv.addWidget(self.log_out)
        center_v.addWidget(self.telemetry_p)
        
        # Bottom Center: Results Grid
        self.results_table = QTableWidget(0, 3)
        self.results_table.setHorizontalHeaderLabels(["ENERGY", "INTENSITY", "PARTICLE"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setStyleSheet(f"""
            QTableWidget {{ background: #0A0E1A; border-radius: 15px; gridline-color: #2F3749; color: white; }}
            QHeaderView::section {{ background: {self.palette['button_colors'][2]}; color: black; font-weight: bold; border: none; }}
        """)
        center_v.addWidget(self.results_table)
        
        main_area.addLayout(center_v, 2)

        # Right Panel: Analysis Chart
        self.chart = QChart()
        self.chart.setBackgroundBrush(QColor(0, 0, 0, 0))
        self.chart.setTitleBrush(QColor("#9EA5BA"))
        self.chart.setTitle("ENERGY_SPECTRUM_ANALYSIS")
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setStyleSheet("background: #000000; border-radius: 20px; border: 1px solid #1A2332;")
        main_area.addWidget(self.chart_view, 2)

        layout.addLayout(main_area)

        # ◥ FOOTER
        self.footer = QFrame()
        self.footer.setFixedHeight(40)
        fl = QHBoxLayout(self.footer)
        self.status_lbl = QLabel("◢ SCIENCE_CORE: STANDBY // NO_ACTIVE_SIMULATION")
        self.status_lbl.setStyleSheet(f"color: {self.palette['button_colors'][1]}; font-size: 12px;")
        fl.addWidget(self.status_lbl)
        fl.addStretch()
        elbow_f = LcarsElbow(self.footer, self.palette['button_colors'][1], "top-right", (100, 20))
        fl.addWidget(elbow_f)
        layout.addWidget(self.footer)

    def make_pill(self, text, cb, clr):
        b = QPushButton(text)
        b.setFixedHeight(35)
        b.setMinimumWidth(100)
        b.setStyleSheet(f"background: {clr}; color: black; font-weight: bold; border-radius: 17px; border: none; font-size: 11px;")
        b.clicked.connect(cb)
        return b

    def log(self, msg):
        self.log_out.append(f"> {msg}")
        self.status_lbl.setText(f"◢ SCIENCE_CORE: {msg[:50].upper()}")

    def exec_build(self):
        proj_name = self.proj_selector.currentText()
        proj = self.project_manager.get_project(proj_name)
        if not proj: return
        
        self.log(f"INITIALIZING BUILD FOR {proj_name}...")
        self.worker = BuildWorker(proj.path, "build")
        self.worker.output_signal.connect(self.log)
        self.worker.finished_signal.connect(lambda x: self.log("BUILD_COMPLETE") if x==0 else self.log("BUILD_FAILED"))
        
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def exec_run(self):
        proj_name = self.proj_selector.currentText()
        proj = self.project_manager.get_project(proj_name)
        if not proj: return
        
        self.log(f"STARTING SIMULATION: {proj_name}")
        self.worker = BuildWorker(proj.path, "run")
        self.worker.output_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_sim_complete)
        
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_sim_complete(self, code):
        if code == 0:
            self.log("SIMULATION_SUCCESS")
            self.generate_dummy_results()
        else:
            self.log("SIMULATION_TERMINATED_UNEXPECTEDLY")

    def generate_dummy_results(self):
        self.results_table.setRowCount(0)
        series = QLineSeries()
        series.setPen(QColor(self.palette['button_colors'][0]))
        
        energy_base = float(self.params["ENERGY (MeV)"].text())
        for i in range(20):
            e = energy_base + i * 0.5
            counts = random.randint(10, 100) * (20-i) / 20
            self.results_table.insertRow(i)
            self.results_table.setItem(i, 0, QTableWidgetItem(f"{e:.2f}"))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{counts:.0f}"))
            self.results_table.setItem(i, 2, QTableWidgetItem("GAMMA"))
            series.append(e, counts)
            
        self.chart.removeAllSeries()
        self.chart.addSeries(series)
        self.chart.createDefaultAxes()

    def inject_macro(self):
        self.log("INJECTING MACRO PARAMETERS...")
        # Verification of parameters logic here

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Geant4Workstation()
    sys.exit(app.exec())
