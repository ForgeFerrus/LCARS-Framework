# LCARS SYSTEM CONSOLE PANEL (Titan V8.0)
# Інтерфейс консолі з вбудованою документацією команд.

# ВИКЛЮЧНО системні типи
from lcars.base.type import (
    Matrix, Label, HorizontalFlow, VerticalFlow, Panel,
    Elbow, Connector
)
from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.base.console import ConsoleBase

class ConsolePanel(Matrix):
    # Панель системної консолі. Містить документацію та інтерфейс командного рядка LCARS.
    def __init__(self, parent=None, event_bus=None, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Instantiate the ConsoleBase widget (Unified)
        self.console_widget = ConsoleBase(event_bus=event_bus, era=era, faction=faction)
        
        self.init_ui()

    def init_ui(self):
        # Палітра з теми
        palette = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF', '#9EA5BA'])
        if len(palette) < 4: palette = palette + ['#9EA5BA'] * (4 - len(palette))
        
        self.setStyleSheet("background-color: black;")
        layout = VerticalFlow(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- TITAN CONSOLE HEADER ---
        header_frame = Panel()
        header_frame.setMinimumHeight(120)
        header_lay = HorizontalFlow(header_frame)
        header_lay.setContentsMargins(0, 5, 20, 0)
        header_lay.setSpacing(20)
        
        # Використання уніфікованого Elbow
        self.header_elbow = Elbow("top-left", color=palette[1], era=self.era)
        self.header_elbow.setMinimumSize(320, 120)
        header_lay.addWidget(self.header_elbow)
        
        title_lay = VerticalFlow()
        self.title_lbl = Label("SYSTEM CONSOLE // CORE INTERFACE", size=32)
        self.title_lbl.setStyleSheet(f"color: {palette[0]}; letter-spacing: 2px; font-weight: bold;")
        title_lay.addWidget(self.title_lbl)
        
        self.status_lbl = Label("TERMINAL: ACTIVE // ENCRYPTION: LEVEL 10", size=18)
        self.status_lbl.setStyleSheet(f"color: {palette[2]};")
        title_lay.addWidget(self.status_lbl)
        header_lay.addLayout(title_lay, 1)
        
        # Використання уніфікованого Connector
        header_lay.addWidget(Connector(color=palette[3]), 1)
        layout.addWidget(header_frame)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        body_hbox = HorizontalFlow()
        body_hbox.setContentsMargins(20, 10, 20, 20)
        body_hbox.setSpacing(30)
        
        # LEFT: DOCS DECO
        left_col = VerticalFlow()
        left_col.setFixedWidth(200)
        
        doc_head = Label("◤ COMMANDS", size=16)
        doc_head.setStyleSheet(f"color: {palette[1]}; font-weight: bold;")
        left_col.addWidget(doc_head)
        
        doc_text = "STATUS\nALERT\nDIAG\nMODE\nCLEAR"
        doc_lbl = Label(doc_text, size=12)
        doc_lbl.setStyleSheet("color: white; line-height: 20px;")
        left_col.addWidget(doc_lbl)
        
        left_col.addStretch()
        left_col.addWidget(Connector(color=palette[2]), 1)
        
        self.left_elbow_bot = Elbow("bottom-left", color=palette[0], era=self.era)
        self.left_elbow_bot.setMinimumHeight(120)
        left_col.addWidget(self.left_elbow_bot)
        
        body_hbox.addLayout(left_col)
        
        # CENTER: CONSOLE AREA
        center_col = VerticalFlow()
        center_col.setContentsMargins(0, 0, 0, 0)
        
        # Встановлення UI Консолі
        self.console_widget.setup_console_ui(center_col)
        
        body_hbox.addLayout(center_col, 1)
        layout.addLayout(body_hbox, 1)

# Aliases for compatibility
ConsoleDrawer = ConsolePanel
ConsoleView = ConsolePanel
