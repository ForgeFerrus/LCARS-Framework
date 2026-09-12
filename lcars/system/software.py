# ◤ TITANIUM SYSTEM FIRMWARE & SOFTWARE MANAGER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/software.py
# ОПИС: Низькорівнева прошивка (Firmware), таблиці стану та дескриптори
#       завантаження й апаратного профілю системи LCARS.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.info import Version
from lcars.core.signal import Transmission

# ═════════════════════════════════════════════════════════════════════
# 1. СИСТЕМНІ СТАНИ ТА ЦІЛІ ЗАВАНТАЖЕННЯ
# ═════════════════════════════════════════════════════════════════════
class StateItem(str):
    # Канонічний елемент стану з властивостями Name та Value
    @property
    def Name(self) -> str:
        return str(self)

    @property
    def Value(self) -> str:
        return str(self)

class SystemState(LCARS):
    # Канонічні операційні стани ядра LCARS
    OFF           = StateItem("OFF")
    BOOTING       = StateItem("BOOTING")
    READY         = StateItem("READY")
    RUNNING       = StateItem("RUNNING")
    DEGRADED      = StateItem("DEGRADED")
    SHUTTING_DOWN = StateItem("SHUTTING_DOWN")
    ERROR         = StateItem("ERROR")

class BootTarget(LCARS):
    # Константи цілей завантаження зорельота
    DESKTOP  = "desktop"
    RECOVERY = "recovery"
    BIOS     = "bios"
    SHELL    = "shell"
    AI_BOOT  = "ai_boot"

# ═════════════════════════════════════════════════════════════════════
# 2. ДЕСКРИПТОРИ АПАРАТУРИ ТА ПРОШИВКИ
# ═════════════════════════════════════════════════════════════════════
class BootEntry(LCARS):
    # Запис у таблиці завантаження UEFI
    def __init__(self, Name: str, Description: str, Target: str, Priority: int = 1, IsDefault: bool = False, Secure: bool = True):
        super().__init__(Id=f"BootEntry.{Name}")
        self.Name = Name
        self.Description = Description
        self.Target = Target
        self.Priority = Priority
        self.IsDefault = IsDefault
        self.Secure = Secure

class HardwareProfile(LCARS):
    # Опис апаратного профілю вузла зорельота
    def __init__(self, Cpu: str = "LCARS-Core-Ti", MemoryTotal: int = 32768, StorageDevices: list | None = None, NetworkInterfaces: list | None = None):
        super().__init__(Id="HardwareProfile")
        self.Cpu = Cpu
        self.MemoryTotal = MemoryTotal
        self.StorageDevices = StorageDevices or []
        self.NetworkInterfaces = NetworkInterfaces or []

class FirmwareConfig(LCARS):
    # Параметри конфігурації прошивки зорельота
    def __init__(self, ConfigVersion: str | None = None, DefaultBoot: str = BootTarget.DESKTOP, Language: str = "uk", BootDelay: int = 3, SecureBoot: bool = True):
        super().__init__(Id="FirmwareConfig")
        self.Version = ConfigVersion or Version.Release
        self.DefaultBoot = DefaultBoot
        self.Language = Language
        self.BootDelay = BootDelay
        self.SecureBoot = SecureBoot
        self.BootEntries: list[BootEntry] = [
            BootEntry("LCARS-MAIN", "Головний графічний інтерфейс LCARS", BootTarget.DESKTOP, Priority=1, IsDefault=True),
            BootEntry("LCARS-SHELL", "Консольний інтерфейс прямого доступу", BootTarget.SHELL, Priority=2),
            BootEntry("BIOS-SETUP", "Утиліта конфігурації прошивки та чіпів", BootTarget.BIOS, Priority=3),
            BootEntry("AI-AUTONOMOUS", "Автономне середовище AI розробника", BootTarget.AI_BOOT, Priority=4),
            BootEntry("RECOVERY", "Аварійне відновлення ядра", BootTarget.RECOVERY, Priority=5, Secure=False),
        ]
        self.Hardware = HardwareProfile()

    def ToDict(self) -> dict:
        # Експорт параметрів прошивки у словник
        return {
            "Version": self.Version,
            "DefaultBoot": self.DefaultBoot,
            "Language": self.Language,
            "BootDelay": self.BootDelay,
            "SecureBoot": self.SecureBoot,
            "Hardware": {
                "Cpu": self.Hardware.Cpu,
                "MemoryTotal": self.Hardware.MemoryTotal,
                "StorageDevices": list(self.Hardware.StorageDevices),
                "NetworkInterfaces": list(self.Hardware.NetworkInterfaces),
            },
            "BootEntries": [
                {
                    "Name": Entry.Name,
                    "Description": Entry.Description,
                    "Target": Entry.Target,
                    "Priority": Entry.Priority,
                    "IsDefault": Entry.IsDefault,
                    "Secure": Entry.Secure,
                }
                for Entry in self.BootEntries
            ],
        }

