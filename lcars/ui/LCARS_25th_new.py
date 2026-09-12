"""
LCARS Interface - 25th Century Edition
Advanced LCARS interface with authentic color scheme from 25th century
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Додаємо корінь проекту до шляху Python
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame,
                           QTreeWidget, QTreeWidgetItem, QProgressBar, QTextEdit, QGridLayout)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt, QTimer, QSize, QDateTime, pyqtSignal, QThread
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color

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

class LCARS25thCentury(QMainWindow):
    """25th Century LCARS Interface with authentic color schemes"""
    
    def __init__(self, root_path: Path, selector=None):
        super().__init__()
        self.selector = selector
        
        # Animation variables
        self.color_timer = QTimer(self)
        self.color_index = 0
        self.color_change_interval = 2500  # 2.5 seconds for better viewing
        self.button_colors = []
        
        # Star date timer
        self.star_date_timer = QTimer(self)
        
        # System monitor
        self.system_monitor = SystemMonitor()
        
        # Set up window
        self.setup_window()
        self.setup_color_scheme()
        self.create_interface()
        
        # Start animations
        self.start_color_animation()
        self.start_star_date_updates()
        self.start_system_monitoring()
        
        # Show window
        self.show()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("LCARS FRAMEWORK")
        self.showFullScreen()

    def setup_color_scheme(self):
        """Set up LCARS colors"""
        self.era = LCARSEra.LCARS_25TH
        palette = get_era_palette(self.era)
        self.colors = palette.copy()
        self.button_colors = self.colors['button_colors'].copy()
        self.font_family = "Orbitron, Arial"
        
    def start_color_animation(self):
        """Start the color animation algorithm"""
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(self.color_change_interval)
        
    def update_colors(self):
        """Update colors using LCARS algorithms"""
        # Get new random colors from palette
        new_primary = get_random_button_color(self.era)
        new_secondary = get_random_button_color(self.era)
        new_accent = get_random_button_color(self.era)
        
        # Update the full stylesheet with new button colors
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {self.colors['background']};
                border: none;
            }}
            QWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: '{self.font_family}';
                font-weight: 500;
                padding: 8px;
                border-bottom: 2px solid {self.colors['panel_border']};
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
            }}
            QPushButton {{
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
                background: {new_primary};
                color: {self.colors['text']};
                min-height: 45px;
                outline: none;
            }}
            QPushButton:hover {{
                background: {new_secondary};
                color: {self.colors['background']};
                border: 2px solid {self.colors['panel_border']};
            }}
            QPushButton:pressed {{
                background: {new_accent};
                border: 2px solid {self.colors['panel_border']};
            }}
            QListWidget {{
                background: rgba(0, 0, 0, 0.8);
                border: 2px solid {self.colors['panel_border']};
                border-radius: 8px;
                color: {self.colors['text']};
                padding: 8px;
                selection-background-color: {new_primary};
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px;
                margin: 4px;
                border: 1px solid transparent;
                border-radius: 6px;
                background: rgba(0, 0, 0, 0.2);
            }}
            QListWidget::item:hover {{
                border: 1px solid {new_primary};
                background: rgba(255, 255, 255, 0.1);
            }}
            QListWidget::item:selected {{
                background: {new_secondary};
                color: {self.colors['background']};
                border: 2px solid {new_accent};
            }}
            QTabWidget::pane {{
                border: 2px solid {self.colors['panel_border']};
                border-radius: 8px;
                background: rgba(0, 0, 0, 0.8);
                padding: 4px;
            }}
            QTabBar::tab {{
                background: {new_secondary};
                color: {self.colors['text']};
                padding: 12px 24px;
                border: 1px solid {self.colors['panel_border']};
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
                font-weight: 600;
            }}
            QTabBar::tab:selected {{
                background: {new_primary};
                color: {self.colors['background']};
                border: 2px solid {new_accent};
            }}
            QProgressBar {{
                border: 1px solid {self.colors['panel_border']};
                border-radius: 5px;
                text-align: center;
                color: {self.colors['text']};
                background: rgba(0, 0, 0, 0.5);
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: {new_primary};
                border-radius: 4px;
            }}
        """)
        
    def create_interface(self):
        """Create authentic LCARS interface"""
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
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
        
        # Navigation buttons
        nav_items = [
            ("MAIN MENU", 0),
            ("PROJECTS", 1),
            ("SIMULATION", 2),
            ("ANALYSIS", 3),
            ("DATA BANK", 4),
            ("SETTINGS", 5)
        ]
        
        for text, index in nav_items:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda checked, idx=index: self.switch_mode(idx))
            left_layout.addWidget(btn)
            
        left_layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("LOGOUT")
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
        right_layout.addWidget(self.mem_bar)
        
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
            ("NEW PROJECT", 1, 0),
            ("OPEN PROJECT", 1, 1),
            ("SYSTEM SCAN", 2, 0),
            ("DATA ANALYSIS", 2, 1)
        ]
        
        for text, row, col in actions:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, t=text: self.quick_action(t))
            main_layout.addWidget(btn, row, col)
            
        self.content_tabs.addTab(main_tab, "MAIN MENU")
        
        # Projects tab
        projects_tab = QWidget()
        projects_layout = QVBoxLayout(projects_tab)
        
        project_list = QListWidget()
        project_list.addItems([
            "PROJECT: ALPHA - SIMULATION",
            "PROJECT: BETA - ANALYSIS", 
            "PROJECT: GAMMA - DATA PROCESSING",
            "PROJECT: DELTA - QUANTUM COMPUTING"
        ])
        projects_layout.addWidget(project_list)
        
        self.content_tabs.addTab(projects_tab, "PROJECTS")
        
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
        
    def switch_mode(self, mode_index):
        """Switch to different mode"""
        mode_names = ["MAIN", "PROJECTS", "SIMULATION", "ANALYSIS", "DATA", "SETTINGS"]
        if mode_index < len(mode_names):
            self.content_tabs.setCurrentIndex(mode_index)
            self.status_message.setText(f"MODE: {mode_names[mode_index]}")
            
    def quick_action(self, action):
        """Handle quick actions"""
        self.status_message.setText(f"EXECUTING: {action}")

def main():
    """Main entry point"""
    if True:
        print("Starting LCARS 25th Century...")
        app = QApplication(sys.argv)
        
        # Create project root path
        root_path = Path(__file__).parent.parent.parent
        print(f"Root path: {root_path}")
        
        # Create and show main window
        print("Creating LCARS window...")
        window = LCARS25thCentury(root_path)
        print("Window created, showing...")
        window.show()
        print("Window shown!")
        print("Starting app event loop...")
        
        # Start the application event loop
        sys.exit(app.exec())
        
    if False: # Removed except block
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    print("Starting LCARS 25th Century...")
    main()
