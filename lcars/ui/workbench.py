# ◤ LCARS SCIENCE WORKBENCH v47.1
# Головний науковий хаб системи (Pure LCARS, No Windows).
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lcars.base.interface import Panel, LCARSButton, LCARSLabel, PADD
from lcars.base.type import LCARS
from lcars.base.register import registry
from lcars.base.default import Palette, RandomButtonColor
from programs.Nova.ide import NovaPanel
from lcars.ui.terminal import LCARSTerminal
from lcars.modules.storage import ListChips
from programs.constructor import TitaniumArchitectEngine

# Науковий робочий стіл LCARS з навігацією та панелями
class ScienceWorkbench(Panel):
    # Ініціалізація робочого столу з заголовком, тулбаром та контейнером
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode, Color=Palette.Background)
        self.Vertical(10, 10, 10, 10, 10)
        
        # Головний заголовок та тулбар
        self.HeaderNode = Panel(Parent=self.widget, Color=Palette.Background)
        self.HeaderNode.Horizontal(0, 0, 0, 0, 10)
        self.HeaderNode.widget.setFixedHeight(80)
        
        Title = LCARSLabel("SCIENCE WORKBENCH", Type="title", Color=Palette.Accent[1], FontSize=18, Parent=self.HeaderNode.widget)
        self.HeaderNode.Add(self.HeaderNode.Layout, Title, 1)
        
        self.Modes = ["DASHBOARD", "WORKSPACE", "IDE", "TERMINAL", "ONBOARD", "CONTROL", "TRICORDER", "ANALYTICS", "DATABANKS"]
        self.NavButtons = {}
        
        # Створення кнопок навігації для кожного режиму
        for Mode in self.Modes:
            BtnColor = Palette.Buttons[0] if Mode != "DASHBOARD" else Palette.Panels[0]
            Btn = LCARSButton(Mode, ColorHexStr=BtnColor, Parent=self.HeaderNode.widget)
            Btn.setFixedHeight(50)
            Btn.setMinimumWidth(150)
            Btn.clicked.Connect(lambda chk=False, m=Mode: self.SwitchMode(m))
            self.NavButtons[Mode] = Btn
            self.HeaderNode.Add(self.HeaderNode.Layout, Btn)
            
        self.Add(self.Layout, self.HeaderNode)
        
        # Робоча зона (Контейнер)
        self.WorkspaceContainer = Panel(Parent=self.widget, Color=Palette.Background)
        self.WorkspaceContainer.Horizontal(0, 0, 0, 0, 15)
        
        # Сайдбар (Лівий блок кнопок)
        self.Sidebar = Panel(Parent=self.WorkspaceContainer.widget, Color=Palette.Background)
        self.Sidebar.Vertical(5, 5, 5, 5, 10)
        self.Sidebar.widget.setFixedWidth(180)
        
        # Декоративний LCARS-елемент сайдбару
        self.SideDeco = Panel(Parent=self.Sidebar.widget, Color=Palette.Panels[0])
        self.SideDeco.widget.setFixedHeight(30)
        self.SideDeco.widget.setStyleSheet(f"background: {Palette.Panels[0]}; border-top-left-radius: 15px; border-bottom-left-radius: 15px;")
        self.Sidebar.Add(self.Sidebar.Layout, self.SideDeco)
        
        self.LblSubsystems = LCARSLabel("SUBSYSTEMS", Color=Palette.Accent[2], FontSize=12, Parent=self.Sidebar.widget)
        self.Sidebar.Add(self.Sidebar.Layout, self.LblSubsystems)
        
        self.BtnSensors = LCARSButton("SENSORS", ColorHexStr=Palette.Buttons[1], Parent=self.Sidebar.widget)
        self.BtnTelemetry = LCARSButton("TELEMETRY", ColorHexStr=Palette.Buttons[1], Parent=self.Sidebar.widget)
        self.BtnAstrometrics = LCARSButton("ASTRO", ColorHexStr=Palette.Buttons[1], Parent=self.Sidebar.widget)
        
        self.Sidebar.Add(self.Sidebar.Layout, self.BtnSensors)
        self.Sidebar.Add(self.Sidebar.Layout, self.BtnTelemetry)
        self.Sidebar.Add(self.Sidebar.Layout, self.BtnAstrometrics)
        self.Sidebar.Layout.addStretch(1)
        
        self.WorkspaceContainer.Add(self.WorkspaceContainer.Layout, self.Sidebar)
        
        # Основна панель перегляду
        self.MainView = Panel(Parent=self.WorkspaceContainer.widget, Color=Palette.Background)
        self.MainView.Vertical(0, 0, 0, 0, 0)
        self.MainView.widget.setStyleSheet(f"border-left: 5px solid {Palette.Accent[1]};")
        self.WorkspaceContainer.Add(self.WorkspaceContainer.Layout, self.MainView, 1)
        
        self.Add(self.Layout, self.WorkspaceContainer, 1)
        
        # Ініціалізація інструментів (Lazy loading через SwitchMode)
        self.TricorderPanel = None
        self.CalculatorPanel = None
        self.DashboardPanel = None
        self.DatabanksPanel = None
        self.IDEPanel = None
        self.TerminalPanel = None
        self.OnboardPanel = None
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
                btn.setStyleSheet(btn.styleSheet().replace(Palette.Buttons[0], Palette.Panels[0]))
            else:
                btn.setStyleSheet(btn.styleSheet().replace(Palette.Panels[0], Palette.Buttons[0]))
                
        if Mode == "DASHBOARD":
            self.ShowDashboard()
        elif Mode == "WORKSPACE":
            self.ShowWorkspace()
        elif Mode == "IDE":
            self.ShowIDE()
        elif Mode == "TERMINAL":
            self.ShowTerminal()
        elif Mode == "ONBOARD":
            self.ShowOnboard()
        elif Mode == "CONTROL":
            self.ShowControl()
        elif Mode == "TRICORDER":
            self.ShowTricorder()
        elif Mode == "ANALYTICS":
            self.ShowAnalytics()
        elif Mode == "DATABANKS":
            self.ShowDatabanks()
            
    # Показ панелі дашборду з системними метриками
    def ShowDashboard(self):
        if not self.DashboardPanel:
            self.DashboardPanel = Panel(Color=Palette.Background)
            self.DashboardPanel.Vertical(20, 20, 20, 20, 20)
            
            Header = LCARSLabel("SYSTEMS NOMINAL. AWAITING DIRECTIVES.", Color=Palette.Green[0], FontSize=16, Parent=self.DashboardPanel.widget)
            self.DashboardPanel.Add(self.DashboardPanel.Layout, Header)
            
            DataGrid = Panel(Parent=self.DashboardPanel.widget, Color=Palette.Background)
            DataGrid.Horizontal(10, 10, 10, 10, 15)
            
            Col1 = LCARSLabel("ALPHA WAVES\n[ OK ]", Color=Palette.Buttons[2], Parent=DataGrid.widget)
            Col2 = LCARSLabel("BETA EMISSIONS\n[ STABLE ]", Color=Palette.Green[0], Parent=DataGrid.widget)
            Col3 = LCARSLabel("DELTA BAND\n[ MONITORING ]", Color=Palette.Accent[2], Parent=DataGrid.widget)
            
            DataGrid.Add(DataGrid.Layout, Col1, 1)
            DataGrid.Add(DataGrid.Layout, Col2, 1)
            DataGrid.Add(DataGrid.Layout, Col3, 1)
            
            self.DashboardPanel.Add(self.DashboardPanel.Layout, DataGrid, 1)
            
        self.MainView.Add(self.MainView.Layout, self.DashboardPanel.widget, 1)

    # Показ вбудованого IDE Nova
    def ShowIDE(self):
        if not self.IDEPanel:
            self.IDEPanel = NovaPanel(Parent=self.widget)
        WidgetToAdd = self.IDEPanel.widget if hasattr(self.IDEPanel, "widget") else self.IDEPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ терміналу LCARS
    def ShowTerminal(self):
        if not self.TerminalPanel:
            self.TerminalPanel = LCARSTerminal(parent=self.widget, lite=True)
        WidgetToAdd = self.TerminalPanel.widget if hasattr(self.TerminalPanel, "widget") else self.TerminalPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ робочого простору Titanium Architect
    def ShowWorkspace(self):
        if not self.WorkspacePanel:
            self.WorkspacePanel = TitaniumArchitectEngine(ParentNode=self.widget)
            
        WidgetToAdd = self.WorkspacePanel.widget if hasattr(self.WorkspacePanel, "widget") else self.WorkspacePanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ панелі керування системою
    def ShowControl(self):
        if not self.ControlPanel:
            self.ControlPanel = Panel(Color=Palette.Background)
            self.ControlPanel.Vertical(20, 20, 20, 20, 20)
            Header = LCARSLabel("SYSTEM CONTROL", Color=Palette.Accent[2], FontSize=16, Parent=self.ControlPanel.widget)
            self.ControlPanel.Add(self.ControlPanel.Layout, Header)
            
            status = registry.Get("Interface.TextEdit")()
            status.setReadOnly(True)
            status.setStyleSheet(f"background: {Palette.Background}; color: {Palette.Accent[2]}; border: 1px solid {Palette.Accent[2]}; font-size: 11pt;")
            self.ControlPanel.Layout.addWidget(status, 1)
            
            BtnsNode = Panel(Color=Palette.Background)
            BtnsNode.Horizontal(0, 0, 0, 0, 10)
            BtnsNode.widget.setFixedHeight(50)
            
            bstart = LCARSButton("Start Core", ColorHexStr=Palette.Green[0], Parent=BtnsNode.widget)
            bstop = LCARSButton("Shutdown Core", ColorHexStr=Palette.RedAlert[0], Parent=BtnsNode.widget)
            borch = LCARSButton("Orchestrate", ColorHexStr=Palette.YellowAlert[0], Parent=BtnsNode.widget)
            
            BtnsNode.Add(BtnsNode.Layout, bstart)
            BtnsNode.Add(BtnsNode.Layout, bstop)
            BtnsNode.Add(BtnsNode.Layout, borch)
            
            self.ControlPanel.Add(self.ControlPanel.Layout, BtnsNode)
            
        self.MainView.Add(self.MainView.Layout, self.ControlPanel.widget, 1)

    # Показ панелі бортового комп'ютера та сервісів
    def ShowOnboard(self):
        if not self.OnboardPanel:
            self.OnboardPanel = Panel(Color=Palette.Background)
            self.OnboardPanel.Vertical(20, 20, 20, 20, 20)
            
            Header = LCARSLabel("ONBOARD COMPUTER - SERVICES & MODULES", Color=Palette.Panels[1], FontSize=16, Parent=self.OnboardPanel.widget)
            self.OnboardPanel.Add(self.OnboardPanel.Layout, Header)
            
            # Список сервісів та модулів згідно архітектури
            StatusLog = registry.Get("Interface.TextEdit")()
            StatusLog.setReadOnly(True)
            StatusLog.setStyleSheet(f"background: {Palette.Background}; color: {Palette.Buttons[1]}; border: 1px solid {Palette.Buttons[1]}; font-size: 11pt;")
            StatusLog.append("--- SYSTEM SERVICES REGISTRY ---")
            StatusLog.append("[ONLINE] DataStorageService")
            StatusLog.append("[ONLINE] ODNNetworkBus")
            StatusLog.append("[ONLINE] LCARSDisplayManager")
            StatusLog.append("[ONLINE] IsolinearSubsystem")
            StatusLog.append("\n--- ACTIVE MODULES ---")
            StatusLog.append("Module: Science/Tricorder")
            StatusLog.append("Module: Core/Kernel")
            
            self.OnboardPanel.Layout.addWidget(StatusLog, 1)
            
            # Динамічний список Chip для зберігання
            ChipsGrid = Panel(Color=Palette.Background)
            ChipsGrid.Horizontal(0, 0, 0, 0, 10)
            ChipsGrid.widget.setFixedHeight(60)
            
            for chip in ListChips():
                ChipBtn = LCARSButton(chip, ColorHexStr=RandomButtonColor(), Parent=ChipsGrid.widget)
                ChipsGrid.Add(ChipsGrid.Layout, ChipBtn)
            ChipsGrid.Layout.addStretch(1)
                
            self.OnboardPanel.Add(self.OnboardPanel.Layout, ChipsGrid)
            
        WidgetToAdd = self.OnboardPanel.widget if hasattr(self.OnboardPanel, "widget") else self.OnboardPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)
        
    # Показ вікна трикодера (зовнішній модуль)
    def ShowTricorder(self):
        if not self.TricorderPanel:
            from programs.science.tricorder import TricorderWindow
            self.TricorderPanel = TricorderWindow()
        
        WidgetToAdd = self.TricorderPanel.widget if hasattr(self.TricorderPanel, "widget") else self.TricorderPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)
        
    # Показ аналітичного калькулятора
    def ShowAnalytics(self):
        if not self.CalculatorPanel:
            from lcars.tools.calculator import AnalyticalCalculative
            self.CalculatorPanel = AnalyticalCalculative()
            
        WidgetToAdd = self.CalculatorPanel.widget if hasattr(self.CalculatorPanel, "widget") else self.CalculatorPanel
        self.MainView.Add(self.MainView.Layout, WidgetToAdd, 1)

    # Показ наукових банків даних
    def ShowDatabanks(self):
        if not self.DatabanksPanel:
            self.DatabanksPanel = Panel(Color=Palette.Background)
            self.DatabanksPanel.Vertical(20, 20, 20, 20, 10)
            
            Header = LCARSLabel("SCIENTIFIC DATABANKS", Color=Palette.Panels[0], FontSize=16, Parent=self.DatabanksPanel.widget)
            self.DatabanksPanel.Add(self.DatabanksPanel.Layout, Header)
            
            TextOut = registry.Get("Interface.TextEdit")()
            TextOut.setReadOnly(True)
            TextOut.setStyleSheet(f"background: {Palette.Background}; color: {Palette.Accent[1]}; border: 1px solid {Palette.Accent[1]}; font-size: 12pt;")
            TextOut.setPlainText("LOG ENTRY 451.2:\n- Initiating broad-spectrum analysis.\n- Sensor telemetry re-routed to main deflector.\n- Subspace harmonics detected in sector 4.")
            
            self.DatabanksPanel.Layout.addWidget(TextOut, 1)
            
        self.MainView.Add(self.MainView.Layout, self.DatabanksPanel.widget, 1)

if __name__ == "__main__":
   
        AppCls = LCARS.Application
        AppInst = AppCls.instance() or AppCls(sys.argv)
        
        Display = PADD("SCIENCE WORKBENCH", color="#000000")
        if hasattr(Display.widget, "resize"):
            Display.widget.resize(1200, 800)
        
        panel = ScienceWorkbench(ParentNode=Display.Items["Content"].widget)
        Display.Items["Content"].Add(Display.Items["Content"].Layout, panel.widget, 1)
        
        if hasattr(Display.widget, "show"):
            Display.widget.show()     
        sys.exit(AppInst.exec())
