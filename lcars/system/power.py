# ◤ TITANIUM LCARS :: SYSTEM POWER & EPS CONDUIT CONTROLLER // STARFLEET CORE 🖖
# =============================================================================
# ФАЙЛ: lcars/system/power.py
# ПРИЗНАЧЕННЯ: Канонічне керування живленням світлової матриці LCARS (Light Matrix)
#              та інтеграція з інженерною електроплазмовою мережею (EPS) зорельота.
# СТАНДАРТ: Titanium LCARS (Pure PascalCase, Zero-Underscore, No-Init, Pure ODN).
# =============================================================================

from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN, Transmission

class PowerState:
    OFF = 0       # Світлова матриця знеструмлена (темрява)
    STANDBY = 1   # Стазис / режим очікування
    ONLINE = 2    # Повне живлення світлової матриці LCARS

class SystemPower(SystemComponent):
    TypeName = "LCARSSystemPower"
    State = PowerState.ONLINE
    Locked = False

    def Initialize(self, **kwargs):
        self.SystemId = "System.Power"
        self.Id = "System.Power"
        self.PowerActionInitiated = Transmission()
        self.MountODN()
        return self

    Init = Initialize

    def MountODN(self):
        ODN.Listen("Engineering.EPS.LoadAdjusted", self.OnEPSLoad)
        ODN.Listen("Engineering.WarpCore.Ejected", self.OnWarpCoreEjected)
        ODN.Listen("Engineering.EPS.EmergencyDumpEngaged", self.OnEmergencyDump)
        return self

    def OnEPSLoad(self, SignalObj=None, **kwargs):
        Load = kwargs.get("Load", 0.0)
        if Load > 2000.0:
            ODN.Transmit("UI.Power.Warning", Status="EPS_OVERLOAD", Level="Caution")
        return self

    def OnWarpCoreEjected(self, SignalObj=None, **kwargs):
        self.Stasis()
        ODN.Transmit("UI.Power", Power=True, State="STANDBY", Source="AuxiliaryBatteries")
        return self

    def OnEmergencyDump(self, SignalObj=None, **kwargs):
        ODN.Transmit("UI.Power.Warning", Status="VENTING_PLASMA")
        return self

    # ─── СВІТЛОВА МАТРИЦЯ LCARS (СЕНСОРНЕ СКЛО ТА ТЕРМІНАЛ) ───────────────────
    def PowerOff(self):
        self.State = PowerState.OFF
        ODN.Transmit("UI.Power", Power=False, State="OFF")
        ODN.Transmit("System.PowerGrid.Carrier", Active=False)
        return self

    def PowerOn(self):
        self.State = PowerState.ONLINE
        ODN.Transmit("UI.Power", Power=True, State="ONLINE")
        ODN.Transmit("System.PowerGrid.Carrier", Active=True)
        return self

    def Stasis(self):
        self.State = PowerState.STANDBY
        ODN.Transmit("UI.Power", Power=True, State="STANDBY")
        return self

    def Lock(self):
        self.Locked = True
        ODN.Transmit("UI.SecurityLock", Action="LOCK", Locked=True)
        return self

    def Unlock(self):
        self.Locked = False
        ODN.Transmit("UI.SecurityLock", Action="UNLOCK", Locked=False)
        return self

    # ─── КЕРУВАННЯ ФІЗИЧНОЮ ОПЕРАЦІЙНОЮ СИСТЕМОЮ (HOST PC) ───────────────────
    def ExecuteSystemCommand(self, WindowsCmd: str, LinuxCmd: str):
        PlatformObj = getattr(LCARS.System, "Platform", None)
        SysName = str(PlatformObj.system() if PlatformObj and callable(getattr(PlatformObj, "system", None)) else "").lower()
        IsWin = "win" in SysName

        TargetCmd = WindowsCmd if IsWin else LinuxCmd
        ExecuteFunc = getattr(LCARS.System, "Execute", None)
        if callable(ExecuteFunc):
            ExecuteFunc(TargetCmd)
        return self

    def Sleep(self):
        ODN.Transmit("System.Power.Sleep", Action="Sleep")
        return self.ExecuteSystemCommand(
            WindowsCmd="rundll32.exe powrprof.dll,SetSuspendState 0,1,0",
            LinuxCmd="systemctl suspend"
        )

    def Hibernate(self):
        ODN.Transmit("System.Power.Hibernate", Action="Hibernate")
        return self.ExecuteSystemCommand(
            WindowsCmd="shutdown /h",
            LinuxCmd="systemctl hibernate"
        )

    def Restart(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Restart", Action="Restart", Delay=DelaySeconds)
        return self.ExecuteSystemCommand(
            WindowsCmd=f"shutdown /r /t {int(DelaySeconds)}",
            LinuxCmd="systemctl reboot"
        )

    def Shutdown(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Shutdown", Action="Shutdown", Delay=DelaySeconds)
        return self.ExecuteSystemCommand(
            WindowsCmd=f"shutdown /s /t {int(DelaySeconds)}",
            LinuxCmd="systemctl poweroff"
        )

    def LockSession(self):
        self.Lock()
        ODN.Transmit("System.Power.Lock", Action="Lock")
        return self.ExecuteSystemCommand(
            WindowsCmd="rundll32.exe user32.dll,LockWorkStation",
            LinuxCmd="loginctl lock-session"
        )

    def ExecuteDirective(self, Directive: str) -> str:
        Clean = str(Directive).strip().lower()
        if Clean in ("poweroff", "dark", "matrix_off"):
            self.PowerOff()
            return "LIGHT MATRIX POWER DEENERGIZED"
        elif Clean in ("poweron", "energize", "matrix_on"):
            self.PowerOn()
            return "LIGHT MATRIX ENERGIZED"
        elif Clean in ("stasis", "standby"):
            self.Stasis()
            return "SYSTEM ENTERING STASIS"
        elif Clean in ("lock", "lockout"):
            self.LockSession()
            return "WORKSTATION LOCKED"
        elif Clean in ("unlock",):
            self.Unlock()
            return "WORKSTATION UNLOCKED"
        elif Clean in ("sleep", "suspend"):
            self.Sleep()
            return "SYSTEM ENTERING SLEEP STATE"
        elif Clean in ("hibernate",):
            self.Hibernate()
            return "SYSTEM ENTERING HIBERNATION STATE"
        elif Clean in ("restart", "reboot"):
            self.Restart(0)
            return "SYSTEM REBOOT INITIATED"
        elif Clean in ("shutdown",):
            self.Shutdown(0)
            return "SYSTEM SHUTDOWN INITIATED"
        return "UNKNOWN POWER DIRECTIVE"

# Канонічний живий вузол живлення ядра LCARS (без GetInstance!)
PowerControl = SystemPower()
PowerControl.Initialize()
PowerManager = PowerControl
Power = PowerControl

LCARS.Power = PowerControl
LCARS.Register("System.Power", PowerControl)

__all__ = ["PowerState", "SystemPower", "PowerControl", "PowerManager", "Power"]
