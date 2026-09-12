# ◤ LCARS SCIENCE WORKBENCH v47.1
# Головний науковий хаб системи (Pure LCARS, No Windows).
from __future__ import annotations
import sys

from lcars.base.interface import Panel, LCARSButton, LCARSLabel, PADD
from lcars.base.type import LCARS
# Titanium Bridge Migration: from lcars.base.register import registry
from lcars.base.default import Palette, RandomButtonColor
# from programs.Nova.ide import NovaPanel  # Temporarily disabled due to import issues
from lcars.ui.terminal import LCARSUnifiedTerminal, LCARSTerminal
from lcars.modules.storage import ListChips
# from programs.constructor import TitaniumArchitectEngine  # Temporarily disabled

# Науковий робочий стіл LCARS з навігацією та панелями
class ScienceWorkbench(Panel):
    # Ініціалізація робочого столу з заголовком, тулбаром та контейнером
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode, Color=Palette.Background)
        self.Vertical(10, 10, 10, 10, 10)
        
        # Головний заголовок з правильним розташуванням
        self.HeaderNode = Panel(Parent=self.widget, Color=Palette.Background)
        self.HeaderNode.Horizontal(0, 0, 0, 0, 10)
        self.HeaderNode.widget.setFixedHeight(60)
        
        Title = LCARSLabel("SCIENCE WORKBENCH", Type="title", Color=Palette.Buttons[1], FontSize=16, Parent=self.HeaderNode.widget)
        self.HeaderNode.Add(self.HeaderNode.Layout, Title, 1)
        
        self.Add(self.Layout, self.HeaderNode)
        
        # Навігаційна панель з кнопками
        self.NavPanel = Panel(Parent=self.widget, Color=Palette.Background)
        self.NavPanel.Horizontal(0, 0, 0, 0, 10)
        self.NavPanel.widget.setFixedHeight(50)
        
        self.Modes = ["DASHBOARD", "TERMINAL", "WORKSPACE", "SYSTEMS"]
        self.NavButtons = {}
        
        # Створення кнопок навігації з правильними розмірами
        Mode0 = self.Modes[0] if len(self.Modes) > 0 else None
        if Mode0:
            BtnColor = Palette.Buttons[0] if len(Palette.Buttons) > 0 else Palette.Buttons[0]
            Btn = LCARSButton(Mode0, ColorHexStr=BtnColor, Parent=self.NavPanel.widget)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(150)
            Btn.Clicked.Connect(lambda chk=False, m=Mode0: self.SwitchMode(m))
            self.NavButtons[Mode0] = Btn
            self.NavPanel.Add(self.NavPanel.Layout, Btn)
        
        Mode1 = self.Modes[1] if len(self.Modes) > 1 else None
        if Mode1:
            BtnColor = Palette.Buttons[1] if len(Palette.Buttons) > 1 else Palette.Buttons[0]
            Btn = LCARSButton(Mode1, ColorHexStr=BtnColor, Parent=self.NavPanel.widget)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(150)
            Btn.Clicked.Connect(lambda chk=False, m=Mode1: self.SwitchMode(m))
            self.NavButtons[Mode1] = Btn
            self.NavPanel.Add(self.NavPanel.Layout, Btn)
        
        Mode2 = self.Modes[2] if len(self.Modes) > 2 else None
        if Mode2:
            BtnColor = Palette.Buttons[2] if len(Palette.Buttons) > 2 else Palette.Buttons[0]
            Btn = LCARSButton(Mode2, ColorHexStr=BtnColor, Parent=self.NavPanel.widget)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(150)
            Btn.Clicked.Connect(lambda chk=False, m=Mode2: self.SwitchMode(m))
            self.NavButtons[Mode2] = Btn
            self.NavPanel.Add(self.NavPanel.Layout, Btn)
        
        Mode3 = self.Modes[3] if len(self.Modes) > 3 else None
        if Mode3:
            BtnColor = Palette.Buttons[3] if len(Palette.Buttons) > 3 else Palette.Buttons[0]
            Btn = LCARSButton(Mode3, ColorHexStr=BtnColor, Parent=self.NavPanel.widget)
            Btn.setFixedHeight(40)
            Btn.setMinimumWidth(150)
            Btn.Clicked.Connect(lambda chk=False, m=Mode3: self.SwitchMode(m))
            self.NavButtons[Mode3] = Btn
            self.NavPanel.Add(self.NavPanel.Layout, Btn)
            
        self.Add(self.Layout, self.NavPanel)
        
        # Робоча зона (Контейнер)
        self.WorkspaceContainer = Panel(Parent=self.widget, Color=Palette.Background)
        self.WorkspaceContainer.Horizontal(0, 0, 0, 0, 15)
        
        # Сайдбар (Лівий блок кнопок)
        self.Sidebar = Panel(Parent=self.WorkspaceContainer.widget, Color=Palette.Background)
        self.Sidebar.Vertical(5, 5, 5, 5, 10)
        self.Sidebar.widget.setFixedWidth(150)
        
        # Декоративний LCARS-елемент сайдбару
        self.SideDeco = Panel(Parent=self.Sidebar.widget, Color=Palette.Buttons[0])
        self.SideDeco.widget.setFixedHeight(20)
        self.SideDeco.widget.setStyleSheet(f"background: {Palette.Buttons[0]}; border-top-left-radius: 10px; border-bottom-left-radius: 10px;")
        self.Sidebar.Add(self.Sidebar.Layout, self.SideDeco)
        
        self.LblSubsystems = LCARSLabel("SYSTEMS", Color=Palette.Buttons[2], FontSize=12, Parent=self.Sidebar.widget)
        self.Sidebar.Add(self.Sidebar.Layout, self.LblSubsystems)
        
        self.BtnSensors = LCARSButton("SENSORS", ColorHexStr=Palette.Buttons[1], Parent=self.Sidebar.widget)
        self.BtnTelemetry = LCARSButton("DATA", ColorHexStr=Palette.Buttons[1], Parent=self.Sidebar.widget)
        
        self.Sidebar.Add(self.Sidebar.Layout, self.BtnSensors)
        self.Sidebar.Add(self.Sidebar.Layout, self.BtnTelemetry)
        self.Sidebar.Layout.addStretch(1)
        
        self.WorkspaceContainer.Add(self.WorkspaceContainer.Layout, self.Sidebar)
        
        # Основна панель перегляду
        self.MainView = Panel(Parent=self.WorkspaceContainer.widget, Color=Palette.Background)
        self.MainView.Vertical(0, 0, 0, 0, 0)
        self.MainView.widget.setStyleSheet(f"border-left: 5px solid {Palette.Buttons[1]};")
        self.WorkspaceContainer.Add(self.WorkspaceContainer.Layout, self.MainView, 1)
        
        self.Add(self.Layout, self.WorkspaceContainer, 1)
        
        # Ініціалізація інструментів (Lazy loading через SwitchMode)
        self.DashboardPanel = None
        self.TerminalPanel = None
        self.WorkspacePanel = None
        self.ControlPanel = None
        
        self.SwitchMode("DASHBOARD")

    # Очищення основної панелі перегляду від усіх віджетів
    def ClearMainView(self):
        while self.MainView.Layout.count():
            Item = self.MainView.Layout.takeAt(0)
            WidgetNode = Item.widget()
            if WidgetNode:
                WidgetNode.setParent(None)

    # Перемикання режиму робочого столу та оновлення кольорів навігації
    def SwitchMode(self, Mode):
        self.ClearMainView()
        
        # Оновлення кольорів навігації
        for name, btn in self.NavButtons.items():
            if name == Mode:
                btn.setStyleSheet(btn.styleSheet().replace(Palette.Buttons[0], Palette.Buttons[0]))
            else:
                btn.setStyleSheet(btn.styleSheet().replace(Palette.Buttons[0], Palette.Buttons[0]))
                
        if Mode == "DASHBOARD":
            self.ShowDashboard()
        elif Mode == "WORKSPACE":
            self.ShowWorkspace()
        elif Mode == "TERMINAL":
            self.ShowTerminal()
        elif Mode == "SYSTEMS":
            self.ShowControl()
            
    # Показ панелі дашборду з системними метриками
    def ShowDashboard(self):
        if not self.DashboardPanel:
            self.DashboardPanel = Panel(Color=Palette.Background)
            self.DashboardPanel.Vertical(20, 20, 20, 20, 20)
            
            Header = LCARSLabel("SYSTEMS NOMINAL. AWAITING DIRECTIVES.", Color=Palette.Buttons[0], FontSize=16, Parent=self.DashboardPanel.widget)
            self.DashboardPanel.Add(self.DashboardPanel.Layout, Header)
            
            DataGrid = Panel(Parent=self.DashboardPanel.widget, Color=Palette.Background)
            DataGrid.Horizontal(10, 10, 10, 10, 15)
            
            Col1 = LCARSLabel("ALPHA WAVES\n[ OK ]", Color=Palette.Buttons[2], Parent=DataGrid.widget)
            Col2 = LCARSLabel("BETA EMISSIONS\n[ STABLE ]", Color=Palette.Buttons[0], Parent=DataGrid.widget)
            Col3 = LCARSLabel("DELTA BAND\n[ MONITORING ]", Color=Palette.Buttons[2], Parent=DataGrid.widget)
            
            DataGrid.Add(DataGrid.Layout, Col1, 1)
            DataGrid.Add(DataGrid.Layout, Col2, 1)
            DataGrid.Add(DataGrid.Layout, Col3, 1)
            
            self.DashboardPanel.Add(self.DashboardPanel.Layout, DataGrid, 1)
            
        self.MainView.Add(self.MainView.Layout, self.DashboardPanel.widget, 1)



    # Показ терміналу LCARS (Єдиний уніфікований термінал)
    def ShowTerminal(self):
        if not self.TerminalPanel:
            self.TerminalPanel = LCARSUnifiedTerminal(Parent=self.widget, Compact=False, SplitOption=True)
        WidgetToAdd = self.TerminalPanel.widget if hasattr(self.TerminalPanel, "widget") else self.TerminalPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ робочого простору Titanium Architect
    def ShowWorkspace(self):
        if not self.WorkspacePanel:
            self.WorkspacePanel = Panel(Color=Palette.Background)
            self.WorkspacePanel.Vertical(20, 20, 20, 20, 20)
            Header = LCARSLabel("WORKSPACE SYSTEM", Color=Palette.Buttons[2], FontSize=16, Parent=self.WorkspacePanel.widget)
            self.WorkspacePanel.Add(self.WorkspacePanel.Layout, Header)
            
        WidgetToAdd = self.WorkspacePanel.widget if hasattr(self.WorkspacePanel, "widget") else self.WorkspacePanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ панелі керування системою
    def ShowControl(self):
        if not self.ControlPanel:
            self.ControlPanel = Panel(Color=Palette.Background)
            self.ControlPanel.Vertical(20, 20, 20, 20, 20)
            Header = LCARSLabel("SYSTEM CONTROL", Color=Palette.Buttons[2], FontSize=16, Parent=self.ControlPanel.widget)
            self.ControlPanel.Add(self.ControlPanel.Layout, Header)
            
            status = LCARS.Terminal(self.ControlPanel.widget)
            status.setReadOnly(True)
            status.setStyleSheet(f"background: {Palette.Background}; color: {Palette.Buttons[2]}; border: 1px solid {Palette.Buttons[2]}; font-size: 11pt;")
            self.ControlPanel.Layout.addWidget(status, 1)
            
            BtnsNode = Panel(Color=Palette.Background)
            BtnsNode.Horizontal(0, 0, 0, 0, 10)
            BtnsNode.widget.setFixedHeight(50)
            
            bstart = LCARSButton("Start Core", ColorHexStr=Palette.Buttons[0], Parent=BtnsNode.widget)
            bstop = LCARSButton("Shutdown Core", ColorHexStr=Palette.Red[0], Parent=BtnsNode.widget)
            borch = LCARSButton("Orchestrate", ColorHexStr=Palette.Yellow[0], Parent=BtnsNode.widget)
            
            BtnsNode.Add(BtnsNode.Layout, bstart)
            BtnsNode.Add(BtnsNode.Layout, bstop)
            BtnsNode.Add(BtnsNode.Layout, borch)
            
            self.ControlPanel.Add(self.ControlPanel.Layout, BtnsNode)
            
        self.MainView.Add(self.MainView.Layout, self.ControlPanel.widget, 1)

def User():
    AppCls = LCARS.Application
    if AppCls is None:
        return 1
    AppInst = AppCls.instance() or AppCls([])
    from lcars.base.default import FontSetup
    FontSetup()
    
    Display = PADD(Title="SCIENCE WORKSPACE", color="#000000", width=1400, height=860, portable=True)
    if hasattr(Display.widget, "resize"):
        Display.widget.resize(1400, 860)
    
    Content = Display.Items.get("Content", Display)
    PanelInst = ScienceWorkbench(ParentNode=Content.widget)
    Content.Add(Content.Layout, PanelInst.widget, 1)
    
    if hasattr(Display.widget, "show"):
        Display.widget.show()     
    return AppInst.exec()


def main():
    return User()


if __name__ == "__main__":
    sys.exit(User())
