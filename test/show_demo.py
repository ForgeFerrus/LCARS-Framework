from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.animation import (
    Blink,
    DataStream,
    DiagnosticGrid,
    Pulse,
    Reveal,
    ScanningBar as AnimatedScanningBar,
    StarfieldCluster,
    TextDecode,
    Transition,
    Typewriter,
    Warp,
)
from lcars.base.component import (
    LCARSBar,
    LCARSButton,
    LCARSElbow,
    LCARSIndicator,
    LCARSType,
    Primitive,
    SetStyle,
)
from lcars.base.default import Palette
from lcars.base.interface import DataBlock, Header, Menu, StatBar, StatusLine, Toolbar
from lcars.base.type import LCARS


ApplicationType = LCARSType(["Application"])
ViewportType = LCARSType(["Console"])
SegmentType = LCARSType(["Segment"])
HMatrixType = LCARSType(["HMatrix"])
VMatrixType = LCARSType(["VMatrix"])
GridType = LCARSType(["GridMatrix"])
BufferType = LCARSType(["Buffer"])
LabelType = LCARSType(["Indicator"])
FontType = LCARSType(["Font"])

class Section:
    def __init__(self, Parent, ParentLayout, Title, Color="#f0b942"):
        self.widget = SegmentType(Parent)
        self.layout = VMatrixType(self.widget)
        self.layout.setContentsMargins(14, 10, 14, 14)
        self.layout.setSpacing(8)
        SetStyle(
            self.widget,
            "background-color: #030303; border-top: 1px solid #263b12; border-left: none; border-right: none; border-bottom: none;",
        )
        Add(ParentLayout, self.widget)
        Add(self.layout, Label(f"// {Title}", self.widget, Color, 10))

    def Row(self, Spacing=8):
        Host = SegmentType(self.widget)
        Layout = HMatrixType(Host)
        Layout.setContentsMargins(0, 0, 0, 0)
        Layout.setSpacing(Spacing)
        Add(self.layout, Host)
        return Host, Layout

    def Add(self, Item, Stretch=None):
        Add(self.layout, Item, Stretch)


