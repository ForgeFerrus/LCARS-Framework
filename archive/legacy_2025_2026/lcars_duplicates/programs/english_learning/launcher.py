#!/usr/bin/env python3
"""
English Learning Application
A comprehensive application for learning English from A1 to C2 levels
"""

import sys
import os
from pathlib import Path

# previous hacks to manipulate sys.path were unnecessary once the
# package is imported properly.  Relative imports are now used instead.
# (retained here as comment for historical context)
proj_root = Path(__file__).resolve().parents[1]
if str(proj_root) not in sys.path:
        sys.path.insert(0, str(proj_root))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QFrame, QSplitter,
    QMenuBar, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap

from lcars.themes.lcars_palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.modules.sound_manager import get_sound_manager

from .database_manager import DatabaseManager
from .learning_modules import LearningModuleManager
from .progress_tracker import ProgressTracker

try:
    from .apps.linguistic_matrix import LinguisticMatrixLCARS
except ImportError:
    # fallback if package imports fail (should not happen when installed correctly)
    from .apps.linguistic_matrix import LinguisticMatrixLCARS

class EnglishLearningApp(QMainWindow):
    """Complete English Learning Application"""
    
    def __init__(self, era=LCARSEra.LCARS_24TH):
        super().__init__()
        
        self.era = era
        self.colors = get_theme(era)
        self.sound_manager = get_sound_manager()
        self.linguistic_matrix = None
        
        # Initialize backend components (previously in main.py)
        self.db_manager = DatabaseManager()
        self.learning_manager = LearningModuleManager(self.db_manager)
        self.progress_tracker = ProgressTracker(self.db_manager)
        
        self.init_ui()
        self.setup_connections()
        
    def init_ui(self):
        """Initialize the complete UI"""
        self.setWindowTitle("◤ ENGLISH LEARNING SYSTEM - LCARS")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create LCARS interface
        self.create_lcars_interface(main_layout)
        
        # Apply LCARS styling
        self.apply_lcars_styling()
        
    def create_lcars_interface(self, main_layout):
        """Create complete LCARS interface"""
        
        # Left panel - Navigation
        self.create_navigation_panel(main_layout)
        
        # Center - Main content
        self.create_main_content(main_layout)
        
        # Right panel - Status
        self.create_status_panel(main_layout)
        
    def create_navigation_panel(self, main_layout):
        """Create left navigation panel"""
        nav_frame = QFrame()
        nav_frame.setFixedWidth(250)
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-right: 2px solid {self.colors['accent']};
            }}
        """)
        
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(15, 15, 15, 15)
        nav_layout.setSpacing(12)
        
        # LCARS elbow at top
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setFixedSize(220, 70)
        nav_layout.addWidget(elbow)
        
        # System title
        title = QLabel("ENGLISH LEARNING")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['accent']};
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(title)
        
        # Navigation buttons
        nav_buttons = [
            ("◤ MAIN DISPLAY", "main", self.colors['palette'][1]),
            ("◤ VOCABULARY", "vocabulary", self.colors['palette'][2]),
            ("◤ EXERCISES", "exercises", self.colors['palette'][3]),
            ("◤ GRAMMAR", "grammar", self.colors['palette'][4]),
            ("◤ PROGRESS", "progress", self.colors['palette'][5]),
            ("◤ SETTINGS", "settings", self.colors['palette'][6])
        ]
        
        self.nav_buttons = {}
        for btn_text, btn_key, color in nav_buttons:
            btn = LCARSButton(btn_text, color)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, k=btn_key: self.switch_panel(k))
            self.nav_buttons[btn_key] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Exit button
        exit_btn = LCARSButton("◤ EXIT", "#FF0000")
        exit_btn.setMinimumHeight(40)
        exit_btn.clicked.connect(self.close)
        nav_layout.addWidget(exit_btn)
        
        main_layout.addWidget(nav_frame)
        
    def create_main_content(self, main_layout):
        """Create main content area"""
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-top: 2px solid {self.colors['accent']};
                border-bottom: 2px solid {self.colors['accent']};
            }}
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header with LCARS contour
        self.create_content_header(content_layout)
        
        # Content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("""
            QStackedWidget {
                background-color: #000000;
                border: none;
            }
        """)
        
        # create pages for each navigation key
        self.pages = {}
        self.pages['main'] = QWidget()
        self.pages['vocabulary'] = __import__('lcars.programs.english_learning.ui.dictionary', fromlist=['DictionaryWidget']).DictionaryWidget(self.db_manager)
        self.pages['exercises'] = __import__('lcars.programs.english_learning.ui.exercises', fromlist=['ExercisesWidget']).ExercisesWidget(self.db_manager, self.learning_manager)
        self.pages['grammar'] = __import__('lcars.programs.english_learning.ui.grammar', fromlist=['GrammarWidget']).GrammarWidget(self.db_manager)
        self.pages['progress'] = __import__('lcars.programs.english_learning.ui.progress', fromlist=['ProgressWidget']).ProgressWidget(self.db_manager, self.progress_tracker)
        # main page: embed linguistic matrix if available
        try:
            self.linguistic_matrix = LinguisticMatrixLCARS(self.era)
            self.linguistic_matrix.initialize()
            if getattr(self.linguistic_matrix, 'window', None) is not None:
                self.pages['main'] = self.linguistic_matrix.window
        except Exception:
            pass
        # add all pages to stack
        for w in self.pages.values():
            self.content_stack.addWidget(w)
        
        content_layout.addWidget(self.content_stack, 1)
        
        main_layout.addWidget(content_frame, 1)
        
    def create_content_header(self, layout):
        """Create simple header"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        # plain title only (no LCARS contour to avoid extraneous shapes)
        title = QLabel("LINGUISTIC MATRIX - ACTIVE")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 24px;
            font-weight: bold;
            padding: 15px;
        """)
        header_layout.addWidget(title)
        layout.addWidget(header_frame)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)
        
        # Status indicator
        self.status_indicator = QLabel("◤ SYSTEM: ONLINE")
        self.status_indicator.setStyleSheet(f"""
            color: #00FF00;
            font-size: 16px;
            font-weight: bold;
            padding: 15px;
            background-color: #001100;
            border: 2px solid #00FF00;
        """)
        header_layout.addWidget(self.status_indicator)
        
        layout.addWidget(header_frame)
        
    def create_status_panel(self, main_layout):
        """Create right status panel"""
        status_frame = QFrame()
        status_frame.setFixedWidth(300)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-left: 2px solid {self.colors['accent']};
            }}
        """)
        
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(15, 15, 15, 15)
        status_layout.setSpacing(12)
        
        # LCARS elbow at top
        elbow = LCARSElbow("top-right", color=self.colors['accent'])
        elbow.setFixedSize(220, 70)
        status_layout.addWidget(elbow, 0, Qt.AlignmentFlag.AlignRight)
        
        # System status
        status_title = QLabel("◤ SYSTEM STATUS")
        status_title.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['palette'][7]};
            border-radius: 5px;
        """)
        status_layout.addWidget(status_title)
        
        # Status indicators
        status_items = [
            ("Database", "#00FF00", "ONLINE"),
            ("Learning Engine", "#00FF00", "ACTIVE"),
            ("Progress Tracker", "#00FF00", "MONITORING"),
            ("Audio System", "#FFFF00", "READY"),
            ("Achievement System", "#00FF00", "ACTIVE")
        ]
        
        for item_name, color, status in status_items:
            item_layout = QHBoxLayout()
            
            name_label = QLabel(f"◤ {item_name}:")
            name_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")
            item_layout.addWidget(name_label)
            
            status_label = QLabel(status)
            status_label.setStyleSheet(f"color: {color}; font-size: 12px;")
            item_layout.addWidget(status_label)
            
            status_layout.addLayout(item_layout)
        
        status_layout.addStretch()
        
        # Session info
        session_title = QLabel("◤ SESSION INFO")
        session_title.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['palette'][8]};
            border-radius: 5px;
        """)
        status_layout.addWidget(session_title)
        
        # current level display (needed by setup_connections)
        self.level_label = QLabel("CURRENT LEVEL: A1")
        self.level_label.setStyleSheet(f"color: {self.colors['palette'][2]}; font-size: 14px;")
        status_layout.addWidget(self.level_label)
        
        self.session_timer_label = QLabel("00:00:00")
        self.session_timer_label.setStyleSheet(f"""
            color: {self.colors['palette'][9]};
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
            background-color: #000000;
            border: 2px solid {self.colors['palette'][9]};
            border-radius: 5px;
        """)
        self.session_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.session_timer_label)
        
        main_layout.addWidget(status_frame)
        
    def apply_lcars_styling(self):
        """Apply LCARS styling to the entire application"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #000000;
                color: white;
                font-family: "Arial", sans-serif;
            }}
            QLabel {{
                color: white;
            }}
        """)
        
    def setup_connections(self):
        """Setup signal connections"""
        # Setup session timer
        self.session_start_time = None
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        # Update level if needed
        current_level = self.progress_tracker.get_current_level()
        self.level_label.setText(f"CURRENT LEVEL: {current_level}")

    def switch_panel(self, key):
        """Switch content stack to named page."""
        if hasattr(self, 'pages') and key in self.pages:
            widget = self.pages[key]
            if widget:
                self.content_stack.setCurrentWidget(widget)
    
    def start_session(self):
        """Start a learning session"""
        self.session_time = 0
        self.session_timer.start(1000)  # Update every second
        self.progress_tracker.start_session()
    
    def update_session_timer(self):
        """Update session timer display"""
        self.session_time += 1
        minutes = self.session_time // 60
        seconds = self.session_time % 60
        self.timer_label.setText(f"SESSION: {minutes:02d}:{seconds:02d}")
    
    def closeEvent(self, event):
        """Handle application close"""
        # End the current session
        self.progress_tracker.end_session(self.session_time)
        
        # Save any unsaved data
        self.db_manager.close()
        
        # Confirm exit
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Are you sure you want to exit? Your progress will be saved.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("English Learning System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LCARS Framework")
    
    # Create and show main window
    window = EnglishLearningApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
