from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from lcars.base.type import SystemComponent
from lcars.base.version import getVersion
from lcars.system.alert import AlertLevel

# Пріоритет інженерної задачі.
class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

# Статус виконання інженерної задачі.
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Одна інженерна задача без зайвих обгорток.
@dataclass
class EngineeringTask:
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    assignedTo: Optional[str] = None
    createdAt: float = field(default_factory=time.time)
    startedAt: Optional[float] = None
    completedAt: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def toDict(self) -> Dict[str, Any]:
        # Плоский словник для журналів, UI і тестів.
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name if isinstance(self.priority, Enum) else self.priority,
            "status": self.status.value if isinstance(self.status, Enum) else self.status,
            "assignedTo": self.assignedTo,
            "createdAt": self.createdAt,
            "startedAt": self.startedAt,
            "completedAt": self.completedAt,
            "metadata": self.metadata,
            "dependencies": self.dependencies,
        }

# Керує інженерними задачами та підключеними вузлами.
class EngineeringController(SystemComponent):
    def __init__(
        self,
        eventBus: Any = None,
        alert: Any = None,
        deflector: Any | None = None,
        drive: Any | None = None,
        collector: Any | None = None,
    ):
        super().__init__()
        self.tasks: Dict[str, EngineeringTask] = {}
        self.agents: Dict[str, Any] = {}
        self.history: List[Dict[str, Any]] = []
        self.listeners: List[Callable[[str, Any], None]] = []
        self.taskCounter = 0
        self.systems: Dict[str, Any] = {}
        self.coordinators: Dict[str, Callable] = {}
        self.status = "idle"
        self.deflector = deflector
        self.drive = drive
        self.collector = collector
        self.currentLevel = AlertLevel.GREEN
        self.eventBus = eventBus
        self.alert = alert

        # Якщо ядро дало канал подій, підписуємося на тривогу.
        if self.eventBus is not None and hasattr(self.eventBus, "On"):
            self.eventBus.On("SYSTEM ALERT", self.OnAlertEvent)

    def ApplyLevel(self, level: AlertLevel) -> None:
        # Переносить рівень тривоги на підключені інженерні вузли.
        self.currentLevel = level

        if self.deflector is not None and hasattr(self.deflector, "SyncPolicy"):
            if level == AlertLevel.RED:
                self.deflector.SyncPolicy("RED")
            elif level == AlertLevel.YELLOW:
                self.deflector.SyncPolicy("YELLOW")
            elif level == AlertLevel.GREEN:
                self.deflector.SyncPolicy("GREEN")

        if self.drive is not None and hasattr(self.drive, "setMode"):
            if level == AlertLevel.RED:
                self.drive.setMode("impulse")
            elif level == AlertLevel.YELLOW:
                self.drive.setMode("standby")
            elif level == AlertLevel.GREEN:
                self.drive.setMode("warp")

    def OnAlertEvent(self, event: str, data: Any) -> None:
        # Реакція на подію тривоги.
        if event == "SYSTEM ALERT" and isinstance(data, AlertLevel):
            self.ApplyLevel(data)

    def RegisterSystem(self, systemId: str, system: Any) -> bool:
        # Реєструє інженерну підсистему.
        self.systems[systemId] = system
        return True

    def RegisterCoordinator(self, coordId: str, handler: Callable) -> bool:
        # Реєструє координатор для задач.
        self.coordinators[coordId] = handler
        return True

    def CreateTask(self, taskId: str, title: str, description: str, priority: TaskPriority, assignedTo: str = "") -> bool:
        # Створює нову інженерну задачу.
        if taskId in self.tasks:
            return False

        self.taskCounter += 1
        task = EngineeringTask(
            id=taskId,
            title=title,
            description=description,
            priority=priority,
            assignedTo=assignedTo if assignedTo else None,
        )
        self.tasks[taskId] = task
        self.notify("task.created", task.toDict())
        return True

    def createTask(self, taskId: str, title: str, description: str, priority: TaskPriority, assignedTo: str = "") -> EngineeringTask | None:
        # Сумісний нижній виклик, який повертає створену задачу.
        if not self.CreateTask(taskId, title, description, priority, assignedTo):
            return None
        return self.tasks.get(taskId)

    def ExecuteTask(self, taskId: str) -> bool:
        # Запускає задачу, якщо всі залежності вже закриті.
        if taskId not in self.tasks:
            return False

        task = self.tasks[taskId]
        if task.status != TaskStatus.PENDING:
            return False

        for depId in task.dependencies:
            if depId not in self.tasks:
                return False
            if self.tasks[depId].status != TaskStatus.COMPLETED:
                return False

        task.status = TaskStatus.IN_PROGRESS
        task.startedAt = time.time()
        self.notify("task.started", task.toDict())
        return True

    def completeTask(self, taskId: str, success: bool = True) -> bool:
        # Закриває задачу як успішну або невдалу.
        if taskId not in self.tasks:
            return False

        task = self.tasks[taskId]
        if task.status != TaskStatus.IN_PROGRESS:
            return False

        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
        task.completedAt = time.time()
        self.history.append({"action": "complete", "taskId": taskId, "time": time.time()})
        self.notify("task.completed", task.toDict())
        return True

    def assignTask(self, taskId: str, agentId: str) -> bool:
        # Призначає задачу агенту.
        if taskId not in self.tasks or agentId not in self.agents:
            return False

        self.tasks[taskId].assignedTo = agentId
        self.notify("task.assigned", self.tasks[taskId].toDict())
        return True

    def registerAgent(self, agentId: str, agent: Any) -> bool:
        # Реєструє інженерного агента.
        self.agents[agentId] = agent
        return True

    def addListener(self, callback: Callable[[str, Any], None]) -> bool:
        # Додає слухача подій.
        self.listeners.append(callback)
        return True

    def notify(self, event: str, data: Any) -> None:
        # Розсилає подію всім слухачам.
        for listener in self.listeners:
            if callable(listener):
                listener(event, data)

    def getStats(self) -> Dict[str, Any]:
        # Повертає коротку статистику по задачах.
        return {
            "total": len(self.tasks),
            "pending": sum(1 for task in self.tasks.values() if task.status == TaskStatus.PENDING),
            "inProgress": sum(1 for task in self.tasks.values() if task.status == TaskStatus.IN_PROGRESS),
            "completed": sum(1 for task in self.tasks.values() if task.status == TaskStatus.COMPLETED),
            "failed": sum(1 for task in self.tasks.values() if task.status == TaskStatus.FAILED),
        }

    def coordinateTask(self, taskId: str, systemIds: List[str]) -> bool:
        # Розкладає координацію на підзадачі для кількох систем.
        if not self.CreateTask(taskId, f"Coord: {taskId}", "", TaskPriority.HIGH):
            return False

        deps: list[str] = []
        for sysId in systemIds:
            if sysId not in self.systems:
                return False
            subTask = f"{taskId}.{sysId}"
            self.CreateTask(subTask, f"Sub: {sysId}", "", TaskPriority.HIGH)
            deps.append(subTask)

        self.tasks[taskId].dependencies = deps
        return True

    def executeCoordination(self, taskId: str) -> bool:
        # Запускає всі координовані підзадачі й головну задачу.
        if taskId not in self.tasks:
            return False

        task = self.tasks[taskId]
        for depId in task.dependencies:
            if depId in self.coordinators:
                handler = self.coordinators[depId]
                if callable(handler):
                    handler(self.tasks[depId])

        return self.ExecuteTask(taskId)

    def getMetrics(self) -> Dict[str, Any]:
        # Берe метрики з колектора, якщо він підключений зовні.
        if self.collector is not None and hasattr(self.collector, "PollAll"):
            return self.collector.PollAll()
        return {}

    def getSystemStatus(self) -> Dict[str, Any]:
        # Дає зведений статус контролера та підключених вузлів.
        deflectorStatus = self.deflector.GetStatus() if self.deflector is not None and hasattr(self.deflector, "GetStatus") else {}
        driveStatus = self.drive.GetStatus() if self.drive is not None and hasattr(self.drive, "GetStatus") else {}
        return {
            "status": self.status,
            "systems": list(self.systems.keys()),
            "coordinators": list(self.coordinators.keys()),
            "tasks": self.getStats(),
            "deflector": deflectorStatus,
            "drive": driveStatus,
            "metrics": self.getMetrics(),
            "alertLevel": self.currentLevel.value if hasattr(self.currentLevel, "value") else str(self.currentLevel),
        }

    def emergencyStop(self) -> bool:
        # Аварійна зупинка контролера.
        self.status = "stopped"
        return True

    # Сумісний нижній виклик для старих місць, де очікують готовий об'єкт задачі.
    executeTask = ExecuteTask
