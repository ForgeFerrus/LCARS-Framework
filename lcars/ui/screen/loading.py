import sys
import time
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.base.component import LCARSBar, LCARSLabel, LCARSButton, LCARSElbow
from lcars.base.interface import Panel, Screen, Segment
from lcars.system.initialization import CreateInitializer

# LCARS boot screen with visible initialization console and emergency handoff.
class LCARSLoading(Screen):
    def __init__(self, parent=None, Target="desktop"):
        super().__init__(Parent=parent)
        self.Target = Target.lower()
        self.PreviewMode = self.Target in ("preview", "loading")
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        if hasattr(self.widget, "setSizePolicy"):
            Policy = LCARS.Policy
            if Policy:
                self.widget.setSizePolicy(Policy.Policy.Expanding, Policy.Policy.Expanding)
        self.sequenceActive = False
        self.BootLines = []
        self.BootQueue = []
        self.BootTypingLine = ""
        self.BootTypingIndex = 0
        self.BootTypingSpeed = 2
        self.BootRendered = []
        self.BootCursorVisible = True
        self.BootDotsPhase = 0
        self.InitUI()

    def InitUI(self):
        root = self.Vertical(0, 0, 0, 0, 0)
        ODN.Channel("Telemetry.Event").Connect(self.OnTelemetryEvent)

        # ─── TOP FRAME ──────────────────────────────────────────────
        TopRow = Segment(Parent=self.widget)
        TopLayout = LCARS.Horizontal(TopRow.widget)
        TopLayout.setContentsMargins(0, 0, 0, 0)
        TopLayout.setSpacing(5)
        
        TopColor = "#71A0CD"
        TopElbow = LCARSElbow(Direction="top-left", Color=TopColor, Parent=TopRow.widget)
        TopElbow.widget.setFixedSize(100, 45)
        TopLayout.addWidget(TopElbow.widget)
        
        TopBar = LCARSBar(Type="rect", Color=TopColor, Parent=TopRow.widget, Height=45)
        TopLayout.addWidget(TopBar.widget, 1)
        
        self.TopRow = TopRow
        self.Add(root, TopRow)
        TopRow.widget.hide()

        # ─── CENTER CONTENT ─────────────────────────────────────────
        CenterRow = Segment(Parent=self.widget)
        CenterLayout = LCARS.Vertical(CenterRow.widget)
        CenterLayout.setContentsMargins(100, 0, 100, 0)
        CenterLayout.setSpacing(15)

        AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)

        title = LCARSLabel(Text="LCARS OPERATING SYSTEM", Color="#BBBBBB", FontSize=48, Parent=CenterRow.widget)
        if AlignmentFlag:
            title.widget.setAlignment(AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(title.widget)
        self.BootTitle = title
        title.widget.hide()

        subtitle = LCARSLabel(Text="SYSTEM BOOT SEQUENCE - MULTI-CORE ANALYSIS", Color="#55AAFF", FontSize=24, Parent=CenterRow.widget)
        if AlignmentFlag:
            subtitle.widget.setAlignment(AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(subtitle.widget)
        self.BootSubtitle = subtitle
        subtitle.widget.hide()

        consoleTitle = LCARSLabel(Text="INITIALIZATION CONSOLE", Color="#99CCFF", FontSize=18, Parent=CenterRow.widget)
        if AlignmentFlag:
            consoleTitle.widget.setAlignment(AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(consoleTitle.widget)
        self.BootConsoleTitle = consoleTitle
        consoleTitle.widget.hide()

        self.BootFrame = Panel(Parent=CenterRow.widget)
        self.BootFrame.setStyleSheet(
            "background-color: #050505; border: 1px solid #335577; "
            "border-radius: 6px;"
        )
        # Boot frame gets its own layout through the wrapper so the container
        # stays a real LCARS object instead of being treated like a raw widget.
        BootFrameLayout = self.BootFrame.Vertical(12, 12, 12, 12, 8)
        BootFrameLayout.setContentsMargins(12, 12, 12, 12)
        BootFrameLayout.setSpacing(8)

        self.BootConsole = LCARS.Terminal(self.BootFrame.widget)
        self.BootConsole.setReadOnly(True)
        if hasattr(self.BootConsole, "setMinimumHeight"):
            self.BootConsole.setMinimumHeight(420)
        self.BootConsole.setStyleSheet(
            "background-color: #000000; color: #99ccff; border: none; "
            "font-family: 'LCARS', Consolas, monospace; font-size: 18px; "
            "padding: 16px; selection-background-color: #FF9900; selection-color: #000000;"
        )
        BootFrameLayout.addWidget(self.BootConsole, 1)
        CenterLayout.addWidget(self.BootFrame.widget, 1)

        self.BootDotsLabel = LCARSLabel(Text="● ● ● ● ● ● ● ● ●", Color="#55AAFF", FontSize=20, Parent=CenterRow.widget)
        if AlignmentFlag:
            self.BootDotsLabel.widget.setAlignment(AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(self.BootDotsLabel.widget)
        self.BootDotsLabel.widget.hide()

        self.BootTextTimer = LCARS.Timer(self.widget)
        if hasattr(self.BootTextTimer, "setSingleShot"):
            self.BootTextTimer.setSingleShot(False)
        if hasattr(self.BootTextTimer, "setInterval"):
            self.BootTextTimer.setInterval(22)
        Timeout = getattr(self.BootTextTimer, "timeout", None)
        if Timeout and hasattr(Timeout, "connect"):
            Timeout.connect(self.TickBootText)
        if hasattr(self.BootTextTimer, "start"):
            self.BootTextTimer.start(22)

        self.Add(root, CenterRow, 1)

        # ─── BOTTOM FRAME ───────────────────────────────────────────
        BottomRow = Segment(Parent=self.widget)
        BottomLayout = LCARS.Horizontal(BottomRow.widget)
        BottomLayout.setContentsMargins(0, 0, 0, 0)
        BottomLayout.setSpacing(5)
        
        BottomColor = "#E18B6B"
        BottomElbow = LCARSElbow(Direction="bottom-left", Color=BottomColor, Parent=BottomRow.widget)
        BottomElbow.widget.setFixedSize(100, 45)
        BottomLayout.addWidget(BottomElbow.widget)
        
        self.btnBios = LCARSButton("BIOS SETUP", Type="rect-left", Color=TopColor, Parent=BottomRow.widget)
        self.btnBios.widget.setFixedHeight(45)
        BottomLayout.addWidget(self.btnBios.widget)
        
        BottomBar = LCARSBar(Type="rect", Color=BottomColor, Parent=BottomRow.widget, Height=45)
        BottomLayout.addWidget(BottomBar.widget, 1)

        self.btnProceed = LCARSButton("PROCEED", Type="rect-right", Color=TopColor, Parent=BottomRow.widget)
        self.btnProceed.widget.setFixedHeight(45)
        self.btnProceed.clicked.connect(self.FinishInitialization)
        BottomLayout.addWidget(self.btnProceed.widget)
        
        self.BottomRow = BottomRow
        self.Add(root, BottomRow)
        BottomRow.widget.hide()
        self.AppendBootLine("LCARS BOOT CONSOLE ONLINE")
        self.AppendBootLine("WAITING FOR INITIALIZATION SEQUENCE")
        self.AppendBootLine("VISIBLE LOG STREAM ENABLED")

        if not self.PreviewMode:
            StartTimer = LCARS.Timer(self.widget)
            if hasattr(StartTimer, "setSingleShot"):
                StartTimer.setSingleShot(True)
            StartTimer.timeout.connect(self.RunInitialization)
            StartTimer.start(0)
            self.StartTimer = StartTimer

    def showEvent(self, event):
        if not self.sequenceActive and not self.PreviewMode:
            self.RunInitialization()

    def AppendBootLine(self, TextValue):
        if not hasattr(self, "BootConsole"):
            return
        self.BootQueue.append(str(TextValue))

    def TickBootText(self):
        if not hasattr(self, "BootConsole"):
            return

        if not self.BootTypingLine and self.BootQueue:
            self.BootTypingLine = self.BootQueue.pop(0)
            self.BootTypingIndex = 0

        if self.BootTypingLine:
            self.BootTypingIndex = min(len(self.BootTypingLine), self.BootTypingIndex + self.BootTypingSpeed)
            ActiveText = self.BootTypingLine[: self.BootTypingIndex]
            Lines = list(self.BootRendered)
            if len(Lines) >= 24:
                Lines = Lines[-23:]
            Lines.append(ActiveText + ("▌" if self.BootCursorVisible else ""))
            self.BootConsole.setPlainText("\n".join(Lines))
            if hasattr(self.BootConsole, "ensureCursorVisible"):
                self.BootConsole.ensureCursorVisible()
            self.BootCursorVisible = not self.BootCursorVisible
            if self.BootTypingIndex >= len(self.BootTypingLine):
                self.BootRendered.append(self.BootTypingLine)
                if len(self.BootRendered) > 24:
                    self.BootRendered = self.BootRendered[-24:]
                self.BootTypingLine = ""
                self.BootTypingIndex = 0
            return

        if self.BootRendered:
            CursorState = "▌" if self.BootCursorVisible else ""
            self.BootConsole.setPlainText("\n".join(self.BootRendered + ([CursorState] if CursorState else [])))
            if hasattr(self.BootConsole, "ensureCursorVisible"):
                self.BootConsole.ensureCursorVisible()
            self.BootCursorVisible = not self.BootCursorVisible

        self.UpdateBootDots()

    def UpdateBootDots(self):
        if not hasattr(self, "BootDotsLabel"):
            return
        Sequence = ["● ○ ○", "○ ● ○", "○ ○ ●", "○ ● ○"]
        self.BootDotsPhase = (self.BootDotsPhase + 1) % len(Sequence)
        Current = Sequence[self.BootDotsPhase]
        self.BootDotsLabel.SetText(Current)

    def OnTelemetryEvent(self, Payload):
        if isinstance(Payload, dict):
            Line = Payload.get("line")
            if Line is None:
                Source = str(Payload.get("source", "TELEMETRY")).upper()
                Level = str(Payload.get("level", "info")).upper()
                Message = str(Payload.get("message", ""))
                Line = f">> {Source} [{Level}]: {Message}"
        else:
            Line = str(Payload)
        self.AppendBootLine(Line)

    def RunInitialization(self):
        if self.PreviewMode:
            self.sequenceActive = True
            return
        if self.sequenceActive:
            return
        self.sequenceActive = True

        self.BootQueue = []
        self.BootRendered = []
        self.BootTypingLine = ""
        self.BootTypingIndex = 0
        self.AppendBootLine("LCARS BOOT CONSOLE ONLINE")
        self.AppendBootLine("ROUTE: " + self.Target.upper())
        self.AppendBootLine("ODN: LINK CHECK")
        self.AppendBootLine("BIOS: POST PENDING")
        self.AppendBootLine("INITIALIZER: STAGE MAP READY")
            
        InitSys = CreateInitializer(ProgressCallback=self.InitStage)
        InitSys.Failed.Connect(self.InitFailed)
        InitSys.Completed.Connect(self.InitFinished)
        
        LCARS.ProcessEvents()
        
        InitSys.Execute()

    def InitStage(self, stageName: str, progress: int):
        self.AppendBootLine(f"[{progress:03}%] {stageName}")
        if stageName == "REGISTER MAP":
            self.AppendBootLine("VERIFYING BASE TYPES AND REGISTRY SECTORS")
        elif stageName == "ODN BUS":
            self.AppendBootLine("OPENING TRANSMISSION PATHS")
        elif stageName == "BIOS POST":
            self.AppendBootLine("READING BIOS DIAGNOSTIC REPORT")
        LCARS.ProcessEvents()
        time.sleep(0.12)

    def InitFailed(self, payload):
        self.AppendBootLine("SYSTEM INIT FAILED")
        if isinstance(payload, dict):
            for item in payload.get("Errors", []):
                self.AppendBootLine("[ERROR] " + str(item))
            for item in payload.get("Warnings", []):
                self.AppendBootLine("[WARN] " + str(item))
        LCARS.ProcessEvents()
        if not self.PreviewMode:
            ODN.send("System.Phase.Emergency")

    def InitFinished(self, payload):
        self.AppendBootLine("SYSTEM INITIALIZATION COMPLETE")
            
        LCARS.ProcessEvents()
        time.sleep(0.2)
        if hasattr(self, "BootTitle"):
            self.BootTitle.widget.show()
        if hasattr(self, "BootSubtitle"):
            self.BootSubtitle.widget.show()
        if hasattr(self, "BootConsoleTitle"):
            self.BootConsoleTitle.widget.show()
        if hasattr(self, "TopRow"):
            self.TopRow.widget.show()
        if hasattr(self, "BottomRow"):
            self.BottomRow.widget.show()
        if hasattr(self, "BootDotsLabel"):
            self.BootDotsLabel.widget.hide()
        self.FinishInitialization()

    def FinishInitialization(self):
        if self.PreviewMode:
            self.AppendBootLine("PREVIEW HOLD: STAYING ON LOADING SCREEN")
            return
        self.AppendBootLine("HANDOFF: " + ("ACCESS" if self.Target == "login" else "DESKTOP"))
        if self.Target == "login":
            ODN.send("System.Phase.Access")
        else:
            ODN.send("System.Phase.Desktop")


def RunLoadingPreview():
    App = LCARS.Application(sys.argv)
    if App is None:
        return 1

    Loader = LCARSLoading(Target="preview")
    LoaderWidget = getattr(Loader, "widget", None)
    if LoaderWidget is None:
        return 1

    LoaderWidget.resize(1280, 720)
    LoaderWidget.setStyleSheet("background-color: #000000; border: none;")
    FramelessFlag = LCARS.Protocol.Display.Frameless
    if FramelessFlag and hasattr(LoaderWidget, "setWindowFlag"):
        LoaderWidget.setWindowFlag(FramelessFlag, True)
    Show = getattr(LoaderWidget, "showFullScreen", None)
    if Show:
        Show()
    else:
        LoaderWidget.show()

    App.processEvents()

    return App.exec()


if __name__ == "__main__":
    raise SystemExit(RunLoadingPreview())
