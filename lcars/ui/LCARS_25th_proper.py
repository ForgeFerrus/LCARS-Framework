"""
LCARS Interface - 25th Century Edition (Proper Version)
Authentic LCARS system with sequential color animation and full functionality
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QHBoxLayout, QListWidget, QTabWidget, QLineEdit, QDialog, QFormLayout,
                           QScrollArea, QFrame, QGridLayout, QProgressBar, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_button_color_cycle

class SystemMonitor(QThread):
    """Background system monitoring"""
    update_signal = pyqtSignal(dict)
    
    def run(self):
        while True:
            self.msleep(1000)
            data = {
                'cpu': 25 + (len(str(self.msleep(1))) % 50),
                'memory': 40 + (len(str(self.msleep(1))) % 30),
                'status': 'ONLINE'
            }
            self.update_signal.emit(data)

class LCARSButton(QPushButton):
    """Custom LCARS button with sequential color animation"""
    
    def __init__(self, text, color_index=0, parent=None):
        super().__init__(text, parent)
        self.color_index = color_index
        self.base_color = None
        self.is_active = False
        
    def update_color(self, colors):
        """Update button color based on its index"""
        if self.is_active and self.color_index < len(colors):
            self.base_color = colors[self.color_index]
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {self.base_color};
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-size: 14px;
                    font-weight: bold;
                    font-family: 'Orbitron, Arial';
                }}
                QPushButton:hover {{
                    background: #FFFFFF;
                    color: #000000;
                }}
                QPushButton:pressed {{
                    background: #FFFF00;
                    color: #000000;
                }}
            """)

class SystemMonitor(QThread):
    """Background system monitoring"""
    update_signal = pyqtSignal(dict)
    
    def run(self):
        while True:
            self.msleep(1000)
            data = {
                'cpu': 25 + (len(str(self.msleep(1))) % 50),
                'memory': 40 + (len(str(self.msleep(1))) % 30),
                'status': 'ONLINE'
            }
            self.update_signal.emit(data)

