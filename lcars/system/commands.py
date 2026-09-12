# ◤ TITANIUM SYSTEM COMMAND CONTROLLER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/commands.py
# ОПИС: Єдиний вузол обробки системних директив зорельота LCARS.
#       Приймає текстові та структурні директиви, виконує системні дії,
#       керує корабельними протоколами та транслює події в шину ODN.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.core.signal import ODN, Transmission
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version
from lcars.system.alert import AlertLevel, AlertSystem
from lcars.system.bios import BIOS
from lcars.modules.protocol import ProtocolManager

# ═════════════════════════════════════════════════════════════════════
# 1. ДИРЕКТИВА (DIRECTIVE DESCRIPTOR)
# ═════════════════════════════════════════════════════════════════════
@LCARS.DataClass
class Directive(LCARS):
    # Паспорт системної команди для консолі, IDE, BIOS-screen або сервісів
    Name: str = ""
    Handler: any = None
    Description: str = ""
    Parameters: dict[str, str] = LCARS.Field(default_factory=dict)
    Level: str = "SYSTEM"

    def __post_init__(self):
        super().__init__(Id=f"Directive.{self.Name}")

    def Export(self) -> dict[str, any]:
        # Експорт опису директиви у словник
        return {
            "Name": self.Name,
            "Description": self.Description,
            "Parameters": dict(self.Parameters),
            "Level": self.Level,
        }

