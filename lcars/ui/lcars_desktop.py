"""
LCARS Desktop - Main Operating System Interface
Full OS replacement with proper LCARS design (no Qt standard widgets)
"""

# Titanium Bridge Migration: import sys
import psutil
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, QScrollArea, QGridLayout, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QKeyEvent, QCloseEvent
# Titanium Bridge Migration: from typing import Optional

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color


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


class LCARSElbow(QFrame):
    """LCARS elbow-shaped panel"""
    def __init__(self, color, width, height, text="", text_color="#000", corner="top-left", clickable=False):
        super().__init__()
        self.setFixedSize(width, height)
        self.text_label = text
        self.base_color = color
        self.text_color = text_color
        
        corner_radius = {
            "top-left": "border-radius: 30px 0px 0px 0px;",
            "top-right": "border-radius: 0px 30px 0px 0px;",
            "bottom-left": "border-radius: 0px 0px 0px 30px;",
            "bottom-right": "border-radius: 0px 0px 30px 0px;",
            "left": "border-radius: 30px 0px 0px 30px;",
            "right": "border-radius: 0px 30px 30px 0px;",
            "full": "border-radius: 30px;",
        }.get(corner, "border-radius: 0px;")
        
        self.corner_style = corner_radius
        self.update_style()
        
        if text:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(15, 10, 15, 10)
            self.label = QLabel(text)
            self.label.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: bold; background: transparent;")
            layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def update_style(self, hover=False):
        color = self.brighten(self.base_color) if hover else self.base_color
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                {self.corner_style}
                border: none;
            }}
        """)
    
    def enterEvent(self, event):
        self.update_style(hover=True)
    
    def leaveEvent(self, a0):
        self.update_style(hover=False)
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+40), a)
        return c.name()


class LCARSDataBlock(QFrame):
    """LCARS data display block (like left sidebar in reference)"""
    def __init__(self, label, value, color, height=50):
        super().__init__()
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Label
        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet("color: #000; font-size: 11px; font-weight: bold; background: transparent;")
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        # Value
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet("color: #000; font-size: 18px; font-weight: bold; background: transparent;")
        layout.addWidget(self.value_label)
    
    def update_value(self, value):
        self.value_label.setText(str(value))


class LCARSAppButton(QPushButton):
    """Application launcher button with dynamic colors"""
    def __init__(self, name, icon_text, era, button_index=0):
        super().__init__()
        self.app_name = name
        self.era = era
        self.button_index = button_index
        self.setFixedSize(160, 120)
        
        # Dynamic color cycling
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer.setInterval(2500)
        
        self.layout_setup(icon_text)
        self.update_style()
    
    def layout_setup(self, icon_text):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon
        icon = QLabel(icon_text)
        icon.setStyleSheet("color: #000; font-size: 36px; font-weight: bold; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)
        
        # Name
        name_label = QLabel(self.app_name)
        name_label.setStyleSheet("color: #000; font-size: 11px; font-weight: bold; background: transparent;")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
    
    def cycle_color(self):
        self.update_style()
    
    def update_style(self):
        color = get_random_button_color(self.era)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color)};
                border: 3px solid #FFFFFF;
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
        c.setHsv(h, max(0, s-40), min(255, v+40), a)
        return c.name()
    
    @staticmethod
    def darken(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, min(255, s+40), max(0, v-40), a)
        return c.name()


class LCARSDesktop(QMainWindow):
    """LCARS Operating System Desktop"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Operating System v25.0")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        
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
    
    def apply_theme(self):
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
    
    def setup_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top header bar
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Left sidebar (LCARS data blocks like in reference image)
        left_sidebar = self.create_left_sidebar()
        content_layout.addWidget(left_sidebar)
        
        # Center workspace
        center = self.create_center_workspace()
        content_layout.addWidget(center, 1)
        
        # Right sidebar (system info)
        right_sidebar = self.create_right_sidebar()
        content_layout.addWidget(right_sidebar)
        
        main_layout.addWidget(content, 1)
        
        # Bottom footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self):
        """Top header bar"""
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet(f"background-color: {self.colors['button_colors'][0]}; border-radius: 0px;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 10, 30, 10)
        
        # Logo
        logo = QLabel("◆")
        logo.setStyleSheet("color: #000; font-size: 36px; font-weight: bold;")
        h_layout.addWidget(logo)
        
        # Title
        title = QLabel("LCARS DATABASE")
        title.setStyleSheet("color: #000; font-size: 32px; font-weight: bold; font-family: 'Swis721 BT';")
        h_layout.addStretch()
        h_layout.addWidget(title)
        h_layout.addStretch()
        
        # Time
        self.header_time = QLabel("--:--:--")
        self.header_time.setStyleSheet("color: #000; font-size: 18px; font-weight: bold;")
        h_layout.addWidget(self.header_time)
        
        return header
    
    def create_left_sidebar(self):
        """Left sidebar with data counts (like reference image)"""
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # Data blocks (alternating colors)
        data_items = [
            ("USER DATA", "20", self.colors['button_colors'][0]),
            ("DOCS", "520", self.colors['button_colors'][1]),
            ("PICTURES", "814", self.colors['button_colors'][0]),
            ("MUSIC", "476", self.colors['button_colors'][1]),
            ("VIDEOS", "973", self.colors['button_colors'][0]),
            ("DOWNLD", "46", self.colors['button_colors'][1]),
            ("", "937", self.colors['button_colors'][0]),
            ("COMPUTER", "257", self.colors['button_colors'][1]),
            ("CONTROLS", "777", self.colors['button_colors'][0]),
            ("SYSTEM", "696", self.colors['button_colors'][1]),
            ("TASK MGR", "194", self.colors['button_colors'][0]),
            ("", "1978", self.colors['button_colors'][1]),
        ]
        
        self.data_blocks = []
        for label, value, color in data_items:
            block = LCARSDataBlock(label, value, color, height=45)
            self.data_blocks.append(block)
            sidebar_layout.addWidget(block)
        
        sidebar_layout.addStretch()
        
        # Bottom control buttons
        settings_btn = LCARSElbow(self.colors['button_colors'][2], 240, 50, "SETTINGS", "#000", "left", clickable=True)
        sidebar_layout.addWidget(settings_btn)
        
        refresh_btn = LCARSElbow(self.colors['button_colors'][0], 240, 50, "REFRESH", "#000", "left", clickable=True)
        sidebar_layout.addWidget(refresh_btn)
        
        return sidebar
    
    def create_center_workspace(self):
        """Center workspace with Starfleet emblem and app grid"""
        center = QFrame()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(20, 20, 20, 20)
        center_layout.setSpacing(20)
        
        # Central emblem/title
        emblem_container = QWidget()
        emblem_layout = QVBoxLayout(emblem_container)
        emblem_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        emblem = QLabel("◆")
        emblem.setStyleSheet(f"color: {self.colors['button_colors'][0]}; font-size: 72px;")
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem_layout.addWidget(emblem)
        
        title = QLabel("THE LCARS COMPUTER NETWORK")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem_layout.addWidget(title)
        
        subtitle = QLabel("AUTHORIZED ACCESS ONLY\nPLEASE REPORT MALFUNCTIONS TO ENGINEERING STAFF ON DUTY")
        subtitle.setStyleSheet(f"color: {self.colors['text']}; font-size: 11px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emblem_layout.addWidget(subtitle)
        
        center_layout.addWidget(emblem_container)
        
        center_layout.addSpacing(40)
        
        # Application grid
        apps_container = QWidget()
        apps_layout = QGridLayout(apps_container)
        apps_layout.setSpacing(15)
        
        applications = [
            ("File\nManager", "📁"),
            ("Task\nManager", "⚙"),
            ("Terminal", "▶"),
            ("Settings", "◆"),
            ("Media\nPlayer", "♫"),
            ("Network", "◈"),
            ("Geant4\nProjects", "⬢"),
            ("Database", "▣"),
        ]
        
        row, col = 0, 0
        button_index = 0
        for name, icon in applications:
            btn = LCARSAppButton(name, icon, self.current_era, button_index=button_index)
            apps_layout.addWidget(btn, row, col)
            button_index += 1
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        center_layout.addWidget(apps_container)
        center_layout.addStretch()
        
        return center
    
    def create_right_sidebar(self):
        """Right sidebar with system info (like media player in reference)"""
        sidebar = QFrame()
        sidebar.setFixedWidth(400)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(10)
        
        # Title bar
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][0]};
            border-radius: 15px;
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 5, 15, 5)
        title_label = QLabel("LCARS SYSTEM STATUS")
        title_label.setStyleSheet("color: #000; font-size: 14px; font-weight: bold;")
        title_layout.addWidget(title_label)
        sidebar_layout.addWidget(title_bar)
        
        # System metrics panel
        metrics_panel = QFrame()
        metrics_panel.setStyleSheet(f"""
            background-color: rgba(47, 55, 73, 0.3);
            border: 2px solid {self.colors['button_colors'][1]};
            border-radius: 20px;
        """)
        metrics_layout = QVBoxLayout(metrics_panel)
        metrics_layout.setContentsMargins(20, 20, 20, 20)
        metrics_layout.setSpacing(15)
        
        # CPU
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        metrics_layout.addWidget(self.cpu_label)
        
        # Memory
        self.mem_label = QLabel("MEMORY: 0%")
        self.mem_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        metrics_layout.addWidget(self.mem_label)
        
        # Disk
        self.disk_label = QLabel("DISK: 0%")
        self.disk_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        metrics_layout.addWidget(self.disk_label)
        
        # Processes
        self.proc_label = QLabel("PROCESSES: 0")
        self.proc_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold;")
        metrics_layout.addWidget(self.proc_label)
        
        sidebar_layout.addWidget(metrics_panel)
        
        # Network status
        network_blocks = [
            ("NETWORK", "ONLINE", self.colors['button_colors'][2]),
            ("UPLINK", "ACTIVE", self.colors['button_colors'][0]),
            ("COMM", "READY", self.colors['button_colors'][3]),
        ]
        
        for label, status, color in network_blocks:
            block = LCARSDataBlock(label, status, color, height=45)
            sidebar_layout.addWidget(block)
        
        sidebar_layout.addStretch()
        
        return sidebar
    
    def create_footer(self):
        """Bottom footer bar"""
        footer = QFrame()
        footer.setFixedHeight(80)
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 10, 15, 10)
        footer_layout.setSpacing(15)
        
        # Left decorative panel
        left_panel = LCARSElbow(self.colors['button_colors'][1], 300, 60, "", "#000", "left")
        footer_layout.addWidget(left_panel)
        
        footer_layout.addStretch()
        
        # Center command button
        command_btn = QFrame()
        command_btn.setFixedSize(600, 60)
        command_btn.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][0]};
            border-radius: 15px;
        """)
        cmd_layout = QHBoxLayout(command_btn)
        cmd_label = QLabel("STARFLEET COMMAND UPLINK")
        cmd_label.setStyleSheet("color: #000; font-size: 16px; font-weight: bold;")
        cmd_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cmd_layout.addWidget(cmd_label)
        footer_layout.addWidget(command_btn)
        
        footer_layout.addStretch()
        
        # Right decorative panel
        right_panel = LCARSElbow(self.colors['button_colors'][3], 300, 60, "v25.0", "#000", "right")
        footer_layout.addWidget(right_panel)
        
        return footer
    
    def update_metrics(self, metrics):
        """Update system metrics from background thread"""
        self.cpu_label.setText(f"CPU: {metrics['cpu']:.0f}%")
        self.mem_label.setText(f"MEMORY: {metrics['memory']:.0f}%")
        self.disk_label.setText(f"DISK: {metrics['disk']:.0f}%")
        self.proc_label.setText(f"PROCESSES: {metrics['processes']}")
    
    def update_clock(self):
        """Update time displays"""
        now = datetime.now()
        self.header_time.setText(now.strftime("%H:%M:%S"))
    
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.close()
        elif a0 and a0.key() == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
    
    def closeEvent(self, a0: Optional[QCloseEvent]):
        self.metrics_worker.stop()
        self.metrics_worker.wait()
        if a0:
            a0.accept()


def main():
    app = QApplication(sys.argv)
    desktop = LCARSDesktop()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
