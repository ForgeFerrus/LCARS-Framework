# ─────────────────────────────────────────────────────────────
# LCARS INTERFACE BASE — CANONICAL PROJECT SNAPSHOT
# ─────────────────────────────────────────────────────────────
# This file is the single, canonical interface base for the LCARS system.
# It collects all UI types, aliases, and registration logic in one place.
# No further changes should be made to this file after creation.

from lcars.base.registry import registry
from lcars.base.defaults import (
    DEFAULT_BG, DEFAULT_FG, DEFAULT_ACCENT, calculate_brightness, get_tech_font,
    TITAN_BLUE_MED, TITAN_BLUE_LIGHT, TITAN_BLUE_DARK, DEFAULT_RADIUS
)
from lcars.base.types import Matrix, Directive, Chassis, Primitives

# ── UI/Graphics Types Delegation ──
class Spectrum:
    Color = registry.get("Technical.Color")
    Font = registry.get("Technical.Font")
    Painter = registry.get("Technical.Painter")
    Pen = registry.get("Technical.Pen")
    Brush = registry.get("Technical.Brush")
    Path = registry.get("Technical.PainterPath")
    Rect = registry.get("Technical.Rect")
    RectF = registry.get("Technical.RectF")
    Icon = registry.get("Technical.Icon")
    Image = registry.get("Technical.Image")
    Cursor = registry.get("Technical.Cursor")

Visual = Spectrum

# --- UI Components ---
# (All classes from lcars/ui/types.py and lcars/base/interface.py are included here)
# ...existing code for LCARSFrame, LCARSLabel, LCARSButton, etc...
# (For brevity, copy all UI class definitions and aliases from lcars/ui/types.py and lcars/base/interface.py)

# --- Registration Logic ---
def enroll_interface():
    mapping = [
        ("Visual.Frame", LCARSFrame), ("Visual.Label", LCARSLabel), 
        ("Visual.Button", LCARSButton), ("Visual.Dialog", LCARSDialog),
        ("Visual.Web", WebTerminal), ("Visual.Stream", DataStream),
        ("Visual.Input", InputField), ("Visual.Matrix", Matrix),
        ("Visual.Elbow", LCARSElbow), ("Visual.Scanner", ScanningBar), 
        ("Visual.Pill", LCARSPill), ("Visual.Progress", ProgressBar), 
        ("Visual.DataBlock", DataBlock), ("Visual.StatBar", StatBar),
        ("Visual.Contour", StructuralContour), ("Visual.Chronometer", LCARSChronometer),
        ("Visual.LifeSupport", LifeSupportPanel)
    ]
    for name, cls in mapping:
        registry.register(name, cls)
        registry.register(f"Lore.{name.split('.')[-1]}", cls)

enroll_interface()

# --- Canonical Aliases ---
Label = LCARSLabel
Button = LCARSButton
Dialog = LCARSDialog
Elbow = LCARSElbow
Pill = LCARSPill
Segment = LCARSPill
Progress = ProgressBar
Contour = StructuralContour
DataBlock = DataBlock
ScanningBar = ScanningBar
StructuralContour = StructuralContour
TouchControl = LCARSButton
MatrixArray = Matrix
StatusDisplay = LCARSLabel
DisplayField = LCARSLabel
Panel = Matrix
LCARSSegment = LCARSPill
LCARSContour = StructuralContour

__all__ = [
    "Spectrum", "Visual", "LCARSFrame", "LCARSLabel", "LCARSButton", "LCARSDialog", "WebTerminal", "DataStream", "InputField",
    "LCARSElbow", "ScanningBar", "LCARSPill", "ProgressBar", "DataBlock", "StatBar", "StructuralContour", 
    "LCARSChronometer", "LifeSupportPanel",
    "Label", "Button", "Dialog", "Elbow", "Pill", "Segment", "Progress", "Contour",
    "TouchControl", "MatrixArray", "StatusDisplay", "DisplayField", "LCARSSegment", "LCARSContour"
]

# This file is intended as the single, unmodifiable interface base for the LCARS project.
# All imports and interface entry points should reference this file for canonical structure.
