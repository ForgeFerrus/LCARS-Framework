# Titanium Bridge Migration: from typing import Optional
from . import hotkeys  # just for import order
from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_theme
from lcars.system import hotkeys
from lcars.system.localization import LOCALIZATION as Language
from lcars.modules.config_manager import config_manager
from lcars.system.hotkeys import HotkeyManager


class ColorManager:
    """Centralized color algorithm based on current era, faction and alert level."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.era = LCARSEra.LCARS_25TH
        self.faction = None
        self.alert_level = 0
        self.index = 0
        self._update_theme()

    def _update_theme(self):
        theme = get_theme(self.era, self.faction)
        self.palette = theme.get('palette', [])
        self.alert_palette = theme.get('alerts', [])
        # reload custom colors from config
        cfg_colors = config_manager.get('ui','colors',{}) or {}
        self.alert_palette = [cfg_colors.get('alert_red', self.alert_palette[0] if self.alert_palette else '#CC0000')] if self.alert_palette else [cfg_colors.get('alert_red','#CC0000')]

    def set_context(self, era: Optional[LCARSEra]=None, faction=None):
        if era is not None:
            self.era = era
        if faction is not None:
            self.faction = faction
        self._update_theme()

    def next_color(self) -> str:
        """Return next color in current palette (accounts for alert)."""
        source = self.alert_palette if self.alert_level>0 else self.palette
        if not source:
            return '#888888'
        color = source[self.index % len(source)]
        self.index += 1
        return color

    def alert_color(self, level:int) -> str:
        self.alert_level = level
        self.index = 0
        return self.next_color()


# expose singleton
COLOR_MANAGER = ColorManager()
