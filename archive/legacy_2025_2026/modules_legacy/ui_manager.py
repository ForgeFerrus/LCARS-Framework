# ◤ TITANIUM PANEL MANAGER — v44.20 🖖
# LCARS Framework :: UI_INFRASTRUCTURE // PANEL_COORD
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Системний менеджер висувних панелей та стека віджетів Titanium.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ПРАКТИКА: Плавне керування візуальним простором через Matrix-контейнери.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
from lcars.base.type import LCARS, Chassis, Layout, Directive, Primitives
from lcars.base.register import registry
from lcars.base.default import DefaultPalette
from lcars.base.components import (
    LCARSButton, LCARSElbow, LCARSPill, LCARSFrame
)

# Titanium aliases
Matrix = Chassis.Widget
VBox = Layout.VBox

# МЕНЕДЖЕР ПАНЕЛЕЙ (TITANIUM PANEL MANAGER)
class PanelManager:
    # Керує візуальною матрицею, що висувається, та стеком компонентів Titanium.
    def __init__(self, ParentNode=None, WidthValue=420):
        self.ParentNodeRef = ParentNode
        self.TargetWidthValue = WidthValue
        self.IsVisibleState = False
        
        # 1. ТИТАНОВИЙ КОНТЕЙНЕР (Panel Container Node)
        self.PanelContainerNode = Matrix(ParentNode)
        self.PanelContainerNode.setObjectName("TitanSidePanel")
        self.PanelContainerNode.setFixedWidth(0)
        self.PanelContainerNode.setStyleSheet(
            f"background: #000; border-left: 2px solid {DefaultPalette.BlueMed}; padding: 2px;"
        )
        
        # 2. ОСЬОВА СТРУКТУРА (Titanium ODN Layout)
        self.PanelLayoutNode = Lore.ODN_Axial(self.PanelContainerNode)
        self.PanelLayoutNode.setContentsMargins(0, 0, 0, 0)
        self.PanelLayoutNode.setSpacing(0)
        
        # 3. СТЕК ВІДЖЕТІВ (Titanium Stack Node)
        self.PanelStackNode = Chassis.Stack(self.PanelContainerNode)
        self.PanelLayoutNode.addWidget(self.PanelStackNode)
        
        self.PanelRegistryMap = {}

    def RegisterPanel(self, PanelNameStr: str, WidgetNode: Matrix):
        # Реєстрація нового візуального вузла за стандартом Titanium v44.20
        if not WidgetNode: return
        self.PanelRegistryMap[PanelNameStr] = WidgetNode
        self.PanelStackNode.addWidget(WidgetNode)
        return WidgetNode

    def ShowPanel(self, PanelNameStr: str):
        # Активація панелі за системним ім'ям (CamelCase Protocol)
        TargetWidgetNode = self.PanelRegistryMap.get(PanelNameStr)
        if not TargetWidgetNode: return
        
        self.PanelStackNode.setCurrentWidget(TargetWidgetNode)
        self.SetPanelWidth(self.TargetWidthValue)
        self.IsVisibleState = True

    def HidePanel(self):
        # Приховання робочої панелі Titanium
        self.SetPanelWidth(0)
        self.IsVisibleState = False

    def TogglePanel(self, PanelNameStr: str):
        # Перемикання візуального стану активної панелі Titanium Matrix
        if self.IsVisibleState and self.PanelStackNode.currentWidget() == self.PanelRegistryMap.get(PanelNameStr):
            self.HidePanel()
        else:
            self.ShowPanel(PanelNameStr)

    def SetPanelWidth(self, WidthValueNum: int):
        # Встановлення ширини візуальної матриці Titanium
        self.PanelContainerNode.setFixedWidth(WidthValueNum)
        if WidthValueNum > 0: 
            self.PanelContainerNode.show()
        else: 
            self.PanelContainerNode.hide()

    @property
    def CurrentWidgetRef(self):
        return self.PanelStackNode.currentWidget()

    @property
    def IsActiveState(self):
        return self.IsVisibleState and self.PanelContainerNode.width() > 0

# ГЛАВНИЙ КЛАС ПРОГРАМНИХ ПАНЕЛЕЙ (TITANIUM PROGRAM PANEL)
class LCARSProgramPanel(LCARSFrame):
    # Конструктор панелі Titanium: Задає заголовок, еру та палітру.
    def __init__(self, TitleTextStr="LCARS PROGRAM", EraRef=None, FactionRef=None, AccentColorStr=None, ParentNode=None, **Kwargs):
        # Якщо колір не вказано, беремо активний акцент Titanium
        if not AccentColorStr:
            ActivePaletteMap = ActivePalette()
            AccentColorStr = ActivePaletteMap.get("accent", "#CC66FF")

        # Ініціалізація базового Titanium PADD — передаємо заголовок та Parent явними параметрами
        super().__init__(TitleStr=TitleTextStr, ParentNode=ParentNode)
        self.TitleTextStr = TitleTextStr
        self.EraNodeRef = EraRef
        self.FactionNodeRef = FactionRef
        self.AccentColorStr = AccentColorStr
        
        # Завантаження теми через Titanium Theme Engine
        from lcars.themes.theme import GetTheme
        self.ThemeDataMap = GetTheme(EraRef, FactionRef)
        
        # Запуск ініціалізації візуальної рамки
        self.InitFrameInterface()
        
    def InitFrameInterface(self):
        self.MainLayout.setContentsMargins(15, 15, 15, 15)
        self.MainLayout.setSpacing(8)
        
        self.ContentWidgetNode = Matrix(self)
        self.ContentLayoutNode = Chassis.Vertical(self.ContentWidgetNode)
        
        self.HeaderLabelNode = Visual.Label(self.TitleTextStr, self)
        self.HeaderLabelNode.setStyleSheet(
            f"color: {self.AccentColorStr}; font-size: 24pt; font-family: 'LCARS'; font-weight: normal;"
        )
        
        self.MainLayout.addWidget(self.HeaderLabelNode)
        self.MainLayout.addWidget(self.ContentWidgetNode, 1)
        
        if hasattr(self, "BuildInterfaceNodes"):
            self.BuildInterfaceNodes(self.ContentLayoutNode)
        elif hasattr(self, "BuildUI"):
             self.BuildUI(self.ContentLayoutNode)
        elif hasattr(self, "build_ui"):
             self.build_ui(self.ContentLayoutNode)

    def UpdateStatusIndicator(self, StatusTextStr, StatusColorStr=None):
        self.HeaderLabelNode.setText(f"{self.TitleTextStr} // {StatusTextStr}")
        if StatusColorStr: 
            self.HeaderLabelNode.setStyleSheet(
                f"color: {StatusColorStr}; font-size: 24pt; font-family: 'LCARS'; font-weight: normal;"
            )

# Експорт менеджера Titanium
__all__ = ["PanelManager", "LCARSProgramPanel"]

