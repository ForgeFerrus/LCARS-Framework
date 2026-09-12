from __future__ import annotations

# Titanium Bridge Migration: from typing import Any

from lcars.base.component import LCARSBar, LCARSButton, LCARSLabel
from lcars.base.default import Palette, SetStyle
from lcars.base.interface import Segment
from lcars.base.type import LCARS
from lcars.base.signal import Transmission
from lcars.system.bios import BIOS


class LCARSBiosScreen(Segment):
    def __init__(self, Parent=None, Core: BIOS | None = None):
        super().__init__(Parent=Parent)
        self.Core = Core or BIOS()
        self.ExitRequested = Transmission(dict)
        self.BuildUi()
        self.BuildSettings()
        self.Refresh()

    def BuildUi(self):
        SetStyle(self.widget, "background-color: #000000; border: none;")
        Layout = LCARS.VBox(self.widget)
        Layout.setContentsMargins(28, 24, 28, 24)
        Layout.setSpacing(14)

        Header = LCARS.HBox()
        Header.setSpacing(10)
        self.HeaderBar = LCARSBar(Type="bar", Color=Palette.Buttons[1], Height=14, Parent=self.widget)
        self.Title = LCARSLabel(Text="BIOS SETUP SYSTEM CONTROL", Color=Palette.Buttons[2], FontSize=22, Parent=self.widget)
        self.ReturnButton = LCARSButton(Text="RETURN", Type="pill", Color=Palette.Buttons[0], Parent=self.widget, Width=160, Height=48, Sound="none")
        self.ReturnButton.clicked.connect(self.Return)
        Header.addWidget(self.Title.widget)
        Header.addWidget(self.HeaderBar.widget, 1)
        Header.addWidget(self.ReturnButton.widget)
        Layout.addLayout(Header)

        Body = LCARS.HBox()
        Body.setSpacing(18)

        Left = LCARS.VBox()
        Left.setSpacing(10)
        self.ConfigButton = LCARSButton(Text="CONFIG", Type="pill", Color=Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00', Parent=self.widget, Width=210, Height=54)
        self.PostButton = LCARSButton(Text="RUN POST", Type="pill", Color=Palette.Buttons[3], Parent=self.widget, Width=210, Height=54)
        self.HealthButton = LCARSButton(Text="SYSTEM HEALTH", Type="pill", Color=Palette.Buttons[1], Parent=self.widget, Width=210, Height=54)
        self.SaveButton = LCARSButton(Text="SAVE EXIT", Type="pill", Color=Palette.Buttons[4], Parent=self.widget, Width=210, Height=54)
        self.BootButton = LCARSButton(Text="BOOT", Type="pill", Color=Palette.Buttons[2], Parent=self.widget, Width=210, Height=54)
        
        self.ConfigButton.clicked.connect(lambda: self.MainChamber.setCurrentIndex(1))
        self.PostButton.clicked.connect(lambda: [self.Refresh(), self.MainChamber.setCurrentIndex(0)])
        self.HealthButton.clicked.connect(lambda: self.MainChamber.setCurrentIndex(2))
        self.SaveButton.clicked.connect(self.SaveAndReturn)
        self.BootButton.clicked.connect(self.SaveAndReturn)
        
        Left.addWidget(self.ConfigButton.widget)
        Left.addWidget(self.PostButton.widget)
        Left.addWidget(self.HealthButton.widget)
        Left.addWidget(self.SaveButton.widget)
        Left.addWidget(self.BootButton.widget)
        Left.addStretch()
        Body.addLayout(Left)

        self.MainChamber = LCARS.Chamber(self.widget)
        
        # Page 0: Console
        self.Console = LCARSLabel(Text="", Type="console", Color=Palette.Buttons[1], Align="left", FontSize=18, Parent=self.widget)
        ConsoleWidget = self.Console.widget
        if hasattr(ConsoleWidget, "setWordWrap"):
            ConsoleWidget.setWordWrap(True)
        self.MainChamber.addWidget(ConsoleWidget)
        
        # Page 1: Settings
        self.SettingsScroll = LCARS.Buffer(self.widget)
        self.SettingsScroll.setWidgetResizable(True)
        SetStyle(self.SettingsScroll, "background-color: transparent; border: none;")
        self.MainChamber.addWidget(self.SettingsScroll)
        
        # Page 2: System Health (Visual UEFI)
        from lcars.ui.uefi import UEFI
        self.HealthPage = UEFI(Parent=self.widget)
        self.MainChamber.addWidget(self.HealthPage.widget)

        Footer = LCARS.HBox()
        Footer.setSpacing(10)
        self.Status = LCARSLabel(Text="BIOS READY", Color=Palette.Buttons[2], FontSize=16, Parent=self.widget)
        self.FooterBar = LCARSBar(Type="bar", Color=Palette.Buttons[1], Height=10, Parent=self.widget)
        Footer.addWidget(self.Status.widget)
        Footer.addWidget(self.FooterBar.widget, 1)
        Layout.addLayout(Footer)

    def BuildSettings(self):
        Container = LCARS.Segment()
        SetStyle(Container, "background-color: transparent; border: none;")
        Layout = LCARS.VBox(Container)
        Layout.setSpacing(15)
        
        Sections = {}
        for Key, Setting in self.Core.Settings.items():
            if Setting.Section not in Sections:
                Sections[Setting.Section] = []
            Sections[Setting.Section].append(Setting)
            
        for SectionName, SettingsList in Sections.items():
            HeaderRow = LCARS.HBox()
            HeaderBar = LCARSBar(Type="rect", Color=Palette.Buttons[0], Width=30, Height=30, Parent=Container)
            Title = LCARSLabel(Text=f"{SectionName}", Color=Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FF9900', FontSize=22, Parent=Container)
            HeaderRow.addWidget(HeaderBar.widget)
            HeaderRow.addWidget(Title.widget, 1)
            Layout.addLayout(HeaderRow)
            
            for Setting in SettingsList:
                Row = LCARS.HBox()
                Lbl = LCARSLabel(Text=f"{Setting.Name} :: {Setting.Description}", Color=Palette.Buttons[1], FontSize=16, Parent=Container)
                if hasattr(Lbl.widget, "setWordWrap"):
                    Lbl.widget.setWordWrap(True)
                
                ValText = str(Setting.Value)
                Btn = LCARSButton(Text=ValText, Color=Palette.Buttons[2], Type="pill", Parent=Container, Width=240, Height=45)
                
                def MakeClick(s, b):
                    def OnClick():
                        if not s.Options: return
                        if True:
                            idx = s.Options.index(s.Value)
                            idx = (idx + 1) % len(s.Options)
                        if False: # Removed except block
                            idx = 0
                        s.Value = s.Options[idx]
                        self.Core.Set(s.Name, s.Value)
                        b.SetText(str(s.Value))
                    return OnClick
                    
                Btn.clicked.connect(MakeClick(Setting, Btn))
                
                Row.addWidget(Lbl.widget, 1)
                Row.addWidget(Btn.widget)
                Layout.addLayout(Row)
                
            Layout.addSpacing(10)
                
        Layout.addStretch()
        self.SettingsScroll.setWidget(Container)

    def Refresh(self):
        Report = self.Core.RunPost()
        Lines = self.Core.LastReport.Lines() if hasattr(self.Core, "LastReport") and self.Core.LastReport else []
        self.Console.SetText("\n".join(Lines))
        self.Status.SetText("BIOS STATUS :: " + Report.Status)

    def SaveAndReturn(self):
        Payload = self.Core.Save()
        self.ExitRequested.Emit(Payload)

    def Return(self):
        self.ExitRequested.Emit(self.Core.ExportPayload() if hasattr(self.Core, "ExportPayload") else {})

__all__ = ["LCARSBiosScreen"]
