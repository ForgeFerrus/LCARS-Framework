"""
LCARS Interface - 29th Century Edition
Futuristic temporal interface with advanced time travel capabilities
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QLabel, QVBoxLayout, QWidget, QPushButton, 
                           QLineEdit, QFormLayout, QTabWidget, QTableWidget, QTableWidgetItem, 
                           QMessageBox, QListWidget, QHBoxLayout, QScrollArea, QFrame, QTreeWidget,
                           QTreeWidgetItem, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
                           QGraphicsRectItem, QGraphicsTextItem, QProgressBar, QSlider)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor, QLinearGradient, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, QRectF, pyqtSignal
from lcars.core.analysis import SpectraAnalyzer
from lcars.core.geant4_wrapper import Simulation, Particle, ParticleType
from lcars.core.project_manager import ProjectManager, ProjectInfo
from lcars.themes.lcars_palette import get_era_palette, get_random_button_color, get_button_color_cycle, LCARSEra
from lcars.themes.theme import Theme
from pathlib import Path
import os
import logging
from lcars.core.file_analyzer import FileAnalyzer
import math

class TemporalDisplay(QGraphicsView):
    """Futuristic temporal coordinate display with animated elements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set dark background
        self.setStyleSheet("background: transparent; border: none;")
        
        # Initialize temporal elements
        self.temporal_rings = []
        self.time_markers = []
        self.current_time = 0
        
        self.setup_temporal_display()
        
    def setup_temporal_display(self):
        """Create animated temporal coordinate system"""
        # Add temporal rings
        for i in range(5):
            ring = QGraphicsEllipseItem(-50 + i*20, -50 + i*20, 100 - i*40, 100 - i*40)
            ring.setPen(QPen(QColor(100, 200, 255, 150 - i*20), 2))
            ring.setBrush(QBrush(QColor(0, 50, 100, 30)))
            self.temporal_rings.append(ring)
            self.scene.addItem(ring)
            
        # Add time markers
        for i in range(8):
            angle = i * 45
            x = 40 * math.cos(math.radians(angle))
            y = 40 * math.sin(math.radians(angle))
            marker = QGraphicsEllipseItem(x-3, y-3, 6, 6)
            marker.setBrush(QBrush(QColor(0, 255, 200)))
            marker.setPen(QPen(QColor(0, 255, 200, 200), 1))
            self.time_markers.append(marker)
            self.scene.addItem(marker)
            
        # Add center temporal core
        core = QGraphicsEllipseItem(-10, -10, 20, 20)
        core.setBrush(QBrush(QColor(0, 150, 255)))
        core.setPen(QPen(QColor(0, 200, 255), 2))
        self.scene.addItem(core)
        
    def update_temporal_state(self, value):
        """Update temporal display based on current time coordinate"""
        self.current_time = value
        
        # Animate rings
        for i, ring in enumerate(self.temporal_rings):
            scale = 1.0 + 0.1 * math.sin(value + i * 0.5)
            ring.setScale(scale)
            
        # Animate markers
        for i, marker in enumerate(self.time_markers):
            angle = (i * 45 + value * 10) % 360
            x = 40 * math.cos(math.radians(angle))
            y = 40 * math.sin(math.radians(angle))
            marker.setPos(x-3, y-3)

