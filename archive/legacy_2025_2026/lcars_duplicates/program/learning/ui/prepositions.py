from __future__ import annotations
# ─────────────────────────────────────────────────────────────
# PREPOSITIONS QUIZ MODULE — LCARS English Learning System
# Тест на прийменники: вибір варіанту, заповнення пропуску, прогрес
# ─────────────────────────────────────────────────────────────
import random
from lcars.base.type import (
    Widget, Chassis, Label, Frame, Signal, ScrollArea, Directive, Timer
)
# LCARS abstractions for UI components (no direct PyQt6 usage)
from lcars.base.interface import LCARSButton
from lcars.base.default import TitanPalette, RandomButtonColor, FontStyle
from lcars.program.learning.ui.interface import LearningStation

# ─────────────────────────────────────────────────────────────
# БАЗА ЗАПИТАНЬ
# Формат: (sentence_with_blank, correct, [wrong1, wrong2, wrong3], uk_hint)
# ─────────────────────────────────────────────────────────────
PREPOSITIONS_DATA = [
    # AT / IN / ON — time
    ("She wakes up ___ 7 o'clock.", "at", ["in", "on", "by"], "о 7 годині"),
    ("I was born ___ 1995.", "in", ["at", "on", "during"], "у 1995 році"),
    ("The meeting is ___ Monday.", "on", ["at", "in", "by"], "у понеділок"),
    ("We go skiing ___ winter.", "in", ["at", "on", "during"], "взимку"),
    ("The train arrives ___ noon.", "at", ["in", "on", "for"], "опівдні"),
    ("He called me ___ the evening.", "in", ["at", "on", "during"], "увечері"),
    ("She graduates ___ June.", "in", ["at", "on", "by"], "у червні"),
    ("The shop closes ___ midnight.", "at", ["in", "on", "by"], "опівночі"),
    ("We met ___ Christmas Day.", "on", ["at", "in", "by"], "на Різдво"),
    ("I'll finish ___ the weekend.", "at", ["in", "on", "by"], "на вихідних"),

    # AT / IN / ON — place
    ("He lives ___ London.", "in", ["at", "on", "to"], "у Лондоні"),
    ("She is ___ school right now.", "at", ["in", "on", "near"], "у школі"),
    ("The keys are ___ the table.", "on", ["in", "at", "under"], "на столі"),
    ("There is milk ___ the fridge.", "in", ["on", "at", "near"], "у холодильнику"),
    ("We arrived ___ the airport.", "at", ["in", "on", "to"], "в аеропорту"),
    ("The picture is ___ the wall.", "on", ["in", "at", "by"], "на стіні"),
    ("He stood ___ the corner.", "at", ["on", "in", "by"], "на розі"),
    ("The cat is ___ the box.", "in", ["on", "at", "under"], "у коробці"),
    ("They live ___ the countryside.", "in", ["at", "on", "near"], "за містом"),
    ("She works ___ a hospital.", "in", ["at", "on", "for"], "у лікарні"),

    # FOR / SINCE / DURING
    ("I have been waiting ___ two hours.", "for", ["since", "during", "in"], "протягом двох годин"),
    ("She has lived here ___ 2010.", "since", ["for", "during", "from"], "з 2010 року"),
    ("He slept ___ the lecture.", "during", ["for", "since", "while"], "під час лекції"),
    ("We stayed there ___ a week.", "for", ["since", "during", "in"], "тиждень"),
    ("I haven't eaten ___ yesterday.", "since", ["for", "during", "from"], "з учора"),
    ("They argued ___ the whole trip.", "during", ["for", "since", "at"], "протягом усієї поїздки"),
    ("She studied ___ three years.", "for", ["since", "during", "in"], "три роки"),

    # BY / WITH / FROM / TO
    ("This book was written ___ Tolkien.", "by", ["from", "with", "of"], "автором є Толкін"),
    ("She cut the bread ___ a knife.", "with", ["by", "from", "using"], "ножем"),
    ("He traveled ___ London to Paris.", "from", ["by", "with", "to"], "з Лондона до Парижа"),
    ("The letter was sent ___ email.", "by", ["with", "from", "via"], "електронною поштою"),
    ("I got this present ___ my sister.", "from", ["by", "with", "of"], "від сестри"),
    ("She came ___ work late.", "from", ["to", "at", "by"], "з роботи"),
    ("He walked ___ the station.", "to", ["at", "towards", "by"], "до станції"),
    ("The package was delivered ___ courier.", "by", ["with", "from", "via"], "кур'єром"),

    # ABOUT / OF / FOR / AGAINST
    ("She talked ___ her new project.", "about", ["of", "for", "on"], "про новий проект"),
    ("I am proud ___ my daughter.", "of", ["about", "for", "from"], "пишаюся донькою"),
    ("Are you looking ___ something?", "for", ["of", "about", "at"], "шукаєш щось?"),
    ("He is afraid ___ spiders.", "of", ["from", "about", "with"], "боїться павуків"),
    ("They voted ___ the proposal.", "against", ["for", "about", "on"], "проголосували проти"),
    ("What do you think ___ this idea?", "about", ["of", "for", "on"], "що думаєш про цю ідею?"),
    ("He thanked me ___ my help.", "for", ["about", "of", "with"], "подякував за допомогу"),

    # THROUGH / ACROSS / ALONG / PAST
    ("They walked ___ the park.", "through", ["across", "along", "past"], "через парк"),
    ("She swam ___ the river.", "across", ["through", "along", "over"], "через річку (вплав)"),
    ("We strolled ___ the beach.", "along", ["through", "across", "beside"], "вздовж пляжу"),
    ("He drove ___ the old house.", "past", ["by", "through", "across"], "повз старий будинок"),

    # PHRASAL / IDIOMATIC
    ("I am interested ___ astronomy.", "in", ["about", "for", "of"], "цікавлюся астрономією"),
    ("She is good ___ languages.", "at", ["in", "with", "for"], "добре знає мови"),
    ("He depends ___ his parents.", "on", ["at", "in", "from"], "залежить від батьків"),
    ("They are responsible ___ safety.", "for", ["of", "about", "on"], "відповідальні за безпеку"),
    ("I agree ___ you.", "with", ["to", "on", "about"], "погоджуюся з тобою"),
    ("She insists ___ doing it herself.", "on", ["in", "at", "for"], "наполягає зробити самій"),
    ("He is married ___ a doctor.", "to", ["with", "by", "for"], "одружений з лікарем"),
    ("We are looking forward ___ summer.", "to", ["for", "at", "of"], "чекаємо літа"),
    ("She complained ___ the noise.", "about", ["of", "for", "on"], "скаржилася на шум"),
    ("He succeeded ___ his goal.", "in", ["at", "with", "on"], "досяг своєї мети"),
]


