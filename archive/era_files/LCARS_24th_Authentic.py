"""
LCARS Interface - 24th Century Edition (TNG/DS9 Style)
Authentic LCARS interface with proper 24th century design elements
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame,
                           QGridLayout, QGroupBox)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QPen, QLinearGradient, QBrush
from PyQt6.QtCore import Qt, QTimer, QSize, QRect, pyqtSignal
from lcars.core.project_manager import ProjectManager, ProjectInfo
from lcars.core.file_analyzer import FileAnalyzer
import os
import logging

class LCARS24thCentury(QMainWindow):
    """Authentic 24th Century LCARS Interface with TNG/DS9 design"""
    
    def __init__(self, root_path: Path, selector=None):
        super().__init__()
        # Save reference to selector
        self.selector = selector
        
        # Initialize managers
        self.project_manager = ProjectManager(root_path)
        self.current_project = None
        self.FileAnalyzer = FileAnalyzer
        
        # Set up window
        self.setup_window()
        self.setup_color_scheme()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window with LCARS aesthetics"""
        self.setWindowTitle("LCARS 24TH CENTURY - TNG/DS9")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_color_scheme(self):
        """Set up authentic 24th century LCARS color scheme"""
        # Classic TNG/DS9 color palette
        self.colors = {
            'background': '#000000',
            'text': '#CCDDFF',  # Light blue-white text
            'primary': '#FFAA00',  # Orange
            'secondary': '#0066CC',  # Blue
            'tertiary': '#00AAFF',  # Light blue
            'accent1': '#FF6600',  # Dark orange
            'accent2': '#FFCC66',  # Light orange
            'warning': '#FF3333',
            'success': '#00CC66',
            'panel': '#0A0A0A',  # Very dark gray
            'border': '#FFAA00'
        }
        
        # Apply LCARS stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
            }}
            QLabel {{
                color: {self.colors['text']};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: {self.colors['accent1']};
                border-color: {self.colors['accent2']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['accent2']};
            }}
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
            }}
            QTabWidget::pane {{
                border: 2px solid {self.colors['border']};
                background-color: {self.colors['panel']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {self.colors['secondary']};
                color: {self.colors['text']};
                border: 2px solid {self.colors['border']};
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                font-weight: bold;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
            QTabBar::tab:hover {{
                background-color: {self.colors['accent1']};
            }}
        """)
        
    def paintEvent(self, event):
        """Draw authentic LCARS TNG/DS9 interface elements"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw characteristic LCARS side panels
        self.draw_side_panels(painter)
        
        # Draw corner elements
        self.draw_corner_elements(painter)
        
        # Draw LCARS header bar
        self.draw_header_bar(painter)
        
    def draw_side_panels(self, painter):
        """Draw characteristic LCARS side panels"""
        # Left side panel
        left_panel = QPainterPath()
        left_panel.moveTo(0, 0)
        left_panel.lineTo(200, 0)
        left_panel.lineTo(200, self.height())
        left_panel.lineTo(0, self.height())
        left_panel.closeSubpath()
        
        gradient = QLinearGradient(0, 0, 200, 0)
        gradient.setColorAt(0, QColor(self.colors['secondary']))
        gradient.setColorAt(0.5, QColor(self.colors['tertiary']))
        gradient.setColorAt(1, QColor(self.colors['secondary']))
        
        painter.fillPath(left_panel, QBrush(gradient))
        painter.setPen(QPen(QColor(self.colors['border']), 3))
        painter.drawPath(left_panel)
        
        # Right side panel
        right_panel = QPainterPath()
        right_panel.moveTo(self.width() - 150, 0)
        right_panel.lineTo(self.width(), 0)
        right_panel.lineTo(self.width(), self.height())
        right_panel.lineTo(self.width() - 150, self.height())
        right_panel.closeSubpath()
        
        gradient2 = QLinearGradient(self.width() - 150, 0, self.width(), 0)
        gradient2.setColorAt(0, QColor(self.colors['accent1']))
        gradient2.setColorAt(0.5, QColor(self.colors['primary']))
        gradient2.setColorAt(1, QColor(self.colors['accent1']))
        
        painter.fillPath(right_panel, QBrush(gradient2))
        painter.drawPath(right_panel)
        
    def draw_corner_elements(self, painter):
        """Draw LCARS corner elements"""
        corner_size = 60
        
        # Top-left corner
        corner_path = QPainterPath()
        corner_path.moveTo(0, 0)
        corner_path.lineTo(corner_size, 0)
        corner_path.lineTo(0, corner_size)
        corner_path.closeSubpath()
        
        painter.fillPath(corner_path, QBrush(QColor(self.colors['primary'])))
        painter.setPen(QPen(QColor(self.colors['border']), 2))
        painter.drawPath(corner_path)
        
        # Top-right corner
        corner_path2 = QPainterPath()
        corner_path2.moveTo(self.width() - corner_size, 0)
        corner_path2.lineTo(self.width(), 0)
        corner_path2.lineTo(self.width(), corner_size)
        corner_path2.lineTo(self.width() - corner_size, corner_size)
        corner_path2.closeSubpath()
        
        painter.fillPath(corner_path2, QBrush(QColor(self.colors['accent1'])))
        painter.drawPath(corner_path2)
        
    def draw_header_bar(self, painter):
        """Draw LCARS header bar"""
        header_height = 80
        
        # Main header bar
        header_path = QPainterPath()
        header_path.moveTo(200, 0)
        header_path.lineTo(self.width() - 150, 0)
        header_path.lineTo(self.width() - 150, header_height)
        header_path.lineTo(200, header_height)
        header_path.closeSubpath()
        
        gradient = QLinearGradient(200, 0, self.width() - 150, 0)
        gradient.setColorAt(0, QColor(self.colors['primary']))
        gradient.setColorAt(0.3, QColor(self.colors['accent2']))
        gradient.setColorAt(0.7, QColor(self.colors['accent2']))
        gradient.setColorAt(1, QColor(self.colors['primary']))
        
        painter.fillPath(header_path, QBrush(gradient))
        painter.drawPath(header_path)
        
        # Add LCARS text
        painter.setPen(QPen(QColor(self.colors['background']), 3))
        font = QFont('Swiss 911', 28, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(250, 50, "LCARS")
        
        # Add starfleet emblem area
        emblem_rect = QRect(self.width() - 300, 10, 120, 60)
        painter.setPen(QPen(QColor(self.colors['background']), 2))
        painter.drawRect(emblem_rect)
        
    def create_layouts(self):
        """Create main layout structure"""
        # Main layout with margins for side panels
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(220, 100, 170, 20)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        
    def create_widgets(self):
        """Create and set up all widgets"""
        self.create_status_display()
        self.create_main_tabs()
        self.create_control_panel()
        self.create_footer()
        
    def create_status_display(self):
        """Create LCARS status display"""
        status_frame = QFrame()
        status_frame.setObjectName("statusFrame")
        status_frame.setStyleSheet(f"""
            QFrame#statusFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        
        status_layout = QHBoxLayout()
        
        # System status
        self.system_status = QLabel("ALL SYSTEMS OPERATIONAL")
        self.system_status.setStyleSheet(f"""
            font-size: 18px;
            color: {self.colors['success']};
            padding: 10px;
        """)
        status_layout.addWidget(self.system_status)
        
        # Stardate
        self.stardate = QLabel()
        self.stardate.setStyleSheet(f"""
            font-size: 16px;
            color: {self.colors['tertiary']};
            padding: 10px;
        """)
        status_layout.addWidget(self.stardate)
        
        status_frame.setLayout(status_layout)
        self.main_layout.addWidget(status_frame)
        
        # Update stardate
        self.update_stardate()
        timer = QTimer(self)
        timer.timeout.connect(self.update_stardate)
        timer.start(1000)
        
    def create_main_tabs(self):
        """Create main content tabs"""
        self.main_tabs = QTabWidget()
        self.main_tabs.setObjectName("mainTabs")
        
        # Create tabs
        self.create_projects_tab()
        self.create_science_tab()
        self.create_engineering_tab()
        self.create_tactical_tab()
        
        self.main_layout.addWidget(self.main_tabs)
        
    def create_projects_tab(self):
        """Create projects management tab"""
        projects_tab = QWidget()
        layout = QHBoxLayout()
        
        # Project list
        list_frame = QFrame()
        list_layout = QVBoxLayout()
        
        list_label = QLabel("PROJECTS")
        list_label.setStyleSheet(f"font-size: 16px; color: {self.colors['primary']};")
        list_layout.addWidget(list_label)
        
        self.project_list = QListWidget()
        self.project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors['panel']};
                border: 1px solid {self.colors['border']};
                color: {self.colors['text']};
                font-size: 14px;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['primary']};
                color: {self.colors['background']};
            }}
        """)
        
        # Add sample projects
        sample_projects = [
            "USS Enterprise-D Systems",
            "Deep Space 9 Operations",
            "Voyager Astrometrics",
            "Holodeck Programs",
            "Transporter Systems"
        ]
        
        for project in sample_projects:
            self.project_list.addItem(project)
        
        list_layout.addWidget(self.project_list)
        list_frame.setLayout(list_layout)
        layout.addWidget(list_frame)
        
        # Project details
        details_frame = QFrame()
        details_layout = QVBoxLayout()
        
        details_label = QLabel("PROJECT DETAILS")
        details_label.setStyleSheet(f"font-size: 16px; color: {self.colors['primary']};")
        details_layout.addWidget(details_label)
        
        self.project_details = QLabel("Select a project to view details")
        self.project_details.setStyleSheet(f"""
            color: {self.colors['text']};
            font-size: 14px;
            padding: 10px;
            background-color: {self.colors['panel']};
            border: 1px solid {self.colors['border']};
            border-radius: 4px;
        """)
        self.project_details.setWordWrap(True)
        details_layout.addWidget(self.project_details)
        
        details_frame.setLayout(details_layout)
        layout.addWidget(details_frame)
        
        projects_tab.setLayout(layout)
        self.main_tabs.addTab(projects_tab, "PROJECTS")
        
    def create_science_tab(self):
        """Create science station tab"""
        science_tab = QWidget()
        layout = QVBoxLayout()
        
        # Science station header
        header_label = QLabel("SCIENCE STATION")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['tertiary']};
            padding: 10px;
            border-bottom: 2px solid {self.colors['border']};
        """)
        layout.addWidget(header_label)
        
        # Sensor status
        sensor_frame = QFrame()
        sensor_layout = QGridLayout()
        
        sensors = [
            ("LONG RANGE SENSORS", "ONLINE"),
            ("SHORT RANGE SENSORS", "ONLINE"),
            ("ASTROMETRICS", "STANDBY"),
            ("SUBSPACE COMMUNICATIONS", "ACTIVE"),
            ("INTERNAL SENSORS", "ONLINE"),
            ("EXTERNAL SENSORS", "ONLINE")
        ]
        
        for i, (sensor, status) in enumerate(sensors):
            sensor_label = QLabel(sensor)
            sensor_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px;")
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {self.colors['success']}; font-size: 12px; font-weight: bold;")
            
            sensor_layout.addWidget(sensor_label, i, 0)
            sensor_layout.addWidget(status_label, i, 1)
        
        sensor_frame.setLayout(sensor_layout)
        layout.addWidget(sensor_frame)
        
        science_tab.setLayout(layout)
        self.main_tabs.addTab(science_tab, "SCIENCE")
        
    def create_engineering_tab(self):
        """Create engineering tab"""
        engineering_tab = QWidget()
        layout = QVBoxLayout()
        
        # Engineering header
        header_label = QLabel("ENGINEERING")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['accent1']};
            padding: 10px;
            border-bottom: 2px solid {self.colors['border']};
        """)
        layout.addWidget(header_label)
        
        # System controls
        controls_frame = QFrame()
        controls_layout = QGridLayout()
        
        systems = [
            ("WARP CORE", "ONLINE", self.colors['success']),
            ("IMPULSE ENGINES", "ONLINE", self.colors['success']),
            ("SHIELDS", "100%", self.colors['tertiary']),
            ("PHASERS", "STANDBY", self.colors['warning']),
            ("PHOTON TORPEDOES", "READY", self.colors['success']),
            ("TRANSPORTER", "OFFLINE", self.colors['warning'])
        ]
        
        for i, (system, status, color) in enumerate(systems):
            system_label = QLabel(system)
            system_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px;")
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            
            controls_layout.addWidget(system_label, i, 0)
            controls_layout.addWidget(status_label, i, 1)
        
        controls_frame.setLayout(controls_layout)
        layout.addWidget(controls_frame)
        
        engineering_tab.setLayout(layout)
        self.main_tabs.addTab(engineering_tab, "ENGINEERING")
        
    def create_tactical_tab(self):
        """Create tactical tab"""
        tactical_tab = QWidget()
        layout = QVBoxLayout()
        
        # Tactical header
        header_label = QLabel("TACTICAL")
        header_label.setStyleSheet(f"""
            font-size: 20px;
            color: {self.colors['accent1']};
            padding: 10px;
            border-bottom: 2px solid {self.colors['border']};
        """)
        layout.addWidget(header_label)
        
        # Tactical display
        tactical_display = QFrame()
        tactical_display.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['panel']};
                border: 2px solid {self.colors['border']};
                border-radius: 8px;
                min-height: 300px;
            }}
        """)
        
        tactical_layout = QVBoxLayout()
        display_label = QLabel("TACTICAL DISPLAY")
        display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        display_label.setStyleSheet(f"""
            font-size: 24px;
            color: {self.colors['warning']};
            padding: 50px;
        """)
        tactical_layout.addWidget(display_label)
        
        tactical_display.setLayout(tactical_layout)
        layout.addWidget(tactical_display)
        
        tactical_tab.setLayout(layout)
        self.main_tabs.addTab(tactical_tab, "TACTICAL")
        
    def create_control_panel(self):
        """Create LCARS control panel"""
        control_frame = QFrame()
        control_layout = QHBoxLayout()
        
        # Control buttons
        controls = [
            ("SCAN", self.run_scan),
            ("ANALYZE", self.run_analysis),
            ("COMPUTE", self.run_compute),
            ("TRANSMIT", self.run_transmit)
        ]
        
        for text, callback in controls:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setFixedWidth(120)
            control_layout.addWidget(btn)
        
        control_layout.addStretch()
        control_frame.setLayout(control_layout)
        self.main_layout.addWidget(control_frame)
        
    def create_footer(self):
        """Create LCARS footer"""
        footer_frame = QFrame()
        footer_layout = QHBoxLayout()
        
        # Status indicators
        self.footer_status = QLabel("READY")
        self.footer_status.setStyleSheet(f"""
            font-size: 16px;
            color: {self.colors['success']};
            padding: 10px;
        """)
        footer_layout.addWidget(self.footer_status)
        
        footer_layout.addStretch()
        
        # Return button
        return_btn = QPushButton("RETURN")
        return_btn.clicked.connect(self.return_to_selector)
        return_btn.setFixedWidth(120)
        footer_layout.addWidget(return_btn)
        
        footer_frame.setLayout(footer_layout)
        self.main_layout.addWidget(footer_frame)
        
    def setup_connections(self):
        """Set up signal/slot connections"""
        self.project_list.currentItemChanged.connect(self.on_project_selected)
        
    def update_stardate(self):
        """Update stardate display"""
        from datetime import datetime
        now = datetime.now()
        # TNG stardate format: 4xxxxx.x
        year_offset = now.year - 1987
        day_of_year = now.timetuple().tm_yday
        stardate = f"{year_offset:04d}.{day_of_year:03d}"
        self.stardate.setText(f"STARDATE {stardate}")
        
    def on_project_selected(self, current, previous):
        """Handle project selection"""
        if current:
            project_name = current.text()
            self.project_details.setText(f"Selected: {project_name}\\n\\nProject details would appear here with full specifications and status information.")
            
    def run_scan(self):
        """Run scan operation"""
        self.footer_status.setText("SCANNING...")
        self.footer_status.setStyleSheet(f"color: {self.colors['tertiary']};")
        QTimer.singleShot(2000, lambda: self.reset_status())
        
    def run_analysis(self):
        """Run analysis operation"""
        self.footer_status.setText("ANALYZING...")
        self.footer_status.setStyleSheet(f"color: {self.colors['tertiary']};")
        QTimer.singleShot(3000, lambda: self.reset_status())
        
    def run_compute(self):
        """Run compute operation"""
        self.footer_status.setText("COMPUTING...")
        self.footer_status.setStyleSheet(f"color: {self.colors['tertiary']};")
        QTimer.singleShot(1500, lambda: self.reset_status())
        
    def run_transmit(self):
        """Run transmit operation"""
        self.footer_status.setText("TRANSMITTING...")
        self.footer_status.setStyleSheet(f"color: {self.colors['tertiary']};")
        QTimer.singleShot(2500, lambda: self.reset_status())
        
    def reset_status(self):
        """Reset status to ready"""
        self.footer_status.setText("READY")
        self.footer_status.setStyleSheet(f"color: {self.colors['success']};")
        
    def return_to_selector(self):
        """Return to interface selector"""
        if self.selector:
            self.selector.show()
            self.close()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create interface with default path
    root_path = Path(__file__).parent.parent.parent
    interface = LCARS24thCentury(root_path)
    interface.show()
    
    sys.exit(app.exec())
