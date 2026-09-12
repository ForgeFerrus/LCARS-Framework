from __future__ import annotations

# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Any, Callable

from lcars.base.component import (
    Graphic,
    LCARSBar,
    LCARSButton,
    LCARSElbow,
    LCARSLabel,
    NativeWidget,
    Primitive,
)
from lcars.base.interface import (
    DataBlock,
    Footer,
    Header,
    Menu,
    Padd,
    Panel,
    ScanningBar,
    Screen,
    Segment,
    Sidebar,
    StatBar,
    StatusLine,
    Toolbar,
)


@dataclass
class ConstructorObject:
    Name: str
    Factory: Callable[..., Any]
    Category: str = "component"
    Defaults: dict[str, Any] = field(default_factory=dict)

    def Create(self, Parent=None, **Overrides):
        Args = self.Defaults.copy()
        Args.update(Overrides)
        if Parent is not None:
            Args["Parent"] = Parent
        return self.Factory(**Args)


class ConstructorCatalog:
    def __init__(self):
        self.Objects: dict[str, ConstructorObject] = {}
        self.LoadBaseObjects()

    def Register(self, Name: str, Factory: Callable[..., Any], Category: str = "component", **Defaults):
        Key = self.Normalize(Name)
        self.Objects[Key] = ConstructorObject(Key, Factory, Category, Defaults)
        return self.Objects[Key]

    def Normalize(self, Name: str):
        return str(Name or "").strip().lower().replace("_", "-")

    def Names(self, Category: str | None = None):
        if Category is None:
            return list(self.Objects.keys())
        return [Name for Name, Item in self.Objects.items() if Item.Category == Category]

    def Get(self, Name: str):
        Key = self.Normalize(Name)
        if Key not in self.Objects:
            raise KeyError(f"Constructor object is not registered: {Name}")
        return self.Objects[Key]

    def Create(self, Name: str, Parent=None, **Overrides):
        return self.Get(Name).Create(Parent=Parent, **Overrides)

    def LoadBaseObjects(self):
        self.RegisterButtons()
        self.RegisterComponents()
        self.RegisterInterface()

    def RegisterButtons(self):
        ButtonTypes = [
            ("button.rect", "RECT", "rect", 240, 56),
            ("button.soft", "SOFT", "soft", 240, 56),
            ("button.pill", "PILL", "pill", 240, 56),
            ("button.cap-left", "CAP LEFT", "cap-left", 240, 56),
            ("button.cap-right", "CAP RIGHT", "cap-right", 240, 56),
            ("button.tab-left", "TAB LEFT", "tab-left", 260, 56),
            ("button.tab-right", "TAB RIGHT", "tab-right", 260, 56),
            ("button.rect-ind-left", "RECT IND LEFT", "rect-ind-left", 300, 56),
            ("button.rect-ind-right", "RECT IND RIGHT", "rect-ind-right", 300, 56),
            ("button.soft-ind-left", "SOFT IND LEFT", "soft-ind-left", 300, 56),
            ("button.soft-ind-right", "SOFT IND RIGHT", "soft-ind-right", 300, 56),
            ("button.authorize", "AUTHORIZED", "authorize", 280, 56),
            ("button.access-code", "ACCESS CODE", "code", 360, 44),
            ("button.number", "07", "number", 260, 58),
            ("button.selected", "SELECTED", "selected", 240, 56),
            ("button.warning", "WARNING", "warning", 240, 56),
            ("button.alert", "ALERT", "alert", 240, 56),
            ("button.terminate", "TERMINATE", "terminate", 260, 56),
            ("button.disabled", "DISABLED", "disabled", 240, 56),
        ]
        for Name, Text, Type, Width, Height in ButtonTypes:
            self.Register(
                Name,
                LCARSButton,
                "button",
                Text=Text,
                Type=Type,
                Width=Width,
                Height=Height,
            )

    def RegisterComponents(self):
        self.Register("label.title", LCARSLabel, "text", Text="LCARS TEXT", Type="title", Width=260, Height=40)
        self.Register("label.status", LCARSLabel, "text", Text="STATUS READY", Type="status", Width=240, Height=34)
        self.Register("bar.basic", LCARSBar, "bar", Type="bar", Width=260, Height=18)
        self.Register("bar.divider", LCARSBar, "bar", Type="divider", Width=260, Height=10)
        self.Register("bar.scanning", LCARSBar, "bar", Type="scanning", Width=260, Height=18)
        self.Register("elbow.top-left", LCARSElbow, "frame", Direction="top-left", Width=320, Height=130)
        self.Register("elbow.top-right", LCARSElbow, "frame", Direction="top-right", Width=320, Height=130)
        self.Register("elbow.bottom-left", LCARSElbow, "frame", Direction="bottom-left", Width=320, Height=130)
        self.Register("elbow.bottom-right", LCARSElbow, "frame", Direction="bottom-right", Width=320, Height=130)
        self.Register("primitive.rect", Primitive, "primitive", Shape="rect", Text="RECT", Width=220, Height=70)
        self.Register("primitive.pill", Primitive, "primitive", Shape="pill", Text="PILL", Width=220, Height=70)
        self.Register("primitive.line", Primitive, "primitive", Shape="line-h", Width=260, Height=12)

    def RegisterInterface(self):
        self.Register("interface.padd", Padd, "interface", Title="LCARS PADD", Width=920, Height=580)
        self.Register("interface.screen", Screen, "interface", Mode="inner", Width=720, Height=460)
        self.Register("interface.panel", Panel, "interface", Width=420, Height=260)
        self.Register("interface.segment", Segment, "interface", Width=320, Height=180)
        self.Register("interface.header", Header, "interface", Title="HEADER", Width=720, Height=90)
        self.Register("interface.footer", Footer, "interface", Title="READY", Width=720, Height=70)
        self.Register("interface.sidebar", Sidebar, "interface", Items=["BRIDGE", "ACCESS", "DESIGNER"], Width=220, Height=420)
        self.Register("interface.menu", Menu, "interface", Items=["BRIDGE", "ACCESS", "DESIGNER"], Width=260, Height=180)
        self.Register("interface.toolbar", Toolbar, "interface", Items=["TOOLS", "BUTTONS"], Width=520, Height=70)
        self.Register("interface.statusline", StatusLine, "interface", Text="READY", Width=520, Height=44)
        self.Register("interface.datablock", DataBlock, "interface", LabelText="CORE", ValueText="ONLINE", Width=260, Height=90)
        self.Register("interface.statbar", StatBar, "interface", LabelText="EPS", Value=77, Width=260, Height=70)
        self.Register("interface.scanningbar", ScanningBar, "interface", Width=260, Height=34)


