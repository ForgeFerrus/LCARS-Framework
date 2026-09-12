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


class ChronometerSubsystem:
    # Сервіс для роботи з часом та зоряною датою
    
    _speed_factor: float = 1.0
    _base_year: int = 2323
    _base_datum: float = 0.0

    @classmethod
    def get_now(cls, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        # Поточний UTC час
        return datetime.now(timezone.utc).strftime(format_str)

    @classmethod
    def get_earth_date(cls, format_str: str = "%a %b %d %Y // %H:%M:%S") -> str:
        # Земна дата в LCARS форматі
        return datetime.now(timezone.utc).strftime(format_str).upper()

    @classmethod
    def get_stardate(cls, base_year: int = None, base_datum: float = None) -> float:
        # Обчислити зоряну дату
        base_year = base_year or cls._base_year
        base_datum = base_datum or cls._base_datum
        
        now = datetime.now(timezone.utc)
        start_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        start_next_year = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
        year_duration = (start_next_year - start_of_year).total_seconds()
        elapsed = (now - start_of_year).total_seconds()
        progress = elapsed / year_duration if year_duration > 0 else 0.0
        star = base_datum + 1000 * (now.year - base_year) + 1000 * progress
        return round(star * cls._speed_factor, 2)

    @classmethod
    def get_federation_date(cls) -> str:
        # Федераційний формат дати
        now = datetime.now(timezone.utc)
        stardate = cls.get_stardate()
        return f"STARDATE {stardate:.2f} // {cls.get_earth_date()}"

    @classmethod
    def get_klingon_date(cls) -> str:
        # Клінгонський формат дати
        now = datetime.now(timezone.utc)
        day_of_year = now.timetuple().tm_yday
        return f"DAY {day_of_year} OF YEAR {now.year} // {now.strftime('%H:%M')}"
    
    @classmethod
    def get_romulan_date(cls) -> str:
        # Ромуланський формат дати
        now = datetime.now(timezone.utc)
        romulan_year = now.year - 2155  # Ромуланська ера
        return f"ROMULAN YEAR {romulan_year} // DAY {now.timetuple().tm_yday}"

    @classmethod
    def set_speed_factor(cls, factor: float):
        # Встановити масштаб часу
        cls._speed_factor = max(0.0, float(factor))

    @classmethod
    def get_speed_factor(cls) -> float:
        # Отримати поточний масштаб
        return cls._speed_factor

    @classmethod
    def set_base_year(cls, year: int):
        # Встановити базовий рік
        cls._base_year = int(year)

    @classmethod
    def get_base_year(cls) -> int:
        # Отримати базовий рік
        return cls._base_year

    @classmethod
    def set_base_datum(cls, datum: float):
        # Встановити базову дату
        cls._base_datum = float(datum)

    @classmethod
    def get_base_datum(cls) -> float:
        # Отримати базову дату
        return cls._base_datum

    @classmethod
    def get_time_until(cls, target_datetime: datetime) -> Dict[str, int]:
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

    @classmethod
    def get_elapsed_since(cls, start_datetime: datetime) -> Dict[str, int]:
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

    @classmethod
    def parse_stardate(cls, stardate: float) -> datetime:
        # Конвертувати зоряну дату в datetime
        base_year = int(stardate / 1000) + cls._base_year
        year_progress = (stardate % 1000) / 1000
        
        start_of_year = datetime(base_year, 1, 1, tzinfo=timezone.utc)
        days_in_year = (datetime(base_year + 1, 1, 1, tzinfo=timezone.utc) - start_of_year).total_seconds()
        elapsed_seconds = year_progress * days_in_year
        
        return start_of_year + timedelta(seconds=elapsed_seconds)

    @classmethod
    def get_mission_time(cls, start_datetime: datetime) -> str:
        # Час місії
        elapsed = cls.get_elapsed_since(start_datetime)
        
        if elapsed['days'] > 0:
            return f"MISSION TIME: {elapsed['days']}D {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"
        else:
            return f"MISSION TIME: {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"

    @classmethod
    def get_all_formats(cls) -> Dict[str, str]:
        # Всі формати дат
        return {
            'utc': cls.get_now(),
            'earth': cls.get_earth_date(),
            'stardate': f"{cls.get_stardate():.2f}",
            'federation': cls.get_federation_date(),
            'klingon': cls.get_klingon_date(),
            'romulan': cls.get_romulan_date()
        }

    @classmethod
    def reset(cls):
        # Скинути до стандартних налаштувань
        cls._speed_factor = 1.0
        cls._base_year = 2323
        cls._base_datum = 0.0


class Timer:
    # Простий таймер
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.running = False

    def start(self):
        # Запустити таймер
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.running = True

    def stop(self):
        # Зупинити таймер
        if self.running:
            self.end_time = datetime.now(timezone.utc)
            self.running = False

    def reset(self):
        # Скинути таймер
        self.start_time = None
        self.end_time = None
        self.running = False

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

    def elapsed_seconds(self) -> float:
        # Час що пройшов в секундах
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or datetime.now(timezone.utc)
        delta = end - self.start_time
        return delta.total_seconds()

    def elapsed_string(self) -> str:
        # Рядок часу що пройшов
        elapsed = self.elapsed()
        
        if elapsed['days'] > 0:
            return f"{elapsed['days']}D {elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"
        else:
            return f"{elapsed['hours']:02d}:{elapsed['minutes']:02d}:{elapsed['seconds']:02d}"


class Stopwatch:
    # Секундомір
    
    def __init__(self):
        self.times = []
        self.running = False
        self.start_time = None

    def start(self):
        # Запустити секундомір
        self.start_time = time.time()
        self.running = True

    def lap(self) -> float:
        # Фіксувати коло
        if not self.running:
            return 0.0
        
        current_time = time.time()
        lap_time = current_time - self.start_time
        self.times.append(lap_time)
        self.start_time = current_time
        return lap_time

    def stop(self) -> float:
        # Зупинити секундомір
        if not self.running:
            return 0.0
        
        return self.lap()

    def reset(self):
        # Скинути секундомір
        self.times = []
        self.running = False
        self.start_time = None

    def get_times(self) -> list:
        # Отримати всі кола
        return self.times.copy()

    def get_total_time(self) -> float:
        # Загальний час
        return sum(self.times)

    def get_average_time(self) -> float:
        # Середній час
        return self.get_total_time() / len(self.times) if self.times else 0.0

    def get_best_time(self) -> float:
        # Найкращий час
        return min(self.times) if self.times else 0.0

    def get_worst_time(self) -> float:
        # Найгірший час
        return max(self.times) if self.times else 0.0


def run_chronometer_cli(interval: float = 1.0, format_type: str = "stardate"):
    # Запустити хронометр в CLI
    chronometer = ChronometerSubsystem()
    
    while True:
        if format_type == "stardate":
            value = chronometer.get_stardate()
            print(f"STARDATE: {value:.2f}")
        elif format_type == "federation":
            print(chronometer.get_federation_date())
        elif format_type == "earth":
            print(chronometer.get_earth_date())
        elif format_type == "klingon":
            print(chronometer.get_klingon_date())
        elif format_type == "romulan":
            print(chronometer.get_romulan_date())
        else:
            print(chronometer.get_now())
        
        time.sleep(interval / max(chronometer.get_speed_factor(), 0.0001))


def run_timer_cli(duration: int = 60):
    # Запустити таймер в CLI
    timer = Timer()
    timer.start()
    
    try:
        while timer.elapsed_seconds() < duration:
            elapsed = timer.elapsed_string()
            remaining = duration - timer.elapsed_seconds()
            print(f"\rELAPSED: {elapsed} | REMAINING: {int(remaining)}s", end="")
            time.sleep(1)
        
        timer.stop()
        print(f"\nTIMER COMPLETED: {timer.elapsed_string()}")
    except KeyboardInterrupt:
        timer.stop()
        print(f"\nTIMER STOPPED: {timer.elapsed_string()}")


def run_stopwatch_cli():
    # Запустити секундомір в CLI
    stopwatch = Stopwatch()
    stopwatch.start()
    
    try:
        while True:
            input("Press Enter for lap time, Ctrl+C to stop...")
            lap_time = stopwatch.lap()
            print(f"LAP {len(stopwatch.get_times())}: {lap_time:.3f}s")
    except KeyboardInterrupt:
        total_time = stopwatch.stop()
        times = stopwatch.get_times()
        
        print(f"\nSTOPWATCH RESULTS:")
        print(f"Total laps: {len(times)}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Average: {stopwatch.get_average_time():.3f}s")
        print(f"Best: {stopwatch.get_best_time():.3f}s")
        print(f"Worst: {stopwatch.get_worst_time():.3f}s")


# Швидкі функції
def now() -> str:
    return ChronometerSubsystem.get_now()

def stardate() -> float:
    return ChronometerSubsystem.get_stardate()

def earth_date() -> str:
    return ChronometerSubsystem.get_earth_date()

def federation_date() -> str:
    return ChronometerSubsystem.get_federation_date()

def create_timer() -> Timer:
    return Timer()

def create_stopwatch() -> Stopwatch:
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
