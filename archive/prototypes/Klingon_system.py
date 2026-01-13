"""
batlh DaHjaj - Klingon Honor System
yIH 'ej HoS - Strength and Honor in Battle
"""

import sys
from pathlib import Path
import os
import logging

# Додавання шляху до проекту для автономного запуску
current_file = Path(__file__).resolve()
project_root = current_file.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QApplication)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QLinearGradient, QBrush
from PyQt6.QtCore import Qt, QTimer, QSize, QPoint
from pathlib import Path
import os
import logging

from lcars.core.project_manager import ProjectManager, ProjectInfo

class KlingonInterface(QMainWindow):
    """Klingon-styled interface with warrior aesthetics"""
    
    def __init__(self, root_path: Path | None = None):
        super().__init__()
        # Determine project root
        self.root_path = root_path or Path(__file__).resolve().parents[2]
        
        self.project_manager = ProjectManager(self.root_path)
        self.current_project = None
        
        from lcars.core.file_analyzer import FileAnalyzer
        self.file_analyzer = FileAnalyzer(self.root_path)
        
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window with Klingon aesthetics"""
        self.setWindowTitle("batlh DaHjaj - tlhIngan wo' HoS")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up Klingon-inspired color scheme"""
        self.colors = {
            # Base colors - dark and aggressive
            'background': '#1A0F0F',     # Very dark red-tinted black
            'text': '#FF0000',           # Bright red for text
            
            # Primary colors - red variants for warrior theme
            'primary': '#8B0000',        # Dark red
            'secondary': '#B22222',      # Firebrick red
            'tertiary': '#CD5C5C',      # Indian red
            
            # Accent colors - metallic and plasma-weapon inspired
            'accent1': '#FFD700',        # Metallic gold
            'accent2': '#C0C0C0',        # Metallic silver
            'accent3': '#800000',        # Maroon
            
            # System colors
            'warning': '#FF0000',        # Bright red
            'success': '#DAA520',        # Goldenrod
            'alert': '#FF4500',          # Orange-red
            
            # Additional Klingon-specific colors
            'battle': '#4B0082',         # Deep purple for battle status
            'honor': '#8B4513',          # Saddle brown for honor system
        }
        
        # Klingon-styled application theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                border: 3px solid {self.colors['primary']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Klingon', 'Arial Black';
                font-weight: bold;
                padding: 5px;
                border: 2px ridge {self.colors['primary']};
                background-color: rgba(139, 0, 0, 0.2);
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['accent1']};
                border: 2px ridge {self.colors['accent1']};
                border-radius: 0px;
                padding: 15px;
                font-family: 'Klingon', 'Arial Black';
                font-weight: bold;
                font-size: 16px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['secondary']};
                border: 2px ridge {self.colors['text']};
                color: {self.colors['accent1']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['tertiary']};
                border: 3px ridge {self.colors['accent1']};
            }}
            QListWidget {{
                background-color: {self.colors['background']};
                border: 2px ridge {self.colors['primary']};
                color: {self.colors['text']};
                padding: 5px;
                alternate-background-color: rgba(139, 0, 0, 0.2);
            }}
            QListWidget::item {{
                padding: 10px;
                border: 1px solid {self.colors['primary']};
            }}
            QListWidget::item:hover {{
                background: {self.colors['battle']};
                border: 1px ridge {self.colors['accent1']};
            }}
            QListWidget::item:selected {{
                background: {self.colors['primary']};
                color: {self.colors['accent1']};
                border: 2px ridge {self.colors['accent1']};
            }}
            QTabWidget::pane {{
                border: 2px ridge {self.colors['primary']};
                background-color: {self.colors['background']};
            }}
            QTabBar::tab {{
                background-color: {self.colors['primary']};
                color: {self.colors['accent1']};
                padding: 10px 20px;
                border: 2px ridge {self.colors['accent1']};
                font-family: 'Klingon', 'Arial Black';
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['secondary']};
                border: 2px ridge {self.colors['text']};
            }}
        """)
        
    def create_layouts(self):
        """Create Klingon-styled layout structure"""
        # Main battle command center layout
        self.command_panel = QWidget()
        self.command_panel.setFixedWidth(350)
        self.command_layout = QVBoxLayout()
        self.command_panel.setLayout(self.command_layout)
        
        # Tactical display area
        self.tactical_area = QWidget()
        self.tactical_layout = QVBoxLayout()
        self.tactical_area.setLayout(self.tactical_layout)
        
        # Battle layout
        self.main_layout = QHBoxLayout()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.main_layout.addWidget(self.command_panel)
        self.main_layout.addWidget(self.tactical_area)
        
    def paintEvent(self, event):
        """Draw Klingon geometric patterns"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw triangular patterns
        pen = QPen(QColor(self.colors['primary']))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Grid size
        grid_size = 100
        
        # Draw triangular grid
        for x in range(0, self.width(), grid_size):
            for y in range(0, self.height(), grid_size):
                # Draw upward triangle
                painter.drawLine(x, y + grid_size, x + grid_size//2, y)
                painter.drawLine(x + grid_size//2, y, x + grid_size, y + grid_size)
                painter.drawLine(x, y + grid_size, x + grid_size, y + grid_size)
                
                # Draw Klingon Empire symbol in some cells
                if (x + y) % (grid_size * 3) == 0:
                    self.draw_empire_symbol(painter, x + grid_size//2, y + grid_size//2)

    def draw_empire_symbol(self, painter, x, y):
        """Draw Klingon Empire symbol"""
        size = 30
        pen = QPen(QColor(self.colors['accent1']))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Draw trefoil symbol
        for i in range(3):
            angle = i * 120
            rad = angle * 3.14159 / 180
            x1 = x + size * 0.866 * 2 * (-1 if i == 1 else (0.5 if i == 0 else 0.5))
            y1 = y + size * (1 if i == 1 else -0.5)
            # QPainter.drawLine expects integer coordinates (or QPoint/QPointF); ensure ints
            painter.drawLine(int(x), int(y), int(x1), int(y1))
            x2 = x1 + size * 0.5
            y2 = y1 + (size * 0.866 if i == 1 else -size * 0.866)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def create_battle_button(self, text, slot):
        """Create a Klingon-styled command button"""
        btn = QPushButton(text)
        btn.setFixedHeight(70)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {self.colors['primary']},
                                          stop:1 {self.colors['battle']});
                color: {self.colors['accent1']};
                text-align: center;
                border: 2px ridge {self.colors['accent1']};
                font-family: 'Klingon', 'Arial Black';
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 {self.colors['secondary']},
                                          stop:1 {self.colors['accent1']});
                color: {self.colors['text']};
                border: 2px ridge {self.colors['text']};
            }}
        """)
        btn.clicked.connect(slot)
        return btn
        
    def create_widgets(self):
        """Create Klingon-themed interface elements"""
        self.create_command_center()
        self.create_battle_header()
        self.create_tactical_display()
        self.create_honor_footer()
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        pass
        
    def create_command_center(self):
        """Create Klingon command center panel"""
        # Empire status
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        status_frame.setStyleSheet(f"""
            QFrame {{
                border: 3px ridge {self.colors['accent1']};
                background-color: rgba(139, 0, 0, 0.3);
            }}
        """)
        
        status_layout = QVBoxLayout()
        
        empire_label = QLabel("tlhIngan wo'")
        empire_label.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['accent1']};
            border: none;
            background: transparent;
        """)
        status_layout.addWidget(empire_label)
        
        self.battle_status = QLabel("Qapla'!")
        self.battle_status.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['text']};
            border: 2px ridge {self.colors['accent1']};
            background: rgba(75, 0, 130, 0.3);
        """)
        status_layout.addWidget(self.battle_status)
        
        status_frame.setLayout(status_layout)
        self.command_layout.addWidget(status_frame)
        
        # Battle commands
        self.add_battle_commands()
        
    def create_battle_header(self):
        """Create Klingon battle interface header"""
        header = QWidget()
        header.setFixedHeight(120)
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                      stop:0 {self.colors['primary']},
                                      stop:1 {self.colors['battle']});
            border: 3px ridge {self.colors['accent1']};
        """)
        
        header_layout = QHBoxLayout()
        
        # Empire emblem
        emblem = QLabel("⚔️")
        emblem.setStyleSheet(f"""
            font-size: 48px;
            border: none;
            background: transparent;
        """)
        header_layout.addWidget(emblem)
        
        # Battle time
        self.battle_time = QLabel()
        self.battle_time.setStyleSheet(f"""
            font-size: 32px;
            color: {self.colors['accent1']};
            border: 2px ridge {self.colors['accent1']};
            background: rgba(139, 0, 0, 0.4);
        """)
        header_layout.addWidget(self.battle_time)
        
        header.setLayout(header_layout)
        self.tactical_layout.addWidget(header)
        
        # Start battle time
        self.update_battle_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_battle_time)
        timer.start(1000)
        
    def add_battle_commands(self):
        """Add Klingon battle command buttons"""
        # Project command
        projects_btn = self.create_battle_button("ghojmoHwI'", self.show_projects)
        self.command_layout.addWidget(projects_btn)
        
        # Simulation command
        sim_btn = self.create_battle_button("HablI'", self.show_simulation)
        self.command_layout.addWidget(sim_btn)
        
        # Analysis command
        analysis_btn = self.create_battle_button("tu'ta'", self.show_analysis)
        self.command_layout.addWidget(analysis_btn)
        
        # Settings command
        settings_btn = self.create_battle_button("SeHlaw", self.show_settings)
        self.command_layout.addWidget(settings_btn)
        
        self.command_layout.addStretch()
        
        # Return button
        return_btn = self.create_battle_button("Return to Command", self.return_to_main)
        return_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['warning']};
                color: {self.colors['text']};
                border: 2px ridge {self.colors['text']};
            }}
            QPushButton:hover {{
                background-color: {self.colors['secondary']};
                border: 2px ridge {self.colors['accent1']};
            }}
        """)
        self.command_layout.addWidget(return_btn)
        
    def return_to_main(self):
        """Return to main menu"""
        # Show selector (if present) before closing so user returns to launcher
        try:
            if hasattr(self, 'selector') and self.selector:
                self.selector.show()
        except Exception:
            pass
        self.close()
        
    def create_tactical_display(self):
        """Create tactical display area"""
        self.tactical_tabs = QTabWidget()
        
        # Projects tactical view
        self.setup_projects_tactical()
        
        # Simulation tactical view
        self.setup_simulation_tactical()
        
        # Analysis tactical view
        self.setup_analysis_tactical()
        
        self.tactical_layout.addWidget(self.tactical_tabs)
        
    def create_honor_footer(self):
        """Create honor system footer"""
        footer = QWidget()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"""
            background-color: {self.colors['honor']};
            border: 2px ridge {self.colors['accent1']};
        """)
        
        footer_layout = QHBoxLayout()
        
        self.honor_status = QLabel("batlh Daqawlu'taH")
        self.honor_status.setStyleSheet(f"""
            color: {self.colors['accent1']};
            font-size: 16px;
            border: none;
            background: transparent;
        """)
        footer_layout.addWidget(self.honor_status)
        
        footer.setLayout(footer_layout)
        self.tactical_layout.addWidget(footer)
        
    def setup_projects_tactical(self):
        """Set up projects tactical view"""
        projects_tab = QWidget()
        layout = QVBoxLayout()
        
        # Project list with Klingon styling
        self.project_list = QListWidget()
        self.project_list.setAlternatingRowColors(True)
        layout.addWidget(self.project_list)
        
        # Project details with battle information
        self.project_info = QWidget()
        info_layout = QVBoxLayout()
        
        self.project_title = QLabel("No Battle Plan Selected")
        info_layout.addWidget(self.project_title)
        
        self.project_info.setLayout(info_layout)
        layout.addWidget(self.project_info)
        
        projects_tab.setLayout(layout)
        self.tactical_tabs.addTab(projects_tab, "yIH")
        
    def setup_simulation_tactical(self):
        """Set up simulation tactical view"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        self.simulation_status = QLabel("No Battle Simulation Running")
        layout.addWidget(self.simulation_status)
        
        simulation_tab.setLayout(layout)
        self.tactical_tabs.addTab(simulation_tab, "HablI'")
        
    def setup_analysis_tactical(self):
        """Set up analysis tactical view"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                gridline-color: {self.colors['accent1']};
                border: 2px ridge {self.colors['primary']};
            }}
            QHeaderView::section {{
                background-color: {self.colors['primary']};
                color: {self.colors['accent1']};
                border: 1px ridge {self.colors['accent1']};
                padding: 5px;
            }}
        """)
        layout.addWidget(self.results_table)
        
        analysis_tab.setLayout(layout)
        self.tactical_tabs.addTab(analysis_tab, "tu'ta'")
        
    def update_battle_time(self):
        """Update Klingon battle time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.battle_time.setText(f"wen: {current_time}")
        
    def show_projects(self):
        """Show projects tactical view"""
        self.tactical_tabs.setCurrentIndex(0)
        
    def show_simulation(self):
        """Show simulation tactical view"""
        self.tactical_tabs.setCurrentIndex(1)
        
    def show_analysis(self):
        """Show analysis tactical view"""
        self.tactical_tabs.setCurrentIndex(2)
        
    def show_settings(self):
        """Show settings with Klingon styling"""
        QMessageBox.information(self, "SeHlaw", 
                              "SeHlaw not yet implemented.\nQapla'!")                         

def main():
    """Main entry point for Klingon Battle Station"""
    from PyQt6.QtWidgets import QApplication
    from pathlib import Path
    import sys
    
    print("Starting Klingon Battle Station...")
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Create Klingon interface
    current_file = Path(__file__).resolve()
    root_path = current_file.parents[2]
    interface = KlingonInterface(root_path)
    
    # Show interface with proper window management
    interface.show()
    interface.raise_()
    interface.activateWindow()
    
    # Force window to front
    interface.setWindowState(Qt.WindowState.WindowActive)
    
    print("Battle Station operational")
    print("Window title:", interface.windowTitle())
    print("Window geometry:", interface.geometry())
    
    # Start event loop
    return app.exec()

if __name__ == "__main__":
    main()