# LCARS FRAMEWORK v0.9.0-PRE
# ◤ BOOT MANAGEMENT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Управління завантаженням системи - BootManager, Bootloader
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from lcars.base.type import LCARS, Directive
from lcars.base.signal import Signal, ODN
from lcars.system.software import LCARSFirmware, CreateFirmware, BootTarget


class BootManager(Directive.Thread):
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
    
    def __init__(self, Config=None):
        super().__init__()
        self.Config = Config or {}
        self.CurrentStage = 0
        self.Era = self.Config.get("era", "LCARS_25TH")
        self.Faction = self.Config.get("faction", "federation")
        self.BootTarget = self.Config.get("target", "desktop")
        self.SkipFirmware = self.Config.get("skip_firmware", False)
        self.Firmware = None
        ODN.Subscribe("Firmware.BootSelected", self.OnFirmwareBootSelected)
        ODN.Subscribe("BIOS.SaveAndExit", self.OnBiosExit)
    
    def run(self):
        self.RunBootSequence()
    
    def RunBootSequence(self):
        if not self.SkipFirmware:
            self.AdvanceStage("INIT")
            self.LaunchFirmware()
            return
        self.AdvanceStage("KERNEL_LOAD")
        self.LoadKernel()
        self.AdvanceStage("SERVICES_START")
        self.StartServices()
        self.AdvanceStage("UI_LAUNCH")
        self.LaunchUI()
        self.AdvanceStage("READY")
        self.SystemReady.emit()
    
    def AdvanceStage(self, StageName):
        self.CurrentStage = self.STAGES.index(StageName) if StageName in self.STAGES else 0
        Progress = int((self.CurrentStage / len(self.STAGES)) * 100)
        self.BootStageChanged.emit(StageName, {"progress": Progress, "era": self.Era, "faction": self.Faction})
        ODN.Emit("Boot.Stage", {"stage": StageName, "progress": Progress})
    
    def LaunchFirmware(self):
        self.Firmware = CreateFirmware().Initialize()
        self.Firmware.ExecuteBoot(autoSelect=True)
        self.Firmware.BootEntrySelected.connect(self.OnFirmwareEntrySelected)
    
    def LoadKernel(self):
        ODN.Emit("Kernel.Load", {"era": self.Era, "faction": self.Faction})
    
    def StartServices(self):
        ODN.Emit("Services.Start", {})
    
    def LaunchUI(self):
        if self.BootTarget == "desktop":
            ODN.Emit("UI.LaunchDesktop", {"era": self.Era, "faction": self.Faction})
        elif self.BootTarget == "terminal":
            ODN.Emit("UI.LaunchTerminal", {})
    
    def OnFirmwareEntrySelected(self, Entry, Data):
        ODN.Emit("Firmware.BootSelected", {"entry": Entry.Name, "target": Entry.Target.value, "data": Data})
        self.OnFirmwareBootSelected(Entry.Target.value, Data)
    
    def OnFirmwareBootSelected(self, Target, Data):
        self.Era = Data.get("Config", {}).get("Era", self.Era) if Data else self.Era
        self.Faction = Data.get("Config", {}).get("Faction", self.Faction) if Data else self.Faction
        if Target == BootTarget.DESKTOP.value:
            self.BootTarget = "desktop"
            self.LoadKernel()
            self.StartServices()
            self.LaunchUI()
            self.AdvanceStage("READY")
            self.SystemReady.emit()
    
    def OnBiosExit(self, Data):
        self.BootTarget = "desktop"
        self.LoadKernel()
        self.StartServices()
        self.LaunchUI()
        self.AdvanceStage("READY")
        self.SystemReady.emit()


class LCARSBootloader:
    def __init__(self):
        self.BootManager = None
        self.Config = {}
        ODN.Subscribe("Boot.Configure", self.OnConfigure)
    
    def Configure(self, Era="LCARS_25TH", Faction="federation", SkipFirmware=False, Target="desktop"):
        self.Config = {
            "era": Era,
            "faction": Faction,
            "skip_firmware": SkipFirmware,
            "target": Target
        }
        return self
    
    def Boot(self):
        self.BootManager = BootManager(self.Config)
        self.BootManager.BootStageChanged.connect(self.OnStageChanged)
        self.BootManager.SystemReady.connect(self.OnSystemReady)
        self.BootManager.start()
        return self.BootManager
    
    def OnStageChanged(self, Stage, Data):
        pass
    
    def OnSystemReady(self):
        ODN.Emit("System.Ready", self.Config)
    
    def OnConfigure(self, Data):
        self.Configure(
            Era=Data.get("era", "LCARS_25TH"),
            Faction=Data.get("faction", "federation"),
            SkipFirmware=Data.get("skip_firmware", False),
            Target=Data.get("target", "desktop")
        )


def CreateBootloader():
    return LCARSBootloader()


def QuickBoot(Era="LCARS_25TH", Faction="federation", Target="desktop"):
    Loader = LCARSBootloader()
    Loader.Configure(Era=Era, Faction=Faction, SkipFirmware=True, Target=Target)
    return Loader.Boot()


def FullBoot(Era="LCARS_25TH", Faction="federation"):
    Loader = LCARSBootloader()
    Loader.Configure(Era=Era, Faction=Faction, SkipFirmware=False, Target="desktop")
    return Loader.Boot()


__all__ = [
    "BootManager",
    "LCARSBootloader", 
    "CreateBootloader",
    "QuickBoot",
    "FullBoot"
]
