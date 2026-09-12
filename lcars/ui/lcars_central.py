"""
LCARS Central System v25.0 - Desktop after authentication
Full LCARS design, no Qt widgets, dynamic color buttons
"""

# Titanium Bridge Migration: import sys
import psutil
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea,
    QTreeView
)
from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QKeyEvent, QCloseEvent
# Titanium Bridge Migration: from typing import Optional

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.theme.lcars_palette import LCARSEra, get_era_palette, get_random_button_color
from lcars.modules.project import ProjectManager


class MetricsWorker(QThread):
    """Background system metrics"""
    metrics_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            if True:
                metrics = {
                    'cpu': psutil.cpu_percent(interval=1),
                    'memory': psutil.virtual_memory().percent,
                    'disk': psutil.disk_usage('/').percent,
                    'processes': len(psutil.pids()),
                }
                self.metrics_updated.emit(metrics)
                self.msleep(2000)
            if False: # Removed except block
                pass
    
    def stop(self):
        self.running = False


class DynamicButton(QPushButton):
    """Button with dynamic color cycling - random from palette"""
    def __init__(self, text, era, width=None, height=None, font_size=12, button_index=0):
        super().__init__(text)
        self.era = era
        self.font_size = font_size
        self.button_index = button_index
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        # Кожна кнопка має свій offset для асинхронної зміни кольорів
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        # Startdelay = button_index * 300ms, потім змінюється кожні 2500ms
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer_interval = 2500
        self.color_timer.setInterval(self.color_timer_interval)
        
        self.update_style()
    
    def cycle_color(self):
        """Cycle to random color from palette"""
        self.update_style()
    
    def update_style(self):
        color = get_random_button_color(self.era)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: {self.font_size}px;
                font-family: 'Swis721 BT';
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color)};
                border: 2px solid rgba(255,255,255,0.5);
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


class LCARSDataRow(QFrame):
    """Custom data row (not QTableWidget)"""
    def __init__(self, data, colors, even_row=False):
        super().__init__()
        
        bg_color = colors['button_colors'][0] if even_row else "rgba(47, 55, 73, 0.2)"
        self.setFixedHeight(45)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: none;
                border-bottom: 1px solid {colors['button_colors'][2]};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(15)
        
        # Columns
        widths = [150, 450, 200, 100, 150]
        for i, (value, width) in enumerate(zip(data, widths)):
            label = QLabel(str(value)[:50])
            label.setFixedWidth(width)
            label.setStyleSheet(f"""
                color: {colors['text']};
                font-size: 11px;
                background: transparent;
                border: none;
                font-family: 'Swis721 BT';
            """)
            layout.addWidget(label)
        
        layout.addStretch()


