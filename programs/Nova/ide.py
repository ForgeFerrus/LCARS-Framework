# ◤ TITANIUM LCARS :: NOVA IDE MISSION DEV WORKBENCH 🖖
# =============================================================================
# ФАЙЛ: programs/Nova/ide.py
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase).
# ПРИЗНАЧЕННЯ: Повноцінна інтегрована система розробки та симуляцій зорельота.
# =============================================================================

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, Dict, List

from lcars.base.component import LCARSButton, LCARSLabel, SetStyle, LCARSBar, LCARSElbow
from lcars.base.interface import Screen, Panel, Segment
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.service.onboard import BoardComputer
from lcars.modules.project import ProjectManager, ProjectInfo
from lcars.core.signal import ODN
from lcars.modules.sound import ActiveAudio

try:
    from PyQt6.QtWidgets import QLineEdit
except ImportError:
    QLineEdit = None

try:
    from programs.Nova.core import NovaCore
    from programs.Nova.logic import NovaState
except ImportError:
    class NovaCore(LCARS):
        def __init__(self, Root=None):
            super().__init__()
            self.Root = Root
        def Setup(self):
            pass
    class NovaState(LCARS):
        def __init__(self, Root=None):
            super().__init__()
            self.CurrentFile = None
        def SetFile(self, File):
            self.CurrentFile = File
        def GetFile(self):
            return self.CurrentFile

from programs.Nova.laboratory import LaboratoryPanel
from programs.Nova.superdesign import SuperDesignPanel
from programs.Nova.vision import MachineVision, VisionPanel


