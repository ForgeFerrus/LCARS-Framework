"""
Progress Widget for English Learning Application
Displays learning progress, statistics, and achievements
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QListWidget, QListWidgetItem, QScrollArea, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from lcars.themes.palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class ProgressWidget(QWidget):
    """Progress tracking and statistics widget"""
    
    # Signals
    export_data = pyqtSignal()
    reset_progress = pyqtSignal()
    
    def __init__(self, db_manager, progress_tracker):
        super().__init__()
        self.db = db_manager
        self.progress_tracker = progress_tracker
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        self.init_ui()
        self.setup_connections()
        self.update_progress_display()
    
    def init_ui(self):
        """Initialize the progress UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left column - Overall progress and level info
        left_column = QVBoxLayout()
        self.create_overall_progress_section(left_column)
        self.create_level_progress_section(left_column)
        content_layout.addLayout(left_column)
        
        # Right column - Statistics and achievements
        right_column = QVBoxLayout()
        self.create_statistics_section(right_column)
        self.create_achievements_section(right_column)
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
        title = QLabel("LEARNING PROGRESS")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 24px;
            font-weight: normal;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)
        
        # Action buttons
        self.export_btn = LCARSButton("Export", self.colors['palette'][1])
        self.export_btn.clicked.connect(self.export_data.emit)
        header_layout.addWidget(self.export_btn)
        
        layout.addWidget(header_frame)
    
    def create_overall_progress_section(self, layout):
        """Create the overall progress section"""
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
        title = QLabel("◤ OVERALL PROGRESS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        progress_layout.addWidget(title)
        
        # Current level display
        self.current_level_label = QLabel("A1 - BEGINNER")
        self.current_level_label.setStyleSheet(f"""
            color: {self.colors['palette'][2]};
            font-size: 24px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        self.current_level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.current_level_label)
        
        # Overall progress bar
        progress_label = QLabel("Total Progress")
        progress_label.setStyleSheet("color: white; font-size: 14px;")
        progress_layout.addWidget(progress_label)
        
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors['palette'][3]};
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: normal;
                font-size: 14px;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['palette'][3]};
                border-radius: 3px;
            }}
        """)
        self.overall_progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.overall_progress_bar)
        
        # Progress stats
        stats_grid = QGridLayout()
        
        self.words_learned_label = QLabel("0")
        self.words_learned_label.setStyleSheet(f"""
            color: {self.colors['palette'][4]};
            font-size: 20px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Words Learned:"), 0, 0)
        stats_grid.addWidget(self.words_learned_label, 0, 1)
        
        self.accuracy_label = QLabel("0%")
        self.accuracy_label.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 20px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Accuracy:"), 1, 0)
        stats_grid.addWidget(self.accuracy_label, 1, 1)
        
        self.study_time_label = QLabel("0 min")
        self.study_time_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 20px;
            font-weight: normal;
        """)
        stats_grid.addWidget(QLabel("Study Time:"), 2, 0)
        stats_grid.addWidget(self.study_time_label, 2, 1)
        
        progress_layout.addLayout(stats_grid)
        
        layout.addWidget(progress_frame)
    
    def create_level_progress_section(self, layout):
        """Create the level progress section"""
        level_frame = QFrame()
        level_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][2]};
                border-radius: 10px;
            }}
        """)
        
        level_layout = QVBoxLayout(level_frame)
        level_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ LEVEL REQUIREMENTS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][2]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        level_layout.addWidget(title)
        
        # Next level info
        self.next_level_label = QLabel("Next Level: A2")
        self.next_level_label.setStyleSheet(f"""
            color: {self.colors['palette'][3]};
            font-size: 16px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        level_layout.addWidget(self.next_level_label)
        
        # Requirements progress bars
        requirements = [
            ("Words", "words_progress", self.colors['palette'][4]),
            ("Accuracy", "accuracy_progress", self.colors['palette'][5]),
            ("Sessions", "sessions_progress", self.colors['palette'][6])
        ]
        
        for req_name, attr_name, color in requirements:
            req_label = QLabel(f"{req_name}:")
            req_label.setStyleSheet("color: white; font-size: 14px;")
            level_layout.addWidget(req_label)
            
            progress_bar = QProgressBar()
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {color};
                    border-radius: 3px;
                    text-align: center;
                    color: white;
                    font-size: 12px;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 2px;
                }}
            """)
            progress_bar.setRange(0, 100)
            setattr(self, attr_name, progress_bar)
            level_layout.addWidget(progress_bar)
        
        layout.addWidget(level_frame)
    
    def create_statistics_section(self, layout):
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
            margin-bottom: 15px;
        """)
        stats_layout.addWidget(title)
        
        # Time period selector
        period_layout = QHBoxLayout()
        
        self.weekly_btn = LCARSButton("Weekly", self.colors['palette'][4])
        self.weekly_btn.setCheckable(True)
        self.weekly_btn.setChecked(True)
        self.weekly_btn.clicked.connect(lambda: self.update_statistics('weekly'))
        period_layout.addWidget(self.weekly_btn)
        
        self.monthly_btn = LCARSButton("Monthly", self.colors['palette'][5])
        self.monthly_btn.setCheckable(True)
        self.monthly_btn.clicked.connect(lambda: self.update_statistics('monthly'))
        period_layout.addWidget(self.monthly_btn)
        
        stats_layout.addLayout(period_layout)
        
        # Statistics display
        self.stats_text = QLabel("Loading statistics...")
        self.stats_text.setStyleSheet(f"""
            color: white;
            font-size: 14px;
            padding: 15px;
            background-color: #000000;
            border: 1px solid {self.colors['palette'][3]};
            border-radius: 5px;
        """)
        self.stats_text.setWordWrap(True)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_frame)
    
    def create_achievements_section(self, layout):
        """Create the achievements section"""
        achievements_frame = QFrame()
        achievements_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][4]};
                border-radius: 10px;
            }}
        """)
        
        achievements_layout = QVBoxLayout(achievements_frame)
        achievements_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ ACHIEVEMENTS")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][4]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        achievements_layout.addWidget(title)
        
        # Achievements list
        self.achievements_list = QListWidget()
        self.achievements_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][4]};
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #333333;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['palette'][4]};
                color: black;
            }}
        """)
        achievements_layout.addWidget(self.achievements_list)
        
        layout.addWidget(achievements_frame)
    
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
        self.progress_tracker.progress_updated.connect(self.update_progress_display)
        self.progress_tracker.achievement_unlocked.connect(self.on_achievement_unlocked)
        self.progress_tracker.level_up.connect(self.on_level_up)
    
    def update_progress_display(self):
        """Update all progress displays"""
        # Update overall progress
        overall_progress = self.progress_tracker.get_overall_progress()
        self.overall_progress_bar.setValue(int(overall_progress))
        
        # Update current level
        current_level = self.progress_tracker.get_current_level()
        level_names = {
            'A1': 'A1 - BEGINNER',
            'A2': 'A2 - ELEMENTARY',
            'B1': 'B1 - INTERMEDIATE',
            'B2': 'B2 - UPPER INTERMEDIATE',
            'C1': 'C1 - ADVANCED',
            'C2': 'C2 - PROFICIENT'
        }
        self.current_level_label.setText(level_names.get(current_level, current_level))
        
        # Update level requirements
        self.update_level_requirements(current_level)
        
        # Update statistics
        self.update_statistics('weekly')
        
        # Update achievements
        self.update_achievements()
        
        # Update word stats
        stats = self.progress_tracker.get_learning_statistics()
        if 'words' in stats:
            words_stats = stats['words']
            self.words_learned_label.setText(str(words_stats.get('learned_words', 0)))
            accuracy = words_stats.get('accuracy_rate', 0) * 100
            self.accuracy_label.setText(f"{accuracy:.1f}%")
        
        # Update study time (placeholder)
        self.study_time_label.setText("0 min")  # Would calculate actual time
    
    def update_level_requirements(self, current_level):
        """Update level requirements display"""
        next_level_info = self.progress_tracker.get_next_level_requirements()
        next_level = next_level_info['next_level']
        requirements = next_level_info['requirements']
        
        self.next_level_label.setText(f"Next Level: {next_level}")
        
        # Get current progress for this level
        level_progress = self.progress_tracker.get_level_progress(current_level)
        
        # Update progress bars
        words_progress = (level_progress.get('words_learned', 0) / 
                         requirements.get('words', 1)) * 100
        self.words_progress.setValue(int(words_progress))
        
        accuracy_progress = (level_progress.get('accuracy', 0) / 
                          requirements.get('accuracy', 1)) * 100
        self.accuracy_progress.setValue(int(accuracy_progress))
        
        sessions_progress = (level_progress.get('sessions', 0) / 
                           requirements.get('sessions', 1)) * 100
        self.sessions_progress.setValue(int(sessions_progress))
    
    def update_statistics(self, period):
        """Update statistics display"""
        if period == 'weekly':
            stats = self.progress_tracker.get_weekly_progress()
            period_text = "Weekly Statistics"
        else:
            stats = self.progress_tracker.get_monthly_progress()
            period_text = "Monthly Statistics"
        
        stats_text = f"=== {period_text} ===\n\n"
        
        if stats:
            stats_text += f"Sessions: {stats.get('session_count', 0)}\n"
            stats_text += f"Study Time: {stats.get('total_minutes', 0)} minutes\n"
            stats_text += f"Words Learned: {stats.get('total_words', 0)}\n"
            stats_text += f"Phrases Learned: {stats.get('total_phrases', 0)}\n"
            stats_text += f"Exercises Completed: {stats.get('total_exercises', 0)}\n"
            avg_score = stats.get('avg_score') or 0
            stats_text += f"Average Score: {avg_score:.1f}%\n"
        else:
            stats_text += "No data available for this period.\n"
            stats_text += "Start learning to see your statistics!"
        
        self.stats_text.setText(stats_text)
    
    def update_achievements(self):
        """Update achievements display"""
        achievements = self.progress_tracker.get_achievements()
        
        self.achievements_list.clear()
        
        for achievement in achievements:
            # Create display text
            status = "🏆" if achievement['unlocked'] else "🔒"
            display_text = f"{status} {achievement['name']}"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, achievement)
            
            # Style based on unlock status
            if achievement['unlocked']:
                item.setStyleSheet(f"""
                    color: {self.colors['palette'][4]};
                    font-weight: normal;
                """)
            else:
                item.setStyleSheet("color: #666666;")
            
            self.achievements_list.addItem(item)
    
    def on_achievement_unlocked(self, achievement_name):
        """Handle achievement unlock"""
        # Update achievements display
        self.update_achievements()
        
        # Could show a notification or animation
        print(f"Achievement unlocked: {achievement_name}")
    
    def on_level_up(self, new_level):
        """Handle level up"""
        # Update level display
        self.update_progress_display()
        
        # Could show a celebration dialog
        print(f"Level up! New level: {new_level}")
