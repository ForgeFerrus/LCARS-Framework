# LCARS Framework :: Theme System v1.0.0
# Система тем LCARS з канонічними кольорами Star Trek
# Автор: LCARS Development Team
# Ліцензія: MIT

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional, List
from pathlib import Path
import json
from lcars.base.version import getVersion

version = getVersion()
# print(f"LCARS Theme System v{version}")  # Вимкнено для UI


class Faction(Enum):
    # Фракції Star Trek
    FEDERATION = "federation"
    KLINGON = "klingon"
    ROMULAN = "romulan"
    CARDASSIAN = "cardassian"
    DOMINION = "dominion"


class Era(Enum):
    # Епохи Star Trek
    ENTERPRISE_22ND = "enterprise_22nd"      # Enterprise (2151-2161)
    TOS_23RD = "tos_23rd"                    # The Original Series (2265-2269)
    TNG_24TH = "tng_24th"                    # The Next Generation (2364-2370)
    DS9_24TH = "ds9_24th"                    # Deep Space Nine (2369-2375)
    VOYAGER_24TH = "voyager_24th"            # Voyager (2371-2378)
    PICARD_25TH = "picard_25th"              # Picard (2399-2400)


class FactionEra(Enum):
    # Комбінації фракцій та епох
    FEDERATION_ENTERPRISE_22ND = "federation_enterprise_22nd"
    FEDERATION_TOS_23RD = "federation_tos_23rd"
    FEDERATION_TNG_24TH = "federation_tng_24th"
    FEDERATION_DS9_24TH = "federation_ds9_24th"
    FEDERATION_VOYAGER_24TH = "federation_voyager_24th"
    FEDERATION_PICARD_25TH = "federation_picard_25th"
    
    KLINGON_ENTERPRISE_22ND = "klingon_enterprise_22nd"
    KLINGON_TOS_23RD = "klingon_tos_23rd"
    KLINGON_TNG_24TH = "klingon_tng_24th"
    KLINGON_DS9_24TH = "klingon_ds9_24th"
    
    ROMULAN_ENTERPRISE_22ND = "romulan_enterprise_22nd"
    ROMULAN_TOS_23RD = "romulan_tos_23rd"
    ROMULAN_TNG_24TH = "romulan_tng_24th"
    ROMULAN_DS9_24TH = "romulan_ds9_24th"


