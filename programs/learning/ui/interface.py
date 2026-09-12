import sys
from lcars.base.type import (
    Label, Frame, Widget, Chassis,
    GridLayout, Signal, Visual
)
from lcars.base.components import SystemComponent
from lcars.base.interface import (
    LCARSButton, LCARSElbow, LCARSSegment,
    ProgressBar, LineEdit, ScrollArea, ComboBox,
    ListWidget, ListWidgetItem,
)
from lcars.base.default import FontStyle, RandomButtonColor
from lcars.modules.sound_manager import GetSoundManager

# UI components are exported via lcars.base.interface (Titanium registry).
# Import them explicitly so downstream modules get proper types/signals
# instead of fragile getattr-based fallbacks.


def ResolvePalette(theme):
    """
    Отримує палітру кольорів з теми або генерує стандартну.
    
    Якщо тема має палітру з 6+ кольорів - використовує її.
    Інакше генерує випадкові кольори для різних елементів інтерфейсу
    (кнопки, акценти, панелі, алерти) використовуючи RandomButtonColor.
    
    Args:
        theme: dict з налаштуваннями теми або None
    
    Returns:
        list: список кольорів у форматі hex (#RRGGBB)
    """
    palette = theme.get("palette") if isinstance(theme, dict) else None
    if isinstance(palette, list) and len(palette) >= 6:
        return palette
    return [
        RandomButtonColor("buttons"),
        RandomButtonColor("buttons"),
        RandomButtonColor("accent"),
        RandomButtonColor("buttons"),
        RandomButtonColor("alert"),
        RandomButtonColor("panels"),
    ]

USER_ROLE = 256
# --- BASE WIDGET ---

class LearningStation(SystemComponent):
    """
    Базовий клас для всіх навчальних панелей (Learning Station).
    
    Наслідує SystemComponent - базовий віджет LCARS з підтримкою:
    - Тем (кольори, шрифти)
    - Фракцій (FEDERATION, etc.)
    - Спільних методів типу createHeader()
    
    Всі панелі (Dashboard, Grammar, Tenses) наслідують цей клас
    для отримання спільного функціоналу.
    """
    def __init__(self, theme, faction, parent=None):
        super().__init__(parent)
        self.theme = theme  # dict з palette, accent, alert кольорами
        self.faction = faction  # "FEDERATION" або інші фракції

    def createHeader(self, titleText, layout, colorIdx=0):
        """
        Створює заголовок панелі з LCARS-стилем.
        
        Args:
            titleText: Текст заголовку (автоматично upper())
            layout: Layout для додавання заголовка
            colorIdx: Індекс кольору з палітри теми
        """
        # Використовуємо колір з палітри теми за індексом
        title = Label(titleText.upper())
        title.setStyleSheet(f"color: {self.theme['palette'][colorIdx]}; {FontStyle(42, 'normal')}; letter-spacing: 2px;")
        title.setContentsMargins(20, 10, 20, 20)
        layout.addWidget(title)
        return title

# --- LEVEL SELECTOR ---

