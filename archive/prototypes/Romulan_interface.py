"""
D'deridex Control System - Strategic Operations Interface
For the Glory of the Romulan Star Empire
"""

# Додавання шляху до проекту для автономного запуску
import sys
from pathlib import Path
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem,  
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QLinearGradient
from PyQt6.QtCore import Qt, QTimer, QPointF, QSize
from lcars.core.analysis import SpectraAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType
from lcars.core.project_manager import ProjectManager, ProjectInfo
import os
import logging

# --- TrapezoidButton: QPushButton з трапецієподібною формою ---
class TrapezoidButton(QPushButton):
    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # Трапеція: верх вузький, низ широкий
        top_margin = int(h * 0.10)
        bottom_margin = int(h * 0.05)
        path = QPainterPath()
        path.moveTo(top_margin, 0)
        path.lineTo(w - top_margin, 0)
        path.lineTo(w - bottom_margin, h)
        path.lineTo(bottom_margin, h)
        path.closeSubpath()
        # Fill
        bg = self.palette().button().color()
        painter.setBrush(bg)
        painter.setPen(QColor(self.property('borderColor')) if self.property('borderColor') else QColor('#32CD32'))
        painter.drawPath(path)
        # Text
        painter.setPen(QColor(self.property('textColor')) if self.property('textColor') else QColor('#00FF99'))
        font = self.font()
        painter.setFont(font)
        text_rect = path.boundingRect().toRect()
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())

    def setColors(self, bg, border, text):
        self.setStyleSheet(f"background:{bg};border:none;")
        self.setProperty('borderColor', border)
        self.setProperty('textColor', text)
        self.update()
        
