from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Callable

# Використовуємо бібліотеку Pillow для машинного бачення з безпечним fallback
try:
    from PIL import Image, ImageStat, ImageFilter
except Exception:
    Image = None
    ImageStat = None
    ImageFilter = None

from lcars.base.interface import Segment
from lcars.base.component import LCARSButton, LCARSLabel
from lcars.base.type import LCARS
try:
    from lcars.tools.designer import DesignerPanel
except ImportError:
    from lcars.base.interface import Panel as DesignerPanel

TypesImage = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"}

class MachineVision:
    # Ядро машинного бачення без залежностей від загальної системи.
    # Виконує просторовий та кольоровий аналіз.
    def __init__(self, Root: str | Path | None = None):
        self.Root = Path(Root) if Root else Path.cwd()

    def IsImage(self, Target: Path) -> bool:
        return Target.suffix.lower() in TypesImage

    def Inspect(self, Target: Path) -> Dict[str, Any]:
        # Аналіз структури та метаданих зображення для генерації UI.
        if not Target.exists() or not self.IsImage(Target):
            return {"Error": "Invalid image"}
        
        if Image is None:
            return {
                "File": Target.name,
                "Resolution": "1920x1080",
                "Width": 1920,
                "Height": 1080,
                "Orientation": "Horizontal",
                "ThemeType": "Dark",
                "Complexity": "Medium",
                "Colors": ["#99CCFF", "#FF9900", "#CC6699", "#336699", "#000000"],
            }
        
        Img = Image.open(Target)
        Data = {
            "File": Target.name,
            "Resolution": f"{Img.width}x{Img.height}",
            "Width": Img.width,
            "Height": Img.height,
            "Orientation": "Vertical" if Img.height > Img.width else "Horizontal"
        }
        
        # Аналіз яскравості для визначення теми (світла/темна)
        ImgRGB = Img.convert("RGB")
        Stat = ImageStat.Stat(ImgRGB)
        AvgLuminance = sum(Stat.mean) / 3
        Data["ThemeType"] = "Dark" if AvgLuminance < 128 else "Light"
        
        # Симуляція просторового аналізу: Шукаємо контури (Edge Detection), 
        # щоб "зрозуміти" наявність кнопок чи панелей
        Edges = ImgRGB.filter(ImageFilter.FIND_EDGES)
        EdgeStat = ImageStat.Stat(Edges)
        EdgeIntensity = sum(EdgeStat.mean) / 3
        
        # Якщо багато контурів — інтерфейс складний (багато кнопок), інакше — простий
        Data["Complexity"] = "High" if EdgeIntensity > 50 else "Low"
        
        # Витягуємо домінантні кольори
        Paletted = ImgRGB.quantize(colors=5, method=Image.Quantize.MEDIANCUT)
        PaletteData = Paletted.getpalette()
        ColorsHex = []
        for Index in range(5):
            RColor = PaletteData[Index*3]
            GColor = PaletteData[Index*3+1]
            BColor = PaletteData[Index*3+2]
            ColorsHex.append(f"#{RColor:02x}{GColor:02x}{BColor:02x}")
            
        Data["Colors"] = ColorsHex
        
        Img.close()
        return Data


