"""
# Theme management and background handling for LCARS Framework
# Фракційні палітри та універсальні функції для всіх комбінацій
"""
import os
from enum import Enum
from PyQt6.QtWidgets import QPushButton, QFrame
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPolygon, QColor, QBrush, QPen, QPainterPath

# FactionEra Enum - всі комбінації фракцій та ер для універсального доступу
class FactionEra(Enum):
    """
    # УНІВЕРСАЛЬНА система фракцій та ер Star Trek
    
    # Призначення:
    # - Єдиний доступ до всіх палітр (Starfleet + інші фракції)
    # - UI компоненти використовують цей enum для вибору теми
    # - Theme.get_faction_era_palette() маршрутизує запити
    
    # Структура назв:
    # - STARFLEET_ERA = "era" (тільки для Starfleet)
    # - FACTION_ERA = "faction_era" (для інших фракцій)
    
    # Приклади використання:
    # - FactionEra.STARFLEET_24TH → TNG палітра
    # - FactionEra.KLINGON_24TH → Klingon TNG палітра
    # - FactionEra.ROMULAN_24TH → Romulan TNG палітра
    """   
    # Starfleet ери (7 варіантів) - офіційні LCARS палітри
    STARFLEET_22ND = "22nd"      # Enterprise NX-01 era
    STARFLEET_23RD = "23rd"      # TOS era (Kirk)
    STARFLEET_23ST = "23st"      # TMP era (Motion Pictures)
    STARFLEET_24TH = "24th"      # TNG/DS9/VOY era
    STARFLEET_24ST = "24st"      # Sovereign era (Enterprise-E)
    STARFLEET_25TH = "25th"      # Picard era
    STARFLEET_29TH = "29th"      # Future era (TCARS)
    
    # Klingon ери (4 варіанти) - алгоритмічна генерація палітр
    KLINGON_22ND = "klingon_22nd"      # Рання Клінгонська імперія (до TOS)
    KLINGON_23RD = "klingon_23rd"      # TOS ера Клінгонів (період Кірка)
    KLINGON_24TH = "klingon_24th"      # TNG Клінгонська імперія (Говрон/Ворф)
    KLINGON_25TH = "klingon_25th"      # Сучасна ера Клінгонів (після війни з Домініоном)
    
    # Romulan ери (6 варіантів) - алгоритмічна генерація палітр
    ROMULAN_22ND = "romulan_22nd"      # Рання Ромуланська зоряна імперія (до TOS)
    ROMULAN_23RD = "romulan_23rd"      # TOS ера Ромуланів (Bird of Prey)
    ROMULAN_23ST = "romulan_23st"      # Альтернативна 23rd Ромулан (часова лінія Немезиди)
    ROMULAN_24TH = "romulan_24th"      # TNG Ромуланська зоряна імперія (Tal Shiar)
    ROMULAN_25TH = "romulan_25th"      # Сучасна ера Ромуланів (після вибуху Хобуса)
    ROMULAN_29TH = "romulan_29th"      # Майбутня ера Ромуланів (часові механізми)
    
    # Cardassian ери (5 варіантів) - алгоритмічна генерація палітр
    CARDASSIAN_22ND = "cardassian_22nd"  # Рання Кардасіанська спілка (до TNG)
    CARDASSIAN_23RD = "cardassian_23rd"  # TNG ера Кардасіанів (ранні конфлікти)
    CARDASSIAN_24TH = "cardassian_24th"  # DS9 Кардасіанська спілка (війна з Домініоном)
    CARDASSIAN_25TH = "cardassian_25th"  # Сучасна ера Кардасіанів (реконструкція)
    CARDASSIAN_29TH = "cardassian_29th"  # Майбутня ера Кардасіанів (в союзі з Федерацією)

