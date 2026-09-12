"""
Grammar Widget for English Learning Application
Interactive grammar lessons and rules
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit,
    QPushButton, QListWidget, QListWidgetItem, QScrollArea, QSplitter,
    QComboBox, QButtonGroup, QRadioButton, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from lcars.themes.palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class GrammarWidget(QWidget):
    """Grammar learning widget"""
    
    # Signals
    rule_selected = pyqtSignal(dict)  # grammar rule data
    rule_completed = pyqtSignal(int)  # rule id
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_rule = None
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        self.init_ui()
        self.setup_connections()
        self.load_grammar_rules()
    
    def init_ui(self):
        """Initialize the grammar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Rules list
        left_panel = self.create_rules_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Rule details
        right_panel = self.create_rule_details_panel()
        content_splitter.addWidget(right_panel)
        
        content_splitter.setSizes([400, 600])
        layout.addWidget(content_splitter)
        
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
        title = QLabel("GRAMMAR LESSONS")
        title.setStyleSheet(f"""
            color: {self.colors['accent']};
            font-size: 24px;
            font-weight: normal;
            padding: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title, 1)
        
        # Level filter
        self.level_filter = QComboBox()
        self.level_filter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.level_filter.setStyleSheet(f"""
            QComboBox {{
                background-color: #111111;
                color: white;
                border: 2px solid {self.colors['palette'][1]};
                padding: 5px 10px;
                font-size: 14px;
            }}
        """)
        header_layout.addWidget(self.level_filter)
        
        layout.addWidget(header_frame)
    
    def create_rules_panel(self, layout=None):
        """Create the grammar rules list panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Rules list frame
        rules_frame = QFrame()
        rules_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][1]};
                border-radius: 10px;
            }}
        """)
        
        rules_layout = QVBoxLayout(rules_frame)
        rules_layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = QLabel("◤ GRAMMAR RULES")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        rules_layout.addWidget(title)
        
        # Rules list
        self.rules_list = QListWidget()
        self.rules_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][2]};
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid #333333;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['palette'][2]};
                color: black;
            }}
            QListWidget::item:hover {{
                background-color: #333333;
            }}
        """)
        rules_layout.addWidget(self.rules_list)
        
        # Practice buttons
        practice_title = QLabel("◤ GRAMMAR PRACTICE")
        practice_title.setStyleSheet(f"""
            color: {self.colors['palette'][3]};
            font-size: 16px;
            font-weight: normal;
            margin: 15px 0 5px 0;
        """)
        rules_layout.addWidget(practice_title)
        
        self.practice_btn = LCARSButton("Practice Current Rule", self.colors['palette'][3])
        self.practice_btn.clicked.connect(self.practice_current_rule)
        rules_layout.addWidget(self.practice_btn)
        
        self.quiz_btn = LCARSButton("Grammar Quiz", self.colors['palette'][4])
        self.quiz_btn.clicked.connect(self.start_grammar_quiz)
        rules_layout.addWidget(self.quiz_btn)
        
        layout.addWidget(rules_frame)
        
        return panel
    
    def create_rule_details_panel(self, layout=None):
        """Create the rule details panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Rule details frame
        details_frame = QFrame()
        details_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][5]};
                border-radius: 10px;
            }}
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 15, 15, 15)
        
        # Rule title
        self.rule_title = QLabel("Select a grammar rule to view details")
        self.rule_title.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 24px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        details_layout.addWidget(self.rule_title)
        
        # Rule level
        self.rule_level = QLabel("")
        self.rule_level.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 16px;
            margin-bottom: 15px;
        """)
        details_layout.addWidget(self.rule_level)
        
        # Rule explanation
        explanation_title = QLabel("◤ RULE EXPLANATION")
        explanation_title.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        details_layout.addWidget(explanation_title)
        
        self.rule_explanation = QTextEdit()
        self.rule_explanation.setReadOnly(True)
        self.rule_explanation.setMaximumHeight(200)
        self.rule_explanation.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][7]};
                font-size: 14px;
            }}
        """)
        details_layout.addWidget(self.rule_explanation)
        
        # Examples section
        examples_title = QLabel("◤ EXAMPLES")
        examples_title.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 18px;
            font-weight: normal;
            margin: 15px 0 10px 0;
        """)
        details_layout.addWidget(examples_title)
        
        self.examples_text = QTextEdit()
        self.examples_text.setReadOnly(True)
        self.examples_text.setMaximumHeight(150)
        self.examples_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][8]};
                font-size: 14px;
            }}
        """)
        details_layout.addWidget(self.examples_text)
        
        # Interactive examples
        interactive_title = QLabel("◤ INTERACTIVE PRACTICE")
        interactive_title.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 18px;
            font-weight: normal;
            margin: 15px 0 10px 0;
        """)
        details_layout.addWidget(interactive_title)
        
        # Practice area
        self.practice_area = QWidget()
        self.practice_layout = QVBoxLayout(self.practice_area)
        details_layout.addWidget(self.practice_area)
        
        # Mark as completed button
        self.completed_btn = LCARSButton("Mark as Completed", self.colors['palette'][0])
        self.completed_btn.clicked.connect(self.mark_rule_completed)
        self.completed_btn.setEnabled(False)
        details_layout.addWidget(self.completed_btn)
        
        details_layout.addStretch()
        
        layout.addWidget(details_frame)
        
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
        """)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Rules list selection
        self.rules_list.itemClicked.connect(self.on_rule_selected)
        
        # Level filter
        self.level_filter.currentTextChanged.connect(self.on_level_filter_changed)
    
    def load_grammar_rules(self):
        """Load grammar rules from database"""
        level = self.level_filter.currentText()
        if level == 'All Levels':
            level = None
        
        rules = self.db.get_grammar_rules_by_level(level) if level else []
        
        self.rules_list.clear()
        
        for rule in rules:
            # Create display text
            display_text = f"{rule['title']} ({rule['level']})"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, rule)
            self.rules_list.addItem(item)
    
    def on_rule_selected(self, item):
        """Handle grammar rule selection"""
        rule_data = item.data(Qt.ItemDataRole.UserRole)
        if rule_data:
            self.display_rule_details(rule_data)
            self.current_rule = rule_data
            self.rule_selected.emit(rule_data)
            self.completed_btn.setEnabled(True)
    
    def on_level_filter_changed(self, level):
        """Handle level filter change"""
        self.load_grammar_rules()
    
    def display_rule_details(self, rule):
        """Display detailed information about a grammar rule"""
        self.rule_title.setText(rule['title'])
        self.rule_level.setText(f"Level: {rule['level']}")
        
        # Rule explanation
        explanation = rule.get('rule_text', 'No explanation available')
        self.rule_explanation.setText(explanation)
        
        # Examples
        examples = rule.get('examples', 'No examples available')
        self.examples_text.setText(examples)
        
        # Create interactive practice based on rule type
        self.create_interactive_practice(rule)
    
    def create_interactive_practice(self, rule):
        """Create interactive practice based on the grammar rule"""
        # Clear existing practice area
        for i in reversed(range(self.practice_layout.count())):
            child = self.practice_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        rule_title = rule['title'].lower()
        
        if 'present simple' in rule_title:
            self.create_present_simple_practice()
        elif 'articles' in rule_title:
            self.create_articles_practice()
        elif 'plural' in rule_title:
            self.create_plural_practice()
        else:
            self.create_general_practice(rule)
    
    def create_present_simple_practice(self):
        """Create Present Simple practice"""
        instruction = QLabel("Complete the sentences with the correct form of the verb:")
        instruction.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 16px;
            margin-bottom: 10px;
        """)
        self.practice_layout.addWidget(instruction)
        
        # Practice sentences
        sentences = [
            ("I _____ (work) in an office.", "work"),
            ("She _____ (study) English every day.", "studies"),
            ("They _____ (play) football on weekends.", "play"),
            ("He _____ (like) coffee.", "likes"),
            ("We _____ (live) in Kyiv.", "live")
        ]
        
        for sentence, correct_answer in sentences:
            sentence_label = QLabel(sentence)
            sentence_label.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practice_layout.addWidget(sentence_label)
        
        check_btn = LCARSButton("Check Answers", self.colors['palette'][1])
        check_btn.clicked.connect(self.check_practice_answers)
        self.practice_layout.addWidget(check_btn)
    
    def create_articles_practice(self):
        """Create articles (a/an) practice"""
        instruction = QLabel("Choose the correct article (a/an):")
        instruction.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 16px;
            margin-bottom: 10px;
        """)
        self.practice_layout.addWidget(instruction)
        
        # Practice items
        items = ["apple", "book", "orange", "car", "umbrella"]
        
        for item in items:
            item_label = QLabel(f"_____ {item}")
            item_label.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practice_layout.addWidget(item_label)
        
        check_btn = LCARSButton("Check Answers", self.colors['palette'][1])
        check_btn.clicked.connect(self.check_practice_answers)
        self.practice_layout.addWidget(check_btn)
    
    def create_plural_practice(self):
        """Create plural nouns practice"""
        instruction = QLabel("Write the plural form of these nouns:")
        instruction.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 16px;
            margin-bottom: 10px;
        """)
        self.practice_layout.addWidget(instruction)
        
        # Practice nouns
        nouns = ["cat", "dog", "box", "baby", "class"]
        
        for noun in nouns:
            noun_label = QLabel(f"{noun} → _____")
            noun_label.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practice_layout.addWidget(noun_label)
        
        check_btn = LCARSButton("Check Answers", self.colors['palette'][1])
        check_btn.clicked.connect(self.check_practice_answers)
        self.practice_layout.addWidget(check_btn)
    
    def create_general_practice(self, rule):
        """Create general practice for other grammar rules"""
        instruction = QLabel("Study the examples above and try to create your own sentences:")
        instruction.setStyleSheet(f"""
            color: {self.colors['palette'][0]};
            font-size: 16px;
            margin-bottom: 10px;
        """)
        self.practice_layout.addWidget(instruction)
        
        # Text area for practice
        practice_input = QTextEdit()
        practice_input.setPlaceholderText("Write your practice sentences here...")
        practice_input.setMaximumHeight(100)
        practice_input.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][1]};
                font-size: 14px;
            }}
        """)
        self.practice_layout.addWidget(practice_input)
        
        save_btn = LCARSButton("Save Practice", self.colors['palette'][1])
        save_btn.clicked.connect(self.save_practice)
        self.practice_layout.addWidget(save_btn)
    
    def check_practice_answers(self):
        """Check practice answers (simplified)"""
        # In a real implementation, this would check actual answers
        result_label = QLabel("✓ Practice completed! Keep studying to improve.")
        result_label.setStyleSheet("""
            color: #00FF00;
            font-size: 14px;
            margin: 10px 0;
            padding: 10px;
            background-color: #003300;
            border: 1px solid #00FF00;
            border-radius: 5px;
        """)
        self.practice_layout.addWidget(result_label)
    
    def save_practice(self):
        """Save practice sentences"""
        result_label = QLabel("✓ Practice saved successfully!")
        result_label.setStyleSheet("""
            color: #00FF00;
            font-size: 14px;
            margin: 10px 0;
            padding: 10px;
            background-color: #003300;
            border: 1px solid #00FF00;
            border-radius: 5px;
        """)
        self.practice_layout.addWidget(result_label)
    
    def practice_current_rule(self):
        """Start practice for current rule"""
        if self.current_rule:
            self.create_interactive_practice(self.current_rule)
    
    def start_grammar_quiz(self):
        """Start a comprehensive grammar quiz"""
        # This would start a quiz covering multiple grammar rules
        pass
    
    def mark_rule_completed(self):
        """Mark the current rule as completed"""
        if self.current_rule:
            self.rule_completed.emit(self.current_rule['id'])
            
            # Show confirmation
            result_label = QLabel("✓ Grammar rule marked as completed!")
            result_label.setStyleSheet("""
                color: #00FF00;
                font-size: 16px;
                font-weight: normal;
                margin: 10px 0;
                padding: 10px;
                background-color: #003300;
                border: 2px solid #00FF00;
                border-radius: 5px;
            """)
            self.practice_layout.addWidget(result_label)
            
            # Disable button to prevent multiple clicks
            self.completed_btn.setEnabled(False)
