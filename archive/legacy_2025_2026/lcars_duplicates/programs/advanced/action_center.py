from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json

class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

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
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.value,
            "assignedTo": self.assignedTo,
            "createdAt": self.createdAt,
            "startedAt": self.startedAt,
            "completedAt": self.completedAt,
            "metadata": self.metadata,
            "dependencies": self.dependencies
        }

class ActionCenter:
    def __init__(self):
        self.tasks: Dict[str, EngineeringTask] = {}
        self.agents: Dict[str, Callable] = {}
        self.history: List[Dict] = []
        self.listeners: List[Callable] = []
        
    def createTask(self, taskId: str, title: str, description: str, 
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   assignedTo: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> EngineeringTask:
        task = EngineeringTask(
            id=taskId,
            title=title,
            description=description,
            priority=priority,
            assignedTo=assignedTo,
            metadata=metadata or {}
        )
        self.tasks[taskId] = task
        self._notify("task_created", task)
        return task
    
    def startTask(self, taskId: str) -> bool:
        if taskId not in self.tasks:
            return False
        task = self.tasks[taskId]
        if task.status != TaskStatus.PENDING:
            return False
        task.status = TaskStatus.IN_PROGRESS
        task.startedAt = time.time()
        self._notify("task_started", task)
        return True
    
    def completeTask(self, taskId: str, result: Optional[Dict] = None) -> bool:
        if taskId not in self.tasks:
            return False
        task = self.tasks[taskId]
        if task.status != TaskStatus.IN_PROGRESS:
            return False
        task.status = TaskStatus.COMPLETED
        task.completedAt = time.time()
        if result:
            task.metadata["result"] = result
        self._notify("task_completed", task)
        self.history.append({
            "action": "complete",
            "taskId": taskId,
            "timestamp": time.time()
        })
        return True
    
    def failTask(self, taskId: str, error: str) -> bool:
        if taskId not in self.tasks:
            return False
        task = self.tasks[taskId]
        task.status = TaskStatus.FAILED
        task.metadata["error"] = error
        task.completedAt = time.time()
        self._notify("task_failed", task)
        return True
    
    def getTasksByStatus(self, status: TaskStatus) -> List[EngineeringTask]:
        return [t for t in self.tasks.values() if t.status == status]
    
    def getTasksByPriority(self, priority: TaskPriority) -> List[EngineeringTask]:
        return [t for t in self.tasks.values() if t.priority == priority]
    
    def getActiveTasks(self) -> List[EngineeringTask]:
        return [t for t in self.tasks.values() 
                if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS)]
    
    def registerAgent(self, agentId: str, handler: Callable):
        self.agents[agentId] = handler
        
    def assignTask(self, taskId: str, agentId: str) -> bool:
        if taskId not in self.tasks or agentId not in self.agents:
            return False
        task = self.tasks[taskId]
        task.assignedTo = agentId
        self._notify("task_assigned", task)
        return True
    
    def executeTask(self, taskId: str) -> bool:
        if taskId not in self.tasks:
            return False
        task = self.tasks[taskId]
        if not task.assignedTo or task.assignedTo not in self.agents:
            return False
        self.startTask(taskId)
        handler = self.agents[task.assignedTo]
        if not callable(handler):
            self.failTask(taskId, "Agent not callable")
            return False
        result = handler(task)
        self.completeTask(taskId, {"result": result})
        return True
    
    def addListener(self, callback: Callable):
        self.listeners.append(callback)
        
    def _notify(self, event: str, task: EngineeringTask):
        for listener in self.listeners:
            if callable(listener):
                listener(event, task)
    
    def exportTasks(self) -> str:
        data = {tid: t.toDict() for tid, t in self.tasks.items()}
        return json.dumps(data, indent=2, default=str)
    
    def getStats(self) -> Dict[str, int]:
        return {
            "total": len(self.tasks),
            "pending": len(self.getTasksByStatus(TaskStatus.PENDING)),
            "in_progress": len(self.getTasksByStatus(TaskStatus.IN_PROGRESS)),
            "completed": len(self.getTasksByStatus(TaskStatus.COMPLETED)),
            "failed": len(self.getTasksByStatus(TaskStatus.FAILED))
        }

_actionCenter: Optional[ActionCenter] = None

def getActionCenter() -> ActionCenter:
    global _actionCenter
    if _actionCenter is None:
        _actionCenter = ActionCenter()
    return _actionCenter