# Фракційні палітри в стилі lcars_palette.py
FACTION_COLOR_PALETTES = {
    # Romulan with era variations
    FactionEra.ROMULAN_22ND: {
            'panel_border': '#336666',
            'panel_color': '#339999',
            'button_colors': [
                '#336666', '#339999', '#336633', '#009166',
                '#33B89E', '#86E3B2', '#4ADDFB', '#2EB2E4',
                '#3599CD', '#1C8BAA', '#00A8B6', '#00CED5'
                '#CC9966', '#FBC6B4', '#FFD2BD', '#CC6633'
            ],
            'alert_colors': ['#CC6633', '#CC9966', '#FBC6B4']
        },
        
    FactionEra.ROMULAN_23RD: {
                'panel_border': '#3EDB58',
                'panel_color': '#00B100',
                'button_colors': [
                    '#3EDB58', '#00B100', '#7CF92B', '#99FF99',
                    '#F0E570', '#FFF708', '#C93300', '#C0101D',
                    '#016EB4', '#24A1E8'
                ],
                'alert_colors': ['#C0101D', '#C93300']
            },
            
    FactionEra.ROMULAN_23ST: {
                'panel_border': '#BAFF80',
                'panel_color': '#7CDE2C',
                'button_colors': [
                    '#BAFF80', '#7CDE2C', '#49B600', '#66CC00',
                    '#59E52E', '#00B100', '#009900', '#F89DB2',
                    '#72DEDE'
                ],
                'alert_colors': ['#FA5876', '#F89DB2']
            },
    
    FactionEra.ROMULAN_24TH: {
                'panel_border': '#0E563E',
                'panel_color': '#007633',
                'button_colors': [
                    '#0E563E', '#007633', '#408360', '#6CBD92',
                    '#068F3A', '#28B856', '#61DB86', '#72DEDE',
                    '#00C9C3', '#26D1E0', '#1E94A9', '#F89DB2'
                ],
                'alert_colors': ['#FA5876', '#E2497F']
            },

    FactionEra.ROMULAN_25TH: {
                'panel_border': '#00523B',
                'panel_color': '#2D513B',
                'button_colors': [
                    '#00523B', '#2D513B', '#227D51', '#1D995D',
                    '#56A334', '#61DB86', '#8BFF9C', '#DAFBF1',
                    '#29E5B5', '#72DEDE', '#2ACCD3', '#9583BC'
                ],
                'alert_colors': ['#E2497F', '#79547F', '#9583BC']
            },
            
    FactionEra.ROMULAN_29TH: {
                'panel_border': '#0A1A1A',
                'panel_color': '#006666',
                'button_colors': [
                    '#0A1A1A', '#006666', '#1C7736', '#99CC99',
                    '#FFFF99', '#E0D060', '#BAB444', '#3399CC',
                    '#2CB1F7', '#999999', '#C2C1C2', '#F398C4'
                ],
                'alert_colors': ['#BB5A87', '#F398C4']
            },
            
    # Klingon palettes
    FactionEra.KLINGON_22ND: {
        'panel_border': '#400000',
        'panel_color': '#CC0000',
        'button_colors': [
            '#400000', '#CC0000', '#FF0000', '#FF3300',
            '#EE6900', '#FF9900', '#A99706', '#95FF00',
            '#A59797'
        ],
        'alert_colors': ['#400000', '#CC0000', '#FF0000', '#FF3300', '#EE6900']
    },
    
    FactionEra.KLINGON_23RD: {
        'panel_border': '#CC0000',
        'panel_color': '#FF0000',
        'button_colors': [
            '#CC0000', '#FF0000', '#FA362A', '#D73713',
            '#E96C29', '#F39C35', '#F1BB2F', '#F6EE24',
            '#F6F0B8', '#B9B170', '#5C8B49'
        ],
        'alert_colors': ['#CC0000', '#FF0000', '#FA362A', '#D73713',
            '#E96C29']
    },
    
    FactionEra.KLINGON_24TH: {
        'panel_border': '#660000',
        'panel_color': '#CA0000',
        'button_colors': [
            '#660000', '#980000', '#CA0000', '#D73713',
            '#E7730E', '#FFCB66', '#F6EE24', '#F6F0B8',
            '#C99600', '#CA6400'
        ],
        'alert_colors': ['#CA6400', '#660000', '#980000', '#CA0000', '#D73713']
    },
    
    FactionEra.KLINGON_25TH: {
        'panel_border': '#660000',
        'panel_color': '#A61A35',
        'button_colors': [
            '#660000', '#A61A35', '#CA0000', '#05C6DE',
            '#99F5F9', '#CDFC80', '#F0E075', '#008B9E',
            '#E68D5D', '#E96C29', '#DBBA78'
        ],
        'alert_colors': ['#660000', '#A61A35', '#CA0000','#E96C29', '#E68D5D']
    },
    
    # Cardassian palettes (зміни за епохами)
    FactionEra.CARDASSIAN_22ND: {
        'panel_border': '#664422',
        'panel_color': '#886644',
        'button_colors': [
            '#664422', '#886644', '#AA8866', '#CCAA88',
            '#4A3C1C', '#6B5D3D', '#8C7E5E', '#AD9F7F',
            '#332211', '#554433', '#776655', '#998877'
        ],
        'alert_colors': ['#CC6600', '#AA5500']
    },
    
    FactionEra.CARDASSIAN_23RD: {
        'panel_border': '#CC3300',
        'panel_color': '#FF4400',
        'button_colors': [
            '#CC3300', '#FF4400', '#FF5500', '#FF6600',
            '#003366', '#004488', '#0055AA', '#0066CC',
            '#FF9900', '#FFAA00', '#00CC66', '#00DD77'
        ],
        'alert_colors': ['#FF0000', '#CC0000']
    },
    
    FactionEra.CARDASSIAN_24TH: {
        'panel_border': '#990000',
        'panel_color': '#CC0000',
        'button_colors': [
            '#990000', '#CC0000', '#FF0000', '#FF1111',
            '#001122', '#002244', '#003366', '#004488',
            '#AA2200', '#BB3300', '#CC4400', '#DD5500'
        ],
        'alert_colors': ['#FF3333', '#CC2222']
    },
    
    FactionEra.CARDASSIAN_25TH: {
        'panel_border': '#AA4444',
        'panel_color': '#CC6666',
        'button_colors': [
            '#AA4444', '#CC6666', '#DD8888', '#EEAAAA',
            '#4466AA', '#6688CC', '#88AADD', '#AACCFF',
            '#FFAA44', '#FFBB66', '#FFCC88', '#FFDDAA'
        ],
        'alert_colors': ['#FF6666', '#DD4444']
    },
    
    FactionEra.CARDASSIAN_29TH: {
        'panel_border': '#666699',
        'panel_color': '#8888BB',
        'button_colors': [
            '#666699', '#8888BB', '#AAAADD', '#CCCCFF',
            '#996666', '#BB8888', '#DDAAAA', '#FFCCCC',
            '#669966', '#88BB88', '#AADDAA', '#CCFFCC'
        ],
        'alert_colors': ['#9999FF', '#7777DD']
    }
}

