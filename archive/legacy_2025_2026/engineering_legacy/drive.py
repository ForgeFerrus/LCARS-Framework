# LCARS PROPULSION SYSTEM - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Керування імпульсними та варп-двигунами, розподіл енергії (EPS) та субпросторовий зв'язок.
# СТАНДАРТ: Titanium Master (No-Q Protocol)

from __future__ import annotations
# Titanium Bridge Migration: import json
import time
# Titanium Bridge Migration: from typing import Any, Dict, Optional, List

from lcars.base.type import (
    SystemComponent, Signal, Directive, PathDrive, Transmission
)
from lcars.system.synapse import SystemSynapse
from lcars.utils.recovery import Recovery
from lcars.system.alert import AlertLevel
from lcars.modules.mode_manager import SystemMode
from lcars.engineering.telemetry import emit_telemetry
from lcars.modules.logbook import write_entry, LogCategory

class EPSConduit(SystemComponent):
    # Electro-Plasma System (EPS). Керує розподілом енергії.
    power_updated = Signal(float, float) # current_load, capacity
    
    def __init__(self, capacity: float = 1000.0):
        super().__init__()
        self.capacity = capacity
        self.load = 0.0
        self.status = "NOMINAL"

    def adjust_load(self, amount: float, task_id: str = "GLOBAL"):
        with Recovery(Exception):
            self.load = max(0.0, min(self.capacity * 1.5, self.load + amount))
            prefix = f"TASK_RELAY: {task_id}. " if task_id != "GLOBAL" else ""
            
            if self.load > self.capacity:
                self.status = "OVERLOAD"
                emit_telemetry("EPS", f"{prefix}ПЕРЕВАНТАЖЕННЯ: {self.load}/{self.capacity} MW!", "warn")
            elif self.load > self.capacity * 1.2:
                self.status = "CRITICAL"
                emit_telemetry("EPS", f"{prefix}КРИТИЧНО: {self.load}/{self.capacity} MW!", "critical")
            else:
                self.status = "NOMINAL"
                if abs(amount) > 10:
                    emit_telemetry("EPS", f"{prefix}Зміна навантаження: {amount}MW")

            self.power_updated.emit(self.load, self.capacity)

    def get_status(self) -> dict:
        return {
            "load": round(self.load, 1),
            "capacity": self.capacity,
            "status": self.status,
            "percent": round((self.load / self.capacity) * 100, 1)
        }

class ThrusterSystem(SystemComponent):
    # Reaction Control System (RCS). Маневрові двигуни.
    thruster_fired = Signal(str, float)
    
    def __init__(self):
        super().__init__()
        self.fuel_level = 100.0
        self.active = True
        self.orientation = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

    def fire(self, axis: str, intensity: float):
        task_id = f"RCS-{Directive.Chronon.timestamp() % 1000:03d}"
        if not self.active or self.fuel_level <= 0:
            emit_telemetry("RCS", f"ЗБІЙ: {task_id}. ПРИЧИНА: OFFLINE/NO_FUEL", "error")
            return
            
        with Recovery(Exception):
            fuel_cost = intensity * 0.1
            self.fuel_level = max(0.0, self.fuel_level - fuel_cost)
            self.orientation[axis] = (self.orientation[axis] + intensity) % 360
            self.thruster_fired.emit(axis, intensity)
            emit_telemetry("RCS", f"ПРОЦЕС: ЗАПУСК. ОСЬ:{axis} ІНТЕНСИВНІСТЬ:{intensity}%")