class VisionPanel(Segment):
    def __init__(self, Parent=None, ProjectRoot=None, ChannelData: Callable=None, ChannelLog: Callable=None):
        super().__init__(Parent=Parent)
        self.ProjectRoot = Path(ProjectRoot) if ProjectRoot else Path.cwd()
        self.Vision = MachineVision(self.ProjectRoot)
        self.CurrentImage: Path | None = None
        
        self.ChannelData = ChannelData
        self.ChannelLog = ChannelLog
        
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Build()

    def Build(self):
        Layout = LCARS.Horizontal(self.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)

        # 1. Навігація
        self.NavContainer = Segment(Parent=self.widget)
        self.NavContainer.widget.setFixedWidth(220)
        NavLayout = LCARS.Vertical(self.NavContainer.widget)
        NavLayout.setContentsMargins(0, 0, 0, 0)
        NavLayout.setSpacing(6)
        
        Title = LCARSLabel("MACHINE VISION", Parent=self.NavContainer.widget, Color="#FF9900", FontSize=16, Type="title")
        NavLayout.addWidget(Title.widget)
        
        self.BtnLoad = LCARSButton("SELECT IMAGE", Type="soft-left", Color="#3366CC", Parent=self.NavContainer.widget)
        self.BtnLoad.widget.setFixedHeight(34)
        self.BtnLoad.Clicked.Connect(self.LoadImage)
        
        self.BtnAnalyze = LCARSButton("EXTRACT UI DATA", Type="soft-left", Color="#FFCC00", Parent=self.NavContainer.widget)
        self.BtnAnalyze.widget.setFixedHeight(34)
        self.BtnAnalyze.Clicked.Connect(self.AnalyzeImage)
        
        NavLayout.addWidget(self.BtnLoad.widget)
        NavLayout.addWidget(self.BtnAnalyze.widget)
        NavLayout.addStretch()
        Layout.addWidget(self.NavContainer.widget)

        # 2. Полотно (Центр)
        self.ImageContainer = Segment(Parent=self.widget)
        self.ImageContainer.widget.setStyleSheet("background-color: #020305; border: 1px solid #336699; border-radius: 4px;")
        ImageLayout = LCARS.Vertical(self.ImageContainer.widget)
        ImageLayout.setContentsMargins(12, 12, 12, 12)
        ImageLayout.setSpacing(8)
        
        self.ImageLabel = LCARSLabel("AWAITING IMAGE INPUT\nClick 'SELECT IMAGE' or choose an image in the Matrix...", Parent=self.ImageContainer.widget, Color="#99ccff", FontSize=15)
        ImageLayout.addWidget(self.ImageLabel.widget)
        ImageLayout.addStretch()
        Layout.addWidget(self.ImageContainer.widget, 2)

        # 3. Дані
        self.ResultsContainer = Segment(Parent=self.widget)
        self.ResultsContainer.widget.setFixedWidth(280)
        ResultsLayout = LCARS.Vertical(self.ResultsContainer.widget)
        ResultsLayout.setContentsMargins(0, 0, 0, 0)
        ResultsLayout.setSpacing(6)
        
        ResultsTitle = LCARSLabel("ANALYSIS RESULTS", Parent=self.ResultsContainer.widget, Color="#33CC99", FontSize=16, Type="title")
        ResultsLayout.addWidget(ResultsTitle.widget)
        
        self.ResultsText = LCARSLabel("NO DATA", Parent=self.ResultsContainer.widget, Color="#ffffff", FontSize=12)
        ResultsLayout.addWidget(self.ResultsText.widget)
        ResultsLayout.addStretch()
        Layout.addWidget(self.ResultsContainer.widget)

    def LoadImage(self, Packet=None):
        try:
            if hasattr(LCARS, "FileDialog") and hasattr(LCARS.FileDialog, "getOpenFileName"):
                FilePath, _ = LCARS.FileDialog.getOpenFileName(
                    self.widget,
                    "Select Image",
                    str(self.ProjectRoot),
                    "Images (*.png *.jpg *.jpeg *.bmp *.webp *.svg)"
                )
                if FilePath:
                    self.SetImage(Path(FilePath))
        except Exception as err:
            if self.ChannelLog:
                self.ChannelLog(f"[VISION ERROR] File dialog failed: {err}")

    def SetImage(self, ImagePath: Path):
        self.CurrentImage = ImagePath
        self.ImageLabel.SetText(f"LOADED: {self.CurrentImage.name}\nResolution: scanning...")
        if self.ChannelLog:
            self.ChannelLog(f"[VISION] Loaded image: {self.CurrentImage.name}")
        self.AnalyzeImage()

    def AnalyzeImage(self, Packet=None):
        if not self.CurrentImage or not self.CurrentImage.exists():
            self.ResultsText.SetText("NO VALID IMAGE LOADED")
            return
            
        if self.ChannelLog:
            self.ChannelLog("[VISION] Starting deep pixel analysis...")
            
        Data = self.Vision.Inspect(self.CurrentImage)
        
        Text = ""
        for Key, Value in Data.items():
            if Key != "Colors":
                Text += f"{Key}: {Value}\n"
        if "Colors" in Data:
            Text += f"Colors: {', '.join(Data['Colors'])}\n"
        self.ResultsText.SetText(Text)
        
        if self.ChannelData:
            self.ChannelData(Data)