class LevelSelectorWidget(LearningStation):
    levelSelected = Signal(str)
    
    def __init__(self, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        
        layout = Chassis.Vertical(self)
        
        title = Label("SELECT LINGUISTIC PROTOCOL LEVEL")
        title.setStyleSheet(f"color: {self.theme['accent']}; {FontStyle(56, 'normal')}")
        layout.addWidget(title)
        layout.addSpacing(60)
        
        gridLay = Chassis.Vertical()
        gridLay.setSpacing(30)
        
        levels = [("A1 - BEGINNER", "A1"), ("A2 - ELEMENTARY", "A2"), 
                  ("B1 - INTERMEDIATE", "B1"), ("B2 - UPPER INTERMEDIATE", "B2"),
                  ("C1 - ADVANCED", "C1"), ("C2 - PROFICIENT", "C2")]
                  
        rowLay = Chassis.Horizontal()
        rowLay.setSpacing(40)
        gridLay.addLayout(rowLay)
        for i, (name, val) in enumerate(levels):
            if i % 2 == 0:
                rowLay = Chassis.Horizontal()
                rowLay.setSpacing(40)
                gridLay.addLayout(rowLay)
                
            btn = LCARSButton(name, Color=self.theme['palette'][i % len(self.theme['palette'])])
            btn.setFixedSize(600, 140)
            btn.setStyleSheet(btn.styleSheet() + f"{FontStyle(36, 'normal')}")
            btn.Clicked.connect(lambda checked, v=val: self.levelSelected.emit(v))
            rowLay.addWidget(btn)
            
        layout.addLayout(gridLay)

# --- DASHBOARD ---

class DashboardWidget(LearningStation):
    # Titan-class Dashboard for the Linguistic Matrix. Displays mission progress and primary command nodes.
    startExercise = Signal(str)
    
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
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

        palette = ResolvePalette(self.theme)

        self.headerElbow = LCARSElbow("top-left", palette[1] if len(palette) > 1 else "#FFFFFF")
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("MAIN MATRIX DASHBOARD // V5.0")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ LINGUISTIC ENGINE: READY // NEURAL LINK STABLE")
        self.statusLbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[3]), 1)
        layout.addWidget(headerFrame)
        
        # --- DASHBOARD ARCHITECTURE ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)
        
        # LEFT: PROGRESS & METRICS
        leftCol = Chassis.Vertical()
        leftCol.setSpacing(20)
        
        # Large Analytics Block
        anaF = Frame()
        anaF.setStyleSheet(f"background: rgba(255,255,255,0.05); border-left: 15px solid {palette[0]}; border-radius: 4px;")
        al = Chassis.Vertical(anaF)
        al.setContentsMargins(30, 20, 30, 20)
        
        self.progLabel = Label("COMPLETION: 0%")
        self.progLabel.setStyleSheet(f"color: #FFF; {FontStyle(36, 'normal')}")
        al.addWidget(self.progLabel)
        
        self.progBar = ProgressBar()
        self.progBar.setObjectName("dashProgress")
        self.progBar.setFixedHeight(30)
        self.progBar.setStyleSheet(f'\n            #dashProgress {{ border: 1px solid #333; background: #111; border-radius: 15px; text-align: center; color: transparent; }}\n            #dashProgress::chunk {{ background: {palette[2]}; border-radius: 15px; }}\n        ')
        al.addWidget(self.progBar)
        
        self.statsLbl = Label("WORDS: 0  //  PRACTICED: 0")
        self.statsLbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(20, 'normal')}; margin-top: 10px;")
        al.addWidget(self.statsLbl)
        
        leftCol.addWidget(anaF)
        
        # Additional Stat Blocks
        self.statDb = self.CreateStatBlock("◢ DATABASE SYNC", "100%", palette[4 % len(palette)])
        leftCol.addWidget(self.statDb)
        
        leftCol.addStretch()
        self.botElbow = LCARSElbow("bottom-left", palette[0])
        self.botElbow.setMinimumHeight(100)
        leftCol.addWidget(self.botElbow)
        bodyHbox.addLayout(leftCol, 1)
        
        # RIGHT: PRIMARY COMMAND NODES (Grid)
        rightCol = GridLayout()
        rightCol.setSpacing(14)
        
        nodes = [
            ("FLASHCARDS", "exercises", palette[2], 0, 0),
            ("DICTIONARY", "dictionary", palette[1], 0, 1),
            ("READING",    "reading",    palette[3], 1, 0),
            ("TESTS",      "tests",      palette[4 % len(palette)], 1, 1),
        ]
        
        for text, cmd, col, r, c in nodes:
            btn = LCARSButton(text, Color=col)
            btn.setMinimumSize(220, 120)
            btn.setMaximumSize(280, 150)
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 20px; font-weight: normal;")
            btn.Clicked.connect(lambda checked, x=cmd: self.startExercise.emit(x))
            rightCol.addWidget(btn, r, c)
            
        bodyHbox.addLayout(rightCol, 1)
        layout.addLayout(bodyHbox, 1)

    def CreateStatBlock(self, title, val, color):
        f = Frame()
        f.setStyleSheet(f"background: #111; border-left: 8px solid {color}; border-radius: 4px;")
        l = Chassis.Vertical(f)
        t = Label(title)
        t.setStyleSheet(f"color: {color}; {FontStyle(12, 'normal')}")
        v = Label(val)
        v.setStyleSheet(f"color: #FFF; {FontStyle(24, 'normal')}")
        l.addWidget(t)
        l.addWidget(v)
        return f

    def updateData(self):
        val = self.progress.getOverallProgress()
        self.progBar.setValue(int(val))
        self.progLabel.setText(f"COMPLETION: {val:.1f}%")
        stats = self.db.getProgressSummary()
        mp = stats.get('vocabulary', {})
        self.statsLbl.setText(f"WORDS IN DB: {mp.get('total_vocabulary', 0)}   //   PRACTICED: {mp.get('total_practiced', 0)}")

