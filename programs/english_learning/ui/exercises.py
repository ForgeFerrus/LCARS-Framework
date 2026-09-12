"""
Exercises Widget for English Learning Application
Interactive exercises for vocabulary, grammar, and phrases
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTextEdit, QPushButton, QButtonGroup, QRadioButton, QCheckBox,
    QProgressBar, QMessageBox, QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from lcars.themes.palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class ExercisesWidget(QWidget):
    """Interactive exercises widget"""
    
    # Signals
    exercise_completed = pyqtSignal(dict)  # exercise result
    session_ended = pyqtSignal()
    
    def __init__(self, db_manager, learning_manager):
        super().__init__()
        self.db = db_manager
        self.learning_manager = learning_manager
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        # Exercise state
        self.current_exercise = None
        self.exercise_history = []
        self.session_stats = {
            'total': 0,
            'correct': 0,
            'incorrect': 0
        }
        
        self.init_ui()
        self.setup_connections()
        self.start_new_session()
    
    def init_ui(self):
        """Initialize the exercises UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left panel - Exercise controls
        left_panel = self.create_control_panel()
        content_layout.addWidget(left_panel)
        
        # Right panel - Exercise area
        right_panel = self.create_exercise_panel()
        content_layout.addWidget(right_panel)
        
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
        title = QLabel("INTERACTIVE EXERCISES")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 24px;
            font-weight: normal;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)
        
        # Progress indicator
        self.progress_label = QLabel("Progress: 0/0")
        self.progress_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 16px;
            font-weight: normal;
            padding: 20px;
            background-color: #111111;
            border: 2px solid {self.colors['palette'][6]};
        """)
        header_layout.addWidget(self.progress_label)
        
        layout.addWidget(header_frame)
    
    def create_control_panel(self, layout=None):
        """Create the exercise control panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Exercise type selection
        type_frame = QFrame()
        type_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][1]};
                border-radius: 10px;
            }}
        """)
        
        type_layout = QVBoxLayout(type_frame)
        type_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ EXERCISE TYPE")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        type_layout.addWidget(title)
        
        # Exercise type buttons
        self.exercise_type_group = QButtonGroup()
        
        exercise_types = [
            ("Translation", "translation", self.colors['palette'][2]),
            ("Multiple Choice", "multiple_choice", self.colors['palette'][3]),
            ("Spelling", "spelling", self.colors['palette'][4]),
            ("Phrases", "phrase_translation", self.colors['palette'][5]),
            ("Grammar", "grammar", self.colors['palette'][6])
        ]
        
        for type_name, type_value, color in exercise_types:
            btn = LCARSButton(type_name, color)
            btn.setCheckable(True)
            self.exercise_type_group.addButton(btn)
            btn.exercise_type = type_value
            type_layout.addWidget(btn)
        
        # Set default selection
        self.exercise_type_group.buttons()[0].setChecked(True)
        
        # Level selection
        level_title = QLabel("◤ DIFFICULTY LEVEL")
        level_title.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 16px;
            font-weight: normal;
            margin: 15px 0 5px 0;
        """)
        type_layout.addWidget(level_title)
        
        self.level_buttons = QButtonGroup()
        
        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        level_colors = [self.colors['palette'][i % len(self.colors['palette'])] for i in range(len(levels))]
        
        for level, color in zip(levels, level_colors):
            btn = LCARSButton(level, color)
            btn.setCheckable(True)
            btn.setMaximumHeight(35)
            self.level_buttons.addButton(btn)
            btn.level = level
            type_layout.addWidget(btn)
        
        # Set A1 as default
        self.level_buttons.buttons()[0].setChecked(True)
        
        # Session controls
        controls_title = QLabel("◤ SESSION CONTROLS")
        controls_title.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 16px;
            font-weight: normal;
            margin: 15px 0 5px 0;
        """)
        type_layout.addWidget(controls_title)
        
        # Control buttons
        self.start_session_btn = LCARSButton("Start Session", self.colors['palette'][0])
        self.start_session_btn.clicked.connect(self.start_new_session)
        type_layout.addWidget(self.start_session_btn)
        
        self.next_exercise_btn = LCARSButton("Next Exercise", self.colors['palette'][1])
        self.next_exercise_btn.clicked.connect(self.next_exercise)
        type_layout.addWidget(self.next_exercise_btn)
        
        self.show_hint_btn = LCARSButton("Show Hint", self.colors['palette'][2])
        self.show_hint_btn.clicked.connect(self.show_hint)
        type_layout.addWidget(self.show_hint_btn)
        
        self.end_session_btn = LCARSButton("End Session", "#FF0000")
        self.end_session_btn.clicked.connect(self.end_session)
        type_layout.addWidget(self.end_session_btn)
        
        type_layout.addStretch()
        
        layout.addWidget(type_frame)
        
        return panel
    
    def create_exercise_panel(self, layout=None):
        """Create the main exercise panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Exercise display frame
        exercise_frame = QFrame()
        exercise_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][3]};
                border-radius: 10px;
            }}
        """)
        
        exercise_layout = QVBoxLayout(exercise_frame)
        exercise_layout.setContentsMargins(20, 20, 20, 20)
        
        # Exercise number and type
        self.exercise_info_label = QLabel("Exercise 1 of 10 - Translation")
        self.exercise_info_label.setStyleSheet(f"""
            color: {self.colors['palette'][3]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        exercise_layout.addWidget(self.exercise_info_label)
        
        # Question area
        self.question_label = QLabel("Click 'Start Session' to begin")
        self.question_label.setStyleSheet(f"""
            color: white;
            font-size: 20px;
            margin: 20px 0;
            padding: 20px;
            background-color: #000000;
            border: 2px solid {self.colors['palette'][4]};
            border-radius: 10px;
        """)
        self.question_label.setWordWrap(True)
        self.question_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        exercise_layout.addWidget(self.question_label)
        
        # Answer input area (will be populated based on exercise type)
        self.answer_widget = QWidget()
        self.answer_layout = QVBoxLayout(self.answer_widget)
        exercise_layout.addWidget(self.answer_widget)
        
        # Hint area
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 14px;
            font-style: italic;
            margin: 10px 0;
            padding: 10px;
            background-color: #222222;
            border: 1px solid {self.colors['palette'][5]};
            border-radius: 5px;
        """)
        self.hint_label.setWordWrap(True)
        self.hint_label.hide()
        exercise_layout.addWidget(self.hint_label)
        
        # Submit button
        self.submit_btn = LCARSButton("Submit Answer", self.colors['palette'][0])
        self.submit_btn.clicked.connect(self.submit_answer)
        self.submit_btn.setEnabled(False)
        exercise_layout.addWidget(self.submit_btn)
        
        # Result area
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        """)
        self.result_label.setWordWrap(True)
        self.result_label.hide()
        exercise_layout.addWidget(self.result_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {self.colors['palette'][6]};
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: normal;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors['palette'][6]};
                border-radius: 3px;
            }}
        """)
        self.progress_bar.setRange(0, 10)
        exercise_layout.addWidget(self.progress_bar)
        
        # Session statistics
        stats_frame = QFrame()
        stats_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][7]};
                border-radius: 10px;
            }}
        """)
        
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        
        self.correct_label = QLabel("Correct: 0")
        self.correct_label.setStyleSheet(f"color: #00FF00; font-size: 16px; font-weight: normal;")
        stats_layout.addWidget(self.correct_label)
        
        self.incorrect_label = QLabel("Incorrect: 0")
        self.incorrect_label.setStyleSheet(f"color: #FF0000; font-size: 16px; font-weight: normal;")
        stats_layout.addWidget(self.incorrect_label)
        
        self.accuracy_label = QLabel("Accuracy: 0%")
        self.accuracy_label.setStyleSheet(f"color: {self.colors['palette'][7]}; font-size: 16px; font-weight: normal;")
        stats_layout.addWidget(self.accuracy_label)
        
        exercise_layout.addWidget(stats_frame)
        
        layout.addWidget(exercise_frame)
        
        return panel
    
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
            QLineEdit {
                background-color: #000000;
                color: white;
                border: 2px solid #4BBEBF;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QTextEdit {
                background-color: #000000;
                color: white;
                border: 2px solid #4BBEBF;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def start_new_session(self):
        """Start a new exercise session"""
        self.session_stats = {'total': 0, 'correct': 0, 'incorrect': 0}
        self.exercise_history = []
        self.progress_bar.setValue(0)
        self.update_statistics()
        
        # Load first exercise
        self.next_exercise()
        
        # Update UI
        self.submit_btn.setEnabled(True)
        self.start_session_btn.setText("Restart Session")
    
    def next_exercise(self):
        """Load the next exercise"""
        # Get selected exercise type and level
        selected_type_btn = self.exercise_type_group.checkedButton()
        exercise_type = selected_type_btn.exercise_type if selected_type_btn else "translation"
        
        selected_level_btn = self.level_buttons.checkedButton()
        level = selected_level_btn.level if selected_level_btn else "A1"
        
        # Generate new exercise
        self.current_exercise = self.learning_manager.get_next_exercise(level, [exercise_type])
        
        if self.current_exercise:
            self.display_exercise()
            self.hide_result()
        else:
            self.show_session_complete()
    
    def display_exercise(self):
        """Display the current exercise"""
        if not self.current_exercise:
            return
        
        # Update exercise info
        exercise_num = self.session_stats['total'] + 1
        exercise_type = self.current_exercise['type'].replace('_', ' ').title()
        self.exercise_info_label.setText(f"Exercise {exercise_num} - {exercise_type}")
        
        # Display question
        self.question_label.setText(self.current_exercise['question'])
        
        # Create answer input based on exercise type
        self.create_answer_input()
        
        # Hide hint and result
        self.hint_label.hide()
        self.result_label.hide()
        
        # Update progress
        self.progress_label.setText(f"Progress: {exercise_num}/10")
        self.progress_bar.setValue(exercise_num)
    
    def create_answer_input(self):
        """Create appropriate answer input based on exercise type"""
        # Clear existing answer widget
        for i in reversed(range(self.answer_layout.count())):
            child = self.answer_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        exercise_type = self.current_exercise['type']
        
        if exercise_type == 'multiple_choice':
            # Create radio buttons for multiple choice
            options = self.current_exercise.get('options', [])
            for i, option in enumerate(options):
                radio = QRadioButton(option)
                radio.setStyleSheet(f"""
                    QRadioButton {{
                        color: white;
                        font-size: 16px;
                        padding: 5px;
                    }}
                    QRadioButton::indicator {{
                        width: 20px;
                        height: 20px;
                    }}
                    QRadioButton::indicator::unchecked {{
                        border: 2px solid {self.colors['palette'][4]};
                        background-color: #000000;
                        border-radius: 10px;
                    }}
                    QRadioButton::indicator::checked {{
                        border: 2px solid {self.colors['palette'][4]};
                        background-color: {self.colors['palette'][4]};
                        border-radius: 10px;
                    }}
                """)
                self.answer_layout.addWidget(radio)
        
        elif exercise_type == 'grammar_fill_blank':
            # Create text input for fill-in-the-blank
            self.answer_input = QLineEdit()
            self.answer_input.setPlaceholderText("Type your answer here...")
            self.answer_input.returnPressed.connect(self.submit_answer)
            self.answer_layout.addWidget(self.answer_input)
        
        else:
            # Create text input for other types
            self.answer_input = QLineEdit()
            self.answer_input.setPlaceholderText("Type your answer here...")
            self.answer_input.returnPressed.connect(self.submit_answer)
            self.answer_layout.addWidget(self.answer_input)
    
    def submit_answer(self):
        """Submit the current answer"""
        if not self.current_exercise:
            return
        
        # Get user answer
        user_answer = self.get_user_answer()
        
        if not user_answer:
            return
        
        # Check answer
        result = self.learning_manager.check_answer(user_answer)
        
        # Update session statistics
        self.session_stats['total'] += 1
        if result['correct']:
            self.session_stats['correct'] += 1
        else:
            self.session_stats['incorrect'] += 1
        
        # Display result
        self.display_result(result)
        
        # Update statistics display
        self.update_statistics()
        
        # Disable submit button for this exercise
        self.submit_btn.setEnabled(False)
        
        # Emit exercise completed signal
        self.exercise_completed.emit(result)
        
        # Auto-load next exercise after delay
        QTimer.singleShot(2000, self.auto_next_exercise)
    
    def get_user_answer(self):
        """Get the user's answer from the input widget"""
        exercise_type = self.current_exercise['type']
        
        if exercise_type == 'multiple_choice':
            # Get selected radio button
            for i in range(self.answer_layout.count()):
                widget = self.answer_layout.itemAt(i).widget()
                if isinstance(widget, QRadioButton) and widget.isChecked():
                    return widget.text()
            return ""
        
        else:
            # Get text input
            if hasattr(self, 'answer_input'):
                return self.answer_input.text().strip()
            return ""
    
    def display_result(self, result):
        """Display the exercise result"""
        self.result_label.show()
        
        if result['correct']:
            self.result_label.setText("✓ CORRECT! Well done!")
            self.result_label.setStyleSheet("""
                color: #00FF00;
                font-size: 16px;
                font-weight: normal;
                margin: 10px 0;
                padding: 10px;
                background-color: #003300;
                border: 2px solid #00FF00;
                border-radius: 5px;
            """)
        else:
            self.result_label.setText(f"✗ Incorrect. {result['message']}")
            self.result_label.setStyleSheet("""
                color: #FF0000;
                font-size: 16px;
                font-weight: normal;
                margin: 10px 0;
                padding: 10px;
                background-color: #330000;
                border: 2px solid #FF0000;
                border-radius: 5px;
            """)
            
            # Show explanation if available
            if result.get('explanation'):
                explanation = QLabel(f"Explanation: {result['explanation']}")
                explanation.setStyleSheet("""
                    color: #CCCCCC;
                    font-size: 14px;
                    margin: 5px 0;
                    padding: 10px;
                    background-color: #222222;
                    border-radius: 5px;
                """)
                explanation.setWordWrap(True)
                self.answer_layout.addWidget(explanation)
    
    def hide_result(self):
        """Hide the result display"""
        self.result_label.hide()
        self.submit_btn.setEnabled(True)
    
    def show_hint(self):
        """Show a hint for the current exercise"""
        if not self.current_exercise:
            return
        
        hints = self.current_exercise.get('hints', [])
        if hints:
            hint_text = "💡 " + hints[0]  # Show first hint
            self.hint_label.setText(hint_text)
            self.hint_label.show()
        else:
            hint_text = "💡 " + self.current_exercise.get('hint', 'No hint available')
            self.hint_label.setText(hint_text)
            self.hint_label.show()
    
    def auto_next_exercise(self):
        """Automatically load next exercise after delay"""
        if self.session_stats['total'] < 10:
            self.next_exercise()
        else:
            self.show_session_complete()
    
    def show_session_complete(self):
        """Show session completion message"""
        self.question_label.setText("Session Complete!")
        
        # Create summary
        accuracy = (self.session_stats['correct'] / self.session_stats['total'] * 100) if self.session_stats['total'] > 0 else 0
        
        summary = f"""
        Session Summary:
        • Total Exercises: {self.session_stats['total']}
        • Correct: {self.session_stats['correct']}
        • Incorrect: {self.session_stats['incorrect']}
        • Accuracy: {accuracy:.1f}%
        """
        
        self.result_label.setText(summary)
        self.result_label.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 16px;
            margin: 10px 0;
            padding: 20px;
            background-color: #111111;
            border: 2px solid {self.colors['palette'][6]};
            border-radius: 10px;
        """)
        self.result_label.show()
        
        # Disable exercise controls
        self.submit_btn.setEnabled(False)
        self.next_exercise_btn.setEnabled(False)
    
    def update_statistics(self):
        """Update the statistics display"""
        self.correct_label.setText(f"Correct: {self.session_stats['correct']}")
        self.incorrect_label.setText(f"Incorrect: {self.session_stats['incorrect']}")
        
        accuracy = (self.session_stats['correct'] / self.session_stats['total'] * 100) if self.session_stats['total'] > 0 else 0
        self.accuracy_label.setText(f"Accuracy: {accuracy:.1f}%")
    
    def end_session(self):
        """End the current session"""
        reply = QMessageBox.question(
            self, 'End Session',
            'Are you sure you want to end the current session?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.session_ended.emit()
            
            # Reset UI
            self.question_label.setText("Click 'Start Session' to begin")
            self.hide_result()
            self.progress_bar.setValue(0)
            self.progress_label.setText("Progress: 0/0")
            self.session_stats = {'total': 0, 'correct': 0, 'incorrect': 0}
            self.update_statistics()
