# LCARS English Learning Application
from __future__ import annotations
import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parents[2]
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

from lcars.core.kernel import CreateApplication
from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor, FontSetup, SetDisplayFlag
from lcars.base.interface import Segment, Panel, DataBlock
from lcars.base.component import LCARSButton, LCARSLabel, LCARSIndicator

from programs.learning.logic import DatabaseManager, LearningModuleManager
from programs.learning.progress import ProgressTracker
from lcars.modules.sound import GetSound

# Import the user's original widgets
from programs.learning.ui.interface import DashboardWidget, DictionaryWidget, ExercisesWidget, ReadingWidget
from programs.learning.ui.tenses import TensesWidget
from programs.learning.ui.prepositions import PrepositionsWidget
from programs.learning.ui.settings import SettingsWidget

class LinguisticApp(Segment):
    def __init__(self, parent=None):
        super().__init__(Parent=parent)
        
        self.db = DatabaseManager()
        self.modules = LearningModuleManager(self.db)
        self.progress = ProgressTracker(self.db)
        
        self.theme = {"palette": Palette.Buttons, "accent": Palette.Buttons[1], "alert": Palette.RedAlert[0]}
        self.faction = "FEDERATION"
        
        self.buttons = {}
        self.panels = {}
        
        self.BuildUI()
        self.InitPanels()
        self.Switch("dashboard")

    def BuildUI(self):
        root = self.Horizontal(0, 0, 0, 0, 8)
        
        C0, C1, C2, C3 = Palette.Buttons[0], Palette.Buttons[1], Palette.Buttons[2], Palette.Buttons[3]

        # SIDEBAR
        self.sidebarColumn = Segment(Parent=self.widget)
        self.sidebarColumn.widget.setFixedWidth(240)
        self.sidebarColumn.Vertical(0, 0, 0, 0, 4)

        appTitle = LCARSIndicator(Text="ENGLISH // LCARS", Type="title", Color=C0, Parent=self.sidebarColumn.widget)
        self.sidebarColumn.Add(self.sidebarColumn.Layout, appTitle)

        navArea = Segment(Parent=self.sidebarColumn.widget)
        navArea.Vertical(0, 0, 0, 0, 4)
        
        menuItems = [
            ("DASHBOARD",    "dashboard",    C0),
            ("DICTIONARY",   "vocabulary",   C1),
            ("EXERCISES",    "exercises",    C2),
            ("TENSES",       "tenses",       C3),
            ("PREPOSITIONS", "prepositions", C1),
            ("READING",      "reading",      C2),
            ("SETTINGS",     "settings",     C0),
        ]

        for text, key, color in menuItems:
            btn = LCARSButton(Text=text, Type="soft-left", Color=color, Parent=navArea.widget)
            btn.widget.setFixedHeight(44)
            btn.Clicked.Connect(lambda k=key: self.Switch(k))
            self.buttons[key] = btn
            navArea.Add(navArea.Layout, btn)
            
        self.sidebarColumn.Add(self.sidebarColumn.Layout, navArea, 1)
        self.sidebarColumn.AddStretch(self.sidebarColumn.Layout)

        # Status block at bottom of sidebar
        statusBlock = Segment(Parent=self.sidebarColumn.widget)
        statusBlock.Vertical()
        self.stLevelValue = LCARSIndicator(Text="LEVEL: A1", Type="status", Status="ready", Parent=statusBlock.widget)
        statusBlock.Add(statusBlock.Layout, self.stLevelValue)
        self.sidebarColumn.Add(self.sidebarColumn.Layout, statusBlock)
        
        self.Add(root, self.sidebarColumn)

        # Content area
        self.contentArea = Segment(Parent=self.widget)
        self.contentArea.Vertical(0, 0, 0, 0, 0)
        
        self.titleLbl = LCARSIndicator(Text="COMMAND CORE // DASHBOARD", Type="rect-left", Color=C1, Parent=self.contentArea.widget)
        self.contentArea.Add(self.contentArea.Layout, self.titleLbl)
        
        self.stackChamber = Segment(Parent=self.contentArea.widget)
        self.stackChamber.Vertical(0, 0, 0, 0, 0)
        self.contentArea.Add(self.contentArea.Layout, self.stackChamber, 1)

        self.Add(root, self.contentArea, 4)

    def InitPanels(self):
        # Кожна панель створюється явно, без прихованого try/except.
        # Так ми одразу бачимо справжню помилку, якщо один із модулів ще не готовий.
        configs = [
            ("dashboard", self.BuildDashboard),
            ("vocabulary", self.BuildDictionary),
            ("exercises", self.BuildExercises),
            ("tenses", self.BuildTenses),
            ("prepositions", self.BuildPrepositions),
            ("reading", self.BuildReading),
            ("settings", self.BuildSettings),
        ]

        for key, builder in configs:
            panel = builder()
            q_widget = panel.widget if hasattr(panel, "widget") else panel
            if hasattr(q_widget, "hide"):
                q_widget.hide()
            self.stackChamber.Layout.addWidget(q_widget)
            self.panels[key] = (panel, q_widget)

        if "dashboard" in self.panels:
            panel, _ = self.panels["dashboard"]
            if hasattr(panel, "startExercise"):
                panel.startExercise.connect(self.SwitchPanel)

    def BuildDashboard(self):
        return DashboardWidget(self.db, self.progress, self.theme, self.faction)

    def BuildDictionary(self):
        return DictionaryWidget(self.db, self.progress, self.theme, self.faction)

    def BuildExercises(self):
        return ExercisesWidget(self.modules, self.progress, self.theme, self.faction)

    def BuildTenses(self):
        return TensesWidget(self.theme, self.db, self.faction)

    def BuildPrepositions(self):
        return PrepositionsWidget(self.theme, self.faction)

    def BuildReading(self):
        return ReadingWidget(self.db, self.progress, self.theme, self.faction)

    def BuildSettings(self):
        return SettingsWidget(self.db, self.progress, self.theme, self.faction)

    def Switch(self, key):
        self.SwitchPanel(key)
        
    def SwitchPanel(self, key):
        GetSound().PlayAudioClip("click")
        
        keyAliases = {
            "dictionary": "vocabulary",
            "tests": "exercises",
        }
        keySafe = keyAliases.get(key, key)
        if keySafe not in self.panels:
            keySafe = "dashboard"

        keysToTitles = {
            "dashboard":    "COMMAND CORE // DASHBOARD",
            "vocabulary":   "DICTIONARY // LINGUISTIC DATABASE",
            "exercises":    "NEURAL RETRIEVAL // FLASHCARDS",
            "tenses":       "MORPHOLOGY // TENSE MATRIX",
            "prepositions": "SYNTAX DRILL // PREPOSITIONS",
            "reading":      "ANALYSIS // READING COMPREHENSION",
            "settings":     "SYSTEM OPS // SETTINGS",
        }
        
        self.titleLbl.SetText(keysToTitles.get(keySafe, keySafe.upper())) # type: ignore
        lvl = self.progress.getCurrentLevel() if hasattr(self.progress, 'getCurrentLevel') else "A1"
        self.stLevelValue.SetText(f"LEVEL: {lvl}")

    def closeEvent(self, event):
        if hasattr(self.progress, 'endSession'):
            self.progress.endSession(0)
        self.db.close()
        event.accept()

# Backward-compatible symbol name
EnglishLearning = LinguisticApp

if __name__ == "__main__":
    app = CreateApplication(sys.argv)
    FontSetup()
    panel = LinguisticApp()
    FramelessFlag = LCARS.Get("Protocol.Display.Frameless")
    if FramelessFlag is not None:
        SetDisplayFlag(panel.widget, FramelessFlag, True)
    ShowFull = getattr(panel.widget, "showFullScreen", None)
    if ShowFull:
        ShowFull()
    else:
        panel.widget.show()
    sys.exit(app.exec())
