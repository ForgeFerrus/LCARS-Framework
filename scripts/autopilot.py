# ◤ LCARS COPILOT RUNNER
# Скрипт запуску AI агента для розробки (реальний автопілот для коду)
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS

class CopilotRunner(LCARS):
    @staticmethod
    def RunCopilot() -> None:
        LCARS.System.Sys.dont_write_bytecode = True

        ProjectRoot = LCARS.System.Path(__file__).resolve().parent.parent
        ProjectRootStr = str(ProjectRoot)

        if ProjectRootStr not in LCARS.System.Sys.path:
            LCARS.System.Sys.path.insert(0, ProjectRootStr)

        print("==========================================================")
        print("   LCARS COPILOT - AI DEVELOPMENT AGENT")
        print("==========================================================")

        BoardComputer = LCARS.Core.BoardComputer.TitaniumBoardComputer
        Copilot = LCARS.Core.Copilot.LCARSCopilot

        if not BoardComputer or not Copilot:
            print("[ERROR] Failed to load Copilot modules")
            return

        BoardComp = BoardComputer()
        Pilot = Copilot(BoardComp)

        print("[COPILOT] AI Agent initialized")
        print("[COPILOT] Ready for development tasks")
        print("[COPILOT] Type 'exit' to quit")
        print("==========================================================")

        if not hasattr(Pilot, "run"):
            print("[ERROR] Copilot does not have run method")
            return

        LCARS.System.Sys.stdout.write("YOU: ")
        LCARS.System.Sys.stdout.flush()

        while True:
            user_input = LCARS.System.Sys.stdin.readline().strip()
            
            if not user_input:
                LCARS.System.Sys.stdout.write("YOU: ")
                LCARS.System.Sys.stdout.flush()
                continue
                
            if user_input.lower() in ("exit", "quit", "q"):
                print("[COPILOT] Session terminated")
                break
            
            print(f"[COPILOT] Processing: {user_input}")
            result = Pilot.run(user_input)
            print(f"[COPILOT] Response: {result}")
            print("==========================================================")
            
            LCARS.System.Sys.stdout.write("YOU: ")
            LCARS.System.Sys.stdout.flush()

if __name__ == "__main__":
    CopilotRunner.RunCopilot()

