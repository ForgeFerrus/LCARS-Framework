"""Authentic LCARS style overrides for eras and factions.

This file provides a compact, opinionated 'authentic' styling guide
that can be applied on top of the existing era palettes. It focuses
on consistent radii, padding, font sizing and elbow geometry so the
UI looks uniform across panels when the 'authentic' mode is enabled
via the project's `config/config.json` ("theme_mode": "authentic").
"""
from __future__ import annotations
# Titanium Bridge Migration: from enum import Enum
from .lcars_palette import LCARSEra


AUTHENTIC_OVERRIDES = {
    LCARSEra.LCARS_25TH: {
        # 25th era uses partial rounding (smaller than 24th)
        "border_radius": "12px",
        "elbow_radius": "30px",
        # Palette remains the same but we provide recommended defaults
        "recommended_font_size": 15,
        "recommended_padding": "6px 14px",
        "panel_border": "#24313f",
    },
}

# Per-faction tweaks: allow sharper edges or color shifts
FACTION_OVERRIDES = {
    # Klingon should prefer harder edges and higher contrast
    "KLINGON": {
        "border_radius": "4px",
        "recommended_font_size": 15,
    },
    # Romulan: softer shapes, slightly larger elbow
    "ROMULAN": {
        "border_radius": "14px",
        "elbow_radius": "40px",
    },
}


def get_authentic_overrides(era, faction=None):
    """Return merged authentic overrides for an era and optional faction."""
    out = {}
    if era in AUTHENTIC_OVERRIDES:
        out.update(AUTHENTIC_OVERRIDES[era])
    if faction:
        # faction may be Enum or str
        key = faction.name if hasattr(faction, "name") else str(faction)
        key = key.upper()
        if key in FACTION_OVERRIDES:
            out.update(FACTION_OVERRIDES[key])
    return out
