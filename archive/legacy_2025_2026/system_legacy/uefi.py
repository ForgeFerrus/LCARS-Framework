# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: from typing import Dict, List, Optional, Callable
# Titanium Bridge Migration: from dataclasses import dataclass

from lcars.base.signal import Signal
from lcars.base.threading import Thread

@dataclass
class BootEntry:
    Name: str
    Description: str
    Target: str
    Priority: int
    IsDefault: bool = False

class UEFIConfig:
    def __init__(self):
        self.Version = "25.0.1-Titanium"
        self.SecureBoot = True
        self.TpmActive = True
        self.FastBoot = False
        self.BootTimeout = 5
        self.DefaultEntry = 0
        self.Entries = [
            BootEntry("LCARS-DESKTOP", "Primary LCARS System", "desktop", 1, True),
            BootEntry("LCARS-RECOVERY", "System Recovery Mode", "recovery", 2),
            BootEntry("LCARS-BIOS", "BIOS Configuration", "bios", 3),
            BootEntry("NETWORK-BOOT", "PXE Network Boot", "pxe", 4),
            BootEntry("UEFI-SHELL", "UEFI Command Shell", "shell", 5)
        ]
    
    def GetDefaultEntry(self) -> BootEntry:
        for entry in self.Entries:
            if entry.IsDefault:
                return entry
        return self.Entries[0] if self.Entries else None
    
    def GetEntryByIndex(self, index: int) -> Optional[BootEntry]:
        if 0 <= index < len(self.Entries):
            return self.Entries[index]
        return None


class UEFIFirmware:
    BootEntrySelected = Signal(BootEntry, Dict)
    TimeoutExpired = Signal()
    ConfigLoaded = Signal(UEFIConfig)
    
    def __init__(self):
        self.Config = UEFIConfig()
        self.SelectedEntry = None
        self.IsRunning = False
        self.TimeoutTimer = None
        self.OnKeyPress = None
    
    def Initialize(self):
        self.ConfigLoaded.Emit(self.Config)
        return self
    
    def StartBootManager(self, autoSelect: bool = True):
        self.IsRunning = True
        if autoSelect and self.Config.FastBoot:
            default = self.Config.GetDefaultEntry()
            if default:
                self.SelectEntry(default)
            return
        if self.Config.BootTimeout > 0:
            self.StartTimeout()
    
    def StartTimeout(self):
        self.TimeoutTimer = Thread.Timer(self.Config.BootTimeout, self.OnTimeout)
        self.TimeoutTimer.start()
    
    def OnTimeout(self):
        if self.SelectedEntry is None:
            default = self.Config.GetDefaultEntry()
            if default:
                self.SelectEntry(default)
        self.TimeoutExpired.Emit()
    
    def SelectEntry(self, entry: BootEntry):
        self.SelectedEntry = entry
        self.BootEntrySelected.Emit(entry, {
            "Timestamp": datetime.now().isoformat(),
            "SecureBoot": self.Config.SecureBoot,
            "TpmActive": self.Config.TpmActive
        })
    
    def SelectByIndex(self, index: int) -> bool:
        entry = self.Config.GetEntryByIndex(index)
        if entry:
            self.SelectEntry(entry)
            return True
        return False
    
    def SelectByName(self, name: str) -> bool:
        for entry in self.Config.Entries:
            if entry.Name == name:
                self.SelectEntry(entry)
                return True
        return False
    
    def HandleInput(self, key: str):
        if key == "UP":
            idx = self.Config.Entries.index(self.SelectedEntry) if self.SelectedEntry else -1
            newIdx = max(0, idx - 1)
            self.SelectedEntry = self.Config.Entries[newIdx]
        elif key == "DOWN":
            idx = self.Config.Entries.index(self.SelectedEntry) if self.SelectedEntry else -1
            newIdx = min(len(self.Config.Entries) - 1, idx + 1)
            self.SelectedEntry = self.Config.Entries[newIdx]
        elif key == "ENTER":
            if self.SelectedEntry:
                self.SelectEntry(self.SelectedEntry)
        elif key == "F2":
            self.SelectByName("LCARS-BIOS")
        elif key == "F12":
            self.Config.FastBoot = False
            self.StartBootManager(autoSelect=False)
    
    def GetBootOrder(self) -> List[BootEntry]:
        return sorted(self.Config.Entries, key=lambda e: e.Priority)
    
    def SetBootOrder(self, order: List[str]):
        for idx, name in enumerate(order):
            for entry in self.Config.Entries:
                if entry.Name == name:
                    entry.Priority = idx + 1
                    break
    
    def Stop(self):
        self.IsRunning = False
        if self.TimeoutTimer:
            self.TimeoutTimer.cancel()


class UEFIManager:
    def __init__(self, onBootSelected: Optional[Callable] = None):
        self.Firmware = UEFIFirmware()
        self.OnBootSelected = onBootSelected
        self.Firmware.BootEntrySelected.connect(self.OnEntrySelected)
    
    def Start(self, autoSelect: bool = True) -> UEFIFirmware:
        self.Firmware.Initialize()
        self.Firmware.StartBootManager(autoSelect)
        return self.Firmware
    
    def OnEntrySelected(self, entry: BootEntry, data: Dict):
        if self.OnBootSelected:
            self.OnBootSelected(entry, data)
    
    def SelectDesktop(self):
        return self.Firmware.SelectByName("LCARS-DESKTOP")
    
    def SelectBIOS(self):
        return self.Firmware.SelectByName("LCARS-BIOS")
    
    def SelectRecovery(self):
        return self.Firmware.SelectByName("LCARS-RECOVERY")


def CreateUEFI(onBootSelected: Optional[Callable] = None) -> UEFIManager:
    return UEFIManager(onBootSelected)


def QuickBoot(target: str = "desktop") -> bool:
    uefi = UEFIFirmware()
    uefi.Initialize()
    return uefi.SelectByName(f"LCARS-{target.upper()}")


if __name__ == "__main__":
    uefi = UEFIFirmware()
    uefi.Initialize()
    print(f"UEFI v{uefi.Config.Version}")
    print(f"Secure Boot: {uefi.Config.SecureBoot}")
    print(f"TPM: {uefi.Config.TpmActive}")
    print("\nBoot Entries:")
    for entry in uefi.GetBootOrder():
        print(f"  [{entry.Priority}] {entry.Name}: {entry.Description}")
    uefi.SelectByName("LCARS-DESKTOP")
