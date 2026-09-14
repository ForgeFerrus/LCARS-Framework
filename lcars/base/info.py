# ◤ TITANIUM SYSTEM PASSPORT & SPECIFICATION 🖖
# =============================================================================
# ФАЙЛ: lcars/base/info.py
# ОПИС: Єдиний канонічний паспорт та специфікація системи LCARS Framework.
#       Містить глобальну версію, метадані та делегує обчислення часу хронометру.
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
# Офіційна глобальна версія проекту (встановлюється розробником)
class Version:
    Release = "0.3.0-alpha"
    Status = "Operational"
    Build = "2026.08.28"
    Title = "LCARS Framework"
    System = "Library Computer Access/Retrieval System"
    Specification = "Starfleet Cybernetics Division Directive 24.5"
    Architecture = "Titanium Master Architecture"
    Design = "Michael Okuda 24th Century Canonical Vector Design"
    Platform = "Optical Transport Network (OTN)"

    @classmethod
    # Делегуємо отримання астрономічного часу спеціалізованому системному хронометру
    def Stardate(cls) -> str:
        from lcars.service.chronometer import StardateCalculator
        return str(StardateCalculator.Stardate())

    @classmethod
    def EarthDate(cls) -> str:
        from lcars.service.chronometer import StardateCalculator
        return StardateCalculator.EarthDate()

    @classmethod
    def Metadata(cls) -> dict:
        return cls.Passport()

    # Повний паспорт системи
    @classmethod
    def Passport(cls) -> dict:
        return {
            "title": cls.Title,
            "release": cls.Release,
            "version": cls.Release,
            "build": cls.Build,
            "status": cls.Status,
            "stardate": cls.Stardate(),
            "earth_date": cls.EarthDate(),
            "system": cls.System,
            "specification": cls.Specification,
            "architecture": cls.Architecture,
            "design": cls.Design,
            "platform": cls.Platform,
            "runtime": f"LCARS Quantum Core v{cls.Release} (Operational)",
        }

    # Рядкове представлення паспорта системи
    @classmethod

    def String(cls) -> str:
        return f"{cls.Title} v{cls.Release} [Stardate {cls.Stardate()}]"

# Канонічні аліаси для зворотної сумісності
Passport = Version

VersionInfo = Version
SystemInfo = Version
__all__ = [
    "Version",
    "Passport",
    "VersionInfo",
    "SystemInfo",
]