class ConstructorSession:
    def __init__(self, Carrier=None, Catalog: ConstructorCatalog | None = None):
        self.Catalog = Catalog or ConstructorCatalog()
        self.Carrier = Carrier or BuildConstructor()
        self.Objects: list[Any] = []
        self.CursorX = 32
        self.CursorY = 32
        self.RowHeight = 74

    @property
    def Content(self):
        Items = getattr(self.Carrier, "Items", {})
        return Items.get("Content", self.Carrier)

    @property
    def ParentWidget(self):
        return NativeWidget(self.Content)

    def Spawn(self, Name: str, X: int | None = None, Y: int | None = None, **Overrides):
        Obj = self.Catalog.Create(Name, Parent=self.ParentWidget, **Overrides)
        Widget = NativeWidget(Obj)
        PosX = self.CursorX if X is None else int(X)
        PosY = self.CursorY if Y is None else int(Y)
        if hasattr(Widget, "move"):
            Widget.move(PosX, PosY)
        if hasattr(Widget, "show"):
            Widget.show()
        self.Objects.append(Obj)
        self.AdvanceCursor(Obj)
        return Obj

    def AdvanceCursor(self, Obj):
        Widget = NativeWidget(Obj)
        Width = Widget.width() if hasattr(Widget, "width") else 240
        Height = Widget.height() if hasattr(Widget, "height") else 56
        self.CursorX += int(Width) + 18
        self.RowHeight = max(self.RowHeight, int(Height) + 18)
        Parent = self.ParentWidget
        Limit = Parent.width() - 320 if Parent and hasattr(Parent, "width") else 900
        if self.CursorX > Limit:
            self.CursorX = 32
            self.CursorY += self.RowHeight
            self.RowHeight = 74

    def Clear(self):
        for Obj in self.Objects:
            Widget = NativeWidget(Obj)
            Delete = getattr(Widget, "deleteLater", None)
            if Delete:
                Delete()
        self.Objects.clear()
        self.CursorX = 32
        self.CursorY = 32
        self.RowHeight = 74


def BuildConstructor(Title: str = "LCARS CONSTRUCTOR", Width: int = 1220, Height: int = 720):
    return Padd(Title=Title, Width=Width, Height=Height, Portable=True)


def BootConstructor():
    return BuildConstructor()


def BuildPreview():
    Constructor = BuildConstructor("LCARS CONSTRUCTOR // BASE CATALOG")
    Session = ConstructorSession(Constructor)
    for Name in Session.Catalog.Names("button"):
        Session.Spawn(Name)
    return Constructor
