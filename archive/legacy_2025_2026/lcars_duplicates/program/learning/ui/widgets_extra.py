from lcars.base.components import SystemComponent
# Additional UI modules for English Learning System:
#  - GrammarWidget  — rules + mini-quiz for each grammar topic
#  - WritingWidget  — translation practice (user types EN→UA or UA→EN)
#
# Imported from the learning UI package via:
#     from lcars.program.learning.ui.widgets_extra import GrammarWidget, WritingWidget
import random
from lcars.base.types import Widget, Chassis, Label, Frame, ScrollArea, SizePolicy, ComboBox, LineEdit, Timer, Visual

from lcars.base.interface import LCARSButton
from lcars.base.defaults import FontStyle
from lcars.program.learning.grammar_data import GRAMMARRules, getGrammarRules


class LCARSStationWidget(SystemComponent):
    # Lightweight duplicate of the base class (avoids circular import).
    def __init__(self, theme, faction, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.faction = faction

    def createLcarsHeader(self, title, layout, cColor=0):
        colors = self.theme.get('palette', ['#FF9900'] * 8)
        color = colors[cColor % len(colors)]
        hdr = Frame()
        hdr.setFixedHeight(88)
        hdr.setStyleSheet(f"background-color: {color}; border-radius: 44px;")
        hLay = Chassis.Horizontal(hdr)
        hLay.setContentsMargins(50, 0, 50, 0)
        lbl = Label(title)
        lbl.setStyleSheet(f"color: #000000; {FontStyle(32, 'normal')}; letter-spacing: 1px;")
        hLay.addWidget(lbl)
        layout.addWidget(hdr)


# ─────────────────────────────────────────────────────────────────────────────
#  GRAMMAR MODULE
# ─────────────────────────────────────────────────────────────────────────────

class GrammarWidget(LCARSStationWidget):
    # Browse grammar rules by level/topic and answer mini fill-in-blank quiz.

    def __init__(self, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.progress = progress
        self.currentRule = None
        self.quizIdx = 0
        self.quizScore = 0

        layout = Chassis.Vertical(self)
        self.createLcarsHeader("GRAMMAR MATRIX", layout, 3)

        # ── Level / Rule selector ──────────────────────
        selLay = Chassis.Horizontal()
        selLay.setContentsMargins(40, 10, 40, 0)
        selLay.setSpacing(20)

        self.lvlBox = ComboBox()
        self.lvlBox.addItems(["ALL", "A1", "A2", "B1", "B2"])
        self.StyleCombo(self.lvlBox)
        self.lvlBox.currentTextChanged.connect(self.RefreshRuleList)
        selLay.addWidget(self.lvlBox)

        self.ruleBox = ComboBox()
        self.StyleCombo(self.ruleBox)
        self.ruleBox.setMinimumWidth(500)
        self.ruleBox.currentIndexChanged.connect(self.LoadRule)
        selLay.addWidget(self.ruleBox, 1)
        layout.addLayout(selLay)
        layout.addSpacing(10)

        # ── Rule panel (scrollable) ─────────────────────
        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setSizePolicy(SizePolicy.Policy.Expanding, SizePolicy.Policy.Expanding)

        self.rulePanel = Widget()
        self.rulePanel.setStyleSheet("background: transparent;")
        self.ruleLayout = Chassis.Vertical(self.rulePanel)
        self.ruleLayout.setContentsMargins(40, 10, 40, 10)
        self.ruleLayout.setSpacing(20)
        scroll.setWidget(self.rulePanel)
        layout.addWidget(scroll, 1)

        # ── Quiz area ──────────────────────────────────
        quizFrame = Frame()
        quizFrame.setStyleSheet("background: #1A1A1A; border-radius: 30px;")
        quizLay = Chassis.Vertical(quizFrame)
        quizLay.setContentsMargins(40, 20, 40, 20)

        self.quizQLbl = Label("SELECT A GRAMMAR RULE TO BEGIN MINI-QUIZ")
        self.quizQLbl.setWordWrap(True)
        self.quizQLbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(24, 'normal')}")
        quizLay.addWidget(self.quizQLbl)

        self.quizOptsLay = Chassis.Horizontal()
        self.quizOptsLay.setSpacing(20)
        self.quizOptBtns = []
        for i in range(4):
            btn = LCARSButton("", Color=self.theme['palette'][i % len(self.theme['palette'])])
            btn.setFixedHeight(56)
            btn.setStyleSheet(btn.styleSheet() + f"{FontStyle(20, 'normal')}")
            btn.Clicked.connect(lambda checked, idx=i: self.CheckAnswer(idx))
            self.quizOptsLay.addWidget(btn)
            self.quizOptBtns.append(btn)
        quizLay.addLayout(self.quizOptsLay)

        self.quizFeedback = Label("")
        self.quizFeedback.setAlignment(Visual.Align.Center)
        self.quizFeedback.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        quizLay.addWidget(self.quizFeedback)

        layout.addWidget(quizFrame)
        self.RefreshRuleList("ALL")

    def StyleCombo(self, box):
        box.setFixedHeight(56)
        box.setStyleSheet(
            f"QComboBox {{ padding: 10px 20px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 28px; {FontStyle(18, 'normal')} }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background: #222; color: #FFFFFF; }}"
        )

    def RefreshRuleList(self, level):
        self.ruleBox.blockSignals(True)
        self.ruleBox.clear()
        rules = getGrammarRules(None if level == "ALL" else level)
        for r in rules:
            self.ruleBox.addItem(f"[{r['level']}] {r['title']}", r)
        self.ruleBox.blockSignals(False)
        if self.ruleBox.count():
            self.LoadRule(0)

    def LoadRule(self, idx):
        if idx < 0 or self.ruleBox.count() == 0:
            return
        rule = self.ruleBox.itemData(idx)
        if not rule:
            return
        self.currentRule = rule
        # Clear rule panel
        while self.ruleLayout.count():
            item = self.ruleLayout.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()

        # Rule text
        ruleLbl = Label(rule['rule'])
        ruleLbl.setWordWrap(True)
        ruleLbl.setStyleSheet(f"color: #CCCCCC; {FontStyle(22, 'normal')}; padding: 16px; "
                               f"background: #111; border-radius: 20px;")
        self.ruleLayout.addWidget(ruleLbl)

        # Examples
        exTitle = Label("✦ EXAMPLES")
        exTitle.setStyleSheet(f"color: {self.theme['palette'][1]}; {FontStyle(22, 'normal')}")
        self.ruleLayout.addWidget(exTitle)

        for en, ua in rule['examples']:
            row = Frame()
            row.setStyleSheet("background: #1a1a1a; border-radius: 15px; padding: 5px;")
            rowLay = Chassis.Vertical(row)
            rowLay.setContentsMargins(20, 10, 20, 10)
            enLbl = Label(f"▸ {en}")
            enLbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(20, 'normal')}")
            uaLbl = Label(f"  {ua}")
            uaLbl.setStyleSheet(f"color: #999; {FontStyle(18, 'normal')}")
            rowLay.addWidget(enLbl)
            rowLay.addWidget(uaLbl)
            self.ruleLayout.addWidget(row)

        self.ruleLayout.addStretch()

        # Reset quiz
        self.quizIdx = 0
        self.quizScore = 0
        self.LoadQuizQuestion()

    def LoadQuizQuestion(self):
        if not self.currentRule:
            return
        questions = self.currentRule['quiz']
        if self.quizIdx >= len(questions):
            self.quizQLbl.setText(f"✓ QUIZ COMPLETE! Score: {self.quizScore}/{len(questions)}")
            self.quizFeedback.setText("")
            for btn in self.quizOptBtns:
                btn.hide()
            return

        q = questions[self.quizIdx]
        self.quizQLbl.setText(f"[{self.quizIdx + 1}/{len(questions)}]  {q['q']}")
        self.quizFeedback.setText("")

        opts = q['opts'][:]
        random.shuffle(opts)
        self.CurrentAnswer = q['a']
        self.CurrentOpts = opts

        for i, btn in enumerate(self.quizOptBtns):
            if i < len(opts):
                btn.setText(opts[i])
                btn.show()
            else:
                btn.hide()

    def CheckAnswer(self, idx):
        if idx >= len(self.CurrentOpts):
            return
        chosen = self.CurrentOpts[idx]
        if chosen == self.CurrentAnswer:
            self.quizFeedback.setText("✓ CORRECT!")
            self.quizFeedback.setStyleSheet(f"color: #00FF88; {FontStyle(20, 'normal')}")
            self.quizScore += 1
        else:
            self.quizFeedback.setText(f"✗ INCORRECT — Answer: {self.CurrentAnswer}")
            self.quizFeedback.setStyleSheet(f"color: #FF4444; {FontStyle(20, 'normal')}")
        self.quizIdx += 1
        Timer.singleShot(1500, self.LoadQuizQuestion)


