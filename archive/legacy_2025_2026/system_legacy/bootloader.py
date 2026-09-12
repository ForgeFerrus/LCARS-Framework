# LCARS system bootloader.
# This is orchestration only. Screens and visual boot panels live in lcars/ui.

from __future__ import annotations

# Titanium Bridge Migration: import threading

from lcars.base.signal import ODN, Observer
from lcars.system.software import BootTarget, CreateFirmware


class BootManager(threading.Thread):
    STAGES = [
        "UEFI",
        "INIT",
        "POST",
        "BIOS",
        "CHECK",
        "FIRMWARE",
        "SELECT",
        "HARDWARE",
        "KERNEL",
        "LOAD",
        "SERVICES",
        "START",
        "READY",
        "UI",
    ]

    def __init__(self, config=None):
        super().__init__()
        self.BootStageChanged = Observer(str, dict)
        self.SystemReady = Observer()
        self.Config = config or {}
        self.CurrentStage = 0
        self.Era = self.Config.get("era", "LCARS_25TH")
        self.Faction = self.Config.get("faction", "federation")
        self.Target = self.Config.get("target", "desktop")
        self.SkipFirmware = self.Config.get("skip_firmware", False)
        self.Firmware = None
        ODN.Subscribe("Firmware.BootSelected", self.OnFirmwareBootSelected)
        ODN.Subscribe("BIOS.SaveAndExit", self.OnBiosExit)

    def run(self):
        self.RunBootSequence()

    def RunBootSequence(self):
        if not self.SkipFirmware:
            self.AdvanceStage("FIRMWARE")
            self.LaunchFirmware()
            return
        self.LoadCoreChain()

    def LoadCoreChain(self):
        self.AdvanceStage("KERNEL")
        self.LoadKernel()
        self.AdvanceStage("SERVICES")
        self.StartServices()
        self.AdvanceStage("UI")
        self.LaunchUi()
        self.AdvanceStage("READY")
        self.SystemReady.Update()

    def AdvanceStage(self, StageName):
        self.CurrentStage = self.STAGES.index(StageName) if StageName in self.STAGES else 0
        Progress = int((self.CurrentStage / max(1, len(self.STAGES) - 1)) * 100)
        Payload = {"progress": Progress, "era": self.Era, "faction": self.Faction}
        self.BootStageChanged.Update(StageName, Payload)
        ODN.Emit("Boot.Stage", {"stage": StageName, "progress": Progress})

    def LaunchFirmware(self):
        self.Firmware = CreateFirmware().Initialize()
        self.Firmware.BootEntrySelected.Attach(self.OnFirmwareEntrySelected)
        self.Firmware.ExecuteBoot(autoSelect=True)

    def LoadKernel(self):
        ODN.Emit("Kernel.Load", {"era": self.Era, "faction": self.Faction})

    def StartServices(self):
        ODN.Emit("Services.Start", {})

    def LaunchUi(self):
        if self.Target == "desktop":
            ODN.Emit("UI.LaunchDesktop", {"era": self.Era, "faction": self.Faction})
        elif self.Target == "terminal":
            ODN.Emit("UI.LaunchTerminal", {})
        elif self.Target == "recovery":
            ODN.Emit("UI.LaunchRecovery", {})

    def OnFirmwareEntrySelected(self, Entry, Data):
        EntryName = getattr(Entry, "Name", "")
        Target = getattr(Entry, "Target", "")
        ODN.Emit("Firmware.BootSelected", {"entry": EntryName, "target": Target, "data": Data})
        self.OnFirmwareBootSelected(Target, Data)

    def OnFirmwareBootSelected(self, Target, Data=None):
        Config = Data.get("Config", {}) if isinstance(Data, dict) else {}
        self.Era = Config.get("Era", self.Era)
        self.Faction = Config.get("Faction", self.Faction)
        if Target == BootTarget.DESKTOP:
            self.Target = "desktop"
            self.LoadCoreChain()
        elif Target == BootTarget.RECOVERY:
            self.Target = "recovery"
            self.LoadCoreChain()

    def OnBiosExit(self, Data=None):
        self.Target = "desktop"
        self.LoadCoreChain()


class LCARSBootloader:
    def __init__(self):
        self.Manager = None
        self.Config = {}
        ODN.Subscribe("Boot.Configure", self.OnConfigure)

    def configure(self, era="LCARS_25TH", faction="federation", skipFirmware=False, target="desktop"):
        self.Config = {
            "era": era,
            "faction": faction,
            "skip_firmware": skipFirmware,
            "target": target,
        }
        return self

    def boot(self):
        self.Manager = BootManager(self.Config)
        self.Manager.BootStageChanged.Attach(self.OnStageChanged)
        self.Manager.SystemReady.Attach(self.OnSystemReady)
        self.Manager.start()
        return self.Manager

    def OnStageChanged(self, Stage, Data):
        ODN.Emit("Boot.Progress", {"stage": Stage, "data": Data})

    def OnSystemReady(self):
        ODN.Emit("System.Ready", self.Config)

    def OnConfigure(self, Data):
        Data = Data or {}
        self.configure(
            era=Data.get("era", "LCARS_25TH"),
            faction=Data.get("faction", "federation"),
            skipFirmware=Data.get("skip_firmware", False),
            target=Data.get("target", "desktop"),
        )


def createBootloader():
    return LCARSBootloader()


def quickBoot(era="LCARS_25TH", faction="federation", target="desktop"):
    Loader = LCARSBootloader()
    Loader.configure(era=era, faction=faction, skipFirmware=True, target=target)
    return Loader.boot()


def fullBoot(era="LCARS_25TH", faction="federation"):
    Loader = LCARSBootloader()
    Loader.configure(era=era, faction=faction, skipFirmware=False, target="desktop")
    return Loader.boot()


__all__ = ["BootManager", "LCARSBootloader", "createBootloader", "quickBoot", "fullBoot"]
