# Демонстраційний файл LCARS - автентична система в стилі Star Trek
# Призначення: Демонстрація палітр проекту через базові компоненти фреймворку

import sys
from pathlib import Path

# Додаємо корінь проекту в шлях Python для імпорту модулів lcars
projectRoot = Path(__file__).parent.absolute()
repoRoot = projectRoot.parent
sys.path.insert(0, str(repoRoot))

# Імпортуємо через реєстр LCARS базові компоненти
from lcars.base.type import LCARS

ComponentModule = LCARS.Import("lcars.base.component")
LCARSButton = ComponentModule.LCARSButton
LCARSElbow = ComponentModule.LCARSElbow
LCARSLabel = ComponentModule.LCARSLabel
LCARSIndicator = ComponentModule.LCARSIndicator
LCARSBar = ComponentModule.LCARSBar

InterfaceModule = LCARS.Import("lcars.base.interface")
Screen = InterfaceModule.Screen
Segment = InterfaceModule.Segment
Header = InterfaceModule.Header
DataBlock = InterfaceModule.DataBlock

DefaultModule = LCARS.Import("lcars.base.default")
Palette = DefaultModule.Palette
RandomButtonColor = DefaultModule.RandomButtonColor
FontStyle = DefaultModule.FontStyle

DesktopModule = LCARS.Import("lcars.base.desktop")
LCARSDesktop = DesktopModule.LCARSDesktop

PaletteModule = LCARS.Import("lcars.themes.lcars_palette")
LCARSEra = PaletteModule.LCARSEra
getTheme = PaletteModule.get_theme
setupLcarsFont = PaletteModule.setup_lcars_font

ThemeModule = LCARS.Import("lcars.themes.theme")
FactionEra = ThemeModule.FactionEra

# Налаштування шрифтів LCARS
setup_lcars_font()

# Побудова словника кольорів з теми для сумісності UI коду
defaultTheme = get_theme(LCARSEra.LCARS_25TH)
palette = defaultTheme.get('palette', ['#4BBEBF'])
LCARSColors = {
    'primary_orange': palette[4] if len(palette) > 4 else palette[0],
    'primary_cyan': palette[0],
    'primary_blue': palette[1] if len(palette) > 1 else palette[0],
    'secondary_cyan': palette[2] if len(palette) > 2 else palette[0],
    'secondary_orange': palette[3] if len(palette) > 3 else palette[0],
    'secondary_blue': palette[1] if len(palette) > 1 else palette[0],
    'alert_red': defaultTheme.get('alerts', ['#D80000'])[0],
    'alert_yellow': defaultTheme.get('alerts', ['#FFBB00'])[1] if len(defaultTheme.get('alerts', [])) > 1 else defaultTheme.get('alerts', ['#FFBB00'])[0],
    'text_black': defaultTheme.get('text', '#000000'),
    'text_white': defaultTheme.get('text', '#FFFFFF'),
    'background_black': defaultTheme.get('bg', '#000000'),
    'panel_gray': palette[0]
}

# Відображення назв епох на enum LCARSEra
ERANameToEnum = {
    "22nd": LCARSEra.COMS_22ND,
    "23rd": LCARSEra.PCARS_23RD,
    "23st": LCARSEra.PCARS_23ST,
    "24th": LCARSEra.LCARS_24TH,
    "24st": LCARSEra.LCARS_24ST,
    "25th": LCARSEra.LCARS_25TH,
    "29th": LCARSEra.TCARS_29TH,
}

def main():
    # Делегуємо до уніфікованого лаунчера демо
    from demo import demo_launcher
    demo_launcher.main()

if __name__ == "__main__":
    main()
