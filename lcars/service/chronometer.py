# ◤ TITANIUM SYSTEM CHRONOMETER SERVICE // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/service/chronometer.py
# ОПИС: Системна служба часу та зоряного календаря LCARS (Chronometer).
#       Виступає єдиним джерелом істини для розрахунку зоряного часу (Stardate),
#       земних дат, зворотного перетворення, місійних таймерів, масштабів часу
#       та системного пульсу (Chrono.Tick).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.conduit import Service
from lcars.core.signal import ODN, Transmission
from lcars.base.info import Version

class Chronometer(Service):
    # Головна системна служба часу, хронометрії та зоряного календаря
    Name = "chronometer"
    Dependencies = []
    SystemVersion = Version.Release

    # Сигнал системного такту часу
    Tick = Transmission(dict)

    # Системні параметри розрахунку
    SpeedFactor: float = 1.0
    BaseYear: int = 2000
    BaseDatum: float = 48000.0

    def __init__(self, Id: str = "Service.Chronometer"):
        super().__init__(Id=Id)
        self.Version = Version.Release
        self.Passport = Version.Passport()
        TimeModule = LCARS.System.Time
        self.BootTime = TimeModule.time() if TimeModule and hasattr(TimeModule, "time") else 0.0

    # ─── ЖИТТЄВИЙ ЦИКЛ СЛУЖБИ ─────────────────────────────────────────
    def OnInit(self, SystemHostRef = None):
        # Ініціалізація служби в операційному середовищі MasterSystem
        super().OnInit(SystemHostRef)

    def OnStart(self):
        # Запуск служби та трансляція події в шину ODN
        super().OnStart()
        ODN.Transmit(
            "Service.Chronometer.Started",
            Service=self.Name,
            Stardate=self.Stardate(),
            EarthDate=self.EarthDate()
        )

    def OnStop(self):
        # Зупинка служби
        super().OnStop()
        ODN.Transmit("Service.Chronometer.Stopped", Service=self.Name)

    def PulseTick(self) -> dict:
        # Генерація системного часового імпульсу для віджетів та екранів
        Packet = {
            "Stardate": self.Stardate(),
            "EarthDate": self.EarthDate(),
            "FederationDate": self.FederationDate(),
            "Timestamp": self.Timestamp(),
            "SpeedFactor": self.SpeedFactor,
            "Uptime": self.Uptime(),
        }
        self.Tick.Emit(Packet)
        ODN.Transmit("Chrono.Tick", **Packet)
        return Packet

    # ─── БАЗОВИЙ СИСТЕМНИЙ ЧАС ────────────────────────────────────────
    @classmethod
    def Now(cls, Dt: any = None) -> any:
        # Поточний системний час у форматі DateTime
        if Dt is not None:
            return Dt
        DateTimeModule = LCARS.System.DateTime
        if DateTimeModule and hasattr(DateTimeModule, "now"):
            Result = DateTimeModule.now()
            if hasattr(Result, "year") and hasattr(Result, "strftime"):
                return Result
        return None

    @classmethod
    def GetNow(cls) -> any:
        # Системний геттер поточного часу DateTime
        return cls.Now()

    @classmethod
    def Timestamp(cls) -> float:
        # Отримання поточної Unix-мітки часу в секундах
        DateTimeModule = LCARS.System.DateTime
        if DateTimeModule and hasattr(DateTimeModule, "now"):
            Result = DateTimeModule.now()
            if hasattr(Result, "timestamp"):
                return Result.timestamp()
        TimeModule = LCARS.System.Time
        if TimeModule and hasattr(TimeModule, "time"):
            return TimeModule.time()
        return 0.0

    # ─── РОЗРАХУНОК ТА КОНВЕРТАЦІЯ STARDATE ───────────────────────────
    @classmethod
    def Stardate(cls, Dt: any = None) -> float:
        # Розрахунок канонічного зоряного часу (Stardate) за формулою Федерації
        TargetDate = Dt if Dt is not None else cls.Now()
        if not TargetDate or not hasattr(TargetDate, "year"):
            return 0.0
        CalendarModule = LCARS.System.Calendar or LCARS.Import("calendar")
        YearDiff = TargetDate.year - cls.BaseYear
        IsLeap = CalendarModule.isleap(TargetDate.year) if CalendarModule and hasattr(CalendarModule, "isleap") else False
        DaysInYear = 366 if IsLeap else 365
        DayOfYear = TargetDate.timetuple().tm_yday
        FractionOfDay = (TargetDate.hour * 3600 + TargetDate.minute * 60 + TargetDate.second) / 86400.0
        CalculatedStardate = cls.BaseDatum + (YearDiff * 1000.0) + ((DayOfYear - 1 + FractionOfDay) / DaysInYear * 1000.0)
        ScaledStardate = CalculatedStardate * cls.SpeedFactor
        return round(ScaledStardate, 2)

    @classmethod
    def GetStardate(cls, Dt: any = None) -> float:
        # Системний геттер зоряного часу
        return cls.Stardate(Dt)

    @classmethod
    def ParseStardate(cls, StardateVal: float) -> any:
        # Зворотне перетворення зоряного часу в об'єкт DateTime
        DateTimeModule = LCARS.System.DateTime
        TimeDeltaModule = LCARS.System.TimeDelta or LCARS.Import("datetime").timedelta
        CalendarModule = LCARS.System.Calendar or LCARS.Import("calendar")
        RawStardate = float(StardateVal) / max(cls.SpeedFactor, 0.0001)
        Offset = RawStardate - cls.BaseDatum
        YearOffset = int(Offset // 1000)
        Year = cls.BaseYear + YearOffset
        Progress = (Offset % 1000) / 1000.0
        IsLeap = CalendarModule.isleap(Year) if CalendarModule and hasattr(CalendarModule, "isleap") else False
        DaysInYear = 366 if IsLeap else 365
        TotalSeconds = Progress * DaysInYear * 86400.0
        StartOfYear = DateTimeModule(Year, 1, 1)
        return StartOfYear + TimeDeltaModule(seconds=TotalSeconds)

    # ─── ФОРМАТУВАННЯ ДАТ ДЛЯ ВІДЖЕТІВ ТА ЕКРАНІВ ─────────────────────
    @classmethod
    def EarthDate(cls, Dt: any = None, FormatStr: str = "%Y-%m-%d %H:%M:%S") -> str:
        # Форматування дати у стандартному земному форматі
        TargetDate = Dt if Dt is not None else cls.Now()
        if not TargetDate:
            return "UNKNOWN"
        return TargetDate.strftime(FormatStr)

    @classmethod
    def GetEarthDate(cls, Dt: any = None) -> str:
        # Системний геттер земної дати
        return cls.EarthDate(Dt)

    @classmethod
    def FederationDate(cls, Dt: any = None) -> str:
        # Повний офіційний рядок дати Федерації для банерів та статус-рядків
        TargetDate = Dt if Dt is not None else cls.Now()
        StarVal = cls.Stardate(TargetDate)
        EarthStr = cls.EarthDate(TargetDate, "%a %b %d %Y // %H:%M:%S").upper()
        return f"STARDATE {StarVal:.2f} // {EarthStr}"

    @classmethod
    def GetAllFormats(cls, Dt: any = None) -> dict[str, str]:
        # Універсальний словник усіх форматів часу для UI-панелей
        TargetDate = Dt if Dt is not None else cls.Now()
        return {
            "Stardate": f"{cls.Stardate(TargetDate):.2f}",
            "Earth": cls.EarthDate(TargetDate),
            "Federation": cls.FederationDate(TargetDate),
            "Timestamp": str(int(cls.Timestamp())),
        }

    # ─── МІСІЙНІ ТАЙМЕРИ ТА ДЕЛЬТИ ────────────────────────────────────
    @classmethod
    def Delta(cls, StartTime: any, EndTime: any = None) -> float:
        # Розрахунок різниці між двома часовими точками в секундах
        End = EndTime if EndTime is not None else cls.Now()
        if hasattr(StartTime, "timestamp") and hasattr(End, "timestamp"):
            return float(End.timestamp() - StartTime.timestamp())
        if isinstance(StartTime, (int, float)) and isinstance(End, (int, float)):
            return float(End - StartTime)
        return 0.0

    @classmethod
    def ElapsedSince(cls, StartTime: any) -> dict[str, int]:
        # Розрахунок пройденого часу у днях, годинах, хвилинах та секундах
        SecondsTotal = max(0, int(cls.Delta(StartTime)))
        Days = SecondsTotal // 86400
        Remaining = SecondsTotal % 86400
        Hours = Remaining // 3600
        Remaining = Remaining % 3600
        Minutes = Remaining // 60
        Seconds = Remaining % 60
        return {"Days": Days, "Hours": Hours, "Minutes": Minutes, "Seconds": Seconds}

    @classmethod
    def TimeUntil(cls, TargetTime: any) -> dict[str, int]:
        # Розрахунок зворотного відліку часу до цільової події
        SecondsTotal = max(0, int(cls.Delta(cls.Now(), TargetTime)))
        Days = SecondsTotal // 86400
        Remaining = SecondsTotal % 86400
        Hours = Remaining // 3600
        Remaining = Remaining % 3600
        Minutes = Remaining // 60
        Seconds = Remaining % 60
        return {"Days": Days, "Hours": Hours, "Minutes": Minutes, "Seconds": Seconds}

    @classmethod
    def MissionTime(cls, MissionStartTime: any) -> str:
        # Форматований рядок часу тривалості місії (MET)
        Elapsed = cls.ElapsedSince(MissionStartTime)
        if Elapsed["Days"] > 0:
            return f"MET {Elapsed['Days']}D {Elapsed['Hours']:02d}:{Elapsed['Minutes']:02d}:{Elapsed['Seconds']:02d}"
        return f"MET {Elapsed['Hours']:02d}:{Elapsed['Minutes']:02d}:{Elapsed['Seconds']:02d}"

    def Uptime(self) -> float:
        # Час безперервної роботи комп'ютера від старту служби
        TimeModule = LCARS.System.Time
        Current = TimeModule.time() if TimeModule and hasattr(TimeModule, "time") else 0.0
        return max(0.0, Current - self.BootTime)

    # ─── МАСШТАБУВАННЯ ТА СТАТУС ──────────────────────────────────────
    @classmethod
    def SetSpeedFactor(cls, Factor: float) -> None:
        # Встановлення коефіцієнта масштабу часу
        cls.SpeedFactor = max(0.0, float(Factor))

    @classmethod
    def GetSpeedFactor(cls) -> float:
        # Отримання поточного коефіцієнта масштабу часу
        return cls.SpeedFactor

    def GetStatus(self) -> dict:
        # Повний системний зліпок стану служби хронометра
        return {
            "Name": self.Name,
            "Running": self.Running,
            "Healthy": self.Healthy,
            "Stardate": self.Stardate(),
            "EarthDate": self.EarthDate(),
            "FederationDate": self.FederationDate(),
            "Timestamp": self.Timestamp(),
            "SpeedFactor": self.SpeedFactor,
            "Uptime": self.Uptime(),
        }

# Канонічні експортні аліаси зорельота
StardateCalculator = Chronometer
ChronoSubsystem = Chronometer

__all__ = [
    "Chronometer",
    "StardateCalculator",
    "ChronoSubsystem",
]
