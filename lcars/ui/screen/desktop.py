# LCARS STARFLEET OS :: 25th CENTURY MASTER DESKTOP WORKSPACE
# ФАЙЛ: lcars/ui/screen/desktop.py
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# ПРИЗНАЧЕННЯ: Головний пункт управління зорельота (Mission Control Desktop Hub),
#              натхнений архітектурою CCX Control / Desktop.
#              Об'єднує внутрішніх агентів (Nova IDE, Copilot, Neural Core),
#              зовнішніх CLI-агентів (Gemini, Devin, OpenCode, Agy, Claude Code),
#              AI-провайдери (OpenRouter, Groqwen, Mistral, Astra, QVAC, LocalLLM),
#              менеджмент проєктів (LCARS-Framework та Geant4 Enterprise),
#              живий системний термінал GATEWAY DAEMON TERM та пряме керування ОС.

from __future__ import annotations
import lcars.base.default as DefaultMod
from lcars.base.default import Palette, SystemTheme
from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, ActiveAudio
from lcars.base.interface import Screen, ScanningBar
from lcars.base.desktop import LCARSDesktop as BaseLCARSDesktop
from lcars.core.signal import ODN
from lcars.system.alert import GetAlertSystem
from lcars.system.environment import Runtime
from lcars.service.provider import AIProviderManager


