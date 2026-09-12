# ◤ TITANIUM UNIFIED SHELL 🖖
# =============================================================================
# ФАЙЛ: lcars/ui/titan_shell.py
# ПРИЗНАЧЕННЯ: Єдина операційна оболонка Titanium.
# МОДУЛІ: Engineering, Explorer, Monitor, Nova IDE, Sensors, Weather, Settings
# СТАНДАРТ: Titanium LCARS (Zero-Underscores, No Direct Imports, Strict PascalCase)
# =============================================================================
from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.default import Palette, SystemTheme
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow
from lcars.base.interface import Screen, Segment
from lcars.core.signal import ODN

class TitaniumShell(Screen):
    def BuildScreen(self):
        pass

    def __init__(self, Parent=None):
        self.ModuleMap = {}
        self.ActiveButton = None
        self.SystemAccessPanel = None
        super().__init__(Parent=Parent, Decorated=False, Color="#000000")
        self._loadConfig()
        self.BuildShell()
        self.MountModules()
        self.SwitchToModule("ENGINEERING")

    def _loadConfig(self):
        import json
        from pathlib import Path
        ConfigPath = Path("config/config.json")
        self.Era = "LCARS_25TH"
        self.Faction = "Federation"
        self.AccentColor = Palette.Buttons[0]
        if ConfigPath.exists():
            try:
                Data = json.loads(ConfigPath.read_text(encoding="utf-8"))
                self.Era = Data.get("era", self.Era)
                self.Faction = Data.get("faction", self.Faction)
            except Exception:
                pass

    def BuildShell(self):
        Widget = self.widget
        Widget.setStyleSheet("background-color: #000000; border: none;")
        RootLayout = LCARS.Vertical(Widget)
        RootLayout.setContentsMargins(0, 0, 0, 0)
        RootLayout.setSpacing(0)

        MainRow = LCARS.Horizontal()
        MainRow.setSpacing(0)

        NavPanel = Segment(Parent=Widget)
        NavPanel.widget.setFixedWidth(200)
        NavLayout = LCARS.Vertical(NavPanel.widget)
        NavLayout.setContentsMargins(16, 60, 10, 20)
        NavLayout.setSpacing(8)

        TitleLabel = LCARSLabel(Text="TITANIUM SHELL", Color=Palette.Buttons[0], FontSize=14, Parent=NavPanel.widget)
        NavLayout.addWidget(TitleLabel.widget)

        Separator = LCARSBar(Type="rect", Color=Palette.Buttons[0], Height=8, Parent=NavPanel.widget)
        NavLayout.addWidget(Separator.widget)

        NavButtons = [
            ("ENGINEERING", Palette.Buttons[0]),
            ("EXPLORER", Palette.Buttons[1]),
            ("MONITOR", Palette.Buttons[2]),
            ("NOVA IDE", Palette.Buttons[3]),
            ("SENSORS", Palette.Buttons[4]),
            ("WEATHER", Palette.Buttons[5] if len(Palette.Buttons) > 5 else Palette.Buttons[0]),
            ("SETTINGS", Palette.Red[0] if hasattr(Palette, "Red") else "#CC6666"),
        ]

        self.ButtonMap = {}
        for Label, Color in NavButtons:
            Btn = LCARSButton(Text=Label, Type="soft-left", Color=Color, Parent=NavPanel.widget)
            Btn.widget.setFixedHeight(36)
            Key = Label.replace(" ", "_")
            Btn.Clicked.Connect(lambda *_, k=Key: self.SwitchToModule(k))
            NavLayout.addWidget(Btn.widget)
            self.ButtonMap[Key] = Btn

        NavLayout.addStretch(1)

        ExitBtn = LCARSButton(Text="TERMINATE", Type="pill", Color="#444444", Parent=NavPanel.widget)
        ExitBtn.widget.setFixedHeight(36)
        ExitBtn.Clicked.Connect(lambda *_: Widget.close())
        NavLayout.addWidget(ExitBtn.widget)

        MainRow.addWidget(NavPanel.widget)

        self.ModuleStack = LCARS.Stacked(Widget)
        self.ModuleStack.setStyleSheet("background-color: #000000; border: none;")
        MainRow.addWidget(self.ModuleStack, 1)

        RootLayout.addLayout(MainRow, 1)

        FooterBar = LCARSBar(Type="rect", Color=Palette.Buttons[4], Height=32, Parent=Widget)
        FooterLayout = LCARS.Horizontal(FooterBar.widget)
        FooterLayout.setContentsMargins(16, 0, 16, 0)
        self.FooterLabel = LCARSLabel(Text="MISSION STATUS: NOMINAL", Color=Palette.Background, FontSize=11, Parent=FooterBar.widget)
        FooterLayout.addWidget(self.FooterLabel.widget, 1)
        RootLayout.addWidget(FooterBar.widget)

    def MountModules(self):
        AvailableModules = {}

        try:
            from lcars.ui.workbench import ScienceWorkbench
            AvailableModules["ENGINEERING"] = ScienceWorkbench
        except Exception:
            pass

        try:
            from programs.Nova.ide import NovaPanel
            AvailableModules["NOVA_IDE"] = NovaPanel
        except Exception:
            pass

        try:
            from lcars.ui.terminal import LCARSTerminal
            AvailableModules["MONITOR"] = LCARSTerminal
        except Exception:
            pass

        for Key, ModuleClass in AvailableModules.items():
            try:
                Instance = ModuleClass(Parent=self.widget)
                self.ModuleStack.addWidget(Instance.widget)
                self.ModuleMap[Key] = Instance
            except Exception as e:
                self._addFallbackModule(Key, str(e))

        for Key in ["ENGINEERING", "EXPLORER", "NOVA_IDE", "SENSORS", "WEATHER", "SETTINGS", "MONITOR"]:
            if Key not in self.ModuleMap:
                self._addFallbackModule(Key, f"Module {Key} not available")

    def _addFallbackModule(self, Key, Reason):
        FallbackWidget = LCARS.Widget()
        FallbackLayout = LCARS.Vertical(FallbackWidget)
        FallbackLayout.setContentsMargins(40, 40, 40, 40)
        FallbackLayout.setSpacing(16)

        Title = LCARSLabel(Text=f"MODULE: {Key}", Color=Palette.Buttons[0], FontSize=20, Parent=FallbackWidget)
        FallbackLayout.addWidget(Title.widget)

        Separator = LCARSBar(Type="rect", Color=Palette.Buttons[0], Height=8, Parent=FallbackWidget)
        FallbackLayout.addWidget(Separator.widget)

        Status = LCARSLabel(Text=f"STATUS: STANDBY", Color=Palette.Buttons[3], FontSize=14, Parent=FallbackWidget)
        FallbackLayout.addWidget(Status.widget)

        ReasonLabel = LCARSLabel(Text=Reason, Color=Palette.Buttons[4], FontSize=12, Parent=FallbackWidget)
        FallbackLayout.addWidget(ReasonLabel.widget)

        FallbackLayout.addStretch(1)

        self.ModuleStack.addWidget(FallbackWidget)
        self.ModuleMap[Key] = type("FallbackModule", (), {"widget": FallbackWidget})()

    def SwitchToModule(self, Key):
        if Key in self.ModuleMap:
            Module = self.ModuleMap[Key]
            Widget = getattr(Module, "widget", Module)
            self.ModuleStack.setCurrentWidget(Widget)

            for BtnKey, Btn in self.ButtonMap.items():
                if BtnKey == Key:
                    Color = Palette.Buttons[0]
                    Btn.widget.setStyleSheet(f"background-color: {Color}; border-left: 4px solid white; border: none;")
                else:
                    Btn.widget.setStyleSheet("border: none;")

            self.FooterLabel.SetText(f"MODULE: {Key}")
            try:
                from lcars.engineering.telemetry import EmitTelemetry
                EmitTelemetry("TitanShell", f"MODULE_FOCUS: {Key}")
            except Exception:
                pass

if __name__ == "__main__":
    App = LCARS.Application.instance() or LCARS.Application([])
    Shell = TitaniumShell()
    if hasattr(Shell.widget, "showFullScreen"):
        Shell.widget.showFullScreen()
    else:
        Shell.widget.show()
    App.exec()
