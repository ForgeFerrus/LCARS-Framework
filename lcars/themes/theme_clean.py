"""
Theme management and background handling for LCARS Framework
"""
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from enum import Enum
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QPixmap, QColor

class FactionEra(Enum):
    """Faction and era enumeration for interfaces."""
    STARFLEET_22ND = "starfleet_22nd"
    STARFLEET_23RD = "starfleet_23rd"
    STARFLEET_23ST = "starfleet_23st"
    STARFLEET_24TH = "starfleet_24th"
    STARFLEET_25TH = "starfleet_25th"
    STARFLEET_29TH = "starfleet_29th"
    KLINGON_22ND = "klingon_22nd"
    KLINGON_23RD = "klingon_23rd"
    KLINGON_24TH = "klingon_24th"
    KLINGON_25TH = "klingon_25th"
    ROMULAN_22ND = "romulan_22nd"
    ROMULAN_23RD = "romulan_23rd"
    ROMULAN_23ST = "romulan_23st"
    ROMULAN_24TH = "romulan_24th"
    ROMULAN_25TH = "romulan_25th"
    ROMULAN_29TH = "romulan_29th"
    CARDASSIAN_22ND = "cardassian_22nd"
    CARDASSIAN_23RD = "cardassian_23rd"
    CARDASSIAN_24TH = "cardassian_24th"
    CARDASSIAN_25TH = "cardassian_25th"
    CARDASSIAN_29TH = "cardassian_29th"