class NovaPanel(Screen):
    ThemeName = "LCARS"
    LayoutMode = "command-console"

    def BuildScreen(self):
        pass

    def __init__(self, Parent=None):
        App = LCARS.Application.instance() if hasattr(LCARS.Application, 'instance') else None
        if App is None:
            App = LCARS.Application([])

        self.App = App
        self.ThemeName = "LCARS"
        self.LayoutMode = "command-console"
        super().__init__(Parent=Parent, Decorated=False, Color='#000000')

        self.ProjectRoot = Path(__file__).resolve().parents[2]
        self.State = NovaState(self.ProjectRoot)
        self.Core = NovaCore(self.ProjectRoot)
        self.Core.Setup()

        # Підключення менеджера проєктів Geant4 Enterprise
        self.ProjectManager = ProjectManager(self.ProjectRoot)
        self.CurrentProject: Optional[ProjectInfo] = None
        self.CurrentProjectRoot: Path = self.ProjectRoot

        self.CurrentFile: Optional[Path] = None
        self.Editors: Dict[Path, str] = {}
        self.FileButtons: List[LCARSButton] = []
        self.ProjectButtons: Dict[str, LCARSButton] = {}
        self.TabButtons: List[LCARSButton] = []
        self.ModeButtons: Dict[str, LCARSButton] = {}

        self.Computer = BoardComputer.GetInstance()
        if hasattr(self.Computer, "AttachIde"):
            self.Computer.AttachIde(self)

        self.Vision = MachineVision(self.ProjectRoot)
        self.ActiveProcess = None
        self.ActiveWorkspaceMode = "CODE"
        self.BottomTerminal = None
        self.TerminalOutput = None

        self.Build()
        self.Sidebar = getattr(self, "NavColumn", self)
        self.RightPane = getattr(self, "RightStack", self)
        self.PreviewPane = getattr(self, "VisionPage", self)
        self.SdkPanel = getattr(self, "CopilotPage", self)
        self.Bind()
        self.LoadInitialProject()

    def Build(self):
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        Content = self.widget
        RootLayout = Content.layout()
        if RootLayout is None:
            RootLayout = LCARS.Vertical(Content)
        RootLayout.setContentsMargins(8, 8, 8, 8)
        RootLayout.setSpacing(6)


        # ── 1. ВЕРХНІЙ LCARS HEADER & TELEMETRY
        TopFrame = Segment(Parent=Content)
        TopFrameLayout = LCARS.Horizontal(TopFrame.widget)
        TopFrameLayout.setContentsMargins(0, 0, 0, 0)
        TopFrameLayout.setSpacing(8)

        TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=TopFrame.widget)
        TopElbow.widget.setFixedSize(200, 48)
        TopFrameLayout.addWidget(TopElbow.widget)

        self.HeaderBar = LCARSBar(Height=48, Color=Palette.Buttons[1], Parent=TopFrame.widget)
        self.HeaderBar.widget.setStyleSheet("background-color: " + Palette.Buttons[1] + "; border-radius: 4px;")
        HeaderLayout = LCARS.Horizontal(self.HeaderBar.widget)
        HeaderLayout.setContentsMargins(14, 0, 14, 0)
        HeaderLayout.setSpacing(12)

        self.TitleLabel = LCARSLabel(Text="NOVA IDE // STARFLEET MISSION DEV WORKBENCH", Color="#000000", FontSize=15, Parent=None)
        HeaderLayout.addWidget(self.TitleLabel.widget)

        self.HeaderTelemetry = LCARSLabel(Text="PROJECT: INITIALIZING // ODN 100%", Color="#000000", FontSize=12, Parent=None)
        HeaderLayout.addWidget(self.HeaderTelemetry.widget, 1)

        self.BtnDesktop = LCARSButton(Text="BRIDGE DESKTOP", Form=LCARSButton.Pill, Color=Palette.Buttons[2], Parent=None)
        self.BtnDesktop.widget.setFixedHeight(30)
        self.BtnDesktop.widget.setFixedWidth(130)
        self.BtnDesktop.Clicked.Connect(self.ReturnToDesktop)
        HeaderLayout.addWidget(self.BtnDesktop.widget)

        self.BtnTerminal = LCARSButton(Text="COMMAND CONSOLE", Form=LCARSButton.Pill, Color=Palette.Buttons[4], Parent=None)
        self.BtnTerminal.widget.setFixedHeight(30)
        self.BtnTerminal.widget.setFixedWidth(140)
        self.BtnTerminal.Clicked.Connect(self.ReturnToTerminal)
        HeaderLayout.addWidget(self.BtnTerminal.widget)

        TopFrameLayout.addWidget(self.HeaderBar.widget, 1)
        RootLayout.addWidget(TopFrame.widget)


        # ── 2. ГОЛОВНЕ ТІЛО (ЛІВИЙ САЙДБАР + ПРАВИЙ РОБОЧИЙ ПРОСТІР)
        BodyRow = Segment(Parent=None)
        BodyLayout = LCARS.Horizontal(BodyRow.widget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(8)

        # ── ЛІВА ПАНЕЛЬ: ПРОЄКТИ ТА ФАЙЛИ
        NavColumn = Segment(Parent=None)
        NavColumn.widget.setFixedWidth(260)
        NavLayout = LCARS.Vertical(NavColumn.widget)
        NavLayout.setContentsMargins(0, 0, 0, 0)
        NavLayout.setSpacing(5)


        # Перемикачі режимів Nova (компактні кнопки)
        ModesRow = Segment(Parent=None)
        MRL = LCARS.Horizontal(ModesRow.widget)
        MRL.setContentsMargins(0, 0, 0, 0)
        MRL.setSpacing(4)
        Modes = [
            ("CODE", "CODE", Palette.Buttons[0]),
            ("DESIGN", "UI", Palette.Buttons[4]),
            ("VISOR", "VISION", Palette.Buttons[1]),
            ("COLOR_LAB", "COLOR", Palette.Buttons[2]),
            ("AST_SENTINEL", "AI", Palette.Buttons[3]),
        ]
        for ModeKey, ModeTitle, ModeColor in Modes:
            Btn = LCARSButton(Text=ModeTitle, Form=LCARSButton.Soft, Color=ModeColor, Parent=None)
            Btn.widget.setFixedHeight(28)
            k = ModeKey
            Btn.Clicked.Connect(lambda *_, mode=k: self.SwitchMode(mode))
            self.ModeButtons[ModeKey] = Btn
            MRL.addWidget(Btn.widget)
        NavLayout.addWidget(ModesRow.widget)


        # Заголовок проєктів
        ProjectsHeader = LCARSLabel(Text="◤ REGISTERED MISSIONS & PROJECTS", Color=Palette.Buttons[0], FontSize=11, Parent=None)
        NavLayout.addWidget(ProjectsHeader.widget)


        # Скрол-зона проєктів Geant4 / Enterprise
        self.ProjectsScroll = LCARS.Buffer(NavColumn.widget)
        self.ProjectsScroll.setFixedHeight(120)
        self.ProjectsScroll.setWidgetResizable(True)
        if getattr(LCARS, "ScrollAlwaysOff", None) is not None:
            self.ProjectsScroll.setVerticalScrollBarPolicy(LCARS.ScrollAlwaysOff)
            self.ProjectsScroll.setHorizontalScrollBarPolicy(LCARS.ScrollAlwaysOff)
        self.ProjectsScroll.setStyleSheet("background-color: #040810; border: none;")

        self.ProjectsContent = LCARS.Widget()
        self.ProjectsContent.setStyleSheet("background-color: transparent;")
        self.ProjectsLayout = LCARS.Vertical(self.ProjectsContent)
        self.ProjectsLayout.setContentsMargins(0, 0, 0, 0)
        self.ProjectsLayout.setSpacing(3)
        self.ProjectsScroll.setWidget(self.ProjectsContent)
        NavLayout.addWidget(self.ProjectsScroll)

        # Інфо-картка активного проєкту
        self.ProjectInfoCard = LCARSLabel(Text="SELECT A MISSION PROJECT", Color=Palette.Buttons[2], FontSize=11, Parent=None)
        NavLayout.addWidget(self.ProjectInfoCard.widget)

        # Заголовок файлів проєкту
        self.FilesHeader = LCARSLabel(Text="◤ PROJECT CHIPS // DIRECTORY TREE", Color=Palette.Buttons[1], FontSize=11, Parent=None)
        NavLayout.addWidget(self.FilesHeader.widget)

        # Дерево файлів проєкту
        self.FilesScroll = LCARS.Buffer(NavColumn.widget)
        self.FilesScroll.setWidgetResizable(True)
        if getattr(LCARS, "ScrollAlwaysOff", None) is not None:
            self.FilesScroll.setVerticalScrollBarPolicy(LCARS.ScrollAlwaysOff)
            self.FilesScroll.setHorizontalScrollBarPolicy(LCARS.ScrollAlwaysOff)
        self.FilesScroll.setStyleSheet("background-color: #03060C; border: none;")
        self.FilesContent = LCARS.Widget()
        self.FilesContent.setStyleSheet("background-color: transparent;")
        self.FilesLayout = LCARS.Vertical(self.FilesContent)
        self.FilesLayout.setSpacing(2)
        self.FilesScroll.setWidget(self.FilesContent)
        NavLayout.addWidget(self.FilesScroll, 1)


        # Дії над файлами
        ActionsRow = Segment(Parent=None)
        ARL = LCARS.Horizontal(ActionsRow.widget)
        ARL.setContentsMargins(0, 0, 0, 0)
        ARL.setSpacing(4)

        self.BtnNew = LCARSButton(Text="NEW FILE", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Parent=None)
        self.BtnNew.widget.setFixedHeight(30)
        ARL.addWidget(self.BtnNew.widget)

        self.BtnSave = LCARSButton(Text="SAVE FILE", Form=LCARSButton.Soft, Color=Palette.Buttons[0], Parent=None)
        self.BtnSave.widget.setFixedHeight(30)
        ARL.addWidget(self.BtnSave.widget)

        self.BtnRefresh = LCARSButton(Text="RELOAD", Form=LCARSButton.Soft, Color=Palette.Buttons[3], Parent=None)
        self.BtnRefresh.widget.setFixedHeight(30)
        ARL.addWidget(self.BtnRefresh.widget)

        NavLayout.addWidget(ActionsRow.widget)
        BodyLayout.addWidget(NavColumn.widget)


        # ── ПАНЕЛЬ 2 (ЦЕНТРАЛЬНА): Вкладки, Редактор коду та Нижня консоль
        CenterColumn = Segment(Parent=BodyRow.widget)
        CenterLayout = LCARS.Vertical(CenterColumn.widget)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(6)

        # Рядок активних вкладок-буферів (LCARS Chips Bar)
        self.TabHeader = Segment(Parent=CenterColumn.widget)
        self.TabHeaderLayout = LCARS.Horizontal(self.TabHeader.widget)
        self.TabHeaderLayout.setContentsMargins(0, 0, 0, 0)
        self.TabHeaderLayout.setSpacing(4)
        self.TabHeaderLayout.addStretch(1)
        CenterLayout.addWidget(self.TabHeader.widget)

        # Редактор коду
        self.CodePage = Segment(Parent=None)
        CodeLayout = LCARS.Vertical(self.CodePage.widget)
        CodeLayout.setContentsMargins(0, 0, 0, 0)
        CodeLayout.setSpacing(2)

        self.Editor = LCARS.Terminal(self.CodePage.widget)
        self.Editor.setReadOnly(False)
        self.Editor.setStyleSheet(
            "background-color: #020408; color: #7FF3FF; border: 1px solid #1F456E; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 13pt; padding: 12px; line-height: 1.4;"
        )
        if hasattr(self.Editor, "cursorPositionChanged"):
            self.Editor.cursorPositionChanged.connect(lambda: self.UpdateEditorStats())
        CodeLayout.addWidget(self.Editor, 1)

        # Рядок статистики редактора
        self.EditorStats = LCARSLabel(Text="LN: 1, COL: 1 | UTF-8 | SOURCE BUFFER", Color=Palette.Buttons[3], FontSize=10, Parent=self.CodePage.widget)
        CodeLayout.addWidget(self.EditorStats.widget)
        CenterLayout.addWidget(self.CodePage.widget, 3)

        # ── НИЖНЯ КОНСОЛЬ ЗБІРКИ ТА ВИКОНАННЯ
        ConsoleBox = Segment(Parent=None)
        ConsoleBoxLayout = LCARS.Vertical(ConsoleBox.widget)
        ConsoleBoxLayout.setContentsMargins(0, 0, 0, 0)
        ConsoleBoxLayout.setSpacing(3)

        ConsoleHeader = Segment(Parent=None)
        CHL = LCARS.Horizontal(ConsoleHeader.widget)
        CHL.setContentsMargins(0, 0, 0, 0)
        CHL.setSpacing(6)

        self.ConsoleTitle = LCARSLabel(Text="◤ COMPILER & SIMULATION ODN STREAM", Color=Palette.Buttons[4], FontSize=11, Parent=None)
        CHL.addWidget(self.ConsoleTitle.widget)
        CHL.addStretch(1)

        self.BtnBuild = LCARSButton(Text="BUILD (CMake)", Form=LCARSButton.Soft, Color=Palette.Buttons[0], Parent=None)
        self.BtnBuild.widget.setFixedHeight(26)
        self.BtnBuild.Clicked.Connect(self.BuildCurrentProject)
        CHL.addWidget(self.BtnBuild.widget)

        self.BtnRun = LCARSButton(Text="RUN SIMULATION", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Parent=None)
        self.BtnRun.widget.setFixedHeight(26)
        self.BtnRun.Clicked.Connect(self.RunSimulation)
        CHL.addWidget(self.BtnRun.widget)

        self.BtnExecPy = LCARSButton(Text="RUN SCRIPT", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Parent=None)
        self.BtnExecPy.widget.setFixedHeight(26)
        self.BtnExecPy.Clicked.Connect(self.RunScript)
        CHL.addWidget(self.BtnExecPy.widget)

        self.BtnKill = LCARSButton(Text="STOP", Form=LCARSButton.Soft, Color=Palette.Red[0], Parent=None)
        self.BtnKill.widget.setFixedHeight(26)
        self.BtnKill.Clicked.Connect(self.KillActiveProcess)
        CHL.addWidget(self.BtnKill.widget)

        self.BtnClearTerm = LCARSButton(Text="CLEAR", Form=LCARSButton.Soft, Color=Palette.Buttons[3], Parent=None)
        self.BtnClearTerm.widget.setFixedHeight(26)
        self.BtnClearTerm.Clicked.Connect(self.ClearTerminal)
        CHL.addWidget(self.BtnClearTerm.widget)

        ConsoleBoxLayout.addWidget(ConsoleHeader.widget)

        # Консольне вікно
        self.TerminalDisplay = LCARS.Terminal(ConsoleBox.widget)
        self.TerminalDisplay.setReadOnly(True)
        self.TerminalDisplay.setStyleSheet(
            "background-color: #010306; color: #00FF99; border: 1px solid #00AA66; "
            "font-family: 'Consolas', monospace; font-size: 11pt; padding: 6px;"
        )
        ConsoleBoxLayout.addWidget(self.TerminalDisplay, 1)
        self.TerminalOutput = self.TerminalDisplay

        # Рядок введення команд та директив копілоту в нижній консолі
        ConsoleInputRow = Segment(Parent=None)
        CIRLayout = LCARS.Horizontal(ConsoleInputRow.widget)
        CIRLayout.setContentsMargins(0, 0, 0, 0)
        CIRLayout.setSpacing(6)

        self.ConsoleInput = LCARS.Terminal(ConsoleInputRow.widget)
        self.ConsoleInput.setReadOnly(False)
        self.ConsoleInput.setFixedHeight(28)
        if hasattr(self.ConsoleInput, "setPlaceholderText"):
            self.ConsoleInput.setPlaceholderText("ENTER LCARS / COPILOT DIRECTIVE...")
        self.ConsoleInput.setStyleSheet(
            "background-color: #030805; color: #00FF99; border: 1px solid #00AA66; "
            "font-family: Consolas, monospace; font-size: 10pt; padding: 3px 8px; border-radius: 3px;"
        )
        CIRLayout.addWidget(self.ConsoleInput, 1)

        self.BtnConsoleSend = LCARSButton(Text="TRANSMIT", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Parent=ConsoleInputRow.widget)
        self.BtnConsoleSend.widget.setFixedHeight(28)
        self.BtnConsoleSend.widget.setFixedWidth(110)
        self.BtnConsoleSend.Clicked.Connect(self.SubmitBottomConsolePrompt)
        CIRLayout.addWidget(self.BtnConsoleSend.widget)

        ConsoleBoxLayout.addWidget(ConsoleInputRow.widget)
        CenterLayout.addWidget(ConsoleBox.widget, 2)
        BodyLayout.addWidget(CenterColumn.widget, 1)

        # ── ПАНЕЛЬ 3 (ПРАВА): ІНТЕГРОВАНИЙ ШІ-КОПІЛОТ, SUPERDESIGN ТА МАШИННЕ БАЧЕННЯ
        RightColumn = Segment(Parent=BodyRow.widget)
        RightColumn.widget.setFixedWidth(400)
        RightLayout = LCARS.Vertical(RightColumn.widget)
        RightLayout.setContentsMargins(0, 0, 0, 0)
        RightLayout.setSpacing(6)

        RightHeader = Segment(Parent=RightColumn.widget)
        RHL = LCARS.Horizontal(RightHeader.widget)
        RHL.setContentsMargins(0, 0, 0, 0)
        RHL.setSpacing(4)

        self.RightTitleLabel = LCARSLabel(Text="◤ AI SENTINEL & LIVE INSPECTOR", Color=Palette.Buttons[3], FontSize=11, Parent=None)
        RHL.addWidget(self.RightTitleLabel.widget, 1)

        self.BtnToggleRight = LCARSButton(Text="COLLAPSE", Form=LCARSButton.Soft, Color="#445566", Parent=None)
        self.BtnToggleRight.widget.setFixedHeight(24)
        self.BtnToggleRight.widget.setFixedWidth(80)
        self.BtnToggleRight.Clicked.Connect(self.ToggleRightPane)
        RHL.addWidget(self.BtnToggleRight.widget)
        RightLayout.addWidget(RightHeader.widget)

        # [PAGE 1] SuperDesign Генератор інтерфейсів
        self.DesignPage = SuperDesignPanel(Parent=None, Editor=self.Editor, Designer=None)

        # [PAGE 2] Машинне бачення (Vision & UI Inspector)
        self.VisionPage = VisionPanel(
            Parent=None,
            ProjectRoot=self.ProjectRoot,
            ChannelData=self.OnVisionData,
            ChannelLog=self.AppendLog
        )

        # [PAGE 3] Лабораторія кольорів та UI (LaboratoryPanel)
        self.LabPage = LaboratoryPanel(
            Parent=None,
            ProjectRoot=self.ProjectRoot,
            ChannelTheme=self.OnThemeExported,
            ChannelLog=self.AppendLog
        )

        # [PAGE 4] AI AST Copilot & Sentinel
        self.CopilotPage = Segment(Parent=None)
        CopilotLayout = LCARS.Vertical(self.CopilotPage.widget)
        CopilotLayout.setContentsMargins(4, 4, 4, 4)
        CopilotLayout.setSpacing(6)

        CopilotTitle = LCARSLabel(Text="LCARS AST SENTINEL // CODE INTELLIGENCE CORE", Color=Palette.Buttons[3], FontSize=12, Parent=self.CopilotPage.widget)
        CopilotLayout.addWidget(CopilotTitle.widget)

        # Вікно діалогу з агентом
        self.CopilotDisplay = LCARS.Terminal(self.CopilotPage.widget)
        self.CopilotDisplay.setReadOnly(True)
        self.CopilotDisplay.setStyleSheet(
            "background-color: #040206; color: #FF99FF; border: 1px solid #CC66CC; font-family: Consolas; font-size: 11pt; padding: 8px;"
        )
        self.CopilotDisplay.setPlainText(
            "◤ SENTINEL ONBOARD INTELLIGENCE 🖖\n>> Ready for AST refactoring, bug fixes, UI generation, and code directives.\n"
        )
        CopilotLayout.addWidget(self.CopilotDisplay, 1)

        # Рядок введення директив для копілота
        InputRow = Segment(Parent=None)
        InputLayout = LCARS.Horizontal(InputRow.widget)
        InputLayout.setContentsMargins(0, 0, 0, 0)
        InputLayout.setSpacing(6)

        self.CopilotInput = LCARS.Terminal(InputRow.widget)
        self.CopilotInput.setReadOnly(False)
        self.CopilotInput.setFixedHeight(32)
        if hasattr(self.CopilotInput, "setPlaceholderText"):
            self.CopilotInput.setPlaceholderText("ENTER DIRECTIVE FOR AI AGENT...")
        self.CopilotInput.setStyleSheet(
            "background-color: #050208; color: #FFCCFF; border: 1px solid #CC66CC; "
            "font-family: Consolas, sans-serif; font-size: 11pt; padding: 4px 10px; border-radius: 4px;"
        )
        InputLayout.addWidget(self.CopilotInput, 1)

        self.BtnCopilotSend = LCARSButton(Text="TRANSMIT", Form=LCARSButton.Soft, Color=Palette.Buttons[3], Parent=InputRow.widget)
        self.BtnCopilotSend.widget.setFixedHeight(30)
        self.BtnCopilotSend.widget.setFixedWidth(110)
        self.BtnCopilotSend.Clicked.Connect(lambda *_: self.SubmitCopilotPrompt())
        InputLayout.addWidget(self.BtnCopilotSend.widget)

        CopilotLayout.addWidget(InputRow.widget)

        # Додаємо сторінки у праву панель
        RightLayout.addWidget(self.CopilotPage.widget, 1)
        RightLayout.addWidget(self.DesignPage.widget, 1)
        RightLayout.addWidget(self.VisionPage.widget, 1)
        RightLayout.addWidget(self.LabPage.widget, 1)

        self.DesignPage.widget.hide()
        self.VisionPage.widget.hide()
        self.LabPage.widget.hide()
        self.CopilotPage.widget.show()

        BodyLayout.addWidget(RightColumn.widget)

        self.Pages = {
            "CODE": self.CodePage,
            "DESIGN": self.DesignPage,
            "VISOR": self.VisionPage,
            "COLOR_LAB": self.LabPage,
            "AST_SENTINEL": self.CopilotPage,
        }

        self.NavColumn = NavColumn
        self.CenterColumn = CenterColumn
        self.RightColumn = RightColumn
        self.RightSidePanel = RightColumn
        self.RightStack = RightColumn
        self.Sidebar = NavColumn
        self.RightPane = RightColumn
        self.PreviewPane = self.VisionPage
        self.SdkPanel = self.CopilotPage

        RootLayout.addWidget(BodyRow.widget, 1)


        # ── 3. НИЖНІЙ LCARS ФУТЕР
        BottomFrame = Segment(Parent=None)
        BottomFrameLayout = LCARS.Horizontal(BottomFrame.widget)
        BottomFrameLayout.setContentsMargins(0, 0, 0, 0)
        BottomFrameLayout.setSpacing(8)


        BotElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Parent=None)
        BotElbow.widget.setFixedSize(200, 32)
        BottomFrameLayout.addWidget(BotElbow.widget)


        self.FooterBar = LCARSBar(Height=32, Color=Palette.Buttons[4], Parent=None)
        self.FooterBar.widget.setStyleSheet("background-color: " + Palette.Buttons[4] + "; border-radius: 4px;")
        FooterLayout = LCARS.Horizontal(self.FooterBar.widget)
        FooterLayout.setContentsMargins(14, 0, 14, 0)


        self.Status = LCARSLabel(Text="NOVA WORKBENCH READY // STARFLEET REPO CATALOG ONLINE", Color="#000000", FontSize=11, Parent=None)
        FooterLayout.addWidget(self.Status.widget, 1)
        BottomFrameLayout.addWidget(self.FooterBar.widget, 1)


        RootLayout.addWidget(BottomFrame.widget)


    def Bind(self):
        self.BtnNew.Clicked.Connect(self.NewBuffer)
        self.BtnSave.Clicked.Connect(self.SaveFile)
        self.BtnRefresh.Clicked.Connect(self.ReloadCurrentProject)

    # ─────────────────────────────────────────────────────────────────────────
    # ЛОГІКА ПРОЄКТІВ GEANT4 ENTERPRISE
    # ─────────────────────────────────────────────────────────────────────────
    def LoadInitialProject(self):

        self.PopulateProjectsList()


        AllProjects = self.ProjectManager.GetProjectNames()
        Target = "ENX01" if "ENX01" in AllProjects else (AllProjects[0] if AllProjects else "LCARS-CORE")


        self.SelectProject(Target)


    def PopulateProjectsList(self):
        while self.ProjectsLayout.count() > 0:
            Item = self.ProjectsLayout.takeAt(0)
            if Item and Item.widget():
                Item.widget().deleteLater()

        Names = self.ProjectManager.GetProjectNames()
        if "LCARS-CORE" not in Names:
            Names.append("LCARS-CORE")

        for Name in Names:
            Btn = LCARSButton(Text=Name, Form=LCARSButton.Soft, Color=Palette.Buttons[1], Parent=None)
            Btn.widget.setFixedHeight(24)
            n = Name
            Btn.Clicked.Connect(lambda *_, p=n: self.SelectProject(p))
            self.ProjectButtons[Name] = Btn
            self.ProjectsLayout.addWidget(Btn.widget)

        self.ProjectsLayout.addStretch(1)

    def SelectProject(self, ProjectName: str):

        ActiveAudio.play("click")
        for Name, Btn in self.ProjectButtons.items():
            if hasattr(Btn, "SetColor"):
                Btn.SetColor(Palette.Buttons[0] if Name == ProjectName else Palette.Buttons[1])

        if ProjectName == "LCARS-CORE":
            self.CurrentProject = ProjectInfo(
                Name="LCARS-CORE",
                Path=self.ProjectRoot,
                BuildDir=self.ProjectRoot / ".venv",
                Executable=self.ProjectRoot / "start_lcars.py",
                Description="LCARS Framework Starfleet Core System"
            )
        else:
            self.CurrentProject = self.ProjectManager.GetProject(ProjectName)

        if not self.CurrentProject:
            return

        self.CurrentProjectRoot = self.CurrentProject.Path

        Desc = (self.CurrentProject.Description or "").replace("# ", "").replace("\n", " ").strip()
        ExecStatus = "[COMPILED // READY]" if (self.CurrentProject.Executable and self.CurrentProject.Executable.exists()) else "[BUILD REQUIRED]"
        self.ProjectInfoCard.SetText(f"ACTIVE: {ProjectName} {ExecStatus}\n{Desc[:65]}")
        self.HeaderTelemetry.SetText(f"PROJECT: {ProjectName} // {ExecStatus} // {self.CurrentProjectRoot.name}")
        self.ConsoleTitle.SetText(f"◤ COMPILER STREAM // {ProjectName} ({self.CurrentProjectRoot.name})")


        self.LoadProjectFiles(self.CurrentProjectRoot)

        Candidates = [
            self.CurrentProjectRoot / f"{ProjectName}.cc",
            self.CurrentProjectRoot / f"{ProjectName}.cpp",
            self.CurrentProjectRoot / "CMakeLists.txt",
            self.CurrentProjectRoot / "start_lcars.py",
            self.CurrentProjectRoot / "main.py"
        ]
        Opened = False
        for Cand in Candidates:
            if Cand.exists():
                self.OpenFile(Cand)
                Opened = True
                break

        if not Opened:
            for Item in sorted(self.CurrentProjectRoot.iterdir()):
                if Item.is_file() and not Item.name.startswith("."):
                    self.OpenFile(Item)
                    break

        self.SetStatus(f"MISSION LOADED // {ProjectName}")

    def ReloadCurrentProject(self):
        if self.CurrentProject:
            self.SelectProject(self.CurrentProject.Name)

    def LoadProjectFiles(self, TargetDir: Path):
        while self.FilesLayout.count() > 0:
            Item = self.FilesLayout.takeAt(0)
            if Item and Item.widget():
                Item.widget().deleteLater()
        self.FileButtons.clear()

        if not TargetDir.exists():
            return

        Items = sorted(list(TargetDir.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        IgnoreDirs = {".git", ".vs", ".vscode", "__pycache__", ".venv", "venv"}

        for Item in Items:
            if Item.name.startswith(".") or Item.name in IgnoreDirs:
                continue

            if Item.is_dir():
                Label = f"📁 {Item.name}/"
                Color = Palette.Buttons[3]
                Btn = LCARSButton(Text=Label, Form=LCARSButton.Soft, Color=Color, Parent=None)
                Btn.widget.setFixedHeight(24)
                p = Item
                Btn.Clicked.Connect(lambda *_, d=p: self.LoadProjectFiles(d))
                self.FilesLayout.addWidget(Btn.widget)
                self.FileButtons.append(Btn)
            else:
                Ext = Item.suffix.lower()
                Color = Palette.Buttons[0]
                Prefix = "📄 "
                if Ext in (".cc", ".cpp", ".c", ".cxx"):
                    Color = Palette.Buttons[0]
                    Prefix = "⚡ "
                elif Ext in (".hh", ".hpp", ".h"):
                    Color = Palette.Buttons[1]
                    Prefix = "🔷 "
                elif Ext in (".mac", ".dat"):
                    Color = Palette.Buttons[4]
                    Prefix = "⚛️ "
                elif Ext in (".cmake", ".txt"):
                    Color = Palette.Buttons[2]
                    Prefix = "⚙️ "
                elif Ext == ".py":
                    Color = Palette.Buttons[1]
                    Prefix = "🐍 "

                Btn = LCARSButton(Text=f"{Prefix}{Item.name}", Form=LCARSButton.Soft, Color=Color, Parent=None)
                Btn.widget.setFixedHeight(24)
                f = Item
                Btn.Clicked.Connect(lambda *_, file_path=f: self.OpenFile(file_path))
                self.FilesLayout.addWidget(Btn.widget)
                self.FileButtons.append(Btn)

        self.FilesLayout.addStretch(1)

    # ─────────────────────────────────────────────────────────────────────────
    # РЕДАКТОР КОДУ ТА ВКЛАДКИ
    # ─────────────────────────────────────────────────────────────────────────
    def OpenFile(self, FilePath: Path):

        File = Path(FilePath).resolve()
        if not File.exists() or not File.is_file():
            return

        if self.CurrentFile and self.Editor:
            self.Editors[self.CurrentFile] = self.Editor.toPlainText()


        Content = File.read_text(encoding="utf-8", errors="replace")


        self.Editor.setPlainText(Content)
        self.CurrentFile = File


        if hasattr(self, "State") and hasattr(self.State, "SetFile"):
            self.State.SetFile(File)


        self.UpdateTabBar()


        self.SwitchMode("CODE")


        self.UpdateEditorStats()


        self.SetStatus(f"ACTIVE FILE // {File.name}")


    def UpdateTabBar(self):
        for Btn in self.TabButtons:
            if hasattr(Btn, "widget") and Btn.widget:
                if hasattr(self.TabHeaderLayout, "removeItem"):
                    self.TabHeaderLayout.removeItem(Btn.widget)
                Btn.widget.deleteLater()
        self.TabButtons.clear()

        OpenPaths = list(self.Editors.keys())
        if self.CurrentFile and self.CurrentFile not in OpenPaths:
            OpenPaths.append(self.CurrentFile)

        for p in OpenPaths:
            IsActive = (p == self.CurrentFile)
            Color = Palette.Buttons[0] if IsActive else Palette.Buttons[3]
            TabBtn = LCARSButton(Text=f"{p.name} ×", Form=LCARSButton.Pill, Color=Color, Parent=None)
            TabBtn.widget.setFixedHeight(26)
            f = p
            TabBtn.Clicked.Connect(lambda *_, target=f: self.OpenFile(target))
            idx = max(0, self.TabHeaderLayout.count() - 1)
            if hasattr(self.TabHeaderLayout, "insertWidget"):
                self.TabHeaderLayout.insertWidget(idx, TabBtn.widget)
            elif hasattr(self.TabHeaderLayout, "addWidget"):
                self.TabHeaderLayout.addWidget(TabBtn.widget)
            self.TabButtons.append(TabBtn)

    def UpdateEditorStats(self):
        if not self.Editor:
            return
        Cursor = self.Editor.textCursor() if hasattr(self.Editor, "textCursor") else None
        Line = (Cursor.blockNumber() + 1) if Cursor else 1
        Col = (Cursor.columnNumber() + 1) if Cursor else 1
        TotalLines = self.Editor.document().blockCount() if hasattr(self.Editor, "document") else 1
        Name = self.CurrentFile.name if self.CurrentFile else "UNSAVED"
        Ext = self.CurrentFile.suffix.upper() if self.CurrentFile else "TXT"
        SizeKb = (self.CurrentFile.stat().st_size / 1024.0) if (self.CurrentFile and self.CurrentFile.exists()) else 0.0

        self.EditorStats.SetText(f"FILE: {Name} | LN: {Line}, COL: {Col} | LINES: {TotalLines} | {Ext} | {SizeKb:.1f} KB | UTF-8")

    def SaveFile(self, *Args):
        if not self.Editor:
            return
        if not self.CurrentFile:
            Scratch = self.ProjectRoot / "scratch" / "untitled.py"
            Scratch.parent.mkdir(parents=True, exist_ok=True)
            self.CurrentFile = Scratch

        Content = self.Editor.toPlainText()
        self.CurrentFile.write_text(Content, encoding="utf-8")
        ActiveAudio.play("click")
        self.AppendLog(f"✓ [SAVED] {self.CurrentFile.name} ({len(Content)} chars)")
        self.SetStatus(f"SAVED // {self.CurrentFile.name}")

    def NewBuffer(self, *Args):
        Scratch = self.ProjectRoot / "scratch"
        Scratch.mkdir(parents=True, exist_ok=True)
        Num = len(list(Scratch.glob("untitled_*.py"))) + 1
        NewPath = Scratch / f"untitled_{Num}.py"
        Template = "# ◤ LCARS NOVA BUFFER\n\ndef main():\n    print('Hello Starfleet!')\n\nif __name__ == '__main__':\n    main()\n"
        NewPath.write_text(Template, encoding="utf-8")
        self.OpenFile(NewPath)
        self.AppendLog(f"✓ [NEW BUFFER CREATED] {NewPath.name}")

    # ─────────────────────────────────────────────────────────────────────────
    # СИСТЕМА КОМПІЛЯЦІЇ ТА СИМУЛЯЦІЇ
    # ─────────────────────────────────────────────────────────────────────────
    def BuildCurrentProject(self):
        if not self.CurrentProject:
            self.AppendLog(">> [BUILD] NO ACTIVE PROJECT SELECTED.")
            return

        ProjDir = self.CurrentProject.Path
        BuildDir = self.CurrentProject.BuildDir or (ProjDir / "build")
        BuildBat = ProjDir / f"build_{self.CurrentProject.Name}.bat"

        self.AppendLog(f"\n◤ INITIATING BUILD SEQUENCE // {self.CurrentProject.Name} 🖖")
        self.SetStatus(f"BUILDING // {self.CurrentProject.Name}...")

        if BuildBat.exists():
            self.AppendLog(f">> EXECUTING BUILD SCRIPT: {BuildBat.name}...")
            self.SpawnProcess("cmd.exe", ["/c", str(BuildBat)], ProjDir)
        elif BuildDir.exists():
            self.AppendLog(f">> EXECUTING CMAKE BUILD IN: {BuildDir}...")
            self.SpawnProcess("cmake", ["--build", str(BuildDir), "--config", "Release"], ProjDir)
        else:
            self.AppendLog(f">> EXECUTING CMAKE GENERATION & BUILD IN: {ProjDir}...")
            self.SpawnProcess("cmake", ["-B", "build", "-DCMAKE_BUILD_TYPE=Release"], ProjDir)

    def RunSimulation(self):
        if not self.CurrentProject:
            self.AppendLog(">> [SIMULATION] NO ACTIVE PROJECT SELECTED.")
            return

        ExePath = self.CurrentProject.Executable
        if not ExePath or not ExePath.exists():
            ExePath = self.ProjectManager.FindExecutable(self.CurrentProject.Path, self.CurrentProject.Name)

        if ExePath and ExePath.exists():
            self.AppendLog(f"\n◤ LAUNCHING GEANT4 SIMULATION // {ExePath.name} 🖖")
            self.SetStatus(f"RUNNING // {ExePath.name}...")
            Args = ["1.0", "100"] if "ENX" in self.CurrentProject.Name else []
            self.SpawnProcess(str(ExePath), Args, ExePath.parent)
        else:
            self.AppendLog(f">> [RUN ERROR] EXECUTABLE FOR {self.CurrentProject.Name} NOT FOUND. RUN 'BUILD (CMake)' FIRST.")
            self.SetStatus(f"EXECUTABLE MISSING // {self.CurrentProject.Name}")

    def RunScript(self):
        if not self.CurrentFile:
            self.AppendLog(">> [RUN SCRIPT] NO SCRIPT OPEN IN EDITOR.")
            return
        self.SaveFile()
        self.AppendLog(f"\n◤ EXECUTING PYTHON SCRIPT // {self.CurrentFile.name} 🖖")
        self.SetStatus(f"RUNNING // {self.CurrentFile.name}...")
        self.SpawnProcess(sys.executable, [str(self.CurrentFile)], self.CurrentFile.parent)

    def SpawnProcess(self, Program: str, Args: List[str], WorkingDir: Path):
        self.KillActiveProcess()

        Proc = LCARS.Core.Process()
        self.ActiveProcess = Proc
        Proc.setProgram(Program)
        Proc.setArguments(Args)
        Proc.setWorkingDirectory(str(WorkingDir))

        if hasattr(Proc, "setProcessChannelMode") and hasattr(LCARS.Core.Process, "ProcessChannelMode"):
            Proc.setProcessChannelMode(LCARS.Core.Process.ProcessChannelMode.MergedChannels)

        def OnReadyRead():
            Raw = bytes(Proc.readAllStandardOutput())
            if Raw:
                Text = Raw.decode("utf-8", errors="replace")
                for Line in Text.splitlines():
                    self.AppendLog(Line)

        def OnFinished(ExitCode, ExitStatus):
            CodeStr = str(ExitCode)
            if ExitCode == 0:
                self.AppendLog(f"\n✓ [PROCESS TERMINATED NOMINALLY] EXIT CODE: {CodeStr} [OK]")
                self.SetStatus("PROCESS COMPLETED // NOMINAL")
            else:
                self.AppendLog(f"\n⚠️ [PROCESS EXITED WITH CODE {CodeStr}]")
                self.SetStatus(f"PROCESS FINISHED // CODE {CodeStr}")
            self.ActiveProcess = None

        Proc.readyReadStandardOutput.connect(OnReadyRead)
        Proc.finished.connect(OnFinished)
        Proc.start()

    def KillActiveProcess(self):
        if self.ActiveProcess:
            self.AppendLog(">> [STOPPING ACTIVE PROCESS]...")
            self.ActiveProcess.kill()
            self.ActiveProcess = None

    def ClearTerminal(self):
        if self.TerminalDisplay:
            self.TerminalDisplay.clear()
            self.AppendLog("◤ ODN LOG PURGED // STREAM READY 🖖")

    def AppendLog(self, Message: str):
        if self.TerminalDisplay:
            self.TerminalDisplay.append(str(Message))

    # ─────────────────────────────────────────────────────────────────────────
    # НАВІГАЦІЯ ТА РЕЖИМИ
    # ─────────────────────────────────────────────────────────────────────────
    def SwitchMode(self, ModeKey: str):
        self.ActiveWorkspaceMode = ModeKey
        CleanMode = str(ModeKey).upper().strip()

        for MKey, Btn in self.ModeButtons.items():
            if hasattr(Btn, "SetColor"):
                Btn.SetColor(Palette.Buttons[0] if MKey == ModeKey else Palette.Buttons[1])

        RightMap = {
            "DESIGN": getattr(self, "DesignPage", None),
            "VISOR": getattr(self, "VisionPage", None),
            "COLOR_LAB": getattr(self, "LabPage", None),
            "AST_SENTINEL": getattr(self, "CopilotPage", None),
        }

        if hasattr(self, "RightColumn") and hasattr(self.RightColumn, "widget"):
            self.RightColumn.widget.show()
            if hasattr(self, "BtnToggleRight") and hasattr(self.BtnToggleRight, "SetText"):
                self.BtnToggleRight.SetText("COLLAPSE")

        TargetPage = RightMap.get(CleanMode, getattr(self, "CopilotPage", None))
        for page in (getattr(self, "DesignPage", None), getattr(self, "VisionPage", None), getattr(self, "LabPage", None), getattr(self, "CopilotPage", None)):
            if page and hasattr(page, "widget") and page.widget:
                page.widget.setVisible(page == TargetPage)

        if hasattr(self, "RightTitleLabel") and self.RightTitleLabel:
            self.RightTitleLabel.SetText(f"◤ {CleanMode} // LIVE WORKBENCH")

        self.SetStatus(f"ACTIVE WORKSPACE // {ModeKey}")

    def ToggleRightPane(self):
        if hasattr(self, "RightColumn") and hasattr(self.RightColumn, "widget"):
            IsVis = self.RightColumn.widget.isVisible()
            self.RightColumn.widget.setVisible(not IsVis)
            if hasattr(self, "BtnToggleRight") and hasattr(self.BtnToggleRight, "SetText"):
                self.BtnToggleRight.SetText("EXPAND" if IsVis else "COLLAPSE")


    def ReturnToDesktop(self):
        ActiveAudio.play("acknowledge")
        ODN.Emit("System.Phase.Desktop", Station="WELCOME")

    def ReturnToTerminal(self):
        ActiveAudio.play("acknowledge")
        ODN.Emit("System.Command.Terminal")
        ODN.Emit("System.Phase.Desktop", Station="CONSOLE")

    def SetStatus(self, Text: str):
        if hasattr(self, "Status") and self.Status:
            self.Status.SetText(str(Text))

    def OnVisionData(self, *Args, **Kwargs):
        pass

    def OnThemeExported(self, *Args, **Kwargs):
        pass

    def SubmitBottomConsolePrompt(self, *Args):
        if not hasattr(self, "ConsoleInput") or not self.ConsoleInput:
            return
        Text = self.ConsoleInput.toPlainText().strip() if hasattr(self.ConsoleInput, "toPlainText") else ""
        if not Text:
            return
        self.ConsoleInput.clear()
        self.AppendLog(f"\n◤ USER DIRECTIVE: {Text}")
        self.ExecuteDirectiveInNova(Text, TargetDisplay=self.TerminalDisplay)

    def SubmitCopilotPrompt(self, PromptText: str = ""):
        Text = PromptText
        if not Text and hasattr(self, "CopilotInput") and self.CopilotInput:
            Text = self.CopilotInput.toPlainText().strip() if hasattr(self.CopilotInput, "toPlainText") else ""
            self.CopilotInput.clear()
        if not Text:
            return
        if hasattr(self, "CopilotDisplay") and self.CopilotDisplay:
            self.CopilotDisplay.append(f"\n◤ DIRECTIVE: {Text}")
        self.ExecuteDirectiveInNova(Text, TargetDisplay=getattr(self, "CopilotDisplay", None))

    def ExecuteDirectiveInNova(self, DirectiveText: str, TargetDisplay=None):
        ActiveAudio.play("input")
        self.SetStatus("PROCESSING DIRECTIVE // ODN TRANSMISSION")
        
        def RunWorker():
            try:
                Computer = self.Computer or BoardComputer.GetInstance()
                Ans = Computer.AskNeuralCore(
                    DirectiveText,
                    StreamCallback=lambda chunk: self.DispatchToConsole(chunk, TargetDisplay)
                )
                self.DispatchToConsole(f"\n{Ans}", TargetDisplay)
                self.SetStatus("DIRECTIVE COMPLETED // READY")
            except Exception as e:
                self.DispatchToConsole(f"\n◤ LCARS ERROR 🖖: {str(e)}", TargetDisplay)
                self.SetStatus("DIRECTIVE ERROR")

        ThreadClass = LCARS.System.Thread if hasattr(LCARS.System, "Thread") else None
        if ThreadClass:
            T = ThreadClass(target=RunWorker, daemon=True)
            T.start()
        else:
            RunWorker()

    def DispatchToConsole(self, Text: str, TargetDisplay=None):
        if TargetDisplay:
            TargetDisplay.append(str(Text))
        elif self.TerminalDisplay:
            self.TerminalDisplay.append(str(Text))


NovaIDE = NovaPanel
