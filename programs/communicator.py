# ◤ LCARS SUBSPACE COMLINK PADD 🖖
# Графічний PADD-термінал підпросторового зв'язку з аудіосупроводом та алгоритмічним стилем.
# СТАНДАРТ: Titanium (Zero-Except, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.default import Palette, FontStyle
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow, SetStyle
from lcars.base.animation import WaveStream
from lcars.modules.sound import ActiveAudio
from lcars.service.communicator import CommunicatorAccess, SubspaceVoiceGateway
from lcars.core.computer import ComputerAccess, Computer

class SubspaceComLink(PADD):
    def __init__(self, ParentNode: any = None, **kwargs):
        TitleVal = kwargs.pop("Title", "LCARS SUBSPACE COMLINK // NCC-74205")
        WidthVal = kwargs.pop("width", 1280)
        HeightVal = kwargs.pop("height", 800)
        PortableVal = kwargs.pop("portable", kwargs.pop("Portable", ParentNode is None))

        self.Gateway = CommunicatorAccess.GetCommunicator()
        self.BoardComputer = Computer()
        self.ActiveChannel = "VOICE GATEWAY"

        super().__init__(
            Parent=ParentNode,
            Title=TitleVal,
            color=Palette.Buttons[0],
            width=WidthVal,
            height=HeightVal,
            portable=PortableVal,
            Decorated=False,
            **kwargs
        )

        self.BuildComLink()
        self.StartStatusTimer()
        ActiveAudio.play("access")

    def BuildComLink(self) -> None:
        SetStyle(self.widget, f"background-color: {Palette.Background}; border: none;")

        Content = self.Items.get("Content", self)

        # Кореневий контейнер
        self.RootPanel = Panel(Parent=Content.widget, Color=Palette.Background)
        self.RootPanel.Horizontal(12, 12, 12, 12, 14)
        Content.Add(Content.Layout, self.RootPanel, 1)

        # ==========================================
        # 1. ЛІВИЙ САЙДБАР (LCARS SWEEP CARRIER)
        # ==========================================
        self.Sidebar = Panel(Parent=self.RootPanel.widget, Color=Palette.Background)
        self.Sidebar.Vertical(0, 0, 0, 0, 6)
        self.Sidebar.widget.setFixedWidth(200)

        # Верхній лікоть
        TopElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[1], Text="COMMS", Parent=self.Sidebar.widget)
        TopElbow.widget.setFixedSize(200, 64)
        self.Sidebar.Add(self.Sidebar.Layout, TopElbow)

        # Канали зв'язку за алгоритмічною палітрою
        CommChannels = [
            ("VOICE GATEWAY", Palette.Buttons[0], lambda *_: self.SelectChannel("VOICE GATEWAY")),
            ("SUBSPACE RELAY", Palette.Buttons[2], lambda *_: self.SelectChannel("SUBSPACE RELAY")),
            ("HAIL STARFLEET", Palette.Buttons[1], lambda *_: self.SelectChannel("HAIL STARFLEET")),
            ("TRANSLATOR", Palette.Buttons[3], lambda *_: self.SelectChannel("TRANSLATOR")),
            ("FREQ SWEEP", Palette.Buttons[4] if len(Palette.Buttons) > 4 else Palette.Buttons[0], lambda *_: self.SelectChannel("FREQ SWEEP")),
            ("TOGGLE GATEWAY", Palette.Buttons[1], lambda *_: self.OnToggleGateway()),
            ("CLEAR LOG", Palette.Buttons[5] if len(Palette.Buttons) > 5 else Palette.Buttons[2], lambda *_: self.ClearLog()),
        ]

        self.ChannelButtons = []
        for LabelText, ColorVal, Callback in CommChannels:
            Btn = LCARSButton(Text=LabelText, Type="right", ColorHexStr=ColorVal, Sound="click", Parent=self.Sidebar.widget)
            Btn.widget.setFixedHeight(34)
            if Callback:
                Btn.Clicked.Connect(Callback)
            self.Sidebar.Add(self.Sidebar.Layout, Btn)
            self.ChannelButtons.append(Btn)

        self.Sidebar.Layout.addStretch(1)

        # Статус шлюзу
        self.StatusLabel = LCARSLabel(Text="GATEWAY: ACTIVE", Type="status", Color=Palette.Buttons[0], Parent=self.Sidebar.widget)
        self.Sidebar.Add(self.Sidebar.Layout, self.StatusLabel)

        # Нижній лікоть
        BotElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Text="READY", Parent=self.Sidebar.widget)
        BotElbow.widget.setFixedSize(200, 64)
        self.Sidebar.Add(self.Sidebar.Layout, BotElbow)

        self.RootPanel.Add(self.RootPanel.Layout, self.Sidebar)

        # ==========================================
        # 2. ГОЛОВНА РОБОЧА ЗОНА
        # ==========================================
        self.MainArea = Panel(Parent=self.RootPanel.widget, Color=Palette.Background)
        self.MainArea.Vertical(0, 0, 0, 0, 8)

        # 2.1. Верхній системний заголовок
        self.HeaderBar = Panel(Parent=self.MainArea.widget, Color=Palette.Background)
        self.HeaderBar.Horizontal(0, 0, 0, 0, 10)

        self.HeaderTitle = LCARSLabel(
            Text="SUBSPACE COMMUNICATOR // ANDROID COMBADGE GATEWAY",
            Type="title",
            Color=Palette.Buttons[1],
            FontSize=16,
            Parent=self.HeaderBar.widget
        )
        self.HeaderBar.Add(self.HeaderBar.Layout, self.HeaderTitle, 1)

        LocalIp = SubspaceVoiceGateway.GetLocalIp()
        self.Port = getattr(self.Gateway, "Port", 8047)
        self.IpBadge = LCARSLabel(
            Text=f"IP: {LocalIp}:{self.Port} [ONLINE]",
            Type="value",
            Color=Palette.Buttons[2],
            FontSize=14,
            Parent=self.HeaderBar.widget
        )
        self.HeaderBar.Add(self.HeaderBar.Layout, self.IpBadge)

        if getattr(self, "PaddPortable", False):
            CloseBtn = LCARSButton(Text="CLOSE", Type="pill", ColorHexStr=Palette.Red[0], Sound="click", Parent=self.HeaderBar.widget)
            CloseBtn.widget.setFixedSize(74, 26)
            CloseBtn.Clicked.Connect(lambda *_: self.widget.close())
            self.HeaderBar.Add(self.HeaderBar.Layout, CloseBtn)

        self.MainArea.Add(self.MainArea.Layout, self.HeaderBar)

        # Розділювач
        Divider = LCARSBar(Type="rect", Height=4, Color=Palette.Buttons[0], Parent=self.MainArea.widget)
        self.MainArea.Add(self.MainArea.Layout, Divider)

        # 2.2. Інформаційний блок підключення смартфона
        self.InfoCard = Panel(Parent=self.MainArea.widget, Color="#080810")
        self.InfoCard.Vertical(10, 10, 10, 10, 4)

        UrlText = f"http://{LocalIp}:{self.Port}"
        self.UrlLabel = LCARSLabel(
            Text=f"1. OPEN BROWSER ON YOUR PHONE:  {UrlText}",
            Color=Palette.Yellow[0] if len(Palette.Yellow) > 0 else Palette.Buttons[1],
            FontSize=14,
            Parent=self.InfoCard.widget
        )
        self.InfoCard.Add(self.InfoCard.Layout, self.UrlLabel)

        NoteLabel = LCARSLabel(
            Text="2. TAP THE GOLDEN COMBADGE SYMBOL AND SPEAK IN UKRAINIAN/ENGLISH TO DIRECT STARSHIP",
            Color=Palette.Buttons[2],
            FontSize=12,
            Parent=self.InfoCard.widget
        )
        self.InfoCard.Add(self.InfoCard.Layout, NoteLabel)
        self.MainArea.Add(self.MainArea.Layout, self.InfoCard)

        # 2.3. Жива анімація підпросторової частоти (WaveStream)
        WaveBox = Panel(Parent=self.MainArea.widget, Color=Palette.Background)
        WaveBox.Vertical(0, 0, 0, 0, 4)

        WaveHeader = Panel(Parent=WaveBox.widget, Color=Palette.Background)
        WaveHeader.Horizontal(0, 0, 0, 0, 6)
        WaveLabel = LCARSLabel(Text="SUBSPACE CARRIER FREQUENCY // 45.2 GHz HARMONIC", Type="status", Color=Palette.Buttons[2], FontSize=11, Parent=WaveHeader.widget)
        WaveHeader.Add(WaveHeader.Layout, WaveLabel, 1)
        WaveBar = LCARSBar(Type="rect", Height=3, Color=Palette.Buttons[2], Parent=WaveHeader.widget)
        WaveHeader.Add(WaveHeader.Layout, WaveBar, 2)
        WaveBox.Add(WaveBox.Layout, WaveHeader)

        self.WaveAnim = WaveStream(Parent=WaveBox.widget, Color=Palette.Buttons[2], WaveCount=3, Speed=0.045)
        self.WaveAnim.widget.setFixedHeight(85)
        self.WaveAnim.Start()
        WaveBox.Add(WaveBox.Layout, self.WaveAnim)

        self.MainArea.Add(self.MainArea.Layout, WaveBox)

        # 2.4. Журнал підпросторових передач
        LogHeader = LCARSLabel(Text="SUBSPACE TRANSMISSION LOG & VOICE DIRECTIVES:", Type="status", Color=Palette.Buttons[0], FontSize=12, Parent=self.MainArea.widget)
        self.MainArea.Add(self.MainArea.Layout, LogHeader)

        self.LogTerminal = LCARS.Terminal(self.MainArea.widget)
        self.LogTerminal.setReadOnly(True)
        self.LogTerminal.setStyleSheet(
            f"background-color: {Palette.Background}; color: #33FF66; border: none; outline: none; "
            f"font-size: 13px; font-family: Consolas, monospace; padding: 6px;"
        )
        if getattr(LCARS, "ScrollAlwaysOff", None) is not None:
            self.LogTerminal.setVerticalScrollBarPolicy(LCARS.ScrollAlwaysOff)
            self.LogTerminal.setHorizontalScrollBarPolicy(LCARS.ScrollAlwaysOff)

        self.LogTerminal.setPlainText(
            f"[*] SUBSPACE GATEWAY ONLINE // PORT {self.Port}\n"
            f"[*] LISTENING FOR ANDROID COMBADGE CLIENTS AT {UrlText}\n"
            f"[*] STARSHIP CORE: {self.BoardComputer.ShipRegistry} // {self.BoardComputer.Version}\n"
            f"[*] TRANSLATION MATRIX: UKRAINIAN / ENGLISH [ACTIVE]\n"
        )
        self.MainArea.Add(self.MainArea.Layout, self.LogTerminal, 1)

        # 2.5. Нижня панель тривог і керування
        ActionRow = Panel(Parent=self.MainArea.widget, Color=Palette.Background)
        ActionRow.Horizontal(0, 0, 0, 0, 8)

        self.ToggleGatewayBtn = LCARSButton(Text="GATEWAY: ACTIVE", Type="rect", ColorHexStr=Palette.Buttons[0], Sound="click", Parent=ActionRow.widget)
        self.ToggleGatewayBtn.widget.setFixedHeight(34)
        self.ToggleGatewayBtn.Clicked.Connect(self.OnToggleGateway)
        ActionRow.Add(ActionRow.Layout, self.ToggleGatewayBtn, 1)

        RedAlertBtn = LCARSButton(Text="RED ALERT", Type="rect", ColorHexStr=Palette.Red[0], Sound="click", Parent=ActionRow.widget)
        RedAlertBtn.widget.setFixedHeight(34)
        RedAlertBtn.Clicked.Connect(lambda *_: self.SetShipAlert("RED"))
        ActionRow.Add(ActionRow.Layout, RedAlertBtn, 1)

        YellowAlertBtn = LCARSButton(Text="YELLOW ALERT", Type="rect", ColorHexStr=Palette.Yellow[0] if len(Palette.Yellow) > 0 else Palette.Buttons[1], Sound="click", Parent=ActionRow.widget)
        YellowAlertBtn.widget.setFixedHeight(34)
        YellowAlertBtn.Clicked.Connect(lambda *_: self.SetShipAlert("YELLOW"))
        ActionRow.Add(ActionRow.Layout, YellowAlertBtn, 1)

        GreenAlertBtn = LCARSButton(Text="CONDITION NORMAL", Type="pill", ColorHexStr=Palette.Buttons[3], Sound="click", Parent=ActionRow.widget)
        GreenAlertBtn.widget.setFixedHeight(34)
        GreenAlertBtn.Clicked.Connect(lambda *_: self.SetShipAlert("NORMAL"))
        ActionRow.Add(ActionRow.Layout, GreenAlertBtn, 1)

        self.MainArea.Add(self.MainArea.Layout, ActionRow)
        self.RootPanel.Add(self.RootPanel.Layout, self.MainArea, 1)

        # Перетягування PADD
        if getattr(self, "PaddPortable", False):
            for DragElem in [TopElbow, self.HeaderBar, BotElbow]:
                DW = getattr(DragElem, "widget", DragElem)
                if DW is not None:
                    DW.mousePressEvent = self.PaddPress
                    DW.mouseMoveEvent = self.PaddMove
                    DW.mouseReleaseEvent = self.PaddRelease

    def SelectChannel(self, ChannelName: str) -> None:
        ActiveAudio.play("click")
        self.ActiveChannel = ChannelName
        self.LogMessage(f">> SWITCHED SUB-CHANNEL TO: {ChannelName}")
        if ChannelName == "HAIL STARFLEET":
            ActiveAudio.play("incoming")
            self.LogMessage(">> TRANSMITTING SUBSPACE HAIL TO STARFLEET COMMAND (SECTOR 001)...")
        elif ChannelName == "TRANSLATOR":
            ActiveAudio.play("ack")
            self.LogMessage(">> UNIVERSAL TRANSLATOR SYNCHRONIZED: 1,450 LANGUAGES LOADED.")
        elif ChannelName == "FREQ SWEEP":
            ActiveAudio.play("beep")
            self.LogMessage(">> SCANNING SUBSPACE FREQUENCIES (0.1 GHz - 100.0 GHz)... OK.")

    def StartStatusTimer(self) -> None:
        TimerClass = getattr(LCARS, "Timer", None)
        if TimerClass:
            self.StatusTimer = TimerClass(self.widget)
            self.StatusTimer.setInterval(2000)
            self.StatusTimer.timeout.connect(self.OnStatusTick)
            self.StatusTimer.start()

    def OnStatusTick(self) -> None:
        if not getattr(self.Gateway, "IsActive", False):
            CommunicatorAccess.StartGateway()

    def LogMessage(self, Text: str) -> None:
        if hasattr(self.LogTerminal, "appendPlainText"):
            self.LogTerminal.appendPlainText(Text)
        elif hasattr(self.LogTerminal, "append"):
            self.LogTerminal.append(Text)
        elif hasattr(self.LogTerminal, "toPlainText"):
            old = self.LogTerminal.toPlainText()
            self.LogTerminal.setPlainText(f"{old}\n{Text}")

    def ClearLog(self) -> None:
        ActiveAudio.play("click")
        self.LogTerminal.clear()

    def OnToggleGateway(self) -> None:
        ActiveAudio.play("click")
        if getattr(self.Gateway, "IsActive", False):
            CommunicatorAccess.StopGateway()
            self.ToggleGatewayBtn.SetText("GATEWAY: SUSPENDED")
            self.ToggleGatewayBtn.SetColor(Palette.Buttons[1])
            self.StatusLabel.SetText("GATEWAY: OFF")
            self.LogMessage(">> SUBSPACE GATEWAY SUSPENDED BY OPERATOR.")
        else:
            CommunicatorAccess.StartGateway()
            self.ToggleGatewayBtn.SetText("GATEWAY: ACTIVE")
            self.ToggleGatewayBtn.SetColor(Palette.Buttons[0])
            self.StatusLabel.SetText("GATEWAY: ACTIVE")
            self.LogMessage(">> SUBSPACE GATEWAY RESUMED.")

    def SetShipAlert(self, LevelStr: str) -> None:
        Comp = ComputerAccess.GetInstance()
        Comp.SetAlert(LevelStr)
        if LevelStr == "RED":
            ActiveAudio.play("alert_red")
        elif LevelStr == "YELLOW":
            ActiveAudio.play("alert_yellow")
        else:
            ActiveAudio.play("ack")
        self.LogMessage(f">> TACTICAL ALERT UPDATED TO: {LevelStr}")


# Сумісні псевдоніми
ComLinkPADD = SubspaceComLink
CommunicatorProgram = SubspaceComLink
CommunicatorWindow = SubspaceComLink
SubspaceCommunicatorApp = SubspaceComLink


def User() -> int:
    AppCls = LCARS.Application
    if AppCls is None:
        return 1
    AppInst = AppCls.instance() or AppCls([])
    FontSetup()

    Display = SubspaceComLink(portable=True, width=1280, height=800)
    Host = Display.widget

    if hasattr(Host, "show"):
        Host.show()

    return AppInst.exec()


def main() -> int:
    return User()


if __name__ == "__main__":
    import sys
    sys.exit(User())
