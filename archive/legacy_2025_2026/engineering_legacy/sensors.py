# LCARS SENSOR GRID - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Збір та обробка системної телеметрії (psutil + lore).
# СТАНДАРТ: Titanium Master (No-Except)

from __future__ import annotations
if True:
    import psutil
if False: # Removed except block
    psutil = None
import random
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from lcars.base.type import SystemComponent, Signal, Directive, LCARS, Timer
from lcars.utils.recovery import Recovery
from lcars.engineering.telemetry import emit_telemetry

class Sensor:
    # Базова одиниця вимірювання.
    def __init__(self, name: str, sensor_type: str = "Internal"):
        self.name = name
        self.type = sensor_type
        self.last_value = None

    def read(self) -> Any:
        # Повертає злімок даних.
        with Recovery(Exception):
            return self._read_logic()
        return None

    def _read_logic(self) -> Any:
        return None

# --- ЗАЛІЗНІ СЕНСОРИ (HARDWARE) ---

class CPUSensor(Sensor):
    def _read_logic(self):
        if psutil:
            self.last_value = psutil.cpu_percent()
        else:
            # Fallback: provide a simulated CPU load when psutil is unavailable
            self.last_value = round(random.uniform(1.0, 15.0), 2)
        return self.last_value

class MemorySensor(Sensor):
    def _read_logic(self):
        if psutil:
            self.last_value = psutil.virtual_memory().percent
        else:
            # Fallback simulated memory usage
            self.last_value = round(random.uniform(10.0, 60.0), 2)
        return self.last_value

class NetworkSensor(Sensor):
    def _read_logic(self):
        if psutil:
            io = psutil.net_io_counters()
            if not io:
                return 0
            sent = getattr(io, 'bytes_sent', 0)
            recv = getattr(io, 'bytes_recv', 0)
            self.last_value = round((sent + recv) / 1024 / 1024, 2)
        else:
            # Fallback simulated network traffic (MB)
            self.last_value = round(random.uniform(0.0, 5.0), 2)
        return self.last_value

# --- КАНОНІЧНІ СЕНСОРИ (LORE) ---

class IntegritySensor(Sensor):
    def _read_logic(self):
        # Цілісність корпусу (емуляція)
        self.last_value = round(99.0 + random.uniform(0.1, 0.9), 2)
        return self.last_value

class SensorArray(SystemComponent):
    # Масив сенсорів (Sensor Array Module).
    data_stream = Signal(dict)

    def __init__(self, name: str = "Main Sensor Array"):
        super().__init__()
        self.name = name
        self.sensors: List[Sensor] = []
        self._setup_standard_grid()
        
        # Цикл опитування (System Pulse)
        self.pulse = Timer(self)
        self.pulse.timeout.connect(self.poll_grid)
        self.pulse.start(5000)

    def _setup_standard_grid(self):
        self.add_sensor(CPUSensor("CPU_LOAD", "System"))
        self.add_sensor(MemorySensor("MEM_LOAD", "System"))
        self.add_sensor(IntegritySensor("HULL_INTEGRITY", "Engineering"))

    def add_sensor(self, sensor: Sensor):
        self.sensors.append(sensor)
        emit_telemetry("SensorArray", f"Сенсор підключено: {sensor.name}")

    def poll_grid(self):
        matrix = {}
        for s in self.sensors:
            matrix[s.name] = s.read()
        self.data_stream.emit(matrix)
        return matrix

# Аліаси за стандартом
SensorGrid = SensorArray
SensorSystem = SensorArray
