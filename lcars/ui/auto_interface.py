# LCARS Auto Interface Generator - автоматична збірка інтерфейсів бортовим комп'ютером
# Призначення: бортовий комп'ютер аналізує систему і генерує відповідний інтерфейс
# Функціонал: динамічне створення UI на основі стану системи, реєстру компонентів
# Titanium Bridge Migration: import sys
from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel, LCARSButton, LCARSLabel, LCARSBar, LCARSElbow
from lcars.base.default import Palette
from lcars.base.register import registry
from lcars.core.signal import Transmission, ODN


class AutoInterfaceGenerator:
    # Генератор автоматичних інтерфейсів на основі системного стану
    
    def __init__(self, BoardComputer=None):
        self.Computer = BoardComputer
        self.Registry = registry
        self.SystemState = "NORMAL"
        self.AvailableComponents = self.ScanComponents()
        self.InterfaceTemplates = self.LoadTemplates()
    
    def ScanComponents(self):
        # Сканування доступних компонентів з реєстру
        components = {}
        for key in self.Registry.keys():
            if "Bridge" in key or "Service" in key or "System" in key:
                category = key.split(".")[0] if "." in key else "System"
                if category not in components:
                    components[category] = []
                components[category].append(key)
        return components
    
    def LoadTemplates(self):
        # Завантаження шаблонів інтерфейсів для різних сценаріїв
        return {
            "normal": self.GetNormalTemplate(),
            "diagnostic": self.GetDiagnosticTemplate(),
            "emergency": self.GetEmergencyTemplate(),
            "ai": self.GetAITemplate(),
            "bridge": self.GetBridgeTemplate()
        }
    
    def GetNormalTemplate(self):
        # Шаблон для нормального режиму роботи
        return {
            "layout": "sidebar_main",
            "panels": [
                {"type": "header", "title": "LCARS BOARD COMPUTER", "status": "ONLINE"},
                {"type": "sidebar", "buttons": ["SYSTEM", "DIAGNOSTICS", "AI CORE", "BRIDGE", "FILES", "NETWORK", "SECURITY"]},
                {"type": "main", "content": "terminal"},
                {"type": "footer", "info": "UPTIME | SESSION | ENCRYPTION | PROTOCOL"}
            ],
            "colors": Palette.Buttons
        }
    
    def GetDiagnosticTemplate(self):
        # Шаблон для діагностичного режиму
        return {
            "layout": "grid_diagnostics",
            "panels": [
                {"type": "header", "title": "SYSTEM DIAGNOSTICS", "status": "RUNNING"},
                {"type": "monitor", "metrics": ["CPU", "MEMORY", "NETWORK", "DISK", "TEMPERATURE"]},
                {"type": "logs", "content": "system_logs"},
                {"type": "controls", "buttons": ["RUN TESTS", "CLEAR LOGS", "EXPORT REPORT"]}
            ],
            "colors": Palette.Yellow
        }
    
    def GetEmergencyTemplate(self):
        # Шаблон для аварійного режиму
        return {
            "layout": "emergency_alert",
            "panels": [
                {"type": "header", "title": "EMERGENCY ALERT", "status": "CRITICAL"},
                {"type": "alert", "level": "RED", "message": "SYSTEM CRITICAL FAILURE"},
                {"type": "status", "systems": ["POWER", "LIFE SUPPORT", "COMMUNICATIONS"]},
                {"type": "controls", "buttons": ["INITIATE EMERGENCY PROTOCOLS", "CONTACT STARFLEET"]}
            ],
            "colors": Palette.Red
        }
    
    def GetAITemplate(self):
        # Шаблон для AI режиму
        return {
            "layout": "ai_interface",
            "panels": [
                {"type": "header", "title": "AI CORE INTERFACE", "status": "ONLINE"},
                {"type": "chat", "history": True, "input": True},
                {"type": "monitor", "metrics": ["AI LOAD", "MEMORY", "TOKENS", "RESPONSE TIME"]},
                {"type": "controls", "buttons": ["CLEAR CONTEXT", "OPTIMIZE", "SWITCH MODEL"]}
            ],
            "colors": Palette.Buttons[2:]
        }
    
    def GetBridgeTemplate(self):
        # Шаблон для Bridge режиму
        return {
            "layout": "bridge_interface",
            "panels": [
                {"type": "header", "title": "BRIDGE INTERFACE", "status": "ACTIVE"},
                {"type": "connections", "services": self.AvailableComponents.get("Bridge", [])},
                {"type": "status", "systems": ["AI PROVIDERS", "RUNTIMES", "MODELS"]},
                {"type": "controls", "buttons": ["TEST CONNECTIONS", "RELOAD BRIDGE", "VIEW REGISTRY"]}
            ],
            "colors": Palette.Buttons[1:4]
        }
    
    def AnalyzeSystemState(self):
        # Аналіз поточного стану системи для вибору шаблону
        state = "normal"
        
        # Перевірка стану системи
        if self.SystemState == "CRITICAL":
            state = "emergency"
        elif self.SystemState == "WARNING":
            state = "diagnostic"
        
        # Аналіз доступних компонентів
        if "AI" in str(self.AvailableComponents):
            # AI компоненти доступні
            pass
        
        return state
    
    def GenerateInterface(self, Parent=None, mode="auto"):
        # Генерація інтерфейсу на основі аналізу
        if mode == "auto":
            template_name = self.AnalyzeSystemState()
        else:
            template_name = mode
        
        template = self.InterfaceTemplates.get(template_name, self.InterfaceTemplates["normal"])
        
        return self.BuildInterfaceFromTemplate(template, Parent)
    
    def BuildInterfaceFromTemplate(self, template, Parent):
        # Побудова інтерфейсу з шаблону
        interface = PADD(Parent=Parent, Title="LCARS AUTO INTERFACE", color=template["colors"][0])
        
        Content = interface.Items.get("Content")
        if Content is None:
            return interface
        
        Layout = getattr(Content, "Layout", None)
        if Layout is None:
            Layout = Content.Vertical(0, 0, 0, 0, 0)
        
        # Побудова панелей згідно з шаблоном
        for panel_spec in template["panels"]:
            panel = self.BuildPanel(panel_spec, Content)
            if panel:
                Layout.addWidget(panel.widget)
        
        return interface
    
    def BuildPanel(self, spec, Parent):
        # Побудова окремої панелі з специфікації
        panel_type = spec.get("type")
        
        if panel_type == "header":
            return self.BuildHeaderPanel(spec, Parent)
        elif panel_type == "sidebar":
            return self.BuildSidebarPanel(spec, Parent)
        elif panel_type == "main":
            return self.BuildMainPanel(spec, Parent)
        elif panel_type == "footer":
            return self.BuildFooterPanel(spec, Parent)
        elif panel_type == "monitor":
            return self.BuildMonitorPanel(spec, Parent)
        elif panel_type == "controls":
            return self.BuildControlsPanel(spec, Parent)
        
        return None
    
    def BuildHeaderPanel(self, spec, Parent):
        # Побудова заголовка
        panel = Panel(Parent=Parent)
        panel.widget.setFixedHeight(80)
        panel.widget.setStyleSheet("background-color: #000000; border-bottom: 2px solid #D37445;")
        
        layout = LCARS.Horizontal(panel.widget)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = LCARSLabel(Text=spec.get("title", "LCARS"), Type="title", Parent=panel.widget)
        title.widget.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: 800; letter-spacing: 0.2em;")
        layout.addWidget(title.widget, 1)
        
        status = LCARSLabel(Text=spec.get("status", "ONLINE"), Type="status", Parent=panel.widget)
        status.widget.setStyleSheet("color: #F0B942; font-size: 14px; letter-spacing: 0.15em;")
        layout.addWidget(status.widget)
        
        return panel
    
    def BuildSidebarPanel(self, spec, Parent):
        # Побудова бічної панелі з кнопками
        panel = Panel(Parent=Parent)
        panel.widget.setFixedWidth(180)
        panel.widget.setStyleSheet("background-color: #000000;")
        
        layout = LCARS.Vertical(panel.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Верхній лікоть
        elbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[1], Text="MENU", Parent=panel.widget)
        elbow.widget.setFixedSize(180, 80)
        layout.addWidget(elbow.widget)
        
        # Кнопки меню
        buttons = spec.get("buttons", [])
        for i, button_text in enumerate(buttons):
            color = Palette.Buttons[i % len(Palette.Buttons)]
            button = LCARSButton(Text=button_text, Type="rect", Color="#000000", Parent=panel.widget)
            button.widget.setFixedSize(180, 40)
            button.SetColor(color)
            button.Clicked.Connect(lambda t, cmd=button_text.lower(): self.HandleMenuCommand(cmd))
            layout.addWidget(button.widget)
        
        # Нижній лікоть
        bot_elbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Parent=panel.widget)
        bot_elbow.widget.setFixedSize(180, 80)
        layout.addWidget(bot_elbow.widget)
        
        return panel
    
    def BuildMainPanel(self, spec, Parent):
        # Побудова головної панелі
        panel = Panel(Parent=Parent)
        panel.widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border: 2px solid #6699CC;")
        
        layout = LCARS.Vertical(panel.widget)
        layout.setContentsMargins(15, 15, 15, 15)
        
        content_type = spec.get("content", "terminal")
        
        if content_type == "terminal":
            terminal = LCARS.Terminal(panel.widget)
            terminal.setReadOnly(True)
            terminal.setStyleSheet(
                "background-color: rgba(0, 0, 0, 0.8); color: #FFFFFF; border: 1px solid #606060;"
                "font-size: 14px; font-family: 'JetBrains Mono', 'Consolas', monospace; padding: 15px;"
            )
            terminal.append("LCARS AUTO INTERFACE GENERATOR")
            terminal.append("System analysis complete")
            terminal.append("Interface generated based on system state")
            layout.addWidget(terminal, 1)
        
        return panel
    
    def BuildFooterPanel(self, spec, Parent):
        # Побудова нижньої панелі
        panel = Panel(Parent=Parent)
        panel.widget.setFixedHeight(60)
        panel.widget.setStyleSheet("background-color: #000000; border-top: 2px solid #D37445;")
        
        layout = LCARS.Horizontal(panel.widget)
        layout.setContentsMargins(20, 0, 20, 0)
        
        info = LCARSLabel(Text=spec.get("info", "LCARS SYSTEM"), Type="status", Parent=panel.widget)
        info.widget.setStyleSheet("color: #606060; font-size: 12px; letter-spacing: 0.1em;")
        layout.addWidget(info.widget, 1)
        
        return panel
    
    def BuildMonitorPanel(self, spec, Parent):
        # Побудова панелі моніторингу
        panel = Panel(Parent=Parent)
        panel.widget.setFixedHeight(150)
        panel.widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border: 2px solid #6699CC;")
        
        layout = LCARS.Horizontal(panel.widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        metrics = spec.get("metrics", [])
        for metric in metrics:
            metric_panel = Panel(Parent=panel.widget)
            metric_panel.widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.6); border: 1px solid #606060;")
            
            metric_layout = LCARS.Vertical(metric_panel.widget)
            metric_layout.setContentsMargins(10, 10, 10, 10)
            
            label = LCARSLabel(Text=metric, Type="status", Parent=metric_panel.widget)
            label.widget.setStyleSheet("color: #606060; font-size: 10px; letter-spacing: 0.1em;")
            metric_layout.addWidget(label.widget)
            
            value = LCARSLabel(Text="NORMAL", Type="value", Parent=metric_panel.widget)
            value.widget.setStyleSheet("color: #99CCFF; font-size: 16px; font-weight: 700;")
            metric_layout.addWidget(value.widget)
            
            layout.addWidget(metric_panel.widget, 1)
        
        return panel
    
    def BuildControlsPanel(self, spec, Parent):
        # Побудова панелі керування
        panel = Panel(Parent=Parent)
        panel.widget.setFixedHeight(50)
        panel.widget.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); border: 2px solid #6699CC;")
        
        layout = LCARS.Horizontal(panel.widget)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)
        
        buttons = spec.get("buttons", [])
        for button_text in buttons:
            button = LCARSButton(Text=button_text, Type="rect", Color=Palette.Buttons[1], Parent=panel.widget)
            button.widget.setFixedHeight(30)
            button.Clicked.Connect(lambda t, cmd=button_text: self.HandleControlCommand(cmd))
            layout.addWidget(button.widget)
        
        layout.addStretch()
        return panel
    
    def HandleMenuCommand(self, command):
        # Обробка команд меню
        print(f"MENU COMMAND: {command}")
        ODN.Channel("UI.Command").Emit({"command": command, "source": "auto_interface"})
    
    def HandleControlCommand(self, command):
        # Обробка команд керування
        print(f"CONTROL COMMAND: {command}")
        ODN.Channel("UI.Control").Emit({"command": command, "source": "auto_interface"})


