# ◤ LCARS TERMINAL
# Графічна оболонка бортового Terminal.
#
# BoardComputer
#     └── LCARSTerminal
#             └── LCARSConsole
#
# Terminal відповідає за UI.
# Console відповідає за виконання команд.

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.base.component import (
    LCARSButton,
    LCARSLabel,
    LCARSBar,
    LCARSElbow,
    LCARSIndicator,
    ActiveAudio,
)
from lcars.base.interface import Panel, PADD
from lcars.base.default import Palette, SystemTheme
from lcars.core.signal import Transmission, ODN
from lcars.service.console import LCARSConsole
from lcars.system.alert import AlertSystem, AlertLevel
from lcars.system.emergency import EmergencySystem
from lcars.system.power import SystemPower


class LCARSTerminal(PADD):

    # Створює графічний Terminal.
    def __init__(self, parent=None, lite=False, ParentNode=None, BoardComputer=None, **kwargs):
        ActualParent = ParentNode or parent or kwargs.pop("Parent", None)
        Width = kwargs.pop("width", 1180)
        Height = kwargs.pop("height", 760)
        MinWidth = kwargs.pop("minWidth", 760)
        MinHeight = kwargs.pop("minHeight", 460)
        BoardComputer = BoardComputer or kwargs.pop("BoardComputer", None)

        from lcars.core.computer import BoardComputer as ShipComputer
        self.BoardComputer = BoardComputer or ShipComputer.GetInstance()
        self.LiteMode = bool(lite)
        self.Console = LCARSConsole(BoardComputer=self.BoardComputer)
        self.ConsoleService = self.Console
        self.CommandSubmitted = Transmission()
        self.AlertState = "GREEN"
        self.PowerColor = Palette.Buttons[1]
        self.PowerColorName = "STANDARD"
        self.IsEmergency = False
        self.EmergencySubsystem = "CORE"
        self.EmergencyReason = ""
        self.EmergencyCriticality = "NONE"
        self.EmergencyAuthorizedBy = "SystemAuto"
        self.EmergencyHistory = []
        self.History = []
        self.HistoryIndex = 0
        self.InputStart = 0
        self.Output = None
        self.OriginalKeyPress = None
        self.ClockTimer = None
        self._ConsoleModelConnected = False
        self._ConsoleModeConnected = False
        self._AlertConnected = False
        self._PaletteConnected = False
        self._EmergencyTriggeredConnected = False
        self._EmergencyDisengagedConnected = False

        super().__init__(
            Parent=ActualParent,
            Title="SYSTEM TERMINAL",
            color=Palette.Background,
            width=Width,
            height=Height,
            minWidth=MinWidth,
            minHeight=MinHeight,
            **kwargs
        )

        self.BuildTerminal()
        self.ConnectODN()
        self.RefreshStatus()
        self.PrintWelcome()

    # Будує основну оболонку Terminal.
    def BuildTerminal(self):
        Content = self.Items.get("Content", self)

        self.RootPanel = Panel(
            Parent=Content.widget,
            Color=Palette.Background
        )

        self.RootPanel.Vertical(8, 8, 8, 8, 8)
        Content.Add(Content.Layout, self.RootPanel, 1)

        self.BuildHeader()
        self.BuildBody()
        self.BuildInput()
        self.BuildStatus()

    # Будує верхню LCARS область.
    def BuildHeader(self):
        self.Header = Panel(Parent=self.RootPanel.widget, Color=Palette.Background)
        self.Header.Horizontal(0, 0, 0, 0, 8)

        self.TopElbow = LCARSElbow(
            Direction="top-left",
            Text="TERMINAL",
            Parent=self.Header.widget
        )
        self.TopElbow.SetColor(
            SystemTheme.RandomButtonColor("buttons", Seed=11, Dynamic=True)
        )
        self.TopElbow.widget.setFixedSize(190, 62)
        self.Header.Add(self.Header.Layout, self.TopElbow)

        self.TitleLabel = LCARSLabel(
            Text="LCARS // BOARD COMPUTER // COMMAND TERMINAL",
            Type="title",
            Parent=self.Header.widget
        )
        self.Header.Add(self.Header.Layout, self.TitleLabel, 1)

        self.ModeLabel = LCARSLabel(
            Text="MODE: OPTICAL",
            Type="status",
            Parent=self.Header.widget
        )
        self.Header.Add(self.Header.Layout, self.ModeLabel)

        self.AlertLabel = LCARSLabel(
            Text="ALERT: GREEN",
            Type="status",
            Parent=self.Header.widget
        )
        self.AlertLabel.SetColor(Palette.Buttons[0])
        self.Header.Add(self.Header.Layout, self.AlertLabel)

        self.StatusIndicator = LCARSIndicator(
            Parent=self.Header.widget,
            IndicatorType=LCARSIndicator.PillHalf
        )
        self.StatusIndicator.SetColor(
            SystemTheme.RandomButtonColor("buttons", Seed=13, Dynamic=True)
        )
        self.Header.Add(self.Header.Layout, self.StatusIndicator)

        self.RootPanel.Add(self.RootPanel.Layout, self.Header)

        self.HeaderRail = LCARSBar(
            Type="rect",
            Height=6,
            Parent=self.RootPanel.widget
        )
        self.RootPanel.Add(self.RootPanel.Layout, self.HeaderRail)

    # Будує робочу область.
    def BuildBody(self):
        self.Body = Panel(Parent=self.RootPanel.widget, Color=Palette.Background)
        self.Body.Horizontal(0, 0, 0, 0, 10)

        self.BuildNavigation()
        self.BuildDisplay()

        self.RootPanel.Add(self.RootPanel.Layout, self.Body, 1)

    # Будує навігацію Terminal.
    def BuildNavigation(self):
        self.Navigation = Panel(Parent=self.Body.widget, Color=Palette.Background)
        self.Navigation.Vertical(0, 0, 0, 0, 6)
        self.Navigation.widget.setFixedWidth(210)

        Buttons = [
            ("COMMAND", "COMMAND"),
            ("SYSTEM", "SYSTEM"),
            ("ACCESS", "ACCESS"),
            ("DIAGNOSTIC", "DIAGNOSTIC"),
            ("SYSTEM MENU", "SYSTEM_MENU"),
            ("ODN", "ODN")
        ]

        self.NavigationButtons = {}

        for Index, (Text, Key) in enumerate(Buttons):
            Button = LCARSButton(
                Text=Text,
                Key=Key,
                Type="right",
                Parent=self.Navigation.widget,
                Handler=lambda t=Text: self.HandleCommand(t)
            )
            Button.widget.setFixedHeight(42)
            Button.SetColor(
                SystemTheme.RandomButtonColor(
                    "buttons",
                    Seed=20 + Index,
                    Dynamic=True
                )
            )
            self.Navigation.Add(self.Navigation.Layout, Button)
            self.NavigationButtons[Key] = Button

        self.Navigation.Layout.addStretch(1)

        self.NavigationRail = LCARSBar(
            Type="rect",
            Height=28,
            Parent=self.Navigation.widget
        )
        self.Navigation.Add(self.Navigation.Layout, self.NavigationRail)

        self.Body.Add(self.Body.Layout, self.Navigation)

    # Будує основний дисплей.
    def BuildDisplay(self):
        self.Display = Panel(
            Parent=self.Body.widget,
            Color=Palette.Background
        )

        self.Display.Vertical(0, 0, 0, 0, 6)

        DisplayHeader = Panel(
            Parent=self.Display.widget,
            Color=Palette.Background
        )

        DisplayHeader.Horizontal(0, 0, 0, 0, 6)

        DisplayLabel = LCARSLabel(
            Text="PRIMARY COMMAND STREAM",
            Type="status",
            Parent=DisplayHeader.widget
        )

        DisplayHeader.Add(
            DisplayHeader.Layout,
            DisplayLabel,
            1
        )

        DisplayRail = LCARSBar(
            Type="rect",
            Height=4,
            Parent=DisplayHeader.widget
        )

        DisplayHeader.Add(
            DisplayHeader.Layout,
            DisplayRail,
            1
        )

        self.Display.Add(
            self.Display.Layout,
            DisplayHeader
        )

        self.Output = LCARS.Terminal(
            self.Display.widget
        )

        self.Output.setReadOnly(False)

        self.ApplyScrollPolicy(self.Output)

        self.OriginalKeyPress = self.Output.keyPressEvent
        self.Output.keyPressEvent = self.OnTerminalKeyPress

        self.Display.Add(
            self.Display.Layout,
            self.Output,
            1
        )

        self.Body.Add(
            self.Body.Layout,
            self.Display,
            1
        )

    # Будує командний рядок.
    def BuildInput(self):
        self.InputPanel = Panel(
            Parent=self.RootPanel.widget,
            Color=Palette.Background
        )
        self.InputPanel.Horizontal(0, 0, 0, 0, 8)

        self.InputButton = LCARSButton(
            Text="LCARS:",
            Type="pill",
            Parent=self.InputPanel.widget
        )
        self.InputButton.widget.setFixedSize(90, 34)
        self.InputPanel.Add(self.InputPanel.Layout, self.InputButton)

        self.InputHint = LCARSLabel(
            Text="AWAITING COMMAND DIRECTIVE...",
            Type="status",
            Align="left",
            Parent=self.InputPanel.widget
        )
        self.InputPanel.Add(self.InputPanel.Layout, self.InputHint, 1)

        self.TransmitButton = LCARSButton(
            Text="TRANSMIT",
            Type="pill",
            Parent=self.InputPanel.widget,
            Handler=self.SubmitCurrentLine
        )
        self.TransmitButton.SetColor(
            SystemTheme.RandomButtonColor("buttons", Seed=31, Dynamic=True)
        )
        self.TransmitButton.widget.setFixedSize(120, 34)
        self.InputPanel.Add(self.InputPanel.Layout, self.TransmitButton)

        self.RootPanel.Add(self.RootPanel.Layout, self.InputPanel)

    # Будує нижню статусну область.
    def BuildStatus(self):
        self.StatusPanel = Panel(
            Parent=self.RootPanel.widget,
            Color=Palette.Background
        )
        self.StatusPanel.Horizontal(0, 0, 0, 0, 8)

        self.ODNLabel = LCARSLabel(
            Text="ODN: ONLINE",
            Type="status",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.ODNLabel)

        self.AlertButton = LCARSButton(
            Text="ALERT: GREEN",
            Type="pill",
            Parent=self.StatusPanel.widget,
            Handler=self.CycleAlert
        )
        self.AlertButton.widget.setFixedSize(110, 32)
        self.StatusPanel.Add(self.StatusPanel.Layout, self.AlertButton)

        self.MatrixLabel = LCARSLabel(
            Text="MATRIX: ONLINE",
            Type="status",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.MatrixLabel)

        self.CoreLabel = LCARSLabel(
            Text="MODEL: LOCAL",
            Type="status",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.CoreLabel)

        self.PowerLabel = LCARSLabel(
            Text="POWER: #6699CC",
            Type="status",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.PowerLabel)

        self.EmergencyLabel = LCARSLabel(
            Text="EMERGENCY: CLEAR",
            Type="status",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.EmergencyLabel)

        self.ClockLabel = LCARSLabel(
            Text="--:--:--",
            Type="value",
            Parent=self.StatusPanel.widget
        )
        self.StatusPanel.Add(self.StatusPanel.Layout, self.ClockLabel, 1)

        self.BottomElbow = LCARSElbow(
            Direction="bottom-right",
            Parent=self.StatusPanel.widget
        )
        self.BottomElbow.SetColor(
            SystemTheme.RandomButtonColor("buttons", Seed=19, Dynamic=True)
        )
        self.BottomElbow.widget.setFixedSize(150, 38)
        self.StatusPanel.Add(self.StatusPanel.Layout, self.BottomElbow)

        self.RootPanel.Add(self.RootPanel.Layout, self.StatusPanel)

    # Підключає тільки сигнали, потрібні для UI.
    def ConnectODN(self):
        if not self._ConsoleModelConnected:
            ODN.Connect("Console.ModelChanged", self.OnModelChanged)
            self._ConsoleModelConnected = True
        if not self._ConsoleModeConnected:
            ODN.Connect("Console.ModeChanged", self.OnModeChanged)
            self._ConsoleModeConnected = True
        if not self._AlertConnected:
            ODN.Connect("Alert.Changed", self.OnAlertChanged)
            self._AlertConnected = True
        if not self._PaletteConnected:
            ODN.Connect("UI.PaletteChanged", self.OnPaletteChanged)
            self._PaletteConnected = True
        if not self._EmergencyTriggeredConnected:
            ODN.Connect("Emergency.Triggered", self.OnEmergencyTriggered)
            self._EmergencyTriggeredConnected = True
        if not self._EmergencyDisengagedConnected:
            ODN.Connect("Emergency.Disengaged", self.OnEmergencyDisengaged)
            self._EmergencyDisengagedConnected = True

    def DisconnectODN(self):
        if self._ConsoleModelConnected:
            ODN.Disconnect("Console.ModelChanged", self.OnModelChanged)
            self._ConsoleModelConnected = False
        if self._ConsoleModeConnected:
            ODN.Disconnect("Console.ModeChanged", self.OnModeChanged)
            self._ConsoleModeConnected = False
        if self._AlertConnected:
            ODN.Disconnect("Alert.Changed", self.OnAlertChanged)
            self._AlertConnected = False
        if self._PaletteConnected:
            ODN.Disconnect("UI.PaletteChanged", self.OnPaletteChanged)
            self._PaletteConnected = False
        if self._EmergencyTriggeredConnected:
            ODN.Disconnect("Emergency.Triggered", self.OnEmergencyTriggered)
            self._EmergencyTriggeredConnected = False
        if self._EmergencyDisengagedConnected:
            ODN.Disconnect("Emergency.Disengaged", self.OnEmergencyDisengaged)
            self._EmergencyDisengagedConnected = False

    # Оновлює модель у статусі.
    def OnModelChanged(self, Packet=None, **kwargs):
        Data = kwargs.get("Backend") or kwargs.get("Model") or kwargs.get("backend") or kwargs.get("model")
        if Data is None and Packet is not None:
            PacketData = getattr(Packet, "Data", None)
            PacketFlags = getattr(Packet, "Flags", {})
            if isinstance(PacketData, dict):
                Data = PacketData.get("Backend") or PacketData.get("Model") or PacketData.get("backend") or PacketData.get("model")
            elif PacketData is not None:
                Data = PacketData
            else:
                Data = PacketFlags.get("Backend") or PacketFlags.get("Model") or PacketFlags.get("backend") or PacketFlags.get("model")

        if Data is not None:
            self.CoreLabel.SetText(f"MODEL: {str(Data).upper()}")

    # Оновлює режим у заголовку.
    def OnModeChanged(self, Packet=None, **kwargs):
        Mode = kwargs.get("Mode") or kwargs.get("mode")
        if Mode is None and Packet is not None:
            PacketData = getattr(Packet, "Data", None)
            PacketFlags = getattr(Packet, "Flags", {})
            if isinstance(PacketData, dict):
                Mode = PacketData.get("Mode") or PacketData.get("mode")
            elif PacketData is not None:
                Mode = PacketData
            else:
                Mode = PacketFlags.get("Mode") or PacketFlags.get("mode")
        if Mode:
            self.ModeLabel.SetText(f"MODE: {str(Mode).upper()}")

    # Оновлює alert-стан терміналу.
    def OnAlertChanged(self, Packet=None, **kwargs):
        Level = kwargs.get("Level") or kwargs.get("level")
        if Level is None and Packet is not None:
            PacketData = getattr(Packet, "Data", None)
            PacketFlags = getattr(Packet, "Flags", {})
            if isinstance(PacketData, dict):
                Level = PacketData.get("Level") or PacketData.get("level")
            elif PacketData is not None:
                Level = PacketData
            else:
                Level = PacketFlags.get("Level") or PacketFlags.get("level")
        if not Level:
            AlertSystem = self.GetAlertSystem()
            Level = getattr(AlertSystem, "Level", None)
        LevelName = self.NormalizeAlertLevel(Level)
        if not LevelName:
            return
        self.AlertState = LevelName
        self.AlertLabel.SetText(f"ALERT: {LevelName}")
        self.AlertButton.SetText(f"ALERT: {LevelName}")
        if LevelName == "RED":
            self.AlertLabel.SetColor(Palette.Red[0] if Palette.Red else "#CC0000")
            self.AlertButton.SetState("alert")
        elif LevelName == "YELLOW":
            self.AlertLabel.SetColor(Palette.Yellow[0] if Palette.Yellow else "#FF9900")
            self.AlertButton.SetState("yellow")
        else:
            self.AlertLabel.SetColor(Palette.Buttons[0])
            self.AlertButton.SetState("active")
        self.StatusIndicator.SetColor(self.GetAlertColor())
        self.ApplyAdaptiveLayout()
        self.RefreshStatus()

    def OnPaletteChanged(self, Packet=None, **kwargs):
        self.OnAlertChanged(Packet, **kwargs)

    def OnEmergencyTriggered(self, Packet=None, **kwargs):
        Data = kwargs
        if Packet is not None:
            PacketData = getattr(Packet, "Data", None)
            if isinstance(PacketData, dict):
                Data = PacketData
        self.IsEmergency = True
        self.EmergencySubsystem = str(Data.get("Subsystem", Data.get("SubsystemName", "CORE")) or "CORE")
        self.EmergencyReason = str(Data.get("Reason", Data.get("reason", "Subsystem Failure")) or "Subsystem Failure")
        self.EmergencyCriticality = str(Data.get("Criticality", Data.get("criticality", "CRITICAL")) or "CRITICAL")
        self.EmergencyAuthorizedBy = str(Data.get("AuthorizedBy", Data.get("authorizedBy", "SystemAuto")) or "SystemAuto")
        self.EmergencyHistory.append({
            "Timestamp": Data.get("Timestamp", ""),
            "Action": "Trigger",
            "Subsystem": self.EmergencySubsystem,
            "Reason": self.EmergencyReason,
            "Criticality": self.EmergencyCriticality,
            "AuthorizedBy": self.EmergencyAuthorizedBy,
        })
        self.EmergencyLabel.SetText(f"EMERGENCY: {self.EmergencySubsystem} // {self.EmergencyCriticality}")
        self.EmergencyLabel.SetColor("#CC0000")
        self.ModeLabel.SetText("MODE: EMERGENCY")
        self.AlertState = "RED"
        self.AlertLabel.SetText("ALERT: RED")
        self.AlertButton.SetText("ALERT: RED")
        self.AlertLabel.SetColor("#CC0000")
        self.AlertButton.SetState("alert")
        self.StatusIndicator.SetColor("#CC0000")
        self.WriteLine(f">> EMERGENCY FAILOVER ENGAGED: {self.EmergencySubsystem} // {self.EmergencyReason}")

    def OnEmergencyDisengaged(self, Packet=None, **kwargs):
        Data = kwargs
        if Packet is not None:
            PacketData = getattr(Packet, "Data", None)
            if isinstance(PacketData, dict):
                Data = PacketData
        self.IsEmergency = False
        self.EmergencySubsystem = str(Data.get("Subsystem", Data.get("SubsystemName", "")) or "")
        self.EmergencyReason = str(Data.get("Reason", Data.get("reason", "All Systems Nominal")) or "All Systems Nominal")
        self.EmergencyCriticality = str(Data.get("Criticality", Data.get("criticality", "NONE")) or "NONE")
        self.EmergencyAuthorizedBy = str(Data.get("AuthorizedBy", Data.get("authorizedBy", "Captain")) or "Captain")
        self.EmergencyHistory.append({
            "Timestamp": Data.get("Timestamp", ""),
            "Action": "Disengage",
            "Subsystem": self.EmergencySubsystem,
            "Reason": self.EmergencyReason,
            "Criticality": self.EmergencyCriticality,
            "AuthorizedBy": self.EmergencyAuthorizedBy,
        })
        self.EmergencyLabel.SetText("EMERGENCY: CLEAR")
        self.EmergencyLabel.SetColor(Palette.Buttons[0])
        self.ModeLabel.SetText("MODE: OPTICAL")
        self.AlertState = "GREEN"
        self.AlertLabel.SetText("ALERT: GREEN")
        self.AlertButton.SetText("ALERT: GREEN")
        self.AlertLabel.SetColor(Palette.Buttons[0])
        self.AlertButton.SetState("active")
        self.StatusIndicator.SetColor(self.GetAlertColor())
        self.WriteLine(f">> EMERGENCY DISENGAGED: {self.EmergencyReason}")

    def RefreshStatus(self):
        self.AlertLabel.SetText(f"ALERT: {self.AlertState}")
        self.AlertButton.SetText(f"ALERT: {self.AlertState}")
        self.PowerLabel.SetText(f"POWER: {self.PowerColor}")
        self.ClockLabel.SetText("--:--:--")

    # Виводить початковий стан Terminal.
    def PrintWelcome(self):
        self.Output.insertPlainText(
            "◤ LCARS BOARD COMPUTER TERMINAL\n"
            ">> TERMINAL INTERFACE INITIALIZED.\n"
            ">> ODN CARRIER: ONLINE\n"
            ">> SYSTEM MATRIX: ONLINE\n"
            ">> COMMAND CONSOLE: READY\n"
            "\n"
            "LCARS: "
        )
        self.InputStart = len(self.Output.toPlainText())
        self.MoveEnd()

    # Передає команду функціональній Console.
    def ExecuteCommand(self, CommandText):
        Text = str(CommandText).strip()

        if not Text:
            return

        self.Console.Execute(Text, self.OnCommandOutput)

    # Обробляє команди шляхом маршрутизації та виконання.
    def HandleCommand(self, CommandText):
        Text = str(CommandText).strip().upper()
        if not Text:
            return

        # Маршрутизація команд:
        if Text.startswith("WRITE "):
            self.WriteText(Text[6:])
        elif Text.startswith("SETALERT "):
            Level = Text[8:].strip().upper()
            self.SetAlert(Level)
        elif Text == "CYCLEALERT":
            self.CycleAlert()
        elif Text.startswith("GETALARMLEVEL"):
            self.GetAlarmLevel()
        elif Text.startswith("GETALARMCOLOR"):
            self.GetAlarmColor()
        elif Text.startswith("SETPOWERCOLOR "):
            Color = Text[13:].strip()
            self.SetPowerColor(Color)
        elif Text.startswith("GETEMERGENCYLEVEL"):
            self.GetEmergencyLevel()
        elif Text.startswith("GETEMERGENCYCOLOR"):
            self.GetEmergencyColor()
        elif Text.startswith("TRIGGERTRAJECTORY "):
            Target = Text[17:].strip()
            self.TriggerEmergency(Target)
        elif Text.startswith("PLAYAUDIO "):
            AudioPath = Text[9:].strip()
            self.PlayAudio(AudioPath)
        elif Text == "SLEEP":
            self.ExecuteSleep()
        elif Text == "HIBERNATE":
            self.ExecuteHibernate()
        else:
            # Спробувати через Console для відладки
            self.Console.Execute(Text, self.OnCommandOutput)

    def WriteText(self, Text):
        self.Output.insertPlainText(f"\n>> DISPLAY: {Text}\n")
        self.MoveEnd()

    def SetAlert(self, Level):
        Level = str(Level).strip().upper()
        if Level in ("GREEN", "YELLOW", "ORANGE", "RED"):
            self.AlertState = Level
            if Level == "RED":
                self.AlertLabel.SetText(f"ALERT: RED")
                self.AlertButton.SetState("alert")
                self.StatusIndicator.SetColor("#CC0000")
            elif Level == "YELLOW":
                self.AlertLabel.SetText(f"ALERT: YELLOW")
                self.AlertButton.SetState("yellow")
                self.StatusIndicator.SetColor("#FF9900")
            else:
                self.AlertLabel.SetText(f"ALERT: GREEN")
                self.AlertButton.SetState("active")
                self.StatusIndicator.SetColor(self.GetAlertColor())
            self.RefreshStatus()

    def CycleAlert(self):
        Cycle = {"GREEN": "YELLOW", "YELLOW": "RED", "RED": "GREEN"}
        NextLevel = Cycle.get(self.AlertState, "GREEN")
        self.SetAlert(NextLevel)

    def GetAlarmLevel(self):
        self.WriteLine(f">> ALARM_LEVEL: {self.AlertState}")

    def GetAlarmColor(self):
        self.WriteLine(f">> ALARM_COLOR: {self.GetAlertColor()}")

    def SetPowerColor(self, Color):
        self.PowerColor = Color
        self.PowerLabel.SetText(f"POWER: {Color}")
        self.RefreshStatus()

    def GetEmergencyLevel(self):
        Level = "EMERGENCY_ACTIVE" if self.IsEmergency else "EMERGENCY_CLEAR"
        self.WriteLine(f">> EMERGENCY_LEVEL: {Level}")

    def GetEmergencyColor(self):
        Color = "#CC0000" if self.IsEmergency else Palette.Buttons[0]
        self.WriteLine(f">> EMERGENCY_COLOR: {Color}")

    def ExecuteSleep(self):
        from lcars.system.power import SystemPower
        PowerSys = SystemPower.GetInstance()
        self.WriteLine(">> [POWER]: INITIATING SYSTEM SLEEP MODE (SUSPEND TO RAM)...")
        PowerSys.Sleep()

    def ExecuteHibernate(self):
        from lcars.system.power import SystemPower
        PowerSys = SystemPower.GetInstance()
        self.WriteLine(">> [POWER]: INITIATING SYSTEM HIBERNATION (SUSPEND TO DISK)...")
        PowerSys.Hibernate()

    def TriggerEmergency(self, Reason):
        self.IsEmergency = True
        self.EmergencyReason = str(Reason)
        self.EmergencyLabel.SetText(f"EMERGENCY: CORE // CRITICAL")
        self.EmergencyLabel.SetColor("#CC0000")
        self.ModeLabel.SetText("MODE: EMERGENCY")
        self.AlertState = "RED"
        self.AlertLabel.SetText("ALERT: RED")
        self.AlertButton.SetText("ALERT: RED")
        self.AlertLabel.SetColor("#CC0000")
        self.AlertButton.SetState("alert")
        self.StatusIndicator.SetColor("#CC0000")
        self.WriteLine(f">> EMERGENCY FAILOVER ENGAGED: {self.EmergencyReason}")

    def PlayAudio(self, AudioPath):
        from lcars.modules.sound import PlayAudioClip
        PlayAudioClip(AudioPath)

    def GetAlertColor(self):
        Colors = {"GREEN": Palette.Buttons[0], "YELLOW": Palette.Yellow[0] if Palette.Yellow else "#FF9900", "RED": "#CC0000"}
        return Colors.get(self.AlertState, Palette.Buttons[0])

    def NormalizeAlertLevel(self, Level):
        LevelStr = str(Level).upper().strip()
        if LevelStr in ("GREEN", "YELLOW", "ORANGE", "RED"):
            return LevelStr if LevelStr != "ORANGE" else "YELLOW"
        return "GREEN"

    def ApplyAdaptiveLayout(self):
        if self.IsEmergency:
            self.Display.widget.setFixedWidth(1180)
            self.Navigation.widget.setFixedWidth(210)
            self.StatusPanel.widget.setFixedHeight(100)
        else:
            self.Display.widget.setFixedWidth(1180)
            self.Navigation.widget.setFixedWidth(210)
            self.StatusPanel.widget.setFixedHeight(80)

    # Єдина точка виводу результату Console.
    def OnCommandOutput(self, Text):
        if self.Output is None:
            return

        self.Output.insertPlainText(str(Text) + "\n")
        self.MoveEnd()

    # Обробляє клавіатуру Terminal.
    def OnTerminalKeyPress(self, Event):
        Key = Event.key()

        if Key in (LCARS.KeyReturn, LCARS.KeyEnter):
            self.SubmitCurrentLine()
            return

        CursorPosition = self.Output.textCursor().position()

        if Key == LCARS.KeyBackspace and CursorPosition <= self.InputStart:
            return

        if Key == LCARS.KeyLeft and CursorPosition <= self.InputStart:
            return

        if Key == LCARS.KeyUp:
            self.ShowHistory(-1)
            return

        if Key == LCARS.KeyDown:
            self.ShowHistory(1)
            return

        if self.OriginalKeyPress:
            self.OriginalKeyPress(Event)

    # Передає поточний рядок Console.
    def SubmitCurrentLine(self):
        self.MoveEnd()

        FullText = self.Output.toPlainText()
        CommandText = FullText[self.InputStart:].strip()

        if not CommandText:
            return

        self.Output.insertPlainText("\n")

        self.History.append(CommandText)
        self.HistoryIndex = len(self.History)

        self.CommandSubmitted.Emit(CommandText)
        self.HandleCommand(CommandText)

        self.Output.insertPlainText("\nLCARS: ")
        self.InputStart = len(self.Output.toPlainText())
        self.MoveEnd()

    # Показує історію команд.
    def ShowHistory(self, Step):
        if not self.History:
            return

        self.HistoryIndex = max(
            0,
            min(len(self.History), self.HistoryIndex + Step)
        )

        if self.HistoryIndex == len(self.History):
            Text = ""
        else:
            Text = self.History[self.HistoryIndex]

        FullText = self.Output.toPlainText()
        self.Output.setPlainText(
            FullText[:self.InputStart] + Text
        )
        self.MoveEnd()

    # Переміщує курсор у кінець дисплея.
    def MoveEnd(self):
        if self.Output is None:
            return

        MoveOperation = getattr(
            getattr(LCARS.TextCursor, "MoveOperation", None),
            "End",
            None
        )

        if MoveOperation is not None:
            self.Output.moveCursor(MoveOperation)

    # Вимикає прокрутку, якщо це передбачено LCARS.
    def ApplyScrollPolicy(self, Widget):
        Policy = getattr(LCARS, "ScrollAlwaysOff", None)

        if Policy is None:
            return

        Widget.setVerticalScrollBarPolicy(Policy)
        Widget.setHorizontalScrollBarPolicy(Policy)

BoardTerminal = LCARSTerminal
