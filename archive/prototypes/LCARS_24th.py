import os
import sys
import logging
from pathlib import Path

# Додавання шляху до проекту для автономного запуску
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QTreeWidget,
                           QTreeWidgetItem, QMainWindow, QApplication)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt, QTimer, QSize
from lcars.core.analysis import SpectraAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType
from lcars.core.project_manager import ProjectManager, ProjectInfo
from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, get_button_color_cycle, LCARSEra
# Theme class is not used or moved to lcars_palette functionality
from lcars.core.file_analyzer import FileAnalyzer

class LCARS24thCentury(QMainWindow):
    """24th Century LCARS Interface with traditional color scheme"""
    
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        # Determine project root
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        self.selector = selector
        
        # Lock state
        self.is_locked = False
        
        # Initialize managers
        self.project_manager = ProjectManager(self.root_path)
        self.current_project = None
        
        # Initialize file analyzer
        from lcars.core.file_analyzer import FileAnalyzer
        self.file_analyzer = FileAnalyzer(self.root_path)
        
        # Set up window
        self.setup_window()
        self.setup_colors()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_colors(self):
        """Set a classic 24th-century LCARS palette using theme system"""
        # Use era palette directly
        self.colors = get_era_palette(LCARSEra.LCARS_24TH)
        # No conversion needed - use palette as-is
        
        def get_random_button_color(self):
            """Get random button color from theme palette"""
            if hasattr(self, 'colors') and self.colors:
                import random
                button_keys = [k for k in self.colors.keys() if k.startswith('btn')]
                if button_keys:
                    return self.colors[random.choice(button_keys)]
            
            # Fallback to era system
            return self.get_random_button_color()
        
        # Apply base stylesheet with proper LCARS styling
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
            QLabel {{
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 18px;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                color: #000000;
                text-align: left;
                padding: 8px 20px;
                border-radius: 15px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 20px;
                font-weight: bold;
                border: none;
                min-height: 35px;
                max-height: 35px;
            }}
            QTableWidget {{
                background-color: rgba(0, 0, 0, 0.8);
                border: 1px solid {self.colors.get('button_colors', ['#FFCC66'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FFCC66'};
                gridline-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 16px;
            }}
            QHeaderView::section {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                color: {self.colors.get('txt', '#FFFFFF')};
                padding: 8px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 18px;
                font-weight: bold;
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors.get('button_colors', ['#FFCC66'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FFCC66'};
                background: {self.colors.get('bg', '#000000')};
            }}
            QTabBar::tab {{
                background: {self.colors.get('button_colors', ['#664466'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#664466'};
                color: {self.colors.get('txt', '#FFFFFF')};
                padding: 12px 24px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 18px;
                min-height: 40px;
            }}
        """)
        
    def create_layouts(self):
        """Create proper LCARS layout with panels and contours"""
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        
        # Header panel with LCARS contour
        self.header_panel = QFrame()
        self.header_panel.setFixedHeight(120)
        self.header_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
        """)
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(0)
        self.header_panel.setLayout(self.header_layout)
        
        # Main content area with LCARS panel structure
        self.content_panel = QFrame()
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_panel.setLayout(self.content_layout)
        self.content_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
        """)
        
        # Left sidebar panel with LCARS contour
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(350)
        self.left_panel.setObjectName("leftSidebar")
        self.left_panel.setStyleSheet(f"""
            QFrame#leftSidebar {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
        """)
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(15, 15, 15, 15)
        self.left_layout.setSpacing(10)
        self.left_panel.setLayout(self.left_layout)
        
        # Main display area with LCARS border contour
        self.main_display = QFrame()
        self.main_display.setObjectName("mainDisplay")
        self.main_display.setStyleSheet(f"""
            QFrame#mainDisplay {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
                border-radius: 0px;
            }}
        """)
        self.display_layout = QVBoxLayout()
        self.display_layout.setContentsMargins(20, 20, 20, 20)
        self.display_layout.setSpacing(15)
        self.main_display.setLayout(self.display_layout)
        
        # Right sidebar panel with LCARS contour
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(200)
        self.right_panel.setObjectName("rightSidebar")
        self.right_panel.setStyleSheet(f"""
            QFrame#rightSidebar {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
        """)
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(15, 15, 15, 15)
        self.right_layout.setSpacing(10)
        self.right_panel.setLayout(self.right_layout)
        
        # Footer panel with LCARS contour
        self.footer_panel = QFrame()
        self.footer_panel.setFixedHeight(60)
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(20, 0, 20, 0)
        self.footer_panel.setLayout(self.footer_layout)
        self.footer_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
            }}
        """)
        
    def create_widgets(self):
        """Create and set up all widgets"""
        self.create_header()
        self.create_left_panel()
        self.create_main_display()
        self.create_right_panel()
        self.create_footer()
        
        # Assemble the layout
        self.content_layout.addWidget(self.left_panel)
        self.content_layout.addWidget(self.main_display)
        self.content_layout.addWidget(self.right_panel)
        
        self.main_layout.addWidget(self.header_panel)
        self.main_layout.addWidget(self.content_panel)
        self.main_layout.addWidget(self.footer_panel)
        
    def create_left_panel(self):
        """Create traditional LCARS navigation panel with proper buttons and contours"""
        # Status display at top with LCARS contour
        status_widget = QFrame()
        status_widget.setFixedHeight(180)
        status_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#FFCC66'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FFCC66'};
                border: none;
                border-radius: 20px;
            }}
        """)
        status_layout = QVBoxLayout()
        
        status_header = QLabel("LCARS 24TH")
        status_header.setStyleSheet(f"""
            color: {self.colors.get('bg', '#000000')};
            font-size: 28px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
            background: transparent;
        """)
        status_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_text = QLabel("CORE SYSTEMS\nOPERATIONAL")
        status_text.setStyleSheet(f"""
            color: {self.colors.get('bg', '#000000')};
            font-size: 20px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 8px;
            background: transparent;
        """)
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_header)
        status_layout.addWidget(status_text)
        status_widget.setLayout(status_layout)
        self.left_layout.addWidget(status_widget)
        
        # LCARS navigation buttons with contours
        nav_buttons = [
            ("PROJECTS", self.show_projects),
            ("SIMULATION", self.show_simulation),
            ("ANALYSIS", self.show_analysis),
            ("SETTINGS", self.show_settings)
        ]
        
        for text, slot in nav_buttons:
            btn = self.create_lcars_button(text, slot)
            self.left_layout.addWidget(btn)
        
        # Add spacer at bottom
        self.left_layout.addStretch()
        
    def create_lcars_button(self, text, slot):
        """Create proper LCARS style button with thick contour and functionality"""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                text-align: center;
                padding: 10px 20px;
                border-radius: 25px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 18px;
                font-weight: bold;
                border: none;
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
            }}
            QPushButton:hover {{
                background-color: {self.colors.get('button_colors', ['#FFCC66'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FFCC66'};
            }}
            QPushButton:pressed {{
                background-color: {self.colors.get('button_colors', ['#9999FF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#9999FF'};
            }}
        """)
        
        # Connect the button to make it functional
        if slot:
            btn.clicked.connect(slot)
        
        return btn
        
    def create_header(self):
        """Create LCARS header with proper styling and thick contours"""
        # Left corner element with thick contour
        corner = QWidget()
        corner.setFixedWidth(180)
        corner.setStyleSheet(f"""
            QWidget {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-top-right-radius: 30px;
                border-bottom-right-radius: 30px;
                border-left: none;
            }}
        """)
        self.header_layout.addWidget(corner)
        
        # Title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            font-size: 42px;
            font-weight: bold;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors.get('txt', '#FFFFFF')};
            padding: 15px;
            border: none;
            background: transparent;
        """)
        self.header_layout.addWidget(title)
        
        # Time display with thick contour
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors.get('bg', '#000000')};
            padding: 10px;
            border: none;
            background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
            border-radius: 10px;
        """)
        self.header_layout.addWidget(self.time_label)
        
        # System status
        system_status = QLabel("SYSTEMS OPERATIONAL")
        system_status.setStyleSheet(f"""
            font-size: 20px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors.get('txt', '#FFFFFF')};
            border: none;
            background: transparent;
        """)
        self.header_layout.addWidget(system_status)
        
        # Add stretch and header buttons
        self.header_layout.addStretch()
        header_buttons = self.create_header_buttons()
        self.header_layout.addLayout(header_buttons)
        
        # Set up timer to update time
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
    def create_main_display(self):
        """Create main display area with content and thick contours"""
        # Create tab widget for main content
        self.content_stack = QTabWidget()
        self.content_stack.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {self.colors.get('bg', '#000000')};
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
            }}
            QTabBar::tab {{
                background: {self.colors.get('button_colors', ['#664466'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#664466'};
                color: {self.colors.get('txt', '#FFFFFF')};
                padding: 12px 24px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 18px;
                min-height: 40px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }}
            QTabBar::tab:selected {{
                background: {self.colors.get('button_colors', ['#664466'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#664466'};
            }}
        """)
        
        # Add tabs
        self.setup_project_tab()
        self.setup_simulation_tab()
        self.setup_analysis_tab()
        
        self.display_layout.addWidget(self.content_stack)
        
    def create_right_panel(self):
        """Create right sidebar with status and controls with thick contours"""
        # Status display with thick contour
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
            }}
        """)
        status_layout = QVBoxLayout()
        
        status_title = QLabel("SYSTEM STATUS")
        status_title.setStyleSheet(f"""
            color: {self.colors.get('bg', '#000000')};
            font-size: 16px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 8px;
            background: transparent;
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("ONLINE")
        self.status_label.setStyleSheet(f"""
            color: {self.colors.get('bg', '#000000')};
            font-size: 14px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 5px;
            background: transparent;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_label)
        status_frame.setLayout(status_layout)
        self.right_layout.addWidget(status_frame)
        
        # Quick actions with thick contour
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
            }}
        """)
        actions_layout = QVBoxLayout()
        
        actions_title = QLabel("QUICK ACTIONS")
        actions_title.setStyleSheet(f"""
            color: {self.colors.get('bg', '#000000')};
            font-size: 16px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 8px;
            background: transparent;
        """)
        actions_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        refresh_btn = QPushButton("REFRESH")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 10px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
            }}
        """)
        
        actions_layout.addWidget(actions_title)
        actions_layout.addWidget(refresh_btn)
        actions_frame.setLayout(actions_layout)
        self.right_layout.addWidget(actions_frame)
        
        self.right_layout.addStretch()
        
    def create_footer(self):
        """Create LCARS footer with controls and thick contours"""
        # Status label
        status_text = QLabel("SYSTEM READY")
        status_text.setStyleSheet(f"""
            color: {self.colors.get('button_colors', ['#664466'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#664466'};
            font-size: 18px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
        """)
        self.footer_layout.addWidget(status_text)
        
        # Add stretch
        self.footer_layout.addStretch()
        
        # Control buttons with thick contours
        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 16px;
                min-width: 100px;
            }}
        """)
        back_btn.clicked.connect(self.return_to_selector)
        self.footer_layout.addWidget(back_btn)
        
        lock_btn = QPushButton("LOCK")
        lock_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 16px;
                min-width: 100px;
            }}
        """)
        lock_btn.clicked.connect(self.lock_interface)
        self.footer_layout.addWidget(lock_btn)
        
    def setup_project_tab(self):
        """Set up project management tab"""
        project_tab = QWidget()
        layout = QHBoxLayout()
        
        # Create project list
        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 14px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: none;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                color: {self.colors.get('txt', '#FFFFFF')};
            }}
        """)
        self.update_project_list()
        
        # Project details panel
        details_frame = QFrame()
        details_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
                border-radius: 10px;
            }}
        """)
        details_layout = QVBoxLayout()
        
        self.project_title = QLabel("No Project Selected")
        self.project_title.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors.get('txt', '#FFFFFF')};
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
            background: transparent;
        """)
        details_layout.addWidget(self.project_title)
        
        self.project_path = QLabel("")
        self.project_path.setStyleSheet(f"""
            font-size: 16px;
            color: {self.colors.get('button_colors', ['#664466'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#664466'};
            font-family: 'Swiss 911', 'Arial', sans-serif;
        """)
        details_layout.addWidget(self.project_path)
        
        # Action buttons
        button_frame = QFrame()
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("RUN")
        self.run_button.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 16px;
                min-width: 100px;
            }}
        """)
        self.run_button.setEnabled(False)
        
        self.analyze_button = QPushButton("ANALYZE")
        self.analyze_button.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                border: none;
                border-radius: 15px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 8px 16px;
                min-width: 100px;
            }}
        """)
        self.analyze_button.setEnabled(False)
        
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.analyze_button)
        button_frame.setLayout(button_layout)
        details_layout.addWidget(button_frame)
        
        details_frame.setLayout(details_layout)
        
        # Add to layout
        list_container = QFrame()
        list_container.setFixedWidth(300)
        list_layout = QVBoxLayout()
        list_header = QLabel("PROJECTS")
        list_header.setStyleSheet(f"""
            color: {self.colors.get('txt', '#FFFFFF')};
            font-size: 20px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
        """)
        list_layout.addWidget(list_header)
        list_layout.addWidget(self.project_list)
        list_container.setLayout(list_layout)
        
        layout.addWidget(list_container)
        layout.addWidget(details_frame)
        
        project_tab.setLayout(layout)
        self.content_stack.addTab(project_tab, "PROJECTS")
        
    def setup_simulation_tab(self):
        """Set up simulation control tab"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        self.simulation_status = QLabel("SIMULATION READY")
        self.simulation_status.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors.get('txt', '#FFFFFF')};
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 20px;
        """)
        self.simulation_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.simulation_status)
        
        simulation_tab.setLayout(layout)
        self.content_stack.addTab(simulation_tab, "SIMULATION")
        
    def setup_analysis_tab(self):
        """Set up data analysis tab"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["ENERGY", "COUNTS", "PARTICLE"])
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors.get('bg', '#000000')};
                border: none;
                gridline-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                color: {self.colors.get('txt', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 16px;
            }}
            QHeaderView::section {{
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                color: {self.colors.get('txt', '#FFFFFF')};
                padding: 8px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(layout)
        self.content_stack.addTab(analysis_tab, "ANALYSIS")
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        self.run_button.clicked.connect(self.run_selected_project)
        self.analyze_button.clicked.connect(self.analyze_selected_project)
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
    def update_project_list(self):
        """Update the list of Geant4 projects"""
        try:
            self.project_list.clear()
            projects = self.project_manager.get_all_projects()
            for project in projects:
                self.project_list.addItem(project.name)
        except Exception as e:
            print(f"Error refreshing projects: {e}")
        
    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if not current:
            return
            
        project_name = current.text()
        self.current_project = self.project_manager.get_project(project_name)
        
        if self.current_project:
            # Create file analyzer
            self.current_analyzer = FileAnalyzer(self.current_project.path)
            
            # Update project info
            self.project_title.setText(self.current_project.name)
            self.project_path.setText(str(self.current_project.path))
            
            # Get and display README
            readme_content = self.current_analyzer.get_readme_content()
            self.project_description.setText(readme_content)
            
            # Enable buttons based on capabilities
            has_exe = self.current_project.executable is not None
            self.run_button.setEnabled(has_exe)
            self.analyze_button.setEnabled(bool(self.current_analyzer.get_data_files()))
            
    def run_selected_project(self):
        """Run selected project"""
        if not self.current_project:
            return
            
        try:
            self.status_label.setText(f"Running {self.current_project.name}...")
            # Add actual project execution logic here
            QMessageBox.information(self, "Project Run", 
                                  f"Project '{self.current_project.name}' would be executed here.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run project: {str(e)}")
            
    def analyze_selected_project(self):
        """Analyze selected project's data"""
        if not self.current_project:
            return
            
        try:
            # Get analysis configuration
            config = self.current_analyzer.get_analysis_configuration()
            
            # Process data files
            data_files = self.current_analyzer.get_data_files()
            if not data_files:
                self.status_label.setText("No data files found")
                self.status_label.setStyleSheet(f"color: {get_random_button_color()};")
                return
                
            # Switch to analysis tab
            self.content_stack.setCurrentIndex(2)
            
        except Exception as e:
            self.status_label.setText(f"Analysis error: {str(e)}")
            self.status_label.setStyleSheet(f"color: {get_random_button_color()};")
            
    def show_projects(self):
        """Switch to projects tab"""
        self.content_stack.setCurrentIndex(0)
        
    def show_simulation(self):
        """Switch to simulation tab"""
        self.content_stack.setCurrentIndex(1)
        
    def show_analysis(self):
        """Switch to analysis tab"""
        self.content_stack.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", 
                              "Settings module not yet implemented.")
                              
    def create_header_buttons(self):
        """Create header action buttons using palette system"""
        button_layout = QHBoxLayout()
        
        # Back button
        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                font-family: 'LCARS', 'Arial';
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 15px;
                border: none;
            }}
        """)
        back_btn.clicked.connect(self.return_to_selector)
        button_layout.addWidget(back_btn)

        # Lock button
        lock_btn = QPushButton("LOCK")
        lock_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('txt', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#FF9900'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF9900'};
                font-family: 'LCARS', 'Arial';
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 15px;
                border: none;
            }}
        """)
        lock_btn.clicked.connect(self.lock_interface)
        button_layout.addWidget(lock_btn)
        
        # Add stretch to push buttons to the right
        button_layout.addStretch()
        
        return button_layout
            
    def return_to_selector(self):
        """Return to interface selector"""
        if self.selector:
            self.selector.show()
            self.close()
            
    def lock_interface(self):
        """Lock interface (simplified)"""
        QMessageBox.information(self, "Lock", "Interface lock not yet implemented.")
    
    def show_projects(self):
        """Show projects tab"""
        self.content_stack.setCurrentIndex(0)
        self.status_label.setText("PROJECTS")
    
    def show_simulation(self):
        """Show simulation tab"""
        self.content_stack.setCurrentIndex(1)
        self.status_label.setText("SIMULATION")
    
    def show_analysis(self):
        """Show analysis tab"""
        self.content_stack.setCurrentIndex(2)
        self.status_label.setText("ANALYSIS")
    
    def show_settings(self):
        """Show settings tab"""
        # Add settings tab if not exists
        if self.content_stack.count() < 4:
            settings_tab = QWidget()
            settings_layout = QVBoxLayout()
            settings_label = QLabel("SETTINGS TAB\n\nConfiguration options coming soon...")
            settings_label.setStyleSheet(f"""
                color: {self.colors.get('txt', '#FFFFFF')};
                font-size: 24px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                padding: 50px;
            """)
            settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            settings_layout.addWidget(settings_label)
            settings_tab.setLayout(settings_layout)
            self.content_stack.addTab(settings_tab, "SETTINGS")
        self.content_stack.setCurrentIndex(3)
        self.status_label.setText("SETTINGS")

def main():
    app = QApplication(sys.argv)
    
    # Generic root path
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    
    window = LCARS24thCentury(root_path=root_path)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
