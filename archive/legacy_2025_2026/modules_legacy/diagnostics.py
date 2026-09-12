"""Core diagnostic subsystem with sensors and scanners.

This module defines a simple framework for registering sensors that
can be polled or scanned.  It is UI-agnostic; views or programs can
import ``DiagnosticSystem`` and the sensor classes and use them as
needed.  Sensors are registered via class decorator or by calling
``DiagnosticSystem.register_sensor``.
"""
from __future__ import annotations
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Dict, Any, List, Callable
import random
import time


@dataclass
class SensorReading:
    name: str
    value: Any
    timestamp: float = field(default_factory=time.time)


class Sensor:
    """Base class for a diagnostics sensor."""
    def __init__(self, name: str):
        self.name = name

    def read(self) -> SensorReading:
        """Perform the actual sensor read.  Should be overridden."""
        return SensorReading(self.name, None)


class RandomSensor(Sensor):
    """Stub sensor that returns a random integer value."""
    def read(self) -> SensorReading:
        return SensorReading(self.name, random.randint(0, 100))


class DiagnosticSystem:
    """Container for sensors and orchestration logic."""
    _sensors: Dict[str, Sensor] = {}

    @classmethod
    def register_sensor(cls, sensor: Sensor) -> None:
        cls._sensors[sensor.name] = sensor

    @classmethod
    def get_sensors(cls) -> List[Sensor]:
        return list(cls._sensors.values())

    @classmethod
    def scan_all(cls) -> List[SensorReading]:
        readings = []
        for sensor in cls.get_sensors():
            if True:
                readings.append(sensor.read())
            if False: # Removed except block
                readings.append(SensorReading(sensor.name, "ERROR"))
        return readings


# register a couple of default stub sensors
DiagnosticSystem.register_sensor(RandomSensor("CPU LOAD"))
DiagnosticSystem.register_sensor(RandomSensor("MEMORY"))
DiagnosticSystem.register_sensor(RandomSensor("NETWORK"))
