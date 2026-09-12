"""
PCARS 23 Century Interface (Merged Standard Edition)
Base: lcars_simple.py
Features: Real-time Monitor from lcars_monitor.py
"""

import sys
import psutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTabWidget, QTextEdit, QListWidget, 
    QMessageBox, QProgressBar, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class PCARS23Century(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # LCARS 23rd Century - Cold Blue Palette (From lcars_simple.py)
        self.colors = {
            'background': '#0A0A12',      # Deep Space Black
            'primary': '#00AAFF',         # Science Blue
            'secondary': '#4A9EFF',       # Function Blue  
            'accent1': '#0088CC',         # Command Dark Blue
            'accent2': '#66BBFF',         # Highlight
            'text': '#E0F0FF',            # Phosphor White
            'success': '#00FF88',         # Isolinear Green
            'warning': '#FFAA00',         # Alert Orange
            'danger': '#FF4444',          # Red Alert
            'info': '#88CCFF'             # Data Blue
        }
        
        self.setup_window()
        self.setup_ui()
        self.apply_lcars_style()
        
        # Timer for time and system stats
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_loop)
        self.timer.start(1000)
        
    def setup_window(self):
        self.setWindowTitle("PCARS Framework 23rd Century - Primary Interface")
        self.setGeometry(100, 100, 1200, 800)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QHBoxLayout(central_widget)
        
    def setup_ui(self):
        # 1. Left Panel (Standard LCARS)
        self.create_left_panel()
        
        # 2. Main Content (Tabs)
        self.create_main_content()
        
    def create_left_panel(self):
        left_panel = QWidget()
        left_panel.setFixedWidth(200)
        left_panel.setObjectName("lcars_left_panel")
        
        layout = QVBoxLayout(left_panel)
        
        # Title
        title = QLabel("LCARS")
        title.setObjectName("lcars_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("SYSTEM\nONLINE")
        self.status_label.setObjectName("lcars_status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Time
        self.time_label = QLabel()
        self.time_label.setObjectName("lcars_time")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # Quick Buttons
        quick_buttons = [
            ("PROJECTS", self.show_projects),
            ("ANALYSIS", self.show_analysis), 
            ("MONITOR", self.show_monitor),
            ("CONFIG", self.show_config)
        ]
        
        for text, func in quick_buttons:
            btn = QPushButton(text)
            btn.setObjectName("lcars_button")
            btn.clicked.connect(func)
            layout.addWidget(btn)
            
        layout.addStretch()
        self.main_layout.addWidget(left_panel)
        
    def create_main_content(self):
        self.tabs = QTabWidget()
        self.tabs.setObjectName("lcars_tabs")
        
        # TAB 1: PROJECTS (From Simple)
        projects_tab = QWidget()
        p_layout = QVBoxLayout(projects_tab)
        
        p_title = QLabel("ENTERPRISE PROJECTS")
        p_title.setObjectName("lcars_tab_title")
        p_layout.addWidget(p_title)
        
        self.projects_list = QListWidget()
        self.projects_list.setObjectName("lcars_list")
        sample_projects = ["ENX-01 Detector System", "ENX-02 Particle Simulation", 
                           "NCC-1701 Enterprise", "NCC-1764 Defiant"]
        for project in sample_projects:
            self.projects_list.addItem(project)
        p_layout.addWidget(self.projects_list)
        
        self.tabs.addTab(projects_tab, "PROJECTS")
        
        # TAB 2: ANALYSIS (From Simple)
        analysis_tab = QWidget()
        a_layout = QVBoxLayout(analysis_tab)
        
        a_title = QLabel("DATA ANALYSIS")
        a_title.setObjectName("lcars_tab_title")
        a_layout.addWidget(a_title)
        
        self.analysis_output = QTextEdit()
        self.analysis_output.setObjectName("lcars_output")
        self.analysis_output.setPlainText("Analysis module ready...\nAwaiting data input...")
        a_layout.addWidget(self.analysis_output)
        
        self.tabs.addTab(analysis_tab, "ANALYSIS")
        
        # TAB 3: MONITOR (Integrated from lcars_monitor.py)
        monitor_tab = QWidget()
        m_layout = QVBoxLayout(monitor_tab)
        
        m_title = QLabel("SYSTEM MONITOR")
        m_title.setObjectName("lcars_tab_title")
        m_layout.addWidget(m_title)
        
        # Monitor Content Grid
        content_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        
        # CPU Group
        cpu_group = QGroupBox("CPU STATUS")
        cpu_group.setObjectName("lcars_group")
        cg_layout = QVBoxLayout(cpu_group)
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setObjectName("lcars_stat_label")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setObjectName("lcars_progress_cpu")
        cg_layout.addWidget(self.cpu_label)
        cg_layout.addWidget(self.cpu_bar)
        left_col.addWidget(cpu_group)
        
        # Memory Group
        mem_group = QGroupBox("MEMORY STATUS")
        mem_group.setObjectName("lcars_group")
        mg_layout = QVBoxLayout(mem_group)
        self.ram_label = QLabel("RAM: 0%")
        self.ram_label.setObjectName("lcars_stat_label")
        self.ram_bar = QProgressBar()
        self.ram_bar.setObjectName("lcars_progress_ram")
        mg_layout.addWidget(self.ram_label)
        mg_layout.addWidget(self.ram_bar)
        left_col.addWidget(mem_group)
        
        # Disk Group
        disk_group = QGroupBox("DISK STATUS")
        disk_group.setObjectName("lcars_group")
        dg_layout = QVBoxLayout(disk_group)
        self.disk_label = QLabel("Disk: 0%")
        self.disk_label.setObjectName("lcars_stat_label")
        self.disk_bar = QProgressBar()
        self.disk_bar.setObjectName("lcars_progress_disk")
        dg_layout.addWidget(self.disk_label)
        dg_layout.addWidget(self.disk_bar)
        right_col.addWidget(disk_group)
        
        # Network Group
        net_group = QGroupBox("NETWORK STATUS")
        net_group.setObjectName("lcars_group")
        ng_layout = QVBoxLayout(net_group)
        self.net_traffic_label = QLabel("Traffic: Calculating...")
        self.net_traffic_label.setObjectName("lcars_info_label")
        ng_layout.addWidget(self.net_traffic_label)
        ng_layout.addStretch()
        right_col.addWidget(net_group)
        
        content_layout.addLayout(left_col)
        content_layout.addLayout(right_col)
        m_layout.addLayout(content_layout)
        
        self.tabs.addTab(monitor_tab, "MONITOR")
        
        self.main_layout.addWidget(self.tabs)

    def update_system_loop(self):
        # 1. Update Time
        current_time = datetime.now().strftime("%H:%M:%S\n%Y-%m-%d")
        self.time_label.setText(current_time)
        
        # 2. Update Monitor (if visible for performance, or always)
        # CPU
        cpu = psutil.cpu_percent()
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.cpu_bar.setValue(int(cpu))
        
        # RAM
        mem = psutil.virtual_memory()
        self.ram_label.setText(f"RAM: {mem.percent:.1f}%")
        self.ram_bar.setValue(int(mem.percent))
        
        # Disk
        try:
            d = psutil.disk_usage('/')
            self.disk_label.setText(f"DISK: {d.percent:.1f}%")
            self.disk_bar.setValue(int(d.percent))
        except: pass
        
        # Net
        try:
            n = psutil.net_io_counters()
            sent_mb = n.bytes_sent / (1024**2)
            recv_mb = n.bytes_recv / (1024**2)
            self.net_traffic_label.setText(f"Sent: {sent_mb:.1f} MB\nRecv: {recv_mb:.1f} MB")
        except: pass

    def show_projects(self): self.tabs.setCurrentIndex(0)
    def show_analysis(self): self.tabs.setCurrentIndex(1)
    def show_monitor(self): self.tabs.setCurrentIndex(2)
    def show_config(self): QMessageBox.information(self, "LCARS", "Access Denied: Level 4 Security Required")

    def apply_lcars_style(self):
        style = f"""
        QMainWindow {{
            background-color: {self.colors['background']};
        }}
        
        #lcars_left_panel {{
            background-color: {self.colors['background']};
            border-right: 3px solid {self.colors['primary']};
        }}
        
        #lcars_title {{
            color: {self.colors['background']};
            font-size: 24px; font-weight: bold; font-family: 'Arial Black';
            padding: 20px;
            background-color: {self.colors['primary']};
            border-radius: 15px; margin: 10px;
        }}
        
        #lcars_status {{
            color: {self.colors['background']};
            font-size: 14px; font-weight: bold;
            padding: 15px;
            background-color: {self.colors['success']};
            border-radius: 10px; margin: 5px;
        }}
        
        #lcars_time {{
            color: {self.colors['background']};
            font-size: 12px; font-weight: bold;
            padding: 10px;
            background-color: {self.colors['info']};
            border-radius: 8px; margin: 5px;
        }}
        
        #lcars_button {{
            background-color: {self.colors['secondary']};
            color: {self.colors['background']};
            font-size: 14px; font-weight: bold;
            padding: 15px; border: none; border-radius: 20px; margin: 5px;
        }}
        #lcars_button:hover {{ background-color: {self.colors['accent1']}; }}
        #lcars_button:pressed {{ background-color: {self.colors['accent2']}; }}
        
        #lcars_tabs {{ background-color: {self.colors['background']}; }}
        #lcars_tabs::pane {{ border: none; }}
        
        #lcars_tabs QTabBar::tab {{
            background-color: {self.colors['secondary']};
            color: {self.colors['background']};
            padding: 15px 25px; margin: 2px;
            font-weight: bold;
            border-top-left-radius: 15px; border-top-right-radius: 15px;
        }}
        #lcars_tabs QTabBar::tab:selected {{ background-color: {self.colors['primary']}; }}
        
        #lcars_tab_title {{
            color: {self.colors['background']};
            font-size: 18px; font-weight: bold;
            padding: 15px;
            background-color: {self.colors['primary']};
            border-radius: 10px; margin-bottom: 10px;
        }}
        
        /* MONITORS */
        #lcars_group {{
            color: {self.colors['text']}; font-weight: bold; font-size: 14px;
            border: 2px solid {self.colors['secondary']};
            border-radius: 10px; margin: 5px; padding: 10px;
        }}
        #lcars_stat_label {{ color: {self.colors['primary']}; font-size: 16px; font-weight: bold; }}
        
        QProgressBar {{
            border: 2px solid {self.colors['secondary']};
            border-radius: 5px;
            background-color: {self.colors['background']};
            height: 20px; text-align: center; color: white;
        }}
        #lcars_progress_cpu::chunk {{ background-color: {self.colors['danger']}; }}
        #lcars_progress_ram::chunk {{ background-color: {self.colors['warning']}; }}
        #lcars_progress_disk::chunk {{ background-color: {self.colors['success']}; }}
        
        #lcars_list {{
            background-color: {self.colors['background']};
            color: {self.colors['text']};
            border: 2px solid {self.colors['primary']};
            border-radius: 10px; padding: 10px; font-size: 14px;
        }}
        #lcars_output {{
            background-color: {self.colors['background']}; color: {self.colors['text']};
            border: 2px solid {self.colors['info']};
            border-radius: 10px; padding: 15px; font-family: 'Courier New';
        }}
        """
        self.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)
    window = PCARS23Century()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
