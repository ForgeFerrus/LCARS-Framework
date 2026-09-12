# Additional UI modules for English Learning System:
#  - GrammarWidget  — rules + mini-quiz for each grammar topic
#  - WritingWidget  — translation practice (user types EN→UA or UA→EN)
#
# Imported from the learning UI package via:
#     from programs.learning.widgets_extra import GrammarWidget, WritingWidget
import random
from lcars.ui.internal import Widget, VBoxLayout, HBoxLayout, Label, Frame, ScrollArea, SizePolicy, ComboBox, LineEdit, Qt, Timer, Cursor

from lcars.base.interface import LCARSButton
from lcars.base.defaults import FontStyle
from programs.learning.grammar_data import GRAMMAR_RULES, get_grammar_rules



class LCARSStationWidget(Widget):
    # Lightweight duplicate of the base class (avoids circular import).
    def __init__(self, theme, faction, parent=None):
        super().__init__(parent)
        self.theme = theme
        self.faction = faction

    def create_lcars_header(self, title, layout, color_idx=0):
        colors = self.theme.get('palette', ['#FF9900'] * 8)
        color = colors[color_idx % len(colors)]
        hdr = Frame()
        hdr.setFixedHeight(88)
        hdr.setStyleSheet(f"background-color: {color}; border-radius: 44px;")
        h_lay = HBoxLayout(hdr)
        h_lay.setContentsMargins(50, 0, 50, 0)
        lbl = Label(title)
        lbl.setStyleSheet(f"color: #000000; {FontStyle(32, 'normal')}; letter-spacing: 1px;")
        h_lay.addWidget(lbl)
        layout.addWidget(hdr)


# ─────────────────────────────────────────────────────────────────────────────
#  GRAMMAR MODULE
# ─────────────────────────────────────────────────────────────────────────────

