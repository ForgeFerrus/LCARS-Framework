# ◤ LCARS STARFLEET OS :: STAGED BOOT VISUALIZER 🖖
# =============================================================================
# ФАЙЛ: lcars/ui/screen/boot.py
# СТАНДАРТ: Titanium LCARS
# РОЛЬ: ЧИСТИЙ ВІЗУАЛІЗАТОР СИСТЕМНОГО ЗАВАНТАЖЕННЯ.
#       Екран НЕ є ядром ініціалізації — він лише підписується на події ODN шини
#       (System.Init.Log, System.Init.Progress, System.Init.Completed)
#       та відображає роботу Бортового Комп'ютера й діагностик.
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.base.default import Palette, SystemTheme
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel, LCARSElbow
from lcars.base.interface import Screen, ScanningBar
from lcars.core.signal import ODN
from lcars.system.initialization import SystemInitializer
from lcars.modules.sound import ActiveAudio

class LCARSBoot(Screen):
    def BuildScreen(self):
        pass

    def __init__(self, LauncherRef = None, ParentNode = None):
        self.Launcher = LauncherRef
        self.Initializer = SystemInitializer.GetInstance()
        self.StepTimer = None
        self.PulseTimer = None
        self.TransitionTimer = None
        self.InterfaceRevealed = False
        self.RailButtons = []
        self.ActionButtons = []

        super().__init__(Parent=ParentNode, Decorated=False)
        self.widget.setObjectName("BootScreenRoot")
        self.widget.setStyleSheet("background-color: #000000; border: none;")

        FramelessFlag = getattr(LCARS, "Frameless", None)
        if FramelessFlag is not None and hasattr(self.widget, "setFlags"):
            self.widget.setFlags(self.widget.flags() | FramelessFlag)

        if hasattr(self.widget, "showFullScreen"):
            self.widget.showFullScreen()

        # Підписка на події життєвого циклу ініціалізації
        ODN.Listen("System.Init.Log", self.OnInitLogReceived)
        ODN.Listen("System.Init.Progress", self.OnInitProgressReceived)
        ODN.Listen("System.Init.Completed", self.OnInitCompletedReceived)

        self.BuildInterface(self.widget)
        self.StartDiagnosticsStream()

    def OnInitLogReceived(self, SignalObj):
        Line = None
        if hasattr(SignalObj, "Flags") and isinstance(SignalObj.Flags, dict):
            Line = SignalObj.Flags.get("Line")
        if not Line and hasattr(SignalObj, "Data"):
            if isinstance(SignalObj.Data, str):
                Line = SignalObj.Data
            elif isinstance(SignalObj.Data, dict):
                Line = SignalObj.Data.get("Line")
        if Line and str(Line) != "Base.Geometry.Line":
            self.AppendLog(str(Line))

    def OnInitProgressReceived(self, SignalObj):
        Data = getattr(SignalObj, "Data", {}) if hasattr(SignalObj, "Data") and isinstance(SignalObj.Data, dict) else {}
        Flags = getattr(SignalObj, "Flags", {}) if hasattr(SignalObj, "Flags") and isinstance(SignalObj.Flags, dict) else {}
        Pct = Flags.get("Percent") or Data.get("Percent") or getattr(SignalObj, "Percent", 0)
        StepName = Flags.get("Name") or Data.get("Name") or getattr(SignalObj, "Name", "DIAGNOSTIC STEP")
        if self.InterfaceRevealed:
            self.StageLabel.SetText(f"[{Pct:03d}%] {StepName}")
            self.FooterStatus.SetText(f"STAGE: {StepName} ({Pct}%) // LIVE SUBSYSTEM TELEMETRY")

    def OnInitCompletedReceived(self, SignalObj):
        self.OnDiagnosticsComplete()

    def BuildInterface(self, TargetWidget = None):
        Host = TargetWidget or getattr(self, "widget", None)
        if Host is None or getattr(self, "LeftRail", None) is not None:
            return
        self.RootLayout = LCARS.Horizontal(Host)
        self.RootLayout.setContentsMargins(18, 16, 18, 16)
        self.RootLayout.setSpacing(14)

        # 1. Лівий рейл (прихований під час діагностики, з'являється після стабілізації)
        self.LeftRail = LCARS.Widget(Host)
        self.LeftRail.setFixedWidth(240)
        self.LeftRail.setStyleSheet("background-color: #000000; border: none;")
        self.LeftRail.setVisible(False)
        LeftLayout = LCARS.Vertical(self.LeftRail)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(8)

        self.TopElbow = LCARSElbow(Direction="top-left", Width=240, Height=56, Thickness=42, Radius=28, ColorGroup="accent", Parent=self.LeftRail)
        LeftLayout.addWidget(self.TopElbow.widget)

        RailSpecs = [
            ("NOVA IDE", "NOVA", 1),
            ("COMMAND CONSOLE", "CONSOLE", 2),
            ("CHIP STORAGE", "PROGRAMS", 3),
            ("UI ARCHITECT", "CONSTRUCTOR", 4),
            ("SECURITY GATE", "LOGIN", 5),
        ]
        self.RailButtons = []
        for BLabel, BKey, BSeed in RailSpecs:
            Btn = LCARSButton(Text=BLabel, Form=LCARSButton.Soft, CornerRadius=4, Parent=self.LeftRail)
            Btn.widget.setFixedHeight(36)
            TargetStation = BKey
            Btn.Clicked.Connect(lambda *Args, k=TargetStation: self.OnStationClicked(k))
            self.RailButtons.append((Btn, BSeed))
            LeftLayout.addWidget(Btn.widget)

        LeftLayout.addStretch(1)

        self.BotElbow = LCARSElbow(Direction="bottom-left", Width=240, Height=48, Thickness=34, Radius=24, ColorGroup="buttons", Parent=self.LeftRail)
        LeftLayout.addWidget(self.BotElbow.widget)
        self.RootLayout.addWidget(self.LeftRail)

        # 2. Головна область (термінал спочатку на весь екран)
        self.RightChamber = LCARS.Widget(Host)
        self.RightChamber.setStyleSheet("background-color: #000000; border: none;")
        self.RightLayout = LCARS.Vertical(self.RightChamber)
        self.RightLayout.setContentsMargins(0, 0, 0, 0)
        self.RightLayout.setSpacing(10)

        # Верхній бар (прихований під час діагностики)
        self.HeaderBar = LCARSBar(Height=56, ColorGroup="accent", Parent=self.RightChamber)
        self.HeaderBar.widget.setVisible(False)
        HeaderLayout = LCARS.Horizontal(self.HeaderBar.widget)
        HeaderLayout.setContentsMargins(20, 0, 20, 0)
        HeaderLayout.setSpacing(14)

        self.HeaderLabel = LCARSLabel(Text="USS ENTERPRISE NCC-1701-F // ODYSSEY CLASS FLAGSHIP // 25th CENTURY", Color="#000000", FontSize=15, Parent=self.HeaderBar.widget)
        HeaderLayout.addWidget(self.HeaderLabel.widget, 1)

        self.StageLabel = LCARSLabel(Text="COLD START SEQUENCE // 000%", Color="#000000", FontSize=13, Parent=self.HeaderBar.widget)
        HeaderLayout.addWidget(self.StageLabel.widget)
        self.RightLayout.addWidget(self.HeaderBar.widget)

        # Термінал (чистий чорний екран без декору під час POST)
        self.TerminalContainer = LCARS.Widget(self.RightChamber)
        self.TerminalContainer.setStyleSheet("background-color: #050B14; border: none;")
        TerminalLayout = LCARS.Vertical(self.TerminalContainer)
        TerminalLayout.setContentsMargins(10, 8, 10, 8)
        TerminalLayout.setSpacing(6)

        self.ScanBar = ScanningBar(ColorGroup="accent", Parent=self.TerminalContainer)
        self.ScanBar.widget.setFixedHeight(6)
        self.ScanBar.widget.setVisible(False)
        TerminalLayout.addWidget(self.ScanBar.widget)

        self.Terminal = LCARS.Terminal(self.TerminalContainer)
        self.Terminal.setReadOnly(True)

        ScrollOff = getattr(LCARS, "ScrollAlwaysOff", None)
        if ScrollOff is not None:
            if hasattr(self.Terminal, "setVerticalScrollBarPolicy"):
                self.Terminal.setVerticalScrollBarPolicy(ScrollOff)
            if hasattr(self.Terminal, "setHorizontalScrollBarPolicy"):
                self.Terminal.setHorizontalScrollBarPolicy(ScrollOff)

        self.Terminal.setStyleSheet(
            "background-color: #050B14; color: #99CCFF; border: none; "
            "font-family: 'Consolas', 'Courier New', monospace; font-size: 11pt; padding: 10px;"
        )
        self.Terminal.setPlainText(
            "◤ STARFLEET ONBOARD COMPUTER ARCHITECTURE // 25th CENTURY NEXUS 🖖\n"
            ">> COLD START SEQUENCE DETECTED. INITIATING LIVE HARDWARE DIAGNOSTICS...\n"
            "─────────────────────────────────────────────────────────────────────────────\n"
        )
        TerminalLayout.addWidget(self.Terminal, 1)
        self.RightLayout.addWidget(self.TerminalContainer, 1)

        # Нижня оперативна панель (прихована на початку)
        self.ActionPanel = LCARS.Widget(self.RightChamber)
        self.ActionPanel.setStyleSheet("background-color: #000000; border: none;")
        self.ActionPanel.setVisible(False)
        ActionLayout = LCARS.Horizontal(self.ActionPanel)
        ActionLayout.setContentsMargins(0, 0, 0, 0)
        ActionLayout.setSpacing(8)

        StationConfigs = [
            ("AUTHORIZATION GATE", "LOGIN", 10),
            ("MAIN DESKTOP", "WELCOME", 20),
            ("NOVA IDE", "NOVA", 30),
            ("COMMAND CONSOLE", "CONSOLE", 40),
            ("UI ARCHITECT", "CONSTRUCTOR", 50),
        ]
        self.ActionButtons = []
        for SLabel, SKey, SSeed in StationConfigs:
            Btn = LCARSButton(Text=SLabel, Form=LCARSButton.Soft, CornerRadius=4, Parent=self.ActionPanel)
            Btn.widget.setFixedHeight(36)
            TargetStation = SKey
            Btn.Clicked.Connect(lambda *Args, k=TargetStation: self.OnStationClicked(k))
            ActionLayout.addWidget(Btn.widget, 1)
            self.ActionButtons.append((Btn, SSeed))

        self.RightLayout.addWidget(self.ActionPanel)

        # Нижній бар (прихований на початку)
        self.FooterBar = LCARSBar(Height=36, ColorGroup="buttons", Parent=self.RightChamber)
        self.FooterBar.widget.setVisible(False)
        FooterLayout = LCARS.Horizontal(self.FooterBar.widget)
        FooterLayout.setContentsMargins(14, 0, 14, 0)
        FooterLayout.setSpacing(12)

        self.FooterStatus = LCARSLabel(Text="STARFLEET SYSTEM STATUS: DIAGNOSTIC AUDIT IN PROGRESS", Color="#000000", FontSize=11, Parent=self.FooterBar.widget)
        FooterLayout.addWidget(self.FooterStatus.widget, 1)
        self.RightLayout.addWidget(self.FooterBar.widget)

        self.RootLayout.addWidget(self.RightChamber, 1)

    def StartDiagnosticsStream(self):
        # Спокійний, реалістичний запуск кроків діагностики (900 мс на крок)
        self.Initializer.IsRunning = True
        self.Initializer.CurrentStepIndex = 0
        self.StepTimer = LCARS.Timer(self.widget)
        self.StepTimer.setInterval(900)
        self.StepTimer.timeout.connect(self.OnStepTimerTick)
        self.StepTimer.start()

    def OnStepTimerTick(self):
        HasNext = self.Initializer.ExecuteNextStep()
        LCARS.ProcessEvents()
        if not HasNext:
            if self.StepTimer:
                self.StepTimer.stop()

    def RevealLCARSInterface(self):
        if self.InterfaceRevealed:
            return
        self.InterfaceRevealed = True
        ActiveAudio.play("acknowledge")
        
        self.LeftRail.setVisible(True)
        self.HeaderBar.widget.setVisible(True)
        self.ScanBar.widget.setVisible(True)
        self.ActionPanel.setVisible(True)
        self.FooterBar.widget.setVisible(True)

        self.StartPulseTimer()
        LCARS.ProcessEvents()

    def StartPulseTimer(self):
        self.PulseTimer = LCARS.Timer(self.widget)
        self.PulseTimer.setInterval(2800)
        self.PulseTimer.timeout.connect(self.OnPulseTick)
        self.PulseTimer.start()

    def OnPulseTick(self):
        GroupKey = "buttons"
        for Btn, Seed in self.RailButtons:
            BaseColor = SystemTheme.RandomButtonColor(Group=GroupKey, Seed=Seed, Dynamic=True)
            Btn.SetColor(BaseColor)

        for Btn, Seed in self.ActionButtons:
            BaseColor = SystemTheme.RandomButtonColor(Group=GroupKey, Seed=Seed, Dynamic=True)
            Btn.SetColor(BaseColor)

    def AppendLog(self, TextLine):
        if hasattr(self, "Terminal") and self.Terminal is not None:
            Clean = str(TextLine).strip()
            if Clean:
                self.Terminal.append(Clean)
                VerticalBar = getattr(self.Terminal, "verticalScrollBar", None)
                if VerticalBar and callable(VerticalBar):
                    BarObj = VerticalBar()
                    if hasattr(BarObj, "setValue") and hasattr(BarObj, "maximum"):
                        BarObj.setValue(BarObj.maximum())

    def OnDiagnosticsComplete(self):
        self.RevealLCARSInterface()
        self.HeaderLabel.SetText("USS ENTERPRISE NCC-1701-F // SYSTEM ONLINE // ALL SUBSYSTEMS NOMINAL")
        self.StageLabel.SetText("CLEARANCE LEVEL 7 // ACCESS GRANTED 🖖")
        self.FooterStatus.SetText("STARFLEET OPERATIONAL MATRIX READY // SELECT STATION TO PROCEED")
        self.AppendLog("\n=======================================================")
        self.AppendLog("◤ STARFLEET COMMAND CLEARANCE: AUTHORIZED 🖖")
        self.AppendLog(">> ALL PRIMARY SYSTEMS SYNCHRONIZED. READY FOR OPERATIONAL DEPLOYMENT.")
        self.AppendLog(">> SYSTEM AWAITING OPERATOR DIRECTIVE: SELECT WORKSTATION ON CONSOLE.")
        self.AppendLog("=======================================================\n")

    def OnStationClicked(self, StationKey):
        ActiveAudio.play("click")
        if self.StepTimer:
            self.StepTimer.stop()
        if self.TransitionTimer:
            self.TransitionTimer.stop()
        if self.PulseTimer:
            self.PulseTimer.stop()

        Launcher = self.Launcher
        if Launcher is None:
            from lcars.core.computer import BoardComputer
            Launcher = BoardComputer.GetInstance()

        if StationKey == "LOGIN":
            if Launcher and hasattr(Launcher, "LaunchLogin"):
                Launcher.LaunchLogin()
            else:
                from lcars.ui.screen.login import LCARSLogin
                LoginScreen = LCARSLogin(LauncherRef=Launcher)
                LoginWidget = getattr(LoginScreen, "widget", LoginScreen)
                if hasattr(self.widget, "close"):
                    self.widget.close()
                if hasattr(LoginWidget, "showFullScreen"):
                    LoginWidget.showFullScreen()
                elif hasattr(LoginWidget, "show"):
                    LoginWidget.show()
                ODN.Emit("System.Phase.Login")
        else:
            if Launcher and hasattr(Launcher, "LaunchDesktop"):
                Launcher.LaunchDesktop(Station=StationKey)
            else:
                from lcars.ui.screen.desktop import LCARSDesktop
                DesktopScreen = LCARSDesktop(BoardComputer=Launcher)
                DesktopWidget = getattr(DesktopScreen, "widget", DesktopScreen)
                if hasattr(self.widget, "close"):
                    self.widget.close()
                if hasattr(DesktopWidget, "showFullScreen"):
                    DesktopWidget.showFullScreen()
                elif hasattr(DesktopWidget, "show"):
                    DesktopWidget.show()
                if hasattr(DesktopScreen, "Select"):
                    DesktopScreen.Select(StationKey)
                ODN.Emit("System.Phase.Desktop", Station=StationKey)


BootScreen = LCARSBoot
LCARSBootScreen = LCARSBoot
__all__ = ["LCARSBoot", "BootScreen", "LCARSBootScreen"]

if __name__ == "__main__":
    App = LCARS.Application.instance()
    if App is None and hasattr(LCARS, "Application"):
        App = LCARS.Application([])
    ScreenInstance = LCARSBoot()
    Widget = getattr(ScreenInstance, "widget", ScreenInstance)
    if hasattr(Widget, "showFullScreen"):
        Widget.showFullScreen()
    elif hasattr(Widget, "show"):
        Widget.show()
    if App and hasattr(App, "exec"):
        App.exec()