# ═════════════════════════════════════════════════════════════════════
# 2. КОМАНДНИЙ ВУЗОЛ (COMMAND ENGINE)
# ═════════════════════════════════════════════════════════════════════
class Command(SystemComponent):
    # Головний процесор виконання системних директив ядра LCARS
    SystemVersion = Version.Release
    Completed = Transmission(dict)
    Failed = Transmission(dict)

    def __init__(self, Id: str = "COMMAND"):
        super().__init__(SystemId=Id)
        self.Version = Version.Release
        self.Passport = Version.Passport()
        TimeModule = LCARS.System.Time
        self.Started = TimeModule.time() if hasattr(TimeModule, "time") else 0.0
        self.Active = True
        self.Alert = AlertSystem.GetInstance()
        self.Protocols = ProtocolManager.GetInstance()
        self.History: list[dict[str, any]] = []
        self.Directives: dict[str, Directive] = {}
        self.RegisterDirectives()
        ODN.Transmit("Command.Ready", Data=self.GetStatus())

    def RegisterDirectives(self) -> None:
        # Реєстрація каталогу канонічних системних директив та протоколів
        self.AddDirective("STATUS", self.GetStatus, "Повертає поточний робочий стан командного вузла.")
        self.AddDirective("VERSION", self.GetVersion, "Повертає офіційну версію та системний паспорт LCARS.")
        self.AddDirective("BIOS", self.RunBiosPost, "Запускає повний діагностичний POST-тест BIOS.")
        self.AddDirective("ALERT", self.SetAlert, "Змінює рівень системної тривоги.", {"Level": "GREEN, YELLOW, RED, BLUE, BLACK"})
        self.AddDirective("PROTOCOL", self.HandleProtocol, "Керування корабельними протоколами (LIST, EXECUTE, ABORT, STATUS).", {"Action": "LIST / EXECUTE / ABORT / STATUS", "Name": "Назва протоколу"})
        self.AddDirective("SELF_DESTRUCT", self.SelfDestructDirective, "Протокол самознищення зорельота (Directive 112).", {"Countdown": "Час у секундах", "Officer": "Ім'я офіцера"})
        self.AddDirective("EJECT_CORE", self.EjectCoreDirective, "Аварійне скидання варп-ядра зорельота.")
        self.AddDirective("QUARANTINE", self.QuarantineDirective, "Карантинна ізоляція відсіку або палуби.", {"Deck": "Номер палуби"})
        self.AddDirective("EVACUATE", self.EvacuateDirective, "Запуск процедури загальної евакуації зорельота.")
        self.AddDirective("SILENT_RUNNING", self.SilentRunningDirective, "Перехід у режим максимальної скритності (радіомовчання).")
        self.AddDirective("FIRST_CONTACT", self.FirstContactDirective, "Протокол першого контакту та субпросторова трансляція.")
        self.AddDirective("SHUTDOWN", self.Shutdown, "Переводить систему в безпечний режим завершення.")
        self.AddDirective("REBOOT", self.Reboot, "Запитує системний перезапуск ядра LCARS.")
        self.AddDirective("HELP", self.Help, "Повертає каталог усіх зареєстрованих директив.")

    def AddDirective(self, Name: str, Handler: any, Description: str,
                     Parameters: dict[str, str] | None = None,
                     Level: str = "SYSTEM") -> None:
        # Додавання нової виконуваної директиви до реєстру
        Key = str(Name).strip().upper()
        self.Directives[Key] = Directive(
            Name=Key,
            Handler=Handler,
            Description=Description,
            Parameters=Parameters or {},
            Level=Level
        )

    def Execute(self, Name: str, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Головна точка виконання системних директив
        Params = Params or {}
        Key = str(Name).strip().upper()
        Item = self.Directives.get(Key)
        if Item is None:
            ResultPacket = self.Result(Key, False, "UNKNOWN DIRECTIVE", {"Known": sorted(self.Directives)})
            self.Record(ResultPacket)
            self.Failed.Emit(ResultPacket)
            ODN.Transmit("Command.Failed", Data=ResultPacket)
            return ResultPacket

        ResultPacket = Item.Handler(Params)
        self.Record(ResultPacket)
        self.Completed.Emit(ResultPacket)
        ODN.Transmit("Command.Completed", Data=ResultPacket)
        return ResultPacket

    def GetStatus(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Діагностичний стан процесора команд
        TimeModule = LCARS.System.Time
        CurrentTime = TimeModule.time() if hasattr(TimeModule, "time") else 0.0
        Uptime = int(CurrentTime - self.Started)
        return self.Result("STATUS", True, "COMMAND CORE NOMINAL", {
            "Node": self.SystemId,
            "Active": self.Active,
            "Uptime": str(Uptime) + "s",
            "Alert": getattr(self.Alert.Level, "Name", str(self.Alert.Level)),
            "History": len(self.History),
            "DirectivesCount": len(self.Directives),
            "ProtocolsCount": len(self.Protocols.List()),
        })

    def GetVersion(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Отримання повної системної версії
        return self.Result("VERSION", True, str(Version.Release), {
            "Release": str(Version.Release),
            "Passport": Version.Passport(),
        })

    def RunBiosPost(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Виконання низькорівневої діагностики BIOS
        BiosNode = BIOS()
        Report = BiosNode.RunPost()
        return self.Result("BIOS", Report.Status == "NOMINAL", Report.Status, BiosNode.BuildReportPacket(Report))

    def SetAlert(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Перемикання тактичного рівня тривоги зорельота
        Data = Params or {}
        RawLevel = Data.get("Level", Data.get("level", AlertLevel.GREEN))
        Level = self.ResolveAlertLevel(RawLevel)
        if Level is None:
            return self.Result("ALERT", False, "UNKNOWN ALERT LEVEL", {"Level": RawLevel})
        self.Alert.SetLevel(Level)
        LevelName = getattr(Level, "Name", str(Level))
        return self.Result("ALERT", True, "ALERT " + LevelName, {"Level": LevelName})

    # ─── ОБРОБНИКИ ДИРЕКТИВ ПРОТОКОЛІВ ЗОРЕЛІТА ──────────────────────
    def HandleProtocol(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Універсальне керування протоколами зорельота
        Data = Params or {}
        Action = str(Data.get("Action", "LIST")).upper().strip()
        ProtoName = str(Data.get("Name", "")).strip()

        if Action == "LIST":
            return self.Result("PROTOCOL", True, "PROTOCOL CATALOG", {"Protocols": self.Protocols.GetAllProtocolsStatus()})
        elif Action == "EXECUTE" and ProtoName:
            Res = self.Protocols.Execute(ProtoName, **Data)
            return self.Result("PROTOCOL", Res.get("Success", False), f"PROTOCOL {ProtoName.upper()} ENGAGED", Res)
        elif Action == "ABORT" and ProtoName:
            Ok = self.Protocols.Abort(ProtoName, Reason=Data.get("Reason", "Directive Override"))
            return self.Result("PROTOCOL", Ok, f"PROTOCOL {ProtoName.upper()} ABORTED" if Ok else "ABORT FAILED", {"Protocol": ProtoName})
        elif Action == "STATUS":
            Active = self.Protocols.GetActiveProtocols()
            return self.Result("PROTOCOL", True, "ACTIVE PROTOCOLS", {"Active": Active})

        return self.Result("PROTOCOL", False, "INVALID PROTOCOL ACTION", {"Action": Action, "Available": ["LIST", "EXECUTE", "ABORT", "STATUS"]})

    def SelfDestructDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Ініціація або авторизація самознищення
        Data = Params or {}
        Officer = Data.get("Officer", "Commanding Officer")
        Proto = self.Protocols.Get("selfdestruct")
        if Proto:
            Proto.Authorize(Officer)
            Countdown = Data.get("Countdown", 60)
            Res = Proto.Execute(Countdown=Countdown)
            return self.Result("SELF_DESTRUCT", True, "DIRECTIVE 112 PROCESSED", Res)
        return self.Result("SELF_DESTRUCT", False, "PROTOCOL NOT FOUND", {})

    def EjectCoreDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Аварійне скидання варп-ядра
        Res = self.Protocols.Execute("warpcoreejection")
        return self.Result("EJECT_CORE", Res.get("Success", False), "WARP CORE EJECTION SEQUENCE ENGAGED", Res)

    def QuarantineDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Встановлення карантину
        Data = Params or {}
        Deck = Data.get("Deck", "DECK_12")
        Res = self.Protocols.Execute("biohazardquarantine", Deck=Deck)
        return self.Result("QUARANTINE", Res.get("Success", False), f"BIOHAZARD QUARANTINE ENGAGED: {Deck}", Res)

    def EvacuateDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Евакуація корабля
        Res = self.Protocols.Execute("evacuation")
        return self.Result("EVACUATE", Res.get("Success", False), "SHIP EVACUATION SEQUENCE ENGAGED", Res)

    def SilentRunningDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Безшумний хід
        Res = self.Protocols.Execute("silentrunning")
        return self.Result("SILENT_RUNNING", Res.get("Success", False), "SILENT RUNNING PROTOCOL ACTIVE", Res)

    def FirstContactDirective(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Перший контакт
        Res = self.Protocols.Execute("firstcontact")
        return self.Result("FIRST_CONTACT", Res.get("Success", False), "FIRST CONTACT TRANSMISSION BROADCASTING", Res)

    def Shutdown(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Запит на штатне завершення роботи системи
        self.Active = False
        ODN.Transmit("Command.ShutdownRequested")
        return self.Result("SHUTDOWN", True, "SYSTEM SHUTDOWN REQUESTED", {})

    def Reboot(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Запит на системне перезавантаження ядра
        self.Active = False
        ODN.Transmit("Command.RebootRequested")
        return self.Result("REBOOT", True, "SYSTEM REBOOT REQUESTED", {})

    def Help(self, Params: dict[str, any] | None = None) -> dict[str, any]:
        # Отримання каталогу доступних директив
        return self.Result("HELP", True, "DIRECTIVE CATALOG", {"Directives": self.Catalog()})

    def Catalog(self) -> list[dict[str, any]]:
        # Повертає список описів усіх директив
        return [self.Directives[Name].Export() for Name in sorted(self.Directives)]

    def ResolveAlertLevel(self, Value: any) -> AlertLevel | None:
        # Розпізнавання рівня тривоги за назвою, об'єктом або цілим числом
        if isinstance(Value, AlertLevel):
            return Value
        if isinstance(Value, int):
            for Level in AlertLevel:
                if int(Level) == Value:
                    return Level
        Text = str(Value).strip().upper()
        if hasattr(AlertLevel, "Members") and Text in AlertLevel.Members:
            return AlertLevel.Members[Text]
        if Text.isdigit():
            Number = int(Text)
            for Level in AlertLevel:
                if int(Level) == Number:
                    return Level
        return None

    def Result(self, CommandName: str, Success: bool, Message: str, Data: dict[str, any]) -> dict[str, any]:
        # Формування стандартизованого пакету відповіді виконання
        TimeModule = LCARS.System.Time
        CurrentTime = TimeModule.time() if hasattr(TimeModule, "time") else 0.0
        return {
            "Command": CommandName,
            "Success": Success,
            "Message": Message,
            "Data": Data,
            "Time": CurrentTime,
        }

    def Record(self, ResultPacket: dict[str, any]) -> None:
        # Додавання результату до журналу виконання
        self.History.append(ResultPacket)

# Канонічний експорт
Commands = Command

__all__ = [
    "Command",
    "Commands",
    "Directive",
]
