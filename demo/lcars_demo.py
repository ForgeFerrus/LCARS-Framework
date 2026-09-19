# Демонстраційний файл LCARS - автентична система в стилі Star Trek
# Призначення: Демонстрація палітр проекту через базові компоненти фреймворку

import sys
from pathlib import Path

# Додаємо корінь проекту в шлях Python для імпорту модулів lcars
projectRoot = Path(__file__).parent.absolute()
repoRoot = projectRoot.parent
sys.path.insert(0, str(repoRoot))

# Імпортуємо через реєстр LCARS базові компоненти
from lcars.base.type import LCARS

ComponentModule = LCARS.Import("lcars.base.component")
LCARSButton = ComponentModule.LCARSButton
LCARSElbow = ComponentModule.LCARSElbow
LCARSLabel = ComponentModule.LCARSLabel
LCARSIndicator = ComponentModule.LCARSIndicator
LCARSBar = ComponentModule.LCARSBar

InterfaceModule = LCARS.Import("lcars.base.interface")
Screen = InterfaceModule.Screen
Segment = InterfaceModule.Segment
Header = InterfaceModule.Header
DataBlock = InterfaceModule.DataBlock

DefaultModule = LCARS.Import("lcars.base.default")
Palette = DefaultModule.Palette
RandomButtonColor = DefaultModule.RandomButtonColor
FontStyle = DefaultModule.FontStyle

# Імпортуємо теми напряму щоб уникнути циркулярних імпортів
from lcars.themes.lcars_palette import LCARSEra, get_theme, setup_lcars_font, get_random_button_color
from lcars.themes.theme import FactionEra

# Налаштування шрифтів LCARS
setupLcarsFont()

# Побудова словника кольорів з теми для сумісності UI коду
defaultTheme = getTheme(LCARSEra.LCARS_25TH)
palette = defaultTheme.get('palette', ['#4BBEBF'])
LCARSColors = {
    'primary_orange': palette[4] if len(palette) > 4 else palette[0],
    'primary_cyan': palette[0],
    'primary_blue': palette[1] if len(palette) > 1 else palette[0],
    'secondary_cyan': palette[2] if len(palette) > 2 else palette[0],
    'secondary_orange': palette[3] if len(palette) > 3 else palette[0],
    'secondary_blue': palette[1] if len(palette) > 1 else palette[0],
    'alert_red': defaultTheme.get('alerts', ['#D80000'])[0],
    'alert_yellow': defaultTheme.get('alerts', ['#FFBB00'])[1] if len(defaultTheme.get('alerts', [])) > 1 else defaultTheme.get('alerts', ['#FFBB00'])[0],
    'text_black': defaultTheme.get('text', '#000000'),
    'text_white': defaultTheme.get('text', '#FFFFFF'),
    'background_black': defaultTheme.get('bg', '#000000'),
    'panel_gray': palette[0]
}

# Відображення назв епох на enum LCARSEra
ERANameToEnum = {
    "22nd": LCARSEra.COMS_22ND,
    "23rd": LCARSEra.PCARS_23RD,
    "23st": LCARSEra.PCARS_23ST,
    "24th": LCARSEra.LCARS_24TH,
    "24st": LCARSEra.LCARS_24ST,
    "25th": LCARSEra.LCARS_25TH,
    "29th": LCARSEra.TCARS_29TH,
}

