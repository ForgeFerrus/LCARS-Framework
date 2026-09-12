# ◤ LCARS WATCHDOG & HEALTH MONITOR DAEMON
# Автономний фоновий монітор працездатності підсистем та квантового ядра.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge
from lcars.tools.monitor import MonitorAccess
from lcars.engineering.telemetry import EmitTelemetry

class SystemWatchdog(LCARS):
    @staticmethod
    def CheckAll() -> dict:
        Cpu = MonitorAccess.GetCpuUsage()
        Mem = MonitorAccess.GetMemoryUsage()
        Disk = MonitorAccess.GetDiskUsage()
        Net = MonitorAccess.GetNetworkStats()

        Path = Bridge().Load("System.Path")
        Sqlite = Bridge().Load("System.Sqlite")
        Root = Path(__file__).resolve().parents[1] if Path else None

        DbStatus = {}
        if Root and Path and Sqlite:
            Dbs = [
                "lcars/database/00/00-0020-board-computer-manual.db",
                "lcars/database/01/01-0004-odn-black-box.db",
                "lcars/database/03/03-0010-starfleet-registry.db",
                "lcars/database/04/04-0020-copilot-agent.db",
                "lcars/database/04/04-0022-agent-skills.db",
            ]
            for DbRel in Dbs:
                DbPath = Root / DbRel
                if DbPath.exists():
                    Conn = Sqlite.connect(str(DbPath))
                    Cur = Conn.cursor()
                    Cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    Tables = Cur.fetchall()
                    Conn.close()
                    DbStatus[DbPath.name] = f"ONLINE ({len(Tables)} tables)"
                else:
                    DbStatus[DbPath.name] = "MISSING"

        HealthStatus = {
            "CpuLoad": f"{Cpu}%",
            "MemoryPercent": f"{Mem.get('percent', 0)}%",
            "DiskPercent": f"{round(Disk.get('percent', 0), 1)}%",
            "NetworkBytesRecv": Net.get("bytes_recv", 0),
            "Databases": DbStatus,
            "Overall": "NOMINAL" if Cpu < 90 and Mem.get("percent", 0) < 90 else "WARNING",
        }

        return HealthStatus

    @staticmethod
    def RunWatchdog(Continuous: bool = False) -> None:
        Time = Bridge().Load("System.Time")
        print("==========================================================")
        print("   LCARS SYSTEM WATCHDOG & SUBSYSTEM HEALTH DAEMON")
        print("==========================================================")

        while True:
            Report = SystemWatchdog.CheckAll()
            print(f"\n[WATCHDOG] System Health: {Report.get('Overall')}")
            print(f"  * CPU: {Report.get('CpuLoad')} | RAM: {Report.get('MemoryPercent')} | Disk: {Report.get('DiskPercent')}")
            print("  * Isolinear Databases:")
            for DbName, Status in Report.get("Databases", {}).items():
                print(f"    - {DbName}: {Status}")

            EmitTelemetry("Watchdog", f"SYSTEM HEALTH {Report.get('Overall')}: CPU {Report.get('CpuLoad')}, RAM {Report.get('MemoryPercent')}")

            if not Continuous:
                break

            if Time and hasattr(Time, "sleep"):
                Time.sleep(5.0)

class WatchdogRunner(LCARS):
    @staticmethod
    def Main() -> None:
        Sys = Bridge().Load("System.Sys")
        if Sys:
            Sys.dont_write_bytecode = True
        Argv = Sys.argv if (Sys and hasattr(Sys, "argv")) else []
        IsWatch = "--watch" in Argv
        SystemWatchdog.RunWatchdog(Continuous=IsWatch)

if __name__ == "__main__":
    WatchdogRunner.Main()