class LCARS25thCenturyProper(QMainWindow):
    """Proper 25th Century LCARS Interface"""
    
    def __init__(self):
        super().__init__()
        
        # Set up window
        self.setWindowTitle("LCARS FRAMEWORK")
        self.showFullScreen()
        
        # Animation variables
        self.color_timer = QTimer(self)
        self.color_change_interval = 2500  # 2.5 seconds for better viewing
        self.current_color_index = 0
        self.button_colors = []
        
        # Star date timer
        self.star_date_timer = QTimer(self)
        
        # System monitor
        self.system_monitor = SystemMonitor()
        
        # Set up colors
        self.setup_colors()
        
        # Create interface
        self.create_interface()
        
        # Start animations
        self.start_color_animation()
        self.start_star_date_updates()
        self.start_system_monitoring()
        
        # Show window
        self.show()
        
    def setup_colors(self):
        """Set up LCARS colors"""
        self.era = LCARSEra.LCARS_25TH
        palette = get_era_palette(self.era)
        self.colors = palette.copy()
        self.button_colors = self.colors['button_colors'].copy()
        self.font_family = "Orbitron, Arial"
        
    def create_interface(self):
        """Create authentic LCARS interface"""
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout with LCARS structure
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top header bar
        self.create_header_bar(main_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout, 1)
        
        # Left sidebar
        self.create_left_sidebar(content_layout)
        
        # Center main area
        self.create_main_area(content_layout)
        
        # Right sidebar
        self.create_right_sidebar(content_layout)
        
        # Bottom status bar
        self.create_status_bar(main_layout)
        
        # Initialize buttons
        self.initialize_buttons()
        
    def create_header_bar(self, main_layout):
        """Create top header with LCARS styling"""
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['background']};
                border: none;
            }}
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Left panel made of buttons
        left_panel = QHBoxLayout()
        
        left_corner_btn = LCARSButton("", 0)
        left_corner_btn.setFixedWidth(100)
        left_corner_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.button_colors[0]};
                border: none;
                border-bottom-right-radius: 20px;
            }}
        """)
        left_panel.addWidget(left_corner_btn)
        
        # Small decorative buttons
        for i in range(3):
            deco_btn = LCARSButton("", i+1)
            deco_btn.setFixedSize(30, 40)
            deco_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+1)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            left_panel.addWidget(deco_btn)
            
        header_layout.addLayout(left_panel)
        
        # Main title
        title = QLabel("LCARS FRAMEWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 28px;
            font-weight: bold;
            font-family: '{self.font_family}';
            padding: 10px 20px;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(title, 1)
        
        # Star date and time
        datetime_panel = QVBoxLayout()
        self.star_date_label = QLabel()
        self.star_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.star_date_label.setStyleSheet(f"""
            color: {self.colors['alert_colors'][0]};
            font-size: 14px;
            font-weight: bold;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"""
            color: {self.button_colors[1]};
            font-size: 16px;
            font-weight: bold;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        
        datetime_panel.addWidget(self.star_date_label)
        datetime_panel.addWidget(self.time_label)
        header_layout.addLayout(datetime_panel)
        
        # Right panel made of buttons
        right_panel = QHBoxLayout()
        
        # Small decorative buttons
        for i in range(3):
            deco_btn = LCARSButton("", i+4)
            deco_btn.setFixedSize(30, 40)
            deco_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+4)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            right_panel.addWidget(deco_btn)
            
        right_corner_btn = LCARSButton("", 7)
        right_corner_btn.setFixedWidth(100)
        right_corner_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.button_colors[2]};
                border: none;
                border-bottom-left-radius: 20px;
            }}
        """)
        right_panel.addWidget(right_corner_btn)
        
        header_layout.addLayout(right_panel)
        
        main_layout.addWidget(header)
        
    def create_left_sidebar(self, content_layout):
        """Create left navigation sidebar made of buttons"""
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['background']};
                border: none;
            }}
        """)
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(5)
        
        # Status display made of buttons
        status_frame = QFrame()
        status_frame.setFixedHeight(120)
        status_frame.setStyleSheet("border: none;")
        
        status_layout = QVBoxLayout(status_frame)
        
        # Status header button
        status_header_btn = LCARSButton("SYSTEM STATUS", 8)
        status_header_btn.setFixedHeight(40)
        status_header_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['alert_colors'][0]};
                color: {self.colors['background']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
        """)
        status_layout.addWidget(status_header_btn)
        
        # Status display buttons
        status_info_layout = QHBoxLayout()
        for i in range(3):
            status_btn = LCARSButton("", 9+i)
            status_btn.setFixedSize(70, 30)
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[i%len(self.button_colors)]};
                    border: none;
                }}
            """)
            status_info_layout.addWidget(status_btn)
        status_layout.addLayout(status_info_layout)
        
        # System status text
        self.system_status = QLabel("ALL SYSTEMS ONLINE")
        self.system_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.system_status.setStyleSheet(f"""
            color: {self.colors['background']};
            font-size: 12px;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        status_layout.addWidget(self.system_status)
        
        left_layout.addWidget(status_frame)
        
        # Navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("MAIN MENU", 12),
            ("PROJECTS", 13),
            ("SIMULATION", 14),
            ("ANALYSIS", 15),
            ("DATA BANK", 16),
            ("SETTINGS", 17)
        ]
        
        for text, index in nav_items:
            btn = LCARSButton(text, index)
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda checked, idx=index: self.switch_mode(idx-12))
            self.nav_buttons.append(btn)
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        # Logout button
        logout_btn = LCARSButton("LOGOUT", 18)
        logout_btn.setFixedHeight(50)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.colors['alert_colors'][1]};
                color: {self.colors['text']};
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
        """)
        logout_btn.clicked.connect(self.close)
        left_layout.addWidget(logout_btn)
        
        content_layout.addWidget(left_panel)
        
    def create_main_area(self, content_layout):
        """Create main content area"""
        main_panel = QFrame()
        main_panel.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['background']};
                border: none;
            }}
        """)
        
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Content tabs
        self.content_tabs = QTabWidget()
        self.content_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background: {self.colors['background']};
                border: none;
            }}
            QTabBar::tab {{
                background: {self.button_colors[1]};
                color: {self.colors['text']};
                padding: 10px 20px;
                border: none;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
            QTabBar::tab:selected {{
                background: {self.button_colors[0]};
                color: {self.colors['background']};
            }}
        """)
        
        self.setup_content_tabs()
        main_layout.addWidget(self.content_tabs)
        
        content_layout.addWidget(main_panel, 1)
        
    def create_right_sidebar(self, content_layout):
        """Create right information sidebar made of buttons"""
        right_panel = QFrame()
        right_panel.setFixedWidth(200)
        right_panel.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['background']};
                border: none;
            }}
        """)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # System monitors header button
        monitor_header_btn = LCARSButton("SYSTEM MONITORS", 19)
        monitor_header_btn.setFixedHeight(40)
        monitor_header_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self.button_colors[3]};
                color: {self.colors['text']};
                border: none;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                font-family: '{self.font_family}';
            }}
        """)
        right_layout.addWidget(monitor_header_btn)
        
        # Monitor display buttons
        monitor_display_layout = QHBoxLayout()
        for i in range(2):
            monitor_btn = LCARSButton("", 20+i)
            monitor_btn.setFixedSize(90, 30)
            monitor_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+3)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            monitor_display_layout.addWidget(monitor_btn)
        right_layout.addLayout(monitor_display_layout)
        
        # CPU monitor
        cpu_label = QLabel("CPU USAGE")
        cpu_label.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 10px;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        right_layout.addWidget(cpu_label)
        
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {self.colors['text']};
                background: {self.colors['background']};
            }}
            QProgressBar::chunk {{
                background: {self.button_colors[0]};
                border-radius: 3px;
            }}
        """)
        right_layout.addWidget(self.cpu_bar)
        
        # Memory monitor
        mem_label = QLabel("MEMORY")
        mem_label.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 10px;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        right_layout.addWidget(mem_label)
        
        self.mem_bar = QProgressBar()
        self.mem_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {self.colors['text']};
                background: {self.colors['background']};
            }}
            QProgressBar::chunk {{
                background: {self.button_colors[1]};
                border-radius: 3px;
            }}
        """)
        right_layout.addWidget(self.mem_bar)
        
        # Additional monitor buttons
        for i in range(4):
            extra_btn = LCARSButton("", 22+i)
            extra_btn.setFixedSize(180, 25)
            extra_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+5)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            right_layout.addWidget(extra_btn)
        
        right_layout.addStretch()
        
        content_layout.addWidget(right_panel)
        
    def create_status_bar(self, main_layout):
        """Create bottom status bar made of buttons"""
        status_bar = QFrame()
        status_bar.setFixedHeight(40)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {self.colors['background']};
                border: none;
            }}
        """)
        
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        # Left status buttons
        left_status_layout = QHBoxLayout()
        for i in range(3):
            status_btn = LCARSButton("", 26+i)
            status_btn.setFixedSize(60, 30)
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+7)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            left_status_layout.addWidget(status_btn)
        
        status_layout.addLayout(left_status_layout)
        
        self.status_message = QLabel("LCARS SYSTEM READY")
        self.status_message.setStyleSheet(f"""
            color: {self.colors['alert_colors'][0]};
            font-size: 12px;
            font-weight: bold;
            font-family: '{self.font_family}';
            background: transparent;
            border: none;
        """)
        status_layout.addWidget(self.status_message)
        
        status_layout.addStretch()
        
        # Right status buttons
        right_status_layout = QHBoxLayout()
        for i in range(3):
            status_btn = LCARSButton("", 29+i)
            status_btn.setFixedSize(60, 30)
            status_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {self.button_colors[(i+8)%len(self.button_colors)]};
                    border: none;
                }}
            """)
            right_status_layout.addWidget(status_btn)
        
        status_layout.addLayout(right_status_layout)
        
        main_layout.addWidget(status_bar)
        
    def setup_content_tabs(self):
        """Setup content tabs"""
        # Main Menu tab
        main_tab = QWidget()
        main_layout = QGridLayout(main_tab)
        
        welcome_label = QLabel("WELCOME TO LCARS FRAMEWORK")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 24px;
            font-weight: bold;
            font-family: '{self.font_family}';
            padding: 20px;
            background: transparent;
            border: none;
        """)
        main_layout.addWidget(welcome_label, 0, 0, 1, 2)
        
        # Quick action buttons
        actions = [
            ("NEW PROJECT", 0, 1),
            ("OPEN PROJECT", 0, 2),
            ("SYSTEM SCAN", 1, 1),
            ("DATA ANALYSIS", 1, 2)
        ]
        
        for text, row, col in actions:
            btn = LCARSButton(text, row + col + 32)
            btn.clicked.connect(lambda checked, t=text: self.quick_action(t))
            main_layout.addWidget(btn, row + 1, col)
            
        self.content_tabs.addTab(main_tab, "MAIN MENU")
        
        # Projects tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        
        project_list = QListWidget()
        project_list.setStyleSheet(f"""
            QListWidget {{
                background: {self.colors['background']};
                border: none;
                color: {self.colors['text']};
                font-family: '{self.font_family}';
            }}
            QListWidget::item {{
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background: {self.button_colors[0]};
                color: {self.colors['background']};
            }}
        """)
        project_list.addItems([
            "PROJECT: ALPHA - SIMULATION",
            "PROJECT: BETA - ANALYSIS", 
            "PROJECT: GAMMA - DATA PROCESSING",
            "PROJECT: DELTA - QUANTUM COMPUTING"
        ])
        projects_layout.addWidget(project_list)
        
        self.content_tabs.addTab(projects_tab, "PROJECTS")
        
        # Simulation tab
        sim_tab = QWidget()
        sim_layout = QVBoxLayout(sim_tab)
        
        sim_control = QTextEdit()
        sim_control.setPlainText("SIMULATION CONTROL PANEL\n\nReady to initialize simulation parameters...")
        sim_control.setStyleSheet(f"""
            QTextEdit {{
                background: {self.colors['background']};
                border: none;
                color: {self.colors['text']};
                font-family: 'Courier New, monospace';
                font-size: 12px;
            }}
        """)
        sim_layout.addWidget(sim_control)
        
        self.content_tabs.addTab(sim_tab, "SIMULATION")
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        analysis_display = QTextEdit()
        analysis_display.setPlainText("DATA ANALYSIS MODULE\n\nAwaiting data input for analysis...")
        analysis_display.setStyleSheet(f"""
            QTextEdit {{
                background: {self.colors['background']};
                border: none;
                color: {self.colors['text']};
                font-family: 'Courier New, monospace';
                font-size: 12px;
            }}
        """)
        analysis_layout.addWidget(analysis_display)
        
        self.content_tabs.addTab(analysis_tab, "ANALYSIS")
        
    def initialize_buttons(self):
        """Initialize all LCARS buttons"""
        all_buttons = self.findChildren(LCARSButton)
        for i, btn in enumerate(all_buttons):
            btn.color_index = i % len(self.button_colors)
            btn.is_active = True
            btn.update_color(self.button_colors)
            
    def start_color_animation(self):
        """Start sequential color animation"""
        self.color_timer.timeout.connect(self.animate_colors)
        self.color_timer.start(self.color_change_interval)
        
    def animate_colors(self):
        """Animate colors sequentially"""
        # Rotate colors
        self.button_colors = self.button_colors[1:] + [self.button_colors[0]]
        
        # Update all buttons
        all_buttons = self.findChildren(LCARSButton)
        for btn in all_buttons:
            if btn.is_active:
                btn.update_color(self.button_colors)
                
    def start_star_date_updates(self):
        """Start star date updates"""
        self.update_star_date()
        self.star_date_timer.timeout.connect(self.update_star_date)
        self.star_date_timer.start(1000)
        
    def update_star_date(self):
        """Update star date and time"""
        current = QDateTime.currentDateTime()
        year = current.date().year()
        day_of_year = current.date().dayOfYear()
        
        star_date = 1000 * (year - 2323) + (day_of_year - 1) * 1000 / 365
        self.star_date_label.setText(f"STARDATE {star_date:.1f}")
        self.time_label.setText(current.toString("HH:mm:ss"))
        
    def start_system_monitoring(self):
        """Start system monitoring"""
        self.system_monitor.update_signal.connect(self.update_system_stats)
        self.system_monitor.start()
        
    def update_system_stats(self, data):
        """Update system statistics"""
        self.cpu_bar.setValue(data['cpu'])
        self.mem_bar.setValue(data['memory'])
        self.system_status.setText(f"STATUS: {data['status']}")
        
    def switch_mode(self, mode_index):
        """Switch to different mode"""
        mode_names = ["MAIN", "PROJECTS", "SIMULATION", "ANALYSIS", "DATA", "SETTINGS"]
        if mode_index < len(mode_names):
            self.content_tabs.setCurrentIndex(mode_index)
            self.status_message.setText(f"MODE: {mode_names[mode_index]}")
            
    def quick_action(self, action):
        """Handle quick actions"""
        self.status_message.setText(f"EXECUTING: {action}")
        # Here you can add actual functionality for each action

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = LCARS25thCenturyProper()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