class LCARSDataBlock(QFrame):
    """Data display block"""
    def __init__(self, label, value, color, height=50, is_status=False):
        super().__init__()
        self.setFixedHeight(height)
        self.base_color = color
        self.is_status = is_status
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(f"color: #000; font-size: 11px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: #000; font-size: 16px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        self.value_label.setText(str(value))


class LCARSCentralSystem(QMainWindow):
    """LCARS Central System - Main Workspace"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central System v25.0")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        self.geant4_root = Path(project_root) / "Geant4" / "Enterprise"
        self.project_manager = ProjectManager(self.geant4_root)
        
        # Load LCARS font
        self.load_lcars_font()
        
        # Metrics
        self.metrics_worker = MetricsWorker()
        self.metrics_worker.metrics_updated.connect(self.update_metrics)
        self.metrics_worker.start()
        
        self.apply_theme()
        self.setup_ui()
        
        # Clock
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        
        self.showFullScreen()
    
    def load_lcars_font(self):
        """Load LCARS font from resources"""
        font_path = Path(project_root) / "resources" / "fonts" / "Swis721 Bt.otf"
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
    
    def apply_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
    
    def setup_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Left dock
        dock = self.create_dock()
        content_layout.addWidget(dock, 0)
        
        # Workspace
        self.workspace = QStackedWidget()
        self.workspace_pages = {}
        self.create_workspace_pages()
        content_layout.addWidget(self.workspace, 1)
        
        main_layout.addWidget(content, 1)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self):
        """Header bar"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {self.colors['button_colors'][0]}; border-radius: 0px;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 10, 30, 10)
        
        logo = QLabel("◆")
        logo.setStyleSheet("color: #000; font-size: 40px; font-weight: bold;")
        h_layout.addWidget(logo)
        
        title = QLabel("LCARS STARFLEET COMMAND")
        title.setStyleSheet("color: #000; font-size: 32px; font-weight: bold; font-family: 'Swis721 BT';")
        h_layout.addStretch()
        h_layout.addWidget(title)
        h_layout.addStretch()
        
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("color: #000; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        self.stardate_label = QLabel("SD 2401.001")
        self.stardate_label.setStyleSheet("color: #000; font-size: 14px; font-family: 'Swis721 BT';")
        
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.stardate_label)
        h_layout.addWidget(time_widget)
        
        return header
    
    def create_dock(self):
        """Left dock with dynamic buttons"""
        dock = QFrame()
        dock.setFixedWidth(260)
        dock.setStyleSheet(f"background-color: {self.colors['background']}; border: 2px solid {self.colors['panel_border']}; border-radius: 20px;")
        
        dock_layout = QVBoxLayout(dock)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(8)
        
        self.dock_buttons = {}
        for idx, (label, key) in enumerate([
            ("WORKSPACE", "workspace"),
            ("OPERATIONS", "operations"),
            ("ANALYTICS", "analytics"),
            ("COMMUNICATIONS", "communications"),
            ("UTILITIES", "utilities"),
            ("APPLICATIONS", "applications"),
            ("AI ASSISTANT", "ai"),
            ("SYSTEM", "system"),
            ("FILE MANAGER", "file_manager"),
        ]):
            btn = DynamicButton(f"◢ {label}", self.current_era, width=240, height=60, font_size=12, button_index=idx)
            btn.clicked.connect(lambda _, k=key: self.switch_workspace(k))
            self.dock_buttons[key] = btn
            dock_layout.addWidget(btn)
        
        dock_layout.addStretch()
        return dock
    
    def create_workspace_pages(self):
        """Create all workspace pages"""
        pages = {
            'workspace': self.create_workspace_page,
            'operations': self.create_operations_page,
            'analytics': self.create_analytics_page,
            'communications': self.create_communications_page,
            'utilities': self.create_utilities_page,
            'applications': self.create_applications_page,
            'ai': self.create_ai_page,
            'system': self.create_system_page,
            'file_manager': self.create_file_manager_page,
        }
        
        for key, builder in pages.items():
            page = builder()
            self.workspace_pages[key] = page
            self.workspace.addWidget(page)
        
        self.switch_workspace('workspace')
    
    def switch_workspace(self, key):
        """Switch workspace page"""
        if key in self.workspace_pages:
            self.workspace.setCurrentWidget(self.workspace_pages[key])

    def create_file_manager_page(self):
        """Geant4-aware file manager (read-only tree)"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("◢ FILE MANAGER // GEANT4 ROOT")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)

        path_label = QLabel(str(self.geant4_root))
        path_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px; font-family: 'Consolas';")
        layout.addWidget(path_label)

        if self.geant4_root.exists():
            # Geant4 folder structure indicator
            info_text = QLabel(f"Geant4 Enterprise Edition\nPath: {self.geant4_root}\nStatus: Available")
            info_text.setStyleSheet(f"color: {self.colors['text']}; font-size: 11px; padding: 10px; background: rgba(0,100,0,0.1); border: 1px solid {self.colors['panel_border']};")
            layout.addWidget(info_text)
        else:
            missing = QLabel("Geant4 path not found. Please configure the path in settings.")
            missing.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px;")
            layout.addWidget(missing)

        layout.addStretch()
        return page
    
    def create_workspace_page(self):
        """Projects workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ GEANT4 PROJECT WORKSPACE")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Custom table header
        header_data = ["NAME", "PATH", "STATUS", "SIZE", "MODIFIED"]
        header_frame = LCARSDataRow(header_data, self.colors, False)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['button_colors'][1]};
                border: none;
            }}
        """)
        for child in header_frame.findChildren(QLabel):
            child.setStyleSheet(f"color: #000; font-size: 12px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(header_frame)
        
        # Projects list
        projects = self.project_manager.get_project_names()
        for i, proj_name in enumerate(projects):
            proj = self.project_manager.get_project(proj_name)
            if proj:
                status = "✓ Ready" if proj.executable else "⚠ Building"
                row_data = [proj.name, str(proj.path)[:40], status, "--", "--"]
            else:
                row_data = [proj_name, "N/A", "⚠ Error", "--", "--"]
            row = LCARSDataRow(row_data, self.colors, i % 2 == 0)
            layout.addWidget(row)
        
        layout.addStretch()
        return page
    
    def create_operations_page(self):
        """Operations workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SIMULATION OPERATIONS")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        for idx, label in enumerate(["BUILD", "RUN", "DEBUG", "OPTIMIZE"]):
            btn = DynamicButton(label, self.current_era, width=140, height=55, font_size=12, button_index=idx)
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        
        log_label = QLabel("◢ OPERATION LOG")
        log_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 14px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(log_label)
        
        log_frame = QFrame()
        log_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000;
                border: 2px solid {self.colors['button_colors'][2]};
                border-radius: 15px;
            }}
        """)
        log_layout = QVBoxLayout(log_frame)
        
        self.op_log = QLabel("Ready for operations...")
        self.op_log.setStyleSheet(f"color: {self.colors['button_colors'][0]}; font-family: 'Swis721 BT'; font-size: 11px; background: transparent; border: none;")
        self.op_log.setWordWrap(True)
        log_layout.addWidget(self.op_log)
        
        layout.addWidget(log_frame, 1)
        return page
    
    def create_analytics_page(self):
        """Analytics workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ DATA ANALYTICS ENGINE")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Metrics blocks
        metrics_layout = QHBoxLayout()
        metrics = [
            ("SAMPLES", "0", self.colors['button_colors'][0]),
            ("PROCESSING", "0", self.colors['button_colors'][1]),
            ("ERRORS", "0", self.colors['button_colors'][2]),
            ("WARNINGS", "0", self.colors['button_colors'][3]),
        ]
        for label, value, color in metrics:
            block = LCARSDataBlock(label, value, color, height=60)
            metrics_layout.addWidget(block)
        layout.addLayout(metrics_layout)
        
        layout.addStretch()
        return page
    
    def create_communications_page(self):
        """Communications workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ COMMUNICATIONS CENTER")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(47, 55, 73, 0.3);
                border: 2px solid {self.colors['button_colors'][0]};
                border-radius: 15px;
            }}
        """)
        alerts_layout = QVBoxLayout(alerts_frame)
        
        for alert in ["◆ System Update Available", "◆ Build Queue: 3 pending", "◆ Memory Usage: 65%"]:
            alert_label = QLabel(alert)
            alert_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 13px; background: transparent; border: none; font-family: 'Swis721 BT';")
            alerts_layout.addWidget(alert_label)
        
        alerts_layout.addStretch()
        layout.addWidget(alerts_frame, 1)
        return page
    
    def create_utilities_page(self):
        """Utilities workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SYSTEM UTILITIES")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        util_layout = QHBoxLayout()
        for idx, label in enumerate(["FILE MANAGER", "TASK MANAGER", "SETTINGS", "SEARCH"]):
            btn = DynamicButton(label, self.current_era, width=160, height=70, font_size=12, button_index=idx)
            util_layout.addWidget(btn)
        layout.addLayout(util_layout)
        layout.addStretch()
        return page
    
    def create_applications_page(self):
        """Applications workspace - ВСІ МОДУЛІ СИСТЕМИ"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        
        title = QLabel("◢ APPLICATIONS REGISTRY - ALL LCARS MODULES")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Scroll area для багатьох кнопок
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: transparent; border: 1px solid {self.colors['panel_border']};")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # ВСІUI модулі системи
        apps = [
            ("🔬 Geant4 Workstation", self.launch_geant4_workstation),
            ("📊 System Monitor", self.launch_system_monitor),
            ("🏥 Health Check", self.launch_health_check),
            ("🖥️ LCARS Desktop", self.launch_lcars_desktop),
            ("🔒 Lock Screen Demo", self.launch_lock_screen),
            ("🎨 Theme Demo (All Eras)", self.launch_theme_demo),
            ("🌌 LCARS 24th Century", self.launch_lcars_24th),
            ("🌠 LCARS 25th Century", self.launch_lcars_25th),
            ("⚡ PCARS 22nd Century", self.launch_pcars_22nd),
            ("🚀 PCARS 23rd Century", self.launch_pcars_23rd),
            ("🔮 TCARS 29th Century", self.launch_tcars_29th),
            ("⚔️ Klingon Interface", self.launch_klingon),
            ("🔧 Modular LCARS", self.launch_modular),
            ("📡 LCARS BIOS", self.launch_bios),
        ]
        
        for idx, (name, callback) in enumerate(apps):
            btn = DynamicButton(name, self.current_era, width=700, height=50, font_size=13, button_index=idx)
            btn.clicked.connect(callback)
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return page
    
    def create_ai_page(self):
        """AI Assistant workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ AI ASSISTANT - SEVEN")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        chat_frame = QFrame()
        chat_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000;
                border: 2px solid {self.colors['button_colors'][2]};
                border-radius: 15px;
            }}
        """)
        chat_layout = QVBoxLayout(chat_frame)
        
        chat_text = QLabel("Seven (AI Core) is ready to assist.\nHow can I help you today?")
        chat_text.setStyleSheet(f"color: {self.colors['text']}; font-size: 13px; background: transparent; border: none; font-family: 'Swis721 BT';")
        chat_text.setWordWrap(True)
        chat_layout.addWidget(chat_text)
        
        layout.addWidget(chat_frame, 1)
        return page
    
    def create_system_page(self):
        """System monitoring workspace"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SYSTEM MONITOR")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        metrics_container = QHBoxLayout()
        
        self.cpu_block = LCARSDataBlock("CPU", "0%", self.colors['button_colors'][0], height=60)
        metrics_container.addWidget(self.cpu_block)
        
        self.mem_block = LCARSDataBlock("MEMORY", "0%", self.colors['button_colors'][1], height=60)
        metrics_container.addWidget(self.mem_block)
        
        self.disk_block = LCARSDataBlock("DISK", "0%", self.colors['button_colors'][2], height=60)
        metrics_container.addWidget(self.disk_block)
        
        self.proc_block = LCARSDataBlock("PROCESSES", "0", self.colors['button_colors'][3], height=60)
        metrics_container.addWidget(self.proc_block)
        
        layout.addLayout(metrics_container)
        layout.addStretch()
        
        return page
    
    def create_footer(self):
        """Footer bar"""
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-radius: 0px;")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 5, 20, 5)
        
        self.cpu_status = QLabel("CPU: 0%")
        self.cpu_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.cpu_status)
        
        self.mem_status = QLabel("MEM: 0%")
        self.mem_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.mem_status)
        
        self.disk_status = QLabel("DISK: 0%")
        self.disk_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.disk_status)
        
        footer_layout.addStretch()
        
        self.version_label = QLabel("v25.0 | STARFLEET | ONLINE")
        self.version_label.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.version_label)
        
        return footer
    
    def update_metrics(self, metrics):
        """Update system metrics"""
        cpu = f"{metrics['cpu']:.0f}%"
        mem = f"{metrics['memory']:.0f}%"
        disk = f"{metrics['disk']:.0f}%"
        proc = f"{metrics['processes']}"
        
        self.cpu_block.update_value(cpu)
        self.mem_block.update_value(mem)
        self.disk_block.update_value(disk)
        self.proc_block.update_value(proc)
        
        self.cpu_status.setText(f"CPU: {cpu}")
        self.mem_status.setText(f"MEM: {mem}")
        self.disk_status.setText(f"DISK: {disk}")
    
    def update_clock(self):
        """Update time"""
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        stardate = 2401 + (now.timetuple().tm_yday / 365.25)
        self.stardate_label.setText(f"SD {stardate:.3f}")
    
    # ========== ЗАПУСК МОДУЛІВ ==========
    
    def launch_geant4_workstation(self):
        """Запуск Geant4 Workstation"""
        if True:
            from lcars.ui.geant4_workstation import Geant4Workstation
            self.geant4_win = Geant4Workstation()
            self.geant4_win.show()
        if False: # Removed except block
            print(f"Error launching Geant4 Workstation: {e}")
    
    def launch_system_monitor(self):
        """Запуск System Monitor"""
        if True:
            from lcars.ui.system_monitor import SystemMonitor
            self.monitor_win = SystemMonitor()
            self.monitor_win.show()
        if False: # Removed except block
            print(f"Error launching System Monitor: {e}")
    
    def launch_health_check(self):
        """Запуск Health Check"""
        if True:
            from lcars.ui.health_check import HealthCheck
            self.health_win = HealthCheck()
            self.health_win.show()
        if False: # Removed except block
            print(f"Error launching Health Check: {e}")
    
    def launch_lcars_desktop(self):
        """Запуск LCARS Desktop"""
        if True:
            from lcars.ui.lcars_desktop import LCARSDesktop
            self.desktop_win = LCARSDesktop()
            self.desktop_win.show()
        if False: # Removed except block
            print(f"Error launching LCARS Desktop: {e}")
    
    def launch_lock_screen(self):
        """Запуск Lock Screen"""
        if True:
            from lcars.ui.lcars_lock_screen import LCARSLockScreen
            self.lock_win = LCARSLockScreen()
            self.lock_win.show()
        if False: # Removed except block
            print(f"Error launching Lock Screen: {e}")
    
    def launch_theme_demo(self):
        """Запуск Theme Demo"""
        if True:
            from lcars.ui.full_theme_demo import LCARSDemo
            self.demo_win = LCARSDemo()
            self.demo_win.show()
        if False: # Removed except block
            print(f"Error launching Theme Demo: {e}")
    
    def launch_lcars_24th(self):
        """Запуск LCARS 24th Century"""
        if True:
            from lcars.ui.LCARS_24th import LCARS24thCentury
            self.lcars24_win = LCARS24thCentury()
            self.lcars24_win.show()
        if False: # Removed except block
            print(f"Error launching LCARS 24th: {e}")
    
    def launch_lcars_25th(self):
        """Запуск LCARS 25th Century"""
        if True:
            from lcars.ui.LCARS_25th import LCARS25thCentury
            self.lcars25_win = LCARS25thCentury()
            self.lcars25_win.show()
        if False: # Removed except block
            print(f"Error launching LCARS 25th: {e}")
    
    def launch_pcars_22nd(self):
        """Запуск PCARS 22nd Century"""
        if True:
            from lcars.ui.PCARS_22nd import PCARS22ndCentury
            self.pcars22_win = PCARS22ndCentury()
            self.pcars22_win.show()
        if False: # Removed except block
            print(f"Error launching PCARS 22nd: {e}")
    
    def launch_pcars_23rd(self):
        """Запуск PCARS 23rd Century"""
        if True:
            from lcars.ui.PCARS_23rd import PCARS23rdCentury
            self.pcars23_win = PCARS23rdCentury()
            self.pcars23_win.show()
        if False: # Removed except block
            print(f"Error launching PCARS 23rd: {e}")
    
    def launch_tcars_29th(self):
        """Запуск TCARS 29th Century"""
        if True:
            from lcars.ui.TCARS_29th import TCARS29thCentury
            self.tcars29_win = TCARS29thCentury()
            self.tcars29_win.show()
        if False: # Removed except block
            print(f"Error launching TCARS 29th: {e}")
    
    def launch_klingon(self):
        """Запуск Klingon Interface"""
        if True:
            from lcars.ui.Klingon_system import KlingonInterface
            self.klingon_win = KlingonInterface()
            self.klingon_win.show()
        if False: # Removed except block
            print(f"Error launching Klingon Interface: {e}")
    
    def launch_modular(self):
        """Запуск Modular LCARS"""
        if True:
            from lcars.ui.modular_lcars import ModularLCARS
            self.modular_win = ModularLCARS()
            self.modular_win.show()
        if False: # Removed except block
            print(f"Error launching Modular LCARS: {e}")
    
    def launch_bios(self):
        """Запуск LCARS BIOS"""
        if True:
            from ui.uefi import LCARSBios
            self.bios_win = LCARSBios()
            self.bios_win.show()
        if False: # Removed except block
            print(f"Error launching LCARS BIOS: {e}")
    
    # ========== КІНЕЦЬ ЗАПУСКІВ ==========
    
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.close()
    
    def closeEvent(self, a0: Optional[QCloseEvent]):
        self.metrics_worker.stop()
        self.metrics_worker.wait()
        if a0:
            a0.accept()


def main():
    app = QApplication(sys.argv)
    window = LCARSCentralSystem()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
