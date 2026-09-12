"""
English Learning Application
LCARS-styled main application window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QStackedWidget, QMenuBar, QStatusBar, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QCloseEvent

from lcars.themes.palette import LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class EnglishLearning(QMainWindow):
    """Main application window with LCARS styling"""
    
    # Signals
    application_closing = pyqtSignal()
    
    def __init__(self, db_manager, progress_tracker):
        super().__init__()
        
        self.db_manager = db_manager
        self.progress_tracker = progress_tracker
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        # Initialize UI
        self.init_ui()
        self.setup_connections()
        self.apply_lcars_styling()
        
        # Start session tracking
        self.start_session_timer()
    
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
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
    
    def create_navigation_panel(self, main_layout):
        """Create the navigation panel with LCARS design"""
        nav_frame = QFrame()
        nav_frame.setMinimumWidth(250)
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
        elbow.setMinimumSize(230, 60)
        nav_layout.addWidget(elbow)
        
        # Title
        title = QLabel("ENGLISH LEARNING")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 16px;
            font-weight: normal;
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
        
        # Content will be added by the main application
        main_layout.addWidget(self.content_stack, 1)
    
    def create_status_panel(self, main_layout):
        """Create the status panel"""
        status_frame = QFrame()
        status_frame.setMinimumWidth(300)
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
        elbow.setMinimumSize(230, 60)
        status_layout.addWidget(elbow, 0, Qt.AlignmentFlag.AlignRight)
        
        # Current level indicator
        self.level_label = QLabel("CURRENT LEVEL: A1")
        self.level_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 14px;
            font-weight: normal;
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
    
    def add_page(self, widget, page_key):
        """Add a page to the content stack"""
        self.content_stack.addWidget(widget)
        # Store mapping for easy access
        if not hasattr(self, 'page_map'):
            self.page_map = {}
        self.page_map[page_key] = self.content_stack.count() - 1
    
    def switch_page(self, page_key):
        """Switch to a different page"""
        if hasattr(self, 'page_map') and page_key in self.page_map:
            self.content_stack.setCurrentIndex(self.page_map[page_key])
            self.status_bar.showMessage(f"Switched to {page_key.title()}")
    
    def update_progress_display(self):
        """Update progress display"""
        progress = self.progress_tracker.get_overall_progress()
        self.progress_label.setText(f"PROGRESS: {progress:.1f}%")
        
        # Update level if needed
        current_level = self.progress_tracker.get_current_level()
        self.level_label.setText(f"CURRENT LEVEL: {current_level}")
    
    def start_session_timer(self):
        """Start session timer"""
        self.session_time = 0
        self.session_timer.start(1000)  # Update every second
        self.progress_tracker.start_session()
    
    def update_session_timer(self):
        """Update session timer display"""
        self.session_time += 1
        minutes = self.session_time // 60
        seconds = self.session_time % 60
        self.timer_label.setText(f"SESSION: {minutes:02d}:{seconds:02d}")
    
    def closeEvent(self, event: QCloseEvent):
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
            self.application_closing.emit()
            event.accept()
        else:
            event.ignore()
    
    def show_about_dialog(self):
        """Show about dialog"""
        about_text = """
        English Learning System v1.0.0
        
        A comprehensive application for learning English from A1 to C2 levels.
        
        Features:
        • Interactive vocabulary exercises
        • Grammar lessons and practice
        • Progress tracking
        • LCARS interface design
        • Achievement system
        
        Built with LCARS Framework
        """
        
        QMessageBox.about(self, "About English Learning System", about_text)
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
        English Learning System - User Guide
        
        Getting Started:
        1. Dashboard - View your progress and start learning
        2. Dictionary - Search and study vocabulary
        3. Exercises - Practice with interactive exercises
        4. Grammar - Learn grammar rules
        5. Progress - Track your learning statistics
        
        Tips:
        • Practice daily for best results
        • Review words you've learned
        • Complete exercises to improve accuracy
        • Track your progress regularly
        
        Keyboard Shortcuts:
        • Ctrl+N - New session
        • Ctrl+S - Save progress
        • Ctrl+Q - Quit application
        """
        
        QMessageBox.information(self, "User Guide", guide_text)
