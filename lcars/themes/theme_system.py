#!/usr/bin/env python3
"""
LCARS Theme System
Повна система тем: епохи + фракції + дизайн
"""

# Titanium Bridge Migration: from dataclasses import dataclass
# Titanium Bridge Migration: from typing import Dict, List, Optional, Any
# Titanium Bridge Migration: from enum import Enum

from lcars.themes.lcars_palette import LCARSEra, ERA_COLOR_PALETTES


class Faction(Enum):
    """LCARS фракції"""
    STARFLEET = "starfleet"
    KLINGON = "klingon"
    ROMULAN = "romulan"
    BORG = "borg"
    CARDASSIAN = "cardassian"
    DOMINION = "dominion"


class DesignStyle(Enum):
    """Стилі дизайну LCARS"""
    MODERN = "modern"
    CLASSIC_TNG = "classic_tng"
    MINIMAL = "minimal"
    TACTICAL = "tactical"
    SCIENTIFIC = "scientific"


@dataclass
class ThemeColors:
    """Повна палітра кольорів теми"""
    # Основні кольори
    background: str
    text: str
    panel_border: str
    panel_color: str
    
    # Кольори для кнопок (набір)
    button_colors: List[str]
    
    # Спеціальні кольори
    alert_colors: List[str]
    success_color: str
    warning_color: str
    error_color: str
    
    # Додаткові кольори для дизайну
    accent_colors: List[str]
    border_colors: List[str]


