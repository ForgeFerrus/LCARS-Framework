# ◤ LCARS THEMES SYSTEM
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.themes.lcars_palette import LCARSEra, FactionEra, GetEraPalette
from lcars.service.bridge import Bridge

UniversalBackground = "#000000"

class ThemeAccess(LCARS):
    @staticmethod
    def GetTheme(Era: any = None, Faction: any = None) -> dict:
        TargetEra = Era if isinstance(Era, LCARSEra) else LCARSEra.LCARS_25TH
        Palette = GetEraPalette(TargetEra)
        BtnColors = Palette.get("button_colors", []) or ["#99CCFF", "#FF9900"]
        Acc = BtnColors[0]
        Sec = BtnColors[1] if len(BtnColors) > 1 else Acc
        Config = {
            "era": TargetEra,
            "faction": Faction,
            "bg": UniversalBackground,
            "text": "#FFFFFF",
            "accent": Acc,
            "secondary": Sec,
            "border": Palette.get("panel_border", "#444444"),
            "radius": Palette.get("border_radius", "2px"),
            "button": BtnColors,
            "alerts": Palette.get("alert_colors", ["#FFBB00", "#D80000"]),
        }
        Config["palette"] = Config["button"]
        return Config

    @staticmethod
    def GetFontStyle(Size: int = 14, Weight: str = "normal", Faction: str | None = None, Era: str | None = None, Lang: str | None = None) -> str:
        return f"font-size: {Size}px; font-weight: {Weight};"

    @staticmethod
    def GetLcarsScrollbarStyle(Color: str | None = None) -> str:
        C = Color or "#FF9900"
        return f"QScrollBar {{ border: none; background: #080808; width: 10px; }} QScrollBar::handle {{ background: {C}; }}"

    @staticmethod
    def StyleLcarsScrollArea(Widget: any, Color: str | None = None) -> None:
        if hasattr(Widget, "setStyleSheet"):
            Widget.setStyleSheet(ThemeAccess.GetLcarsScrollbarStyle(Color))

GetTheme = ThemeAccess.GetTheme
GetFontStyle = ThemeAccess.GetFontStyle
GetLcarsFontStyle = ThemeAccess.GetFontStyle
GetLcarsScrollbarStyle = ThemeAccess.GetLcarsScrollbarStyle
StyleLcarsScrollArea = ThemeAccess.StyleLcarsScrollArea
get_theme = GetTheme
get_lcars_font_style = GetLcarsFontStyle

__all__ = [
    "ThemeAccess",
    "GetTheme",
    "GetFontStyle",
    "GetLcarsFontStyle",
    "GetLcarsScrollbarStyle",
    "StyleLcarsScrollArea",
    "get_theme",
    "get_lcars_font_style",
]
