# ◤ TITANIUM SYSTEM ALERT & TACTICAL CONTROLLER // CANONICAL STARFLEET 🖖
# =============================================================================
# ФАЙЛ: lcars/system/alert.py
# ОПИС: Тактична система тривог, бойової готовності та повного перемикання станів
#       усіх підсистем, конфігурацій та візуального оформлення LCARS.
#       КАНОНІЧНІ РІВНІ ТРИВОГ ЗОРЯНОГО ФЛОТУ:
#       - GREEN (0 / Normal / Nominal) — штатний режим, стандартне освітлення, щити 0%.
#       - YELLOW (1 / Caution / Standby) — підвищена готовність, бурштиновий інтерфейс, щити 50%.
#       - RED (2 / Tactical / Combat) — бойова тривога, червона пульсація, щити 100%, бойовий імпульс.
#       АРХІТЕКТУРНИЙ ПОДІЛ ВІДПОВІДАЛЬНОСТІ (SEPARATION OF CONCERNS):
#       - AlertConfiguration: зберігає всі налаштування кольорів, порогів заліза та звуків.
#       - AlertSystem: контролер станів, аудит-журнал, оцінка телеметрії та аварійний перехід.
#       - Palette (в default.py): чисті декларативні константи кольорів.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version
from lcars.core.signal import ODN, Transmission
from lcars.base.default import Palette

from enum import IntEnum, EnumMeta

# ═════════════════════════════════════════════════════════════════════
# 1. МЕТАКЛАС ТА СТАТУСИ РІВНІВ БОЙОВОЇ ГОТОВНОСТІ (ALERT LEVELS)
# ═════════════════════════════════════════════════════════════════════
class AlertLevelMeta(EnumMeta):
    @property
    def Members(cls):
        return {
            "GREEN": cls.GREEN,
            "YELLOW": cls.YELLOW,
            "RED": cls.RED,
        }

    def __iter__(cls):
        return iter([cls.GREEN, cls.YELLOW, cls.RED])

    def __contains__(cls, Item):
        return Item in [cls.GREEN, cls.YELLOW, cls.RED] or any(Item == m.value or Item == m for m in cls)

    def __getitem__(cls, Name):
        NameStr = str(Name).upper().strip()
        MembersMap = {
            "GREEN": cls.GREEN,
            "NORMAL": cls.GREEN,
            "NOMINAL": cls.GREEN,
            "YELLOW": cls.YELLOW,
            "CAUTION": cls.YELLOW,
            "STANDBY": cls.YELLOW,
            "RED": cls.RED,
            "TACTICAL": cls.RED,
            "COMBAT": cls.RED,
            "BATTLE": cls.RED,
        }
        if NameStr in MembersMap:
            return MembersMap[NameStr]
        raise KeyError(Name)

class AlertLevel(IntEnum, metaclass=AlertLevelMeta):
    GREEN = 0
    NORMAL = 0
    NOMINAL = 0

    YELLOW = 1
    CAUTION = 1
    STANDBY = 1

    RED = 2
    TACTICAL = 2
    COMBAT = 2
    BATTLE = 2

    @property
    def Name(self) -> str:
        if self.value == 0:
            return "GREEN"
        elif self.value == 1:
            return "YELLOW"
        elif self.value == 2:
            return "RED"
        return self.name

    @property
    def Value(self) -> int:
        return self.value

# ═════════════════════════════════════════════════════════════════════
# 2. АРХІТЕКТУРНА КОНФІГУРАЦІЯ ТРИВОГ (ALERT CONFIGURATION)
# ═════════════════════════════════════════════════════════════════════
class AlertConfiguration(LCARS):
    # Кольорові палітри для кожного рівня тривоги (беруться з канону Palette)
    Palettes = {
        "GREEN": Palette.Buttons,
        "YELLOW": Palette.Yellow,
        "RED": Palette.Red,
    }

    # Пороги апаратного навантаження (CPU / RAM)
    Thresholds = {
        "CpuCritical": 92.0,
        "CpuWarning": 80.0,
        "MemoryCritical": 92.0,
        "MemoryWarning": 82.0,
    }

    # Звукові сигнали тривоги
    Sounds = {
        "GREEN": "alert_green",
        "YELLOW": "alert_yellow",
        "RED": "alert_red",
    }

    # Назви візуальних тем
    Themes = {
        "GREEN": "Standard",
        "YELLOW": "YellowAlert",
        "RED": "RedAlert",
    }

