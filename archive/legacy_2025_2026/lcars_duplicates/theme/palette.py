# ◤ TITANIUM CHROMATIC MATRIX — v44.20 🖖
# LCARS Framework :: COLOR_SYSTEM // PALETTE_REGISTRY // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Головний реєстр кольорових палітр LCARS Titanium Matrix.
# ФУНКЦІЇ: Мапування ер, фракцій та алертових станів (Standard v44.20).
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
import random

# БАЗОВІ КОНСТАНТИ TITANIUM
BackgroundHex = "#000000"
BACKGROUND = BackgroundHex

# ЕКЗЕМПЛЯР СТАБУ ДЛЯ ШРИФТІВ
def LcarsFontStyle(*ArgsSet, **KwargsSet):
    # Повертає стандартну конфігурацію шрифту Titanium v44.20.
    return {
        'family': 'LCARS',
        'size': 12,
        'weight': 'normal',
        'italic': False
    }

def get_lcars_font_style(size=12, weight='normal'):
    # Повертає CSS стиль для шрифту LCARS
    return f"font-family: 'LCARS'; font-size: {size}px; font-weight: {weight};"

# Легасі аліаси
GetLcarsFontStyle = LcarsFontStyle

# АЛІАСИ ДЛЯ ЗВОРОТНОЇ СУМІСНОСТІ (Legacy Aliases)
get_lcars_font_style_legacy = GetLcarsFontStyle


# ОПИС ЕР ТА ФРАКЦІЙ (TITANIUM REGISTRY KEYS)
class LCARSEra(Enum):
    COMS_22ND = "22nd"
    PCARS_23RD = "23rd"
    PCARS_23ST = "23st"
    LCARS_24TH = "24th"
    LCARS_24ST = "24st"
    LCARS_25TH = "25th"
    TCARS_29TH = "29th"

class FactionEra(Enum):
    Federation = "federation"
    Klingon = "klingon"
    Romulan = "romulan"
    Cardassian = "cardassian"
    Borg = "borg"
    Romulan_22ND = "romulan_22nd"
    Romulan_23RD = "romulan_23rd"
    Romulan_24TH = "romulan_24th"
    Klingon_23RD = "klingon_23rd"
    Klingon_25TH = "klingon_25th"
    Cardassian_25TH = "cardassian_25th"
    Cardassian_29TH = "cardassian_29th"

# ГЛОБАЛЬНІ МАТРИЦІ КОЛЬОРІВ (TITANIUM COLOR MAPS)
EraColorPalettesMap: Dict[LCARSEra, Dict[str, Any]] = {
    LCARSEra.COMS_22ND: {
        "PanelBorder": "#444444",
        "ButtonColors": ["#CCCCCC", "#999999", "#666666"],
        "AlertColors": ["#FFBB00", "#D80000"],
    },
    LCARSEra.PCARS_23RD: {
        "PanelBorder": "#D3A200",
        "ButtonColors": ["#FFFF00", "#FF9900", "#FF6600"],
        "AlertColors": ["#FFAE00", "#E60000"],
    },
    LCARSEra.PCARS_23ST: {
        "PanelBorder": "#0066FF",
        "ButtonColors": ["#0066FF", "#3399FF", "#99CCFF"],
        "AlertColors": ["#FFD900", "#CA2525"],
    },
    LCARSEra.LCARS_24TH: {
        "PanelBorder": "#2F3749",
        "ButtonColors": ["#FFCC66", "#FF9900", "#3399FF", "#664466"],
        "AlertColors": ["#F9CA00", "#A30E2A"],
    },
    LCARSEra.LCARS_24ST: {
        "PanelBorder": "#000088",
        "ButtonColors": ["#AA5533", "#5599FF", "#3366FF"],
        "AlertColors": ["#AA5533", "#EE9955"],
    },
    LCARSEra.LCARS_25TH: {
        "PanelBorder": "#2F3749",
        "ButtonColors": ["#4BBEBF", "#37A6D1", "#FF6753", "#FFBB00", "#9EA5BA"],
        "AlertColors": ["#E7442A", "#A80F00"],
    },
    LCARSEra.TCARS_29TH: {
        "PanelBorder": "#D19FAE",
        "ButtonColors": ["#31C9F4", "#72E2E4", "#24BEB2"],
        "AlertColors": ["#CC6633", "#CC0000"],
    },
}

