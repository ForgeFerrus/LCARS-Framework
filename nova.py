# ◤ TITANIUM LCARS :: NOVA IDE STANDALONE LAUNCHER 🖖
# =============================================================================
# ФАЙЛ: nova.py
# ПРИЗНАЧЕННЯ: Прямий запуск Nova IDE (Tri-Modal Dev Workbench).
# РЕЖИМИ: CODE EDITOR / SUPERDESIGN / MACHINE VISION / COLOR LAB / AST COPILOT
# =============================================================================
from __future__ import annotations
from lcars.base.type import LCARS

def Main():
    SysModule = LCARS.Import("sys")
    ArgsList = SysModule.argv if SysModule and hasattr(SysModule, "argv") else []

    if SysModule and hasattr(SysModule.stdout, "reconfigure"):
        SysModule.stdout.reconfigure(encoding="utf-8")
    if SysModule and hasattr(SysModule.stdin, "reconfigure"):
        SysModule.stdin.reconfigure(encoding="utf-8")

    App = LCARS.Application.instance() or LCARS.Application(ArgsList)

    from lcars.core.computer import BoardComputer
    Computer = BoardComputer.GetInstance()
    Station = Computer.Synthesize("nova")

    ScreenDisplay = getattr(Station, "widget", Station)
    if hasattr(Station, "showFullScreen"):
        Station.showFullScreen()
    elif hasattr(ScreenDisplay, "showFullScreen"):
        ScreenDisplay.showFullScreen()
    elif hasattr(ScreenDisplay, "show"):
        ScreenDisplay.show()

    return App.exec()

if __name__ == "__main__":
    Main()
