from lcars.base.signal import Signal, ODN
from lcars.base.threading import Thread
from lcars.core.boot_manager import BootManager, LCARSBootloader
from lcars.system.firmware import LCARSFirmware, CreateFirmware, BootTarget

class LCARSSystemIntegrator:
    SystemBooted = Signal()
    UEFICompleted = Signal(dict)
    BIOSCompleted = Signal()
    DesktopLaunched = Signal()
    
    def __init__(self):
        self.bootloader = None
        self.firmware = None
        self.era = "LCARS_25TH"
        self.faction = "federation"
        self.setupODNListeners()
    
    def setupODNListeners(self):
        ODN.Subscribe("System.LaunchFirmware", self.onLaunchFirmware)
        ODN.Subscribe("System.LaunchDesktop", self.onLaunchDesktop)
        ODN.Subscribe("System.LaunchRecovery", self.onLaunchRecovery)
        ODN.Subscribe("Firmware.BootSelected", self.onFirmwareBootSelected)
        ODN.Subscribe("Firmware.ConfigSaved", self.onFirmwareConfigSaved)
    
    def Initialize(self):
        ODN.Emit("System.Initialized", {})
        return self
    
    def StartBootSequence(self, config=None):
        if config:
            self.era = config.get("era", self.era)
            self.faction = config.get("faction", self.faction)
        self.bootloader = LCARSBootloader()
        self.bootloader.configure(era=self.era, faction=self.faction, target="desktop")
        self.bootloader.boot()
        return self
    
    def onBootStage(self, stage, data):
        ODN.Emit("Boot.Progress", {"stage": stage, "data": data})
    
    def onSystemReady(self):
        self.SystemBooted.emit()
        ODN.Emit("System.Ready", {"era": self.era, "faction": self.faction})
    
    def onLaunchFirmware(self, data):
        self.firmware = CreateFirmware().Initialize()
        self.firmware.RunPOST()
        self.firmware.Validate()
        ODN.Emit("Firmware.Ready", self.firmware.GetSystemInfo())
    
    def onLaunchDesktop(self, data):
        self.era = data.get("era", self.era)
        self.faction = data.get("faction", self.faction)
        self.DesktopLaunched.emit()
        ODN.Emit("Desktop.Launch", {"era": self.era, "faction": self.faction})
    
    def onLaunchRecovery(self, data):
        ODN.Emit("Recovery.Launch", {})
    
    def onFirmwareBootSelected(self, data):
        target = data.get("target", "")
        if target == BootTarget.DESKTOP.value:
            self.onLaunchDesktop(data)
        elif target == BootTarget.RECOVERY.value:
            self.onLaunchRecovery(data)
    
    def onFirmwareConfigSaved(self, data):
        self.era = self.firmware.Config.Era if self.firmware else self.era
        self.faction = self.firmware.Config.Faction if self.firmware else self.faction
    
    def Shutdown(self):
        ODN.Emit("System.Shutdown", {})
        if self.firmware:
            self.firmware.SaveConfiguration()


class LCARSRuntime:
    def __init__(self):
        self.integrator = None
    
    def Initialize(self):
        self.integrator = LCARSSystemIntegrator()
        self.integrator.Initialize()
        return self
    
    def Boot(self, fullSequence=False, era="LCARS_25TH", faction="federation"):
        config = {"era": era, "faction": faction, "full_sequence": fullSequence}
        self.integrator.StartBootSequence(config)
        return self
    
    def Run(self):
        if self.integrator and self.integrator.bootloader:
            self.integrator.bootmanager.join()
        return 0
    
    def Shutdown(self):
        if self.integrator:
            self.integrator.Shutdown()


def CreateRuntime():
    return LCARSRuntime()


def QuickStart(era="LCARS_25TH", faction="federation"):
    runtime = CreateRuntime()
    runtime.Initialize()
    runtime.Boot(fullSequence=False, era=era, faction=faction)
    return runtime.Run()


def FullStart(era="LCARS_25TH", faction="federation"):
    runtime = CreateRuntime()
    runtime.Initialize()
    runtime.Boot(fullSequence=True, era=era, faction=faction)
    return runtime.Run()
