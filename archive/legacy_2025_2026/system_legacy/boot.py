# Завантаження системи LCARS — оркестрація стадій boot
# Рівень: SYSTEM
# Ізолінійний чіп: 00-0001 (boot-контролер)

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import threading
from lcars.base.type import LCARS, Protocol
from lcars.base.signal import Observer, ODN
from lcars.base.interface import Screen
from lcars.system.software import LCARSFirmware, CreateFirmware, BootTarget

# Аварійний режим при критичних помилках завантаження
class EmergencyMode(Screen):
    def init(self, errorContext=None):
        # Ініціалізація аварійного режиму
        self.errorContext = errorContext or {}
        self.recoveryAttempts = 0
    
    def enter(self):
        # Вхід в аварійний режим — мінімальний UI для діагностики
        print("◤ EMERGENCY MODE ACTIVATED")
        print(f"Error: {self.errorContext.get('error', 'Unknown critical failure')}")
        print(f"Stage: {self.errorContext.get('stage', 'Unknown')}")
        self.showMinimalUi()
    
    def showMinimalUi(self):
        # Показує мінімальний аварійний інтерфейс через UI компонент
        from lcars.ui.screen.boot import LCARSBoot           
        app = LCARS.Application.instance()
        if not app:
            app = LCARS.Application(sys.argv)
            
        boot_screen = LCARSBoot(auto_start=False, emergency_mode=True)
        boot_screen.set_error_context(self.errorContext)
        
        # Callback для вибору режиму завантаження
        def on_mode_selected(mode, context):
            print(f"◤ User selected boot mode: {mode.value}")
            # Тут можна додати логіку для продовження завантаження
            # в обраному режимі
            boot_screen.set_boot_callback(on_mode_selected)
            boot_screen.showFullScreen()
            
        # Не блокуємо, EmergencyMode показує UI і продовжує
        # app.exec() не викликається тут
        # Fallback до консольного інтерфейсу якщо UI недоступний
        print("\n◤ LCARS EMERGENCY INTERFACE v1.0")
        print("1. System Diagnostics")
        print("2. Safe Mode Boot")
        print("3. Recovery Console")
        print("4. Power Off")
    
    def attemptRecovery(self):
        # Спроба відновлення системи
        self.recoveryAttempts += 1
        if self.recoveryAttempts > 3:
            return False
        return True

class QuickSystemCheck:
    # Швидка перевірка критичних компонентів системи перед завантаженням
    criticalNodes = [
        "Application",
        "Widget",
        "Timer",
        "Window",
        "Layout.VBox",
        "Protocol"
    ]
    
    def init(self):
        # Ініціалізація списків помилок та попереджень
        self.errors = []
        self.warnings = []
    
    def run(self):
        # Виконує швидку перевірку системи без затримок
        self.checkRegistryNodes()
        self.checkPythonVersion()
        self.checkPlatformSupport()
        return len(self.errors) == 0
    
    def checkRegistryNodes(self):
        # Перевіряє критичні вузли реєстру LCARS
        from lcars.base.register import registry
        nodeMap = {
            "Application": registry.Get("Interface.Application"),
            "Widget": registry.Get("Interface.Widget"),
            "Timer": registry.Get("Base.Timer"),
            "Window": registry.Get("Interface.Window"),
            "Layout.VBox": registry.Get("Interface.Layout.VBox"),
            "Protocol": Protocol
        }
        for nodeType, nodeRef in nodeMap.items():
            if not nodeRef:
                self.errors.append(f"Critical node {nodeType} not found")
    
    def checkPythonVersion(self):
        # Перевіряє версію Python (потрібна 3.8+)
        if sys.version_info < (3, 8):
            self.errors.append(f"Python {sys.version_info.major}.{sys.version_info.minor} not supported (need 3.8+)")
    
    def checkPlatformSupport(self):
        # Перевіряє підтримку платформи
        supported = {"win32", "linux", "darwin"}
        if sys.platform not in supported:
            self.warnings.append(f"Platform {sys.platform} may have limited support")
    
    def getReport(self):
        # Повертає звіт перевірки системи
        return {
            "status": "OK" if not self.errors else "FAILED",
            "errors": self.errors,
            "warnings": self.warnings
        }