# --- DICTIONARY ---

class DictionaryWidget(LearningStation):
    # Titan-class Dictionary / Database lookup.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        self.currentCategory = "ALL"
        
        self.setStyleSheet("background-color: black;")
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = ResolvePalette(self.theme)
        
        # --- INTERNAL TITAN HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(100)
        headerLay = Chassis.Horizontal(headerFrame)
        headerLay.setContentsMargins(0, 10, 20, 0)
        headerLay.setSpacing(20)

        self.headerElbow = LCARSElbow("top-left", palette[2])
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("LINGUISTIC DATABASE // WORD LOOKUP")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ DATABASE: ONLINE // NEURAL SEARCH ENABLED")
        self.statusLbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[3]), 1)
        layout.addWidget(headerFrame)
        
        # --- SEARCH & ARCHITECTURE ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)
        
        # Left Panel (Search & Categories)
        self.leftPanel = Frame()
        self.leftPanel.setFixedWidth(300)
        self.leftPanel.setStyleSheet("background: transparent; border: none;")
        leftCol = Chassis.Vertical(self.leftPanel)
        leftCol.setContentsMargins(0, 0, 0, 0)
        leftCol.setSpacing(15)
        
        self.catBox = ComboBox()
        self.catBox.addItems(["ALL", "GENERAL", "FAMILY", "WORK", "TRAVEL", "NATURE", "TECHNOLOGY", "FOOD"])
        self.StyleCombo(self.catBox)
        self.catBox.currentTextChanged.connect(self.changeCategory)
        leftCol.addWidget(self.catBox)
        
        self.searchIn = LineEdit()
        self.searchIn.setPlaceholderText("SEARCH...")
        self.searchIn.setStyleSheet(f"background: #111; color: #FFF; border: 1px solid #333; padding: 10px; {FontStyle(18, 'normal')}")
        self.searchIn.textChanged.connect(self.search)
        leftCol.addWidget(self.searchIn)
        
        leftCol.addStretch()
        self.botElbow = LCARSElbow("bottom-left", palette[1])
        self.botElbow.setMinimumHeight(100)
        leftCol.addWidget(self.botElbow)
        bodyHbox.addWidget(self.leftPanel)
        
        # Right: Result Stream
        rightCol = Chassis.Vertical()
        
        self.list = ListWidget()
        self.list.setObjectName("dictionaryList")
        self.list.setStyleSheet(f'\n            #dictionaryList {{ background: transparent; color: #FFF; border: none; outline: none; }}\n            #dictionaryList::item {{ \n                background: #0A0A0A; padding: 15px; border-bottom: 1px solid #222; \n                margin-bottom: 2px; border-left: 5px solid {palette[0]};\n            }}\n            #dictionaryList::item:selected {{ background: {palette[0]}; color: #000; border-left-color: #FFF; }}\n        ')
        self.list.itemClicked.connect(self.playAudio)
        rightCol.addWidget(self.list)
        
        bodyHbox.addLayout(rightCol, 1)
        layout.addLayout(bodyHbox, 1)
        self.search("")

    def StyleCombo(self, box):
        palette = ResolvePalette(self.theme)
        box.setObjectName("stationCombo")
        css = f"\n            #stationCombo {{ \n                padding: 5px 20px; background: #222; color: #FFF; border: none;\n                border-left: 8px solid {palette[1]}; border-radius: 4px;\n                {FontStyle(18, 'normal')} \n            }}\n        "
        box.setStyleSheet(css)

    def changeCategory(self, text):
        self.currentCategory = text
        self.search(self.searchIn.text())

    def search(self, text):
        self.list.clear()
        lvl = self.progress.getCurrentLevel()
        cat = None if self.currentCategory == "ALL" else self.currentCategory.lower()
        
        words = self.db.getRandomWords(level=lvl, category=cat, count=100) if text.strip() == "" else self.db.searchWords(text, category=cat, limit=100)
            
        for w in words:
            en = w.get('English', w.get('english', ''))
            ua = w.get('Ukrainian', w.get('ukrainian', ''))
            wLvl = w.get('Level', w.get('level', 'A1'))
            if ListWidgetItem is None:
                self.list.addItem(f"◢ [{wLvl}]  {en.upper()}   ──   {ua.upper()}")
                continue
            item = ListWidgetItem(f"◢ [{wLvl}]  {en.upper()}   ──   {ua.upper()}")
            item.setData(USER_ROLE, en)
            self.list.addItem(item)
                
    def playAudio(self, item):
        word = item.data(USER_ROLE)
        if word:
            GetSoundManager().PlayAudioClip("click")

