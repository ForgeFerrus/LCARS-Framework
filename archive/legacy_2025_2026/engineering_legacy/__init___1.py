# engineering package initializer
# this file exists to make the directory a proper namespace package
# and to ensure the local modules are preferred over the archived copies.
# we also export the primary classes and helpers so consumers can do
# ``from lcars.engineering import InterfaceConstructor`` etc.  

from .architecture import IsolinearArchitect
from .constructor import InterfaceConstructor
from .connector import BlenderConnector, DetectorBuilder, GeometryType, MaterialEnum, DetectorObjectDefinition
from .detector_builder import DetectorBuilder as SimpleDetectorBuilder, MaterialEnum as SimpleMaterialEnum
from .edit_mode import EditMode
from .vision_tools import VisionHelper
from .generators import component_factory
from .controller import (
    EngineeringController,
    getEngineeringController,
    TaskPriority,
    TaskStatus,
    EngineeringTask
)
__all__ = [
    "IsolinearArchitect",
    "InterfaceConstructor",
    "BlenderConnector",
    "DetectorBuilder",
    "GeometryType",
    "MaterialEnum",
    "DetectorObjectDefinition",
    "SimpleDetectorBuilder",
    "SimpleMaterialEnum",
    "EditMode",
    "VisionHelper",
    "component_factory",
    "EngineeringController",
    "getEngineeringController",
    "TaskPriority",
    "TaskStatus",
    "EngineeringTask",
]

