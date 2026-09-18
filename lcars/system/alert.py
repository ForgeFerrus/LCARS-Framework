# ◤ TITANIUM SYSTEM ALERT & TACTICAL CONTROLLER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/alert.py
# ОПИС: Тактичний контролер бойової готовності та розподілу станів LCARS.
#       КАНОНІЧНІ РІВНІ ТРИВОГ ЗОРЯНОГО ФЛОТУ:
#       - GREEN (0 / Nominal)  — штатний режим, стандартне освітлення, щити 0%.
#       - YELLOW (1 / Caution) — підвищена готовність, бурштиновий інтерфейс, щити 50%.
#       - RED (2 / Tactical)   — бойова тривога, червона пульсація, щити 100%.
# СТАНДАРТ: Titanium LCARS (Pure PascalCase, No-Init, No-Property, Zero-Underscore, No-Get).
# =============================================================================

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version
from lcars.core.signal import ODN, Transmission
from lcars.base.default import Palette

# =============================================================================
# 1. СТАТУСИ РІВНІВ БОЙОВОЇ ГОТОВНОСТІ (ALERT LEVELS)
# =============================================================================
class AlertLevel:
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

    # Канонічні імена рівнів
    Names = {
        0: "GREEN",
        1: "YELLOW",
        2: "RED",
    }

    @staticmethod
    def Designation(Level: int) -> str:
        return AlertLevel.Names.get(int(Level), "GREEN")

# =============================================================================
# 2. АРХІТЕКТУРНА КОНФІГУРАЦІЯ ТРИВОГ (ALERT CONFIGURATION)
# =============================================================================
class AlertConfiguration(LCARS):
    Palettes = {
        "GREEN": Palette.Buttons,
        "YELLOW": Palette.Yellow,
        "RED": Palette.Red,
    }

    Thresholds = {
        "CpuCritical": 92.0,
        "CpuWarning": 80.0,
        "MemoryCritical": 92.0,
        "MemoryWarning": 82.0,
    }

    Sounds = {
        "GREEN": "alert_green",
        "YELLOW": "alert_yellow",
        "RED": "alert_red",
    }

    Themes = {
        "GREEN": "Standard",
        "YELLOW": "YellowAlert",
        "RED": "RedAlert",
    }

