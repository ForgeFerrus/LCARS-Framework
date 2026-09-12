# ◤ LCARS COMMUNICATION SUBSYSTEM & SUBSPACE LINK 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/comm.py
# ОПИС: Головна суверенна підсистема зв'язку зорельота та підпросторовий міст (SubspaceLink).
#       Керує голосовим комлінком (Comlink), субпросторовими частотами (SubspaceFrequency),
#       станціями зорельота (ShipStation), реєстрацією PADD-пристроїв екіпажу
#       (зокрема мобільного терміналу Motorola "LCARS 25th"), спільним буфером обміну,
#       субпросторовою передачею файлів та прямим віддаленим керуванням інженерією.
# ЧІП: 06-0002 (Communication Subsystem // ODN-06)
# БАЗА: lcars/data/06/06-0002-comm.db
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS, SystemComponent
from lcars.core.system import Subsystem
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission

# Статус підключення мобільного пристрою
class DeviceStatus(LCARS):
    Online = "Online"
    Offline = "Offline"
    Standby = "Standby"

# Стан голосового комлінка
class ComlinkState(LCARS):
    Idle = "Idle"
    Transmitting = "Transmitting"
    Receiving = "Receiving"
    Encrypted = "Encrypted"

# Субпросторові частоти зв'язку Зоряного Флоту
class SubspaceFrequency(LCARS):
    Emergency = 1.0        # Загальнофлотська аварійна частота (Канал 1)
    Intercom = 2.4         # Внутрішньокорабельний інтерком (Канал 2)
    Engineering = 3.6      # Інженерна телеметрія та варп-контроль (Канал 3)
    Tactical = 4.8         # Тактична мережа та щити (Канал 4)
    PersonalPADD = 5.5     # Персональні термінали та мобільні PADD (Канал 5)

# Канонічні станції зорельота для інтеркому
class ShipStation(LCARS):
    Bridge = "Bridge"
    MainEngineering = "MainEngineering"
    Sickbay = "Sickbay"
    Security = "Security"
    Astrometrics = "Astrometrics"
    CaptainQuarters = "CaptainQuarters"
    MobilePADD = "MobilePADD"

# Підключений пристрій екосистеми SubspaceLink (наприклад, Motorola LCARS 25th)
class SubspaceDevice(LCARS):
    def __init__(self, DeviceId: str, Name: str, IpAddress: str = "127.0.0.1", DeviceType: str = "PADD"):
        super().__init__()
        self.DeviceId = DeviceId
        self.Name = Name
        self.IpAddress = IpAddress
        self.DeviceType = DeviceType
        self.Status = DeviceStatus.Online
        self.ConnectedAt = LCARS.System.Time.time()
        self.LastSeen = self.ConnectedAt
        self.BatteryPercent = 100.0
        self.SignalStrength = 100.0
        self.AssignedFrequency = SubspaceFrequency.PersonalPADD

    def Ping(self) -> None:
        self.LastSeen = LCARS.System.Time.time()
        self.Status = DeviceStatus.Online

    def ToDict(self) -> dict:
        return {
            "DeviceId": self.DeviceId,
            "Name": self.Name,
            "IpAddress": self.IpAddress,
            "DeviceType": self.DeviceType,
            "Status": self.Status,
            "ConnectedAt": round(self.ConnectedAt, 2),
            "LastSeen": round(self.LastSeen, 2),
            "BatteryPercent": self.BatteryPercent,
            "SignalStrength": self.SignalStrength,
            "AssignedFrequency": self.AssignedFrequency,
        }

