"""UI components"""

# Import всіх  віджетів 
from .widgets import (
    LCARSButton,
    LCARSPanel,
    LCARSLabel,
    LCARSConsole,
)

# Import interfaces
from .PCARS_22nd import PCARS22ndCentury
from .PCARS_23rd import PCARS23rdCentury
from .LCARS_24th import LCARS24thCentury 
from .LCARS_25th import LCARS25thCentury
from .TCARS_29th import TCARS29thCentury
from .Klingon_system import KlingonInterface


# Add get_faction_era_theme to the exports
# from lcars.themes.lcars_theme import (
#     get_faction_era_theme, 
#     LCARSTheme, FactionEra, get_theme_by_name, get_lcars_stylesheet, 
#     get_faction_specific_stylesheet, get_title_stylesheet, get_era_specific_accent
# )   
__all__ = [
    # Widgets
    "LCARSButton",
    "LCARSPanel",
    "LCARSLabel",
    "LCARSConsole",
    "LCARSTheme",
    "FactionEra",
    
    # Interfaces
    "PCARS22ndCentury",
    "PCARS23rdCentury",
    "LCARS24thCentury",
    "LCARS25thCentury",
    "TCARS29thCentury",
    "KlingonInterface",
    # Theme functions
    "get_faction_era_theme",
    "get_theme_by_name",
    "get_lcars_stylesheet",
    "get_faction_specific_stylesheet",
    "get_title_stylesheet",
    "get_era_specific_accent",
]
