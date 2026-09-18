# ◤ TITANIUM LCARS :: SYSTEM POWER & EPS ENERGY GRID CONTROLLER // STARFLEET CORE 🖖
# =============================================================================
# ФАЙЛ: lcars/system/power.py
# ПРИЗНАЧЕННЯ: Головний диспетчер системного живлення терміналів LCARS (Light Matrix),
#              інтеграція з інженерною електроплазмовою мережею (EPS / Warp Core)
#              та виконання директив фізичного керування хост-машиною.
# СТАНДАРТ: Titanium LCARS (Pure PascalCase, No-Init, Pure ODN, Zero-Underscore).
# =============================================================================

from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN, Transmission

# ─── СТАТУСИ ЖИВЛЕННЯ СВІТЛОВОЇ МАТРИЦІ LCARS ───────────────────────────────
class PowerState:
    OFF = 0       # Матриця знеструмлена (повна темрява консолі)
    STANDBY = 1   # Стазис / режим очікування сенсорів
    ONLINE = 2    # Повне бойове/штатне живлення оптичного скла

# =============================================================================
# ГОЛОВНИЙ СИСТЕМНИЙ КОНТРОЛЕР ЕНЕРГІЇ ТА СЕСІЙ
# =============================================================================
class SystemPower(SystemComponent):
    TypeName = "LCARSSystemPower"
    State = PowerState.ONLINE
    Locked = False

    # Ініціалізація вузла та підключення до шини ODN
    def Initialize(self, **kwargs):
        self.SystemId = "System.Power"
        self.Id = "System.Power"
        self.PowerActionInitiated = Transmission()
        self.MountODN()
        return self

    Init = Initialize

    # Підключення слухачів інженерної підсистеми корабля (Warp Core / EPS Grid)
    def MountODN(self):
        # 1. Відстеження динамічного навантаження електроплазмових магістралей (EPSConduit)
        ODN.Listen("Engineering.EPS.LoadAdjusted", self.OnEPSLoad)
        # 2. Реакція на катапультування варп-ядра (EjectCore) — перехід на аварійні батареї
        ODN.Listen("Engineering.WarpCore.Ejected", self.OnWarpCoreEjected)
        # 3. Аварійне скидання плазми у відкритий космос через реле EPS
        ODN.Listen("Engineering.EPS.EmergencyDumpEngaged", self.OnEmergencyDump)
        return self

    # Реакція на зміну навантаження в мережі EPS
    def OnEPSLoad(self, SignalObj=None, **kwargs):
        Load = kwargs.get("Load", 0.0)
        # Якщо навантаження перевищує номінал (2000 МВт) — транслюємо попередження на інтерфейс
        if Load > 2000.0:
            ODN.Transmit("UI.Power.Warning", Status="EPS_OVERLOAD", Level="Caution")
        return self

    # Обробка аварійної втрати ядра: автоматичний перехід консолей у стазис для економії живлення
    def OnWarpCoreEjected(self, SignalObj=None, **kwargs):
        self.Stasis()
        ODN.Transmit("UI.Power", Power=True, State="STANDBY", Source="AuxiliaryBatteries")
        return self

    # Сигнал про аварійний вихід плазми
    def OnEmergencyDump(self, SignalObj=None, **kwargs):
        ODN.Transmit("UI.Power.Warning", Status="VENTING_PLASMA")
        return self

    # ─── КЕРУВАННЯ СВІТЛОВОЮ МАТРИЦЕЮ ТЕРМІНАЛІВ LCARS ─────────────────────────

    # Знеструмлення консолі (вимикає світлодіоди та гасить екран)
    def PowerOff(self):
        self.State = PowerState.OFF
        ODN.Transmit("UI.Power", Power=False, State="OFF")
        ODN.Transmit("System.PowerGrid.Carrier", Active=False)
        return self

    # Подача повного живлення на скло інтерфейсу
    def PowerOn(self):
        self.State = PowerState.ONLINE
        ODN.Transmit("UI.Power", Power=True, State="ONLINE")
        ODN.Transmit("System.PowerGrid.Carrier", Active=True)
        return self

    # Переведення робочої станції в режим стазису (Standby)
    def Stasis(self):
        self.State = PowerState.STANDBY
        ODN.Transmit("UI.Power", Power=True, State="STANDBY")
        return self

    # Блокування сенсорного введення термінала (Security Stasis Lock)
    def Lock(self):
        self.Locked = True
        ODN.Transmit("UI.SecurityLock", Action="LOCK", Locked=True)
        return self

    # Зняття блокування доступу офіцера
    def Unlock(self):
        self.Locked = False
        ODN.Transmit("UI.SecurityLock", Action="UNLOCK", Locked=False)
        return self

    # ─── ФІЗИЧНЕ КЕРУВАННЯ РОБОЧОЮ СТАНЦІЄЮ (HOST PC DIRECTIVES) ──────────────

    # Переведення хост-комп'ютера в режим сну (Sleep / Suspend)
    def Sleep(self):
        ODN.Transmit("System.Power.Sleep", Action="Sleep")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], shell=True)
        return self

    # Глибокий сон машини зі збереженням стану на диск (Hibernate)
    def Hibernate(self):
        ODN.Transmit("System.Power.Hibernate", Action="Hibernate")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            Popen(["shutdown", "/h"], shell=True)
        return self

    # Перезавантаження комп'ютера з можливістю затримки
    def Restart(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Restart", Action="Restart", Delay=DelaySeconds)
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            Popen(["shutdown", "/r", "/t", str(int(DelaySeconds))], shell=True)
        return self

    # Повне завершення роботи комп'ютера (Shutdown)
    def Shutdown(self, DelaySeconds: int = 0):
        ODN.Transmit("System.Power.Shutdown", Action="Shutdown", Delay=DelaySeconds)
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            Popen(["shutdown", "/s", "/t", str(int(DelaySeconds))], shell=True)
        return self

    # Блокування облікового запису користувача операційної системи
    def LockSession(self):
        self.Lock()
        ODN.Transmit("System.Power.Lock", Action="Lock")
        Popen = getattr(LCARS.System, "Process", None)
        if Popen:
            Popen(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)
        return self

    # Універсальний маршрутизатор текстових команд і голосових директив
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

# Канонічний активний вузол керування живленням у системі LCARS
PowerControl = SystemPower()
PowerManager = PowerControl
Power = PowerControl

# Автоматична інтеграція в системне ядро
LCARS.Power = PowerControl
LCARS.Register("System.Power", PowerControl)