class RomulanInterface(QMainWindow):
    """Romulan-styled interface with strategic and elegant design"""
    
    def __init__(self, root_path: Path | None = None, selector=None, palette: str = 'Romulan'):
        """
        RomulanInterface
        :param root_path: Path to project root
        :param selector: optional reference to launcher
        :param palette: str, one of 'Romulan', 'Romulan_Tactical', 'Romulan_Engineering', 'Romulan_Command', 'Romulan_Display'
        """
        super().__init__()
        # Determine project root
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        self.selector = selector
        self.color_palette = 'Romulan'  # Default palette, can be changed later
        
        # Initialize managers
        self.project_manager = ProjectManager(self.root_path)
        self.current_project = None
        
        # Initialize file analyzer
        from lcars.core.file_analyzer import FileAnalyzer
        self.file_analyzer = FileAnalyzer(self.root_path)
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window with Romulan aesthetics"""
        self.setWindowTitle("D'deridex Control System - ch'Rihan Command")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up Romulan-inspired color scheme with local fallbacks for independence"""
        try:
            from lcars.themes.theme import get_faction_colors
            self.colors = get_faction_colors(self.color_palette)
        except (ImportError, AttributeError):
            # Basic fallback for independence
            self.colors = {
                'panel_border': '#336666',
                'button_colors': ['#00FF9D', '#034226', '#026938', '#00FF99'],
                'background': '#000805',
                'text': '#E0FFF0',
                'cloak': '#4169E1' # Royal Blue for cloaking device
            }
            
        # Ensure all required keys exist (for backward compatibility)
        if 'background' not in self.colors: self.colors['background'] = '#000000'
        if 'text' not in self.colors: self.colors['text'] = '#FFFFFF'
        
        btn_cols = self.colors.get('button_colors', ['#00FF9D', '#034226', '#026938', '#00FF99'])
        if 'primary' not in self.colors: self.colors['primary'] = btn_cols[0]
        if 'secondary' not in self.colors: self.colors['secondary'] = btn_cols[1]
        if 'tertiary' not in self.colors: self.colors['tertiary'] = btn_cols[2]
        if 'accent1' not in self.colors: self.colors['accent1'] = btn_cols[3] if len(btn_cols) > 3 else '#32CD32'
        if 'strategic' not in self.colors: self.colors['strategic'] = self.colors.get('panel_border', '#336666')
        if 'cloak' not in self.colors: self.colors['cloak'] = '#4169E1'
        if 'warning' not in self.colors: self.colors['warning'] = '#FFA500'
        if 'success' not in self.colors: self.colors['success'] = '#00FF7F'
        if 'alert' not in self.colors: self.colors['alert'] = '#FF4500'
        if 'caution' not in self.colors: self.colors['caution'] = '#FFD700'

        # Local font handling
        font_family = "Romulan, Arial"
        font_size_btn = 18
        
        # Backgrounds
        btn_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['primary']}, stop:1 {self.colors['strategic']})"
        header_bg = btn_bg
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 2px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: '{font_family}';
                font-weight: bold;
                padding: 5px;
                border: 1px solid {self.colors['primary']};
                background-color: rgba(0, 100, 0, 0.12);
            }}
            QPushButton {{
                background: {btn_bg};
                color: {self.colors['text']};
                border: 1px solid {self.colors['accent1']};
                border-radius: 8px;
                padding: 12px;
                font-family: '{font_family}';
                font-weight: bold;
                font-size: {font_size_btn}px;
                min-height: 44px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {self.colors['secondary']}, stop:1 {self.colors['accent1']});
                border: 1px solid {self.colors['text']};
            }}
            QPushButton:pressed {{
                background: {self.colors['tertiary']};
                border: 2px solid {self.colors['accent1']};
            }}
            QListWidget {{
                background-color: {self.colors['background']};
                border: 1px solid {self.colors['primary']};
                color: {self.colors['text']};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 10px;
                border: 1px solid {self.colors['primary']};
            }}
            QListWidget::item:hover {{
                background: {self.colors['strategic']};
                border: 1px solid {self.colors['accent1']};
            }}
            QListWidget::item:selected {{
                background: {self.colors['primary']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['accent1']};
            }}
            QTabWidget::pane {{
                border: 1px solid {self.colors['primary']};
                background-color: {self.colors['background']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                padding: 10px 20px;
                border: 1px solid {self.colors['accent1']};
                font-family: '{font_family}';
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['secondary']};
                border: 1px solid {self.colors['text']};
            }}
        """)
        
    def create_layouts(self):
        """Create Romulan-styled layout structure"""
        # Strategic command panel layout
        self.command_panel = QWidget()
        self.command_panel.setFixedWidth(350)
        self.command_layout = QVBoxLayout()
        self.command_panel.setLayout(self.command_layout)
        
        # Strategic display area
        self.strategic_area = QWidget()
        self.strategic_layout = QVBoxLayout()
        self.strategic_area.setLayout(self.strategic_layout)
        
        # Main layout
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.command_panel)
        self.main_layout.addWidget(self.strategic_area)
        
    def paintEvent(self, a0):
        """Draw Romulan geometric patterns"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circular and trapezoidal patterns
        pen = QPen(QColor(self.colors['primary']))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Grid size for patterns
        grid_size = 120
        
        # Draw pattern grid
        for x in range(0, self.width(), grid_size):
            for y in range(0, self.height(), grid_size):
                # Draw trapezoid
                path = QPainterPath()
                path.moveTo(x + grid_size * 0.2, y)
                path.lineTo(x + grid_size * 0.8, y)
                path.lineTo(x + grid_size, y + grid_size * 0.8)
                path.lineTo(x, y + grid_size * 0.8)
                path.closeSubpath()
                painter.drawPath(path)
                
                # Draw circle
                if (x + y) % (grid_size * 2) == 0:
                    painter.drawEllipse(
                        x + grid_size//4,
                        y + grid_size//4,
                        grid_size//2,
                        grid_size//2
                    )
                    
                    # Draw Romulan bird symbol
                    if (x + y) % (grid_size * 4) == 0:
                        self.draw_bird_symbol(painter, 
                                           x + grid_size//2, 
                                           y + grid_size//2)

    def draw_bird_symbol(self, painter, x, y):
        """Draw Romulan bird symbol"""
        size = 30
        pen = QPen(QColor(self.colors['accent1']))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw stylized bird
        path = QPainterPath()
        path.moveTo(x, y - size)
        path.cubicTo(x + size, y - size//2,
                    x + size, y + size//2,
                    x, y + size)
        path.cubicTo(x - size, y + size//2,
                    x - size, y - size//2,
                    x, y - size)
        painter.drawPath(path)
        
        # Add eye
        painter.drawEllipse(QPointF(x, y), size//6, size//6)

    def create_strategic_button(self, text, slot):
        """Create a Romulan-styled trapezoid command button"""
        btn = TrapezoidButton(text)
        btn.setFixedHeight(70)
        bg = self.colors['primary']
        border = self.colors.get('accent1', '#32CD32')
        text_color = self.colors.get('text', '#00FF99')
        btn.setColors(bg, border, text_color)
        font = btn.font()
        font.setPointSize(18)
        font.setBold(True)
        btn.setFont(font)
        btn.clicked.connect(slot)
        return btn
        
    def create_widgets(self):
        """Create Romulan-themed interface elements"""
        self.create_command_center()
        self.create_strategic_header()
        self.create_strategic_display()
        self.create_status_footer()
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        pass
        
    def create_command_center(self):
        """Create Romulan command center panel"""
        # Empire status
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        status_frame.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {self.colors['accent1']};
                background-color: rgba(0, 100, 0, 0.3);
            }}
        """)
        
        status_layout = QVBoxLayout()
        
        empire_label = QLabel("Romulan Star Empire")
        empire_label.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['accent1']};
            border: none;
            background: transparent;
        """)
        status_layout.addWidget(empire_label)
        
        self.cloak_status = QLabel("Cloaking Device: Active")
        self.cloak_status.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['cloak']};
            border: 1px solid {self.colors['accent1']};
            background: rgba(30, 144, 255, 0.1);
        """)
        status_layout.addWidget(self.cloak_status)
        
        status_frame.setLayout(status_layout)
        self.command_layout.addWidget(status_frame)
        
        # Strategic commands
        self.add_strategic_commands()
        
    def create_strategic_header(self):
        """Create Romulan strategic interface header"""
        header = QWidget()
        header.setFixedHeight(120)
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 {self.colors['primary']},
                                      stop:1 {self.colors['strategic']});
            border: 2px solid {self.colors['accent1']};
        """)
        
        header_layout = QHBoxLayout()
        
        # Empire emblem
        emblem = QLabel("🦅")
        emblem.setStyleSheet(f"""
            font-size: 48px;
            border: none;
            background: transparent;
        """)
        header_layout.addWidget(emblem)
        
        # Strategic time
        self.strategic_time = QLabel()
        self.strategic_time.setStyleSheet(f"""
            font-size: 32px;
            color: {self.colors['text']};
            border: 1px solid {self.colors['accent1']};
            background: rgba(0, 100, 0, 0.3);
        """)
        header_layout.addWidget(self.strategic_time)
        
        header.setLayout(header_layout)
        self.strategic_layout.addWidget(header)
        
        # Start strategic time
        self.update_strategic_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_strategic_time)
        timer.start(1000)
        
    def add_strategic_commands(self):
        """Add Romulan strategic command buttons"""
        # Project command
        projects_btn = self.create_strategic_button("Strategic Projects", self.show_projects)
        self.command_layout.addWidget(projects_btn)
        
        # Simulation command
        sim_btn = self.create_strategic_button("Tactical Simulations", self.show_simulation)
        self.command_layout.addWidget(sim_btn)
        
        # Analysis command
        analysis_btn = self.create_strategic_button("Intelligence Analysis", self.show_analysis)
        self.command_layout.addWidget(analysis_btn)
        
        # Settings command
        settings_btn = self.create_strategic_button("System Configuration", self.show_settings)
        self.command_layout.addWidget(settings_btn)
        
        self.command_layout.addStretch()
        
        # Return button
        return_btn = self.create_strategic_button("Return to Command Center", self.return_to_main)
        return_btn.setStyleSheet(return_btn.styleSheet() + f"background-color: {self.colors['warning']};")
        self.command_layout.addWidget(return_btn)
        
    def return_to_main(self):
        """Return to main launcher"""
        try:
            if hasattr(self, 'selector') and self.selector:
                self.selector.show()
        except Exception:
            pass
        self.close()
        
    def create_strategic_display(self):
        """Create strategic display area"""
        self.strategic_tabs = QTabWidget()
        
        # Projects strategic view
        self.setup_projects_strategic()
        
        # Simulation strategic view
        self.setup_simulation_strategic()
        
        # Analysis strategic view
        self.setup_analysis_strategic()
        
        self.strategic_layout.addWidget(self.strategic_tabs)
        
    def create_status_footer(self):
        """Create system status footer"""
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"""
            background-color: {self.colors['strategic']};
            border: 1px solid {self.colors['accent1']};
        """)
        
        footer_layout = QHBoxLayout()
        
        self.system_status = QLabel("All Systems Nominal")
        self.system_status.setStyleSheet(f"""
            color: {self.colors['success']};
            font-size: 16px;
            border: none;
            background: transparent;
        """)
        footer_layout.addWidget(self.system_status)
        
        footer.setLayout(footer_layout)
        self.strategic_layout.addWidget(footer)
        
    def setup_projects_strategic(self):
        """Set up projects strategic view with real functionality"""
        projects_tab = QWidget()
        layout = QVBoxLayout()
        
        # Project list with real data
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.on_project_selected)
        
        # Load actual projects
        try:
            projects = self.project_manager.get_all_projects()
            for project in projects:
                self.project_list.addItem(f"{project.name} - {project.build_dir}")
        except Exception:
            self.project_list.addItem("No projects found")
        
        layout.addWidget(self.project_list)
        
        # Project details with real information
        self.project_info = QWidget()
        info_layout = QVBoxLayout()
        
        self.project_title = QLabel("No Strategic Project Selected")
        self.project_path = QLabel("")
        self.project_status = QLabel("")
        
        info_layout.addWidget(self.project_title)
        info_layout.addWidget(self.project_path)
        info_layout.addWidget(self.project_status)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        build_btn = QPushButton("Build Project")
        build_btn.clicked.connect(self.build_selected_project)
        actions_layout.addWidget(build_btn)
        
        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self.run_project_simulation)
        actions_layout.addWidget(run_btn)
        
        info_layout.addLayout(actions_layout)
        self.project_info.setLayout(info_layout)
        layout.addWidget(self.project_info)
        
        projects_tab.setLayout(layout)
        self.strategic_tabs.addTab(projects_tab, "Projects")
        
    def on_project_selected(self, item):
        """Handle project selection"""
        try:
            project_name = item.text().split(" - ")[0]
            self.current_project = self.project_manager.get_project(project_name)
            
            if self.current_project:
                self.project_title.setText(f"Strategic Project: {self.current_project.name}")
                self.project_path.setText(f"Path: {self.current_project.build_dir}")
                self.project_status.setText(f"Status: Ready for tactical operations")
        except Exception as e:
            self.project_title.setText(f"Error loading project: {str(e)}")
            
    def build_selected_project(self):
        """Build the selected project"""
        if self.current_project:
            try:
                # Real build functionality
                result = self.project_manager.build_project(self.current_project)
                self.project_status.setText(f"Build Status: {result}")
            except Exception as e:
                self.project_status.setText(f"Build Error: {str(e)}")
        else:
            self.project_status.setText("No project selected")
            
    def run_project_simulation(self):
        """Run simulation for selected project"""
        if self.current_project:
            try:
                # Real simulation functionality
                simulation = Simulation(self.current_project)
                particle = Particle(ParticleType.ELECTRON, energy=1.0)
                results = simulation.run(particle)
                self.project_status.setText(f"Simulation completed with {len(results)} events")
            except Exception as e:
                self.project_status.setText(f"Simulation Error: {str(e)}")
        else:
            self.project_status.setText("No project selected")
            
    def setup_simulation_strategic(self):
        """Set up simulation strategic view"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        self.simulation_status = QLabel("No Tactical Simulation Running")
        layout.addWidget(self.simulation_status)
        
        simulation_tab.setLayout(layout)
        self.strategic_tabs.addTab(simulation_tab, "Simulations")
        
    def setup_analysis_strategic(self):
        """Set up analysis strategic view"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                gridline-color: {self.colors['accent1']};
                border: 1px solid {self.colors['primary']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: {self.colors['text']};
                border: 1px solid {self.colors['accent1']};
                padding: 5px;
            }}
        """)
        layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(layout)
        self.strategic_tabs.addTab(analysis_tab, "Analysis")
        
    def update_strategic_time(self):
        """Update Romulan strategic time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.strategic_time.setText(f"Strategic Time: {current_time}")
        
    def show_projects(self):
        """Show projects strategic view"""
        self.strategic_tabs.setCurrentIndex(0)
        
    def show_simulation(self):
        """Show simulation strategic view"""
        self.strategic_tabs.setCurrentIndex(1)
        
    def show_analysis(self):
        """Show analysis strategic view"""
        self.strategic_tabs.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings with Romulan styling"""
        QMessageBox.information(self, "System Configuration", 
                              "Configuration module not yet implemented.")

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    
    print("Starting Romulan Interface...")
    
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Get the root path (project directory)
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    print(f"Root path: {root_path}")
    
    # Create and show the Romulan interface
    try:
        romulan_interface = RomulanInterface(root_path)
        print("RomulanInterface created successfully")
        romulan_interface.show()
        print("Window shown successfully")
        
        # Run the application
        print("Starting app.exec()...")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()