# --- EXERCISES (FLASHCARDS) ---

class ExercisesWidget(LearningStation):
    # Titan-class Flashcard Engine.
    def __init__(self, modules, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.modules = modules
        self.progress = progress
        self.era = None
        self.currentWord = None
        self.isFlipped = False
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        
        self.setStyleSheet("background-color: black;")
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = ResolvePalette(self.theme)
        
        # --- INTERNAL TITAN HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(100)
        headerLay = Chassis.Horizontal(headerFrame)
        headerLay.setContentsMargins(0, 10, 20, 0)
        headerLay.setSpacing(20)

        self.headerElbow = LCARSElbow("top-left", palette[0])
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("NEURAL RETRIEVAL // FLASHCARD MATRIX")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ COGNITIVE BUFFER: SYNCING // SESSION READY")
        self.statusLbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[3]), 1)
        layout.addWidget(headerFrame)
        
        # --- MAIN CARD ARCHITECTURE ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)
        
        # Left Panel (Decorative)
        self.leftPanel = Frame()
        self.leftPanel.setFixedWidth(100)
        self.leftCol = Chassis.Vertical(self.leftPanel)
        self.leftCol.addWidget(LCARSSegment(Color=palette[1]), 1)
        bodyHbox.addWidget(self.leftPanel)
        
        # Center: The Card
        cardVbox = Chassis.Vertical()
        self.cardFrame = Frame()
        self.cardFrame.setStyleSheet(f"background-color: #0A0A0A; border: 2px solid #222; border-radius: 10px;")
        self.cardFrame.mousePressEvent = self.flipCard
        
        cardLay = Chassis.Vertical(self.cardFrame)
        self.lblWord = Label("INITIATE SESSION")
        self.lblWord.setStyleSheet(f"color: #FFF; {FontStyle(72, 'normal')}; letter-spacing: 4px;")
        
        self.lblTrans = Label("")
        self.lblTrans.setStyleSheet(f"color: #AAA; {FontStyle(48, 'normal')}")
        
        self.lblExample = Label("")
        self.lblExample.setStyleSheet(f"color: #555; {FontStyle(24, 'normal')}")
        self.lblExample.setWordWrap(True)
        
        cardLay.addStretch(1)
        cardLay.addWidget(self.lblWord)
        cardLay.addWidget(self.lblTrans)
        cardLay.addSpacing(40)
        cardLay.addWidget(self.lblExample)
        cardLay.addStretch(1)
        
        cardVbox.addWidget(self.cardFrame, 1)
        
        # Controls below card
        self.controlsWidget = Widget()
        cl = Chassis.Horizontal(self.controlsWidget)
        cl.setContentsMargins(0, 20, 0, 0)
        cl.setSpacing(20)
        
        self.btnHard = LCARSButton(
            "HARD / REPEAT",
            Color=(palette[5] if len(palette) > 5 else self.theme.get('alert', palette[0])),
        )
        self.btnGood = LCARSButton("GOOD / STABLE", Color=palette[3])
        self.btnEasy = LCARSButton("EASY / MASTERED", Color=palette[1])
        
        for b, s in [(self.btnHard, False), (self.btnGood, True), (self.btnEasy, True)]:
            b.setFixedSize(300, 80)
            b.setStyleSheet(b.styleSheet() + f"{FontStyle(20, 'normal')}")
            b.Clicked.connect(lambda checked, x=s: self.scoreWord(x))
            cl.addWidget(b)
        
        cardVbox.addWidget(self.controlsWidget)
        self.controlsWidget.hide()
        
        # Start button
        self.startBtn = LCARSButton("BEGIN NEURAL RECONSTRUCTION", Color=palette[0])
        self.startBtn.setFixedSize(600, 100)
        self.startBtn.Clicked.connect(self.nextCard)
        cardVbox.addWidget(self.startBtn)
        
        bodyHbox.addLayout(cardVbox, 1)
        
        # Right Panel (Decorative)
        self.rightPanel = Frame()
        self.rightPanel.setFixedWidth(100)
        rightCol = Chassis.Vertical(self.rightPanel)
        rightCol.addWidget(LCARSSegment(Color=palette[2]), 1)
        bodyHbox.addWidget(self.rightPanel)
        
        layout.addLayout(bodyHbox, 1)

    def flipCard(self, a0=None):
        if not self.currentWord: return
        GetSoundManager().PlayAudioClip("click")
        self.isFlipped = not self.isFlipped
        if self.isFlipped:
            ukr = self.currentWord.get('Ukrainian', self.currentWord.get('ukrainian', ''))
            self.lblTrans.setText(f"◤ {ukr.upper()}")
            ex = self.currentWord.get('ExampleSentence', self.currentWord.get('example_sentence', ''))
            if ex:
                self.lblExample.setText(f"EXAMPLE: {ex.upper()}")
            self.controlsWidget.show()
            GetSoundManager().PlayAudioClip("click")
        else:
            self.lblTrans.setText("")
            self.lblExample.setText("")

    def nextCard(self):
        GetSoundManager().PlayAudioClip("click")
        self.startBtn.hide()
        lvl = self.progress.getCurrentLevel()
        ex = self.modules.generateVocabularyExercise(level=lvl, exerciseType='translation')
        if not ex or 'word_data' not in ex:
            self.lblWord.setText("◤ DATABASE EMPTY")
            return
        self.currentWord = ex['word_data']
        self.isFlipped = False
        self.lblWord.setText(self.currentWord.get('English', self.currentWord.get('english', '')).upper())
        self.lblTrans.setText("")
        self.lblExample.setText("")
        self.controlsWidget.hide()

    def scoreWord(self, success):
        if success: GetSoundManager().PlayAudioClip("acknowledge")
        else: GetSoundManager().PlayAudioClip("error")
        if self.currentWord:
            word_id = self.currentWord.get('Id', self.currentWord.get('id'))
            self.modules.db.updateWordProgress('default', word_id, success)
        self.nextCard()