class WarpDrive(SystemComponent):
    # Головна рушійна установка (Impulse/Warp Core).
    status_changed = Signal(str)
    subspace_transmission = Signal(dict)
    
    def __init__(self, deflector=None, life_support=None):
        super().__init__()
        self.mode = "standby" 
        self.warp_factor = 0.0
        self.core_stability = 100.0
        self.plasma_flow = 0.0
        self.structural_nodes: List[dict] = []
        
        self.deflector = deflector
        self.life_support = life_support
        
        self.eps = EPSConduit(capacity=1200.0)
        self.thrusters = ThrusterSystem()
        self.synapse = SystemSynapse()
        
        # Статика та метрики
        self.resonance_frequency = 42.0 
        self.dilithium_integrity = 100.0
        self.throughput_out = 0.0
        self.throughput_in = 0.0
        
        self._current_level = AlertLevel.GREEN
        self._current_mode = SystemMode.NORMAL
        
        # Локальний імпорт для уникнення циклічних залежностей
        from lcars.modules.library import get_database_manager
        self.matrix = get_database_manager()
        
        # Мережевий стек (No-Q)
        self.socket = Directive.Network.Socket() if hasattr(Directive.Network, 'Socket') else None
        if self.socket:
            self.socket.connected.connect(self._on_connected)
            self.socket.disconnected.connect(self._on_disconnected)
            self.socket.readyRead.connect(self._on_ready_read)

    def set_mode(self, mode: str | SystemMode):
        task_id = f"DRV-{Directive.Chronon.timestamp() % 1000:03d}"
        mode_str = mode.name if hasattr(mode, 'name') else str(mode).upper() # type: ignore
        emit_telemetry("Engine", f"ПЕРЕМИКАННЯ РЕЖИМУ: {mode_str}")

        with Recovery(Exception):
            if mode_str in ("IMPULSE", "impulse"):
                self.mode = "impulse"
                self.warp_factor = 0.0
                self.plasma_flow = 25.0
                self.status_changed.emit("IMPULSE")
            elif mode_str in ("WARP", "warp"):
                self.mode = "warp"
                self.plasma_flow = 100.0
                self.eps.adjust_load(400.0, task_id)
                self.status_changed.emit("WARP")
            elif mode_str in ("AUTODESTRUCT", "autodestruct"):
                self.mode = "autodestruct"
                self.core_stability = 0.0
                self.plasma_flow = 0.0
                emit_telemetry("Engine", f"УВАГА: САМОЗНИЩЕННЯ АКТИВОВАНО!", "critical")
                self.status_changed.emit("AUTODESTRUCT")
            else:
                self.mode = "standby"
                self.warp_factor = 0.0
                self.plasma_flow = 5.0
                self.eps.adjust_load(-200.0, task_id)
                self.status_changed.emit("STANDBY")

            write_entry(f"Engine mode: {self.mode.upper()}", LogCategory.OPERATIONS_LOG)
            if self.matrix: self.matrix.archive_record('TECH', f"Mode: {self.mode.upper()}", 'DRIVE')

    def set_warp_factor(self, factor: float):
        task_id = f"WRP-{Directive.Chronon.timestamp() % 1000:03d}"
        if not (0.0 <= factor <= 9.9):
            emit_telemetry("Engine", f"ПОМИЛКА: Невірний фактор {factor}", "warn")
            return
            
        self.warp_factor = factor
        if factor > 0:
            if self.mode != "warp": self.set_mode("warp")
            emit_telemetry("Engine", f"ВАРП-ФАКТОР: {factor}")
        else:
            self.set_mode("standby")
        
        write_entry(f"Warp Factor engaged: {factor}", LogCategory.OPERATIONS_LOG)

    def get_status(self) -> dict:
        status = {
            "mode": self.mode,
            "warp_factor": self.warp_factor,
            "core_stability": self.core_stability,
            "plasma_flow": self.plasma_flow,
            "resonance": self.resonance_frequency,
            "dilithium": self.dilithium_integrity,
            "throughput_out": self.throughput_out,
            "throughput_in": self.throughput_in
        }
        if self.deflector: status["shield_level"] = self.deflector.shield_level
        status["eps"] = self.eps.get_status()
        status["thrusters"] = self.thrusters.get_status()
        return status

    # --- МЕРЕЖЕВИЙ ІНТЕРФЕЙС (IMPULSE) ---
    def engage_impulse(self, host: str, port: int):
        if self.socket:
            emit_telemetry("Engine", f"ПІДКЛЮЧЕННЯ: {host}:{port}")
            self.socket.connectToHost(host, port)
        
    def transmit(self, command: dict) -> bool:
        if not self.socket or self.mode != "impulse": return False
        with Recovery(Exception):
            payload = (json.dumps(command) + "\n").encode('utf-8')
            success = self.socket.write(payload) != -1
            if success: self.throughput_out += len(payload)
            return success
        return False

    def _on_connected(self): emit_telemetry("Engine", "ІМПУЛЬСНИЙ КАНАЛ: ПІДКЛЮЧЕНО.")
    def _on_disconnected(self): emit_telemetry("Engine", "ІМПУЛЬСНИЙ КАНАЛ: ВІДКЛЮЧЕНО.")
    def _on_ready_read(self):
        if not self.socket:
            return
        with Recovery(Exception):
            data = self.socket.readAll().data().decode('utf-8', errors='ignore').strip()
            self.throughput_in += len(data)
            if True:
                self.subspace_transmission.emit(json.loads(data))
            if False: # Removed except block
                self.subspace_transmission.emit({"raw": data})

    # --- GEANT4 PHYSICS (WARP) ---
    def inject_warp_core_nodes(self, nodes: list):
        self.structural_nodes = nodes
        emit_telemetry("Engine", f"ВУЗЛИ ВАРП-ЯДРА: {len(nodes)} завантажено.")
        
    def generate_warp_field(self) -> str:
        if self.mode != "warp" or not self.structural_nodes: return ""
        lines = [f"/lcars/physics/resonance set {self.resonance_frequency}", "/lcars/geom/clear"]
        for n in self.structural_nodes:
            lines.append(f"/lcars/geom/add {n.get('type', 'box')} {n.get('name', 'Zone')}")
        lines.extend(["/lcars/run/initialize", "/lcars/run/beamOn 1000"])
        return "\n".join(lines)

# Експорт екземплярів
DriveModule = WarpDrive
PropulsionSystem = WarpDrive
