# ─────────────────────────────────────────────────────────────
# Tenses Subsystem Module :: Standard Realignment
# ─────────────────────────────────────────────────────────────
# LCARS abstractions for UI components (no direct PyQt6 usage)
from lcars.base.type import Chassis, Label, Frame, ScrollArea, Widget, ComboBox, ListWidget
from lcars.base.interface import LCARSElbow
from lcars.base.components import LearningStation
from lcars.base.default import FontStyle, RandomButtonColor
from lcars.modules.sound_manager import GetSoundManager

def BuildTensesPalette():
    return [
        RandomButtonColor("buttons"),
        RandomButtonColor("buttons"),
        RandomButtonColor("accent"),
        RandomButtonColor("panels"),
        RandomButtonColor("alert"),
    ]

# --- IMPORT BASE CLASS ---
from lcars.program.learning.ui.interface import LearningStation, ComboBox, ListWidget
# ─────────────────────────────────────────────────────────────
# Tenses Database (Static)
# ─────────────────────────────────────────────────────────────
TENSESData = [
    {
        "id": "prs_simple",
        "name": "Present Simple",
        "uk_name": "Теперішній простий",
        "group": "PRESENT",
        "formula": "Subject + Verb(s)",
        "usage": "Regular actions, habits, general truths, and future schedules.",
        "markers": ["always", "usually", "often", "sometimes", "rarely", "never", "every day", "on Mondays"],
        "examples": [
            ("I work in an office.", "Я працюю в офісі."),
            ("He drinks tea every morning.", "Він п'є чай щоранку."),
            ("Water boils at 100 degrees.", "Вода закипає при 100 градусах.")
        ],
    },
    {
        "id": "prs_cont",
        "name": "Present Continuous",
        "uk_name": "Теперішній тривалий",
        "group": "PRESENT",
        "formula": "Subject + am/is/are + Verb-ing",
        "usage": "Actions happening right now, temporary situations, or fixed future plans.",
        "markers": ["now", "at the moment", "right now", "currently", "today", "this week"],
        "examples": [
            ("I am reading a book now.", "Я читаю книгу зараз."),
            ("She is staying with us for a week.", "Вона живе у нас тиждень."),
            ("We are meeting at 5 PM.", "Ми зустрічаємося о 5 вечора.")
        ],
    },
    {
        "id": "prs_perf",
        "name": "Present Perfect",
        "uk_name": "Теперішній доконаний",
        "group": "PRESENT",
        "formula": "Subject + have/has + Past Participle (V3)",
        "usage": "Actions completed in the past with a result in the present, or life experiences.",
        "markers": ["just", "already", "yet", "ever", "never", "recently", "lately", "so far"],
        "examples": [
            ("I have just finished my report.", "Я щойно закінчив свій звіт."),
            ("Have you ever been to Paris?", "Ви коли-небудь були в Парижі?"),
            ("She hasn't finished her coffee yet.", "Вона ще не допила свою каву.")
        ],
    },
    {
        "id": "prs_perf_cont",
        "name": "Present Perfect Continuous",
        "uk_name": "Теперішній доконано-тривалий",
        "group": "PRESENT",
        "formula": "Subject + have/has been + Verb-ing",
        "usage": "Actions that started in the past and are still continuing, or actions with a visible result now.",
        "markers": ["for", "since", "all day", "lately", "recently"],
        "examples": [
            ("I have been waiting for two hours.", "Я чекаю вже дві години."),
            ("She has been learning French since June.", "Вона вивчає французьку з червня."),
            ("It has been raining all day.", "Дощить увесь день.")
        ],
    },
    # PAST
    {
        "id": "past_simple",
        "name": "Past Simple",
        "uk_name": "Минулий простий",
        "group": "PAST",
        "formula": "Subject + Verb-ed (or V2)",
        "usage": "Completed actions in a specific time in the past.",
        "markers": ["yesterday", "last week", "ago", "in 2010", "when I was young"],
        "examples": [
            ("I saw a movie yesterday.", "Я бачив фільм учора."),
            ("They moved to Kyiv in 2015.", "Вони переїхали до Києва у 2015 році."),
            ("She didn't call me last night.", "Вона не дзвонила мені минулої ночі.")
        ],
    },
    {
        "id": "past_cont",
        "name": "Past Continuous",
        "uk_name": "Минулий тривалий",
        "group": "PAST",
        "formula": "Subject + was/were + Verb-ing",
        "usage": "Actions occurring at a specific time in the past or interrupted actions.",
        "markers": ["at 5 o'clock yesterday", "when", "while", "all morning"],
        "examples": [
            ("I was sleeping at midnight.", "Я спав опівночі."),
            ("He was cooking while I was working.", "Він готував, поки я працював."),
            ("They were playing football when it started to rain.", "Вони грали у футбол, коли почався дощ.")
        ],
    },
    {
        "id": "past_perf",
        "name": "Past Perfect",
        "uk_name": "Минулий доконаний",
        "group": "PAST",
        "formula": "Subject + had + V3",
        "usage": "Action completed before another action in the past.",
        "markers": ["before", "after", "by the time", "already"],
        "examples": [
            ("The train had left when I arrived.", "Поїзд пішов, коли я приїхав."),
            ("I had finished my work by 6 PM.", "Я закінчив роботу до 6-ї години вечора."),
            ("She had already seen the film.", "Вона вже бачила цей фільм.")
        ],
    },
    {
        "id": "past_perf_cont",
        "name": "Past Perfect Continuous",
        "uk_name": "Минулий доконано-тривалий",
        "group": "PAST",
        "formula": "Subject + had been + Verb-ing",
        "usage": "Action that was ongoing until another past action.",
        "markers": ["for", "since", "all day", "by the time"],
        "examples": [
            ("I had been studying for 3 hours when he called.", "Я вчився 3 години, коли він подзвонив."),
            ("She was tired because she had been running.", "Вона втомилася, бо бігала."),
            ("They had been building the bridge for years.", "Вони будували міст роками.")
        ],
    },
    # FUTURE
    {
        "id": "fut_simple",
        "name": "Future Simple",
        "uk_name": "Майбутній простий",
        "group": "FUTURE",
        "formula": "Subject + will + Verb",
        "usage": "Spontaneous decisions, predictions, promises, or threats.",
        "markers": ["tomorrow", "next week", "soon", "in the future", "one day"],
        "examples": [
            ("I will call you tomorrow.", "Я подзвоню тобі завтра."),
            ("I think it will snow tonight.", "Я думаю, ввечері піде сніг."),
            ("She won't be at the party.", "Її не буде на вечірці.")
        ],
    },
    {
        "id": "fut_cont",
        "name": "Future Continuous",
        "uk_name": "Майбутній тривалий",
        "group": "FUTURE",
        "formula": "Subject + will be + Verb-ing",
        "usage": "Action that will be occurring at a specific time in the future.",
        "markers": ["at this time tomorrow", "all day next Monday", "at 9 PM"],
        "examples": [
            ("This time tomorrow I will be flying to Paris.", "Завтра в цей час я летітиму в Париж."),
            ("At 8 PM she will be working.", "О 8-й вечора вона буде працювати."),
            ("We will be studying all night.", "Ми вчитимемося всю ніч.")
        ],
    },
    {
        "id": "fut_perf",
        "name": "Future Perfect",
        "uk_name": "Майбутній доконаний",
        "group": "FUTURE",
        "formula": "Subject + will have + V3",
        "usage": "Action that will be finished by a specific future point.",
        "markers": ["by", "by the time", "before", "by 2030"],
        "examples": [
            ("I will have finished the project by Monday.", "Я закінчу проект до понеділка."),
            ("She will have graduated by next summer.", "Вона закінчить навчання до наступного літа."),
            ("By the time you arrive, I will have cooked dinner.", "До твого приїзду я приготую вечерю.")
        ],
    },
    {
        "id": "fut_perf_cont",
        "name": "Future Perfect Continuous",
        "uk_name": "Майбутній доконано-тривалий",
        "group": "FUTURE",
        "formula": "Subject + will have been + Verb-ing",
        "usage": "Ongoing action that will continue until a future point.",
        "markers": ["for", "by the end of", "all day"],
        "examples": [
            ("By June, I will have been working here for 5 years.", "До червня я працюватиму тут вже 5 років."),
            ("He will have been studying for 10 hours by then.", "На той час він вчитиметься вже 10 годин."),
        ],
    }
]

