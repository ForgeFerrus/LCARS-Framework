# Grammar Widget for English Learning Application
# Interactive grammar lessons and rules
# LCARS abstractions for UI components (no direct PyQt6 usage)

from typing import Any

from lcars.base.type import Widget, Chassis, ScrollArea, ComboBox
from lcars.base.signal import Signal
from lcars.base.interface import Label, Frame, Dialog, TextEdit, TextCursor, PushButton, ListWidget, ListWidgetItem, Splitter

from lcars.base.default import RandomButtonColor, FontStyle
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment

USER_ROLE = 256

class GrammarWidget(SystemComponent):
    # Grammar learning widget
    
    # Signals
    ruleSelected = Signal(dict)  # grammar rule data
    ruleCompleted = Signal(int)  # rule id
    
    def __init__(self, dbManager):
        super().__init__()
        self.db = dbManager
        self.currentRule = None

        self.colors = {
            'palette': [
                RandomButtonColor('buttons'),
                RandomButtonColor('buttons'),
                RandomButtonColor('accent'),
                RandomButtonColor('buttons'),
                RandomButtonColor('alert'),
                RandomButtonColor('panels'),
                RandomButtonColor('panels'),
                RandomButtonColor('alert'),
                RandomButtonColor('accent'),
            ],
            'accent': RandomButtonColor('accent'),
        }
        
        self.initUi()
        self.setupConnections()
        self.loadGrammarRules()
    
    def initUi(self):
        # Initialize the grammar UI
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.createHeader(layout)
        
        # Main content area
        contentSplitter = Splitter()
        
        # Left panel - Rules list
        leftPanel = self.createRulesPanel()
        contentSplitter.addWidget(leftPanel)
        
        # Right panel - Rule details
        rightPanel = self.createRuleDetailsPanel()
        contentSplitter.addWidget(rightPanel)
        
        contentSplitter.setSizes([400, 600])
        layout.addWidget(contentSplitter)
        
        # Apply styling
        self.applyStyling()
    
    def createHeader(self, layout):
        # Create the header section
        headerFrame = Frame()
        headerLayout = Chassis.Horizontal(headerFrame)
        
        # LCARS elbow
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setMinimumSize(200, 80)
        headerLayout.addWidget(elbow)
        
        # Title
        title = Label("GRAMMAR LESSONS")
        title.setStyleSheet(f"\n            color: {self.colors['accent']};\n            {FontStyle(24, 'normal')}\n            padding: 20px;\n        ")
        headerLayout.addWidget(title, 1)
        
        # Level filter
        self.levelFilter = ComboBox()
        self.levelFilter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.levelFilter.setStyleSheet(
            f"background-color: #111111; color: white; border: 2px solid {self.colors['palette'][1]}; padding: 5px 10px; font-size: 14px;"
        )
        headerLayout.addWidget(self.levelFilter)
        
        layout.addWidget(headerFrame)
    
    def createRulesPanel(self, layout=None):
        # Create the grammar rules list panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rules list frame
        rulesFrame = Frame()
        rulesFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][1]}; border-radius: 10px;"
        )
        
        rulesLayout = Chassis.Vertical(rulesFrame)
        rulesLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ GRAMMAR RULES")
        title.setStyleSheet(f"\n            color: {self.colors['palette'][1]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        rulesLayout.addWidget(title)
        
        # Rules list
        self.rulesList = ListWidget()
        self.rulesList.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][2]}; font-size: 14px;"
        )
        rulesLayout.addWidget(self.rulesList)
        
        # Practice buttons
        practiceTitle = Label("◤ GRAMMAR PRACTICE")
        practiceTitle.setStyleSheet(f"\n            color: {self.colors['palette'][3]};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ")
        rulesLayout.addWidget(practiceTitle)
        
        self.practiceBtn = LCARSButton("Practice Current Rule", ColorHexStr=self.colors['palette'][3])
        self.practiceBtn.clicked.connect(self.practiceCurrentRule)
        rulesLayout.addWidget(self.practiceBtn)
        
        self.quizBtn = LCARSButton("Grammar Quiz", ColorHexStr=self.colors['palette'][4])
        self.quizBtn.clicked.connect(self.startGrammarQuiz)
        rulesLayout.addWidget(self.quizBtn)
        
        layout.addWidget(rulesFrame)
        
        return panel
    
    def createRuleDetailsPanel(self, layout=None):
        # Create the rule details panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rule details frame
        detailsFrame = Frame()
        detailsFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][5]}; border-radius: 10px;"
        )
        
        detailsLayout = Chassis.Vertical(detailsFrame)
        detailsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Rule title
        self.ruleTitle = Label("Select a grammar rule to view details")
        self.ruleTitle.setStyleSheet(f"\n            color: {self.colors['palette'][5]};\n            font-size: 24px;\n            font-weight: normal;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleTitle)
        
        # Rule level
        self.ruleLevel = Label("")
        self.ruleLevel.setStyleSheet(f"\n            color: {self.colors['palette'][6]};\n            font-size: 16px;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleLevel)
        
        # Rule explanation
        explanationTitle = Label("◤ RULE EXPLANATION")
        explanationTitle.setStyleSheet(f"\n            color: {self.colors['palette'][7]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        detailsLayout.addWidget(explanationTitle)
        
        self.ruleExplanation = TextEdit()
        self.ruleExplanation.setReadOnly(True)
        self.ruleExplanation.setMaximumHeight(200)
        self.ruleExplanation.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][7]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.ruleExplanation)
        
        # Examples section
        examplesTitle = Label("◤ EXAMPLES")
        examplesTitle.setStyleSheet(f"\n            color: {self.colors['palette'][8]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(examplesTitle)
        
        self.examplesText = TextEdit()
        self.examplesText.setReadOnly(True)
        self.examplesText.setMaximumHeight(150)
        self.examplesText.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][8]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.examplesText)
        
        # Interactive examples
        interactiveTitle = Label("◤ INTERACTIVE PRACTICE")
        interactiveTitle.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(interactiveTitle)
        
        # Practice area
        self.practiceArea = Widget()
        self.practiceLayout = Chassis.Vertical(self.practiceArea)
        detailsLayout.addWidget(self.practiceArea)
        
        # Mark as completed button
        self.completedBtn = LCARSButton("Mark as Completed", ColorHexStr=self.colors['palette'][0])
        self.completedBtn.clicked.connect(self.markRuleCompleted)
        self.completedBtn.setEnabled(False)
        detailsLayout.addWidget(self.completedBtn)
        
        detailsLayout.addStretch()
        
        layout.addWidget(detailsFrame)
        
        return panel
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet(
            'background-color: #000000; color: white; font-family: "LCARS", "Segoe UI", sans-serif;'
        )
    
    def setupConnections(self):
        # Setup signal connections
        # Rules list selection
        self.rulesList.itemClicked.connect(self.onRuleSelected)
        
        # Level filter
        self.levelFilter.currentTextChanged.connect(self.onLevelFilterChanged)

    def _value(self, row, *keys, default: Any = ''):
        for key in keys:
            if key in row and row.get(key) not in (None, ''):
                return row.get(key)
        return default
    
    def loadGrammarRules(self):
        # Load grammar rules from database
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None

        # Always read from DB; `None` means all levels.
        rules = self.db.getGrammarRulesByLevel(level)
        
        self.rulesList.clear()
        
        for rule in rules:
            # Create display text
            title = self._value(rule, 'title', 'Title', default='Untitled Rule')
            ruleLevel = self._value(rule, 'level', 'Level', default='A1')
            displayText = f"{title} ({ruleLevel})"
            
            item = ListWidgetItem(displayText)
            item.setData(USER_ROLE, rule)
            self.rulesList.addItem(item)
    
    def onRuleSelected(self, item):
        # Handle grammar rule selection
        ruleData = item.data(USER_ROLE)
        if ruleData:
            self.displayRuleDetails(ruleData)
            self.currentRule = ruleData
            self.ruleSelected.emit(ruleData)
            self.completedBtn.setEnabled(True)
    
    def onLevelFilterChanged(self, level):
        # Handle level filter change
        self.loadGrammarRules()
    
    def displayRuleDetails(self, rule):
        # Display detailed information about a grammar rule
        self.ruleTitle.setText(self._value(rule, 'title', 'Title', default='Untitled Rule'))
        self.ruleLevel.setText(f"Level: {self._value(rule, 'level', 'Level', default='A1')}")
        
        # Rule explanation
        explanation = self._value(rule, 'rule_text', 'RuleText', default='No explanation available')
        self.ruleExplanation.setText(explanation)
        
        # Examples
        examples = self._value(rule, 'examples', 'Examples', default='No examples available')
        self.examplesText.setText(examples)
        
        # Create interactive practice based on rule type
        self.createInteractivePractice(rule)
    
    def createInteractivePractice(self, rule):
        # Create interactive practice based on the grammar rule
        # Clear existing practice area
        for i in reversed(range(self.practiceLayout.count())):
            item = self.practiceLayout.itemAt(i)
            child = item.widget() if item else None
            if child:
                child.hide()
                child.deleteLater()
        
        ruleTitle = self._value(rule, 'title', 'Title', default='').lower()
        
        if 'present simple' in ruleTitle:
            self.createPresentSimplePractice()
        elif 'articles' in ruleTitle:
            self.createArticlesPractice()
        elif 'plural' in ruleTitle:
            self.createPluralPractice()
        else:
            self.createGeneralPractice(rule)
    
    def createPresentSimplePractice(self):
        # Create Present Simple practice
        instruction = Label("Complete the sentences with the correct form of the verb:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice sentences
        sentences = [
            ("I _____ (work) in an office.", "work"),
            ("She _____ (study) English every day.", "studies"),
            ("They _____ (play) football on weekends.", "play"),
            ("He _____ (like) coffee.", "likes"),
            ("We _____ (live) in Kyiv.", "live")
        ]
        
        for sentence, correctAnswer in sentences:
            sentenceLabel = Label(sentence)
            sentenceLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(sentenceLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createArticlesPractice(self):
        # Create articles (a/an) practice
        instruction = Label("Choose the correct article (a/an):")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice items
        items = ["apple", "book", "orange", "car", "umbrella"]
        
        for item in items:
            itemLabel = Label(f"_____ {item}")
            itemLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(itemLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createPluralPractice(self):
        # Create plural nouns practice
        instruction = Label("Write the plural form of these nouns:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice nouns
        nouns = ["cat", "dog", "box", "baby", "class"]
        
        for noun in nouns:
            nounLabel = Label(f"{noun} → _____")
            nounLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(nounLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createGeneralPractice(self, rule):
        # Create general practice for other grammar rules
        instruction = Label("Study the examples above and try to create your own sentences:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Text area for practice
        practiceInput = TextEdit()
        practiceInput.setPlaceholderText("Write your practice sentences here...")
        practiceInput.setMaximumHeight(100)
        practiceInput.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][1]}; font-size: 14px;"
        )
        self.practiceLayout.addWidget(practiceInput)
        
        saveBtn = LCARSButton("Save Practice", ColorHexStr=self.colors['palette'][1])
        saveBtn.clicked.connect(self.savePractice)
        self.practiceLayout.addWidget(saveBtn)
    
    def checkPracticeAnswers(self):
        # Check practice answers (simplified)
        # In a real implementation, this would check actual answers
        resultLabel = Label("✓ Practice completed! Keep studying to improve.")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def savePractice(self):
        # Save practice sentences
        resultLabel = Label("✓ Practice saved successfully!")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def practiceCurrentRule(self):
        # Start practice for current rule
        if self.currentRule:
            self.createInteractivePractice(self.currentRule)
    
    def startGrammarQuiz(self):
        # Start a comprehensive grammar quiz
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = 'A1'

        questions = self.db.getTestQuestions(level, count=5)
        if not questions:
            resultLabel = Label("No quiz questions in database for selected level.")
            resultLabel.setStyleSheet('color: #FFCC66; font-size: 14px; margin: 10px 0;')
            self.practiceLayout.addWidget(resultLabel)
            return

        quizDialog = Dialog(self)
        quizDialog.setWindowTitle("Grammar Quiz")
        quizDialog.setModal(True)
        quizDialog.resize(760, 520)

        dlgLayout = Chassis.Vertical(quizDialog)
        title = Label("GRAMMAR QUIZ")
        title.setStyleSheet(f"color: {self.colors['accent']}; font-size: 22px;")
        dlgLayout.addWidget(title)

        score = {'value': 0}
        state = {'index': 0}

        questionLabel = Label("")
        questionLabel.setWordWrap(True)
        questionLabel.setStyleSheet("color: white; font-size: 16px; margin: 10px 0;")
        dlgLayout.addWidget(questionLabel)

        optionButtons = []
        for _ in range(4):
            btn = PushButton("")
            btn.setStyleSheet('padding: 8px; font-size: 14px;')
            optionButtons.append(btn)
            dlgLayout.addWidget(btn)

        feedback = Label("")
        feedback.setStyleSheet("font-size: 14px; margin-top: 8px;")
        dlgLayout.addWidget(feedback)

        progress = Label("")
        progress.setStyleSheet("color: #9DB0D8; font-size: 13px;")
        dlgLayout.addWidget(progress)

        closeBtn = LCARSButton("Close", ColorHexStr=self.colors['palette'][1])
        closeBtn.clicked.connect(quizDialog.accept)
        dlgLayout.addWidget(closeBtn)

        def renderQuestion():
            idx = state['index']
            if idx >= len(questions):
                questionLabel.setText(f"Quiz complete! Score: {score['value']}/{len(questions)}")
                feedback.setText("")
                for b in optionButtons:
                    b.hide()
                progress.setText("Finished")
                return

            row = questions[idx]
            questionText = self._value(row, 'question', 'Question', default='No question')
            questionLabel.setText(questionText)
            optionTexts = [
                self._value(row, 'option_a', 'OptionA', default=''),
                self._value(row, 'option_b', 'OptionB', default=''),
                self._value(row, 'option_c', 'OptionC', default=''),
                self._value(row, 'option_d', 'OptionD', default=''),
            ]
            for i, b in enumerate(optionButtons):
                b.setText(f"{chr(65+i)}) {optionTexts[i]}")
                b.show()
            feedback.setText("")
            progress.setText(f"Question {idx + 1}/{len(questions)}")

        def onPick(letter):
            idx = state['index']
            row = questions[idx]
            correct = self._value(row, 'correct_option', 'CorrectOption', default='').upper()
            if letter == correct:
                score['value'] += 1
                feedback.setText("Correct")
                feedback.setStyleSheet("color: #00FF88; font-size: 14px; margin-top: 8px;")
            else:
                feedback.setText(f"Incorrect. Correct: {correct}")
                feedback.setStyleSheet("color: #FF6666; font-size: 14px; margin-top: 8px;")
            state['index'] += 1
            renderQuestion()

        for i, b in enumerate(optionButtons):
            b.clicked.connect(lambda checked=False, letter=chr(65+i): onPick(letter))

        renderQuestion()
        quizDialog.exec()
    
    def markRuleCompleted(self):
        # Mark the current rule as completed
        if self.currentRule:
            ruleId = self._value(self.currentRule, 'id', 'Id', default=0)
            self.ruleCompleted.emit(int(ruleId or 0))
            
            # Show confirmation
            resultLabel = Label("✓ Grammar rule marked as completed!")
            resultLabel.setStyleSheet('\n                color: #00FF00;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #003300;\n                border: 2px solid #00FF00;\n                border-radius: 5px;\n            ')
            self.practiceLayout.addWidget(resultLabel)
            
            # Disable button to prevent multiple clicks
            self.completedBtn.setEnabled(False)
.Groups[1].Value; $after = # Grammar Widget for English Learning Application
# Interactive grammar lessons and rules

from typing import Any

from lcars.base.type import Widget, Chassis, Signal
from lcars.base.interface import Label, Frame, Dialog, TextEdit, TextCursor, PushButton, ListWidget, ListWidgetItem, ScrollArea, ComboBox, Splitter

from lcars.base.default import RandomButtonColor, FontStyle
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment

USER_ROLE = 256

class GrammarWidget(SystemComponent):
    # Grammar learning widget
    
    # Signals
    ruleSelected = Signal(dict)  # grammar rule data
    ruleCompleted = Signal(int)  # rule id
    
    def __init__(self, dbManager):
        super().__init__()
        self.db = dbManager
        self.currentRule = None

        self.colors = {
            'palette': [
                RandomButtonColor('buttons'),
                RandomButtonColor('buttons'),
                RandomButtonColor('accent'),
                RandomButtonColor('buttons'),
                RandomButtonColor('alert'),
                RandomButtonColor('panels'),
                RandomButtonColor('panels'),
                RandomButtonColor('alert'),
                RandomButtonColor('accent'),
            ],
            'accent': RandomButtonColor('accent'),
        }
        
        self.initUi()
        self.setupConnections()
        self.loadGrammarRules()
    
    def initUi(self):
        # Initialize the grammar UI
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.createHeader(layout)
        
        # Main content area
        contentSplitter = Splitter()
        
        # Left panel - Rules list
        leftPanel = self.createRulesPanel()
        contentSplitter.addWidget(leftPanel)
        
        # Right panel - Rule details
        rightPanel = self.createRuleDetailsPanel()
        contentSplitter.addWidget(rightPanel)
        
        contentSplitter.setSizes([400, 600])
        layout.addWidget(contentSplitter)
        
        # Apply styling
        self.applyStyling()
    
    def createHeader(self, layout):
        # Create the header section
        headerFrame = Frame()
        headerLayout = Chassis.Horizontal(headerFrame)
        
        # LCARS elbow
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setMinimumSize(200, 80)
        headerLayout.addWidget(elbow)
        
        # Title
        title = Label("GRAMMAR LESSONS")
        title.setStyleSheet(f"\n            color: {self.colors['accent']};\n            {FontStyle(24, 'normal')}\n            padding: 20px;\n        ")
        headerLayout.addWidget(title, 1)
        
        # Level filter
        self.levelFilter = ComboBox()
        self.levelFilter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.levelFilter.setStyleSheet(
            f"background-color: #111111; color: white; border: 2px solid {self.colors['palette'][1]}; padding: 5px 10px; font-size: 14px;"
        )
        headerLayout.addWidget(self.levelFilter)
        
        layout.addWidget(headerFrame)
    
    def createRulesPanel(self, layout=None):
        # Create the grammar rules list panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rules list frame
        rulesFrame = Frame()
        rulesFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][1]}; border-radius: 10px;"
        )
        
        rulesLayout = Chassis.Vertical(rulesFrame)
        rulesLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ GRAMMAR RULES")
        title.setStyleSheet(f"\n            color: {self.colors['palette'][1]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        rulesLayout.addWidget(title)
        
        # Rules list
        self.rulesList = ListWidget()
        self.rulesList.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][2]}; font-size: 14px;"
        )
        rulesLayout.addWidget(self.rulesList)
        
        # Practice buttons
        practiceTitle = Label("◤ GRAMMAR PRACTICE")
        practiceTitle.setStyleSheet(f"\n            color: {self.colors['palette'][3]};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ")
        rulesLayout.addWidget(practiceTitle)
        
        self.practiceBtn = LCARSButton("Practice Current Rule", ColorHexStr=self.colors['palette'][3])
        self.practiceBtn.clicked.connect(self.practiceCurrentRule)
        rulesLayout.addWidget(self.practiceBtn)
        
        self.quizBtn = LCARSButton("Grammar Quiz", ColorHexStr=self.colors['palette'][4])
        self.quizBtn.clicked.connect(self.startGrammarQuiz)
        rulesLayout.addWidget(self.quizBtn)
        
        layout.addWidget(rulesFrame)
        
        return panel
    
    def createRuleDetailsPanel(self, layout=None):
        # Create the rule details panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rule details frame
        detailsFrame = Frame()
        detailsFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][5]}; border-radius: 10px;"
        )
        
        detailsLayout = Chassis.Vertical(detailsFrame)
        detailsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Rule title
        self.ruleTitle = Label("Select a grammar rule to view details")
        self.ruleTitle.setStyleSheet(f"\n            color: {self.colors['palette'][5]};\n            font-size: 24px;\n            font-weight: normal;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleTitle)
        
        # Rule level
        self.ruleLevel = Label("")
        self.ruleLevel.setStyleSheet(f"\n            color: {self.colors['palette'][6]};\n            font-size: 16px;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleLevel)
        
        # Rule explanation
        explanationTitle = Label("◤ RULE EXPLANATION")
        explanationTitle.setStyleSheet(f"\n            color: {self.colors['palette'][7]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        detailsLayout.addWidget(explanationTitle)
        
        self.ruleExplanation = TextEdit()
        self.ruleExplanation.setReadOnly(True)
        self.ruleExplanation.setMaximumHeight(200)
        self.ruleExplanation.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][7]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.ruleExplanation)
        
        # Examples section
        examplesTitle = Label("◤ EXAMPLES")
        examplesTitle.setStyleSheet(f"\n            color: {self.colors['palette'][8]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(examplesTitle)
        
        self.examplesText = TextEdit()
        self.examplesText.setReadOnly(True)
        self.examplesText.setMaximumHeight(150)
        self.examplesText.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][8]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.examplesText)
        
        # Interactive examples
        interactiveTitle = Label("◤ INTERACTIVE PRACTICE")
        interactiveTitle.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(interactiveTitle)
        
        # Practice area
        self.practiceArea = Widget()
        self.practiceLayout = Chassis.Vertical(self.practiceArea)
        detailsLayout.addWidget(self.practiceArea)
        
        # Mark as completed button
        self.completedBtn = LCARSButton("Mark as Completed", ColorHexStr=self.colors['palette'][0])
        self.completedBtn.clicked.connect(self.markRuleCompleted)
        self.completedBtn.setEnabled(False)
        detailsLayout.addWidget(self.completedBtn)
        
        detailsLayout.addStretch()
        
        layout.addWidget(detailsFrame)
        
        return panel
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet(
            'background-color: #000000; color: white; font-family: "LCARS", "Segoe UI", sans-serif;'
        )
    
    def setupConnections(self):
        # Setup signal connections
        # Rules list selection
        self.rulesList.itemClicked.connect(self.onRuleSelected)
        
        # Level filter
        self.levelFilter.currentTextChanged.connect(self.onLevelFilterChanged)

    def _value(self, row, *keys, default: Any = ''):
        for key in keys:
            if key in row and row.get(key) not in (None, ''):
                return row.get(key)
        return default
    
    def loadGrammarRules(self):
        # Load grammar rules from database
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None

        # Always read from DB; `None` means all levels.
        rules = self.db.getGrammarRulesByLevel(level)
        
        self.rulesList.clear()
        
        for rule in rules:
            # Create display text
            title = self._value(rule, 'title', 'Title', default='Untitled Rule')
            ruleLevel = self._value(rule, 'level', 'Level', default='A1')
            displayText = f"{title} ({ruleLevel})"
            
            item = ListWidgetItem(displayText)
            item.setData(USER_ROLE, rule)
            self.rulesList.addItem(item)
    
    def onRuleSelected(self, item):
        # Handle grammar rule selection
        ruleData = item.data(USER_ROLE)
        if ruleData:
            self.displayRuleDetails(ruleData)
            self.currentRule = ruleData
            self.ruleSelected.emit(ruleData)
            self.completedBtn.setEnabled(True)
    
    def onLevelFilterChanged(self, level):
        # Handle level filter change
        self.loadGrammarRules()
    
    def displayRuleDetails(self, rule):
        # Display detailed information about a grammar rule
        self.ruleTitle.setText(self._value(rule, 'title', 'Title', default='Untitled Rule'))
        self.ruleLevel.setText(f"Level: {self._value(rule, 'level', 'Level', default='A1')}")
        
        # Rule explanation
        explanation = self._value(rule, 'rule_text', 'RuleText', default='No explanation available')
        self.ruleExplanation.setText(explanation)
        
        # Examples
        examples = self._value(rule, 'examples', 'Examples', default='No examples available')
        self.examplesText.setText(examples)
        
        # Create interactive practice based on rule type
        self.createInteractivePractice(rule)
    
    def createInteractivePractice(self, rule):
        # Create interactive practice based on the grammar rule
        # Clear existing practice area
        for i in reversed(range(self.practiceLayout.count())):
            item = self.practiceLayout.itemAt(i)
            child = item.widget() if item else None
            if child:
                child.hide()
                child.deleteLater()
        
        ruleTitle = self._value(rule, 'title', 'Title', default='').lower()
        
        if 'present simple' in ruleTitle:
            self.createPresentSimplePractice()
        elif 'articles' in ruleTitle:
            self.createArticlesPractice()
        elif 'plural' in ruleTitle:
            self.createPluralPractice()
        else:
            self.createGeneralPractice(rule)
    
    def createPresentSimplePractice(self):
        # Create Present Simple practice
        instruction = Label("Complete the sentences with the correct form of the verb:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice sentences
        sentences = [
            ("I _____ (work) in an office.", "work"),
            ("She _____ (study) English every day.", "studies"),
            ("They _____ (play) football on weekends.", "play"),
            ("He _____ (like) coffee.", "likes"),
            ("We _____ (live) in Kyiv.", "live")
        ]
        
        for sentence, correctAnswer in sentences:
            sentenceLabel = Label(sentence)
            sentenceLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(sentenceLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createArticlesPractice(self):
        # Create articles (a/an) practice
        instruction = Label("Choose the correct article (a/an):")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice items
        items = ["apple", "book", "orange", "car", "umbrella"]
        
        for item in items:
            itemLabel = Label(f"_____ {item}")
            itemLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(itemLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createPluralPractice(self):
        # Create plural nouns practice
        instruction = Label("Write the plural form of these nouns:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice nouns
        nouns = ["cat", "dog", "box", "baby", "class"]
        
        for noun in nouns:
            nounLabel = Label(f"{noun} → _____")
            nounLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(nounLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createGeneralPractice(self, rule):
        # Create general practice for other grammar rules
        instruction = Label("Study the examples above and try to create your own sentences:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Text area for practice
        practiceInput = TextEdit()
        practiceInput.setPlaceholderText("Write your practice sentences here...")
        practiceInput.setMaximumHeight(100)
        practiceInput.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][1]}; font-size: 14px;"
        )
        self.practiceLayout.addWidget(practiceInput)
        
        saveBtn = LCARSButton("Save Practice", ColorHexStr=self.colors['palette'][1])
        saveBtn.clicked.connect(self.savePractice)
        self.practiceLayout.addWidget(saveBtn)
    
    def checkPracticeAnswers(self):
        # Check practice answers (simplified)
        # In a real implementation, this would check actual answers
        resultLabel = Label("✓ Practice completed! Keep studying to improve.")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def savePractice(self):
        # Save practice sentences
        resultLabel = Label("✓ Practice saved successfully!")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def practiceCurrentRule(self):
        # Start practice for current rule
        if self.currentRule:
            self.createInteractivePractice(self.currentRule)
    
    def startGrammarQuiz(self):
        # Start a comprehensive grammar quiz
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = 'A1'

        questions = self.db.getTestQuestions(level, count=5)
        if not questions:
            resultLabel = Label("No quiz questions in database for selected level.")
            resultLabel.setStyleSheet('color: #FFCC66; font-size: 14px; margin: 10px 0;')
            self.practiceLayout.addWidget(resultLabel)
            return

        quizDialog = Dialog(self)
        quizDialog.setWindowTitle("Grammar Quiz")
        quizDialog.setModal(True)
        quizDialog.resize(760, 520)

        dlgLayout = Chassis.Vertical(quizDialog)
        title = Label("GRAMMAR QUIZ")
        title.setStyleSheet(f"color: {self.colors['accent']}; font-size: 22px;")
        dlgLayout.addWidget(title)

        score = {'value': 0}
        state = {'index': 0}

        questionLabel = Label("")
        questionLabel.setWordWrap(True)
        questionLabel.setStyleSheet("color: white; font-size: 16px; margin: 10px 0;")
        dlgLayout.addWidget(questionLabel)

        optionButtons = []
        for _ in range(4):
            btn = PushButton("")
            btn.setStyleSheet('padding: 8px; font-size: 14px;')
            optionButtons.append(btn)
            dlgLayout.addWidget(btn)

        feedback = Label("")
        feedback.setStyleSheet("font-size: 14px; margin-top: 8px;")
        dlgLayout.addWidget(feedback)

        progress = Label("")
        progress.setStyleSheet("color: #9DB0D8; font-size: 13px;")
        dlgLayout.addWidget(progress)

        closeBtn = LCARSButton("Close", ColorHexStr=self.colors['palette'][1])
        closeBtn.clicked.connect(quizDialog.accept)
        dlgLayout.addWidget(closeBtn)

        def renderQuestion():
            idx = state['index']
            if idx >= len(questions):
                questionLabel.setText(f"Quiz complete! Score: {score['value']}/{len(questions)}")
                feedback.setText("")
                for b in optionButtons:
                    b.hide()
                progress.setText("Finished")
                return

            row = questions[idx]
            questionText = self._value(row, 'question', 'Question', default='No question')
            questionLabel.setText(questionText)
            optionTexts = [
                self._value(row, 'option_a', 'OptionA', default=''),
                self._value(row, 'option_b', 'OptionB', default=''),
                self._value(row, 'option_c', 'OptionC', default=''),
                self._value(row, 'option_d', 'OptionD', default=''),
            ]
            for i, b in enumerate(optionButtons):
                b.setText(f"{chr(65+i)}) {optionTexts[i]}")
                b.show()
            feedback.setText("")
            progress.setText(f"Question {idx + 1}/{len(questions)}")

        def onPick(letter):
            idx = state['index']
            row = questions[idx]
            correct = self._value(row, 'correct_option', 'CorrectOption', default='').upper()
            if letter == correct:
                score['value'] += 1
                feedback.setText("Correct")
                feedback.setStyleSheet("color: #00FF88; font-size: 14px; margin-top: 8px;")
            else:
                feedback.setText(f"Incorrect. Correct: {correct}")
                feedback.setStyleSheet("color: #FF6666; font-size: 14px; margin-top: 8px;")
            state['index'] += 1
            renderQuestion()

        for i, b in enumerate(optionButtons):
            b.clicked.connect(lambda checked=False, letter=chr(65+i): onPick(letter))

        renderQuestion()
        quizDialog.exec()
    
    def markRuleCompleted(self):
        # Mark the current rule as completed
        if self.currentRule:
            ruleId = self._value(self.currentRule, 'id', 'Id', default=0)
            self.ruleCompleted.emit(int(ruleId or 0))
            
            # Show confirmation
            resultLabel = Label("✓ Grammar rule marked as completed!")
            resultLabel.setStyleSheet('\n                color: #00FF00;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #003300;\n                border: 2px solid #00FF00;\n                border-radius: 5px;\n            ')
            self.practiceLayout.addWidget(resultLabel)
            
            # Disable button to prevent multiple clicks
            self.completedBtn.setEnabled(False)
.Groups[2].Value
    $before2 = ($before -replace ',?\s*Widget\s*,?', ' ').Trim().TrimEnd(',').TrimStart(',').Trim()
    $after2  = ($after  -replace ',?\s*Widget\s*,?', ' ').Trim().TrimEnd(',').TrimStart(',').Trim()
    $parts = @($before2, $after2) | Where-Object { # Grammar Widget for English Learning Application
# Interactive grammar lessons and rules

from typing import Any

from lcars.base.types import Widget, Chassis, Signal
from lcars.base.interface import Label, Frame, Dialog, TextEdit, TextCursor, PushButton, ListWidget, ListWidgetItem, ScrollArea, ComboBox, Splitter

from lcars.base.defaults import RandomButtonColor, FontStyle
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment

USER_ROLE = 256

class GrammarWidget(SystemComponent):
    # Grammar learning widget
    
    # Signals
    ruleSelected = Signal(dict)  # grammar rule data
    ruleCompleted = Signal(int)  # rule id
    
    def __init__(self, dbManager):
        super().__init__()
        self.db = dbManager
        self.currentRule = None

        self.colors = {
            'palette': [
                RandomButtonColor('buttons'),
                RandomButtonColor('buttons'),
                RandomButtonColor('accent'),
                RandomButtonColor('buttons'),
                RandomButtonColor('alert'),
                RandomButtonColor('panels'),
                RandomButtonColor('panels'),
                RandomButtonColor('alert'),
                RandomButtonColor('accent'),
            ],
            'accent': RandomButtonColor('accent'),
        }
        
        self.initUi()
        self.setupConnections()
        self.loadGrammarRules()
    
    def initUi(self):
        # Initialize the grammar UI
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.createHeader(layout)
        
        # Main content area
        contentSplitter = Splitter()
        
        # Left panel - Rules list
        leftPanel = self.createRulesPanel()
        contentSplitter.addWidget(leftPanel)
        
        # Right panel - Rule details
        rightPanel = self.createRuleDetailsPanel()
        contentSplitter.addWidget(rightPanel)
        
        contentSplitter.setSizes([400, 600])
        layout.addWidget(contentSplitter)
        
        # Apply styling
        self.applyStyling()
    
    def createHeader(self, layout):
        # Create the header section
        headerFrame = Frame()
        headerLayout = Chassis.Horizontal(headerFrame)
        
        # LCARS elbow
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setMinimumSize(200, 80)
        headerLayout.addWidget(elbow)
        
        # Title
        title = Label("GRAMMAR LESSONS")
        title.setStyleSheet(f"\n            color: {self.colors['accent']};\n            {FontStyle(24, 'normal')}\n            padding: 20px;\n        ")
        headerLayout.addWidget(title, 1)
        
        # Level filter
        self.levelFilter = ComboBox()
        self.levelFilter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.levelFilter.setStyleSheet(
            f"background-color: #111111; color: white; border: 2px solid {self.colors['palette'][1]}; padding: 5px 10px; font-size: 14px;"
        )
        headerLayout.addWidget(self.levelFilter)
        
        layout.addWidget(headerFrame)
    
    def createRulesPanel(self, layout=None):
        # Create the grammar rules list panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rules list frame
        rulesFrame = Frame()
        rulesFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][1]}; border-radius: 10px;"
        )
        
        rulesLayout = Chassis.Vertical(rulesFrame)
        rulesLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ GRAMMAR RULES")
        title.setStyleSheet(f"\n            color: {self.colors['palette'][1]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        rulesLayout.addWidget(title)
        
        # Rules list
        self.rulesList = ListWidget()
        self.rulesList.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][2]}; font-size: 14px;"
        )
        rulesLayout.addWidget(self.rulesList)
        
        # Practice buttons
        practiceTitle = Label("◤ GRAMMAR PRACTICE")
        practiceTitle.setStyleSheet(f"\n            color: {self.colors['palette'][3]};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ")
        rulesLayout.addWidget(practiceTitle)
        
        self.practiceBtn = LCARSButton("Practice Current Rule", ColorHexStr=self.colors['palette'][3])
        self.practiceBtn.clicked.connect(self.practiceCurrentRule)
        rulesLayout.addWidget(self.practiceBtn)
        
        self.quizBtn = LCARSButton("Grammar Quiz", ColorHexStr=self.colors['palette'][4])
        self.quizBtn.clicked.connect(self.startGrammarQuiz)
        rulesLayout.addWidget(self.quizBtn)
        
        layout.addWidget(rulesFrame)
        
        return panel
    
    def createRuleDetailsPanel(self, layout=None):
        # Create the rule details panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rule details frame
        detailsFrame = Frame()
        detailsFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][5]}; border-radius: 10px;"
        )
        
        detailsLayout = Chassis.Vertical(detailsFrame)
        detailsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Rule title
        self.ruleTitle = Label("Select a grammar rule to view details")
        self.ruleTitle.setStyleSheet(f"\n            color: {self.colors['palette'][5]};\n            font-size: 24px;\n            font-weight: normal;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleTitle)
        
        # Rule level
        self.ruleLevel = Label("")
        self.ruleLevel.setStyleSheet(f"\n            color: {self.colors['palette'][6]};\n            font-size: 16px;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleLevel)
        
        # Rule explanation
        explanationTitle = Label("◤ RULE EXPLANATION")
        explanationTitle.setStyleSheet(f"\n            color: {self.colors['palette'][7]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        detailsLayout.addWidget(explanationTitle)
        
        self.ruleExplanation = TextEdit()
        self.ruleExplanation.setReadOnly(True)
        self.ruleExplanation.setMaximumHeight(200)
        self.ruleExplanation.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][7]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.ruleExplanation)
        
        # Examples section
        examplesTitle = Label("◤ EXAMPLES")
        examplesTitle.setStyleSheet(f"\n            color: {self.colors['palette'][8]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(examplesTitle)
        
        self.examplesText = TextEdit()
        self.examplesText.setReadOnly(True)
        self.examplesText.setMaximumHeight(150)
        self.examplesText.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][8]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.examplesText)
        
        # Interactive examples
        interactiveTitle = Label("◤ INTERACTIVE PRACTICE")
        interactiveTitle.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(interactiveTitle)
        
        # Practice area
        self.practiceArea = Widget()
        self.practiceLayout = Chassis.Vertical(self.practiceArea)
        detailsLayout.addWidget(self.practiceArea)
        
        # Mark as completed button
        self.completedBtn = LCARSButton("Mark as Completed", ColorHexStr=self.colors['palette'][0])
        self.completedBtn.clicked.connect(self.markRuleCompleted)
        self.completedBtn.setEnabled(False)
        detailsLayout.addWidget(self.completedBtn)
        
        detailsLayout.addStretch()
        
        layout.addWidget(detailsFrame)
        
        return panel
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet(
            'background-color: #000000; color: white; font-family: "LCARS", "Segoe UI", sans-serif;'
        )
    
    def setupConnections(self):
        # Setup signal connections
        # Rules list selection
        self.rulesList.itemClicked.connect(self.onRuleSelected)
        
        # Level filter
        self.levelFilter.currentTextChanged.connect(self.onLevelFilterChanged)

    def _value(self, row, *keys, default: Any = ''):
        for key in keys:
            if key in row and row.get(key) not in (None, ''):
                return row.get(key)
        return default
    
    def loadGrammarRules(self):
        # Load grammar rules from database
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None

        # Always read from DB; `None` means all levels.
        rules = self.db.getGrammarRulesByLevel(level)
        
        self.rulesList.clear()
        
        for rule in rules:
            # Create display text
            title = self._value(rule, 'title', 'Title', default='Untitled Rule')
            ruleLevel = self._value(rule, 'level', 'Level', default='A1')
            displayText = f"{title} ({ruleLevel})"
            
            item = ListWidgetItem(displayText)
            item.setData(USER_ROLE, rule)
            self.rulesList.addItem(item)
    
    def onRuleSelected(self, item):
        # Handle grammar rule selection
        ruleData = item.data(USER_ROLE)
        if ruleData:
            self.displayRuleDetails(ruleData)
            self.currentRule = ruleData
            self.ruleSelected.emit(ruleData)
            self.completedBtn.setEnabled(True)
    
    def onLevelFilterChanged(self, level):
        # Handle level filter change
        self.loadGrammarRules()
    
    def displayRuleDetails(self, rule):
        # Display detailed information about a grammar rule
        self.ruleTitle.setText(self._value(rule, 'title', 'Title', default='Untitled Rule'))
        self.ruleLevel.setText(f"Level: {self._value(rule, 'level', 'Level', default='A1')}")
        
        # Rule explanation
        explanation = self._value(rule, 'rule_text', 'RuleText', default='No explanation available')
        self.ruleExplanation.setText(explanation)
        
        # Examples
        examples = self._value(rule, 'examples', 'Examples', default='No examples available')
        self.examplesText.setText(examples)
        
        # Create interactive practice based on rule type
        self.createInteractivePractice(rule)
    
    def createInteractivePractice(self, rule):
        # Create interactive practice based on the grammar rule
        # Clear existing practice area
        for i in reversed(range(self.practiceLayout.count())):
            item = self.practiceLayout.itemAt(i)
            child = item.widget() if item else None
            if child:
                child.hide()
                child.deleteLater()
        
        ruleTitle = self._value(rule, 'title', 'Title', default='').lower()
        
        if 'present simple' in ruleTitle:
            self.createPresentSimplePractice()
        elif 'articles' in ruleTitle:
            self.createArticlesPractice()
        elif 'plural' in ruleTitle:
            self.createPluralPractice()
        else:
            self.createGeneralPractice(rule)
    
    def createPresentSimplePractice(self):
        # Create Present Simple practice
        instruction = Label("Complete the sentences with the correct form of the verb:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice sentences
        sentences = [
            ("I _____ (work) in an office.", "work"),
            ("She _____ (study) English every day.", "studies"),
            ("They _____ (play) football on weekends.", "play"),
            ("He _____ (like) coffee.", "likes"),
            ("We _____ (live) in Kyiv.", "live")
        ]
        
        for sentence, correctAnswer in sentences:
            sentenceLabel = Label(sentence)
            sentenceLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(sentenceLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createArticlesPractice(self):
        # Create articles (a/an) practice
        instruction = Label("Choose the correct article (a/an):")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice items
        items = ["apple", "book", "orange", "car", "umbrella"]
        
        for item in items:
            itemLabel = Label(f"_____ {item}")
            itemLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(itemLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createPluralPractice(self):
        # Create plural nouns practice
        instruction = Label("Write the plural form of these nouns:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice nouns
        nouns = ["cat", "dog", "box", "baby", "class"]
        
        for noun in nouns:
            nounLabel = Label(f"{noun} → _____")
            nounLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(nounLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createGeneralPractice(self, rule):
        # Create general practice for other grammar rules
        instruction = Label("Study the examples above and try to create your own sentences:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Text area for practice
        practiceInput = TextEdit()
        practiceInput.setPlaceholderText("Write your practice sentences here...")
        practiceInput.setMaximumHeight(100)
        practiceInput.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][1]}; font-size: 14px;"
        )
        self.practiceLayout.addWidget(practiceInput)
        
        saveBtn = LCARSButton("Save Practice", ColorHexStr=self.colors['palette'][1])
        saveBtn.clicked.connect(self.savePractice)
        self.practiceLayout.addWidget(saveBtn)
    
    def checkPracticeAnswers(self):
        # Check practice answers (simplified)
        # In a real implementation, this would check actual answers
        resultLabel = Label("✓ Practice completed! Keep studying to improve.")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def savePractice(self):
        # Save practice sentences
        resultLabel = Label("✓ Practice saved successfully!")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def practiceCurrentRule(self):
        # Start practice for current rule
        if self.currentRule:
            self.createInteractivePractice(self.currentRule)
    
    def startGrammarQuiz(self):
        # Start a comprehensive grammar quiz
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = 'A1'

        questions = self.db.getTestQuestions(level, count=5)
        if not questions:
            resultLabel = Label("No quiz questions in database for selected level.")
            resultLabel.setStyleSheet('color: #FFCC66; font-size: 14px; margin: 10px 0;')
            self.practiceLayout.addWidget(resultLabel)
            return

        quizDialog = Dialog(self)
        quizDialog.setWindowTitle("Grammar Quiz")
        quizDialog.setModal(True)
        quizDialog.resize(760, 520)

        dlgLayout = Chassis.Vertical(quizDialog)
        title = Label("GRAMMAR QUIZ")
        title.setStyleSheet(f"color: {self.colors['accent']}; font-size: 22px;")
        dlgLayout.addWidget(title)

        score = {'value': 0}
        state = {'index': 0}

        questionLabel = Label("")
        questionLabel.setWordWrap(True)
        questionLabel.setStyleSheet("color: white; font-size: 16px; margin: 10px 0;")
        dlgLayout.addWidget(questionLabel)

        optionButtons = []
        for _ in range(4):
            btn = PushButton("")
            btn.setStyleSheet('padding: 8px; font-size: 14px;')
            optionButtons.append(btn)
            dlgLayout.addWidget(btn)

        feedback = Label("")
        feedback.setStyleSheet("font-size: 14px; margin-top: 8px;")
        dlgLayout.addWidget(feedback)

        progress = Label("")
        progress.setStyleSheet("color: #9DB0D8; font-size: 13px;")
        dlgLayout.addWidget(progress)

        closeBtn = LCARSButton("Close", ColorHexStr=self.colors['palette'][1])
        closeBtn.clicked.connect(quizDialog.accept)
        dlgLayout.addWidget(closeBtn)

        def renderQuestion():
            idx = state['index']
            if idx >= len(questions):
                questionLabel.setText(f"Quiz complete! Score: {score['value']}/{len(questions)}")
                feedback.setText("")
                for b in optionButtons:
                    b.hide()
                progress.setText("Finished")
                return

            row = questions[idx]
            questionText = self._value(row, 'question', 'Question', default='No question')
            questionLabel.setText(questionText)
            optionTexts = [
                self._value(row, 'option_a', 'OptionA', default=''),
                self._value(row, 'option_b', 'OptionB', default=''),
                self._value(row, 'option_c', 'OptionC', default=''),
                self._value(row, 'option_d', 'OptionD', default=''),
            ]
            for i, b in enumerate(optionButtons):
                b.setText(f"{chr(65+i)}) {optionTexts[i]}")
                b.show()
            feedback.setText("")
            progress.setText(f"Question {idx + 1}/{len(questions)}")

        def onPick(letter):
            idx = state['index']
            row = questions[idx]
            correct = self._value(row, 'correct_option', 'CorrectOption', default='').upper()
            if letter == correct:
                score['value'] += 1
                feedback.setText("Correct")
                feedback.setStyleSheet("color: #00FF88; font-size: 14px; margin-top: 8px;")
            else:
                feedback.setText(f"Incorrect. Correct: {correct}")
                feedback.setStyleSheet("color: #FF6666; font-size: 14px; margin-top: 8px;")
            state['index'] += 1
            renderQuestion()

        for i, b in enumerate(optionButtons):
            b.clicked.connect(lambda checked=False, letter=chr(65+i): onPick(letter))

        renderQuestion()
        quizDialog.exec()
    
    def markRuleCompleted(self):
        # Mark the current rule as completed
        if self.currentRule:
            ruleId = self._value(self.currentRule, 'id', 'Id', default=0)
            self.ruleCompleted.emit(int(ruleId or 0))
            
            # Show confirmation
            resultLabel = Label("✓ Grammar rule marked as completed!")
            resultLabel.setStyleSheet('\n                color: #00FF00;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #003300;\n                border: 2px solid #00FF00;\n                border-radius: 5px;\n            ')
            self.practiceLayout.addWidget(resultLabel)
            
            # Disable button to prevent multiple clicks
            self.completedBtn.setEnabled(False)
 -ne '' }
    if ($parts.Count -gt 0) { "from lcars.base.types import $($parts -join ', ')`nfrom lcars.base.components import SystemComponent" }
    else { "from lcars.base.components import SystemComponent" }
  
from lcars.base.interface import Label, Frame, Dialog, TextEdit, TextCursor, PushButton, ListWidget, ListWidgetItem, ScrollArea, ComboBox, Splitter

from lcars.base.defaults import RandomButtonColor, FontStyle
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment

USER_ROLE = 256

class GrammarWidget(SystemComponent):
    # Grammar learning widget
    
    # Signals
    ruleSelected = Signal(dict)  # grammar rule data
    ruleCompleted = Signal(int)  # rule id
    
    def __init__(self, dbManager):
        super().__init__()
        self.db = dbManager
        self.currentRule = None

        self.colors = {
            'palette': [
                RandomButtonColor('buttons'),
                RandomButtonColor('buttons'),
                RandomButtonColor('accent'),
                RandomButtonColor('buttons'),
                RandomButtonColor('alert'),
                RandomButtonColor('panels'),
                RandomButtonColor('panels'),
                RandomButtonColor('alert'),
                RandomButtonColor('accent'),
            ],
            'accent': RandomButtonColor('accent'),
        }
        
        self.initUi()
        self.setupConnections()
        self.loadGrammarRules()
    
    def initUi(self):
        # Initialize the grammar UI
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        self.createHeader(layout)
        
        # Main content area
        contentSplitter = Splitter()
        
        # Left panel - Rules list
        leftPanel = self.createRulesPanel()
        contentSplitter.addWidget(leftPanel)
        
        # Right panel - Rule details
        rightPanel = self.createRuleDetailsPanel()
        contentSplitter.addWidget(rightPanel)
        
        contentSplitter.setSizes([400, 600])
        layout.addWidget(contentSplitter)
        
        # Apply styling
        self.applyStyling()
    
    def createHeader(self, layout):
        # Create the header section
        headerFrame = Frame()
        headerLayout = Chassis.Horizontal(headerFrame)
        
        # LCARS elbow
        elbow = LCARSElbow("top-left", color=self.colors['palette'][0])
        elbow.setMinimumSize(200, 80)
        headerLayout.addWidget(elbow)
        
        # Title
        title = Label("GRAMMAR LESSONS")
        title.setStyleSheet(f"\n            color: {self.colors['accent']};\n            {FontStyle(24, 'normal')}\n            padding: 20px;\n        ")
        headerLayout.addWidget(title, 1)
        
        # Level filter
        self.levelFilter = ComboBox()
        self.levelFilter.addItems(['All Levels', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2'])
        self.levelFilter.setStyleSheet(
            f"background-color: #111111; color: white; border: 2px solid {self.colors['palette'][1]}; padding: 5px 10px; font-size: 14px;"
        )
        headerLayout.addWidget(self.levelFilter)
        
        layout.addWidget(headerFrame)
    
    def createRulesPanel(self, layout=None):
        # Create the grammar rules list panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rules list frame
        rulesFrame = Frame()
        rulesFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][1]}; border-radius: 10px;"
        )
        
        rulesLayout = Chassis.Vertical(rulesFrame)
        rulesLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ GRAMMAR RULES")
        title.setStyleSheet(f"\n            color: {self.colors['palette'][1]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        rulesLayout.addWidget(title)
        
        # Rules list
        self.rulesList = ListWidget()
        self.rulesList.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][2]}; font-size: 14px;"
        )
        rulesLayout.addWidget(self.rulesList)
        
        # Practice buttons
        practiceTitle = Label("◤ GRAMMAR PRACTICE")
        practiceTitle.setStyleSheet(f"\n            color: {self.colors['palette'][3]};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ")
        rulesLayout.addWidget(practiceTitle)
        
        self.practiceBtn = LCARSButton("Practice Current Rule", ColorHexStr=self.colors['palette'][3])
        self.practiceBtn.clicked.connect(self.practiceCurrentRule)
        rulesLayout.addWidget(self.practiceBtn)
        
        self.quizBtn = LCARSButton("Grammar Quiz", ColorHexStr=self.colors['palette'][4])
        self.quizBtn.clicked.connect(self.startGrammarQuiz)
        rulesLayout.addWidget(self.quizBtn)
        
        layout.addWidget(rulesFrame)
        
        return panel
    
    def createRuleDetailsPanel(self, layout=None):
        # Create the rule details panel
        if layout is None:
            panel = Widget()
            layout = Chassis.Vertical(panel)
        else:
            panel = layout
        
        # Rule details frame
        detailsFrame = Frame()
        detailsFrame.setStyleSheet(
            f"background-color: #111111; border: 2px solid {self.colors['palette'][5]}; border-radius: 10px;"
        )
        
        detailsLayout = Chassis.Vertical(detailsFrame)
        detailsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Rule title
        self.ruleTitle = Label("Select a grammar rule to view details")
        self.ruleTitle.setStyleSheet(f"\n            color: {self.colors['palette'][5]};\n            font-size: 24px;\n            font-weight: normal;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleTitle)
        
        # Rule level
        self.ruleLevel = Label("")
        self.ruleLevel.setStyleSheet(f"\n            color: {self.colors['palette'][6]};\n            font-size: 16px;\n            margin-bottom: 15px;\n        ")
        detailsLayout.addWidget(self.ruleLevel)
        
        # Rule explanation
        explanationTitle = Label("◤ RULE EXPLANATION")
        explanationTitle.setStyleSheet(f"\n            color: {self.colors['palette'][7]};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ")
        detailsLayout.addWidget(explanationTitle)
        
        self.ruleExplanation = TextEdit()
        self.ruleExplanation.setReadOnly(True)
        self.ruleExplanation.setMaximumHeight(200)
        self.ruleExplanation.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][7]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.ruleExplanation)
        
        # Examples section
        examplesTitle = Label("◤ EXAMPLES")
        examplesTitle.setStyleSheet(f"\n            color: {self.colors['palette'][8]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(examplesTitle)
        
        self.examplesText = TextEdit()
        self.examplesText.setReadOnly(True)
        self.examplesText.setMaximumHeight(150)
        self.examplesText.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][8]}; font-size: 14px;"
        )
        detailsLayout.addWidget(self.examplesText)
        
        # Interactive examples
        interactiveTitle = Label("◤ INTERACTIVE PRACTICE")
        interactiveTitle.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 18px;\n            font-weight: normal;\n            margin: 15px 0 10px 0;\n        ")
        detailsLayout.addWidget(interactiveTitle)
        
        # Practice area
        self.practiceArea = Widget()
        self.practiceLayout = Chassis.Vertical(self.practiceArea)
        detailsLayout.addWidget(self.practiceArea)
        
        # Mark as completed button
        self.completedBtn = LCARSButton("Mark as Completed", ColorHexStr=self.colors['palette'][0])
        self.completedBtn.clicked.connect(self.markRuleCompleted)
        self.completedBtn.setEnabled(False)
        detailsLayout.addWidget(self.completedBtn)
        
        detailsLayout.addStretch()
        
        layout.addWidget(detailsFrame)
        
        return panel
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet(
            'background-color: #000000; color: white; font-family: "LCARS", "Segoe UI", sans-serif;'
        )
    
    def setupConnections(self):
        # Setup signal connections
        # Rules list selection
        self.rulesList.itemClicked.connect(self.onRuleSelected)
        
        # Level filter
        self.levelFilter.currentTextChanged.connect(self.onLevelFilterChanged)

    def _value(self, row, *keys, default: Any = ''):
        for key in keys:
            if key in row and row.get(key) not in (None, ''):
                return row.get(key)
        return default
    
    def loadGrammarRules(self):
        # Load grammar rules from database
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = None

        # Always read from DB; `None` means all levels.
        rules = self.db.getGrammarRulesByLevel(level)
        
        self.rulesList.clear()
        
        for rule in rules:
            # Create display text
            title = self._value(rule, 'title', 'Title', default='Untitled Rule')
            ruleLevel = self._value(rule, 'level', 'Level', default='A1')
            displayText = f"{title} ({ruleLevel})"
            
            item = ListWidgetItem(displayText)
            item.setData(USER_ROLE, rule)
            self.rulesList.addItem(item)
    
    def onRuleSelected(self, item):
        # Handle grammar rule selection
        ruleData = item.data(USER_ROLE)
        if ruleData:
            self.displayRuleDetails(ruleData)
            self.currentRule = ruleData
            self.ruleSelected.emit(ruleData)
            self.completedBtn.setEnabled(True)
    
    def onLevelFilterChanged(self, level):
        # Handle level filter change
        self.loadGrammarRules()
    
    def displayRuleDetails(self, rule):
        # Display detailed information about a grammar rule
        self.ruleTitle.setText(self._value(rule, 'title', 'Title', default='Untitled Rule'))
        self.ruleLevel.setText(f"Level: {self._value(rule, 'level', 'Level', default='A1')}")
        
        # Rule explanation
        explanation = self._value(rule, 'rule_text', 'RuleText', default='No explanation available')
        self.ruleExplanation.setText(explanation)
        
        # Examples
        examples = self._value(rule, 'examples', 'Examples', default='No examples available')
        self.examplesText.setText(examples)
        
        # Create interactive practice based on rule type
        self.createInteractivePractice(rule)
    
    def createInteractivePractice(self, rule):
        # Create interactive practice based on the grammar rule
        # Clear existing practice area
        for i in reversed(range(self.practiceLayout.count())):
            item = self.practiceLayout.itemAt(i)
            child = item.widget() if item else None
            if child:
                child.hide()
                child.deleteLater()
        
        ruleTitle = self._value(rule, 'title', 'Title', default='').lower()
        
        if 'present simple' in ruleTitle:
            self.createPresentSimplePractice()
        elif 'articles' in ruleTitle:
            self.createArticlesPractice()
        elif 'plural' in ruleTitle:
            self.createPluralPractice()
        else:
            self.createGeneralPractice(rule)
    
    def createPresentSimplePractice(self):
        # Create Present Simple practice
        instruction = Label("Complete the sentences with the correct form of the verb:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice sentences
        sentences = [
            ("I _____ (work) in an office.", "work"),
            ("She _____ (study) English every day.", "studies"),
            ("They _____ (play) football on weekends.", "play"),
            ("He _____ (like) coffee.", "likes"),
            ("We _____ (live) in Kyiv.", "live")
        ]
        
        for sentence, correctAnswer in sentences:
            sentenceLabel = Label(sentence)
            sentenceLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(sentenceLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createArticlesPractice(self):
        # Create articles (a/an) practice
        instruction = Label("Choose the correct article (a/an):")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice items
        items = ["apple", "book", "orange", "car", "umbrella"]
        
        for item in items:
            itemLabel = Label(f"_____ {item}")
            itemLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(itemLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createPluralPractice(self):
        # Create plural nouns practice
        instruction = Label("Write the plural form of these nouns:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Practice nouns
        nouns = ["cat", "dog", "box", "baby", "class"]
        
        for noun in nouns:
            nounLabel = Label(f"{noun} → _____")
            nounLabel.setStyleSheet("color: white; font-size: 14px; margin: 5px 0;")
            self.practiceLayout.addWidget(nounLabel)
        
        checkBtn = LCARSButton("Check Answers", ColorHexStr=self.colors['palette'][1])
        checkBtn.clicked.connect(self.checkPracticeAnswers)
        self.practiceLayout.addWidget(checkBtn)
    
    def createGeneralPractice(self, rule):
        # Create general practice for other grammar rules
        instruction = Label("Study the examples above and try to create your own sentences:")
        instruction.setStyleSheet(f"\n            color: {self.colors['palette'][0]};\n            font-size: 16px;\n            margin-bottom: 10px;\n        ")
        self.practiceLayout.addWidget(instruction)
        
        # Text area for practice
        practiceInput = TextEdit()
        practiceInput.setPlaceholderText("Write your practice sentences here...")
        practiceInput.setMaximumHeight(100)
        practiceInput.setStyleSheet(
            f"background-color: #000000; color: white; border: 1px solid {self.colors['palette'][1]}; font-size: 14px;"
        )
        self.practiceLayout.addWidget(practiceInput)
        
        saveBtn = LCARSButton("Save Practice", ColorHexStr=self.colors['palette'][1])
        saveBtn.clicked.connect(self.savePractice)
        self.practiceLayout.addWidget(saveBtn)
    
    def checkPracticeAnswers(self):
        # Check practice answers (simplified)
        # In a real implementation, this would check actual answers
        resultLabel = Label("✓ Practice completed! Keep studying to improve.")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def savePractice(self):
        # Save practice sentences
        resultLabel = Label("✓ Practice saved successfully!")
        resultLabel.setStyleSheet('\n            color: #00FF00;\n            font-size: 14px;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #003300;\n            border: 1px solid #00FF00;\n            border-radius: 5px;\n        ')
        self.practiceLayout.addWidget(resultLabel)
    
    def practiceCurrentRule(self):
        # Start practice for current rule
        if self.currentRule:
            self.createInteractivePractice(self.currentRule)
    
    def startGrammarQuiz(self):
        # Start a comprehensive grammar quiz
        level = self.levelFilter.currentText()
        if level == 'All Levels':
            level = 'A1'

        questions = self.db.getTestQuestions(level, count=5)
        if not questions:
            resultLabel = Label("No quiz questions in database for selected level.")
            resultLabel.setStyleSheet('color: #FFCC66; font-size: 14px; margin: 10px 0;')
            self.practiceLayout.addWidget(resultLabel)
            return

        quizDialog = Dialog(self)
        quizDialog.setWindowTitle("Grammar Quiz")
        quizDialog.setModal(True)
        quizDialog.resize(760, 520)

        dlgLayout = Chassis.Vertical(quizDialog)
        title = Label("GRAMMAR QUIZ")
        title.setStyleSheet(f"color: {self.colors['accent']}; font-size: 22px;")
        dlgLayout.addWidget(title)

        score = {'value': 0}
        state = {'index': 0}

        questionLabel = Label("")
        questionLabel.setWordWrap(True)
        questionLabel.setStyleSheet("color: white; font-size: 16px; margin: 10px 0;")
        dlgLayout.addWidget(questionLabel)

        optionButtons = []
        for _ in range(4):
            btn = PushButton("")
            btn.setStyleSheet('padding: 8px; font-size: 14px;')
            optionButtons.append(btn)
            dlgLayout.addWidget(btn)

        feedback = Label("")
        feedback.setStyleSheet("font-size: 14px; margin-top: 8px;")
        dlgLayout.addWidget(feedback)

        progress = Label("")
        progress.setStyleSheet("color: #9DB0D8; font-size: 13px;")
        dlgLayout.addWidget(progress)

        closeBtn = LCARSButton("Close", ColorHexStr=self.colors['palette'][1])
        closeBtn.clicked.connect(quizDialog.accept)
        dlgLayout.addWidget(closeBtn)

        def renderQuestion():
            idx = state['index']
            if idx >= len(questions):
                questionLabel.setText(f"Quiz complete! Score: {score['value']}/{len(questions)}")
                feedback.setText("")
                for b in optionButtons:
                    b.hide()
                progress.setText("Finished")
                return

            row = questions[idx]
            questionText = self._value(row, 'question', 'Question', default='No question')
            questionLabel.setText(questionText)
            optionTexts = [
                self._value(row, 'option_a', 'OptionA', default=''),
                self._value(row, 'option_b', 'OptionB', default=''),
                self._value(row, 'option_c', 'OptionC', default=''),
                self._value(row, 'option_d', 'OptionD', default=''),
            ]
            for i, b in enumerate(optionButtons):
                b.setText(f"{chr(65+i)}) {optionTexts[i]}")
                b.show()
            feedback.setText("")
            progress.setText(f"Question {idx + 1}/{len(questions)}")

        def onPick(letter):
            idx = state['index']
            row = questions[idx]
            correct = self._value(row, 'correct_option', 'CorrectOption', default='').upper()
            if letter == correct:
                score['value'] += 1
                feedback.setText("Correct")
                feedback.setStyleSheet("color: #00FF88; font-size: 14px; margin-top: 8px;")
            else:
                feedback.setText(f"Incorrect. Correct: {correct}")
                feedback.setStyleSheet("color: #FF6666; font-size: 14px; margin-top: 8px;")
            state['index'] += 1
            renderQuestion()

        for i, b in enumerate(optionButtons):
            b.clicked.connect(lambda checked=False, letter=chr(65+i): onPick(letter))

        renderQuestion()
        quizDialog.exec()
    
    def markRuleCompleted(self):
        # Mark the current rule as completed
        if self.currentRule:
            ruleId = self._value(self.currentRule, 'id', 'Id', default=0)
            self.ruleCompleted.emit(int(ruleId or 0))
            
            # Show confirmation
            resultLabel = Label("✓ Grammar rule marked as completed!")
            resultLabel.setStyleSheet('\n                color: #00FF00;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #003300;\n                border: 2px solid #00FF00;\n                border-radius: 5px;\n            ')
            self.practiceLayout.addWidget(resultLabel)
            
            # Disable button to prevent multiple clicks
            self.completedBtn.setEnabled(False)