def get_faction_palette(faction_era):
    """
    Отримати палітру для фракції/ери
    Використання: palette = get_faction_palette(FactionEra.KLINGON_24TH)
    """
    base_palette = FACTION_COLOR_PALETTES.get(faction_era, {
        'panel_border': '#666666',
        'button_colors': ['#666666', '#999999', '#CCCCCC', '#FFFFFF'],
        'alert_colors': ['#CC3333', '#FF6666']
    })
    
    # Додаємо універсальні LCARS кольори
    base_palette['background'] = '#000000'  # Завжди чорний фон
    base_palette['text'] = '#FFFFFF'        # Завжди білий текст
    
    return base_palette

# Додаткові функції для роботи з палітрами
def get_faction_colors(faction_name, era_name=None):
    """
    Універсальна функція для отримання палітри фракції
    faction_name: str - назва фракції ('klingon', 'romulan', 'cardassian')
    era_name: str - ера (опційно)
    """
    # Формуємо ключ для пошуку
    if era_name:
        faction_key = f"{faction_name.lower()}_{era_name.lower()}"
    else:
        faction_key = faction_name.lower()
    
    # Шукаємо відповідний enum
    for era in FactionEra:
        if era.value == faction_key:
            return get_faction_palette(era)
    
    # Якщо не знайдено, повертаємо базову палітру
    return {
        'panel_border': '#666666',
        'button_colors': ['#666666', '#999999', '#CCCCCC', '#FFFFFF'],
        'alert_colors': ['#CC3333', '#FF6666']
    }

# Функція для отримання всіх доступних фракцій
def get_available_factions():
    """
    Повертає список всіх доступних фракцій
    """
    factions = set()
    for era in FactionEra:
        faction = era.value.split('_')[0]
        factions.add(faction)
    return list(factions)

# Функція для отримання ер фракції
def get_faction_eras(faction_name):
    """
    Повертає список ер для вказаної фракції
    """
    eras = []
    faction_lower = faction_name.lower()
    for era in FactionEra:
        if era.value.startswith(faction_lower + '_'):
            era_name = era.value.split('_')[1]
            eras.append(era_name)
    return eras

