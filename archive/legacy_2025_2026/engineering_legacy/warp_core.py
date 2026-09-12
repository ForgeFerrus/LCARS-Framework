# LCARS WARP CORE - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Генератор геометрії для фізичних симуляцій
# СТАНДАРТ: Titanium Master (No-External)

from __future__ import annotations
# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from enum import Enum
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent

class GeometryType(Enum):
    CYLINDER = "cylinder"
    BOX = "box"
    SPHERE = "sphere"
    TUBE = "tube"
    CONE = "cone"

class MaterialEnum(Enum):
    COBALT_59 = "Cobalt-59"
    LEAD = "Lead"
    TUNGSTEN = "Tungsten"
    COPPER = "Copper"
    ALUMINUM = "Aluminum"
    VACUUM = "Vacuum"

@dataclass
class DetectorNode:
    # Вузол детектора для симуляції
    Name: str
    GeomType: GeometryType
    Dimensions: tuple[float, ...]
    Position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    Rotation: tuple[float, float, float] = (0.0, 0.0, 0.0)
    Material: MaterialEnum = MaterialEnum.VACUUM


class WarpCoreEngine(SystemComponent):
    # Варп-ядро - генератор геометрії для фізичних симуляцій

    def __init__(self):
        super().__init__()
        self.Nodes: list[DetectorNode] = []
        self.Status = "ONLINE"

    def AddNode(self, Node: DetectorNode) -> None:
        # Додавання вузла до ядра
        self.Nodes.append(Node)
        
    def ExportToGDML(self) -> str:
        # Експорт геометрії в формат GDML
        if not self.Nodes:
            return ""

        XML = ['<?xml version="1.0"?>', '<gdml>']

        XML.append('  <materials>')
        for Mat in MaterialEnum:
            XML.append(f'    <material name="{Mat.value}"/>')
        XML.append('  </materials>')

        XML.append('  <solids>')
        for N in self.Nodes:
            if N.GeomType == GeometryType.BOX:
                XML.append(f'    <box name="{N.Name}_solid" x="{N.Dimensions[0]}" y="{N.Dimensions[1]}" z="{N.Dimensions[2]}"/>')
            elif N.GeomType == GeometryType.CYLINDER:
                XML.append(f'    <tube name="{N.Name}_solid" rmin="0" rmax="{N.Dimensions[0]}" z="{N.Dimensions[1]}"/>')
        XML.append('  </solids>')

        XML.append('  <structure>')
        for N in self.Nodes:
            XML.append(f'    <volume name="{N.Name}_log">')
            XML.append(f'      <materialref ref="{N.Material.value}"/>')
            XML.append(f'      <solidref ref="{N.Name}_solid"/>')
            XML.append(f'    </volume>')
        XML.append('  </structure>')

        XML.append('  <setup name="Default" version="1.0">')
        if self.Nodes:
            XML.append(f'    <world ref="{self.Nodes[0].Name}_log"/>')
        XML.append('  </setup>')
        XML.append('</gdml>')

        return "\n".join(XML)

    def GenerateCPPMacro(self) -> str:
        # Генерація C++ макросу
        if not self.Nodes:
            return ""

        Macro = []
        for N in self.Nodes:
            Macro.append(f"/lcars/geom/add {N.GeomType.value} {N.Name}")
            Macro.append(f"/lcars/geom/material {N.Name} {N.Material.value}")
            Macro.append(f"/lcars/geom/pos {N.Name} {N.Position[0]} {N.Position[1]} {N.Position[2]}")

        return "\n".join(Macro)

    def GetStatus(self) -> dict[str, Any]:
        # Отримання статусу варп-ядра
        return {
            "Status": self.Status,
            "NodeCount": len(self.Nodes),
            "Nodes": [N.Name for N in self.Nodes],
        }
