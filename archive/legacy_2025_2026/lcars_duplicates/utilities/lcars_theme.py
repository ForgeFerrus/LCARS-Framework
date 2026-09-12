
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class FactionEra(Enum):
    """All faction and era combinations"""
    # Federation eras
    FEDERATION_22ND = "federation_22nd"
    FEDERATION_23RD = "federation_23rd"
    FEDERATION_24TH = "federation_24th"
    FEDERATION_25TH = "federation_25th"
    FEDERATION_29TH = "federation_29th"
    
    # Klingon eras
    KLINGON_22ND = "klingon_22nd"
    KLINGON_23RD = "klingon_23rd"
    KLINGON_24TH = "klingon_24th"
    KLINGON_DOMINION = "klingon_dominion"
    
    # Romulan eras
    ROMULAN_22ND = "romulan_22nd"
    ROMULAN_23RD = "romulan_23rd"
    ROMULAN_24TH = "romulan_24th"
    ROMULAN_DOMINION = "romulan_dominion"


class LCARSColor(Enum):
    """Canonical LCARS color palette from Star Trek interfaces"""
    
    # Base colors
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    
    # Federation LCARS Palette (from TNG/DS9/VOY)
    # Primary blues and teals
    FED_BLUE_1 = "#336699"      # Classic LCARS blue
    FED_BLUE_2 = "#6699CC"      # Medium blue
    FED_BLUE_3 = "#99CCFF"      # Light blue
    FED_CYAN_1 = "#1C3C55"      # Dark teal
    FED_CYAN_2 = "#2A7193"      # Medium teal
    FED_CYAN_3 = "#37A6D1"      # Light teal
    
    # Federation backgrounds
    FED_DARK_BG = "#0A0A12"     # Very dark blue-black
    FED_MEDIUM_BG = "#1A1A2E"   # Dark blue
    FED_LIGHT_BG = "#2F3749"    # Medium dark blue
    
    # Federation accent colors
    FED_GOLD = "#FFCC99"        # LCARS orange/gold
    FED_SALMON = "#FF9966"      # LCARS salmon
    FED_RED_ALERT = "#FF4444"   # Alert red
    FED_GREEN = "#99FF99"       # System green
    
    # Klingon Empire Palette
    # Primary reds and oranges
    KLINGON_RED_1 = "#CC3333"       # Primary red
    KLINGON_RED_2 = "#990000"       # Dark red
    KLINGON_RED_3 = "#FF6666"       # Light red
    KLINGON_ORANGE_1 = "#FF6600"    # Primary orange
    KLINGON_ORANGE_2 = "#CC4400"    # Dark orange
    KLINGON_ORANGE_3 = "#FF9933"    # Light orange
    
    # Klingon backgrounds
    KLINGON_DARK_BG = "#1A0000"     # Very dark red
    KLINGON_MEDIUM_BG = "#2E1A1A"   # Dark red-brown
    KLINGON_LIGHT_BG = "#4A2A2A"    # Medium dark red
    
    # Klingon accent colors
    KLINGON_GOLD = "#FFD700"        # Klingon gold
    KLINGON_BRONZE = "#CD7F32"      # Bronze accents
    KLINGON_CRIMSON = "#8B0000"     # Deep crimson
    
    # Romulan Star Empire Palette
    # Primary greens
    ROMULAN_GREEN_1 = "#33AA33"     # Primary green
    ROMULAN_GREEN_2 = "#006600"     # Dark green
    ROMULAN_GREEN_3 = "#66CC66"     # Light green
    ROMULAN_TEAL_1 = "#008844"      # Teal green
    ROMULAN_TEAL_2 = "#004422"      # Dark teal
    ROMULAN_TEAL_3 = "#00AA66"      # Light teal
    
    # Romulan backgrounds
    ROMULAN_DARK_BG = "#001A00"     # Very dark green
    ROMULAN_MEDIUM_BG = "#1A2E1A"   # Dark green
    ROMULAN_LIGHT_BG = "#2A4A2A"    # Medium dark green
    
    # Romulan accent colors
    ROMULAN_SILVER = "#C0C0C0"      # Silver accents
    ROMULAN_EMERALD = "#50C878"     # Emerald green
    ROMULAN_JADE = "#00A86B"        # Jade green
    
    # Era-specific colors
    # 22nd Century (Enterprise era) - Bronze/Copper tones
    ERA_22_BRONZE = "#CD7F32"
    ERA_22_COPPER = "#B87333"
    ERA_22_BRASS = "#B5A642"
    ERA_22_GOLD = "#DAA520"
    
    # 23rd Century (TOS era) - Classic bright colors
    ERA_23_RED = "#E7442A"          # TOS command red
    ERA_23_GOLD = "#FFD700"         # TOS operations gold
    ERA_23_BLUE = "#1C3C55"         # TOS science blue
    ERA_23_GREEN = "#228B22"        # TOS green
    
    # 24th Century (TNG/DS9/VOY era) - Modern LCARS
    ERA_24_ORANGE = "#FF9966"       # LCARS orange
    ERA_24_YELLOW = "#FFCC99"       # LCARS yellow
    ERA_24_BLUE = "#6699CC"         # LCARS blue
    ERA_24_RED = "#FF6666"          # LCARS red
    ERA_24_PURPLE = "#CC99FF"       # LCARS purple
    
    # 25th Century (Odyssey era) - Advanced colors


def get_faction_era_theme(faction_era: FactionEra) -> LCARSTheme:
    """Get theme for specific faction and era"""
    theme_colors = FACTION_ERA_THEMES[faction_era]
    
    return LCARSTheme(
        faction_era=faction_era,
        **theme_colors
    )


def get_theme_by_name(faction: str, era: str) -> LCARSTheme:
    """Get theme by faction and era names"""
    faction_era_key = f"{faction.lower()}_{era.lower()}"
    
    # Map common era names
    era_mapping = {
        "22nd": "22nd",
        "23rd": "23rd", 
        "24th": "24th",
        "25th": "25th",
        "29th": "29th",
        "dominion": "dominion",
        "enterprise": "22nd",
        "original": "23rd",
        "tos": "23rd",
        "tng": "24th",
        "ds9": "24th",
        "voyager": "24th",
        "future": "29th",
        "temporal": "29th"
    }