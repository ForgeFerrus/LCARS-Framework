# ◤ TITANIUM CHRONOMETER UTILITY APPLICATION // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: programs/utilities/chronometer.py
# ОПИС: Консольна та системна утиліта-хронометр зорельота LCARS.
#       Відображає реальний зоряний час (Stardate), земну дату, тайм-лінії
#       та системний пульс, використовуючи ChronometerService.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS, SystemComponent
from lcars.service.chronometer import StardateCalculator, ChronoSubsystem

class ChronometerApp(SystemComponent):
    # Користувацька програма-утиліта відображення часу та зоряних дат
    def __init__(self):
        super().__init__(SystemId="App.Chronometer")
        self.Service = StardateCalculator()

    def GetCurrentStardate(self) -> float:
        # Отримання поточної зоряної дати
        return self.Service.Stardate()

    def GetCurrentEarthDate(self) -> str:
        # Отримання поточної земної дати
        return self.Service.EarthDate()

    def RunDisplay(self, Iterations: int = 1, IntervalSeconds: float = 1.0, FormatType: str = "stardate") -> None:
        # Виведення часу в термінал
        TimeModule = LCARS.System.Time
        Count = 0
        while Count < Iterations or Iterations <= 0:
            if FormatType == "stardate":
                Value = self.Service.Stardate()
                print(f"[LCARS CHRONOMETER] STARDATE: {Value:.2f}")
            else:
                Value = self.Service.EarthDate()
                print(f"[LCARS CHRONOMETER] EARTH DATE: {Value}")

            Count += 1
            if Iterations > 0 and Count >= Iterations:
                break
            if TimeModule and hasattr(TimeModule, "sleep"):
                TimeModule.sleep(IntervalSeconds / max(self.Service.GetSpeedFactor(), 0.0001))

def RunChronometer(Interval: float = 1.0, Format: str = "stardate", Iterations: int = 1) -> None:
    # Точка запуску утиліти хронометра
    App = ChronometerApp()
    App.RunDisplay(Iterations=Iterations, IntervalSeconds=Interval, FormatType=Format)

__all__ = [
    "ChronometerApp",
    "ChronometerSubsystem",
    "RunChronometer",
]
