# LCARS English Learning Application
# Створює інтерактивну систему навчання англійської мови з інтерфейсом у стилі LCARS, що включає словник, вправи, читання та налаштування.
# Використовує базу даних для зберігання прогресу та словникового запасу, а також має динамічну тему з випадковими кольорами для різних категорій елементів інтерфейсу.
from __future__ import annotations
import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parents[2]
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lcars.base.type import Application, Frame, Label, Chassis
from lcars.base.default import RandomButtonColor, DefaultPalette, FontSetup
from lcars.base.interface import LCARSButton, LCARSPadd
from lcars.program.learning.modules import DatabaseManager, LearningModuleManager
from lcars.program.learning.progress import ProgressTracker
# укр система навчання англійської мови з інтерфейсом у стилі LCARS, що включає словник, вправи, читання та налаштування.
# Вона використовує базу даних для зберігання прогресу та словникового запасу, а також має динамічну тему з випадковими кольорами для різних категорій елементів інтерфейсу.
class LinguisticApp(LCARSPadd):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS English Learning")
        self.setMinimumSize(1200, 800)

        self.db = DatabaseManager()
        self.engine = LearningModuleManager(self.db)
        self.modules = self.engine
        self.progress = ProgressTracker(self.db)

        self.faction = "FEDERATION"
        self.theme = self.BuildDefaultTheme()
        self.panels = {}
        self.buttons = {}

        self.BuildUI()
        self.Switch("dashboard")
        # -- PADD: вікно з відступами від країв, не на весь екран --
        self.setGeometry(60, 60, 1800, 960)
        # -- рамка з заокругленням як у погоди --
        self.setStyleSheet(f"""
            Frame {{
                background-color: {{self.GetThemeColor('bg')}};
                border: 2px solid {C0};
                border-radius: 12px;
            }}
        """)

    def GetThemeColor(self, role="primary"):
        # -- використовуємо DefaultPalette з defaults --
        if role == "primary":
            return RandomButtonColor("buttons")
        elif role == "secondary":
            return RandomButtonColor("accent")
        elif role == "accent":
            return RandomButtonColor("panels")
        elif role == "alert":
            return RandomButtonColor("alert")
        elif role == "bg":
            return "#000000"
        elif role == "text":
            return "#FFFFFF"
        return "#FF9900"
    def BuildUI(self):
        # Lazy imports - only import UI widgets when actually building UI
        from lcars.program.learning.ui.interface import ( 
            DashboardWidget, DictionaryWidget, ExercisesWidget, ReadingWidget,
        )
        from lcars.program.learning.ui.settings import SettingsWidget
        from lcars.program.learning.ui.tenses import TensesWidget
        from lcars.program.learning.ui.prepositions import PrepositionsWidget
        from lcars.program.learning.ui.onboard import OnboardWidget
        
        # Main layout attached directly to self (Frame)
        root = Chassis.Horizontal(self)
        # -- PADD: відступи як у погоди --
        root.setContentsMargins(5, 5, 5, 5)
        root.setSpacing(0)

        C0 = self.GetThemeColor("primary")
        C1 = self.GetThemeColor("secondary")
        C2 = self.GetThemeColor("accent")
        C3 = self.GetThemeColor("alert")

        # ── SIDEBAR ──────────────────────────────────────────────
        sidebarFrame = Frame()
        sidebarFrame.setFixedWidth(240)
        sidebarFrame.setStyleSheet("background: #05080e;")
        sidebarCol = Chassis.Vertical(sidebarFrame)
        sidebarCol.setContentsMargins(0, 0, 0, 0)
        sidebarCol.setSpacing(0)

        # Header block: colored top + title
        headerBlock = Frame()
        headerBlock.setStyleSheet(f"background: {C0};")
        headerBlock.setFixedHeight(70)
        headerRow = Chassis.Horizontal(headerBlock)
        headerRow.setContentsMargins(16, 0, 12, 0)
        appTitle = Label("ENGLISH  //  LCARS")
        appTitle.setStyleSheet("color: #000; font-family: 'LCARS'; font-size: 16pt; letter-spacing: 2px;")
        headerRow.addWidget(appTitle, 1)
        sidebarCol.addWidget(headerBlock)

        # Thin accent strip below header
        strip = Frame()
        strip.setFixedHeight(4)
        strip.setStyleSheet(f"background: {C1};")
        sidebarCol.addWidget(strip)

        # Nav buttons
        navArea = Frame()
        navArea.setStyleSheet("background: transparent;")
        navCol = Chassis.Vertical(navArea)
        navCol.setContentsMargins(0, 12, 0, 12)
        navCol.setSpacing(4)

        self.buttons = {}
        menuItems = [
            ("DASHBOARD",    "dashboard",    C0),
            ("DICTIONARY",   "vocabulary",   C1),
            ("EXERCISES",    "exercises",    C2),
            ("TENSES",       "tenses",       C3),
            ("PREPOSITIONS", "prepositions", C1),
            ("READING",      "reading",      C2),
            ("ONBOARD",      "onboard",      C3),
            ("SETTINGS",     "settings",     C0),
        ]

        for text, key, color in menuItems:
            btn = LCARSButton(text, Color=color)
            btn.setFixedHeight(44)
            btn.Clicked.connect(lambda ch=False, k=key: self.Switch(k))
            self.buttons[key] = btn
            navCol.addWidget(btn)

        sidebarCol.addWidget(navArea, 1)

        # Bottom status block
        statusBlock = Frame()
        statusBlock.setStyleSheet(f"background: #0a0d18; border-top: 3px solid {C2};")
        statusCol = Chassis.Vertical(statusBlock)
        statusCol.setContentsMargins(14, 10, 14, 10)
        statusCol.setSpacing(6)

        lvlRow = Chassis.Horizontal()
        lvlLabel = Label("LEVEL")
        lvlLabel.setStyleSheet(f"color: {C1}; font-family: 'LCARS'; font-size: 10pt;")
        self.stLevelValue = Label("A1")
        self.stLevelValue.setStyleSheet("color: #FFF; font-family: 'LCARS'; font-size: 14pt;")
        lvlRow.addWidget(lvlLabel)
        lvlRow.addStretch(1)
        lvlRow.addWidget(self.stLevelValue)
        statusCol.addLayout(lvlRow)

        accRow = Chassis.Horizontal()
        accLabel = Label("ACCURACY")
        accLabel.setStyleSheet(f"color: {C1}; font-family: 'LCARS'; font-size: 10pt;")
        self.stProgValue = Label("—")
        self.stProgValue.setStyleSheet("color: #FFF; font-family: 'LCARS'; font-size: 14pt;")
        accRow.addWidget(accLabel)
        accRow.addStretch(1)
        accRow.addWidget(self.stProgValue)
        statusCol.addLayout(accRow)

        # Add status block to sidebar
        sidebarCol.addWidget(statusBlock)

        # Add sidebar to main layout
        root.addWidget(sidebarFrame)

        # Content area
        self.contentArea = Frame()
        self.contentArea.setStyleSheet(f"background: #1a1d2e;")
        root.addWidget(self.contentArea, 4)

    def Switch(self, key):
        print(f"Switching to: {key}")
        # Clear content area
        while self.contentArea.layout() and self.contentArea.layout().count():
            item = self.contentArea.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Create layout for content
        contentLayout = Chassis.Vertical(self.contentArea)
        label = Label(f"{key.upper()} MODULE")
        label.setStyleSheet("color: #FF9900; font-family: 'LCARS'; font-size: 24pt;")
        contentLayout.addWidget(label)

    def closeEvent(self, event):

        print("Closing English Learning App...")
        event.accept()

# 
def main():
    import sys
    from lcars.base.type import Application
    from lcars.base.default import FontSetup

    app = Application(sys.argv)
    FontSetup()
    
    # LCARS Panel as display
    panel = LinguisticApp()
    panel.show()
    
    sys.exit(app.exec())