class Theme: 
    @staticmethod
    def get_background_image(faction=None, era=None):
        """
        Get background image path based on faction and era
        Dynamic image selection system
        """
        base_path = "C:\\Users\\Forge\\MyProject\\LCARS-Framework\\resources"
        
        # Default images for different factions/eras
        image_map = {
            # Federation
            'federation': {
                '22nd': 'PCARS_22.png',
                '23rd': 'PCARS_22.png', 
                '24th': 'LCARS_24.png',
                '25th': 'LCARS_25.png',
                'default': 'PCARS_22.png'
            },
            # Klingon
            'klingon': {
                '22nd': 'Klingon_22.png',
                '23rd': 'Klingon_23.png',
                'default': 'PCARS_22.png'
            },
            # Romulan
            'romulan': {
                '22nd': 'COMS2.png',
                '23rd': 'COMS2.png',
                'default': 'COMS2.png'
            },
            # Cardassian
            'cardassian': {
                'default': 'COMS2.png'
            },
            # Default fallback
            'default': 'PCARS_22.png'
        }
        
        # Normalize inputs
        faction = faction.lower() if faction else 'default'
        era = era.lower() if era else None
        
        # Get image path
        if faction in image_map:
            if era and era in image_map[faction]:
                image_name = image_map[faction][era]
            else:
                image_name = image_map[faction].get('default', image_map['default'])
        else:
            image_name = image_map['default']
        
        # Construct full path
        image_path = os.path.join(base_path, image_name)
        
        # Check if file exists, fallback to default
        if not os.path.exists(image_path):
            image_path = os.path.join(base_path, image_map['default'])
        
        return image_path 

    @staticmethod
    def generate_faction_palette(faction, era=None):
        """
        Generate faction-specific palette using algorithms
        Returns palette in same format as lcars_palette.py
        """
        faction = faction.lower()
        era = era.lower() if era else None
        
        # Romulan with era variations
        if 'romulan' in faction:
            if era and '22' in era:
                # Romulan 22nd century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#336666',
                    'panel_color': '#339999',
                    'button_colors': [
                        '#336666', '#339999', '#336633', '#009166',
                        '#33B89E', '#86E3B2', '#4ADDFB', '#2EB2E4',
                        '#3599CD', '#1C8BAA', '#00A8B6', '#00CED5'
                    ],
                    'alert_colors': ['#72DEDE', '#FFC5B3']
                }
            elif era and '23rd' in era:
                # Romulan 23rd century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#3EDB58',
                    'panel_color': '#00B100',
                    'button_colors': [
                        '#3EDB58', '#00B100', '#7CF92B', '#99FF99',
                        '#F0E570', '#FFF708', '#C93300', '#C0101D',
                        '#016EB4', '#24A1E8'
                    ],
                    'alert_colors': ['#C0101D', '#C93300']
                }
            elif era and '23st' in era:
                # Romulan 23st century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#BAFF80',
                    'panel_color': '#7CDE2C',
                    'button_colors': [
                        '#BAFF80', '#7CDE2C', '#49B600', '#66CC00',
                        '#59E52E', '#00B100', '#009900', '#F89DB2',
                        '#72DEDE'
                    ],
                    'alert_colors': ['#72DEDE', '#F89DB2']
                }
            elif era and '24' in era:
                # Romulan 24th century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#0E563E',
                    'panel_color': '#007633',
                    'button_colors': [
                        '#0E563E', '#007633', '#408360', '#6CBD92',
                        '#068F3A', '#28B856', '#61DB86', '#72DEDE',
                        '#00C9C3', '#26D1E0', '#1E94A9', '#F89DB2'
                    ],
                    'alert_colors': ['#FA5876', '#E2497F']
                }
            elif era and '25' in era:
                # Romulan 25th century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#00523B',
                    'panel_color': '#2D513B',
                    'button_colors': [
                        '#00523B', '#2D513B', '#227D51', '#1D995D',
                        '#56A334', '#61DB86', '#8BFF9C', '#DAFBF1',
                        '#29E5B5', '#72DEDE', '#2ACCD3', '#9583BC'
                    ],
                    'alert_colors': ['#79547F', '#9583BC']
                }
            elif era and '29' in era:
                # Romulan 29th century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#0A1A1A',
                    'panel_color': '#006666',
                    'button_colors': [
                        '#0A1A1A', '#006666', '#1C7736', '#99CC99',
                        '#FFFF99', '#E0D060', '#BAB444', '#3399CC',
                        '#2CB1F7', '#999999', '#C2C1C2', '#F398C4'
                    ],
                    'alert_colors': ['#BB5A87', '#F398C4']
                }
        
        # Klingon with era variations
        elif 'klingon' in faction:
            if era and '22' in era:
                # Klingon 22nd century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#400000',
                    'panel_color': '#CC0000',
                    'button_colors': [
                        '#400000', '#CC0000', '#FF0000', '#FF3300',
                        '#EE6900', '#FF9900', '#A99706', '#95FF00',
                        '#A59797'
                    ],
                    'alert_colors': ['#95FF00', '#A99706']
                }
            elif era and '23' in era:
                # Klingon 23rd century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#CC0000',
                    'panel_color': '#FF0000',
                    'button_colors': [
                        '#CC0000', '#FF0000', '#FA362A', '#D73713',
                        '#E96C29', '#F39C35', '#F1BB2F', '#F6EE24',
                        '#F6F0B8', '#B9B170', '#5C8B49'
                    ],
                    'alert_colors': ['#5C8B49', '#B9B170']
                }
            elif era and '24' in era:
                # Klingon 24th century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#660000',
                    'panel_color': '#CA0000',
                    'button_colors': [
                        '#660000', '#980000', '#CA0000', '#D73713',
                        '#E7730E', '#FFCB66', '#F6EE24', '#F6F0B8',
                        '#C99600', '#CA6400'
                    ],
                    'alert_colors': ['#CA6400', '#C99600']
                }
            elif era and '25' in era:
                # Klingon 25th century palette
                return {
                    'background': '#000000',
                    'text': '#FFFFFF',
                    'panel_border': '#660000',
                    'panel_color': '#A61A35',
                    'button_colors': [
                        '#660000', '#A61A35', '#CA0000', '#05C6DE',
                        '#99F5F9', '#CDFC80', '#F0E075', '#DBBA78',
                        '#E68D5D', '#E96C29'
                    ],
                    'alert_colors': ['#E96C29', '#E68D5D']
                }
        
        # Cardassian with era variations
        elif 'cardassian' in faction:
            # All Cardassian eras use the same palette as you specified
            return {
                'background': '#000000',
                'text': '#FFFFFF',
                'panel_border': '#CC3300',
                'panel_color': '#FF3300',
                'button_colors': [
                    '#CC3300', '#FF3300', '#FF4400', '#003366',
                    '#004488', '#FF9900', '#00CC66', '#FFFFFF',
                    '#990000', '#66CCFF', '#FFAA00', '#DDDDDD',
                    '#00FF66', '#666666', '#333333', '#555555',
                    '#888888', '#330000', '#550000', '#770000'
                ],
                'alert_colors': ['#770000', '#550000']
            }
        
        # Fallback to Starfleet palette
        else:
            return {
                'background': '#000000',
                'text': '#FFFFFF',
                'panel_border': '#2F3749',
                'panel_color': '#52596E',
                'button_colors': [
                    '#2F3749', '#52596E', '#6D748C', '#9EA5BA',
                    '#E7442A', '#FF6753', '#FF977B', '#1C3C55',
                    '#2A7193', '#37A6D1', '#4BBEBF'
                ],
                'alert_colors': ['#E7442A', '#A80F00']
            }

    @staticmethod
    def get_faction_era_palette(faction_era):
        """
        Get palette for any FactionEra combination
        Returns palette in same format as lcars_palette.py
        """
        from lcars.themes.lcars_palette import ERA_COLOR_PALETTES, LCARSEra
        
        faction_era_str = faction_era.value
        
        # Extract faction and era
        if 'starfleet' in faction_era_str:
            faction = 'starfleet'
            if '22nd' in faction_era_str:
                lcars_era = LCARSEra.PCARS_22ND
            elif '23rd' in faction_era_str:
                lcars_era = LCARSEra.PCARS_23RD
            elif '23st' in faction_era_str:
                lcars_era = LCARSEra.PCARS_23ST
            elif '24th' in faction_era_str:
                lcars_era = LCARSEra.LCARS_24TH
            elif '25th' in faction_era_str:
                lcars_era = LCARSEra.LCARS_25TH
            elif '29th' in faction_era_str:
                lcars_era = LCARSEra.TCARS_29TH
            else:
                lcars_era = LCARSEra.LCARS_24TH
            
            return ERA_COLOR_PALETTES[lcars_era]
        
        else:
            # For non-Starfleet factions, use generate_faction_palette
            if 'klingon' in faction_era_str:
                faction = 'klingon'
            elif 'romulan' in faction_era_str:
                faction = 'romulan'
            elif 'cardassian' in faction_era_str:
                faction = 'cardassian'
            else:
                faction = 'starfleet'
            
            # Extract era from FactionEra value
            era = faction_era_str.split('_')[-1]  # Get last part after underscore
            
            return Theme.generate_faction_palette(faction, era)