_enginController: Optional[EngineeringController] = None

# Повертає один спільний інженерний контролер для сумісних викликів.
def getEngineeringController() -> EngineeringController:
    global _enginController
    if _enginController is None:
        _enginController = EngineeringController()
    return _enginController

# Керує вузлами ізолінійного банку без зайвих обгорток.
class ISOController:
    def __init__(self, Bank: Any):
        self.Bank = Bank
        self.ActiveChips: Dict[str, Any] = {}
        self.DisabledChips: Dict[str, Any] = {}
        self.LastError: Optional[str] = None
    # Активує чіп і переносить його в активний список.
    def ActivateChip(self, ChipId: str) -> bool:
        Chip = self.Bank.GetChip(ChipId)
        if Chip is None:
            self.LastError = f"Chip {ChipId} not found"
            return False

        Success = Chip.Connect()
        if Success:
            self.ActiveChips[ChipId] = Chip
            if ChipId in self.DisabledChips:
                del self.DisabledChips[ChipId]
            return True

        self.LastError = f"Failed to connect chip {ChipId}"
        return False

    def DeactivateChip(self, ChipId: str) -> bool:
        # Відключає чіп і лишає його у списку вимкнених.
        Chip = self.ActiveChips.get(ChipId)
        if Chip is None:
            return False

        Chip.Disconnect()
        self.DisabledChips[ChipId] = Chip
        del self.ActiveChips[ChipId]
        return True

    def DetachChip(self, ChipId: str) -> bool:
        # Повністю від'єднує чіп від активного списку.
        Chip = self.ActiveChips.get(ChipId)
        if Chip is None:
            return False

        Chip.Disconnect()
        del self.ActiveChips[ChipId]
        return True

    def GetChipStatus(self, ChipId: str) -> Optional[Dict[str, Any]]:
        # Повертає статус конкретного чіпа.
        Chip = self.Bank.GetChip(ChipId)
        if Chip is not None:
            return Chip.GetStatus()
        return None

    def GetSystemStatus(self) -> Dict[str, Any]:
        # Зведений статус ізолінійного банку.
        return {
            "ActiveCount": len(self.ActiveChips),
            "DisabledCount": len(self.DisabledChips),
            "ActiveIds": list(self.ActiveChips.keys()),
            "DisabledIds": list(self.DisabledChips.keys()),
            "LastError": self.LastError,
            "version": getVersion(),
        }

IsolinearController = ISOController
__all__ = [
    "TaskPriority",
    "TaskStatus",
    "EngineeringTask",
    "EngineeringController",
    "ISOController",
    "IsolinearController",
    "getEngineeringController",
]
