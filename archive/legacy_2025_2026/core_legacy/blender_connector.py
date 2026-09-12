"""
Core-level shim: re-export Blender connector implementation
from the engineering package. This keeps a stable import path for
code that expects `lcars.core.blender_connector` while centralizing
the real implementation in `lcars.engineering.connector`.
"""

from lcars.engineering.connector import (
    BlenderConnector,
    BlenderSession,
    BlenderObject,
    GeometryType,
    MaterialEnum,
    DetectorObjectDefinition,
)

__all__ = [
    "BlenderConnector",
    "BlenderSession",
    "BlenderObject",
    "GeometryType",
    "MaterialEnum",
    "DetectorObjectDefinition",
]
