# ◤ TITANIUM LCARS :: CONTROL MAIN APPLICATION WINDOW 🖖
# =============================================================================
# ФАЙЛ: programs/Control/app.py
# ПРИЗНАЧЕННЯ: Головне повноцінне вікно застосунку «LCARS Control» (CCX Desktop Hub),
#              змодельоване безпосередньо за зразком програми CCX Desktop.
#              Відкривається на весь екран (showMaximized), адаптивно масштабується,
#              має лівий сайдбар з усіма 7 станціями, нижній статусний под
#              та центральний динамічний стек робочих просторів.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase).
# =============================================================================

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, ActiveAudio
from .daemon import GatewayDaemon
from .views import StatusView, AgentView, ChannelsView, SubscriptionsView, EnvironmentView, DashboardView, CockpitView


class LCARSControlApp:
    def __init__(self):
        self.Daemon = GatewayDaemon.GetInstance()
        BaseWindow = LCARS.Widget
        self.Window = BaseWindow()
        self.Window.setWindowTitle("LCARS Control // CCX Desktop Master Hub")
        self.Window.setStyleSheet("background-color: #000000; color: #FFFFFF;")

        self.NavButtons = {}
        self.Views = {}
        self.ActiveStation = "Status"
        self.SidebarStatusDot = None
        self.SidebarStatusText = None
        self.SidebarPortLabel = None
        self.SyncTimer = None
        self.IsFullScreen = True
        self.WindowToggleBtn = None
        self.ShutdownBtn = None

        self.BuildInterface()
        self.StartSyncTimer()
        self.SelectStation("Status")

        # Відкриття вікна на весь екран
        self.Window.showFullScreen()

    def BuildInterface(self):
        RootLayout = LCARS.Horizontal(self.Window)
        RootLayout.setContentsMargins(0, 0, 0, 0)
        RootLayout.setSpacing(0)

        # 1. ЛІВИЙ САЙДБАР CCX CONTROL
        Sidebar = LCARS.Widget(self.Window)
        Sidebar.setFixedWidth(240)
        Sidebar.setStyleSheet("background-color: #020408; border-right: 1px solid #102030;")
        SidebarLayout = LCARS.Vertical(Sidebar)
        SidebarLayout.setContentsMargins(12, 12, 12, 12)
        SidebarLayout.setSpacing(6)

        # Логотип і назва CCX CONTROL
        LogoRow = LCARS.Widget(Sidebar)
        LogoRow.setStyleSheet("background-color: transparent;")
        LLayout = LCARS.Horizontal(LogoRow)
        LLayout.setContentsMargins(0, 0, 0, 0)
        LLayout.setSpacing(6)

        LogoIcon = LCARSButton(Text="CCX", Form=LCARSButton.Soft, Color="#0088FF", CornerRadius=4, Parent=LogoRow)
        LogoIcon.widget.setFixedSize(36, 30)
        LLayout.addWidget(LogoIcon.widget)

        LogoTitle = LCARSLabel(Text="CONTROL", Color="#FFFFFF", FontSize=12, Parent=LogoRow)
        LLayout.addWidget(LogoTitle.widget)
        LLayout.addStretch(1)

        self.WindowToggleBtn = LCARSButton(Text="WIN", Form=LCARSButton.Soft, Color="#335577", CornerRadius=4, Parent=LogoRow)
        self.WindowToggleBtn.widget.setFixedSize(36, 30)
        self.WindowToggleBtn.Clicked.Connect(self.ToggleFullScreen)
        LLayout.addWidget(self.WindowToggleBtn.widget)

        self.ShutdownBtn = LCARSButton(Text="X", Form=LCARSButton.Soft, Color=Palette.Red[0], CornerRadius=4, Parent=LogoRow)
        self.ShutdownBtn.widget.setFixedSize(28, 30)
        self.ShutdownBtn.Clicked.Connect(self.close)
        LLayout.addWidget(self.ShutdownBtn.widget)

        SidebarLayout.addWidget(LogoRow)

        SidebarLayout.addSpacing(10)

        # 7 Станцій навігації з підписами
        StationsConfig = [
            ("Status", "Live status and logs", "📈"),
            ("Agent", "Local agent configuration", "🤖"),
            ("Channels", "Protocol channel orchestration", "🌐"),
            ("Subscriptions", "Account auth and subscription access", "💳"),
            ("Environment", "Edit gateway .env file", "⚙️"),
            ("Dashboard", "Native management dashboard", "📊"),
            ("Cockpit", "Conversation and subagent board", "🚀"),
        ]

        for StationName, Subtitle, IconChar in StationsConfig:
            BtnContainer = LCARS.Widget(Sidebar)
            BtnContainer.setFixedHeight(46)
            BtnContainer.setStyleSheet("background-color: transparent; border-radius: 6px;")
            BCL = LCARS.Vertical(BtnContainer)
            BCL.setContentsMargins(6, 4, 6, 4)
            BCL.setSpacing(1)

            TopLine = LCARS.Widget(BtnContainer)
            TopLine.setStyleSheet("background-color: transparent;")
            TLL = LCARS.Horizontal(TopLine)
            TLL.setContentsMargins(0, 0, 0, 0)
            TLL.setSpacing(6)

            IconLbl = LCARSLabel(Text=IconChar, Color="#0099FF", FontSize=11, Parent=TopLine)
            TLL.addWidget(IconLbl.widget)

            NameLbl = LCARSLabel(Text=StationName, Color="#FFFFFF", FontSize=11, Parent=TopLine)
            TLL.addWidget(NameLbl.widget, 1)
            BCL.addWidget(TopLine)

            SubLbl = LCARSLabel(Text=Subtitle, Color="#6688AA", FontSize=8, Parent=BtnContainer)
            BCL.addWidget(SubLbl.widget)

            # Робимо контейнер клікабельним через кнопку або подію
            NavBtn = LCARSButton(Text=StationName, Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=Sidebar)
            NavBtn.widget.setFixedHeight(44)
            TargetStation = StationName
            NavBtn.Clicked.Connect(lambda *Args, S=TargetStation: self.SelectStation(S))
            self.NavButtons[StationName] = NavBtn
            SidebarLayout.addWidget(NavBtn.widget)

        SidebarLayout.addStretch(1)

        # НИЖНІЙ СТАТУСНИЙ ПОД САЙДБАРУ
        StatusPod = LCARS.Widget(Sidebar)
        StatusPod.setStyleSheet("background-color: #040810; border: 1px solid #142840; border-radius: 6px;")
        PodLayout = LCARS.Vertical(StatusPod)
        PodLayout.setContentsMargins(10, 10, 10, 10)
        PodLayout.setSpacing(6)

        # Рядок статусу сервісу
        ServiceRow = LCARS.Widget(StatusPod)
        ServiceRow.setStyleSheet("background-color: transparent;")
        SRL = LCARS.Horizontal(ServiceRow)
        SRL.setContentsMargins(0, 0, 0, 0)
        SRL.setSpacing(6)

        self.SidebarStatusDot = LCARSLabel(Text="●", Color=Palette.Red[0], FontSize=12, Parent=ServiceRow)
        SRL.addWidget(self.SidebarStatusDot.widget)

        self.SidebarStatusText = LCARSLabel(Text="Service disconnected", Color="#CCCCCC", FontSize=9, Parent=ServiceRow)
        SRL.addWidget(self.SidebarStatusText.widget, 1)
        PodLayout.addWidget(ServiceRow)

        # Gateway port
        PortRow = LCARS.Widget(StatusPod)
        PortRow.setStyleSheet("background-color: transparent;")
        PRL = LCARS.Horizontal(PortRow)
        PRL.setContentsMargins(0, 0, 0, 0)
        PRL.addWidget(LCARSLabel(Text="Gateway port", Color="#6688AA", FontSize=8, Parent=PortRow).widget, 1)
        self.SidebarPortLabel = LCARSLabel(Text=str(self.Daemon.Port), Color="#FFFFFF", FontSize=9, Parent=PortRow)
        PRL.addWidget(self.SidebarPortLabel.widget)
        PodLayout.addWidget(PortRow)

        # Autostart
        AutoRow = LCARS.Widget(StatusPod)
        AutoRow.setStyleSheet("background-color: transparent;")
        ARL = LCARS.Horizontal(AutoRow)
        ARL.setContentsMargins(0, 0, 0, 0)
        ARL.addWidget(LCARSLabel(Text="Autostart", Color="#6688AA", FontSize=8, Parent=AutoRow).widget, 1)
        ARL.addWidget(LCARSLabel(Text="Disabled", Color="#888888", FontSize=8, Parent=AutoRow).widget)
        PodLayout.addWidget(AutoRow)

        # Language
        LangRow = LCARS.Widget(StatusPod)
        LangRow.setStyleSheet("background-color: transparent;")
        LangRL = LCARS.Horizontal(LangRow)
        LangRL.setContentsMargins(0, 0, 0, 0)
        LangRL.addWidget(LCARSLabel(Text="Language", Color="#6688AA", FontSize=8, Parent=LangRow).widget, 1)
        LangRL.addWidget(LCARSLabel(Text="English / УКР", Color="#0099FF", FontSize=8, Parent=LangRow).widget)
        PodLayout.addWidget(LangRow)

        # Version
        VerRow = LCARS.Widget(StatusPod)
        VerRow.setStyleSheet("background-color: transparent;")
        VRL = LCARS.Horizontal(VerRow)
        VRL.setContentsMargins(0, 0, 0, 0)
        VRL.addWidget(LCARSLabel(Text="Version", Color="#6688AA", FontSize=8, Parent=VerRow).widget, 1)
        VRL.addWidget(LCARSLabel(Text="2.9.37", Color="#FFFFFF", FontSize=8, Parent=VerRow).widget)
        PodLayout.addWidget(VerRow)

        SidebarLayout.addWidget(StatusPod)
        RootLayout.addWidget(Sidebar)

        # 2. ПРАВИЙ РОБОЧИЙ ПРОСТІР З QSTACKEDWIDGET
        WorkspaceContainer = LCARS.Widget(self.Window)
        WorkspaceContainer.setStyleSheet("background-color: #000000;")
        WorkspaceLayout = LCARS.Vertical(WorkspaceContainer)
        WorkspaceLayout.setContentsMargins(0, 0, 0, 0)
        WorkspaceLayout.setSpacing(0)

        self.MainStack = LCARS.Stacked(WorkspaceContainer)

        # Створення 7 станцій
        self.Views["Status"] = StatusView(ParentWidget=WorkspaceContainer, OnSwitchTab=self.SelectStation)
        self.Views["Agent"] = AgentView(ParentWidget=WorkspaceContainer)
        self.Views["Channels"] = ChannelsView(ParentWidget=WorkspaceContainer)
        self.Views["Subscriptions"] = SubscriptionsView(ParentWidget=WorkspaceContainer)
        self.Views["Environment"] = EnvironmentView(ParentWidget=WorkspaceContainer)
        self.Views["Dashboard"] = DashboardView(ParentWidget=WorkspaceContainer)
        self.Views["Cockpit"] = CockpitView(ParentWidget=WorkspaceContainer)

        for StationKey in ["Status", "Agent", "Channels", "Subscriptions", "Environment", "Dashboard", "Cockpit"]:
            ViewObj = self.Views[StationKey]
            self.MainStack.addWidget(ViewObj.Widget)

        WorkspaceLayout.addWidget(self.MainStack, 1)
        RootLayout.addWidget(WorkspaceContainer, 1)

    def SelectStation(self, StationName):
        ActiveAudio.play("click")
        CleanName = str(StationName).strip()
        if CleanName in self.Views:
            self.ActiveStation = CleanName
            ViewObj = self.Views[CleanName]
            self.MainStack.setCurrentWidget(ViewObj.Widget)

            for Key, Btn in self.NavButtons.items():
                if Key == CleanName:
                    Btn.SetColor("#0088FF")
                else:
                    Btn.SetColor(Palette.Buttons[1])

    def StartSyncTimer(self):
        self.SyncTimer = LCARS.Timer(self.Window)
        self.SyncTimer.setInterval(1000)
        self.SyncTimer.timeout.connect(self.SyncStatus)
        self.SyncTimer.start()

    def SyncStatus(self):
        IsActive = self.Daemon.IsActive()
        if IsActive:
            self.SidebarStatusDot.SetColor("#00FF99")
            self.SidebarStatusText.SetText("Service connected")
        else:
            self.SidebarStatusDot.SetColor(Palette.Red[0])
            self.SidebarStatusText.SetText("Service disconnected")
        if self.SidebarPortLabel:
            self.SidebarPortLabel.SetText(str(self.Daemon.Port))

    def ToggleFullScreen(self):
        if self.IsFullScreen:
            self.Window.showNormal()
            self.IsFullScreen = False
            if self.WindowToggleBtn:
                self.WindowToggleBtn.SetText("MAX")
        else:
            self.Window.showFullScreen()
            self.IsFullScreen = True
            if self.WindowToggleBtn:
                self.WindowToggleBtn.SetText("WIN")

    def show(self):
        self.Window.showMaximized()

    def close(self):
        if self.SyncTimer:
            self.SyncTimer.stop()
        self.Window.close()

