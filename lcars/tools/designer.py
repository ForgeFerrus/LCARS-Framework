from __future__ import annotations

from typing import Optional, Any
from lcars.base.type import LCARS
from lcars.base.interface import Panel


def Native(Item: Any) -> Any:
    Widget = getattr(Item, "widget", None)
    if Widget is not None:
        return Widget
    return Item


class DesignerPanel(Panel):
    def Vertical(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutType = getattr(LCARS, "Vertical", None) or getattr(getattr(LCARS, "Interface", None), "Layout", None)
        if LayoutType is None or not hasattr(LayoutType, "__call__"):
            LayoutType = getattr(LCARS, "Vertical", None)
        return self.SetDesignerLayout(LayoutType, Left, Top, Right, Bottom, Spacing)

    def Horizontal(self, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        LayoutType = getattr(LCARS, "Horizontal", None) or getattr(getattr(LCARS, "Interface", None), "Layout", None)
        if LayoutType is None or not hasattr(LayoutType, "__call__"):
            LayoutType = getattr(LCARS, "Horizontal", None)
        return self.SetDesignerLayout(LayoutType, Left, Top, Right, Bottom, Spacing)

    def SetDesignerLayout(self, LayoutType, Left, Top, Right, Bottom, Spacing):
        if not LayoutType:
            self.Layout = None
            return None
        Layout = LayoutType(self.widget)
        setMargins = getattr(Layout, "setContentsMargins", None)
        setSpacing = getattr(Layout, "setSpacing", None)
        if setMargins:
            setMargins(Left, Top, Right, Bottom)
        if setSpacing:
            setSpacing(Spacing)
        self.Layout = Layout
        return Layout

    def Add(self, Item: Any, Stretch: Optional[int] = None):
        if not hasattr(self, "Layout") or self.Layout is None:
            return
        addWidget = getattr(self.Layout, "addWidget", None)
        if not addWidget:
            return
        if Stretch is None:
            addWidget(Native(Item))
        else:
            addWidget(Native(Item), Stretch)

    def AddStretch(self):
        if not hasattr(self, "Layout") or self.Layout is None:
            return
        addStretch = getattr(self.Layout, "addStretch", None)
        if addStretch:
            addStretch()

    def ClearCanvas(self):
        return


class Canvas(DesignerPanel):
    def __init__(self, Parent=None, Color="#000000"):
        super().__init__(Parent=Parent, Color=Color)
        self.Components = []
        self.Canvas = self
        self.Vertical(0, 0, 0, 0, 0)
        if hasattr(self.widget, "setStyleSheet"):
            self.widget.setStyleSheet("background-color: #000000; border: none;")

    def ClearCanvas(self):
        for Component in list(self.Components):
            Widget = Native(Component)
            if hasattr(Widget, "hide"):
                Widget.hide()
            if hasattr(Widget, "deleteLater"):
                Widget.deleteLater()
        self.Components.clear()

    def Bind(self, Item: Any):
        if Item is None:
            return
        self.Components.append(Item)


class Designer(DesignerPanel):
    def __init__(self, Parent=None, Color="#000000"):
        super().__init__(Parent=Parent, Color=Color)
        self.Vertical(0, 0, 0, 0, 0)
        self.Canvas = Canvas(Parent=self.widget)
        self.Add(self.Canvas, 1)

    def ClearCanvas(self):
        if hasattr(self.Canvas, "ClearCanvas"):
            self.Canvas.ClearCanvas()


def ApplyHostMode(Host):
    Protocol = getattr(LCARS, "Protocol", None)
    AppliedState = False
    if Protocol is not None:
        FlagGroup = getattr(Protocol, "WindowType", None)
        StateGroup = getattr(Protocol, "WindowState", None)
        Frameless = getattr(FlagGroup, "FramelessWindowHint", None) if FlagGroup else None
        Full = getattr(StateGroup, "WindowFullScreen", None) if StateGroup else None
        SetFlag = getattr(Host, "setWindowFlag", None)
        SetState = getattr(Host, "setWindowState", None)
        if SetFlag and Frameless is not None:
            SetFlag(Frameless, True)
        if SetState and Full is not None:
            SetState(Full)
            AppliedState = True
    showFull = getattr(Host, "showFullScreen", None)
    if showFull and not AppliedState:
        showFull()
        return
    if AppliedState:
        if hasattr(Host, "show"):
            Host.show()
        return
    showMax = getattr(Host, "showMaximized", None)
    if showMax:
        showMax()
        return
    if hasattr(Host, "show"):
        Host.show()
