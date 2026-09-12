"""
LCARS Interface - 23rd Century Edition
Classic LCARS interface with traditional design from the 23rd century
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QSize, QPointF
from lcars.core.analysis import SpectraAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType
from lcars.core.project_manager import ProjectManager, ProjectInfo
import os
import logging

class PCARS23rdCentury(QMainWindow):
    """23rd Century LCARS Interface with classic design elements"""
    
    def __init__(self, root_path: Path, selector=None, ship_class=None):
        super().__init__()
        # Save reference to selector
        self.selector = selector
        self.ship_class = ship_class or "Constitution"
        # Initialize managers
        self.project_manager = ProjectManager(root_path)
        self.current_project = None
        # Import file analyzer
        from lcars.core.file_analyzer import FileAnalyzer
        self.FileAnalyzer = FileAnalyzer
        # Set up window
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window properties"""
        if self.ship_class == "Excelsior":
            self.setWindowTitle("USS EXCELSIOR NCC-2000 - LCARS 23rd Century")
        else:
            self.setWindowTitle("USS ENTERPRISE NCC-1701 - LCARS 23rd Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up color scheme using Theme for both Constitution and Excelsior"""
        # Use Theme to get palette for current era/ship_class
        from lcars.themes.theme import Theme
        if self.ship_class == "Excelsior":
            Theme.set_era("23rd-excelsior")
        else:
            Theme.set_era("23rd")
        self.colors = Theme.get_colors()
        
        # Fallback colors if Theme fails
        if not self.colors:
            self.colors = {
                'primary': '#FF9900',      # Orange
                'secondary': '#0099FF',    # Blue  
                'tertiary': '#00FF99',     # Green
                'background': '#000000',   # Black
                'text': '#FFFFFF',         # White
                'success': '#00FF00',     # Bright green
                'accent1': '#FFFF00'      # Yellow
            }
        
        border_width = 6 if self.ship_class == "Excelsior" else 2
        # Set application-wide stylesheet using Theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors.get('background', '#000000')};
                border: {border_width}px solid {self.colors.get('secondary', '#0099FF')};
            }}
            QLabel {{
                color: {self.colors.get('primary', '#FF9900')};
                font-family: {Theme.font_family() if hasattr(Theme, 'font_family') else 'Arial'};
                font-weight: bold;
                padding: 5px;
                border: {border_width}px solid {self.colors.get('secondary', '#0099FF')};
                background-color: {self.colors.get('background', '#000000')};
            }}
            QFrame {{
                background-color: {self.colors.get('background', '#000000')};
                border: {border_width}px solid {self.colors.get('secondary', '#0099FF')};
            }}
            QPushButton {{
                background-color: {self.colors.get('primary', '#FF9900')};
                color: {self.colors.get('background', '#000000')};
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-family: {Theme.button_font_family() if hasattr(Theme, 'button_font_family') else 'Arial'};
                font-weight: bold;
                font-size: 16px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {self.colors.get('accent1', '#FFFF00')};
            }}
            QPushButton:pressed {{
                background-color: {self.colors.get('tertiary', '#00FF99')};
            }}
            QListWidget {{
                background-color: {self.colors.get('background', '#000000')};
                border: {border_width}px solid {self.colors.get('primary', '#FF9900')};
                border-radius: 10px;
                color: {self.colors.get('text', '#FFFFFF')};
            }}
            QListWidget::item:selected {{
                background: {self.colors.get('primary', '#FF9900')};
                color: {self.colors.get('background', '#000000')};
            }}
        """)

    def paintEvent(self, a0):
        """Draw classic 23rd century interface elements, Excelsior = thick blue/green border, big number"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Draw retro-style interface elements
        self.draw_department_stripes(painter)
        self.draw_console_decorations(painter)
        if self.ship_class == "Excelsior":
            # Draw big ship number in header area
            painter.setPen(QPen(QColor(self.colors['secondary']), 8))
            font = QFont('Arial', 64, QFont.Weight.Bold)
            painter.setFont(font)
            painter.setOpacity(0.18)
            painter.drawText(80, 140, "NCC-2000")
            painter.setOpacity(1.0)
        
    def draw_department_stripes(self, painter):
        """Draw department color stripes"""
        stripe_width = 10
        colors = [self.colors['primary'],      # Command
                 self.colors['secondary'],      # Science
                 self.colors['tertiary']]       # Engineering
        
        y = 0
        for color in colors:
            painter.fillRect(0, y, self.width(), stripe_width, QColor(color))
            y += stripe_width + 2

    def draw_console_decorations(self, painter):
        """Draw classic console decorations, Excelsior = thick border"""
        if self.ship_class == "Excelsior":
            pen = QPen(QColor(self.colors['primary']))
            pen.setWidth(10)
        else:
            pen = QPen(QColor(self.colors['primary']))
            pen.setWidth(2)
        painter.setPen(pen)
        # Draw corner arcs
        radius = 50
        # Top-left
        painter.drawArc(0, 0, radius*2, radius*2, 90*16, 90*16)
        # Top-right
        painter.drawArc(self.width()-radius*2, 0, radius*2, radius*2, 0*16, 90*16)
        # Bottom-left
        painter.drawArc(0, self.height()-radius*2, radius*2, radius*2, 180*16, 90*16)
        # Bottom-right
        painter.drawArc(self.width()-radius*2, self.height()-radius*2, radius*2, radius*2, 270*16, 90*16)

    def create_layouts(self):
        """Create main layout structure: header, main_tabs, footer (vertical)"""
        self.main_layout = QVBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

    def create_classic_button(self, text, slot):
        """Create a classic 23rd century button"""
        btn = QPushButton(text)
        btn.setFixedHeight(50)
        btn.clicked.connect(slot)
        return btn

    def create_widgets(self):
        """Create and set up all widgets: header, main_tabs, footer"""
        self.create_header()
        self.create_main_display()
        self.create_footer()
        
    # def create_num_pad(self):
    #     pass  # Removed: not used in new layout
            
    # def create_com_section(self):
    #     pass  # Removed: not used in new layout
            
    def create_sys_controls(self):
        """Create system control section"""
        sys_buttons = [
            ("SCAN", 0, 0), ("NET", 0, 1), ("SYSTEM", 0, 2),
            ("FACTOR", 1, 0), ("WARP", 1, 1), ("SHIELD", 1, 2),
            ("PREVENT", 2, 0), ("IMPULS", 2, 1), ("POWER", 2, 2)
        ]
        
        for text, row, col in sys_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(90, 45)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors['tertiary']};
                    color: {self.colors['background']};
                    border: 1px solid {self.colors['primary']};
                    border-radius: 5px;
                    font-family: 'Swiss 911', 'Arial';
                    font-size: 14px;
                }}
            """)
        
    # def create_navigation_panel(self):
    #     pass  # Removed: not used in new layout

    def create_header(self):
        """Create classic header, Excelsior = big blue/green, number"""
        header = QWidget()
        header_layout = QHBoxLayout()
        # Title
        if self.ship_class == "Excelsior":
            title = QLabel("USS EXCELSIOR NCC-2000")
            title.setStyleSheet(f"""
                font-size: 32px;
                color: {self.colors['secondary']};
                background: transparent;
                font-weight: bold;
            """)
        else:
            title = QLabel("USS ENTERPRISE NCC-1701")
            title.setStyleSheet(f"""
                font-size: 24px;
                color: {self.colors['primary']};
                background: transparent;
            """)
        header_layout.addWidget(title)
        # Stardate
        self.stardate = QLabel()
        self.stardate.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['text']};
            background: transparent;
        """)
        header_layout.addWidget(self.stardate)
        header.setLayout(header_layout)
        self.main_layout.addWidget(header)
        # Update stardate
        self.update_stardate()
        timer = QTimer(self)
        timer.timeout.connect(self.update_stardate)
        timer.start(1000)

    def create_main_display(self):
        """Create main display area"""
        self.main_tabs = QTabWidget()
        self.main_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.colors['primary']};
                border-radius: 10px;
                background: {self.colors['background']};
            }}
            QTabBar::tab {{
                background: {self.colors['background']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['primary']};
                padding: 10px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}
            QTabBar::tab:selected {{
                background: {self.colors['primary']};
                color: {self.colors['background']};
            }}
        """)
        # Add tabs
        self.setup_command_tab()
        self.setup_science_tab()
        self.setup_engineering_tab()
        self.main_layout.addWidget(self.main_tabs)

    def create_footer(self):
        """Create classic footer"""
        footer = QWidget()
        footer_layout = QHBoxLayout()
        self.status_label = QLabel("All Systems Nominal")
        self.status_label.setStyleSheet(f"""
            color: {self.colors['success']};
            background: transparent;
        """)
        footer_layout.addWidget(self.status_label)
        footer.setLayout(footer_layout)
        self.main_layout.addWidget(footer)

    def setup_command_tab(self):
        """Set up command department tab"""
        command_tab = QWidget()
        layout = QVBoxLayout()
        
        # Project list
        self.project_list = QListWidget()
        layout.addWidget(self.project_list)
        
        command_tab.setLayout(layout)
        self.main_tabs.addTab(command_tab, "COMMAND")

    def setup_science_tab(self):
        """Set up science department tab"""
        science_tab = QWidget()
        layout = QVBoxLayout()
        
        self.simulation_status = QLabel("No Active Experiments")
        layout.addWidget(self.simulation_status)
        
        science_tab.setLayout(layout)
        self.main_tabs.addTab(science_tab, "SCIENCE")

    def setup_engineering_tab(self):
        """Set up engineering department tab"""
        engineering_tab = QWidget()
        layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background: {self.colors['background']};
                color: {self.colors['text']};
                gridline-color: {self.colors['primary']};
                border: 1px solid {self.colors['primary']};
            }}
            QHeaderView::section {{
                background: {self.colors['primary']};
                color: {self.colors['background']};
                padding: 5px;
            }}
        """)
        layout.addWidget(self.results_table)
        
        engineering_tab.setLayout(layout)
        self.main_tabs.addTab(engineering_tab, "ENGINEERING")

    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)

    def update_stardate(self):
        """Update stardate display"""
        from datetime import datetime
        now = datetime.now()
        # Classic stardate format: YYMM.DD
        stardate = f"{now.year%100}{now.month:02d}.{now.day:02d}"
        self.stardate.setText(f"STARDATE {stardate}")

    def show_projects(self):
        """Show command department view"""
        self.main_tabs.setCurrentIndex(0)
        
    def show_simulation(self):
        """Show science department view"""
        self.main_tabs.setCurrentIndex(1)
        
    def show_analysis(self):
        """Show engineering department view"""
        self.main_tabs.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Systems", 
                              "Systems configuration not yet implemented.")

    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if not current:
            return
            
        project_name = current.text()
        self.current_project = self.project_manager.get_project(project_name)
        
        if self.current_project:
            self.status_label.setText(f"Selected: {project_name}")
            
    def return_to_selector(self):
        """Return to interface selector"""
        if self.selector:
            self.selector.show()
            self.close()
            
    def return_to_main(self):
        """Return to main menu"""
        self.close()

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    print("Starting PCARS 23rd Century Interface...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get the root path (project directory)
    root_path = Path(__file__).parent.parent.parent
    print(f"Root path: {root_path}")
    
    # Create and show the 23rd century interface
    try:
        pears_interface = PCARS23rdCentury(root_path)
        print("PCARS23rdCentury created successfully")
        pears_interface.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()