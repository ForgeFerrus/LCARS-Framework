# LCARS FRAMEWORK Головний десктопний екран LCARS.
# Побудовано виключно на векторній топології LCARS без застарілих .widget

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor, FontStyle
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import Screen, Segment, Panel, PADD, Header, DataBlock, StatBar, StatusLine
from lcars.base.animation import Warp, DataStream, DiagnosticGrid
from lcars.core.signal import Transmission
from lcars.ui.panels.access import SystemAccess

class LCARSDesktop(Screen):
    def __init__(self, Parent=None):
        super().__init__(Parent=Parent)
        self.LockRequested = Transmission()
        
        self.Pages = {}
        self.NavButtons = {}
        self.Mode = "MENU"

        self.ClockTimer = None
        self.TopStatus = None
        self.Chamber = None

        self.Root = self

        self.Build()
        self.StartClock()
        self.Select(self.Mode)

    # -------------------------------------------------------------------------
    # ВЕКТОРНА СКУПКА ТА КОМПОЗИЦІЯ
    # -------------------------------------------------------------------------

    def Build(self):
        self.SetHorizontal(18, 18, 18, 18, Spacing=10)

        self.LeftColumn = Panel()
        self.LeftColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.LeftColumn.GetSurface().setFixedWidth(220)
        self.Add(self.LeftColumn)

        self.RightColumn = Panel()
        self.RightColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.Add(self.RightColumn, 1)

        self.BuildLeftNavigation()
        self.BuildRightShell()
        self.BuildPages()
        self.Select("BRIDGE")

    def BuildLeftNavigation(self):
        TopElbow = LCARSElbow(
            Corner="top-left",
            Height=85
        )
        self.LeftColumn.Add(TopElbow)

        Items = [
            ("WORKSPACE", self.ShowWorkspace),
            ("BRIDGE", self.ShowBridge),
            ("SYSTEM", self.ShowSystem),
            ("SUPPORT", self.ShowSupport),
            ("MENU", self.ShowMenu),
            ("CONSOLE", self.ShowConsole),
            ("ENGINE", self.ShowEngineering),
            ("SCIENCE", self.ShowScience),
            ("AGENT", self.ShowAgent),
            ("DESIGNER", self.ShowDesigner),
            ("COMMANDER", self.ShowCommander),
            ("IDE", self.ShowIDE),
            ("LOCK", self.RequestLock),
        ]

        for Index, (Name, Callback) in enumerate(Items):
            Btn = LCARSButton(
                Text=Name,
                Form=LCARSButton.SoftLeftType,
                Height=36,
                Handler=Callback
            )
            self.NavButtons[Name] = Btn
            self.LeftColumn.Add(Btn)

        BottomElbow = LCARSElbow(
            Corner="bottom-left",
            Height=61
        )
        self.LeftColumn.Add(BottomElbow)

    def BuildRightShell(self):
        self.BuildHeader()
        self.BuildChamber()
        self.BuildFooter()

    def BuildHeader(self):
        TopRow = Panel()
        TopRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.TopStatus = LCARSIndicator(
            Text="ОСНОВНА ОПЕРАЦІЙНА СИСТЕМА LCARS // АКТИВНА",
            Form=LCARSIndicator.RectLeftType,
            FontSize=16,
            Height=52
        )
        TopRow.Add(self.TopStatus, 1)

        Accent = LCARSBar(
            Form=LCARSBar.RectType,
            Width=72,
            Height=52
        )
        TopRow.Add(Accent)
        self.RightColumn.Add(TopRow)

        SecondRow = Panel()
        SecondRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.ModeStatus = LCARSIndicator(
            Text="РЕЖИМ // МІСТОК",
            Form=LCARSIndicator.RectLeftType,
            FontSize=16,
            Height=32
        )
        SecondRow.Add(self.ModeStatus, 1)

        Scan = LCARSBar(
            Form=LCARSBar.PillHalfType,
            Width=180,
            Height=32
        )
        SecondRow.Add(Scan)
        self.RightColumn.Add(SecondRow)

    def BuildChamber(self):
        self.Chamber = Panel()
        self.Chamber.SetVertical(0, 0, 0, 0, Spacing=4)
        self.RightColumn.Add(self.Chamber, 1)

    def BuildFooter(self):
        FooterOne = Panel()
        FooterOne.SetHorizontal(0, 0, 0, 0, Spacing=7)

        Stats = [
            ("ЯДРО TEMP", "47.2 °C"),
            ("ПОТУЖНІСТЬ", "12.4 GW"),
            ("СУБПРОСТІР", "НОМІНАЛ"),
            ("ЩИТИ", "ГОТОВНІСТЬ"),
            ("СЕНСОРИ", "АКТИВНІ"),
        ]

        for LabelText, ValueText in Stats:
            Block = Panel()
            Block.SetVertical(0, 0, 0, 0, Spacing=2)
            Block.Add(LCARSLabel(Text=LabelText, FontSize=16, Height=20))
            Block.Add(LCARSLabel(Text=ValueText, FontSize=16, Height=24))
            FooterOne.Add(Block, 1)

        self.RightColumn.Add(FooterOne)

        FooterTwo = Panel()
        FooterTwo.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.FooterStatus = LCARSIndicator(
            Text="ГОЛОВНИЙ ДЕСКТОП ОНЛАЙН",
            Form=LCARSIndicator.RectLeftType,
            FontSize=16,
            Height=36
        )
        FooterTwo.Add(self.FooterStatus, 1)

        BottomRightElbow = LCARSElbow(
            Corner="bottom-right",
            Width=160,
            Height=36
        )
        FooterTwo.Add(BottomRightElbow)
        self.RightColumn.Add(FooterTwo)

    def BuildPages(self):
        self.Pages["BRIDGE"] = LCARSLabel(Text="ГОЛОВНИЙ ТАКТИЧНИЙ МОНІТОР МІСТКА", FontSize=24, Align="center", Height=100)
        self.Pages["MENU"] = LCARSLabel(Text="СИСТЕМНЕ МЕНЮ УПРАВЛІННЯ", FontSize=24, Align="center", Height=100)
        self.Pages["WORKSPACE"] = LCARSLabel(Text="РОБОЧИЙ ПРОСТІР ОПЕРАТОРА", FontSize=24, Align="center", Height=100)
        self.Pages["SYSTEM"] = LCARSLabel(Text="ДИАГНОСТИКА СИСТЕМ ЗОРЕЛЬОТА", FontSize=24, Align="center", Height=100)

        for PageNode in self.Pages.values():
            self.Chamber.Add(PageNode)
            PageNode.hide()

    def Select(self, Name):
        self.Mode = Name
        if self.ModeStatus:
            self.ModeStatus.SetText(f"РЕЖИМ // {Name}")
        for PageName, PageNode in self.Pages.items():
            if PageName == Name:
                PageNode.show()
            else:
                PageNode.hide()

    def StartClock(self):
        pass

    def ShowWorkspace(self): self.Select("WORKSPACE")
    def ShowBridge(self): self.Select("BRIDGE")
    def ShowSystem(self): self.Select("SYSTEM")
    def ShowSupport(self): self.Select("MENU")
    def ShowMenu(self): self.Select("MENU")
    def ShowConsole(self): self.Select("BRIDGE")
    def ShowEngineering(self): self.Select("SYSTEM")
    def ShowScience(self): self.Select("WORKSPACE")
    def ShowAgent(self): self.Select("BRIDGE")
    def ShowDesigner(self): self.Select("WORKSPACE")
    def ShowCommander(self): self.Select("BRIDGE")
    def ShowIDE(self): self.Select("WORKSPACE")
    def RequestLock(self): pass