# ─────────────────────────────────────────────────────────────────────────────
#  WRITING / TRANSLATION PRACTICE MODULE
# ─────────────────────────────────────────────────────────────────────────────

class WritingWidget(LCARSStationWidget):
    # Translation typing exercise — shows a word/sentence, user types the translation.

    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.currentWord = None
        self.direction = "en→ua"   # or "ua→en"
        self.score = 0
        self.total = 0

        layout = Chassis.Vertical(self)
        self.createLcarsHeader("WRITING PRACTICE", layout, 2)

        # ── Controls bar ───────────────────────────────
        ctrlLay = Chassis.Horizontal()
        ctrlLay.setContentsMargins(40, 10, 40, 0)
        ctrlLay.setSpacing(20)

        self.dirBox = ComboBox()
        self.dirBox.addItems(["EN → УКРАЇНСЬКА", "УКРАЇНСЬКА → EN"])
        self.dirBox.setFixedHeight(56)
        self.dirBox.setStyleSheet(
            f"QComboBox {{ padding: 10px 20px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 28px; {FontStyle(18, 'normal')} }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background: #222; color: #FFFFFF; }}"
        )
        self.dirBox.currentIndexChanged.connect(self.ToggleDirection)
        ctrlLay.addWidget(self.dirBox)

        self.scoreLbl = Label("SCORE: 0 / 0")
        self.scoreLbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {FontStyle(22, 'normal')}")
        ctrlLay.addStretch()
        ctrlLay.addWidget(self.scoreLbl)
        layout.addLayout(ctrlLay)
        layout.addSpacing(20)

        # ── Word display card ──────────────────────────
        self.card = Frame()
        self.card.setFixedHeight(210)
        self.card.setStyleSheet("background: #1A1A1A; border-radius: 24px;")
        cardLay = Chassis.Vertical(self.card)

        self.promptLbl = Label("PRESS START")
        self.promptLbl.setAlignment(Visual.Align.Center)
        self.promptLbl.setWordWrap(True)
        self.promptLbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(44, 'normal')}")
        cardLay.addWidget(self.promptLbl)

        self.hintLbl = Label("")
        self.hintLbl.setAlignment(Visual.Align.Center)
        self.hintLbl.setStyleSheet(f"color: #666; {FontStyle(18, 'normal')}")
        cardLay.addWidget(self.hintLbl)
        layout.addWidget(self.card)
        layout.addSpacing(20)

        # ── Input ──────────────────────────────────────
        inputLay = Chassis.Horizontal()
        inputLay.setContentsMargins(40, 0, 40, 0)
        inputLay.setSpacing(20)

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

        # ── Feedback ───────────────────────────────────
        self.feedbackLbl = Label("")
        self.feedbackLbl.setAlignment(Visual.Align.Center)
        self.feedbackLbl.setWordWrap(True)
        self.feedbackLbl.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        layout.addWidget(self.feedbackLbl)
        layout.addSpacing(10)

        # ── Buttons ────────────────────────────────────
        btnLay = Chassis.Horizontal()
        btnLay.setContentsMargins(40, 0, 40, 0)
        btnLay.setSpacing(20)

        self.startBtn = LCARSButton("START", Color=self.theme['accent'])
        self.startBtn.setFixedSize(210, 64)
        self.startBtn.setStyleSheet(self.startBtn.styleSheet() + f"{FontStyle(20, 'normal')}")
        self.startBtn.Clicked.connect(self.NextWord)
        btnLay.addWidget(self.startBtn)

        self.skipBtn = LCARSButton("SKIP →", Color=self.theme['palette'][4])
        self.skipBtn.setFixedSize(160, 64)
        self.skipBtn.setStyleSheet(self.skipBtn.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.skipBtn.Clicked.connect(self.Skip)
        btnLay.addWidget(self.skipBtn)

        btnLay.addStretch()
        layout.addLayout(btnLay)
        layout.addStretch()

    def ToggleDirection(self, idx):
        self.direction = "en→ua" if idx == 0 else "ua→en"
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

        if self.direction == "en→ua":
            self.promptLbl.setText(en.upper())
            self.hintLbl.setText(f"[{pos}]  →  Type Ukrainian translation")
        else:
            self.promptLbl.setText(ua)
            self.hintLbl.setText(f"[{pos}]  →  Type English word")

        self.answerIn.clear()
        self.answerIn.setFocus()
        self.feedbackLbl.setText("")
        self.startBtn.setText("NEXT →")

    def CheckAnswer(self):
        if not self.currentWord:
            self.NextWord()
            return
        userAns = self.answerIn.text().strip().lower()
        if not userAns:
            return

        en = self.currentWord.get('english', '').lower()
        ua = self.currentWord.get('ukrainian', '').lower()

        if self.direction == "en→ua":
            correct = ua
        else:
            correct = en

        # Lenient matching: accept if user answer is contained in correct or vice versa
        self.total += 1
        if userAns in correct or correct.startswith(userAns) or userAns == correct.split("/")[0].strip():
            self.score += 1
            self.feedbackLbl.setText(f"✓ CORRECT! → {correct}")
            self.feedbackLbl.setStyleSheet(f"color: #00FF88; {FontStyle(20, 'normal')}")
        else:
            self.feedbackLbl.setText(f"✗ INCORRECT — Correct answer: {correct}")
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

# ─────────────────────────────────────────────────────────────────────────────
#  SETTINGS MODULE
# ─────────────────────────────────────────────────────────────────────────────

class SettingsWidget(LCARSStationWidget):
    # Configuration and maintenance panel for the English Learning System.

    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress

        layout = Chassis.Vertical(self)
        self.createLcarsHeader("SYSTEM SETTINGS", layout, 1)

        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        container = Widget()
        container.setStyleSheet("background: transparent;")
        cLay = Chassis.Vertical(container)
        cLay.setContentsMargins(40, 20, 40, 20)
        cLay.setSpacing(30)

        # -- Database Stats --
        statFrame = Frame()
        statFrame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        statLay = Chassis.Vertical(statFrame)
        
        lblStatTitle = Label("DATABASE STATISTICS")
        lblStatTitle.setStyleSheet(f"color: {self.theme['palette'][2]}; {FontStyle(24, 'normal')}")
        statLay.addWidget(lblStatTitle)

        stats = self.db.getStatistics()
        lblTotal = Label(f"Total Words: {stats.get('total_words', 0)}")
        lblTotal.setStyleSheet(f"color: #FFFFFF; {FontStyle(20, 'normal')}")
        statLay.addWidget(lblTotal)

        # Show break down
        levelsText = " • ".join([f"{lvl}: {stats.get('by_level',{}).get(lvl,0)}" for lvl in ["A1","A2","B1","B2","C1","C2"]])
        lblLvls = Label(f"Levels: {levelsText}")
        lblLvls.setStyleSheet(f"color: #AAAAAA; {FontStyle(18, 'normal')}")
        statLay.addWidget(lblLvls)
        
        cLay.addWidget(statFrame)

        # -- Progress Management --
        prgFrame = Frame()
        prgFrame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        prgLay = Chassis.Vertical(prgFrame)
        
        lblPrgTitle = Label("USER PROGRESS")
        lblPrgTitle.setStyleSheet(f"color: {self.theme['palette'][3]}; {FontStyle(24, 'normal')}")
        prgLay.addWidget(lblPrgTitle)

        self.btnResetPrg = LCARSButton(
            "RESET ALL PROGRESS",
            Color=self.theme.get('alert', self.theme['palette'][0]),
        )
        self.btnResetPrg.setFixedHeight(56)
        self.btnResetPrg.setStyleSheet(self.btnResetPrg.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.btnResetPrg.Clicked.connect(self.ResetProgress)
        prgLay.addWidget(self.btnResetPrg)

        self.lblResetStatus = Label("")
        self.lblResetStatus.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        prgLay.addWidget(self.lblResetStatus)
        
        cLay.addWidget(prgFrame)

        # -- Audio Settings placeholder --
        audFrame = Frame()
        audFrame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        audLay = Chassis.Vertical(audFrame)
        
        lblAudTitle = Label("AUDIO & TTS")
        lblAudTitle.setStyleSheet(f"color: {self.theme['palette'][4]}; {FontStyle(24, 'normal')}")
        audLay.addWidget(lblAudTitle)

        lblAudInfo = Label("Text-to-Speech (TTS) uses default OS En-US voice.\nEnsure Windows TTS packs are installed for best quality.")
        lblAudInfo.setStyleSheet(f"color: #CCCCCC; {FontStyle(18, 'normal')}")
        audLay.addWidget(lblAudInfo)
        
        cLay.addWidget(audFrame)

        cLay.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def ResetProgress(self):
        self.db.connection.execute("DELETE FROM user_progress")
        self.db.connection.execute("DELETE FROM learning_sessions")
        self.db.connection.execute("UPDATE vocabulary SET mastery_level = 0.0, next_review = NULL, times_reviewed = 0")
        self.db.connection.commit()

        # Reset tracker cache
        self.progress.currentLevel = "A1"
        if hasattr(self.progress, 'session_start'):
            self.progress.sessionStart = None

        self.lblResetStatus.setText("SUCCESS: PROGRESS WIPED")
        # Force UI update
        self.progress.progressUpdated.emit()
        Timer.singleShot(3000, lambda: self.lblResetStatus.setText(""))
