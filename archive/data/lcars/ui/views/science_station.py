"""
Science Station - Simulation Analysis & Spectrometry View
Interfaces with Geant4 Enterprise results (CSV/Data).
"""
import pandas as pd
import numpy as np
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QListWidget, QSplitter
)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style

class ScienceStationView(QWidget):
    def __init__(self, system, era="24th", faction="federation", parent=None):
        super().__init__(parent)
        self.system = system
        self.era = str(era)
        self.faction = str(faction)
        self.data_root = Path(r"C:\Users\Forge\MyProject\Geant4\Enterprise")
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Header
        header = QHBoxLayout()
        self.elbow = LCARSElbow("top-left")
        self.elbow.setFixedSize(80, 50)
        header.addWidget(self.elbow)
        
        title = QLabel("◤ SCIENCE STATION :: SPECTRAL ANALYSIS")
        title.setStyleSheet(f"color: #99CCFF; {get_lcars_font_style(24, 'normal')}")
        header.addWidget(title)
        header.addStretch()
        
        self.btn_refresh = LCARSButton("RESCAN SENSORS", "#FF9900")
        self.btn_refresh.setFixedSize(180, 35)
        self.btn_refresh.clicked.connect(self.scan_projects)
        header.addWidget(self.btn_refresh)

        self.btn_majel = LCARSButton("ASK COMPUTER", "#CC66FF")
        self.btn_majel.setFixedSize(180, 35)
        self.btn_majel.clicked.connect(self.ask_majel)
        header.addWidget(self.btn_majel)
        
        self.main_layout.addLayout(header)

        # Main Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Project/File List
        left_panel = QFrame()
        left_panel.setFixedWidth(300)
        lp_layout = QVBoxLayout(left_panel)
        
        lp_layout.addWidget(QLabel("◤ DETECTED PROJECTS"))
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("background: #050505; color: #99CCFF; border: 1px solid #333;")
        self.project_list.itemClicked.connect(self.on_project_selected)
        lp_layout.addWidget(self.project_list)
        
        lp_layout.addWidget(QLabel("◤ AVAILABLE DATASETS"))
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("background: #050505; color: #FF9900; border: 1px solid #333;")
        self.file_list.itemClicked.connect(self.load_data)
        lp_layout.addWidget(self.file_list)
        
        self.splitter.addWidget(left_panel)
        
        # Right Panel: Visualization area
        self.viz_container = QFrame()
        self.viz_container.setStyleSheet("background: #000; border: 2px solid #222;")
        self.viz_layout = QVBoxLayout(self.viz_container)
        
        # Matplotlib Figure
        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('black')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('#444')
            
        self.viz_layout.addWidget(self.canvas)
        
        self.info_lbl = QLabel("READY FOR SENSOR INPUT...")
        self.info_lbl.setStyleSheet(f"color: #66CCFF; {get_lcars_font_style(14, 'normal')}")
        self.viz_layout.addWidget(self.info_lbl)
        
        self.splitter.addWidget(self.viz_container)
        self.main_layout.addWidget(self.splitter)

        self.scan_projects()

    def scan_projects(self):
        """Find ENX* folders in the Enterprise workspace."""
        self.project_list.clear()
        if not self.data_root.exists():
            self.info_lbl.setText("◤ ERROR: SCIENCE DATA SUBSTRATE NOT FOUND")
            return
            
        for d in self.data_root.glob("ENX*"):
            if d.is_dir():
                self.project_list.addItem(d.name)

    def on_project_selected(self, item):
        """Scan selected project for CSV data."""
        self.file_list.clear()
        p_name = item.text()
        p_path = self.data_root / p_name
        
        # Look for CSVs in root or data/ or archive/
        search_paths = [p_path, p_path / "data", p_path.parent / "archive"]
        
        for path in search_paths:
            if path.exists():
                for f in path.glob("*.csv"):
                    self.file_list.addItem(f"{p_name}/{f.name}")

    def load_data(self, item):
        """Parse CSV and plot."""
        parts = item.text().split('/')
        p_name = parts[0]
        f_name = parts[1]
        
        # Resolve path
        f_path = self.data_root / p_name / f_name
        if not f_path.exists(): # Check archive
             f_path = self.data_root / "archive" / f_name
        df = pd.read_csv(f_path)
        self.plot_spectrum(df, f_name)
        self.info_lbl.setText(f"◤ ANALYSIS COMPLETE: {f_name} :: ENTRIES: {len(df)}")

    def ask_majel(self):
        """Invoke Majel AI for data interpretation."""
        from lcars.ui.onboard import OnboardComputerView
        self.majel = OnboardComputerView(era=self.era, faction=self.faction)
        self.majel.show()
        self.info_lbl.setText(f"◤ COMPUTER LINK ERROR: {e}")

    def plot_spectrum(self, df, title):
        self.ax.clear()
        
        # Dynamic LCARS Styling
        color = "#FF9900"
        
        if len(df.columns) >= 2:
            x_col = df.columns[0]
            y_col = df.columns[1]
            self.ax.plot(df[x_col], df[y_col], color=color, linewidth=2)
            self.ax.fill_between(df[x_col], df[y_col], color=color, alpha=0.2)
            self.ax.set_xlabel(x_col.upper(), color='#99CCFF')
            self.ax.set_ylabel(y_col.upper(), color='#99CCFF')
        else:
            # Single column histogram
            self.ax.hist(df.iloc[:,0], bins=50, color=color, alpha=0.7)
            self.ax.set_xlabel(df.columns[0].upper(), color='#99CCFF')

        self.ax.set_title(f"SPEC-DATA: {title.upper()}", color='white', pad=20)
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#333')
        self.canvas.draw()
