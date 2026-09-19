# ◤ TITANIUM SYSTEM PASSPORT & SPECIFICATION 🖖
# =============================================================================
# ФАЙЛ: lcars/base/info.py
# ОПИС: Єдиний канонічний паспорт та специфікація системи LCARS Framework.
#       Містить глобальну версію, метадані та делегує обчислення часу хронометру.
# =============================================================================
# Офіційна глобальна версія проекту (встановлюється розробником)
class Version:
    Release = "0.3.0-alpha"
    Status = "Operational"
    Title = "LCARS Framework"
    System = "Library Computer Access/Retrieval System"
    Specification = "Starfleet Cybernetics Division Directive 24.5"
    Architecture = "Titanium Master Architecture"
    Design = "Michael Okuda 24th Century Canonical Vector Design"
    Platform = "Optical Transport Network (OTN)"

    # Астрономічний час (канонічні функції вузла — замінник classmethod)
    def Stardate() -> str: # Зоряна дата
        from lcars.service.chronometer import StardateCalculator
        return str(StardateCalculator.Stardate())

    # Земна дата
    def EarthDate() -> str:
        from lcars.service.chronometer import StardateCalculator
        return StardateCalculator.EarthDate()

    # Метадані
    def Metadata() -> dict:
        return Version.Passport()

    # Повний паспорт системи
    def Passport() -> dict:
        return {
            "title": Version.Title,
            "release": Version.Release,
            "version": Version.Release,
            "status": Version.Status,
            "stardate": Version.Stardate(), # Зоряна дата
            "earth_date": Version.EarthDate(), # Земна дата
            "system": Version.System, # Система
            "specification": Version.Specification, # Специфікація
            "architecture": Version.Architecture, # Архітектура
            "design": Version.Design, # Дизайн
            "platform": Version.Platform, # Платформа
            "runtime": f"LCARS Quantum Core v{Version.Release} (Operational)",
        }

    # Рядкове представлення паспорта системи
    def String() -> str:
        return f"{Version.Title} v{Version.Release} [Stardate {Version.Stardate()}]"

    # Канонічний отримувач релізу (вузол інженерного контуру: VersionInfo.GetVersion())
    def GetVersion() -> str:
        return Version.Release

# Канонічні аліаси для зворотної сумісності
Passport = Version
VersionInfo = Version
SystemInfo = Version
getVersion = Version.GetVersion