# =============================================================================
# 3. СИСТЕМНИЙ КОНТРОЛЕР ТРИВОГ (ALERT SYSTEM & ACTUATOR)
# =============================================================================
class AlertSystem(SystemComponent):
    TypeName = "LCARSAlertSystem"
    SystemId = "System.Alert"
    Id = "System.Alert"
    SystemVersion = Version.Release

    Level = AlertLevel.GREEN
    PreviousLevel = AlertLevel.GREEN
    Reason = "System Nominal"
    AuthorizedBy = "SystemBootstrap"
    AlertHistory = []

    # Фізичні та тактичні параметри корабля
    ShieldPower = 0.0
    WeaponsStatus = "Safe"
    WarpDriveMode = "Cruise"
    SensorsPower = "Standard"
    SubspaceComms = "Online"
    StructuralIntegrity = "Nominal"
    InertialDampeners = "Standard"
    ActiveTheme = "Standard"

    EmergencyFailoverActive = False
    FailoverSubsystem = ""
    IsDrillActive = False

    # Сигнали ODN
    Changed = Transmission(dict)
    LevelRaised = Transmission(dict)
    LevelLowered = Transmission(dict)
    EmergencyFailover = Transmission(dict)

    # Канонічне позначення поточного рівня тривоги
    def LevelDesignation(self) -> str:
        return AlertLevel.Designation(self.Level)

    # Активна оптична палітра
    def Palette(self) -> list[str]:
        return AlertConfiguration.Palettes.get(self.LevelDesignation(), Palette.Buttons)

    # Головна точка повного перемикання стану та вигляду фреймворка
    def SetLevel(self, LevelInput: any, Reason: str = "Manual Directive", AuthorizedBy: str = "Captain") -> int:
        OldLevel = self.Level
        NewLevel = self.ParseLevel(LevelInput)

        if self.Level != NewLevel:
            NowTime = LCARS.System.Time.time() if hasattr(LCARS.System, "Time") and callable(getattr(LCARS.System.Time, "time", None)) else 0.0
            self.PreviousLevel = OldLevel
            self.Level = NewLevel
            self.Reason = str(Reason)
            self.AuthorizedBy = str(AuthorizedBy)

            # Фіксація в історії тривог
            HistoryRecord = {
                "Timestamp": round(NowTime, 2),
                "FromLevel": AlertLevel.Designation(OldLevel),
                "ToLevel": AlertLevel.Designation(NewLevel),
                "Reason": self.Reason,
                "AuthorizedBy": self.AuthorizedBy,
                "IsFailover": self.EmergencyFailoverActive,
            }
            self.AlertHistory.append(HistoryRecord)

            # 1. Перемикання тактичного стану
            self.ApplyTacticalProfile(NewLevel)

            # 2. Синхронізація з Інженерним комплексом
            self.SyncEngineeringLayer(NewLevel)

            # 3. Синхронізація з Системним Середовищем
            self.SyncSystemEnvironment(NewLevel)

            # 4. Активація звукової сигналізації
            self.ActuateAlertSound(NewLevel)

            # 5. Оновлення візуальної теми інтерфейсу всього фреймворка
            self.ActuateInterfaceTheme(NewLevel)

            # 6. Квантово-оптична мережа ODN
            TelemetryMap = self.Telemetry()
            ODN.Transmit(
                "Alert.Changed",
                Level=AlertLevel.Designation(NewLevel),
                Value=NewLevel,
                Previous=AlertLevel.Designation(OldLevel),
                Reason=self.Reason,
                AuthorizedBy=self.AuthorizedBy,
                ActiveColors=self.Palette(),
                Tactical=self.TacticalProfile()
            )
            ODN.Transmit("UI.AlertChanged", Level=AlertLevel.Designation(NewLevel), Theme=self.ActiveTheme, Colors=self.Palette())

            # 7. Сигнали передачі
            self.Changed.Emit(TelemetryMap)
            if NewLevel > OldLevel:
                self.LevelRaised.Emit(TelemetryMap)
            else:
                self.LevelLowered.Emit(TelemetryMap)

        return self.Level

    # Налаштування інженерних та тактичних параметрів
    def ApplyTacticalProfile(self, Level: int) -> None:
        LevelName = AlertLevel.Designation(Level)
        self.ActiveTheme = AlertConfiguration.Themes.get(LevelName, "Standard")

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

    # Синхронізація з Інженерним комплексом корабля
    def SyncEngineeringLayer(self, Level: int) -> None:
        ODN.Transmit("Engineering.AlertSync", AlertLevel=AlertLevel.Designation(Level))

    # Синхронізація з Системним Середовищем
    def SyncSystemEnvironment(self, Level: int) -> None:
        LevelName = AlertLevel.Designation(Level)
        import lcars.base.default as DefaultMod
        DefaultMod.SystemState = LevelName
        ODN.Transmit("System.Environment.Alert", AlertLevel=LevelName)

    # Активація звукової сигналізації
    def ActuateAlertSound(self, Level: int) -> None:
        LevelName = AlertLevel.Designation(Level)
        SoundName = AlertConfiguration.Sounds.get(LevelName, "alert_green")
        ODN.Transmit("Audio.PlayAlert", Sound=SoundName, Loop=(Level != AlertLevel.GREEN))

    # Оновлення візуального оформлення фреймворка
    def ActuateInterfaceTheme(self, Level: int) -> None:
        ActiveColors = self.Palette()
        ODN.Transmit("UI.ThemeChanged", Theme=self.ActiveTheme, Level=AlertLevel.Designation(Level), Colors=ActiveColors)
        ODN.Transmit("UI.PaletteChanged", CurrentAlert=AlertLevel.Designation(Level), Colors=ActiveColors)

    # Обробка критичних збоїв, помилок та аварійний перехід
    def Failover(self, FailedSubsystem: str, ErrorMessage: str, Criticality: str = "HIGH") -> int:
        self.EmergencyFailoverActive = True
        self.FailoverSubsystem = str(FailedSubsystem)
        CritUpper = str(Criticality or "").upper()

        FailoverEvent = {
            "Subsystem": FailedSubsystem,
            "Error": ErrorMessage,
            "Criticality": CritUpper,
            "Timestamp": LCARS.System.Time.time() if hasattr(LCARS.System, "Time") and callable(getattr(LCARS.System.Time, "time", None)) else 0.0,
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

    # Оцінка апаратної телеметрії
    def AuditTelemetry(self, Cpu: float = 0.0, Memory: float = 0.0) -> int:
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
    def TriggerDrill(self, LevelInput: any = AlertLevel.RED) -> int:
        self.IsDrillActive = True
        TargetLvl = self.ParseLevel(LevelInput)
        return self.SetLevel(TargetLvl, Reason="Tactical Readiness Drill", AuthorizedBy="CommandDrill")

    # Зняття тривоги
    def ClearAlert(self, AuthorizedBy: str = "Captain") -> int:
        self.EmergencyFailoverActive = False
        self.IsDrillActive = False
        return self.SetLevel(AlertLevel.GREEN, Reason="All Systems Nominal", AuthorizedBy=AuthorizedBy)

    # Швидка бойова тривога (Red Alert)
    def EngageRedAlert(self, Reason: str = "Tactical Engagement", AuthorizedBy: str = "Captain") -> int:
        return self.SetLevel(AlertLevel.RED, Reason=Reason, AuthorizedBy=AuthorizedBy)

    # Швидка підвищена готовність (Yellow Alert)
    def EngageYellowAlert(self, Reason: str = "Heightened Readiness", AuthorizedBy: str = "TacticalOfficer") -> int:
        return self.SetLevel(AlertLevel.YELLOW, Reason=Reason, AuthorizedBy=AuthorizedBy)

    # Парсинг вхідного значення у канонічний числовий рівень (0, 1, 2)
    def ParseLevel(self, LevelInput: any) -> int:
        if isinstance(LevelInput, int):
            return max(0, min(2, LevelInput))
        Norm = str(LevelInput or "").upper().strip()
        if "RED" in Norm or "TACTICAL" in Norm or "COMBAT" in Norm or "BATTLE" in Norm:
            return AlertLevel.RED
        elif "YELLOW" in Norm or "CAUTION" in Norm or "STANDBY" in Norm:
            return AlertLevel.YELLOW
        return AlertLevel.GREEN

    # Послідовне циклічне перемикання (Green -> Yellow -> Red -> Green)
    def CycleLevel(self) -> int:
        NextLevel = (self.Level + 1) % 3
        return self.SetLevel(NextLevel, Reason="Level Cycled", AuthorizedBy="OfficerCycle")

    # Покрокове підвищення готовності (Green -> Yellow -> Red)
    def RaiseLevel(self) -> int:
        if self.Level < AlertLevel.RED:
            return self.SetLevel(self.Level + 1, Reason="Alert Raised", AuthorizedBy="TacticalEscalation")
        return self.Level

    # Покрокове зниження тривоги (Red -> Yellow -> Green)
    def LowerLevel(self) -> int:
        if self.Level > AlertLevel.GREEN:
            return self.SetLevel(self.Level - 1, Reason="Alert Lowered", AuthorizedBy="TacticalDeescalation")
        return self.Level

    # Перевірка чи активний певний рівень
    def IsLevel(self, LevelInput: any) -> bool:
        return self.Level == self.ParseLevel(LevelInput)

    # Чи активна будь-яка тривога (не зелений режим)
    def IsAlert(self) -> bool:
        return self.Level != AlertLevel.GREEN

    # Тактичний профіль корабля
    def TacticalProfile(self) -> dict:
        return {
            "ShieldPowerPercent": self.ShieldPower,
            "WeaponsStatus": self.WeaponsStatus,
            "WarpDriveMode": self.WarpDriveMode,
            "SensorsPower": self.SensorsPower,
            "SubspaceComms": self.SubspaceComms,
            "StructuralIntegrity": self.StructuralIntegrity,
            "InertialDampeners": self.InertialDampeners,
            "ActiveTheme": self.ActiveTheme,
            "ActivePaletteColors": self.Palette(),
            "EmergencyFailover": self.EmergencyFailoverActive,
            "FailoverSubsystem": self.FailoverSubsystem,
        }

    # Повна телеметрія контролера тривог
    def Telemetry(self) -> dict:
        return {
            "SystemId": self.SystemId,
            "Version": self.SystemVersion,
            "Level": AlertLevel.Designation(self.Level),
            "Value": self.Level,
            "PreviousLevel": AlertLevel.Designation(self.PreviousLevel),
            "IsAlertActive": self.IsAlert(),
            "Reason": self.Reason,
            "AuthorizedBy": self.AuthorizedBy,
            "EmergencyFailover": self.EmergencyFailoverActive,
            "Tactical": self.TacticalProfile(),
            "TotalHistoryRecords": len(self.AlertHistory),
        }

    # Журнал історії зміни тривог
    def History(self) -> list[dict]:
        return list(self.AlertHistory)

# Канонічний активний вузол системи LCARS (автоматично ініціалізований як SystemComponent)
AlertControl = AlertSystem()
ActiveAlerts = AlertControl
AlertStatus = AlertControl

# Реєстрація в ядрі LCARS
LCARS.Alert = AlertControl
LCARS.Register("System.Alert", AlertControl)
