from __future__ import annotations

# Titanium Bridge Migration: from pathlib import Path

from lcars.base.component import LCARSBar, LCARSButton, LCARSLabel, SetStyle
from lcars.base.default import Palette
from lcars.base.interface import Padd, Segment
from lcars.base.type import LCARS


class LCARS25thCentury(Padd):
    def __init__(self, root_path: Path | None = None, selector=None, Parent=None):
        self.RootPath = root_path or Path(__file__).resolve().parents[2]
        self.Selector = selector
        self.Pages = {}
        super().__init__(
            Parent=Parent,
            Title="LCARS 25TH CENTURY NODE",
            Width=1280,
            Height=760,
            MinWidth=760,
            MinHeight=460,
            Portable=Parent is None,
        )
        self.BuildConsole()

    def BuildConsole(self):
        Content = self.Items.get("Content")
        Layout = getattr(Content, "Layout", None)
        if not Content:
            return
        if not Layout:
            Layout = Content.Vertical(0, 0, 0, 0, 10)

        Host = NativeWidget(Content)
        SetStyle(Host, "background-color: #000000; border: none;")

        Header = LCARS.Horizontal()
        Header.setSpacing(10)
        self.SystemPlate = LCARSButton(Text="ENTERPRISE SYSTEMS", Type="soft", Parent=Host, Width=280, Height=52)
        self.HeaderBar = LCARSBar(Type="bar", Parent=Host, Height=12, Color=Palette.Buttons[5])
        self.CoreState = LCARSLabel(Text="QUANTUM CORE ONLINE", Parent=Host, Color=Palette.Buttons[2], FontSize=18)
        Header.addWidget(NativeWidget(self.SystemPlate))
        Header.addWidget(NativeWidget(self.HeaderBar), 1)
        Header.addWidget(NativeWidget(self.CoreState))
        Layout.addLayout(Header)

        Body = LCARS.Horizontal()
        Body.setSpacing(18)
        Layout.addLayout(Body, 1)

        Nav = Segment(Parent=Host)
        NavLayout = Nav.Vertical(0, 0, 0, 0, 8)
        self.Navigation = []
        Buttons = [
            ("DASHBOARD", "dashboard"),
            ("SCIENCE", "science"),
            ("ANALYSIS", "analysis"),
            ("SYSTEMS", "systems"),
            ("RETURN", "return"),
        ]
        Index = 0
        for Text, Target in Buttons:
            Button = LCARSButton(Text=Text, Type="pill", Parent=NativeWidget(Nav), Width=210, Height=52, Seed=Text)
            Button.clicked.connect(lambda *args, Name=Target: self.SelectPage(Name))
            NavLayout.addWidget(NativeWidget(Button))
            self.Navigation.append(Button)
            Index += 1
        NavLayout.addStretch()
        Body.addWidget(NativeWidget(Nav))

        self.Display = Segment(Parent=Host)
        self.DisplayLayout = self.Display.Vertical(4, 4, 4, 4, 10)
        SetStyle(NativeWidget(self.Display), "background-color: #030308; border: none;")
        Body.addWidget(NativeWidget(self.Display), 1)

        self.Side = Segment(Parent=Host)
        SideLayout = self.Side.Vertical(0, 0, 0, 0, 10)
        self.MonitorTitle = LCARSLabel(Text="NODE STATUS", Parent=NativeWidget(self.Side), Color=Palette.Buttons[2], FontSize=18)
        self.StatusOne = LCARSButton(Text="BIOFILTER ACTIVE", Type="soft", Parent=NativeWidget(self.Side), Width=250, Height=44)
        self.StatusTwo = LCARSButton(Text="SUBSPACE LINK", Type="soft", Parent=NativeWidget(self.Side), Width=250, Height=44)
        self.StatusThree = LCARSButton(Text="SENSOR LOCK", Type="soft", Parent=NativeWidget(self.Side), Width=250, Height=44)
        SideLayout.addWidget(NativeWidget(self.MonitorTitle))
        SideLayout.addWidget(NativeWidget(self.StatusOne))
        SideLayout.addWidget(NativeWidget(self.StatusTwo))
        SideLayout.addWidget(NativeWidget(self.StatusThree))
        SideLayout.addStretch()
        Body.addWidget(NativeWidget(self.Side))

        Footer = LCARS.Horizontal()
        Footer.setSpacing(10)
        self.Ready = LCARSButton(Text="READY", Type="pill-left", Parent=Host, Width=120, Height=38)
        self.FooterBar = LCARSBar(Type="bar", Parent=Host, Height=8, Color=Palette.Buttons[6])
        Footer.addWidget(NativeWidget(self.Ready))
        Footer.addWidget(NativeWidget(self.FooterBar), 1)
        Layout.addLayout(Footer)

        self.SelectPage("dashboard")

    def ClearDisplay(self):
        Layout = getattr(self, "DisplayLayout", None)
        if not Layout:
            return
        TakeAt = getattr(Layout, "takeAt", None)
        if not TakeAt:
            return
        Item = TakeAt(0)
        while Item:
            Widget = Item.widget()
            if Widget:
                Widget.deleteLater()
            Item = TakeAt(0)

    def SelectPage(self, Name):
        if Name == "return":
            self.ReturnToMain()
            return
        self.ClearDisplay()
        Host = NativeWidget(self.Display)
        Title = LCARSLabel(Text=self.PageTitle(Name), Parent=Host, Color=Palette.Buttons[2], FontSize=26, Align="left")
        Line = LCARSBar(Type="bar", Parent=Host, Height=8, Color=Palette.Buttons[1])
        self.DisplayLayout.addWidget(NativeWidget(Title))
        self.DisplayLayout.addWidget(NativeWidget(Line))

        Rows = self.PageRows(Name)
        for RowText in Rows:
            Row = LCARSButton(Text=RowText, Type="soft", Parent=Host, Height=46, Seed=RowText)
            self.DisplayLayout.addWidget(NativeWidget(Row))
        self.DisplayLayout.addStretch()

    def PageTitle(self, Name):
        Titles = {
            "dashboard": "OPERATING SYSTEM CORE",
            "science": "SCIENCE STATION",
            "analysis": "TACTICAL ANALYSIS",
            "systems": "SYSTEMS CONTROL",
        }
        return Titles.get(Name, "LCARS NODE")

    def PageRows(self, Name):
        Rows = {
            "dashboard": ["ALL SYSTEMS OPERATIONAL", "PRIMARY CORE READY", "LCARS 47-ALPHA"],
            "science": ["ASTROMETRIC GRID", "BIO-SCAN BUFFER", "SENSOR ARRAY STANDING BY"],
            "analysis": ["ODN CHANNELS NOMINAL", "ISOLINEAR MATRIX ONLINE", "BLACKBOX STREAM ACTIVE"],
            "systems": ["BIOS LEVEL SECURE", "KERNEL LINKED", "SERVICES WAITING"],
        }
        return Rows.get(Name, [])

    def ReturnToMain(self):
        Hide = getattr(NativeWidget(self), "hide", None)
        if Hide:
            Hide()
        if self.Selector:
            self.Selector()

    def ReturnToMain(self):
        self.ReturnToMain()

    def show(self):
        Host = NativeWidget(self)
        Show = getattr(Host, "show", None)
        if Show:
            Show()


__all__ = ["LCARS25thCentury"]
