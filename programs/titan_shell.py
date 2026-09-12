# ◤ TITANIUM UNIFIED SHELL — v44.20 🖖
# LCARS Framework :: MONOLITHIC_SYSTEM_INTERFACE // COMMAND_SHELL // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Єдина операційна оболонка Titanium. Консолідує всі модулі в одну систему.
# ФУНКЦІЇ: Глобальна навігація, керування в’юпортами та фонова стабільність.
# СТАНДАРТ: Titanium CamelCase + No-Contours (Surgical Shell Architecture).
# ─────────────────────────────────────────────────────────────────────────────

import sys
import json
from pathlib import Path
from lcars.base.registry import registry
from lcars.base.types import ODN, Matrix, Directive, Primitives
from lcars.base.defaults import TitanPalette, ActivePalette
from lcars.base.signals import ActiveSignals
from lcars.themes.palette import LCARSEra, FactionEra, EraPalette, get_theme, get_random_button_color
from lcars.themes.theme import ThemeFontStyle as FontStyle
from lcars.engineering.telemetry import TelemetryGrid, EmitTelemetry
from engineering.chips.architecture import ARCHITECTURE

# Системні вузли Titanium
BasePadd    = registry.Node("Technical.Visual.Padd")
BaseLabel   = registry.Node("Technical.Visual.Label")
BaseButton  = registry.Node("Technical.Visual.Button")
BaseFrame   = registry.Node("Technical.Visual.Frame")
ElbowNode   = registry.Node("Technical.Visual.Elbow")
StackWidget = registry.Node("Technical.Visual.Stacked")

