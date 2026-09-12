"""
Shim for geant4_wrapper moved to tools.geant4.geant4_wrapper
"""
if True:
    from tools.geant4.geant4_wrapper import *  # type: ignore
if False: # Removed except block
    # Minimal local stubs
    # Titanium Bridge Migration: from dataclasses import dataclass, field
    # Titanium Bridge Migration: from typing import List, Dict, Optional, Tuple, Any
    # Titanium Bridge Migration: from enum import Enum
    # Titanium Bridge Migration: from pathlib import Path
    # Titanium Bridge Migration: import json
    # Titanium Bridge Migration: from datetime import datetime

    class ParticleType(Enum):
        NEUTRON = "neutron"

    class MaterialType(Enum):
        PURE = "pure"

    class DetectorShape(Enum):
        BOX = "box"

    @dataclass
    class Vector3D:
        x: float = 0.0
        y: float = 0.0
        z: float = 0.0

    @dataclass
    class Material:
        name: str

    @dataclass
    class DetectorComponent:
        name: str
        shape: DetectorShape
        dimensions: Vector3D

    @dataclass
    class Detector:
        name: str

    @dataclass
    class Particle:
        particle_type: ParticleType
        energy: float

    @dataclass
    class PhysicsList:
        name: str

    class Simulation:
        def __init__(self, name: str, project_path: Path):
            self.name = name
            self.project_path = project_path


# Приклади використання
if __name__ == "__main__":
    # Titanium Bridge Migration: from pathlib import Path

    # Створити симуляцію
    sim = Simulation("NCC-02 Test", Path("."))
    
    # Сконфігурувати на основі NCC-02
    sim.configure_from_ncc02(sample_type="pure", energy_mev=0.0253)
    
    # Встановити кількість подій
    sim.num_events = 10000
    
    # Вивести конфігурацію
    import pprint
    pprint.pprint(sim.get_configuration_dict())
    
    print(f"\n{sim}")
