from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.component import LCARSButton, SetStyle
from lcars.base.default import FontSetup, Palette
from lcars.base.type import LCARS


ApplicationType: Any = LCARS.Application
HostType: Any = LCARS.Console
SegmentType: Any = LCARS.Segment
BufferType: Any = LCARS.Buffer
VLayoutType: Any = LCARS.Vertical
HLayoutType: Any = LCARS.Horizontal
GridType: Any = LCARS.Grid
FontType: Any = LCARS.Font


def Native(Element):
    Widget = getattr(Element, "widget", None)
    if Widget is not None and not callable(Widget):
        return Widget
    return Element


def Add(Layout, Element, Row=None, Column=None, RowSpan=1, ColumnSpan=1):
    Widget = Native(Element)
    if Row is None or Column is None:
        Layout.addWidget(Widget)
    else:
        Layout.addWidget(Widget, Row, Column, RowSpan, ColumnSpan)


def Size(Element, Width, Height):
    Widget = Native(Element)
    Method = getattr(Widget, "setFixedSize", None)
    if Method:
        Method(Width, Height)
    return Element


def Label(Text, Parent, Color=Palette.Buttons[4]):
    Item = SegmentType(Parent)
    Layout = HLayoutType(Item)
    Layout.setContentsMargins(0, 0, 0, 0)
    TextNode = LCARSButton(Text=Text, Type="rect", Color="#050505", Active=False, Parent=Item, FontSize=11)
    SetStyle(
        Native(TextNode),
        "#LCARSButton { background-color: #050505; color: " + Color + "; border: none; "
        "font-family: 'Arial'; font-size: 11pt; font-weight: 700; text-align: left; padding: 0px; }",
    )
    Add(Layout, TextNode)
    return Item


class ButtonShowcase:
    def __init__(self):
        self.App = ApplicationType(sys.argv)
        self.Host = HostType()
        Title = getattr(self.Host, "set" + "Win" + "dowTitle", None)
        if Title:
            Title("LCARS Button Objects")
        self.Root = SegmentType(self.Host)
        Setter = getattr(self.Host, "setCentralWidget", None)
        if Setter:
            Setter(self.Root)
        SetStyle(self.Root, "background-color: #000000;")

        self.RootLayout = VLayoutType(self.Root)
        self.RootLayout.setContentsMargins(28, 24, 28, 24)
        self.RootLayout.setSpacing(20)
        self.Build()

    def Build(self):
        Add(self.RootLayout, Label("LCARS BUTTON OBJECTS // SHAPE, STATE, COLOR, MOTION, SOUND", self.Root))
        self.BuildShapes()
        self.BuildStates()
        self.BuildAutoColor()
        self.BuildCommands()

    def Section(self, Title):
        Add(self.RootLayout, Label(Title, self.Root, Palette.Buttons[2]))
        Host = SegmentType(self.Root)
        Grid = GridType(Host)
        Grid.setContentsMargins(0, 0, 0, 0)
        Grid.setHorizontalSpacing(14)
        Grid.setVerticalSpacing(14)
        Add(self.RootLayout, Host)
        return Host, Grid

    def BuildShapes(self):
        Host, Grid = self.Section("SHAPES")
        Specs = [
            ("RECT", "rect", Palette.Buttons[0]),
            ("PILL", "pill", Palette.Buttons[1]),
            ("LEFT", "left", Palette.Buttons[2]),
            ("RIGHT", "right", Palette.Buttons[3]),
            ("TOP", "top", Palette.Buttons[4]),
            ("BOTTOM", "bottom", Palette.Buttons[5]),
            ("CUT", "cut", Palette.Buttons[6]),
            ("CUT LEFT", "cut-left", Palette.Buttons[0]),
            ("CUT RIGHT", "cut-right", Palette.Buttons[1]),
        ]
        for Index, Spec in enumerate(Specs):
            Text, Shape, Color = Spec
            Button = LCARSButton(Text=Text, Type=Shape, Color=Color, Parent=Host, FontSize=12, Sound="acknowledge")
            Add(Grid, Size(Button, 180, 52), Index // 3, Index % 3)

    def BuildStates(self):
        Host, Grid = self.Section("STATES")
        Specs = [
            ("NORMAL", "normal", Palette.Buttons[0], True),
            ("SELECTED", "selected", Palette.Buttons[1], True),
            ("WARNING", "warning", Palette.Buttons[2], True),
            ("ALERT", "alert", Palette.Buttons[3], True),
            ("DISABLED", "disabled", Palette.Neutral[0], False),
            ("CYCLE", "normal", None, True),
        ]
        for Index, Spec in enumerate(Specs):
            Text, State, Color, Active = Spec
            Button = LCARSButton(Text=Text, Type="pill", State=State, Color=Color, Active=Active, Cycle=Text == "CYCLE", Parent=Host, FontSize=12)
            Add(Grid, Size(Button, 220, 52), Index // 3, Index % 3)

    def BuildAutoColor(self):
        Host, Grid = self.Section("AUTOMATIC COLOR FACTORY")
        for Index in range(12):
            Button = LCARSButton(Text="AUTO " + str(Index + 1).zfill(2), Type="rect", Seed="auto-" + str(Index), Parent=Host, FontSize=11)
            Add(Grid, Size(Button, 150, 46), Index // 4, Index % 4)

    def BuildCommands(self):
        Host, Grid = self.Section("COMMAND BUTTONS WITH SOUND ROUTES")
        Specs = [
            ("AUTHORIZE", "pill", Palette.Buttons[2], "acknowledge"),
            ("EXECUTE", "right", Palette.Buttons[4], "acknowledge"),
            ("ABORT", "left", Palette.YellowAlert[1], "click"),
            ("RED ALERT", "pill", Palette.RedAlert[0], "alert_red"),
            ("YELLOW ALERT", "pill", Palette.YellowAlert[0], "alert_yellow"),
            ("TERMINATE", "cut", Palette.RedAlert[3], "alert_red"),
        ]
        for Index, Spec in enumerate(Specs):
            Text, Shape, Color, Sound = Spec
            Button = LCARSButton(Text=Text, Type=Shape, Color=Color, Sound=Sound, Parent=Host, FontSize=12)
            Add(Grid, Size(Button, 230, 54), Index // 3, Index % 3)

    def Run(self):
        self.Host.resize(1180, 820)
        self.Host.show()
        return self.App.exec()


if __name__ == "__main__":
    Showcase = ButtonShowcase()
    raise SystemExit(Showcase.Run())
