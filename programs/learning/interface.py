from programs.learning.ui.interface import *

# Deprecated root-level compatibility module.
# The real learning UI implementation now lives in programs.learning.ui.interface.

def create_lcars_header(self, title_text, layout, color_idx=0):
    # Use this for subtitles.
    title = Label(title_text.upper())
    title.setStyleSheet(f"color: {self.theme['palette'][color_idx]}; {FontStyle(42, 'normal')}; letter-spacing: 2px;")
    title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    title.setContentsMargins(20, 10, 20, 20)
    layout.addWidget(title)
    return title

# --- LEVEL SELECTOR ---

class LevelSelectorWidget(LCARSStationWidget):
    level_selected = pyqtSignal(str)
    
    def __init__(self, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        
        layout = VBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = Label("SELECT LINGUISTIC PROTOCOL LEVEL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {self.theme['accent']}; {FontStyle(56, 'normal')}")
        layout.addWidget(title)
        layout.addSpacing(60)
        
        grid_lay = VBoxLayout()
        grid_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_lay.setSpacing(30)
        
        levels = [("A1 - BEGINNER", "A1"), ("A2 - ELEMENTARY", "A2"), 
                  ("B1 - INTERMEDIATE", "B1"), ("B2 - UPPER INTERMEDIATE", "B2"),
                  ("C1 - ADVANCED", "C1"), ("C2 - PROFICIENT", "C2")]
                  
        row_lay = HBoxLayout()
        row_lay.setSpacing(40)
        row_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grid_lay.addLayout(row_lay)
        for i, (name, val) in enumerate(levels):
            if i % 2 == 0:
                row_lay = HBoxLayout()
                row_lay.setSpacing(40)
                row_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                grid_lay.addLayout(row_lay)
                
            btn = LCARSButton(name, "none", self.theme['palette'][i % len(self.theme['palette'])], radius=4)
            btn.setFixedSize(600, 140)
            btn.setStyleSheet(btn.styleSheet() + f"{FontStyle(36, 'normal')}")
            btn.clicked.connect(lambda checked, v=val: self.level_selected.emit(v))
            row_lay.addWidget(btn)
            
        layout.addLayout(grid_lay)

# --- DASHBOARD ---

class DashboardWidget(LCARSStationWidget):
    # Titan-class Dashboard for the Linguistic Matrix. Displays mission progress and primary command nodes.
    start_exercise = pyqtSignal(str)
    
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        
        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- INTERNAL TITAN HEADER ---
        header_frame = Frame()
        header_frame.setMinimumHeight(100)
        header_lay = HBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 10, 20, 0)
        header_lay.setSpacing(20)

        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        self.header_elbow = LCARSElbow("top-left", palette[1])
        self.header_elbow.setMinimumSize(320, 100)
        header_lay.addWidget(self.header_elbow)

        title_lay = VBoxLayout()
        title_lbl = Label("MAIN MATRIX DASHBOARD // V5.0")
        title_lbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        title_lay.addWidget(title_lbl)
        
        self.status_lbl = Label("◢ LINGUISTIC ENGINE: READY // NEURAL LINK STABLE")
        self.status_lbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(16, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)

        header_lay.addWidget(LCARSSegment(ColorHexStr=palette[3]), 1)
        layout.addWidget(header_frame)
        
        # --- DASHBOARD ARCHITECTURE ---
        body_hbox = HBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(20)
        
        # LEFT: PROGRESS & METRICS
        left_col = VBoxLayout()
        left_col.setSpacing(20)
        
        # Large Analytics Block
        ana_f = Frame()
        ana_f.setStyleSheet(f"background: rgba(255,255,255,0.05); border-left: 15px solid {palette[0]}; border-radius: 4px;")
        al = VBoxLayout(ana_f)
        al.setContentsMargins(30, 20, 30, 20)
        
        self.prog_label = Label("COMPLETION: 0%")
        self.prog_label.setStyleSheet(f"color: #FFF; {FontStyle(36, 'normal')}")
        al.addWidget(self.prog_label)
        
        self.prog_bar = ProgressBar()
        self.prog_bar.setFixedHeight(30)
        self.prog_bar.setStyleSheet(f"""
            QProgressBar {{ border: 1px solid #333; background: #111; border-radius: 15px; text-align: center; color: transparent; }}
            QProgressBar::chunk {{ background: {palette[2]}; border-radius: 15px; }}
        """)
        al.addWidget(self.prog_bar)
        
        self.stats_lbl = Label("WORDS: 0  //  PRACTICED: 0")
        self.stats_lbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(20, 'normal')}; margin-top: 10px;")
        al.addWidget(self.stats_lbl)
        
        left_col.addWidget(ana_f)
        
        # Additional Stat Blocks
        self.stat_db = self.CreateStatBlock("◢ DATABASE SYNC", "100%", palette[4 % len(palette)])
        left_col.addWidget(self.stat_db)
        
        left_col.addStretch()
        self.bot_elbow = LCARSElbow("bottom-left", palette[0])
        self.bot_elbow.setMinimumHeight(100)
        left_col.addWidget(self.bot_elbow)
        body_hbox.addLayout(left_col, 1)
        
        # RIGHT: PRIMARY COMMAND NODES (Grid)
        right_col = GridLayout()
        right_col.setSpacing(14)
        
        nodes = [
            ("FLASHCARDS", "exercises", palette[2], 0, 0),
            ("DICTIONARY", "dictionary", palette[1], 0, 1),
            ("READING",    "reading",    palette[3], 1, 0),
            ("TESTS",      "tests",      palette[4 % len(palette)], 1, 1),
        ]
        
        for text, cmd, col, r, c in nodes:
            btn = LCARSButton(text, "none", col, radius=4)
            btn.setMinimumSize(220, 120)
            btn.setMaximumSize(280, 150)
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 20px; font-weight: normal;")
            btn.clicked.connect(lambda checked, x=cmd: self.start_exercise.emit(x))
            right_col.addWidget(btn, r, c)
            
        body_hbox.addLayout(right_col, 1)
        layout.addLayout(body_hbox, 1)

    def CreateStatBlock(self, title, val, color):
        f = Frame()
        f.setStyleSheet(f"background: #111; border-left: 8px solid {color}; border-radius: 4px;")
        l = VBoxLayout(f)
        t = Label(title)
        t.setStyleSheet(f"color: {color}; {FontStyle(12, 'normal')}")
        v = Label(val)
        v.setStyleSheet(f"color: #FFF; {FontStyle(24, 'normal')}")
        l.addWidget(t)
        l.addWidget(v)
        return f

    def update_data(self):
        val = self.progress.get_overall_progress()
        self.prog_bar.setValue(int(val))
        self.prog_label.setText(f"COMPLETION: {val:.1f}%")
        stats = self.db.get_progress_summary()
        mp = stats.get('vocabulary', {})
        self.stats_lbl.setText(f"WORDS IN DB: {mp.get('total_vocabulary', 0)}   //   PRACTICED: {mp.get('total_practiced', 0)}")