# ═════════════════════════════════════════════════════════════════════
# 3. СИСТЕМНИЙ КОНТРОЛЕР ТРИВОГ (ALERT SYSTEM & ACTUATOR)
# ═════════════════════════════════════════════════════════════════════
class AlertSystem(SystemComponent):
    SystemVersion = Version.Release
    InstanceRef = None

    # Канали сигналів LCARS Transmission для підписки компонентів
    Changed = Transmission(dict)
    LevelRaised = Transmission(dict)
    LevelLowered = Transmission(dict)
    EmergencyFailover = Transmission(dict)

    def __new__(cls, *args, **kwargs):
        if cls.InstanceRef is None:
            cls.InstanceRef = super().__new__(cls)
        return cls.InstanceRef

    def __init__(self, SystemId: str = "System.Alert"):
        if getattr(self, "Initialized", False):
            return
        super().__init__(SystemId=SystemId)
        self.Initialized = True
        self.Version = Version.Release
        self.Passport = Version.Passport()
        self.Level = AlertLevel.GREEN
        self.PreviousLevel = AlertLevel.GREEN
        self.Reason = "System Nominal"
        self.AuthorizedBy = "SystemBootstrap"
        self.EventBus = None
        self.Controller = None
        self.AlertHistory = []

        # Фізичні та тактичні параметри корабля
        self.ShieldPower = 0.0
        self.WeaponsStatus = "Safe"
        self.WarpDriveMode = "Cruise"
        self.SensorsPower = "Standard"
        self.SubspaceComms = "Online"
        self.StructuralIntegrity = "Nominal"
        self.InertialDampeners = "Standard"
        self.ActiveTheme = AlertConfiguration.Themes["GREEN"]

        # Аварійний режим та дублюючі контури
        self.EmergencyFailoverActive = False
        self.FailoverSubsystem = ""
        self.IsDrillActive = False

    @classmethod
    def GetInstance(cls) -> AlertSystem:
        if cls.InstanceRef is None:
            cls.InstanceRef = AlertSystem()
        return cls.InstanceRef

    def Init(self, EventBus=None, Controller=None) -> AlertSystem:
        self.EventBus = EventBus
        self.Controller = Controller
        self.Level = AlertLevel.GREEN
        self.PreviousLevel = AlertLevel.GREEN
        self.Reason = "System Nominal"
        self.AuthorizedBy = "SystemBootstrap"
        self.EmergencyFailoverActive = False
        self.ApplyTacticalProfile(self.Level)
        return self

    # Повертає активну палітру кольорів відповідно до поточного рівня тривоги
    def GetActivePalette(self) -> list[str]:
        return AlertConfiguration.Palettes.get(self.Level.Name, Palette.Buttons)

    # Головна точка повного перемикання стану та вигляду фреймворка
    def SetLevel(self, LevelInput: any, Reason: str = "Manual Directive", AuthorizedBy: str = "Captain") -> AlertLevel:
        OldLevel = self.Level
        NewLevel = self.ParseLevel(LevelInput)

        if self.Level != NewLevel:
            NowTime = LCARS.System.Time.time() if hasattr(LCARS.System, "Time") else 0.0
            self.PreviousLevel = OldLevel
            self.Level = NewLevel
            self.Reason = str(Reason)
            self.AuthorizedBy = str(AuthorizedBy)

            # Фіксація в історії тривог
            HistoryRecord = {
                "Timestamp": round(NowTime, 2),
                "FromLevel": OldLevel.Name,
                "ToLevel": NewLevel.Name,
                "Reason": self.Reason,
                "AuthorizedBy": self.AuthorizedBy,
                "IsFailover": self.EmergencyFailoverActive,
            }
            self.AlertHistory.append(HistoryRecord)

            # 1. Перемикання тактичного стану
            self.ApplyTacticalProfile(NewLevel)

            # 2. Синхронізація з Інженерним комплексом (Engineering: щити, варп, розподіл живлення)
            self.SyncEngineeringLayer(NewLevel)

            # 3. Синхронізація з Системним Середовищем (SystemEnvironment)
            self.SyncSystemEnvironment(NewLevel)

            # 4. Активація корабельної звукової сигналізації
            self.ActuateAlertSound(NewLevel)

            # 5. Оновлення візуальної теми інтерфейсу всього фреймворка
            self.ActuateInterfaceTheme(NewLevel)

            # 6. Квантово-оптична мережа ODN (мовлення для всіх станцій)
            StateMap = self.GetState()
            ODN.Transmit(
                "Alert.Changed",
                Level=NewLevel.Name,
                Value=NewLevel.Value,
                Previous=OldLevel.Name,
                Reason=self.Reason,
                AuthorizedBy=self.AuthorizedBy,
                ActiveColors=self.GetActivePalette(),
                Tactical=self.GetTacticalState()
            )
            ODN.Transmit("UI.AlertChanged", Level=NewLevel.Name, Theme=self.ActiveTheme, Colors=self.GetActivePalette())
            ODN.Transmit("ODN.06.RemoteAlertPush", Level=NewLevel.Name, Reason=self.Reason)

            # 7. EventBus integration
            if self.EventBus:
                EventPayload = {
                    "level": NewLevel.Name,
                    "previous_level": OldLevel.Name,
                    "reason": self.Reason,
                    "authorized_by": self.AuthorizedBy,
                }
                if hasattr(self.EventBus, "emit"):
                    self.EventBus.emit("CHANGED", EventPayload)
                elif hasattr(self.EventBus, "Emit"):
                    self.EventBus.Emit("CHANGED", EventPayload)

            # 8. Внутрішні канали сигналів
            self.Changed.Emit(StateMap)
            if NewLevel.Value > OldLevel.Value:
                self.LevelRaised.Emit(StateMap)
            else:
                self.LevelLowered.Emit(StateMap)

        return self.Level

    # Налаштування інженерних та тактичних параметрів
    def ApplyTacticalProfile(self, Level: AlertLevel) -> None:
        self.ActiveTheme = AlertConfiguration.Themes.get(Level.Name, "Standard")
        if Level == AlertLevel.RED:
            self.ShieldPower = 100.0
            self.WeaponsStatus = "Hot"
            self.WarpDriveMode = "CombatImpulse"
            self.SensorsPower = "Maximum"
            self.SubspaceComms = "SecurePriority"
            self.StructuralIntegrity = "Maximum100Percent"
            self.InertialDampeners = "HeavyCombat"

        elif Level == AlertLevel.YELLOW:
            self.ShieldPower = 50.0
            self.WeaponsStatus = "Armed"
            self.WarpDriveMode = "Standby"
            self.SensorsPower = "Enhanced"
            self.SubspaceComms = "Online"
            self.StructuralIntegrity = "Reinforced"
            self.InertialDampeners = "Standard"

        else:
            self.ShieldPower = 0.0
            self.WeaponsStatus = "Safe"
            self.WarpDriveMode = "Cruise"
            self.SensorsPower = "Standard"
            self.SubspaceComms = "Online"
            self.StructuralIntegrity = "Nominal"
            self.InertialDampeners = "Standard"

    # Синхронізація з Інженерним комплексом
    def SyncEngineeringLayer(self, Level: AlertLevel) -> None:
        from lcars.engineering.controller import Engineering
        Eng = Engineering.GetInstance()
        if Eng:
            Eng.ApplyAlertLevel(Level.Name)

    # Синхронізація з Системним Середовищем
    def SyncSystemEnvironment(self, Level: AlertLevel) -> None:
        from lcars.system.environment import SystemEnvironment
        import lcars.base.default as DefaultMod
        DefaultMod.SystemState = Level.Name
        SystemEnvironment.Set("AlertLevel", Level.Name)
        ModeStr = "TACTICAL" if Level == AlertLevel.RED else ("ALERT" if Level == AlertLevel.YELLOW else "NORMAL")
        SystemEnvironment.Set("SystemMode", ModeStr)

    # Активація звукової сигналізації
    def ActuateAlertSound(self, Level: AlertLevel) -> None:
        from lcars.modules.sound import ActiveAudio
        if Level == AlertLevel.RED:
            ActiveAudio.StartAlertLoop("red")
        elif Level == AlertLevel.YELLOW:
            ActiveAudio.StartAlertLoop("yellow")
        else:
            ActiveAudio.StopAlertLoop()
            SoundName = AlertConfiguration.Sounds.get(Level.Name, "alert_green")
            ActiveAudio.Play(SoundName)

    # Оновлення візуального оформлення фреймворка
    def ActuateInterfaceTheme(self, Level: AlertLevel) -> None:
        if self.Controller:
            if hasattr(self.Controller, "ApplyLevel"):
                self.Controller.ApplyLevel(Level)
            elif hasattr(self.Controller, "apply_level"):
                self.Controller.apply_level(Level)
            elif hasattr(self.Controller, "SetAlertLevel"):
                self.Controller.SetAlertLevel(Level)
            elif hasattr(self.Controller, "set_alert_level"):
                self.Controller.set_alert_level(Level)
            elif callable(self.Controller):
                self.Controller(Level)
        ActiveColors = self.GetActivePalette()
        ODN.Transmit("UI.ThemeChanged", Theme=self.ActiveTheme, Level=Level.Name, Colors=ActiveColors)
        ODN.Transmit("UI.PaletteChanged", CurrentAlert=Level.Name, Colors=ActiveColors)

    # Обробка критичних збоїв, помилок та автоматичний перехід в аварійний режим
    def HandleSystemFailure(self, FailedSubsystem: str, ErrorMessage: str, Criticality: str = "HIGH") -> AlertLevel:
        self.EmergencyFailoverActive = True
        self.FailoverSubsystem = str(FailedSubsystem)
        CritUpper = str(Criticality or "").upper()

        FailoverEvent = {
            "Subsystem": FailedSubsystem,
            "Error": ErrorMessage,
            "Criticality": CritUpper,
            "Timestamp": LCARS.System.Time.time() if hasattr(LCARS.System, "Time") else 0.0,
        }
        self.EmergencyFailover.Emit(FailoverEvent)
        ODN.Transmit("System.EmergencyFailoverEngaged", **FailoverEvent)

        if CritUpper == "CRITICAL":
            return self.SetLevel(
                AlertLevel.RED,
                Reason=f"Critical Subsystem Failure: {FailedSubsystem} - {ErrorMessage}",
                AuthorizedBy="AutomatedHealthFailover"
            )
        else:
            return self.SetLevel(
                AlertLevel.YELLOW,
                Reason=f"Subsystem Degradation: {FailedSubsystem} - {ErrorMessage}",
                AuthorizedBy="AutomatedHealthFailover"
            )

    # Автоматична оцінка апаратної телеметрії (CPU, пам'ять, диски)
    def EvaluateHardwareTelemetry(self, Stats: dict | None = None) -> AlertLevel:
        from lcars.system.environment import SystemEnvironment
        HardwareStats = Stats or SystemEnvironment.GetSystemStats()

        Cpu = float(HardwareStats.get("CpuPercent", 0.0))
        Memory = float(HardwareStats.get("MemoryPercent", 0.0))

        CpuCrit = AlertConfiguration.Thresholds["CpuCritical"]
        MemCrit = AlertConfiguration.Thresholds["MemoryCritical"]
        CpuWarn = AlertConfiguration.Thresholds["CpuWarning"]
        MemWarn = AlertConfiguration.Thresholds["MemoryWarning"]

        if Cpu >= CpuCrit or Memory >= MemCrit:
            return self.SetLevel(
                AlertLevel.RED,
                Reason=f"Critical Hardware Strain: CPU {Cpu}%, RAM {Memory}%",
                AuthorizedBy="AutomatedTelemetryGrid"
            )
        elif Cpu >= CpuWarn or Memory >= MemWarn:
            return self.SetLevel(
                AlertLevel.YELLOW,
                Reason=f"High Hardware Strain: CPU {Cpu}%, RAM {Memory}%",
                AuthorizedBy="AutomatedTelemetryGrid"
            )
        elif self.Reason.startswith("Critical Hardware Strain") or self.Reason.startswith("High Hardware Strain"):
            return self.SetLevel(
                AlertLevel.GREEN,
                Reason="Hardware Resources Normalized",
                AuthorizedBy="AutomatedTelemetryGrid"
            )

        return self.Level

    # Навчальна тривога (Alert Drill)
    def TriggerDrill(self, LevelInput: any = AlertLevel.RED) -> AlertLevel:
        self.IsDrillActive = True
        TargetLvl = self.ParseLevel(LevelInput)
        return self.SetLevel(TargetLvl, Reason="Tactical Readiness Drill", AuthorizedBy="CommandDrill")

    # Зняття тривоги
    def ClearAlert(self, AuthorizedBy: str = "Captain") -> AlertLevel:
        self.EmergencyFailoverActive = False
        self.IsDrillActive = False
        return self.SetLevel(AlertLevel.GREEN, Reason="All Systems Nominal", AuthorizedBy=AuthorizedBy)

    # Швидкі директиви
    def EngageRedAlert(self, Reason: str = "Tactical Engagement", AuthorizedBy: str = "Captain") -> AlertLevel:
        return self.SetLevel(AlertLevel.RED, Reason=Reason, AuthorizedBy=AuthorizedBy)

    def EngageYellowAlert(self, Reason: str = "Heightened Readiness", AuthorizedBy: str = "TacticalOfficer") -> AlertLevel:
        return self.SetLevel(AlertLevel.YELLOW, Reason=Reason, AuthorizedBy=AuthorizedBy)

    # Парсинг вхідного значення у канонічний AlertLevel
    def ParseLevel(self, LevelInput: any) -> AlertLevel:
        if isinstance(LevelInput, AlertLevel):
            return LevelInput
        if isinstance(LevelInput, int):
            for Lvl in AlertLevel:
                if int(Lvl) == LevelInput:
                    return Lvl
            return AlertLevel.GREEN

        Normalized = str(LevelInput or "").upper().strip()
        if hasattr(AlertLevel, "Members") and Normalized in AlertLevel.Members:
            return AlertLevel.Members[Normalized]
        if Normalized.isdigit():
            Num = int(Normalized)
            for Lvl in AlertLevel:
                if int(Lvl) == Num:
                    return Lvl
        return AlertLevel.GREEN

    # Послідовне циклічне перемикання (Green -> Yellow -> Red -> Green)
    def CycleLevel(self) -> AlertLevel:
        Order = [AlertLevel.GREEN, AlertLevel.YELLOW, AlertLevel.RED]
        CurrentIdx = 0
        for Idx, L in enumerate(Order):
            if self.Level == L:
                CurrentIdx = Idx
                break
        NextLevel = Order[(CurrentIdx + 1) % len(Order)]
        return self.SetLevel(NextLevel, Reason="Level Cycled", AuthorizedBy="OfficerCycle")

    # Покрокове підвищення готовності (Green -> Yellow -> Red)
    def RaiseLevel(self) -> AlertLevel:
        if self.Level == AlertLevel.GREEN:
            return self.SetLevel(AlertLevel.YELLOW, Reason="Alert Raised", AuthorizedBy="TacticalEscalation")
        elif self.Level == AlertLevel.YELLOW:
            return self.SetLevel(AlertLevel.RED, Reason="Alert Raised", AuthorizedBy="TacticalEscalation")
        return self.Level

    # Покрокове зниження тривоги (Red -> Yellow -> Green)
    def LowerLevel(self) -> AlertLevel:
        if self.Level == AlertLevel.RED:
            return self.SetLevel(AlertLevel.YELLOW, Reason="Alert Lowered", AuthorizedBy="TacticalDeescalation")
        elif self.Level == AlertLevel.YELLOW:
            return self.SetLevel(AlertLevel.GREEN, Reason="Alert Lowered", AuthorizedBy="TacticalDeescalation")
        return self.Level

    def IsLevel(self, LevelInput: any) -> bool:
        return self.Level == self.ParseLevel(LevelInput)

    def IsAlert(self) -> bool:
        return self.Level != AlertLevel.GREEN

    def GetTacticalState(self) -> dict:
        return {
            "ShieldPowerPercent": self.ShieldPower,
            "WeaponsStatus": self.WeaponsStatus,
            "WarpDriveMode": self.WarpDriveMode,
            "SensorsPower": self.SensorsPower,
            "SubspaceComms": self.SubspaceComms,
            "StructuralIntegrity": self.StructuralIntegrity,
            "InertialDampeners": self.InertialDampeners,
            "ActiveTheme": self.ActiveTheme,
            "ActivePaletteColors": self.GetActivePalette(),
            "EmergencyFailover": self.EmergencyFailoverActive,
            "FailoverSubsystem": self.FailoverSubsystem,
        }

    def GetState(self) -> dict:
        return {
            "SystemId": self.SystemId,
            "Version": self.Version,
            "Level": self.Level.Name,
            "Value": self.Level.Value,
            "PreviousLevel": self.PreviousLevel.Name,
            "IsAlertActive": self.IsAlert(),
            "Reason": self.Reason,
            "AuthorizedBy": self.AuthorizedBy,
            "EmergencyFailover": self.EmergencyFailoverActive,
            "Tactical": self.GetTacticalState(),
            "TotalHistoryRecords": len(self.AlertHistory),
        }

    def GetAlertHistory(self) -> list[dict]:
        return list(self.AlertHistory)

# Точки доступу та канонічний експорт
ActiveAlerts = AlertSystem.GetInstance()
AlertStatus = AlertSystem.GetInstance()

def GetAlertSystem(EventBus=None, Controller=None) -> AlertSystem:
    Sys = AlertSystem.GetInstance()
    if EventBus is not None or Controller is not None:
        Sys.Init(EventBus=EventBus, Controller=Controller)
    return Sys

def GetSystemVersion() -> str:
    return str(Version.Release)

getSystemVersion = GetSystemVersion

__all__ = [
    "AlertLevel",
    "AlertConfiguration",
    "AlertSystem",
    "ActiveAlerts",
    "AlertStatus",
    "GetAlertSystem",
    "GetSystemVersion",
    "getSystemVersion",
]