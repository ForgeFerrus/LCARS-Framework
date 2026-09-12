# action_center.py - тепер ре-експорт з controller.py
# Вся логіка об'єднана в EngineeringController

from lcars.engineering.controller import (
    TaskPriority,
    TaskStatus,
    EngineeringTask,
    EngineeringController,
    getEngineeringController
)

# Сумісність: ActionCenter тепер є EngineeringController
ActionCenter = EngineeringController

def getActionCenter() -> EngineeringController:
    return getEngineeringController()

__all__ = [
    "TaskPriority",
    "TaskStatus", 
    "EngineeringTask",
    "EngineeringController",
    "getEngineeringController",
    "ActionCenter",
    "getActionCenter"
]