# Голосовий комлінк та інтерком (Starfleet Comlink Channel)
class ComlinkChannel(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.State = ComlinkState.Idle
        self.ActiveCaller = ""
        self.ActiveCallee = ""
        self.SessionStart = 0.0
        self.DirectiveHistory = []
        self.CurrentFrequency = SubspaceFrequency.Intercom

    @classmethod
    def GetInstance(cls) -> ComlinkChannel:
        if cls.Instance is None:
            cls.Instance = ComlinkChannel()
        return cls.Instance

    # Початок голосової передачі (Push-to-Talk)
    def OpenChannel(self, Caller: str = "LCARS 25th", Callee: str = ShipStation.Bridge) -> dict:
        self.State = ComlinkState.Transmitting
        self.ActiveCaller = Caller
        self.ActiveCallee = Callee
        self.SessionStart = LCARS.System.Time.time()
        ODN.Transmit("ODN.06.ComlinkOpened", Caller=Caller, Callee=Callee, Frequency=self.CurrentFrequency)
        return {
            "Status": "ChannelOpened",
            "Caller": Caller,
            "Callee": Callee,
            "Frequency": self.CurrentFrequency,
            "Timestamp": self.SessionStart,
        }

    # Закриття голосового каналу
    def CloseChannel(self) -> dict:
        Now = LCARS.System.Time.time()
        Duration = Now - self.SessionStart if self.SessionStart > 0 else 0.0
        Result = {
            "Status": "ChannelClosed",
            "Caller": self.ActiveCaller,
            "DurationSeconds": round(Duration, 2),
        }
        self.State = ComlinkState.Idle
        self.ActiveCaller = ""
        self.ActiveCallee = ""
        self.SessionStart = 0.0
        ODN.Transmit("ODN.06.ComlinkClosed", Duration=Duration)
        return Result

    # Передача повноцінного голосового повідомлення по ІЗО-мережі зорельота
    def TransmitVoiceMessage(self, SenderId: str, RecipientStation: str = "Bridge", AudioBytes: bytes = b"", DirectiveText: str = "") -> dict:
        SessionId = f"VOX-{int(LCARS.System.Time.time() * 1000)}"
        DurationSec = len(AudioBytes) / 32000.0 if AudioBytes else 1.0
        
        # 1. Фіксація в ізолінійній базі даних чіпа 06-0002
        DbPath = "lcars/data/06/06-0002-comm.db"
        if LCARS.System.Path(DbPath).exists():
            import sqlite3
            Conn = sqlite3.connect(DbPath)
            Cur = Conn.cursor()
            Cur.execute(
                "INSERT INTO ComlinkLogs (SessionId, Sender, Recipient, DurationSec, DirectiveText, Timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (SessionId, SenderId, RecipientStation, DurationSec, DirectiveText, LCARS.System.Time.time())
            )
            Conn.commit()
            Conn.close()

        # 2. Оповіщення звукової підсистеми корабля
        from lcars.core.system import MasterSystem
        Sys = MasterSystem.GetInstance()
        Sound = Sys.Modules.get("sound")
        if Sound and hasattr(Sound, "Play"):
            Sound.Play("ComlinkChime")

        # 3. Виконання директиви через Бортовий Комп'ютер
        CompResponse = ""
        if DirectiveText:
            from lcars.core.computer import BoardComputer
            Comp = BoardComputer.GetInstance()
            ExecRes = Comp.ExecuteDirective(DirectiveText)
            CompResponse = ExecRes.get("Message", "Directive received.")

        # 4. Емісія імпульсу по шині ODN-06
        ODN.Transmit("ODN.06.VoiceTransmission", SessionId=SessionId, Sender=SenderId, Recipient=RecipientStation, Directive=DirectiveText)

        return {
            "SessionId": SessionId,
            "Status": "Transmitted",
            "Sender": SenderId,
            "Recipient": RecipientStation,
            "Response": CompResponse,
            "DurationSeconds": round(DurationSec, 2),
        }

    # Обробка голосової команди через комп'ютер корабля
    def ProcessDirective(self, VoiceText: str, SenderId: str = "LCARS 25th") -> dict:
        CleanText = str(VoiceText or "").strip()
        from lcars.core.computer import BoardComputer
        Comp = BoardComputer.GetInstance()
        ExecResult = Comp.ExecuteDirective(CleanText) if CleanText else {"Message": "Directive received."}
        ComputerResponse = ExecResult.get("Message", "Directive processed.")

        LogEntry = {
            "SenderId": SenderId,
            "DirectiveText": CleanText,
            "Response": ComputerResponse,
            "Timestamp": LCARS.System.Time.time(),
        }
        self.DirectiveHistory.append(LogEntry)
        ODN.Transmit("ODN.06.VoiceDirectiveExecuted", Directive=CleanText)
        return LogEntry

# Субпросторовий трансивер зв'язку (SubspaceTransceiver)
class SubspaceTransceiver(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.ActiveFrequencies = [
            SubspaceFrequency.Emergency,
            SubspaceFrequency.Intercom,
            SubspaceFrequency.Engineering,
            SubspaceFrequency.Tactical,
            SubspaceFrequency.PersonalPADD,
        ]
        self.HailingStatus = "STANDBY"

    @classmethod
    def GetInstance(cls) -> SubspaceTransceiver:
        if cls.Instance is None:
            cls.Instance = SubspaceTransceiver()
        return cls.Instance

    # Виклик станції зорельота
    def HailStation(self, TargetStation: str) -> dict:
        self.HailingStatus = f"Hailing{TargetStation}"
        ODN.Transmit("ODN.06.StationHailed", Target=TargetStation)
        return {
            "Status": "HailingInitiated",
            "TargetStation": TargetStation,
            "Frequency": SubspaceFrequency.Intercom,
        }

    # Загальнокорабельна трансляція
    def BroadcastShipwide(self, MessageText: str, Priority: str = "NORMAL") -> dict:
        ODN.Transmit("ODN.06.ShipwideBroadcast", Message=MessageText, Priority=Priority)
        return {
            "Status": "BroadcastSent",
            "Message": MessageText,
            "Priority": Priority,
            "Timestamp": LCARS.System.Time.time(),
        }

# Суверенний міст SubspaceLink (заміна Motorola Smart Connect)
class SubspaceLink(SystemComponent):
    Instance = None

    def __init__(self):
        super().__init__()
        self.Devices = {}
        self.SharedClipboard = ""
        self.ClipboardUpdatedBy = ""
        self.ClipboardTimestamp = 0.0
        self.ReceivedFiles = []
        self.RegisterDefaultDevice()

    @classmethod
    def GetInstance(cls) -> SubspaceLink:
        if cls.Instance is None:
            cls.Instance = SubspaceLink()
        return cls.Instance

    # Реєстрація дефолтного пристрою користувача (Motorola LCARS 25th)
    def RegisterDefaultDevice(self) -> None:
        Dev = SubspaceDevice(
            DeviceId="DEV-LCARS-25TH",
            Name="LCARS 25th (Motorola)",
            IpAddress="127.0.0.1",
            DeviceType="MobilePADD"
        )
        self.Devices[Dev.DeviceId] = Dev

    # Реєстрація або оновлення підключеного пристрою
    def RegisterDevice(self, DeviceId: str, Name: str, IpAddress: str, DeviceType: str = "PADD") -> SubspaceDevice:
        Dev = SubspaceDevice(DeviceId=DeviceId, Name=Name, IpAddress=IpAddress, DeviceType=DeviceType)
        self.Devices[DeviceId] = Dev
        ODN.Transmit("ODN.06.DeviceConnected", DeviceId=DeviceId, Name=Name)
        return Dev

    def GetDevice(self, DeviceId: str) -> SubspaceDevice | None:
        return self.Devices.get(DeviceId)

    def GetAllDevices(self) -> list[dict]:
        return [Dev.ToDict() for Dev in self.Devices.values()]

    # Синхронізація спільного буфера обміну
    def SetClipboard(self, TextContent: str, SourceDeviceId: str = "Host") -> str:
        self.SharedClipboard = str(TextContent or "")
        self.ClipboardUpdatedBy = SourceDeviceId
        self.ClipboardTimestamp = LCARS.System.Time.time()
        ODN.Transmit("ODN.06.ClipboardSynced", Source=SourceDeviceId, Length=len(self.SharedClipboard))
        return self.SharedClipboard

    def GetClipboard(self) -> dict:
        return {
            "Content": self.SharedClipboard,
            "UpdatedBy": self.ClipboardUpdatedBy,
            "Timestamp": round(self.ClipboardTimestamp, 2),
        }

    # Прийом та збереження переданого файлу
    def ReceiveFile(self, FileName: str, PayloadBytes: bytes, SenderId: str = "LCARS 25th") -> dict:
        CleanName = LCARS.System.Path(FileName).name
        TargetDir = LCARS.System.Path("lcars/data/transfers")
        TargetDir.mkdir(parents=True, exist_ok=True)
        TargetFile = TargetDir / CleanName
        TargetFile.write_bytes(PayloadBytes)

        Record = {
            "FileName": CleanName,
            "SizeBytes": len(PayloadBytes),
            "SavedPath": str(TargetFile).replace("\\", "/"),
            "SenderId": SenderId,
            "Timestamp": LCARS.System.Time.time(),
        }
        self.ReceivedFiles.append(Record)
        ODN.Transmit("ODN.06.FileReceived", FileName=CleanName, Size=len(PayloadBytes))
        return Record

    # Повне віддалене виконання команд через Системний Термінал та Бортовий Комп'ютер
    def ExecuteCommand(self, Action: str, Parameters: dict | None = None) -> dict:
        Params = Parameters or {}
        CleanAction = str(Action or "").strip()
        ActUpper = CleanAction.upper()

        # 1. Швидкі інженерні гарячі команди
        from lcars.engineering.controller import Engineering
        Eng = Engineering.GetInstance()

        if ActUpper == "ALERT":
            Level = str(Params.get("Level", "GREEN")).upper()
            Reactions = Eng.ApplyAlertLevel(Level)
            return {"Status": "Success", "Action": "AlertApplied", "Level": Level, "Reactions": Reactions}

        elif ActUpper == "WARP":
            Factor = float(Params.get("Factor", 0.0))
            if hasattr(Eng.WarpDrive, "SetWarpFactor"):
                CurrentWarp = Eng.WarpDrive.SetWarpFactor(Factor)
                return {"Status": "Success", "Action": "WarpEngaged", "Factor": CurrentWarp}

        elif ActUpper == "SHIELDS":
            Percent = float(Params.get("Percent", 100.0))
            if hasattr(Eng.Deflector, "SetAllQuadrants"):
                Eng.Deflector.SetAllQuadrants(Percent)
                return {"Status": "Success", "Action": "ShieldsModulated", "Percent": Percent}

        elif ActUpper == "MODE":
            ModeStr = str(Params.get("Mode", "CRUISE")).upper()
            Profile = Eng.ApplySystemMode(ModeStr)
            return {"Status": "Success", "Action": "ModeApplied", "Mode": ModeStr, "Profile": Profile}

        # 2. Універсальне виконання БУДЬ-ЯКОЇ системної команди через LCARSConsole
        from lcars.service.console import LCARSConsole
        from lcars.core.computer import BoardComputer
        Comp = BoardComputer.GetInstance()
        Console = LCARSConsole(BoardComputer=Comp)

        OutputLines = []
        Console.Execute(CleanAction, lambda Line: OutputLines.append(str(Line)))

        if OutputLines:
            ODN.Transmit("ODN.06.RemoteConsoleExecuted", Command=CleanAction, LinesCount=len(OutputLines))
            return {
                "Status": "Success",
                "Action": CleanAction,
                "Source": "LCARSConsole",
                "Output": OutputLines,
                "Summary": "\n".join(OutputLines),
            }

        # 3. Делегування природної директиви безпосередньо Бортовому Комп'ютеру
        ExecResult = Comp.ExecuteDirective(CleanAction)
        ODN.Transmit("ODN.06.RemoteDirectiveExecuted", Directive=CleanAction)
        return {
            "Status": "Success",
            "Action": CleanAction,
            "Source": "BoardComputer",
            "Result": ExecResult,
            "Summary": ExecResult.get("Message", "Directive Executed"),
        }
# Головна суверенна підсистема зв'язку зорельота
class CommSubsystem(Subsystem):
    Instance = None

    def __init__(self):
        super().__init__(SubsystemId="Subsystem.Communication")
        self.Name = "Communication"
        self.Category = "Communication"
        self.Version = VersionInfo.GetVersion()
        self.ChipId = "06-0002"
        self.DatabasePath = "lcars/data/06/06-0002-comm.db"
        self.Comlink = ComlinkChannel.GetInstance()
        self.Subspace = SubspaceLink.GetInstance()
        self.Transceiver = SubspaceTransceiver.GetInstance()
        self.SmartConnect = self.Subspace  # Зворотна сумісність

    @classmethod
    def GetInstance(cls) -> CommSubsystem:
        if cls.Instance is None:
            cls.Instance = CommSubsystem()
        return cls.Instance

    def GetStatus(self) -> dict:
        return {
            "Subsystem": self.Name,
            "ChipId": self.ChipId,
            "Version": self.Version,
            "Database": self.DatabasePath,
            "ComlinkState": self.Comlink.State,
            "ConnectedDevices": self.Subspace.GetAllDevices(),
            "TotalDirectives": len(self.Comlink.DirectiveHistory),
            "ReceivedFilesCount": len(self.Subspace.ReceivedFiles),
            "HailingStatus": self.Transceiver.HailingStatus,
        }

# Канонічні точки входу для маніфесту 06-0002.yaml та комп'ютера
InitializeCommSubsystem = CommSubsystem.GetInstance
InitializeContacts = CommSubsystem.GetInstance
InitializeMessages = CommSubsystem.GetInstance
InitializeCalls = CommSubsystem.GetInstance
COMMUNICATION = CommSubsystem.GetInstance()