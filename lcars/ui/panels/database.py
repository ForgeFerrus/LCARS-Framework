import os
import subprocess
from pathlib import Path

from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow
from lcars.base.interface import Segment, DataBlock
from lcars.base.default import Palette
from lcars.base.type import LCARS

class DatabasePanel(Segment):
    def __init__(self, DesktopNodeRef=None, ParentNode=None, Era=None, Faction=None):
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.widget.setStyleSheet("background-color: #000000;")
        self.Build()

    def Build(self):
        MainLayout = LCARS.Horizontal(self.widget)
        MainLayout.setContentsMargins(10, 10, 10, 10)
        MainLayout.setSpacing(20)

        # ЛІВА КОЛОНКА (Доступ до даних та папок)
        LeftCol = Segment(Parent=self.widget)
        LeftCol.widget.setFixedWidth(280)
        LeftLayout = LCARS.Vertical(LeftCol.widget)
        LeftLayout.setSpacing(6)

        ElbowLeft = LCARSElbow("top-left", Color=Palette.Buttons[0], Parent=LeftCol.widget)
        ElbowLeft.widget.setFixedHeight(60)
        LeftLayout.addWidget(ElbowLeft.widget)

        user_dir = str(Path.home())
        paths = {
            "DOCS": os.path.join(user_dir, "Documents"),
            "PICTURES": os.path.join(user_dir, "Pictures"),
            "MUSIC": os.path.join(user_dir, "Music"),
            "VIDEOS": os.path.join(user_dir, "Videos"),
            "DOWNL": os.path.join(user_dir, "Downloads"),
        }

        left_buttons = [
            ("USER DATA", None, Palette.Buttons[0]),
            ("DOCS", lambda: os.startfile(paths["DOCS"]), Palette.Buttons[1]),
            ("PICTURES", lambda: os.startfile(paths["PICTURES"]), Palette.Buttons[1]),
            ("MUSIC", lambda: os.startfile(paths["MUSIC"]), Palette.Buttons[1]),
            ("VIDEOS", lambda: os.startfile(paths["VIDEOS"]), Palette.Buttons[1]),
            ("DOWNL", lambda: os.startfile(paths["DOWNL"]), Palette.Buttons[1]),
            ("COMPUTER", lambda: os.startfile("explorer.exe"), Palette.Buttons[2]),
            ("CONTROLS", lambda: os.startfile("control.exe"), Palette.Buttons[2]),
            ("SYSTEM", lambda: os.startfile("ms-settings:"), Palette.Buttons[3]),
            ("TASK MGR", lambda: os.startfile("taskmgr.exe"), Palette.Buttons[3])
        ]

        for text, handler, color in left_buttons:
            btn = LCARSButton(text, Type="soft-left", Color=color, Parent=LeftCol.widget)
            btn.widget.setFixedHeight(45)
            if handler:
                btn.clicked.connect(handler)
            LeftLayout.addWidget(btn.widget)
            
        LeftLayout.addStretch()
        MainLayout.addWidget(LeftCol.widget)

        # ЦЕНТРАЛЬНА КОЛОНКА (Інформація)
        CenterCol = Segment(Parent=self.widget)
        CenterLayout = LCARS.Vertical(CenterCol.widget)
        CenterLayout.setSpacing(10)

        TitleLayout = LCARS.Horizontal()
        Title1 = LCARSLabel("LIBRARY COMPUTER ACCESS AND RETRIEVAL SYSTEM", Color=Palette.Buttons[1], FontSize=22, Parent=CenterCol.widget)
        TitleLayout.addStretch()
        TitleLayout.addWidget(Title1.widget)
        CenterLayout.addLayout(TitleLayout)

        QuickLinks = LCARS.Horizontal()
        QuickLinks.addStretch()
        BtnGoogle = LCARSButton("Google", Color=Palette.Buttons[2], Parent=CenterCol.widget)
        BtnYouTube = LCARSButton("YouTube", Color=Palette.Buttons[2], Parent=CenterCol.widget)
        BtnGoogle.clicked.connect(lambda: os.startfile("https://google.com"))
        BtnYouTube.clicked.connect(lambda: os.startfile("https://youtube.com"))
        QuickLinks.addWidget(BtnGoogle.widget)
        QuickLinks.addWidget(BtnYouTube.widget)
        CenterLayout.addLayout(QuickLinks)

        CenterLayout.addStretch()
        
        LogoLbl = LCARSLabel("THE LCARS COMPUTER NETWORK\nAUTHORIZED ACCESS ONLY", Color=Palette.Buttons[0], FontSize=26, Parent=CenterCol.widget)
        AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
        if AlignmentFlag:
            LogoLbl.widget.setAlignment(AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(LogoLbl.widget)

        CenterLayout.addStretch()
        MainLayout.addWidget(CenterCol.widget, 1)

        # ПРАВА КОЛОНКА (Media Player & Menu)
        RightCol = Segment(Parent=self.widget)
        RightCol.widget.setFixedWidth(350)
        RightLayout = LCARS.Vertical(RightCol.widget)
        RightLayout.setSpacing(20)

        MediaPanel = Segment(Parent=RightCol.widget)
        MediaLayout = LCARS.Vertical(MediaPanel.widget)
        MediaLayout.setSpacing(6)
        
        MediaTitle = LCARSLabel("LCARS MEDIA PLAYER", Color=Palette.Buttons[3], FontSize=16, Parent=MediaPanel.widget)
        if AlignmentFlag:
            MediaTitle.widget.setAlignment(AlignmentFlag.AlignRight)
        MediaLayout.addWidget(MediaTitle.widget)

        media_buttons = [
            ("PLAY / PAUSE", self.MediaPlayPause),
            ("STOP", None),
            ("NEXT", self.MediaNext),
            ("PREVIOUS", self.MediaPrev),
            ("VOL UP", self.MediaVolUp),
            ("VOL DOWN", self.MediaVolDown)
        ]

        for text, handler in media_buttons:
            btn = LCARSButton(text, Type="soft-right", Color=Palette.Buttons[4], Parent=MediaPanel.widget)
            btn.widget.setFixedHeight(40)
            if handler:
                btn.clicked.connect(handler)
            MediaLayout.addWidget(btn.widget)
            
        RightLayout.addWidget(MediaPanel.widget)

        AddPanel = Segment(Parent=RightCol.widget)
        AddLayout = LCARS.Vertical(AddPanel.widget)
        AddLayout.setSpacing(6)
        
        AddTitle = LCARSLabel("LCARS ADDITIONAL MENU", Color=Palette.Buttons[3], FontSize=16, Parent=AddPanel.widget)
        if AlignmentFlag:
            AddTitle.widget.setAlignment(AlignmentFlag.AlignRight)
        AddLayout.addWidget(AddTitle.widget)

        add_buttons = [
            ("POWER CONTROLS", lambda: os.startfile("powercfg.cpl")),
            ("CALCULATOR", lambda: os.startfile("calc.exe")),
            ("WEATHER", lambda: os.startfile("ms-weather:")),
            ("STEAM", lambda: os.startfile("steam://open/main")),
            ("SLIDESHOW", None)
        ]

        for text, handler in add_buttons:
            btn = LCARSButton(text, Type="soft-right", Color=Palette.Buttons[2], Parent=AddPanel.widget)
            btn.widget.setFixedHeight(40)
            if handler:
                btn.clicked.connect(handler)
            AddLayout.addWidget(btn.widget)
            
        RightLayout.addWidget(AddPanel.widget)
        RightLayout.addStretch()

        MainLayout.addWidget(RightCol.widget)

    def MediaPlayPause(self):
        self.SendKey(0xB3)

    def MediaNext(self):
        self.SendKey(0xB0)

    def MediaPrev(self):
        self.SendKey(0xB1)

    def MediaVolUp(self):
        self.SendKey(0xAF)

    def MediaVolDown(self):
        self.SendKey(0xAE)

    def SendKey(self, keycode):
        ps_api = f"""
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class KeySender {{
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
}}
"@
[KeySender]::keybd_event({keycode}, 0, 0, 0)
[KeySender]::keybd_event({keycode}, 0, 2, 0)
"""
        import threading
        def run():
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_api], creationflags=subprocess.CREATE_NO_WINDOW)
        threading.Thread(target=run).start()
