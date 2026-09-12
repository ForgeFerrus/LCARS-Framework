# Exercises Widget for English Learning Application
# Interactive exercises for vocabulary, grammar, and phrases
# LCARS abstractions for UI components (no direct PyQt6 usage)
from lcars.base.default import RandomButtonColor, FontStyle
from lcars.base.type import Chassis, Matrix, SystemComponent
from lcars.core.signal import Signal
from lcars.base.component import LCARSButton
from lcars.base.interface import LCARSButton, Label, Frame, ButtonGroup, RadioButton, ProgressBar, LineEdit, MessageBox

class ExercisesWidget(SystemComponent):
    # Interactive exercises widget

    # Signals
    ExerciseCompleted = Signal(dict)
    SessionEnded = Signal()

    def __init__(self, DbManager, LearningManager):
        super().__init__()
        self.DbManager = DbManager
        self.LearningManager = LearningManager
        # Use RandomButtonColor for button colors and FontStyle for text
        self.PrimaryColor = RandomButtonColor("buttons")
        self.SecondaryColor = RandomButtonColor("panels")
        self.HighlightColor = RandomButtonColor("accent")
        self.SupportColor = RandomButtonColor("panels")
        self.AlertColor = RandomButtonColor("alert")
        self.BackgroundColor = "#000000"

        self.CurrentExercise = None
        self.ExerciseHistory = []
        self.SessionStats = {'total': 0, 'correct': 0, 'incorrect': 0}

        self.BuildUI()
        self.SetupConnections()
        self.StartNewSession()

    def BuildUI(self):
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.CreateHeader(layout)

        ContentLayout = Chassis.Horizontal()
        LeftPanel = self.CreateControlPanel()
        ContentLayout.addWidget(LeftPanel)
        RightPanel = self.CreateExercisePanel()
        ContentLayout.addWidget(RightPanel)
        layout.addLayout(ContentLayout)

        self.ApplyStyling()

    def CreateHeader(self, layout):
        HeaderFrame = Frame()
        HeaderLayout = Chassis.Horizontal(HeaderFrame)

        elbow = LCARSElbow("top-left", color=self.PrimaryColor)
        elbow.setMinimumSize(200, 80)
        HeaderLayout.addWidget(elbow)

        title = Label("INTERACTIVE EXERCISES")
        title.setStyleSheet(f"\n            color: {self.PrimaryColor};\n            {FontStyle(24, 'bold')};\n            padding: 20px;\n            text-align: center;\n        ")
        HeaderLayout.addWidget(title, 1)

        self.ProgressLabel = Label("Progress: 0/0")
        self.ProgressLabel.setStyleSheet(f'\n            color: {self.HighlightColor};\n            font-size: 16px;\n            font-weight: normal;\n            padding: 20px;\n            background-color: #111111;\n            border: 2px solid {self.HighlightColor};\n        ')
        HeaderLayout.addWidget(self.ProgressLabel)

        layout.addWidget(HeaderFrame)

    def CreateControlPanel(self, layout=None):
        if layout is None:
            Panel = Matrix()
            Layout = Chassis.Vertical(Panel)
        else:
            Panel = layout
            Layout = layout

        TypeFrame = Frame()
        TypeFrame.setStyleSheet(f'\n            QFrame {{\n                background-color: #111111;\n                border: 2px solid {self.SecondaryColor};\n                border-radius: 10px;\n            }}\n        ')

        TypeLayout = Chassis.Vertical(TypeFrame)
        TypeLayout.setContentsMargins(15, 15, 15, 15)

        title = Label("◤ EXERCISE TYPE")
        title.setStyleSheet(f'\n            color: {self.SecondaryColor};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 10px;\n        ')
        TypeLayout.addWidget(title)

        self.ExerciseTypeGroup = ButtonGroup()
        ExerciseTypes = [
            ("Translation", "translation", self.PrimaryColor),
            ("Multiple Choice", "multiple_choice", self.SecondaryColor),
            ("Spelling", "spelling", self.HighlightColor),
            ("Phrases", "phrase_translation", self.SupportColor),
            ("Grammar", "grammar", self.PrimaryColor)
        ]

        for TypeName, TypeValue, Color in ExerciseTypes:
            btn = LCARSButton(TypeName, ColorHexStr=Color)
            btn.setCheckable(True)
            self.ExerciseTypeGroup.addButton(btn)
            btn.ExerciseType = TypeValue
            TypeLayout.addWidget(btn)

        self.ExerciseTypeGroup.buttons()[0].setChecked(True)

        LevelTitle = Label("◤ DIFFICULTY LEVEL")
        LevelTitle.setStyleSheet(f'\n            color: {self.SupportColor};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ')
        TypeLayout.addWidget(LevelTitle)

        self.LevelButtons = ButtonGroup()
        Levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        LevelColors = [self.SecondaryColor, self.HighlightColor, self.PrimaryColor, self.SupportColor, self.SecondaryColor, self.HighlightColor]

        for Level, Color in zip(Levels, LevelColors):
            btn = LCARSButton(Level, ColorHexStr=Color)
            btn.setCheckable(True)
            btn.setMaximumHeight(35)
            self.LevelButtons.addButton(btn)
            btn.Level = Level
            TypeLayout.addWidget(btn)

        self.LevelButtons.buttons()[0].setChecked(True)

        ControlsTitle = Label("◤ SESSION CONTROLS")
        ControlsTitle.setStyleSheet(f'\n            color: {self.AlertColor};\n            font-size: 16px;\n            font-weight: normal;\n            margin: 15px 0 5px 0;\n        ')
        TypeLayout.addWidget(ControlsTitle)

        self.StartSessionBtn = LCARSButton("Start Session", ColorHexStr=self.PrimaryColor)
        self.StartSessionBtn.clicked.Connect(self.StartNewSession)
        TypeLayout.addWidget(self.StartSessionBtn)

        self.NextExerciseBtn = LCARSButton("Next Exercise", ColorHexStr=self.SecondaryColor)
        self.NextExerciseBtn.clicked.Connect(self.NextExercise)
        TypeLayout.addWidget(self.NextExerciseBtn)

        self.ShowHintBtn = LCARSButton("Show Hint", ColorHexStr=self.HighlightColor)
        self.ShowHintBtn.clicked.Connect(self.ShowHint)
        TypeLayout.addWidget(self.ShowHintBtn)

        self.EndSessionBtn = LCARSButton("End Session", ColorHexStr="#FF0000")
        self.EndSessionBtn.clicked.Connect(self.EndSession)
        TypeLayout.addWidget(self.EndSessionBtn)

        TypeLayout.addStretch()
        Layout.addWidget(TypeFrame)

        return Panel

    def CreateExercisePanel(self, layout=None):
        if layout is None:
            Panel = Matrix()
            Layout = Chassis.Vertical(Panel)
        else:
            Panel = layout
            Layout = layout

        ExerciseFrame = Frame()
        ExerciseFrame.setStyleSheet(f'\n            QFrame {{\n                background-color: #111111;\n                border: 2px solid {self.SupportColor};\n                border-radius: 10px;\n            }}\n        ')

        ExerciseLayout = Chassis.Vertical(ExerciseFrame)
        ExerciseLayout.setContentsMargins(20, 20, 20, 20)

        self.ExerciseInfoLabel = Label("Exercise 1 of 10 - Translation")
        self.ExerciseInfoLabel.setStyleSheet(f'\n            color: {self.SupportColor};\n            font-size: 18px;\n            font-weight: normal;\n            margin-bottom: 15px;\n        ')
        ExerciseLayout.addWidget(self.ExerciseInfoLabel)

        self.QuestionLabel = Label("Click 'Start Session' to begin")
        self.QuestionLabel.setStyleSheet(f"\n            color: white;\n            {FontStyle(20, 'normal')};\n            margin: 20px 0;\n            padding: 20px;\n            background-color: #000000;\n            border: 2px solid {self.PrimaryColor};\n            border-radius: 10px;\n            text-align: center;\n        ")
        self.QuestionLabel.setWordWrap(True)
        ExerciseLayout.addWidget(self.QuestionLabel)

        self.AnswerWidget = Matrix()
        self.AnswerLayout = Chassis.Vertical(self.AnswerWidget)
        ExerciseLayout.addWidget(self.AnswerWidget)

        self.HintLabel = Label("")
        self.HintLabel.setStyleSheet(f'\n            color: {self.SecondaryColor};\n            font-size: 14px;\n            font-style: italic;\n            margin: 10px 0;\n            padding: 10px;\n            background-color: #222222;\n            border: 1px solid {self.SecondaryColor};\n            border-radius: 5px;\n        ')
        self.HintLabel.setWordWrap(True)
        self.HintLabel.hide()
        ExerciseLayout.addWidget(self.HintLabel)

        self.SubmitBtn = LCARSButton("Submit Answer", ColorHexStr=self.PrimaryColor)
        self.SubmitBtn.clicked.Connect(self.SubmitAnswer)
        self.SubmitBtn.setEnabled(False)
        ExerciseLayout.addWidget(self.SubmitBtn)

        self.ResultLabel = Label("")
        self.ResultLabel.setStyleSheet('\n            color: white;\n            font-size: 16px;\n            margin: 10px 0;\n            padding: 10px;\n            border-radius: 5px;\n        ')
        self.ResultLabel.setWordWrap(True)
        self.ResultLabel.hide()
        ExerciseLayout.addWidget(self.ResultLabel)

        self.ProgressBarWidget = ProgressBar()
        self.ProgressBarWidget.setStyleSheet(f'\n            QProgressBar {{\n                border: 2px solid {self.HighlightColor};\n                border-radius: 5px;\n                text-align: center;\n                color: white;\n                font-weight: normal;\n            }}\n            QProgressBar::chunk {{\n                background-color: {self.HighlightColor};\n                border-radius: 3px;\n            }}\n        ')
        self.ProgressBarWidget.setRange(0, 10)
        ExerciseLayout.addWidget(self.ProgressBarWidget)

        StatsFrame = Frame()
        StatsFrame.setStyleSheet(f'\n            QFrame {{\n                background-color: #111111;\n                border: 2px solid {self.SupportColor};\n                border-radius: 10px;\n            }}\n        ')

        StatsLayout = Chassis.Horizontal(StatsFrame)
        StatsLayout.setContentsMargins(15, 10, 15, 10)

        self.CorrectLabel = Label("Correct: 0")
        self.CorrectLabel.setStyleSheet("color: #00FF00; font-size: 16px; font-weight: normal;")
        StatsLayout.addWidget(self.CorrectLabel)

        self.IncorrectLabel = Label("Incorrect: 0")
        self.IncorrectLabel.setStyleSheet("color: #FF0000; font-size: 16px; font-weight: normal;")
        StatsLayout.addWidget(self.IncorrectLabel)

        self.AccuracyLabel = Label("Accuracy: 0%")
        self.AccuracyLabel.setStyleSheet(f"color: {self.SupportColor}; font-size: 16px; font-weight: normal;")
        StatsLayout.addWidget(self.AccuracyLabel)

        ExerciseLayout.addWidget(StatsFrame)
        Layout.addWidget(ExerciseFrame)

        return Panel

    def ApplyStyling(self):
        self.setStyleSheet("\n            QWidget {\n                background-color: #000000;\n                color: white;\n                font-family: 'Arial', sans-serif;\n            }\n            QLabel {\n                color: white;\n            }\n            QLineEdit {\n                background-color: #000000;\n                color: white;\n                border: 2px solid #4BBEBF;\n                padding: 10px;\n                font-size: 16px;\n                border-radius: 5px;\n            }\n            QTextEdit {\n                background-color: #000000;\n                color: white;\n                border: 2px solid #4BBEBF;\n                padding: 10px;\n                font-size: 16px;\n                border-radius: 5px;\n            }\n        ")

    def SetupConnections(self):
        pass

    def StartNewSession(self):
        self.SessionStats = {'total': 0, 'correct': 0, 'incorrect': 0}
        self.ExerciseHistory = []
        self.ProgressBarWidget.setValue(0)
        self.UpdateStatistics()
        self.NextExercise()
        self.SubmitBtn.setEnabled(True)
        self.StartSessionBtn.setText("Restart Session")

    def NextExercise(self):
        SelectedTypeButton = self.ExerciseTypeGroup.checkedButton()
        ExerciseType = getattr(SelectedTypeButton, 'ExerciseType', 'translation') if SelectedTypeButton else "translation"

        SelectedLevelButton = self.LevelButtons.checkedButton()
        Level = getattr(SelectedLevelButton, 'Level', 'A1') if SelectedLevelButton else "A1"

        self.CurrentExercise = self.GetNextExercise(Level, [ExerciseType])

        if self.CurrentExercise:
            self.DisplayExercise()
            self.HideResult()
        else:
            self.ShowSessionComplete()

    def DisplayExercise(self):
        if not self.CurrentExercise:
            return

        ExerciseNum = self.SessionStats['total'] + 1
        ExerciseType = self.CurrentExercise['type'].replace('_', ' ').title()
        self.ExerciseInfoLabel.setText(f"Exercise {ExerciseNum} - {ExerciseType}")
        self.QuestionLabel.setText(self.CurrentExercise['question'])
        self.CreateAnswerInput()
        self.HintLabel.hide()
        self.ResultLabel.hide()
        self.ProgressLabel.setText(f"Progress: {ExerciseNum}/10")
        self.ProgressBarWidget.setValue(ExerciseNum)

    def CreateAnswerInput(self):
        if not self.CurrentExercise:
            return

        for i in reversed(range(self.AnswerLayout.count())):
            child = self.AnswerLayout.itemAt(i).widget()
            if child:
                child.hide()
                child.deleteLater()

        ExerciseType = self.CurrentExercise['type']

        if ExerciseType == 'multiple_choice':
            Options = self.CurrentExercise.get('options', [])
            for Index, Option in enumerate(Options):
                radio = RadioButton(Option)
                radio.setStyleSheet(f'\n                    QRadioButton {{\n                        color: white;\n                        font-size: 16px;\n                        padding: 5px;\n                    }}\n                    QRadioButton::indicator {{\n                        width: 20px;\n                        height: 20px;\n                    }}\n                    QRadioButton::indicator::unchecked {{\n                        border: 2px solid {self.PrimaryColor};\n                        background-color: #000000;\n                        border-radius: 10px;\n                    }}\n                    QRadioButton::indicator::checked {{\n                        border: 2px solid {self.PrimaryColor};\n                        background-color: {self.PrimaryColor};\n                        border-radius: 10px;\n                    }}\n                ')
                self.AnswerLayout.addWidget(radio)
        else:
            self.AnswerInput = LineEdit()
            self.AnswerInput.setPlaceholderText("Type your answer here...")
            self.AnswerInput.returnPressed.connect(self.SubmitAnswer)
            self.AnswerLayout.addWidget(self.AnswerInput)

    def SubmitAnswer(self):
        if not self.CurrentExercise:
            return

        userAnswer = self.GetUserAnswer()
        if not userAnswer:
            return

        Result = self.CheckLearningAnswer(userAnswer)

        self.SessionStats['total'] += 1
        if Result['correct']:
            self.SessionStats['correct'] += 1
        else:
            self.SessionStats['incorrect'] += 1

        self.DisplayResult(Result)
        self.UpdateStatistics()
        self.SubmitBtn.setEnabled(False)
        self.ExerciseCompleted.emit(Result)
        Timer.singleShot(2000, self.AutoNextExercise)

    def GetUserAnswer(self):
        if not self.CurrentExercise:
            return ""

        ExerciseType = self.CurrentExercise['type']
        if ExerciseType == 'multiple_choice':
            for i in range(self.AnswerLayout.count()):
                widget = self.AnswerLayout.itemAt(i).widget()
                if isinstance(widget, RadioButton) and widget.isChecked():
                    return widget.text()
            return ""

        if hasattr(self, 'AnswerInput'):
            return self.AnswerInput.text().strip()
        return ""

    def DisplayResult(self, Result):
        self.ResultLabel.show()
        if Result['correct']:
            self.ResultLabel.setText("✓ CORRECT! Well done!")
            self.ResultLabel.setStyleSheet('\n                color: #00FF00;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #003300;\n                border: 2px solid #00FF00;\n                border-radius: 5px;\n            ')
        else:
            self.ResultLabel.setText(f"✗ Incorrect. {Result['message']}")
            self.ResultLabel.setStyleSheet('\n                color: #FF0000;\n                font-size: 16px;\n                font-weight: normal;\n                margin: 10px 0;\n                padding: 10px;\n                background-color: #330000;\n                border: 2px solid #FF0000;\n                border-radius: 5px;\n            ')
            if Result.get('explanation'):
                explanation = Label(f"Explanation: {Result['explanation']}")
                explanation.setStyleSheet('\n                    color: #CCCCCC;\n                    font-size: 14px;\n                    margin: 5px 0;\n                    padding: 10px;\n                    background-color: #222222;\n                    border-radius: 5px;\n                ')
                explanation.setWordWrap(True)
                self.AnswerLayout.addWidget(explanation)

    def HideResult(self):
        self.ResultLabel.hide()
        self.SubmitBtn.setEnabled(True)

    def ShowHint(self):
        if not self.CurrentExercise:
            return

        hints = self.CurrentExercise.get('hints', [])
        if hints:
            HintText = "💡 " + hints[0]
        else:
            HintText = "💡 " + self.CurrentExercise.get('hint', 'No hint available')
        self.HintLabel.setText(HintText)
        self.HintLabel.show()

    def AutoNextExercise(self):
        if self.SessionStats['total'] < 10:
            self.NextExercise()
        else:
            self.ShowSessionComplete()

    def ShowSessionComplete(self):
        self.QuestionLabel.setText("Session Complete!")
        Accuracy = (self.SessionStats['correct'] / self.SessionStats['total'] * 100) if self.SessionStats['total'] > 0 else 0
        summary = f"\n        Session Summary:\n        • Total Exercises: {self.SessionStats['total']}\n        • Correct: {self.SessionStats['correct']}\n        • Incorrect: {self.SessionStats['incorrect']}\n        • Accuracy: {Accuracy:.1f}%\n        "
        self.ResultLabel.setText(summary)
        self.ResultLabel.setStyleSheet(f'\n            color: {self.HighlightColor};\n            font-size: 16px;\n            margin: 10px 0;\n            padding: 20px;\n            background-color: #111111;\n            border: 2px solid {self.HighlightColor};\n            border-radius: 10px;\n        ')
        self.ResultLabel.show()
        self.SubmitBtn.setEnabled(False)
        self.NextExerciseBtn.setEnabled(False)

    def UpdateStatistics(self):
        self.CorrectLabel.setText(f"Correct: {self.SessionStats['correct']}")
        self.IncorrectLabel.setText(f"Incorrect: {self.SessionStats['incorrect']}")
        Accuracy = (self.SessionStats['correct'] / self.SessionStats['total'] * 100) if self.SessionStats['total'] > 0 else 0
        self.AccuracyLabel.setText(f"Accuracy: {Accuracy:.1f}%")

    def EndSession(self):
        reply = MessageBox.question(
            self, 'End Session',
            'Are you sure you want to end the current session?',
            MessageBox.StandardButton.Yes | MessageBox.StandardButton.No
        )
        if reply == MessageBox.StandardButton.Yes:
            self.SessionEnded.emit()
            self.QuestionLabel.setText("Click 'Start Session' to begin")
            self.HideResult()
            self.ProgressBarWidget.setValue(0)
            self.ProgressLabel.setText("Progress: 0/0")
            self.SessionStats = {'total': 0, 'correct': 0, 'incorrect': 0}
            self.UpdateStatistics()

    def GetNextExercise(self, level, exerciseTypes):
        exerciseType = exerciseTypes[0] if exerciseTypes else 'translation'

        if exerciseType in ('translation', 'multiple_choice', 'spelling'):
            return self.LearningManager.generateVocabularyExercise(level=level, exerciseType=exerciseType)
        if exerciseType == 'phrase_translation':
            return self.LearningManager.generatePhraseExercise(level=level)
        if exerciseType == 'grammar':
            return self.LearningManager.generateGrammarExercise(level=level)
        return self.LearningManager.generateVocabularyExercise(level=level, exerciseType='translation')

    def CheckLearningAnswer(self, userAnswer):
        if hasattr(self.LearningManager, 'checkAnswer'):
            return self.LearningManager.checkAnswer(userAnswer)

        correctAnswer = str(self.CurrentExercise.get('correct_answer', '')).strip().lower() if self.CurrentExercise else ''
        isCorrect = str(userAnswer).strip().lower() == correctAnswer
        return {
            'correct': isCorrect,
            'message': 'Correct!' if isCorrect else f"Incorrect. Correct: {self.CurrentExercise.get('correct_answer', '') if self.CurrentExercise else ''}",
            'exercise_type': self.CurrentExercise.get('type') if self.CurrentExercise else 'unknown'
        }


