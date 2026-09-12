import random

from lcars.base.type import Chassis, Label, Frame, Timer, ComboBox, LineEdit
from lcars.base.interface import LCARSButton
from lcars.base.default import FontStyle

from lcars.program.learning.ui.interface import LearningStation


class WritingWidget(LearningStation):
    # Translation typing exercise.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.currentWord = None
        self.direction = "en->ua"
        self.score = 0
        self.total = 0

        layout = Chassis.Vertical(self)
        # Створюємо заголовок панелі з кольором з палітри (індекс 2)
        self.createHeader("WRITING PRACTICE", layout, 2)

        ctrlLay = Chassis.Horizontal()
        ctrlLay.setContentsMargins(40, 10, 40, 0)
        ctrlLay.setSpacing(20)

        # LCARS ComboBox для вибору напрямку перекладу
        self.dirBox = ComboBox()
        self.dirBox.setObjectName("dirBox")
        self.dirBox.addItems(["EN -> UKRAINIAN", "UKRAINIAN -> EN"])
        self.dirBox.setFixedHeight(56)
        self.dirBox.setStyleSheet(
            f"#dirBox {{ padding: 10px 20px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 28px; {FontStyle(18, 'normal')} }}"
        )
        self.dirBox.currentIndexChanged.connect(self.ToggleDirection)
        ctrlLay.addWidget(self.dirBox)

        self.scoreLbl = Label("SCORE: 0 / 0")
        self.scoreLbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {FontStyle(22, 'normal')}")
        ctrlLay.addStretch()
        ctrlLay.addWidget(self.scoreLbl)
        layout.addLayout(ctrlLay)
        layout.addSpacing(20)

        self.card = Frame()
        self.card.setFixedHeight(210)
        self.card.setStyleSheet("background: #1A1A1A; border-radius: 24px;")
        cardLay = Chassis.Vertical(self.card)

        self.promptLbl = Label("PRESS START")
        self.promptLbl.setWordWrap(True)
        self.promptLbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(44, 'normal')};")
        cardLay.addWidget(self.promptLbl)

        self.hintLbl = Label("")
        self.hintLbl.setStyleSheet(f"color: #666; {FontStyle(18, 'normal')};")
        cardLay.addWidget(self.hintLbl)
        layout.addWidget(self.card)
        layout.addSpacing(20)

        inputLay = Chassis.Horizontal()
        inputLay.setContentsMargins(40, 0, 40, 0)
        inputLay.setSpacing(20)

        # LCARS LineEdit для введення відповіді з обробкою Enter
        self.answerIn = LineEdit()
        self.answerIn.setPlaceholderText("TYPE YOUR TRANSLATION HERE...")
        self.answerIn.setFixedHeight(60)
        self.answerIn.setStyleSheet(
            f"padding: 10px 30px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 30px; {FontStyle(20, 'normal')}"
        )
        self.answerIn.returnPressed.connect(self.CheckAnswer)
        inputLay.addWidget(self.answerIn, 1)

        self.submitBtn = LCARSButton("CHECK", Color=self.theme['palette'][2])
        self.submitBtn.setFixedSize(160, 60)
        self.submitBtn.setStyleSheet(self.submitBtn.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.submitBtn.Clicked.connect(self.CheckAnswer)
        inputLay.addWidget(self.submitBtn)
        layout.addLayout(inputLay)
        layout.addSpacing(10)

        self.feedbackLbl = Label("")
        self.feedbackLbl.setWordWrap(True)
        self.feedbackLbl.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')};")
        layout.addWidget(self.feedbackLbl)
        layout.addSpacing(10)

        btnLay = Chassis.Horizontal()
        btnLay.setContentsMargins(40, 0, 40, 0)
        btnLay.setSpacing(20)

        self.startBtn = LCARSButton("START", Color=self.theme['accent'])
        self.startBtn.setFixedSize(210, 64)
        self.startBtn.setStyleSheet(self.startBtn.styleSheet() + f"{FontStyle(20, 'normal')}")
        self.startBtn.Clicked.connect(self.NextWord)
        btnLay.addWidget(self.startBtn)

        self.skipBtn = LCARSButton("SKIP ->", Color=self.theme['palette'][4])
        self.skipBtn.setFixedSize(160, 64)
        self.skipBtn.setStyleSheet(self.skipBtn.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.skipBtn.Clicked.connect(self.Skip)
        btnLay.addWidget(self.skipBtn)

        btnLay.addStretch()
        layout.addLayout(btnLay)
        layout.addStretch()

    def ToggleDirection(self, idx):
        self.direction = "en->ua" if idx == 0 else "ua->en"
        self.feedbackLbl.setText("")
        self.NextWord()

    def NextWord(self):
        lvl = self.progress.getCurrentLevel()
        words = self.db.getRandomWords(level=lvl, count=1)
        if not words:
            words = self.db.getRandomWords(count=1)
        if not words:
            self.promptLbl.setText("NO WORDS IN DATABASE")
            return
        self.currentWord = words[0]
        en = self.currentWord.get('english', '')
        ua = self.currentWord.get('ukrainian', '')
        pos = self.currentWord.get('part_of_speech', '')

        if self.direction == "en->ua":
            self.promptLbl.setText(en.upper())
            self.hintLbl.setText(f"[{pos}]  ->  Type Ukrainian translation")
        else:
            self.promptLbl.setText(ua)
            self.hintLbl.setText(f"[{pos}]  ->  Type English word")

        self.answerIn.clear()
        self.answerIn.setFocus()
        self.feedbackLbl.setText("")
        self.startBtn.setText("NEXT ->")

    def CheckAnswer(self):
        if not self.currentWord:
            self.NextWord()
            return
        userAns = self.answerIn.text().strip().lower()
        if not userAns:
            return

        en = self.currentWord.get('english', '').lower()
        ua = self.currentWord.get('ukrainian', '').lower()
        correct = ua if self.direction == "en->ua" else en

        self.total += 1
        if userAns in correct or correct.startswith(userAns) or userAns == correct.split('/')[0].strip():
            self.score += 1
            self.feedbackLbl.setText(f"OK: {correct}")
            self.feedbackLbl.setStyleSheet(f"color: #00FF88; {FontStyle(20, 'normal')}")
        else:
            self.feedbackLbl.setText(f"Incorrect. Correct: {correct}")
            self.feedbackLbl.setStyleSheet(f"color: #FF4444; {FontStyle(20, 'normal')}")

        self.scoreLbl.setText(f"SCORE: {self.score} / {self.total}")
        Timer.singleShot(1800, self.NextWord)

    def Skip(self):
        self.total += 1
        self.scoreLbl.setText(f"SCORE: {self.score} / {self.total}")
        self.NextWord()

    def reset(self):
        self.score = 0
        self.total = 0
        self.scoreLbl.setText("SCORE: 0 / 0")
        self.currentWord = None
        self.promptLbl.setText("PRESS START")
        self.feedbackLbl.setText("")