# ═════════════════════════════════════════════════════════════════════
# 3. КЕРУВАННЯ ПРОШИВКОЮ (FIRMWARE CONTROLLER)
# ═════════════════════════════════════════════════════════════════════
class Firmware(LCARS):
    # Головний контролер життєвого циклу прошивки
    SystemVersion = Version.Release

    def __init__(self, ConfigPathStr: str = "config/firmware.json"):
        super().__init__(Id="Firmware")
        self.ConfigPath = ConfigPathStr
        self.Config = FirmwareConfig()
        self.State = SystemState.OFF
        self.PostCompleted = False
        self.AiInitialized = False
        self.Stage = "OFF"

        self.StateChanged = Transmission(SystemState)
        self.PostProgress = Transmission(str, bool)
        self.ConfigLoaded = Transmission(FirmwareConfig)
        self.BootEntrySelected = Transmission(BootEntry, dict)
        self.SystemReady = Transmission()

    def Initialize(self) -> Firmware:
        # Початкова ініціалізація прошивки
        self.State = SystemState.BOOTING
        self.StateChanged.Emit(self.State)
        self.LoadConfiguration()
        return self

    def RunPOST(self) -> bool:
        # Виконання низькорівневих перевірок прошивки
        self.AdvanceStage("POST")
        Checks = [
            ("Core Memory Integrity", True),
            ("Isolinear Bus Synchronization", True),
            ("ODN Transmission Links", True),
            ("Optical Substrate Transceiver", True),
        ]
        for Name, Status in Checks:
            self.PostProgress.Emit(Name, Status)
            if not Status:
                self.State = SystemState.ERROR
                self.StateChanged.Emit(self.State)
                return False
        self.PostCompleted = True
        return True

    def InitAiEngine(self) -> bool:
        # Ініціалізація нейромережевого контуру
        self.AdvanceStage("AI_INIT")
        self.AiInitialized = True
        return True

    def Validate(self) -> bool:
        # Перевірка валідності проходження перевірок
        return self.PostCompleted and self.AiInitialized

    def AdvanceStage(self, NewStage: str) -> None:
        # Зміна поточної стадії запуску
        self.Stage = NewStage

    def LoadConfiguration(self) -> None:
        # Завантаження конфігурації з файлу
        PathModule = LCARS.System.Path
        ConfigPathObj = PathModule(self.ConfigPath)
        if ConfigPathObj.exists() and ConfigPathObj.is_file():
            JsonModule = LCARS.Import("json")
            Content = ConfigPathObj.read_text(encoding="utf-8", errors="replace")
            Data = JsonModule.loads(Content) if JsonModule else {}
            if isinstance(Data, dict):
                self.Config.Version = Data.get("Version", self.Config.Version)
                self.Config.Language = Data.get("Language", self.Config.Language)
                self.Config.DefaultBoot = Data.get("DefaultBoot", self.Config.DefaultBoot)
        self.ConfigLoaded.Emit(self.Config)

    def ExecuteBoot(self, AutoSelect: bool = False) -> bool:
        # Виконання повного ланцюга завантаження прошивки
        if not self.RunPOST():
            return False
        if not self.InitAiEngine():
            return False
        if not self.Validate():
            return False

        self.AdvanceStage("LOAD")
        self.AdvanceStage("READY")

        if AutoSelect and self.Config.BootEntries:
            DefaultEntry = self.Config.BootEntries[0]
            self.BootEntrySelected.Emit(DefaultEntry, {"Config": self.Config.ToDict()})

        self.SystemReady.Emit()
        return True

    def GetSystemInfo(self) -> dict:
        # Отримання повної системної інформації прошивки
        return self.Config.ToDict()

    def SaveConfiguration(self) -> None:
        # Збереження поточної конфігурації прошивки
        PathModule = LCARS.System.Path
        Target = PathModule(self.ConfigPath)
        Target.parent.mkdir(parents=True, exist_ok=True)
        JsonModule = LCARS.Import("json")
        if JsonModule:
            Target.write_text(JsonModule.dumps(self.Config.ToDict(), indent=2), encoding="utf-8")

class SoftwareAccess(LCARS):
    # Фасад швидкого доступу до запуску прошивки
    @staticmethod
    def QuickBoot() -> Firmware:
        Loader = Firmware().Initialize()
        Loader.ExecuteBoot(AutoSelect=True)
        return Loader

def CreateFirmware(ConfigPathStr: str = "config/firmware.json") -> Firmware:
    # Фабрична функція створення екземпляра прошивки
    return Firmware(ConfigPathStr=ConfigPathStr)

QuickBoot = SoftwareAccess.QuickBoot

__all__ = [
    "SystemState",
    "StateItem",
    "BootTarget",
    "BootEntry",
    "HardwareProfile",
    "FirmwareConfig",
    "Firmware",
    "CreateFirmware",
    "SoftwareAccess",
    "QuickBoot",
]
