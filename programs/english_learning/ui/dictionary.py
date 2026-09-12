"""
Dictionary Widget for English Learning Application
Interactive dictionary with search, pronunciation, and examples
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QPushButton, QSplitter,
    QScrollArea, QGridLayout, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from lcars.themes.palette import get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour

class DictionaryWidget(QWidget):
    """Dictionary widget with search and word details"""
    
    # Signals
    word_selected = pyqtSignal(dict)  # word data
    add_to_study = pyqtSignal(int)   # word id
    
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.current_word = None
        
        # Set LCARS theme
        self.era = LCARSEra.LCARS_24TH
        self.colors = get_theme(self.era)
        
        self.init_ui()
        self.setup_connections()
        self.load_recent_words()
    
    def init_ui(self):
        """Initialize the dictionary UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.create_header(layout)
        
        # Main content area
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Search and word list
        left_panel = self.create_search_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel - Word details
        right_panel = self.create_word_details_panel()
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
        title = QLabel("ENGLISH-UKRAINIAN DICTIONARY")
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
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.colors['palette'][1]};
            }}
        """)
        header_layout.addWidget(self.level_filter)
        
        layout.addWidget(header_frame)
    
    def create_search_panel(self, layout=None):
        """Create the search and word list panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Search section
        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][1]};
                border-radius: 10px;
            }}
        """)
        
        search_layout = QVBoxLayout(search_frame)
        search_layout.setContentsMargins(15, 15, 15, 15)
        
        # Search title
        title = QLabel("◤ SEARCH DICTIONARY")
        title.setStyleSheet(f"""
            color: {self.colors['palette'][1]};
            font-size: 18px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        search_layout.addWidget(title)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter English or Ukrainian word...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: #000000;
                color: white;
                border: 2px solid {self.colors['palette'][2]};
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }}
        """)
        search_layout.addWidget(self.search_input)
        
        # Search options
        options_layout = QHBoxLayout()
        
        self.search_english_btn = LCARSButton("English", self.colors['palette'][2])
        self.search_english_btn.setCheckable(True)
        self.search_english_btn.setChecked(True)
        options_layout.addWidget(self.search_english_btn)
        
        self.search_ukrainian_btn = LCARSButton("Ukrainian", self.colors['palette'][3])
        self.search_ukrainian_btn.setCheckable(True)
        options_layout.addWidget(self.search_ukrainian_btn)
        
        search_layout.addLayout(options_layout)
        
        # Word list
        list_title = QLabel("◤ WORD RESULTS")
        list_title.setStyleSheet(f"""
            color: {self.colors['palette'][4]};
            font-size: 16px;
            font-weight: normal;
            margin: 15px 0 5px 0;
        """)
        search_layout.addWidget(list_title)
        
        self.word_list = QListWidget()
        self.word_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][4]};
                font-size: 14px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #333333;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['palette'][4]};
                color: black;
            }}
            QListWidget::item:hover {{
                background-color: #333333;
            }}
        """)
        search_layout.addWidget(self.word_list)
        
        # Category filter
        category_title = QLabel("◤ CATEGORIES")
        category_title.setStyleSheet(f"""
            color: {self.colors['palette'][5]};
            font-size: 16px;
            font-weight: normal;
            margin: 15px 0 5px 0;
        """)
        search_layout.addWidget(category_title)
        
        self.category_list = QListWidget()
        self.category_list.setMaximumHeight(150)
        self.category_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][5]};
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 5px;
                border-bottom: 1px solid #333333;
            }}
            QListWidget::item:selected {{
                background-color: {self.colors['palette'][5]};
                color: black;
            }}
        """)
        search_layout.addWidget(self.category_list)
        
        layout.addWidget(search_frame)
        
        return panel
    
    def create_word_details_panel(self, layout=None):
        """Create the word details panel"""
        if layout is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
        else:
            panel = layout
        
        # Word details frame
        details_frame = QFrame()
        details_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #111111;
                border: 2px solid {self.colors['palette'][6]};
                border-radius: 10px;
            }}
        """)
        
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(15, 15, 15, 15)
        
        # Word title
        self.word_title = QLabel("Select a word to view details")
        self.word_title.setStyleSheet(f"""
            color: {self.colors['palette'][6]};
            font-size: 24px;
            font-weight: normal;
            margin-bottom: 10px;
        """)
        details_layout.addWidget(self.word_title)
        
        # Pronunciation
        self.pronunciation_label = QLabel("")
        self.pronunciation_label.setStyleSheet("""
            color: #CCCCCC;
            font-size: 16px;
            font-style: italic;
            margin-bottom: 10px;
        """)
        details_layout.addWidget(self.pronunciation_label)
        
        # Translation
        self.translation_label = QLabel("")
        self.translation_label.setStyleSheet(f"""
            color: {self.colors['palette'][7]};
            font-size: 20px;
            font-weight: normal;
            margin-bottom: 15px;
        """)
        details_layout.addWidget(self.translation_label)
        
        # Word info grid
        info_grid = QGridLayout()
        
        # Part of speech
        self.pos_label = QLabel("")
        info_grid.addWidget(QLabel("Part of Speech:"), 0, 0)
        info_grid.addWidget(self.pos_label, 0, 1)
        
        # Level
        self.level_label = QLabel("")
        info_grid.addWidget(QLabel("Level:"), 1, 0)
        info_grid.addWidget(self.level_label, 1, 1)
        
        # Category
        self.category_label = QLabel("")
        info_grid.addWidget(QLabel("Category:"), 2, 0)
        info_grid.addWidget(self.category_label, 2, 1)
        
        details_layout.addLayout(info_grid)
        
        # Example sentence
        example_title = QLabel("◤ EXAMPLE SENTENCE")
        example_title.setStyleSheet(f"""
            color: {self.colors['palette'][8]};
            font-size: 16px;
            font-weight: normal;
            margin: 20px 0 5px 0;
        """)
        details_layout.addWidget(example_title)
        
        self.example_sentence = QTextEdit()
        self.example_sentence.setReadOnly(True)
        self.example_sentence.setMaximumHeight(100)
        self.example_sentence.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: white;
                border: 1px solid {self.colors['palette'][8]};
                font-size: 14px;
            }}
        """)
        details_layout.addWidget(self.example_sentence)
        
        # Example translation
        self.example_translation = QLabel("")
        self.example_translation.setStyleSheet("""
            color: #CCCCCC;
            font-size: 14px;
            font-style: italic;
            margin-bottom: 15px;
        """)
        details_layout.addWidget(self.example_translation)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.add_to_study_btn = LCARSButton("Add to Study", self.colors['palette'][0])
        self.add_to_study_btn.clicked.connect(self.add_current_word_to_study)
        actions_layout.addWidget(self.add_to_study_btn)
        
        self.pronounce_btn = LCARSButton("Pronounce", self.colors['palette'][1])
        self.pronounce_btn.clicked.connect(self.pronounce_current_word)
        actions_layout.addWidget(self.pronounce_btn)
        
        details_layout.addLayout(actions_layout)
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
        # Search input
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Search language buttons
        self.search_english_btn.clicked.connect(self.on_search_language_changed)
        self.search_ukrainian_btn.clicked.connect(self.on_search_language_changed)
        
        # Word list selection
        self.word_list.itemClicked.connect(self.on_word_selected)
        
        # Category selection
        self.category_list.itemClicked.connect(self.on_category_selected)
        
        # Level filter
        self.level_filter.currentTextChanged.connect(self.on_level_filter_changed)
        
        # Setup search timer for delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
    
    def load_recent_words(self):
        """Load recent words for display"""
        # Load categories
        categories = self.db.get_all_categories()
        self.category_list.clear()
        
        for category in categories:
            item = QListWidgetItem(f"{category['name']} ({category['level']})")
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.category_list.addItem(item)
        
        # Load some A1 words by default
        self.load_words_by_level('A1')
    
    def load_words_by_level(self, level):
        """Load words by difficulty level"""
        words = self.db.get_words_by_level(level, limit=50)
        self.populate_word_list(words)
    
    def load_words_by_category(self, category_id):
        """Load words by category"""
        level = self.level_filter.currentText()
        if level == 'All Levels':
            level = None
        
        words = self.db.get_words_by_category(category_id, level)
        self.populate_word_list(words)
    
    def populate_word_list(self, words):
        """Populate the word list with search results"""
        self.word_list.clear()
        
        for word in words:
            # Create display text
            display_text = f"{word['english']} - {word['ukrainian']}"
            if word.get('part_of_speech'):
                display_text += f" ({word['part_of_speech']})"
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, word)
            self.word_list.addItem(item)
    
    def on_search_text_changed(self, text):
        """Handle search text change with delay"""
        if len(text) >= 2 or len(text) == 0:
            self.search_timer.start(300)  # 300ms delay
    
    def perform_search(self):
        """Perform the search"""
        search_text = self.search_input.text().strip()
        
        if not search_text:
            # Load default words
            level = self.level_filter.currentText()
            if level != 'All Levels':
                self.load_words_by_level(level)
            return
        
        # Determine search language
        search_english = self.search_english_btn.isChecked()
        
        # Get level filter
        level = self.level_filter.currentText()
        if level == 'All Levels':
            level = None
        
        # Perform search
        results = self.db.search_words(search_text, level)
        
        # Filter by language if needed
        if search_english:
            results = [w for w in results if search_text.lower() in w['english'].lower()]
        else:
            results = [w for w in results if search_text.lower() in w['ukrainian'].lower()]
        
        self.populate_word_list(results)
    
    def on_search_language_changed(self):
        """Handle search language toggle"""
        if self.sender() == self.search_english_btn:
            self.search_english_btn.setChecked(True)
            self.search_ukrainian_btn.setChecked(False)
        else:
            self.search_english_btn.setChecked(False)
            self.search_ukrainian_btn.setChecked(True)
        
        # Re-perform search
        self.perform_search()
    
    def on_word_selected(self, item):
        """Handle word selection"""
        word_data = item.data(Qt.ItemDataRole.UserRole)
        if word_data:
            self.display_word_details(word_data)
            self.current_word = word_data
            self.word_selected.emit(word_data)
    
    def on_category_selected(self, item):
        """Handle category selection"""
        category_data = item.data(Qt.ItemDataRole.UserRole)
        if category_data:
            self.load_words_by_category(category_data['id'])
    
    def on_level_filter_changed(self, level):
        """Handle level filter change"""
        if level == 'All Levels':
            # Load some default words
            self.load_words_by_level('A1')
        else:
            self.load_words_by_level(level)
    
    def display_word_details(self, word):
        """Display detailed information about a word"""
        self.word_title.setText(word['english'])
        
        # Pronunciation
        pronunciation = word.get('pronunciation', '')
        if pronunciation:
            self.pronunciation_label.setText(f"[{pronunciation}]")
        else:
            self.pronunciation_label.setText("")
        
        # Translation
        self.translation_label.setText(word['ukrainian'])
        
        # Word info
        self.pos_label.setText(word.get('part_of_speech', 'Unknown'))
        self.level_label.setText(word.get('level', 'Unknown'))
        self.category_label.setText(word.get('category_name', 'Unknown'))
        
        # Example sentence
        example = word.get('example_sentence', '')
        if example:
            self.example_sentence.setText(example)
            example_translation = word.get('example_translation', '')
            if example_translation:
                self.example_translation.setText(f"Translation: {example_translation}")
            else:
                self.example_translation.setText("")
        else:
            self.example_sentence.setText("No example available")
            self.example_translation.setText("")
    
    def add_current_word_to_study(self):
        """Add current word to study list"""
        if self.current_word:
            self.add_to_study.emit(self.current_word['id'])
            # Could show confirmation message
    
    def pronounce_current_word(self):
        """Pronounce the current word (simulated)"""
        if self.current_word:
            # In a real app, this would use text-to-speech
            print(f"Pronouncing: {self.current_word['english']}")
            # Could play audio file or use TTS engine
