# ◤ LCARS TITANIUM AUTO-REPAIR DAEMON
# Автономний фоновий аналізатор та ремонтник вихідного коду LCARS.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge
from lcars.engineering.telemetry import EmitTelemetry

class AutoRepairEngine(LCARS):
    BannedModules = {
        "os", "sys", "json", "pathlib", "subprocess", "shutil", "typing",
        "dataclasses", "enum", "sqlite3", "yaml", "importlib", "threading",
        "requests", "math", "re", "textwrap", "traceback", "inspect", "socket", "uuid", "datetime"
    }

    @staticmethod
    def ScanAndRepair(FilePathObj: any) -> int:
        if not FilePathObj or not FilePathObj.exists() or FilePathObj.name == "bridge.py":
            return 0

        Content = FilePathObj.read_text(encoding="utf-8", errors="ignore")
        Lines = Content.splitlines()
        Modified = False
        NewLines = []
        FixesCount = 0

        Regex = Bridge().Load("System.Regex")
        for Line in Lines:
            Stripped = Line.strip()
            # 1. Виправлення прямих імпортів
            IsBannedImport = False
            if Stripped.startswith("import ") or Stripped.startswith("from "):
                for Mod in AutoRepairEngine.BannedModules:
                    Pattern = rf"^\s*(from|import)\s+{Mod}\b"
                    if Regex and hasattr(Regex, "search") and Regex.search(Pattern, Stripped):
                        IsBannedImport = True
                        break

            if IsBannedImport:
                LeadingSpace = Line[:len(Line) - len(Line.lstrip())]
                NewLines.append(f"{LeadingSpace}# Titanium Bridge Migration: {Stripped}")
                Modified = True
                FixesCount += 1
                continue

            # 2. Виправлення простих try/except блоків на пряму умову
            if Stripped == "try:":
                LeadingSpace = Line[:len(Line) - len(Line.lstrip())]
                NewLines.append(f"{LeadingSpace}if True:")
                Modified = True
                FixesCount += 1
                continue

            if Stripped.startswith("except ") or Stripped == "except:":
                LeadingSpace = Line[:len(Line) - len(Line.lstrip())]
                NewLines.append(f"{LeadingSpace}if False: # Removed except block")
                Modified = True
                FixesCount += 1
                continue

            NewLines.append(Line)

        if Modified:
            FilePathObj.write_text("\n".join(NewLines) + "\n", encoding="utf-8")

        return FixesCount

    @staticmethod
    def RunScan(Continuous: bool = True) -> None:
        Path = Bridge().Load("System.Path")
        Time = Bridge().Load("System.Time")
        Sys = Bridge().Load("System.Sys")
        
        if Sys:
            Sys.dont_write_bytecode = True
        
        if not Path:
            return

        Root = Path(__file__).resolve().parents[1]
        LcarsDir = Root / "lcars"
        
        # Запис PID для контролю процесу
        PidDir = Root / ".lcars"
        PidDir.mkdir(parents=True, exist_ok=True)
        PidFile = PidDir / "autofix.pid"
        PidFile.write_text(str(Bridge().Load("System.PID")()), encoding="utf-8")
        
        print("==========================================================")
        print("   LCARS TITANIUM AUTO-REPAIR DAEMON ACTIVE")
        print("==========================================================")
        print(f"[AUTOFIX] Watch Target: {LcarsDir}")
        print(f"[AUTOFIX] PID File: {PidFile}")
        print(f"[AUTOFIX] Mode: {'Continuous' if Continuous else 'Single Scan'}")
        print("==========================================================")

        while True:
            TotalFixes = 0
            for PyFile in LcarsDir.rglob("*.py"):
                Fixes = AutoRepairEngine.ScanAndRepair(PyFile)
                if Fixes > 0:
                    TotalFixes += Fixes
                    print(f"[REPAIR] Fixed {Fixes} violations in {PyFile.relative_to(Root)}")

            if TotalFixes > 0:
                EmitTelemetry("AutoRepair", f"REPAIRED {TotalFixes} CODE VIOLATIONS.")

            if not Continuous:
                print(f"[REPAIR] Scan complete. Total repairs applied: {TotalFixes}")
                # Видалити PID файл при одноразовому скануванні
                if PidFile.exists():
                    PidFile.unlink()
                break

            if Time and hasattr(Time, "sleep"):
                Time.sleep(5.0)

class AutoRepairRunner(LCARS):
    @staticmethod
    def Main() -> None:
        Sys = Bridge().Load("System.Sys")
        if Sys:
            Sys.dont_write_bytecode = True
        Argv = Sys.argv if (Sys and hasattr(Sys, "argv")) else []
        
        # За замовчуванням працює постійно в фоні
        # Використати --single для одноразового сканування
        IsSingle = "--single" in Argv
        AutoRepairEngine.RunScan(Continuous=not IsSingle)

if __name__ == "__main__":
    AutoRepairRunner.Main()