# --- READING ---

class ReadingWidget(LearningStation):
    # Titan-class Reading Comprehension module.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        self.currentText = None
        
        self.setStyleSheet("background-color: black;")
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = ResolvePalette(self.theme)
        
        # --- INTERNAL TITAN HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(100)
        headerLay = Chassis.Horizontal(headerFrame)
        headerLay.setContentsMargins(0, 10, 20, 0)
        headerLay.setSpacing(20)

        self.headerElbow = LCARSElbow("top-left", palette[3])
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("LINGUISTIC ANALYSIS // READING COMPREHENSION")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ TEXT STREAM: ACTIVE // COMPREHENSION MATRIX ENGAGED")
        self.statusLbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[2]), 1)
        layout.addWidget(headerFrame)
        
        # --- MAIN CONTENT ARCHITECTURE ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)
        
        # Left Panel (Controls)
        self.leftPanel = Frame()
        self.leftPanel.setFixedWidth(280)
        leftCol = Chassis.Vertical(self.leftPanel)
        leftCol.setContentsMargins(0, 0, 0, 0)
        leftCol.setSpacing(10)
        
        self.btnAudio = LCARSButton("PLAY AUDIO", Color=palette[1])
        self.btnTrans = LCARSButton("TRANSLATION", Color=palette[3])
        self.btnNext = LCARSButton("NEXT ENTRY", Color=palette[0])
        
        for b in [self.btnAudio, self.btnTrans, self.btnNext]:
            b.setFixedSize(280, 80)
            b.setStyleSheet(b.styleSheet() + f"{FontStyle(20, 'normal')}")
            leftCol.addWidget(b)
            
        self.btnAudio.Clicked.connect(self.playAudio)
        self.btnTrans.Clicked.connect(self.toggleTrans)
        self.btnNext.Clicked.connect(self.loadText)
        
        leftCol.addStretch()
        leftCol.addWidget(LCARSElbow("bottom-left", palette[0]))
        bodyHbox.addWidget(self.leftPanel)
        
        # Right: The Text Hub
        textVbox = Chassis.Vertical()
        self.textScroll = ScrollArea()
        self.textScroll.setWidgetResizable(True)
        self.textScroll.setFrameShape(Frame.Shape.NoFrame)
        self.textScroll.setStyleSheet("background: #050505; border: 1px solid #222; border-radius: 4px;")
        
        self.textPanel = Widget()
        self.textLay = Chassis.Vertical(self.textPanel)
        self.textLay.setContentsMargins(40, 30, 40, 30)
        self.textLay.setSpacing(20)
        
        self.lblTitle = Label("◢ INITIATE TEXT ACQUISITION")
        self.lblTitle.setStyleSheet(f"color: {palette[3]}; {FontStyle(42, 'normal')}; letter-spacing: 2px;")
        self.lblTitle.setWordWrap(True)
        self.textLay.addWidget(self.lblTitle)
        
        self.textLay.addWidget(LCARSSegment(Color=palette[0]))
        
        self.lblEn = Label("")
        self.lblEn.setWordWrap(True)
        self.lblEn.setStyleSheet(f"color: #FFF; {FontStyle(28, 'normal')}; line-height: 150%;")
        self.textLay.addWidget(self.lblEn)
        
        self.lblUa = Label("")
        self.lblUa.setWordWrap(True)
        self.lblUa.setStyleSheet(f"color: #666; {FontStyle(22, 'normal')};")
        self.lblUa.hide()
        self.textLay.addWidget(self.lblUa)
        
        self.textLay.addStretch()
        self.textScroll.setWidget(self.textPanel)
        textVbox.addWidget(self.textScroll)
        
        bodyHbox.addLayout(textVbox, 1)
        layout.addLayout(bodyHbox, 1)
        self.loadText()

    def loadText(self):
        GetSoundManager().PlayAudioClip("click")
        level = self.progress.getCurrentLevel()
        self.currentText = self.db.getMiniText(level)
        if self.currentText:
            self.lblTitle.setText(f"◢ {self.currentText['title'].upper()}")
            self.lblEn.setText(self.currentText['english_text'])
            self.lblUa.setText(self.currentText['translated_text'])
            self.lblUa.hide()
            self.btnTrans.setText("SHOW TRANSLATION")
        else:
            self.lblTitle.setText("◢ DATA UNAVAILABLE")
            self.lblEn.setText("")
            self.lblUa.setText("")

    def playAudio(self):
        if self.currentText:
            GetSoundManager().PlayAudioClip("click")

    def toggleTrans(self):
        GetSoundManager().PlayAudioClip("click")
        isHidden = self.lblUa.isHidden()
        self.lblUa.setHidden(not isHidden)
        self.btnTrans.setText("HIDE TRANSLATION" if isHidden else "SHOW TRANSLATION")