class LCARSAutoBoardTerminal(PADD):
    # LCARS термінал з автоматичною генерацією інтерфейсу
    
    def __init__(self, parent=None, lite=False, ParentNode=None, BoardComputer=None, **kwargs):
        ActualParent = ParentNode or parent or kwargs.get("Parent")
        kwargs.pop("ParentNode", None)
        kwargs.pop("Parent", None)
        kwargs.pop("parent", None)

        TitleVal = kwargs.pop("Title", "LCARS AUTO INTERFACE")
        ColorVal = kwargs.pop("color", Palette.Buttons[0])
        WidthVal = kwargs.pop("width", 1400)
        HeightVal = kwargs.pop("height", 900)
        MinWidthVal = kwargs.pop("minWidth", 1000)
        MinHeightVal = kwargs.pop("minHeight", 600)

        self.Computer = BoardComputer
        self.AutoGenerator = AutoInterfaceGenerator(BoardComputer=BoardComputer)
        
        super().__init__(
            Parent=ActualParent,
            Title=TitleVal,
            color=ColorVal,
            width=WidthVal,
            height=HeightVal,
            minWidth=MinWidthVal,
            minHeight=MinHeightVal,
            **kwargs
        )
        
        self.BuildAutoInterface()
    
    def BuildAutoInterface(self):
        # Побудова автоматичного інтерфейсу
        self.AutoInterface = self.AutoGenerator.GenerateInterface(
            Parent=self.Items.get("Content"),
            mode="auto"
        )
        
        # Додаткове логування
        self.LogInterfaceGeneration()
    
    def LogInterfaceGeneration(self):
        # Логування процесу генерації інтерфейсу
        components = self.AutoGenerator.AvailableComponents
        template_used = self.AutoGenerator.AnalyzeSystemState()
        
        print(f"LCARS AUTO INTERFACE GENERATION COMPLETE")
        print(f"Components detected: {len(components)} categories")
        print(f"Template used: {template_used}")
        print(f"Available components: {list(components.keys())}")

# Експорт
__all__ = ["AutoInterfaceGenerator", "LCARSAutoBoardTerminal"]