class LCARSColor(Enum):
    # Канонічна палітра LCARS з реальних Star Trek інтерфейсів
    
    # Базові кольори
    BLACK = "#000000"
    WHITE = "#FFFFFF"
    GRAY = "#CCCCCC"
    
    # Federation LCARS (TNG/DS9/VOY) - реальні кольори з шоу
    # Основні сині та блакитні
    LCARS_BLUE = "#3366CC"           # Реальний LCARS синій
    LCARS_LIGHT_BLUE = "#6699FF"      # Світлий синій
    LCARS_DARK_BLUE = "#1A3366"       # Темний синій
    LCARS_CYAN = "#00CCCC"            # Блакитний
    LCARS_TEAL = "#009999"           # Бірюзовий
    
    # Фонові кольори Federation
    FED_DARK_BG = "#000033"         # Темно-синій фон
    FED_MEDIUM_BG = "#001A33"        # Середній фон
    FED_LIGHT_BG = "#003366"         # Світлий фон
    
    # Акцентні кольори Federation
    LCARS_ORANGE = "#FF9966"         # LCARS помаранчевий
    LCARS_GOLD = "#FFCC99"            # LCARS золотий
    LCARS_YELLOW = "#FFFF99"           # LCARS жовтий
    LCARS_RED_ALERT = "#FF6666"        # Тривога червоний
    LCARS_GREEN = "#99FF99"           # Системний зелений
    
    # Klingon Empire - реальні кольори з шоу
    KLINGON_RED = "#CC3333"           # Клінгонський червоний
    KLINGON_DARK_RED = "#990000"      # Темний червоний
    KLINGON_ORANGE = "#FF6600"        # Клінгонський помаранчевий
    KLINGON_BROWN = "#993300"         # Коричневий
    KLINGON_GOLD = "#FFD700"           # Клінгонське золото
    
    # Klingon фонові кольори
    KLINGON_DARK_BG = "#1A0000"         # Темно-червоний фон
    KLINGON_MEDIUM_BG = "#330000"        # Середній фон
    KLINGON_LIGHT_BG = "#4D0000"         # Світлий фон
    
    # Romulan Star Empire - реальні кольори з шоу  
    ROMULAN_GREEN = "#00AA66"         # Ромуланський зелений
    ROMULAN_DARK_GREEN = "#004422"    # Темний зелений
    ROMULAN_TEAL = "#008844"          # Ромуланський бірюзовий
    ROMULAN_SILVER = "#C0C0C0"        # Ромуланське срібло
    ROMULAN_JADE = "#00AA66"          # Нефритовий
    
    # Romulan фонові кольори
    ROMULAN_DARK_BG = "#001A00"         # Темно-зелений фон
    ROMULAN_MEDIUM_BG = "#002200"        # Середній фон
    ROMULAN_LIGHT_BG = "#003300"         # Світлий фон
    
    # Епохові кольори
    # 22nd Century (Enterprise era)
    ERA_22_BRONZE = "#CD7F32"       # Бронза
    ERA_22_COPPER = "#B87333"        # Мідь
    ERA_22_BRASS = "#B5A642"         # Латунь
    ERA_22_GOLD = "#DAA520"          # Золото
    
    # 23rd Century (TOS era)
    ERA_23_RED = "#CC0000"            # TOS червоний
    ERA_23_GOLD = "#FFD700"           # TOS золотий
    ERA_23_BLUE = "#0066CC"           # TOS синій
    ERA_23_GREEN = "#009900"          # TOS зелений
    
    # 24th Century (TNG/DS9/VOY era)
    ERA_24_BLUE = "#6699FF"           # TNG синій
    ERA_24_ORANGE = "#FF9900"         # TNG помаранчевий
    ERA_24_YELLOW = "#FFCC00"         # TNG жовтий
    ERA_24_RED = "#FF0000"            # TNG червоний
    ERA_24_PURPLE = "#CC66FF"         # TNG фіолетовий
    
    # 25th Century (Picard era)
    ERA_25_CYAN = "#00FFFF"           # Picard блакитний
    ERA_25_MAGENTA = "#FF00FF"         # Picard пурпурний
    ERA_25_WHITE = "#FFFFFF"           # Picard білий


@dataclass
class LCARSTheme:
    # Повна тема LCARS
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
    gradient_start: str
    gradient_end: str