# --- DICTIONARY ---

class DictionaryWidget(LCARSStationWidget):
    # Titan-class Dictionary / Database lookup.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        self.current_category = "ALL"
        
        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        # --- INTERNAL TITAN HEADER ---
        header_frame = Frame()
        header_frame.setMinimumHeight(100)
        header_lay = HBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 10, 20, 0)
        header_lay.setSpacing(20)

        self.header_elbow = LCARSElbow("top-left", palette[2])
        self.header_elbow.setMinimumSize(320, 100)
        header_lay.addWidget(self.header_elbow)

        title_lay = VBoxLayout()
        title_lbl = Label("LINGUISTIC DATABASE // WORD LOOKUP")
        title_lbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        title_lay.addWidget(title_lbl)
        
        self.status_lbl = Label("◢ DATABASE: ONLINE // NEURAL SEARCH ENABLED")
        self.status_lbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)

        header_lay.addWidget(LCARSSegment(ColorHexStr=palette[3]), 1)
        layout.addWidget(header_frame)
        
        # --- SEARCH & ARCHITECTURE ---
        body_hbox = HBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(20)
        
        # Left Panel (Search & Categories)
        self.left_panel = Frame()
        self.left_panel.setFixedWidth(300)
        self.left_panel.setStyleSheet("background: transparent; border: none;")
        left_col = VBoxLayout(self.left_panel)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(15)
        
        self.cat_box = ComboBox()
        self.cat_box.addItems(["ALL", "GENERAL", "FAMILY", "WORK", "TRAVEL", "NATURE", "TECHNOLOGY", "FOOD"])
        self.StyleCombo(self.cat_box)
        self.cat_box.currentTextChanged.connect(self.change_category)
        left_col.addWidget(self.cat_box)
        
        self.search_in = LineEdit()
        self.search_in.setPlaceholderText("SEARCH...")
        self.search_in.setStyleSheet(f"background: #111; color: #FFF; border: 1px solid #333; padding: 10px; {FontStyle(18, 'normal')}")
        self.search_in.textChanged.connect(self.search)
        left_col.addWidget(self.search_in)
        
        left_col.addStretch()
        self.bot_elbow = LCARSElbow("bottom-left", palette[1])
        self.bot_elbow.setMinimumHeight(100)
        left_col.addWidget(self.bot_elbow)
        body_hbox.addWidget(self.left_panel)
        
        # Right: Result Stream
        right_col = VBoxLayout()
        
        self.list = ListWidget()
        self.list.setStyleSheet(f"""
            QListWidget {{ background: transparent; color: #FFF; border: none; outline: none; }}
            QListWidget::item {{ 
                background: #0A0A0A; padding: 15px; border-bottom: 1px solid #222; 
                margin-bottom: 2px; border-left: 5px solid {palette[0]};
            }}
            QListWidget::item:selected {{ background: {palette[0]}; color: #000; border-left-color: #FFF; }}
        """)
        self.list.itemClicked.connect(self.play_audio)
        right_col.addWidget(self.list)
        
        body_hbox.addLayout(right_col, 1)
        layout.addLayout(body_hbox, 1)
        self.search("")

    def StyleCombo(self, box):
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        css = f"""
            QComboBox {{ 
                padding: 5px 20px; background: #222; color: #FFF; border: none;
                border-left: 8px solid {palette[1]}; border-radius: 4px;
                {FontStyle(18, 'normal')} 
            }}
            QComboBox::drop-down {{ border: none; width: 0px; }}
            QComboBox QAbstractItemView {{ background: #111; color: #FFF; selection-background-color: {palette[0]}; }}
        """
        box.setStyleSheet(css)

    def change_category(self, text):
        self.current_category = text
        self.search(self.search_in.text())

    def search(self, text):
        self.list.clear()
        lvl = self.progress.get_current_level()
        cat = None if self.current_category == "ALL" else self.current_category.lower()
        
        words = self.db.get_random_words(level=lvl, category=cat, count=100) if text.strip() == "" else self.db.search_words(text, category=cat, limit=100)
            
        for w in words:
            en, ua, w_lvl = w.get('english', ''), w.get('ukrainian', ''), w.get('level', 'A1')
            item = ListWidgetItem(f"◢ [{w_lvl}]  {en.upper()}   ──   {ua.upper()}")
            item.setData(Qt.ItemDataRole.UserRole, en)
            item.setFont(Font("Swiss911 UCm BT", 18))
            self.list.addItem(item)
                
    def play_audio(self, item):
        word = item.data(Qt.ItemDataRole.UserRole)
        if word:
            GetSoundManager().PlayAudioClip("click")

