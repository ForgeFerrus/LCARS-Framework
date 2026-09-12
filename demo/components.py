from lcars.base.type import LCARS
from lcars.base.interface import PADD
from lcars.base.component import LCARSButton, LCARSIndicator, LCARSBar, LCARSLabel, LCARSElbow
from lcars.base.default import Palette

App = LCARS.Application.instance() or LCARS.Application([])

Padd = PADD(Title="LCARS UNIFIED COMPONENT LIBRARY", Width=1280, Height=800)
C = Padd.Items.get("Content")

# --- HEADER ---
C.Add(LCARSLabel(Text="SYSTEM COMPONENTS SHOWCASE", FontSize=18, Bold=True))
C.Add(LCARSBar(Form=LCARSBar.Soft, Height=6, Sensory=True)) 
C.Add(LCARSBar(Form=LCARSBar.Rect, Height=10, Color="#000000")) # Invisible spacer

# --- 1. BUTTON FORMS ---
C.Add(LCARSLabel(Text="1. BUTTON FORMS (Smart Auto-Color, Auto-Num, SwapMode)", FontSize=14))
R1 = LCARS.Horizontal()
R1.setContentsMargins(0, 0, 0, 0)
R1.setSpacing(12)
R1.addWidget(LCARSButton(Text="PILL FORM",   Form=LCARSButton.Pill,     Width=180, Height=44).widget)
R1.addWidget(LCARSButton(Text="RECT FORM",   Form=LCARSButton.Rect,     Width=180, Height=44).widget)
R1.addWidget(LCARSButton(Text="SOFT FORM",   Form=LCARSButton.Soft,     Width=180, Height=44).widget)
R1.addWidget(LCARSButton(Text="HALF LEFT",   Form=LCARSButton.PillHalf, Direction=180, Width=180, Height=44).widget)
R1.addWidget(LCARSButton(Text="HALF RIGHT",  Form=LCARSButton.SoftHalf, Direction=0,   Width=180, Height=44).widget)
R1.addStretch()
C.Layout.addLayout(R1)

C.Add(LCARSBar(Form=LCARSBar.Rect, Height=16, Color="#000000")) # Invisible spacer

# --- 2. BUTTON STATES ---
C.Add(LCARSLabel(Text="2. COMPONENT STATES", FontSize=14))
R2 = LCARS.Horizontal()
R2.setContentsMargins(0, 0, 0, 0)
R2.setSpacing(12)
R2.addWidget(LCARSButton(Text="DISABLED", State=LCARSButton.DISABLED, Width=180, Height=44).widget)
R2.addWidget(LCARSButton(Text="ACTIVE",   State=LCARSButton.ACTIVE,   Width=180, Height=44).widget)
R2.addWidget(LCARSButton(Text="CONFIRM",  State=LCARSButton.CONFIRM,  Width=180, Height=44).widget)
R2.addWidget(LCARSButton(Text="YELLOW",   State=LCARSButton.YELLOW,   Width=180, Height=44).widget)
R2.addWidget(LCARSButton(Text="ALERT",    State=LCARSButton.ALERT,    Width=180, Height=44).widget)
R2.addStretch()
C.Layout.addLayout(R2)

C.Add(LCARSBar(Form=LCARSBar.Rect, Height=16, Color="#000000")) # Invisible spacer

# --- 3. INDICATORS ---
C.Add(LCARSLabel(Text="3. INDICATORS", FontSize=14))
R3 = LCARS.Horizontal()
R3.setContentsMargins(0, 0, 0, 0)
R3.setSpacing(12)
R3.addWidget(LCARSIndicator(Text="SYS OK",  Form=LCARSIndicator.Rect,     Width=120, Height=32, Number="", SwapMode=False).widget)
R3.addWidget(LCARSIndicator(Text="DATA",    Form=LCARSIndicator.PillHalf, Direction=180, Width=120, Height=32, Number="", SwapMode=False).widget)
R3.addWidget(LCARSIndicator(Text="UPLINK",  Form=LCARSIndicator.SoftHalf, Direction=0,   Width=120, Height=32, Number="", SwapMode=False).widget)
R3.addStretch()
C.Layout.addLayout(R3)

C.Add(LCARSBar(Form=LCARSBar.Rect, Height=16, Color="#000000")) # Invisible spacer

# --- 4. BARS & ELBOWS ---
C.Add(LCARSLabel(Text="4. STRUCTURAL ELEMENTS (BARS & ELBOWS)", FontSize=14))
R4 = LCARS.Horizontal()
R4.setContentsMargins(0, 0, 0, 0)
R4.setSpacing(12)
# explicitly pass Sensory=True so they are colored
R4.addWidget(LCARSElbow(Direction="top-left",     Width=140, Height=90, Sensory=True).widget)
R4.addWidget(LCARSElbow(Direction="bottom-right", Width=140, Height=90, Sensory=True).widget)

VBarBox = LCARS.Vertical()
VBarBox.setContentsMargins(0, 0, 0, 0)
VBarBox.setSpacing(10)
VBarBox.addWidget(LCARSBar(Form=LCARSBar.Rect, Width=400, Height=16, Sensory=True).widget)
VBarBox.addWidget(LCARSBar(Form=LCARSBar.Pill, Width=400, Height=16, Sensory=True).widget)
VBarBox.addWidget(LCARSBar(Form=LCARSBar.Soft, Width=400, Height=16, Sensory=True).widget)
VBarBox.addStretch()

R4.addLayout(VBarBox)
R4.addStretch()
C.Layout.addLayout(R4)

# Push everything to the top
C.Layout.addStretch()

Padd.Widget.show()
App.exec()
