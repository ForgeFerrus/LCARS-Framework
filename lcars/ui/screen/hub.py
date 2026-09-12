from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSBar, LCARSIndicator
from lcars.base.interface import Screen, Segment, Panel
from lcars.core.signal import ODN
from lcars.ui.starship_node import StarshipNode
from lcars.ui.headquarters import HeadquartersNode

class LCARSNetworkHub(Screen):
    def BuildScreen(self):
        pass

    def __init__(self, parent=None):
        super().__init__(Parent=parent, Decorated=False)
        self.widget.setStyleSheet("background-color: black; border: none;")
        self.Build()

    def Build(self):
        Content = self.widget
        Layout = Content.layout()
        if Layout is None:
            Layout = LCARS.Vertical(Content)
        Layout.setContentsMargins(15, 15, 15, 15)
        Layout.setSpacing(10)

        # Header Row
        HeaderRow = Segment(Parent=Content)
        HeaderLayout = LCARS.Horizontal(HeaderRow.widget)
        HeaderLayout.setSpacing(10)
        
        Elbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=HeaderRow.widget)
        Elbow.widget.setFixedSize(140, 70)
        HeaderLayout.addWidget(Elbow.widget)
        
        TitleBar = LCARSBar(Type="rect", Color=Palette.Buttons[2], Parent=HeaderRow.widget)
        TitleLayout = LCARS.Horizontal(TitleBar.widget)
        TitleLayout.setContentsMargins(20, 0, 20, 0)
        TitleLabel = LCARSLabel(Text="GLOBAL NETWORK HUB", Color=Palette.Background, FontSize=24, Parent=TitleBar.widget)
        TitleLayout.addWidget(TitleLabel.widget)
        TitleLayout.addStretch(1)
        HeaderLayout.addWidget(TitleBar.widget, 1)
        
        StatusIndicator = LCARSIndicator(Text="UPLINK: ACTIVE", Type="rect-right", Color=Palette.Yellow[1], Parent=HeaderRow.widget)
        StatusIndicator.widget.setFixedSize(200, 70)
        HeaderLayout.addWidget(StatusIndicator.widget)
        
        Layout.addWidget(HeaderRow.widget)

        # Main Area with side menu
        MainRow = Segment(Parent=Content)
        MainLayout = LCARS.Horizontal(MainRow.widget)
        MainLayout.setSpacing(12)

        # Left Menu
        LeftMenu = Panel(Parent=MainRow.widget)
        LeftMenu.widget.setFixedWidth(180)
        LeftLayout = LCARS.Vertical(LeftMenu.widget)
        LeftLayout.setSpacing(6)
        
        for i, name in enumerate(["SCAN", "SYNC", "QUERY", "NODE LIST", "LOGS"]):
            btn = LCARSButton(Text=name, Type="soft-left", Color=Palette.Buttons[i % len(Palette.Buttons)], Parent=LeftMenu.widget)
            btn.widget.setFixedHeight(40)
            LeftLayout.addWidget(btn.widget)
        LeftLayout.addStretch(1)
        
        MainLayout.addWidget(LeftMenu.widget)

        # Central Stack
        self.MainStack = LCARS.Stacked(MainRow.widget)
        
        # Grid of Nodes
        self.NodesGrid = Segment(Parent=MainRow.widget)
        GridLayout = LCARS.Grid(self.NodesGrid.widget)
        GridLayout.setSpacing(15)
        
        Nodes = [
            ("STARSHIP NCC-1701-E", Palette.Buttons[0], self.OpenStarship),
            ("FEDERATION HQ", Palette.Buttons[1], self.OpenHQ),
            ("STARBASE 74", Palette.Buttons[2], lambda: self.ConnectToNode("STARBASE 74")),
            ("VULCAN ACADEMY", Palette.Yellow[2], lambda: self.ConnectToNode("VULCAN ACADEMY")),
            ("ARCHIVE CORE", Palette.Buttons[1], lambda: self.ConnectToNode("ARCHIVE CORE")),
            ("SCIENCE STATION", Palette.Buttons[0], lambda: self.ConnectToNode("SCIENCE STATION")),
        ]
        
        for i, (name, color, callback) in enumerate(Nodes):
            btn = LCARSButton(Text=name, Type="rect", Color=color, Parent=self.NodesGrid.widget)
            btn.widget.setMinimumHeight(120)
            btn.Clicked.Connect(callback)
            GridLayout.addWidget(btn.widget, i // 3, i % 3)
            
        self.MainStack.addWidget(self.NodesGrid.widget)
        
        # Starship Node View
        self.StarshipView = StarshipNode(parent=Content)
        self.MainStack.addWidget(self.StarshipView)
        
        # HQ Node View
        self.HQView = HeadquartersNode(parent=Content)
        self.MainStack.addWidget(self.HQView)
        
        # Loading/Connecting View
        self.LoadingView = Panel(Parent=Content)
        self.LoadingLayout = LCARS.Vertical(self.LoadingView.widget)
        self.LoadingLayout.setContentsMargins(50, 50, 50, 50)
        self.LoadingText = LCARSLabel(Text="ESTABLISHING LINK...", Color=Palette.Yellow[1], FontSize=22, Parent=self.LoadingView.widget)
        self.LoadingLayout.addStretch(1)
        self.LoadingLayout.addWidget(self.LoadingText.widget, 0, LCARS.Protocol.AlignmentFlag.AlignCenter if hasattr(LCARS.Protocol, "AlignmentFlag") else 0)
        self.LoadingScan = LCARSBar(Type="scanning", Color=Palette.Buttons[1], Parent=self.LoadingView.widget, Height=20)
        self.LoadingLayout.addWidget(self.LoadingScan.widget)
        self.LoadingLayout.addStretch(1)
        self.MainStack.addWidget(self.LoadingView.widget)

        MainLayout.addWidget(self.MainStack, 1)
        Layout.addWidget(MainRow.widget, 1)

        # Footer Row
        FooterRow = Segment(Parent=Content)
        FooterLayout = LCARS.Horizontal(FooterRow.widget)
        FooterLayout.setSpacing(10)
        
        BackBtn = LCARSButton(Text="BACK TO HUB", Color=Palette.Buttons[1], Parent=FooterRow.widget)
        BackBtn.widget.setFixedSize(200, 45)
        BackBtn.Clicked.Connect(self.ShowHub)
        FooterLayout.addWidget(BackBtn.widget)
        
        FooterLayout.addStretch(1)
        
        ProceedBtn = LCARSButton(Text="PROCEED TO DESKTOP", Color=Palette.Buttons[2], Parent=FooterRow.widget)
        ProceedBtn.widget.setFixedSize(250, 45)
        ProceedBtn.Clicked.Connect(lambda: ODN.Emit("System.Phase.Desktop"))
        FooterLayout.addWidget(ProceedBtn.widget)
        
        Layout.addWidget(FooterRow.widget)

    def ShowHub(self):
        self.MainStack.setCurrentWidget(self.NodesGrid.widget)

    def ConnectToNode(self, NodeName, FinalCallback=None):
        self.LoadingText.SetText(f"ESTABLISHING SECURE LINK TO {NodeName}...")
        self.MainStack.setCurrentWidget(self.LoadingView.widget)
        
        def finish():
            if FinalCallback:
                FinalCallback()
            else:
                self.NotImplemented(NodeName)
                self.ShowHub()
                
        LCARS.Timer.singleShot(1500, finish)

    def OpenStarship(self):
        self.ConnectToNode("STARSHIP NCC-1701-E", lambda: self.MainStack.setCurrentWidget(self.StarshipView))

    def OpenHQ(self):
        self.ConnectToNode("FEDERATION HQ", lambda: self.MainStack.setCurrentWidget(self.HQView))

    def NotImplemented(self, node):
        print(f"Node {node} connection sequence initiated...")
