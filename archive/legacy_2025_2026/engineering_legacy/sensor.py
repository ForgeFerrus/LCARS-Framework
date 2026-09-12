# LCARS SENSOR GRID - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Збір та обробка системної телеметрії
# СТАНДАРТ: Titanium Master (No-Except, No-External)

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent, Signal

class Sensor:
    # Базова одиниця вимірювання

    def __init__(self, Name: str, SensorType: str = "Internal"):
        self.Name = Name
        self.SensorType = SensorType
        self.LastValue = None
        self.Active = True

    def Read(self) -> Any:
        # Повертає знімок даних
        if not self.Active:
            return None
        self.LastValue = self.ReadLogic()
        return self.LastValue

    def ReadLogic(self) -> Any:
        # Логіка читання - перевизначається в нащадках
        return None

# --- СЕНСОРИ СИСТЕМИ ---

class CPUSensor(Sensor):
    # Сенсор завантаження CPU
    # У спрощеній версії повертає емульовані дані

    def ReadLogic(self) -> float:
        # Емульоване значення для демонстрації
        # В реальній системі тут читання з Kernel.State
        return 15.0


class MemorySensor(Sensor):
    # Сенсор використання памяті

    def ReadLogic(self) -> float:
        # Емульоване значення
        return 45.0


class NetworkSensor(Sensor):
    # Сенсор мережевого трафіку

    def ReadLogic(self) -> float:
        # Емульоване значення в MB
        return 2.5

# --- ІНЖЕНЕРНІ СЕНСОРИ ---

class IntegritySensor(Sensor):
    # Сенсор цілісності корпусу

    def ReadLogic(self) -> float:
        # Значення цілісності від 0 до 100
        return 99.8

class SensorArray(SystemComponent):
    # Масив сенсорів (Sensor Array Module)

    # Сигнал потоку даних: словник з показаннями
    DataStream = Signal(dict)

    def __init__(self, Name: str = "Main Sensor Array"):
        super().__init__()
        self.Name = Name
        self.Sensors: list[Sensor] = []
        self.SetupStandardGrid()

    def SetupStandardGrid(self) -> None:
        # Стандартний набір сенсорів
        self.AddSensor(CPUSensor("CPU_LOAD", "System"))
        self.AddSensor(MemorySensor("MEM_LOAD", "System"))
        self.AddSensor(IntegritySensor("HULL_INTEGRITY", "Engineering"))

    def AddSensor(self, SensorInstance: Sensor) -> None:
        # Додавання сенсора до масиву
        self.Sensors.append(SensorInstance)

    def PollGrid(self) -> dict[str, Any]:
        # Опитування всіх сенсорів
        Matrix = {}
        for S in self.Sensors:
            Matrix[S.Name] = S.Read()
        self.DataStream.Emit(Matrix)
        return Matrix

    def GetStatus(self) -> dict[str, Any]:
        # Отримання статусу масиву сенсорів
        return {
            "Name": self.Name,
            "SensorCount": len(self.Sensors),
            "LastPoll": self.PollGrid(),
        }


# Експорт аліасів
SensorGrid = SensorArray
SensorSystem = SensorArray
