from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from lcars.base.type import SystemComponent
from lcars.core.signal import Signal

class TransportStatus(Enum):
    IDLE = "idle"
    ENERGIZING = "energizing"
    MATTER_STREAM = "matterStream"
    REMATERIALIZING = "rematerializing"
    COMPLETE = "complete"
    ERROR = "error"
    
# Система транспортування даних між підсистемами
class SystemTransporter(SystemComponent):
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

    def LoadPattern(self, Data: str, Source: str = "LOCAL") -> bool:
        # Завантаження даних у буфер
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

    def Energize(self, Target: str = "BUFFER") -> bool:
        # Початок процесу передачі
        if self.PatternBuffer["Status"] != "STAGED":
            return False

        self.PatternBuffer["Status"] = "ENERGIZING"
        self.PatternBuffer["Target"] = Target
        self.Status = "ENERGIZING"
        return True

    def CompleteTransport(self) -> bool:
        # Завершення транспортування (дематеріалізація)
        if self.PatternBuffer["Status"] != "ENERGIZING":
            return False

        self.PatternBuffer["Status"] = "BEAMING"
        # Імітація передачі
        self.UnloadPattern()
        return True

    def UnloadPattern(self) -> bool:
        # Вивантаження даних з буфера
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

    def BeamData(self, Data: str, Target: str) -> bool:
        # Повний цикл транспортування даних
        if not self.LoadPattern(Data, "INTERNAL"):
            return False
        if not self.Energize(Target):
            return False
        return self.CompleteTransport()

    def GetStatus(self) -> dict[str, Any]:
        # Отримання статусу транспортера
        return {
            "Status": self.Status,
            "BufferStatus": self.PatternBuffer["Status"],
            "BioFilter": self.BioFilterStatus,
            "Stability": self.PatternBuffer["Stability"],
        }

    def ScanBioFilter(self, Data: str | None = None) -> bool:
        # Перевірка на шкідливі паттерни
        MalwareSigs = ["eval(", "exec(", "os.system(", "subprocess.Popen(", "__import__"]
        TestData = Data or self.PatternBuffer.get("Data", "")

        for Sig in MalwareSigs:
            if Sig in TestData:
                self.BioFilterStatus = "INFECTED"
                return False

        self.BioFilterStatus = "CLEAN"
        return True

    def AbortTransport(self) -> None:
        # Екстрене скидання транспортування
        self.PatternBuffer["Status"] = "ABORTED"
        self.Status = "ABORTED"
        self.TransportFailed.Emit("Transport Aborted")

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

class TransporterSubsystem:
    def __init__(self):
        self.logs: List[TransportLog] = []
        self.patterns: Dict[str, Any] = {}
        self.buffers: Dict[str, Any] = {}
        self.listeners: List[Callable] = []
        self.activeTransports: Dict[str, TransportLog] = {}
        
    def energize(self, transportId: str, origin: str, destination: str, payload: Dict) -> bool:
        # Почати транспортування
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
        
    def rematerialize(self, transportId: str) -> bool:
        # Завершити транспортування
        if transportId not in self.activeTransports:
            return False
        log = self.activeTransports[transportId]
        log.status = TransportStatus.COMPLETE
        self.logs.append(log)
        del self.activeTransports[transportId]
        self.notify("transportComplete", log)
        return True
        
    def bufferMatter(self, transportId: str, data: Any) -> bool:
        # Буферизація матерії
        if transportId not in self.buffers:
            self.buffers[transportId] = []
        self.buffers[transportId].append(data)
        return True
        
    def getActiveTransports(self) -> List[TransportLog]:
        # Активні транспортування
        return list(self.activeTransports.values())
        
    def getLogs(self) -> List[TransportLog]:
        # Історія транспортувань
        return self.logs.copy()
        
    def addListener(self, callback: Callable):
        # Додати слухача
        self.listeners.append(callback)
        
    def notify(self, event: str, log: TransportLog):
        # Сповістити слухачів
        for listener in self.listeners:
            if callable(listener):
                listener(event, log)
                
    def getStats(self) -> Dict[str, Any]:
        # Статистика
        return {
            "total": len(self.logs),
            "active": len(self.activeTransports),
            "buffered": len(self.buffers)
        }

transporterSubsystem: Optional[TransporterSubsystem] = None

def getTransporterSubsystem() -> TransporterSubsystem:
    # Глобальний екземпляр
    global transporterSubsystem
    if transporterSubsystem is None:
        transporterSubsystem = TransporterSubsystem()
    return transporterSubsystem

TransporterSubsystem = TransporterSubsystem
