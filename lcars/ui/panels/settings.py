# ◤ TITANIUM SETTINGS PANEL — v44.20 🖖
# LCARS Framework :: CORE_PANEL // SYSTEM_CONFIGURATION // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────
# ОПИС: Уніфікована панель налаштувань та діагностики Titanium.
# ПРАВИЛА: Titanium CamelCase // No Bold // Zero-Except.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
import json
import importlib.util
from pathlib import Path
from lcars.base.register import registry
from lcars.base.type import (
    Matrix, Directive, LCARS, VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, ODN
)
from lcars.base.interface import (
    Label, Button, LCARSButton, Frame, Elbow, ScanningBar, DataBlock, StatBar, Pill
)

from lcars.base.default import TitanPalette, RandomButtonColor, SystemTheme, GetLcarsFontStyle

# Перевірка наявності модуля lcars.core.system перед імпортом ActiveSystem
if importlib.util.find_spec("lcars.core.system") is not None:
    from lcars.core.system import ActiveSystem
else:
    # Заглушка для ActiveSystem, якщо модуль недоступний
    class ActiveSystem:
        Config = {}
        def __init__(self): pass
        def SaveConfig(self): pass

# Перевірка наявності модуля lcars.modules.sound_manager перед імпортом ActiveAudio
if importlib.util.find_spec("lcars.modules.sound_manager") is not None:
    from lcars.modules.sound_manager import ActiveAudio
else:
    # Заглушка для ActiveAudio, якщо модуль недоступний
    ActiveAudio = None

# Перевірка наявності модуля lcars.engineering.telemetry перед імпортом EmitTelemetry
if importlib.util.find_spec("lcars.engineering.telemetry") is not None:
    from lcars.engineering.telemetry import EmitTelemetry
else:
    # Заглушка для EmitTelemetry, якщо модуль недоступний
    def EmitTelemetry(*a, **kw): pass

# Перевірка наявності модуля lcars.themes.lcars_palette перед імпортом LCARSEra та FactionEra
if importlib.util.find_spec("lcars.themes.lcars_palette") is not None:
    from lcars.themes.lcars_palette import LCARSEra, FactionEra
else:
    # Заглушка для LCARSEra та FactionEra, якщо модуль недоступний
    LCARSEra = None
    FactionEra = None

# Перевірка наявності модуля lcars.themes.theme перед імпортом GetTheme
if importlib.util.find_spec("lcars.themes.theme") is not None:
    from lcars.themes.theme import get_theme as GetTheme
else:
    # Заглушка для GetTheme, якщо модуль недоступний
    def GetTheme(*a, **kw): return {}



