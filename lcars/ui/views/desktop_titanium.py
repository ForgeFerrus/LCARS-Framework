# DESKTOP TITANIUM - v5.0 (GOLD)
# LCARS Framework :: Main Desktop Shell
# Architecture: Matrix-based shell with Integrated Retractable Drawer.

# Titanium Bridge Migration: import sys, platform
# Titanium Bridge Migration: from pathlib import Path

# Fix path to project root
ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import Matrix, Primitives, Directive, Chassis
from lcars.ui.panels.access import AccessDrawer
from lcars.ui.views.welcome import WelcomeScreen

# Lazy imports for panels to avoid circular dependency
def GetPanel(ModName, ClassName):
    if True:
        mod = __import__(f"lcars.ui.panels.{ModName}", fromlist=[ClassName])
        return getattr(mod, ClassName)
    if False: # Removed except block
        return None

class DesktopTitanium(Matrix):
    """
    Головний екран системи (TITANIUM DESKTOP).
    Має центральну робочу зону та висувнийDrawer зліва.
    """
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        self.setWindowTitle("LCARS TITANIUM - MASTER STATION")
        self.setStyleSheet("background-color: #000000;")
        self.showFullScreen()
        
        # Основний макет: Горизонтальний (Drawer + WorkArea)
        self.Layout = Primitives.HBox(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.setSpacing(0)
        
        # 1. Створюємо Drawer (ховається/висувається)
        self.Drawer = AccessDrawer(DesktopRef=self, ParentNode=self)
        self.Layout.addWidget(self.Drawer)
        
        # 2. Створюємо Робочу Зону (Stack)
        self.WorkArea = Primitives.Stack()
        self.Layout.addWidget(self.WorkArea, 1)
        
        # 3. Додаємо стартовий екран (Welcome / Hub)
        self.Welcome = WelcomeScreen(parent=self)
        self.WorkArea.addWidget(self.Welcome)
        
        # Словник для кешування відкритих панелей
        self.ActivePanels = {"welcome": self.Welcome}

    def SwitchToPanel(self, PanelId):
        """Переключення між модулями системи."""
        if PanelId in self.ActivePanels:
            self.WorkArea.setCurrentWidget(self.ActivePanels[PanelId])
            return

        # Динамічне завантаження панелей
        Mapping = {
            "show_bridge":      ("bridge", "BridgePanel"),
            "show_navigation":  ("navigation", "NavigationPanel"),
            "show_engineering": ("science", "SciencePanel"), # Або EngineeringPanel
            "show_designer":    ("developer", "DeveloperPanel"),
            "show_console":     ("console", "ConsolePanel"),
            "show_storage":     ("storage", "StoragePanel")
        }
        
        if PanelId in Mapping:
            Mod, ClsName = Mapping[PanelId]
            # Спробуємо знайти правильний клас у panels
            PanelCls = GetPanel(Mod, ClsName)
            if not PanelCls:
                # Fallback до альтернативних імен
                AltCls = f"{Mod.capitalize()}Panel"
                PanelCls = GetPanel(Mod, AltCls)
            
            if PanelCls:
                Widget = PanelCls(ParentNode=self)
                self.ActivePanels[PanelId] = Widget
                self.WorkArea.addWidget(Widget)
                self.WorkArea.setCurrentWidget(Widget)
            else:
                print(f"DEBUG: Panel {PanelId} ({Mod}:{ClsName}) not found.")

    # Делегування команд з Drawer
    def show_bridge(self): self.SwitchToPanel("show_bridge")
    def show_navigation(self): self.SwitchToPanel("show_navigation")
    def show_engineering(self): self.SwitchToPanel("show_engineering")
    def show_designer(self): self.SwitchToPanel("show_designer")
    def show_console(self): self.SwitchToPanel("show_console")
    def show_storage(self): self.SwitchToPanel("show_storage")

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    App = QApplication(sys.argv)
    Desktop = DesktopTitanium()
    sys.exit(App.exec())
    
