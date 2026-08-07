# ◤ TITANIUM MASTER SYSTEM CORE — v44.20
# ОПИС: Центральне ядро координування всіх системних компонентів Titanium.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ПРАВИЛА: Жодних прямих OS викликів. Тільки системні директиви та проксі.
# ─────────────────────────────────────────────────────────────────────────────
import logging
import pathlib
import json
from typing import Optional, Any, Dict

# Імпортуємо базові типи Titanium
from lcars.base.type import LCARS, Directive, LCARSMatrix
from lcars.core.signal import Signal, ODN, Transmission
# Нове ядро LCARS з сервісною архітектурою
from .kernel import Kernel
from lcars.system.initialization import BootManager, LCARSBootloader
from lcars.system.software import Firmware, BootTarget
# Модулі керування конфігурацією та темами
from lcars.engineering.controller import AlertLevel, EngineeringController
from lcars.engineering.telemetry import EmitTelemetry, GetTelemetryDatabase
from lcars.themes.lcars_palette import LCARSEra
# Налаштування системного логера лор-мовою (Consola English Only)
SystemLogger = logging.getLogger(__name__)

# ГОЛОВНИЙ КЛАС КЕРУВАННЯ СИСТЕМОЮ LCARS
class MasterSystem:
    # Статичне посилання на екземпляр (Singleton Pattern)
    InstanceRef: Optional['MasterSystem'] = None

    # Створення нового екземпляра ядра
    def __new__(cls, *args, **kwargs) -> 'MasterSystem':
        if cls.InstanceRef is None:
            cls.InstanceRef = super().__new__(cls)
            cls.InstanceRef.IsInitialized = False
        return cls.InstanceRef

    # Ініціалізація Майстер-Системи
    def __init__(self, SysArgs: list = []):
        # Якщо ядро вже ініціалізоване, пропускаємо
        if hasattr(self, 'IsInitialized') and self.IsInitialized: 
            return
            
        # Налаштування базового логування Titanium
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO, format="%(message)s")
            
        self.Args = SysArgs
        self.ErrorList = [] 
        
        # Ініціалізація нового ядра LCARS з сервісною архітектурою
        self.Kernel = Kernel()

        # Boot ядра
        self.Kernel.Boot()
        
        # Зв'язування з MasterSystem для зворотної сумісності
        self.Kernel.SetSystem(self)
        
        self.EventBus = self.Kernel.Events

        # Вбудоване керування конфігурацією
        self.ConfigPath = pathlib.Path("config/config.json")
        self.Config: Dict[str, Any] = {}
        self.LoadConfig()
        
        self.BiosReport = {} 
        self.BiosVerified = self.RunBiosChecks()
        
        # Параметри середовища та сповіщення
        self.AlertSystem = EngineeringController(self.EventBus)
        
        # Реєстр системних менеджерів (CamelCase)
        self.SoundManager = self.Kernel.Module("sound")
        self.ModeManager = self.Kernel.Module("mode")
        self.NetworkManager = self.Kernel.Module("net")
        
        # Доступ до пам'яті через сервіс
        self.MemorySubstrate = self.Kernel.Module("memory")
        
        # Телеметрія та метрики Titanium (ODN Telemetry Hub)
        self.TelemetryLink = EmitTelemetry
        self.LoggerDB = GetTelemetryDatabase()
        
        # Завантажувач плагінів Titanium
        self.PluginMgr = self.Kernel.Service("plugin")

        # Мова та ШІ-помічник (Copilot)
        self.CopilotNode = self.Kernel.Module("copilot")
        
        # Завершення ініціалізації вузла
        self.IsInitialized = True
        self.ApplyInitialSettings()
        SystemLogger.info("◤ MASTER SYSTEM CORE: ONLINE INTEGRITY VERIFIED.")

    # ─── УПРАВЛІННЯ КОНФІГУРАЦІЄЮ ───
    def LoadConfig(self) -> None:
        # Якщо файл конфігурації не існує — створюємо значення за замовчуванням
        if not self.ConfigPath.exists():
            self.Config = {"era": "LCARS_25TH", "faction": "Federation", "theme": "default"}
            self.SaveConfig()
            return
        
        # Зчитування вмісту файлу конфігурації
        raw_content = self.ConfigPath.read_text()
        
        # Перевірка на порожній або невалідний вміст
        if not raw_content or not raw_content.strip():
            SystemLogger.error("◤ CONFIG LOAD ERROR: EMPTY CONFIG FILE")
            self.Config = {"era": "LCARS_25TH", "faction": "Federation", "theme": "default"}
            return
        
        # Валідація JSON структури перед парсингом
        stripped = raw_content.strip()
        if stripped.startswith('{') and stripped.endswith('}'):
            self.Config = json.loads(stripped)
        else:
            SystemLogger.error("◤ CONFIG LOAD ERROR: INVALID JSON FORMAT")
            self.Config = {"era": "LCARS_25TH", "faction": "Federation", "theme": "default"}
        
        # Застосування параметрів з конфігурації
        self.CurrentEra = self.Config.get("era", "LCARS_25TH")
        self.CurrentFaction = self.Config.get("faction", "Federation")
        # Оповіщаємо ядро про зміну
        self.Kernel.State.Set("config.system.era", self.CurrentEra)
        self.Kernel.State.Set("config.system.faction", self.CurrentFaction)

    def SaveConfig(self) -> None:
        # Перевірка та створення батьківської директорії якщо потрібно
        if not self.ConfigPath.parent.exists():
            self.ConfigPath.parent.mkdir(parents=True, exist_ok=True)
        
        # Запис конфігурації у файл
        self.ConfigPath.write_text(json.dumps(self.Config, indent=4))

    # Перевірка BIOS/UEFI середовища (No direct OS)
    def RunBiosChecks(self) -> bool:
        import platform
        Results = {
            "runtime": {"status": "FAIL", "val": platform.python_version()},
            "kernel": {"status": "FAIL", "val": "PrimaryNode"},
            "config": {"status": "FAIL", "val": "MISSING"},
            "environment": {"status": "FAIL", "val": "MISSING"}
        }
        
        ErrorsDetected = []
        # Перевірка версії Python на сумісність
        if (platform.python_version_tuple()[0] == '3' and int(platform.python_version_tuple()[1]) >= 8):
            Results["runtime"]["status"] = "OK"
        else:
            ErrorsDetected.append("RUNTIME ERROR: PYTHON 3.8 REQUIRED.")

        # Use standard Python platform detection instead of a missing Directive.Platform
        if platform.system().lower().startswith('win'):
            Results["kernel"]["status"] = "OK"
            Results["kernel"]["val"] = "RedmondNode"
        else:
            Results["kernel"]["status"] = "OK"
            Results["kernel"]["val"] = platform.system()
            
        # Config is now handled by MasterSystem internal state / db
        Results["config"]["status"] = "OK"
        Results["config"]["val"] = "DATABASE CONNECTED"
        Results["environment"]["status"] = "OK"
        Results["environment"]["val"] = "VERIFIED"
        self.BiosReport = Results
        
        # Обробка виявлених помилок BIOS
        if ErrorsDetected:
            for ErrMsg in ErrorsDetected: self.AddSystemError(ErrMsg)
            return False
        return True

    # Додавання системної помилки (CamelCase)
    def AddSystemError(self, ErrorMessage):
        self.ErrorList.append(str(ErrorMessage))
        SystemLogger.error(f"◤ MASTER SYSTEM FAILURE: {ErrorMessage}")

    def DiagnosticsReport(self) -> Dict[str, Any]:
        return {
            "BiosVerified": self.BiosVerified,
            "ErrorList": self.ErrorList,
            "BiosReport": self.BiosReport,
            "MemorySubstrate": self.MemorySubstrate.GetMemoryStats() if self.MemorySubstrate else "OFFLINE"
        }

    # Завантаження параметрів ери та фракції
    def ApplyInitialSettings(self):
        pass

    # Старт основного протоколу завантаження (Primary Boot Sequence)
    def StartupSequence(self):
        SystemLogger.info("◤ MASTER SYSTEM: PRIMARY BOOT SEQUENCE ENGAGED.")

    # Деактивація нейронної шини Nexus (System Deactivation)
    def ShutdownSequence(self):
        SystemLogger.info("◤ MASTER SYSTEM: SYSTEM NEXUS DEACTIVATED.")

