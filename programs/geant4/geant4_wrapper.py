"""
Geant4 wrapper (tools copy)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum
from pathlib import Path
import json
from datetime import datetime


class ParticleType(Enum):
    NEUTRON = "neutron"
    GAMMA = "gamma"
    ELECTRON = "electron"
    PROTON = "proton"
    ALPHA = "alpha"
    SECONDARY = "secondary"


class MaterialType(Enum):
    PURE = "pure"
    COMPOUND = "compound"
    MIXTURE = "mixture"
    VACUUM = "vacuum"


class DetectorShape(Enum):
    BOX = "box"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    CONE = "cone"
    POLYCONE = "polycone"


@dataclass
class Vector3D:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Material:
    name: str
    material_type: MaterialType = MaterialType.PURE
    density: float = 1.0
    components: Dict[str, float] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.material_type.value,
            "density": self.density,
            "components": self.components,
            "properties": self.properties,
        }


@dataclass
class DetectorComponent:
    name: str
    shape: DetectorShape
    dimensions: Vector3D
    position: Vector3D = field(default_factory=lambda: Vector3D())
    rotation: Vector3D = field(default_factory=lambda: Vector3D())
    material: Optional[Material] = None
    color: Tuple[float, float, float] = (1.0, 0.5, 0.0)

    def to_dict(self):
        return {
            "name": self.name,
            "shape": self.shape.value,
            "dimensions": self.dimensions.to_dict(),
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "material": self.material.to_dict() if self.material else None,
            "color": self.color,
        }


@dataclass
class Detector:
    name: str
    components: List[DetectorComponent] = field(default_factory=list)
    total_volume: float = 0.0

    def add_component(self, component: DetectorComponent):
        self.components.append(component)

    def calculate_volume(self):
        import math
        total = 0.0
        for component in self.components:
            dim = component.dimensions
            if component.shape == DetectorShape.BOX:
                volume = dim.x * dim.y * dim.z
            elif component.shape == DetectorShape.CYLINDER:
                volume = math.pi * (dim.x ** 2) * dim.z
            elif component.shape == DetectorShape.SPHERE:
                volume = (4 / 3) * math.pi * (dim.x ** 3)
            elif component.shape == DetectorShape.CONE:
                volume = (1 / 3) * math.pi * (dim.x ** 2) * dim.z
            else:
                volume = 0.0
            total += volume
        self.total_volume = round(total, 3)
        return self.total_volume


@dataclass
class Particle:
    particle_type: ParticleType
    energy: float
    direction: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 1))
    position: Vector3D = field(default_factory=lambda: Vector3D())
    multiplicity: int = 1

    def to_dict(self):
        return {
            "type": self.particle_type.value,
            "energy": self.energy,
            "direction": self.direction.to_dict(),
            "position": self.position.to_dict(),
            "multiplicity": self.multiplicity,
        }


@dataclass
class PhysicsList:
    name: str
    enable_radioactive_decay: bool = True
    enable_optical: bool = False
    enable_em: bool = True
    enable_hadronic: bool = True

    def to_dict(self):
        return {
            "name": self.name,
            "radioactive_decay": self.enable_radioactive_decay,
            "optical": self.enable_optical,
            "em": self.enable_em,
            "hadronic": self.enable_hadronic,
        }


class Simulation:
    def __init__(self, name: str, project_path: Path):
        self.name = name
        self.project_path = project_path
        self.detector: Optional[Detector] = None
        self.primary_particle: Optional[Particle] = None
        self.physics_list: Optional[PhysicsList] = None
        self.num_events: int = 1000
        self.output_dir: Path = project_path / "output"
        self.created_at: datetime = datetime.now()
        self.status: str = "created"

    def configure_from_ncc02(self, sample_type: str = "pure", energy_mev: float = 0.0253):
        crystal = DetectorComponent(
            name="Co-59 Crystal",
            shape=DetectorShape.CYLINDER,
            dimensions=Vector3D(x=2.0, y=2.0, z=2.0),
            material=Material.cobalt_59() if sample_type == "pure" else Material.cobalt_oxide(),
            color=(1.0, 0.6, 0.2),
        )
        shield = DetectorComponent(
            name="Lead Shield",
            shape=DetectorShape.BOX,
            dimensions=Vector3D(x=5.0, y=5.0, z=5.0),
            material=Material.lead_shield(),
            color=(0.4, 0.4, 0.4),
        )
        self.detector = Detector(name="NCC-02 Detector")
        self.detector.add_component(crystal)
        self.detector.add_component(shield)
        self.primary_particle = Particle(particle_type=ParticleType.NEUTRON, energy=energy_mev)
        self.physics_list = PhysicsList(name="QGSP_BIC_HP", enable_radioactive_decay=True)
        self.status = "configured"

    def get_configuration_dict(self):
        return {
            "name": self.name,
            "detector": self.detector.to_dict() if self.detector else None,
            "primary_particle": self.primary_particle.to_dict() if self.primary_particle else None,
            "physics_list": self.physics_list.to_dict() if self.physics_list else None,
            "num_events": self.num_events,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }
