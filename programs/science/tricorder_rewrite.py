# ◤ TR-590 TRICORDER — TITANIUM SCIENTIFIC v44.20 🖖
# LCARS Framework :: SCIENCE STATION // SENSOR MATRIX // NO Q PROTOCOL
# STANDARD: Titanium CamelCase — zero underscores.
from __future__ import annotations
import sys
import random
from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[2])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

import lcars.base.interface as UI
from lcars.base.type import Directive, Chassis, Lore, Matrix, Visual
from lcars.engineering.collector import Collector
from lcars.modules.sensory import sensory
from lcars.engineering.telemetry import EmitTelemetry
from lcars.system.odn.scanner import scanner as OdnScanner
from lcars.base.register import registry
from lcars.base.default import ALERT_RED, TitanPalette, RandomButtonColor

TricorderBaseClass = registry.get("Technical.Window")


class TricorderWindow(TricorderBaseClass):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TR-590 SCIENTIFIC TRICORDER")
        self.setFixedSize(600, 900)
        self.setWindowFlags(Directive.Protocol.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")

        self.AccentColor   = TitanPalette.Buttons[4]
        self.BgColor       = TitanPalette.Buttons[1]
        self.AlertColorHex = ALERT_RED

        self.ScanningActive = False
        self.EditActive     = False
        self.AlertActive    = False
        self.ScanMode       = "ALPHA"
        self.DragPosNode    = None

        self.CollectorNode = Collector()
        EmitTelemetry("Tricorder", "TASK: SYSTEM SCANNER ONLINE.")

        self.CenterWidget = Matrix(self)
        self.setCentralWidget(self.CenterWidget)
        MainLayout = Chassis.Vertical(self.CenterWidget)
        MainLayout.setSpacing(20)
        MainLayout.setContentsMargins(30, 30, 30, 30)

        # ── TOP: SCANNING AREA ──────────────────────────────────────
        TopGrid = Chassis.Horizontal()
        TopGrid.setSpacing(10)

        # Left column: scan mode selectors
        TopLeft = Chassis.Vertical()
        TopLeft.setSpacing(10)
        TopLeft.addStretch()
        self.NavButtonMap = {}
        for ModeLabel in ["ALPHA", "BETA", "DELTA", "GAMMA"]:
            NavBtn = UI.Button(ModeLabel, side="left", color=self.AccentColor)
            NavBtn.setFixedHeight(30)
            NavBtn.setMinimumWidth(100)
            NavBtn.clicked.connect(lambda Chk=False, M=ModeLabel: self.OnNavClicked(M))
            TopLeft.addWidget(NavBtn)
            self.NavButtonMap[ModeLabel] = NavBtn
        TopLeft.addStretch()
        TopGrid.addLayout(TopLeft)

        # Center column: scanner display
        CenterScanLayout = Chassis.Vertical()
        CenterScanLayout.setSpacing(5)

        TabsRow = Chassis.Horizontal()
        TabsRow.setSpacing(5)
        self.BtnData  = UI.Button("DATA",  side="none", color=RandomButtonColor())
        self.BtnSense = UI.Button("SENSE", side="none", color=RandomButtonColor())
        self.BtnData.clicked.connect(self.StartSystemScan)
        self.BtnSense.clicked.connect(self.StopScan)
        TabsRow.addWidget(self.BtnData, 1)
        TabsRow.addWidget(self.BtnSense, 1)

        self.ScannerDisplay = Visual.Text()
        self.ScannerDisplay.setReadOnly(True)
        self.ScannerDisplay.setMinimumSize(250, 200)
        self.ScannerDisplay.setStyleSheet(
            f"background-color: #001122;"
            f"border-right: 20px solid {TitanPalette.Accent[0]};"
            f"border-left: 20px solid {TitanPalette.Accent[0]};"
            f"border-radius: 20px;"
            f"color: {self.BgColor};"
            f"font-family: 'LCARS'; font-size: 14pt;"
        )
        self.ScannerDisplay.setPlainText(">>> SENSORS YIELDED\nWaiting...")

        self.BtnTracking = UI.Button("TRACKING MODE: ACTIVE", side="none", color=RandomButtonColor())
        self.BtnTracking.setFixedHeight(25)

        CenterScanLayout.addLayout(TabsRow)
        CenterScanLayout.addWidget(self.ScannerDisplay, 1)
        CenterScanLayout.addWidget(self.BtnTracking)
        TopGrid.addLayout(CenterScanLayout, 1)

        # Right column: power + numeric
        TopRight = Chassis.Vertical()
        TopRight.setSpacing(5)
        PwrRow = Chassis.Horizontal()
        PwrRow.setSpacing(5)
        self.BtnPwr   = UI.Button("PWR",   side="none", color=self.BgColor)
        self.BtnStdby = UI.Button("STDBY", side="none", color=self.BgColor)
        self.BtnPwr.clicked.connect(self.StartSystemScan)
        self.BtnStdby.clicked.connect(self.StopScan)
        PwrRow.addWidget(self.BtnPwr)
        PwrRow.addWidget(self.BtnStdby)
        TopRight.addLayout(PwrRow)

        NumColumn = Chassis.Vertical()
        NumColumn.setSpacing(2)
        for NumVal in range(10, 70, 10):
            BtnColor = self.BgColor if NumVal % 2 == 0 else self.AccentColor
            NumColumn.addWidget(UI.Button(str(NumVal), side="none", color=BtnColor))
        TopRight.addSpacing(10)
        TopRight.addLayout(NumColumn)
        TopGrid.addLayout(TopRight)

        MainLayout.addLayout(TopGrid)

        # ── MIDDLE: COM TRANSMISSION ─────────────────────────────────
        ComLabel = UI.Label("COM TRANSMISSION", background="black")
        ComLabel.setStyleSheet("color: white; font-family: 'LCARS'; font-size: 16pt; font-weight: bold;")
        MainLayout.addWidget(ComLabel)

        MidGrid = Chassis.Horizontal()
        MidGrid.setSpacing(10)

        # Elbow structure: FWD, RVS, INPUT, ERASE
        MidElbowLayout = Chassis.Vertical()
        MidElbowLayout.setSpacing(0)

        RowOne = Chassis.Horizontal()
        RowOne.setSpacing(5)
        self.BtnFwd = UI.Button("FWD", side="left",  color=RandomButtonColor())
        self.BtnRvs = UI.Button("RVS", side="none",  color=RandomButtonColor())
        self.BtnFwd.setFixedHeight(40)
        self.BtnRvs.setFixedHeight(40)
        RowOne.addWidget(self.BtnFwd, 1)
        RowOne.addWidget(self.BtnRvs, 1)

        RowTwo = Chassis.Horizontal()
        RowTwo.setSpacing(5)
        self.BtnInput = UI.Button("INPUT", side="left", color=self.AccentColor)
        self.BtnErase = UI.Button("ERASE", side="none", color=self.AccentColor)
        self.BtnInput.setFixedHeight(40)
        self.BtnErase.setFixedHeight(40)
        RowTwo.addWidget(self.BtnInput, 1)
        RowTwo.addWidget(self.BtnErase, 1)

        MidElbowLayout.addLayout(RowOne)
        MidElbowLayout.addSpacing(5)
        MidElbowLayout.addLayout(RowTwo)

        self.ComElbow = UI.Elbow("top-left", color=self.BgColor, thickness=40, radius=40)
        self.ComElbow.setFixedHeight(120)
        MidElbowLayout.addSpacing(5)
        MidElbowLayout.addWidget(self.ComElbow)
        MidGrid.addLayout(MidElbowLayout)

        # Center library buttons
        MidCenter = Chassis.Vertical()
        MidCenter.setSpacing(5)
        self.LibButtonMap = {}
        for LibLabel in ["GRP", "FLDR", "FILE", "VIEW"]:
            LibColor = self.BgColor if LibLabel != "VIEW" else self.AccentColor
            LibBtn = UI.Button(f"^ {LibLabel}", side="both", color=LibColor)
            LibBtn.setFixedHeight(22)
            LibBtn.clicked.connect(lambda Chk=False, L=LibLabel: self.OnLibClicked(L))
            MidCenter.addWidget(LibBtn)
            self.LibButtonMap[LibLabel] = LibBtn
        MidCenter.addStretch()
        MidGrid.addLayout(MidCenter)

        # Right: Library B
        LibB = Chassis.Vertical()
        LibB.setSpacing(5)
        LibBLabel = UI.Label("LIBRARY B", background="black")
        LibBLabel.setStyleSheet(
            f"color: {self.AlertColorHex}; font-family: 'LCARS'; font-size: 14pt; font-weight: bold;"
        )
        LibB.addWidget(LibBLabel)
        LibRowOne = Chassis.Horizontal()
        LibRowOne.addWidget(UI.Button("I", side="none", color=self.BgColor), 1)
        LibRowOne.addWidget(UI.Button("+", side="none", color=self.BgColor), 3)
        LibRowTwo = Chassis.Horizontal()
        LibRowTwo.addWidget(UI.Button("E", side="none", color=self.AccentColor), 1)
        LibRowTwo.addWidget(UI.Button("-", side="none", color=self.AccentColor), 3)
        LibB.addLayout(LibRowOne)
        LibB.addLayout(LibRowTwo)
        LibB.addStretch()
        MidGrid.addLayout(LibB)
        MainLayout.addLayout(MidGrid)

        # ── DATA BARS ────────────────────────────────────────────────
        DataBars = Chassis.Horizontal()
        DataBars.setSpacing(40)

        DbLeft = Chassis.Vertical()
        DbLeft.setSpacing(5)
        DbLeft.addWidget(UI.Button("452.88568.910", side="both", color=TitanPalette.Accent[0]))
        DbLeft.addWidget(UI.Button("045.13935.325", side="both", color=ALERT_RED))
        DbLeft.addWidget(UI.Button("599.28432.787", side="both", color=TitanPalette.Buttons[7]))

        DbRight = Chassis.Vertical()
        DbRight.setSpacing(5)
        DbRight.addWidget(UI.Button("84515.63.00811", side="both", color=RandomButtonColor()))
        DbRight.addWidget(UI.Button("15528.72.19630", side="both", color=RandomButtonColor()))
        DbRight.addWidget(UI.Button("90321.47.86544", side="both", color=RandomButtonColor()))

        DataBars.addLayout(DbLeft)
        DataBars.addLayout(DbRight)
        MainLayout.addLayout(DataBars)
        MainLayout.addSpacing(10)

        # ── BOTTOM: DEVICE INPUT ─────────────────────────────────────
        BotGrid = Chassis.Horizontal()
        BotGrid.setSpacing(10)

        BotLeft = Chassis.Vertical()
        BotLeft.setSpacing(0)

        BotLeftTop = Chassis.Horizontal()
        BotLeftTop.setSpacing(5)
        self.BtnEmerg = UI.Button("EMERG / IMAGE RECORD", side="left", color=self.AlertColorHex)
        BotLeftTop.addWidget(self.BtnEmerg, 1)
        BotLeft.addLayout(BotLeftTop)
        BotLeft.addSpacing(5)

        self.BotElbow = UI.Elbow("bottom-left", color=self.AccentColor, thickness=40, radius=40)
        self.BotElbow.setFixedHeight(80)
        BotLeft.addWidget(self.BotElbow)

        self.BtnExit = UI.Button("EXIT", side="both", color=self.AccentColor)
        self.BtnExit.setFixedHeight(40)
        BotLeft.addSpacing(5)
        BotLeft.addWidget(self.BtnExit)
        BotLeft.addStretch()
        BotGrid.addLayout(BotLeft)
        BotGrid.addSpacing(60)

        BotRight = Chassis.Vertical()
        BotRight.setSpacing(5)
        DevLabel = UI.Label("DEVICE INPUT", background="black")
        DevLabel.setStyleSheet(
            f"color: {self.AlertColorHex}; font-family: 'LCARS'; font-size: 14pt; font-weight: bold;"
        )
        BotRight.addWidget(DevLabel)

        self.BtnGeo = UI.Button("GEO", side="none", color=TitanPalette.Accent[0])
        self.BtnMet = UI.Button("MET", side="none", color=self.AlertColorHex)
        self.BtnBio = UI.Button("BIO", side="none", color=TitanPalette.Accent[0])
        self.BtnGeo.setFixedHeight(40)
        self.BtnMet.setFixedHeight(40)
        self.BtnBio.setFixedHeight(40)
        BotRight.addWidget(self.BtnGeo)
        BotRight.addWidget(self.BtnMet)
        BotRight.addWidget(self.BtnBio)
        BotRight.addStretch()
        BotGrid.addLayout(BotRight)
        MainLayout.addLayout(BotGrid)

        # ── BIND EVENTS ──────────────────────────────────────────────
        self.BtnFwd.clicked.connect(self.StartSystemScan)
        self.BtnInput.clicked.connect(self.StopScan)
        self.BtnExit.clicked.connect(self.close)
        self.BtnTracking.clicked.connect(self.ToggleEditMode)
        self.BtnEmerg.clicked.connect(self.TriggerRedAlert)
        self.BtnGeo.clicked.connect(self.RestoreDefaultPalette)
        self.BtnMet.clicked.connect(self.TriggerYellowAlert)
        self.BtnBio.clicked.connect(self.RestoreDefaultPalette)

        self.PulserNode = Lore.Pulser(self)
        self.PulserNode.timeout.connect(self.PerformScan)

    # ── NAVIGATION ───────────────────────────────────────────────────
    def OnNavClicked(self, ModeStr):
        self.ScanMode = ModeStr
        self.ScannerDisplay.setPlainText(
            f">>> CHANNEL {ModeStr} SELECTED.\nRecalibrating isolinear matrix..."
        )
        EmitTelemetry("Tricorder", f"TASK: SCAN MODE SWITCHED: {ModeStr}")

    def OnLibClicked(self, CmdStr):
        SampleFiles = [
            "log39.st", "isolinear5.db",
            "sensorarray.xml", "subspacetx.enc"
        ]
        ResultText = f">>> LIBRARY B: {CmdStr}\n"
        ResultText += "\n".join(
            [f" FOUND: {F}" for F in random.sample(SampleFiles, 2)]
        )
        self.ScannerDisplay.setPlainText(ResultText)

    # ── EDIT MODE ────────────────────────────────────────────────────
    def ToggleEditMode(self):
        self.EditActive = not self.EditActive
        if self.EditActive:
            self.BtnTracking.setText("TRACKING MODE: EDITING")
            EmitTelemetry("Tricorder", "TASK: CONSTRUCTION MODE ACTIVE")
        else:
            self.BtnTracking.setText("TRACKING MODE: ACTIVE")
            EmitTelemetry("Tricorder", "TASK: CONSTRUCTION MODE DEACTIVATED")

    # ── ALERTS ───────────────────────────────────────────────────────
    def TriggerRedAlert(self):
        self.AlertActive = True
        self.setStyleSheet("background-color: #220000; border: 3px solid #FF0000;")
        EmitTelemetry("Tricorder", "RED ALERT DEPLOYED", "critical")

    def TriggerYellowAlert(self):
        self.AlertActive = True
        self.setStyleSheet("background-color: #221000; border: 3px solid #FF9900;")
        EmitTelemetry("Tricorder", "YELLOW ALERT DEPLOYED", "warn")

    def RestoreDefaultPalette(self):
        self.AlertActive = False
        self.setStyleSheet("background-color: black; border: none;")
        self.ScannerDisplay.setStyleSheet(
            f"background-color: #001122;"
            f"border-right: 20px solid {self.AccentColor};"
            f"border-left: 20px solid {self.AccentColor};"
            f"border-radius: 20px;"
            f"color: {self.BgColor};"
            f"font-family: 'LCARS'; font-size: 14pt;"
        )
        EmitTelemetry("Tricorder", "CONDITION GREEN: Palette restored")

    # ── SCAN ─────────────────────────────────────────────────────────
    def StartSystemScan(self):
        EmitTelemetry("Tricorder", "PROCESS: INITIATING SENSOR SWEEP")
        self.ScanningActive = True
        self.ScannerDisplay.setPlainText(
            ">>> OMEGA SENSORS ACTIVE\nScanning subsystem matrix...\n"
        )
        self.PulserNode.start(1500)
        self.PerformScan()

    def StopScan(self):
        if not self.ScanningActive:
            return
        EmitTelemetry("Tricorder", "EVENT: SENSOR SWEEP HALTED")
        self.ScanningActive = False
        self.PulserNode.stop()
        self.ScannerDisplay.setPlainText(">>> SENSORS HALTED\nAwaiting commands.")
        self.ScannerDisplay.setStyleSheet(
            f"background-color: #001122;"
            f"border-right: 20px solid {self.AccentColor};"
            f"border-left: 20px solid {self.AccentColor};"
            f"border-radius: 20px;"
            f"color: {self.BgColor};"
            f"font-family: 'LCARS'; font-size: 14pt;"
        )

    def PerformScan(self):
        StatusData = sensory.GetCurrentSensoryData()
        CpuLoadVal = StatusData.get("SystemLoad", 0)
        RamVal     = StatusData.get("MemoryUsage", 0)
        TimeStr    = Directive.Chronon.now().strftime("%H:%M:%S")

        LogText  = f"=== SCAN MODE: {self.ScanMode} ===\n"
        LogText += f"SYSTEM CPU: {CpuLoadVal:.1f} %\n"
        LogText += f"SYSTEM RAM: {RamVal:.1f} %\n"

        if self.ScanMode == "BETA":
            NetData  = OdnScanner.GetNetworkIO()
            LogText += f"RX IN:  {NetData.get('ReceiveKbps', 0):.1f} kb/s\n"
            LogText += f"TX OUT: {NetData.get('TransmitKbps', 0):.1f} kb/s\n"
        elif self.ScanMode == "DELTA":
            ProcList = self.CollectorNode.GetProcessMatrix(5)
            LogText += f"PROCESSES: {len(ProcList)} active\n"
            LogText += f"THM REG:   {StatusData.get('CoreTemp', 0):.1f} C\n"
        elif self.ScanMode == "GAMMA":
            LogText += f"SHIELD:  {StatusData.get('ShieldStatus', 'ACTIVE')}\n"
            LogText += f"EPS:     {StatusData.get('EpsStatus', 'NOMINAL')}\n"

        LogText += f"\n> TACHYON SWEEP {TimeStr} — Nominal"

        if CpuLoadVal > 80:
            EmitTelemetry("Tricorder", "WARNING: SYSTEM OVERLOAD", "warn")
            self.ScannerDisplay.setStyleSheet(
                f"background-color: #330000;"
                f"border-right: 20px solid {self.AlertColorHex};"
                f"border-left: 20px solid {self.AlertColorHex};"
                f"border-radius: 20px;"
                f"color: {self.AccentColor};"
                f"font-family: 'LCARS'; font-size: 14pt;"
            )

        self.ScannerDisplay.setPlainText(LogText)

    # ── DRAG ─────────────────────────────────────────────────────────
    def mousePressEvent(self, EventNode):
        if EventNode.button() == Directive.Protocol.MouseButton.LeftButton:
            self.DragPosNode = (
                EventNode.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            EventNode.accept()

    def mouseMoveEvent(self, EventNode):
        if (EventNode.buttons() == Directive.Protocol.MouseButton.LeftButton
                and self.DragPosNode is not None):
            self.move(EventNode.globalPosition().toPoint() - self.DragPosNode)
            EventNode.accept()


# ── LAUNCH ───────────────────────────────────────────────────────────
def Launch():
    AppClass = registry.get("Technical.Application")
    AppNode  = AppClass.instance() or AppClass(sys.argv)
    AppNode.setStyle("Fusion")
    from lcars.base.default import FontSetup
    FontSetup()
    TricorderNode = TricorderWindow()
    TricorderNode.show()
    sys.exit(AppNode.exec())


if __name__ == "__main__":
    Launch()