# --- TESTS ---

class TestWidget(LearningStation):
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        self.questions = []
        self.currentIndex = 0
        self.score = 0
        
        self.setStyleSheet("background-color: black;")
        layout = Chassis.Vertical(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = ResolvePalette(self.theme)
        
        # --- INTERNAL TITAN HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(100)
        headerLay = Chassis.Horizontal(headerFrame)
        headerLay.setContentsMargins(0, 10, 20, 0)
        headerLay.setSpacing(20)

        self.headerElbow = LCARSElbow("top-left", palette[4 % len(palette)])
        self.headerElbow.setMinimumSize(320, 100)
        headerLay.addWidget(self.headerElbow)

        titleLay = Chassis.Vertical()
        titleLbl = Label("ASSESSMENT MATRIX // NEURAL VALIDATION")
        titleLbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        titleLay.addWidget(titleLbl)
        
        self.statusLbl = Label("◢ COGNITIVE EVALUATION: WAITING // LINK READY")
        self.statusLbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        titleLay.addWidget(self.statusLbl)
        headerLay.addLayout(titleLay, 1)

        headerLay.addWidget(LCARSSegment(Color=palette[2]), 1)
        layout.addWidget(headerFrame)
        
        # --- MAIN ASSESSMENT ARCHITECTURE ---
        bodyHbox = Chassis.Horizontal()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(20)
        
        # Left Panel (Progress Indicators)
        self.leftPanel = Frame()
        self.leftPanel.setFixedWidth(200)
        self.leftCol = Chassis.Vertical(self.leftPanel)
        self.leftCol.setContentsMargins(0, 0, 0, 0)
        self.leftCol.setSpacing(10)
        
        self.indicatorLay = Chassis.Vertical()
        self.indicatorLay.setSpacing(5)
        self.leftCol.addLayout(self.indicatorLay)
        
        self.leftCol.addStretch()
        self.botElbow = LCARSElbow("bottom-left", palette[0])
        self.botElbow.setMinimumHeight(100)
        self.leftCol.addWidget(self.botElbow)
        bodyHbox.addWidget(self.leftPanel)
        
        # Center: The Evaluation Chamber
        evalVbox = Chassis.Vertical()
        evalVbox.setSpacing(20)
        
        self.questionCard = Frame()
        self.questionCard.setStyleSheet("background: #080808; border: 1px solid #222; border-radius: 4px;")
        questionCardLayout = Chassis.Vertical(self.questionCard)
        questionCardLayout.setContentsMargins(40, 40, 40, 40)
        
        self.questionLabel = Label("◢ INITIATE NEURAL VALIDATION PROTOCOL")
        self.questionLabel.setStyleSheet(f"color: #FFF; {FontStyle(32, 'normal')}; letter-spacing: 1px;")
        self.questionLabel.setWordWrap(True)
        questionCardLayout.addWidget(self.questionLabel)
        
        # Question Divider
        questionCardLayout.addWidget(LCARSSegment(Color=palette[1]))
        
        self.optionsLayout = GridLayout()
        self.optionsLayout.setSpacing(15)
        self.optBtns = []
        for i in range(4):
            btn = LCARSButton(f"OPTION {chr(65+i)}", Color=palette[i%len(palette)])
            btn.setFixedSize(400, 100)
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 20px; font-weight: normal;")
            btn.Clicked.connect(lambda checked, idx=i: self.checkAnswer(idx))
            self.optBtns.append(btn)
            self.optionsLayout.addWidget(btn, i // 2, i % 2)
            btn.hide()
            
        questionCardLayout.addLayout(self.optionsLayout)
        evalVbox.addWidget(self.questionCard, 1)
        
        # Result Overlay
        self.resLbl = Label("")
        self.resLbl.setStyleSheet(f"{FontStyle(24, 'normal')}")
        evalVbox.addWidget(self.resLbl)
        
        # Control Nodes
        ctrlLay = Chassis.Horizontal()
        self.btnStart = LCARSButton("BEGIN EVALUATION", Color=palette[0])
        self.btnStart.setFixedSize(400, 80)
        self.btnStart.Clicked.connect(self.startTest)
        ctrlLay.addWidget(self.btnStart)
        
        self.btnNext = LCARSButton("NEXT PHASE", Color=palette[2])
        self.btnNext.setFixedSize(400, 80)
        self.btnNext.Clicked.connect(self.nextQ)
        self.btnNext.hide()
        ctrlLay.addWidget(self.btnNext)
        
        evalVbox.addLayout(ctrlLay)
        bodyHbox.addLayout(evalVbox, 3)
        
        # Right: Metrics readout
        self.rightPanel = Frame()
        self.rightPanel.setFixedWidth(200)
        self.rightCol = Chassis.Vertical(self.rightPanel)
        self.metricsLbl = Label("SCORE: 0\nACCURACY: 0%")
        self.metricsLbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(18, 'normal')}; border-left: 2px solid #333; padding-left: 10px;")
        self.rightCol.addWidget(self.metricsLbl)
        self.rightCol.addStretch()
        bodyHbox.addWidget(self.rightPanel)
        
        layout.addLayout(bodyHbox, 1)

    def startTest(self):
        GetSoundManager().PlayAudioClip("click")
        level = self.progress.getCurrentLevel()
        self.questions = self.db.getTestQuestions(level, count=5)
        if not self.questions:
            self.questionLabel.setText("◢ DATASTREAM EMPTY")
            return
        self.currentIndex = 0
        self.score = 0
        self.btnStart.hide()
        for btn in self.optBtns: btn.show()
        self.UpdateProgressIndicators()
        self.showQuestion()

    def UpdateProgressIndicators(self):
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        while self.indicatorLay.count():
            item = self.indicatorLay.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()
        for i in range(len(self.questions)):
            color = palette[1] if i == self.currentIndex else "#333" if i > self.currentIndex else palette[0]
            ind = LCARSSegment(Color=color)
            ind.setFixedHeight(10)
            self.indicatorLay.addWidget(ind)

    def showQuestion(self):
        if self.currentIndex >= len(self.questions):
            self.finishTest()
            return
        GetSoundManager().PlayAudioClip("click")
        self.UpdateProgressIndicators()
        questionRow = self.questions[self.currentIndex]
        questionText = str(questionRow.get('question', questionRow.get('Question', '')))
        self.questionLabel.setText(f"◢ EVALUATION PHASE {self.currentIndex + 1}:\n{questionText.upper()}")
        optionTexts = [
            str(questionRow.get('option_a', questionRow.get('OptionA', ''))),
            str(questionRow.get('option_b', questionRow.get('OptionB', ''))),
            str(questionRow.get('option_c', questionRow.get('OptionC', ''))),
            str(questionRow.get('option_d', questionRow.get('OptionD', ''))),
        ]
        for i, optionText in enumerate(optionTexts):
            self.optBtns[i].setText(f"{chr(65+i)}) {optionText.upper()}")
            self.optBtns[i].setEnabled(True)
        self.resLbl.setText("")
        self.btnNext.hide()

    def checkAnswer(self, idx):
        questionRow = self.questions[self.currentIndex]
        correctOption = str(questionRow.get('correct_option', questionRow.get('CorrectOption', ''))).upper()
        isCorrect = chr(65 + idx) == correctOption
        if isCorrect:
            self.score += 1
            GetSoundManager().PlayAudioClip("acknowledge")
            self.resLbl.setText("◢ NEURAL LINK ESTABLISHED: CORRECT")
            self.resLbl.setStyleSheet("color: #00FF00;")
        else:
            GetSoundManager().PlayAudioClip("error")
            self.resLbl.setText(f"◢ DATA CORRUPTION: INCORRECT // WAS {correctOption}")
            self.resLbl.setStyleSheet("color: #FF3333;")
        
        for b in self.optBtns: b.setEnabled(False)
        self.btnNext.show()
        self.UpdateMetrics()

    def UpdateMetrics(self):
        acc = (self.score / (self.currentIndex + 1)) * 100
        self.metricsLbl.setText(f"SCORE: {self.score}\nACCURACY: {acc:.0f}%")

    def nextQ(self):
        self.currentIndex += 1
        self.showQuestion()

    def finishTest(self):
        self.questionLabel.setText(f"◢ EVALUATION COMPLETE\nFINAL SCORE: {self.score} / {len(self.questions)}")
        for btn in self.optBtns: btn.hide()
        self.btnNext.hide()
        self.btnStart.show()
        self.btnStart.setText("RESTART EVALUATION")
        