# --- EXERCISES (FLASHCARDS) ---

class ExercisesWidget(LCARSStationWidget):
    # Titan-class Flashcard Engine.
    def __init__(self, modules, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.modules = modules
        self.progress = progress
        self.era = None
        self.current_word = None
        self.is_flipped = False
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        
        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        # --- INTERNAL TITAN HEADER ---
        header_frame = Frame()
        header_frame.setMinimumHeight(100)
        header_lay = HBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 10, 20, 0)
        header_lay.setSpacing(20)

        self.header_elbow = LCARSElbow("top-left", palette[0])
        self.header_elbow.setMinimumSize(320, 100)
        header_lay.addWidget(self.header_elbow)

        title_lay = VBoxLayout()
        title_lbl = Label("NEURAL RETRIEVAL // FLASHCARD MATRIX")
        title_lbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        title_lay.addWidget(title_lbl)
        
        self.status_lbl = Label("◢ COGNITIVE BUFFER: SYNCING // SESSION READY")
        self.status_lbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(16, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)

        header_lay.addWidget(LCARSSegment(ColorHexStr=palette[3]), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN CARD ARCHITECTURE ---
        body_hbox = HBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(20)
        
        # Left Panel (Decorative)
        self.left_panel = Frame()
        self.left_panel.setFixedWidth(100)
        self.left_col = VBoxLayout(self.left_panel)
        self.left_col.addWidget(LCARSSegment(ColorHexStr=palette[1]), 1)
        body_hbox.addWidget(self.left_panel)
        
        # Center: The Card
        card_vbox = VBoxLayout()
        self.card_frame = Frame()
        self.card_frame.setStyleSheet(f"background-color: #0A0A0A; border: 2px solid #222; border-radius: 10px;")
        self.card_frame.setCursor(Cursor(Qt.CursorShape.PointingHandCursor))
        self.card_frame.mousePressEvent = self.flip_card
        
        card_lay = VBoxLayout(self.card_frame)
        self.lbl_word = Label("INITIATE SESSION")
        self.lbl_word.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_word.setStyleSheet(f"color: #FFF; {FontStyle(72, 'normal')}; letter-spacing: 4px;")
        
        self.lbl_trans = Label("")
        self.lbl_trans.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_trans.setStyleSheet(f"color: #AAA; {FontStyle(48, 'normal')}")
        
        self.lbl_example = Label("")
        self.lbl_example.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_example.setStyleSheet(f"color: #555; {FontStyle(24, 'normal')}")
        self.lbl_example.setWordWrap(True)
        
        card_lay.addStretch(1)
        card_lay.addWidget(self.lbl_word)
        card_lay.addWidget(self.lbl_trans)
        card_lay.addSpacing(40)
        card_lay.addWidget(self.lbl_example)
        card_lay.addStretch(1)
        
        card_vbox.addWidget(self.card_frame, 1)
        
        # Controls below card
        self.controls_widget = Widget()
        cl = HBoxLayout(self.controls_widget)
        cl.setContentsMargins(0, 20, 0, 0)
        cl.setSpacing(20)
        
        self.btn_hard = LCARSButton("HARD / REPEAT", "none", "none", "none", palette[5] if len(palette)>5 else "#CC3333")
        self.btn_good = LCARSButton("GOOD / STABLE", "none", "none", "none", palette[3])
        self.btn_easy = LCARSButton("EASY / MASTERED", "none", "none", "none", palette[1])
        
        for b, s in [(self.btn_hard, False), (self.btn_good, True), (self.btn_easy, True)]:
            b.setFixedSize(300, 80)
            b.setStyleSheet(b.styleSheet() + f"{FontStyle(20, 'normal')}")
            b.clicked.connect(lambda checked, x=s: self.score_word(x))
            cl.addWidget(b)
        
        card_vbox.addWidget(self.controls_widget)
        self.controls_widget.hide()
        
        # Start button
        self.start_btn = LCARSButton("BEGIN NEURAL RECONSTRUCTION", "none", "none", "none", palette[0])
        self.start_btn.setFixedSize(600, 100)
        self.start_btn.clicked.connect(self.next_card)
        card_vbox.addWidget(self.start_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        body_hbox.addLayout(card_vbox, 1)
        
        # Right Panel (Decorative)
        self.right_panel = Frame()
        self.right_panel.setFixedWidth(100)
        right_col = VBoxLayout(self.right_panel)
        right_col.addWidget(LCARSSegment(ColorHexStr=palette[2]), 1)
        body_hbox.addWidget(self.right_panel)
        
        layout.addLayout(body_hbox, 1)

    def flip_card(self, a0=None):
        if not self.current_word: return
        GetSoundManager().PlayAudioClip("click")
        self.is_flipped = not self.is_flipped
        if self.is_flipped:
            self.lbl_trans.setText(f"◤ {self.current_word['ukrainian'].upper()}")
            ex = self.current_word.get('example_sentence', '')
            if ex: self.lbl_example.setText(f"EXAMPLE: {ex.upper()}")
            self.controls_widget.show()
            GetSoundManager().PlayAudioClip("click")
        else:
            self.lbl_trans.setText("")
            self.lbl_example.setText("")

    def next_card(self):
        GetSoundManager().PlayAudioClip("click")
        self.start_btn.hide()
        lvl = self.progress.get_current_level()
        ex = self.modules.generate_vocabulary_exercise(level=lvl, exercise_type='translation')
        if not ex or 'word_data' not in ex:
            self.lbl_word.setText("◤ DATABASE EMPTY")
            return
        self.current_word = ex['word_data']
        self.is_flipped = False
        self.lbl_word.setText(self.current_word['english'].upper())
        self.lbl_trans.setText("")
        self.lbl_example.setText("")
        self.controls_widget.hide()

    def score_word(self, success):
        if success: GetSoundManager().PlayAudioClip("acknowledge")
        else: GetSoundManager().PlayAudioClip("error")
        if self.current_word:
            self.modules.db.update_word_progress('default', self.current_word['id'], success)
        self.next_card()

# --- READING ---

class ReadingWidget(LCARSStationWidget):
    # Titan-class Reading Comprehension module.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        # QTextToSpeech removed; use sound manager for audio feedback
        self.tts = None
        self.current_text = None
        
        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        # --- INTERNAL TITAN HEADER ---
        header_frame = Frame()
        header_frame.setMinimumHeight(100)
        header_lay = HBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 10, 20, 0)
        header_lay.setSpacing(20)

        self.header_elbow = LCARSElbow("top-left", palette[3])
        self.header_elbow.setMinimumSize(320, 100)
        header_lay.addWidget(self.header_elbow)

        title_lay = VBoxLayout()
        title_lbl = Label("LINGUISTIC ANALYSIS // READING COMPREHENSION")
        title_lbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        title_lay.addWidget(title_lbl)
        
        self.status_lbl = Label("◢ TEXT STREAM: ACTIVE // COMPREHENSION MATRIX ENGAGED")
        self.status_lbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)

        header_lay.addWidget(LCARSSegment(ColorHexStr=palette[2]), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN CONTENT ARCHITECTURE ---
        body_hbox = HBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(20)
        
        # Left Panel (Controls)
        self.left_panel = Frame()
        self.left_panel.setFixedWidth(280)
        left_col = VBoxLayout(self.left_panel)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(10)
        
        self.btn_audio = LCARSButton("PLAY AUDIO", "none", "none", "none", palette[1])
        self.btn_trans = LCARSButton("TRANSLATION", "none", "none", "none", palette[3])
        self.btn_next = LCARSButton("NEXT ENTRY", "none", "none", "none", palette[0])
        
        for b in [self.btn_audio, self.btn_trans, self.btn_next]:
            b.setFixedSize(280, 80)
            b.setStyleSheet(b.styleSheet() + f"{FontStyle(20, 'normal')}")
            left_col.addWidget(b)
            
        self.btn_audio.clicked.connect(self.play_audio)
        self.btn_trans.clicked.connect(self.toggle_trans)
        self.btn_next.clicked.connect(self.load_text)
        
        left_col.addStretch()
        left_col.addWidget(LCARSElbow("bottom-left", palette[0]))
        body_hbox.addWidget(self.left_panel)
        
        # Right: The Text Hub
        text_vbox = VBoxLayout()
        self.text_scroll = ScrollArea()
        self.text_scroll.setWidgetResizable(True)
        self.text_scroll.setFrameShape(Frame.Shape.NoFrame)
        self.text_scroll.setStyleSheet("background: #050505; border: 1px solid #222; border-radius: 4px;")
        
        self.text_panel = Widget()
        self.text_lay = VBoxLayout(self.text_panel)
        self.text_lay.setContentsMargins(40, 30, 40, 30)
        self.text_lay.setSpacing(20)
        
        self.lbl_title = Label("◢ INITIATE TEXT ACQUISITION")
        self.lbl_title.setStyleSheet(f"color: {palette[3]}; {FontStyle(42, 'normal')}; letter-spacing: 2px;")
        self.lbl_title.setWordWrap(True)
        self.text_lay.addWidget(self.lbl_title)
        
        self.text_lay.addWidget(LCARSSegment(ColorHexStr=palette[0]))
        
        self.lbl_en = Label("")
        self.lbl_en.setWordWrap(True)
        self.lbl_en.setStyleSheet(f"color: #FFF; {FontStyle(28, 'normal')}; line-height: 150%;")
        self.text_lay.addWidget(self.lbl_en)
        
        self.lbl_ua = Label("")
        self.lbl_ua.setWordWrap(True)
        self.lbl_ua.setStyleSheet(f"color: #666; {FontStyle(22, 'normal')};")
        self.lbl_ua.hide()
        self.text_lay.addWidget(self.lbl_ua)
        
        self.text_lay.addStretch()
        self.text_scroll.setWidget(self.text_panel)
        text_vbox.addWidget(self.text_scroll)
        
        body_hbox.addLayout(text_vbox, 1)
        layout.addLayout(body_hbox, 1)
        self.load_text()

    def load_text(self):
        GetSoundManager().PlayAudioClip("click")
        level = self.progress.get_current_level()
        self.current_text = self.db.get_mini_text(level)
        if self.current_text:
            self.lbl_title.setText(f"◢ {self.current_text['title'].upper()}")
            self.lbl_en.setText(self.current_text['english_text'])
            self.lbl_ua.setText(self.current_text['translated_text'])
            self.lbl_ua.hide()
            self.btn_trans.setText("SHOW TRANSLATION")
        else:
            self.lbl_title.setText("◢ DATA UNAVAILABLE")

    def play_audio(self):
        if self.current_text: GetSoundManager().PlayAudioClip("click")

    def toggle_trans(self):
        GetSoundManager().PlayAudioClip("click")
        is_hidden = self.lbl_ua.isHidden()
        self.lbl_ua.setHidden(not is_hidden)
        self.btn_trans.setText("HIDE TRANSLATION" if is_hidden else "SHOW TRANSLATION")

# --- TESTS ---

class TestWidget(LCARSStationWidget):
    # Titan-class Assessment Matrix.
    def __init__(self, db, progress, theme, faction, parent=None):
        super().__init__(theme, faction, parent)
        self.db = db
        self.progress = progress
        self.era = None
        self.questions = []
        self.current_index = 0
        self.score = 0
        
        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        
        # --- INTERNAL TITAN HEADER ---
        header_frame = Frame()
        header_frame.setMinimumHeight(100)
        header_lay = HBoxLayout(header_frame)
        header_lay.setContentsMargins(0, 10, 20, 0)
        header_lay.setSpacing(20)

        self.header_elbow = LCARSElbow("top-left", palette[4 % len(palette)])
        self.header_elbow.setMinimumSize(320, 100)
        header_lay.addWidget(self.header_elbow)

        title_lay = VBoxLayout()
        title_lbl = Label("ASSESSMENT MATRIX // NEURAL VALIDATION")
        title_lbl.setStyleSheet(f"color: {palette[0]}; {FontStyle(32, 'normal')}; letter-spacing: 2px;")
        title_lay.addWidget(title_lbl)
        
        self.status_lbl = Label("◢ COGNITIVE EVALUATION: WAITING // LINK READY")
        self.status_lbl.setStyleSheet(f"color: {palette[1]}; {FontStyle(16, 'normal')};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)

        header_lay.addWidget(LCARSSegment(ColorHexStr=palette[2]), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN ASSESSMENT ARCHITECTURE ---
        body_hbox = HBoxLayout()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(20)
        
        # Left Panel (Progress Indicators)
        self.left_panel = Frame()
        self.left_panel.setFixedWidth(200)
        self.left_col = VBoxLayout(self.left_panel)
        self.left_col.setContentsMargins(0, 0, 0, 0)
        self.left_col.setSpacing(10)
        
        self.indicator_lay = VBoxLayout()
        self.indicator_lay.setSpacing(5)
        self.left_col.addLayout(self.indicator_lay)
        
        self.left_col.addStretch()
        self.bot_elbow = LCARSElbow("bottom-left", palette[0])
        self.bot_elbow.setMinimumHeight(100)
        self.left_col.addWidget(self.bot_elbow)
        body_hbox.addWidget(self.left_panel)
        
        # Center: The Evaluation Chamber
        eval_vbox = VBoxLayout()
        eval_vbox.setSpacing(20)
        
        self.q_card = Frame()
        self.q_card.setStyleSheet("background: #080808; border: 1px solid #222; border-radius: 4px;")
        ql = VBoxLayout(self.q_card)
        ql.setContentsMargins(40, 40, 40, 40)
        
        self.q_lbl = Label("◢ INITIATE NEURAL VALIDATION PROTOCOL")
        self.q_lbl.setStyleSheet(f"color: #FFF; {FontStyle(32, 'normal')}; letter-spacing: 1px;")
        self.q_lbl.setWordWrap(True)
        ql.addWidget(self.q_lbl)
        
        # Question Divider
        ql.addWidget(LCARSSegment(ColorHexStr=palette[1]))
        
        self.opts_lay = GridLayout()
        self.opts_lay.setSpacing(15)
        self.opt_btns = []
        for i in range(4):
            btn = LCARSButton(f"OPTION {chr(65+i)}", "none", "none", "none", palette[i%len(palette)], radius=4)
            btn.setFixedSize(400, 100)
            btn.setStyleSheet(btn.styleSheet() + f"font-size: 20px; font-weight: normal;")
            btn.clicked.connect(lambda checked, idx=i: self.check_answer(idx))
            self.opt_btns.append(btn)
            self.opts_lay.addWidget(btn, i // 2, i % 2)
            btn.hide()
            
        ql.addLayout(self.opts_lay)
        eval_vbox.addWidget(self.q_card, 1)
        
        # Result Overlay
        self.res_lbl = Label("")
        self.res_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.res_lbl.setStyleSheet(f"{FontStyle(24, 'normal')}")
        eval_vbox.addWidget(self.res_lbl)
        
        # Control Nodes
        ctrl_lay = HBoxLayout()
        self.btn_start = LCARSButton("BEGIN EVALUATION", "none", "none", "none", palette[0])
        self.btn_start.setFixedSize(400, 80)
        self.btn_start.clicked.connect(self.start_test)
        ctrl_lay.addWidget(self.btn_start, 0, Qt.AlignmentFlag.AlignCenter)
        
        self.btn_next = LCARSButton("NEXT PHASE", "none", "none", "none", palette[2])
        self.btn_next.setFixedSize(400, 80)
        self.btn_next.clicked.connect(self.next_q)
        self.btn_next.hide()
        ctrl_lay.addWidget(self.btn_next, 0, Qt.AlignmentFlag.AlignCenter)
        
        eval_vbox.addLayout(ctrl_lay)
        body_hbox.addLayout(eval_vbox, 3)
        
        # Right: Metrics readout
        self.right_panel = Frame()
        self.right_panel.setFixedWidth(200)
        self.right_col = VBoxLayout(self.right_panel)
        self.metrics_lbl = Label("SCORE: 0\nACCURACY: 0%")
        self.metrics_lbl.setStyleSheet(f"color: {palette[2]}; {FontStyle(18, 'normal')}; border-left: 2px solid #333; padding-left: 10px;")
        self.right_col.addWidget(self.metrics_lbl)
        self.right_col.addStretch()
        body_hbox.addWidget(self.right_panel)
        
        layout.addLayout(body_hbox, 1)

    def start_test(self):
        GetSoundManager().PlayAudioClip("click")
        level = self.progress.get_current_level()
        self.questions = self.db.get_test_questions(level, count=5)
        if not self.questions:
            self.q_lbl.setText("◢ DATASTREAM EMPTY")
            return
        self.current_index = 0
        self.score = 0
        self.btn_start.hide()
        for btn in self.opt_btns: btn.show()
        self.UpdateProgressIndicators()
        self.show_question()

    def UpdateProgressIndicators(self):
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        while self.indicator_lay.count():
            item = self.indicator_lay.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()
        for i in range(len(self.questions)):
            color = palette[1] if i == self.current_index else "#333" if i > self.current_index else palette[0]
            ind = LCARSSegment(ColorHexStr=color)
            ind.setFixedHeight(10)
            self.indicator_lay.addWidget(ind)

    def show_question(self):
        if self.current_index >= len(self.questions):
            self.finish_test()
            return
        GetSoundManager().PlayAudioClip("click")
        self.UpdateProgressIndicators()
        q = self.questions[self.current_index]
        self.q_lbl.setText(f"◢ EVALUATION PHASE {self.current_index+1}:\n{q['question'].upper()}")
        opts = [q['option_a'], q['option_b'], q['option_c'], q['option_d']]
        for i, opt in enumerate(opts):
            self.opt_btns[i].setText(f"{chr(65+i)}) {opt.upper()}")
            self.opt_btns[i].setEnabled(True)
        self.res_lbl.setText("")
        self.btn_next.hide()

    def check_answer(self, idx):
        q = self.questions[self.current_index]
        is_correct = chr(65+idx) == q['correct_option'].upper()
        if is_correct:
            self.score += 1
            GetSoundManager().PlayAudioClip("acknowledge")
            self.res_lbl.setText("◢ NEURAL LINK ESTABLISHED: CORRECT")
            self.res_lbl.setStyleSheet("color: #00FF00;")
        else:
            GetSoundManager().PlayAudioClip("error")
            self.res_lbl.setText(f"◢ DATA CORRUPTION: INCORRECT // WAS {q['correct_option'].upper()}")
            self.res_lbl.setStyleSheet("color: #FF3333;")
        
        for b in self.opt_btns: b.setEnabled(False)
        self.btn_next.show()
        self.UpdateMetrics()

    def UpdateMetrics(self):
        acc = (self.score / (self.current_index + 1)) * 100
        self.metrics_lbl.setText(f"SCORE: {self.score}\nACCURACY: {acc:.0f}%")

    def next_q(self):
        self.current_index += 1
        self.show_question()

    def finish_test(self):
        self.q_lbl.setText(f"◢ EVALUATION COMPLETE\nFINAL SCORE: {self.score} / {len(self.questions)}")
        for btn in self.opt_btns: btn.hide()
        self.btn_next.hide()
        self.btn_start.show()
        self.btn_start.setText("RESTART EVALUATION")

# --- WEB BROWSER (uses full LCARSBrowserProgram) ---

class MiniWebBrowserWidget(Widget):
    # Simple stub: embedded browser disabled in this build.
    def __init__(self, theme, faction, parent=None):
        super().__init__(parent)
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        lbl = Label("WEB BROWSER DISABLED")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #FF6600; font-size: 24px;")
        layout.addWidget(lbl)