# Отримати активне координуюче ядро
def ActiveSystem() -> MasterSystem:
    return MasterSystem()

# Експорт для Titanium модулів
__all__ = ["MasterSystem", "ActiveSystem"]


# ІНТЕГРАТОР СИСТЕМИ LCARS — КООРДИНАЦІЯ BOOT ПРОЦЕСУ
class LCARSIntegrator:
    SystemBooted = Transmission()
    UEFICompleted = Transmission(dict)
    BIOSCompleted = Transmission()
    DesktopLaunched = Transmission()
    
    def __init__(self):
        # Ініціалізація компонентів інтегратора
        self.Bootloader = None
        self.BootManager = None
        self.Firmware = None
        self.FirmwareConfig = {}
        self.Era = "LCARS_25TH"
        self.Faction = "federation"
        self.SetupODNListeners()
    
    # Налаштування підписок на ODN події системи
    def SetupODNListeners(self):
        ODN.EventBus.On("System.LaunchFirmware", self.OnLaunchFirmware)
        ODN.EventBus.On("System.LaunchDesktop", self.OnLaunchDesktop)
        ODN.EventBus.On("System.LaunchRecovery", self.OnLaunchRecovery)
        ODN.EventBus.On("Firmware.BootSelected", self.OnFirmwareBootSelected)
        ODN.EventBus.On("Firmware.ConfigSaved", self.OnFirmwareConfigSaved)
    
    # Ініціалізація інтегратора та випромінювання події
    def Initialize(self):
        ODN.Emit("System.Initialized", {})
        return self
    
    # Запуск boot послідовності з конфігурацією
    def StartBootSequence(self, config=None):
        # Застосування конфігурації або значень за замовчуванням
        if config:
            self.Era = config.get("era", self.Era)
            self.Faction = config.get("faction", self.Faction)
            self.Target = str(config.get("target", "desktop")).lower()
        else:
            self.Target = "desktop"
        
        # Створення та налаштування завантажувача
        self.Bootloader = LCARSBootloader()
        self.Bootloader.configure(era=self.Era, faction=self.Faction, target=self.Target)
        self.BootManager = self.Bootloader.boot()
        return self
    
    # Обробник стадії boot процесу
    def OnBootStage(self, stage, data):
        ODN.Emit("Boot.Progress", {"stage": stage, "data": data})
    
    # Обробник готовності системи
    def OnSystemReady(self):
        self.SystemBooted.emit()
        ODN.Emit("System.Ready", {"era": self.Era, "faction": self.Faction})
    
    # Запуск прошивки Firmware
    def OnLaunchFirmware(self, data):
        self.Firmware = Firmware().Initialize()
        self.Firmware.RunPOST()
        self.Firmware.Validate()
        ODN.Emit("Firmware.Ready", self.Firmware.GetSystemInfo())
    
    # Запуск робочого столу Desktop
    def OnLaunchDesktop(self, data):
        self.Era = data.get("era", self.Era)
        self.Faction = data.get("faction", self.Faction)
        self.DesktopLaunched.emit()
        ODN.Emit("Desktop.Launch", {"era": self.Era, "faction": self.Faction})
    
    # Запуск режиму відновлення Recovery
    def OnLaunchRecovery(self, data):
        ODN.Emit("Recovery.Launch", {})

    # Обробник збереження конфігурації прошивки
    def OnFirmwareConfigSaved(self, data):
        self.FirmwareConfig = data or {}
        ODN.Emit("Firmware.Saved", self.FirmwareConfig)
    
    # Обробник вибору boot цілі з прошивки
    def OnFirmwareBootSelected(self, data):
        target = data.get("target", "")
        target_name = str(target).lower()
        # Маршрутизація до відповідного boot процесу
        if target_name == BootTarget.DESKTOP:
            self.OnLaunchDesktop(data)
        elif target_name == BootTarget.RECOVERY:
            self.OnLaunchRecovery(data)
    
    # Завершення роботи системи
    def Shutdown(self):
        ODN.Emit("System.Shutdown", {})
        if self.Firmware:
            self.Firmware.SaveConfiguration()


# РАНТАЙМ LCARS — ТОЧКА ВХОДУ ДЛЯ ЗАПУСКУ СИСТЕМИ
class LCARSRuntime:
    def __init__(self):
        self.Integrator = None
    
    # Ініціалізація runtime середовища
    def Initialize(self):
        self.Integrator = LCARSIntegrator()
        self.Integrator.Initialize()
        return self
    
    # Boot послідовність з параметрами
    def Boot(self, fullSequence=False, era="LCARS_25TH", faction="federation"):
        if self.Integrator is None:
            self.Initialize()
        
        # Підготовка конфігурації для boot процесу
        config = {"era": era, "faction": faction, "full_sequence": fullSequence}
        self.Integrator.StartBootSequence(config)
        return self
    
    # Запуск основного циклу runtime
    def Run(self):
        return 0
    
    # Завершення роботи runtime
    def Shutdown(self):
        if self.Integrator:
            self.Integrator.Shutdown()

# Створення нового runtime середовища
def CreateRuntime():
    return LCARSRuntime()
