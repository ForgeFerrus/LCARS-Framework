from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class FactionEra(Enum):
    FEDERATION_ENTERPRISE = "federation_enterprise"
    FEDERATION_TOS = "federation_tos"
    FEDERATION_TNG = "federation_tng"
    KLINGON_TNG = "klingon_tng"
    ROMULAN_TNG = "romulan_tng"


@dataclass
class LCARSTheme:
    faction_era: FactionEra
    primary: str
    secondary: str
    background: str
    text: str
    accent: str
    warning: str
    success: str
    error: str
    button_normal: str
    button_hover: str
    button_active: str
    panel_bg: str
    border: str


class ThemeManager:
    def __init__(self):
        self.current_theme: Optional[LCARSTheme] = None
        self.themes: Dict[FactionEra, LCARSTheme] = {}
        self._init_default_themes()

    def _init_default_themes(self):
        self.themes[FactionEra.FEDERATION_TNG] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_TNG,
            primary="#3366CC",
            secondary="#00CCCC",
            background="#000033",
            text="#FFFFFF",
            accent="#FFCC99",
            warning="#FF9900",
            success="#99FF99",
            error="#FF6666",
            button_normal="#3366CC",
            button_hover="#6699FF",
            button_active="#00CCCC",
            panel_bg="#001A33",
            border="#3366CC",
        )
        self.themes[FactionEra.FEDERATION_TOS] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_TOS,
            primary="#CC0000",
            secondary="#FFD700",
            background="#000000",
            text="#FFFFFF",
            accent="#0066CC",
            warning="#CC0000",
            success="#009900",
            error="#CC0000",
            button_normal="#FFD700",
            button_hover="#FFCC33",
            button_active="#0066CC",
            panel_bg="#222222",
            border="#CC0000",
        )
        self.themes[FactionEra.KLINGON_TNG] = LCARSTheme(
            faction_era=FactionEra.KLINGON_TNG,
            primary="#CC3333",
            secondary="#FF6600",
            background="#1A0000",
            text="#FFFFFF",
            accent="#FFD700",
            warning="#FF6600",
            success="#FFD700",
            error="#990000",
            button_normal="#CC3333",
            button_hover="#FF6600",
            button_active="#FFD700",
            panel_bg="#330000",
            border="#CC3333",
        )
        self.themes[FactionEra.ROMULAN_TNG] = LCARSTheme(
            faction_era=FactionEra.ROMULAN_TNG,
            primary="#00AA66",
            secondary="#008844",
            background="#001A00",
            text="#FFFFFF",
            accent="#C0C0C0",
            warning="#00AA66",
            success="#00AA66",
            error="#CC3333",
            button_normal="#004422",
            button_hover="#00AA66",
            button_active="#008844",
            panel_bg="#002200",
            border="#00AA66",
        )
        self.themes[FactionEra.FEDERATION_ENTERPRISE] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_ENTERPRISE,
            primary="#CD7F32",
            secondary="#B87333",
            background="#000000",
            text="#FFFFFF",
            accent="#DAA520",
            warning="#B5A642",
            success="#DAA520",
            error="#CC0000",
            button_normal="#CD7F32",
            button_hover="#B87333",
            button_active="#DAA520",
            panel_bg="#111111",
            border="#CD7F32",
        )
        self.current_theme = self.themes[FactionEra.FEDERATION_TNG]

    def get_theme(self, faction_era: FactionEra) -> LCARSTheme:
        return self.themes.get(faction_era, self.current_theme)

    def set_current_theme(self, faction_era: FactionEra):
        theme = self.get_theme(faction_era)
        if theme is not None:
            self.current_theme = theme

    def get_current_theme(self) -> Optional[LCARSTheme]:
        return self.current_theme

    def get_css_stylesheet(self, theme: Optional[LCARSTheme] = None) -> str:
        if theme is None:
            theme = self.current_theme
        if theme is None:
            return ""
        return f"""
QWidget {{
    background-color: {theme.background};
    color: {theme.text};
    font-family: 'LCARS', 'Arial', sans-serif;
}}
QPushButton {{
    background-color: {theme.button_normal};
    color: {theme.text};
    border: 2px solid {theme.border};
    padding: 8px 16px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {theme.button_hover};
}}
QPushButton:pressed {{
    background-color: {theme.button_active};
}}
QLabel {{
    color: {theme.text};
    background-color: transparent;
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {theme.panel_bg};
    color: {theme.text};
    border: 2px solid {theme.border};
    padding: 6px;
}}
QFrame {{
    background-color: {theme.panel_bg};
    border: 2px solid {theme.border};
}}
"""


theme_manager = ThemeManager()


def get_theme_by_name(faction: str, era: str) -> LCARSTheme:
    faction_lower = faction.lower()
    era_lower = era.lower()
    if faction_lower == "federation" and era_lower in ("tng", "tng_24th"):
        return theme_manager.get_theme(FactionEra.FEDERATION_TNG)
    if faction_lower == "federation" and era_lower in ("tos", "tos_23rd"):
        return theme_manager.get_theme(FactionEra.FEDERATION_TOS)
    if faction_lower == "klingon" and era_lower in ("tng", "tng_24th"):
        return theme_manager.get_theme(FactionEra.KLINGON_TNG)
    if faction_lower == "romulan" and era_lower in ("tng", "tng_24th"):
        return theme_manager.get_theme(FactionEra.ROMULAN_TNG)
    if faction_lower == "federation" and era_lower in ("enterprise", "enterprise_22nd"):
        return theme_manager.get_theme(FactionEra.FEDERATION_ENTERPRISE)
    return theme_manager.get_theme(FactionEra.FEDERATION_TNG)


def set_current_theme(faction_era: FactionEra):
    theme_manager.set_current_theme(faction_era)


def get_current_theme() -> Optional[LCARSTheme]:
    return theme_manager.get_current_theme()


def get_css_stylesheet(theme: Optional[LCARSTheme] = None) -> str:
    return theme_manager.get_css_stylesheet(theme)