class LCARS29thCentury(QMainWindow):
    """29th Century LCARS Interface with temporal capabilities"""
    
    def __init__(self, root_path: Path | None = None, selector=None):
        super().__init__()
        self.root_path = root_path or Path(__file__).parent.parent.parent
        self.selector = selector
        
        # Initialize managers
        self.project_manager = ProjectManager()
        self.file_analyzer = FileAnalyzer()
        
        # Setup interface
        self.setup_window()
        self.setup_colors()
        self.setup_temporal_system()
        self.create_layouts()
        self.create_widgets()
        self.setup_connections()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("LCARS Framework - 29th Century")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
    def setup_colors(self):
        """Set futuristic 29th-century LCARS palette"""
        # Use era palette directly
        self.colors = get_era_palette(LCARSEra.LCARS_29TH)
        
    def setup_temporal_system(self):
        """Initialize temporal coordinate system and animations"""
        self.temporal_timer = QTimer()
        self.temporal_timer.timeout.connect(self.update_temporal_coordinates)
        self.temporal_timer.start(50)  # 20 FPS animation
        
        self.temporal_value = 0
        
    def update_temporal_coordinates(self):
        """Update temporal coordinate display"""
        self.temporal_value += 0.1
        if hasattr(self, 'temporal_display'):
            self.temporal_display.update_temporal_state(self.temporal_value)
            
    def create_layouts(self):
        """Create futuristic LCARS layout with temporal elements"""
        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        
        # Temporal header panel
        self.temporal_header = QFrame()
        self.temporal_header.setFixedHeight(150)
        self.temporal_header.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('background', '#000000')},
                    stop:0.5 {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'},
                    stop:1 {self.colors.get('background', '#000000')});
                border: none;
            }}
        """)
        self.temporal_layout = QHBoxLayout()
        self.temporal_layout.setContentsMargins(20, 10, 20, 10)
        self.temporal_header.setLayout(self.temporal_layout)
        
        # Main content area
        self.content_panel = QFrame()
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.content_panel.setLayout(self.content_layout)
        self.content_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('background', '#000000')};
                border: none;
            }}
        """)
        
        # Left temporal navigation
        self.left_panel = QFrame()
        self.left_panel.setFixedWidth(400)
        self.left_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('background', '#000000')},
                    stop:1 {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'});
                border: none;
            }}
        """)
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(20, 20, 20, 20)
        self.left_layout.setSpacing(15)
        self.left_panel.setLayout(self.left_layout)
        
        # Central temporal display
        self.main_display = QFrame()
        self.main_display.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('background', '#000000')};
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                border-radius: 20px;
            }}
        """)
        self.display_layout = QVBoxLayout()
        self.display_layout.setContentsMargins(20, 20, 20, 20)
        self.display_layout.setSpacing(15)
        self.main_display.setLayout(self.display_layout)
        
        # Right temporal controls
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(250)
        self.right_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'},
                    stop:1 {self.colors.get('background', '#000000')});
                border: none;
            }}
        """)
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_layout.setSpacing(15)
        self.right_panel.setLayout(self.right_layout)
        
        # Footer temporal status
        self.footer_panel = QFrame()
        self.footer_panel.setFixedHeight(80)
        self.footer_layout = QHBoxLayout()
        self.footer_layout.setContentsMargins(20, 10, 20, 10)
        self.footer_panel.setLayout(self.footer_layout)
        self.footer_panel.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('background', '#000000')},
                    stop:0.5 {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'},
                    stop:1 {self.colors.get('background', '#000000')});
                border: none;
            }}
        """)
        
    def create_widgets(self):
        """Create futuristic widgets with temporal elements"""
        self.create_temporal_header()
        self.create_left_panel()
        self.create_main_display()
        self.create_right_panel()
        self.create_footer()
        
        # Assemble layout
        self.content_layout.addWidget(self.left_panel)
        self.content_layout.addWidget(self.main_display)
        self.content_layout.addWidget(self.right_panel)
        
        self.main_layout.addWidget(self.temporal_header)
        self.main_layout.addWidget(self.content_panel)
        self.main_layout.addWidget(self.footer_panel)
        
    def create_temporal_header(self):
        """Create temporal header with coordinate display"""
        # Temporal coordinate display
        self.temporal_display = TemporalDisplay()
        self.temporal_display.setFixedSize(120, 120)
        self.temporal_layout.addWidget(self.temporal_display)
        
        # Title
        title = QLabel("U.S.S. RELATIVITY NCC-474439-G")
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors.get('text', '#FFFFFF')};
            text-shadow: 0 0 10px {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
            padding: 20px;
            background: transparent;
        """)
        self.temporal_layout.addWidget(title)
        
        # Temporal coordinates
        self.temporal_coords = QLabel("TEMPORAL COORDINATES: 29th CENTURY")
        self.temporal_coords.setStyleSheet(f"""
            font-size: 18px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
            padding: 10px;
            background: transparent;
        """)
        self.temporal_layout.addWidget(self.temporal_coords)
        
        # Add stretch
        self.temporal_layout.addStretch()
        
    def create_left_panel(self):
        """Create temporal navigation panel"""
        # Temporal status display
        status_frame = QFrame()
        status_frame.setFixedHeight(200)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                border: none;
                border-radius: 20px;
            }}
        """)
        status_layout = QVBoxLayout()
        
        status_title = QLabel("TEMPORAL SYSTEMS")
        status_title.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 24px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 10px;
            background: transparent;
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_text = QLabel("TEMPORAL DRIVE\nSTANDBY")
        status_text.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 18px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 8px;
            background: transparent;
        """)
        status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(status_text)
        status_frame.setLayout(status_layout)
        self.left_layout.addWidget(status_frame)
        
        # Temporal navigation buttons
        temporal_buttons = [
            ("TIME WARP", self.activate_time_warp),
            ("PARADOX SHIELD", self.activate_paradox_shield),
            ("TEMPORAL DRIVE", self.activate_temporal_drive),
            ("CHRONITON SCAN", self.activate_chroniton_scan)
        ]
        
        for text, slot in temporal_buttons:
            btn = self.create_temporal_button(text, slot)
            self.left_layout.addWidget(btn)
            
        # Temporal progress indicator
        self.temporal_progress = QProgressBar()
        self.temporal_progress.setFixedHeight(30)
        self.temporal_progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
                border-radius: 15px;
                text-align: center;
                color: {self.colors.get('text', '#FFFFFF')};
                background-color: {self.colors.get('background', '#000000')};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#0066FF'};
                border-radius: 13px;
            }}
        """)
        self.temporal_progress.setValue(75)
        self.left_layout.addWidget(self.temporal_progress)
        
        self.left_layout.addStretch()
        
    def create_temporal_button(self, text, slot):
        """Create futuristic temporal button"""
        btn = QPushButton(text)
        btn.setFixedHeight(60)
        
        btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('text', '#FFFFFF')};
                text-align: center;
                padding: 15px 25px;
                border-radius: 30px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('background', '#000000')},
                    stop:0.5 {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'},
                    stop:1 {self.colors.get('background', '#000000')});
            }}
            QPushButton:hover {{
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#0066FF'};
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'},
                    stop:0.5 {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'},
                    stop:1 {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'});
            }}
            QPushButton:pressed {{
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#0033CC'};
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
            }}
        """)
        
        if slot:
            btn.clicked.connect(slot)
            
        return btn
        
    def create_main_display(self):
        """Create central temporal display area"""
        # Create tab widget for temporal content
        self.content_stack = QTabWidget()
        self.content_stack.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {self.colors.get('background', '#000000')};
                border-radius: 15px;
            }}
            QTabBar::tab {{
                background: {self.colors.get('button_colors', ['#00CCFF'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#0033CC'};
                color: {self.colors.get('text', '#FFFFFF')};
                padding: 15px 30px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                min-height: 50px;
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }}
            QTabBar::tab:selected {{
                background: {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                color: {self.colors.get('background', '#000000')};
            }}
        """)
        
        # Add temporal tabs
        self.setup_temporal_projects_tab()
        self.setup_temporal_simulation_tab()
        self.setup_temporal_analysis_tab()
        
        self.display_layout.addWidget(self.content_stack)
        
    def create_right_panel(self):
        """Create temporal control panel"""
        # Temporal status display
        status_frame = QFrame()
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
                border: none;
                border-radius: 20px;
            }}
        """)
        status_layout = QVBoxLayout()
        
        status_title = QLabel("TEMPORAL STATUS")
        status_title.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 18px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 8px;
            background: transparent;
        """)
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.temporal_status = QLabel("ONLINE")
        self.temporal_status.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 16px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            padding: 5px;
            background: transparent;
        """)
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.temporal_status)
        status_frame.setLayout(status_layout)
        self.right_layout.addWidget(status_frame)
        
        # Temporal controls
        controls_frame = QFrame()
        controls_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#0066FF'};
                border: none;
                border-radius: 15px;
            }}
        """)
        controls_layout = QVBoxLayout()
        
        # Time coordinate slider
        time_label = QLabel("TIME COORDINATE")
        time_label.setStyleSheet(f"""
            color: {self.colors.get('background', '#000000')};
            font-size: 14px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 5px;
            background: transparent;
        """)
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {self.colors.get('background', '#000000')};
                height: 8px;
                background: {self.colors.get('background', '#000000')};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {self.colors.get('text', '#FFFFFF')};
                border: 1px solid {self.colors.get('text', '#FFFFFF')};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        self.time_slider.setRange(0, 100)
        self.time_slider.setValue(50)
        
        controls_layout.addWidget(time_label)
        controls_layout.addWidget(self.time_slider)
        controls_frame.setLayout(controls_layout)
        self.right_layout.addWidget(controls_frame)
        
        self.right_layout.addStretch()
        
    def create_footer(self):
        """Create temporal footer with status"""
        # Temporal status label
        status_text = QLabel("TEMPORAL MATRIX STABLE - CHRONITON LEVELS NOMINAL")
        status_text.setStyleSheet(f"""
            color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
            font-size: 20px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 15px;
            text-shadow: 0 0 5px {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
        """)
        self.footer_layout.addWidget(status_text)
        
        # Add stretch
        self.footer_layout.addStretch()
        
        # Control buttons
        back_btn = QPushButton("RETURN TO PRESENT")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('text', '#FFFFFF')};
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#0033CC'};
                border: none;
                border-radius: 20px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 10px 20px;
            }}
        """)
        back_btn.clicked.connect(self.return_to_selector)
        self.footer_layout.addWidget(back_btn)
        
    def setup_connections(self):
        """Set up signal connections"""
        # Time slider connection
        self.time_slider.valueChanged.connect(self.update_time_coordinate)
        
    def update_time_coordinate(self, value):
        """Update temporal coordinate display"""
        self.temporal_coords.setText(f"TEMPORAL COORDINATES: {value}th CENTURY")
        
    def activate_time_warp(self):
        """Activate time warp drive"""
        QMessageBox.information(self, "Time Warp", "Time warp drive activated!\nTemporal displacement initiated.")
        self.temporal_status.setText("TIME WARP")
        
    def activate_paradox_shield(self):
        """Activate paradox shield"""
        QMessageBox.information(self, "Paradox Shield", "Paradox shield activated!\nTemporal protection engaged.")
        self.temporal_status.setText("SHIELD ACTIVE")
        
    def activate_temporal_drive(self):
        """Activate temporal drive"""
        QMessageBox.information(self, "Temporal Drive", "Temporal drive activated!\nChroniton flow stabilized.")
        self.temporal_status.setText("DRIVE ACTIVE")
        
    def activate_chroniton_scan(self):
        """Activate chroniton scan"""
        QMessageBox.information(self, "Chroniton Scan", "Chroniton scan initiated!\nAnalyzing temporal anomalies.")
        self.temporal_status.setText("SCANNING")
        
    def setup_temporal_projects_tab(self):
        """Setup temporal projects tab"""
        projects_tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("TEMPORAL PROJECT ARCHIVE")
        title.setStyleSheet(f"""
            color: {self.colors.get('text', '#FFFFFF')};
            font-size: 28px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 20px;
            text-shadow: 0 0 10px {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Project list with temporal styling
        project_list = QListWidget()
        project_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.colors.get('background', '#000000')};
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                border-radius: 10px;
                color: {self.colors.get('text', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 14px;
                padding: 10px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {self.colors.get('button_colors', ['#00CCFF'])[3] if len(self.colors.get('button_colors', [])) > 3 else '#0033CC'};
            }}
            QListWidget::item:selected {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
                color: {self.colors.get('background', '#000000')};
            }}
        """)
        
        # Add sample temporal projects
        temporal_projects = [
            "Temporal Displacement Study",
            "Chroniton Particle Analysis",
            "Paradox Resolution Protocol",
            "Time Stream Mapping",
            "Future Timeline Projection"
        ]
        
        for project in temporal_projects:
            project_list.addItem(project)
            
        layout.addWidget(project_list)
        projects_tab.setLayout(layout)
        self.content_stack.addTab(projects_tab, "PROJECTS")
        
    def setup_temporal_simulation_tab(self):
        """Setup temporal simulation tab"""
        simulation_tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("TEMPORAL SIMULATION MATRIX")
        title.setStyleSheet(f"""
            color: {self.colors.get('text', '#FFFFFF')};
            font-size: 28px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 20px;
            text-shadow: 0 0 10px {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Simulation status
        sim_status = QLabel("TEMPORAL SIMULATION READY\nCHRONITON LEVELS: NOMINAL")
        sim_status.setStyleSheet(f"""
            color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
            font-size: 20px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 30px;
            text-align: center;
        """)
        sim_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sim_status)
        
        # Simulation controls
        controls_layout = QHBoxLayout()
        
        start_btn = QPushButton("INITIATE TEMPORAL SIMULATION")
        start_btn.setStyleSheet(f"""
            QPushButton {{
                color: {self.colors.get('background', '#000000')};
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                border: none;
                border-radius: 25px;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
                font-size: 16px;
                padding: 15px 25px;
            }}
        """)
        
        controls_layout.addStretch()
        controls_layout.addWidget(start_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        layout.addStretch()
        
        simulation_tab.setLayout(layout)
        self.content_stack.addTab(simulation_tab, "SIMULATION")
        
    def setup_temporal_analysis_tab(self):
        """Setup temporal analysis tab"""
        analysis_tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("TEMPORAL ANALYSIS CONSOLE")
        title.setStyleSheet(f"""
            color: {self.colors.get('text', '#FFFFFF')};
            font-size: 28px;
            font-family: 'Swiss 911', 'Arial', sans-serif;
            font-weight: bold;
            padding: 20px;
            text-shadow: 0 0 10px {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Analysis table with temporal styling
        analysis_table = QTableWidget()
        analysis_table.setColumnCount(4)
        analysis_table.setHorizontalHeaderLabels(["TEMPORAL EVENT", "CHRONITON LEVEL", "PARADOX RISK", "TIMELINE STABILITY"])
        analysis_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.colors.get('background', '#000000')};
                border: 2px solid {self.colors.get('button_colors', ['#00CCFF'])[0] if len(self.colors.get('button_colors', [])) > 0 else '#00CCFF'};
                gridline-color: {self.colors.get('button_colors', ['#00CCFF'])[1] if len(self.colors.get('button_colors', [])) > 1 else '#0099FF'};
                color: {self.colors.get('text', '#FFFFFF')};
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-size: 14px;
            }}
            QHeaderView::section {{
                background-color: {self.colors.get('button_colors', ['#00CCFF'])[2] if len(self.colors.get('button_colors', [])) > 2 else '#0066FF'};
                color: {self.colors.get('background', '#000000')};
                padding: 10px;
                border: none;
                font-family: 'Swiss 911', 'Arial', sans-serif;
                font-weight: bold;
            }}
        """)
        
        # Add sample temporal analysis data
        temporal_data = [
            ("Time Displacement", "75.3%", "LOW", "STABLE"),
            ("Chroniton Surge", "89.7%", "MEDIUM", "FLUCTUATING"),
            ("Paradox Detection", "23.1%", "HIGH", "CRITICAL"),
            ("Timeline Convergence", "95.8%", "MINIMAL", "OPTIMAL")
        ]
        
        analysis_table.setRowCount(len(temporal_data))
        for row, (event, level, risk, stability) in enumerate(temporal_data):
            analysis_table.setItem(row, 0, QTableWidgetItem(event))
            analysis_table.setItem(row, 1, QTableWidgetItem(level))
            analysis_table.setItem(row, 2, QTableWidgetItem(risk))
            analysis_table.setItem(row, 3, QTableWidgetItem(stability))
            
        layout.addWidget(analysis_table)
        analysis_tab.setLayout(layout)
        self.content_stack.addTab(analysis_tab, "ANALYSIS")
        
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
    window = LCARS29thCentury(root_path=root_path)
    window.show()
    
    sys.exit(app.exec())