class ThemeSystem:
    """Основна система тем LCARS"""
    
    def __init__(self):
        self.faction_modifications = self._init_faction_modifications()
        self.design_styles = self._init_design_styles()
    
    def _init_faction_modifications(self) -> Dict[Faction, Dict[str, Any]]:
        """Модифікації кольорів для кожної фракції"""
        return {
            Faction.STARFLEET: {
                # Базові LCARS кольори - без змін
                'modifications': {}
            },
            Faction.KLINGON: {
                'modifications': {
                    'background': '#1A0000',
                    'panel_color': '#330000',
                    'panel_border': '#8B0000',
                    'text': '#FFCCCC',
                    'button_colors': [
                        '#FF4500', '#FF0000', '#B22222', '#8B0000',
                        '#CD5C5C', '#DC143C', '#8B0000', '#A52A2A'
                    ],
                    'alert_colors': ['#FF0000', '#FFD700'],
                    'success_color': '#00FF00',
                    'warning_color': '#FFD700',
                    'error_color': '#FF0000',
                    'accent_colors': ['#FF6347', '#CD5C5C'],
                    'border_colors': ['#8B0000', '#A52A2A']
                }
            },
            Faction.ROMULAN: {
                'modifications': {
                    'background': '#000814',
                    'panel_color': '#001D3D',
                    'panel_border': '#003566',
                    'text': '#6699CC',
                    'button_colors': [
                        '#003566', '#001D3D', '#004080', '#002244',
                        '#336699', '#4A90E2', '#0066CC', '#0080FF'
                    ],
                    'alert_colors': ['#0066CC', '#00CCFF'],
                    'success_color': '#00FF00',
                    'warning_color': '#FFD700',
                    'error_color': '#0066CC',
                    'accent_colors': ['#4A90E2', '#6699CC'],
                    'border_colors': ['#003566', '#002244']
                }
            },
            Faction.BORG: {
                'modifications': {
                    'background': '#000000',
                    'panel_color': '#001100',
                    'panel_border': '#003300',
                    'text': '#00FF00',
                    'button_colors': [
                        '#00FF00', '#00CC00', '#009900', '#006600',
                        '#00FF00', '#33FF33', '#00CC00', '#00FF00'
                    ],
                    'alert_colors': ['#00FF00', '#FFFF00'],
                    'success_color': '#00FF00',
                    'warning_color': '#FFFF00',
                    'error_color': '#FF0000',
                    'accent_colors': ['#00FF00', '#33FF33'],
                    'border_colors': ['#003300', '#006600']
                }
            },
            Faction.CARDASSIAN: {
                'modifications': {
                    'background': '#1A0A00',
                    'panel_color': '#4B2F1A',
                    'panel_border': '#8B4513',
                    'text': '#D2691E',
                    'button_colors': [
                        '#8B4513', '#A0522D', '#CD853F', '#DEB887',
                        '#D2691E', '#BC8F8F', '#F4A460', '#DAA520'
                    ],
                    'alert_colors': ['#CD853F', '#FF8C00'],
                    'success_color': '#00FF00',
                    'warning_color': '#FFD700',
                    'error_color': '#FF4500',
                    'accent_colors': ['#CD853F', '#DEB887'],
                    'border_colors': ['#8B4513', '#A0522D']
                }
            },
            Faction.DOMINION: {
                'modifications': {
                    'background': '#0A0014',
                    'panel_color': '#2E0040',
                    'panel_border': '#4B0082',
                    'text': '#9370DB',
                    'button_colors': [
                        '#4B0082', '#6A0DAD', '#8A2BE2', '#9370DB',
                        '#9932CC', '#BA55D3', '#DDA0DD', '#EE82EE'
                    ],
                    'alert_colors': ['#8A2BE2', '#DDA0DD'],
                    'success_color': '#00FF00',
                    'warning_color': '#FFD700',
                    'error_color': '#FF1493',
                    'accent_colors': ['#9370DB', '#BA55D3'],
                    'border_colors': ['#4B0082', '#6A0DAD']
                }
            }
        }
    
    def _init_design_styles(self) -> Dict[DesignStyle, Dict[str, Any]]:
        """Стилі дизайну для кожної теми"""
        return {
            DesignStyle.MODERN: {
                'description': 'Сучасний LCARS з круглими кутами',
                'button_style': {
                    'border_radius': '8px',
                    'padding': '15px 25px',
                    'font_size': '14px',
                    'font_weight': 'bold'
                },
                'layout_spacing': 15,
                'panel_style': {
                    'border_radius': '6px',
                    'border_width': '2px'
                }
            },
            DesignStyle.CLASSIC_TNG: {
                'description': 'Класичний стиль TNG з гострими кутами',
                'button_style': {
                    'border_radius': '4px',
                    'padding': '12px 20px',
                    'font_size': '14px',
                    'font_weight': 'bold'
                },
                'layout_spacing': 10,
                'panel_style': {
                    'border_radius': '2px',
                    'border_width': '1px'
                }
            },
            DesignStyle.MINIMAL: {
                'description': 'Мінімальний дизайн з прозорими елементами',
                'button_style': {
                    'border_radius': '20px',
                    'padding': '12px 30px',
                    'font_size': '16px',
                    'font_weight': '300'
                },
                'layout_spacing': 20,
                'panel_style': {
                    'border_radius': '12px',
                    'border_width': '1px'
                }
            },
            DesignStyle.TACTICAL: {
                'description': 'Тактичний червоний дизайн',
                'button_style': {
                    'border_radius': '6px',
                    'padding': '15px 20px',
                    'font_size': '14px',
                    'font_weight': 'bold'
                },
                'layout_spacing': 10,
                'panel_style': {
                    'border_radius': '6px',
                    'border_width': '2px'
                }
            },
            DesignStyle.SCIENTIFIC: {
                'description': 'Науковий синій дизайн',
                'button_style': {
                    'border_radius': '6px',
                    'padding': '12px 20px',
                    'font_size': '14px',
                    'font_weight': 'bold'
                },
                'layout_spacing': 10,
                'panel_style': {
                    'border_radius': '6px',
                    'border_width': '2px'
                }
            }
        }
    
    def get_theme(self, era: LCARSEra, faction: Faction, design: DesignStyle) -> ThemeColors:
        """Отримати повну тему для епохи + фракції + дизайну"""
        # Базова палітра епохи
        base_palette = ERA_COLOR_PALETTES[era]
        
        # Модифікації фракції
        faction_mods = self.faction_modifications[faction]['modifications']
        
        # Застосувати модифікації фракції
        final_colors = {}
        for key, default_value in base_palette.items():
            final_colors[key] = faction_mods.get(key, default_value)
        
        # Додати відсутні кольори з дефолтними значеннями
        final_colors.update({
            'success_color': faction_mods.get('success_color', '#00FF00'),
            'warning_color': faction_mods.get('warning_color', '#FFD700'),
            'error_color': faction_mods.get('error_color', '#FF0000'),
            'accent_colors': faction_mods.get('accent_colors', final_colors.get('button_colors', [])[:2]),
            'border_colors': faction_mods.get('border_colors', [final_colors.get('panel_border', '#666666')])
        })
        
        # Ensure all required fields exist
        if 'panel_color' not in final_colors:
            final_colors['panel_color'] = final_colors.get('background', '#000000')
        if 'panel_border' not in final_colors:
            final_colors['panel_border'] = final_colors.get('text', '#FFFFFF')
        if 'background' not in final_colors:
            final_colors['background'] = '#000000'
        if 'text' not in final_colors:
            final_colors['text'] = '#FFFFFF'
        if 'button_colors' not in final_colors:
            final_colors['button_colors'] = ['#FFCC66', '#FF9900']
        if 'alert_colors' not in final_colors:
            final_colors['alert_colors'] = ['#FFD700', '#FF0000']
        
        return ThemeColors(**final_colors)
    
    def get_design_style(self, design: DesignStyle) -> Dict[str, Any]:
        """Отримати стиль дизайну"""
        return self.design_styles[design]
    
    def list_available_themes(self) -> Dict[str, List[str]]:
        """Список доступних тем"""
        return {
            'eras': [era.value for era in LCARSEra],
            'factions': [faction.value for faction in Faction],
            'designs': [design.value for design in DesignStyle]
        }


# Глобальна система тем
theme_system = ThemeSystem()


def get_theme(era_name: str, faction_name: str, design_name: str) -> Optional[ThemeColors]:
    """Отримати тему за назвами"""
    if True:
        era = LCARSEra(era_name)
        faction = Faction(faction_name)
        design = DesignStyle(design_name)
        return theme_system.get_theme(era, faction, design)
    if False: # Removed except block
        return None


def get_design_style(design_name: str) -> Optional[Dict[str, Any]]:
    """Отримати стиль дизайну за назвою"""
    if True:
        design = DesignStyle(design_name)
        return theme_system.get_design_style(design)
    if False: # Removed except block
        return None


def list_themes() -> Dict[str, List[str]]:
    """Список всіх доступних тем"""
    return theme_system.list_available_themes()