class TitaniumShell(BasePadd):
    # ГОЛОВНА МОНОЛІТНА ОБОЛОНКА (Unified Architecture Protocol)
    def __init__(self):
        super().__init__(TitleStr="TITANIUM OPERATING SHELL", color="#3399FF")
        self.setStyleSheet("background: #000000; border: none;") # LOCK BLACK
        self.TelemetryNode = TelemetryGrid.GlobalInstance()
        self.ConfigPath = Path("config/config.json")
        
        # Завантажуємо конфігурацію (Era/Faction)
        EraObj, FactionObj = self._load_runtime_config()
        
        # Ініціалізація компонентів оболонки
        self.ActiveTheme = get_theme(EraObj, FactionObj)
        self.AccentCol = self.ActiveTheme.get("accent", "#3399FF")
        self.ViewportMap = {}
        self.ActiveButton = None
        self.SignalsNode = ActiveSignals()
        
        self.BuildShellStructure()
        self.MountSystemModules()
        
        # Підключення глобальних сигналів (System Cohesion)
        self.SignalsNode.alert_update.connect(self.OnGlobalAlertLevelChanged)
        
        # За замовчуванням відкриваємо MSD
        self.SwitchToModule("ENGINEERING")
        
        EmitTelemetry("TitanShell", f"TASK: SHELL_ONLINE. Era: {EraObj.name if EraObj else 'Default'}. 🖖")

    def _load_runtime_config(self) -> tuple:
        # Безпечне зчитування ери та фракції зі сховища
        DefaultEra = LCARSEra.LCARS_25TH
        DefaultFaction = FactionEra.Federation
        
        if not self.ConfigPath.exists():
            return DefaultEra, DefaultFaction
            
        try:
            Data = json.loads(self.ConfigPath.read_text())
            EraStr = Data.get("era", "LCARS_25TH")
            FactionStr = Data.get("faction", "Federation")
            
            # Конвертація рядків в Enums
            EraObj = getattr(LCARSEra, EraStr, DefaultEra)
            FactionObj = getattr(FactionEra, FactionStr, DefaultFaction)
            
            return EraObj, FactionObj
        except Exception:
            return DefaultEra, DefaultFaction

    def paintEvent(self, DrawEvent):
        # ◤ ТИТАНОВИЙ ШЕЛЬ: ВЕКТОРНИЙ КОРПУС КОМАНДНОГО МІСТКА
        PainterNode = Primitives.Painter(self)
        PainterNode.setRenderHint(Primitives.Antialiasing)
        
        W, H = self.width(), self.height()
        Th = 50 # Thick shell wall
        Rl = 60 # Large elbow radius
        
        ColorNode = Primitives.Color(self.AccentCol)
        PainterNode.setBrush(Primitives.Brush(ColorNode))
        PainterNode.setPen(Primitives.Pen(Primitives.Color(0,0,0,0)))
        
        PathNode = Primitives.Path()
        
        # 1. Зовнішній контур (Full Screen Frame)
        PathNode.moveTo(W, 0)
        PathNode.lineTo(Rl, 0)
        PathNode.arcTo(Primitives.RectF(0, 0, Rl*2, Rl*2), 90, 90) # Top-left external
        PathNode.lineTo(0, H - Rl)
        PathNode.arcTo(Primitives.RectF(0, H - Rl*2, Rl*2, Rl*2), 180, 90) # Bottom-left external
        PathNode.lineTo(W, H)
        PathNode.lineTo(W, H - 15) # Thin bottom bar
        PathNode.lineTo(Rl, H - 15)
        PathNode.arcTo(Primitives.RectF(15, H - Rl*2 + 15, (Rl-15)*2, (Rl-15)*2), 270, -90)
        PathNode.lineTo(15, Rl) # Thin inner vertical
        PathNode.arcTo(Primitives.RectF(15, 15, (Rl-15)*2, (Rl-15)*2), 180, -90)
        PathNode.lineTo(W, 15)
        PathNode.lineTo(W, 0)
        
        # 2. Додаткова "Стіна" Навігації (Wall Bar)
        PathNode.addRect(Primitives.RectF(0, Rl, Th, H - (Rl*2)))
        
        PainterNode.drawPath(PathNode)
        
        # Title Text (Monolithic Header)
        PainterNode.setPen(Primitives.Pen(Primitives.Color("black")))
        PainterNode.setFont(Primitives.Font("LCARS", 14, 75))
        PainterNode.drawText(Primitives.RectF(Rl + 10, 0, W - Rl - 20, 30), Directive.Align.AlignVCenter | Directive.Align.AlignLeft, "TITANIUM OPERATING SHELL")

    def BuildShellStructure(self):
        MainLayout = self.viewport_layout()
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)
        
        # 1. ГОЛОВНИЙ ШЛЮЗ
        ShellHub = ODN.Horizontal()
        ShellHub.setSpacing(0)
        
        # --- LEFT: NAVIGATION ---
        NavFrame = Matrix()
        NavFrame.setFixedWidth(180)
        NavLayout = ODN.Vertical(NavFrame)
        NavLayout.setContentsMargins(20, 60, 10, 20)
        NavLayout.setSpacing(12)
        
        NavLayout.addWidget(BaseLabel("◢ NAVIGATION", FontSizeVal=11, ColorHexStr="white"))
        
        ButtonConfig = [
            ("ENGINEERING", "ENGINEERING", self.AccentCol),
            ("EXPLORER",    "EXPLORER",    "#99CCFF"),
            ("MONITOR",     "MONITOR",     "#FF9900"),
            ("NOVA IDE",    "NOVA",        "#7FF3FF"),
            ("SENSORS",     "SENSORS",     "#9EA5BA"),
            ("WEATHER",     "WEATHER",     "#39C"),
            ("CONFIGURATION",  "SETTINGS", "#FF9966")
        ]
        
        self.ButtonsMap = {}
        for Lbl, Key, Col in ButtonConfig:
            Btn = BaseButton(Lbl, ColorHexStr=Col, shape="rect")
            Btn.clicked.connect(lambda k=Key: self.SwitchToModule(k))
            NavLayout.addWidget(Btn)
            self.ButtonsMap[Key] = Btn
            
        NavLayout.addStretch()
        ExitBtn = BaseButton("TERMINATE", ColorHexStr="#444", shape="rect")
        ExitBtn.clicked.connect(self.close)
        NavLayout.addWidget(ExitBtn)
        ShellHub.addWidget(NavFrame)
        
        # --- CENTER: MODULE VIEWPORT ---
        self.ModuleStack = StackWidget()
        self.ModuleStack.setStyleSheet("background: #000000; border: none;")
        ShellHub.addWidget(self.ModuleStack, 1)
        MainLayout.addLayout(ShellHub, 1)
        
        # 2. ФУТЕР
        self.FooterLabel = BaseLabel("◢ MISSION STATUS: NOMINAL // DEPARTMENTS READY")
        self.FooterLabel.setFixedHeight(30)
        self.FooterLabel.setStyleSheet(f"color: #444; {FontStyle(10)}; padding-left: 60px;")
        MainLayout.addWidget(self.FooterLabel)

    def MountSystemModules(self):
        from lcars.ui import monitor as ui_monitor

        Modules = [
            ("ENGINEERING", "Technical.Visual.MasterCommand"),
            ("EXPLORER",    "Technical.Visual.TitanExplorer"),
            ("MONITOR",     "Technical.Visual.TitanMonitor"),
            ("NOVA",        "Technical.Visual.NovaIDE"),
            ("SENSORS",     "Technical.Visual.Tricorder"),
            ("WEATHER",     "Technical.Visual.WeatherStation"), # НОВИЙ МОДУЛЬ 🖖
            ("SETTINGS",    "Technical.Visual.SettingsPanel")
        ]
        
        for Key, NodeStr in Modules:
            ModClass = registry.Node(NodeStr)
            if ModClass:
                Instance = ModClass()
                self.ModuleStack.addWidget(Instance)
                self.ViewportMap[Key] = Instance

    def SwitchToModule(self, ModuleKeyStr):
        if ModuleKeyStr in self.ViewportMap:
            self.ModuleStack.setCurrentWidget(self.ViewportMap[ModuleKeyStr])
            for Key, Btn in self.ButtonsMap.items():
                Btn.setStyleSheet(Btn.styleSheet().replace("border-left: 5px solid white;", ""))
            if ModuleKeyStr in self.ButtonsMap:
                Btn = self.ButtonsMap[ModuleKeyStr]
                Btn.setStyleSheet(Btn.styleSheet() + "border-left: 5px solid white;")
                self.ActiveButton = Btn
            EmitTelemetry("TitanShell", f"MODULE_FOCUS: {ModuleKeyStr}")

    def OnGlobalAlertLevelChanged(self, LevelKeyStr):
        AlertData = {
            "RED":    ("#FF0000", "CONDITION: RED ALERT // ALL SYSTEMS TO BATTLE STATIONS"),
            "YELLOW": ("#FFFF00", "CONDITION: YELLOW ALERT // STAND BY FOR SENSOR ARRAY FOCUS"),
            "NORMAL": (self.AccentCol, "CONDITION: NORMAL // MISSION PARAMETERS STABLE")
        }
        Col, Msg = AlertData.get(LevelKeyStr, AlertData["NORMAL"])
        self.FooterLabel.setText(f"◢ {Msg}")
        self.FooterLabel.setStyleSheet(f"color: {Col}; {FontStyle(11, 'bold')}; padding-left: 60px;")
        if LevelKeyStr == "RED": self.setStyleSheet("background: #100000;")
        else: self.setStyleSheet("background: #000000;")

if __name__ == "__main__":
    AppCls = registry.Node("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    Shell = TitaniumShell()
    Shell.showFullScreen()
    sys.exit(AppInst.exec())
