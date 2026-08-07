from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from lcars.base.type import SystemComponent
from lcars.core.signal import Signal

# Система транспортування даних між підсистемами
class TransporterSystem(SystemComponent):
    # Система транспортування даних між підсистемами

    # Сигнал успішної передачі: ціль
    TransportComplete = Signal(str)
    # Сигнал помилки: повідомлення
    TransportFailed = Signal(str)

    def __init__(self):
        super().__init__()
        # Буфер транспортування
        self.PatternBuffer = {
            "Status": "IDLE",
            "Data": None,
            "Target": None,
            "Stability": 100.0,
        }
        # Статус біо-фільтра
        self.BioFilterStatus = "ACTIVE"
        # Загальний статус системи
        self.Status = "ONLINE"

    # Завантаження даних у буфер з перевіркою біо-фільтра
    def LoadPattern(self, Data: str, Source: str = "LOCAL") -> bool:
        if self.PatternBuffer["Status"] != "IDLE":
            self.TransportFailed.Emit("Buffer busy")
            return False

        # Перевірка біо-фільтра
        if not self.ScanBioFilter(Data):
            self.PatternBuffer["Status"] = "ABORTED"
            self.Status = "ABORTED"
            return False

        self.PatternBuffer["Data"] = Data
        self.PatternBuffer["Status"] = "STAGED"
        return True

    # Початок процесу передачі даних
    def Energize(self, Target: str = "BUFFER") -> bool:
        if self.PatternBuffer["Status"] != "STAGED":
            return False

        self.PatternBuffer["Status"] = "ENERGIZING"
        self.PatternBuffer["Target"] = Target
        self.Status = "ENERGIZING"
        return True

    # Завершення транспортування (дематеріалізація)
    def CompleteTransport(self) -> bool:
        if self.PatternBuffer["Status"] != "ENERGIZING":
            return False

        self.PatternBuffer["Status"] = "BEAMING"
        # Імітація передачі
        self.UnloadPattern()
        return True

    # Вивантаження даних з буфера та сповіщення отримувача
    def UnloadPattern(self) -> bool:
        if not self.PatternBuffer["Data"]:
            self.TransportFailed.Emit("Null pattern")
            return False

        Target = self.PatternBuffer.get("Target", "SYSTEM")

        # Скидання буфера
        self.PatternBuffer["Status"] = "IDLE"
        self.PatternBuffer["Data"] = None
        self.Status = "ONLINE"

        self.TransportComplete.Emit(Target)
        return True

    # Повний цикл транспортування даних
    def BeamData(self, Data: str, Target: str) -> bool:
        if not self.LoadPattern(Data, "INTERNAL"):
            return False
        if not self.Energize(Target):
            return False
        return self.CompleteTransport()

    # Отримання поточного статусу транспортера
    def GetStatus(self) -> dict[str, Any]:
        return {
            "Status": self.Status,
            "BufferStatus": self.PatternBuffer["Status"],
            "BioFilter": self.BioFilterStatus,
            "Stability": self.PatternBuffer["Stability"],
        }

    # Перевірка даних на шкідливі паттерни через біо-фільтр
    def ScanBioFilter(self, Data: str | None = None) -> bool:
        MalwareSigs = ["eval(", "exec(", "os.system(", "subprocess.Popen(", "__import__"]
        TestData = Data or self.PatternBuffer.get("Data", "")

        for Sig in MalwareSigs:
            if Sig in TestData:
                self.BioFilterStatus = "INFECTED"
                return False

        self.BioFilterStatus = "CLEAN"
        return True

    # Екстрене скидання транспортування
    def AbortTransport(self) -> None:
        self.PatternBuffer["Status"] = "ABORTED"
        self.Status = "ABORTED"
        self.TransportFailed.Emit("Transport Aborted")

# Статуси транспортування для зовнішнього API
class TransportStatus(Enum):
    IDLE = "idle"
    ENERGIZING = "energizing"
    MATTER_STREAM = "matterStream"
    REMATERIALIZING = "rematerializing"
    COMPLETE = "complete"
    ERROR = "error"

# Запис транспортування для логування
@dataclass
class TransportLog:
    id: str
    origin: str
    destination: str
    status: TransportStatus
    timestamp: float = field(default_factory=time.time)
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def toDict(self) -> Dict:
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "status": self.status.value,
            "timestamp": self.timestamp,
            "payload": self.payload
        }

# Зовнішній сервіс транспортування з логуванням та слухачами
class TransporterService:
    def __init__(self):
        self.logs: List[TransportLog] = []
        self.patterns: Dict[str, Any] = {}
        self.buffers: Dict[str, Any] = {}
        self.listeners: List[Callable] = []
        self.activeTransports: Dict[str, TransportLog] = {}
        
    # Почати транспортування з реєстрацією логу
    def energize(self, transportId: str, origin: str, destination: str, payload: Dict) -> bool:
        log = TransportLog(
            id=transportId,
            origin=origin,
            destination=destination,
            status=TransportStatus.ENERGIZING,
            payload=payload
        )
        self.activeTransports[transportId] = log
        self.notify("transportStarted", log)
        return True
        
    # Завершити транспортування та перемістити до архіву
    def rematerialize(self, transportId: str) -> bool:
        if transportId not in self.activeTransports:
            return False
        log = self.activeTransports[transportId]
        log.status = TransportStatus.COMPLETE
        self.logs.append(log)
        del self.activeTransports[transportId]
        self.notify("transportComplete", log)
        return True
        
    # Буферизація матерії для транспортування
    def bufferMatter(self, transportId: str, data: Any) -> bool:
        if transportId not in self.buffers:
            self.buffers[transportId] = []
        self.buffers[transportId].append(data)
        return True
        
    # Отримання списку активних транспортувань
    def getActiveTransports(self) -> List[TransportLog]:
        return list(self.activeTransports.values())
        
    # Отримання історії транспортувань
    def getLogs(self) -> List[TransportLog]:
        return self.logs.copy()
        
    # Додати слухача подій транспортування
    def addListener(self, callback: Callable):
        self.listeners.append(callback)
        
    # Сповістити всіх слухачів про подію
    def notify(self, event: str, log: TransportLog):
        for listener in self.listeners:
            if callable(listener):
                listener(event, log)
                
    # Отримання статистики транспортувань
    def getStats(self) -> Dict[str, Any]:
        return {
            "total": len(self.logs),
            "active": len(self.activeTransports),
            "buffered": len(self.buffers)
        }

transporterService: Optional[TransporterService] = None

# Глобальний екземпляр сервісу транспортування
def getTransporterService() -> TransporterService:
    global transporterService
    if transporterService is None:
        transporterService = TransporterService()
    return transporterService
