# ◤ TITANIUM NAVIGATION PANEL
# Файл: lcars/ui/panels/navigation.py

from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow
from lcars.base.interface import Segment
from lcars.base.default import Palette
from lcars.base.type import LCARS

class NavigationPanel(Segment):
    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        self.widget.setStyleSheet("background-color: #000000;")
        
        self.Astrometrics = None
        if self.DesktopNode and hasattr(self.DesktopNode, 'System'):
            self.Astrometrics = self.DesktopNode.System.Get("astrometrics")
            
        self.Build()

    def Build(self):
        RootHBox = LCARS.Horizontal(self.widget)
        RootHBox.setContentsMargins(10, 10, 10, 10)
        RootHBox.setSpacing(16)

        # LEFT NAV
        NavBox = LCARS.Vertical()
        NavBox.setSpacing(8)
        
        ElbowTop = LCARSElbow(Color=Palette.Buttons[0], Type="top-left", Width=180, Height=100, Parent=self.widget)
        NavBox.addWidget(ElbowTop.widget)
        
        NavTitle = LCARSLabel("NAVIGATION", Color=Palette.Buttons[0], FontSize=18, Parent=self.widget)
        NavTitle.widget.setAlignment(LCARS.Protocol.AlignmentFlag.AlignCenter)
        NavBox.addWidget(NavTitle.widget)
        
        self.BtnScan = LCARSButton("SECTOR SCAN", Color=Palette.Buttons[1], Type="soft", Width=180, Height=50, Parent=self.widget)
        self.BtnScan.clicked.connect(self.OnSectorScan)
        NavBox.addWidget(self.BtnScan.widget)

        self.BtnEngage = LCARSButton("ENGAGE", Color=Palette.Text[1], Type="soft", Width=180, Height=50, Parent=self.widget)
        NavBox.addWidget(self.BtnEngage.widget)
        
        NavBox.addStretch(1)
        RootHBox.addLayout(NavBox)

        # CENTER RADAR
        MainAreaBox = LCARS.Vertical()
        HeadBar = LCARSBar(Color=Palette.Buttons[0], Height=20, Parent=self.widget)
        MainAreaBox.addWidget(HeadBar.widget)
        
        Title = LCARSLabel("ASTROMETRICS RADAR (Z=50)", Color="#FFFFFF", FontSize=22, Parent=self.widget)
        MainAreaBox.addWidget(Title.widget)
        
        # 10x10 Grid representation for radar
        self.RadarGrid = LCARS.Grid()
        self.RadarGrid.setSpacing(1)
        MainAreaBox.addLayout(self.RadarGrid, 1)
        
        self.DrawRadar()
        
        RootHBox.addLayout(MainAreaBox, 1)

    def DrawRadar(self):
        # Clear
        for i in reversed(range(self.RadarGrid.count())):
            item = self.RadarGrid.itemAt(i)
            if item.widget(): item.widget().deleteLater()
            
        if not self.Astrometrics:
            Lbl = LCARSLabel("ASTROMETRICS SENSOR OFFLINE", Color=Palette.Text[1], FontSize=20, Parent=self.widget)
            self.RadarGrid.addWidget(Lbl.widget, 0, 0)
            return
            
        # Get slice
        slice_data = self.Astrometrics.GetMapSlice(50)
        
        # Draw 10x10 grid of 10x10 blocks for visual radar
        for x in range(10):
            for y in range(10):
                Block = LCARS.Panel()
                Block.setStyleSheet("background-color: #001133; border: 1px solid #003366;")
                Block.setFixedSize(50, 50)
                
                # Check if there is anything in this 10x10 chunk
                has_entity = False
                entity_name = ""
                for cx in range(x*10, (x+1)*10):
                    for cy in range(y*10, (y+1)*10):
                        if (cx, cy) in slice_data:
                            has_entity = True
                            entity_name = slice_data[(cx,cy)].get("name", "Unknown")
                            break
                    if has_entity: break
                
                if has_entity:
                    Block.setStyleSheet("background-color: #FFCC00; border-radius: 25px;")
                    Lbl = LCARSLabel("★", Color="#000000", FontSize=20, Parent=Block)
                    Lbl.widget.setAlignment(LCARS.Protocol.AlignmentFlag.AlignCenter)
                    L = LCARS.Vertical(Block)
                    L.addWidget(Lbl.widget)
                    Block.setToolTip(entity_name)
                    
                self.RadarGrid.addWidget(Block, y, x)

    def OnSectorScan(self):
        if self.Astrometrics:
            self.Astrometrics._populate_sector()
        self.DrawRadar()
