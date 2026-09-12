"""Loader that normalizes and exposes theme palettes.

This module ensures ERA_THEMES from `lcars.themes.lcars_palette` conform to
the ThemeContract required keys by filling reasonable fallbacks in-place.
Call ensure_normalized() early in startup so other modules (which import
ERA_THEMES) will observe normalized palettes.
"""
# Titanium Bridge Migration: from typing import Dict
from lcars.themes import lcars_palette
from lcars.themes.theme_contract import validate_theme_mapping


def ensure_normalized() -> Dict:
    """Normalize ERA_THEMES in-place and return the normalized mapping.

    Returns the mapping of era_key -> normalized palette dict.
    """
    mapping = lcars_palette.ERA_THEMES
    contracts, problems = validate_theme_mapping(mapping)
    normalized = {}
    for c in contracts:
        norm = c.as_normalized()
        # write back into original mapping in-place so other code sees normalized values
        # find the original key by matching contract name to enum member name
        for k in list(mapping.keys()):
            kname = getattr(k, 'name', str(k))
            if kname == c.name:
                mapping[k] = norm
                normalized[k] = norm
                break
    # return normalized mapping for convenience
    return normalized


def get_normalized_palette_by_name(name: str):
    """Convenience: return normalized palette for friendly name like '25th' or '22nd'."""
    # ensure normalized before lookup
    ensure_normalized()
    name_map = {
        "22nd": lcars_palette.LCARSEra.NX_CLASS_22ND,
        "23rd": lcars_palette.LCARSEra.CONSTITUTION_CLASS_23RD,
        "23st": lcars_palette.LCARSEra.EXCELSIOR_CLASS_23ST,
        "24th": lcars_palette.LCARSEra.GALAXY_CLASS_24TH,
        "25th": lcars_palette.LCARSEra.TITAN_CLASS_25TH,
        "29th": lcars_palette.LCARSEra.RELATIVITY_CLASS_29TH,
        "Default": lcars_palette.LCARSEra.TITAN_CLASS_25TH,
    }
    era = name_map.get(name)
    if era is None:
        # try lower/name matches
        for k in lcars_palette.ERA_THEMES.keys():
            if name.lower() in getattr(k, 'name', str(k)).lower():
                era = k
                break
    if era is None:
        return None
    return lcars_palette.ERA_THEMES.get(era)
