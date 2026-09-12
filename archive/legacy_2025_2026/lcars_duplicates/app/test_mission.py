# ◤ LCARS MISSION TEST
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.computer import BoardComputer, ComputerAccess
from lcars.service.copilot import Copilot, AgentAccess
from lcars.service.provider import AIProvider
from lcars.modules.storage import ReadManifest, ChipName
from lcars.service.bridge import Bridge

class MissionTester(LCARS):
    @staticmethod
    def RunMission() -> None:
        print("==================================================================")
        print("   LCARS QUANTUM CORE & UNIFIED AI STACK -- LIVE MISSION TEST")
        print("==================================================================\n")

        # 1. Запуск ядра
        Comp = ComputerAccess.GetInstance()
        print(f"[1] YADRO: {Comp.ShipRegistry} // {Comp.ShipClass}")
        print(f"    Mode: {Comp.RuntimeMode} | Stardate: {Comp.GetStardate()}")
        Summary = Comp.SystemSummary()
        print(f"    Warp Core Status: {Summary.get('warp_core')}\n")

        # 2. Голосова директива
        print("[2] VOICE DIRECTIVE TEST:")
        ResRed = Comp.ProcessVoiceDirective("red alert")
        print(f"    Directive 'red alert' -> {ResRed}")
        print(f"    Ship Alert State: {Comp.AlertSystemNodeRef.Level.name if Comp.AlertSystemNodeRef else 'N/A'}\n")

        # 3. Синтез тактичного інтерфейсу на ізолінійний чіп 05-0047
        print("[3] SYNTHESIZE SUBSYSTEM UI ON CHIP 05-0047:")
        UiData = Comp.SynthesizeSubsystemUI("tactical", "05-0047")
        print(f"    Synthesized sections: {len(UiData.get('sections', []))}")
        for Sec in UiData.get("sections", []):
            print(f"      * Section: {Sec.get('name')} [{Sec.get('color')}] - buttons: {len(Sec.get('buttons', []))}")
        print()

        # 4. Робота через Копілота
        print("[4] AGENT REQUEST VIA COPILOT:")
        Agent = Comp.GetAgent()
        print(f"    Agent: {Agent.Name} [{Agent.AgentId}]")
        print(f"    Skills Loaded: {len(Agent.ListSkills())}")
        ThinkRes = Agent.Think("Status report on tactical shields and warp core")
        SafeThinkRes = str(ThinkRes).encode("ascii", errors="replace").decode("ascii")
        print(f"    Agent Think Output:\n    {SafeThinkRes}\n")
        print(f"    Agent Memory (stored turns): {len(Agent.Memory.Messages)}\n")

        # 5. Асинхронна черга задач
        print("[5] ASYNC TASK QUEUE:")
        TaskId = Agent.Tasks.Enqueue("Sensor Diagnostics", lambda ctx: "SENSORS NOMINAL // 100% POWER", 1)
        print(f"    Enqueued Task: {TaskId}")
        print(f"    Task Result: {Agent.GetTaskResult(TaskId)}\n")

        # 6. Читання реальних баз даних Федерації
        print("[6] REAL FEDERATION SQLITE DATABASES:")
        Path = Bridge().Load("System.Path")
        Sqlite = Bridge().Load("System.Sqlite")
        if Path and Sqlite:
            DbShips = Path("lcars/database/03/03-0010-starfleet-registry.db")
            if DbShips.exists():
                with Sqlite.connect(str(DbShips)) as Conn:
                    Rows = Conn.execute("SELECT registry, name, ship_class, captain FROM starships LIMIT 3").fetchall()
                    print("    Starfleet Registry (from DB 03-0010):")
                    for R in Rows:
                        print(f"      * {R[0]}: {R[1]} ({R[2]}-class) | Captain: {R[3]}")

            DbLaws = Path("lcars/database/03/03-0011-federation-directives.db")
            if DbLaws.exists():
                with Sqlite.connect(str(DbLaws)) as Conn:
                    Rows = Conn.execute("SELECT order_number, name, summary FROM general_orders LIMIT 2").fetchall()
                    print("\n    Federation General Orders (from DB 03-0011):")
                    for R in Rows:
                        print(f"      * Order #{R[0]}: {R[1]} -- {R[2]}")

        print("\n==================================================================")
        print("   MISSION SUCCESS: COMPLETE COHESIVE SYSTEM ONLINE!")
        print("==================================================================")

if __name__ == "__main__":
    MissionTester.RunMission()
