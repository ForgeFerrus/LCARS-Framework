from __future__ import annotations
from lcars.base.components import SystemComponent
# ─────────────────────────────────────────────────────────────
# ONBOARD PANEL — LCARS English Learning System
# Панель статусу сесії: рівень, прогрес, тижнева статистика, наступний рівень
# Без жодних системних/інженерних залежностей.
# ─────────────────────────────────────────────────────────────
# LCARS abstractions for UI components (no direct PyQt6 usage)
from lcars.base.default import RandomButtonColor, FontStyle
from lcars.base.type import Chassis, Label, Frame, GridLayout, Timer, ScrollArea, Widget
from lcars.base.signal import Signal
from lcars.base.components import SystemComponent
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment, PushButton, ProgressBar
from lcars.base.components import LCARSSegment
from lcars.base.default import FontStyle, TitanPalette


def BuildOnboardPalette(theme):
    P = theme.get("palette") if isinstance(theme, dict) else None
    if isinstance(P, list) and len(P) >= 4:
        base = list(P[:4])
    else:
        base = [
            TitanPalette.Buttons[0],
            TitanPalette.Buttons[1],
            TitanPalette.Accent[0],
            TitanPalette.YellowAlert[0],
        ]
    return base


class OnboardWidget(SystemComponent):
    """Session & progress status panel. No system/engineering dependencies."""

    def __init__(self, db, progress, theme, faction=None, parent=None):
        super().__init__(parent)
        self.Db = db
        self.Progress = progress
        self.Theme = theme
        self.Pal = BuildOnboardPalette(theme)
        self.setStyleSheet("background: black;")

        self.BuildUI()
        self.Refresh()

    # ─── UI ───────────────────────────────────────────────────

    def BuildUI(self):
        C = self.Pal
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = Frame()
        header.setMinimumHeight(80)
        header.setStyleSheet("background: #050a10;")
        hrow = Chassis.Horizontal(header)
        hrow.setContentsMargins(0, 0, 20, 0)
        hrow.setSpacing(0)
        elbow = LCARSElbow("top-left", C[0])
        elbow.setMinimumSize(260, 80)
        hrow.addWidget(elbow)
        title = Label("SESSION STATUS // ONBOARD")
        title.setStyleSheet(
            f"color: {C[0]}; {FontStyle(24, 'normal')}; letter-spacing: 3px; padding-left: 20px;"
        )
        hrow.addWidget(title, 1)
        self.LevelBadge = Label("—")
        self.LevelBadge.setStyleSheet(
            f"color: #000; background: {C[2]}; {FontStyle(20, 'normal')}; "
            f"padding: 6px 20px; border-radius: 4px;"
        )
        hrow.addWidget(self.LevelBadge)
        layout.addWidget(header)

        strip = Frame()
        strip.setFixedHeight(5)
        strip.setStyleSheet(f"background: {C[1]};")
        layout.addWidget(strip)

        # ── Body ─────────────────────────────────────────────
        body = Chassis.Horizontal()
        body.setContentsMargins(30, 20, 30, 20)
        body.setSpacing(24)

        # LEFT: key metrics
        leftCol = Chassis.Vertical()
        leftCol.setSpacing(14)

        self.MetricLabels = {}
        metrics = [
            ("WORDS IN DATABASE",  "words",     C[0]),
            ("WORDS PRACTICED",    "practiced", C[1]),
            ("WORDS MASTERED",     "mastered",  C[2]),
            ("OVERALL ACCURACY",   "accuracy",  C[3]),
            ("TOTAL SESSIONS",     "sessions",  C[0]),
            ("TIME SPENT",         "time",      C[1]),
        ]
        for label_text, key, color in metrics:
            row = Frame()
            row.setStyleSheet(
                f"background: #0a0f18; border-left: 6px solid {color}; border-radius: 4px;"
            )
            row.setFixedHeight(60)
            rlay = Chassis.Horizontal(row)
            rlay.setContentsMargins(18, 0, 18, 0)
            lbl = Label(label_text)
            lbl.setStyleSheet(f"color: {color}; {FontStyle(11, 'normal')}; letter-spacing: 2px;")
            val = Label("—")
            val.setStyleSheet(f"color: #FFF; {FontStyle(20, 'normal')};")
            rlay.addWidget(lbl)
            rlay.addStretch(1)
            rlay.addWidget(val)
            leftCol.addWidget(row)
            self.MetricLabels[key] = val

        leftCol.addStretch(1)
        body.addLayout(leftCol, 1)

        # RIGHT: level progress + weekly
        rightCol = Chassis.Vertical()
        rightCol.setSpacing(14)

        # Level progress block
        lvlBlock = Frame()
        lvlBlock.setStyleSheet(f"background: #0a0f18; border-left: 6px solid {C[2]}; border-radius: 4px;")
        lvlLay = Chassis.Vertical(lvlBlock)
        lvlLay.setContentsMargins(18, 14, 18, 14)
        lvlLay.setSpacing(8)
        lvlTitle = Label("LEVEL PROGRESS")
        lvlTitle.setStyleSheet(f"color: {C[2]}; {FontStyle(11, 'normal')}; letter-spacing: 2px;")
        lvlLay.addWidget(lvlTitle)
        self.LevelProgressBars = {}
        for crit_label, key in [
            ("VOCABULARY", "vocab_pct"),
            ("ACCURACY",   "acc_pct"),
            ("EXERCISES",  "ex_pct"),
        ]:
            cRow = Chassis.Horizontal()
            cLbl = Label(crit_label)
            cLbl.setFixedWidth(110)
            cLbl.setStyleSheet(f"color: #AAB; {FontStyle(11, 'normal')};")
            cRow.addWidget(cLbl)
            if ProgressBar:
                bar = ProgressBar()
                bar.setRange(0, 100)
                bar.setValue(0)
                bar.setFixedHeight(18)
                bar.setObjectName(f"lvlbar_{key}")
                bar.setStyleSheet(
                    f"#lvlbar_{key} {{ border: 1px solid #1a1f2e; background: #111; border-radius: 8px; text-align: center; color: transparent; }}"
                    f"#lvlbar_{key}::chunk {{ background: {C[2]}; border-radius: 8px; }}"
                )
                cRow.addWidget(bar, 1)
                self.LevelProgressBars[key] = bar
            valLbl = Label("0%")
            valLbl.setFixedWidth(42)
            valLbl.setStyleSheet(f"color: #FFF; {FontStyle(11, 'normal')}; padding-left: 4px;")
            cRow.addWidget(valLbl)
            lvlLay.addLayout(cRow)
            self.LevelProgressBars[key + "_lbl"] = valLbl
        rightCol.addWidget(lvlBlock)

        # Next level block
        nextBlock = Frame()
        nextBlock.setStyleSheet(f"background: #0a0f18; border-left: 6px solid {C[3]}; border-radius: 4px;")
        nextLay = Chassis.Vertical(nextBlock)
        nextLay.setContentsMargins(18, 14, 18, 14)
        nextLay.setSpacing(6)
        nextTitle = Label("NEXT LEVEL TARGET")
        nextTitle.setStyleSheet(f"color: {C[3]}; {FontStyle(11, 'normal')}; letter-spacing: 2px;")
        nextLay.addWidget(nextTitle)
        self.NextLevelLbl = Label("—")
        self.NextLevelLbl.setStyleSheet(f"color: #FFF; {FontStyle(16, 'normal')};")
        self.NextLevelLbl.setWordWrap(True)
        nextLay.addWidget(self.NextLevelLbl)
        rightCol.addWidget(nextBlock)

        # Weekly block
        weekBlock = Frame()
        weekBlock.setStyleSheet(f"background: #0a0f18; border-left: 6px solid {C[1]}; border-radius: 4px;")
        weekLay = Chassis.Vertical(weekBlock)
        weekLay.setContentsMargins(18, 14, 18, 14)
        weekLay.setSpacing(6)
        weekTitle = Label("THIS WEEK")
        weekTitle.setStyleSheet(f"color: {C[1]}; {FontStyle(11, 'normal')}; letter-spacing: 2px;")
        weekLay.addWidget(weekTitle)
        self.WeekLabels = {}
        for wlabel, wkey in [("SESSIONS", "w_sessions"), ("MINUTES", "w_minutes"), ("WORDS", "w_vocab"), ("EXERCISES", "w_exercises")]:
            wr = Chassis.Horizontal()
            wl = Label(wlabel)
            wl.setFixedWidth(110)
            wl.setStyleSheet(f"color: #AAB; {FontStyle(11, 'normal')};")
            wv = Label("—")
            wv.setStyleSheet(f"color: #FFF; {FontStyle(16, 'normal')};")
            wr.addWidget(wl)
            wr.addStretch(1)
            wr.addWidget(wv)
            weekLay.addLayout(wr)
            self.WeekLabels[wkey] = wv
        rightCol.addWidget(weekBlock)

        rightCol.addStretch(1)
        body.addLayout(rightCol, 1)
        layout.addLayout(body, 1)

        # Refresh button + bottom strip
        footRow = Chassis.Horizontal()
        footRow.setContentsMargins(30, 0, 30, 12)
        btn = LCARSButton("REFRESH", Color=self.Pal[0])
        btn.setFixedHeight(38)
        btn.Clicked.connect(self.Refresh)
        footRow.addWidget(btn)
        footRow.addStretch(1)
        layout.addLayout(footRow)

        bot = LCARSSegment(Color=self.Pal[0])
        bot.setFixedHeight(8)
        layout.addWidget(bot)

    # ─── DATA ─────────────────────────────────────────────────

    def Refresh(self):
        self.updateData()

    def updateData(self):
        summary   = self.Db.getProgressSummary()
        mp        = summary.get("vocabulary") or {}
        total     = mp.get("total_vocabulary") or 0
        practiced = mp.get("total_practiced") or 0
        mastered  = mp.get("learned_vocabulary") or 0
        raw_acc   = mp.get("vocabulary_accuracy") or 0.0
        acc       = round(raw_acc * 100, 1)
        lvl       = self.Progress.getCurrentLevel()

        self.MetricLabels["words"].setText(str(total))
        self.MetricLabels["practiced"].setText(str(practiced))
        self.MetricLabels["mastered"].setText(str(mastered))
        self.MetricLabels["accuracy"].setText(f"{acc:.1f}%")
        self.LevelBadge.setText(f"  LEVEL {lvl}  ")

        if hasattr(self.Db, "getStatistics"):
            stats    = self.Db.getStatistics()
            sessions = stats.get("total_sessions") or "—"
            minutes  = stats.get("total_minutes")
            self.MetricLabels["sessions"].setText(str(sessions))
            self.MetricLabels["time"].setText(f"{int(minutes)} min" if minutes else "—")
        else:
            self.MetricLabels["sessions"].setText("—")
            self.MetricLabels["time"].setText("—")

        lvlData = self.Progress.getLevelProgress(lvl)
        bar_map = [
            ("vocab_pct", (lvlData.get("vocabulary") or {})),
            ("acc_pct",   (lvlData.get("accuracy")   or {})),
            ("ex_pct",    (lvlData.get("points")      or {})),
        ]
        for key, block in bar_map:
            pct = int(block.get("progress") or 0)
            if key in self.LevelProgressBars:
                self.LevelProgressBars[key].setValue(pct)
            lbl_key = key + "_lbl"
            if lbl_key in self.LevelProgressBars:
                self.LevelProgressBars[lbl_key].setText(f"{pct}%")

        nxt       = self.Progress.getNextLevelRequirements()
        nl        = nxt.get("next_level") or "—"
        req       = nxt.get("requirements") or {}
        vocab_req = req.get("vocabulary") or "?"
        acc_req   = req.get("accuracy") or "?"
        self.NextLevelLbl.setText(
            f"TARGET: {nl}\n"
            f"VOCAB: {vocab_req} words\n"
            f"ACCURACY: {acc_req}%"
        )

        week = self.Progress.getWeeklyProgress()
        self.WeekLabels["w_sessions"].setText(str(week.get("session_count") or "—"))
        raw_mins = week.get("total_minutes")
        self.WeekLabels["w_minutes"].setText(str(int(raw_mins)) if raw_mins else "—")
        self.WeekLabels["w_vocab"].setText(str(week.get("total_vocabulary") or "—"))
        self.WeekLabels["w_exercises"].setText(str(week.get("total_exercises") or "—"))
