# ◤ TITANIUM LCARS :: CONTROL APPLICATION VIEWS 🖖
# =============================================================================
# ФАЙЛ: programs/Control/views.py
# ПРИЗНАЧЕННЯ: 7 повнофункціональних робочих станцій для LCARS Control:
#              1. StatusView (Метрики DataBlock, Gateway Daemon, Шляхи, GATEWAY DAEMON TERM)
#              2. AgentView (Внутрішні та зовнішні CLI агенти, налаштування, ConPTY)
#              3. ChannelsView (Оркестрація каналів зв'язку ODN, HTTP RPC, WebSocket)
#              4. SubscriptionsView (Керування API-ключами AI-провайдерів та пінг)
#              5. EnvironmentView (Інтерактивний редактор змінних середовища .env)
#              6. DashboardView (Телеметрія хоста CPU/RAM, менеджмент LCARS та Geant4)
#              7. CockpitView (Прямий інтерактивний чат і дошка директив)
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# ГРАФІКА: Автентичні об'єкти Okuda LCARS, велика типографіка, жодних емодзі.
# =============================================================================

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel, LCARSIndicator, ActiveAudio
from lcars.base.interface import ScanningBar, DataBlock
from .daemon import GatewayDaemon


class StatusView:
    def __init__(self, ParentWidget=None, OnSwitchTab=None):
        self.ParentWidget = ParentWidget
        self.OnSwitchTab = OnSwitchTab
        self.Daemon = GatewayDaemon.GetInstance()
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.LogsCache = []
        self.UptimeBlock = None
        self.StatusIndicator = None
        self.PidLabel = None
        self.TerminalBox = None
        self.SearchInput = None
        self.UpdateTimer = None

        self.Daemon.RegisterLogCallback(self.OnDaemonLogReceived)
        self.Build()
        self.StartTimer()

    def Build(self):
        MainLayout = LCARS.Vertical(self.Widget)
        MainLayout.setContentsMargins(16, 12, 16, 12)
        MainLayout.setSpacing(10)

        # 1. ЗАГОЛОВОК СТАНЦІЇ ЗІ СКАНУВАЛЬНОЮ СМУГОЮ
        HeaderRow = LCARS.Widget(self.Widget)
        HeaderRow.setFixedHeight(44)
        HeaderRow.setStyleSheet("background-color: transparent;")
        HeaderLayout = LCARS.Horizontal(HeaderRow)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(10)

        Badge = LCARSButton(Text="LCARS CORE", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="01-POST", CornerRadius=4, Parent=HeaderRow)
        Badge.widget.setFixedSize(140, 38)
        HeaderLayout.addWidget(Badge.widget)

        Title = LCARSLabel(Text="GATEWAY ARCHITECTURE & DAEMON TELEMETRY", Color="#FFFFFF", FontSize=16, Parent=HeaderRow)
        HeaderLayout.addWidget(Title.widget)
        HeaderLayout.addStretch(1)

        self.PidLabel = LCARSLabel(Text="PID: STANDBY", Color=Palette.Buttons[6], FontSize=12, Parent=HeaderRow)
        HeaderLayout.addWidget(self.PidLabel.widget)

        self.StatusIndicator = LCARSButton(Text="GATEWAY OFFLINE", Form=LCARSButton.Soft, Color=Palette.Red[0], Number="47-OFF", CornerRadius=4, Parent=HeaderRow)
        self.StatusIndicator.widget.setFixedSize(180, 38)
        HeaderLayout.addWidget(self.StatusIndicator.widget)

        MainLayout.addWidget(HeaderRow)

        Scan = ScanningBar(Color=Palette.Buttons[4], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        MainLayout.addWidget(Scan.widget)

        # 2. ЧОТИРИ ВЕЛИКІ КАРТКИ МЕТРИК DATABLOCK
        MetricsContainer = LCARS.Widget(self.Widget)
        MetricsContainer.setFixedHeight(95)
        MetricsContainer.setStyleSheet("background-color: transparent;")
        MetricsLayout = LCARS.Horizontal(MetricsContainer)
        MetricsLayout.setContentsMargins(0, 0, 0, 0)
        MetricsLayout.setSpacing(10)

        # Картка 1: GATEWAY PORT
        Card1 = LCARS.Widget(MetricsContainer)
        Card1.setStyleSheet("background-color: #03060C; border-left: 6px solid " + Palette.Buttons[1] + "; border-radius: 4px;")
        C1Layout = LCARS.Vertical(Card1)
        C1Layout.setContentsMargins(14, 10, 14, 10)
        C1Layout.setSpacing(2)
        C1Layout.addWidget(LCARSLabel(Text="01 // GATEWAY PORT", Color=Palette.Buttons[1], FontSize=11, Parent=Card1).widget)
        C1Layout.addWidget(LCARSLabel(Text=str(self.Daemon.Port), Color="#FFFFFF", FontSize=24, Parent=Card1).widget)
        C1Layout.addWidget(LCARSLabel(Text="ODN 1024-BIT CARRIER BUS", Color=Palette.Buttons[6], FontSize=9, Parent=Card1).widget)
        MetricsLayout.addWidget(Card1, 1)

        # Картка 2: UPTIME
        Card2 = LCARS.Widget(MetricsContainer)
        Card2.setStyleSheet("background-color: #03060C; border-left: 6px solid " + Palette.Buttons[4] + "; border-radius: 4px;")
        C2Layout = LCARS.Vertical(Card2)
        C2Layout.setContentsMargins(14, 10, 14, 10)
        C2Layout.setSpacing(2)
        C2Layout.addWidget(LCARSLabel(Text="02 // CHRONO UPTIME", Color=Palette.Buttons[4], FontSize=11, Parent=Card2).widget)
        self.UptimeBlock = LCARSLabel(Text="OFFLINE", Color="#FFFFFF", FontSize=24, Parent=Card2)
        C2Layout.addWidget(self.UptimeBlock.widget)
        C2Layout.addWidget(LCARSLabel(Text="CONTINUOUS SERVICE ELAPSED", Color=Palette.Buttons[6], FontSize=9, Parent=Card2).widget)
        MetricsLayout.addWidget(Card2, 1)

        # Картка 3: CHANNELS
        Card3 = LCARS.Widget(MetricsContainer)
        Card3.setStyleSheet("background-color: #03060C; border-left: 6px solid " + Palette.Buttons[2] + "; border-radius: 4px;")
        C3Layout = LCARS.Vertical(Card3)
        C3Layout.setContentsMargins(14, 10, 14, 10)
        C3Layout.setSpacing(2)
        C3Layout.addWidget(LCARSLabel(Text="03 // PROTOCOL CHANNELS", Color=Palette.Buttons[2], FontSize=11, Parent=Card3).widget)
        C3Layout.addWidget(LCARSLabel(Text="4 CHANNELS", Color="#FFFFFF", FontSize=24, Parent=Card3).widget)
        C3Layout.addWidget(LCARSLabel(Text="ODN / HTTP / WS / AI PROXY", Color=Palette.Buttons[6], FontSize=9, Parent=Card3).widget)
        MetricsLayout.addWidget(Card3, 1)

        # Картка 4: GATEWAY VERSION
        Card4 = LCARS.Widget(MetricsContainer)
        Card4.setStyleSheet("background-color: #03060C; border-left: 6px solid " + Palette.Buttons[3] + "; border-radius: 4px;")
        C4Layout = LCARS.Vertical(Card4)
        C4Layout.setContentsMargins(14, 10, 14, 10)
        C4Layout.setSpacing(2)
        C4Layout.addWidget(LCARSLabel(Text="04 // SYSTEM VERSION", Color=Palette.Buttons[3], FontSize=11, Parent=Card4).widget)
        C4Layout.addWidget(LCARSLabel(Text="v2.9.37 STABLE", Color="#FFFFFF", FontSize=24, Parent=Card4).widget)
        C4Layout.addWidget(LCARSLabel(Text="TITANIUM STANDARD KERNEL", Color=Palette.Buttons[6], FontSize=9, Parent=Card4).widget)
        MetricsLayout.addWidget(Card4, 1)

        MainLayout.addWidget(MetricsContainer)

        # 3. ОСНОВНІ КНОПКИ УПРАВЛІННЯ ДЕМОНОМ (ВЕЛИКІ LCARS КНОПКИ)
        ActionsRow = LCARS.Widget(self.Widget)
        ActionsRow.setFixedHeight(46)
        ActionsRow.setStyleSheet("background-color: transparent;")
        ActionsLayout = LCARS.Horizontal(ActionsRow)
        ActionsLayout.setContentsMargins(0, 0, 0, 0)
        ActionsLayout.setSpacing(8)

        BtnStart = LCARSButton(Text="START DAEMON", Form=LCARSButton.Soft, Color="#00AA66", Number="47-01", CornerRadius=4, Parent=ActionsRow)
        BtnStart.widget.setFixedSize(170, 42)
        BtnStart.Clicked.Connect(self.OnStartClicked)
        ActionsLayout.addWidget(BtnStart.widget)

        BtnStop = LCARSButton(Text="STOP DAEMON", Form=LCARSButton.Soft, Color=Palette.Red[0], Number="47-02", CornerRadius=4, Parent=ActionsRow)
        BtnStop.widget.setFixedSize(170, 42)
        BtnStop.Clicked.Connect(self.OnStopClicked)
        ActionsLayout.addWidget(BtnStop.widget)

        BtnRestart = LCARSButton(Text="RESTART DAEMON", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="47-03", CornerRadius=4, Parent=ActionsRow)
        BtnRestart.widget.setFixedSize(180, 42)
        BtnRestart.Clicked.Connect(self.OnRestartClicked)
        ActionsLayout.addWidget(BtnRestart.widget)

        ActionsLayout.addStretch(1)

        BtnOpenBrowser = LCARSButton(Text="OPEN IN BROWSER", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="47-04", CornerRadius=4, Parent=ActionsRow)
        BtnOpenBrowser.widget.setFixedSize(190, 42)
        BtnOpenBrowser.Clicked.Connect(self.OnOpenBrowserClicked)
        ActionsLayout.addWidget(BtnOpenBrowser.widget)

        BtnOpenDash = LCARSButton(Text="OPEN DASHBOARD", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Number="47-05", CornerRadius=4, Parent=ActionsRow)
        BtnOpenDash.widget.setFixedSize(180, 42)
        if callable(self.OnSwitchTab):
            BtnOpenDash.Clicked.Connect(lambda: self.OnSwitchTab("Dashboard"))
        ActionsLayout.addWidget(BtnOpenDash.widget)

        BtnRefresh = LCARSButton(Text="REFRESH", Form=LCARSButton.Soft, Color=Palette.Buttons[6], Number="47-06", CornerRadius=4, Parent=ActionsRow)
        BtnRefresh.widget.setFixedSize(110, 42)
        BtnRefresh.Clicked.Connect(self.UpdateStatus)
        ActionsLayout.addWidget(BtnRefresh.widget)

        MainLayout.addWidget(ActionsRow)

        # 4. ШЛЯХИ BINARY ТА DATA DIR (АВТЕНТИЧНІ СМУГИ З КНОПКАМИ ACCESS)
        PathsContainer = LCARS.Widget(self.Widget)
        PathsContainer.setFixedHeight(76)
        PathsContainer.setStyleSheet("background-color: #020408; border-left: 6px solid " + Palette.Buttons[1] + "; border-radius: 4px;")
        PathsLayout = LCARS.Vertical(PathsContainer)
        PathsLayout.setContentsMargins(14, 8, 14, 8)
        PathsLayout.setSpacing(6)

        # Рядок Binary
        PathMod = LCARS.Import("pathlib").Path
        BinaryRow = LCARS.Widget(PathsContainer)
        BinaryRow.setStyleSheet("background-color: transparent;")
        BRLayout = LCARS.Horizontal(BinaryRow)
        BRLayout.setContentsMargins(0, 0, 0, 0)
        BRLayout.setSpacing(10)
        BRLayout.addWidget(LCARSLabel(Text="CANONICAL GATEWAY:", Color=Palette.Buttons[4], FontSize=11, Parent=BinaryRow).widget)
        NetworkModulePath = PathMod(__file__).resolve().parents[2] / "lcars" / "service" / "network.py"
        BRLayout.addWidget(LCARSLabel(Text=str(NetworkModulePath), Color="#CCCCCC", FontSize=11, Parent=BinaryRow).widget, 1)
        BtnOpenBin = LCARSButton(Text="ACCESS MODULE", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Number="DIR-01", CornerRadius=3, Parent=BinaryRow)
        BtnOpenBin.widget.setFixedSize(170, 26)
        BtnOpenBin.Clicked.Connect(lambda: self.OpenFolder(NetworkModulePath, IsFile=True))
        BRLayout.addWidget(BtnOpenBin.widget)
        PathsLayout.addWidget(BinaryRow)

        # Рядок Data dir
        DataRow = LCARS.Widget(PathsContainer)
        DataRow.setStyleSheet("background-color: transparent;")
        DRLayout = LCARS.Horizontal(DataRow)
        DRLayout.setContentsMargins(0, 0, 0, 0)
        DRLayout.setSpacing(10)
        DRLayout.addWidget(LCARSLabel(Text="DATA REPOSITORY: ", Color=Palette.Buttons[2], FontSize=11, Parent=DataRow).widget)
        PathMod = LCARS.Import("pathlib").Path
        ProjectRoot = PathMod(__file__).resolve().parents[2]
        DRLayout.addWidget(LCARSLabel(Text=str(ProjectRoot), Color="#CCCCCC", FontSize=11, Parent=DataRow).widget, 1)
        BtnOpenData = LCARSButton(Text="ACCESS REPOSITORY", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Number="DIR-02", CornerRadius=3, Parent=DataRow)
        BtnOpenData.widget.setFixedSize(170, 26)
        BtnOpenData.Clicked.Connect(lambda: self.OpenFolder(ProjectRoot, IsFile=False))
        DRLayout.addWidget(BtnOpenData.widget)
        PathsLayout.addWidget(DataRow)

        MainLayout.addWidget(PathsContainer)

        # 5. GATEWAY DAEMON TERM
        TermContainer = LCARS.Widget(self.Widget)
        TermContainer.setStyleSheet("background-color: #020408; border: 1px solid #142840; border-radius: 4px;")
        TermLayout = LCARS.Vertical(TermContainer)
        TermLayout.setContentsMargins(12, 10, 12, 10)
        TermLayout.setSpacing(8)

        # Хедер терміналу
        TermHeader = LCARS.Widget(TermContainer)
        TermHeader.setFixedHeight(36)
        TermHeader.setStyleSheet("background-color: transparent;")
        THLayout = LCARS.Horizontal(TermHeader)
        THLayout.setContentsMargins(0, 0, 0, 0)
        THLayout.setSpacing(8)

        THLayout.addWidget(LCARSLabel(Text=">_ GATEWAY DAEMON TERMINAL CONDUIT", Color=Palette.Buttons[4], FontSize=13, Parent=TermHeader).widget)
        THLayout.addStretch(1)

        self.SearchInput = LCARS.Input(TermHeader)
        self.SearchInput.setPlaceholderText("Filter daemon buffer...")
        self.SearchInput.setStyleSheet("background-color: #040810; color: #99CCFF; border: 1px solid #1E3A5F; padding: 4px 10px; font-size: 10pt; border-radius: 4px;")
        self.SearchInput.setFixedWidth(220)
        if hasattr(self.SearchInput, "textChanged"):
            self.SearchInput.textChanged.connect(self.FilterLogs)
        THLayout.addWidget(self.SearchInput)

        BtnCopy = LCARSButton(Text="COPY BUFFER", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="47-10", CornerRadius=3, Parent=TermHeader)
        BtnCopy.widget.setFixedSize(130, 32)
        BtnCopy.Clicked.Connect(self.CopyLogs)
        THLayout.addWidget(BtnCopy.widget)

        BtnClear = LCARSButton(Text="PURGE BUFFER", Form=LCARSButton.Soft, Color=Palette.Red[0], Number="47-11", CornerRadius=3, Parent=TermHeader)
        BtnClear.widget.setFixedSize(140, 32)
        BtnClear.Clicked.Connect(self.ClearLogs)
        THLayout.addWidget(BtnClear.widget)

        TermLayout.addWidget(TermHeader)

        # Сам термінал
        self.TerminalBox = LCARS.Terminal(TermContainer)
        self.TerminalBox.setReadOnly(True)
        FontFamily = "'Consolas', 'Courier New', 'Bahnschrift', monospace"
        self.TerminalBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #0D1B2A; font-size: 12px; font-family: " + FontFamily + "; padding: 10px; line-height: 140%;")
        self.TerminalBox.append("◤ GATEWAY DAEMON STANDBY. Initiate Start Daemon to establish telemetry carrier.")
        TermLayout.addWidget(self.TerminalBox, 1)

        MainLayout.addWidget(TermContainer, 1)

    def StartTimer(self):
        self.UpdateTimer = LCARS.Timer(self.Widget)
        self.UpdateTimer.setInterval(1000)
        self.UpdateTimer.timeout.connect(self.UpdateStatus)
        self.UpdateTimer.start()

    def UpdateStatus(self):
        IsLive = self.Daemon.IsActive()
        if IsLive:
            self.StatusIndicator.SetText("GATEWAY ONLINE")
            self.StatusIndicator.SetColor("#00CC66")
            PidVal = self.Daemon.GetPid()
            self.PidLabel.SetText("PID: " + str(PidVal) if PidVal else "PID: ACTIVE")
            self.UptimeBlock.SetText(self.Daemon.GetFormattedUptime())
        else:
            self.StatusIndicator.SetText("GATEWAY OFFLINE")
            self.StatusIndicator.SetColor(Palette.Red[0])
            self.PidLabel.SetText("PID: STANDBY")
            self.UptimeBlock.SetText("OFFLINE")

    def OnStartClicked(self):
        ActiveAudio.play("click")
        if not self.Daemon.IsActive():
            if len(self.LogsCache) == 0:
                self.TerminalBox.clear()
        self.Daemon.StartDaemon()
        self.UpdateStatus()

    def OnStopClicked(self):
        ActiveAudio.play("click")
        self.Daemon.StopDaemon()
        self.UpdateStatus()

    def OnRestartClicked(self):
        ActiveAudio.play("click")
        self.Daemon.RestartDaemon()
        self.UpdateStatus()

    def OnOpenBrowserClicked(self):
        ActiveAudio.play("click")
        WebbrowserMod = LCARS.Import("webbrowser")
        TargetUrl = "http://127.0.0.1:" + str(self.Daemon.Port)
        if WebbrowserMod and hasattr(WebbrowserMod, "open"):
            WebbrowserMod.open(TargetUrl)
            self.Daemon.DispatchLog(">> Opened gateway URL in browser: " + TargetUrl)

    def OpenFolder(self, TargetPath, IsFile=False):
        ActiveAudio.play("click")
        OsMod = LCARS.Import("os")
        PathMod = LCARS.Import("pathlib").Path
        Resolved = PathMod(str(TargetPath))
        if IsFile:
            Resolved = Resolved.parent
        if OsMod and hasattr(OsMod, "startfile") and Resolved.exists():
            OsMod.startfile(str(Resolved))
            self.Daemon.DispatchLog(">> Opened Explorer folder: " + str(Resolved))

    def OnDaemonLogReceived(self, LogLine):
        self.LogsCache.append(LogLine)
        if len(self.LogsCache) > 1000:
            self.LogsCache.pop(0)
        Query = str(self.SearchInput.text()).strip().lower() if self.SearchInput and hasattr(self.SearchInput, "text") else ""
        if not Query or Query in LogLine.lower():
            if hasattr(self.TerminalBox, "append"):
                self.TerminalBox.append(LogLine)

    def FilterLogs(self, SearchQueryText):
        Query = str(SearchQueryText or "").strip().lower()
        self.TerminalBox.clear()
        for Line in self.LogsCache:
            if not Query or Query in Line.lower():
                self.TerminalBox.append(Line)

    def CopyLogs(self):
        ActiveAudio.play("click")
        App = LCARS.Application.instance()
        if App and hasattr(App, "clipboard"):
            Clipboard = App.clipboard()
            if Clipboard and hasattr(Clipboard, "setText"):
                Clipboard.setText("\n".join(self.LogsCache))
                self.Daemon.DispatchLog(">> Log history copied to clipboard.")

    def ClearLogs(self):
        ActiveAudio.play("click")
        self.LogsCache.clear()
        self.TerminalBox.clear()
        self.TerminalBox.append("◤ GATEWAY DAEMON STANDBY. Initiate Start Daemon to establish telemetry carrier.")


class AgentView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.ActiveAgentKey = "neuralcore"
        self.AgentButtons = {}
        self.DialogueBox = None
        self.DirectiveInput = None
        self.AgentTitleLabel = None
        self.AgentRouteLabel = None
        self.AgentStatusBadge = None
        self.ExecutionThread = None

        self.AgentsDirectory = {
            "neuralcore": {
                "Name": "ONBOARD NEURAL CORE",
                "Type": "INTERNAL SHIP BRAIN",
                "Route": "ODN 1024-BIT SUPERPOSITION",
                "Color": Palette.Buttons[4],
                "Number": "02-01",
                "Description": "Central Sovereign-class quantum computer core with direct neural access to all 13 subsystems.",
                "Category": "INTERNAL"
            },
            "copilot": {
                "Name": "STARFLEET COPILOT",
                "Type": "IN-PROCESS ASSISTANT",
                "Route": "CENTRAL BRIDGE CONDUIT",
                "Color": Palette.Buttons[1],
                "Number": "02-02",
                "Description": "Autonomous software assistant & isolinear circuit generator integrated into the bridge.",
                "Category": "INTERNAL"
            },
            "nova": {
                "Name": "NOVA WORKBENCH",
                "Type": "LOCAL ISOLINEAR ENGINE",
                "Route": "QVAC RPC PORT 3055",
                "Color": Palette.Buttons[2],
                "Number": "02-03",
                "Description": "Local isolinear IDE engine and circuit designer communicating over gateway port 3055.",
                "Category": "INTERNAL"
            },
            "tars": {
                "Name": "TARS TACTICAL AGENT",
                "Type": "AUTONOMOUS UI & SYSTEMS",
                "Route": "ODN TACTICAL PERCEPTION",
                "Color": "#CC9966",
                "Number": "02-04",
                "Description": "Tactical Autonomous Reconnaissance & Systems agent with UI perception and adaptive personality matrix.",
                "Category": "INTERNAL"
            },
            "gemini": {
                "Name": "GOOGLE GEMINI CLI",
                "Type": "DEVELOPER CLI AGENT",
                "Route": "SYSTEM PROCESS PIPE",
                "Color": "#00CC66",
                "Number": "02-05",
                "Description": "Google Gemini developer assistant CLI executing non-interactive directives directly on repository.",
                "Category": "CLI"
            },
            "devin": {
                "Name": "COGNITION DEVIN CLI",
                "Type": "ENGINEERING CLI AGENT",
                "Route": "SYSTEM PROCESS PIPE",
                "Color": "#FF6633",
                "Number": "02-05",
                "Description": "Devin autonomous software engineer executing print-mode directives on the local workspace.",
                "Category": "CLI"
            },
            "opencode": {
                "Name": "OPENCODE AGENT",
                "Type": "CODING CLI AGENT",
                "Route": "SYSTEM PROCESS PIPE",
                "Color": "#33CCFF",
                "Number": "02-06",
                "Description": "Autonomous terminal code engineering agent executing multi-file refactoring runs.",
                "Category": "CLI"
            },
            "claude": {
                "Name": "CLAUDE 3.5 SONNET",
                "Type": "ANTHROPIC REASONING",
                "Route": "OPENROUTER GATEWAY",
                "Color": Palette.Buttons[1],
                "Number": "02-07",
                "Description": "State-of-the-art coding and architecture reasoning model via OpenRouter API.",
                "Category": "CLOUD"
            },
            "gpt4o": {
                "Name": "OPENAI GPT-4O",
                "Type": "FRONTIER MULTIMODAL",
                "Route": "OPENROUTER GATEWAY",
                "Color": Palette.Buttons[4],
                "Number": "02-08",
                "Description": "High-velocity general intelligence and analytical model via OpenRouter API.",
                "Category": "CLOUD"
            },
            "deepseek": {
                "Name": "DEEPSEEK V3",
                "Type": "DEEP COGNITIVE CORE",
                "Route": "OPENROUTER GATEWAY",
                "Color": Palette.Buttons[2],
                "Number": "02-09",
                "Description": "DeepSeek V3 671B mixture-of-experts model for complex algorithmic synthesis.",
                "Category": "CLOUD"
            },
            "groqwen": {
                "Name": "GROQ LLAMA 70B",
                "Type": "ULTRA-FAST LPU",
                "Route": "GROQ TENSOR CLOUD",
                "Color": Palette.Buttons[0],
                "Number": "02-10",
                "Description": "Sub-second inference via Groq Tensor Processing Units for instant directive turnaround.",
                "Category": "CLOUD"
            },
            "mistral": {
                "Name": "MISTRAL CODESTRAL",
                "Type": "SPECIALIZED CODER",
                "Route": "MISTRAL AI CLOUD",
                "Color": Palette.Buttons[3],
                "Number": "02-11",
                "Description": "Specialized programming intelligence model for codebase refactoring and tests.",
                "Category": "CLOUD"
            },
            "astra": {
                "Name": "ASTRA GPT-6",
                "Type": "EXPERIENTIAL LABS CORE",
                "Route": "EXPERIENTIAL CLOUD API",
                "Color": Palette.Buttons[6],
                "Number": "02-12",
                "Description": "GPT-6 Astra frontier deep cognitive model with active subspace uplink.",
                "Category": "CLOUD"
            },
        }

        self.Build()

    def Build(self):
        MainLayout = LCARS.Vertical(self.Widget)
        MainLayout.setContentsMargins(16, 12, 16, 12)
        MainLayout.setSpacing(10)

        # 1. ТОП ХЕДЕР СТАНЦІЇ
        Header = LCARS.Widget(self.Widget)
        Header.setFixedHeight(40)
        Header.setStyleSheet("background-color: transparent;")
        HL = LCARS.Horizontal(Header)
        HL.setContentsMargins(0, 0, 0, 0)
        HL.setSpacing(10)

        Badge = LCARSButton(Text="AGENTS HUB", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="02-ROSTER", CornerRadius=4, Parent=Header)
        Badge.widget.setFixedSize(140, 36)
        HL.addWidget(Badge.widget)

        self.AgentTitleLabel = LCARSLabel(Text="ACTIVE AGENT: ONBOARD NEURAL CORE // SOVEREIGN QUANTUM BRAIN", Color="#FFFFFF", FontSize=15, Parent=Header)
        HL.addWidget(self.AgentTitleLabel.widget, 1)

        self.AgentStatusBadge = LCARSButton(Text="CONDUIT ONLINE", Form=LCARSButton.Soft, Color="#00CC66", Number="SYNC", CornerRadius=3, Parent=Header)
        self.AgentStatusBadge.widget.setFixedSize(160, 36)
        HL.addWidget(self.AgentStatusBadge.widget)

        MainLayout.addWidget(Header)

        Scan = ScanningBar(Color=Palette.Buttons[1], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        MainLayout.addWidget(Scan.widget)

        # 2. ГОЛОВНИЙ РОБОЧИЙ ПРОСТІР: ЛІВИЙ СЕЛЕКТОР АГЕНТІВ + ЦЕНТРАЛЬНА ІНТЕРАКТИВНА СРЕДА
        WorkspaceRow = LCARS.Widget(self.Widget)
        WorkspaceRow.setStyleSheet("background-color: transparent;")
        WRL = LCARS.Horizontal(WorkspaceRow)
        WRL.setContentsMargins(0, 0, 0, 0)
        WRL.setSpacing(12)

        # ЛІВИЙ СЕЛЕКТОР АГЕНТІВ
        RosterScroll = LCARS.Buffer(WorkspaceRow)
        RosterScroll.setFixedWidth(270)
        RosterScroll.setWidgetResizable(True)
        RosterScroll.setStyleSheet("background-color: #000000; border: none;")

        RosterContainer = LCARS.Widget()
        RosterContainer.setStyleSheet("background-color: #000000;")
        RCL = LCARS.Vertical(RosterContainer)
        RCL.setContentsMargins(0, 0, 0, 0)
        RCL.setSpacing(5)

        for AgentKey, AgentMeta in self.AgentsDirectory.items():
            Btn = LCARSButton(
                Text=AgentMeta["Name"],
                Form=LCARSButton.Soft,
                Color=AgentMeta["Color"],
                Number=AgentMeta["Number"],
                CornerRadius=4,
                Parent=RosterContainer
            )
            Btn.widget.setFixedHeight(44)
            TargetKey = AgentKey
            Btn.Clicked.Connect(lambda *Args, K=TargetKey: self.SelectAgent(K))
            self.AgentButtons[AgentKey] = Btn
            RCL.addWidget(Btn.widget)

        RCL.addStretch(1)
        RosterScroll.setWidget(RosterContainer)
        WRL.addWidget(RosterScroll)

        # ПРАВА ІНТЕРАКТИВНА КОНСОЛЬ ВЗАЄМОДІЇ З АГЕНТОМ
        ConsoleContainer = LCARS.Widget(WorkspaceRow)
        ConsoleContainer.setStyleSheet("background-color: #020408; border-left: 6px solid " + Palette.Buttons[4] + "; border-radius: 4px;")
        CCL = LCARS.Vertical(ConsoleContainer)
        CCL.setContentsMargins(14, 10, 14, 10)
        CCL.setSpacing(8)

        # Верхня смуга параметрів активного агента
        BarRow = LCARS.Widget(ConsoleContainer)
        BarRow.setFixedHeight(34)
        BarRow.setStyleSheet("background-color: transparent;")
        BRL = LCARS.Horizontal(BarRow)
        BRL.setContentsMargins(0, 0, 0, 0)
        BRL.setSpacing(8)

        self.AgentRouteLabel = LCARSLabel(Text="ROUTE: ODN 1024-BIT // WORKSPACE: LCARS-FRAMEWORK", Color=Palette.Buttons[4], FontSize=11, Parent=BarRow)
        BRL.addWidget(self.AgentRouteLabel.widget, 1)

        BtnPytest = LCARSButton(Text="RUN PYTEST", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="CMD-01", CornerRadius=3, Parent=BarRow)
        BtnPytest.widget.setFixedSize(130, 30)
        BtnPytest.Clicked.Connect(self.QuickRunPytest)
        BRL.addWidget(BtnPytest.widget)

        BtnClear = LCARSButton(Text="CLEAR CONDUIT", Form=LCARSButton.Soft, Color=Palette.Buttons[0], Number="CMD-02", CornerRadius=3, Parent=BarRow)
        BtnClear.widget.setFixedSize(140, 30)
        BtnClear.Clicked.Connect(self.ClearDialogue)
        BRL.addWidget(BtnClear.widget)

        CCL.addWidget(BarRow)

        # Термінал живого спілкування та міркувань
        self.DialogueBox = LCARS.Terminal(ConsoleContainer)
        self.DialogueBox.setReadOnly(True)
        FontFamily = "'Consolas', 'Courier New', monospace"
        self.DialogueBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #142840; font-size: 13px; font-family: " + FontFamily + "; padding: 12px; line-height: 145%;")
        self.DialogueBox.append("◤ STARFLEET NEURAL AGENT MATRIX ACTIVE.")
        self.DialogueBox.append("   Connected to: ONBOARD NEURAL CORE (NCC-74205). Ready for directives.")
        CCL.addWidget(self.DialogueBox, 1)

        # Рядок введення директиви
        InputRow = LCARS.Widget(ConsoleContainer)
        InputRow.setFixedHeight(48)
        InputRow.setStyleSheet("background-color: transparent;")
        IRL = LCARS.Horizontal(InputRow)
        IRL.setContentsMargins(0, 0, 0, 0)
        IRL.setSpacing(8)

        self.DirectiveInput = LCARS.Input(InputRow)
        self.DirectiveInput.setPlaceholderText("Enter natural directive in Ukrainian or English for active agent...")
        self.DirectiveInput.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #1E3A5F; padding: 6px 12px; font-size: 12pt; border-radius: 4px;")
        if hasattr(self.DirectiveInput, "returnPressed"):
            self.DirectiveInput.returnPressed.connect(self.TransmitDirective)
        IRL.addWidget(self.DirectiveInput, 1)

        BtnSend = LCARSButton(Text="TRANSMIT DIRECTIVE", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="TX-01", CornerRadius=4, Parent=InputRow)
        BtnSend.widget.setFixedSize(200, 44)
        BtnSend.Clicked.Connect(self.TransmitDirective)
        IRL.addWidget(BtnSend.widget)

        CCL.addWidget(InputRow)
        WRL.addWidget(ConsoleContainer, 1)
        MainLayout.addWidget(WorkspaceRow, 1)

        self.HighlightActiveButton()

    def HighlightActiveButton(self):
        for Key, Btn in self.AgentButtons.items():
            if Key == self.ActiveAgentKey:
                Btn.SetColor("#FFFFFF")
            else:
                Meta = self.AgentsDirectory.get(Key, {})
                Btn.SetColor(Meta.get("Color", Palette.Buttons[1]))

    def SelectAgent(self, AgentKey):
        ActiveAudio.play("click")
        if AgentKey not in self.AgentsDirectory:
            return
        self.ActiveAgentKey = AgentKey
        self.HighlightActiveButton()

        Meta = self.AgentsDirectory[AgentKey]
        self.AgentTitleLabel.SetText("ACTIVE AGENT: " + Meta["Name"] + " // " + Meta["Type"])
        self.AgentRouteLabel.SetText("ROUTE: " + Meta["Route"] + " // WORKSPACE: LCARS-FRAMEWORK")

        if Meta["Category"] == "CLOUD":
            ProviderMod = LCARS.Import("lcars.service.provider")
            if ProviderMod and hasattr(ProviderMod, "AIProviderManager"):
                AiMgr = ProviderMod.AIProviderManager.GetInstance()
                if AiMgr:
                    AiMgr.SwitchModel(AgentKey)

        self.DialogueBox.append("\n" + "=" * 70)
        self.DialogueBox.append("◤ NEURAL CONDUIT COMMUTED TO: [" + Meta["Name"] + "]")
        self.DialogueBox.append("   Designation: " + Meta["Type"] + " // Route: " + Meta["Route"])
        self.DialogueBox.append("   " + Meta["Description"])
        self.DialogueBox.append("=" * 70 + "\n")

    def ClearDialogue(self):
        ActiveAudio.play("click")
        self.DialogueBox.clear()
        Meta = self.AgentsDirectory.get(self.ActiveAgentKey, {})
        self.DialogueBox.append("◤ CONDUIT BUFFER PURGED. Active Agent: " + Meta.get("Name", "STANDBY") + "\n")

    def QuickRunPytest(self):
        self.DirectiveInput.setText("Run full pytest suite and verify all modules")
        self.TransmitDirective()

    def TransmitDirective(self):
        DirectiveText = str(self.DirectiveInput.text()).strip()
        if not DirectiveText:
            return
        ActiveAudio.play("click")
        self.DirectiveInput.clear()

        Meta = self.AgentsDirectory.get(self.ActiveAgentKey, {})
        AgentName = Meta.get("Name", "AGENT")
        Category = Meta.get("Category", "INTERNAL")

        self.DialogueBox.append(">> [COMMANDER]: " + DirectiveText)
        self.DialogueBox.append("   [PROCESSING // " + AgentName + "]...")

        ThreadingMod = LCARS.Import("threading")

        def ExecutionWorker():
            ResponseText = ""
            if Category == "CLI":
                ResponseText = self.ExecuteCliAgent(self.ActiveAgentKey, DirectiveText)
            elif Category == "INTERNAL":
                ResponseText = self.ExecuteInternalAgent(self.ActiveAgentKey, DirectiveText)
            elif Category == "CLOUD":
                ResponseText = self.ExecuteCloudAgent(self.ActiveAgentKey, DirectiveText)

            CleanResponse = str(ResponseText or "No transmission received.")
            self.DialogueBox.append("<< [" + AgentName + "]:\n" + CleanResponse + "\n")
            ActiveAudio.play("acknowledge")

        self.ExecutionThread = ThreadingMod.Thread(target=ExecutionWorker, daemon=True)
        self.ExecutionThread.start()

    def ExecuteCliAgent(self, AgentKey, PromptText):
        SubprocessMod = LCARS.Import("subprocess")
        PathMod = LCARS.Import("pathlib").Path
        ProjectRoot = str(PathMod(__file__).resolve().parents[2])

        CmdList = []
        if AgentKey == "gemini":
            CmdList = ["cmd.exe", "/c", "gemini", "-p", PromptText]
        elif AgentKey == "devin":
            CmdList = ["cmd.exe", "/c", "devin", "-p", PromptText]
        elif AgentKey == "opencode":
            CmdList = ["cmd.exe", "/c", "opencode", "run", PromptText]

        if not CmdList:
            return "[CLI]: Agent executable not configured."

        Proc = SubprocessMod.Popen(
            CmdList,
            cwd=ProjectRoot,
            stdout=SubprocessMod.PIPE,
            stderr=SubprocessMod.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        Lines = []
        for Line in Proc.stdout:
            Lines.append(Line.rstrip())
        Proc.wait()
        return "\n".join(Lines) if Lines else "[CLI]: Process completed with exit code " + str(Proc.returncode)

    def ExecuteInternalAgent(self, AgentKey, PromptText):
        if AgentKey == "tars":
            TarsMod = LCARS.Import("lcars.service.tars")
            if TarsMod and hasattr(TarsMod, "LCARSTARS"):
                return TarsMod.LCARSTARS.GetInstance().Execute(PromptText)

        if AgentKey == "neuralcore":
            ComputerMod = LCARS.Import("lcars.core.computer")
            if ComputerMod and hasattr(ComputerMod, "BoardComputer"):
                Board = ComputerMod.BoardComputer.GetInstance()
                Resp = Board.ExecuteDirective(PromptText)
                if isinstance(Resp, dict):
                    return Resp.get("Message", str(Resp))
                return str(Resp)

        ProviderMod = LCARS.Import("lcars.service.provider")
        if ProviderMod and hasattr(ProviderMod, "AIProviderManager"):
            AiMgr = ProviderMod.AIProviderManager.GetInstance()
            Meta = self.AgentsDirectory.get(AgentKey, {})
            AgentName = Meta.get("Name", AgentKey.upper())
            SystemText = "You are " + AgentName + ". Workspace: LCARS-Framework. Language: Ukrainian or English. Execute directives with high technical precision."
            Messages = [{"role": "system", "content": SystemText}, {"role": "user", "content": PromptText}]
            return AiMgr.Route(Messages)
        return "Internal Ship Computer Offline."

    def ExecuteCloudAgent(self, AgentKey, PromptText):
        ProviderMod = LCARS.Import("lcars.service.provider")
        if ProviderMod and hasattr(ProviderMod, "AIProviderManager"):
            AiMgr = ProviderMod.AIProviderManager.GetInstance()
            if AiMgr:
                AiMgr.SwitchModel(AgentKey)
                Meta = self.AgentsDirectory.get(AgentKey, {})
                AgentName = Meta.get("Name", AgentKey.upper())
                AgentRole = Meta.get("Type", "ADVANCED AI AGENT")
                SystemText = "You are " + AgentName + " (" + AgentRole + ").\nWorkspace: LCARS-Framework. Language: Ukrainian or English as addressed.\nProvide direct, highly competent, production-grade technical reasoning and solutions."
                Messages = [{"role": "system", "content": SystemText}, {"role": "user", "content": PromptText}]
                return AiMgr.Route(Messages)
        return "AI Cloud Conduit Offline."


class ChannelsView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.Build()

    def Build(self):
        Layout = LCARS.Vertical(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(10)

        Layout.addWidget(LCARSLabel(Text="PROTOCOL CHANNEL ORCHESTRATION // ODN & RPC MATRIX", Color=Palette.Buttons[1], FontSize=16, Parent=self.Widget).widget)
        Scan = ScanningBar(Color=Palette.Buttons[2], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        Layout.addWidget(Scan.widget)

        Channels = [
            ("ODN OPTICAL CARRIER BUS", "1024-bit In-Memory Superposition Event Dispatcher", "ACTIVE NOMINAL", Palette.Buttons[1], "03-01"),
            ("HTTP RPC MASTER GATEWAY", "REST & JSON-RPC Gateway on port 3055 (/generate)", "READY FOR CONDUIT", Palette.Buttons[4], "03-02"),
            ("WEBSOCKET SUBSPACE PIPE", "Bidirectional live telemetry stream on port 3056", "STANDBY MONITOR", Palette.Buttons[2], "03-03"),
            ("AI MULTIPLEXER PROXY", "Central routing proxy for OpenRouter, Groq, Mistral, Astra", "ONLINE ROUTED", Palette.Buttons[3], "03-04"),
        ]

        for Title, Desc, State, ColorHex, NumberCode in Channels:
            Card = LCARS.Widget(self.Widget)
            Card.setStyleSheet("background-color: #03060C; border-left: 6px solid " + ColorHex + "; border-radius: 4px;")
            CL = LCARS.Vertical(Card)
            CL.setContentsMargins(14, 12, 14, 12)
            CL.setSpacing(4)

            Top = LCARS.Widget(Card)
            Top.setStyleSheet("background-color: transparent;")
            TL = LCARS.Horizontal(Top)
            TL.setContentsMargins(0, 0, 0, 0)
            TL.addWidget(LCARSLabel(Text=Title, Color=ColorHex, FontSize=14, Parent=Top).widget, 1)
            TL.addWidget(LCARSLabel(Text=State, Color="#00FF99", FontSize=12, Parent=Top).widget)
            CL.addWidget(Top)

            CL.addWidget(LCARSLabel(Text=Desc, Color="#CCCCCC", FontSize=11, Parent=Card).widget)

            ActionRow = LCARS.Widget(Card)
            ActionRow.setStyleSheet("background-color: transparent;")
            ARL = LCARS.Horizontal(ActionRow)
            ARL.setContentsMargins(0, 0, 0, 0)
            ARL.addStretch(1)

            BtnProbe = LCARSButton(Text="PING CONDUIT", Form=LCARSButton.Soft, Color=ColorHex, Number=NumberCode, CornerRadius=3, Parent=ActionRow)
            BtnProbe.widget.setFixedSize(160, 28)
            ARL.addWidget(BtnProbe.widget)
            CL.addWidget(ActionRow)

            Layout.addWidget(Card)

        Layout.addStretch(1)


class SubscriptionsView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.KeyInputs = {}
        self.Build()

    def Build(self):
        Layout = LCARS.Vertical(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(10)

        Layout.addWidget(LCARSLabel(Text="ACCOUNT AUTH & SUBSCRIPTIONS // AI MODEL PROVIDERS", Color=Palette.Buttons[4], FontSize=16, Parent=self.Widget).widget)
        Scan = ScanningBar(Color=Palette.Buttons[4], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        Layout.addWidget(Scan.widget)

        RuntimeMod = LCARS.Import("lcars.system.environment").Runtime
        Providers = [
            ("OpenRouter Gateway", "OPENROUTER_API_KEY", "Multi-model router (Claude 3.5 Sonnet, GPT-4o, DeepSeek V3, Llama 3.3)", Palette.Buttons[1], "04-01"),
            ("Groq Cloud Inference", "GROQ_API_KEY", "Ultra-fast Llama 70B inference via Groq Tensor Processing Units", Palette.Buttons[4], "04-02"),
            ("Mistral AI Codestral", "MISTRAL_API_KEY", "Codestral & Mistral Large specialized programming intelligence", Palette.Buttons[0], "04-03"),
            ("Experiential Astra GPT-6", "EXPERIENTIAL_API_KEY", "Experiential Labs GPT-6 Astra deep reasoning endpoint", Palette.Buttons[2], "04-04"),
        ]

        for Name, EnvKey, Description, ColorHex, NumberCode in Providers:
            Card = LCARS.Widget(self.Widget)
            Card.setStyleSheet("background-color: #03060C; border-left: 6px solid " + ColorHex + "; border-radius: 4px;")
            CL = LCARS.Vertical(Card)
            CL.setContentsMargins(14, 10, 14, 10)
            CL.setSpacing(6)

            CL.addWidget(LCARSLabel(Text=Name.upper(), Color=ColorHex, FontSize=14, Parent=Card).widget)
            CL.addWidget(LCARSLabel(Text=Description, Color="#AAAAAA", FontSize=10, Parent=Card).widget)

            Row = LCARS.Widget(Card)
            Row.setStyleSheet("background-color: transparent;")
            RL = LCARS.Horizontal(Row)
            RL.setContentsMargins(0, 0, 0, 0)
            RL.setSpacing(8)

            CurrentVal = str(RuntimeMod.get(EnvKey, "") if RuntimeMod else "")
            InputBox = LCARS.Input(Row)
            InputBox.setText(CurrentVal)
            if hasattr(InputBox, "EchoMode") and hasattr(InputBox.EchoMode, "Password"):
                InputBox.setEchoMode(InputBox.EchoMode.Password)
            InputBox.setPlaceholderText("Enter API token...")
            InputBox.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #1E3A5F; padding: 6px 10px; font-size: 11pt; border-radius: 4px;")
            self.KeyInputs[EnvKey] = InputBox
            RL.addWidget(InputBox, 1)

            BtnSave = LCARSButton(Text="SAVE TOKEN", Form=LCARSButton.Soft, Color=ColorHex, Number=NumberCode, CornerRadius=3, Parent=Row)
            BtnSave.widget.setFixedSize(130, 32)
            TargetKey = EnvKey
            BtnSave.Clicked.Connect(lambda *A, K=TargetKey: self.SaveKey(K))
            RL.addWidget(BtnSave.widget)

            BtnPing = LCARSButton(Text="TEST PING", Form=LCARSButton.Soft, Color=Palette.Buttons[6], Number="PING", CornerRadius=3, Parent=Row)
            BtnPing.widget.setFixedSize(120, 32)
            TargetName = Name
            BtnPing.Clicked.Connect(lambda *A, N=TargetName: self.PingBackend(N))
            RL.addWidget(BtnPing.widget)

            CL.addWidget(Row)
            Layout.addWidget(Card)

        Layout.addStretch(1)

    def SaveKey(self, KeyName):
        ActiveAudio.play("click")
        Val = str(self.KeyInputs[KeyName].text()).strip()
        PathMod = LCARS.Import("pathlib").Path
        EnvPath = PathMod(__file__).resolve().parents[2] / ".env"
        Lines = EnvPath.read_text(encoding="utf-8").splitlines() if EnvPath.exists() else []
        NewLines = []
        Found = False
        for Line in Lines:
            if Line.startswith(KeyName + "="):
                NewLines.append(KeyName + "=" + Val)
                Found = True
            else:
                NewLines.append(Line)
        if not Found:
            NewLines.append(KeyName + "=" + Val)
        EnvPath.write_text("\n".join(NewLines) + "\n", encoding="utf-8")
        RuntimeMod = LCARS.Import("lcars.system.environment").Runtime
        if RuntimeMod:
            RuntimeMod.set(KeyName, Val)

    def PingBackend(self, ProviderName):
        ActiveAudio.play("click")
        ProviderModule = LCARS.Import("lcars.service.provider")
        if ProviderModule:
            AiMgr = ProviderModule.AIProviderManager.GetInstance()
            if AiMgr:
                for Backend in AiMgr.Backends:
                    if Backend.Name.lower() in ProviderName.lower():
                        Backend.CheckAvailable()


class EnvironmentView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.EditorBox = None
        self.EnvPath = None
        self.Build()

    def Build(self):
        Layout = LCARS.Vertical(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(10)

        Header = LCARS.Widget(self.Widget)
        Header.setFixedHeight(40)
        Header.setStyleSheet("background-color: transparent;")
        HL = LCARS.Horizontal(Header)
        HL.setContentsMargins(0, 0, 0, 0)
        HL.addWidget(LCARSLabel(Text="GATEWAY ENVIRONMENT // EDIT .ENV CONFIGURATION MATRIX", Color=Palette.Buttons[4], FontSize=16, Parent=Header).widget, 1)

        BtnReload = LCARSButton(Text="RELOAD FILE", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="05-01", CornerRadius=3, Parent=Header)
        BtnReload.widget.setFixedSize(140, 34)
        BtnReload.Clicked.Connect(self.LoadFile)
        HL.addWidget(BtnReload.widget)

        BtnSave = LCARSButton(Text="COMMIT CHANGES", Form=LCARSButton.Soft, Color="#00AA66", Number="05-02", CornerRadius=3, Parent=Header)
        BtnSave.widget.setFixedSize(160, 34)
        BtnSave.Clicked.Connect(self.SaveFile)
        HL.addWidget(BtnSave.widget)

        Layout.addWidget(Header)

        Scan = ScanningBar(Color=Palette.Buttons[4], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        Layout.addWidget(Scan.widget)

        PathMod = LCARS.Import("pathlib").Path
        self.EnvPath = PathMod(__file__).resolve().parents[2] / ".env"

        self.EditorBox = LCARS.Terminal(self.Widget)
        FontFamily = "'Consolas', 'Courier New', monospace"
        self.EditorBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #142840; font-size: 13px; font-family: " + FontFamily + "; padding: 12px; line-height: 140%;")
        Layout.addWidget(self.EditorBox, 1)

        self.LoadFile()

    def LoadFile(self):
        if self.EnvPath and self.EnvPath.exists():
            Content = self.EnvPath.read_text(encoding="utf-8")
            self.EditorBox.setPlainText(Content)

    def SaveFile(self):
        ActiveAudio.play("click")
        if self.EnvPath:
            Content = self.EditorBox.toPlainText()
            self.EnvPath.write_text(Content, encoding="utf-8")


class DashboardView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.ConsoleBox = None
        self.CpuLabel = None
        self.RamLabel = None
        self.TelemetryTimer = None
        self.Build()
        self.StartTelemetry()

    def Build(self):
        Layout = LCARS.Vertical(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(10)

        Layout.addWidget(LCARSLabel(Text="NATIVE MANAGEMENT DASHBOARD // HOST TELEMETRY & WORKSPACES", Color=Palette.Buttons[1], FontSize=16, Parent=self.Widget).widget)
        Scan = ScanningBar(Color=Palette.Buttons[1], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        Layout.addWidget(Scan.widget)

        # Телеметрія хоста
        TeleRow = LCARS.Widget(self.Widget)
        TeleRow.setFixedHeight(80)
        TeleRow.setStyleSheet("background-color: #03060C; border-left: 6px solid " + Palette.Buttons[2] + "; border-radius: 4px;")
        TL = LCARS.Horizontal(TeleRow)
        TL.setContentsMargins(16, 10, 16, 10)
        TL.setSpacing(20)

        self.CpuLabel = LCARSLabel(Text="HOST CPU: --%", Color=Palette.Buttons[4], FontSize=18, Parent=TeleRow)
        TL.addWidget(self.CpuLabel.widget)

        self.RamLabel = LCARSLabel(Text="HOST MEMORY: --%", Color=Palette.Buttons[2], FontSize=18, Parent=TeleRow)
        TL.addWidget(self.RamLabel.widget)

        TL.addStretch(1)
        Layout.addWidget(TeleRow)

        # Робочі проєкти та кнопки дій
        BtnRow = LCARS.Widget(self.Widget)
        BtnRow.setFixedHeight(46)
        BtnRow.setStyleSheet("background-color: transparent;")
        BL = LCARS.Horizontal(BtnRow)
        BL.setContentsMargins(0, 0, 0, 0)
        BL.setSpacing(8)

        BtnPytest = LCARSButton(Text="RUN PYTEST SUITE", Form=LCARSButton.Soft, Color=Palette.Buttons[1], Number="06-01", CornerRadius=4, Parent=BtnRow)
        BtnPytest.widget.setFixedSize(180, 42)
        BtnPytest.Clicked.Connect(lambda: self.RunCli(["py", "-3.14", "-m", "pytest"]))
        BL.addWidget(BtnPytest.widget)

        BtnPost = LCARSButton(Text="EXECUTE BIOS POST", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="06-02", CornerRadius=4, Parent=BtnRow)
        BtnPost.widget.setFixedSize(190, 42)
        BtnPost.Clicked.Connect(lambda: self.RunCli(["py", "-3.14", "terminal.py", "--test"]))
        BL.addWidget(BtnPost.widget)

        BtnGit = LCARSButton(Text="INSPECT GIT AUDIT", Form=LCARSButton.Soft, Color=Palette.Buttons[2], Number="06-03", CornerRadius=4, Parent=BtnRow)
        BtnGit.widget.setFixedSize(180, 42)
        BtnGit.Clicked.Connect(lambda: self.RunCli(["git", "status", "-s"]))
        BL.addWidget(BtnGit.widget)

        BtnVsCode = LCARSButton(Text="LAUNCH VS CODE", Form=LCARSButton.Soft, Color=Palette.Buttons[3], Number="06-04", CornerRadius=4, Parent=BtnRow)
        BtnVsCode.widget.setFixedSize(170, 42)
        BtnVsCode.Clicked.Connect(lambda: self.RunCli(["code", "."]))
        BL.addWidget(BtnVsCode.widget)

        BL.addStretch(1)
        Layout.addWidget(BtnRow)

        # Консоль виводу
        self.ConsoleBox = LCARS.Terminal(self.Widget)
        self.ConsoleBox.setReadOnly(True)
        FontFamily = "'Consolas', 'Courier New', monospace"
        self.ConsoleBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #142840; font-size: 12px; font-family: " + FontFamily + "; padding: 10px; line-height: 140%;")
        Layout.addWidget(self.ConsoleBox, 1)

    def StartTelemetry(self):
        self.TelemetryTimer = LCARS.Timer(self.Widget)
        self.TelemetryTimer.setInterval(2000)
        self.TelemetryTimer.timeout.connect(self.UpdateTelemetry)
        self.TelemetryTimer.start()

    def UpdateTelemetry(self):
        PsUtil = LCARS.Import("psutil")
        if PsUtil and hasattr(PsUtil, "cpu_percent"):
            Cpu = PsUtil.cpu_percent()
            Ram = PsUtil.virtual_memory().percent
            self.CpuLabel.SetText("HOST CPU: " + str(Cpu) + "%")
            self.RamLabel.SetText("HOST MEMORY: " + str(Ram) + "%")

    def RunCli(self, CommandArgs):
        ActiveAudio.play("click")
        self.ConsoleBox.append(">> Executing: " + " ".join(CommandArgs))
        SubprocessMod = LCARS.Import("subprocess")
        ThreadingMod = LCARS.Import("threading")

        def Worker():
            Proc = SubprocessMod.Popen(CommandArgs, stdout=SubprocessMod.PIPE, stderr=SubprocessMod.STDOUT, text=True, encoding="utf-8", errors="replace")
            for Line in Proc.stdout:
                CleanLine = Line.rstrip()
                if CleanLine:
                    self.ConsoleBox.append("   " + CleanLine)
            Proc.wait()
            self.ConsoleBox.append(">> Process finished // Exit code: " + str(Proc.returncode))

        Thread = ThreadingMod.Thread(target=Worker, daemon=True)
        Thread.start()


class CockpitView:
    def __init__(self, ParentWidget=None):
        self.ParentWidget = ParentWidget
        self.Widget = LCARS.Widget(ParentWidget)
        self.Widget.setStyleSheet("background-color: #000000;")
        self.ChatBox = None
        self.PromptInput = None
        self.Build()

    def Build(self):
        Layout = LCARS.Vertical(self.Widget)
        Layout.setContentsMargins(16, 12, 16, 12)
        Layout.setSpacing(10)

        Layout.addWidget(LCARSLabel(Text="CONVERSATION & SUBAGENT BOARD // DIRECT COCKPIT", Color=Palette.Buttons[2], FontSize=16, Parent=self.Widget).widget)
        Scan = ScanningBar(Color=Palette.Buttons[2], Parent=self.Widget)
        Scan.widget.setFixedHeight(4)
        Layout.addWidget(Scan.widget)

        self.ChatBox = LCARS.Terminal(self.Widget)
        self.ChatBox.setReadOnly(True)
        FontFamily = "'Consolas', 'Courier New', monospace"
        self.ChatBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #142840; font-size: 13px; font-family: " + FontFamily + "; padding: 12px; line-height: 140%;")
        self.ChatBox.append("◤ STARFLEET COCKPIT ACTIVE // Channel established. Enter directives in Ukrainian or English.")
        Layout.addWidget(self.ChatBox, 1)

        InputRow = LCARS.Widget(self.Widget)
        InputRow.setFixedHeight(48)
        InputRow.setStyleSheet("background-color: transparent;")
        IRL = LCARS.Horizontal(InputRow)
        IRL.setContentsMargins(0, 0, 0, 0)
        IRL.setSpacing(8)

        self.PromptInput = LCARS.Input(InputRow)
        self.PromptInput.setPlaceholderText("Enter natural directive in Ukrainian or English...")
        self.PromptInput.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #1E3A5F; padding: 6px 12px; font-size: 12pt; border-radius: 4px;")
        if hasattr(self.PromptInput, "returnPressed"):
            self.PromptInput.returnPressed.connect(self.SendPrompt)
        IRL.addWidget(self.PromptInput, 1)

        BtnSend = LCARSButton(Text="TRANSMIT DIRECTIVE", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="07-01", CornerRadius=4, Parent=InputRow)
        BtnSend.widget.setFixedSize(200, 44)
        BtnSend.Clicked.Connect(self.SendPrompt)
        IRL.addWidget(BtnSend.widget)

        Layout.addWidget(InputRow)

    def SendPrompt(self):
        TextVal = str(self.PromptInput.text()).strip()
        if not TextVal:
            return
        ActiveAudio.play("click")
        self.PromptInput.clear()
        self.ChatBox.append("\n>> COMMANDER DIRECTIVE: " + TextVal)

        ProviderModule = LCARS.Import("lcars.service.provider")
        if ProviderModule:
            AiMgr = ProviderModule.AIProviderManager.GetInstance()
            Messages = [{"role": "user", "content": TextVal}]
            Resp = AiMgr.Route(Messages) if AiMgr else "AI Provider Manager Offline"
            self.ChatBox.append("<< " + str(Resp))
            ActiveAudio.play("acknowledge")
