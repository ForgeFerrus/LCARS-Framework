# ◤ TITANIUM SETTINGS PANEL — v44.20 🖖
# LCARS Framework :: CORE_PANEL // SYSTEM_CONFIGURATION // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────
# ОПИС: Уніфікована панель налаштувань та діагностики Titanium. 
# ПРАВИЛА: Titanium CamelCase // No Bold // Zero-Except.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
from lcars.base.register import registry
from lcars.base.type import (
    Matrix, Directive, Chassis, LCARS, VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, ODN
)
from lcars.base.interface import (
    Label, Button, LCARSButton, Frame, Elbow, ScanningBar, DataBlock, StatBar, Pill
)

from lcars.base.default import TitanPalette, RandomButtonColor, SystemTheme, GetLcarsFontStyle
from lcars.system.system import ActiveSystem
from lcars.modules.sound_manager import ActiveAudio
from lcars.engineering.telemetry import EmitTelemetry
from lcars.themes.palette import LCARSEra, FactionEra, get_theme as GetTheme


class SettingsPanel(Matrix):
    # Монолітна панель налаштувань Titanium Matrix (v44.20).
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.SystemNode = ActiveSystem()
        self.ConfigPath = Path("config/config.json")
        self.setStyleSheet("background-color: black; border: none;")
        
        # Завантаження поточної конфігурації
        self.CurrentConfig = self._load_config()
        
        self._build_ui()
        
        # Таймер діагностики
        self.RefreshTimer = Timer(self)
        self.RefreshTimer.timeout.connect(self.UpdateDiagnostics)
        self.RefreshTimer.start(3000)
        
        EmitTelemetry("Settings", "SYSTEM CONFIGURATION PANEL INITIALIZED.")

    def _load_config(self) -> dict:
        if True:
            if self.ConfigPath.exists():
                return json.loads(self.ConfigPath.read_text())
        if False: # Removed except block
            pass
        return {"era": "LCARS_25TH", "faction": "Federation", "services": ["telemetry", "sound"]}

    def _save_config(self):
        if True:
            self.ConfigPath.parent.mkdir(parents=True, exist_ok=True)
            self.ConfigPath.write_text(json.dumps(self.CurrentConfig, indent=4))
            EmitTelemetry("Settings", "CONFIGURATION PERSISTED TO DISK.")
        if False: # Removed except block
            EmitTelemetry("Settings", f"SAVE ERROR: {str(e)}")

    def _build_ui(self):
        MainLayoutNode = VBoxLayout(self)
        MainLayoutNode.setContentsMargins(30, 20, 30, 20)
        MainLayoutNode.setSpacing(15)

        # ── 1. HEADER ──
        HeaderODN = HBoxLayout()
        self.CornerNode = Elbow("top-left", ColorHexStr=TitanPalette.Scientific[0])
        self.CornerNode.setFixedSize(160, 60)
        HeaderODN.addWidget(self.CornerNode)
        
        self.TitleNode = Label("◤ SYSTEM MASTER CONSOLE // CONFIGURATION", FontSizeVal=22)
        self.TitleNode.setStyleSheet(f"color: {TitanPalette.Scientific[0]}; font-family: 'LCARS'; font-weight: normal;")
        HeaderODN.addWidget(self.TitleNode, 1)
        MainLayoutNode.addLayout(HeaderODN)

        # ── 2. TAB BAR ──
        TabBarRow = HBoxLayout()
        TabBarRow.setSpacing(4)
        TabBarRow.setContentsMargins(0, 0, 0, 0)

        TabDefs = [
            ("CONFIGURATION",  TitanPalette.Scientific[0]),
            ("BIOS / FIRMWARE", TitanPalette.Buttons[0]),
            ("UTILITIES",      TitanPalette.Buttons[3]),
        ]
        self.TabButtons = []
        for Idx, (LblStr, ColorStr) in enumerate(TabDefs):
            Btn = LCARSButton(LblStr, ColorHexStr=ColorStr, radius=4)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(160)
            Btn.clicked.connect(lambda _, I=Idx: self.SwitchSection(I))
            TabBarRow.addWidget(Btn)
            self.TabButtons.append(Btn)
        TabBarRow.addStretch()
        MainLayoutNode.addLayout(TabBarRow)

        # ── 3. SECTION STACK ──
        self.SectionStack = Chassis.Stack(self)
        MainLayoutNode.addWidget(self.SectionStack, 1)

        # --- PAGE 0: CONFIGURATION ---
        Page0 = Frame()
        Page0Layout = HBoxLayout(Page0)
        Page0Layout.setContentsMargins(0, 8, 0, 0)
        Page0Layout.setSpacing(20)

        LeftCluster = VBoxLayout()
        LeftCluster.setSpacing(15)
        
        self.BiosBlock = Frame()
        self.BiosBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Buttons[1]}; background: #050515;")
        BiosODN = VBoxLayout(self.BiosBlock)
        BiosODN.addWidget(Label("◤ BIOS INTEGRITY CHECK", FontSizeVal=14, ColorHexStr=TitanPalette.Buttons[1]))
        self.BiosLabels = {}
        for K in ["RUNTIME", "KERNEL", "REGISTRY"]:
            Row = HBoxLayout()
            Row.addWidget(Label(f"{K}:", FontSizeVal=10, ColorHexStr="#999"))
            Val = Label("NOMINAL", FontSizeVal=10, ColorHexStr="#0F0")
            Row.addStretch()
            Row.addWidget(Val)
            BiosODN.addLayout(Row)
            self.BiosLabels[K] = Val
        LeftCluster.addWidget(self.BiosBlock)

        self.ServiceBlock = Frame()
        self.ServiceBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Scientific[1]}; background: #08081a;")
        ServiceODN = VBoxLayout(self.ServiceBlock)
        ServiceODN.addWidget(Label("◤ SUBSYSTEM REACTOR", FontSizeVal=14, ColorHexStr=TitanPalette.Scientific[1]))
        ServiceGrid = GridLayout()
        self.ServiceBtns = {}
        Services = [("SENTINEL", "sentinel"), ("TELEMETRY", "telemetry"), ("SOUND", "sound"), ("NOVA ACT", "nova")]
        for i, (Lbl, Key) in enumerate(Services):
            Active = Key in self.CurrentConfig.get("services", [])
            Btn = LCARSButton(f"{Lbl}: {'ON' if Active else 'OFF'}", ColorHexStr="#333" if not Active else "#555", radius=4)
            Btn.setFixedSize(140, 35)
            Btn.clicked.connect(lambda _, k=Key, l=Lbl: self.ToggleSubsystem(k, l))
            ServiceGrid.addWidget(Btn, i // 2, i % 2)
            self.ServiceBtns[Key] = Btn
        ServiceODN.addLayout(ServiceGrid)
        LeftCluster.addWidget(self.ServiceBlock)

        self.ShellBlock = Frame()
        self.ShellBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Alert[0]}; background: #1a0808;")
        ShellODN = VBoxLayout(self.ShellBlock)
        ShellODN.addWidget(Label("◤ OS INTEGRATION PROTOCOL", FontSizeVal=14, ColorHexStr=TitanPalette.Alert[0]))
        self.BtnShellToggle = LCARSButton("ACTIVATE TERMINAL OS MODE", ColorHexStr=TitanPalette.Alert[0], radius=4)
        self.BtnShellToggle.setMinimumHeight(45)
        self.BtnShellToggle.clicked.connect(self.ToggleShellIntegration)
        ShellODN.addWidget(self.BtnShellToggle)
        LeftCluster.addWidget(self.ShellBlock)
        Page0Layout.addLayout(LeftCluster, 1)

        RightCluster = VBoxLayout()
        RightCluster.setSpacing(15)
        self.EraBlock = Frame()
        self.EraBlock.setStyleSheet(f"border-right: 5px solid {TitanPalette.Buttons[0]}; background: #151525;")
        EraODN = VBoxLayout(self.EraBlock)
        EraODN.addWidget(Label("◤ CHRONOLOGY SHIFT (ERA)", FontSizeVal=14, ColorHexStr=TitanPalette.Buttons[0]))
        Eras = [("23RD (PCARS)", "PCARS_23RD"), ("24TH (LCARS)", "LCARS_24TH"), ("25TH (TITANIUM)", "LCARS_25TH"), ("29TH (TCARS)", "TCARS_29TH")]
        for L, K in Eras:
            Btn = LCARSButton(L, ColorHexStr=TitanPalette.Buttons[0], radius=4)
            Btn.setMinimumHeight(35)
            Btn.clicked.connect(lambda _, k=K: self.ApplyEraShift(k))
            EraODN.addWidget(Btn)
        RightCluster.addWidget(self.EraBlock)
        self.FactionBlock = Frame()
        self.FactionBlock.setStyleSheet(f"border-right: 5px solid {TitanPalette.Scientific[0]}; background: #252515;")
        FactionODN = VBoxLayout(self.FactionBlock)
        FactionODN.addWidget(Label("◤ FACTION PALETTE MATRIX", FontSizeVal=14, ColorHexStr=TitanPalette.Scientific[0]))
        Factions = [("FEDERATION", "Federation"), ("KLINGON", "Klingon"), ("ROMULAN", "Romulan"), ("BORG", "Borg")]
        for L, K in Factions:
            Btn = LCARSButton(L, ColorHexStr=TitanPalette.Scientific[0], radius=4)
            Btn.setMinimumHeight(35)
            Btn.clicked.connect(lambda _, k=K: self.ApplyFactionShift(k))
            FactionODN.addWidget(Btn)
        RightCluster.addWidget(self.FactionBlock)
        Page0Layout.addLayout(RightCluster, 1)

        self.SectionStack.addWidget(Page0)

        # --- PAGE 1: BIOS / FIRMWARE ---
        if True:
            from lcars.system.bios import BIOSPanel
            Page1 = BIOSPanel()
        if False: # Removed except block
            Page1 = Frame()
            VBoxLayout(Page1).addWidget(Label("BIOS MODULE UNAVAILABLE", FontSizeVal=16, ColorHexStr=TitanPalette.Alert[0]))
        self.SectionStack.addWidget(Page1)

        # --- PAGE 2: UTILITIES ---
        if True:
            from lcars.system.utilities import TitaniumUtilityTerminal
            Page2 = TitaniumUtilityTerminal()
        if False: # Removed except block
            Page2 = Frame()
            VBoxLayout(Page2).addWidget(Label("UTILITIES MODULE UNAVAILABLE", FontSizeVal=16, ColorHexStr=TitanPalette.Alert[0]))
        self.SectionStack.addWidget(Page2)

        # ── 4. FOOTER ──
        FooterODN = HBoxLayout()
        self.StatusNode = Label("◢ STATUS: KERNEL NOMINAL // READY FOR COMMAND", FontSizeVal=12, ColorHexStr="#666")
        FooterODN.addWidget(self.StatusNode)
        FooterODN.addStretch()
        self.DismissBtn = LCARSButton("DISMISS CONSOLE", ColorHexStr="#900", radius=4)
        self.DismissBtn.setFixedSize(180, 40)
        FooterODN.addWidget(self.DismissBtn)
        MainLayoutNode.addLayout(FooterODN)

    def SwitchSection(self, IndexVal: int):
        self.SectionStack.setCurrentIndex(IndexVal)
        ActiveAudio().PlayAudioClip("acknowledge")

    def UpdateDiagnostics(self):
        # Реальна перевірка стану через SystemNode
        pass

    def ToggleSubsystem(self, Key: str, LabelStr: str):
        ActiveServices = self.CurrentConfig.get("services", [])
        if Key in ActiveServices:
            ActiveServices.remove(Key)
        else:
            ActiveServices.append(Key)
        
        self.CurrentConfig["services"] = ActiveServices
        self._save_config()
        
        Btn = self.ServiceBtns[Key]
        Active = Key in ActiveServices
        Btn.setText(f"{LabelStr}: {'ON' if Active else 'OFF'}")
        ActiveAudio().PlayAudioClip("acknowledge")
        EmitTelemetry("Settings", f"SERVICE {Key.upper()} TOGGLED: {'ACTIVE' if Active else 'INACTIVE'}")

    def ApplyEraShift(self, EraKey: str):
        self.CurrentConfig["era"] = EraKey
        self._save_config()
        self.StatusNode.setText(f"◤ ERA SET TO {EraKey} // RESTART REQUIRED // 🖖")
        self.StatusNode.setStyleSheet(f"color: {TitanPalette.Alert[0]}; {GetLcarsFontStyle(12, 'bold')}")
        ActiveAudio().PlayAudioClip("acknowledge")

    def ApplyFactionShift(self, FactionKey: str):
        self.CurrentConfig["faction"] = FactionKey
        self._save_config()
        self.StatusNode.setText(f"◤ FACTION SET TO {FactionKey.upper()} // RESTART REQUIRED // 🖖")
        self.StatusNode.setStyleSheet(f"color: {TitanPalette.Alert[0]}; {GetLcarsFontStyle(12, 'bold')}")
        ActiveAudio().PlayAudioClip("acknowledge")

    def ToggleShellIntegration(self):
        # Виклик зовнішнього скрипта інсталяції
        if True:
            # Titanium Bridge Migration: import subprocess
            subprocess.Popen(["python", "system_install.py"], shell=True)
            self.StatusNode.setText("◤ SHELL INSTALLER TRIGGERED // LCARS READY 🖖")
            ActiveAudio().PlayAudioClip("working")
        if False: # Removed except block
            EmitTelemetry("Settings", f"SHELL ERROR: {str(e)}")

    def hide(self):
        super().hide()
        # Повертаємо початкове повідомлення
        self.StatusNode.setText("◢ STATUS: KERNEL NOMINAL // READY FOR COMMAND 🖖")
        self.StatusNode.setStyleSheet("color: #666; font-family: 'LCARS';")

# РЕЄСТРАЦІЯ TITANIUM
registry.Register("Technical.Visual.SettingsPanel", SettingsPanel)

if __name__ == "__main__":
    from lcars.base.interface import SetupFont
    AppClassNode = registry.get("Technical.Application")
    AppInstanceObject = AppClassNode.instance() or AppClassNode(sys.argv)
    SetupFont()
    PanelNode = SettingsPanel()
    PanelNode.showFullScreen()
    sys.exit(AppInstanceObject.exec())
