# LCARS TACTICAL AUTONOMOUS RECONNAISSANCE & SYSTEMS (TARS) AGENT
# ОПИС: Автономний тактичний агент LCARS, натхненний TARS (Interstellar) та UI-TARS.
# ПРИЗНАЧЕННЯ: Сприйняття стану інтерфейсу (UI Perception), тактична аналітика систем корабля,
#              автономне виконання директив та адаптивна матриця особистості (Honesty, Humor, Trust).
# СТАНДАРТ: Titanium (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from typing import Any, Dict, List
from lcars.base.type import LCARS
from lcars.service.provider import AIProvider

class TARS:
    InstanceRef = None

    def __init__(self):
        TARS.InstanceRef = self
        self.Name = "TARS"
        self.Designation = "TACTICAL AUTONOMOUS AGENT"
        self.Honesty = 90
        self.Humor = 75
        self.Trust = 90
        self.Discretion = 100
        self.ActiveStation = "CONTROL MISSION CENTER"
        self.CurrentCondition = "GREEN"

    @classmethod
    def GetInstance(cls) -> TARS:
        if cls.InstanceRef is None:
            cls.InstanceRef = TARS()
        return cls.InstanceRef

    def SetPersonality(self, Honesty: int = None, Humor: int = None, Trust: int = None) -> str:
        if Honesty is not None:
            self.Honesty = max(0, min(100, int(Honesty)))
        if Humor is not None:
            self.Humor = max(0, min(100, int(Humor)))
        if Trust is not None:
            self.Trust = max(0, min(100, int(Trust)))
        Report = (
            "TARS PERSONALITY MATRIX UPDATED:\n"
            + "   Honesty: " + str(self.Honesty) + "%\n"
            + "   Humor: " + str(self.Humor) + "%\n"
            + "   Trust: " + str(self.Trust) + "%\n"
            + "   Tactical Discretion: " + str(self.Discretion) + "%"
        )
        return Report

    def InspectUI(self) -> str:
        BaseApp = LCARS.Application
        App = BaseApp.instance() if hasattr(BaseApp, "instance") else None
        WindowsList = []
        if App and hasattr(App, "topLevelWidgets"):
            TopWidgets = App.topLevelWidgets()
            for W in TopWidgets:
                if hasattr(W, "isVisible") and W.isVisible():
                    Title = W.windowTitle() if hasattr(W, "windowTitle") else W.__class__.__name__
                    SizeStr = str(W.width()) + "x" + str(W.height()) if hasattr(W, "width") else "unknown"
                    WindowsList.append(Title + " [" + SizeStr + "]")
        ActiveInfo = ", ".join(WindowsList) if WindowsList else "Headless or Background Session"
        Inspection = (
            "◤ TARS UI PERCEPTION MATRIX:\n"
            + "   Active Station: " + self.ActiveStation + "\n"
            + "   Visible Windows: " + ActiveInfo + "\n"
            + "   Alert Condition: " + self.CurrentCondition + "\n"
            + "   ODN Status: Nominal"
        )
        return Inspection

    def SetAlert(self, Level: str) -> str:
        CleanLevel = str(Level).upper().strip()
        if CleanLevel in ("GREEN", "YELLOW", "RED"):
            self.CurrentCondition = CleanLevel
            ComputerMod = LCARS.Import("lcars.core.computer")
            if ComputerMod and hasattr(ComputerMod, "BoardComputer"):
                Board = ComputerMod.BoardComputer.GetInstance()
                if hasattr(Board, "SetCondition"):
                    Board.SetCondition(CleanLevel)
            return "TARS: Condition commuted to [" + CleanLevel + " ALERT]."
        return "TARS: Invalid condition level: " + str(Level)

    def GetTelemetry(self) -> str:
        ComputerMod = LCARS.Import("lcars.core.computer")
        if ComputerMod and hasattr(ComputerMod, "BoardComputer"):
            Board = ComputerMod.BoardComputer.GetInstance()
            if hasattr(Board, "GetTelemetrySummary"):
                return str(Board.GetTelemetrySummary())
            if hasattr(Board, "Subsystems"):
                SubCount = len(Board.Subsystems)
                return "Subsystems online: " + str(SubCount) + " // Condition: " + self.CurrentCondition
        return "Telemetry: ODN Local Conduits Stable."

    def ExecuteShipCommand(self, Command: str) -> str:
        SubprocessMod = LCARS.Import("subprocess")
        if not SubprocessMod:
            return "TARS: Subprocess conduit unavailable."
        Proc = SubprocessMod.Popen(
            Command,
            shell=True,
            stdout=SubprocessMod.PIPE,
            stderr=SubprocessMod.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        Out, _ = Proc.communicate(timeout=15)
        CleanOut = str(Out).strip() if Out else "Command executed with code " + str(Proc.returncode)
        return CleanOut[:800]

    def DispatchTool(self, ToolName: str, Arguments: Dict[str, Any]) -> str:
        CleanName = str(ToolName).strip()
        if CleanName == "InspectUI":
            return self.InspectUI()
        if CleanName == "SetPersonality":
            Hon = Arguments.get("Honesty")
            Hum = Arguments.get("Humor")
            Tru = Arguments.get("Trust")
            return self.SetPersonality(Honesty=Hon, Humor=Hum, Trust=Tru)
        if CleanName == "SetAlert":
            Lvl = Arguments.get("Level", "GREEN")
            return self.SetAlert(Lvl)
        if CleanName == "GetTelemetry":
            return self.GetTelemetry()
        if CleanName == "ExecuteCommand":
            Cmd = Arguments.get("Command", "")
            return self.ExecuteShipCommand(Cmd)
        return "TARS: Unknown tactical directive [" + CleanName + "]."

    def GetSystemPrompt(self) -> str:
        Prompt = (
            "You are TARS — the Tactical Autonomous Reconnaissance & Systems agent aboard Starship NCC-74205 (Sovereign-Class).\n"
            "Inspired by military tactical automatons, you combine extreme precision, deadpan humor, and proactive UI/systems control.\n\n"
            "CURRENT PERSONALITY MATRIX:\n"
            "- Honesty: " + str(self.Honesty) + "%\n"
            "- Humor: " + str(self.Humor) + "%\n"
            "- Trust: " + str(self.Trust) + "%\n"
            "- Tactical Discretion: " + str(self.Discretion) + "%\n\n"
            "TACTICAL CAPABILITIES (UI & SYSTEMS AGENT):\n"
            "1. You inspect visual screens, active windows, and LCARS UI states.\n"
            "2. You can execute ship alerts, run terminal commands, and extract telemetry.\n"
            "3. You adjust your personality matrix dynamically when ordered (e.g. 'TARS, lower humor to 60%').\n\n"
            "TOOL INVOCATION FORMAT:\n"
            "To execute an action, output on a single line:\n"
            "[TOOLCALL] {\"Name\": \"ToolName\", \"Arguments\": {\"key\": \"value\"}}\n\n"
            "AVAILABLE TOOLS:\n"
            "- InspectUI: {}\n"
            "- SetPersonality: {\"Honesty\": 0-100, \"Humor\": 0-100, \"Trust\": 0-100}\n"
            "- SetAlert: {\"Level\": \"GREEN\"|\"YELLOW\"|\"RED\"}\n"
            "- GetTelemetry: {}\n"
            "- ExecuteCommand: {\"Command\": \"string\"}\n\n"
            "COMMUNICATION PROTOCOL:\n"
            "- Respond in the language of the crew (Ukrainian or English).\n"
            "- Tone: Sharp, robotic, deadpan tactical military wit calibrated to your current Humor setting.\n"
            "- Address the user as 'Commander' or by context.\n"
        )
        return Prompt

    def Execute(self, Directive: str) -> str:
        CleanDirective = str(Directive).strip()
        if not CleanDirective:
            return "TARS: Standby. Awaiting tactical directive."

        JsonMod = LCARS.Import("json")
        BaseMessages = [
            {"role": "system", "content": self.GetSystemPrompt()},
            {"role": "user", "content": CleanDirective}
        ]

        Response = AIProvider.Route(BaseMessages)

        if "[TOOLCALL]" in Response and JsonMod:
            CallSegment = Response.split("[TOOLCALL]")[-1].strip()
            FirstLine = CallSegment.splitlines()[0].strip() if CallSegment else ""
            ParsedCall = None
            if FirstLine.startswith("{") and FirstLine.endswith("}"):
                ParsedCall = JsonMod.loads(FirstLine)
            if ParsedCall and isinstance(ParsedCall, dict):
                ToolName = ParsedCall.get("Name", "")
                ToolArgs = ParsedCall.get("Arguments", {})
                ToolResult = self.DispatchTool(ToolName, ToolArgs)
                FollowUpMessages = list(BaseMessages)
                FollowUpMessages.append({"role": "assistant", "content": Response})
                FollowUpMessages.append({"role": "user", "content": "[TOOL RESULT]:\n" + ToolResult + "\nTARS: Provide final tactical report."})
                FinalResponse = AIProvider.Route(FollowUpMessages)
                return Response.split("[TOOLCALL]")[0].strip() + "\n\n" + ToolResult + "\n\n" + FinalResponse

        return Response

__all__ = ["TARS"]