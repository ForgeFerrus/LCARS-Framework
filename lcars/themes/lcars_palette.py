"""
LCARS Color Palette System

# Концепція LCARS:
# - Кожна ера має НАБІР кольорів (палітру)
# - Кнопки вибирають кольори ВИПАДКОВО або ПРОГРАМОВАНО з цієї палітри
# - Кольори можуть змінюватися в часі (анімація/програмування)
"""
from enum import Enum
import random

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
UNIVERSAL_TEXT = '#FFFFFF'        # Завжди білий текст

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

# Функції для роботи з палітрою
def get_era_palette(era: LCARSEra) -> dict:
    """
    Отримати повну палітру для вказаної ери
    
    Дія:
    1. Приймає: LCARSEra.PCARS_22ND (або іншу еру)
    2. Пошук: Шукає в ERA_COLOR_PALETTES словнику
    3. Додає універсальні background та text
    4. Fallback: Якщо не знайдено → LCARS_24TH (безпечний дефолт)
    5. Повертає: {background, text, panel_border, button_colors[], alert_colors[]}
    
    Використання: palette = get_era_palette(LCARSEra.LCARS_25TH)
    """
    palette = ERA_COLOR_PALETTES.get(era, ERA_COLOR_PALETTES[LCARSEra.LCARS_24TH]).copy()
    # Додаємо універсальні кольори
    palette['background'] = UNIVERSAL_BACKGROUND
    palette['text'] = UNIVERSAL_TEXT
    return palette

def get_random_button_color(era: LCARSEra) -> str:
    """
    Випадковий колір кнопки з палітри ери
    
    Дія:
    1. Приймає: LCARSEra.LCARS_24TH
    2. Крок 1: get_era_palette(era) → отримує повну палітру
    3. Крок 2: random.choice() → випадковий колір з button_colors[]
    4. Повертає: '#E7442A' (один HEX колір)
    
    Використання: color = get_random_button_color(LCARSEra.LCARS_25TH)
    """
    palette = get_era_palette(era)
    return random.choice(palette['button_colors'])

def get_button_color_cycle(era: LCARSEra, index: int) -> str:
    """
    Отримати колір за індексом для циклічної анімації
    """
    palette = get_era_palette(era)
    colors = palette['button_colors']
    return colors[index % len(colors)]

def get_alert_color(era: LCARSEra, alert_level: int = 0) -> str:
    """
    Колір для alert/warning (безпечний вибір рівня)
    
    Дія:
    1. Приймає: era, alert_level=2 (критична помилка)
    2. Крок 1: get_era_palette(era) → повна палітра
    3. Крок 2: min(alert_level, len(alerts)-1) → безпечний індекс
    4. Повертає: '#CC0000' (червоний для критичного)
    
    Використання: color = get_alert_color(LCARSEra.LCARS_25TH, 1)
    """
    palette = get_era_palette(era)
    alerts = palette['alert_colors']
    return alerts[min(alert_level, len(alerts) - 1)]

def get_background_color() -> str:
    """Колір фону для всіх LCARS ер"""
    return UNIVERSAL_BACKGROUND

def get_text_color() -> str:
    """Колір тексту для всіх LCARS ер"""
    return UNIVERSAL_TEXT

def get_palette_by_name(name: str) -> dict:
    """
    # ПРОСТА функція - отримання палітри за текстовою назвою
    
    # Призначення:
    # - Для UI компонентів, які мають назви ер у текстовому форматі
    # - Для конфігураційних файлів, JSON, налаштувань
    
    # Дія:
    # 1. Приймає: "24th", "default", "unknown" (текст)
    # 2. Конвертує в нижній регістр → "24th"
    # 3. Шукає в name_to_era словнику → LCARSEra.LCARS_24TH
    # 4. Отримує палітру через get_era_palette()
    # 5. Повертає: стандартну палітру {background, text, panel_border, button_colors[], alert_colors[]}
    
    # Приклади використання:
    # palette = get_palette_by_name("24th")  # → TNG палітра
    # palette = get_palette_by_name("default")  # → LCARS_25TH
    # palette = get_palette_by_name("unknown")  # → fallback LCARS_25TH
    """
    try:
        name_lower = str(name).lower()  
    except Exception:
        name_lower = "default"
    
    # Словник відповідності текстових назв → LCARSEra
    name_to_era = {
        "default": LCARSEra.LCARS_25TH,
        "22nd": LCARSEra.COMS_22ND,
        "23rd": LCARSEra.PCARS_23RD,
        "23st": LCARSEra.PCARS_23ST,
        "24th": LCARSEra.LCARS_24TH,
        "24st": LCARSEra.LCARS_24ST,
        "25th": LCARSEra.LCARS_25TH,
        "29th": LCARSEra.TCARS_29TH,
    }
    # Отримуємо еру і повертаємо стандартну палітру
    era = name_to_era.get(name_lower, LCARSEra.LCARS_25TH)
    return get_era_palette(era)