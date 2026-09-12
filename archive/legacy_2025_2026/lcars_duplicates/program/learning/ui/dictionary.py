# Dictionary Widget for English Learning Application
# Interactive dictionary with search, pronunciation, and examples
# LCARS abstractions for UI components (no direct PyQt6 usage)

from lcars.base.default import RandomButtonColor, FontStyle
from lcars.base.type import Chassis, Label, Frame, GridLayout, Timer, ScrollArea, Widget, LineEdit, TextEdit
from lcars.base.signal import Signal
from lcars.base.components import SystemComponent
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment, PushButton, ProgressBar

# All LCARS components imported directly from abstractions above

# Default dictionary color set using built-in LCARS defaults.
def buildDictionaryColors() -> dict:
    return {
        'panelBg': '#111111',
        'text': '#FFFFFF',
        'accent': RandomButtonColor(),
        'highlight': RandomButtonColor('panels'),
        'border': RandomButtonColor('accent'),
        'edge': RandomButtonColor('buttons'),
        'action': RandomButtonColor('alert'),
        'detail': RandomButtonColor('panels'),
        'support': RandomButtonColor('buttons'),
        'notice': RandomButtonColor('accent'),
    }

class DictionaryWidget(SystemComponent):
    # Dictionary widget with search and word details

    # Signals
    wordSelected = Signal(dict)
    addToStudy = Signal(int)

    def __init__(self, dbManager):
        super().__init__()
        self.db = dbManager
        self.currentWord = None
        self.colors = buildDictionaryColors()

        self.initUI()
        self.setupConnections()
        self.loadRecentWords()
    
    def initUI(self):
        # Initialize the dictionary UI
        layout = VBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.createHeader(layout)

        bodyLayout = HBoxLayout()
        bodyLayout.setSpacing(20)
        bodyLayout.addWidget(self.createSearchPanel(), 1)
        bodyLayout.addWidget(self.createWordDetailsPanel(), 2)

        layout.addLayout(bodyLayout, 1)
        self.applyStyling()

    def createHeader(self, layout):
        # Create the header section
        headerFrame = Frame()
        headerLayout = HBoxLayout(headerFrame)
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.setSpacing(20)

        elbow = LCARSElbow('top-left', self.colors['accent'])
        elbow.setMinimumSize(220, 80)
        headerLayout.addWidget(elbow)

        titleLabel = Label('ENGLISH-UKRAINIAN DICTIONARY')
        titleLabel.setStyleSheet(f"color: {self.colors['border']}; {FontStyle(28, 'bold')}; padding: 18px;")
        headerLayout.addWidget(titleLabel, 1)

        self.levelFilter = ComboBox()
        self.levelFilter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.levelFilter.setStyleSheet(f"\n            QComboBox {{\n                background-color: {self.colors['panelBg']};\n                color: {self.colors['text']};\n                border: 2px solid {self.colors['highlight']};\n                padding: 8px 12px;\n                {FontStyle(14, 'normal')}\n                border-radius: 6px;\n            }}\n            QComboBox::drop-down {{ border: none; }}\n            QComboBox::down-arrow {{\n                image: none;\n                border-left: 5px solid transparent;\n                border-right: 5px solid transparent;\n                border-top: 5px solid {self.colors['highlight']};\n            }}\n        ")
        headerLayout.addWidget(self.levelFilter)

        layout.addWidget(headerFrame)

    def createSearchPanel(self, layout=None):
        # Create the search and word list panel
        if layout is None:
            panel = Widget()
            layout = VBoxLayout(panel)
        else:
            panel = layout

        searchFrame = Frame()
        searchFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['accent']};\n                border-radius: 10px;\n            }}\n        ")

        searchLayout = VBoxLayout(searchFrame)
        searchLayout.setContentsMargins(18, 18, 18, 18)
        searchLayout.setSpacing(12)
        
        # Search title
        title = Label("◤ SEARCH DICTIONARY")
        title.setStyleSheet(f"color: {self.colors['support']}; {FontStyle(18, 'normal')}; margin-bottom: 10px;")
        searchLayout.addWidget(title)

        self.searchInput = LineEdit()
        self.searchInput.setPlaceholderText('Enter English or Ukrainian word...')
        self.searchInput.setStyleSheet(f"\n            QLineEdit {{\n                background-color: #000000;\n                color: {self.colors['text']};\n                border: 2px solid {self.colors['highlight']};\n                padding: 10px;\n                {FontStyle(14, 'normal')}\n                border-radius: 6px;\n            }}\n        ")
        searchLayout.addWidget(self.searchInput)

        optionsLayout = HBoxLayout()
        optionsLayout.setSpacing(10)

        self.searchEnglishBtn = LCARSButton('English', self.colors['highlight'])
        self.searchEnglishBtn.setCheckable(True)
        self.searchEnglishBtn.setChecked(True)
        optionsLayout.addWidget(self.searchEnglishBtn)

        self.searchUkrainianBtn = LCARSButton('Ukrainian', self.colors['detail'])
        self.searchUkrainianBtn.setCheckable(True)
        optionsLayout.addWidget(self.searchUkrainianBtn)

        searchLayout.addLayout(optionsLayout)

        listTitle = Label('◤ WORD RESULTS')
        listTitle.setStyleSheet(f"color: {self.colors['border']}; {FontStyle(16, 'normal')}; margin: 15px 0 5px 0;")
        searchLayout.addWidget(listTitle)

        self.wordList = ListWidget()
        self.wordList.setStyleSheet(f"\n            QListWidget {{\n                background-color: #000000;\n                color: {self.colors['text']};\n                border: 1px solid {self.colors['border']};\n                {FontStyle(14, 'normal')}\n            }}\n            QListWidget::item {{ padding: 8px; border-bottom: 1px solid #222222; }}\n            QListWidget::item:selected {{ background-color: {self.colors['border']}; color: black; }}\n            QListWidget::item:hover {{ background-color: #222222; }}\n        ")
        searchLayout.addWidget(self.wordList)

        categoryTitle = Label('◤ CATEGORIES')
        categoryTitle.setStyleSheet(f"color: {self.colors['support']}; {FontStyle(16, 'normal')}; margin: 15px 0 5px 0;")
        searchLayout.addWidget(categoryTitle)

        self.categoryList = ListWidget()
        self.categoryList.setMaximumHeight(150)
        self.categoryList.setStyleSheet(f"\n            QListWidget {{\n                background-color: #000000;\n                color: {self.colors['text']};\n                border: 1px solid {self.colors['support']};\n                {FontStyle(12, 'normal')}\n            }}\n            QListWidget::item {{ padding: 8px; border-bottom: 1px solid #222222; }}\n            QListWidget::item:selected {{ background-color: {self.colors['support']}; color: black; }}\n        ")
        searchLayout.addWidget(self.categoryList)

        layout.addWidget(searchFrame)

        return panel
    
    def createWordDetailsPanel(self, layout=None):
        # Create the word details panel
        if layout is None:
            panel = Widget()
            layout = VBoxLayout(panel)
        else:
            panel = layout

        detailsFrame = Frame()
        detailsFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['detail']};\n                border-radius: 10px;\n            }}\n        ")

        detailsLayout = VBoxLayout(detailsFrame)
        detailsLayout.setContentsMargins(18, 18, 18, 18)
        detailsLayout.setSpacing(12)

        self.wordTitle = Label('Select a word to view details')
        self.wordTitle.setStyleSheet(f"color: {self.colors['detail']}; {FontStyle(24, 'bold')}; margin-bottom: 10px;")
        detailsLayout.addWidget(self.wordTitle)

        self.pronunciationLabel = Label('')
        self.pronunciationLabel.setStyleSheet('\n            color: #CCCCCC;\n            font-size: 16px;\n            font-style: italic;\n            margin-bottom: 10px;\n        ')
        detailsLayout.addWidget(self.pronunciationLabel)

        self.translationLabel = Label('')
        self.translationLabel.setStyleSheet(f"\n            color: {self.colors['notice']};\n            {FontStyle(20, 'normal')}\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.translationLabel)

        infoGrid = GridLayout()
        self.posLabel = Label('')
        infoGrid.addWidget(Label('Part of Speech:'), 0, 0)
        infoGrid.addWidget(self.posLabel, 0, 1)

        self.levelLabel = Label('')
        infoGrid.addWidget(Label('Level:'), 1, 0)
        infoGrid.addWidget(self.levelLabel, 1, 1)

        self.categoryLabel = Label('')
        infoGrid.addWidget(Label('Category:'), 2, 0)
        infoGrid.addWidget(self.categoryLabel, 2, 1)
        detailsLayout.addLayout(infoGrid)

        exampleTitle = Label('◤ EXAMPLE SENTENCE')
        exampleTitle.setStyleSheet(f"color: {self.colors['accent']}; {FontStyle(16, 'normal')}; margin: 20px 0 5px 0;")
        detailsLayout.addWidget(exampleTitle)

        self.exampleSentence = TextEdit()
        self.exampleSentence.setReadOnly(True)
        self.exampleSentence.setMaximumHeight(120)
        self.exampleSentence.setStyleSheet(f"\n            QTextEdit {{\n                background-color: #000000;\n                color: {self.colors['text']};\n                border: 1px solid {self.colors['accent']};\n                {FontStyle(14, 'normal')}\n            }}\n        ")
        detailsLayout.addWidget(self.exampleSentence)

        self.exampleTranslation = Label('')
        self.exampleTranslation.setStyleSheet('\n            color: #CCCCCC;\n            font-size: 14px;\n            font-style: italic;\n            margin-bottom: 15px;\n        ')
        detailsLayout.addWidget(self.exampleTranslation)

        actionsLayout = HBoxLayout()
        actionsLayout.setSpacing(10)

        self.addToStudyBtn = LCARSButton('Add to Study', self.colors['accent'])
        self.addToStudyBtn.clicked.connect(self.addCurrentWordToStudy)
        actionsLayout.addWidget(self.addToStudyBtn)

        self.pronounceBtn = LCARSButton('Pronounce', self.colors['highlight'])
        self.pronounceBtn.clicked.connect(self.pronounceCurrentWord)
        actionsLayout.addWidget(self.pronounceBtn)

        detailsLayout.addLayout(actionsLayout)
        detailsLayout.addStretch()

        layout.addWidget(detailsFrame)

        return panel
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet('\n            QWidget {\n                background-color: #000000;\n                color: white;\n                font-family: "Arial", sans-serif;\n            }\n            QLabel {\n                color: white;\n            }\n        ')

    def setupConnections(self):
        self.searchInput.textChanged.connect(self.onSearchTextChanged)
        self.searchInput.returnPressed.connect(self.performSearch)

        self.searchEnglishBtn.clicked.connect(self.onSearchLanguageChanged)
        self.searchUkrainianBtn.clicked.connect(self.onSearchLanguageChanged)

        self.wordList.itemClicked.connect(self.onWordSelected)
        self.categoryList.itemClicked.connect(self.onCategorySelected)
        self.levelFilter.currentTextChanged.connect(self.onLevelFilterChanged)

        self.searchTimer = Timer()
        self.searchTimer.setSingleShot(True)
        self.searchTimer.timeout.connect(self.performSearch)
    
    def loadRecentWords(self):
        self.categoryList.clear()
        for category in self.db.getAllCategories():
            item = ListWidgetItem(f"{category['name']} ({category['level']})")
            item.setData(32, category)
            self.categoryList.addItem(item)
        self.loadWordsByLevel('A1')

    def loadWordsByLevel(self, level):
        words = self.db.getWordsByLevel(level, limit=50)
        self.populateWordList(words)

    def loadWordsByCategory(self, categoryId):
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None
        words = self.db.getWordsByCategory(categoryId, level)
        self.populateWordList(words)

    def populateWordList(self, words):
        self.wordList.clear()
        for word in words:
            eng = word.get('English', word.get('english', ''))
            ukr = word.get('Ukrainian', word.get('ukrainian', ''))
            pos = word.get('PartOfSpeech', word.get('part_of_speech'))
            displayText = f"{eng} - {ukr}"
            if pos:
                displayText += f" ({pos})"
            item = ListWidgetItem(displayText)
            item.setData(32, word)
            self.wordList.addItem(item)

    def onSearchTextChanged(self, text):
        if len(text) >= 2 or len(text) == 0:
            self.searchTimer.start(300)

    def performSearch(self):
        searchText = self.searchInput.text().strip()
        if not searchText:
            level = self.levelFilter.currentText()
            if level != 'All Levels':
                self.loadWordsByLevel(level)
            return

        searchEnglish = self.searchEnglishBtn.isChecked()
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None

        results = self.db.searchWords(searchText, level)
        if searchEnglish:
            results = [w for w in results if searchText.lower() in w.get('English', w.get('english','')).lower()]
        else:
            results = [w for w in results if searchText.lower() in w.get('Ukrainian', w.get('ukrainian','')).lower()]
        self.populateWordList(results)

    def onSearchLanguageChanged(self):
        if self.sender() == self.searchEnglishBtn:
            self.searchEnglishBtn.setChecked(True)
            self.searchUkrainianBtn.setChecked(False)
        else:
            self.searchEnglishBtn.setChecked(False)
            self.searchUkrainianBtn.setChecked(True)
        self.performSearch()

    def onWordSelected(self, item):
        wordData = item.data(32)
        if wordData:
            self.displayWordDetails(wordData)
            self.currentWord = wordData
            self.wordSelected.emit(wordData)

    def onCategorySelected(self, item):
        categoryData = item.data(32)
        if categoryData:
            self.loadWordsByCategory(categoryData['id'])

    def onLevelFilterChanged(self, level):
        if level == 'All Levels':
            self.loadWordsByLevel('A1')
        else:
            self.loadWordsByLevel(level)

    def displayWordDetails(self, word):
        eng = word.get('English', word.get('english', ''))
        ukr = word.get('Ukrainian', word.get('ukrainian', ''))
        self.wordTitle.setText(eng)
        pronunciation = word.get('Pronunciation', word.get('pronunciation', ''))
        self.pronunciationLabel.setText(f"[{pronunciation}]" if pronunciation else '')
        self.translationLabel.setText(ukr)
        self.posLabel.setText(word.get('PartOfSpeech', word.get('part_of_speech', 'Unknown')))
        self.levelLabel.setText(word.get('Level', word.get('level', 'Unknown')))
        self.categoryLabel.setText(word.get('CategoryName', word.get('category_name', 'Unknown')))

        example = word.get('example_sentence', '')
        if example:
            self.exampleSentence.setText(example)
            translation = word.get('example_translation', '')
            self.exampleTranslation.setText(f"Translation: {translation}" if translation else '')
        else:
            self.exampleSentence.setText('No example available')
            self.exampleTranslation.setText('')

    def addCurrentWordToStudy(self):
        if self.currentWord:
            self.addToStudy.emit(self.currentWord.get('Id', self.currentWord.get('id')))

    def pronounceCurrentWord(self):
        if self.currentWord:
            print(f"Pronouncing: {self.currentWord.get('English', self.currentWord.get('english'))}")

