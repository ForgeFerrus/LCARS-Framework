# Dashboard Widget for English Learning Application
# Main dashboard showing progress, recent activity, and quick access to features

from lcars.base.defaults import RandomButtonColor, FontStyle
# LCARS abstractions for UI components (no direct PyQt6 usage)
from lcars.base.types import Chassis, Label, Frame, GridLayout, Timer, Signal, ScrollArea, Widget, LineEdit, ProgressBar
from lcars.base.interface import LCARSButton, LCARSElbow, LCARSSegment, PushButton
from lcars.base.components import SystemComponent
import lcars.base.interface as BaseInterface
from lcars.modules.sound_manager import GetSoundManager
from pathlib import Path

# Всі компоненти імпортовані напряму з LCARS abstractions вище

# One default dashboard styling algorithm: use the built-in Titanium color generator.

def buildDashboardColors() -> dict:
    return {
        'panelBg': '#111111',
        'text': '#FFFFFF',
        'accent': RandomButtonColor(),
        'highlight': RandomButtonColor('panels'),
        'border': RandomButtonColor('accent'),
        'edge': RandomButtonColor('buttons'),
        'action': RandomButtonColor('alert'),
        'activityText': '#00FF00',
    }

class DashboardWidget(SystemComponent):
    # Main dashboard widget
    
    # Signals
    startExercise = Signal(str)  # exercise type
    viewDictionary = Signal()
    viewGrammar = Signal()
    viewProgress = Signal()
    
    def __init__(self, dbManager, progressTracker):
        super().__init__()
        self.db = dbManager
        self.progressTracker = progressTracker
        self.colors = buildDashboardColors()

        self.initUI()
        self.setupConnections()
        self.updateDashboard()
    
    def initUI(self):
        # Initialize the high-fidelity TITAN Dashboard UI

        self.setStyleSheet("background-color: black;")
        layout = VBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- TITAN DASHBOARD HEADER ---
        headerFrame = Frame()
        headerFrame.setMinimumHeight(120)
        headerLay = HBoxLayout(headerFrame)
        headerLay.setContentsMargins(0, 5, 20, 0)
        headerLay.setSpacing(20)
        
        self.headerElbow = LCARSElbow("top-left", self.colors['accent'])
        self.headerElbow.setMinimumSize(320, 120)
        headerLay.addWidget(self.headerElbow)
        
        titleLay = VBoxLayout()
        self.titleLbl = Label("ENGLISH LEARNING DASHBOARD V5.0")
        self.titleLbl.setStyleSheet(f"color: {self.colors['border']}; {FontStyle(32, 'bold')}; letter-spacing: 2px;")
        titleLay.addWidget(self.titleLbl)
        
        self.statusLabel = Label("SYSTEM STATUS: NOMINAL (LEVEL 10 ACCESS)")
        self.statusLabel.setStyleSheet(f"color: {self.colors['highlight']}; {FontStyle(18, 'normal')};")
        titleLay.addWidget(self.statusLabel)
        headerLay.addLayout(titleLay, 1)
        
        headerLay.addWidget(LCARSSegment(self.colors['edge'], direction="horizontal"), 1)
        layout.addWidget(headerFrame)
        
        # --- MAIN ARCHITECTURAL CONTENT ---
        bodyHbox = HBoxLayout()
        bodyHbox.setContentsMargins(20, 10, 20, 20)
        bodyHbox.setSpacing(30)
        
        # LEFT COLUMN (Progress & Stats)
        leftColumn = VBoxLayout()
        leftColumn.setSpacing(20)
        self.createProgressSection(leftColumn)
        self.createStatsSection(leftColumn)
        bodyHbox.addLayout(leftColumn, 2)
        
        # RIGHT COLUMN (Actions & Activity)
        rightColumn = VBoxLayout()
        rightColumn.setSpacing(20)
        self.createQuickActions(rightColumn)
        self.createRecentActivity(rightColumn)
        bodyHbox.addLayout(rightColumn, 1)
        
        layout.addLayout(bodyHbox, 1)

        # Floating ONBOARD button (always visible) — directly toggles global PanelManager 'onboard'
        self.floating_onboard_btn = LCARSButton("ONBOARD", ColorHexStr=self.colors['accent'])
        self.floating_onboard_btn.setParent(self)
        self.floating_onboard_btn.setFixedSize(140, 48)
        try:
            # Prefer a strong visible border so it cannot be missed
            base_ss = self.floating_onboard_btn.styleSheet() or ""
            self.floating_onboard_btn.setStyleSheet(base_ss + "; border: 3px solid #FFFFFF; box-shadow: 0 4px 8px rgba(0,0,0,0.5);")
        except Exception:
            pass
        self.floating_onboard_btn.clicked.connect(self.ToggleOnboardPanel)
        # initial placement; resizeEvent will keep it anchored
        try:
            self.floating_onboard_btn.move(18, 18)
            self.floating_onboard_btn.raise_()
        except Exception:
            pass
        
        # Bottom Architecture
        footerLay = HBoxLayout()
        footerLay.setContentsMargins(0, 0, 0, 0)
        self.footerElbow = LCARSElbow("bottom-left", self.colors['border'])
        self.footerElbow.setMinimumHeight(100)
        footerLay.addWidget(self.footerElbow)
        footerLay.addWidget(LCARSSegment(self.colors['highlight'], direction="horizontal"), 1)
        layout.addLayout(footerLay)
    
    def createProgressSection(self, layout):
        # Create the progress section
        progressFrame = Frame()
        progressFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['accent']};\n                border-radius: 10px;\n            }}\n        ")
        
        progressLayout = VBoxLayout(progressFrame)
        progressLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ LEARNING PROGRESS")
        title.setStyleSheet(f"\n            color: {self.colors['accent']};\n            {FontStyle(18, 'normal')}\n            margin-bottom: 10px;\n        ")
        progressLayout.addWidget(title)
        
        # Current level
        self.levelLabel = Label("Current Level: A1")
        self.levelLabel.setStyleSheet(f"\n            color: {self.colors['text']};\n            {FontStyle(16, 'normal')}\n            margin: 5px 0;\n        ")
        progressLayout.addWidget(self.levelLabel)
        
        # Overall progress bar
        progressLabel = Label("Overall Progress")
        progressLabel.setStyleSheet(f"color: {self.colors['text']}; {FontStyle(14, 'normal')}")
        progressLayout.addWidget(progressLabel)
        
        self.progressBar = ProgressBar()
        self.progressBar.setStyleSheet(f"\n            QProgressBar {{\n                border: 2px solid {self.colors['highlight']};\n                border-radius: 5px;\n                text-align: center;\n                color: {self.colors['text']};\n                {FontStyle(12, 'normal')}\n            }}\n            QProgressBar::chunk {{\n                background-color: {self.colors['highlight']};\n                border-radius: 3px;\n            }}\n        ")
        self.progressBar.setRange(0, 100)
        progressLayout.addWidget(self.progressBar)
        
        # Level requirements
        self.requirementsLabel = Label("Loading requirements...")
        self.requirementsLabel.setStyleSheet(f"\n            color: {self.colors['text']};\n            {FontStyle(12, 'normal')}\n            margin-top: 10px;\n        ")
        progressLayout.addWidget(self.requirementsLabel)
        
        layout.addWidget(progressFrame)
    
    def createStatsSection(self, layout):
        # Create the statistics section
        statsFrame = Frame()
        statsFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['edge']};\n                border-radius: 10px;\n            }}\n        ")
        
        statsLayout = VBoxLayout(statsFrame)
        statsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ STATISTICS")
        title.setStyleSheet(f"\n            color: {self.colors['edge']};\n            {FontStyle(18, 'normal')}\n            margin-bottom: 10px;\n        ")
        statsLayout.addWidget(title)
        
        # Stats grid
        statsGrid = GridLayout()
        
        # Words learned
        self.wordsLearnedLabel = Label("0")
        self.wordsLearnedLabel.setStyleSheet(f"\n            color: {self.colors['action']};\n            {FontStyle(24, 'normal')}\n        ")
        statsGrid.addWidget(Label("Words Learned:"), 0, 0)
        statsGrid.addWidget(self.wordsLearnedLabel, 0, 1)
        
        # Accuracy
        self.accuracyLabel = Label("0%")
        self.accuracyLabel.setStyleSheet(f"\n            color: {self.colors['highlight']};\n            {FontStyle(24, 'normal')}\n        ")
        statsGrid.addWidget(Label("Accuracy:"), 1, 0)
        statsGrid.addWidget(self.accuracyLabel, 1, 1)
        
        # Study streak
        self.streakLabel = Label("0 days")
        self.streakLabel.setStyleSheet(f"\n            color: {self.colors['border']};\n            {FontStyle(24, 'normal')}\n        ")
        statsGrid.addWidget(Label("Study Streak:"), 2, 0)
        statsGrid.addWidget(self.streakLabel, 2, 1)
        
        statsLayout.addLayout(statsGrid)
        layout.addWidget(statsFrame)
    
    def createQuickActions(self, layout):
        # Create quick action buttons
        actionsFrame = Frame()
        actionsFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['action']};\n                border-radius: 10px;\n            }}\n        ")
        
        actionsLayout = VBoxLayout(actionsFrame)
        actionsLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ QUICK ACTIONS")
        title.setStyleSheet(f"\n            color: {self.colors['action']};\n            {FontStyle(18, 'normal')}\n            margin-bottom: 10px;\n        ")
        actionsLayout.addWidget(title)
        
        # Action buttons
        actions = [
            ("Start Vocabulary", "vocabulary", self.colors['border']),
            ("Practice Grammar", "grammar", self.colors['accent']),
            ("Learn Phrases", "phrases", self.colors['highlight']),
            ("Take Test", "test", self.colors['edge']),
            ("Review Words", "review", self.colors['highlight'])
        ]
        
        for actionName, actionType, color in actions:
            btn = LCARSButton(actionName, ColorHexStr=color)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, t=actionType: self.startExercise.emit(t))
            actionsLayout.addWidget(btn)
        
        # Onboard quick action (secondary) — calls the same public toggle
        self.onboard_btn = LCARSButton("ONBOARD", ColorHexStr=self.colors['accent'])
        self.onboard_btn.setMinimumHeight(40)
        self.onboard_btn.clicked.connect(self.ToggleOnboardPanel)
        actionsLayout.addWidget(self.onboard_btn)

        layout.addWidget(actionsFrame)
    
    def createRecentActivity(self, layout):
        # Create recent activity section
        activityFrame = Frame()
        activityFrame.setStyleSheet(f"\n            QFrame {{\n                background-color: {self.colors['panelBg']};\n                border: 2px solid {self.colors['highlight']};\n                border-radius: 10px;\n            }}\n        ")
        
        activityLayout = VBoxLayout(activityFrame)
        activityLayout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title = Label("◤ RECENT ACTIVITY")
        title.setStyleSheet(f"\n            color: {self.colors['highlight']};\n            {FontStyle(18, 'normal')}\n            margin-bottom: 10px;\n        ")
        activityLayout.addWidget(title)
        
        # Activity text
        self.activityText = TextEdit()
        self.activityText.setReadOnly(True)
        self.activityText.setMaximumHeight(200)
        self.activityText.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {self.colors['panelBg']};
                color: {self.colors['activityText']};
                border: 1px solid {self.colors['highlight']};
                font-family: "Courier New", monospace;
                {FontStyle(12, 'normal')}
            }}
            """
        )
        self.activityText.setText("Loading recent activity...")
        activityLayout.addWidget(self.activityText)
        
        layout.addWidget(activityFrame)
    
    def applyStyling(self):
        # Apply overall styling
        self.setStyleSheet('\n            QWidget {\n                background-color: #000000;\n                color: white;\n                font-family: "Arial", sans-serif;\n            }\n            QLabel {\n                color: white;\n            }\n        ')
    
    def setupConnections(self):
        # Setup signal connections
        # Connect progress tracker signals
        self.progressTracker.progressUpdated.connect(self.updateDashboard)
        self.progressTracker.achievementUnlocked.connect(self.onAchievementUnlocked)
        self.progressTracker.levelUp.connect(self.onLevelUp)
        
        # Setup update timer
        self.updateTimer = Timer()
        self.updateTimer.timeout.connect(self.updateDashboard)
        self.updateTimer.start(30000)  # Update every 30 seconds
    
    def updateDashboard(self):
        # Update dashboard with current data
        # Update progress
        overallProgress = self.progressTracker.getOverallProgress()
        self.progressBar.setValue(int(overallProgress))
        
        # Update level
        currentLevel = self.progressTracker.getCurrentLevel()
        self.levelLabel.setText(f"Current Level: {self.progressTracker.getLevelDisplayName(currentLevel)}")
        
        # Update requirements
        nextLevelReqs = self.progressTracker.getNextLevelRequirements()
        reqsText = f"Next Level: {nextLevelReqs['next_level']}\n"
        reqs = nextLevelReqs['requirements']
        reqsText += f"Words: {reqs.get('vocabulary', 0)} | "
        reqsText += f"Accuracy: {reqs.get('accuracy', 0)}% | "
        reqsText += f"Sessions: {reqs.get('sessions', 0)}"
        self.requirementsLabel.setText(reqsText)
        
        # Update statistics
        stats = self.progressTracker.getLearningStatistics()
        if 'vocabulary' in stats:
            wordsStats = stats['vocabulary']
            self.wordsLearnedLabel.setText(str(wordsStats.get('learned_vocabulary', 0)))
            accuracy = (wordsStats.get('vocabulary_accuracy') or 0) * 100
            self.accuracyLabel.setText(f"{accuracy:.1f}%")
        
        # Update streak
        self.streakLabel.setText(f"{self.progressTracker.getStudyStreakDays()} days")
        
        # Update recent activity
        self.updateRecentActivity()
        
        # Update status
        self.statusLabel.setText("STATUS: ACTIVE")
    
    def updateRecentActivity(self):
        # Update recent activity display
        weeklyStats = self.progressTracker.getWeeklyProgress()
        
        activityText = "=== RECENT ACTIVITY ===\n\n"
        
        if weeklyStats:
            activityText += f"Weekly Sessions: {weeklyStats.get('session_count', 0)}\n"
            activityText += f"Study Time: {weeklyStats.get('total_minutes', 0)} minutes\n"
            activityText += f"Words Learned: {weeklyStats.get('total_vocabulary', 0)}\n"
            activityText += f"Exercises: {weeklyStats.get('total_exercises', 0)}\n"
            avgScore = weeklyStats.get('avg_accuracy') or 0
            activityText += f"Average Score: {avgScore:.1f}%\n"
        else:
            activityText += "No recent activity found.\n"
            activityText += "Start learning to see your progress here!"
        
        # Add recent achievements
        achievements = self.progressTracker.getAchievements()
        unlockedAchievements = [a for a in achievements if a['unlocked']]
        
        if unlockedAchievements:
            activityText += "\n=== RECENT ACHIEVEMENTS ===\n"
            for achievement in unlockedAchievements[-3:]:  # Show last 3
                activityText += f"🏆 {achievement['name']}\n"
                activityText += f"   {achievement['description']}\n"
        
        self.activityText.setText(activityText)
    
    def onAchievementUnlocked(self, achievementName):
        # Handle achievement unlock
        self.statusLabel.setText(f"ACHIEVEMENT: {achievementName}")
        # Could show a notification dialog
    
    def onLevelUp(self, newLevel):
        # Handle level up
        self.statusLabel.setText(f"LEVEL UP: {newLevel}")
        # Could show a celebration dialog

    def ToggleOnboardPanel(self):
        """Public toggle: try Workbench helper/PanelManager, else walk parents.

        This deliberately does not create an onboard instance locally — the
        system-wide `PanelManager` (registered on the Workbench) is the source
        of truth for the onboard drawer. We only attempt a local fallback by
        searching parents for a `PanelManagerNode`.
        """
        # 1) top-level window helper
        win = None
        try:
            win = self.window() if callable(getattr(self, 'window', None)) else None
        except Exception:
            win = None

        if win:
            helper = getattr(win, 'ToggleOnboardPanel', None)
            if callable(helper):
                helper()
                return
            pm = getattr(win, 'PanelManagerNode', None)
            if pm and callable(getattr(pm, 'TogglePanel', None)):
                pm.TogglePanel('onboard')
                return

        # 2) walk parent chain
        try:
            p = self.parent() if callable(getattr(self, 'parent', None)) else None
        except Exception:
            p = None

        while p is not None:
            pm = getattr(p, 'PanelManagerNode', None)
            if pm and callable(getattr(pm, 'TogglePanel', None)):
                pm.TogglePanel('onboard')
                return
            try:
                p = p.parent() if callable(getattr(p, 'parent', None)) else None
            except Exception:
                p = None

        # 3) no panel manager found — audible feedback as fallback
        try:
            GetSoundManager().PlayAudioClip('click')
        except Exception:
            pass

    def resizeEvent(self, event):
        # Keep floating button anchored and call base implementation.
        try:
            super().resizeEvent(event)
        except Exception:
            pass

        btn = getattr(self, 'floating_onboard_btn', None)
        if btn:
            try:
                btn.move(18, 18)
                btn.raise_()
            except Exception:
                pass