class Showcase:
    def __init__(self):
        self.app = ApplicationType(sys.argv)
        if FontType:
            self.app.setFont(FontType("Segoe UI", 10))
        self.Viewport = ViewportType()
        self.SetViewportTitle("LCARS Base Visual Showcase")
        SetStyle(self.Viewport, "background-color: #000000;")

        self.root = SegmentType(self.Viewport)
        SetStyle(self.root, "background-color: #000000;")
        SetCentral = getattr(self.Viewport, "setCentralWidget", None)
        if SetCentral:
            SetCentral(self.root)

        self.layout = VMatrixType(self.root)
        self.layout.setContentsMargins(20, 16, 20, 16)
        self.layout.setSpacing(10)

        self.BuildFrame()

    def SetViewportTitle(self, Text):
        Setter = getattr(self.Viewport, "set" + "WindowTitle", None)
        if Setter:
            Setter(Text)

    def SetFullDisplay(self):
        Frameless = LCARS.Frameless
        SetFlag = getattr(self.Viewport, "set" + "WindowFlag", None)
        if SetFlag and Frameless:
            SetFlag(Frameless, True)
        Show = getattr(self.Viewport, "showFullScreen", None)
        if Show:
            Show()

    def BuildFrame(self):
        top = SegmentType(self.root)
        topLayout = HMatrixType(top)
        topLayout.setContentsMargins(0, 0, 0, 0)
        topLayout.setSpacing(8)
        Add(self.layout, top)

        Add(topLayout, Size(Render(LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=top)), 220, 78))
        Add(topLayout, Label("LCARS BASE // VISUAL COMPONENT SHOWCASE", top, Palette.Buttons[2], 18), 1)
        Add(topLayout, Label("ALL CREATED BASE OBJECTS ON ONE SCREEN", top, Palette.Buttons[1], 10))
        Add(topLayout, Size(Render(LCARSElbow(Direction="top-right", Color=Palette.Buttons[2], Parent=top)), 220, 78))

        self.scroll = BufferType(self.root)
        self.content = SegmentType(self.scroll)
        self.contentLayout = VMatrixType(self.content)
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(10)
        SetStyle(self.content, "background-color: #000000;")
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.content)
        SetStyle(self.scroll, "background-color: #000000; border: 1px solid #1d334c;")
        Add(self.layout, self.scroll, 1)

        self.BuildButtons()
        self.BuildIndicators()
        self.BuildBarsAndElbows()
        self.BuildPrimitives()
        self.BuildInterfaceBlocks()
        self.BuildAnimations()

        bottom = SegmentType(self.root)
        bottomLayout = HMatrixType(bottom)
        bottomLayout.setContentsMargins(0, 0, 0, 0)
        bottomLayout.setSpacing(8)
        Add(self.layout, bottom)
        Add(bottomLayout, Size(Render(LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[3], Parent=bottom)), 220, 78))
        Add(bottomLayout, Size(Render(LCARSBar(Type="scanning", Height=20, Color=Palette.Buttons[3], Parent=bottom, Animated=True)), 900, 24), 1)
        Add(bottomLayout, Label("READY // REVIEW BASE MATERIAL", bottom, Palette.Buttons[4], 10))
        Add(bottomLayout, Size(Render(LCARSElbow(Direction="bottom-right", Color=Palette.Buttons[4], Parent=bottom)), 220, 78))

    def BuildButtons(self):
        section = Section(self.content, self.contentLayout, "BUTTONS // base class with shape/state variants")
        row, layout = section.Row()
        specs = [
            ("RECT", "rect", Palette.Buttons[0]),
            ("LEFT", "left", Palette.Buttons[1]),
            ("RIGHT", "right", Palette.Buttons[2]),
            ("PILL", "pill", Palette.Buttons[4]),
            ("SPLIT", "split", Palette.Buttons[3]),
            ("CUT", "cut", Palette.Accent[1]),
        ]
        for text, kind, color in specs:
            Add(layout, Size(ApplyReadable(LCARSButton(Text=text, Type=kind, Color=color, Parent=row)), 150, 46))

    def BuildIndicators(self):
        section = Section(self.content, self.contentLayout, "INDICATORS // label, status, alert, value")
        row, layout = section.Row()
        specs = [
            ("LABEL", "label", "normal"),
            ("READY", "status", "ready"),
            ("WARNING", "status", "warning"),
            ("ALERT", "alert", "alert"),
            ("047", "value", "normal"),
            ("TITLE NODE", "title", "normal"),
        ]
        for text, kind, status in specs:
            Add(layout, Size(ApplyReadable(LCARSIndicator(Text=text, Type=kind, Status=status, Parent=row)), 160, 38))

    def BuildBarsAndElbows(self):
        section = Section(self.content, self.contentLayout, "ELBOWS AND BARS // frame construction pieces")
        row, layout = section.Row()
        for direction, color in [
            ("top-left", Palette.Buttons[0]),
            ("top-right", Palette.Buttons[1]),
            ("bottom-left", Palette.Buttons[2]),
            ("bottom-right", Palette.Buttons[4]),
        ]:
            Add(layout, Size(Render(LCARSElbow(Direction=direction, Text=direction.upper(), Color=color, Parent=row)), 180, 110))

        row, layout = section.Row()
        for kind, text, color in [
            ("bar", "", Palette.Buttons[0]),
            ("divider", "", Palette.Buttons[1]),
            ("text", "SECTION", Palette.Buttons[4]),
            ("scanning", "", Palette.Buttons[3]),
        ]:
            Add(layout, Size(Render(LCARSBar(Type=kind, Text=text, Height=26, Color=color, Parent=row, Animated=True)), 260, 34))

    def BuildPrimitives(self):
        section = Section(self.content, self.contentLayout, "PRIMITIVES // graphic layer shapes")
        grid = SegmentType(section.widget)
        layout = GridType(grid)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        Add(section.layout, grid)

        specs = [
            ("surface", "SURFACE"),
            ("rect", "RECT"),
            ("square", "SQUARE"),
            ("pill", "PILL"),
            ("circle", "CIRCLE"),
            ("ellipse", "ELLIPSE"),
            ("triangle", "TRIANGLE"),
            ("trapezoid", "TRAPEZOID"),
            ("diamond", "DIAMOND"),
            ("hexagon", "HEXAGON"),
            ("star", "STAR"),
            ("line", "LINE"),
            ("text", "TEXT"),
            ("symbol", "47"),
            ("structure", "STRUCTURE"),
            ("access-panel", "ACCESS"),
        ]
        for index, (shape, text) in enumerate(specs):
            item = Primitive(Shape=shape, Text=text, Color=Palette.Buttons[index % len(Palette.Buttons)], Parent=grid)
            Size(Render(item), 170, 80)
            layout.addWidget(item.widget, index // 4, index % 4)

    def BuildInterfaceBlocks(self):
        section = Section(self.content, self.contentLayout, "INTERFACE BLOCKS // ready assembled objects")
        row, layout = section.Row()
        Add(layout, Size(Header("HEADER BLOCK", Parent=row), 360, 76))
        Add(layout, Size(StatusLine("SYSTEM READY", Parent=row), 280, 48))
        Add(layout, Size(DataBlock(LabelText="MODE", ValueText="BRIDGE", Parent=row), 240, 90))

        row, layout = section.Row()
        Add(layout, Size(Menu(Items=["BRIDGE", "CONSOLE", "ACCESS"], Parent=row), 210, 160))
        Add(layout, Size(Toolbar(Items=["BACK", "HOME", "NEXT"], Parent=row), 360, 62))
        Add(layout, Size(StatBar(LabelText="POWER", Value=74, Parent=row), 340, 70))

    def BuildAnimations(self):
        section = Section(self.content, self.contentLayout, "ANIMATIONS // moving and staged visual objects")
        grid = SegmentType(section.widget)
        layout = GridType(grid)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        Add(section.layout, grid)

        specs = [
            AnimatedScanningBar(Type="horizontal", Running=True, Parent=grid, Width=220, Height=32),
            AnimatedScanningBar(Type="blocks", Running=True, Parent=grid, Width=220, Height=90),
            Reveal(Type="blocks", Running=True, Parent=grid, Width=220, Height=90),
            Transition(Type="bars", Running=True, Parent=grid, Width=220, Height=90),
            TextDecode(Text="ACCESS GRANTED", Running=True, Parent=grid, Width=240, Height=44),
            Typewriter(Text="LCARS ONLINE", Running=True, Parent=grid, Width=240, Height=44),
            Blink(Text="ALERT", Running=True, Parent=grid, Width=160, Height=44),
            DataStream(Running=True, Parent=grid, Width=260, Height=120),
            Pulse(Running=True, Parent=grid, Width=120, Height=120),
            DiagnosticGrid(Running=True, Parent=grid, Width=220, Height=120),
            StarfieldCluster(Running=True, Parent=grid, Width=260, Height=120),
            Warp(Running=True, Engaged=True, Parent=grid, Width=260, Height=120),
        ]
        for index, item in enumerate(specs):
            Render(item)
            layout.addWidget(item.widget, index // 4, index % 4)

    def Show(self):
        self.SetFullDisplay()
        return self.app.exec()


def run():
    return Showcase().Show()


if __name__ == "__main__":
    sys.exit(run() or 0)
