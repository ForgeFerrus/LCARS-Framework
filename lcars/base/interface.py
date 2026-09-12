# LCARS FRAMEWORK
# Готові елементи та канонічні композиції LCARS (Michael Okuda Standard).
# У component.py лежать фізичні примітиви. Тут лежить віртуальний контейнер/оркестратор Element
# та канонічні складені об'єкти інтерфейсу зорельота за векторними кресленнями CorelDRAW.

from __future__ import annotations
import json
import sqlite3
import yaml
from pathlib import Path
from typing import Any, Optional, Dict, List, Union, Tuple

from lcars.base.component import (
    Component,
    LCARSBar,
    LCARSButton,
    LCARSElbow,
    LCARSIndicator,
    LCARSLabel,
    Primitive,
    SetStyle,
)
from lcars.base.graphic import LCARSBuilder
from lcars.base.default import DefaultBackground, Palette
from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.base.info import Version


# =====================================================================
# ЕЛЕМЕНТИ ІНТЕРФЕЙСУ — семантичні оркестратори та композиційні вузли
# Базовий клас Element — віртуальна конструкція, що координує фізичні віджети
# =====================================================================
class Element(Component):
    Type = "element"
    ElementType = "container"

    def __init__(self, Parent=None, **Args):
        super().__init__(
            Parent=Parent,
            WidgetType=LCARS.Widget,
            **Args
        )
        self.Items: Dict[str, Any] = {}
        self.Layout = None
        self.Builder = LCARSBuilder(self)
        self.Title = str(self.Take(Args, ["Title", "title"], ""))
        self.ActionText = str(self.Take(Args, ["ActionText", "actionText"], ""))
        self.ConfirmCallback = self.Take(Args, ["ConfirmCallback", "OnConfirm", "onConfirm"], None)
        self.Owner = self.Take(Args, ["Owner", "owner"], None)
        self.Speed = float(self.Take(Args, ["Speed", "speed"], 1.0))
        self.Phase = 0
        self.Scan = None
        self.Visible = True

    def UpdateAlert(self, SignalObj=None, **kw):
        super().UpdateAlert(SignalObj, **kw)
        for Child in list(self.Items.values()):
            if hasattr(Child, "UpdateAlert"):
                Child.UpdateAlert(SignalObj, **kw)
            elif hasattr(Child, "widget") and hasattr(Child.widget, "repaint"):
                Child.widget.repaint()
        return self

    def UpdatePower(self, SignalObj=None, **kw):
        super().UpdatePower(SignalObj, **kw)
        for Child in list(self.Items.values()):
            if hasattr(Child, "UpdatePower"):
                Child.UpdatePower(SignalObj, **kw)
            elif hasattr(Child, "widget") and hasattr(Child.widget, "repaint"):
                Child.widget.repaint()
        return self

    def UpdateSecurityLock(self, SignalObj=None, **kw):
        super().UpdateSecurityLock(SignalObj, **kw)
        for Child in list(self.Items.values()):
            if hasattr(Child, "UpdateSecurityLock"):
                Child.UpdateSecurityLock(SignalObj, **kw)
            elif hasattr(Child, "widget") and hasattr(Child.widget, "repaint"):
                Child.widget.repaint()
        return self

    def Vertical(
        self,
        Left=0,
        Top=0,
        Right=0,
        Bottom=0,
        Spacing=0
    ):
        LayoutRef = self.Layout
        if LayoutRef is None:
            LayoutRef = LCARS.Vertical()
            self.Widget.setLayout(LayoutRef)
        LayoutRef.setContentsMargins(Left, Top, Right, Bottom)
        LayoutRef.setSpacing(Spacing)
        self.Layout = LayoutRef
        return LayoutRef

    def Horizontal(
        self,
        Left=0,
        Top=0,
        Right=0,
        Bottom=0,
        Spacing=0
    ):
        LayoutRef = self.Layout
        if LayoutRef is None:
            LayoutRef = LCARS.Horizontal()
            self.Widget.setLayout(LayoutRef)
        LayoutRef.setContentsMargins(Left, Top, Right, Bottom)
        LayoutRef.setSpacing(Spacing)
        self.Layout = LayoutRef
        return LayoutRef

    def Add(self, *Arguments):
        if not Arguments:
            return self

        if self.Layout is None:
            if hasattr(self.Widget, "layout") and self.Widget.layout() is not None:
                self.Layout = self.Widget.layout()
            else:
                self.Vertical(0, 0, 0, 0, 0)

        TargetLayout = self.Layout
        Item = Arguments[0]
        Stretch = None

        if len(Arguments) == 1:
            Item = Arguments[0]
        elif len(Arguments) == 2:
            if hasattr(Arguments[0], "addWidget") or hasattr(Arguments[0], "addLayout"):
                TargetLayout = Arguments[0]
                Item = Arguments[1]
            else:
                Item = Arguments[0]
                Stretch = Arguments[1]
        elif len(Arguments) >= 3:
            TargetLayout = Arguments[0]
            Item = Arguments[1]
            Stretch = Arguments[2]

        if Item is None or TargetLayout is None:
            return self

        TargetWidget = getattr(Item, "Widget", getattr(Item, "widget", Item))
        if hasattr(TargetLayout, "addWidget") and (not hasattr(Item, "addWidget") or TargetWidget is not Item):
            if Stretch is None:
                TargetLayout.addWidget(TargetWidget)
            else:
                TargetLayout.addWidget(TargetWidget, int(Stretch))
        elif hasattr(TargetLayout, "addLayout"):
            SubLayout = getattr(Item, "Layout", Item)
            TargetLayout.addLayout(SubLayout)

        return self

    def AddLayout(self, TargetLayout, SubLayout):
        if TargetLayout is not None and SubLayout is not None and hasattr(TargetLayout, "addLayout"):
            LayoutObj = getattr(SubLayout, "Layout", SubLayout)
            TargetLayout.addLayout(LayoutObj)
        return self

    def AddStretch(self, TargetLayout=None, Factor=1):
        LayoutObj = TargetLayout or self.Layout
        if LayoutObj is not None and hasattr(LayoutObj, "addStretch"):
            LayoutObj.addStretch(int(Factor))
        return self

    def Clear(self):
        if self.Layout is None:
            return self

        while self.Layout.count():
            Item = self.Layout.takeAt(0)
            if Item is None:
                continue
            WidgetRef = Item.widget()
            if WidgetRef is not None:
                WidgetRef.deleteLater()

        self.Items.clear()
        return self

    def Get(self, Key: str, Default: Any = None) -> Any:
        return self.Items.get(Key, Default)

    def __getitem__(self, Key: str) -> Any:
        return self.Items[Key]

    def __setitem__(self, Key: str, Value: Any) -> None:
        self.Items[Key] = Value

    def Build(self):
        return self.BuildInterface()

    def BuildInterface(self):
        TargetType = str(self.Type).lower()
        if TargetType == "padd":
            return self.BuildPadd()
        elif TargetType == "screen":
            return self.BuildScreen()
        elif TargetType == "segment":
            return self.BuildSegment()
        elif TargetType in ("header", "headerframe"):
            return self.BuildHeader()
        elif TargetType == "footer":
            return self.BuildFooter()
        elif TargetType == "sidebar":
            return self.BuildSidebar()
        elif TargetType == "menu":
            return self.BuildMenu()
        elif TargetType == "toolbar":
            return self.BuildToolbar()
        elif TargetType == "statusline":
            return self.BuildStatusLine()
        elif TargetType == "datablock":
            return self.BuildDataBlock()
        elif TargetType == "statbar":
            return self.BuildStatBar()
        elif TargetType == "scanningbar":
            return self.BuildScanningBar()
        elif TargetType == "overlay":
            return self.BuildOverlay()
        elif TargetType == "stasis":
            return self.BuildStasis()
        elif TargetType in ("access", "accesscode"):
            return self.BuildAccess()
        elif TargetType in ("coupled", "coupledblock"):
            return self.BuildCoupled()
        elif TargetType in ("telemetry", "telemetryblock"):
            return self.BuildTelemetry()
        elif TargetType in ("bracket", "framebracket"):
            return self.BuildBracket()
        return self.BuildPanel()

    def BuildPanel(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        return self

    def BuildScreen(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        if "Content" not in self.Items:
            ContentSeg = Segment(Parent=self.Widget)
            self.Items["Content"] = ContentSeg
            RootLayout = getattr(self.Widget, "layout", lambda: None)()
            if RootLayout is None:
                RootLayout = LCARS.Vertical(self.Widget)
                RootLayout.setContentsMargins(0, 0, 0, 0)
                RootLayout.setSpacing(0)
                self.Layout = RootLayout
            Policy = getattr(LCARS, "Policy", None)
            if Policy and hasattr(ContentSeg.Widget, "setSizePolicy"):
                ContentSeg.Widget.setSizePolicy(Policy.Expanding, Policy.Expanding)
            RootLayout.addWidget(ContentSeg.Widget, 1)
        return self

    def BuildSegment(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        return self

    def BuildPadd(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet(f"background-color: #000000; border: none; color: {Palette.Buttons[0]};")
        if "Content" not in self.Items:
            ContentSeg = Segment(Parent=self.Widget)
            self.Items["Content"] = ContentSeg
            RootLayout = getattr(self.Widget, "layout", lambda: None)()
            if RootLayout is None:
                RootLayout = LCARS.Vertical(self.Widget)
                RootLayout.setContentsMargins(0, 0, 0, 0)
                RootLayout.setSpacing(0)
                self.Layout = RootLayout
            Policy = getattr(LCARS, "Policy", None)
            if Policy and hasattr(ContentSeg.Widget, "setSizePolicy"):
                ContentSeg.Widget.setSizePolicy(Policy.Expanding, Policy.Expanding)
            RootLayout.addWidget(ContentSeg.Widget, 1)
        return self

    # Канонічний верхній фрейм за кресленням CorelDRAW:
    # PillHalf(180°) + Заголовок + Код + Шина + PillHalf(0°)
    def BuildHeader(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 8)
        TitleText = self.Title or "USS ENTERPRISE"
        SubText = getattr(self, "SubTitle", "") or getattr(self, "Code", "") or "NCC 1071-D"

        self.Items["CapLeft"] = LCARSIndicator(
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=180,
            Width=28,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Title"] = LCARSLabel(
            Text=TitleText,
            Color=Palette.Buttons[2],
            FontSize=16,
            Parent=self.Widget
        )
        self.Items["Code"] = LCARSLabel(
            Text=SubText,
            Color=Palette.Buttons[1],
            FontSize=14,
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Type="bar",
            Height=12,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Items["CapRight"] = LCARSIndicator(
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=0,
            Width=28,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )

        self.Add(LayoutRef, self.Items["CapLeft"])
        self.Add(LayoutRef, self.Items["Title"])
        self.Add(LayoutRef, self.Items["Code"])
        self.Add(LayoutRef, self.Items["Bar"], 1)
        self.Add(LayoutRef, self.Items["CapRight"])
        return self

    def BuildFooter(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        if hasattr(self.Widget, "setFixedHeight"):
            self.Widget.setFixedHeight(36)
        LayoutRef = self.Horizontal(0, 0, 0, 0, 8)
        self.Items["Bar"] = LCARSBar(
            Type="divider",
            Height=8,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Items["Status"] = LCARSIndicator(
            Text=self.Title or "READY",
            Form=LCARSIndicator.SoftHalf,
            Direction=180,
            Height=28,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Cap"] = LCARSIndicator(
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=0,
            Width=28,
            Height=28,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Bar"], 1)
        self.Add(LayoutRef, self.Items["Status"])
        self.Add(LayoutRef, self.Items["Cap"])
        return self

    def BuildSidebar(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 6)
        self.Items["Top"] = LCARSElbow(
            Direction="top-left",
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Rail"] = Primitive(
            type="rect",
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Items["Bottom"] = LCARSElbow(
            Direction="bottom-left",
            Color=Palette.Buttons[2],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Top"])
        self.Add(LayoutRef, self.Items["Rail"], 1)
        self.Add(LayoutRef, self.Items["Bottom"])
        return self

    def BuildMenu(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(getattr(self, "Value", None), list) else ["SYSTEM", "PROGRAMS", "SETTINGS", "DIAGNOSTICS"]
        Index = 0
        for ItemText in Labels:
            ColorHex = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=ItemText,
                Form=LCARSButton.SoftHalf,
                Direction=0,
                Color=ColorHex,
                Parent=self.Widget
            )
            self.Items[f"Button{Index}"] = Btn
            self.Add(LayoutRef, Btn)
            Index += 1
        self.AddStretch(LayoutRef)
        return self

    def BuildToolbar(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        Labels = self.Value if isinstance(getattr(self, "Value", None), list) else ["BACK", "HOME", "NEXT"]
        Index = 0
        for ItemText in Labels:
            ColorHex = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=ItemText,
                Form=LCARSButton.Pill,
                Color=ColorHex,
                Parent=self.Widget
            )
            self.Items[f"Tool{Index}"] = Btn
            self.Add(LayoutRef, Btn)
            Index += 1
        self.AddStretch(LayoutRef)
        return self

    def BuildStatusLine(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 8)
        StatusText = getattr(self, "Value", None) or "READY"
        self.Items["Status"] = LCARSIndicator(
            Text=StatusText,
            Type="status",
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Type="divider",
            Height=4,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Status"])
        self.Add(LayoutRef, self.Items["Bar"], 1)
        return self

    def BuildDataBlock(self):
        ColorHex = self.Color or Palette.Buttons[1]
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet(f"background-color: #060608; border-left: 4px solid {ColorHex}; border-radius: 4px;")
        LayoutRef = self.Vertical(8, 8, 8, 8, 4)
        
        RawLabel = getattr(self, "LabelText", None) or getattr(self, "Label", "")
        if isinstance(RawLabel, str):
            LabelStr = RawLabel.upper()
        elif hasattr(RawLabel, "Text"):
            LabelStr = str(RawLabel.Text).upper()
        else:
            LabelStr = "DATA"

        RawValue = getattr(self, "ValueText", None) or getattr(self, "Value", "")
        if isinstance(RawValue, (str, int, float)):
            ValueStr = str(RawValue).upper()
        else:
            ValueStr = "--"

        self.Items["Label"] = LCARSLabel(
            Text=LabelStr,
            Color=ColorHex,
            FontSize=13,
            Parent=self.Widget
        )
        self.Items["Value"] = LCARSLabel(
            Text=ValueStr,
            Color="#FFFFFF",
            FontSize=15,
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Add(LayoutRef, self.Items["Value"])
        return self

    def BuildStatBar(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 10)
        MaxValue = 100
        Val = int(getattr(self, "Value", 0) or 0)
        LabelStr = str(getattr(self, "LabelText", "") or getattr(self, "Label", "") or "")
        ColorHex = self.Color or Palette.Buttons[1]

        self.Items["Label"] = LCARSIndicator(
            Text=LabelStr,
            Type="label",
            Color=ColorHex,
            Parent=self.Widget
        )
        ProgressClass = getattr(LCARS, "Progress", None)
        if ProgressClass:
            ProgressBarWidget = ProgressClass(self.Widget)
        else:
            ProgressBarWidget = LCARSBar(
                Type="bar",
                Height=12,
                Color=ColorHex,
                Parent=self.Widget
            )
        self.Items["Progress"] = ProgressBarWidget
        if hasattr(ProgressBarWidget, "setObjectName"):
            ProgressBarWidget.setObjectName("LCARSProgress")
        if hasattr(ProgressBarWidget, "setTextVisible"):
            ProgressBarWidget.setTextVisible(False)
        if hasattr(ProgressBarWidget, "setRange"):
            ProgressBarWidget.setRange(0, MaxValue)
        if hasattr(ProgressBarWidget, "setValue"):
            ProgressBarWidget.setValue(Val)
        SetStyle(
            ProgressBarWidget,
            "#LCARSProgress { background: #111111; border: none; border-radius: 6px; }"
            f"#LCARSProgress::chunk {{ background: {ColorHex}; border-radius: 5px; }}",
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Add(LayoutRef, ProgressBarWidget, 1)
        return self

    def BuildScanningBar(self):
        self.Phase = 0
        ColorHex = self.Color or Palette.Buttons[1]
        self.Scan = LCARSBar(
            Type="scanning",
            Height=15,
            Color=ColorHex,
            Parent=self.Widget
        )
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 0)
        self.Add(LayoutRef, self.Scan)
        return self

    def BuildOverlay(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: rgba(0, 0, 0, 240);")
        LayoutRef = self.Vertical(40, 40, 40, 40, 12)
        ActionDesc = str(self.ActionText or "").upper()
        self.Items["Title"] = LCARSIndicator(
            "SECURITY CLEARANCE AUTHORIZATION",
            Type="alert",
            Color=Palette.Red[0],
            Parent=self.Widget
        )
        self.Items["Message"] = LCARSIndicator(
            f"CRITICAL ACTION: {ActionDesc}",
            Type="label",
            Color=Palette.Buttons[2],
            Parent=self.Widget
        )
        self.Items["Confirm"] = LCARSButton(
            "AUTHORIZE",
            Color=Palette.Red[0],
            Form=LCARSButton.Pill,
            Parent=self.Widget
        )
        self.Items["Cancel"] = LCARSButton(
            "ABORT",
            Color=Palette.Disabled[0],
            Form=LCARSButton.Pill,
            Parent=self.Widget
        )
        self.Items["Confirm"].Clicked.Connect(self.AuthorizeAction)
        self.Items["Cancel"].Clicked.Connect(self.Cleanup)

        ButtonLayout = self.Horizontal(0, 0, 0, 0, 10)
        self.Add(LayoutRef, self.Items["Title"])
        self.Add(LayoutRef, self.Items["Message"])
        self.AddStretch(LayoutRef)
        self.Add(ButtonLayout, self.Items["Confirm"])
        self.Add(ButtonLayout, self.Items["Cancel"])
        self.AddLayout(LayoutRef, ButtonLayout)
        return self

    def BuildStasis(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 0)
        self.Items["Label"] = LCARSIndicator(
            "SYSTEM IN STASIS",
            Type="title",
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Label"])
        self.Widget.mousePressEvent = self.TriggerWakeup
        return self

    # Канонічний блок доступу за кресленням CorelDRAW:
    # AccentBar + Label("ACCESS CODE") + Mask("**********") + StatusButton("AUTHORIZED")
    def BuildAccess(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        TitleText = getattr(self, "Title", "") or "ACCESS CODE"
        MaskCode = getattr(self, "Code", "") or getattr(self, "Value", "") or "**********"
        StatusText = getattr(self, "StatusText", "") or "AUTHORIZED"

        self.Items["Bar"] = LCARSBar(
            Width=8,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Title"] = LCARSLabel(
            Text=TitleText,
            Color=Palette.Buttons[2],
            FontSize=14,
            Parent=self.Widget
        )
        self.Items["Mask"] = LCARSLabel(
            Text=MaskCode,
            Color="#FFFFFF",
            FontSize=15,
            Parent=self.Widget
        )
        self.Items["Button"] = LCARSButton(
            Text=StatusText,
            Form=LCARSButton.SoftHalf,
            Direction=0,
            Color=Palette.Buttons[1],
            Height=34,
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Bar"])
        self.Add(LayoutRef, self.Items["Title"])
        self.Add(LayoutRef, self.Items["Mask"])
        self.AddStretch(LayoutRef)
        self.Add(LayoutRef, self.Items["Button"])
        return self

    # Канонічний спарений блок за кресленням CorelDRAW:
    # Button + вузький SuffixBar (зазор 2–4px)
    def BuildCoupled(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 3)
        BtnText = getattr(self, "Text", "") or getattr(self, "Title", "") or "COUPLED"
        BtnNum = getattr(self, "Number", "") or "01"
        BtnForm = getattr(self, "Form", LCARSButton.SoftHalf)
        BtnDir = getattr(self, "Direction", 0)

        self.Items["Button"] = LCARSButton(
            Text=BtnText,
            Number=BtnNum,
            Form=BtnForm,
            Direction=BtnDir,
            Height=getattr(self, "Height", 36),
            Color=self.Color or Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Width=12,
            Height=getattr(self, "Height", 36),
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Button"], 1)
        self.Add(LayoutRef, self.Items["Bar"])
        return self

    # Канонічний блок телеметрії за кресленням CorelDRAW:
    # Placard + NumberLabel("07") + Terminator
    def BuildTelemetry(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: transparent; border: none;")
        LayoutRef = self.Horizontal(0, 0, 0, 0, 6)
        TelemetryVal = str(getattr(self, "Value", "") or getattr(self, "Number", "") or "07")
        BadgeText = str(getattr(self, "Badge", "") or getattr(self, "Title", "") or "SEC")

        self.Items["Badge"] = LCARSIndicator(
            Text=BadgeText,
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=180,
            Width=32,
            Height=34,
            Color=Palette.Buttons[2],
            Parent=self.Widget
        )
        self.Items["Number"] = LCARSLabel(
            Text=TelemetryVal,
            FontSize=22,
            Width=52,
            Color="#FFFFFF",
            Parent=self.Widget
        )
        self.Items["Bar"] = LCARSBar(
            Height=12,
            Color=Palette.Buttons[1],
            Parent=self.Widget
        )
        self.Items["Terminator"] = LCARSIndicator(
            IndicatorType=LCARSIndicator.PillHalf,
            Direction=0,
            Width=20,
            Height=34,
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, self.Items["Badge"])
        self.Add(LayoutRef, self.Items["Number"])
        self.Add(LayoutRef, self.Items["Bar"], 1)
        self.Add(LayoutRef, self.Items["Terminator"])
        return self

    # Канонічний каркасний кутник за кресленням CorelDRAW:
    # Elbow + Shelf + SpineRail
    def BuildBracket(self):
        if hasattr(self.Widget, "setStyleSheet"):
            self.Widget.setStyleSheet("background-color: #000000; border: none;")
        LayoutRef = self.Vertical(0, 0, 0, 0, 4)
        TopRow = Segment(Parent=self.Widget)
        TopRowLayout = TopRow.Horizontal(0, 0, 0, 0, 4)

        self.Items["Elbow"] = LCARSElbow(
            Direction="top-left",
            Width=getattr(self, "Width", 320),
            Height=getattr(self, "Height", 64),
            Thickness=getattr(self, "Thickness", 24),
            Color=self.Color or Palette.Buttons[0],
            Parent=TopRow.Widget
        )
        self.Items["Shelf"] = LCARSBar(
            Height=getattr(self, "Thickness", 24),
            Color=Palette.Buttons[1],
            Parent=TopRow.Widget
        )
        TopRow.Add(TopRowLayout, self.Items["Elbow"])
        TopRow.Add(TopRowLayout, self.Items["Shelf"], 1)

        self.Items["Spine"] = LCARSBar(
            Width=getattr(self, "Thickness", 24),
            Color=Palette.Buttons[0],
            Parent=self.Widget
        )
        self.Add(LayoutRef, TopRow)
        self.Add(LayoutRef, self.Items["Spine"], 1)
        return self

    def SetValue(self, Value):
        self.Value = Value
        ValueItem = self.Items.get("Value")
        if ValueItem and hasattr(ValueItem, "SetValue"):
            ValueItem.SetValue(Value)
        elif ValueItem and hasattr(ValueItem, "SetText"):
            ValueItem.SetText(str(Value))
        Progress = self.Items.get("Progress")
        if Progress and hasattr(Progress, "setValue"):
            Progress.setValue(int(Value))
        return self

    def SetLabel(self, Label):
        self.Label = str(Label)
        LabelItem = self.Items.get("Label")
        if LabelItem and hasattr(LabelItem, "SetText"):
            LabelItem.SetText(str(Label))
        return self

    def AuthorizeAction(self):
        if self.ConfirmCallback:
            self.ConfirmCallback()
        self.Cleanup()

    def Cleanup(self):
        DeleteMethod = getattr(self.Widget, "deleteLater", None)
        if DeleteMethod:
            DeleteMethod()

    def TriggerWakeup(self, Event):
        WakeUpMethod = getattr(self.Owner, "WakeUp", None)
        if WakeUpMethod:
            WakeUpMethod()

    def SetFixedSize(self, *Args):
        if self.Widget and hasattr(self.Widget, "setFixedSize"):
            self.Widget.setFixedSize(*Args)
        return self

    def SetFixedWidth(self, Width: int):
        if self.Widget and hasattr(self.Widget, "setFixedWidth"):
            self.Widget.setFixedWidth(int(Width))
        return self

    def SetFixedHeight(self, Height: int):
        if self.Widget and hasattr(self.Widget, "setFixedHeight"):
            self.Widget.setFixedHeight(int(Height))
        return self

    def SetVisible(self, VisibleState: bool):
        if self.Widget and hasattr(self.Widget, "setVisible"):
            self.Widget.setVisible(bool(VisibleState))
        self.Visible = bool(VisibleState)
        return self

    def IsVisible(self) -> bool:
        if self.Widget and hasattr(self.Widget, "isVisible"):
            return self.Widget.isVisible()
        return getattr(self, "Visible", True)

    setFixedSize = SetFixedSize
    setFixedWidth = SetFixedWidth
    setFixedHeight = SetFixedHeight
    setVisible = SetVisible
    isVisible = IsVisible


# =====================================================================
# PADD — Повнофункціональний екранний термінал зорельота
# =====================================================================
class PADD(Element):
    Type = "PADD"

    def __init__(self, Parent=None, **Args):
        Width = self.Take(Args, ["Width", "width"], 920)
        Height = self.Take(Args, ["Height", "height"], 580)
        MinWidth = self.Take(Args, ["MinWidth", "minWidth"], 1)
        MinHeight = self.Take(Args, ["MinHeight", "minHeight"], 1)
        Portable = self.Take(Args, ["Portable", "portable"], Parent is None)

        super().__init__(
            Parent=Parent,
            **Args
        )

        self.PaddStartWidth = int(Width)
        self.PaddStartHeight = int(Height)
        self.PaddMinWidth = int(MinWidth)
        self.PaddMinHeight = int(MinHeight)
        self.PaddPortable = bool(Portable)

        self.PaddAction = ""
        self.PaddStartGlobal = (0, 0)
        self.PaddStartRect = (0, 0, 0, 0)
        self.PaddOffset = (0, 0)

        self.PaddCurrentWidth = int(Width)
        self.PaddCurrentHeight = int(Height)

        self.PaddFullscreen = False
        self.PaddSavedGeometry = None

        self.Builder = LCARSBuilder(self)
        self.ConfigurePadd()
        self.Build()

    @property
    def Content(self):
        return self.Items.get("Content")

    def ConfigurePadd(self):
        Host = self.Widget
        if hasattr(Host, "setMinimumSize"):
            Host.setMinimumSize(self.PaddMinWidth, self.PaddMinHeight)
        if hasattr(Host, "setMaximumSize"):
            Host.setMaximumSize(16777215, 16777215)
        if hasattr(Host, "resize"):
            Host.resize(self.PaddStartWidth, self.PaddStartHeight)

        OriginalResize = getattr(Host, "resizeEvent", None)
        PaddSelf = self

        def PaddResizeHook(Event):
            PaddSelf.AdaptPaddGeometry(Event)
            if OriginalResize:
                OriginalResize(Event)
        Host.resizeEvent = PaddResizeHook

        if self.PaddPortable:
            FramelessFlag = getattr(LCARS, "Frameless", None)
            if hasattr(Host, "setWindowFlags") and FramelessFlag is not None:
                Host.setWindowFlags(Host.windowFlags() | FramelessFlag)
            if hasattr(Host, "setStyleSheet"):
                Host.setStyleSheet(f"background-color: #000000; color: {Palette.Buttons[0]};")
            if hasattr(Host, "setSizePolicy"):
                Policy = getattr(LCARS, "Policy", None)
                if Policy:
                    Host.setSizePolicy(Policy.Expanding, Policy.Expanding)
            self.EnablePortablePadd(Host)

    def AdaptPaddGeometry(self, Event):
        Host = self.Widget
        if not Host:
            return
        W = Host.width() if hasattr(Host, "width") else 0
        H = Host.height() if hasattr(Host, "height") else 0
        if W < 1 or H < 1:
            return

        Margin = max(4, min(20, W // 50, H // 50))
        Spacing = max(2, min(8, Margin // 2))

        ContentItem = self.Items.get("Content")
        if ContentItem is not None:
            ContentLayout = getattr(ContentItem, "Layout", None)
            if ContentLayout and hasattr(ContentLayout, "setContentsMargins"):
                ContentLayout.setContentsMargins(Margin, Margin, Margin, Margin)
                ContentLayout.setSpacing(Spacing)

        self.PaddCurrentWidth = W
        self.PaddCurrentHeight = H

    OnPaddResize = AdaptPaddGeometry

    def EnablePortablePadd(self, Host=None):
        Targets = [
            Host,
            self.Items.get("Body"),
        ]
        for Target in Targets:
            TargetWidget = getattr(Target, "Widget", getattr(Target, "widget", Target))
            if TargetWidget is None:
                continue
            TargetWidget.mousePressEvent = self.PaddPress
            TargetWidget.mouseMoveEvent = self.PaddMove
            TargetWidget.mouseReleaseEvent = self.PaddRelease

    def EventGlobal(self, Event):
        Method = getattr(Event, "globalPosition", None)
        if Method:
            Point = Method()
            Convert = getattr(Point, "toPoint", None)
            if Convert:
                Point = Convert()
            return int(Point.x()), int(Point.y())
        Method = getattr(Event, "globalPos", None)
        if Method:
            Point = Method()
            return int(Point.x()), int(Point.y())
        return 0, 0

    def PaddPress(self, Event):
        Host = self.Widget
        GX, GY = self.EventGlobal(Event)
        self.PaddStartGlobal = (GX, GY)
        self.PaddStartRect = (
            int(Host.x()),
            int(Host.y()),
            int(Host.width()),
            int(Host.height()),
        )
        LX = GX - self.PaddStartRect[0]
        LY = GY - self.PaddStartRect[1]
        self.PaddOffset = (LX, LY)
        self.PaddAction = self.PaddEdgeAction(LX, LY)
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def PaddMove(self, Event):
        if not self.PaddAction:
            return
        Host = self.Widget
        if not Host:
            return
        GX, GY = self.EventGlobal(Event)
        X, Y, W, H = self.PaddStartRect
        DX = GX - self.PaddStartGlobal[0]
        DY = GY - self.PaddStartGlobal[1]

        if self.PaddAction == "move":
            Host.move(GX - self.PaddOffset[0], GY - self.PaddOffset[1])
            return

        NewX = X
        NewY = Y
        NewW = W
        NewH = H
        if "left" in self.PaddAction:
            NewX = X + DX
            NewW = W - DX
        if "right" in self.PaddAction:
            NewW = W + DX
        if "top" in self.PaddAction:
            NewY = Y + DY
            NewH = H - DY
        if "bottom" in self.PaddAction:
            NewH = H + DY

        if NewW < self.PaddMinWidth:
            if "left" in self.PaddAction:
                NewX -= self.PaddMinWidth - NewW
            NewW = self.PaddMinWidth
        if NewH < self.PaddMinHeight:
            if "top" in self.PaddAction:
                NewY -= self.PaddMinHeight - NewH
            NewH = self.PaddMinHeight

        Host.move(NewX, NewY)
        Host.resize(NewW, NewH)
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def PaddRelease(self, Event):
        self.PaddAction = ""
        AcceptMethod = getattr(Event, "accept", None)
        if AcceptMethod:
            AcceptMethod()

    def ToggleFullscreen(self):
        Host = self.Widget
        if not Host:
            return
        if not self.PaddFullscreen:
            Geometry = getattr(Host, "geometry", None)
            if Geometry:
                self.PaddSavedGeometry = Geometry()
            ShowFull = getattr(Host, "showFullScreen", None)
            if ShowFull:
                ShowFull()
            self.PaddFullscreen = True
            return
        ShowNormal = getattr(Host, "showNormal", None)
        if ShowNormal:
            ShowNormal()
        if self.PaddSavedGeometry is not None and hasattr(Host, "setGeometry"):
            Host.setGeometry(self.PaddSavedGeometry)
        self.PaddFullscreen = False

    def PaddEdgeAction(self, X, Y):
        Host = self.Widget
        Edge = 28
        Width = int(Host.width())
        Height = int(Host.height())
        Left = X <= Edge
        Right = X >= Width - Edge
        Top = Y <= Edge
        Bottom = Y >= Height - Edge
        Parts = []
        if Top:
            Parts.append("top")
        if Bottom:
            Parts.append("bottom")
        if Left:
            Parts.append("left")
        if Right:
            Parts.append("right")
        if Parts:
            return "-".join(Parts)
        return "move"


# =====================================================================
# ПІДКЛАСИ ТА СЕМАНТИЧНІ ТИПИ ЕЛЕМЕНТІВ
# =====================================================================
class Screen(Element):
    Type = "screen"

    def __init__(self, Parent=None, **Args):
        super().__init__(Parent=Parent, **Args)
        Host = self.Widget
        # Канонічний термінал зорельота: без рамок Windows OS
        if Parent is None and Host is not None:
            FramelessFlag = getattr(LCARS, "Frameless", None)
            if hasattr(Host, "setWindowFlags") and FramelessFlag is not None:
                Host.setWindowFlags(Host.windowFlags() | FramelessFlag)
            if hasattr(Host, "setStyleSheet"):
                Host.setStyleSheet("background-color: #000000; border: none; color: #FFFFFF;")
            if hasattr(Host, "setAttribute") and hasattr(LCARS, "Protocol"):
                AlignObj = getattr(LCARS.Protocol, "Align", None)
                WidgetAttr = getattr(AlignObj, "WidgetAttribute", None)
                if WidgetAttr and hasattr(WidgetAttr, "WA_TranslucentBackground"):
                    pass
        self.Build()

Display = Screen


class Panel(Element):
    Type = "panel"


class Segment(Element):
    Type = "segment"


class Header(Element):
    Type = "header"

    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="header", Parent=Parent, Title=Title, **Args)
        self.Build()

HeaderFrame = Header


class Footer(Element):
    Type = "footer"

    def __init__(self, Title="", Parent=None, **Args):
        super().__init__(Type="footer", Parent=Parent, Title=Title, **Args)
        self.Build()


class Sidebar(Element):
    Type = "sidebar"

    def __init__(self, Parent=None, **Args):
        super().__init__(Type="sidebar", Parent=Parent, **Args)
        self.Build()


class Menu(Element):
    Type = "menu"

    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="menu", Parent=Parent, Value=Items or [], **Args)
        self.Build()


class Toolbar(Element):
    Type = "toolbar"

    def __init__(self, Items=None, Parent=None, **Args):
        super().__init__(Type="toolbar", Parent=Parent, Value=Items or [], **Args)
        self.Build()


class StatusLine(Element):
    Type = "statusline"

    def __init__(self, Text="READY", Parent=None, **Args):
        super().__init__(Type="statusline", Parent=Parent, Value=Text, **Args)
        self.Build()


class Confirmation(Element):
    Type = "overlay"

    def __init__(self, ActionText="", OnConfirm=None, Parent=None, **Args):
        super().__init__(
            Type="overlay",
            Parent=Parent,
            ActionText=ActionText,
            ConfirmCallback=OnConfirm,
            **Args
        )
        self.Build()


class Stasis(Element):
    Type = "stasis"

    def __init__(self, Owner=None, Parent=None, **Args):
        super().__init__(Type="stasis", Parent=Parent, Owner=Owner, **Args)
        self.Build()


class AccessCode(Element):
    Type = "access"

    def __init__(self, Title="ACCESS CODE", Code="**********", Status="AUTHORIZED", Parent=None, **Args):
        super().__init__(
            Type="access",
            Parent=Parent,
            Title=Title,
            Code=Code,
            StatusText=Status,
            **Args
        )
        self.Build()

Access = AccessCode


class CoupledBlock(Element):
    Type = "coupled"

    def __init__(self, Text="", Number="", Form=None, Direction=0, Height=36, Parent=None, **Args):
        super().__init__(
            Type="coupled",
            Parent=Parent,
            Text=Text,
            Number=Number,
            Form=Form or LCARSButton.SoftHalf,
            Direction=Direction,
            Height=Height,
            **Args
        )
        self.Build()

Coupled = CoupledBlock


class TelemetryBlock(Element):
    Type = "telemetry"

    def __init__(self, Number="07", Badge="SEC", Parent=None, **Args):
        super().__init__(
            Type="telemetry",
            Parent=Parent,
            Number=Number,
            Badge=Badge,
            **Args
        )
        self.Build()

Telemetry = TelemetryBlock


class FrameBracket(Element):
    Type = "bracket"

    def __init__(self, Width=320, Height=64, Thickness=24, Parent=None, **Args):
        super().__init__(
            Type="bracket",
            Parent=Parent,
            Width=Width,
            Height=Height,
            Thickness=Thickness,
            **Args
        )
        self.Build()

Bracket = FrameBracket


class DataBlock(Element):
    Type = "datablock"

    def __init__(self, *Arguments, **Args):
        LabelText = Args.pop("Label", Args.pop("label", Args.pop("LabelText", Args.pop("labelText", ""))))
        ValueText = Args.pop("Value", Args.pop("value", Args.pop("ValueText", Args.pop("valueText", ""))))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Color = Args.pop("Color", Args.pop("color", None))

        if len(Arguments) >= 1:
            LabelText = Arguments[0]
        if len(Arguments) >= 2:
            ValueText = Arguments[1]
        if len(Arguments) >= 3:
            if isinstance(Arguments[2], str):
                Color = Arguments[2]
            else:
                Parent = Arguments[2]
        if len(Arguments) >= 4:
            if isinstance(Arguments[3], str):
                Color = Arguments[3]
            else:
                Parent = Arguments[3]

        super().__init__(
            Type="datablock",
            Parent=Parent,
            Color=Color,
            Label=LabelText,
            Value=ValueText,
            **Args
        )
        self.Build()


class StatBar(Element):
    Type = "statbar"

    def __init__(self, *Arguments, **Args):
        LabelText = Args.pop("Label", Args.pop("label", Args.pop("LabelText", Args.pop("labelText", ""))))
        Value = Args.pop("Value", Args.pop("value", 0))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Color = Args.pop("Color", Args.pop("color", None))

        if len(Arguments) >= 1:
            LabelText = Arguments[0]
        if len(Arguments) >= 2:
            if isinstance(Arguments[1], str) and Arguments[1].startswith("#"):
                Color = Arguments[1]
            else:
                Value = Arguments[1]
        if len(Arguments) >= 3:
            if isinstance(Arguments[2], str) and Arguments[2].startswith("#"):
                Color = Arguments[2]
            else:
                Parent = Arguments[2]

        super().__init__(
            Type="statbar",
            Parent=Parent,
            Color=Color,
            Label=LabelText,
            Value=Value,
            **Args
        )
        self.Build()


class ScanningBar(Element):
    Type = "scanningbar"

    def __init__(self, *Arguments, **Args):
        ColorVal = Args.pop("Color", Args.pop("color", Args.pop("ColorVal", None)))
        Parent = Args.pop("Parent", Args.pop("parent", None))
        Speed = Args.pop("Speed", Args.pop("speed", 1.0))

        if len(Arguments) >= 1:
            if isinstance(Arguments[0], str):
                ColorVal = Arguments[0]
            else:
                Parent = Arguments[0]
        if len(Arguments) >= 2:
            if isinstance(Arguments[1], (int, float)):
                Speed = Arguments[1]
            elif isinstance(Arguments[1], str):
                ColorVal = Arguments[1]
            else:
                Parent = Arguments[1]

        super().__init__(
            Type="scanningbar",
            Parent=Parent,
            Color=ColorVal,
            Speed=Speed,
            **Args
        )
        self.Build()


class ButtonGroup:
    def __init__(self):
        self.ButtonsList = []

    def AddButton(self, button):
        self.ButtonsList.append(button)

    def Buttons(self):
        return list(self.ButtonsList)

    def CheckedButton(self):
        for ButtonObj in self.ButtonsList:
            if hasattr(ButtonObj, "isChecked") and ButtonObj.isChecked():
                return ButtonObj
        return self.ButtonsList[0] if self.ButtonsList else None


# =====================================================================
# CHIP INTERFACE BUILDER — Фабрика зчитування й побудови чіпів ODN
# =====================================================================
class ChipInterfaceBuilder:
    @classmethod
    def LocateChip(cls, ChipId: str) -> Optional[Path]:
        CleanId = str(ChipId).strip().replace(".yaml", "").replace(".yml", "")
        BaseDir = Path(__file__).resolve().parents[2]
        Cat = CleanId.split("-")[0] if "-" in CleanId else "05"
        Candidates = [
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / f"{CleanId[:7]}.yaml",
            BaseDir / "lcars" / "engineering" / "chips" / Cat / "05-0000.yaml",
        ]
        for Candidate in Candidates:
            if Candidate.exists():
                return Candidate
        return None

    @classmethod
    def LoadChipData(cls, ChipId: str) -> dict:
        ChipFile = cls.LocateChip(ChipId)
        if not ChipFile:
            return {}
        with open(ChipFile, "r", encoding="utf-8") as FileStream:
            Manifest = yaml.safe_load(FileStream) or {}

        DbConfig = Manifest.get("config", {}).get("database", {})
        DbRelPath = DbConfig.get("path", "")
        if DbRelPath:
            BaseDir = Path(__file__).resolve().parents[2]
            DbPath = BaseDir / DbRelPath
            if DbPath.exists():
                Conn = sqlite3.connect(str(DbPath))
                Cursor = Conn.cursor()
                Table = DbConfig.get("table", "ui_chip_images")
                ScreenName = DbConfig.get("screen", "master_catalog")
                Cursor.execute(
                    f"SELECT elements_json FROM {Table} WHERE chip_id=? OR screen_name=? LIMIT 1",
                    (str(ChipId), str(ScreenName))
                )
                Row = Cursor.fetchone()
                Conn.close()
                if Row and Row[0]:
                    Payload = json.loads(Row[0])
                    if "layout" not in Payload and "sections" in Payload:
                        return {"layout": Payload}
                    return Payload

        LayoutPayload = Manifest.get("layout", {})
        if LayoutPayload:
            return {"layout": LayoutPayload}
        return {}

    @classmethod
    def Build(cls, ChipId: str, ParentHost: Any = None, MasterPadd: Any = None):
        Data = cls.LoadChipData(ChipId)
        if not Data:
            return None
        LayoutConfig = Data.get("layout", {})
        RootPanel = Panel(Parent=ParentHost)
        RootLayout = RootPanel.Vertical(16, 14, 16, 14, 18)
        StatusLabelRef = [None]

        def HandleModeAction(ActionType):
            from lcars.system.alert import GetAlertSystem, AlertLevel
            import lcars.base.default as DefaultMod
            AlertSys = GetAlertSystem()
            if ActionType == "normal":
                DefaultMod.SystemState = "normal"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.GREEN)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: NORMAL // STANDARD STARFLEET OPERATIONAL PALETTE")
            elif ActionType == "yellow":
                DefaultMod.SystemState = "yellow"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.YELLOW)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION YELLOW // ACTIVE SENSOR CAUTION")
            elif ActionType == "red":
                DefaultMod.SystemState = "red"
                if AlertSys:
                    AlertSys.SetLevel(AlertLevel.RED)
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: CONDITION RED // ALL STATIONS TO TACTICAL ALERT")
            elif ActionType == "auth":
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("AUTHORIZATION ACCEPTED // SECURITY CLEARANCE LEVEL 4")
                    StatusLabelRef[0].Update()
            elif ActionType == "standby":
                DefaultMod.SystemState = "disabled"
                if StatusLabelRef[0]:
                    StatusLabelRef[0].SetText("SYSTEM MODE: STANDBY // POWER CONSERVE PROTOCOL")
            if MasterPadd and hasattr(MasterPadd, "Widget") and MasterPadd.Widget:
                MasterPadd.Widget.update()

        Sections = LayoutConfig.get("sections", [])
        for SecData in Sections:
            SecPanel = Panel(Parent=RootPanel.Widget)
            SecVL = SecPanel.Vertical(0, 0, 0, 0, SecData.get("spacing", 8))

            if "header" in SecData:
                HdrData = SecData["header"]
                HdrLbl = LCARSLabel(
                    Text=HdrData.get("text", ""),
                    FontSize=HdrData.get("font_size", 18),
                    Parent=SecPanel.Widget,
                )
                SecPanel.Add(SecVL, HdrLbl)

            if "status_label" in SecData:
                StData = SecData["status_label"]
                StRow = Segment(Parent=SecPanel.Widget)
                StRL = StRow.Horizontal(0, 0, 0, 0, 6)
                StLbl = LCARSLabel(
                    Text=StData.get("text", ""),
                    FontSize=StData.get("font_size", 18),
                    Parent=StRow.Widget,
                )
                StatusLabelRef[0] = StLbl
                StRow.Add(StRL, StLbl)
                SecPanel.Add(SecVL, StRow)

            for RowData in SecData.get("rows", []):
                RowType = RowData.get("type", "segment")
                if RowType == "compound_stacks":
                    RowMain = Segment(Parent=SecPanel.Widget)
                    RML = RowMain.Horizontal(0, 0, 0, 0, 12)

                    LeftStack = Segment(Parent=RowMain.Widget)
                    LSL = LeftStack.Vertical(0, 0, 0, 0, 4)
                    for NumVal, NameVal, ChipCode in RowData.get("left_rows", []):
                        RowItem = Segment(Parent=LeftStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        Cap = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=180,
                            Width=28,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        Bar = LCARSBar(Width=6, Height=28, Parent=RowItem.Widget)
                        NumLbl = LCARSLabel(Text=NumVal, FontSize=20, Width=48, Parent=RowItem.Widget)
                        Btn = LCARSButton(
                            Text=NameVal,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=0,
                            Height=28,
                            Width=180,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, Cap)
                        RowItem.Add(RL, Bar)
                        RowItem.Add(RL, NumLbl)
                        RowItem.Add(RL, Btn)
                        LeftStack.Add(LSL, RowItem)
                    RowMain.Add(RML, LeftStack)

                    RightStack = Segment(Parent=RowMain.Widget)
                    RSL = RightStack.Vertical(0, 0, 0, 0, 4)
                    for Subsys, BadgeVal, TelemetryVal, ChipCode in RowData.get("right_rows", []):
                        RowItem = Segment(Parent=RightStack.Widget)
                        RL = RowItem.Horizontal(0, 0, 0, 0, 4)
                        LBtn = LCARSButton(
                            Text=Subsys,
                            Number=ChipCode,
                            Form=LCARSButton.SoftHalf,
                            Direction=180,
                            Height=28,
                            Width=160,
                            FontSize=16,
                            Parent=RowItem.Widget
                        )
                        BadgeLbl = LCARSLabel(Text=BadgeVal, FontSize=20, Width=36, Parent=RowItem.Widget)
                        DataLbl = LCARSLabel(Text=TelemetryVal, FontSize=18, Width=140, Parent=RowItem.Widget)
                        CapR = LCARSIndicator(
                            IndicatorType=LCARSIndicator.PillHalf,
                            Direction=0,
                            Width=24,
                            Height=28,
                            Parent=RowItem.Widget
                        )
                        RowItem.Add(RL, LBtn)
                        RowItem.Add(RL, BadgeLbl)
                        RowItem.Add(RL, DataLbl)
                        RowItem.Add(RL, CapR)
                        RightStack.Add(RSL, RowItem)
                    RowMain.Add(RML, RightStack, 1)
                    SecPanel.Add(SecVL, RowMain)

                elif RowType == "bars_stack":
                    BarRow = Segment(Parent=SecPanel.Widget)
                    BRL = BarRow.Vertical(0, 0, 0, 0, 4)
                    for HVal in RowData.get("heights", [4, 8, 14, 22]):
                        Bar = LCARSBar(Height=HVal, Parent=BarRow.Widget)
                        BarRow.Add(BRL, Bar)
                    SecPanel.Add(SecVL, BarRow)

                else:
                    RowSeg = Segment(Parent=SecPanel.Widget)
                    RL = RowSeg.Horizontal(0, 0, 0, 0, RowData.get("spacing", 6))
                    for Item in RowData.get("items", []):
                        IType = Item.get("type", "button")
                        Flex = Item.get("flex", 0)
                        if IType == "button":
                            ActionKey = Item.get("action", "")
                            Btn = LCARSButton(
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Form=Item.get("form", LCARSButton.Pill),
                                Height=Item.get("height", 38),
                                Width=Item.get("width", 0),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            if ActionKey:
                                def MakeHandler(Act):
                                    return lambda *a: HandleModeAction(Act)
                                Btn.Clicked.Connect(MakeHandler(ActionKey))
                            RowSeg.Add(RL, Btn, Flex)
                        elif IType == "elbow":
                            Elb = LCARSElbow(
                                Direction=Item.get("direction", "top-left"),
                                Text=Item.get("text", ""),
                                Number=Item.get("number", ""),
                                Width=Item.get("width", 480),
                                Height=Item.get("height", 80),
                                Thickness=Item.get("thickness", 24),
                                Radius=Item.get("radius", 36),
                                FontSize=Item.get("font_size", 18),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Elb, Flex)
                        elif IType == "indicator":
                            IndMap = {
                                "pill": LCARSIndicator.Pill,
                                "pill_half": LCARSIndicator.PillHalf,
                                "bar": LCARSIndicator.Rect,
                                "rect": LCARSIndicator.Rect,
                            }
                            IndTypeEnum = IndMap.get(Item.get("indicator_type", "pill_half"), LCARSIndicator.PillHalf)
                            Ind = LCARSIndicator(
                                Text=Item.get("text", ""),
                                IndicatorType=IndTypeEnum,
                                Direction=Item.get("direction", 0),
                                Height=Item.get("height", 34),
                                Width=Item.get("width", 140),
                                FontSize=Item.get("font_size", 16),
                                Parent=RowSeg.Widget,
                            )
                            RowSeg.Add(RL, Ind, Flex)
                        elif IType == "datablock":
                            DB = DataBlock(
                                Item.get("title", ""),
                                Item.get("data", {}),
                                RowSeg.Widget,
                            )
                            RowSeg.Add(RL, DB, Flex)
                    SecPanel.Add(SecVL, RowSeg)

            RootPanel.Add(RootLayout, SecPanel)
        return RootPanel


# =====================================================================
# ЕКСПОРТНІ СИНОНІМИ ТА СИМВОЛИ
# =====================================================================
Button = LCARSButton
Label = LCARSLabel
Indicator = LCARSIndicator
Elbow = LCARSElbow
Bar = LCARSBar
Pill = LCARSButton
Frame = Panel
LCARSPadd = PADD
LCARSScreen = Screen
LCARSSegment = Segment
LCARSInput = LCARSButton
LCARSProgramPanel = Panel
LCARSWaveform = ScanningBar

__all__ = [
    "Element",
    "PADD",
    "Screen",
    "Display",
    "Panel",
    "Segment",
    "Header",
    "HeaderFrame",
    "Footer",
    "Sidebar",
    "Menu",
    "Toolbar",
    "StatusLine",
    "Confirmation",
    "Stasis",
    "AccessCode",
    "Access",
    "CoupledBlock",
    "Coupled",
    "TelemetryBlock",
    "Telemetry",
    "Bracket",
    "FrameBracket",
    "DataBlock",
    "StatBar",
    "ScanningBar",
    "ButtonGroup",
    "ChipInterfaceBuilder",
    "Button",
    "Label",
    "Indicator",
    "Elbow",
    "Bar",
    "Pill",
    "Frame",
    "LCARSButton",
    "LCARSLabel",
    "LCARSIndicator",
    "LCARSElbow",
    "LCARSBar",
    "LCARSPadd",
    "LCARSScreen",
    "LCARSSegment",
    "LCARSInput",
    "LCARSProgramPanel",
    "LCARSWaveform",
    "Primitive",
    "SetStyle",
]
