#!/usr/bin/env python3
"""
English Learning Application
A comprehensive application for learning English from A1 to C2 levels
"""

import sys
import os
from pathlib import Path

# Add project root to path
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
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

from .database_manager import DatabaseManager
from .learning_modules import LearningModuleManager
from .progress_tracker import ProgressTracker
from .ui.main_window import EnglishLearningMainWindow
from .ui.dashboard import DashboardWidget
from .ui.dictionary import DictionaryWidget
from .ui.exercises import ExercisesWidget
from .ui.grammar import GrammarWidget
from .ui.progress import ProgressWidget

class EnglishLearningApp(QMainWindow):
    """Main application for English learning"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Initialize core components
        self.learning_manager = LearningModuleManager(self.db_manager)
        self.progress_tracker = ProgressTracker(self.db_manager)
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH  # Use TNG theme for educational feel
        self.colors = get_theme(self.era)
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        
        # Start session tracking
        self.start_session()
    
    def init_ui(self):
        """Initialize the main UI"""
        self.setWindowTitle("English Learning System - LCARS Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create navigation panel (left side)
        self.create_navigation_panel(main_layout)
        
        # Create content area (center)
        self.create_content_area(main_layout)
        
        # Create status panel (right side)
        self.create_status_panel(main_layout)
        
        # Apply LCARS styling
        self.apply_lcars_styling()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
    
    def create_navigation_panel(self, main_layout):
        """Create the navigation panel with LCARS design"""
        nav_frame = QFrame()
        nav_frame.setFixedWidth(250)
        nav_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-right: 2px solid {self.colors['accent']};
            }}
        """)
        
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(10)
        
        # LCARS elbow at top
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setFixedSize(230, 60)
        nav_layout.addWidget(elbow)
        
        # Title
        title = QLabel("ENGLISH LEARNING")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 16px;
            font-weight: bold;
            padding: 10px;
        """)
        nav_layout.addWidget(title)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", "dashboard", self.colors['palette'][1]),
            ("Dictionary", "dictionary", self.colors['palette'][2]),
            ("Exercises", "exercises", self.colors['palette'][3]),
            ("Grammar", "grammar", self.colors['palette'][4]),
            ("Progress", "progress", self.colors['palette'][5]),
        ]
        
        for name, key, color in nav_items:
            btn = LCARSButton(name, color, shape="left")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            self.nav_buttons[key] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        # Exit button
        exit_btn = LCARSButton("EXIT", "#FF0000", shape="left")
        exit_btn.setMinimumHeight(40)
        exit_btn.clicked.connect(self.close)
        nav_layout.addWidget(exit_btn)
        
        main_layout.addWidget(nav_frame)
    
    def create_content_area(self, main_layout):
        """Create the main content area"""
        self.content_stack = QStackedWidget()
        
        # Create different pages
        self.dashboard = DashboardWidget(self.db_manager, self.progress_tracker)
        self.dictionary = DictionaryWidget(self.db_manager)
        self.exercises = ExercisesWidget(self.db_manager, self.learning_manager)
        self.grammar = GrammarWidget(self.db_manager)
        self.progress = ProgressWidget(self.db_manager, self.progress_tracker)
        
        # Add pages to stack
        self.content_stack.addWidget(self.dashboard)  # index 0
        self.content_stack.addWidget(self.dictionary)  # index 1
        self.content_stack.addWidget(self.exercises)  # index 2
        self.content_stack.addWidget(self.grammar)    # index 3
        self.content_stack.addWidget(self.progress)   # index 4
        
        main_layout.addWidget(self.content_stack, 1)
    
    def create_status_panel(self, main_layout):
        """Create the status panel"""
        status_frame = QFrame()
        status_frame.setFixedWidth(300)
        status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000000;
                border-left: 2px solid {self.colors['accent']};
            }}
        """)
        
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 10, 10, 10)
        status_layout.setSpacing(10)
        
        # LCARS elbow at top
        elbow = LCARSElbow("top-right", color=self.colors['accent'])
        elbow.setFixedSize(230, 60)
        status_layout.addWidget(elbow, 0, Qt.AlignmentFlag.AlignRight)
        
        # Current level indicator
        self.level_label = QLabel("CURRENT LEVEL: A1")
        self.level_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['palette'][6]};
        """)
        status_layout.addWidget(self.level_label)
        
        # Progress indicator
        self.progress_label = QLabel("PROGRESS: 0%")
        self.progress_label.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 14px;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['palette'][7]};
        """)
        status_layout.addWidget(self.progress_label)
        
        # Session timer
        self.timer_label = QLabel("SESSION: 00:00")
        self.timer_label.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 14px;
            padding: 10px;
            background-color: #111111;
            border: 1px solid {self.colors['palette'][8]};
        """)
        status_layout.addWidget(self.timer_label)
        
        status_layout.addStretch()
        
        main_layout.addWidget(status_frame)
    
    def apply_lcars_styling(self):
        """Apply LCARS styling to the main window"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #000000;
                color: white;
            }}
            QStackedWidget {{
                background-color: #000000;
                border: none;
            }}
            QLabel {{
                color: white;
                font-family: "Arial", sans-serif;
            }}
        """)
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet(f"""
            QMenuBar {{
                background-color: #000000;
                color: white;
                border-bottom: 1px solid {self.colors['accent']};
            }}
            QMenuBar::item {{
                background-color: transparent;
                padding: 5px 10px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.colors['palette'][0]};
            }}
        """)
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('Import Vocabulary')
        file_menu.addAction('Export Progress')
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # Learning menu
        learning_menu = menubar.addMenu('Learning')
        learning_menu.addAction('Start New Session')
        learning_menu.addAction('Review Mistakes')
        learning_menu.addAction('Practice Pronunciation')
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('User Guide')
        help_menu.addAction('About')
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: #000000;
                color: white;
                border-top: 1px solid {self.colors['accent']};
            }}
        """)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to learn English!")
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect progress tracker updates
        self.progress_tracker.progress_updated.connect(self.update_progress_display)
        
        # Setup session timer
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        self.session_time = 0
    
    def switch_page(self, page_key):
        """Switch to a different page"""
        page_map = {
            'dashboard': 0,
            'dictionary': 1,
            'exercises': 2,
            'grammar': 3,
            'progress': 4
        }
        
        if page_key in page_map:
            self.content_stack.setCurrentIndex(page_map[page_key])
            self.status_bar.showMessage(f"Switched to {page_key.title()}")
    
    def update_progress_display(self):
        """Update progress display"""
        progress = self.progress_tracker.get_overall_progress()
        self.progress_label.setText(f"PROGRESS: {progress:.1f}%")
        
        # Update level if needed
        current_level = self.progress_tracker.get_current_level()
        self.level_label.setText(f"CURRENT LEVEL: {current_level}")
    
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
