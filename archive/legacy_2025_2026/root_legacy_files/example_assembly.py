# LCARS Component Assembly Example
# Демонстрація збірки UI з базових типів без залежності від Qt

from lcars.base.component import (
    Surface, Symbol, Structure,
    Button1, Button2, Button3, Label1, Label2,
    Elbow1, Elbow2, Bar1, Bar2,
    LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSPill
)
from lcars.base.default import Palette
from lcars.base import registry

# ═══════════════════════════════════════════════════════════════════════════
# ПРИКЛАД 1: Кнопка статусу системи
# ═══════════════════════════════════════════════════════════════════════════
def CreateStatusButton(Text="ONLINE", Color=None):
    return Button3(
        Text=Text,
        Color=Color or Palette.Buttons[6],  # Зелений
        FontSize=16
    )

# ═══════════════════════════════════════════════════════════════════════════
# ПРИКЛАД 2: Панель заголовка з кутами
# ═══════════════════════════════════════════════════════════════════════════
def CreateHeaderPanel(Width=800, Title="SYSTEM"):
    Color = Palette.Buttons[0]  # Синій
    
    return {
        "LeftElbow": Elbow1(Color=Color),
        "TopBar": Bar1(Color=Color),
        "Title": Label1(Text=Title, Color=Palette.Buttons[2]),
        "RightElbow": Elbow2(Color=Color)
    }

# ═══════════════════════════════════════════════════════════════════════════
# ПРИКЛАД 3: Повна збірка - Панель навігації
# ═══════════════════════════════════════════════════════════════════════════
class NavigationPanel:
   
    def __init__(self):
        self.Components = []
        
    def Assemble(self):
        # Верхня смуга з кутами
        self.TopLeft = Elbow1(Color=Palette.Buttons[0])
        self.TopBar = Bar1(Color=Palette.Buttons[0])
        self.TopRight = Elbow2(Color=Palette.Buttons[0])
        
        # Кнопки управління
        self.BtnMain = LCARSButton(Text="MAIN", Color=Palette.Buttons[1])
        self.BtnConfig = LCARSButton(Text="CONFIG", Color=Palette.Buttons[1])
        self.BtnExit = Button6(Text="EXIT", Color=Palette.Buttons[3])  # Cropped/orange
        
        # Індикатор статусу
        self.StatusPill = LCARSPill(Text="ACTIVE", Color=Palette.Buttons[6])
        self.StatusLabel = LCARSLabel(Text="v1.0.0", Color=Palette.Buttons[2])
        
        # Зберігаємо всі компоненти
        self.Components = [
            self.TopLeft, self.TopBar, self.TopRight,
            self.BtnMain, self.BtnConfig, self.BtnExit,
            self.StatusPill, self.StatusLabel
        ]
        
        # Реєстрація всіх компонентів у реєстрі
        for i, Comp in enumerate(self.Components):
            registry.Register(f"NavPanel.{i}.{Comp.__class__.__name__}", Comp)
        
        return self
    
    def GetComponentsByType(self, TypeName):
        """Повертає компоненти за типом"""
        return [c for c in self.Components if c.__class__.__name__ == TypeName]

# ═══════════════════════════════════════════════════════════════════════════
# ПРИКЛАД 4: Демонстрація використання
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Створюємо панель навігації
    Panel = NavigationPanel()
    Panel.Assemble()
    
    print(f"[LCARS] Assembled {len(Panel.Components)} components")
    print(f"[LCARS] Surfaces: {len(Panel.GetComponentsByType('Surface'))}")
    print(f"[LCARS] Symbols: {len(Panel.GetComponentsByType('Symbol'))}")
    print(f"[LCARS] Structures: {len(Panel.GetComponentsByType('Structure'))}")
    
    # Перевіряємо реєстр
    Keys = [k for k in registry.Keys if k.startswith("NavPanel")]
    print(f"[LCARS] Registered {len(Keys)} keys in registry")