class ThemeManager:
    # Менеджер тем LCARS
    
    def __init__(self):
        self.custom_themes: Dict[str, LCARSTheme] = {}
        self.current_theme: Optional[LCARSTheme] = None
        self.theme_file = Path.home() / '.lcars_themes.json'
        self._init_default_themes()
        self._load_custom_themes()
    
    def _init_default_themes(self):
        # Автоматичне створення тем з палітри
        self.default_themes = {}
        
        # Federation теми
        self._create_federation_themes()
        
        # Klingon теми
        self._create_klingon_themes()
        
        # Romulan теми
        self._create_romulan_themes()
    
    def _create_federation_themes(self):
        # Створити Federation теми з палітри
        
        # TNG 24th
        self.default_themes[FactionEra.FEDERATION_TNG_24TH] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_TNG_24TH,
            primary=LCARSColor.LCARS_BLUE.value,
            secondary=LCARSColor.LCARS_CYAN.value,
            background=LCARSColor.FED_DARK_BG.value,
            text=LCARSColor.WHITE.value,
            accent=LCARSColor.LCARS_GOLD.value,
            warning=LCARSColor.LCARS_ORANGE.value,
            success=LCARSColor.LCARS_GREEN.value,
            error=LCARSColor.LCARS_RED_ALERT.value,
            button_normal=LCARSColor.LCARS_DARK_BLUE.value,
            button_hover=LCARSColor.LCARS_LIGHT_BLUE.value,
            button_active=LCARSColor.LCARS_CYAN.value,
            panel_bg=LCARSColor.FED_MEDIUM_BG.value,
            border=LCARSColor.LCARS_BLUE.value,
            gradient_start=LCARSColor.FED_DARK_BG.value,
            gradient_end=LCARSColor.FED_LIGHT_BG.value
        )
        
        # TOS 23rd
        self.default_themes[FactionEra.FEDERATION_TOS_23RD] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_TOS_23RD,
            primary=LCARSColor.ERA_23_RED.value,
            secondary=LCARSColor.ERA_23_GOLD.value,
            background=LCARSColor.BLACK.value,
            text=LCARSColor.WHITE.value,
            accent=LCARSColor.ERA_23_BLUE.value,
            warning=LCARSColor.ERA_23_RED.value,
            success=LCARSColor.ERA_23_GREEN.value,
            error=LCARSColor.ERA_23_RED.value,
            button_normal=LCARSColor.ERA_23_GOLD.value,
            button_hover=LCARSColor.LCARS_GOLD.value,
            button_active=LCARSColor.ERA_23_BLUE.value,
            panel_bg=LCARSColor.ERA_23_BLUE.value,
            border=LCARSColor.ERA_23_RED.value,
            gradient_start=LCARSColor.BLACK.value,
            gradient_end=LCARSColor.ERA_23_BLUE.value
        )
        
        # Enterprise 22nd
        self.default_themes[FactionEra.FEDERATION_ENTERPRISE_22ND] = LCARSTheme(
            faction_era=FactionEra.FEDERATION_ENTERPRISE_22ND,
            primary=LCARSColor.ERA_22_BRONZE.value,
            secondary=LCARSColor.ERA_22_COPPER.value,
            background=LCARSColor.BLACK.value,
            text=LCARSColor.WHITE.value,
            accent=LCARSColor.ERA_22_GOLD.value,
            warning=LCARSColor.ERA_22_BRASS.value,
            success=LCARSColor.ERA_22_GOLD.value,
            error=LCARSColor.ERA_23_RED.value,
            button_normal=LCARSColor.ERA_22_BRONZE.value,
            button_hover=LCARSColor.ERA_22_COPPER.value,
            button_active=LCARSColor.ERA_22_GOLD.value,
            panel_bg=LCARSColor.ERA_22_BRASS.value,
            border=LCARSColor.ERA_22_BRONZE.value,
            gradient_start=LCARSColor.BLACK.value,
            gradient_end=LCARSColor.ERA_22_COPPER.value
        )
    
    def _create_klingon_themes(self):
        # Створити Klingon теми з палітри
        
        self.default_themes[FactionEra.KLINGON_TNG_24TH] = LCARSTheme(
            faction_era=FactionEra.KLINGON_TNG_24TH,
            primary=LCARSColor.KLINGON_RED.value,
            secondary=LCARSColor.KLINGON_ORANGE.value,
            background=LCARSColor.KLINGON_DARK_BG.value,
            text=LCARSColor.WHITE.value,
            accent=LCARSColor.KLINGON_GOLD.value,
            warning=LCARSColor.KLINGON_ORANGE.value,
            success=LCARSColor.KLINGON_GOLD.value,
            error=LCARSColor.KLINGON_DARK_RED.value,
            button_normal=LCARSColor.KLINGON_RED.value,
            button_hover=LCARSColor.KLINGON_ORANGE.value,
            button_active=LCARSColor.KLINGON_GOLD.value,
            panel_bg=LCARSColor.KLINGON_MEDIUM_BG.value,
            border=LCARSColor.KLINGON_RED.value,
            gradient_start=LCARSColor.KLINGON_DARK_BG.value,
            gradient_end=LCARSColor.KLINGON_LIGHT_BG.value
        )
    
    def _create_romulan_themes(self):
        # Створити Romulan теми з палітри
        
        self.default_themes[FactionEra.ROMULAN_TNG_24TH] = LCARSTheme(
            faction_era=FactionEra.ROMULAN_TNG_24TH,
            primary=LCARSColor.ROMULAN_GREEN.value,
            secondary=LCARSColor.ROMULAN_TEAL.value,
            background=LCARSColor.ROMULAN_DARK_BG.value,
            text=LCARSColor.WHITE.value,
            accent=LCARSColor.ROMULAN_SILVER.value,
            warning=LCARSColor.ROMULAN_JADE.value,
            success=LCARSColor.ROMULAN_GREEN.value,
            error=LCARSColor.KLINGON_RED.value,
            button_normal=LCARSColor.ROMULAN_DARK_GREEN.value,
            button_hover=LCARSColor.ROMULAN_GREEN.value,
            button_active=LCARSColor.ROMULAN_TEAL.value,
            panel_bg=LCARSColor.ROMULAN_MEDIUM_BG.value,
            border=LCARSColor.ROMULAN_GREEN.value,
            gradient_start=LCARSColor.ROMULAN_DARK_BG.value,
            gradient_end=LCARSColor.ROMULAN_LIGHT_BG.value
        )
    
    def get_theme(self, faction_era: FactionEra) -> LCARSTheme:
        # Отримати тему
        return self.default_themes.get(faction_era, self.default_themes[FactionEra.FEDERATION_TNG_24TH])
    
    def set_current_theme(self, faction_era: FactionEra):
        # Встановити поточну тему
        self.current_theme = self.get_theme(faction_era)
    
    def get_current_theme(self) -> Optional[LCARSTheme]:
        # Отримати поточну тему
        return self.current_theme
    
    def add_custom_theme(self, name: str, theme: LCARSTheme):
        # Додати власну тему
        self.custom_themes[name] = theme
        self._save_custom_themes()
    
    def get_custom_theme(self, name: str) -> Optional[LCARSTheme]:
        # Отримати власну тему
        return self.custom_themes.get(name)
    
    def list_themes(self) -> List[str]:
        # Список всіх доступних тем
        return list(self.default_themes.keys()) + list(self.custom_themes.keys())
    
    def get_css_stylesheet(self, theme: LCARSTheme) -> str:
        # Згенерувати CSS стилі для теми
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
        
        QLineEdit {{
            background-color: {theme.panel_bg};
            color: {theme.text};
            border: 2px solid {theme.border};
            padding: 5px;
        }}
        
        QFrame {{
            background-color: {theme.panel_bg};
            border: 2px solid {theme.border};
        }}
        """
    
    def _load_custom_themes(self):
        # Завантажити власні теми
        if self.theme_file.exists():
            with open(self.theme_file, 'r') as f:
                data = json.load(f)
                for name, theme_data in data.items():
                    theme = LCARSTheme(**theme_data)
                    self.custom_themes[name] = theme
    
    def _save_custom_themes(self):
        # Зберегти власні теми
        data = {}
        for name, theme in self.custom_themes.items():
            data[name] = {
                'faction_era': theme.faction_era.value,
                'primary': theme.primary,
                'secondary': theme.secondary,
                'background': theme.background,
                'text': theme.text,
                'accent': theme.accent,
                'warning': theme.warning,
                'success': theme.success,
                'error': theme.error,
                'button_normal': theme.button_normal,
                'button_hover': theme.button_hover,
                'button_active': theme.button_active,
                'panel_bg': theme.panel_bg,
                'border': theme.border,
                'gradient_start': theme.gradient_start,
                'gradient_end': theme.gradient_end
            }
        
        with open(self.theme_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_theme_from_colors(self, name: str, faction_era: FactionEra, colors: Dict[str, str]) -> LCARSTheme:
        # Створити тему з кольорів
        
        theme = LCARSTheme(
            faction_era=faction_era,
            primary=colors.get('primary', '#000000'),
            secondary=colors.get('secondary', '#000000'),
            background=colors.get('background', '#000000'),
            text=colors.get('text', '#FFFFFF'),
            accent=colors.get('accent', '#FFFFFF'),
            warning=colors.get('warning', '#FF0000'),
            success=colors.get('success', '#00FF00'),
            error=colors.get('error', '#FF0000'),
            button_normal=colors.get('button_normal', '#000000'),
            button_hover=colors.get('button_hover', '#000000'),
            button_active=colors.get('button_active', '#000000'),
            panel_bg=colors.get('panel_bg', '#000000'),
            border=colors.get('border', '#FFFFFF'),
            gradient_start=colors.get('gradient_start', '#000000'),
            gradient_end=colors.get('gradient_end', '#000000')
        )
        
        self.add_custom_theme(name, theme)
        return theme
    
    def export_theme(self, theme: LCARSTheme, filepath: str):
        # Експортувати тему
        theme_data = {
            'faction_era': theme.faction_era.value,
            'primary': theme.primary,
            'secondary': theme.secondary,
            'background': theme.background,
            'text': theme.text,
            'accent': theme.accent,
            'warning': theme.warning,
            'success': theme.success,
            'error': theme.error,
            'button_normal': theme.button_normal,
            'button_hover': theme.button_hover,
            'button_active': theme.button_active,
            'panel_bg': theme.panel_bg,
            'border': theme.border,
            'gradient_start': theme.gradient_start,
            'gradient_end': theme.gradient_end
        }
        
        with open(filepath, 'w') as f:
            json.dump(theme_data, f, indent=2)
    
    def import_theme(self, filepath: str, name: str) -> LCARSTheme:
        # Імпортувати тему
        with open(filepath, 'r') as f:
            theme_data = json.load(f)
        
        theme = LCARSTheme(**theme_data)
        self.add_custom_theme(name, theme)
        return theme


# Глобальний менеджер тем
theme_manager = ThemeManager()

# Швидкі функції
def get_faction_era_theme(faction_era: FactionEra) -> LCARSTheme:
    return theme_manager.get_theme(faction_era)

def get_theme_by_name(faction: str, era: str) -> LCARSTheme:
    # Отримати тему за назвами фракцій та епох
    faction_mapping = {
        'federation': 'FEDERATION',
        'klingon': 'KLINGON',
        'romulan': 'ROMULAN'
    }
    
    era_mapping = {
        'enterprise': 'ENTERPRISE_22ND',
        'tos': 'TOS_23RD',
        'tng': 'TNG_24TH',
        'ds9': 'DS9_24TH',
        'voyager': 'VOYAGER_24TH',
        'picard': 'PICARD_25TH'
    }
    
    faction_key = faction_mapping.get(faction.lower(), 'FEDERATION')
    era_key = era_mapping.get(era.lower(), 'TNG_24TH')
    
    faction_era = FactionEra[f"{faction_key}_{era_key}"]
    return theme_manager.get_theme(faction_era)

def set_current_theme(faction_era: FactionEra):
    theme_manager.set_current_theme(faction_era)

def get_current_theme() -> Optional[LCARSTheme]:
    return theme_manager.get_current_theme()

def get_css_stylesheet(theme: Optional[LCARSTheme] = None) -> str:
    if theme is None:
        theme = theme_manager.get_current_theme()
    
    if theme is None:
        return ""
    
    return theme_manager.get_css_stylesheet(theme)

def create_custom_theme(name: str, faction_era: FactionEra, colors: Dict[str, str]) -> LCARSTheme:
    return theme_manager.create_theme_from_colors(name, faction_era, colors)
