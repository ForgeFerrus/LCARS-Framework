import sys

from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import LCARSButton, LCARSElbow, LCARSBar, LCARSLabel
from lcars.base.default import Palette

def OpenSystemDemo():
    print("System Demo opened (stub)")

def OpenPaletteWindow():
    print("Palette Window opened (stub)")

def Main():
    App = LCARS.Application.instance() or LCARS.Application(sys.argv)
    
    Padd = PADD(Title="LCARS MINIMAL DEMO - PALETTE SHOWCASE", Width=1000, Height=760)
    C = Padd.Items.get("Content")
    
    # Header
    Header = LCARSLabel(Text="LCARS FRAMEWORK - COMBINED MINIMAL DEMO", FontSize=26, Bold=True)
    Header.Color = "#4BBEBF"
    C.Add(Header)
    
    C.Add(LCARSBar(Form=LCARSBar.Rect, Height=10, Color="#000000")) # Spacer
    
    # Top elbows
    RowElbows = LCARS.Horizontal()
    RowElbows.setSpacing(0)
    RowElbows.setContentsMargins(0,0,0,0)
    RowElbows.addWidget(LCARSElbow(Direction="top-left", Color="#4BBEBF", Width=200, Height=60).widget)
    RowElbows.addStretch()
    RowElbows.addWidget(LCARSElbow(Direction="top-right", Color="#FF9900", Width=200, Height=60).widget)
    C.Layout.addLayout(RowElbows)
    
    C.Add(LCARSBar(Form=LCARSBar.Rect, Height=20, Color="#000000")) # Spacer
    
    # Faction buttons and counts (2x2 Grid using nested layouts)
    Factions = [
        ("STARFLEET", "#4BBEBF"),
        ("KLINGON", "#CC0000"),
        ("ROMULAN", "#009933"),
        ("CARDASSIAN", "#FF9900")
    ]
    
    GridWrapper = LCARS.Vertical()
    GridWrapper.setSpacing(20)
    
    for i in range(0, len(Factions), 2):
        Row = LCARS.Horizontal()
        Row.setSpacing(30)
        Row.addStretch()
        for j in range(2):
            if i + j < len(Factions):
                Name, Color = Factions[i + j]
                
                Col = LCARS.Vertical()
                Btn = LCARSButton(Text=Name, Form=LCARSButton.Rect, Color=Color, Width=260, Height=110, Sensory=False)
                Btn.Number = ""
                Btn.SwapMode = False
                Desc = LCARSLabel(Text=f"{Name} - 8 COLORS", FontSize=12)
                
                Col.addWidget(Btn.widget)
                Col.addWidget(Desc.widget)
                Row.addLayout(Col)
        Row.addStretch()
        GridWrapper.addLayout(Row)
        
    C.Layout.addLayout(GridWrapper)
    
    C.Add(LCARSBar(Form=LCARSBar.Rect, Height=30, Color="#000000")) # Spacer
    
    # Era label
    EraLabel = LCARSLabel(Text="LCARS 25TH ERA SAMPLE PALETTE", FontSize=18, Bold=True)
    C.Add(EraLabel)
    
    # Palette samples
    PalRow = LCARS.Horizontal()
    PalRow.setSpacing(10)
    Colors = ["#4BBEBF", "#FF9900", "#CC0000", "#009933", "#FFCC33", "#99ccff", "#ffffff", "#666666"]
    for C in Colors:
        Swatch = LCARSButton(Text="", Form=LCARSButton.Rect, Color=c, Width=90, Height=60, Sensory=False)
        Swatch.Number = ""
        Swatch.SwapMode = False
        PalRow.addWidget(Swatch.widget)
    PalRow.addStretch()
    C.Layout.addLayout(PalRow)
    
    C.Add(LCARSBar(Form=LCARSBar.Rect, Height=20, Color="#000000")) # Spacer
    
    # Scanning bars
    C.Add(LCARSBar(Form=LCARSBar.Rect, Height=14, Color="#4BBEBF", Sensory=True))
    C.Add(LCARSBar(Form=LCARSBar.Pill, Height=24, Color="#FF9900", Sensory=True))
    
    C.Layout.addStretch()
    
    # Footer
    Footer = LCARS.Horizontal()
    Footer.setSpacing(15)
    
    BtnDemo = LCARSButton(Text="SYSTEM DEMO", Form=LCARSButton.Rect, Color="#4BBEBF", Width=160, Height=44)
    BtnDemo.Clicked.Connect(lambda data: OpenSystemDemo())
    
    BtnShowcase = LCARSButton(Text="PALETTE SHOWCASE", Form=LCARSButton.Rect, Color="#FF9900", Width=180, Height=44)
    BtnShowcase.Clicked.Connect(lambda data: OpenPaletteWindow())
    
    BtnClose = LCARSButton(Text="CLOSE", Form=LCARSButton.Rect, Color="#666666", Width=120, Height=44)
    BtnClose.Clicked.Connect(lambda data: Padd.widget.close())
    
    Footer.addWidget(BtnDemo.widget)
    Footer.addWidget(BtnShowcase.widget)
    Footer.addWidget(BtnClose.widget)
    Footer.addStretch()
    C.Layout.addLayout(Footer)
    
    Padd.Widget.show()
    sys.exit(App.exec())

if __name__ == '__main__':
    Main()
