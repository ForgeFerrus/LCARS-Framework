import sys
import psutil
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QFrame, QProgressBar, QPushButton,
                           QComboBox, QTabWidget, QGridLayout, QGroupBox, QSlider,
                           QCheckBox, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont

# Add project root to path
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    import lcars.themes.palette as palette_module
    from lcars.themes.palette import LCARSEra, get_era_palette
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    print("LCARS theme system not available, using fallback colors")

class MonitorConfig:
    """Configuration class for system monitor settings"""
    def __init__(self):
        self.era = "25th"
        self.update_interval = 1000  # ms
        self.show_processes = True
        self.show_network = True
        self.show_disk = True
        self.show_temperature = True
        self.alert_threshold_cpu = 80
        self.alert_threshold_memory = 85
        self.alert_threshold_disk = 90
        self.dark_mode = True
        self.compact_view = False
        
    def get_era_enum(self):
        era_map = {
            "22nd": LCARSEra.COMS_22ND if THEME_AVAILABLE else None,
            "23rd": LCARSEra.PCARS_23RD if THEME_AVAILABLE else None,
            "24th": LCARSEra.LCARS_24TH if THEME_AVAILABLE else None,
            "25th": LCARSEra.LCARS_25TH if THEME_AVAILABLE else None,
            "29th": LCARSEra.TCARS_29TH if THEME_AVAILABLE else None,
        }
        return era_map.get(self.era, LCARSEra.LCARS_25TH if THEME_AVAILABLE else None)
    
    def get_palette(self):
        # Always use fallback palette to avoid theme issues
        return {
            'background': '#000000',
            'panel_color': '#1a1a1a',
            'text': '#ffffff',
            'button_colors': ['#37A6D1', '#FF6B35', '#00FF00', '#FF0000', '#FFAA00'],
            'alert_colors': ['#FF0000', '#FF6600', '#FFFF00'],
            'panel_border': '#333333',
            'panel': '#1a1a1a'
        }