class DemoLCARSScreen(Screen):
    def __init__(self, faction="FEDERATION", era="25th"):
        super().__init__()
        self.faction = faction
        self.era = era
        
        eraEnum = ERANameToEnum.get(str(self.era).lower(), LCARSEra.LCARS_25TH)
        
        self.setWindowTitle(f"LCARS Desktop - {faction} {era}")
        self.setGeometry(50, 50, 1600, 1000)
        self.widget.setStyleSheet(f"background-color: {LCARSColors['background_black']};")
        
        self.build_demo_interface(eraEnum)
        
    def build_demo_interface(self, eraEnum):
        mainLayout = LCARS.Vertical(self.widget)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(4)
        
        # === TOP HEADER ===
        headerLayout = LCARS.Horizontal()
        headerLayout.setSpacing(4)
        
        # Left elbow
        elbowLeft = LCARSElbow(
            Direction="top-left",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget
        )
        elbowLeft.widget.setFixedSize(250, 80)
        headerLayout.addWidget(elbowLeft.widget)
        
        # Title panel з використанням LCARSBar
        titleBar = LCARSBar(
            Type="rect",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget,
            Width=800,
            Height=80
        )
        titleBar.widget.setFixedHeight(80)
        headerLayout.addWidget(titleBar.widget, 1)
        
        # Title label
        title = LCARSLabel(
            Text=f"USS ENTERPRISE - {self.faction} {self.era} CONFIGURATION",
            FontSize=32,
            Parent=self.widget
        )
        title.widget.setStyleSheet(f"color: #000000; font-size: 32px; font-weight: bold; text-transform: uppercase;")
        headerLayout.addWidget(title.widget)
        
        # Right cap
        rightCap = LCARSElbow(
            Direction="top-right",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget
        )
        rightCap.widget.setFixedSize(80, 80)
        headerLayout.addWidget(rightCap.widget)
        
        mainLayout.addLayout(headerLayout)
        
        # === MAIN INTERFACE ===
        interfaceLayout = LCARS.Horizontal()
        interfaceLayout.setSpacing(4)
        
        # === LEFT CONTROL PANEL ===
        leftPanelLayout = LCARS.Vertical()
        leftPanelLayout.setSpacing(4)
        
        # Main panel bar
        mainLeftBar = LCARSBar(
            Type="rect",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget,
            Width=250,
            Height=200
        )
        mainLeftBar.widget.setFixedWidth(250)
        mainLeftBar.widget.setStyleSheet(f"background-color: {getRandomButtonColor(eraEnum)}; border-bottom-left-radius: 100px; border-top-left-radius: 4px;")
        leftPanelLayout.addWidget(mainLeftBar.widget, 1)
        
        # Control buttons
        controls = [
            ("DASHBOARD", getRandomButtonColor(eraEnum)),
            ("TACTICAL", getRandomButtonColor(eraEnum, None, 1)),
            ("SCIENCE", getRandomButtonColor(eraEnum)),
            ("ENGINEERING", getRandomButtonColor(eraEnum)),
            ("COMMUNICATIONS", getRandomButtonColor(eraEnum)),
            ("COMPUTER", getRandomButtonColor(eraEnum))
        ]
        
        for controlName, color in controls:
            btn = LCARSButton(
                Text=controlName,
                Color=color,
                Type="soft-left",
                Parent=self.widget,
                Width=250,
                Height=60
            )
            leftPanelLayout.addWidget(btn.widget)
        
        leftPanelLayout.addStretch(1)
        
        # Bottom elbow
        bottomElbow = LCARSElbow(
            Direction="bottom-left",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget
        )
        bottomElbow.widget.setFixedSize(250, 80)
        leftPanelLayout.addWidget(bottomElbow.widget)
        
        interfaceLayout.addLayout(leftPanelLayout)
        
        # === CENTER DISPLAY AREA ===
        centerDisplayLayout = LCARS.Vertical()
        centerDisplayLayout.setSpacing(20)
        centerDisplayLayout.setContentsMargins(20, 20, 20, 20)
        
        # Main status panel
        statusBar = LCARSBar(
            Type="rect",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget,
            Height=100
        )
        statusBar.widget.setFixedHeight(100)
        centerDisplayLayout.addWidget(statusBar.widget)
        
        # Status labels
        statusTitle = LCARSLabel(
            Text="MAIN SYSTEMS STATUS",
            FontSize=28,
            Parent=self.widget
        )
        statusTitle.widget.setStyleSheet(f"color: #FFFFFF; font-size: 28px; font-weight: bold; text-transform: uppercase;")
        centerDisplayLayout.addWidget(statusTitle.widget)
        
        statusInfo = LCARSLabel(
            Text="ALL SYSTEMS OPERATIONAL - GREEN ALERT",
            FontSize=20,
            Parent=self.widget
        )
        statusInfo.widget.setStyleSheet(f"color: #FFFFFF; font-size: 20px; font-weight: bold; text-transform: uppercase;")
        centerDisplayLayout.addWidget(statusInfo.widget)
        
        # Data display panels з використанням DataBlock
        dataPanels = [
            ("SHIELDS", getRandomButtonColor(eraEnum), "ONLINE - 100%"),
            ("WEAPONS", getRandomButtonColor(eraEnum, None, 1), "STANDBY"),
            ("ENGINES", getRandomButtonColor(eraEnum), "WARP 9.0 AVAILABLE"),
            ("SENSORS", getRandomButtonColor(eraEnum), "LONG RANGE SCAN"),
            ("COMMUNICATIONS", getRandomButtonColor(eraEnum), "SUBSPACE CHANNEL OPEN"),
            ("LIFE SUPPORT", getRandomButtonColor(eraEnum), "OPTIMAL")
        ]
        
        for title, color, status in dataPanels:
            block = DataBlock(
                LabelText=title,
                ValueText=status,
                Color=color,
                Parent=self.widget
            )
            centerDisplayLayout.addWidget(block.widget)
        
        centerDisplayLayout.addStretch()
        
        interfaceLayout.addLayout(centerDisplayLayout, 1)
        mainLayout.addLayout(interfaceLayout)
        
        # === BOTTOM STATUS BAR ===
        bottomBarLayout = LCARS.Horizontal()
        bottomBarLayout.setSpacing(4)
        
        # Left status elbow
        leftStatusElbow = LCARSElbow(
            Direction="bottom-left",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget
        )
        leftStatusElbow.widget.setFixedSize(300, 50)
        bottomBarLayout.addWidget(leftStatusElbow.widget)
        
        # Center status bar
        centerStatusBar = LCARSBar(
            Type="rect",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget,
            Height=50
        )
        centerStatusBar.widget.setFixedHeight(50)
        bottomBarLayout.addWidget(centerStatusBar.widget, 1)
        
        # Status text
        statusText = LCARSLabel(
            Text=f"STARDATE: 58432.7 - {self.faction} {self.era} SYSTEM READY",
            FontSize=18,
            Parent=self.widget
        )
        statusText.widget.setStyleSheet(f"color: #000000; font-size: 18px; font-weight: bold; text-transform: uppercase;")
        bottomBarLayout.addWidget(statusText.widget)
        
        # Right status elbow
        rightStatusElbow = LCARSElbow(
            Direction="bottom-right",
            Color=getRandomButtonColor(eraEnum),
            Parent=self.widget
        )
        rightStatusElbow.widget.setFixedSize(150, 50)
        bottomBarLayout.addWidget(rightStatusElbow.widget)
        
        mainLayout.addLayout(bottomBarLayout)

LCARS.Launch(DemoLCARSScreen)
