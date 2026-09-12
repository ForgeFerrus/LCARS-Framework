from lcars.base.signal import Signal, ODN
from lcars.base.threading import Thread
from lcars.system.firmware import LCARSFirmware, CreateFirmware, BootTarget

class BootManager(Thread):
    BootStageChanged = Signal(str, dict)
    SystemReady = Signal()
    
    STAGES = [
        "UEFI_INIT",
        "POST",
        "BIOS_CHECK",
        "HARDWARE_INIT", 
        "KERNEL_LOAD",
        "SERVICES_START",
        "UI_LAUNCH",
        "READY"
    ]
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.currentStage = 0
        self.era = self.config.get("era", "LCARS_25TH")
        self.faction = self.config.get("faction", "federation")
        self.bootTarget = self.config.get("target", "desktop")
        self.skipFirmware = self.config.get("skip_firmware", False)
        self.firmware = None
        ODN.Subscribe("Firmware.BootSelected", self.onFirmwareBootSelected)
        ODN.Subscribe("BIOS.SaveAndExit", self.onBiosExit)
    
    def run(self):
        self.runBootSequence()
    
    def runBootSequence(self):
        if not self.skipFirmware:
            self.advanceStage("INIT")
            self.launchFirmware()
            return
        self.advanceStage("KERNEL_LOAD")
        self.loadKernel()
        self.advanceStage("SERVICES_START")
        self.startServices()
        self.advanceStage("UI_LAUNCH")
        self.launchUI()
        self.advanceStage("READY")
        self.SystemReady.emit()
    
    def advanceStage(self, stageName):
        self.currentStage = self.STAGES.index(stageName) if stageName in self.STAGES else 0
        progress = int((self.currentStage / len(self.STAGES)) * 100)
        self.BootStageChanged.emit(stageName, {"progress": progress, "era": self.era, "faction": self.faction})
        ODN.Emit("Boot.Stage", {"stage": stageName, "progress": progress})
    
    def launchFirmware(self):
        self.firmware = CreateFirmware().Initialize()
        self.firmware.ExecuteBoot(autoSelect=True)
        self.firmware.BootEntrySelected.connect(self.onFirmwareEntrySelected)
    
    def loadKernel(self):
        ODN.Emit("Kernel.Load", {"era": self.era, "faction": self.faction})
    
    def startServices(self):
        ODN.Emit("Services.Start", {})
    
    def launchUI(self):
        if self.bootTarget == "desktop":
            ODN.Emit("UI.LaunchDesktop", {"era": self.era, "faction": self.faction})
        elif self.bootTarget == "terminal":
            ODN.Emit("UI.LaunchTerminal", {})
    
    def onFirmwareEntrySelected(self, entry, data):
        ODN.Emit("Firmware.BootSelected", {"entry": entry.Name, "target": entry.Target.value, "data": data})
        self.onFirmwareBootSelected(entry.Target.value, data)
    
    def onFirmwareBootSelected(self, target, data):
        self.era = data.get("Config", {}).get("Era", self.era) if data else self.era
        self.faction = data.get("Config", {}).get("Faction", self.faction) if data else self.faction
        if target == BootTarget.DESKTOP.value:
            self.bootTarget = "desktop"
            self.loadKernel()
            self.startServices()
            self.launchUI()
            self.advanceStage("READY")
            self.SystemReady.emit()
    
    def onBiosExit(self, data):
        self.bootTarget = "desktop"
        self.loadKernel()
        self.startServices()
        self.launchUI()
        self.advanceStage("READY")
        self.SystemReady.emit()


class LCARSBootloader:
    def __init__(self):
        self.bootManager = None
        self.config = {}
        ODN.Subscribe("Boot.Configure", self.onConfigure)
    
    def configure(self, era="LCARS_25TH", faction="federation", skipFirmware=False, target="desktop"):
        self.config = {
            "era": era,
            "faction": faction,
            "skip_firmware": skipFirmware,
            "target": target
        }
        return self
    
    def boot(self):
        self.bootManager = BootManager(self.config)
        self.bootManager.BootStageChanged.connect(self.onStageChanged)
        self.bootManager.SystemReady.connect(self.onSystemReady)
        self.bootManager.start()
        return self.bootManager
    
    def onStageChanged(self, stage, data):
        pass
    
    def onSystemReady(self):
        ODN.Emit("System.Ready", self.config)
    
    def onConfigure(self, data):
        self.configure(
            era=data.get("era", "LCARS_25TH"),
            faction=data.get("faction", "federation"),
            skipFirmware=data.get("skip_firmware", False),
            target=data.get("target", "desktop")
        )


def createBootloader():
    return LCARSBootloader()


def quickBoot(era="LCARS_25TH", faction="federation", target="desktop"):
    loader = LCARSBootloader()
    loader.configure(era=era, faction=faction, skipFirmware=True, target=target)
    return loader.boot()


def fullBoot(era="LCARS_25TH", faction="federation"):
    loader = LCARSBootloader()
    loader.configure(era=era, faction=faction, skipFirmware=False, target="desktop")
    return loader.boot()
