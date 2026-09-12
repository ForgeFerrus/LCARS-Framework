from __future__ import annotations
import random
import colorsys
from pathlib import Path
from typing import Callable

from lcars.base.type import LCARS
from lcars.base.interface import Segment
from lcars.base.component import LCARSButton, LCARSLabel
from lcars.tools.designer import DesignerPanel

class LaboratoryPanel(Segment):
    # Лабораторія кольору та UI-компонентів.
    # Відповідає за маніпуляцію кольором, експорт CSS та тестування нових LCARS-компонентів.
    # Використовує ізолінійні канали для зв'язку з Бортовим Комп'ютером.
    def __init__(self, Parent=None, ProjectRoot=None, ChannelTheme: Callable=None, ChannelLog: Callable=None):
        super().__init__(Parent=Parent)
        self.ProjectRoot = Path(ProjectRoot) if ProjectRoot else Path.cwd()
        self.CurrentTheme = []
        
        # Ізолінійні канали
        self.ChannelTheme = ChannelTheme
        self.ChannelLog = ChannelLog
        
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Build()

    def Build(self):
        Layout = LCARS.Horizontal(self.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)

        # 1. ЛІВА ПАНЕЛЬ (Інструменти генерації та експорту)
        self.ToolsPanel = Segment(Parent=self.widget)
        self.ToolsPanel.widget.setFixedWidth(240)
        ToolsLayout = LCARS.Vertical(self.ToolsPanel.widget)
        ToolsLayout.setContentsMargins(0, 0, 0, 0)
        ToolsLayout.setSpacing(6)
        
        Title = LCARSLabel("COLOR LAB TOOLS", Parent=self.ToolsPanel.widget, Color="#CC99FF", FontSize=16, Type="title")
        ToolsLayout.addWidget(Title.widget)
        
        # Створення кнопок для різних алгоритмів генерування
        self.BtnGenMono = LCARSButton("GEN MONOCHROME", Type="soft-left", Color="#CC99FF", Parent=self.ToolsPanel.widget)
        self.BtnGenAnalogous = LCARSButton("GEN ANALOGOUS", Type="soft-left", Color="#99CCFF", Parent=self.ToolsPanel.widget)
        self.BtnGenComplement = LCARSButton("GEN COMPLEMENT", Type="soft-left", Color="#FFCC00", Parent=self.ToolsPanel.widget)
        self.BtnGenTriadic = LCARSButton("GEN TRIADIC", Type="soft-left", Color="#FF6699", Parent=self.ToolsPanel.widget)
        
        # Пресети Федерації
        self.BtnTngPreset = LCARSButton("PRESET: TNG CLASSIC", Type="soft-left", Color="#FF9933", Parent=self.ToolsPanel.widget)
        self.BtnVoyPreset = LCARSButton("PRESET: VOYAGER", Type="soft-left", Color="#3399FF", Parent=self.ToolsPanel.widget)
        self.BtnNemPreset = LCARSButton("PRESET: NEMESIS", Type="soft-left", Color="#4169E1", Parent=self.ToolsPanel.widget)
        
        self.BtnInject = LCARSButton("INJECT TO EDITOR", Type="pill", Color="#FF9933", Parent=self.ToolsPanel.widget)
        self.BtnExport = LCARSButton("EXPORT CSS / JSON", Type="pill", Color="#33CC99", Parent=self.ToolsPanel.widget)
        
        for btn in [self.BtnGenMono, self.BtnGenAnalogous, self.BtnGenComplement, self.BtnGenTriadic,
                    self.BtnTngPreset, self.BtnVoyPreset, self.BtnNemPreset]:
            btn.widget.setFixedHeight(32)
            ToolsLayout.addWidget(btn.widget)
            
        ToolsLayout.addSpacing(10)
        self.BtnInject.widget.setFixedHeight(36)
        self.BtnExport.widget.setFixedHeight(36)
        ToolsLayout.addWidget(self.BtnInject.widget)
        ToolsLayout.addWidget(self.BtnExport.widget)
        ToolsLayout.addStretch()
        
        Layout.addWidget(self.ToolsPanel.widget)

        # 2. ЦЕНТРАЛЬНА ПАНЕЛЬ (Візуалізатор кольорів)
        self.MainArea = Segment(Parent=self.widget)
        self.MainArea.widget.setStyleSheet("background-color: #000000; border: none;")
        MainLayout = LCARS.Vertical(self.MainArea.widget)
        MainLayout.setContentsMargins(10, 0, 0, 0)
        MainLayout.setSpacing(8)
        
        self.InfoLabel = LCARSLabel("LABORATORY READY\nSelect a generation mode or Starfleet preset...", Parent=self.MainArea.widget, Color="#CC99FF", FontSize=15)
        MainLayout.addWidget(self.InfoLabel.widget)
        
        self.PaletteWidget = DesignerPanel(Color="#000000")
        self.PaletteWidget.Horizontal(6, 6, 6, 6, 8)
        
        self.ColorBlocks = []
        self.ColorLabels = []
        
        for Index in range(8):
            ColumnPanel = DesignerPanel(Color="#000000")
            ColumnPanel.Vertical(0, 0, 0, 0, 4)
            
            Block = DesignerPanel(Color="#222222")
            Block.widget.setFixedSize(72, 72)
            
            Label = LCARSLabel("N/A", Parent=ColumnPanel.widget, Color="#FFFFFF", FontSize=12)
            
            ColumnPanel.Add(Block)
            ColumnPanel.Add(Label)
            self.PaletteWidget.Add(ColumnPanel)
            
            self.ColorBlocks.append(Block)
            self.ColorLabels.append(Label)
            
        MainLayout.addWidget(self.PaletteWidget.widget)
        MainLayout.addStretch()
        Layout.addWidget(self.MainArea.widget, 1)

        # Підключення обробників
        self.BtnGenMono.Clicked.Connect(lambda chk=False: self.GenerateTheme("monochrome"))
        self.BtnGenAnalogous.Clicked.Connect(lambda chk=False: self.GenerateTheme("analogous"))
        self.BtnGenComplement.Clicked.Connect(lambda chk=False: self.GenerateTheme("complementary"))
        self.BtnGenTriadic.Clicked.Connect(lambda chk=False: self.GenerateTheme("triadic"))
        self.BtnTngPreset.Clicked.Connect(lambda chk=False: self.ApplyPreset(["#FF9900", "#CC6699", "#99CCFF", "#FFCC00", "#CC3333", "#FF9966", "#9999FF", "#664466"], "TNG CLASSIC"))
        self.BtnVoyPreset.Clicked.Connect(lambda chk=False: self.ApplyPreset(["#9999FF", "#3366CC", "#FF9933", "#CC6699", "#FFCC33", "#006699", "#663366", "#3399CC"], "VOYAGER"))
        self.BtnNemPreset.Clicked.Connect(lambda chk=False: self.ApplyPreset(["#4169E1", "#6495ED", "#4682B4", "#00BFFF", "#1E90FF", "#000080", "#5F9EA0", "#87CEEB"], "NEMESIS BLUE"))
        self.BtnInject.Clicked.Connect(lambda chk=False: self.InjectToEditor())
        self.BtnExport.Clicked.Connect(lambda chk=False: self.ExportTheme())

        # За замовчуванням завантажуємо TNG
        self.ApplyPreset(["#FF9900", "#CC6699", "#99CCFF", "#FFCC00", "#CC3333", "#FF9966", "#9999FF", "#664466"], "TNG CLASSIC")

    def ApplyPreset(self, Colors: list, PresetName: str):
        self.CurrentTheme = Colors[:8]
        self.UpdatePaletteUI(PresetName)
        if self.ChannelTheme:
            self.ChannelTheme(PresetName, self.CurrentTheme)

    def LoadExternalPalette(self, Colors: list):
        if Colors:
            self.CurrentTheme = (Colors + ["#000000"] * 8)[:8]
            self.UpdatePaletteUI("VISION EXTRACTED")
            self.InfoLabel.SetText("RECEIVED PALETTE FROM VISION MODULE VIA DATA CHANNEL")
            if self.ChannelLog:
                self.ChannelLog("[LAB] Loaded external palette from Vision Data.")

    def GenerateTheme(self, ModeName: str):
        BaseH = random.random()
        BaseS = random.uniform(0.6, 0.9)
        BaseL = random.uniform(0.5, 0.7)
        
        Colors = []
        for Index in range(8):
            if ModeName == "monochrome":
                HValue = BaseH
                SValue = BaseS
                LValue = max(0.2, min(0.9, BaseL + (Index - 3) * 0.1))
            elif ModeName == "analogous":
                HValue = (BaseH + (Index - 3) * 0.05) % 1.0
                SValue = BaseS
                LValue = BaseL + random.uniform(-0.1, 0.1)
            elif ModeName == "complementary":
                HValue = BaseH if Index < 4 else (BaseH + 0.5) % 1.0
                HValue = (HValue + random.uniform(-0.05, 0.05)) % 1.0
                SValue = BaseS
                LValue = max(0.3, min(0.8, BaseL + (Index % 4 - 1.5) * 0.15))
            elif ModeName == "triadic":
                Offset = (Index % 3) * 0.333
                HValue = (BaseH + Offset) % 1.0
                SValue = BaseS
                LValue = BaseL + random.uniform(-0.1, 0.1)
            else:
                HValue, SValue, LValue = BaseH, BaseS, BaseL
                
            LValue = max(0.1, min(0.9, LValue))
            RValue, GValue, BValue = [int(CValue * 255) for CValue in colorsys.hls_to_rgb(HValue, LValue, SValue)]
            HexColor = f"#{RValue:02x}{GValue:02x}{BValue:02x}"
            Colors.append(HexColor)
            
        self.CurrentTheme = Colors
        self.UpdatePaletteUI(ModeName.upper())
        
        if self.ChannelTheme:
            self.ChannelTheme(ModeName, Colors)

    def UpdatePaletteUI(self, ModeName: str):
        self.InfoLabel.SetText(f"ACTIVE THEME: {ModeName}\nReady for editor injection or CSS export.")
        for Index, ColorValue in enumerate(self.CurrentTheme):
            if Index < len(self.ColorBlocks):
                self.ColorBlocks[Index].widget.setStyleSheet(f"background-color: {ColorValue}; border-radius: 6px;")
                self.ColorLabels[Index].SetText(ColorValue)

    def InjectToEditor(self):
        if not self.CurrentTheme:
            self.InfoLabel.SetText("ERROR: NO THEME AVAILABLE TO INJECT")
            return
        DictLines = ["# STARFLEET PALETTE CONFIGURATION", "LCARS_THEME = {"]
        for idx, col in enumerate(self.CurrentTheme):
            DictLines.append(f'    "COLOR_{idx+1}": "{col}",')
        DictLines.append("}\n")
        Payload = "\n".join(DictLines)
        if self.ChannelTheme:
            self.ChannelTheme("INJECT_CODE", Payload)
        self.InfoLabel.SetText("THEME INJECTED INTO ACTIVE CODE BUFFER.")
        if self.ChannelLog:
            self.ChannelLog("[COLOR LAB] Injected palette code to editor.")

    def ExportTheme(self):
        if not self.CurrentTheme:
            self.InfoLabel.SetText("ERROR: NO THEME TO EXPORT")
            return
            
        CssOutput = "/* LCARS GENERATED THEME */\n:root {\n"
        for Index, ColorValue in enumerate(self.CurrentTheme):
            CssOutput += f"    --lcars-color-{Index+1}: {ColorValue};\n"
        CssOutput += "}\n"
        
        self.InfoLabel.SetText("THEME EXPORTED TO CONSOLE & LOG.")
        if self.ChannelLog:
            self.ChannelLog(f"[LAB] CSS Exported:\n{CssOutput}")
