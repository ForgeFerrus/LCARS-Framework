"""
LCARS Interface - 25th Century Edition
Clean, minimal LCARS interface with authentic color scheme
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QListWidget, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from lcars.core.project_manager import ProjectManager
from lcars.core.file_analyzer import FileAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType

class LCARS25thCentury(QMainWindow):
    """25th Century LCARS Interface - Clean and Essential"""

    def __init__(self, root_path: Path, selector=None):
        super().__init__()
        self.selector = selector
        self.project_manager = ProjectManager(root_path)
        self.current_project = None
        self.current_simulation = None
        
        # Set up window
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up main window properties"""
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up authentic 25th century LCARS color scheme using theme system"""
        from lcars.themes.lcars_theme import get_theme_by_name
        
        # Use theme system instead of direct palette
        self.theme = get_theme_by_name('lcars_25th')
        self.colors = self.theme.colors
        
        # Simple clean stylesheet using theme colors directly
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Chakra Petch', 'Orbitron', 'Arial';
                font-weight: bold;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {self.colors['button_colors'][0]};
                color: {self.colors['text']};
                font-weight: bold;
                font-size: 16px;
                padding: 15px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_colors'][1]};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['button_colors'][2]};
            }}
            QListWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['button_colors'][0]};
                color: {self.colors['text']};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 10px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['button_colors'][1]};
                color: {self.colors['text']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['button_colors'][0]};
                background-color: {self.colors['background']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                padding: 10px 20px;
                border: 1px solid {self.colors['button_colors'][0]};
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['button_colors'][0]};
                color: {self.colors['text']};
            }}
            QTableWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['button_colors'][0]};
                color: {self.colors['text']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['button_colors'][0]};
                color: {self.colors['text']};
                padding: 5px;
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
        self.create_header()
        self.create_navigation()
        self.create_content_area()
        
    def create_header(self):
        """Create header with title and stardate"""
        header = QWidget()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel("LCARS 25TH CENTURY")
        title.setStyleSheet(f"""
            font-size: 32px;
            color: {self.colors['text']};
            padding: 10px;
        """)
        header_layout.addWidget(title)
        
        # Stardate
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['button_colors'][2]};
            padding: 10px;
        """)
        header_layout.addWidget(self.time_label)
        
        header.setLayout(header_layout)
        self.content_layout.addWidget(header)
        
        # Update timer
        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        
    def create_navigation(self):
        """Create navigation panel"""
        # Status
        status = QLabel("QUANTUM CORE ONLINE")
        status.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][0]};
            color: {self.colors['text']};
            padding: 20px;
            font-size: 18px;
        """)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.left_layout.addWidget(status)
        
        # Navigation buttons
        self.create_nav_button("PROJECTS", self.show_projects)
        self.create_nav_button("SIMULATION", self.show_simulation)
        self.create_nav_button("ANALYSIS", self.show_analysis)
        
        self.left_layout.addStretch()
        
        # Return button
        return_btn = QPushButton("RETURN")
        return_btn.setStyleSheet(f"""
            background-color: {self.colors['alert_colors'][0]};
            color: {self.colors['text']};
            font-size: 16px;
            padding: 15px 30px;
        """)
        return_btn.clicked.connect(self.return_to_main)
        self.left_layout.addWidget(return_btn)
        
    def return_to_main(self):
        """Return to main menu"""
        try:
            if hasattr(self, 'selector') and self.selector:
                self.selector.show()
            self.close()
        except:
            pass
        
    def create_nav_button(self, text, slot):
        """Create authentic 25th century LCARS navigation button"""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['button_colors'][0]};
                color: {self.colors['text']};
                text-align: left;
                padding-left: 40px;
                font-family: 'Chakra Petch', 'Orbitron', 'Arial';
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self.colors['button_colors'][1]};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['button_colors'][2]};
            }}
        """)
        btn.clicked.connect(slot)
        self.left_layout.addWidget(btn)
        
    def create_content_area(self):
        """Create main content area with tabs"""
        self.content_stack = QTabWidget()
        
        # Projects tab
        projects_tab = QWidget()
        projects_layout = QHBoxLayout()
        
        # Project list
        self.project_list = QListWidget()
        self.update_project_list()
        projects_layout.addWidget(self.project_list)
        
        # Project info
        self.project_info = QLabel("Select a project")
        self.project_info.setStyleSheet(f"""
            color: {self.colors['text']};
            padding: 20px;
            font-size: 16px;
        """)
        projects_layout.addWidget(self.project_info)
        
        projects_tab.setLayout(projects_layout)
        self.content_stack.addTab(projects_tab, "PROJECTS")
        
        # Simulation tab
        sim_tab = QWidget()
        sim_layout = QVBoxLayout()
        
        self.sim_status = QLabel("No simulation running")
        self.sim_status.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 18px;
            padding: 20px;
        """)
        sim_layout.addWidget(self.sim_status)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.start_sim_btn = QPushButton("START")
        self.start_sim_btn.clicked.connect(self.start_simulation)
        btn_layout.addWidget(self.start_sim_btn)
        
        self.stop_sim_btn = QPushButton("STOP")
        self.stop_sim_btn.clicked.connect(self.stop_simulation)
        self.stop_sim_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_sim_btn)
        
        sim_layout.addLayout(btn_layout)
        sim_tab.setLayout(sim_layout)
        self.content_stack.addTab(sim_tab, "SIMULATION")
        
        # Analysis tab
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Energy", "Counts", "Particle"])
        analysis_layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(analysis_layout)
        self.content_stack.addTab(analysis_tab, "ANALYSIS")
        
        self.content_layout.addWidget(self.content_stack)
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        
    def calculate_stardate(self):
        """Calculate current stardate"""
        now = datetime.now()
        year_start = datetime(now.year, 1, 1)
        day_of_year = (now - year_start).days + 1
        stardate = (now.year - 1900) * 1000 + day_of_year * 2.73785
        return f"{stardate:.1f}"
    
    def update_time(self):
        """Update time and stardate display"""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        stardate_str = self.calculate_stardate()
        self.time_label.setText(f"STARDATE {stardate_str}\n{time_str}")
        
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
            analyzer = FileAnalyzer(self.current_project.path)
            info_text = f"Project: {self.current_project.name}\n"
            info_text += f"Path: {self.current_project.path}\n"
            info_text += f"Files: {len(analyzer.get_source_files())} source, {len(analyzer.get_data_files())} data"
            self.project_info.setText(info_text)
            
    def start_simulation(self):
        """Start simulation"""
        if not self.current_project:
            self.sim_status.setText("No project selected")
            return
            
        try:
            self.sim_status.setText("Initializing simulation...")
            self.current_simulation = Simulation()
            
            # Add particles
            electron = Particle(ParticleType.ELECTRON, energy=1.0)
            proton = Particle(ParticleType.PROTON, energy=10.0)
            self.current_simulation.add_particle(electron)
            self.current_simulation.add_particle(proton)
            
            self.current_simulation.run()
            
            self.sim_status.setText("Simulation running")
            self.start_sim_btn.setEnabled(False)
            self.stop_sim_btn.setEnabled(True)
            
        except Exception as e:
            self.sim_status.setText(f"Error: {str(e)}")
            
    def stop_simulation(self):
        """Stop simulation"""
        try:
            if self.current_simulation:
                self.current_simulation.stop()
                self.current_simulation = None
                
            self.sim_status.setText("Simulation stopped")
            self.start_sim_btn.setEnabled(True)
            self.stop_sim_btn.setEnabled(False)
            
        except Exception as e:
            self.sim_status.setText(f"Error: {str(e)}")
            
    def show_projects(self):
        """Switch to projects tab"""
        self.content_stack.setCurrentIndex(0)
        
    def show_simulation(self):
        """Switch to simulation tab"""
        self.content_stack.setCurrentIndex(1)
        
    def show_analysis(self):
        """Switch to analysis tab"""
        self.content_stack.setCurrentIndex(2)
        
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    print("Starting LCARS 25th Century Prototype...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get root path (project directory)
    root_path = Path(__file__).parent.parent.parent
    print(f"Root path: {root_path}")
    
    # Create and show 25th century interface
    try:
        lcars_25th = LCARS25thCentury(root_path)
        print("LCARS25thCentury created successfully")
        lcars_25th.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