class GrammarWidget(LCARSStationWidget):
    # Browse grammar rules by level/topic and answer mini fill-in-blank quiz.

    def __init__(self, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.progress = progress
        self.current_rule = None
        self.quiz_idx = 0
        self.quiz_score = 0

        layout = VBoxLayout(self)
        self.create_lcars_header("GRAMMAR MATRIX", layout, 3)

        # ── Level / Rule selector ──────────────────────
        sel_lay = HBoxLayout()
        sel_lay.setContentsMargins(40, 10, 40, 0)
        sel_lay.setSpacing(20)

        self.lvl_box = ComboBox()
        self.lvl_box.addItems(["ALL", "A1", "A2", "B1", "B2"])
        self.StyleCombo(self.lvl_box)
        self.lvl_box.currentTextChanged.connect(self.RefreshRuleList)
        sel_lay.addWidget(self.lvl_box)

        self.rule_box = ComboBox()
        self.StyleCombo(self.rule_box)
        self.rule_box.setMinimumWidth(500)
        self.rule_box.currentIndexChanged.connect(self.LoadRule)
        sel_lay.addWidget(self.rule_box, 1)
        layout.addLayout(sel_lay)
        layout.addSpacing(10)

        # ── Rule panel (scrollable) ─────────────────────
        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        scroll.setSizePolicy(SizePolicy.Policy.Expanding, SizePolicy.Policy.Expanding)

        self.rule_panel = Widget()
        self.rule_panel.setStyleSheet("background: transparent;")
        self.rule_layout = VBoxLayout(self.rule_panel)
        self.rule_layout.setContentsMargins(40, 10, 40, 10)
        self.rule_layout.setSpacing(20)
        scroll.setWidget(self.rule_panel)
        layout.addWidget(scroll, 1)

        # ── Quiz area ──────────────────────────────────
        quiz_frame = Frame()
        quiz_frame.setStyleSheet("background: #1A1A1A; border-radius: 30px;")
        quiz_lay = VBoxLayout(quiz_frame)
        quiz_lay.setContentsMargins(40, 20, 40, 20)

        self.quiz_q_lbl = Label("SELECT A GRAMMAR RULE TO BEGIN MINI-QUIZ")
        self.quiz_q_lbl.setWordWrap(True)
        self.quiz_q_lbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(24, 'normal')}")
        quiz_lay.addWidget(self.quiz_q_lbl)

        self.quiz_opts_lay = HBoxLayout()
        self.quiz_opts_lay.setSpacing(20)
        self.quiz_opt_btns = []
        for i in range(4):
            btn = LCARSButton("", "none", "none", "none", self.theme['palette'][i % len(self.theme['palette'])], radius=4)
            btn.setFixedHeight(56)
            btn.setStyleSheet(btn.styleSheet() + f"{FontStyle(20, 'normal')}")
            btn.clicked.connect(lambda checked, idx=i: self.CheckAnswer(idx))
            self.quiz_opts_lay.addWidget(btn)
            self.quiz_opt_btns.append(btn)
        quiz_lay.addLayout(self.quiz_opts_lay)

        self.quiz_feedback = Label("")
        self.quiz_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quiz_feedback.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        quiz_lay.addWidget(self.quiz_feedback)

        layout.addWidget(quiz_frame)
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
        self.rule_box.blockSignals(True)
        self.rule_box.clear()
        rules = get_grammar_rules(None if level == "ALL" else level)
        for r in rules:
            self.rule_box.addItem(f"[{r['level']}] {r['title']}", r)
        self.rule_box.blockSignals(False)
        if self.rule_box.count():
            self.LoadRule(0)

    def LoadRule(self, idx):
        if idx < 0 or self.rule_box.count() == 0:
            return
        rule = self.rule_box.itemData(idx)
        if not rule:
            return
        self.current_rule = rule
        # Clear rule panel
        while self.rule_layout.count():
            item = self.rule_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()

        # Rule text
        rule_lbl = Label(rule['rule'])
        rule_lbl.setWordWrap(True)
        rule_lbl.setStyleSheet(f"color: #CCCCCC; {FontStyle(22, 'normal')}; padding: 16px; "
                               f"background: #111; border-radius: 20px;")
        self.rule_layout.addWidget(rule_lbl)

        # Examples
        ex_title = Label("✦ EXAMPLES")
        ex_title.setStyleSheet(f"color: {self.theme['palette'][1]}; {FontStyle(22, 'normal')}")
        self.rule_layout.addWidget(ex_title)

        for en, ua in rule['examples']:
            row = Frame()
            row.setStyleSheet("background: #1a1a1a; border-radius: 15px; padding: 5px;")
            row_lay = VBoxLayout(row)
            row_lay.setContentsMargins(20, 10, 20, 10)
            en_lbl = Label(f"▸ {en}")
            en_lbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(20, 'normal')}")
            ua_lbl = Label(f"  {ua}")
            ua_lbl.setStyleSheet(f"color: #999; {FontStyle(18, 'normal')}")
            row_lay.addWidget(en_lbl)
            row_lay.addWidget(ua_lbl)
            self.rule_layout.addWidget(row)

        self.rule_layout.addStretch()

        # Reset quiz
        self.quiz_idx = 0
        self.quiz_score = 0
        self.LoadQuizQuestion()

    def LoadQuizQuestion(self):
        if not self.current_rule:
            return
        questions = self.current_rule['quiz']
        if self.quiz_idx >= len(questions):
            self.quiz_q_lbl.setText(f"✓ QUIZ COMPLETE! Score: {self.quiz_score}/{len(questions)}")
            self.quiz_feedback.setText("")
            for btn in self.quiz_opt_btns:
                btn.hide()
            return

        q = questions[self.quiz_idx]
        self.quiz_q_lbl.setText(f"[{self.quiz_idx + 1}/{len(questions)}]  {q['q']}")
        self.quiz_feedback.setText("")

        opts = q['opts'][:]
        random.shuffle(opts)
        self._current_answer = q['a']
        self._current_opts = opts

        for i, btn in enumerate(self.quiz_opt_btns):
            if i < len(opts):
                btn.setText(opts[i])
                btn.show()
            else:
                btn.hide()

    def CheckAnswer(self, idx):
        if idx >= len(self._current_opts):
            return
        chosen = self._current_opts[idx]
        if chosen == self._current_answer:
            self.quiz_feedback.setText("✓ CORRECT!")
            self.quiz_feedback.setStyleSheet(f"color: #00FF88; {FontStyle(20, 'normal')}")
            self.quiz_score += 1
        else:
            self.quiz_feedback.setText(f"✗ INCORRECT — Answer: {self._current_answer}")
            self.quiz_feedback.setStyleSheet(f"color: #FF4444; {FontStyle(20, 'normal')}")
        self.quiz_idx += 1
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
        self.current_word = None
        self.direction = "en→ua"   # or "ua→en"
        self.score = 0
        self.total = 0

        layout = VBoxLayout(self)
        self.create_lcars_header("WRITING PRACTICE", layout, 2)

        # ── Controls bar ───────────────────────────────
        ctrl_lay = HBoxLayout()
        ctrl_lay.setContentsMargins(40, 10, 40, 0)
        ctrl_lay.setSpacing(20)

        self.dir_box = ComboBox()
        self.dir_box.addItems(["EN → УКРАЇНСЬКА", "УКРАЇНСЬКА → EN"])
        self.dir_box.setFixedHeight(56)
        self.dir_box.setStyleSheet(
            f"QComboBox {{ padding: 10px 20px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 28px; {FontStyle(18, 'normal')} }}"
            f"QComboBox::drop-down {{ border: none; }}"
            f"QComboBox QAbstractItemView {{ background: #222; color: #FFFFFF; }}"
        )
        self.dir_box.currentIndexChanged.connect(self.ToggleDirection)
        ctrl_lay.addWidget(self.dir_box)

        self.score_lbl = Label("SCORE: 0 / 0")
        self.score_lbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {FontStyle(22, 'normal')}")
        ctrl_lay.addStretch()
        ctrl_lay.addWidget(self.score_lbl)
        layout.addLayout(ctrl_lay)
        layout.addSpacing(20)

        # ── Word display card ──────────────────────────
        self.card = Frame()
        self.card.setFixedHeight(210)
        self.card.setStyleSheet("background: #1A1A1A; border-radius: 24px;")
        card_lay = VBoxLayout(self.card)

        self.prompt_lbl = Label("PRESS START")
        self.prompt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_lbl.setWordWrap(True)
        self.prompt_lbl.setStyleSheet(f"color: #FFFFFF; {FontStyle(44, 'normal')}")
        card_lay.addWidget(self.prompt_lbl)

        self.hint_lbl = Label("")
        self.hint_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_lbl.setStyleSheet(f"color: #666; {FontStyle(18, 'normal')}")
        card_lay.addWidget(self.hint_lbl)
        layout.addWidget(self.card)
        layout.addSpacing(20)

        # ── Input ──────────────────────────────────────
        input_lay = HBoxLayout()
        input_lay.setContentsMargins(40, 0, 40, 0)
        input_lay.setSpacing(20)

        self.answer_in = LineEdit()
        self.answer_in.setPlaceholderText("TYPE YOUR TRANSLATION HERE...")
        self.answer_in.setFixedHeight(60)
        self.answer_in.setStyleSheet(
            f"padding: 10px 30px; background: #222; color: #FFFFFF; border: none; "
            f"border-radius: 30px; {FontStyle(20, 'normal')}"
        )
        self.answer_in.returnPressed.connect(self.CheckAnswer)
        input_lay.addWidget(self.answer_in, 1)

        self.submit_btn = LCARSButton("CHECK", "none", "none", "none", self.theme['palette'][2], radius=4)
        self.submit_btn.setFixedSize(160, 60)
        self.submit_btn.setStyleSheet(self.submit_btn.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.submit_btn.clicked.connect(self.CheckAnswer)
        input_lay.addWidget(self.submit_btn)
        layout.addLayout(input_lay)
        layout.addSpacing(10)

        # ── Feedback ───────────────────────────────────
        self.feedback_lbl = Label("")
        self.feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_lbl.setWordWrap(True)
        self.feedback_lbl.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        layout.addWidget(self.feedback_lbl)
        layout.addSpacing(10)

        # ── Buttons ────────────────────────────────────
        btn_lay = HBoxLayout()
        btn_lay.setContentsMargins(40, 0, 40, 0)
        btn_lay.setSpacing(20)

        self.start_btn = LCARSButton("START", "none", "none", "none", self.theme['accent'], radius=4)
        self.start_btn.setFixedSize(210, 64)
        self.start_btn.setStyleSheet(self.start_btn.styleSheet() + f"{FontStyle(20, 'normal')}")
        self.start_btn.clicked.connect(self.NextWord)
        btn_lay.addWidget(self.start_btn)

        self.skip_btn = LCARSButton("SKIP →", "none", self.theme['palette'][4], radius=4)
        self.skip_btn.setFixedSize(160, 64)
        self.skip_btn.setStyleSheet(self.skip_btn.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.skip_btn.clicked.connect(self.Skip)
        btn_lay.addWidget(self.skip_btn)

        btn_lay.addStretch()
        layout.addLayout(btn_lay)
        layout.addStretch()

    def ToggleDirection(self, idx):
        self.direction = "en→ua" if idx == 0 else "ua→en"
        self.feedback_lbl.setText("")
        self.NextWord()

    def NextWord(self):
        lvl = self.progress.get_current_level()
        words = self.db.get_random_words(level=lvl, count=1)
        if not words:
            words = self.db.get_random_words(count=1)
        if not words:
            self.prompt_lbl.setText("NO WORDS IN DATABASE")
            return
        self.current_word = words[0]
        en = self.current_word.get('english', '')
        ua = self.current_word.get('ukrainian', '')
        pos = self.current_word.get('part_of_speech', '')

        if self.direction == "en→ua":
            self.prompt_lbl.setText(en.upper())
            self.hint_lbl.setText(f"[{pos}]  →  Type Ukrainian translation")
        else:
            self.prompt_lbl.setText(ua)
            self.hint_lbl.setText(f"[{pos}]  →  Type English word")

        self.answer_in.clear()
        self.answer_in.setFocus()
        self.feedback_lbl.setText("")
        self.start_btn.setText("NEXT →")

    def CheckAnswer(self):
        if not self.current_word:
            self.NextWord()
            return
        user_ans = self.answer_in.text().strip().lower()
        if not user_ans:
            return

        en = self.current_word.get('english', '').lower()
        ua = self.current_word.get('ukrainian', '').lower()

        if self.direction == "en→ua":
            correct = ua
        else:
            correct = en

        # Lenient matching: accept if user answer is contained in correct or vice versa
        self.total += 1
        if user_ans in correct or correct.startswith(user_ans) or user_ans == correct.split("/")[0].strip():
            self.score += 1
            self.feedback_lbl.setText(f"✓ CORRECT! → {correct}")
            self.feedback_lbl.setStyleSheet(f"color: #00FF88; {FontStyle(20, 'normal')}")
        else:
            self.feedback_lbl.setText(f"✗ INCORRECT — Correct answer: {correct}")
            self.feedback_lbl.setStyleSheet(f"color: #FF4444; {FontStyle(20, 'normal')}")

        self.score_lbl.setText(f"SCORE: {self.score} / {self.total}")
        Timer.singleShot(1800, self.NextWord)

    def Skip(self):
        self.total += 1
        self.score_lbl.setText(f"SCORE: {self.score} / {self.total}")
        self.NextWord()

    def reset(self):
        self.score = 0
        self.total = 0
        self.score_lbl.setText("SCORE: 0 / 0")
        self.current_word = None
        self.prompt_lbl.setText("PRESS START")
        self.feedback_lbl.setText("")

# ─────────────────────────────────────────────────────────────────────────────
#  SETTINGS MODULE
# ─────────────────────────────────────────────────────────────────────────────

class SettingsWidget(LCARSStationWidget):
    # Configuration and maintenance panel for the English Learning System.

    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress

        layout = VBoxLayout(self)
        self.create_lcars_header("SYSTEM SETTINGS", layout, 1)

        scroll = ScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        
        container = Widget()
        container.setStyleSheet("background: transparent;")
        c_lay = VBoxLayout(container)
        c_lay.setContentsMargins(40, 20, 40, 20)
        c_lay.setSpacing(30)

        # -- Database Stats --
        stat_frame = Frame()
        stat_frame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        stat_lay = VBoxLayout(stat_frame)
        
        lbl_stat_title = Label("DATABASE STATISTICS")
        lbl_stat_title.setStyleSheet(f"color: {self.theme['palette'][2]}; {FontStyle(24, 'normal')}")
        stat_lay.addWidget(lbl_stat_title)

        stats = self.db.get_statistics()
        lbl_total = Label(f"Total Words: {stats.get('total_words', 0)}")
        lbl_total.setStyleSheet(f"color: #FFFFFF; {FontStyle(20, 'normal')}")
        stat_lay.addWidget(lbl_total)

        # Show break down
        levels_text = " • ".join([f"{lvl}: {stats.get('by_level',{}).get(lvl,0)}" for lvl in ["A1","A2","B1","B2","C1","C2"]])
        lbl_lvls = Label(f"Levels: {levels_text}")
        lbl_lvls.setStyleSheet(f"color: #AAAAAA; {FontStyle(18, 'normal')}")
        stat_lay.addWidget(lbl_lvls)
        
        c_lay.addWidget(stat_frame)

        # -- Progress Management --
        prg_frame = Frame()
        prg_frame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        prg_lay = VBoxLayout(prg_frame)
        
        lbl_prg_title = Label("USER PROGRESS")
        lbl_prg_title.setStyleSheet(f"color: {self.theme['palette'][3]}; {FontStyle(24, 'normal')}")
        prg_lay.addWidget(lbl_prg_title)

        self.btn_reset_prg = LCARSButton("RESET ALL PROGRESS", "none", "#FF3333", radius=4)
        self.btn_reset_prg.setFixedHeight(56)
        self.btn_reset_prg.setStyleSheet(self.btn_reset_prg.styleSheet() + f"{FontStyle(18, 'normal')}")
        self.btn_reset_prg.clicked.connect(self.ResetProgress)
        prg_lay.addWidget(self.btn_reset_prg)

        self.lbl_reset_status = Label("")
        self.lbl_reset_status.setStyleSheet(f"color: #FFD700; {FontStyle(20, 'normal')}")
        prg_lay.addWidget(self.lbl_reset_status)
        
        c_lay.addWidget(prg_frame)

        # -- Audio Settings placeholder --
        aud_frame = Frame()
        aud_frame.setStyleSheet("background: #1A1A1A; border-radius: 20px;")
        aud_lay = VBoxLayout(aud_frame)
        
        lbl_aud_title = Label("AUDIO & TTS")
        lbl_aud_title.setStyleSheet(f"color: {self.theme['palette'][4]}; {FontStyle(24, 'normal')}")
        aud_lay.addWidget(lbl_aud_title)

        lbl_aud_info = Label("Text-to-Speech (TTS) uses default OS En-US voice.\nEnsure Windows TTS packs are installed for best quality.")
        lbl_aud_info.setStyleSheet(f"color: #CCCCCC; {FontStyle(18, 'normal')}")
        aud_lay.addWidget(lbl_aud_info)
        
        c_lay.addWidget(aud_frame)

        c_lay.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def ResetProgress(self):
        self.db.connection.execute("DELETE FROM user_progress")
        self.db.connection.execute("DELETE FROM learning_sessions")
        self.db.connection.execute("UPDATE vocabulary SET mastery_level = 0.0, next_review = NULL, times_reviewed = 0")
        self.db.connection.commit()

        # Reset tracker cache
        self.progress.current_level = "A1"
        if hasattr(self.progress, 'session_start'):
            self.progress.session_start = None

        self.lbl_reset_status.setText("SUCCESS: PROGRESS WIPED")
        # Force UI update
        self.progress.progress_updated.emit()
        Timer.singleShot(3000, lambda: self.lbl_reset_status.setText(""))
