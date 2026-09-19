"""Unified LCARS System - Single Chain Boot Sequence"""
import sys
import time
from pathlib import Path

project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFontDatabase

from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSBar, LCARSIndicator
from lcars.base.animation import Blink, Stagger, Reveal, TextDecode, DataStream
from lcars.base.default import Palette, SystemTheme, FontStyle
from lcars.modules.sound import ActiveAudio


class UnifiedLCARSSystem:

    def __init__(self):
        self.Screen = Screen(Title="LCARS UNIFIED SYSTEM")
        self.CurrentPhase = "boot"
        self.NodePhase = 0
        self.Faction = "FEDERATION"

        self.Screen.SetVertical(0, 0, 0, 0, Spacing=0)
        Host = self.Screen.GetSurface()
        self.Stack = QStackedWidget()
        Host.layout().addWidget(self.Stack)

        self.BootPanel = self.BuildBoot()
        self.LoginPanel = self.BuildLogin()
        self.LauncherPanel = self.BuildLauncher()
        self.DesktopPanel = self.BuildDesktop()

        self.Stack.addWidget(self.BootPanel)
        self.Stack.addWidget(self.LoginPanel)
        self.Stack.addWidget(self.LauncherPanel)
        self.Stack.addWidget(self.DesktopPanel)

    # ── BOOT ────────────────────────────────────────────────────────────────
    def BuildBoot(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        P.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="SYS-INIT",
                         Width=200, Height=70, Thickness=24, Radius=20))

        self.BootStep = LCARSLabel(Text="INITIALIZING...", FontSize=20, Height=36)
        P.Add(self.BootStep)

        self.BootLog = LCARSLabel(Text="> BOOT_MODE: NOMINAL", FontSize=12, Height=200)
        P.Add(self.BootLog)

        P.AddStretch(1)

        self.BootScanBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=8)
        P.Add(self.BootScanBar)
        Blink(Target=self.BootScanBar, Period=0.5, Loop=True).Start()

        P.Add(LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="NCC-1701",
                         Width=200, Height=50, Thickness=22, Radius=18))

        return P

    def StartBoot(self):
        self.CurrentPhase = "boot"
        self.Stack.setCurrentIndex(0)
        self.BootSteps = [
            "ISOLINEAR CORE: INITIALIZING",
            "NEXUS DATA HUB: CONNECTING",
            "NEURAL PROCESSOR: CALIBRATING",
            "SUBSPACE COMMS: ESTABLISHING LINK",
            "TACTICAL SYSTEMS: LOADING",
            "SHIELD GENERATORS: POWERING UP",
            "WARP CORE: IGNITION SEQUENCE",
            "LIFE SUPPORT: ONLINE",
            "LCARS INTERFACE: READY",
        ]
        self.BootIdx = 0
        self.BootTimer = QTimer()
        self.BootTimer.timeout.connect(self.TickBoot)
        self.BootTimer.start(800)
        ActiveAudio.play("acknowledge")

    def TickBoot(self):
        if self.BootIdx < len(self.BootSteps):
            Step = self.BootSteps[self.BootIdx]
            self.BootStep.SetText(Step)
            self.BootLog.SetText(self.BootLog.Text + "\n> " + Step.split(":")[0] + " :: ONLINE")
            ActiveAudio.play("click")
            self.BootIdx += 1
        else:
            self.BootTimer.stop()
            ActiveAudio.play("ready")
            QTimer.singleShot(1500, self.TransitionToLogin)

    # ── LOGIN ───────────────────────────────────────────────────────────────
    def BuildLogin(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        P.Add(LCARSElbow(Corner="top-left", Text="SECURITY", Number="AUTH-01",
                         Width=180, Height=60, Thickness=22, Radius=18))

        self.LoginStatus = LCARSLabel(Text="IDENTIFYING NEURAL PATTERN...", FontSize=16, Height=30)
        P.Add(self.LoginStatus)

        self.LoginBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=10)
        P.Add(self.LoginBar)
        Blink(Target=self.LoginBar, Period=0.6, Loop=True).Start()

        P.AddStretch(1)

        self.LoginBtn = LCARSButton(Text="AUTHORIZE", Number="01-AUTH", Width=200, Height=50,
                                    Sound="ack", Handler=self.CompleteLogin)
        P.Add(self.LoginBtn)

        P.Add(LCARSElbow(Corner="bottom-right", Text="DECK-47", Number="47-SEC",
                         Width=180, Height=40, Thickness=18, Radius=14))

        return P

    def TransitionToLogin(self):
        self.CurrentPhase = "login"
        self.Stack.setCurrentIndex(1)
        QTimer.singleShot(2000, self.StartLogin)

    def StartLogin(self):
        self.LoginStatus.SetText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        ActiveAudio.play("acknowledge")
        QTimer.singleShot(2000, self.TransitionToLauncher)

    def CompleteLogin(self):
        self.LoginStatus.SetText("SCANNING BIOMETRICS... [MATCH CONFIRMED]")
        ActiveAudio.play("acknowledge")
        QTimer.singleShot(1500, self.TransitionToLauncher)

    # ── LAUNCHER ────────────────────────────────────────────────────────────
    def BuildLauncher(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        Header = Panel()
        Header.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Header.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="SYS-LAUNCH",
                              Width=220, Height=80, Thickness=26, Radius=20))
        Header.Add(LCARSLabel(Text="SYSTEM ACCESS // TEMPORAL ALIGNMENT", FontSize=20, Height=80))
        P.Add(Header)

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=6)

        # Sidebar
        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=4)
        Side.GetSurface().setFixedWidth(220)
        Side.Add(LCARSElbow(Corner="top-left", Text="NAV", Number="01-NAV",
                            Width=220, Height=60, Thickness=22, Radius=18))

        self.NodeLabels = []
        for i in range(6):
            L = LCARSLabel(Text=f"NODE-{i+1:02d}", FontSize=10, Height=20)
            Side.Add(L)
            self.NodeLabels.append(L)

        Side.AddStretch(1)

        Side.Add(LCARSButton(Text="RED ALERT", Number="09-ALERT", Width=220, Height=60,
                             State=LCARSButton.ALERT, Sound="alertred",
                             Handler=lambda: SystemTheme.SetSystemState("Red")))
        Side.Add(LCARSElbow(Corner="bottom-left", Text="DECK-47", Number="47-LC",
                            Width=220, Height=50, Thickness=20, Radius=16))
        Body.Add(Side)

        # Content
        Content = Panel()
        Content.SetVertical(0, 0, 0, 0, Spacing=12)

        Stardate = time.strftime("%Y.%m.%d")
        self.LauncherInfo = LCARSLabel(Text=f"STARDATE: {Stardate} // {self.Faction} SECTOR",
                                       FontSize=22, Height=36)
        Content.Add(self.LauncherInfo)

        Content.Add(LCARSLabel(Text="SELECT FACTION", FontSize=14, Height=24))

        FactionRow = Panel()
        FactionRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
        for Name in ["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"]:
            FactionRow.Add(LCARSButton(Text=Name, Number="FAC", Width=180, Height=60,
                                       Sound="click", Handler=lambda n=Name: self.SelectFaction(n)))
        FactionRow.AddStretch()
        Content.Add(FactionRow)

        Content.Add(LCARSLabel(Text="SELECT TEMPORAL PERIOD", FontSize=14, Height=24))

        EraRow = Panel()
        EraRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
        for Era in ["22ND", "23RD", "24TH", "25TH", "29TH"]:
            EraRow.Add(LCARSButton(Text=Era, Number="ERA", Width=140, Height=50, Sound="click"))
        EraRow.AddStretch()
        Content.Add(EraRow)

        Content.AddStretch(1)

        Content.Add(LCARSButton(Text="LAUNCH SYSTEM", Number="10-LAUNCH", Width=300, Height=60,
                                Sound="ready", Handler=self.TransitionToDesktop))

        Body.Add(Content, 1)
        P.Add(Body, 1)

        P.Add(LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="SF-47",
                         Width=200, Height=44, Thickness=18, Radius=14))

        self.NodeTimer = QTimer()
        self.NodeTimer.timeout.connect(self.CycleNodes)
        self.NodeTimer.start(4000)

        return P

    def TransitionToLauncher(self):
        self.CurrentPhase = "launcher"
        self.Stack.setCurrentIndex(2)
        ActiveAudio.play("ready")

    def SelectFaction(self, Name):
        ActiveAudio.play("acknowledge")
        self.Faction = Name
        Stardate = time.strftime("%Y.%m.%d")
        self.LauncherInfo.SetText(f"STARDATE: {Stardate} // {Name} SECTOR")

    def CycleNodes(self):
        if self.CurrentPhase != "launcher":
            return
        Colors = Palette.Buttons
        for i, L in enumerate(self.NodeLabels):
            Idx = (self.NodePhase + i) % len(Colors)
            L.Spectrum = Colors[Idx]
            L.Refresh()
        self.NodePhase = (self.NodePhase + 1) % len(Colors)

    # ── DESKTOP ─────────────────────────────────────────────────────────────
    def BuildDesktop(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        Header = Panel()
        Header.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Header.Add(LCARSElbow(Corner="top-left", Text="USS ENTERPRISE", Number="NCC-1701",
                              Width=250, Height=80, Thickness=28, Radius=22))
        Header.Add(LCARSLabel(Text=f"STARFLEET TACTICAL // {self.Faction}", FontSize=22, Height=80))
        P.Add(Header)

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=6)

        # Left sidebar
        Left = Panel()
        Left.SetVertical(0, 0, 0, 0, Spacing=6)
        Left.GetSurface().setFixedWidth(250)
        Left.Add(LCARSElbow(Corner="top-left", Text="CTRL", Number="01-CTL",
                            Width=250, Height=60, Thickness=22, Radius=18))

        for Name in ["DASHBOARD", "TACTICAL", "SCIENCE", "ENGINEERING", "COMMS"]:
            Left.Add(LCARSButton(Text=Name, Width=250, Height=50, Sound="click"))

        Left.AddStretch(1)
        Left.Add(LCARSElbow(Corner="bottom-left", Text="DECK-47", Number="47-LC",
                            Width=250, Height=60, Thickness=22, Radius=18))
        Body.Add(Left)

        # Center
        Center = Panel()
        Center.SetVertical(0, 0, 0, 0, Spacing=10)

        StatusPanel = Panel()
        StatusPanel.SetVertical(0, 0, 0, 0, Spacing=4)
        StatusPanel.Add(LCARSLabel(Text="MAIN SYSTEMS STATUS", FontSize=18, Align="center", Height=32))
        StatusPanel.Add(LCARSLabel(Text="ALL SYSTEMS OPERATIONAL", FontSize=14, Align="center", Height=24))
        Center.Add(StatusPanel)

        Grid = Panel()
        Grid.SetVertical(0, 0, 0, 0, Spacing=6)
        for System, Status in [("SHIELDS", "ONLINE 100%"), ("WEAPONS", "STANDBY"),
                               ("ENGINES", "WARP 9.0"), ("SENSORS", "LONG RANGE"),
                               ("COMM", "SUBSPACE OPEN"), ("LIFE SUPPORT", "OPTIMAL")]:
            Row = Panel()
            Row.SetHorizontal(0, 0, 0, 0, Spacing=6)
            Row.Add(LCARSLabel(Text=System, FontSize=12, Width=120, Height=28))
            Row.Add(LCARSLabel(Text=Status, FontSize=12, Height=28))
            Row.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=24, Height=28))
            Grid.Add(Row)
        Center.Add(Grid, 1)

        Center.AddStretch(1)

        ScanBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=8)
        Center.Add(ScanBar)
        Blink(Target=ScanBar, Period=0.8, Loop=True).Start()

        Body.Add(Center, 1)

        # Right sidebar
        Right = Panel()
        Right.SetVertical(0, 0, 0, 0, Spacing=6)
        Right.GetSurface().setFixedWidth(200)
        Right.Add(LCARSElbow(Corner="top-right", Text="TEL", Number="02-TLM",
                             Width=200, Height=60, Thickness=22, Radius=18))

        for i in range(5):
            Ind = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=200, Height=22)
            Right.Add(Ind)
            Blink(Target=Ind, Period=0.4 + i * 0.2, Loop=True).Start()

        Right.AddStretch(1)
        Right.Add(LCARSElbow(Corner="bottom-right", Text="SF", Number="SF-47",
                             Width=200, Height=50, Thickness=20, Radius=16))
        Body.Add(Right)

        P.Add(Body, 1)

        # Footer
        Footer = Panel()
        Footer.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Footer.Add(LCARSElbow(Corner="bottom-left", Text="STARFLEET", Number="SF-47",
                              Width=250, Height=44, Thickness=18, Radius=14))
        Footer.Add(LCARSLabel(Text=f"STARDATE: {int(time.time()) % 100000} // SYSTEM READY",
                              FontSize=12, Height=44))
        P.Add(Footer)

        return P

    def TransitionToDesktop(self):
        self.CurrentPhase = "desktop"
        self.Stack.setCurrentIndex(3)
        ActiveAudio.play("ready")

    # ── LAUNCH ──────────────────────────────────────────────────────────────
    def Show(self):
        self.Screen.Show()
        self.StartBoot()


def EntryPoint():
    System = UnifiedLCARSSystem()
    System.Show()
    return System.Screen


LCARS.Launch(EntryPoint)
