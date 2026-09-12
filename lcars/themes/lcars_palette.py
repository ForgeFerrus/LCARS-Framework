
# Концепція LCARS:
# - Кожна ера має НАБІР кольорів (палітру)
# - Кнопки вибирають кольори ВИПАДКОВО або ПРОГРАМОВАНО з цієї палітри
# - Кольори можуть змінюватися в часі (анімація/програмування)
# - Є універсальні кольори (фон, текст), які залишаються сталими
# - Додаткові кольори для alert/warning, які виділяються в кожній ері
# - Стиль рамок і заокруглення також може змінюватися в залежності від ери 

# Titanium Bridge Migration: from enum import Enum
import random
from lcars.themes.theme import FactionEra

# LCARS Era definitions - 6 офіційних ер Starfleet
class LCARSEra(Enum):
    """LCARS Era definitions"""
    COMS_22ND = "22nd"  # Computer Operating System (Enterprise NX-01)
    PCARS_23RD = "23rd"  # Pre-LCARS (TOS Pre-Library Computer Access and Retrieval System)
    PCARS_23ST = "23st"  # Pre-LCARS (Pre-Library Computer Access and Retrieval System II-VI)
    LCARS_24TH = "24th"  # The Next Generation (TNG/DS9/VOY)
    LCARS_24ST = "24st"  # Sovereign era (Enterprise-E, First Contact)
    LCARS_25TH = "25th"  # Titan era (Star Trek Picard)
    TCARS_29TH = "29th"  # Future (Temporal Library Computer Access and Retrieval System)

# Універсальні кольори для всіх LCARS ер
UNIVERSAL_BACKGROUND = '#000000'  # Завжди чорний фон
UNIVERSAL_TEXT = '#9EA5BA'  # Стандартний текст
# LCARS Color Palettes - списки кольорів для кожної ери
# Кнопки вибирають з цих кольорів випадково або програмовано
ERA_COLOR_PALETTES = {
    LCARSEra.COMS_22ND: {
        'panel_border': '#444444',
        'panel_color': '#CCCCCC',
        # Набір кольорів для кнопок (вибираються випадково/програмовано)
        'button_colors': [
            '#FFE600', "#269EEE", '#5C5C5C', '#27F8FF', 
            '#018D76', '#FFBB00', '#00A35F',
            '#2062EE', '#CE6363', '#9EFFB5'
        ],
        # Спеціальні кольори для alert/warning
        'alert_colors': ['#FFBB00', '#D80000'],
        'border_radius': '0px'  # Компактний, функціональний стиль NX-01
    },
    
    LCARSEra.PCARS_23RD: {
        'panel_border': '#D3A200',
        'button_colors': [
            '#FFFF00', '#FF0000', '#00FF00', '#FA7B13',
            '#66FF66', '#FFAE00', '#E60000', '#003819',
            '#156B15', '#FFFF99'
        ],
        'alert_colors': ['#FFAE00', '#E60000'],
        'border_radius': '5px'  # Початок заокруглення (TOS)
    },
    
    LCARSEra.PCARS_23ST: {
        'panel_border': '#0066FF',
        'button_colors': [
            '#002FFF', '#006321', '#693FFF', '#3399FF',
            '#009933', '#FFD900', '#21D17F', '#99CCFF',
        ],
        'alert_colors': ['#FFD900', '#CA2525'],
        'border_radius': '10px' # Більш плавні лінії (Movie era)
    },
    
    LCARSEra.LCARS_24TH: {
        'panel_border': '#664466',
        'button_colors': [
            '#FFCC66', '#FF9900', '#9999FF', '#B1957A',
            '#EEC222', '#3399FF', '#CD6363', '#646DCC',
            '#99CCFF', '#FFFF9C'
        ],
        'alert_colors': ['#A30E2A', '#CD6363'],
        'border_radius': '15px' # Класичний LCARS (TNG)
    },
    
    LCARSEra.LCARS_24ST: {
        'panel_border': '#000088',     # Navy-blue рамка (Sovereign class)
        'button_colors': [
            '#AA5533', '#BB6622', '#EE9955', '#CCDDFF',  # medium-carmine, bourbon, sandy-brown, periwinkle
            '#5599FF', '#3366FF', '#0011EE', '#000088',  # dodger-pale, dodger-soft, near-blue, navy-blue
            '#BBAA55', '#BB4411', '#882211'             # husk, rust, tamarillo
        ],
        'alert_colors': ['#BB4411', '#882211'],  # rust, tamarillo (Enterprise-E)
        'border_radius': '18px' # Елегантний стиль (Enterprise-E)
    },
    
    LCARSEra.LCARS_25TH: {
        'panel_border': '#2F3749',
        'button_colors': [
            '#2F3749', '#52596E', '#6D748C', '#9EA5BA',
            '#E7442A', '#FF6753', '#FF977B', '#1C3C55',
            '#2A7193', '#37A6D1', '#4BBEBF'
        ],
        'alert_colors': ['#E7442A', '#A80F00'],
        'border_radius': '20px' # Сучасний LCARS (Picard era)
    },
    
    LCARSEra.TCARS_29TH: {
        'panel_border': '#D19FAE',
        'button_colors': [
            '#31C9F4', '#72E2E4', '#20788C', '#24BEB2',
            '#A656C5', '#D19FAE', '#99FFCC', '#CC6633',
            '#805070', '#2062EE', '#FFCC99'
        ],
        'alert_colors': ['#CC6633', '#CC0000'],
        'border_radius': '25px' # Футуристичний TCARS
    }
}