class LcarsProgressBar(QProgressBar):
    def __init__(self, color="#37A6D1", parent=None):
        super().__init__(parent)
        self.color = color
        self.setTextVisible(False)
        self.setHeight = 25
        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: #050505;
                border: 1px solid #1A2332;
                border-radius: 12px;
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {self.color};
                border-radius: 10px;
            }}
        """)

class SystemMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = MonitorConfig()
        # Always use fallback palette for now to avoid theme issues
        self.palette = self.config.get_palette()
        self.setWindowTitle("LCARS System Monitor")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        self.setStyleSheet(f"background-color: {self.palette['background']};")
        
        # Setup UI
        self.setup_ui()
        
        # Setup timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_stats)
        self.update_timer.start(self.config.update_interval)
        
        # Initial update
        self.update_stats()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header with era selector and controls
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content with tabs
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - System stats
        left_panel = self.create_system_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Configuration
        right_panel = self.create_config_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)
        
    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {self.palette['button_colors'][0]};
                border: none;
                border-radius: 10px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        
        # Title
        title = QLabel("◢ LCARS SYSTEM MONITOR")
        title.setStyleSheet("color: black; font-size: 24px; font-weight: bold; text-transform: uppercase;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Era selector
        era_label = QLabel("ERA:")
        era_label.setStyleSheet("color: black; font-weight: bold;")
        layout.addWidget(era_label)
        
        self.era_combo = QComboBox()
        self.era_combo.addItems(["22nd", "23rd", "24th", "25th", "29th"])
        self.era_combo.setCurrentText(self.config.era)
        self.era_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: black;
                border: none;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.era_combo.currentTextChanged.connect(self.change_era)
        layout.addWidget(self.era_combo)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF0000;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6666;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return header
        
    def create_system_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.palette['panel_color']};
                border: 2px solid {self.palette['panel_border']};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        
        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.palette['panel_border']};
                background-color: {self.palette['background']};
                border-radius: 10px;
            }}
            QTabBar::tab {{
                background-color: {self.palette['button_colors'][1]};
                color: black;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            QTabBar::tab:selected {{
                background-color: {self.palette['button_colors'][0]};
            }}
        """)
        
        # System Overview Tab
        overview_tab = self.create_overview_tab()
        self.tabs.addTab(overview_tab, "OVERVIEW")
        
        # Processes Tab
        if self.config.show_processes:
            processes_tab = self.create_processes_tab()
            self.tabs.addTab(processes_tab, "PROCESSES")
        
        # Network Tab
        if self.config.show_network:
            network_tab = self.create_network_tab()
            self.tabs.addTab(network_tab, "NETWORK")
            
        layout.addWidget(self.tabs)
        return panel
        
    def create_overview_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # CPU Usage
        cpu_group = QGroupBox("◢ CPU UTILIZATION")
        cpu_group.setStyleSheet(f"color: {self.palette['text']}; font-weight: bold;")
        cpu_layout = QVBoxLayout(cpu_group)
        
        self.cpu_bar = LcarsProgressBar(self.palette['button_colors'][0])
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet(f"color: {self.palette['text']};")
        cpu_layout.addWidget(self.cpu_label)
        cpu_layout.addWidget(self.cpu_bar)
        layout.addWidget(cpu_group)
        
        # Memory Usage
        memory_group = QGroupBox("◢ MEMORY UTILIZATION")
        memory_group.setStyleSheet(f"color: {self.palette['text']}; font-weight: bold;")
        memory_layout = QVBoxLayout(memory_group)
        
        self.memory_bar = LcarsProgressBar(self.palette['button_colors'][1])
        self.memory_label = QLabel("Memory: 0%")
        self.memory_label.setStyleSheet(f"color: {self.palette['text']};")
        memory_layout.addWidget(self.memory_label)
        memory_layout.addWidget(self.memory_bar)
        layout.addWidget(memory_group)
        
        # Disk Usage
        if self.config.show_disk:
            disk_group = QGroupBox("◢ DISK UTILIZATION")
            disk_group.setStyleSheet(f"color: {self.palette['text']}; font-weight: bold;")
            disk_layout = QVBoxLayout(disk_group)
            
            self.disk_bar = LcarsProgressBar(self.palette['button_colors'][2])
            self.disk_label = QLabel("Disk: 0%")
            self.disk_label.setStyleSheet(f"color: {self.palette['text']};")
            disk_layout.addWidget(self.disk_label)
            disk_layout.addWidget(self.disk_bar)
            layout.addWidget(disk_group)
        
        layout.addStretch()
        return widget
        
    def create_processes_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("◢ TOP PROCESSES"))
        self.processes_text = QTextEdit()
        self.processes_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.palette['background']};
                color: {self.palette['text']};
                border: 1px solid {self.palette['panel_border']};
                font-family: 'Consolas', monospace;
            }}
        """)
        self.processes_text.setReadOnly(True)
        layout.addWidget(self.processes_text)
        
        return widget
        
    def create_network_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("◢ NETWORK STATISTICS"))
        
        # Network stats
        net_layout = QGridLayout()
        
        self.bytes_sent_label = QLabel("Bytes Sent: 0")
        self.bytes_recv_label = QLabel("Bytes Received: 0")
        self.packets_sent_label = QLabel("Packets Sent: 0")
        self.packets_recv_label = QLabel("Packets Received: 0")
        
        for label in [self.bytes_sent_label, self.bytes_recv_label, 
                     self.packets_sent_label, self.packets_recv_label]:
            label.setStyleSheet(f"color: {self.palette['text']};")
            
        net_layout.addWidget(self.bytes_sent_label, 0, 0)
        net_layout.addWidget(self.bytes_recv_label, 0, 1)
        net_layout.addWidget(self.packets_sent_label, 1, 0)
        net_layout.addWidget(self.packets_recv_label, 1, 1)
        
        layout.addLayout(net_layout)
        layout.addStretch()
        
        return widget
        
    def create_config_panel(self):
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.palette['panel_color']};
                border: 2px solid {self.palette['panel_border']};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        
        # Configuration Title
        config_title = QLabel("◢ CONFIGURATION")
        config_title.setStyleSheet(f"color: {self.palette['text']}; font-size: 18px; font-weight: bold;")
        layout.addWidget(config_title)
        
        # Update Interval
        interval_group = QGroupBox("Update Interval")
        interval_group.setStyleSheet(f"color: {self.palette['text']};")
        interval_layout = QVBoxLayout(interval_group)
        
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(100, 5000)
        self.interval_slider.setValue(self.config.update_interval)
        self.interval_slider.valueChanged.connect(self.update_interval_changed)
        
        self.interval_label = QLabel(f"{self.config.update_interval} ms")
        self.interval_label.setStyleSheet(f"color: {self.palette['text']};")
        
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.interval_slider)
        layout.addWidget(interval_group)
        
        # Display Options
        display_group = QGroupBox("Display Options")
        display_group.setStyleSheet(f"color: {self.palette['text']};")
        display_layout = QVBoxLayout(display_group)
        
        self.show_processes_cb = QCheckBox("Show Processes")
        self.show_processes_cb.setChecked(self.config.show_processes)
        self.show_processes_cb.toggled.connect(self.toggle_processes)
        self.show_processes_cb.setStyleSheet(f"color: {self.palette['text']};")
        display_layout.addWidget(self.show_processes_cb)
        
        self.show_network_cb = QCheckBox("Show Network")
        self.show_network_cb.setChecked(self.config.show_network)
        self.show_network_cb.toggled.connect(self.toggle_network)
        self.show_network_cb.setStyleSheet(f"color: {self.palette['text']};")
        display_layout.addWidget(self.show_network_cb)
        
        self.show_disk_cb = QCheckBox("Show Disk")
        self.show_disk_cb.setChecked(self.config.show_disk)
        self.show_disk_cb.toggled.connect(self.toggle_disk)
        self.show_disk_cb.setStyleSheet(f"color: {self.palette['text']};")
        display_layout.addWidget(self.show_disk_cb)
        
        layout.addWidget(display_group)
        
        # Alert Thresholds
        alerts_group = QGroupBox("Alert Thresholds")
        alerts_group.setStyleSheet(f"color: {self.palette['text']};")
        alerts_layout = QVBoxLayout(alerts_group)
        
        # CPU Threshold
        cpu_threshold_layout = QHBoxLayout()
        cpu_threshold_layout.addWidget(QLabel("CPU Alert:"))
        self.cpu_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.cpu_threshold_slider.setRange(50, 100)
        self.cpu_threshold_slider.setValue(self.config.alert_threshold_cpu)
        self.cpu_threshold_slider.valueChanged.connect(self.update_cpu_threshold)
        cpu_threshold_layout.addWidget(self.cpu_threshold_slider)
        self.cpu_threshold_label = QLabel(f"{self.config.alert_threshold_cpu}%")
        self.cpu_threshold_label.setStyleSheet(f"color: {self.palette['text']};")
        cpu_threshold_layout.addWidget(self.cpu_threshold_label)
        alerts_layout.addLayout(cpu_threshold_layout)
        
        # Memory Threshold
        mem_threshold_layout = QHBoxLayout()
        mem_threshold_layout.addWidget(QLabel("Memory Alert:"))
        self.mem_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.mem_threshold_slider.setRange(50, 100)
        self.mem_threshold_slider.setValue(self.config.alert_threshold_memory)
        self.mem_threshold_slider.valueChanged.connect(self.update_memory_threshold)
        mem_threshold_layout.addWidget(self.mem_threshold_slider)
        self.mem_threshold_label = QLabel(f"{self.config.alert_threshold_memory}%")
        self.mem_threshold_label.setStyleSheet(f"color: {self.palette['text']};")
        mem_threshold_layout.addWidget(self.mem_threshold_label)
        alerts_layout.addLayout(mem_threshold_layout)
        
        layout.addWidget(alerts_group)
        
        # Apply Button
        apply_btn = QPushButton("APPLY SETTINGS")
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['button_colors'][0]};
                color: black;
                border: none;
                padding: 10px;
                font-weight: bold;
                text-transform: uppercase;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: white;
                color: {self.palette['button_colors'][0]};
            }}
        """)
        apply_btn.clicked.connect(self.apply_settings)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        return panel
        
    def change_era(self, era):
        self.config.era = era
        self.palette = self.config.get_palette()
        self.apply_theme()
        
    def apply_theme(self):
        self.setStyleSheet(f"background-color: {self.palette['background']};")
        # Rebuild UI to apply new theme
        self.setup_ui()
        
    def update_interval_changed(self, value):
        self.interval_label.setText(f"{value} ms")
        
    def update_cpu_threshold(self, value):
        self.cpu_threshold_label.setText(f"{value}%")
        
    def update_memory_threshold(self, value):
        self.mem_threshold_label.setText(f"{value}%")
        
    def toggle_processes(self, checked):
        self.config.show_processes = checked
        
    def toggle_network(self, checked):
        self.config.show_network = checked
        
    def toggle_disk(self, checked):
        self.config.show_disk = checked
        
    def apply_settings(self):
        self.config.update_interval = self.interval_slider.value()
        self.config.alert_threshold_cpu = self.cpu_threshold_slider.value()
        self.config.alert_threshold_memory = self.mem_threshold_slider.value()
        
        # Restart timer with new interval
        self.update_timer.stop()
        self.update_timer.start(self.config.update_interval)
        
    def update_stats(self):
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_bar.setValue(int(cpu_percent))
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
            
            # Alert color for CPU
            if cpu_percent > self.config.alert_threshold_cpu:
                self.cpu_bar.color = self.palette['alert_colors'][0]
            else:
                self.cpu_bar.color = self.palette['button_colors'][0]
            self.cpu_bar.setStyleSheet(self.cpu_bar.styleSheet())
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.memory_bar.setValue(int(memory_percent))
            self.memory_label.setText(f"Memory: {memory_percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)")
            
            # Alert color for Memory
            if memory_percent > self.config.alert_threshold_memory:
                self.memory_bar.color = self.palette['alert_colors'][0]
            else:
                self.memory_bar.color = self.palette['button_colors'][1]
            self.memory_bar.setStyleSheet(self.memory_bar.styleSheet())
            
            # Disk Usage
            if self.config.show_disk and hasattr(self, 'disk_bar'):
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.disk_bar.setValue(int(disk_percent))
                self.disk_label.setText(f"Disk: {disk_percent:.1f}% ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)")
                
                # Alert color for Disk
                if disk_percent > self.config.alert_threshold_disk:
                    self.disk_bar.color = self.palette['alert_colors'][0]
                else:
                    self.disk_bar.color = self.palette['button_colors'][2]
                self.disk_bar.setStyleSheet(self.disk_bar.styleSheet())
            
            # Network Stats
            if self.config.show_network:
                net = psutil.net_io_counters()
                self.bytes_sent_label.setText(f"Bytes Sent: {net.bytes_sent:,}")
                self.bytes_recv_label.setText(f"Bytes Received: {net.bytes_recv:,}")
                self.packets_sent_label.setText(f"Packets Sent: {net.packets_sent:,}")
                self.packets_recv_label.setText(f"Packets Received: {net.packets_recv:,}")
            
            # Processes
            if self.config.show_processes and hasattr(self, 'processes_text'):
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                    try:
                        processes.append(f"{proc.info['pid']:>6} {proc.info['name']:<20} {proc.info['cpu_percent']:>5.1f}%")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                processes.sort(key=lambda x: float(x.split()[-1].strip('%')), reverse=True)
                self.processes_text.setText('\n'.join(processes[:10]))
                
        except Exception as e:
            print(f"Error updating stats: {e}")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    from PyQt6.QtGui import QColor
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    monitor = SystemMonitor()
    monitor.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
        
    def setup_ui(self):
        # Header
        header = QHBoxLayout()
        header.setSpacing(0)
        
        title = QLabel("SYSTEM MONITORING // NODE_01")
        title.setStyleSheet(f"color: {self.palette['button_colors'][0]}; font-size: 24px; font-weight: normal; font-family: 'Swis721 BT';")
        header.addWidget(title)
        header.addStretch()
        
        exit_btn = QPushButton("✕")
        exit_btn.setFixedSize(40, 40)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet(f"background: {self.palette['alert_colors'][0]}; color: black; border-radius: 20px; font-weight: normal;")
        header.addWidget(exit_btn)
        
        self.layout.addLayout(header)
        
        # Stats Grid
        self.grid = QGridLayout()
        self.layout.addLayout(self.grid)
        
        self.cpu_bar = self.add_stat("CPU USAGE", 0, self.palette['button_colors'][1])
        self.mem_bar = self.add_stat("MEMORY USAGE", 1, self.palette['button_colors'][2])
        self.disk_bar = self.add_stat("DISK SPACE", 2, self.palette['button_colors'][3])
        
        self.layout.addStretch()
        
    def add_stat(self, name, row, color):
        lbl = QLabel(name)
        lbl.setStyleSheet(f"color: {color}; font-weight: normal; font-size: 14px;")
        self.grid.addWidget(lbl, row * 2, 0)
        
        bar = LcarsProgressBar(color)
        self.grid.addWidget(bar, row * 2 + 1, 0)
        
        val_lbl = QLabel("0%")
        val_lbl.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.grid.addWidget(val_lbl, row * 2 + 1, 1)
        
        return (bar, val_lbl)
        
    def update_stats(self):
        cpu = psutil.cpu_percent()
        self.cpu_bar[0].setValue(int(cpu))
        self.cpu_bar[1].setText(f"{cpu}%")
        
        mem = psutil.virtual_memory().percent
        self.mem_bar[0].setValue(int(mem))
        self.mem_bar[1].setText(f"{mem}%")
        
        disk = psutil.disk_usage('/').percent
        self.disk_bar[0].setValue(int(disk))
        self.disk_bar[1].setText(f"{disk}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    from PyQt6.QtWidgets import QPushButton, QGridLayout
    win = SystemMonitor()
    win.show()
    sys.exit(app.exec())
