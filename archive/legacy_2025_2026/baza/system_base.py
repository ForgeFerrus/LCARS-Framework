# ─────────────────────────────────────────────────────────────
# LCARS SYSTEM BASE — CANONICAL PROJECT SNAPSHOT
# ─────────────────────────────────────────────────────────────
# This file is the unchangeable, canonical base of the entire LCARS system.
# It collects all core types, UI types, main classes, and system entry points.
# No further changes should be made to this file after creation.

from lcars.base.types import *
from lcars.ui.components import *
from lcars.core.system import MasterSystem, get_system

__all__ = (
    # Core/system types
    "Matrix", "Primitives", "Directive", "Chassis",
    # UI types
    "Spectrum", "Visual", "LCARSFrame", "LCARSLabel", "LCARSButton", "LCARSDialog", "WebTerminal", "DataStream", "InputField",
    "LCARSElbow", "ScanningBar", "LCARSPill", "ProgressBar", "DataBlock", "StatBar", "StructuralContour", "LCARSChronometer", "LifeSupportPanel",
    "Label", "Button", "Dialog", "Elbow", "Pill", "Segment", "Progress", "Contour", "TouchControl", "MatrixArray", "StatusDisplay", "DisplayField",
    "LCARSSegment", "LCARSContour",
    # Main system classes
    "MasterSystem", "get_system"
)

# This file is intended as the single, unmodifiable base for the LCARS project.
# All imports and system entry points should reference this file for canonical structure.
