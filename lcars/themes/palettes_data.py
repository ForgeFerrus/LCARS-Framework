# Палітри кольорів для LCARS
# Винесено з palette.py для розділення даних і функціоналу

# Titanium Bridge Migration: from enum import Enum

class LCARSEra(Enum):
    COMS_22ND = "22nd"
    PCARS_23RD = "23rd"
    PCARS_23ST = "23st"
    LCARS_24TH = "24th"
    LCARS_24ST = "24st"
    LCARS_25TH = "25th"
    TCARS_29TH = "29th"

class FactionEra(Enum):
    KLINGON = "klingon"
    ROMULAN = "romulan"
    CARDASSIAN = "cardassian"
    KLINGON_22ND = "klingon_22nd"
    ROMULAN_22ND = "romulan_22nd"
    CARDASSIAN_22ND = "cardassian_22nd"
    # ... (інші фракції та ери)

UNIVERSAL_BACKGROUND = "#000000"

ERA_COLOR_PALETTES = {
    LCARSEra.COMS_22ND: {
        "panel_border": "#444444",
        "panel_color": "#CCCCCC",
        "button_colors": [
            "#FFE600", "#269EEE", "#5C5C5C", "#27F8FF", "#018D76",
            "#FFBB00", "#00A35F", "#2062EE", "#CE6363", "#9EFFB5",
        ],
        "alert_colors": ["#FFBB00", "#CE6363", "#D80000"],
        "border_radius": "0px",
        "elbow_radius": "0px",
    },
    # ... (інші ери)
}

FACTION_COLOR_PALETTES = {
    FactionEra.KLINGON: {
        "panel_border": "#660000",
        "button_colors": ["#660000", "#980000", "#CA0000", "#D73713", "#E7730E"],
        "alert_colors": ["#CA6400", "#660000"],
    },
    # ... (інші фракції)
}
