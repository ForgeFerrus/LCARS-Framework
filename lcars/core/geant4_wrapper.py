"""
LCARS Geant4 Object-Oriented Wrapper
=====================================
Об'єктна модель для управління симуляціями, матеріалами та детекторами.

Клас:
    - Simulation: Основний об'єкт симуляції
    - Detector: Геометрія детектора
    - Material: Матеріали
    - Particle: Характеристики частинок
    - PhysicsList: Фізичні процеси
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from pathlib import Path
import json
from datetime import datetime


class ParticleType(Enum):
    """Типи частинок"""
    NEUTRON = "neutron"
    GAMMA = "gamma"
    ELECTRON = "electron"
    PROTON = "proton"
    ALPHA = "alpha"
    SECONDARY = "secondary"


class MaterialType(Enum):
    """Типи матеріалів"""
    PURE = "pure"
    COMPOUND = "compound"
    MIXTURE = "mixture"
    VACUUM = "vacuum"


class DetectorShape(Enum):
    """Геометричні форми"""
    BOX = "box"
    CYLINDER = "cylinder"
    SPHERE = "sphere"
    CONE = "cone"
    POLYCONE = "polycone"


@dataclass
class Vector3D:
    """3D вектор"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def to_dict(self):
        return {"x": self.x, "y": self.y, "z": self.z}


@dataclass
class Material:
    """Матеріал для детектора"""
    name: str
    material_type: MaterialType = MaterialType.PURE
    density: float = 1.0  # g/cm³
    components: Dict[str, float] = field(default_factory=dict)  # {element: fraction}
    properties: Dict[str, any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.material_type.value,
            "density": self.density,
            "components": self.components,
            "properties": self.properties
        }

    @classmethod
    def cobalt_59(cls):
        """Co-59 чистий метал"""
        return cls(
            name="Co-59",
            material_type=MaterialType.PURE,
            density=8.9,
            components={"Co": 1.0}
        )

    @classmethod
    def cobalt_oxide(cls):
        """CoO3 оксид"""
        return cls(
            name="CoO3",
            material_type=MaterialType.COMPOUND,
            density=3.8,
            components={"Co": 1.0, "O": 3.0}
        )

    @classmethod
    def lead_shield(cls):
        """Pb екран"""
        return cls(
            name="Lead",
            material_type=MaterialType.PURE,
            density=11.34,
            components={"Pb": 1.0}
        )


@dataclass
class DetectorComponent:
    """Компонент детектора (Crystal, Shield, Collimator)"""
    name: str
    shape: DetectorShape
    dimensions: Vector3D  # залежить від форми
    position: Vector3D = field(default_factory=lambda: Vector3D())
    rotation: Vector3D = field(default_factory=lambda: Vector3D())
    material: Optional[Material] = None
    color: Tuple[float, float, float] = (1.0, 0.5, 0.0)  # RGB для візуалізації

    def to_dict(self):
        return {
            "name": self.name,
            "shape": self.shape.value,
            "dimensions": self.dimensions.to_dict(),
            "position": self.position.to_dict(),
            "rotation": self.rotation.to_dict(),
            "material": self.material.to_dict() if self.material else None,
            "color": self.color
        }


@dataclass
class Detector:
    """Детектор з компонентами"""
    name: str
    components: List[DetectorComponent] = field(default_factory=list)
    total_volume: float = 0.0  # см³

    def add_component(self, component: DetectorComponent):
        """Додати компонент"""
        self.components.append(component)

    def calculate_volume(self):
        """Розрахувати загальний об'єм"""
        # TODO: реалізувати за формами
        pass

    def to_dict(self):
        return {
            "name": self.name,
            "components": [c.to_dict() for c in self.components],
            "total_volume": self.total_volume
        }


@dataclass
class Particle:
    """Первинна частинка"""
    particle_type: ParticleType
    energy: float  # MeV
    direction: Vector3D = field(default_factory=lambda: Vector3D(0, 0, 1))
    position: Vector3D = field(default_factory=lambda: Vector3D())
    multiplicity: int = 1

    def to_dict(self):
        return {
            "type": self.particle_type.value,
            "energy": self.energy,
            "direction": self.direction.to_dict(),
            "position": self.position.to_dict(),
            "multiplicity": self.multiplicity
        }


@dataclass
class PhysicsList:
    """Фізичні процеси"""
    name: str  # QGSP_BIC_HP, FTFP_BERT, LowE, тощо
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
            "hadronic": self.enable_hadronic
        }


class Simulation:
    """Головний об'єкт симуляції"""

    def __init__(self, name: str, project_path: Path):
        self.name = name
        self.project_path = project_path
        self.detector: Optional[Detector] = None
        self.primary_particle: Optional[Particle] = None
        self.physics_list: Optional[PhysicsList] = None
        self.num_events: int = 1000
        self.output_dir: Path = project_path / "output"
        self.created_at: datetime = datetime.now()
        self.status: str = "created"  # created, configured, running, finished, error

    def set_detector(self, detector: Detector):
        """Встановити детектор"""
        self.detector = detector
        self.status = "detector_set"

    def set_primary_particle(self, particle: Particle):
        """Встановити первинну частинку"""
        self.primary_particle = particle

    def set_physics(self, physics_list: PhysicsList):
        """Встановити фізичні процеси"""
        self.physics_list = physics_list

    def configure_from_ncc02(self, sample_type: str = "pure", energy_mev: float = 0.0253):
        """Сконфігурувати симуляцію на основі NCC-02 проекту"""
        # Детектор
        crystal = DetectorComponent(
            name="Co-59 Crystal",
            shape=DetectorShape.CYLINDER,
            dimensions=Vector3D(x=2.0, y=2.0, z=2.0),
            material=Material.cobalt_59() if sample_type == "pure" else Material.cobalt_oxide(),
            color=(1.0, 0.6, 0.2)
        )
        
        shield = DetectorComponent(
            name="Lead Shield",
            shape=DetectorShape.BOX,
            dimensions=Vector3D(x=5.0, y=5.0, z=5.0),
            position=Vector3D(),
            material=Material.lead_shield(),
            color=(0.4, 0.4, 0.4)
        )

        self.detector = Detector(name="NCC-02 Detector")
        self.detector.add_component(crystal)
        self.detector.add_component(shield)

        # Первинна частинка
        self.primary_particle = Particle(
            particle_type=ParticleType.NEUTRON,
            energy=energy_mev,
            direction=Vector3D(0, 0, 1)
        )

        # Фізика
        self.physics_list = PhysicsList(
            name="QGSP_BIC_HP",
            enable_radioactive_decay=True
        )

        self.status = "configured"

    def get_configuration_dict(self):
        """Отримати конфігурацію як dict"""
        return {
            "name": self.name,
            "detector": self.detector.to_dict() if self.detector else None,
            "primary_particle": self.primary_particle.to_dict() if self.primary_particle else None,
            "physics_list": self.physics_list.to_dict() if self.physics_list else None,
            "num_events": self.num_events,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }

    def save_config(self, filepath: Path):
        """Зберегти конфігурацію в JSON"""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.get_configuration_dict(), f, indent=2)

    def load_config(self, filepath: Path):
        """Завантажити конфігурацію з JSON"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # TODO: парсити JSON та відновлювати об'єкти
        self.status = "loaded"

    def __repr__(self):
        return f"<Simulation: {self.name} ({self.status})>"


# Приклади використання
if __name__ == "__main__":
    from pathlib import Path

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