def BuildPalette(theme):
    fallback = [
        TitanPalette.Buttons[0],
        TitanPalette.Buttons[1],
        TitanPalette.Accent[0],
        TitanPalette.YellowAlert[0],
        TitanPalette.RedAlert[0],
    ]
    p = theme.get("palette") if isinstance(theme, dict) else None
    if not isinstance(p, list) or len(p) < 4:
        return fallback
    if len(p) >= 5:
        return list(p[:5])
    return list(p[:4]) + [TitanPalette.RedAlert[0]]


class PrepositionsWidget(LearningStation):

    def __init__(self, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.Palette = BuildPalette(theme)
        self.setStyleSheet("background: black;")

        self.Queue: list = []
        self.Answered = 0
        self.Correct  = 0
        self.Current  = None
        self.BtnMap: list[tuple] = []
        self.Locked   = False

        self.BuildUI()
        self.NextQuestion()

    # ─── UI CONSTRUCTION ──────────────────────────────────────

    def BuildUI(self):
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = Frame()
        header.setMinimumHeight(80)
        header.setStyleSheet("background: #050a10;")
        hrow = Chassis.Horizontal(header)
        hrow.setContentsMargins(0, 0, 20, 0)
        hrow.setSpacing(0)

        elbow = LCARSElbow("top-left", self.Palette[0])
        elbow.setMinimumSize(260, 80)
        hrow.addWidget(elbow)

        title_lbl = Label("PREPOSITIONS // SYNTAX DRILL")
        title_lbl.setStyleSheet(
            f"color: {self.Palette[0]}; {FontStyle(26, 'normal')}; letter-spacing: 3px; padding-left: 20px;"
        )
        hrow.addWidget(title_lbl, 1)

        self.ScoreLbl = Label("0 / 0")
        self.ScoreLbl.setStyleSheet(
            f"color: {self.Palette[1]}; {FontStyle(22, 'normal')}; padding: 0 14px;"
        )
        self.ScoreLbl.setAlignment(Directive.Align.AlignRight)
        hrow.addWidget(self.ScoreLbl)

        layout.addWidget(header)

        self.ProgBar = Frame()
        self.ProgBar.setFixedHeight(6)
        self.ProgBar.setStyleSheet(f"background: {self.Palette[1]};")
        layout.addWidget(self.ProgBar)

        body = Chassis.Vertical()
        body.setContentsMargins(40, 18, 40, 10)
        body.setSpacing(12)

        self.SentenceLbl = Label("")
        self.SentenceLbl.setStyleSheet(
            f"color: #FFF; {FontStyle(26, 'normal')}; background: #0a0f18; "
            f"border-left: 8px solid {self.Palette[0]}; padding: 20px 26px; "
            "border-radius: 4px;"
        )
        self.SentenceLbl.setWordWrap(True)
        self.SentenceLbl.setMinimumHeight(80)
        body.addWidget(self.SentenceLbl)

        self.HintLbl = Label("")
        self.HintLbl.setStyleSheet(
            f"color: {self.Palette[2]}; {FontStyle(14, 'normal')}; padding-left: 4px; letter-spacing: 1px;"
        )
        body.addWidget(self.HintLbl)

        self.ChoiceFrame = Frame()
        self.ChoiceFrame.setStyleSheet("background: transparent;")
        self.ChoiceLayout = Chassis.Horizontal(self.ChoiceFrame)
        self.ChoiceLayout.setSpacing(10)
        self.ChoiceLayout.setContentsMargins(0, 0, 0, 0)
        body.addWidget(self.ChoiceFrame)

        self.FeedbackLbl = Label("")
        self.FeedbackLbl.setStyleSheet(
            f"color: #FFF; {FontStyle(18, 'normal')}; padding: 8px 12px; border-radius: 4px;"
        )
        self.FeedbackLbl.setWordWrap(True)
        body.addWidget(self.FeedbackLbl)

        ctrl_row = Chassis.Horizontal()
        ctrl_row.setSpacing(12)
        self.BtnNext = LCARSButton("NEXT ▶", Color=self.Palette[0])
        self.BtnNext.setFixedHeight(40)
        self.BtnNext.Clicked.connect(self.NextQuestion)
        ctrl_row.addWidget(self.BtnNext)

        btn_restart = LCARSButton("RESTART", Color=self.Palette[2])
        btn_restart.setFixedHeight(40)
        btn_restart.Clicked.connect(self.Restart)
        ctrl_row.addWidget(btn_restart)
        ctrl_row.addStretch(1)
        body.addLayout(ctrl_row)

        hist_title = Label("◤ SESSION LOG")
        hist_title.setStyleSheet(f"color: #444; {FontStyle(12, 'normal')}; letter-spacing: 2px;")
        body.addWidget(hist_title)

        self.HistScroll = ScrollArea()
        self.HistScroll.setWidgetResizable(True)
        self.HistScroll.setFixedHeight(150)
        self.HistScroll.setFrameShape(Frame.Shape.NoFrame)
        self.HistScroll.setStyleSheet(
            "background: #05080e; border: 1px solid #151a26; border-radius: 4px;"
        )
        self.HistInner = Widget()
        self.HistLay = Chassis.Vertical(self.HistInner)
        self.HistLay.setContentsMargins(10, 6, 10, 6)
        self.HistLay.setSpacing(3)
        self.HistLay.addStretch(1)
        self.HistScroll.setWidget(self.HistInner)
        body.addWidget(self.HistScroll)

        layout.addLayout(body, 1)

        bot = LCARSSegment(Color=self.Palette[0])
        bot.setFixedHeight(8)
        layout.addWidget(bot)

    # ─── QUIZ LOGIC ───────────────────────────────────────────

    def Restart(self):
        self.Answered = 0
        self.Correct  = 0
        self.Queue    = []
        self.UpdateScore()
        self.ClearHistory()
        self.NextQuestion()

    def NextQuestion(self):
        if not self.Queue:
            self.Queue = random.sample(PREPOSITIONS_DATA, len(PREPOSITIONS_DATA))

        self.Current = self.Queue.pop()
        self.Locked  = False

        sentence, correct, wrongs, hint = self.Current
        self.SentenceLbl.setText(sentence.replace("___", "  ___  "))
        self.HintLbl.setText(f"◤ ПІДКАЗКА: {hint}")
        self.FeedbackLbl.setText("")
        self.FeedbackLbl.setStyleSheet(
            f"color: #FFF; {FontStyle(20, 'normal')}; padding: 10px; border-radius: 4px;"
        )

        self.ClearChoices()
        options = [correct] + wrongs[:3]
        random.shuffle(options)

        colors = [self.Palette[0], self.Palette[1], self.Palette[2], self.Palette[3]]
        self.BtnMap = []
        for i, opt in enumerate(options):
            c = colors[i % len(colors)]
            btn = LCARSButton(opt.upper(), Color=c)
            btn.setFixedHeight(38)
            btn.setMinimumWidth(110)
            btn.Clicked.connect(lambda ch=False, o=opt: self.Answer(o))
            self.ChoiceLayout.addWidget(btn)
            self.BtnMap.append((btn, opt == correct, c))
        self.ChoiceLayout.addStretch(1)

        self.BtnNext.setEnabled(False)

    def Answer(self, chosen: str):
        if self.Locked:
            return
        self.Locked = True
        self.Answered += 1

        sentence, correct, _, _ = self.Current
        is_ok = (chosen == correct)
        if is_ok:
            self.Correct += 1
            GetSoundManager().PlayAudioClip("success")
            self.FeedbackLbl.setText(f"✓  CORRECT  —  \"{correct}\"")
            self.FeedbackLbl.setStyleSheet(
                f"color: #000; background: {self.Palette[2]}; {FontStyle(20, 'normal')}; "
                f"padding: 10px; border-radius: 4px;"
            )
        else:
            GetSoundManager().PlayAudioClip("error")
            self.FeedbackLbl.setText(f"✗  WRONG  —  correct: \"{correct}\"")
            self.FeedbackLbl.setStyleSheet(
                f"color: #FFF; background: {self.Palette[4]}; {FontStyle(20, 'normal')}; "
                f"padding: 10px; border-radius: 4px;"
            )

        for btn, btn_correct, orig_c in self.BtnMap:
            if btn_correct:
                btn.setStyleSheet(
                    f"background-color: {TitanPalette.Accent[0]} !important; color: #000 !important; "
                    f"border: none; border-radius: 6px; "
                    f"{FontStyle(13, 'normal')} padding: 0 10px;"
                )
            else:
                btn.setStyleSheet(
                    f"background-color: #1a1a1a !important; color: #444 !important; "
                    f"border: none; border-radius: 6px; "
                    f"{FontStyle(13, 'normal')} padding: 0 10px;"
                )

        self.UpdateScore()
        self.LogResult(sentence, chosen, correct, is_ok)
        self.BtnNext.setEnabled(True)

    def ClearChoices(self):
        while self.ChoiceLayout.count():
            item = self.ChoiceLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def UpdateScore(self):
        pct = int(self.Correct / self.Answered * 100) if self.Answered else 0
        self.ScoreLbl.setText(f"{self.Correct} / {self.Answered}  ({pct}%)")
        if self.Answered == 0:
            c = self.Palette[1]
        elif pct >= 75:
            c = TitanPalette.Accent[0]
        elif pct >= 50:
            c = TitanPalette.YellowAlert[0]
        else:
            c = TitanPalette.RedAlert[0]
        self.ProgBar.setStyleSheet(f"background: {c};")

    def LogResult(self, sentence, chosen, correct, is_ok):
        icon = "✓" if is_ok else "✗"
        clr  = TitanPalette.Accent[0] if is_ok else TitanPalette.RedAlert[0]
        short = sentence.replace("___", f"[{correct}]")
        if len(short) > 55:
            short = short[:52] + "…"
        entry = Label(f"{icon}  {short}")
        entry.setStyleSheet(
            f"color: {clr}; {FontStyle(12, 'normal')}; background: transparent;"
        )
        self.HistLay.insertWidget(self.HistLay.count() - 1, entry)
        sb = self.HistScroll.verticalScrollBar()
        if sb:
            sb.setValue(sb.maximum())

    def ClearHistory(self):
        while self.HistLay.count() > 1:
            item = self.HistLay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.FeedbackLbl.setText("")
        self.SentenceLbl.setText("")
        self.HintLbl.setText("")
