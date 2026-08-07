# LCARS Palette System — minimal restore
from enum import Enum

class LCARSEra(Enum):
    COMS_22ND = "22nd"
    PCARS_23RD = "23rd"
    PCARS_23ST = "23st"
    LCARS_24TH = "24th"
    LCARS_24ST = "24st"
    LCARS_25TH = "25th"
    TCARS_29TH = "29th"

class FactionEra(Enum):
    FEDERATION = "federation"
    KLINGON = "klingon"
    ROMULAN = "romulan"
    CARDASIAN = "cardasian"
    BORG = "borg"

def GetEraPalette(era: LCARSEra) -> dict:
    base = {
        'panel_border': '#444444',
        'panel_color': '#CCCCCC',
        'button_colors': ['#FFE600', '#269EEE', '#5C5C5C', '#27F8FF', '#018D76', '#FFBB00', '#00A35F', '#2062EE', '#CE6363', '#9EFFB5'],
        'alert_colors': ['#FFBB00', '#D80000'],
        'border_radius': '0px',
    }
    return base

def GetRandomButtonColor(era: LCARSEra = None) -> str:
    import random
    colors = GetEraPalette(era or LCARSEra.LCARS_25TH)['button_colors']
    return random.choice(colors)

def GetLcarsFontStyle(size: int, weight: str = "normal") -> str:
    return f"font-size: {size}px; font-weight: {weight};"

def GetFactionColors(faction: FactionEra) -> dict:
    return GetEraPalette(LCARSEra.LCARS_25TH)