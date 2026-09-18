# ◤ TITANIUM LCARS :: SYSTEM POWER & SESSION CONTROL // STARFLEET CORE 🖖
# =============================================================================
# ФАЙЛ: lcars/system/power.py
# ПРИЗНАЧЕННЯ: Керування живленням світлової матриці LCARS (Light Matrix / Stasis / Lock)
#              та низькорівневе керування енергомережами корабля через чисті типи LCARS.
# =============================================================================
from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.signal import ODN, Transmission

class PowerState:
    OFF = 0       # Матриця знеструмлена (темрява)
    STANDBY = 1   # Режим очікування / стазис
    ONLINE = 2    # Повне живлення світлової матриці

class SystemPower(LCARS):
    InstanceRef = None
    State = PowerState.ONLINE
    Locked = False

    @classmethod
    def GetInstance(cls) -> SystemPower:
        if cls.InstanceRef is None:
            cls.InstanceRef = SystemPower().Initialize()
        return cls.InstanceRef

    def Initialize(self, **kwargs):
        super().Initialize(SystemId="System.Power", Id="System.Power", **kwargs)
        self.PowerActionInitiated = Transmission()
        return self

    Init = Initialize

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

    @staticmethod
    def IsWindows() -> bool:
        PlatformObj = getattr(LCARS.System, "Platform", None)
        SysName = str(PlatformObj.system() if PlatformObj and callable(getattr(PlatformObj, "system", None)) else "").lower()
        return "win" in SysName

    def Sleep(self):
        ODN.Transmit("System.Power.Sleep", Action="Sleep")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            if self.IsWindows():
                Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=True)
                return self
            else:
                Popen(["systemctl", "suspend"], shell=True)
                return self
        return self

    def Hibernate(self):
        ODN.Transmit("System.Power.Hibernate", Action="Hibernate")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            if self.IsWindows():
                Popen(["shutdown", "/h"], shell=True)
                return self
            else:
                Popen(["systemctl", "hibernate"], shell=True)
                return self
        return self

    def Restart(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Restart", Action="Restart", Delay=DelaySeconds)
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            if self.IsWindows():
                Popen(["shutdown", "/r", "/t", str(int(DelaySeconds))], shell=True)
                return self
            else:
                Popen(["systemctl", "reboot"], shell=True)
                return self
        return self

    def Shutdown(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Shutdown", Action="Shutdown", Delay=DelaySeconds)
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            if self.IsWindows():
                Popen(["shutdown", "/s", "/t", str(int(DelaySeconds))], shell=True)
                return self
            else:
                Popen(["systemctl", "poweroff"], shell=True)
                return self
        return self

    def LockSession(self):
        self.Lock()
        ODN.Transmit("System.Power.Lock", Action="Lock")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            if self.IsWindows():
                Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
                return self
            else:
                Popen(["loginctl", "lock-session"], shell=True)
                return self
        return self

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

PowerControl = SystemPower.GetInstance()
PowerManager = SystemPower
__all__ = ["PowerState", "SystemPower", "PowerControl", "PowerManager"]
