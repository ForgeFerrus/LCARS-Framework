"""
Lightweight DetectorBuilder stub used by `DetectorDesignerTab`.
This provides the minimal API expected by the UI: DetectorBuilder, MaterialEnum.

# Розміщено у `lcars.engineering` — невелика допоміжна реалізація для UI та тестування.
"""
# Titanium Bridge Migration: from enum import Enum
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from typing import Any, Dict, Tuple


class MaterialEnum(Enum):
    COBALT_59 = "Cobalt-59"
    LEAD = "Lead"
    TUNGSTEN = "Tungsten"
    # Додайте інші матеріали за потреби


class DetectorBuilder:
    """Проста реалізація збирача геометрії для UI (скелет для подальшої інтеграції).

    Підтримує методи, що викликаються у `DetectorDesignerTab`:
      - add_crystal(name, material, radius, height)
      - add_shield(name, material, dimensions)
      - add_collimator(name, material, inner_radius, outer_radius)
      - to_json(path)

    Це НЕ є повною геометричною моделлю — лише зручний контейнер для збереження
    конфігурації з подальшим експортом у JSON.
    """

    def __init__(self) -> None:
        self.parts: Dict[str, Any] = {"crystal": None, "shield": None, "collimator": None}

    def add_crystal(self, name: str, material: MaterialEnum, radius: float, height: float) -> None:
        self.parts["crystal"] = {
            "name": name,
            "material": material.value if isinstance(material, MaterialEnum) else str(material),
            "radius_cm": float(radius),
            "height_cm": float(height),
        }

    def add_shield(self, name: str, material: MaterialEnum, dimensions: Tuple[float, float, float]) -> None:
        self.parts["shield"] = {
            "name": name,
            "material": material.value if isinstance(material, MaterialEnum) else str(material),
            "dimensions_cm": tuple(float(d) for d in dimensions),
        }

    def add_collimator(self, name: str, material: MaterialEnum, inner_radius: float, outer_radius: float) -> None:
        self.parts["collimator"] = {
            "name": name,
            "material": material.value if isinstance(material, MaterialEnum) else str(material),
            "inner_radius_cm": float(inner_radius),
            "outer_radius_cm": float(outer_radius),
        }

    def to_json(self, path: Path) -> None:
        path = Path(path)
        path.write_text(json.dumps(self.parts, indent=2))
