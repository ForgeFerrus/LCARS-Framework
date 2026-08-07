# LCARS command core.
# Призначення: єдиний каталог директив для console, terminal, onboard і агентів.
# Команда не виконує зовнішні процеси та не створює власну шину: результат і
# життєвий цикл публікуються в глобальній ізолінійній мережі ODN.

from dataclasses import dataclass, field
from time import time
from typing import Any, Callable, Dict, List, Optional

from lcars.base.type import SystemComponent
from lcars.base.version import getVersion
from lcars.core.signal import ODN, Transmission
from lcars.system.alert import AlertLevel, AlertSystem


@dataclass
class Directive:
    Name: str
    Handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    Description: str
    Parameters: Dict[str, str] = field(default_factory=dict)
    Level: str = "SYSTEM"

    def Export(self) -> Dict[str, Any]:
        return {
            "Name": self.Name,
            "Description": self.Description,
            "Parameters": dict(self.Parameters),
            "Level": self.Level,
        }


class Command(SystemComponent):
    # Transmission тут тільки тип сигналу результату; фактичний transport — ODN.
    Completed = Transmission(dict)
    Failed = Transmission(dict)

    def __init__(self, Id: str = "COMMAND"):
        super().__init__(Id)
        self.Started = time()
        self.Active = True
        self.Alert = AlertSystem()
        self.Alert.Init(EventBus=ODN)
        self.History: List[Dict[str, Any]] = []
        self.Directives: Dict[str, Directive] = {}
        self.RegisterDirectives()
        self.Publish("Command.Ready", self.GetStatus())

    def Publish(self, Channel: str, Payload: Dict[str, Any]) -> None:
        if hasattr(ODN, "Emit"):
            ODN.Emit(Channel, Payload)

    def RegisterDirectives(self) -> None:
        self.AddDirective("STATUS", self.GetStatus, "Повертає стан командного вузла.")
        self.AddDirective("VERSION", self.Version, "Повертає версію LCARS.")
        self.AddDirective("BIOS", self.Bios, "Повертає діагностичний звіт BIOS.")
        self.AddDirective("ALERT", self.SetAlert, "Змінює рівень системної тривоги.", {"Level": "GREEN, YELLOW, RED або 0, 1, 2"})
        self.AddDirective("SHUTDOWN", self.Shutdown, "Запитує завершення сесії.")
        self.AddDirective("REBOOT", self.Reboot, "Запитує перезапуск сесії.")
        self.AddDirective("HELP", self.Help, "Повертає каталог директив.")

    def AddDirective(self, Name: str, Handler: Callable, Description: str, Parameters: Optional[Dict[str, str]] = None, Level: str = "SYSTEM") -> None:
        Key = str(Name).strip().upper()
        self.Directives[Key] = Directive(Key, Handler, Description, Parameters or {}, Level)

    def Execute(self, Name: str, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        Key = str(Name).strip().upper()
        Item = self.Directives.get(Key)
        if Item is None:
            Result = self.Result(Key, False, "UNKNOWN DIRECTIVE", {"Known": sorted(self.Directives)})
            self.Record(Result)
            self.Failed.Emit(Result)
            self.Publish("Command.Failed", Result)
            return Result
        Result = Item.Handler(Params or {})
        self.Record(Result)
        self.Completed.Emit(Result)
        self.Publish("Command.Completed", Result)
        return Result

    def GetStatus(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.Result("STATUS", True, "COMMAND CORE NOMINAL", {
            "Node": getattr(self, "SystemId", "COMMAND"),
            "Active": self.Active,
            "Uptime": str(int(time() - self.Started)) + "s",
            "Alert": self.Alert.Level.name,
            "History": len(self.History),
        })

    def Version(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.Result("VERSION", True, getVersion(), {})

    def Bios(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        from lcars.system.bios import BIOS
        Node = BIOS()
        Report = Node.RunPost()
        Status = getattr(Report, "Status", "UNKNOWN")
        Payload = Node.ReportPayload(Report) if hasattr(Node, "ReportPayload") else {"Status": Status}
        return self.Result("BIOS", Status == "NOMINAL", Status, Payload)

    def SetAlert(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        Data = Params or {}
        Raw = Data.get("Level", Data.get("level", AlertLevel.GREEN))
        Level = self.ResolveAlertLevel(Raw)
        if Level is None:
            return self.Result("ALERT", False, "UNKNOWN ALERT LEVEL", {"Level": Raw})
        self.Alert.SetLevel(Level)
        return self.Result("ALERT", True, "ALERT " + Level.name, {"Level": Level.name})

    def Shutdown(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.Active = False
        return self.Result("SHUTDOWN", True, "SESSION SHUTDOWN REQUESTED", {})

    def Reboot(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.Active = False
        return self.Result("REBOOT", True, "SESSION REBOOT REQUESTED", {})

    def Help(self, Params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.Result("HELP", True, "DIRECTIVE CATALOG", {"Directives": self.Catalog()})

    def Catalog(self) -> List[Dict[str, Any]]:
        return [self.Directives[Name].Export() for Name in sorted(self.Directives)]

    def ResolveAlertLevel(self, Value: Any) -> Optional[AlertLevel]:
        if isinstance(Value, AlertLevel):
            return Value
        Text = str(Value).strip().upper()
        if Text in AlertLevel.__members__:
            return AlertLevel[Text]
        if Text.isdigit():
            Number = int(Text)
            for Level in AlertLevel:
                if int(Level) == Number:
                    return Level
        return None

    def Result(self, Name: str, Success: bool, Message: str, Data: Dict[str, Any]) -> Dict[str, Any]:
        return {"Command": Name, "Success": Success, "Message": Message, "Data": Data, "Time": time()}

    def Record(self, Result: Dict[str, Any]) -> None:
        self.History.append(Result)


__all__ = ["Command", "Directive"]
