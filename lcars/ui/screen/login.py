# ◤ LCARS STARFLEET OS :: SECURITY GATE LOGIN & AUTHORIZATION 🖖
# =============================================================================
# ФАЙЛ: lcars/ui/screen/login.py
# СТАНДАРТ: Titanium LCARS (Michael Okuda Vector Standard)
# АРХІТЕКТУРА: Побудовано виключно з готових компонентів LCARS Framework:
#              Screen, Segment, Panel, LCARSElbow, LCARSBar, LCARSButton,
#              LCARSLabel, LCARSIndicator, ScanningBar, StarfieldCluster.
#              Жодного втручання через setStyleSheet, нуль захардкоджених кольорів,
#              автоматична реакція на AlertSystem та зміну стану через SetState.
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.interface import Screen, Segment, Panel
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSIndicator
from lcars.base.animation import StarfieldCluster, ScanningBar
from lcars.core.signal import ODN
from lcars.modules.sound import ActiveAudio


class LCARSLogin(Screen):
    def BuildScreen(self):
        pass

    def __init__(self, LauncherRef = None, ParentNode = None):
        self.Launcher = LauncherRef
        self.AuthTimer = None
        self.AutoTransitionTimer = None
        self.CurrentPhase = 0
        self.TopElbow = None
        self.TopRightElbow = None
        self.BotElbow = None
        self.BotRightElbow = None
        self.TopBar = None
        self.BotBar = None
        self.HeaderLabel = None
        self.HeaderSub = None
        self.StatusHeader = None
        self.DetailLine1 = None
        self.DetailLine2 = None
        self.DetailLine3 = None
        self.EnterBtn = None
        self.FooterStatus = None
        self.ScanBarTop = None
        self.ScanBarBot = None
        self.Starfield = None
        self.StationButtons = []

        super().__init__(Parent=ParentNode, Decorated=False)
        self.widget.setObjectName("LoginScreenRoot")

        FramelessFlag = getattr(LCARS, "Frameless", None)
        if FramelessFlag is not None and hasattr(self.widget, "setWindowFlags"):
            self.widget.setWindowFlags(self.widget.windowFlags() | FramelessFlag)

        if hasattr(self.widget, "showFullScreen"):
            self.widget.showFullScreen()

        self.Build()
        self.StartAuthSequence()

    def Build(self):
        Root = self.widget.layout()
        if Root is None:
            Root = LCARS.Vertical(self.widget)
        Root.setContentsMargins(18, 16, 18, 16)
        Root.setSpacing(10)

        # ─── 1. ВЕРХНІЙ СТРУКТУРНИЙ КАРКАС (HEADER) ───────────────────────
        TopHeader = Segment(Parent=self.widget)
        TopHeader.widget.setFixedHeight(64)
        TL = LCARS.Horizontal(TopHeader.widget)
        TL.setContentsMargins(0, 0, 0, 0)
        TL.setSpacing(10)

        self.TopElbow = LCARSElbow(Direction="top-left", Width=280, Height=64, Thickness=46, Radius=32, ColorGroup="accent", Parent=TopHeader.widget)
        TL.addWidget(self.TopElbow.widget)

        self.TopBar = LCARSBar(Height=46, ColorGroup="accent", Parent=TopHeader.widget)
        TopBarLayout = LCARS.Horizontal(self.TopBar.widget)
        TopBarLayout.setContentsMargins(20, 0, 20, 0)
        TopBarLayout.setSpacing(14)

        self.HeaderLabel = LCARSLabel(Text="STARFLEET SECURITY ARCHITECTURE // QUANTUM ACCESS GATE 🖖", Color="#000000", FontSize=15, Parent=self.TopBar.widget)
        TopBarLayout.addWidget(self.HeaderLabel.widget, 1)

        self.HeaderSub = LCARSLabel(Text="USS ENTERPRISE NCC-1701-F // CLEARANCE LEVEL 7", Color="#000000", FontSize=12, Parent=self.TopBar.widget)
        TopBarLayout.addWidget(self.HeaderSub.widget)

        TL.addWidget(self.TopBar.widget, 1)

        self.TopRightElbow = LCARSElbow(Direction="top-right", Width=120, Height=64, Thickness=46, Radius=32, ColorGroup="accent", Parent=TopHeader.widget)
        TL.addWidget(self.TopRightElbow.widget)
        Root.addWidget(TopHeader.widget)

        # ─── 2. ГОЛОВНА ЦЕНТРАЛЬНА КАМЕРА (CENTER BODY) ───────────────────
        CenterChamber = Segment(Parent=self.widget)
        ChamberLayout = LCARS.Horizontal(CenterChamber.widget)
        ChamberLayout.setContentsMargins(0, 0, 0, 0)
        ChamberLayout.setSpacing(16)

        # Лівий функціональний пілон (Left Rail)
        LeftRail = Panel(Parent=CenterChamber.widget)
        LeftRail.widget.setFixedWidth(240)
        LRL = LCARS.Vertical(LeftRail.widget)
        LRL.setContentsMargins(0, 0, 0, 0)
        LRL.setSpacing(8)

        LRL.addWidget(LCARSLabel(Text="ACCESS PROTOCOL", ColorGroup="accent", FontSize=12, Parent=LeftRail.widget).widget)
        LRL.addWidget(LCARSLabel(Text="ISO-SEC-47//ALPHA", ColorGroup="buttons", FontSize=11, Parent=LeftRail.widget).widget)
        LRL.addSpacing(10)

        RailConfigs = [
            "AUTHENTICATION",
            "SUBSPACE CIPHER",
            "CLEARANCE VERIFY",
            "STATION DISPATCH",
        ]
        for RLabel in RailConfigs:
            BarItem = LCARSBar(Height=32, ColorGroup="buttons", Parent=LeftRail.widget)
            BarLayout = LCARS.Horizontal(BarItem.widget)
            BarLayout.setContentsMargins(12, 0, 12, 0)
            BarLayout.addWidget(LCARSLabel(Text=RLabel, Color="#000000", FontSize=10, Parent=BarItem.widget).widget)
            LRL.addWidget(BarItem.widget)

        LRL.addStretch(1)
        ChamberLayout.addWidget(LeftRail.widget)

        # Центральна робоча консоль
        CenterPanel = Segment(Parent=CenterChamber.widget)
        CPL = LCARS.Vertical(CenterPanel.widget)
        CPL.setContentsMargins(10, 0, 10, 0)
        CPL.setSpacing(12)

        # Жива симуляція частинок зоряного простору (StarfieldCluster)
        self.Starfield = StarfieldCluster(Parent=CenterPanel.widget, StarCount=140, Depth=2.4, Speed=0.045)
        self.Starfield.widget.setFixedHeight(120)
        CPL.addWidget(self.Starfield.widget)

        # Верхній сканер готовності
        self.ScanBarTop = ScanningBar(ColorGroup="accent", Parent=CenterPanel.widget)
        self.ScanBarTop.widget.setFixedHeight(8)
        CPL.addWidget(self.ScanBarTop.widget)

        # Каркас квантової верифікації
        AuthCard = Panel(Parent=CenterPanel.widget)
        ACL = LCARS.Vertical(AuthCard.widget)
        ACL.setContentsMargins(20, 16, 20, 16)
        ACL.setSpacing(12)

        self.StatusHeader = LCARSLabel(
            Text="◤ SECURITY GATE // INITIATING QUANTUM CLEARANCE AUDIT 🖖",
            ColorGroup="accent",
            FontSize=18,
            Parent=AuthCard.widget
        )
        ACL.addWidget(self.StatusHeader.widget)

        self.DetailLine1 = LCARSLabel(
            Text="[1] BIOMETRIC VERIFICATION : DNA & RETINAL SENSORS ACQUIRING SIGNATURE...",
            ColorGroup="buttons",
            FontSize=13,
            Parent=AuthCard.widget
        )
        ACL.addWidget(self.DetailLine1.widget)

        self.DetailLine2 = LCARSLabel(
            Text="[2] SUBSPACE ENCRYPTION    : 1024-BIT QUANTUM CIPHER HANDSHAKE STANDBY...",
            ColorGroup="buttons",
            FontSize=13,
            Parent=AuthCard.widget
        )
        ACL.addWidget(self.DetailLine2.widget)

        self.DetailLine3 = LCARSLabel(
            Text="[3] COMMAND DISPATCH       : AWAITING CLEARANCE VALIDATION PROTOCOL...",
            ColorGroup="buttons",
            FontSize=13,
            Parent=AuthCard.widget
        )
        ACL.addWidget(self.DetailLine3.widget)

        # Нижній сканер статусу картки
        self.ScanBarBot = ScanningBar(ColorGroup="buttons", Parent=AuthCard.widget)
        self.ScanBarBot.widget.setFixedHeight(6)
        ACL.addWidget(self.ScanBarBot.widget)

        # Головна сенсорна кнопка входу (алгоритмічний стан)
        self.EnterBtn = LCARSButton(Text="ACCESS VERIFYING // PLEASE STAND BY...", Form=LCARSButton.Soft, CornerRadius=6, Parent=AuthCard.widget)
        self.EnterBtn.widget.setFixedHeight(48)
        self.EnterBtn.Clicked.Connect(self.OnEnterClicked)
        ACL.addWidget(self.EnterBtn.widget)

        CPL.addWidget(AuthCard.widget, 1)

        # Панель прямого переходу на станції
        QuickRow = Segment(Parent=CenterPanel.widget)
        QRL = LCARS.Horizontal(QuickRow.widget)
        QRL.setContentsMargins(0, 4, 0, 0)
        QRL.setSpacing(10)

        StationList = [
            ("MAIN BRIDGE", "WELCOME"),
            ("NOVA WORKBENCH", "NOVA"),
            ("COMMAND CONSOLE", "CONSOLE"),
            ("ISOLINEAR STORAGE", "PROGRAMS"),
            ("UI ARCHITECT", "CONSTRUCTOR"),
        ]
        self.StationButtons = []
        for SName, SCode in StationList:
            Btn = LCARSButton(Text=SName, Form=LCARSButton.Soft, CornerRadius=4, Parent=QuickRow.widget)
            Btn.widget.setFixedHeight(36)
            TargetCode = SCode
            Btn.Clicked.Connect(lambda *Args, c=TargetCode: self.OnStationClicked(c))
            QRL.addWidget(Btn.widget, 1)
            self.StationButtons.append(Btn)

        CPL.addWidget(QuickRow.widget)
        ChamberLayout.addWidget(CenterPanel.widget, 1)
        Root.addWidget(CenterChamber.widget, 1)

        # ─── 3. НИЖНІЙ СТРУКТУРНИЙ КАРКАС (FOOTER) ───────────────────────
        BotFooter = Segment(Parent=self.widget)
        BotFooter.widget.setFixedHeight(48)
        BL = LCARS.Horizontal(BotFooter.widget)
        BL.setContentsMargins(0, 0, 0, 0)
        BL.setSpacing(10)

        self.BotElbow = LCARSElbow(Direction="bottom-left", Width=280, Height=48, Thickness=34, Radius=24, ColorGroup="buttons", Parent=BotFooter.widget)
        BL.addWidget(self.BotElbow.widget)

        self.BotBar = LCARSBar(Height=34, ColorGroup="buttons", Parent=BotFooter.widget)
        BotBarLayout = LCARS.Horizontal(self.BotBar.widget)
        BotBarLayout.setContentsMargins(20, 0, 20, 0)
        self.FooterStatus = LCARSLabel(Text="SECURITY PROTOCOL ACTIVE // AWAITING CLEARANCE VALIDATION", Color="#000000", FontSize=12, Parent=self.BotBar.widget)
        BotBarLayout.addWidget(self.FooterStatus.widget, 1)
        BL.addWidget(self.BotBar.widget, 1)

        self.BotRightElbow = LCARSElbow(Direction="bottom-right", Width=120, Height=48, Thickness=34, Radius=24, ColorGroup="buttons", Parent=BotFooter.widget)
        BL.addWidget(self.BotRightElbow.widget)
        Root.addWidget(BotFooter.widget)

    def StartAuthSequence(self):
        self.CurrentPhase = 0
        self.AuthTimer = LCARS.Timer(self.widget)
        self.AuthTimer.setInterval(850)
        self.AuthTimer.timeout.connect(self.AdvanceAuth)
        self.AuthTimer.start()

    def AdvanceAuth(self):
        self.CurrentPhase += 1
        if self.CurrentPhase == 1 and self.DetailLine1:
            self.DetailLine1.SetText("[1] BIOMETRIC VERIFICATION : DNA & RETINAL MATCH 100.0% [VERIFIED]")
            self.DetailLine1.SetState("confirm")
            ActiveAudio.play("click")
        elif self.CurrentPhase == 2 and self.DetailLine2:
            self.DetailLine2.SetText("[2] SUBSPACE ENCRYPTION    : 1024-BIT QUANTUM CIPHER [CONFIRMED]")
            self.DetailLine2.SetState("confirm")
            ActiveAudio.play("click")
        elif self.CurrentPhase == 3:
            if self.DetailLine3:
                self.DetailLine3.SetText("[3] COMMAND DISPATCH       : STARFLEET COMMANDER // LEVEL 7 [GRANTED 🖖]")
                self.DetailLine3.SetState("confirm")
            ActiveAudio.play("acknowledge")
            self.AuthTimer.stop()
            self.OnAuthSuccess()

    def OnAuthSuccess(self):
        if self.StatusHeader:
            self.StatusHeader.SetText("◤ AUTHORIZATION COMPLETE // LEVEL 7 ACCESS GRANTED 🖖")
            self.StatusHeader.SetState("confirm")
        if self.FooterStatus:
            self.FooterStatus.SetText("SECURITY CLEARANCE ACCEPTED // WELCOME ABOARD, COMMANDER // ENTERING DESKTOP...")
        if self.EnterBtn:
            self.EnterBtn.SetState(LCARSButton.CONFIRM, Text=">> ACCESS GRANTED: PROCEEDING TO STARFLEET DESKTOP <<")

        LCARS.ProcessEvents()

        # Автоматичний плавний перехід на робочий стіл через 1.8 с
        if self.AutoTransitionTimer is None:
            self.AutoTransitionTimer = LCARS.Timer(self.widget)
            self.AutoTransitionTimer.setSingleShot(True)
            self.AutoTransitionTimer.setInterval(1800)
            self.AutoTransitionTimer.timeout.connect(self.OnEnterClicked)
            self.AutoTransitionTimer.start()

    def OnEnterClicked(self, *Args):
        ActiveAudio.play("click")
        if self.AutoTransitionTimer:
            self.AutoTransitionTimer.stop()
        if self.Launcher and hasattr(self.Launcher, "LaunchDesktop"):
            self.Launcher.LaunchDesktop(Station="WELCOME")
        else:
            ODN.Emit("System.Phase.Desktop", Station="WELCOME")

    def OnStationClicked(self, StationKey):
        ActiveAudio.play("click")
        if self.AutoTransitionTimer:
            self.AutoTransitionTimer.stop()
        if self.Launcher and hasattr(self.Launcher, "LaunchDesktop"):
            self.Launcher.LaunchDesktop(Station=StationKey)
        else:
            ODN.Emit("System.Phase.Desktop", Station=StationKey)


LoginScreen = LCARSLogin
LCARSLoginScreen = LCARSLogin
__all__ = ["LCARSLogin", "LoginScreen", "LCARSLoginScreen"]

if __name__ == "__main__":
    App = LCARS.Application.instance()
    if App is None and hasattr(LCARS, "Application"):
        App = LCARS.Application([])
    ScreenInstance = LCARSLogin()
    Widget = getattr(ScreenInstance, "widget", ScreenInstance)
    if hasattr(Widget, "showFullScreen"):
        Widget.showFullScreen()
    elif hasattr(Widget, "show"):
        Widget.show()
    if App and hasattr(App, "exec"):
        App.exec()