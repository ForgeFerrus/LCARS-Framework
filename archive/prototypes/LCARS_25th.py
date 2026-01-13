"""
LCARS Interface - 25th Century Edition
Future LCARS interface with holographic design from 25th century
"""

import sys
from pathlib import Path

# Додавання шляху до проекту для автономного запуску
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QGridLayout, QTreeWidget, QTreeWidgetItem, QApplication)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF, QRectF
import os
import logging
from pathlib import Path
from lcars.themes.lcars_palette import get_era_palette, LCARSEra
from lcars.core.project_manager import ProjectManager
from lcars.core.file_analyzer import FileAnalyzer

class LCARS25thCentury(QMainWindow):
    """25th Century LCARS Interface with authentic color schemes"""
    
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        # Determine project root
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        self.selector = selector
        
        # Initialize managers
        self.project_manager = ProjectManager(self.root_path)
        self.current_project = None
        
        # Initialize file analyzer
        self.file_analyzer = FileAnalyzer(self.root_path)
        
        # Set up window
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up authentic 25th century LCARS color scheme using palette"""
        # Use era palette directly
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        
        self.font_family = "Chakra Petch, Orbitron, Arial"

        # Set application-wide stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('background', '#000000')};
                border: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
            }}
            QLabel {{
                color: {self.colors.get('text', '#FFFFFF')};
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 5px;
                border-bottom: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
            }}
            QPushButton {{
                border: none;
                border-radius: 4px;
                padding: 15px;
                font-weight: bold;
                font-size: 14px;
                background-color: {self.colors.get('button_colors', ['#FF6733'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF6733'};
                color: {self.colors.get('background', '#000000')};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                color: {self.colors.get('background', '#000000')};
                border: 1px solid {self.colors.get('text', '#FFFFFF')};
            }}
            QPushButton:pressed {{
                background-color: {self.colors.get('button_colors', ['#66CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#66CCFF'};
            }}
            QListWidget {{
                background-color: rgba(0, 20, 40, 0.8);
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                border-radius: 4px;
                color: {self.colors.get('text', '#FFFFFF')};
                padding: 5px;
                selection-background-color: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
            }}
            QListWidget::item {{
                padding: 10px;
                margin: 2px;
                border: 1px solid transparent;
                border-radius: 2px;
            }}
            QListWidget::item:hover {{
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                background-color: rgba(255, 103, 83, 0.1);
            }}
            QListWidget::item:selected {{
                background-color: rgba(255, 103, 83, 0.2);
                color: {self.colors.get('text', '#FFFFFF')};
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                border-radius: 4px;
                background-color: rgba(0, 20, 40, 0.8);
            }}
            QTabBar::tab {{
                background-color: {self.colors.get('background', '#000000')};
                color: {self.colors.get('text', '#FFFFFF')};
                padding: 10px 20px;
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                color: {self.colors.get('background', '#000000')};
            }}
            QScrollBar:vertical {{
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                background: {self.colors['background']};
                width: 10px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                border-radius: 3px;
            }}
            QTableWidget {{
                background-color: rgba(0, 20, 40, 0.8);
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                gridline-color: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                color: {self.colors.get('text', '#FFFFFF')};
                selection-background-color: rgba(255, 103, 83, 0.2);
            }}
            QHeaderView::section {{
                background-color: {self.colors.get('button_colors', ['#FF6733'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF6733'};
                color: {self.colors.get('background', '#000000')};
                padding: 5px;
                border: none;
            }}
        """)
        
    def create_layouts(self):
        """Create main layout structure"""
        # Left panel (navigation)
        self.left_panel = QWidget()
        self.left_panel.setFixedWidth(300)
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)
        
        # Main content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
        
        # Add to main layout
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addWidget(self.content_area)
        
    def create_widgets(self):
        """Create and set up all widgets"""
        self.create_left_panel()
        self.create_header()
        self.create_project_list()
        self.create_content_area()
        self.create_footer()
        
    def create_left_panel(self):
        """Create 25th century LCARS navigation panel"""
        # Top quantum core status section
        status_widget = QWidget()
        status_widget.setFixedHeight(200)
        status_widget.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors.get('button_colors', ['#FF3333'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF3333'}, stop:1 {self.colors.get('button_colors', ['#66CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#66CCFF'});
            border-top-right-radius: 40px;
            border-bottom-right-radius: 40px;
            border: 1px solid {self.colors.get('button_colors', ['#3366CC'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#3366CC'};
        """)
        
        status_layout = QVBoxLayout()
        
        # Create holographic status display
        status_header = QLabel("LCARS 25TH")
        status_header.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 24px;
            font-family: '{self.font_family}';
            font-weight: bold;
            padding: 5px;
            border: none;
            background: transparent;
        """)
        status_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_text = QLabel("QUANTUM CORE\nACTIVE")
        status_text.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 20px;
            font-family: '{self.font_family}';
            font-weight: bold;
            padding: 5px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 4px;
            background: rgba(0, 0, 0, 0.3);
        """)
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_header)
        status_layout.addWidget(status_text)
        status_widget.setLayout(status_layout)
        self.left_layout.addWidget(status_widget)
        
        # Navigation buttons - holographic style
        self.create_nav_button("PROJECTS", self.show_projects)
        self.create_nav_button("SIMULATION", self.show_simulation)
        self.create_nav_button("ANALYSIS", self.show_analysis)
        self.create_nav_button("SETTINGS", self.show_settings)
        
        # Add spacer at bottom
        self.left_layout.addStretch()
        
    def create_nav_button(self, text, slot):
        """Create a holographic LCARS navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(60)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors.get('button_colors', ['#FF6733'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF6733'}, stop:1 {self.colors.get('button_colors', ['#66CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#66CCFF'});
                color: {self.colors.get('background', '#000000')};
                border: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                text-align: left;
                padding: 5px 15px;
                font-family: '{self.font_family}';
                font-size: 16px;
                font-weight: bold;
                border-radius: 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'}, stop:1 {self.colors.get('button_colors', ['#FF3333'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF3333'});
                border-color: {self.colors.get('text', '#FFFFFF')};
            }}
        """)
        btn.clicked.connect(slot)
        self.left_layout.addWidget(btn)
        
    def create_header(self):
        """Create holographic LCARS header"""
        header = QFrame()
        header.setFixedHeight(100)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)
        
        # Create left corner element - holographic
        corner = QWidget()
        corner.setFixedWidth(150)
        corner.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors.get('button_colors', ['#FF3333'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF3333'}, stop:1 {self.colors.get('button_colors', ['#66CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#66CCFF'});
            border-bottom-right-radius: 40px;
            border: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
        """)
        header_layout.addWidget(corner)
        
        # Create title
        title = QLabel("LCARS FRAMEWORK")
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            font-family: '{self.font_family}';
            color: {self.colors.get('background', '#000000')};
            padding: 10px;
            border: none;
        """)
        header_layout.addWidget(title)
        
        # Create right status panel
        status_panel = QWidget()
        status_layout = QVBoxLayout()
        
        # Add time display
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            font-family: '{self.font_family}';
            color: {self.colors.get('text', '#FFFFFF')};
            padding: 5px;
            border-radius: 4px;
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
        """)
        status_layout.addWidget(self.time_label)
        
        # Add system status
        system_status = QLabel("QUANTUM SYSTEMS ONLINE")
        system_status.setStyleSheet(f"""
            font-size: 16px;
            font-family: '{self.font_family}';
            color: {self.colors.get('text', '#FFFFFF')};
            border: none;
        """)
        status_layout.addWidget(system_status)
        
        status_panel.setLayout(status_layout)
        header_layout.addWidget(status_panel)
        
        # Add header buttons
        header_buttons = self.create_header_buttons()
        header_layout.addLayout(header_buttons)
        
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        
        # Set up timer to update time
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
        return header
        
    def create_project_list(self):
        """Create project list with file browser"""
        # Project list
        self.project_list = QListWidget()
        self.update_project_list()
        
        # Project details
        self.project_info = QWidget()
        info_layout = QVBoxLayout()
        
        # Header
        self.project_title = QLabel("No Project Selected")
        self.project_title.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors.get('button_colors', ['#66CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#66CCFF'};
            padding: 10px;
            border-bottom: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
        """)
        info_layout.addWidget(self.project_title)
        
        # Path
        path_widget = QWidget()
        path_layout = QHBoxLayout()
        path_label = QLabel("Location:")
        path_label.setStyleSheet(f"color: {self.colors.get('button_colors', ['#FF6733'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF6733'};")
        self.project_path = QLabel()
        self.project_path.setStyleSheet(f"color: {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};")
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.project_path)
        path_widget.setLayout(path_layout)
        info_layout.addWidget(path_widget)
        
        # Description
        desc_scroll = QScrollArea()
        desc_scroll.setWidgetResizable(True)
        desc_scroll.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                border-radius: 4px;
                background: {self.colors['background']};
            }}
        """)
        self.project_description = QLabel()
        self.project_description.setWordWrap(True)
        self.project_description.setStyleSheet(f"""
            QLabel {{
                color: {self.colors.get('text', '#FFFFFF')};
                padding: 10px;
                background: transparent;
            }}
        """)
        desc_scroll.setWidget(self.project_description)
        info_layout.addWidget(desc_scroll)
        
        # File browser
        self.create_file_browser()
        info_layout.addWidget(self.file_browser)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.run_button = QPushButton("Run Project")
        self.run_button.clicked.connect(self.run_selected_project)
        self.run_button.setEnabled(False)
        button_layout.addWidget(self.run_button)
        
        self.analyze_button = QPushButton("Analyze Data")
        self.analyze_button.clicked.connect(self.analyze_selected_project)
        self.analyze_button.setEnabled(False)
        button_layout.addWidget(self.analyze_button)
        
        info_layout.addLayout(button_layout)
        self.project_info.setLayout(info_layout)
        
    def create_content_area(self):
        """Create main content area"""
        self.content_stack = QTabWidget()
        
        # Add tabs
        self.setup_project_tab()
        self.setup_simulation_tab()
        self.setup_analysis_tab()
        
        self.content_layout.addWidget(self.content_stack)
        
    def create_footer(self):
        """Create footer with status information"""
        footer = QFrame()
        footer.setFixedHeight(40)
        footer_layout = QHBoxLayout()
        
        self.status_label = QLabel("System Status: Online")
        self.status_label.setStyleSheet(f"color: {self.colors.get('button_colors', ['#37A6D1'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#37A6D1'};")
        footer_layout.addWidget(self.status_label)
        
        footer.setLayout(footer_layout)
        self.content_layout.addWidget(footer)
        return footer
        
    def setup_project_tab(self):
        """Set up project management tab"""
        project_tab = QWidget()
        layout = QHBoxLayout()
        
        # Add project list and info
        list_container = QWidget()
        list_layout = QVBoxLayout()
        header_label = QLabel("Available Projects")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        list_layout.addWidget(header_label)
        list_layout.addWidget(self.project_list)
        list_container.setLayout(list_layout)
        
        layout.addWidget(list_container)
        layout.addWidget(self.project_info)
        
        project_tab.setLayout(layout)
        self.content_stack.addTab(project_tab, "Projects")
        
    def setup_simulation_tab(self):
        """Set up simulation control tab"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        # Add simulation controls
        self.simulation_status = QLabel("No simulation running")
        layout.addWidget(self.simulation_status)
        
        simulation_tab.setLayout(layout)
        self.content_stack.addTab(simulation_tab, "Simulation")
        
    def setup_analysis_tab(self):
        """Set up data analysis tab"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        # Add analysis tools
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Energy", "Counts", "Particle"])
        layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(layout)
        self.content_stack.addTab(analysis_tab, "Analysis")
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
    def update_project_list(self):
        """Update list of available projects"""
        self.project_list.clear()
        for project_name in self.project_manager.get_project_names():
            self.project_list.addItem(project_name)
            
    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if not current:
            return
            
        project_name = current.text()
        self.current_project = self.project_manager.get_project(project_name)
        
        if self.current_project:
            # Create file analyzer
            self.current_analyzer = self.FileAnalyzer(self.current_project.path)
            
            # Update project info
            self.project_title.setText(self.current_project.name)
            self.project_path.setText(str(self.current_project.path))
            
            # Get and display README
            readme_content = self.current_analyzer.get_readme_content()
            self.project_description.setText(readme_content)
            
            # Get project files
            source_files = self.current_analyzer.get_source_files()
            data_files = self.current_analyzer.get_data_files()
            macro_files = self.current_analyzer.get_macro_files()
            
            # Update file lists
            self.update_file_lists(source_files, data_files, macro_files)
            
            # Enable buttons based on capabilities
            has_exe = self.current_project.executable is not None
            self.run_button.setEnabled(has_exe)
            self.analyze_button.setEnabled(bool(data_files))
            
    def create_file_browser(self):
        """Create file browser"""
        self.file_browser = QWidget()
        layout = QVBoxLayout()
        
        # Create tree structure
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type", "Size"])
        layout.addWidget(self.file_tree)
        
        self.file_browser.setLayout(layout)
        
    def update_file_lists(self, source_files, data_files, macro_files):
        """Update file lists"""
        # Clear existing items
        self.file_tree.clear()
        
        # Add source files
        for file in source_files:
            item = QTreeWidgetItem([file.name, "Source", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
        # Add data files
        for file in data_files:
            item = QTreeWidgetItem([file.name, "Data", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
        # Add macro files
        for file in macro_files:
            item = QTreeWidgetItem([file.name, "Macro", str(file.stat().st_size)])
            self.file_tree.addTopLevelItem(item)
            
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
                self.status_label.setStyleSheet(f"color: {self.colors['warning']};")
                return
                
            # Switch to analysis tab
            self.content_stack.setCurrentIndex(2)
            
        except Exception as e:
            self.status_label.setText(f"Analysis error: {str(e)}")
            self.status_label.setStyleSheet(f"color: {self.colors['warning']};")
            
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
        """Create header action buttons"""
        button_layout = QHBoxLayout()
        
        # Back button (plain text - no emoji)
        back_btn = QPushButton("BACK")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('background', '#000000')};
                background-color: {self.colors.get('button_colors', ['#3366CC'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#3366CC'};
                border: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 8px 16px;
            }}
        """)
        back_btn.clicked.connect(self.return_to_selector)
        button_layout.addWidget(back_btn)

        # Lock button (plain text)
        lock_btn = QPushButton("LOCK")
        lock_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('background', '#000000')};
                background-color: {self.colors.get('button_colors', ['#FF0000'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#FF0000'};
                border: 2px solid {self.colors.get('button_colors', ['#FF8C42'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#FF8C42'};
                font-family: '{self.font_family}';
                font-weight: bold;
                padding: 8px 16px;
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

def main():
    app = QApplication(sys.argv)
    
    # Generic root path
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    
    interface = LCARS25thCentury(root_path)
    interface.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
