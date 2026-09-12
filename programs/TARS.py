# LCARS TARS — TACTICAL AUTONOMOUS RECONNAISSANCE & SYSTEMS PROGRAM
# ОПИС: Повноцінний графічний застосунок LCARS для тактичного агента TARS.
# ПРИЗНАЧЕННЯ: Візуальний інтерфейс калібрування матриці особистості (Honesty/Humor),
#              сприйняття інтерфейсу (UI Perception), тактична телеметрія 13 підсистем,
#              автономне виконання директив та управління рівнем бойової готовності.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
import sys
from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parent.parent)
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSLabel, LCARSIndicator, ActiveAudio
from lcars.base.interface import ScanningBar, DataBlock
PrimaryColor = Palette.Yellow[0]

PyQtModule = LCARS.Import("PyQt6.QtWidgets")

class TARSWorker(QtCoreModule.QThread):
    FinishedSignal = QtCoreModule.pyqtSignal(str)

    def __init__(self, DirectiveText: str, Parent=None):
        super().__init__(Parent)
        self.DirectiveText = DirectiveText

    def run(self):
        Agent = LCARSTARS.GetInstance()
        Response = Agent.Execute(self.DirectiveText)
        self.FinishedSignal.emit(Response)

class TARSApplication(PyQtModule.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS TARS // TACTICAL AUTONOMOUS SYSTEMS [02-04]")
        self.resize(1440, 900)
        self.setStyleSheet("background-color: #000000; color: #FF9900; font-family: 'LCARS', 'Arial', sans-serif;")

        self.Agent = LCARSTARS.GetInstance()
        self.ActiveWorker = None
        self.ConditionButtons = {}
        self.SubsystemLabels = {}

        self.BuildInterface()
        self.RefreshTelemetry()

    def BuildInterface(self):
        Central = PyQtModule.QWidget(self)
        self.setCentralWidget(Central)
        MainLayout = PyQtModule.QVBoxLayout(Central)
        MainLayout.setContentsMargins(16, 12, 16, 12)
        MainLayout.setSpacing(10)

        # 1. ВЕРХНІЙ ЗАГОЛОВОК (HEADER)
        HeaderRow = PyQtModule.QWidget(Central)
        HeaderLayout = PyQtModule.QHBoxLayout(HeaderRow)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(12)

        Badge = LCARSButton(Text="TARS", Form=LCARSButton.Pill, Color=PrimaryColor, Number="02-04", CornerRadius=4, Parent=HeaderRow)
        Badge.widget.setFixedSize(140, 48)
        HeaderLayout.addWidget(Badge.widget)

        TitleBox = PyQtModule.QVBoxLayout()
        SubTitle = PyQtModule.QLabel("SOVEREIGN-CLASS NCC-74205 // AUTONOMOUS TACTICAL PERCEPTION MATRIX", HeaderRow)
        SubTitle.setStyleSheet("font-size: 13px; color: " + Palette.Buttons[1] + "; letter-spacing: 1px;")
        TitleBox.addWidget(MainTitle)
        TitleBox.addWidget(SubTitle)
        HeaderLayout.addLayout(TitleBox, 1)
        self.ConditionBadge = PyQtModule.QLabel("CONDITION: GREEN", HeaderRow)
        self.ConditionBadge.setAlignment(QtCoreModule.Qt.AlignmentFlag.AlignCenter)
        self.ConditionBadge.setStyleSheet("background-color: #004411; color: #00FF66; font-size: 15px; font-weight: bold; border-radius: 4px; padding: 8px 16px; border: 1px solid #00FF66;")
        HeaderLayout.addWidget(self.ConditionBadge)

        self.GatewayBadge = PyQtModule.QLabel("GATEWAY: ONLINE", HeaderRow)
        self.GatewayBadge.setAlignment(QtCoreModule.Qt.AlignmentFlag.AlignCenter)
        self.GatewayBadge.setStyleSheet("background-color: #112233; color: #33CCFF; font-size: 14px; font-weight: bold; border-radius: 4px; padding: 8px 14px; border: 1px solid #33CCFF;")
        HeaderLayout.addWidget(self.GatewayBadge)

        MainLayout.addWidget(HeaderRow)

        Scan = ScanningBar(Color=PrimaryColor, Parent=Central)
        Scan.widget.setFixedHeight(4)
        MainLayout.addWidget(Scan.widget)

        # 2. ГОЛОВНИЙ РОБОЧИЙ ПРОСТІР (3 КОЛОНКИ: МАТРИЦЯ ОСОБИСТОСТІ | ДІАЛОГ | ТЕЛЕМЕТРІЯ)
        Workspace = PyQtModule.QHBoxLayout()
        Workspace.setSpacing(12)
        # ЛІВА КОЛОНКА — МАТРИЦЯ ОСОБИСТОСТІ ТА ТАКТИЧНІ КОМАНДИ
        LeftCol = PyQtModule.QWidget(Central)
        LeftCol.setFixedWidth(280)
        LeftLayout = PyQtModule.QVBoxLayout(LeftCol)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(8)

        SecLabel1 = PyQtModule.QLabel("◤ PERSONALITY MATRIX", LeftCol)
        SecLabel1.setStyleSheet("color: " + Palette.Buttons[4] + "; font-size: 14px; font-weight: bold;")
        LeftLayout.addWidget(SecLabel1)

        # Чесність (Honesty)
        HonLabel = PyQtModule.QLabel("HONESTY CALIBRATION", LeftCol)
        HonLabel.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        LeftLayout.addWidget(HonLabel)
        HonRow = PyQtModule.QHBoxLayout()
        for Val in [75, 90, 100]:
            Btn = LCARSButton(Text=str(Val) + "%", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=3, Parent=LeftCol)
            Btn.widget.setFixedHeight(30)
            TargetVal = Val
            Btn.Clicked.Connect(lambda *Args, V=TargetVal: self.QuickSetHonesty(V))
            HonRow.addWidget(Btn.widget)
        LeftLayout.addLayout(HonRow)

        # Гумор (Humor)
        HumLabel = PyQtModule.QLabel("HUMOR CALIBRATION", LeftCol)
        HumLabel.setStyleSheet("color: #FFFFFF; font-size: 12px;")
        LeftLayout.addWidget(HumLabel)
        HumRow = PyQtModule.QHBoxLayout()
        for Val in [0, 50, 65, 75, 90]:
            Btn = LCARSButton(Text=str(Val) + "%", Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=3, Parent=LeftCol)
            Btn.widget.setFixedHeight(30)
            TargetVal = Val
            Btn.Clicked.Connect(lambda *Args, V=TargetVal: self.QuickSetHumor(V))
            HumRow.addWidget(Btn.widget)
        LeftLayout.addLayout(HumRow)

        self.MatrixStatus = PyQtModule.QLabel(LeftCol)
        self.MatrixStatus.setStyleSheet("background-color: #0A0D14; border: 1px solid #334466; border-radius: 4px; padding: 8px; color: #CCDDFF; font-size: 12px;")
        LeftLayout.addWidget(self.MatrixStatus)
        self.UpdateMatrixStatusLabel()

        # Тактичні директиви
        SecLabel2 = PyQtModule.QLabel("◤ TACTICAL DIRECTIVES", LeftCol)
        SecLabel2.setStyleSheet("color: " + Palette.Buttons[4] + "; font-size: 14px; font-weight: bold; margin-top: 10px;")
        LeftLayout.addWidget(SecLabel2)

        BtnInspect = LCARSButton(Text="INSPECT LCARS UI", Form=LCARSButton.Soft, Color=Palette.Buttons[0], CornerRadius=4, Parent=LeftCol)
        BtnInspect.widget.setFixedHeight(38)
        BtnInspect.Clicked.Connect(self.OnInspectUIClicked)
        LeftLayout.addWidget(BtnInspect.widget)

        BtnDiag = LCARSButton(Text="DIAGNOSTIC TELEMETRY", Form=LCARSButton.Soft, Color=Palette.Buttons[3], CornerRadius=4, Parent=LeftCol)
        BtnDiag.widget.setFixedHeight(38)
        BtnDiag.Clicked.Connect(self.OnDiagnosticClicked)
        LeftLayout.addWidget(BtnDiag.widget)

        # Рівні тривоги
        AlertLabel = PyQtModule.QLabel("ALERT CONDITION COMMUTATION", LeftCol)
        AlertLabel.setStyleSheet("color: #FFFFFF; font-size: 12px; margin-top: 6px;")
        LeftLayout.addWidget(AlertLabel)
        AlertRow = PyQtModule.QHBoxLayout()
        for Lvl, Col in [("GREEN", "#00CC66"), ("YELLOW", "#FFCC00"), ("RED", "#FF3333")]:
            ABtn = LCARSButton(Text=Lvl, Form=LCARSButton.Soft, Color=Col, CornerRadius=3, Parent=LeftCol)
            ABtn.widget.setFixedHeight(32)
            TargetLvl = Lvl
            ABtn.Clicked.Connect(lambda *Args, L=TargetLvl: self.QuickSetAlert(L))
            AlertRow.addWidget(ABtn.widget)
        LeftLayout.addLayout(AlertRow)

        BtnClear = LCARSButton(Text="PURGE BUFFER", Form=LCARSButton.Soft, Color="#666666", CornerRadius=4, Parent=LeftCol)
        BtnClear.widget.setFixedHeight(34)
        BtnClear.Clicked.Connect(self.OnClearClicked)
        LeftLayout.addWidget(BtnClear.widget)

        LeftLayout.addStretch(1)
        Workspace.addWidget(LeftCol)

        # ЦЕНТРАЛЬНА КОНСОЛЬ — ДІАЛОГ ТА ВВЕДЕННЯ ДИРЕКТИВ
        CenterCol = PyQtModule.QWidget(Central)
        CenterLayout = PyQtModule.QVBoxLayout(CenterCol)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(8)

        self.ConsoleBox = PyQtModule.QTextEdit(CenterCol)
        self.ConsoleBox.setReadOnly(True)
        self.ConsoleBox.setStyleSheet(
            "background-color: #03060C; border: 2px solid " + PrimaryColor + "; border-radius: 6px; "
            + "color: #DDEEFF; font-family: 'Consolas', 'Lucida Console', monospace; font-size: 14px; padding: 12px;"
        )
        CenterLayout.addWidget(self.ConsoleBox, 1)

        self.StatusIndicator = PyQtModule.QLabel("◤ TARS READY // AWAITING DIRECTIVE", CenterCol)
        self.StatusIndicator.setStyleSheet("color: " + Palette.Buttons[1] + "; font-size: 13px; font-weight: bold; letter-spacing: 1px;")
        CenterLayout.addWidget(self.StatusIndicator)
        # Рядок введення
        InputRow = PyQtModule.QHBoxLayout()
        InputRow.setSpacing(8)

        self.DirectiveInput = PyQtModule.QLineEdit(CenterCol)
        self.DirectiveInput.setPlaceholderText("Enter tactical directive or query (e.g. 'TARS, доповідь про готовність', 'TARS, перевір інтерфейс')...")
        self.DirectiveInput.setStyleSheet(
            "background-color: #0A0F1A; border: 2px solid " + Palette.Buttons[1] + "; border-radius: 4px; "
            + "color: #FFFFFF; font-size: 15px; padding: 8px 12px;"
        )
        self.DirectiveInput.returnPressed.connect(self.OnTransmitClicked)
        InputRow.addWidget(self.DirectiveInput, 1)

        BtnTransmit = LCARSButton(Text="TRANSMIT DIRECTIVE", Form=LCARSButton.Soft, Color=Palette.Buttons[4], Number="TX-04", CornerRadius=4, Parent=CenterCol)
        BtnTransmit.widget.setFixedSize(200, 44)
        BtnTransmit.Clicked.Connect(self.OnTransmitClicked)
        InputRow.addWidget(BtnTransmit.widget)

        CenterLayout.addLayout(InputRow)
        Workspace.addWidget(CenterCol, 1)

        # ПРАВА КОЛОНКА — СТАН ПІДСИСТЕМ ТА СПРИЙНЯТТЯ ІНТЕРФЕЙСУ
        RightCol = PyQtModule.QWidget(Central)
        RightCol.setFixedWidth(280)
        RightLayout = PyQtModule.QVBoxLayout(RightCol)
        RightLayout.setContentsMargins(0, 0, 0, 0)
        RightLayout.setSpacing(8)

        TelTitle = PyQtModule.QLabel("◤ ODN SUBSYSTEM MATRIX", RightCol)
        TelTitle.setStyleSheet("color: " + Palette.Buttons[4] + "; font-size: 14px; font-weight: bold;")
        RightLayout.addWidget(TelTitle)

        SubsystemsList = [
            ("01", "WARP CORE", "#00FF66"),
            ("02", "IMPULSE ENGINES", "#00FF66"),
            ("03", "DEFLECTOR SHIELDS", "#00FF66"),
            ("04", "LONG-RANGE SENSORS", "#00FF66"),
            ("05", "TACTICAL WEAPONS", "#00FF66"),
            ("06", "ODN 1024-BIT BUS", "#00FF66"),
            ("07", "MAIN COMPUTER", "#00FF66"),
            ("08", "LIFE SUPPORT", "#00FF66"),
            ("09", "COMMUNICATIONS", "#00FF66"),
            ("10", "TRANSPORTER ARRAY", "#00FF66"),
            ("11", "NAVIGATIONAL DEFLECTOR", "#00FF66"),
            ("12", "SICKBAY MEDICAL CORE", "#00FF66"),
            ("13", "STRUCTURAL INTEGRITY", "#00FF66"),
        ]

        SubScroll = PyQtModule.QScrollArea(RightCol)
        SubScroll.setWidgetResizable(True)
        SubScroll.setStyleSheet("background-color: #050811; border: 1px solid #223355; border-radius: 4px;")
        SubContainer = PyQtModule.QWidget()
        SubLayout = PyQtModule.QVBoxLayout(SubContainer)
        SubLayout.setContentsMargins(6, 6, 6, 6)
        SubLayout.setSpacing(4)

        for Code, Name, Col in SubsystemsList:
            Row = PyQtModule.QHBoxLayout()
            LblCode = PyQtModule.QLabel(Code, SubContainer)
            LblCode.setFixedWidth(24)
            LblCode.setStyleSheet("color: " + Palette.Buttons[1] + "; font-size: 11px; font-weight: bold;")
            LblName = PyQtModule.QLabel(Name, SubContainer)
            LblName.setStyleSheet("color: #FFFFFF; font-size: 11px;")
            LblStatus = PyQtModule.QLabel("NOMINAL", SubContainer)
            LblStatus.setAlignment(QtCoreModule.Qt.AlignmentFlag.AlignRight)
            LblStatus.setStyleSheet("color: " + Col + "; font-size: 11px; font-weight: bold;")
            self.SubsystemLabels[Name] = LblStatus
            Row.addWidget(LblCode)
            Row.addWidget(LblName, 1)
            Row.addWidget(LblStatus)
            SubLayout.addLayout(Row)

        SubLayout.addStretch(1)
        SubScroll.setWidget(SubContainer)
        RightLayout.addWidget(SubScroll, 1)

        # Блок сприйняття UI
        PerTitle = PyQtModule.QLabel("◤ ACTIVE UI PERCEPTION", RightCol)
        PerTitle.setStyleSheet("color: " + Palette.Buttons[4] + "; font-size: 14px; font-weight: bold; margin-top: 6px;")
        RightLayout.addWidget(PerTitle)

        self.PerceptionFeed = PyQtModule.QLabel(RightCol)
        self.PerceptionFeed.setStyleSheet("background-color: #050811; border: 1px solid #223355; border-radius: 4px; padding: 8px; color: #99BBEE; font-size: 11px;")
        self.PerceptionFeed.setWordWrap(True)
        RightLayout.addWidget(self.PerceptionFeed)
        self.RefreshPerceptionFeed()

        Workspace.addWidget(RightCol)
        MainLayout.addLayout(Workspace, 1)

        # Початкове вітальне повідомлення
        self.AppendDialogue("◤ LCARS TARS TACTICAL AUTONOMOUS SYSTEM ONLINE")
        self.AppendDialogue("   Designation: TARS 02-04 // Sovereign-Class NCC-74205")
        self.AppendDialogue("   Personality: Honesty " + str(self.Agent.Honesty) + "%, Humor " + str(self.Agent.Humor) + "%, Trust " + str(self.Agent.Trust) + "%")
        self.AppendDialogue("   Tactical channels open. Ready for Commander directives.\n" + "=" * 65 + "\n")

    def UpdateMatrixStatusLabel(self):
        Txt = (
            "HONESTY: " + str(self.Agent.Honesty) + "%\n"
            + "HUMOR: " + str(self.Agent.Humor) + "%\n"
            + "TRUST: " + str(self.Agent.Trust) + "%\n"
            + "TACTICAL DISCRETION: " + str(self.Agent.Discretion) + "%"
        )
        self.MatrixStatus.setText(Txt)

    def RefreshPerceptionFeed(self):
        UIInfo = self.Agent.InspectUI()
        self.PerceptionFeed.setText(UIInfo.replace("◤ TARS UI PERCEPTION MATRIX:\n", "").strip())

    def RefreshTelemetry(self):
        CompMod = LCARS.Import("lcars.core.computer")
        if CompMod and hasattr(CompMod, "BoardComputer"):
            Board = CompMod.BoardComputer.GetInstance()
            if hasattr(Board, "Condition"):
                Cond = getattr(Board, "Condition", "GREEN")
                self.QuickSetAlert(Cond, Broadcast=False)

    def QuickSetHonesty(self, Val: int):
        ActiveAudio.play("click")
        self.Agent.SetPersonality(Honesty=Val)
        self.UpdateMatrixStatusLabel()
        self.AppendDialogue("[TARS]: Honesty calibrated to " + str(Val) + "%.")

    def QuickSetHumor(self, Val: int):
        ActiveAudio.play("click")
        self.Agent.SetPersonality(Humor=Val)
        self.UpdateMatrixStatusLabel()
        self.AppendDialogue("[TARS]: Humor parameter adjusted to " + str(Val) + "%.")

    def QuickSetAlert(self, Level: str, Broadcast: bool = True):
        ActiveAudio.play("click")
        Clean = str(Level).upper().strip()
        self.Agent.CurrentCondition = Clean
        if Broadcast:
            self.Agent.SetAlert(Clean)
        BgCol = "#004411" if Clean == "GREEN" else ("#443300" if Clean == "YELLOW" else "#440000")
        TxtCol = "#00FF66" if Clean == "GREEN" else ("#FFCC00" if Clean == "YELLOW" else "#FF3333")
        self.ConditionBadge.setText("CONDITION: " + Clean)
        self.ConditionBadge.setStyleSheet(
            "background-color: " + BgCol + "; color: " + TxtCol + "; font-size: 15px; font-weight: bold; border-radius: 4px; padding: 8px 16px; border: 1px solid " + TxtCol + ";"
        )
        if Broadcast:
            self.AppendDialogue("[TARS]: ALERT STATUS COMMUTED TO " + Clean + ".")

    def OnInspectUIClicked(self):
        ActiveAudio.play("click")
        self.RefreshPerceptionFeed()
        Report = self.Agent.InspectUI()
        self.AppendDialogue(Report)

    def OnDiagnosticClicked(self):
        ActiveAudio.play("click")
        Tel = self.Agent.GetTelemetry()
        self.AppendDialogue("◤ TARS SUBSYSTEM DIAGNOSTIC:\n" + Tel)

    def OnClearClicked(self):
        ActiveAudio.play("click")
        self.ConsoleBox.clear()
        self.AppendDialogue("◤ CONDUIT BUFFER PURGED. TARS STANDBY.\n")

    def OnTransmitClicked(self):
        DirectiveText = str(self.DirectiveInput.text()).strip()
        if not DirectiveText:
            return
        ActiveAudio.play("click")
        self.DirectiveInput.clear()
        self.AppendDialogue("\nCOMMANDER: " + DirectiveText)
        self.StatusIndicator.setText("◤ TARS PROCESSING DIRECTIVE...")
        self.StatusIndicator.setStyleSheet("color: #FFCC00; font-size: 13px; font-weight: bold;")

        self.ActiveWorker = TARSWorker(DirectiveText, self)
        self.ActiveWorker.FinishedSignal.connect(self.OnDirectiveFinished)
        self.ActiveWorker.start()

    def OnDirectiveFinished(self, ResponseText: str):
        self.StatusIndicator.setText("◤ TARS READY // AWAITING DIRECTIVE")
        self.StatusIndicator.setStyleSheet("color: " + Palette.Buttons[1] + "; font-size: 13px; font-weight: bold;")
        self.AppendDialogue("\nTARS: " + ResponseText + "\n" + "-" * 55)
        self.UpdateMatrixStatusLabel()
        self.RefreshPerceptionFeed()

    def AppendDialogue(self, Text: str):
        self.ConsoleBox.append(Text)
        ScrollBar = self.ConsoleBox.verticalScrollBar()
        if ScrollBar:
            ScrollBar.setValue(ScrollBar.maximum())

def Run():
    BaseApp = LCARS.Application
    App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
    if App is None and callable(BaseApp):
        App = BaseApp(sys.argv)
    Window = TARSApplication()
    Window.show()
    sys.exit(App.exec())

if __name__ == "__main__":
    Run()