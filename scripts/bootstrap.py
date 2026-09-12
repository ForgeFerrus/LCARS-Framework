# ◤ LCARS SYSTEM BOOTSTRAPPER
# Первинний ініціалізатор середовища, баз даних та ізолінійних чіпів.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge
from lcars.app.seed_databases import DatabaseSeeder
from lcars.service.sentinel import SentinelAccess

class SystemBootstrapper(LCARS):
    @staticmethod
    def Main() -> None:
        Bridge.DisableBytecode()
        Path = Bridge().Load("System.Path")
        if not Path:
            return

        Root = Path(__file__).resolve().parents[1]
        print("==========================================================")
        print("   LCARS SYSTEM BOOTSTRAPPER & ENVIRONMENT INITIALIZER")
        print("==========================================================")

        # 1. Створення системних каталогів
        Directories = [
            Root / "logs",
            Root / "lcars" / "database" / "00",
            Root / "lcars" / "database" / "01",
            Root / "lcars" / "database" / "03",
            Root / "lcars" / "database" / "04",
            Root / "lcars" / "database" / "05",
            Root / "lcars" / "database" / "06",
            Root / "lcars" / "engineering" / "chips",
        ]
        for TargetDir in Directories:
            TargetDir.mkdir(parents=True, exist_ok=True)
            print(f"[INIT] Verified Directory: {TargetDir.relative_to(Root)}")

        # 2. Первинне наповнення баз даних
        print("\n[INIT] Seeding Isolinear Databases...")
        DatabaseSeeder.SeedAll()
        print("[INIT] Databases successfully seeded and verified.")

        # 3. Первинне очищення кешу через Sentinel
        print("\n[INIT] Initial Cache Purge via Sentinel...")
        Purged = SentinelAccess.PurgeNow()
        print(f"[INIT] Purged {len(Purged)} cache directories and bytecode files.")

        print("\n==========================================================")
        print("   BOOTSTRAP COMPLETE: SYSTEM READY FOR INITIALIZATION")
        print("==========================================================")

if __name__ == "__main__":
    SystemBootstrapper.Main()
