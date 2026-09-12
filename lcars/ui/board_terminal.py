# ◤ LCARS BOARD COMPUTER TERMINAL 🖖
# Єдиний автономний термінал бортового комп'ютера на базі LCARSUnifiedTerminal
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

from lcars.base.interface import PADD
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.ui.terminal import LCARSUnifiedTerminal


class LCARSBoardTerminal(PADD):
    def __init__(self, parent=None, lite=False, ParentNode=None, BoardComputer=None, **kwargs):
        ActualParent = ParentNode or parent or kwargs.get("Parent")
        kwargs.pop("ParentNode", None)
        kwargs.pop("Parent", None)
        kwargs.pop("parent", None)

        TitleVal = kwargs.pop("Title", "LCARS BOARD COMPUTER TERMINAL")
        ColorVal = kwargs.pop("color", Palette.Buttons[0])
        WidthVal = kwargs.pop("width", 1400)
        HeightVal = kwargs.pop("height", 900)
        MinWidthVal = kwargs.pop("minWidth", 1000)
        MinHeightVal = kwargs.pop("minHeight", 600)

        super().__init__(
            Parent=ActualParent,
            Title=TitleVal,
            color=ColorVal,
            width=WidthVal,
            height=HeightVal,
            minWidth=MinWidthVal,
            minHeight=MinHeightVal,
            **kwargs
        )

        Content = self.Items.get("Content")
        ParentWidget = Content.widget if Content else self.widget
        self.UnifiedTerminal = LCARSUnifiedTerminal(
            Parent=ParentWidget,
            BoardComputer=BoardComputer,
            Compact=False,
            SplitOption=True,
            Title="BOARD COMPUTER COMMAND STATION // ODN 5.0"
        )

    def Append(self, text: str):
        if hasattr(self, "UnifiedTerminal"):
            self.UnifiedTerminal.Append(text)

    def Clear(self):
        if hasattr(self, "UnifiedTerminal"):
            self.UnifiedTerminal.Clear()


__all__ = ["LCARSBoardTerminal"]