class LCARSDesktop(BaseLCARSDesktop):
    def __init__(self, parent=None, BoardComputer=None):
        self.TelemetryTimer = None
        self.ChronoTimer = None
        self.CpuLabel = None
        self.RamLabel = None
        self.DetailTitle = None
        self.DetailPath = None
        self.ChipCountLbl = None
        self.StardateLabel = None
        self.TimeLabel = None
        self.UptimeLabel = None
        self.FooterStatus = None
        self.AlertBtn = None
        self.LockBtn = None
        self.PowerBtn = None
        self.ModeBtn = None
        self.ModelBtn = None
        self.AlertState = "GREEN"
        self.ActivePage = "STATUS"
        self.ProcessorMode = "QUANTUM"
        self.UptimeSeconds = 0
        self.GatewayPort = int(Runtime.get("GATEWAY_PORT", Runtime.get("QVAC_PORT", 3055)) or 3055)
        self.SubsystemButtons = {}
        self.DaemonLogBox = None
        self.ProjectOutputBox = None
        self.CockpitResponseBox = None
        self.ActiveProjectKey = "LCARS"

        PathMod = LCARS.Import("pathlib")
        if PathMod and hasattr(PathMod, "Path"):
            self.ProjectRootLCARS = PathMod.Path(__file__).resolve().parents[3]
            self.ProjectRootEnterprise = self.ProjectRootLCARS.parent / "Geant4" / "Enterprise"
        else:
            self.ProjectRootLCARS = None
            self.ProjectRootEnterprise = None

        self.LogsList = [
            "[00:00:01] ◤ LCARS ODN CARRIER INITIALIZED // NCC-74205 [1024-BIT SUPERPOSITION]",
            "[00:00:01] ✓ MASTER SYSTEM CORE ONLINE // 8 CORE SERVICES ACTIVE",
            "[00:00:02] ✓ QUANTUM INTELLIGENCE CONNECTED // GATEWAY PORT " + str(self.GatewayPort) + " ONLINE",
            "[00:00:02] ✓ AI PROVIDERS READY // ACTIVE BACKENDS REGISTERED",
            "[00:00:03] >> MISSION CONTROL DESKTOP SYNTHESIS COMPLETE // STATUS: NOMINAL",
        ]

        if BoardComputer is not None:
            self.BoardComputer = BoardComputer
        else:
            from lcars.core.computer import BoardComputer as ShipComputer
            self.BoardComputer = ShipComputer.GetInstance()

        super().__init__(parent=parent)
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.SubscribeSignals()
        self.StartChronoTimer()
        self.StartTelemetryTimer()
        self.Select("STATUS", RecordHistory=False)

    def IsWidgetActive(self) -> bool:
        if not hasattr(self, "widget") or self.widget is None:
            return False
        SipMod = LCARS.Import("PyQt6.sip")
        if SipMod and hasattr(SipMod, "isdeleted"):
            if SipMod.isdeleted(self.widget):
                return False
        return True

    def SubscribeSignals(self):
        ODN.Listen("UI.AlertChanged", self.OnAlertChanged)
        ODN.Listen("UI.PaletteChanged", self.OnAlertChanged)
        ODN.Listen("AI.ModelChanged", self.OnModelChangedODN)
        ODN.Listen("System.Log", self.OnSystemLogODN)

    def UnsubscribeSignals(self):
        ODN.Disconnect("UI.AlertChanged", self.OnAlertChanged)
        ODN.Disconnect("UI.PaletteChanged", self.OnAlertChanged)
        ODN.Disconnect("AI.ModelChanged", self.OnModelChangedODN)
        ODN.Disconnect("System.Log", self.OnSystemLogODN)

    def close(self):
        self.UnsubscribeSignals()
        if hasattr(self, "ChronoTimer") and self.ChronoTimer:
            self.ChronoTimer.stop()
        if hasattr(self, "TelemetryTimer") and self.TelemetryTimer:
            self.TelemetryTimer.stop()
        if self.IsWidgetActive():
            self.widget.close()

    def OnAlertChanged(self, Packet=None, **Extra):
        if not self.IsWidgetActive():
            return
        Flags = getattr(Packet, "Flags", {}) if Packet else Extra
        LevelStr = Flags.get("Level", Extra.get("Level", "GREEN"))
        self.AlertState = str(LevelStr).upper()
        if self.AlertBtn:
            self.AlertBtn.SetText("ALERT: " + self.AlertState)
        if self.FooterStatus:
            self.FooterStatus.SetText(f"TACTICAL ALERT LEVEL: {self.AlertState} // ODN SYNCHRONIZED")
        if self.widget and hasattr(self.widget, "update"):
            self.widget.update()

    def OnSystemLogODN(self, Packet=None, **Extra):
        if not self.IsWidgetActive():
            self.UnsubscribeSignals()
            return
        DataPayload = getattr(Packet, "Data", Packet) if Packet is not None else None
        LogMsg = DataPayload or Extra.get("Message", "")
        if LogMsg:
            self.Log(str(LogMsg))

    def OnModelChangedODN(self, Packet=None, **Extra):
        if not self.IsWidgetActive():
            self.UnsubscribeSignals()
            return
        Flags = getattr(Packet, "Flags", {}) if Packet else Extra
        ModelName = Flags.get("Model", Extra.get("Model", "GROQWEN"))
        if self.ModelBtn:
            self.ModelBtn.SetText("MODEL: " + str(ModelName).upper())
        if self.FooterStatus:
            self.FooterStatus.SetText("AI INTELLIGENCE ROUTED TO [" + str(ModelName).upper() + "] // ODN SYNCHRONIZED")

    @staticmethod
    def AppendToBox(BoxWidget, TextLine: str):
        if BoxWidget is None:
            return
        if hasattr(BoxWidget, "append"):
            BoxWidget.append(TextLine)
        elif hasattr(BoxWidget, "appendPlainText"):
            BoxWidget.appendPlainText(TextLine)
        elif hasattr(BoxWidget, "insertPlainText"):
            BoxWidget.insertPlainText(TextLine + "\n")
        EndOp = getattr(getattr(LCARS.TextCursor, "MoveOperation", None), "End", None)
        if EndOp is not None and hasattr(BoxWidget, "moveCursor"):
            BoxWidget.moveCursor(EndOp)

    def Log(self, Message: str):
        DTV = LCARS.System.DateTime
        TimeStr = DTV.now().strftime("%H:%M:%S") if DTV and hasattr(DTV, "now") else "00:00:00"
        Entry = "[" + TimeStr + "] " + str(Message)
        self.LogsList.append(Entry)
        if len(self.LogsList) > 600:
            self.LogsList.pop(0)

        TargetBox = None
        if hasattr(self, "DaemonLogBox") and self.DaemonLogBox is not None:
            TargetBox = self.DaemonLogBox
        elif hasattr(self, "ProjectOutputBox") and self.ProjectOutputBox is not None:
            TargetBox = self.ProjectOutputBox

        if TargetBox is not None:
            self.AppendToBox(TargetBox, Entry)

    def ClearLogs(self):
        ActiveAudio.play("click")
        self.LogsList.clear()
        if hasattr(self, "DaemonLogBox") and self.DaemonLogBox is not None:
            self.DaemonLogBox.clear()
        self.Log(">> Log buffer cleared by Commander clearance.")

    def CopyLogs(self):
        ActiveAudio.play("click")
        App = LCARS.Application.instance()
        if App and hasattr(App, "clipboard"):
            Clipboard = App.clipboard()
            if Clipboard and hasattr(Clipboard, "setText"):
                AllText = "\n".join(self.LogsList)
                Clipboard.setText(AllText)
                if self.FooterStatus:
                    self.FooterStatus.SetText("DAEMON LOGS COPIED TO SYSTEM CLIPBOARD // " + str(len(self.LogsList)) + " ENTRIES")

    def FilterLogs(self, SearchQuery: str):
        if not hasattr(self, "DaemonLogBox") or self.DaemonLogBox is None:
            return
        Query = str(SearchQuery or "").strip().lower()
        self.DaemonLogBox.clear()
        for Item in self.LogsList:
            if not Query or Query in Item.lower():
                self.AppendToBox(self.DaemonLogBox, Item)

    def RunProjectCommand(self, CommandArgs, WorkingDir):
        ActiveAudio.play("click")
        CmdText = " ".join(CommandArgs)
        self.Log(">> [EXEC INITIATED]: " + CmdText + " (cwd: " + str(WorkingDir) + ")")
        SubprocessMod = LCARS.Import("subprocess")
        ThreadingMod = LCARS.Import("threading")
        if not SubprocessMod or not ThreadingMod:
            self.Log(">> [ERROR]: System process conduits unavailable")
            return

        def ExecutionWorker():
            Proc = SubprocessMod.Popen(
                CommandArgs,
                cwd=str(WorkingDir),
                stdout=SubprocessMod.PIPE,
                stderr=SubprocessMod.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            for Line in Proc.stdout:
                CleanLine = Line.rstrip()
                if CleanLine:
                    self.Log("   " + CleanLine)
            Proc.wait()
            self.Log(">> [COMPLETED]: " + CmdText + " -> Exit Code " + str(Proc.returncode))

        WorkerThread = ThreadingMod.Thread(target=ExecutionWorker, daemon=True)
        WorkerThread.start()

    def OpenInExplorer(self, TargetPath):
        ActiveAudio.play("click")
        OsMod = LCARS.Import("os")
        if OsMod and hasattr(OsMod, "startfile") and TargetPath:
            OsMod.startfile(str(TargetPath))
            self.Log(">> [EXPLORER]: Opened directory conduit: " + str(TargetPath))

    def LaunchExternalAgent(self, AgentName: str):
        ActiveAudio.play("click")
        from lcars.service.console import LCARSConsole
        self.Log(">> [AGENT DISPATCH]: Launching interactive agent in external ConPTY: " + str(AgentName))
        LCARSConsole.RunInteractiveProcess(AgentName, lambda Line: self.Log(Line))

    def SwitchProvider(self, ProviderName: str):
        ActiveAudio.play("click")
        AiMgr = AIProviderManager.GetInstance()
        if AiMgr:
            Success = AiMgr.SwitchModel(ProviderName)
            ActName = AiMgr.ActiveBackend.Name if AiMgr.ActiveBackend else ProviderName
            ODN.Emit("AI.ModelChanged", Model=ActName.upper(), Provider="CENTRAL_BRIDGE")
            self.Log(">> [AI SWITCH]: Neural Core routed to [" + ActName.upper() + "] (Success=" + str(Success) + ")")
            if self.ModelBtn:
                self.ModelBtn.SetText("MODEL: " + ActName.upper())
            if self.FooterStatus:
                self.FooterStatus.SetText("NEURAL CORE COMMUTED TO [" + ActName.upper() + "] // MATRIX NOMINAL")

    def PingProvider(self, ProviderName: str):
        ActiveAudio.play("click")
        AiMgr = AIProviderManager.GetInstance()
        self.Log(">> [PING]: Testing telemetry conduit to provider [" + str(ProviderName).upper() + "]...")
        if AiMgr:
            for Backend in AiMgr.Backends:
                if Backend.Name.lower() == str(ProviderName).lower():
                    IsAvail = Backend.CheckAvailable()
                    self.Log("   ✓ Backend: " + Backend.Name + " // Available: " + str(IsAvail) + " // Token: " + str(bool(getattr(Backend, "Token", None))))
                    if hasattr(Backend, "GetAvailableModels"):
                        self.Log("   ✓ Models: " + ", ".join(Backend.GetAvailableModels()[:3]))
                    return
        self.Log(">> [PING]: Provider [" + str(ProviderName) + "] checked // Standby on bridge.")

    def ToggleProcessorMode(self):
        ActiveAudio.play("click")
        NewMode = "OPTICAL" if self.ProcessorMode == "QUANTUM" else "QUANTUM"
        self.ProcessorMode = NewMode
        if self.BoardComputer:
            self.BoardComputer.RuntimeMode = NewMode
        if self.ModeBtn:
            self.ModeBtn.SetText("MODE: " + self.ProcessorMode)
        self.Log(">> [ODN MODE TOGGLE]: Core processor switched to " + self.ProcessorMode + " mode.")
        if self.FooterStatus:
            self.FooterStatus.SetText("PROCESSOR BUS RECONFIGURED TO " + self.ProcessorMode + " // TERAOPS SYNCHRONIZED")

    def OnAlertChanged(self, Packet=None, **Extra):
        if not self.IsWidgetActive():
            self.UnsubscribeSignals()
            return
        Flags = getattr(Packet, "Flags", {}) if Packet else {}
        LevelName = Flags.get("Level") or Extra.get("Level") or str(Packet or "")
        if not LevelName:
            AlertSys = GetAlertSystem()
            LevelName = AlertSys.Level.Name if AlertSys and hasattr(AlertSys, "Level") else "GREEN"
        self.AlertState = str(LevelName).upper()
        if self.AlertBtn:
            self.AlertBtn.SetText("ALERT: " + self.AlertState)
        if self.IsWidgetActive():
            self.widget.update()

    def Build(self):
        Root = self.widget.layout()
        if Root is None:
            Root = LCARS.Vertical(self.widget)
        Root.setContentsMargins(10, 8, 10, 8)
        Root.setSpacing(6)

        # 1. ТОП ХЕДЕР (LCARS TOP STRIP + ELBOW)
        TopBar = LCARS.Widget(self.widget)
        TopBar.setFixedHeight(50)
        TopBar.setStyleSheet("background-color: #000000;")
        TBL = LCARS.Horizontal(TopBar)
        TBL.setContentsMargins(0, 0, 0, 0)
        TBL.setSpacing(8)

        self.TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[4], Width=160, Height=50, Thickness=36, Radius=24, Parent=TopBar)
        TBL.addWidget(self.TopElbow.widget)

        TopStrip = LCARS.Widget(TopBar)
        TopStrip.setStyleSheet("background-color:" + Palette.Buttons[4] + ";border:none;border-radius:4px;")
        TSL = LCARS.Horizontal(TopStrip)
        TSL.setContentsMargins(16, 0, 16, 0)
        TSL.setSpacing(12)

        ShipName = getattr(self.BoardComputer, "ShipRegistry", "NCC-74205")
        ShipClass = getattr(self.BoardComputer, "ShipClass", "Sovereign-Class Master Core")
        self.TitleLabel = LCARSLabel(Text="STARSHIP " + str(ShipName) + " // " + str(ShipClass).upper() + " // MISSION DESKTOP", Color="#000000", FontSize=14, Parent=TopStrip)
        TSL.addWidget(self.TitleLabel.widget, 1)

        self.StardateLabel = LCARSLabel(Text="STARDATE " + self.ComputeStardate(), Color="#000000", FontSize=12, Parent=TopStrip)
        TSL.addWidget(self.StardateLabel.widget)

        self.TimeLabel = LCARSLabel(Text="00:00:00", Color="#000000", FontSize=12, Parent=TopStrip)
        TSL.addWidget(self.TimeLabel.widget)
        TBL.addWidget(TopStrip, 1)
        Root.addWidget(TopBar)

        # 2. ГОЛОВНЕ ТІЛО (БОКОВИЙ САЙДБАР + РОБОЧИЙ ПРОСТІР)
        Body = LCARS.Widget(self.widget)
        Body.setStyleSheet("background-color: #000000;")
        BL = LCARS.Horizontal(Body)
        BL.setContentsMargins(0, 0, 0, 0)
        BL.setSpacing(8)

        # САЙДБАР НАВІГАЦІЇ
        Rail = LCARS.Widget(Body)
        Rail.setFixedWidth(200)
        Rail.setStyleSheet("background-color: #000000;")
        RL = LCARS.Vertical(Rail)
        RL.setContentsMargins(0, 0, 0, 0)
        RL.setSpacing(4)

        Stations = [
            ("STATUS // CORE", "STATUS", 1),
            ("AGENT COCKPIT", "AGENTS", 2),
            ("AI PROVIDERS", "PROVIDERS", 3),
            ("PROJECTS", "PROJECTS", 4),
            ("DIRECT COCKPIT", "COCKPIT", 5),
            ("WORKBENCH", "WORKBENCH", 6),
            ("TERMINAL", "CONSOLE", 7),
            ("CONSTRUCTOR", "CONSTRUCTOR", 8),
            ("CHIP MATRIX", "PROGRAMS", 9),
        ]

        for SLabel, SKey, SSeed in Stations:
            Btn = LCARSButton(Text=SLabel, Form=LCARSButton.Soft, CornerRadius=4, Number=str(SSeed).zfill(2) + "-" + str(abs(hash(SLabel)) % 900 + 100), Parent=Rail)
            Btn.widget.setFixedHeight(34)
            K = SKey
            Btn.Clicked.Connect(lambda *A, K=K: self.Select(K))
            self.NavButtons[SKey] = Btn
            RL.addWidget(Btn.widget)

        RL.addStretch(1)

        # НИЖНІЙ СТАТУСНИЙ БЛОК САЙДБАРУ (CCX STYLE)
        StatusPod = LCARS.Widget(Rail)
        StatusPod.setStyleSheet("background-color: #050A14; border: 1px solid #1A2E44; border-radius: 4px;")
        SPL = LCARS.Vertical(StatusPod)
        SPL.setContentsMargins(8, 8, 8, 8)
        SPL.setSpacing(4)

        SPL.addWidget(LCARSLabel(Text="● ODN ONLINE", Color="#00FF99", FontSize=11, Parent=StatusPod).widget)
        SPL.addWidget(LCARSLabel(Text="GATEWAY PORT: " + str(self.GatewayPort), Color=Palette.Buttons[1], FontSize=10, Parent=StatusPod).widget)

        self.ModeBtn = LCARSButton(Text="MODE: " + self.ProcessorMode, Form=LCARSButton.Soft, Color=Palette.Buttons[3], CornerRadius=4, Parent=StatusPod)
        self.ModeBtn.widget.setFixedHeight(28)
        self.ModeBtn.Clicked.Connect(self.ToggleProcessorMode)
        SPL.addWidget(self.ModeBtn.widget)

        AiMgr = AIProviderManager.GetInstance()
        CurModelName = AiMgr.ActiveBackend.Name.upper() if AiMgr and AiMgr.ActiveBackend else "GROQWEN"
        self.ModelBtn = LCARSButton(Text="MODEL: " + CurModelName, Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=4, Parent=StatusPod)
        self.ModelBtn.widget.setFixedHeight(28)
        def CycleModelQuick():
            ModelsCycle = ["groqwen", "openrouter", "mistral", "qvac", "localllm"]
            CurIdx = 0
            for Idx, MName in enumerate(ModelsCycle):
                if MName.lower() in CurModelName.lower():
                    CurIdx = Idx
                    break
            NextModel = ModelsCycle[(CurIdx + 1) % len(ModelsCycle)]
            self.SwitchProvider(NextModel)
        self.ModelBtn.Clicked.Connect(CycleModelQuick)
        SPL.addWidget(self.ModelBtn.widget)

        self.AlertBtn = LCARSButton(Text="ALERT: GREEN", Form=LCARSButton.Soft, CornerRadius=4, Parent=StatusPod)
        self.AlertBtn.widget.setFixedHeight(28)
        self.AlertBtn.Clicked.Connect(self.CycleAlert)
        SPL.addWidget(self.AlertBtn.widget)

        RL.addWidget(StatusPod)

        self.LockBtn = LCARSButton(Text="LOCK CONSOLE", Form=LCARSButton.Soft, CornerRadius=4, Parent=Rail)
        self.LockBtn.widget.setFixedHeight(30)
        self.LockBtn.Clicked.Connect(self.ToggleLock)
        RL.addWidget(self.LockBtn.widget)

        self.PowerBtn = LCARSButton(Text="POWER DOWN", Form=LCARSButton.Soft, CornerRadius=4, Parent=Rail)
        self.PowerBtn.widget.setFixedHeight(30)
        self.PowerBtn.Clicked.Connect(self.Shutdown)
        RL.addWidget(self.PowerBtn.widget)

        self.BotElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[0], Width=200, Height=36, Thickness=24, Radius=20, Parent=Rail)
        RL.addWidget(self.BotElbow.widget)
        BL.addWidget(Rail)

        # ГОЛОВНИЙ РОБОЧИЙ ПРОСТІР
        self.WorkspaceWidget = LCARS.Widget(Body)
        self.WorkspaceWidget.setStyleSheet("background-color: #000000;")
        self.WorkspaceLayout = LCARS.Vertical(self.WorkspaceWidget)
        self.WorkspaceLayout.setContentsMargins(0, 0, 0, 0)
        self.WorkspaceLayout.setSpacing(0)
        BL.addWidget(self.WorkspaceWidget, 1)
        Root.addWidget(Body, 1)

        # 3. НИЖНІЙ ФУТЕР
        self.FooterBar = LCARSBar(Height=26, Color=Palette.Buttons[0], Parent=self.widget)
        self.FooterBar.widget.setFixedHeight(26)
        FBL = LCARS.Horizontal(self.FooterBar.widget)
        FBL.setContentsMargins(14, 0, 14, 0)
        self.FooterStatus = LCARSLabel(Text="STARSHIP " + str(ShipName) + " // BOARD COMPUTER QUANTUM CORE OPERATIONAL // READY", Color="#FFFFFF", FontSize=11, Parent=self.FooterBar.widget)
        FBL.addWidget(self.FooterStatus.widget, 1)
        Root.addWidget(self.FooterBar.widget)

    def ClearWorkspace(self):
        L = self.WorkspaceLayout
        while L.count():
            Item = L.takeAt(0)
            if Item and Item.widget():
                Item.widget().deleteLater()

    def Select(self, StationKey, RecordHistory=True):
        ActiveAudio.play("click")
        Target = str(StationKey or "STATUS").strip().upper()
        self.ActivePage = Target
        self.ClearWorkspace()

        if Target in ("STATUS", "WELCOME", "MSD", ""):
            self.ShowStatusMSD()
        elif Target == "AGENTS":
            self.ShowAgentsStation()
        elif Target == "PROVIDERS":
            self.ShowProvidersStation()
        elif Target == "PROJECTS":
            self.ShowProjectsStation()
        elif Target == "COCKPIT":
            self.ShowCockpitStation()
        elif Target == "WORKBENCH":
            from lcars.ui.workbench import ScienceWorkbench
            Wb = ScienceWorkbench(ParentNode=self.WorkspaceWidget)
            self.WorkspaceLayout.addWidget(Wb.widget if hasattr(Wb, "widget") else Wb, 1)
        elif Target == "CONSOLE":
            from lcars.ui.terminal import LCARSUnifiedTerminal
            Term = LCARSUnifiedTerminal(Parent=self.WorkspaceWidget, Compact=False)
            self.WorkspaceLayout.addWidget(Term.widget if hasattr(Term, "widget") else Term, 1)
        elif Target == "CONSTRUCTOR":
            from programs.constructor import TitaniumArchitectEngine
            Arch = TitaniumArchitectEngine(ParentNode=self.WorkspaceWidget)
            self.WorkspaceLayout.addWidget(Arch.widget if hasattr(Arch, "widget") else Arch, 1)
        elif Target == "PROGRAMS":
            self.ShowChipMatrix()
        else:
            self.ShowStatusMSD()

        if self.FooterStatus:
            ShipName = getattr(self.BoardComputer, "ShipRegistry", "NCC-74205")
            self.FooterStatus.SetText("STATION: [" + str(self.ActivePage) + "] // " + str(ShipName) + " CORE NOMINAL")

    def ToggleSubsystemState(self, SubsystemName: str):
        ActiveAudio.play("click")
        if self.BoardComputer and hasattr(self.BoardComputer, "GetSubsystemState") and hasattr(self.BoardComputer, "SetSubsystemState"):
            from lcars.core.computer import SubsystemState
            Current = self.BoardComputer.GetSubsystemState(SubsystemName)
            NewState = SubsystemState.Offline if SubsystemState.IsOperational(Current) else SubsystemState.Online
            self.BoardComputer.SetSubsystemState(SubsystemName, NewState)
            Btn = self.SubsystemButtons.get(SubsystemName)
            if Btn:
                Btn.SetText(str(SubsystemName).upper() + ": " + str(NewState))
            self.Log(">> [SUBSYSTEM]: " + str(SubsystemName).upper() + " transitioned to " + str(NewState))
            if self.FooterStatus:
                self.FooterStatus.SetText("SUBSYSTEM [" + str(SubsystemName).upper() + "] TRANSITIONED TO " + str(NewState))

    # СТАНЦІЯ 1: STATUS & GATEWAY CONTROL (CCX STYLE)
    def ShowStatusMSD(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(8, 4, 8, 4)
        ML.setSpacing(6)

        # 1. ТОП КАРТКИ МЕТРИК (CCX 4 METRIC CARDS)
        MetricsRow = LCARS.Widget(W)
        MetricsRow.setStyleSheet("background-color: #000000;")
        MRL = LCARS.Horizontal(MetricsRow)
        MRL.setContentsMargins(0, 0, 0, 0)
        MRL.setSpacing(8)

        # Картка 1: GATEWAY PORT
        CardPort = LCARS.Widget(MetricsRow)
        CardPort.setStyleSheet("background-color: #040810; border-left: 4px solid " + Palette.Buttons[1] + "; border-radius: 4px;")
        CPL = LCARS.Vertical(CardPort)
        CPL.setContentsMargins(8, 6, 8, 6)
        CPL.addWidget(LCARSLabel(Text="GATEWAY PORT", Color=Palette.Buttons[1], FontSize=10, Parent=CardPort).widget)
        CPL.addWidget(LCARSLabel(Text=str(self.GatewayPort), Color="#FFFFFF", FontSize=16, Parent=CardPort).widget)
        CPL.addWidget(LCARSLabel(Text="ODN 1024-BIT BUS", Color=Palette.Buttons[6], FontSize=9, Parent=CardPort).widget)
        MRL.addWidget(CardPort, 1)

        # Картка 2: UPTIME / STARDATE
        CardUptime = LCARS.Widget(MetricsRow)
        CardUptime.setStyleSheet("background-color: #040810; border-left: 4px solid " + Palette.Buttons[2] + "; border-radius: 4px;")
        CUL = LCARS.Vertical(CardUptime)
        CUL.setContentsMargins(8, 6, 8, 6)
        CUL.addWidget(LCARSLabel(Text="STARDATE / UPTIME", Color=Palette.Buttons[2], FontSize=10, Parent=CardUptime).widget)
        self.UptimeLabel = LCARSLabel(Text=self.ComputeStardate(), Color="#FFFFFF", FontSize=14, Parent=CardUptime)
        CUL.addWidget(self.UptimeLabel.widget)
        CUL.addWidget(LCARSLabel(Text="CHRONO CARRIER NOMINAL", Color=Palette.Buttons[6], FontSize=9, Parent=CardUptime).widget)
        MRL.addWidget(CardUptime, 1)

        # Картка 3: ACTIVE CHANNELS & AGENTS
        CardChannels = LCARS.Widget(MetricsRow)
        CardChannels.setStyleSheet("background-color: #040810; border-left: 4px solid " + Palette.Buttons[3] + "; border-radius: 4px;")
        CCL = LCARS.Vertical(CardChannels)
        CCL.setContentsMargins(8, 6, 8, 6)
        CCL.addWidget(LCARSLabel(Text="CHANNELS & AGENTS", Color=Palette.Buttons[3], FontSize=10, Parent=CardChannels).widget)
        SubCount = len(getattr(self.BoardComputer, "Subsystems", []))
        CCL.addWidget(LCARSLabel(Text=str(SubCount) + " SUBSYSTEMS", Color="#FFFFFF", FontSize=14, Parent=CardChannels).widget)
        CCL.addWidget(LCARSLabel(Text="8 AGENTS READY", Color=Palette.Buttons[6], FontSize=9, Parent=CardChannels).widget)
        MRL.addWidget(CardChannels, 1)

        # Картка 4: CORE TELEMETRY
        CardTele = LCARS.Widget(MetricsRow)
        CardTele.setStyleSheet("background-color: #040810; border-left: 4px solid " + Palette.Buttons[4] + "; border-radius: 4px;")
        CTL = LCARS.Vertical(CardTele)
        CTL.setContentsMargins(8, 6, 8, 6)
        CTL.addWidget(LCARSLabel(Text="CORE TELEMETRY", Color=Palette.Buttons[4], FontSize=10, Parent=CardTele).widget)
        self.CpuLabel = LCARSLabel(Text="CPU: --% // RAM: --%", Color="#FFFFFF", FontSize=13, Parent=CardTele)
        CTL.addWidget(self.CpuLabel.widget)
        CTL.addWidget(LCARSLabel(Text="MODE: " + self.ProcessorMode, Color=Palette.Buttons[6], FontSize=9, Parent=CardTele).widget)
        MRL.addWidget(CardTele, 1)

        ML.addWidget(MetricsRow)

        # 2. СМУГА СИСТЕМНИХ ДІЙ (CCX ACTION CONTROLS)
        ActionsRow = LCARS.Widget(W)
        ActionsRow.setStyleSheet("background-color: #000000;")
        ARL = LCARS.Horizontal(ActionsRow)
        ARL.setContentsMargins(0, 0, 0, 0)
        ARL.setSpacing(6)

        BtnStart = LCARSButton(Text="▶ START CORE", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=ActionsRow)
        BtnStart.widget.setFixedHeight(30)
        def OnStartCore():
            ActiveAudio.play("click")
            ODN.Emit("System.Core.Start")
            self.Log(">> [CORE]: Quantum Core Start signal broadcast on ODN bus.")
        BtnStart.Clicked.Connect(OnStartCore)
        ARL.addWidget(BtnStart.widget)

        BtnStop = LCARSButton(Text="■ STOP CORE", Form=LCARSButton.Soft, Color=Palette.Buttons[0], CornerRadius=4, Parent=ActionsRow)
        BtnStop.widget.setFixedHeight(30)
        def OnStopCore():
            ActiveAudio.play("click")
            ODN.Emit("System.Core.Stop")
            self.Log(">> [CORE]: Standby standby engaged for core subsystems.")
        BtnStop.Clicked.Connect(OnStopCore)
        ARL.addWidget(BtnStop.widget)

        BtnRestart = LCARSButton(Text="🔄 RESTART CORE", Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=4, Parent=ActionsRow)
        BtnRestart.widget.setFixedHeight(30)
        def OnRestartCore():
            ActiveAudio.play("click")
            ODN.Emit("System.Core.Restart")
            self.Log(">> [CORE]: Reboot cycle executed // Subsystems re-synchronized.")
        BtnRestart.Clicked.Connect(OnRestartCore)
        ARL.addWidget(BtnRestart.widget)

        ARL.addStretch(1)

        BtnNova = LCARSButton(Text="🌐 OPEN NOVA IDE", Form=LCARSButton.Soft, Color=Palette.Buttons[3], CornerRadius=4, Parent=ActionsRow)
        BtnNova.widget.setFixedHeight(30)
        BtnNova.Clicked.Connect(lambda: self.Select("WORKBENCH"))
        ARL.addWidget(BtnNova.widget)

        BtnPTY = LCARSButton(Text="💻 LAUNCH CONPTY SHELL", Form=LCARSButton.Soft, Color=Palette.Buttons[4], CornerRadius=4, Parent=ActionsRow)
        BtnPTY.widget.setFixedHeight(30)
        BtnPTY.Clicked.Connect(lambda: self.LaunchExternalAgent("cmd.exe"))
        ARL.addWidget(BtnPTY.widget)

        BtnRefresh = LCARSButton(Text="🔄 REFRESH", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=ActionsRow)
        BtnRefresh.widget.setFixedHeight(30)
        BtnRefresh.Clicked.Connect(self.UpdateLiveTelemetry)
        ARL.addWidget(BtnRefresh.widget)

        ML.addWidget(ActionsRow)

        # 3. ШЛЯХИ РОБОЧИХ ДИРЕКТОРІЙ (CCX PATHS BAR)
        PathsRow = LCARS.Widget(W)
        PathsRow.setStyleSheet("background-color: #03060C; border: 1px solid #1A2E44; border-radius: 4px;")
        PRL = LCARS.Horizontal(PathsRow)
        PRL.setContentsMargins(10, 4, 10, 4)
        PRL.setSpacing(8)

        PRL.addWidget(LCARSLabel(Text="FRAMEWORK:", Color=Palette.Buttons[2], FontSize=10, Parent=PathsRow).widget)
        PRL.addWidget(LCARSLabel(Text=str(self.ProjectRootLCARS or "c:/Users/Forge/MyProject/LCARS-Framework"), Color="#FFFFFF", FontSize=10, Parent=PathsRow).widget, 1)
        BtnExp1 = LCARSButton(Text="📁 OPEN", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=PathsRow)
        BtnExp1.widget.setFixedSize(70, 24)
        BtnExp1.Clicked.Connect(lambda: self.OpenInExplorer(self.ProjectRootLCARS))
        PRL.addWidget(BtnExp1.widget)

        PRL.addWidget(LCARSLabel(Text="ENTERPRISE:", Color=Palette.Buttons[3], FontSize=10, Parent=PathsRow).widget)
        PRL.addWidget(LCARSLabel(Text=str(self.ProjectRootEnterprise or "c:/Users/Forge/MyProject/Geant4/Enterprise"), Color="#FFFFFF", FontSize=10, Parent=PathsRow).widget, 1)
        BtnExp2 = LCARSButton(Text="📁 OPEN", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=PathsRow)
        BtnExp2.widget.setFixedSize(70, 24)
        BtnExp2.Clicked.Connect(lambda: self.OpenInExplorer(self.ProjectRootEnterprise))
        PRL.addWidget(BtnExp2.widget)

        ML.addWidget(PathsRow)

        # 4. SUBSYSTEM INTERACTIVE GRID
        SubGrid = LCARS.Widget(W)
        SubGrid.setStyleSheet("background-color: #000000;")
        SGL = LCARS.Horizontal(SubGrid)
        SGL.setContentsMargins(0, 0, 0, 0)
        SGL.setSpacing(6)

        PrimarySubs = ["WarpCore", "Sensors", "Shields", "ODNBus", "LifeSupport", "Communications"]
        for SubName in PrimarySubs:
            CurState = "ONLINE"
            if self.BoardComputer and hasattr(self.BoardComputer, "GetSubsystemState"):
                CurState = self.BoardComputer.GetSubsystemState(SubName)
            Btn = LCARSButton(Text=str(SubName).upper() + ": " + str(CurState), Form=LCARSButton.Soft, CornerRadius=4, Parent=SubGrid)
            Btn.widget.setFixedHeight(30)
            TargetSub = SubName
            Btn.Clicked.Connect(lambda *A, S=TargetSub: self.ToggleSubsystemState(S))
            self.SubsystemButtons[SubName] = Btn
            SGL.addWidget(Btn.widget, 1)
        ML.addWidget(SubGrid)

        # 5. GATEWAY DAEMON TERM (CCX LIVE LOG CONSOLE)
        TermContainer = LCARS.Widget(W)
        TermContainer.setStyleSheet("background-color: #03060C; border: 1px solid #1A2E44; border-radius: 4px;")
        TCL = LCARS.Vertical(TermContainer)
        TCL.setContentsMargins(8, 6, 8, 6)
        TCL.setSpacing(4)

        TermHeader = LCARS.Widget(TermContainer)
        TermHeader.setStyleSheet("background-color: transparent;")
        THL = LCARS.Horizontal(TermHeader)
        THL.setContentsMargins(0, 0, 0, 0)
        THL.setSpacing(6)

        THL.addWidget(LCARSLabel(Text=">_ GATEWAY DAEMON TERM", Color=Palette.Buttons[2], FontSize=12, Parent=TermHeader).widget)
        THL.addStretch(1)

        SearchInput = LCARS.Input(TermHeader)
        SearchInput.setPlaceholderText("Search logs...")
        SearchInput.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #336699; padding: 2px 6px; font-size: 9pt; border-radius: 3px;")
        SearchInput.setFixedWidth(160)
        if hasattr(SearchInput, "textChanged"):
            SearchInput.textChanged.connect(self.FilterLogs)
        THL.addWidget(SearchInput)

        BtnCopy = LCARSButton(Text="COPY LOGS", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=3, Parent=TermHeader)
        BtnCopy.widget.setFixedSize(90, 24)
        BtnCopy.Clicked.Connect(self.CopyLogs)
        THL.addWidget(BtnCopy.widget)

        BtnClear = LCARSButton(Text="CLEAR", Form=LCARSButton.Soft, Color=Palette.Buttons[0], CornerRadius=3, Parent=TermHeader)
        BtnClear.widget.setFixedSize(70, 24)
        BtnClear.Clicked.Connect(self.ClearLogs)
        THL.addWidget(BtnClear.widget)

        TCL.addWidget(TermHeader)

        self.DaemonLogBox = LCARS.Terminal(TermContainer)
        self.DaemonLogBox.setReadOnly(True)
        FontStack = "'LCARS', 'Bahnschrift SemiCondensed', 'Bahnschrift', 'Consolas', monospace"
        self.DaemonLogBox.setStyleSheet("background-color: #010204; color: #99CCFF; border: 1px solid #0D1B2A; font-size: 11px; font-family: " + FontStack + "; padding: 6px;")
        for Item in self.LogsList:
            self.AppendToBox(self.DaemonLogBox, Item)
        TCL.addWidget(self.DaemonLogBox, 1)

        # РЯДОК ДИРЕКТИВ
        DirRow = LCARS.Widget(TermContainer)
        DirRow.setStyleSheet("background-color: transparent;")
        DRL = LCARS.Horizontal(DirRow)
        DRL.setContentsMargins(0, 0, 0, 0)
        DRL.setSpacing(6)

        DRL.addWidget(LCARSLabel(Text="DIRECTIVE >", Color=Palette.Buttons[3], FontSize=11, Parent=DirRow).widget)
        DirInput = LCARS.Input(DirRow)
        DirInput.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #336699; padding: 4px 8px; font-family: 'Consolas', monospace; font-size: 10pt; border-radius: 4px;")
        DirInput.setPlaceholderText("Enter natural directive or system command (e.g. 'status', 'scan sensors', 'switch model openrouter')...")
        DRL.addWidget(DirInput, 1)

        BtnTransmit = LCARSButton(Text="TRANSMIT", Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=4, Parent=DirRow)
        BtnTransmit.widget.setFixedSize(110, 28)
        def OnTransmitDirective():
            CmdText = str(DirInput.text()).strip() if hasattr(DirInput, "text") else ""
            if not CmdText:
                return
            ActiveAudio.play("click")
            DirInput.clear()
            self.Log(">> DIRECTIVE SENT: " + CmdText)
            if self.BoardComputer:
                Resp = self.BoardComputer.ExecuteDirective(CmdText)
                Msg = Resp.get("Message", str(Resp)) if isinstance(Resp, dict) else str(Resp)
                self.Log("   ✓ " + str(Msg))
                if self.FooterStatus:
                    self.FooterStatus.SetText(">> " + str(Msg)[:80])
                ActiveAudio.play("acknowledge")
        BtnTransmit.Clicked.Connect(OnTransmitDirective)
        if hasattr(DirInput, "returnPressed"):
            DirInput.returnPressed.connect(OnTransmitDirective)
        DRL.addWidget(BtnTransmit.widget)

        TCL.addWidget(DirRow)
        ML.addWidget(TermContainer, 1)

        self.WorkspaceLayout.addWidget(W, 1)
        self.UpdateLiveTelemetry()

    # СТАНЦІЯ 2: AGENT COCKPIT (ВСІ ВНУТРІШНІ ТА ЗОВНІШНІ АГЕНТИ)
    def ShowAgentsStation(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(10, 8, 10, 8)
        ML.setSpacing(8)

        HeaderRow = LCARS.Widget(W)
        HeaderRow.setStyleSheet("background-color: transparent;")
        HRL = LCARS.Horizontal(HeaderRow)
        HRL.setContentsMargins(0, 0, 0, 0)
        HRL.addWidget(LCARSLabel(Text="STARFLEET AGENT COCKPIT // INTERNAL CORES & EXTERNAL CLI AGENTS", Color=Palette.Buttons[1], FontSize=14, Parent=HeaderRow).widget, 1)
        ML.addWidget(HeaderRow)

        Scan = ScanningBar(Color=Palette.Buttons[2], Parent=W)
        Scan.widget.setFixedHeight(4)
        ML.addWidget(Scan.widget)

        ScrollArea = LCARS.Buffer(W)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setStyleSheet("background-color: #000000; border: none;")

        Container = LCARS.Widget()
        Container.setStyleSheet("background-color: #000000;")
        CL = LCARS.Vertical(Container)
        CL.setContentsMargins(0, 0, 0, 0)
        CL.setSpacing(8)

        AgentsList = [
            ("NOVA IDE & WORKBENCH", "INTERNAL SYSTEM IDE", "Integrated dev environment, isolinear chip editor, Geant4 Enterprise visualizer.", "ONLINE [PORT " + str(self.GatewayPort) + "]", Palette.Buttons[1], lambda: self.Select("WORKBENCH")),
            ("STARFLEET COPILOT", "IN-PROCESS COPILOT", "Autonomous code assistant & isolinear circuit generator connected via central bridge.", "READY", Palette.Buttons[2], lambda: self.Select("COCKPIT")),
            ("ONBOARD NEURAL CORE", "QUANTUM INTELLIGENCE", "1024-bit Starship Sovereign central computer brain. Full access to all 13 subsystems.", "ACTIVE", Palette.Buttons[4], lambda: self.Select("STATUS")),
            ("GOOGLE GEMINI CLI", "EXTERNAL CLI AGENT", "Google Gemini developer CLI assistant running via interactive terminal conduit.", "PTY STANDBY", Palette.Buttons[3], lambda: self.LaunchExternalAgent("gemini")),
            ("COGNITION DEVIN CLI", "EXTERNAL CLI AGENT", "Autonomous software engineering CLI agent running via interactive terminal.", "PTY STANDBY", Palette.Buttons[0], lambda: self.LaunchExternalAgent("devin")),
            ("OPENCODE AGENT", "EXTERNAL CLI AGENT", "Terminal-based autonomous coding agent running via interactive terminal.", "PTY STANDBY", Palette.Buttons[6], lambda: self.LaunchExternalAgent("opencode")),
            ("ANTIGRAVITY CLI", "EXTERNAL CLI AGENT", "Google DeepMind Antigravity CLI system running via interactive terminal.", "PTY STANDBY", Palette.Buttons[2], lambda: self.LaunchExternalAgent("agy")),
            ("CLAUDE CODE", "EXTERNAL CLI AGENT", "Anthropic Claude Code CLI engineering agent running via interactive terminal.", "PTY STANDBY", Palette.Buttons[1], lambda: self.LaunchExternalAgent("claude")),
        ]

        Row = None
        for Idx, (AName, AType, ADesc, AStat, ACol, AAction) in enumerate(AgentsList):
            if Idx % 2 == 0:
                Row = LCARS.Widget(Container)
                Row.setStyleSheet("background-color: transparent;")
                RowL = LCARS.Horizontal(Row)
                RowL.setContentsMargins(0, 0, 0, 0)
                RowL.setSpacing(8)
                CL.addWidget(Row)

            Card = LCARS.Widget(Row)
            Card.setStyleSheet("background-color: #040810; border-left: 4px solid " + ACol + "; border-radius: 4px;")
            CardL = LCARS.Vertical(Card)
            CardL.setContentsMargins(10, 8, 10, 8)
            CardL.setSpacing(4)

            TopCardRow = LCARS.Widget(Card)
            TopCardRow.setStyleSheet("background-color: transparent;")
            TCRL = LCARS.Horizontal(TopCardRow)
            TCRL.setContentsMargins(0, 0, 0, 0)
            TCRL.addWidget(LCARSLabel(Text=AName, Color=ACol, FontSize=13, Parent=TopCardRow).widget, 1)
            TCRL.addWidget(LCARSLabel(Text=AStat, Color="#00FF99" if "ON" in AStat or "ACT" in AStat or "READ" in AStat else Palette.Buttons[3], FontSize=10, Parent=TopCardRow).widget)
            CardL.addWidget(TopCardRow)

            CardL.addWidget(LCARSLabel(Text="TYPE: " + AType, Color=Palette.Buttons[6], FontSize=10, Parent=Card).widget)
            CardL.addWidget(LCARSLabel(Text=ADesc, Color="#CCCCCC", FontSize=10, Parent=Card).widget)

            BtnAction = LCARSButton(Text="LAUNCH / ENGAGE", Form=LCARSButton.Soft, Color=ACol, CornerRadius=4, Parent=Card)
            BtnAction.widget.setFixedHeight(28)
            BtnAction.Clicked.Connect(AAction)
            CardL.addWidget(BtnAction.widget)

            RowL.addWidget(Card, 1)

        CL.addStretch(1)
        ScrollArea.setWidget(Container)
        ML.addWidget(ScrollArea, 1)
        self.WorkspaceLayout.addWidget(W, 1)

    # СТАНЦІЯ 3: PROVIDERS MATRIX (OPENROUTER & PROVIDER MANAGEMENT)
    def ShowProvidersStation(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(10, 8, 10, 8)
        ML.setSpacing(8)

        HeaderRow = LCARS.Widget(W)
        HeaderRow.setStyleSheet("background-color: transparent;")
        HRL = LCARS.Horizontal(HeaderRow)
        HRL.setContentsMargins(0, 0, 0, 0)
        HRL.addWidget(LCARSLabel(Text="NEURAL PROVIDER MATRIX // OPENROUTER, CLOUD & LOCAL ACCELERATORS", Color=Palette.Buttons[3], FontSize=14, Parent=HeaderRow).widget, 1)
        ML.addWidget(HeaderRow)

        Scan = ScanningBar(Color=Palette.Buttons[4], Parent=W)
        Scan.widget.setFixedHeight(4)
        ML.addWidget(Scan.widget)

        ScrollArea = LCARS.Buffer(W)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setStyleSheet("background-color: #000000; border: none;")

        Container = LCARS.Widget()
        Container.setStyleSheet("background-color: #000000;")
        CL = LCARS.Vertical(Container)
        CL.setContentsMargins(0, 0, 0, 0)
        CL.setSpacing(8)

        ProvidersData = [
            ("OPENROUTER GATEWAY", "openrouter", "Multi-model router (Claude 3.5 Sonnet, GPT-4o, DeepSeek V3, Llama 3.3 70B)", Palette.Buttons[1], bool(Runtime.get("OPENROUTER_API_KEY", ""))),
            ("GROQWEN CLOUD INFERENCE", "groqwen", "Ultra-fast Llama 70B inference via Groq Tensor Processing Units.", Palette.Buttons[2], bool(Runtime.get("GROQ_API_KEY", ""))),
            ("MISTRAL CODESTRAL", "mistral", "Mistral AI Codestral & Large models for deep reasoning and code synthesis.", Palette.Buttons[0], bool(Runtime.get("MISTRAL_API_KEY", ""))),
            ("ASTRA GPT-6 (EXPERIENTIAL)", "astra", "Experiential Labs GPT-6 Astra reasoning endpoint.", Palette.Buttons[4], bool(Runtime.get("EXPERIENTIAL_API_KEY", ""))),
            ("QVAC LOCAL RUNTIME", "qvac", "Local Quantum Vector Accelerator & async RPC worker on port " + str(self.GatewayPort) + ".", Palette.Buttons[3], True),
            ("LOCAL PYTORCH TRANSFORMERS", "localllm", "Local CPU/GPU Transformers (Qwen 2.5, Gemma 2, TinyLlama).", Palette.Buttons[6], True),
        ]

        AiMgr = AIProviderManager.GetInstance()
        ActiveProvName = AiMgr.ActiveBackend.Name.lower() if AiMgr and AiMgr.ActiveBackend else "groqwen"

        for PTitle, PKey, PDesc, PCol, HasToken in ProvidersData:
            Card = LCARS.Widget(Container)
            IsActive = (PKey == ActiveProvName)
            BorderCol = "#00FF99" if IsActive else PCol
            Card.setStyleSheet("background-color: #040810; border-left: 4px solid " + BorderCol + "; border-radius: 4px;")
            CardL = LCARS.Vertical(Card)
            CardL.setContentsMargins(12, 8, 12, 8)
            CardL.setSpacing(4)

            TRow = LCARS.Widget(Card)
            TRow.setStyleSheet("background-color: transparent;")
            TRL = LCARS.Horizontal(TRow)
            TRL.setContentsMargins(0, 0, 0, 0)
            TRL.addWidget(LCARSLabel(Text=PTitle, Color=BorderCol, FontSize=13, Parent=TRow).widget, 1)

            StatusTag = "ACTIVE PROVIDER" if IsActive else ("CONFIGURED" if HasToken else "API KEY REQUIRED")
            StatusCol = "#00FF99" if IsActive else (Palette.Buttons[1] if HasToken else Palette.Red[0])
            TRL.addWidget(LCARSLabel(Text=StatusTag, Color=StatusCol, FontSize=10, Parent=TRow).widget)
            CardL.addWidget(TRow)

            CardL.addWidget(LCARSLabel(Text=PDesc, Color="#CCCCCC", FontSize=10, Parent=Card).widget)

            BRow = LCARS.Widget(Card)
            BRow.setStyleSheet("background-color: transparent;")
            BRL = LCARS.Horizontal(BRow)
            BRL.setContentsMargins(0, 0, 0, 0)
            BRL.setSpacing(6)

            TargetKey = PKey
            BtnSetActive = LCARSButton(Text="SET ACTIVE", Form=LCARSButton.Soft, Color=PCol, CornerRadius=4, Parent=BRow)
            BtnSetActive.widget.setFixedSize(110, 26)
            BtnSetActive.Clicked.Connect(lambda *A, K=TargetKey: self.SwitchProvider(K))
            BRL.addWidget(BtnSetActive.widget)

            BtnPing = LCARSButton(Text="PING BACKEND", Form=LCARSButton.Soft, Color=Palette.Buttons[6], CornerRadius=4, Parent=BRow)
            BtnPing.widget.setFixedSize(110, 26)
            BtnPing.Clicked.Connect(lambda *A, K=TargetKey: self.PingProvider(K))
            BRL.addWidget(BtnPing.widget)

            BRL.addStretch(1)
            CardL.addWidget(BRow)

            CL.addWidget(Card)

        CL.addStretch(1)
        ScrollArea.setWidget(Container)
        ML.addWidget(ScrollArea, 1)
        self.WorkspaceLayout.addWidget(W, 1)

    # СТАНЦІЯ 4: PROJECTS MANAGER (LCARS & GEANT4 ENTERPRISE)
    def ShowProjectsStation(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(10, 8, 10, 8)
        ML.setSpacing(8)

        HeaderRow = LCARS.Widget(W)
        HeaderRow.setStyleSheet("background-color: transparent;")
        HRL = LCARS.Horizontal(HeaderRow)
        HRL.setContentsMargins(0, 0, 0, 0)
        HRL.addWidget(LCARSLabel(Text="MISSION CONTROL WORKSPACES // PROJECT REPOSITORIES & RUNTIMES", Color=Palette.Buttons[2], FontSize=14, Parent=HeaderRow).widget, 1)
        ML.addWidget(HeaderRow)

        Scan = ScanningBar(Color=Palette.Buttons[1], Parent=W)
        Scan.widget.setFixedHeight(4)
        ML.addWidget(Scan.widget)

        # ДВІ КАРТКИ ПРОЄКТІВ
        ProjRow = LCARS.Widget(W)
        ProjRow.setStyleSheet("background-color: #000000;")
        PRL = LCARS.Horizontal(ProjRow)
        PRL.setContentsMargins(0, 0, 0, 0)
        PRL.setSpacing(8)

        # Картка 1: LCARS-Framework
        Card1 = LCARS.Widget(ProjRow)
        BorderCol1 = "#00FF99" if self.ActiveProjectKey == "LCARS" else Palette.Buttons[1]
        Card1.setStyleSheet("background-color: #040810; border-left: 4px solid " + BorderCol1 + "; border-radius: 4px;")
        C1L = LCARS.Vertical(Card1)
        C1L.setContentsMargins(10, 8, 10, 8)
        C1L.setSpacing(4)
        C1L.addWidget(LCARSLabel(Text="LCARS-FRAMEWORK", Color=Palette.Buttons[1], FontSize=13, Parent=Card1).widget)
        C1L.addWidget(LCARSLabel(Text=str(self.ProjectRootLCARS), Color=Palette.Buttons[6], FontSize=10, Parent=Card1).widget)
        C1L.addWidget(LCARSLabel(Text="STATUS: ACTIVE REPOSITORY // TITANIUM COMPLIANT", Color="#FFFFFF", FontSize=10, Parent=Card1).widget)
        PRL.addWidget(Card1, 1)

        # Картка 2: Geant4 Enterprise
        Card2 = LCARS.Widget(ProjRow)
        BorderCol2 = "#00FF99" if self.ActiveProjectKey == "ENTERPRISE" else Palette.Buttons[4]
        Card2.setStyleSheet("background-color: #040810; border-left: 4px solid " + BorderCol2 + "; border-radius: 4px;")
        C2L = LCARS.Vertical(Card2)
        C2L.setContentsMargins(10, 8, 10, 8)
        C2L.setSpacing(4)
        C2L.addWidget(LCARSLabel(Text="GEANT4 ENTERPRISE", Color=Palette.Buttons[4], FontSize=13, Parent=Card2).widget)
        C2L.addWidget(LCARSLabel(Text=str(self.ProjectRootEnterprise), Color=Palette.Buttons[6], FontSize=10, Parent=Card2).widget)
        C2L.addWidget(LCARSLabel(Text="STATUS: QUANTUM PARTICLE SIMULATOR // ONLINE", Color="#FFFFFF", FontSize=10, Parent=Card2).widget)
        PRL.addWidget(Card2, 1)

        ML.addWidget(ProjRow)

        # КНОПКИ УПРАВЛІННЯ ПРОЄКТОМ
        CmdRow = LCARS.Widget(W)
        CmdRow.setStyleSheet("background-color: #000000;")
        CRL = LCARS.Horizontal(CmdRow)
        CRL.setContentsMargins(0, 0, 0, 0)
        CRL.setSpacing(6)

        BtnPytest = LCARSButton(Text="RUN PYTEST SUITE", Form=LCARSButton.Soft, Color=Palette.Buttons[1], CornerRadius=4, Parent=CmdRow)
        BtnPytest.widget.setFixedHeight(30)
        BtnPytest.Clicked.Connect(lambda: self.RunProjectCommand(["py", "-3.14", "-m", "pytest"], self.ProjectRootLCARS))
        CRL.addWidget(BtnPytest.widget)

        BtnPost = LCARSButton(Text="RUN BIOS POST SELF-TEST", Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=4, Parent=CmdRow)
        BtnPost.widget.setFixedHeight(30)
        BtnPost.Clicked.Connect(lambda: self.RunProjectCommand(["py", "-3.14", "terminal.py", "--test"], self.ProjectRootLCARS))
        CRL.addWidget(BtnPost.widget)

        BtnGit = LCARSButton(Text="GIT STATUS & AUDIT", Form=LCARSButton.Soft, Color=Palette.Buttons[3], CornerRadius=4, Parent=CmdRow)
        BtnGit.widget.setFixedHeight(30)
        BtnGit.Clicked.Connect(lambda: self.RunProjectCommand(["git", "status", "-s"], self.ProjectRootLCARS))
        CRL.addWidget(BtnGit.widget)

        BtnVS = LCARSButton(Text="OPEN IN VS CODE", Form=LCARSButton.Soft, Color=Palette.Buttons[4], CornerRadius=4, Parent=CmdRow)
        BtnVS.widget.setFixedHeight(30)
        BtnVS.Clicked.Connect(lambda: self.RunProjectCommand(["code", "."], self.ProjectRootLCARS))
        CRL.addWidget(BtnVS.widget)

        BtnExp = LCARSButton(Text="OPEN IN EXPLORER", Form=LCARSButton.Soft, Color=Palette.Buttons[0], CornerRadius=4, Parent=CmdRow)
        BtnExp.widget.setFixedHeight(30)
        BtnExp.Clicked.Connect(lambda: self.OpenInExplorer(self.ProjectRootLCARS))
        CRL.addWidget(BtnExp.widget)

        ML.addWidget(CmdRow)

        # ТЕРМІНАЛЬНИЙ ВИВІД ПРОЄКТУ
        self.ProjectOutputBox = LCARS.Terminal(W)
        self.ProjectOutputBox.setReadOnly(True)
        FontStack = "'LCARS', 'Bahnschrift SemiCondensed', 'Bahnschrift', 'Consolas', monospace"
        self.ProjectOutputBox.setStyleSheet("background-color: #020408; color: #99CCFF; border: 1px solid #1A2E44; font-size: 11px; font-family: " + FontStack + "; padding: 6px;")
        for Item in self.LogsList[-20:]:
            self.AppendToBox(self.ProjectOutputBox, Item)
        ML.addWidget(self.ProjectOutputBox, 1)

        self.WorkspaceLayout.addWidget(W, 1)

    # СТАНЦІЯ 5: DIRECT COCKPIT (ДИАЛОГ ТА ДИРЕКТИВИ АГЕНТАМ)
    def ShowCockpitStation(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(10, 8, 10, 8)
        ML.setSpacing(8)

        HeaderRow = LCARS.Widget(W)
        HeaderRow.setStyleSheet("background-color: transparent;")
        HRL = LCARS.Horizontal(HeaderRow)
        HRL.setContentsMargins(0, 0, 0, 0)
        HRL.addWidget(LCARSLabel(Text="CONVERSATION & SUBAGENT DISPATCH BOARD // DIRECT REASONING", Color=Palette.Buttons[1], FontSize=14, Parent=HeaderRow).widget, 1)
        ML.addWidget(HeaderRow)

        Scan = ScanningBar(Color=Palette.Buttons[2], Parent=W)
        Scan.widget.setFixedHeight(4)
        ML.addWidget(Scan.widget)

        # ВІКНО ВІДПОВІДІ ТА РОЗДУМІВ
        self.CockpitResponseBox = LCARS.Terminal(W)
        self.CockpitResponseBox.setReadOnly(True)
        FontStack = "'LCARS', 'Bahnschrift SemiCondensed', 'Bahnschrift', 'Consolas', monospace"
        self.CockpitResponseBox.setStyleSheet("background-color: #020408; color: #99CCFF; border: 1px solid #1A2E44; font-size: 12px; font-family: " + FontStack + "; padding: 8px;")
        self.AppendToBox(self.CockpitResponseBox, "◤ COCKPIT CHANNEL ESTABLISHED. READY FOR NATURAL DIRECTIVES.")
        ML.addWidget(self.CockpitResponseBox, 1)

        # ПОЛЕ ВВОДУ
        PromptInput = LCARS.Input(W)
        PromptInput.setStyleSheet("background-color: #050A14; color: #99CCFF; border: 1px solid #336699; padding: 6px 10px; font-family: 'Consolas', monospace; font-size: 11pt; border-radius: 4px;")
        PromptInput.setPlaceholderText("Enter natural language directive in Ukrainian or English...")
        ML.addWidget(PromptInput)

        # КНОПКИ ВІДПРАВКИ
        ActionRow = LCARS.Widget(W)
        ActionRow.setStyleSheet("background-color: transparent;")
        ARL = LCARS.Horizontal(ActionRow)
        ARL.setContentsMargins(0, 0, 0, 0)
        ARL.setSpacing(8)

        BtnSend = LCARSButton(Text="TRANSMIT DIRECTIVE", Form=LCARSButton.Soft, Color=Palette.Buttons[2], CornerRadius=4, Parent=ActionRow)
        BtnSend.widget.setFixedHeight(32)
        def OnTransmitPrompt():
            TextVal = str(PromptInput.text()).strip() if hasattr(PromptInput, "text") else ""
            if not TextVal:
                return
            ActiveAudio.play("click")
            PromptInput.clear()
            self.AppendToBox(self.CockpitResponseBox, "\n>> COMMANDER DIRECTIVE: " + TextVal)
            self.Log(">> COCKPIT TRANSMISSION: " + TextVal)
            AiMgr = AIProviderManager.GetInstance()
            Resp = AiMgr.Route([{"role": "user", "content": TextVal}]) if AiMgr else "AI Manager Offline"
            self.Log("<< RESPONSE: " + str(Resp)[:100] + "...")
            ActiveAudio.play("acknowledge")
        BtnSend.Clicked.Connect(OnTransmitPrompt)
        if hasattr(PromptInput, "returnPressed"):
            PromptInput.returnPressed.connect(OnTransmitPrompt)
        ARL.addWidget(BtnSend.widget)

        BtnClear = LCARSButton(Text="CLEAR OUTPUT", Form=LCARSButton.Soft, Color=Palette.Buttons[0], CornerRadius=4, Parent=ActionRow)
        BtnClear.widget.setFixedHeight(32)
        BtnClear.Clicked.Connect(lambda: self.CockpitResponseBox.clear())
        ARL.addWidget(BtnClear.widget)

        ARL.addStretch(1)
        ML.addWidget(ActionRow)

        self.WorkspaceLayout.addWidget(W, 1)

    # СТАНЦІЯ: CHIP MATRIX
    def ShowChipMatrix(self):
        W = LCARS.Widget(self.WorkspaceWidget)
        W.setStyleSheet("background-color: #000000;")
        ML = LCARS.Vertical(W)
        ML.setContentsMargins(10, 8, 10, 8)
        ML.setSpacing(8)

        TRow = LCARS.Widget(W)
        TRL = LCARS.Horizontal(TRow)
        TRL.setContentsMargins(0, 0, 0, 0)
        TRL.addWidget(LCARSLabel(Text="ISOLINEAR CHIP MATRIX // 42-BIT OPTICAL DATA VAULT", Color=Palette.Buttons[3], FontSize=14, Parent=TRow).widget, 1)
        self.ChipCountLbl = LCARSLabel(Text="CHIPS: --", Color=Palette.Buttons[1], FontSize=12, Parent=TRow)
        TRL.addWidget(self.ChipCountLbl.widget)
        ML.addWidget(TRow)

        ScanB2 = ScanningBar(Color=Palette.Buttons[3], Parent=W)
        ScanB2.widget.setFixedHeight(4)
        ML.addWidget(ScanB2.widget)

        Content = LCARS.Widget(W)
        Content.setStyleSheet("background-color: #000000;")
        CL = LCARS.Horizontal(Content)
        CL.setContentsMargins(0, 0, 0, 0)
        CL.setSpacing(10)

        ScrollArea = LCARS.Buffer(Content)
        ScrollArea.setWidgetResizable(True)
        ScrollArea.setStyleSheet("background-color:#000000;border:none;")

        ChipBox = LCARS.Widget()
        ChipBox.setStyleSheet("background-color:#000000;")
        ChipBoxL = LCARS.Vertical(ChipBox)
        ChipBoxL.setContentsMargins(0, 0, 0, 0)
        ChipBoxL.setSpacing(4)

        from lcars.modules.storage import ListChips
        Chips = ListChips() if callable(ListChips) else []
        if self.ChipCountLbl:
            self.ChipCountLbl.SetText("CHIPS ONLINE: " + str(len(Chips)))

        for ChipData in Chips:
            ChipId = ChipData.get("ChipId", "00-0000")
            Name = ChipData.get("Name", "UNKNOWN")
            Sector = ChipData.get("Sector", "00")
            Btn = LCARSButton(
                Text="[" + str(Sector) + "] " + str(ChipId) + "  " + str(Name).upper(),
                Form=LCARSButton.Soft, CornerRadius=4,
                Number=str(ChipId), Parent=ChipBox
            )
            Btn.widget.setFixedHeight(30)
            D = ChipData
            Btn.Clicked.Connect(lambda *A, D=D: self.OnChipClicked(D))
            ChipBoxL.addWidget(Btn.widget)

        ChipBoxL.addStretch(1)
        ScrollArea.setWidget(ChipBox)
        CL.addWidget(ScrollArea, 2)

        InfoBox = LCARS.Widget(Content)
        InfoBox.setStyleSheet("background-color:#03060C;border-left:4px solid " + Palette.Buttons[4] + ";")
        IL = LCARS.Vertical(InfoBox)
        IL.setContentsMargins(12, 12, 12, 12)
        IL.setSpacing(8)
        IL.addWidget(LCARSLabel(Text="ISOLINEAR SUB-CIRCUIT ANALYSIS", Color=Palette.Buttons[4], FontSize=13, Parent=InfoBox).widget)
        self.DetailTitle = LCARSLabel(Text="SELECT CHIP FROM LEFT REGISTER", Color=Palette.Buttons[1], FontSize=12, Parent=InfoBox)
        self.DetailPath = LCARSLabel(Text="DATABASE PATH: STANDBY", Color=Palette.Buttons[6], FontSize=11, Parent=InfoBox)
        IL.addWidget(self.DetailTitle.widget)
        IL.addWidget(self.DetailPath.widget)
        IL.addStretch(1)
        CL.addWidget(InfoBox, 1)

        ML.addWidget(Content, 1)
        self.WorkspaceLayout.addWidget(W, 1)

    def OnChipClicked(self, ChipData):
        ActiveAudio.play("click")
        if self.DetailTitle:
            self.DetailTitle.SetText("CHIP " + str(ChipData.get("ChipId", "")) + " // SECTOR " + str(ChipData.get("Sector", "")))
        if self.DetailPath:
            self.DetailPath.SetText("PATH: " + str(ChipData.get("Path", "N/A")))

    def CycleAlert(self, Packet=None):
        ActiveAudio.play("click")
        NewLevel = GetAlertSystem().CycleLevel()
        self.AlertState = NewLevel.Name
        DefaultMod.SystemState = NewLevel.Name
        self.AlertBtn.SetText("ALERT: " + self.AlertState)
        self.widget.update()
        ODN.Emit("System.Alert", self.AlertState)

    def ToggleLock(self, Packet=None):
        ActiveAudio.play("click")
        ODN.Emit("System.Phase.Login")

    def Shutdown(self, Packet=None):
        ActiveAudio.play("acknowledge")
        App = LCARS.Application.instance()
        if App and hasattr(App, "quit"):
            App.quit()

    def StartChronoTimer(self):
        self.ChronoTimer = LCARS.Timer(self.widget)
        self.ChronoTimer.setInterval(1000)
        self.ChronoTimer.timeout.connect(self.OnChronoTick)
        self.ChronoTimer.start()

    def OnChronoTick(self):
        self.UptimeSeconds += 1
        DTV = LCARS.System.DateTime
        if DTV and hasattr(DTV, "now"):
            Now = DTV.now()
            if hasattr(Now, "strftime"):
                if self.StardateLabel:
                    self.StardateLabel.SetText("STARDATE " + self.ComputeStardate())
                if self.TimeLabel:
                    self.TimeLabel.SetText(Now.strftime("%H:%M:%S"))
                if self.UptimeLabel:
                    Mins, Secs = divmod(self.UptimeSeconds, 60)
                    Hrs, Mins = divmod(Mins, 60)
                    UptimeStr = str(Hrs).zfill(2) + ":" + str(Mins).zfill(2) + ":" + str(Secs).zfill(2)
                    self.UptimeLabel.SetText(self.ComputeStardate() + " // " + UptimeStr)

    def StartTelemetryTimer(self):
        self.TelemetryTimer = LCARS.Timer(self.widget)
        self.TelemetryTimer.setInterval(2500)
        self.TelemetryTimer.timeout.connect(self.UpdateLiveTelemetry)
        self.TelemetryTimer.start()

    def UpdateLiveTelemetry(self):
        PsUtil = LCARS.Import("psutil")
        if PsUtil and hasattr(PsUtil, "cpu_percent") and hasattr(PsUtil, "virtual_memory"):
            CpuVal = round(PsUtil.cpu_percent(), 1)
            RamVal = round(PsUtil.virtual_memory().percent, 1)
            if self.CpuLabel and getattr(self.CpuLabel, "IsWidgetActive", lambda: True)():
                self.CpuLabel.SetText("CPU: " + str(CpuVal) + "% // RAM: " + str(RamVal) + "%")

    def ComputeStardate(self):
        DTV = LCARS.System.DateTime
        if not DTV or not hasattr(DTV, "now"):
            return "74205.1"
        Now = DTV.now()
        N = (Now.year - 2323) * 1000 + (Now.timetuple().tm_yday * 2.73) + (Now.hour * 0.1)
        return str(round(N, 1))


DesktopScreen = LCARSDesktop
__all__ = ["LCARSDesktop", "DesktopScreen"]
