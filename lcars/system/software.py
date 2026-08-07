# LCARS firmware layer.
# Цей модуль відповідає за логіку "прошивки" (Firmware) системи LCARS.
# Він симулює низькорівневі процеси POST (Power-On Self-Test), 
# конфігурацію обладнання та вибір цілі для завантаження системи.

from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from lcars.base.version import getVersion
from lcars.core.signal import Observer
from lcars.base.type import LCARS

# Константи для визначення цілей завантаження.
# Вказують системі, в який режим їй потрібно перейти після ініціалізації.
class BootTarget:
    DESKTOP = "desktop"    # Стандартний графічний інтерфейс LCARS
    RECOVERY = "recovery"  # Режим відновлення (наприклад, для усунення збоїв)
    BIOS = "bios"          # Вхід в налаштування конфігурації
    SHELL = "shell"        # Командний рядок (термінал)
    AI_BOOT = "ai_boot"    # Автономний запуск AI ядра

# Представляє окремий запис у меню завантаження (Boot Menu).
@dataclass
class BootEntry:
    Name: str
    Description: str
    Target: str
    Priority: int = 1
    IsDefault: bool = False
    Secure: bool = True

# Симулює профіль апаратного забезпечення бортового комп'ютера.
# Містить базову інформацію про процесор, пам'ять та периферію.
@dataclass
class HardwareProfile:
    Cpu: str = "LCARS-Core-Ti"
    MemoryTotal: int = 32768
    StorageDevices: List[Dict[str, Any]] = field(default_factory=list)
    NetworkInterfaces: List[Dict[str, Any]] = field(default_factory=list)
# Клас конфігурації прошивки.
# Зберігає версію системи, поточну мову, параметри обладнання та список доступних систем для завантаження.
class FirmwareConfig:
    def __init__(self):
        self.Version = getVersion()
        self.BuildDate = datetime.now().strftime("%Y.%m.%d")
        self.Language = "ukrainian"
        self.DefaultBoot = BootTarget.DESKTOP
        self.Hardware = HardwareProfile()
        self.BootEntries = [
            BootEntry("TITANIUM-OS", "Primary LCARS Interface", BootTarget.DESKTOP, 1, True),
            BootEntry("AI-AUTONOMOUS", "AI direct boot", BootTarget.AI_BOOT, 2, False),
            BootEntry("RECOVERY", "Maintenance mode", BootTarget.RECOVERY, 3, False),
        ]
    # Перетворює конфігурацію в словник для подальшого збереження в JSON
    def ToDict(self) -> Dict[str, Any]:
        return {
            "Version": self.Version,
            "BuildDate": self.BuildDate,
            "Language": self.Language,
            "DefaultBoot": self.DefaultBoot,
            "Hardware": self.Hardware.__dict__,
            "Entries": [Entry.__dict__ for Entry in self.BootEntries],
        }


class Firmware(LCARS):
    # Головний клас керування прошивкою.
    # Відповідає за проходження всіх етапів завантаження (INIT, POST, VALIDATE тощо)
    # та вибір фінальної цілі для ядра системи.
    STAGES = ["INIT", "POST", "AI_ENGINE", "VALIDATE", "LOAD", "READY"]

    def __init__(self, ConfigPath: Optional[str] = None):
        super().__init__(Id="firmware_core")
        
        # Сигнали (Transmission/Observer) для повідомлення системи про проходження етапів
        self.ConfigLoaded = Observer(object)
        self.PostCompleted = Observer(bool, list)
        self.StageChanged = Observer(str, dict)
        self.SystemReady = Observer()
        self.ValidationFailed = Observer()
        self.BootEntrySelected = Observer(object, dict)
        
        # Шлях до конфігураційного файлу прошивки
        self.ConfigPath = ConfigPath or str(Path.home() / ".lcars" / "firmware.json")
        self.Config = FirmwareConfig()
        self.CurrentStage = "INIT"
        self.Results: List[Dict[str, Any]] = []

    def Initialize(self) -> "Firmware":
        # Запуск початкової ініціалізації: завантаження налаштувань та імітація підключення пристроїв
        self.AdvanceStage("INIT")
        self.LoadConfiguration()
        self.Config.Hardware.StorageDevices = [{"ID": "ISO-0", "Status": "OK"}]
        self.Config.Hardware.NetworkInterfaces = [{"ID": "ODN-1", "Status": "Active"}]
        return self

    def RunPOST(self) -> bool:
        # Power-On Self-Test (POST)
        # Симулює перевірку основних вузлів системи: процесора, пам'яті та оптичної мережі (ODN)
        self.AdvanceStage("POST")
        self.Results = [
            {"Node": "CPU", "Status": "OK"},
            {"Node": "MEM", "Status": "OK"},
            {"Node": "ODN", "Status": "OK"},
        ]
        self.PostCompleted.Update(True, self.Results)
        return True

    def InitAiEngine(self) -> bool:
        # Ініціалізація інтелектуального ядра на етапі завантаження
        self.AdvanceStage("AI_ENGINE")
        return True

    def Validate(self) -> bool:
        # Перевірка цілісності системи
        self.AdvanceStage("VALIDATE")
        return True

    def AdvanceStage(self, Stage: str):
        # Перехід на наступний етап завантаження з оновленням прогресу
        self.CurrentStage = Stage
        if Stage in self.STAGES:
            Progress = int((self.STAGES.index(Stage) / max(1, len(self.STAGES) - 1)) * 100)
            self.StageChanged.Update(Stage, {"Progress": Progress})

    def LoadConfiguration(self):
        # Зчитування файлу конфігурації прошивки, якщо він існує
        ConfigPath = Path(self.ConfigPath)
        if ConfigPath.exists() and ConfigPath.is_file():
            with open(ConfigPath, "r", encoding="utf-8") as Source:
                Data = json.load(Source)
            if isinstance(Data, dict):
                self.Config.Version = Data.get("Version", self.Config.Version)
                self.Config.Language = Data.get("Language", self.Config.Language)
                self.Config.DefaultBoot = Data.get("DefaultBoot", self.Config.DefaultBoot)
        self.ConfigLoaded.Update(self.Config)

    def ExecuteBoot(self, autoSelect: bool = False) -> bool:
        # Повний цикл завантаження
        if not self.RunPOST():
            return False
        if not self.InitAiEngine():
            return False
        if not self.Validate():
            return False

        self.AdvanceStage("LOAD")
        self.AdvanceStage("READY")

        # Якщо включено автовибір, одразу обираємо перший запис у списку завантаження
        if autoSelect:
            DefaultEntry = self.Config.BootEntries[0]
            self.BootEntrySelected.Update(DefaultEntry, {"Config": self.Config.ToDict()})

        self.SystemReady.Update()
        return True

    def GetSystemInfo(self) -> Dict[str, Any]:
        return self.Config.ToDict()

    def SaveConfiguration(self):
        # Збереження налаштувань прошивки на диск
        Target = Path(self.ConfigPath)
        Target.parent.mkdir(parents=True, exist_ok=True)
        with open(Target, "w", encoding="utf-8") as Output:
            json.dump(self.Config.ToDict(), Output, indent=2)

def QuickBoot() -> Firmware:
    # Швидкий запуск: ініціалізуємо і одразу завантажуємо дефолтну ціль
    Loader = Firmware().Initialize()
    Loader.ExecuteBoot(autoSelect=True)
    return Loader

__all__ = [
    "BootTarget",
    "BootEntry",
    "HardwareProfile",
    "FirmwareConfig",
    "Firmware",
    "QuickBoot",
]
