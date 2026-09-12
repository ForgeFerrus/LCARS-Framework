"""
PCARS 23st (Movie-era) archive UI — uses real project palettes when available.

This file was restored and updated in-place (no deletions).
"""

import sys
from pathlib import Path
from datetime import datetime

import psutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QListWidget, QMessageBox, QProgressBar, QGroupBox,
    QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, QTimer

# allow importing lcars.* from repo root
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# try to use the project's theme API
get_palette_by_name = None
LCARSEra = None

from lcars.theme.palette import LCARSEra

import logging

get_palette_by_name = None
LCARSEra = None

# local fallback MOVIE palette (keeps old prototype colors)
MOVIE_COLORS = {
    "bg": "#000000",
    "frame": "#00BFFF",
    "frame_dim": "#001218",
    "text_cyan": "#00E5FF",
    "text_green": "#00FF66",
    "accent_blue": "#00A0FF",
    "button_cyan": "#00C8FF",
    "button_green": "#00CC66",
    "alert": "#FF3333",
    "grid": "#114466",
}

def fetch_palette(name: str) -> dict:
    """Return a palette dict: prefer project's `get_palette_by_name`, else fallback."""
    if get_palette_by_name:
            p = get_palette_by_name(name)
            if isinstance(p, dict) and p:
                return p.copy()
            pass
    return MOVIE_COLORS.copy()


class PCARS23Century(QMainWindow):
    def __init__(self):
        super().__init__()
        # default to movie-era palette key used historically
        default_era = '23st' if get_palette_by_name else 'movie'
        self.colors = fetch_palette(default_era)

        self.setup_window()
        self.setup_ui()
        self.apply_lcars_style()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_loop)
        self.timer.start(1000)

    def setup_window(self):
        self.setWindowTitle("PCARS Framework 23st - Movie Era")
        self.setGeometry(100, 100, 1200, 800)
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout(central)

    def setup_ui(self):
        self.create_left_panel()
        self.create_main_content()

    def create_left_panel(self):
        left = QWidget()
        left.setFixedWidth(220)
        layout = QVBoxLayout(left)

        title = QLabel("LCARS")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel("SYSTEM\nONLINE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)

        # populate era selector from project enums when available
        layout.addWidget(QLabel("Era"))
        self.era_selector = QComboBox()
        if LCARSEra is not None:
            era_items = [e.value for e in LCARSEra]
        else:
            era_items = ['movie', '23rd', '23st', '22nd', '24th', '24st', '25th', '29th']
        self.era_selector.addItems(era_items)
        # prefer movie/23st default
        default_item = '23st' if '23st' in era_items else era_items[0]
        self.era_selector.setCurrentText(default_item)
        self.era_selector.currentTextChanged.connect(self.on_era_changed)
        layout.addWidget(self.era_selector)

        for text, func in ("PROJECTS", self.show_projects), ("ANALYSIS", self.show_analysis), ("MONITOR", self.show_monitor), ("CONFIG", self.show_config):
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        layout.addStretch()
        self.main_layout.addWidget(left)

    def create_main_content(self):
        self.tabs = QTabWidget()
        projects = QWidget()
        p_layout = QVBoxLayout(projects)
        p_layout.addWidget(QLabel("ENTERPRISE PROJECTS"))
        self.projects_list = QListWidget()
        for p in ("ENX-01 Detector System", "ENX-02 Particle Simulation", "NCC-1701 Enterprise"):
            self.projects_list.addItem(p)
        p_layout.addWidget(self.projects_list)
        self.tabs.addTab(projects, "PROJECTS")

        analysis = QWidget()
        a_layout = QVBoxLayout(analysis)
        a_layout.addWidget(QLabel("DATA ANALYSIS"))
        self.analysis_output = QTextEdit()
        self.analysis_output.setPlainText("Analysis module ready...\nAwaiting data input...")
        a_layout.addWidget(self.analysis_output)
        self.tabs.addTab(analysis, "ANALYSIS")

        monitor = QWidget()
        m_layout = QVBoxLayout(monitor)
        m_layout.addWidget(QLabel("SYSTEM MONITOR"))
        cpu_group = QGroupBox("CPU STATUS")
        cg = QVBoxLayout(cpu_group)
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        cg.addWidget(self.cpu_label)
        cg.addWidget(self.cpu_bar)
        m_layout.addWidget(cpu_group)

        ram_group = QGroupBox("MEMORY STATUS")
        rg = QVBoxLayout(ram_group)
        self.ram_label = QLabel("RAM: 0%")
        self.ram_bar = QProgressBar()
        rg.addWidget(self.ram_label)
        rg.addWidget(self.ram_bar)
        m_layout.addWidget(ram_group)

        disk_group = QGroupBox("DISK STATUS")
        dg = QVBoxLayout(disk_group)
        self.disk_label = QLabel("Disk: 0%")
        self.disk_bar = QProgressBar()
        dg.addWidget(self.disk_label)
        dg.addWidget(self.disk_bar)
        m_layout.addWidget(disk_group)

        self.tabs.addTab(monitor, "MONITOR")
        self.main_layout.addWidget(self.tabs)

    def update_system_loop(self):
        self.time_label.setText(datetime.now().strftime("%H:%M:%S\n%Y-%m-%d"))
        cpu = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.cpu_bar.setValue(int(cpu))
        mem = psutil.virtual_memory()
        self.ram_label.setText(f"RAM: {mem.percent:.1f}%")
        self.ram_bar.setValue(int(mem.percent))
        d = psutil.disk_usage('/')
        self.disk_label.setText(f"DISK: {d.percent:.1f}%")
        self.disk_bar.setValue(int(d.percent))

    def show_projects(self): self.tabs.setCurrentIndex(0)
    def show_analysis(self): self.tabs.setCurrentIndex(1)
    def show_monitor(self): self.tabs.setCurrentIndex(2)
    def show_config(self): QMessageBox.information(self, "LCARS", "Access Denied: Level 4 Security Required")

    def apply_lcars_style(self):
        # map palette keys to used names
        bg = self.colors.get('bg') or self.colors.get('background') or '#000000'
        primary = self.colors.get('frame') or self.colors.get('primary') or '#00BFFF'
        secondary = self.colors.get('accent_blue') or self.colors.get('secondary') or '#00A0FF'
        text = self.colors.get('text_cyan') or self.colors.get('text') or '#00E5FF'
        success = self.colors.get('text_green') or self.colors.get('success') or '#00FF66'
        warn = self.colors.get('alert') or self.colors.get('warning') or '#FFAA00'

        style = f"""
        QMainWindow {{ background-color: {bg}; }}
        QLabel {{ color: {text}; }}
        QPushButton {{ background-color: {secondary}; color: {bg}; padding: 8px; border-radius: 8px; }}
        QProgressBar {{ background-color: {bg}; color: {text}; border: 1px solid {primary}; height: 16px; }}
        QGroupBox {{ border: 1px solid {primary}; color: {text}; margin-top: 6px; }}
        QTextEdit {{ background-color: {bg}; color: {text}; border: 1px solid {primary}; }}
        """
        self.setStyleSheet(style)

    def on_era_changed(self, era_name: str):
        self.colors = fetch_palette(era_name)
        self.apply_lcars_style()


def main():
    app = QApplication(sys.argv)
    w = PCARS23Century()
    w.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
    
