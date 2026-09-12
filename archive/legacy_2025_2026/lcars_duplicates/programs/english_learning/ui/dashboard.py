"""
Dashboard Widget for English Learning Application
Main dashboard showing progress, recent activity, and quick access to features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea,
    QGridLayout, QPushButton, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from lcars.themes.palette import LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class DashboardWidget(QWidget):
    """Main dashboard widget"""
    
    # Signals
    start_exercise = pyqtSignal(str)  # exercise type
    view_dictionary = pyqtSignal()
    view_grammar = pyqtSignal()
    view_progress = pyqtSignal()
    
    def __init__(self, db_manager, progress_tracker):
        super().__init__()
        self.db = db_manager
        self.progress_tracker = progress_tracker
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        self.init_ui()
        self.setup_connections()
        self.update_dashboard()
    
    def init_ui(self):
        """Initialize the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left column - Progress and Stats
        left_column = QVBoxLayout()
        self.create_progress_section(left_column)
        self.create_stats_section(left_column)
        content_layout.addLayout(left_column)
        
        # Right column - Quick Actions and Recent Activity
        right_column = QVBoxLayout()
        self.create_quick_actions(right_column)
        self.create_recent_activity(right_column)
        content_layout.addLayout(right_column)
        
        layout.addLayout(content_layout)
        
        # Apply styling
        self.apply_styling()
    
    def create_header(self, layout):
        """Create the header section"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # LCARS elbow
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setMinimumSize(200, 80)
        header_layout.addWidget(elbow)
        
        # Title
        title = QLabel("ENGLISH LEARNING DASHBOARD")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 24px;
            font-weight: normal;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)
        
        # Status indicator
        self.status_label = QLabel("STATUS: READY")
        self.status_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 16px;
            font-weight: normal;
            padding: 20px;
            background-color: #111111;
            border: 2px solid {self.colors['palette'][6]};
        """)
        header_layout.addWidget(self.status_label)
        
        layout.addWidget(header_frame)
    
    def create_progress_section(self, layout):
        """Create the progress section"""
        progress_frame = QFrame()
        progress_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][1]};
                border-radius: 10px;
            }}
        """)
        
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ LEARNING PROGRESS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        progress_layout.addWidget(title)
        
        # Current level
        self.level_label = QLabel("Current Level: A1")
        self.level_label.setStyleSheet(f"""
            color: white;
            font-size: 16px;
            margin: 5px 0;
        """)
        progress_layout.addWidget(self.level_label)
        
        # Overall progress bar
        progress_label = QLabel("Overall Progress")
        progress_label.setStyleSheet("color: white; font-size: 14px;")
        progress_layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors['palette'][2]};
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: normal;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['palette'][2]};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        # Level requirements
        self.requirements_label = QLabel("Loading requirements...")
        self.requirements_label.setStyleSheet("""
            color: #CCCCCC;
            font-size: 12px;
            margin-top: 10px;
        """)
        progress_layout.addWidget(self.requirements_label)
        
        layout.addWidget(progress_frame)
    
    def create_stats_section(self, layout):
        """Create the statistics section"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][3]};
                border-radius: 10px;
            }}
        """)
        
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ STATISTICS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][3]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        stats_layout.addWidget(title)
        
        # Stats grid
        stats_grid = QGridLayout()
        
        # Words learned
        self.words_learned_label = QLabel("0")
        self.words_learned_label.setStyleSheet(f"""
            color: {self.colors['palette'][4]};
            font-size: 24px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Words Learned:"), 0, 0)
        stats_grid.addWidget(self.words_learned_label, 0, 1)
        
        # Accuracy
        self.accuracy_label = QLabel("0%")
        self.accuracy_label.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 24px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Accuracy:"), 1, 0)
        stats_grid.addWidget(self.accuracy_label, 1, 1)
        
        # Study streak
        self.streak_label = QLabel("0 days")
        self.streak_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 24px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Study Streak:"), 2, 0)
        stats_grid.addWidget(self.streak_label, 2, 1)
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_frame)
    
    def create_quick_actions(self, layout):
        """Create quick action buttons"""
        actions_frame = QFrame()
        actions_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][4]};
                border-radius: 10px;
            }}
        """)
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ QUICK ACTIONS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][4]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        actions_layout.addWidget(title)
        
        # Action buttons
        actions = [
            ("Start Vocabulary", "vocabulary", self.colors['palette'][0]),
            ("Practice Grammar", "grammar", self.colors['palette'][1]),
            ("Learn Phrases", "phrases", self.colors['palette'][2]),
            ("Take Test", "test", self.colors['palette'][3]),
            ("Review Words", "review", self.colors['palette'][5])
        ]
        
        for action_name, action_type, color in actions:
            btn = LCARSButton(action_name, color)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, t=action_type: self.start_exercise.emit(t))
            actions_layout.addWidget(btn)
        
        layout.addWidget(actions_frame)
    
    def create_recent_activity(self, layout):
        """Create recent activity section"""
        activity_frame = QFrame()
        activity_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][5]};
                border-radius: 10px;
            }}
        """)
        
        activity_layout = QVBoxLayout(activity_frame)
        activity_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ RECENT ACTIVITY")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        activity_layout.addWidget(title)
        
        # Activity text
        self.activity_text = QTextEdit()
        self.activity_text.setReadOnly(True)
        self.activity_text.setMaximumHeight(200)
        self.activity_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: #00FF00;
                border: 1px solid {self.colors['palette'][5]};
                font-family: "Courier New", monospace;
                font-size: 12px;
            }}
        """)
        self.activity_text.setText("Loading recent activity...")
        activity_layout.addWidget(self.activity_text)
        
        layout.addWidget(activity_frame)
    
    def apply_styling(self):
        """Apply overall styling"""
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: white;
                font-family: "Arial", sans-serif;
            }
            QLabel {
                color: white;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Connect progress tracker signals
        self.progress_tracker.progress_updated.connect(self.update_dashboard)
        self.progress_tracker.achievement_unlocked.connect(self.on_achievement_unlocked)
        self.progress_tracker.level_up.connect(self.on_level_up)
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(30000)  # Update every 30 seconds
    
    def update_dashboard(self):
        """Update dashboard with current data"""
        # Update progress
        overall_progress = self.progress_tracker.get_overall_progress()
        self.progress_bar.setValue(int(overall_progress))
        
        # Update level
        current_level = self.progress_tracker.get_current_level()
        self.level_label.setText(f"Current Level: {current_level}")
        
        # Update requirements
        next_level_reqs = self.progress_tracker.get_next_level_requirements()
        reqs_text = f"Next Level: {next_level_reqs['next_level']}\n"
        reqs = next_level_reqs['requirements']
        reqs_text += f"Words: {reqs.get('words', 0)} | "
        reqs_text += f"Accuracy: {reqs.get('accuracy', 0)}% | "
        reqs_text += f"Sessions: {reqs.get('sessions', 0)}"
        self.requirements_label.setText(reqs_text)
        
        # Update statistics
        stats = self.progress_tracker.get_learning_statistics()
        if 'words' in stats:
            words_stats = stats['words']
            self.words_learned_label.setText(str(words_stats.get('learned_words', 0)))
            accuracy = (words_stats.get('accuracy_rate') or 0) * 100
            self.accuracy_label.setText(f"{accuracy:.1f}%")
        
        # Update streak (placeholder)
        self.streak_label.setText("0 days")  # Would calculate actual streak
        
        # Update recent activity
        self.update_recent_activity()
        
        # Update status
        self.status_label.setText("STATUS: ACTIVE")
    
    def update_recent_activity(self):
        """Update recent activity display"""
        weekly_stats = self.progress_tracker.get_weekly_progress()
        
        activity_text = "=== RECENT ACTIVITY ===\n\n"
        
        if weekly_stats:
            activity_text += f"Weekly Sessions: {weekly_stats.get('session_count', 0)}\n"
            activity_text += f"Study Time: {weekly_stats.get('total_minutes', 0)} minutes\n"
            activity_text += f"Words Learned: {weekly_stats.get('total_words', 0)}\n"
            activity_text += f"Exercises: {weekly_stats.get('total_exercises', 0)}\n"
            avg_score = weekly_stats.get('avg_score') or 0
            activity_text += f"Average Score: {avg_score:.1f}%\n"
        else:
            activity_text += "No recent activity found.\n"
            activity_text += "Start learning to see your progress here!"
        
        # Add recent achievements
        achievements = self.progress_tracker.get_achievements()
        unlocked_achievements = [a for a in achievements if a['unlocked']]
        
        if unlocked_achievements:
            activity_text += "\n=== RECENT ACHIEVEMENTS ===\n"
            for achievement in unlocked_achievements[-3:]:  # Show last 3
                activity_text += f"🏆 {achievement['name']}\n"
                activity_text += f"   {achievement['description']}\n"
        
        self.activity_text.setText(activity_text)
    
    def on_achievement_unlocked(self, achievement_name):
        """Handle achievement unlock"""
        self.status_label.setText(f"ACHIEVEMENT: {achievement_name}")
        # Could show a notification dialog
    
    def on_level_up(self, new_level):
        """Handle level up"""
        self.status_label.setText(f"LEVEL UP: {new_level}")
        # Could show a celebration dialog