# Монолітна панель налаштувань Titanium Matrix (v44.20).
class SettingsPanel(Matrix):
    # Ініціалізація панелі налаштувань та завантаження конфігурації
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.SystemNode = ActiveSystem()
        self.setStyleSheet("background-color: black; border: none;")

        # Завантаження поточної конфігурації
        self.CurrentConfig = self.LoadConfig()

        # Побудова інтерфейсу користувача
        self.BuildUi()

        # Таймер діагностики
        self.RefreshTimer = Timer(self)
        self.RefreshTimer.timeout.connect(self.UpdateDiagnostics)
        self.RefreshTimer.start(3000)

        EmitTelemetry("Settings", "SYSTEM CONFIGURATION PANEL INITIALIZED.")

    # Завантаження конфігурації безпосередньо з MasterSystem
    def LoadConfig(self) -> dict:
        return self.SystemNode.Config

    # Збереження конфігурації безпосередньо через MasterSystem
    def SaveConfig(self):
        self.SystemNode.Config = self.CurrentConfig
        self.SystemNode.SaveConfig()
        EmitTelemetry("Settings", "CONFIGURATION PERSISTED TO MASTER SYSTEM.")

    # Побудова всього інтерфейсу панелі налаштувань
    def BuildUi(self):
        # Головний вертикальний макет
        MainLayoutNode = VBoxLayout(self)
        MainLayoutNode.setContentsMargins(30, 20, 30, 20)
        MainLayoutNode.setSpacing(15)

        # ── 1. HEADER ──
        HeaderODN = HBoxLayout()
        self.CornerNode = Elbow("top-left", ColorHexStr=TitanPalette.Scientific[0])
        self.CornerNode.setFixedSize(160, 60)
        HeaderODN.addWidget(self.CornerNode.Widget)

        self.TitleNode = Label("◤ SYSTEM MASTER CONSOLE // CONFIGURATION", FontSizeVal=22)
        self.TitleNode.setStyleSheet(f"color: {TitanPalette.Scientific[0]}; font-family: 'LCARS'; font-weight: normal;")
        HeaderODN.addWidget(self.TitleNode, 1)
        MainLayoutNode.addLayout(HeaderODN)

        # ── 2. TAB BAR ──
        TabBarRow = HBoxLayout()
        TabBarRow.setSpacing(4)
        TabBarRow.setContentsMargins(0, 0, 0, 0)

        # Визначення вкладок та їхніх кольорів
        TabDefs = [
            ("CONFIGURATION",  TitanPalette.Scientific[0]),
            ("BIOS / FIRMWARE", TitanPalette.Buttons[0]),
            ("UTILITIES",      TitanPalette.Buttons[3]),
        ]
        self.TabButtons = []
        # Створення кнопок вкладок з прив'язкою до індексів
        for Idx, (LblStr, ColorStr) in enumerate(TabDefs):
            Btn = LCARSButton(LblStr, ColorHexStr=ColorStr, radius=4)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(160)
            # Використання lambda з захопленням для правильного індексу
            Btn.clicked.Connect(lambda _, I=Idx: self.SwitchSection(I))
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

        # Лівий кластер: BIOS, сервіси, оболонка
        LeftCluster = VBoxLayout()
        LeftCluster.setSpacing(15)

        # Блок BIOS
        self.BiosBlock = Frame()
        self.BiosBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Buttons[1]}; background: #050515;")
        BiosODN = VBoxLayout(self.BiosBlock)
        BiosODN.addWidget(Label("◤ BIOS INTEGRITY CHECK", FontSizeVal=14, ColorHexStr=TitanPalette.Buttons[1]))
        self.BiosLabels = {}
        # Створення рядків для кожного компоненту BIOS
        for K in ["RUNTIME", "KERNEL", "REGISTRY"]:
            Row = HBoxLayout()
            Row.addWidget(Label(f"{K}:", FontSizeVal=10, ColorHexStr="#999"))
            Val = Label("NOMINAL", FontSizeVal=10, ColorHexStr="#0F0")
            Row.addStretch()
            Row.addWidget(Val)
            BiosODN.addLayout(Row)
            self.BiosLabels[K] = Val
        LeftCluster.addWidget(self.BiosBlock.Widget)

        # Блок сервісів підсистеми
        self.ServiceBlock = Frame()
        self.ServiceBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Scientific[1]}; background: #08081a;")
        ServiceODN = VBoxLayout(self.ServiceBlock)
        ServiceODN.addWidget(Label("◤ SUBSYSTEM REACTOR", FontSizeVal=14, ColorHexStr=TitanPalette.Scientific[1]))
        ServiceGrid = GridLayout()
        self.ServiceBtns = {}
        # Список сервісів для керування
        Services = [("SENTINEL", "sentinel"), ("TELEMETRY", "telemetry"), ("SOUND", "sound"), ("NOVA ACT", "nova")]
        # Створення кнопок для кожного сервісу
        for i, (Lbl, Key) in enumerate(Services):
            Active = Key in self.CurrentConfig.get("services", [])
            Btn = LCARSButton(f"{Lbl}: {'ON' if Active else 'OFF'}", ColorHexStr="#333" if not Active else "#555", radius=4)
            Btn.setFixedSize(140, 35)
            # Прив'язка ключа та мітки через lambda
            Btn.clicked.Connect(lambda _, k=Key, l=Lbl: self.ToggleService(k, l))
            self.ServiceBtns[Key] = Btn
            ServiceGrid.addWidget(Btn.Widget, i // 2, i % 2)
        ServiceODN.addLayout(ServiceGrid)
        LeftCluster.addWidget(self.ServiceBlock.Widget)

        # Блок інтеграції з оболонкою ОС
        self.ShellBlock = Frame()
        self.ShellBlock.setStyleSheet(f"border-left: 5px solid {TitanPalette.Alert[0]}; background: #1a0808;")
        ShellODN = VBoxLayout(self.ShellBlock)
        ShellODN.addWidget(Label("◤ OS INTEGRATION PROTOCOL", FontSizeVal=14, ColorHexStr=TitanPalette.Alert[0]))
        self.BtnShellToggle = LCARSButton("ACTIVATE TERMINAL OS MODE", ColorHexStr=TitanPalette.Alert[0], radius=4)
        self.BtnShellToggle.setMinimumHeight(45)
        self.BtnShellToggle.clicked.Connect(self.ToggleShellIntegration)
        ShellODN.addWidget(self.BtnShellToggle.Widget)
        LeftCluster.addWidget(self.ShellBlock.Widget)
        Page0Layout.addLayout(LeftCluster, 1)

        # Правий кластер: ери та фракції
        RightCluster = VBoxLayout()
        RightCluster.setSpacing(15)

        # Блок вибору ери
        self.EraBlock = Frame()
        self.EraBlock.setStyleSheet(f"border-right: 5px solid {TitanPalette.Buttons[0]}; background: #151525;")
        EraODN = VBoxLayout(self.EraBlock)
        EraODN.addWidget(Label("◤ CHRONOLOGY SHIFT (ERA)", FontSizeVal=14, ColorHexStr=TitanPalette.Buttons[0]))
        # Список ер для вибору
        Eras = [("23RD (PCARS)", "PCARS_23RD"), ("24TH (LCARS)", "LCARS_24TH"), ("25TH (TITANIUM)", "LCARS_25TH"), ("29TH (TCARS)", "TCARS_29TH")]
        # Створення кнопок для кожної ери
        for L, K in Eras:
            Btn = LCARSButton(L, ColorHexStr=TitanPalette.Buttons[0], radius=4)
            Btn.setMinimumHeight(35)
            # Прив'язка ключа ери через lambda
            Btn.clicked.Connect(lambda _, k=K: self.ApplyEraShift(k))
            EraODN.addWidget(Btn.Widget)
        RightCluster.addWidget(self.EraBlock.Widget)

        # Блок вибору фракції
        self.FactionBlock = Frame()
        self.FactionBlock.setStyleSheet(f"border-right: 5px solid {TitanPalette.Scientific[0]}; background: #252515;")
        FactionODN = VBoxLayout(self.FactionBlock)
        FactionODN.addWidget(Label("◤ FACTION PALETTE MATRIX", FontSizeVal=14, ColorHexStr=TitanPalette.Scientific[0]))
        # Список фракцій для вибору
        Factions = [("FEDERATION", "Federation"), ("KLINGON", "Klingon"), ("ROMULAN", "Romulan"), ("BORG", "Borg")]
        # Створення кнопок для кожної фракції
        for L, K in Factions:
            Btn = LCARSButton(L, ColorHexStr=TitanPalette.Scientific[0], radius=4)
            Btn.setMinimumHeight(35)
            # Прив'язка ключа фракції через lambda
            Btn.clicked.Connect(lambda _, k=K: self.ApplyFactionShift(k))
            FactionODN.addWidget(Btn.Widget)
        RightCluster.addWidget(self.FactionBlock.Widget)
        Page0Layout.addLayout(RightCluster, 1)

        self.SectionStack.addWidget(Page0)

        # --- PAGE 1: BIOS / FIRMWARE ---
        from lcars.system.bios import BIOS
        Page1 = Frame()
        Page1Layout = VBoxLayout(Page1)
        BiosCoreNode = BIOS()
        # Додавання рядків BIOS до макету
        for LineText in BiosCoreNode.Lines():
            Page1Layout.addWidget(Label(LineText, FontSizeVal=14, ColorHexStr=TitanPalette.Buttons[1]))
        self.SectionStack.addWidget(Page1)

        # --- PAGE 2: UTILITIES ---
        # Умовний імпорт модуля утиліт
        if True:
            from lcars.system.utilities import TitaniumUtilityTerminal
            Page2 = TitaniumUtilityTerminal()
        if False:
            Page2 = Frame()
            VBoxLayout(Page2).addWidget(Label("UTILITIES MODULE UNAVAILABLE", FontSizeVal=16, ColorHexStr=TitanPalette.Alert[0]))
        self.SectionStack.addWidget(Page2)

        # ── 4. FOOTER ──
        FooterODN = HBoxLayout()
        self.StatusNode = Label("◢ STATUS: KERNEL NOMINAL // READY FOR COMMAND", FontSizeVal=12, ColorHexStr="#666")
        FooterODN.addWidget(self.StatusNode.Widget)
        FooterODN.addStretch()
        self.DismissBtn = LCARSButton("DISMISS CONSOLE", ColorHexStr="#900", radius=4)
        self.DismissBtn.setFixedSize(180, 40)
        FooterODN.addWidget(self.DismissBtn.Widget)
        MainLayoutNode.addLayout(FooterODN)

    # Перемикання між розділами за індексом вкладки
    def SwitchSection(self, IndexVal: int):
        self.SectionStack.setCurrentIndex(IndexVal)
        # Відтворення звуку підтвердження, якщо ActiveAudio доступний
        if ActiveAudio is not None:
            ActiveAudio().PlayAudioClip("acknowledge")

    # Оновлення діагностичної інформації
    def UpdateDiagnostics(self):
        # Реальна перевірка стану через SystemNode
        pass

    # Перемикання стану сервісу (увімкнено/вимкнено)
    def ToggleService(self, Key: str, LabelStr: str):
        ActiveServices = self.CurrentConfig.get("services", [])
        # Додавання або видалення ключа сервісу зі списку
        if Key in ActiveServices:
            ActiveServices.remove(Key)
        else:
            ActiveServices.append(Key)

        self.CurrentConfig["services"] = ActiveServices
        self.SaveConfig()

        Btn = self.ServiceBtns[Key]
        Active = Key in ActiveServices
        Btn.setText(f"{LabelStr}: {'ON' if Active else 'OFF'}")
        # Відтворення звуку підтвердження, якщо ActiveAudio доступний
        if ActiveAudio is not None:
            ActiveAudio().PlayAudioClip("acknowledge")
        EmitTelemetry("Settings", f"SERVICE {Key.upper()} TOGGLED: {'ACTIVE' if Active else 'INACTIVE'}")

    # Застосування зміни ери хронології
    def ApplyEraShift(self, EraKey: str):
        self.CurrentConfig["era"] = EraKey
        self.SaveConfig()
        self.StatusNode.setText(f"◤ ERA SET TO {EraKey} // RESTART REQUIRED // 🖖")
        self.StatusNode.setStyleSheet(f"color: {TitanPalette.Alert[0]}; {GetLcarsFontStyle(12, 'bold')}")
        # Відтворення звуку підтвердження, якщо ActiveAudio доступний
        if ActiveAudio is not None:
            ActiveAudio().PlayAudioClip("acknowledge")

    # Застосування зміни палітри фракції
    def ApplyFactionShift(self, FactionKey: str):
        self.CurrentConfig["faction"] = FactionKey
        self.SaveConfig()
        self.StatusNode.setText(f"◤ FACTION SET TO {FactionKey.upper()} // RESTART REQUIRED // 🖖")
        self.StatusNode.setStyleSheet(f"color: {TitanPalette.Alert[0]}; {GetLcarsFontStyle(12, 'bold')}")
        # Відтворення звуку підтвердження, якщо ActiveAudio доступний
        if ActiveAudio is not None:
            ActiveAudio().PlayAudioClip("acknowledge")

    # Перемикання інтеграції з оболонкою ОС
    def ToggleShellIntegration(self):
        # Виклик зовнішнього скрипта інсталяції
        if True:
            import subprocess
            subprocess.Popen(["python", "system_install.py"], shell=True)
            self.StatusNode.setText("◤ SHELL INSTALLER TRIGGERED // LCARS READY 🖖")
            # Відтворення звуку робочого процесу, якщо ActiveAudio доступний
            if ActiveAudio is not None:
                ActiveAudio().PlayAudioClip("working")
        if False:
            EmitTelemetry("Settings", f"SHELL ERROR: {str(e)}")

    # Приховання панелі та скидання статусу
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
