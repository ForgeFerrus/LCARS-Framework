"""
LCARS PROGRAMS PANEL - SYSTEM APPLICATION LAUNCHER
SYSTEM MODULE: UI-PRG-25
Titanium CamelCase / Zero-Except / No bare-Qt rules.
"""

import subprocess
import sys
import os
from pathlib import Path

from lcars.base.interface import Segment
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar


class ProgramsPanel(Segment):
    """
    Titanium Application Launcher Panel.
    Lists all known programs that can be embedded into the LCARS Desktop.
    """

    Programs = [
        ("FILE MANAGER",    "STORAGE",     0),
        ("TERMINAL",        "CONSOLE",     1),
        ("CODE IDE",        "IDE",         2),
        ("SCIENCE LAB",     "SCIENCE",     3),
        ("ENGINEERING",     "ENGINEERING", 4),
        ("DATABASE",        "DATABASE",    5),
        ("COMMUNICATIONS",  "COMM",        6),
        ("NAVIGATION",      "NAV",         7),
        ("TACTICAL",        "TACTICAL",    0),
        ("MEDICAL",         "MEDICAL",     1),
        ("LIBRARY",         "LIBRARY",     2),
        ("AI TERMINAL",     "AGENT",       3),
        ("SYSTEM ACCESS",   "SYSTEM",      4),
        ("CONFIGURATION",   "CONFIG",      5),
        ("SUPPORT",         "SUPPORT",     6),
        ("DIAGNOSTICS",     "DIAG",        7),
    ]

    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.widget.setStyleSheet("background-color: #000000;")
        self.Build()

    def Build(self):
        RootLayout = self.Vertical(15, 15, 15, 15, 10)

        # --- HEADER ---
        HeaderRow = Segment(Parent=self.widget)
        HeaderLayout = LCARS.Horizontal(HeaderRow.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(8)

        Elbow = LCARSElbow(
            Direction="top-left",
            Color=Palette.Buttons[0],
            Parent=HeaderRow.widget,
        )
        Elbow.widget.setFixedSize(220, 90)
        HeaderLayout.addWidget(Elbow.widget)

        TitleContainer = Segment(Parent=HeaderRow.widget)
        TitleLayout = LCARS.Vertical(TitleContainer.widget)
        TitleLayout.setContentsMargins(0, 0, 0, 0)
        TitleLayout.setSpacing(4)

        Title = LCARSLabel(
            "APPLICATION LIBRARY",
            Color=Palette.Buttons[1],
            FontSize=28,
            Parent=TitleContainer.widget,
        )
        TitleLayout.addWidget(Title.widget)

        Sub = LCARSLabel(
            "LCARS TITAN v9.0  //  AUTHORIZED ACCESS",
            Color=Palette.Buttons[3],
            FontSize=16,
            Parent=TitleContainer.widget,
        )
        TitleLayout.addWidget(Sub.widget)
        HeaderLayout.addWidget(TitleContainer.widget, 1)

        AccentBar = LCARSBar(
            Type="rect-right",
            Color=Palette.Buttons[2],
            Width=60,
            Height=90,
            Parent=HeaderRow.widget,
        )
        AccentBar.widget.setFixedWidth(60)
        AccentBar.widget.setFixedHeight(90)
        HeaderLayout.addWidget(AccentBar.widget)

        RootLayout.addWidget(HeaderRow.widget)

        # --- SEPARATOR ---
        Sep = LCARSBar(Type="bar", Color=Palette.Buttons[0], Height=6, Parent=self.widget)
        Sep.widget.setFixedHeight(6)
        RootLayout.addWidget(Sep.widget)

        # --- GRID ---
        GridContainer = Segment(Parent=self.widget)
        GridLayout = LCARS.Grid(GridContainer.widget)
        GridLayout.setContentsMargins(10, 10, 10, 10)
        GridLayout.setSpacing(12)

        Columns = 4
        for Idx, (Name, Target, ColorIdx) in enumerate(self.Programs):
            Color = Palette.Buttons[ColorIdx % len(Palette.Buttons)]
            Btn = LCARSButton(
                Text=Name,
                Type="rect",
                Color=Color,
                Parent=GridContainer.widget,
                Height=70,
                FontSize=16,
            )
            Row, Col = divmod(Idx, Columns)
            GridLayout.addWidget(Btn.widget, Row, Col)
            Btn.clicked.connect(self.MakeLauncher(Target))

        RootLayout.addWidget(GridContainer.widget, 1)

    def MakeLauncher(self, Target):
        def Launch():
            if self.DesktopNode and hasattr(self.DesktopNode, "Select"):
                self.DesktopNode.Select(Target)
        return Launch