# ─────────────────────────────────────────────────────────────
# Tenses Subsystem Module :: Standard Realignment
# ─────────────────────────────────────────────────────────────
class TensesWidget(LearningStation):
    # Titan-class overhaul of the Temporal Matrix (Tenses).
    # Implements a 3-column architectural layout:
    # - LEFT: ARCH-SELECTOR (Categories & Tense list)
    # - CENTER: CORE LOGIC (Formula & Usage)
    # - RIGHT: DATA STREAM (Examples & Context)

    def __init__(self, theme, dbManager, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = dbManager
        self.currentTense = None
        self.era = None

        self.setStyleSheet("background-color: black;")
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- INTERNAL TITAN HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(100)
        headerLay = Chassis.Horizontal(headerFrame)
        headerLay.setContentsMargins(0, 10, 20, 0)
        headerLay.setSpacing(20)

        palette = self.theme.get('palette', BuildTensesPalette())
        if len(palette) < 5:
            palette = (palette + BuildTensesPalette())[:5]
        
        self.headerElbow = LCARSElbow("top-left", palette[1])
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("TEMPORAL MATRIX // ENGLISH TENSES")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'bold')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ PHASE LOCK: STABLE // ALL SYSTEMS NOMINAL")
        self.statusLbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[3]), 1)
        layout.addWidget(headerFrame)

        # --- MAIN ARCHITECTURAL CONTENT ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)

        # 1. LEFT COLUMN: SELECTOR
        self.leftPanel = Frame()
        self.leftPanel.setFixedWidth(300)
        self.leftPanel.setStyleSheet("background: #0b0d14; border: 1px solid #23283a; border-radius: 10px;")
        leftCol = Chassis.Vertical(self.leftPanel)
        leftCol.setContentsMargins(0, 0, 0, 0)
        leftCol.setSpacing(10)

        self.groupBox = ComboBox()
        self.groupBox.addItems(["ALL", "PRESENT", "PAST", "FUTURE"])
        self.StyleCombo(self.groupBox)
        self.groupBox.currentTextChanged.connect(self.RefreshTenseList)
        leftCol.addWidget(self.groupBox)

        self.tenseList = ListWidget()
        self.tenseList.setStyleSheet(f"\n            QListWidget {{\n                background: transparent; border: none; color: #FFF;\n                {FontStyle(18, 'bold')}\n            }}\n            QListWidget::item {{\n                background: #11151f; padding: 15px; border-left: 10px solid {palette[1]};\n                margin-bottom: 6px; border-radius: 6px;\n            }}\n            QListWidget::item:selected {{\n                background: {palette[0]}; color: #000; border-left-color: #FFF;\n            }}\n        ")
        self.tenseList.currentRowChanged.connect(self.LoadTenseByIdx)
        leftCol.addWidget(self.tenseList, 1)

        self.botElbow = LCARSElbow("bottom-left", palette[0])
        self.botElbow.setMinimumHeight(80)
        leftCol.addWidget(self.botElbow)
        bodyHbox.addWidget(self.leftPanel)

        # 2. CENTER COLUMN: RULES / FORMULA
        centerCol = Chassis.Vertical()
        centerCol.setSpacing(20)

        self.centerScroll = ScrollArea()
        self.centerScroll.setWidgetResizable(True)
        self.centerScroll.setFrameShape(Frame.Shape.NoFrame)
        self.centerScroll.setStyleSheet("background: #05060a; border: 1px solid #1f2431; border-radius: 10px;")
        
        self.centerPanel = Widget()
        self.centerLay = Chassis.Vertical(self.centerPanel)
        self.centerLay.setContentsMargins(10, 0, 10, 0)
        self.centerLay.setSpacing(20)
        self.centerScroll.setWidget(self.centerPanel)
        
        centerCol.addWidget(self.centerScroll, 1)
        
        # Center Footer Decoration
        centerCol.addWidget(LCARSSegment(Color=palette[2]), 0)
        bodyHbox.addLayout(centerCol, 2)

        # 3. RIGHT COLUMN: EXAMPLES / DATA STREAM
        rightCol = Chassis.Vertical()
        rightCol.setSpacing(15)

        self.rightScroll = ScrollArea()
        self.rightScroll.setWidgetResizable(True)
        self.rightScroll.setFrameShape(Frame.Shape.NoFrame)
        self.rightScroll.setStyleSheet("background: #05060a; border: 1px solid #1f2431; border-radius: 10px;")
        
        self.rightPanel = Widget()
        self.rightLay = Chassis.Vertical(self.rightPanel)
        self.rightLay.setContentsMargins(10, 0, 10, 0)
        self.rightLay.setSpacing(15)
        self.rightScroll.setWidget(self.rightPanel)
        
        rightCol.addWidget(self.rightScroll, 1)
        bodyHbox.addLayout(rightCol, 1)

        layout.addLayout(bodyHbox, 1)

        self.RefreshTenseList("ALL")

    def StyleCombo(self, box):
        palette = self.theme.get('palette', BuildTensesPalette())
        css = f"\n            QComboBox {{ \n                padding: 5px 20px; background: #222; color: #FFF; border: none;\n                border-left: 8px solid {palette[2]}; border-radius: 4px;\n                {FontStyle(20, 'bold')} \n            }}\n            QComboBox::drop-down {{ border: none; width: 0px; }}\n            QComboBox QAbstractItemView {{ \n                background: #111; color: #FFF; selection-background-color: {palette[0]};\n            }}\n        "
        box.setStyleSheet(css)

    def RefreshTenseList(self, group):
        self.tenseList.blockSignals(True)
        self.tenseList.clear()
        self.filteredData = []
        for t in TENSESData:
            if group == "ALL" or t['group'] == group:
                self.tenseList.addItem(f"◤ {t['name'].upper()}")
                self.filteredData.append(t)
        self.tenseList.blockSignals(False)
        if self.tenseList.count() > 0:
            self.tenseList.setCurrentRow(0)

    def LoadTenseByIdx(self, idx):
        if idx < 0 or idx >= len(self.filteredData): return
        t = self.filteredData[idx]
        self.ShowTenseData(t)

    def ShowTenseData(self, t):
        self.currentTense = t
        GetSoundManager().PlayAudioClip("click")
        palette = self.theme.get('palette', BuildTensesPalette())
        if len(palette) < 5:
            palette = (palette + BuildTensesPalette())[:5]

        # --- CLEAR CHANNELS ---
        while self.centerLay.count():
            item = self.centerLay.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()
        while self.rightLay.count():
            item = self.rightLay.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()

        # --- CENTER: LOGIC & FORMULA ---
        # Tense Meta
        metaF = Frame()
        metaF.setStyleSheet(f"background: rgba(255,255,255,0.05); border-left: 12px solid {palette[0]};")
        ml = Chassis.Vertical(metaF)
        
        nameL = Label(t['name'].upper())
        nameL.setStyleSheet(f"color: {palette[0]}; {FontStyle(42, 'bold')};")
        ml.addWidget(nameL)
        
        ukNameL = Label(f"◤ {t['uk_name'].upper()}")
        ukNameL.setStyleSheet(f"color: #888; {FontStyle(22, 'normal')};")
        ml.addWidget(ukNameL)
        self.centerLay.addWidget(metaF)

        # Formula
        self.AddLogicBlock("◤ LINGUISTIC FORMULA", t['formula'], palette[1], self.centerLay, isBig=True)
        # Usage
        self.AddLogicBlock("◤ OPERATIONAL USAGE", t['usage'], palette[2], self.centerLay)
        # Markers
        self.AddMarkerChips(t['markers'], palette[3], self.centerLay)
        self.centerLay.addStretch()

        # --- RIGHT: EXAMPLES ---
        titleR = Label("◢ DATA STREAM EXAMPLES")
        titleR.setStyleSheet(f"color: {palette[4 % len(palette)]}; {FontStyle(20, 'bold')}; letter-spacing: 2px;")
        self.rightLay.addWidget(titleR)

        for en, ua in t['examples']:
            exF = Frame()
            exF.setStyleSheet("background: #080808; border: 1px solid #222; border-radius: 4px;")
            el = Chassis.Vertical(exF)
            
            enL = Label(f"• {en}")
            enL.setStyleSheet(f"color: #FFF; {FontStyle(22, 'normal')};")
            enL.setWordWrap(True)
            
            uaL = Label(f"  {ua}")
            uaL.setStyleSheet(f"color: #666; {FontStyle(16, 'normal')};")
            uaL.setWordWrap(True)
            
            el.addWidget(enL)
            el.addWidget(uaL)
            self.rightLay.addWidget(exF)
        self.rightLay.addStretch()

    def AddLogicBlock(self, title, text, color, layout, isBig=False):
        tl = Label(title)
        tl.setStyleSheet(f"color: {color}; {FontStyle(18, 'bold')}; margin-top: 10px;")
        layout.addWidget(tl)
        
        cl = Label(text)
        cl.setWordWrap(True)
        size = 36 if isBig else 22
        cl.setStyleSheet(f"color: #EEE; {FontStyle(size, 'bold' if isBig else 'normal')}; padding-left: 20px;")
        layout.addWidget(cl)

    def AddMarkerChips(self, markers, color, layout):
        tl = Label("◤ TEMPORAL MARKERS")
        tl.setStyleSheet(f"color: {color}; {FontStyle(18, 'bold')}; margin-top: 10px;")
        layout.addWidget(tl)
        
        container = Widget()
        cl = Chassis.Horizontal(container)
        cl.setContentsMargins(20, 0, 0, 0)
        cl.setSpacing(8)
        
        # Simple flow layout simulation
        for m in markers:
            mL = Label(m.upper())
            mL.setStyleSheet(f"background: {color}; color: #000; padding: 4px 10px; {FontStyle(14, 'bold')}; border-radius: 2px;")
            cl.addWidget(mL)
        cl.addStretch()
        layout.addWidget(container)

    def BuildQuantifiersSection(self, layout):
        """Build some/any/no grammar section"""
        title = Label("◤ QUANTIFIERS: SOME / ANY / NO")
        title.setStyleSheet("color: #CC6699; font-family: 'LCARS'; font-size: 20pt; font-weight: bold; margin-top: 20px;")
        layout.addWidget(title)

        rules = [
            ("SOME", "Ствердження + пропозиції", [
                "I have SOME free time.",
                "Would you like SOME coffee?",
                "SOME people like jazz."
            ]),
            ("ANY", "Заперечення + питання", [
                "I don't have ANY money.",
                "Do you have ANY questions?",
                "If you need ANY help, call me."
            ]),
            ("NO", "Замість 'not any'", [
                "I have NO time = I don't have any time.",
                "NO smoking allowed.",
                "There is NO milk left."
            ])
        ]

        for name, desc, examples in rules:
            rule_frame = Frame()
            rule_layout = Chassis.Vertical(rule_frame)

            name_lbl = Label(f"• {name}: {desc}")
            name_lbl.setStyleSheet("color: #FF9900; font-family: 'LCARS'; font-size: 16pt;")
            rule_layout.addWidget(name_lbl)

            for ex in examples:
                ex_lbl = Label(f"  → {ex}")
                ex_lbl.setStyleSheet("color: #CCCCCC; font-family: 'LCARS'; font-size: 12pt; margin-left: 30px;")
                rule_layout.addWidget(ex_lbl)

            layout.addWidget(rule_frame)

        # Test button
        test_btn = LCARSButton("TEST QUANTIFIERS", "rounded", RandomButtonColor())
        test_btn.Clicked.connect(self.ShowQuantifiersTest)
        layout.addWidget(test_btn)

    def ShowQuantifiersTest(self):
        """Show quantifiers test"""
        exercises = [
            ("I have ___ questions.", "some", ["some", "any", "no"]),
            ("Do you have ___ money?", "any", ["some", "any", "no"]),
            ("There is ___ bread left.", "no", ["some", "any", "no"]),
            ("Would you like ___ tea?", "some", ["some", "any", "no"]),
        ]
        # Implementation would show interactive test
        print("Quantifiers test started")


# Alias for backward compatibility
TensesWidget = TenseWidget
