DefaultRadius=20
# ◤ TITANIUM DEFAULTS — v1.0.0 ФАЙЛ ЗАВЕРШЕНО ЗМІНИ НЕ ВНОСИТИ!!!
# ЦЕЙ ФАЙЛ: Базові візуальні константи та утиліти стилізації. 
# ПРАВИЛО: Функціональне групування кольорів (Кнопки, Панелі, Алерт).
# ───────────────────────────────────────────────────────────────
import random
# Titanium Bridge Migration: from typing import Dict, List, Any
# Titanium Bridge Migration: from pathlib import Path

# ◤ МАТРИЦЯ TITANIUM (FUNCTIONAL COLOR GROUPS)
class DefaultPalette:
    Background  = "#000000"
    
    # 1. ГРУПА: КНОПКИ (Interactive Matrices)
    Buttons = [
        "#336699", "#6699CC", "#99CCFF", # Blue Cluster
        "#D37445", "#F0B942", "#BA985D", # Gold Cluster
        "#7D8736", "#606060", "#333333"  # Grey Cluster
    ]
    # 2. ГРУПА: (Structural Elements)
    Panels = ["#336699", "#6699CC", "#99CCFF"] # Blue Variants
    # 3. ГРУПА: (Accent Mode)
    Accent = [ "#7D8736", "#3D8736", "#50571A" ] # Green Variants
    # 4. ГРУПА:(Alert Modes)
    RedAlert = ["#D37445", "#CC0000C7", "#E63946"] # Orange, Red Med, Red Alert
    # 5. ГРУПА: (Engineering Mode)
    YellowAlert = ["#FF9900", "#CC9966", "#D37445"] # Orange, Gold, Deep Orange

    # Допоміжні кольори / імена, які можуть бути запитані у компонентах
    BlueMed = Buttons[1]
    OrangeStd = YellowAlert[0]
    Scientific = [Accent[0], Accent[1], Accent[2]]
    Alert = YellowAlert

# ◤ СИСТЕМНІ ПАРАМЕТРИ
DefaultRadius = 20
DefaultBackground = DefaultPalette.Background
DefaultPrimary = DefaultPalette.Buttons[0]
DefaultSecondary = DefaultPalette.Buttons[1]
DefaultAccent = DefaultPalette.Accent[0]

GREEN = "#7D8736"
YELLOW = DefaultPalette.YellowAlert[0]
RED = DefaultPalette.RedAlert[1]

NORMAL = DefaultPalette.Accent[0]
ALERT_GREEN = GREEN
ALERT_YELLOW = DefaultPalette.YellowAlert[0]
ALERT_RED = DefaultPalette.RedAlert[0]

# ◤ АЛГОРИТМ ВИПАДКОВОГО КОЛЬОРУ (TITANIUM POOL)
def RandomButtonColor(GroupStr: str = "buttons") -> str:
    # Пул кольорів на основі функціональної групи
    if GroupStr == "accent": Pool = DefaultPalette.Accent
    elif GroupStr == "alert": Pool = DefaultPalette.RedAlert
    elif GroupStr == "panels": Pool = DefaultPalette.Panels
    else: Pool = DefaultPalette.Buttons
    return random.choice(Pool)

def AlertColor(LevelInt: int = 1) -> str:
    # ◤ ТРИВОЖНИЙ ТИТАНІУМ (Functional Alert)
    return DefaultPalette.RedAlert[min(LevelInt - 1, len(DefaultPalette.RedAlert) - 1)] if LevelInt > 0 else "#00CC00"

def ColorBrightness(Hex: str) -> float:
    H = Hex.lstrip('#')
    if len(H) == 3:
        H = ''.join([c*2 for c in H])
    R, G, B = int(H[0:2], 16), int(H[2:4], 16), int(H[4:6], 16)
    return (R * 299 + G * 587 + B * 114) / 1000

def ContrastColor(Hex: str) -> str:
    return '#FFFFFF' if ColorBrightness(Hex) < 128 else '#000000'

def FontStyle(Size: int = 16, Weight: str = "normal") -> str:
    return f"font-size: {Size}pt; font-family: 'LCARS'; font-weight: {Weight};"

def FontSetup():
    from lcars.base.register import registry
    FontDb = registry.Node("Technical.FontDatabase") or registry.Node("Technical.Gui")
    if not FontDb: return
    BaseDir = Path(__file__).resolve().parent.parent.parent
    FontPath = BaseDir / "resources" / "fonts" / "lcars.ttf"
    if FontPath.exists() and hasattr(FontDb, 'addApplicationFont'):
        FontDb.addApplicationFont(str(FontPath))

def ActivePalette() -> Dict[str, str]:
    return {
        "primary":   DefaultPalette.Buttons[0],
        "secondary": DefaultPalette.Buttons[1],
        "accent":    DefaultPalette.Accent[2],
        "neutral":   DefaultPalette.Panels[0],
        "background": DefaultPalette.Background
    }

def DefaultTheme():
    return {
        "primary":    DefaultPalette.Buttons[1],
        "accent":     DefaultPalette.Accent[0],
        "background": DefaultPalette.Background,
        "radius":     DefaultRadius
    }

# АЛІАСИ ДЛЯ TITANIUM V44.20 (Architectural Aliases)
GetDefaultTheme = DefaultTheme
SetupLcarsFont = FontSetup
GetLcarsFontStyle = FontStyle
SystemTheme = DefaultTheme
SetupFont = FontSetup
GetActivePalette = lambda: DefaultPalette
GetRandomButtonColor = RandomButtonColor
GetRandomFactionColor = lambda: "#4BBEBF"

__all__ = [
    "DefaultPalette", "DefaultRadius", "DefaultPrimary", "DefaultSecondary", 
    "DefaultAccent", "RandomButtonColor", "ContrastColor", "FontStyle", 
    "FontSetup", "AlertColor", "ActivePalette", "DefaultTheme"
    
]

TitanPalette = DefaultPalette
ActivePalette = DefaultPalette
AlertPalette = DefaultPalette