FactionColorPalettesMap: Dict[FactionEra, Dict[str, Any]] = {
    FactionEra.Federation: EraColorPalettesMap[LCARSEra.LCARS_25TH],
    FactionEra.Klingon: {
        "PanelBorder": "#660000",
        "ButtonColors": ["#660000", "#A61A35", "#CA0000"],
        "AlertColors": ["#E96C29", "#CA0000"],
    },
    FactionEra.Romulan: {
        "PanelBorder": "#0E563E",
        "ButtonColors": ["#0E563E", "#007633", "#33B89E"],
        "AlertColors": ["#FA5876", "#E2497F"],
    },
    FactionEra.Cardassian_25TH: {
        "PanelBorder": "#AA4444",
        "ButtonColors": ["#AA4444", "#CC6666", "#FFAA44", "#4466AA"],
        "AlertColors": ["#FF6666", "#DD4444"],
    },
    FactionEra.Romulan_23RD: {
        "PanelBorder": "#3EDB58",
        "ButtonColors": ["#3EDB58", "#00B100", "#7CF92B", "#016EB4"],
        "AlertColors": ["#C0101D", "#C93300"],
    },
    FactionEra.Klingon_23RD: {
        "PanelBorder": "#880000",
        "ButtonColors": ["#880000", "#CC3333", "#FF6600", "#660000"],
        "AlertColors": ["#FF6600", "#CC0000"],
    },
}

# МЕТОДИ ОТРИМАННЯ ПАЛІТРИ (TITANIUM ACCESSORS)
def EraPalette(EraKey: LCARSEra) -> Dict[str, Any]:
    # Повертає кольорову палітру для вказаної ери Titanium.
    PaletteNode = EraColorPalettesMap.get(EraKey, EraColorPalettesMap[LCARSEra.LCARS_25TH]).copy()
    PaletteNode["Background"] = BackgroundHex
    PaletteNode["Accent"] = PaletteNode["ButtonColors"][0] if PaletteNode.get("ButtonColors") else "#FF9900"
    PaletteNode["Secondary"] = PaletteNode["ButtonColors"][1] if len(PaletteNode.get("ButtonColors", [])) > 1 else "#3399FF"
    return PaletteNode

def FactionPalette(FactionKey: FactionEra) -> Dict[str, Any]:
    # Повертає кольорову палітру для вказаної фракції Titanium.
    PaletteNode = FactionColorPalettesMap.get(FactionKey, {}).copy()
    if not PaletteNode:
        return EraPalette(LCARSEra.LCARS_25TH)
    PaletteNode["Background"] = BackgroundHex
    PaletteNode["Accent"] = PaletteNode["ButtonColors"][0] if PaletteNode.get("ButtonColors") else "#FF9900"
    return PaletteNode

def get_theme(EraKey: Optional[LCARSEra] = None, FactionKey: Optional[FactionEra] = None) -> Dict[str, Any]:
    # Уніфікований метод отримання теми Titanium Matrix (v44.20).
    if FactionKey: return FactionPalette(FactionKey)
    return EraPalette(EraKey or LCARSEra.LCARS_25TH)

# Легасі аліаси
GetEraPalette = EraPalette
GetFactionPalette = FactionPalette

def get_random_button_color(EraKey: Optional[LCARSEra] = None, FactionKey: Optional[FactionEra] = None) -> str:
    # Повертає випадковий преміальний колір із палітри Titanium.
    ThemeNode = get_theme(EraKey, FactionKey)
    ColorsArray = ThemeNode.get("ButtonColors", ["#FFFFFF"])
    return random.choice(ColorsArray)

def AlertColor(EraKey: Optional[LCARSEra] = None, AlertLevelInt: int = 1) -> str:
    # Повертає колір стану тривоги Titanium (Standard v44.20).
    ThemeNode = get_theme(EraKey)
    AlertsArray = ThemeNode.get("AlertColors", ["#FFBC00", "#D80000"])
    if AlertLevelInt <= 0: return "#00CC00" # System Nominal (Green)
    return AlertsArray[min(AlertLevelInt - 1, len(AlertsArray) - 1)]

# Легасі аліаси
GetAlertColor = AlertColor

# ДОДАТКОВІ КЛАСИ ДЛЯ ЗАВАНТАЖУВАЧА
class LCARSColorGenerator:
    def __init__(self, era=LCARSEra.LCARS_25TH):
        self.era = era
        self.palette = EraPalette(era)
        self.colors = self.palette.get("ButtonColors", ["#FF9900", "#3399FF", "#00CC99", "#FFCC33"])
        self.current_index = 0
    
    def get_color_at_index(self, index):
        return self.colors[index % len(self.colors)]
    
    def get_next_color(self):
        color = self.get_color_at_index(self.current_index)
        self.current_index += 1
        return color

def get_era_palette(era):
    return EraPalette(era)

def get_alert_color(era=None, level=1):
    return AlertColor(era, level)

# ЕКСПОРТ TITANIUM Matrix
__all__ = [
    "LCARSEra", "FactionEra", "EraPalette", "FactionPalette", 
    "get_random_button_color", "AlertColor", "BackgroundHex", "BACKGROUND", "get_theme", 
    "LcarsFontStyle", "get_lcars_font_style", "LCARSColorGenerator", 
    "get_era_palette", "get_alert_color"
]