# Графічні елементи для різних фракцій
class KlingonTriangleButton(QPushButton):
    """Клінгонська трикутна кнопка"""
    def __init__(self, text: str, center_type="black_circle", faction_era=FactionEra.KLINGON_24TH, parent=None):
        super().__init__(text, parent)
        self.setObjectName("KlingonTriangleButton")
        self.center_type = center_type  # "black_circle" або "text_in_circle"
        self.faction_era = faction_era
        
        # Отримуємо палітру для фракції/ери
        palette = get_faction_palette(faction_era)
        self.main_color = palette.get('button_colors', ['#8B0000'])[0]
        # Використовуємо другий колір з палітри для акценту, або золотий за замовчуванням
        button_colors = palette.get('button_colors', ['#8B0000'])
        if len(button_colors) > 1:
            self.accent_color = button_colors[1]  # Другий колір кнопки
        else:
            self.accent_color = '#FFD700'  # Золотий за замовчуванням
        
        # Дебаг: виводимо кольори
        print(f"Klingon {faction_era.value}: main={self.main_color}, accent={self.accent_color}")
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #FFD700;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.setFixedSize(120, 80)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Класична клінгонська кнопка - трикутник з гострим кінцем
        path = QPainterPath()
        
        # Починаємо з верхнього лівого кута
        path.moveTo(5, 5)
        
        # Верхня межа
        path.lineTo(self.width() - 5, 5)
        
        # Правий бічний виступ
        path.lineTo(self.width() - 5, 25)
        
        # Правий нижній кут (гострий)
        path.lineTo(self.width() // 2 + 15, self.height() - 10)
        
        # Центральний гострий кінчик
        path.lineTo(self.width() // 2, self.height() - 5)
        
        # Лівий нижній кут (гострий)
        path.lineTo(self.width() // 2 - 15, self.height() - 10)
        
        # Лівий бічний виступ
        path.lineTo(5, 25)
        
        # Замкнути фігуру
        path.closeSubpath()
        
        # Малюємо основну форму
        painter.setBrush(QBrush(QColor(self.main_color)))
        painter.setPen(QPen(QColor(self.accent_color), 2))  # Золота обводка
        painter.drawPath(path)
        
        # Центральний круг
        painter.setBrush(QBrush(QColor("#000000")))
        painter.setPen(QPen(QColor(self.accent_color), 2))
        painter.drawEllipse(self.width()//2 - 6, self.height()//2 - 6, 12, 12)
        
        # Якщо є текст, малюємо його
        if self.text():
            painter.setPen(QPen(QColor(self.accent_color)))
            font = painter.font()
            font.setBold(True)
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        
        # Центральний елемент
        center_x = self.width() // 2
        center_y = self.height() // 2 + 10
        
        if self.center_type == "black_circle":
            # Чорний кружечок без контуру
            painter.setBrush(QBrush(QColor("#000000")))
            painter.setPen(QPen(QColor("#000000"), 1))  # Чорний контур
            painter.drawEllipse(QPoint(center_x, center_y), 8, 8)
            
        elif self.center_type == "text_in_circle":
            # Золотий кружечок з текстом
            painter.setBrush(QBrush(QColor("#FFD700")))
            painter.setPen(QPen(QColor("#FFD700"), 1))  # Золотий контур
            painter.drawEllipse(QPoint(center_x, center_y), 8, 8)

class RomulanTrapezoidButton(QPushButton):
    """Ромуланська кнопка форми "1" - нахилений прямокутник"""
    def __init__(self, text: str, faction_era=FactionEra.ROMULAN_24TH, parent=None):
        super().__init__(text, parent)
        self.setObjectName("RomulanTrapezoidButton")
        self.faction_era = faction_era
        
        # Отримуємо палітру для фракції/ери
        palette = get_faction_palette(faction_era)
        self.main_color = palette.get('button_colors', ['#006666'])[0]
        self.accent_color = palette.get('panel_border', '#00FF99')
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #00FF99;
                font-weight: bold;
                font-style: italic;
                padding: 10px;
            }
        """)
        self.setFixedSize(120, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо форму "1" - нахилений прямокутник, розтягнутий вгору
        shape = QPolygon([
            QPoint(15, self.height() - 5),      # лівий нижній
            QPoint(self.width() - 15, self.height() - 5),  # правий нижній
            QPoint(self.width() - 10, 5),       # правий верхній (вище)
            QPoint(10, 5)                       # лівий верхній (вище)
        ])
        
        painter.setBrush(QBrush(QColor(self.main_color)))
        painter.setPen(QPen(QColor(self.accent_color), 2))
        painter.drawPolygon(shape)
        
        # Текст в центрі
        painter.setPen(QPen(QColor(self.accent_color)))
        font = painter.font()
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class RomulanTrapezoidButton2(QPushButton):
    """Ромуланська кнопка форми "2" - нахилений прямокутник, розтягнутий вбік"""
    def __init__(self, text: str, faction_era=FactionEra.ROMULAN_24TH, parent=None):
        super().__init__(text, parent)
        self.setObjectName("RomulanTrapezoidButton2")
        self.faction_era = faction_era
        
        # Отримуємо палітру для фракції/ери
        palette = get_faction_palette(faction_era)
        self.main_color = palette.get('button_colors', ['#006666'])[0]
        self.accent_color = palette.get('panel_border', '#00FF99')
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #00FF99;
                font-weight: bold;
                font-style: italic;
                padding: 10px;
            }
        """)
        self.setFixedSize(120, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо форму "2" - нахилений прямокутник, розтягнутий вбік
        shape = QPolygon([
            QPoint(5, self.height() - 10),      # лівий нижній (далі)
            QPoint(self.width() - 5, self.height() - 10),  # правий нижній (ближче)
            QPoint(self.width() - 15, 5),       # правий верхній
            QPoint(15, 5)                       # лівий верхній
        ])
        
        painter.setBrush(QBrush(QColor(self.main_color)))
        painter.setPen(QPen(QColor(self.accent_color), 2))
        painter.drawPolygon(shape)
        
        # Текст в центрі
        painter.setPen(QPen(QColor(self.accent_color)))
        font = painter.font()
        font.setBold(True)
        font.setItalic(True)
        font.setPointSize(9)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class RomulanTrapezoidPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RomulanTrapezoidPanel")
        self.setStyleSheet("""
            QFrame {
                background-color: #0A1A1A;
                border: 2px solid #00FF99;
            }
        """)

class CardassianHexagonButton(QPushButton):
    """Кардасіанська шестикутна кнопка"""
    def __init__(self, text: str, faction_era=FactionEra.CARDASSIAN_24TH, parent=None):
        super().__init__(text, parent)
        self.setObjectName("CardassianHexagonButton")
        self.faction_era = faction_era
        
        # Отримуємо палітру для фракції/ери
        palette = get_faction_palette(faction_era)
        self.main_color = palette.get('button_colors', ['#CC3300'])[0]
        self.accent_color = palette.get('panel_border', '#FFD700')
        
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #FFD700;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.setFixedSize(100, 60)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Малюємо складну кардасіанську форму
        shape = QPolygon([
            QPoint(10, self.height() - 5),      # лівий нижній
            QPoint(25, self.height() - 15),     # лівий нижній внутрішній кут
            QPoint(30, self.height() - 25),     # лівий середній нижній
            QPoint(40, self.height() - 20),     # лівий середній
            QPoint(45, self.height() - 30),     # лівий верхній внутрішній
            QPoint(self.width() // 2, 5),       # верхівка
            QPoint(self.width() - 45, self.height() - 30),  # правий верхній внутрішній
            QPoint(self.width() - 40, self.height() - 20),  # правий середній
            QPoint(self.width() - 30, self.height() - 25),  # правий середній нижній
            QPoint(self.width() - 25, self.height() - 15),  # правий нижній внутрішній кут
            QPoint(self.width() - 10, self.height() - 5)    # правий нижній
        ])
        
        painter.setBrush(QBrush(QColor(self.main_color)))
        painter.setPen(QPen(QColor(self.accent_color), 2))
        painter.drawPolygon(shape)
        
        # Текст в центрі
        painter.setPen(QPen(QColor(self.accent_color)))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(7)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())

class CardassianHexagonPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardassianHexagonPanel")
        self.setStyleSheet("""
            QFrame {
                background-color: #2F4F4F;
                border: 2px solid #FFD700;
            }
        """)

# Клас для управління шрифтами фракцій
class FactionFontManager:
    """Менеджер шрифтів для різних фракцій та ер"""
    
    # Шляхи до шрифтів у папці resources
    FONT_PATHS = {
        'klingon': 'resources/klingon font.ttf',
        'romulan': 'resources/Romulan Regular.ttf', 
        'cardassian': 'resources/Cardassian.ttf',
        'starfleet_24th': 'resources/Federation_Wide.ttf',
        'starfleet_25th': 'resources/Roddenberry.ttf',
        'starfleet_22nd': 'resources/startitle.ttf',
        'starfleet_23rd': 'resources/startitle.ttf',
        'starfleet_29th': 'resources/Modern-vulcan-11.ttf'
    }
    
    def __init__(self):
        self.loaded_fonts = {}
        self.current_font = None
    
    def get_font_path(self, faction, era=None):
        """
        Отримати шлях до шрифту для фракції/ери
        faction: str - назва фракції
        era: str - ера (опційно)
        """
        faction_lower = faction.lower()
        
        # Starfleet має різні шрифти за ерами
        if faction_lower == 'starfleet' and era:
            era_lower = era.lower()
            if '24' in era_lower:
                return self.FONT_PATHS['starfleet_24th']
            elif '25' in era_lower:
                return self.FONT_PATHS['starfleet_25th']
            elif '22' in era_lower:
                return self.FONT_PATHS['starfleet_22nd']
            elif '23' in era_lower:
                return self.FONT_PATHS['starfleet_23rd']
            elif '29' in era_lower:
                return self.FONT_PATHS['starfleet_29th']
        
        # Інші фракції використовують один шрифт
        return self.FONT_PATHS.get(faction_lower)
    
    def load_font(self, faction, era=None):
        """
        Завантажити шрифт для фракції/ери
        Повертає шлях якщо файл існує
        """
        font_path = self.get_font_path(faction, era)
        if font_path and os.path.exists(font_path):
            self.current_font = font_path
            return font_path
        return None
    
    def get_available_fonts(self):
        """
        Повертає список доступних шрифтів
        """
        available = {}
        for key, path in self.FONT_PATHS.items():
            if os.path.exists(path):
                available[key] = path
        return available
    
    def get_font_info(self, faction, era=None):
        """
        Отримати інформацію про шрифт
        """
        path = self.get_font_path(faction, era)
        exists = os.path.exists(path) if path else False
        
        return {
            'path': path,
            'exists': exists,
            'faction': faction,
            'era': era
        }

# Глобальний менеджер шрифтів
font_manager = FactionFontManager()

class CardassianHexagonPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardassianHexagonPanel")
        self.setStyleSheet("""
            QFrame {
                background-color: #2F4F4F;
                border: 2px solid #FFD700;
            }
        """)

# QML компоненти для LCARS
class QMLKlingonButton:
    """
    QML клінгонська кнопка з ShapePath
    Використання: QMLKlingonButton.create_widget(parent, "klingon_24th")
    """
    @staticmethod
    def create_widget(parent, faction_era="klingon_24th"):
        """Створює QML віджет клінгонської кнопки"""
        try:
            from PyQt6.QtQuickWidgets import QQuickWidget
            from PyQt6.QtCore import QUrl, QObject, pyqtSignal
            from PyQt6.QtQml import QQmlApplicationEngine
            
            print(f"🔧 Спроба створити QML кнопку для {faction_era}")
            
            class Bridge(QObject):
                clicked = pyqtSignal(str)
                
                def __init__(self, era):
                    super().__init__()
                    self.era = era
                
                def emit_clicked(self):
                    self.clicked.emit(self.era)
            
            # Створюємо QML віджет
            widget = QQuickWidget(parent)
            widget.setFixedSize(120, 80)
            
            # Правильний шлях до QML файлу
            qml_path = "lcars/themes/KlingonButton.qml"
            print(f"🔧 Завантаження QML з: {qml_path}")
            widget.setSource(QUrl.fromLocalFile(qml_path))
            
            # Перевіряємо чи завантажився QML
            if widget.rootObject():
                print("✅ QML завантажено успішно")
                # Встановлюємо колір з палітри
                palette = get_faction_palette(FactionEra(faction_era))
                color = palette['button_colors'][0]
                widget.rootObject().setProperty("btnColor", color)
                widget.rootObject().setProperty("factionEra", faction_era)
                
                # Додаємо білу рамку для видимості
                widget.setStyleSheet("border: 2px solid white;")
                return widget
            else:
                print("❌ QML не завантажився, використовуємо QPushButton")
                return KlingonTriangleButton(faction_era, parent)
            
        except ImportError as e:
            print(f"❌ ImportError QML: {e}")
            # Якщо QML не доступний, повертаємо QPushButton
            return KlingonTriangleButton(faction_era, parent)
        except Exception as e:
            print(f"❌ Помилка QML: {e}")
            return KlingonTriangleButton(faction_era, parent)

class CardassianHexagonPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardassianHexagonPanel")
        self.setStyleSheet("""
            QFrame {
                background-color: #2F4F4F;
                border: 2px solid #FFD700;
            }
        """)