class BootOrchestrator(threading.Thread):
    # Оркестратор завантаження LCARS — керує стадіями від UEFI до READY
    bootStageChanged = Observer(str, dict)
    systemReady = Observer()
    stages = [
        "UEFI_INIT",
        "POST",
        "BIOS_CHECK",
        "HARDWARE_INIT",
        "KERNEL_LOAD",
        "SERVICES_START",
        "UI_LAUNCH",
        "READY"
    ]
    
    def init(self, config=None):
        # Ініціалізація оркестратора завантаження
        super().__init__()
        self.config = config or {}
        self.currentStage = 0
        self.era = self.config.get("era", "LCARS_25TH")
        self.faction = self.config.get("faction", "federation")
        self.bootTarget = self.config.get("target", "desktop")
        self.skipFirmware = self.config.get("skip_firmware", False)
        self.firmware = None
        ODN.subscribe("Firmware.BootSelected", self.onFirmwareBootSelected)
        ODN.subscribe("BIOS.SaveAndExit", self.onBiosExit)
    
    def run(self):
        # Головний цикл завантаження системи
        self.runBootSequence()
    
    def runBootSequence(self):
        # Послідовність стадій завантаження LCARS
        if not self.runQuickCheck():
            return
        
        if not self.skipFirmware:
            self.advanceStage("INIT")
            self.launchFirmware()
            return
        
        self.advanceStage("KERNEL_LOAD")
        self.loadKernel()
        self.advanceStage("SERVICES_START")
        self.startServices()
        self.advanceStage("UI_LAUNCH")
        self.launchUi()
        self.advanceStage("READY")
        self.systemReady.Update()
    
    def advanceStage(self, stageName):
        # Переходить до наступної стадії завантаження
        self.currentStage = self.stages.index(stageName) if stageName in self.stages else 0
        progress = int((self.currentStage / len(self.stages)) * 100)
        self.bootStageChanged.Update(stageName, {"progress": progress, "era": self.era, "faction": self.faction})
        ODN.emit("Boot.Stage", {"stage": stageName, "progress": progress})
    
    def launchFirmware(self):
        # Запускає прошивку (firmware) з вибором завантаження
        self.firmware = CreateFirmware().initialize()
        self.firmware.executeBoot(autoSelect=True)
        self.firmware.bootEntrySelected.connect(self.onFirmwareEntrySelected)
    
    def loadKernel(self):
        # Завантажує ядро системи
        ODN.emit("Kernel.Load", {"era": self.era, "faction": self.faction})
    
    def startServices(self):
        # Запускає системні служби
        ODN.emit("Services.Start", {})
    
    def launchUi(self):
        # Запускає UI відповідно до target (desktop/terminal)
        if self.bootTarget == "desktop":
            ODN.emit("UI.LaunchDesktop", {"era": self.era, "faction": self.faction})
        elif self.bootTarget == "terminal":
            ODN.emit("UI.LaunchTerminal", {})
    
    def onFirmwareEntrySelected(self, entry, data):
        # Обробник вибору пункту завантаження в firmware
        ODN.emit("Firmware.BootSelected", {"entry": entry.name, "target": entry.target.value, "data": data})
        self.onFirmwareBootSelected(entry.target.value, data)
    
    def onFirmwareBootSelected(self, target, data):
        # Продовжує завантаження після вибору в firmware
        self.era = data.get("Config", {}).get("Era", self.era) if data else self.era
        self.faction = data.get("Config", {}).get("Faction", self.faction) if data else self.faction
        if target == BootTarget.DESKTOP.value:
            self.bootTarget = "desktop"
            self.loadKernel()
            self.startServices()
            self.launchUi()
            self.advanceStage("READY")
            self.systemReady.Update()
    
    def onBiosExit(self, data):
        # Продовжує завантаження після виходу з BIOS
        self.bootTarget = "desktop"
        self.loadKernel()
        self.startServices()
        self.launchUi()
        self.advanceStage("READY")
        self.systemReady.Update()
    
    def runQuickCheck(self):
        # Швидка перевірка системи перед продовженням завантаження
        checker = QuickSystemCheck()
        success = checker.run()
        report = checker.getReport()
        
        if report["warnings"]:
            for warning in report["warnings"]:
                ODN.emit("Boot.Warning", {"message": warning})
        
        if not success:
            ODN.emit("Boot.Error", {"errors": report["errors"]})
            emergency = EmergencyMode()
            emergency.init({
                "error": "System check failed",
                "stage": self.stages[self.currentStage],
                "details": report["errors"]
            })
            emergency.enter()
            return False
        
        return True


class Bootloader:
    # Головний завантажувач LCARS — точка входу для старту системи
    
    def init(self):
        # Ініціалізація завантажувача
        self.bootManager = None
        self.config = {}
        ODN.subscribe("Boot.Configure", self.onConfigure)
    
    def configure(self, era="LCARS_25TH", faction="federation", skipFirmware=False, target="desktop"):
        # Конфігурує параметри завантаження
        self.config = {
            "era": era,
            "faction": faction,
            "skip_firmware": skipFirmware,
            "target": target
        }
        return self
    
    def boot(self):
        # Запускає процес завантаження системи
        self.orchestrator = BootOrchestrator(self.config)
        self.orchestrator.init(self.config)
        self.orchestrator.bootStageChanged.Attach(self.onStageChanged)
        self.orchestrator.systemReady.Attach(self.onSystemReady)
        self.orchestrator.start()
        return self.orchestrator
    
    def onStageChanged(self, stage, data):
        # Обробник зміни стадії завантаження
        pass
    
    def onSystemReady(self):
        # Викликається коли система повністю готова
        ODN.emit("System.Ready", self.config)
    
    def onConfigure(self, data):
        # Обробник конфігурації через ODN
        self.configure(
            era=data.get("era", "LCARS_25TH"),
            faction=data.get("faction", "federation"),
            skipFirmware=data.get("skip_firmware", False),
            target=data.get("target", "desktop")
        )


def createBootloader():
    # Фабрична функція створення завантажувача
    return Bootloader()


def quickBoot(era="LCARS_25TH", faction="federation", target="desktop"):
    # Швидке завантаження без прошивки (firmware)
    loader = Bootloader()
    loader.init()
    loader.configure(era=era, faction=faction, skipFirmware=True, target=target)
    return loader.boot()


def fullBoot(era="LCARS_25TH", faction="federation"):
    # Повне завантаження з прошивкою та вибором
    loader = Bootloader()
    loader.init()
    loader.configure(era=era, faction=faction, skipFirmware=False, target="desktop")
    return loader.boot()


__all__ = [
    "BootOrchestrator",
    "Bootloader",
    "quickBoot",
    "fullBoot",
    "QuickSystemCheck",
    "EmergencyMode"
]
