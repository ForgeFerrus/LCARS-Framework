# LCARS Framework :: Chronometer v1.0.0
# Хронометр та зоряна дата
# Автор: LCARS Development Team
# Ліцензія: MIT

__version__ = "1.0.0"
__author__ = "LCARS Development Team"
__license__ = "MIT"

import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Chronometer v{version}")  # Вимкнено для UI


# Сервіс для роботи з часом та зоряною датою
class ChronometerService:
    # Сервіс для роботи з часом та зоряною датою
    
    # Масштаб часу
    SpeedFactor: float = 1.0
    # Базовий рік для зоряної дати
    BaseYear: int = 2323
    # Базова дата для зоряної дати
    BaseDatum: float = 0.0

    # Отримати поточний UTC час
    @classmethod
    def GetNow(cls, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        # Поточний UTC час
        return datetime.now(timezone.utc).strftime(format_str)

    # Земна дата в LCARS форматі
    @classmethod
    def GetEarthDate(cls, format_str: str = "%a %b %d %Y // %H:%M:%S") -> str:
        # Земна дата в LCARS форматі
        return datetime.now(timezone.utc).strftime(format_str).upper()

    # Обчислити зоряну дату
    @classmethod
    def GetStardate(cls, base_year: int = None, base_datum: float = None) -> float:
        # Обчислити зоряну дату
        base_year = base_year or cls.BaseYear
        base_datum = base_datum or cls.BaseDatum
        
        now = datetime.now(timezone.utc)
        start_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        start_next_year = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        year_duration = (start_next_year - start_of_year).total_seconds()
        elapsed = (now - start_of_year).total_seconds()
        # Обчислення прогресу року як частки
        progress = elapsed / year_duration if year_duration > 0 else 0.0
        star = base_datum + 1000 * (now.year - base_year) + 1000 * progress
        return round(star * cls.SpeedFactor, 2)

    # Федераційний формат дати
    @classmethod
    def GetFederationDate(cls) -> str:
        # Федераційний формат дати
        now = datetime.now(timezone.utc)
        stardate = cls.GetStardate()
        return f"STARDATE {stardate:.2f} // {cls.GetEarthDate()}"

    # Клінгонський формат дати
    @classmethod
    def GetKlingonDate(cls) -> str:
        # Клінгонський формат дати
        now = datetime.now(timezone.utc)
        day_of_year = now.timetuple().tm_yday
        return f"DAY {day_of_year} OF YEAR {now.year} // {now.strftime('%H:%M')}"
    
    # Ромуланський формат дати
    @classmethod
    def GetRomulanDate(cls) -> str:
        # Ромуланський формат дати
        now = datetime.now(timezone.utc)
        romulan_year = now.year - 2155  # Ромуланська ера
        return f"ROMULAN YEAR {romulan_year} // DAY {now.timetuple().tm_yday}"

    # Встановити масштаб часу
    @classmethod
    def SetSpeedFactor(cls, factor: float):
        # Встановити масштаб часу
        cls.SpeedFactor = max(0.0, float(factor))

    # Отримати поточний масштаб
    @classmethod
    def GetSpeedFactor(cls) -> float:
        # Отримати поточний масштаб
        return cls.SpeedFactor

    # Встановити базовий рік
    @classmethod
    def SetBaseYear(cls, year: int):
        # Встановити базовий рік
        cls.BaseYear = int(year)

    # Отримати базовий рік
    @classmethod
    def GetBaseYear(cls) -> int:
        # Отримати базовий рік
        return cls.BaseYear

    # Встановити базову дату
    @classmethod
    def SetBaseDatum(cls, datum: float):
        # Встановити базову дату
        cls.BaseDatum = float(datum)

    # Отримати базову дату
    @classmethod
    def GetBaseDatum(cls) -> float:
        # Отримати базову дату
        return cls.BaseDatum

    # Час до цільової дати
    @classmethod
    def GetTimeUntil(cls, target_datetime: datetime) -> Dict[str, int]:
        # Час до цільової дати
        now = datetime.now(timezone.utc)
        if target_datetime.tzinfo is None:
            target_datetime = target_datetime.replace(tzinfo=timezone.utc)
        
        delta = target_datetime - now
        
        if delta.total_seconds() < 0:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

    # Час що пройшов з початкової дати
    @classmethod
    def GetElapsedSince(cls, start_datetime: datetime) -> Dict[str, int]:
        # Час що пройшов з початкової дати
        now = datetime.now(timezone.utc)
        if start_datetime.tzinfo is None:
            start_datetime = start_datetime.replace(tzinfo=timezone.utc)
        
        delta = now - start_datetime
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

    # Конвертувати зоряну дату в datetime
    @classmethod
    def ParseStardate(cls, stardate: float) -> datetime:
        # Конвертувати зоряну дату в datetime
        base_year = int(stardate / 1000) + cls.BaseYear
        year_progress = (stardate % 1000) / 1000
        
        start_of_year = datetime(base_year, 1, 1, tzinfo=timezone.utc)
        days_in_year = (datetime(base_year + 1, 1, 1, tzinfo=timezone.utc) - start_of_year).total_seconds()
        ElapsedSeconds = year_progress * days_in_year
        
        return start_of_year + timedelta(seconds=ElapsedSeconds)

    # Час місії
    @classmethod
    def GetMissionTime(cls, start_datetime: datetime) -> str:
        # Час місії
        elapsed = cls.GetElapsedSince(start_datetime)
        
        if elapsed['days'] > 0:
            return f"MISSION TIME: {elapsed['days']}D {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"
        else:
            return f"MISSION TIME: {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"

    # Всі формати дат
    @classmethod
    def GetAllFormats(cls) -> Dict[str, str]:
        # Всі формати дат
        return {
            'utc': cls.GetNow(),
            'earth': cls.GetEarthDate(),
            'stardate': f"{cls.GetStardate():.2f}",
            'federation': cls.GetFederationDate(),
            'klingon': cls.GetKlingonDate(),
            'romulan': cls.GetRomulanDate()
        }

    # Скинути до стандартних налаштувань
    @classmethod
    def reset(cls):
        # Скинути до стандартних налаштувань
        cls.SpeedFactor = 1.0
        cls.BaseYear = 2323
        cls.BaseDatum = 0.0


# Простий таймер
class Timer:
    # Простий таймер
    
    # Конструктор таймера
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.running = False

    # Запустити таймер
    def start(self):
        # Запустити таймер
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.running = True

    # Зупинити таймер
    def stop(self):
        # Зупинити таймер
        if self.running:
            self.end_time = datetime.now(timezone.utc)
            self.running = False

    # Скинути таймер
    def reset(self):
        # Скинути таймер
        self.start_time = None
        self.end_time = None
        self.running = False

    # Час що пройшов
    def elapsed(self) -> Dict[str, int]:
        # Час що пройшов
        if self.start_time is None:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
        
        end = self.end_time or datetime.now(timezone.utc)
        delta = end - self.start_time
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        return {'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}

    # Час що пройшов в секундах
    def ElapsedSeconds(self) -> float:
        # Час що пройшов в секундах
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or datetime.now(timezone.utc)
        delta = end - self.start_time
        return delta.total_seconds()

    # Рядок часу що пройшов
    def ElapsedString(self) -> str:
        # Рядок часу що пройшов
        elapsed = self.elapsed()
        
        if elapsed['days'] > 0:
            return f"{elapsed['days']}D {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"
        else:
            return f"{elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"


# Секундомір
class Stopwatch:
    # Секундомір
    
    # Конструктор секундоміра
    def __init__(self):
        self.times = []
        self.running = False
        self.start_time = None

    # Запустити секундомір
    def start(self):
        # Запустити секундомір
        self.start_time = time.time()
        self.running = True

    # Фіксувати коло
    def lap(self) -> float:
        # Фіксувати коло
        if not self.running:
            return 0.0
        
        current_time = time.time()
        lap_time = current_time - self.start_time
        self.times.append(lap_time)
        self.start_time = current_time
        return lap_time

    # Зупинити секундомір
    def stop(self) -> float:
        # Зупинити секундомір
        if not self.running:
            return 0.0
        
        return self.lap()

    # Скинути секундомір
    def reset(self):
        # Скинути секундомір
        self.times = []
        self.running = False
        self.start_time = None

    # Отримати всі кола
    def GetTimes(self) -> list:
        # Отримати всі кола
        return self.times.copy()

    # Загальний час
    def GetTotalTime(self) -> float:
        # Загальний час
        return sum(self.times)

    # Середній час
    def GetAverageTime(self) -> float:
        # Середній час
        return self.GetTotalTime() / len(self.times) if self.times else 0.0

    # Найкращий час
    def GetBestTime(self) -> float:
        # Найкращий час
        return min(self.times) if self.times else 0.0

    # Найгірший час
    def GetWorstTime(self) -> float:
        # Найгірший час
        return max(self.times) if self.times else 0.0


# Запустити хронометр в CLI
def RunChronometerCli(interval: float = 1.0, format_type: str = "stardate"):
    # Запустити хронометр в CLI
    chronometer = ChronometerService()
    
    running = True
    while running:
        if format_type == "stardate":
            value = chronometer.GetStardate()
            print(f"STARDATE: {value:.2f}")
        elif format_type == "federation":
            print(chronometer.GetFederationDate())
        elif format_type == "earth":
            print(chronometer.GetEarthDate())
        elif format_type == "klingon":
            print(chronometer.GetKlingonDate())
        elif format_type == "romulan":
            print(chronometer.GetRomulanDate())
        else:
            print(chronometer.GetNow())
        
        time.sleep(interval / max(chronometer.GetSpeedFactor(), 0.0001))


# Запустити таймер в CLI
def RunTimerCli(duration: int = 60):
    # Запустити таймер в CLI
    timer = Timer()
    timer.start()
    
    while timer.ElapsedSeconds() < duration:
        elapsed = timer.ElapsedString()
        remaining = duration - timer.ElapsedSeconds()
        print(f"\rELAPSED: {elapsed} | REMAINING: {int(remaining)}s", end="")
        time.sleep(1)
    
    timer.stop()
    print(f"\nTIMER COMPLETED: {timer.ElapsedString()}")


# Запустити секундомір в CLI
def RunStopwatchCli():
    # Запустити секундомір в CLI
    stopwatch = Stopwatch()
    stopwatch.start()
    print("Press Enter for lap time, type 'quit' to stop...")
    
    running = True
    while running:
        user_input = input()
        if user_input.strip().lower() == 'quit':
            running = False
        else:
            lap_time = stopwatch.lap()
            print(f"LAP {len(stopwatch.GetTimes())}: {lap_time:.3f}s")
    
    total_time = stopwatch.stop()
    times = stopwatch.GetTimes()
    
    print(f"\nSTOPWATCH RESULTS:")
    print(f"Total laps: {len(times)}")
    print(f"Total time: {total_time:.3f}s")
    print(f"Average: {stopwatch.GetAverageTime():.3f}s")
    print(f"Best: {stopwatch.GetBestTime():.3f}s")
    print(f"Worst: {stopwatch.GetWorstTime():.3f}s")


# Швидкі функції
def now() -> str:
    return ChronometerService.GetNow()

def stardate() -> float:
    return ChronometerService.GetStardate()

def EarthDate() -> str:
    return ChronometerService.GetEarthDate()

def FederationDate() -> str:
    return ChronometerService.GetFederationDate()

def CreateTimer() -> Timer:
    return Timer()

def CreateStopwatch() -> Stopwatch:
    return Stopwatch()


# Константи
STAR_TREK_ERAS = {
    'enterprise': {'start_year': 2151, 'base_datum': 0},
    'tos': {'start_year': 2265, 'base_datum': 1000},
    'tng': {'start_year': 2364, 'base_datum': 41000},
    'ds9': {'start_year': 2369, 'base_datum': 41500},
    'voyager': {'start_year': 2371, 'base_datum': 41800},
    'picard': {'start_year': 2399, 'base_datum': 58000}
}

LCARS_TIME_FORMATS = {
    'standard': "%Y-%m-%d %H:%M:%S",
    'lcars': "%Y.%j %H:%M:%S",
    'military': "%H%M %Z %d %b %Y",
    'stardate': "STARDATE %.2f"
}
