# LCARS MENU PANEL - MAIN NAVIGATION
# SYSTEM MODULE: UI-MENU-25
# PROTOCOL: LCARS / ODYSSEY CORE
# DESCRIPTION: Головне меню для навігації по панелях системи.

import sys
from lcars.core.kernel import CreateApplication, ExistingApplication
from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from lcars.base.component import Graphic, LCARSButton, LCARSLabel, PillButton, LCARSElbow
from lcars.base.default import RandomButtonColor, FontSetup
from lcars.base.type import Primitives

FontSetup()

class MenuPanel(Graphic):
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.active_panel = 0
        self.setStyleSheet("background-color: #000000;")
        self.CreateComponents()
    
    def CreateComponents(self):
        Root = Primitives.VBox(self)
        Root.setContentsMargins(20, 20, 20, 20)
        Root.setSpacing(16)

        # === HEADER ===
        Header = Primitives.HBox()
        Header.setSpacing(10)
        HLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_left", Thickness=40, Radius=40)
        HLElbow.setFixedSize(80, 80)
        Header.addWidget(HLElbow)
        HLPill = PillButton(Color=RandomButtonColor())
        HLPill.setFixedSize(12, 40)
        Header.addWidget(HLPill)
        self.TitleLbl = LCARSLabel("◢ MAIN MENU", Color=RandomButtonColor(), FontSize=24)
        self.TitleLbl.setFixedHeight(40)
        Header.addWidget(self.TitleLbl.Widget)
        Header.addStretch()
        HRPill = PillButton(Color=RandomButtonColor())
        HRPill.setFixedSize(12, 40)
        Header.addWidget(HRPill)
        HRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_right", Thickness=40, Radius=40)
        HRElbow.setFixedSize(80, 80)
        Header.addWidget(HRElbow)
        Root.addLayout(Header)
        Root.addSpacing(20)

        # === BODY: 3 частини ===
        Body = Primitives.HBox()
        Body.setSpacing(16)

        # --- ЛІВА ЧАСТИНА: МЕНЮ ---
        LeftPanel = Primitives.VBox()
        LeftPanel.setContentsMargins(0, 0, 0, 0)
        
        MenuHeader = Primitives.HBox()
        MenuHeader.setSpacing(10)
        MenuPill = PillButton(Color="#6699CC")
        MenuPill.setFixedSize(8, 32)
        MenuHeader.addWidget(MenuPill)
        MenuLabel = LCARSLabel("◤ NAVIGATION", Color="#6699CC", FontSize=14)
        MenuHeader.addWidget(MenuLabel)
        LeftPanel.addLayout(MenuHeader)
        
        Sep1 = PillButton(Color="#333333")
        Sep1.setFixedHeight(3)
        LeftPanel.addWidget(Sep1)
        LeftPanel.addSpacing(8)

        # Пункти меню
        self.MenuItems = [
            ("SYSTEM ACCESS", "#6699CC"),
            ("PROGRAMS", "#99CCFF"),
            ("NAVIGATION", "#66CC66"),
            ("COMMUNICATION", "#CC9966"),
            ("MEDICAL", "#FF9900"),
            ("SCIENCE", "#FF6600"),
            ("TACTICAL", "#FF3300"),
            ("SETTINGS", "#9966CC"),
        ]
        
        self.MenuButtons = []
        for i, (Text, Color) in enumerate(self.MenuItems):
            Btn = LCARSButton(Text, Color=Color)
            Btn.setFixedHeight(44)
            Btn.Clicked = lambda *args, idx=i: self.SwitchPanel(idx)
            LeftPanel.addWidget(Btn)
            self.MenuButtons.append(Btn)
        
        LeftPanel.addStretch()
        
        LogoutBtn = LCARSButton("LOGOUT", Color="#CC0000")
        LogoutBtn.setFixedHeight(50)
        LeftPanel.addWidget(LogoutBtn)
        
        Body.addLayout(LeftPanel)

        # --- СЕРЕДИНА: ПОКАЗ ПАНЕЛІ ---
        CenterPanel = Primitives.VBox()
        
        CenterHeader = Primitives.HBox()
        CenterHeaderPill = PillButton(Color="#99CCFF")
        CenterHeaderPill.setFixedSize(8, 32)
        CenterHeader.addWidget(CenterHeaderPill)
        self.PanelTitle = LCARSLabel("◤ SYSTEM ACCESS", Color="#99CCFF", FontSize=16)
        CenterHeader.addWidget(self.PanelTitle.Widget)
        CenterPanel.addLayout(CenterHeader)
        
        Sep2 = PillButton(Color="#333333")
        Sep2.setFixedHeight(3)
        CenterPanel.addWidget(Sep2)
        CenterPanel.addSpacing(8)
        
        # Стек панелей
        self.PanelStack = Primitives.VBox()
        self.PanelFrames = []
        
        for Text, Color in self.MenuItems:
            Frame = Graphic()
            Frame.setStyleSheet(f"background-color: #0A0A0A; border: 2px solid {Color}; border-radius: 10px;")
            FrameLayout = Primitives.VBox(Frame)
            FrameLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            Label = LCARSLabel(f"◤ {Text}\n\nACTIVE PANEL", Color=Color, FontSize=20)
            Label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            FrameLayout.addWidget(Label)
            self.PanelFrames.append(Frame)
            self.PanelStack.addWidget(Frame)
        
        for i, Frame in enumerate(self.PanelFrames):
            if i != 0:
                Frame.hide()
        
        CenterPanel.addLayout(self.PanelStack)
        
        Body.addLayout(CenterPanel, 1)

        # --- ПРАВА ЧАСТИНА: СТАТУС ---
        RightPanel = Primitives.VBox()
        RightPanel.setContentsMargins(0, 0, 0, 0)
        RightPanel.setFixedWidth(200)
        
        RightHeader = Primitives.HBox()
        RightHeader.setSpacing(10)
        RightHeaderPill = PillButton(Color="#FF9900")
        RightHeaderPill.setFixedSize(8, 32)
        RightHeader.addWidget(RightHeaderPill)
        RightHeaderLabel = LCARSLabel("◤ SYSTEM STATUS", Color="#FF9900", FontSize=14)
        RightHeader.addWidget(RightHeaderLabel)
        RightPanel.addLayout(RightHeader)
        
        Sep3 = PillButton(Color="#333333")
        Sep3.setFixedHeight(3)
        RightPanel.addWidget(Sep3)
        RightPanel.addSpacing(8)
        
        # Статусні елементи
        StatusItems = [
            ("CORE", "ONLINE", "#00FF00"),
            ("MEMORY", "NOMINAL", "#FFCC00"),
            ("NETWORK", "ACTIVE", "#66CCFF"),
            ("POWER", "100%", "#FF9900"),
        ]
        
        for Title, Value, Color in StatusItems:
            Box = Graphic()
            Box.setStyleSheet(f"background-color: #111111; border-left: 5px solid {Color}; border-radius: 4px;")
            BoxLayout = Primitives.VBox(Box)
            TitleLbl = LCARSLabel(Title, Color="#FFFFFF", FontSize=10)
            ValueLbl = LCARSLabel(Value, Color=Color, FontSize=12)
            BoxLayout.addWidget(TitleLbl)
            BoxLayout.addWidget(ValueLbl)
            RightPanel.addWidget(Box)
        
        RightPanel.addStretch()
        
        Body.addLayout(RightPanel)

        Root.addLayout(Body)
        
        self.HighlightMenu(0)
    
    def SwitchPanel(self, Index):
        self.active_panel = Index
        for i, Frame in enumerate(self.PanelFrames):
            if i == Index:
                Frame.show()
            else:
                Frame.hide()
        self.PanelTitle.setText(f"◤ {self.MenuItems[Index][0]}")
        self.HighlightMenu(Index)
    
    def HighlightMenu(self, Index):
        for i, Btn in enumerate(self.MenuButtons):
            if i == Index:
                Btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.MenuItems[i][1]};
                        color: #000000;
                        border: none;
                        border-top-right-radius: 12px;
                        border-bottom-right-radius: 12px;
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        text-align: left;
                        padding-left: 12px;
                        font-weight: bold;
                        font-family: 'LCARS';
                        font-size: 12px;
                    }}
                """)
            else:
                Btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {self.MenuItems[i][1]};
                        color: #000000;
                        border: none;
                        border-top-right-radius: 12px;
                        border-bottom-right-radius: 12px;
                        border-top-left-radius: 0px;
                        border-bottom-left-radius: 0px;
                        text-align: left;
                        padding-left: 12px;
                        font-weight: normal;
                        font-family: 'LCARS';
                        font-size: 12px;
                    }}
                    QPushButton:hover {{
                        background-color: #FFFFFF;
                    }}
                """)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = CreateApplication(sys.argv)
    menu = MenuPanel()
    menu.setGeometry(100, 100, 1400, 800)
    menu.show()
    sys.exit(app.exec())
