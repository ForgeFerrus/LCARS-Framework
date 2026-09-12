# LCARS STARFLEET OS :: LOADING SCREEN
# ФАЙЛ: lcars/ui/screen/loading.py
# СТАНДАРТ: Titanium LCARS
from __future__ import annotations
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.base.interface import Screen, ScanningBar
from lcars.base.component import LCARSLabel, LCARSElbow, LCARSBar
from lcars.base.animation import DiagnosticGrid
from lcars.core.signal import ODN
from lcars.modules.sound import ActiveAudio
from lcars.system.initialization import SystemInitializer

class LCARSLoading(Screen):
    def BuildScreen(self):
        pass
    def __init__(self, LauncherRef=None, ParentNode=None):
        self.Launcher = LauncherRef
        self.Initializer = SystemInitializer.GetInstance()
        self.CurrentStepIndex = 0
        self.StepTimer = None
        self.StepLbl = None
        self.PercentLbl = None
        self.DotsLbl = None
        self.FooterLbl = None
        super().__init__(Parent=ParentNode, Decorated=False)
        self.widget.setStyleSheet("background-color:#000000;border:none;")
        self.Build()
        self.StartSequence()
    def Build(self):
        Root = LCARS.Vertical(self.widget)
        Root.setContentsMargins(14,14,14,14)
        Root.setSpacing(10)
        Top = LCARS.Widget(self.widget)
        Top.setFixedHeight(48)
        Top.setStyleSheet("background-color:#000000;")
        TL = LCARS.Horizontal(Top)
        TL.setContentsMargins(0,0,0,0)
        TL.setSpacing(8)
        self.TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[4], Width=160, Height=48, Thickness=34, Radius=22, Parent=Top)
        TL.addWidget(self.TopElbow.widget)
        Strip = LCARS.Widget(Top)
        Strip.setStyleSheet("background-color:" + Palette.Buttons[4] + ";border:none;border-radius:4px;")
        SL = LCARS.Horizontal(Strip)
        SL.setContentsMargins(16,0,16,0)
        SL.setSpacing(12)
        SL.addWidget(LCARSLabel(Text="USS ENTERPRISE NCC-1701-F // QUANTUM SUBSYSTEM INITIALIZATION", Color="#000000", FontSize=14, Parent=Strip).widget, 1)
        self.PercentLbl = LCARSLabel(Text="INITIALIZING // 000%", Color="#000000", FontSize=13, Parent=Strip)
        SL.addWidget(self.PercentLbl.widget)
        TL.addWidget(Strip, 1)
        Root.addWidget(Top)
        Root.addStretch(1)
        Center = LCARS.Widget(self.widget)
        Center.setStyleSheet("background-color:#000000;")
        CL = LCARS.Vertical(Center)
        CL.setContentsMargins(0,0,0,0)
        CL.setSpacing(14)
        self.DiagGrid = DiagnosticGrid(Parent=Center)
        self.DiagGrid.widget.setFixedSize(480,200)
        CL.addWidget(self.DiagGrid.widget)
        self.ScanBar = ScanningBar(Color=Palette.Buttons[1], Parent=Center)
        self.ScanBar.widget.setFixedSize(720,8)
        CL.addWidget(self.ScanBar.widget)
        CL.addWidget(LCARSLabel(Text="LCARS OPERATING SYSTEM // 25th CENTURY ARCHITECTURE", Color=Palette.Buttons[2], FontSize=20, Parent=Center).widget)
        self.StepLbl = LCARSLabel(Text="COMMENCING QUANTUM SUBSYSTEM INITIALIZATION...", Color=Palette.Buttons[4], FontSize=14, Parent=Center)
        CL.addWidget(self.StepLbl.widget)
        self.DotsLbl = LCARSLabel(Text="o  o  o  o  o  o  o", Color=Palette.Buttons[0], FontSize=16, Parent=Center)
        CL.addWidget(self.DotsLbl.widget)
        Root.addWidget(Center)
        Root.addStretch(1)
        Bot = LCARS.Widget(self.widget)
        Bot.setFixedHeight(40)
        Bot.setStyleSheet("background-color:#000000;")
        BL = LCARS.Horizontal(Bot)
        BL.setContentsMargins(0,0,0,0)
        BL.setSpacing(8)
        self.BotElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Width=160, Height=40, Thickness=28, Radius=20, Parent=Bot)
        BL.addWidget(self.BotElbow.widget)
        BotStrip = LCARS.Widget(Bot)
        BotStrip.setStyleSheet("background-color:" + Palette.Buttons[0] + ";border:none;border-radius:4px;")
        BSL = LCARS.Horizontal(BotStrip)
        BSL.setContentsMargins(16,0,16,0)
        self.FooterLbl = LCARSLabel(Text="OPTICAL DATA NETWORK BUS: 1024-BIT CARRIER SYNCHRONIZED", Color="#FFFFFF", FontSize=11, Parent=BotStrip)
        BSL.addWidget(self.FooterLbl.widget, 1)
        BL.addWidget(BotStrip, 1)
        Root.addWidget(Bot)
    def StartSequence(self):
        self.CurrentStepIndex = 0
        self.StepTimer = LCARS.Timer(self.widget)
        self.StepTimer.setInterval(380)
        self.StepTimer.timeout.connect(self.ExecuteNextStep)
        self.StepTimer.start()
    def ExecuteNextStep(self):
        Seq = self.Initializer.Sequence if self.Initializer else []
        if self.CurrentStepIndex < len(Seq):
            Step = Seq[self.CurrentStepIndex]
            Total = len(Seq)
            Pct = int(((self.CurrentStepIndex+1)/Total)*100)
            if callable(getattr(Step,"Handler",None)):
                Step.Handler()
            if self.StepLbl:
                self.StepLbl.SetText(">> [" + str(self.CurrentStepIndex+1).zfill(2) + "/" + str(Total) + "] " + str(Step.Name) + " // [OK]")
            if self.PercentLbl:
                self.PercentLbl.SetText("SYNCHRONIZING // " + str(Pct).zfill(3) + "%")
            if self.DotsLbl:
                Done = self.CurrentStepIndex+1
                self.DotsLbl.SetText(("* " * Done + "o  " * (Total-Done)).strip())
            self.CurrentStepIndex += 1
            LCARS.ProcessEvents()
        else:
            if self.StepTimer:
                self.StepTimer.stop()
            self.OnComplete()
    def OnComplete(self):
        ActiveAudio.play("acknowledge")
        if self.PercentLbl:
            self.PercentLbl.SetText("CORE SYNCHRONIZED // 100%")
        if self.StepLbl:
            self.StepLbl.SetText(">> ALL QUANTUM CHIP MATRICES ONLINE. ACCESS GATE READY")
        if self.FooterLbl:
            self.FooterLbl.SetText("STARFLEET COMMAND CLEARANCE VERIFIED // TRANSITIONING TO SECURITY GATE")
        LCARS.ProcessEvents()
        LCARS.Timer.singleShot(1200, self.TransitionToLogin)
    def TransitionToLogin(self):
        if self.Launcher and hasattr(self.Launcher,"LaunchLogin"):
            self.Launcher.LaunchLogin()
        else:
            ODN.Emit("System.Phase.Login")

LoadingScreen = LCARSLoading
LCARSLoadingScreen = LCARSLoading
__all__ = ["LCARSLoading","LoadingScreen","LCARSLoadingScreen"]
