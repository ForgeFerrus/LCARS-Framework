# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: import importlib.util
# Titanium Bridge Migration: from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.base.interface import Segment
from lcars.base.default import Palette

class CentralPanel(Segment):
    def __init__(self, system=None, DesktopNodeRef=None, ParentNode=None, era=None, faction=None):
        super().__init__(Parent=ParentNode)
        self.system = system
        self.DesktopNode = DesktopNodeRef
        self.LoadedPanels = set()
        
        self.widget.setStyleSheet("background-color: #000000;")
        self.Build()

    def Build(self):
        MainLayout = LCARS.Vertical(self.widget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)

        # Header Menu
        HeaderPanel = LCARS.Panel()
        HeaderPanel.setMinimumHeight(64)
        HeaderLayout = LCARS.Horizontal(HeaderPanel)
        HeaderLayout.setContentsMargins(15, 8, 15, 8)
        HeaderLayout.setSpacing(8)

        modes = [
            ("BRIDGE", 0),
            ("STORAGE", 1),
            ("ENGINEERING", 2),
            ("CONSTRUCT", 3),
            ("NAVIGATION", 4),
            ("COMMS", 5),
            ("MEDICAL", 6),
            ("DATABASE", 7),
            ("PROGRAMS", 8),
            ("CONFIG", 9)
        ]
        
        self.ModeButtons = []
        for i, (text, idx) in enumerate(modes):
            col = Palette.Buttons[i % len(Palette.Buttons)]
            btn = LCARSButton(text, Color=col, Parent=HeaderPanel, Height=40)
            btn.clicked.connect(lambda checked, i=idx: self.ActivateMode(i))
            HeaderLayout.addWidget(btn.widget)
            self.ModeButtons.append(btn)

        HeaderLayout.addStretch()

        term_col = Palette.Buttons[-1]
        self.TerminalBtn = LCARSButton("CONSOLE", Color=term_col, Parent=HeaderPanel, Height=40)
        self.TerminalBtn.clicked.connect(self.ToggleTerminal)
        HeaderLayout.addWidget(self.TerminalBtn.widget)

        ai_col = Palette.Buttons[2]
        self.OnboardBtn = LCARSButton("AI TERMINAL", Color=ai_col, Parent=HeaderPanel, Height=40)
        self.OnboardBtn.clicked.connect(lambda checked: self.ActivateMode(10))
        HeaderLayout.addWidget(self.OnboardBtn.widget)

        menu_col = Palette.RedAlert[0]
        self.MenuBtn = LCARSButton("SYSTEM MENU", Color=menu_col, Parent=HeaderPanel, Height=40)
        self.MenuBtn.clicked.connect(self.OpenSystemMenu)
        HeaderLayout.addWidget(self.MenuBtn.widget)

        MainLayout.addWidget(HeaderPanel)

        # Body
        BodyLayout = LCARS.Horizontal()
        BodyLayout.setSpacing(5)

        self.ModeStack = LCARS.Chamber()
        
        mode_names = [m[0] for m in modes]
        for name in mode_names:
            lbl = LCARSLabel(f"◤ {name} — click the mode button to load", Color=Palette.Buttons[1], FontSize=16)
            AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
            if AlignmentFlag:
                lbl.widget.setAlignment(AlignmentFlag.AlignCenter)
            self.ModeStack.addWidget(lbl.widget)

        lbl_onboard = LCARSLabel("◤ AI TERMINAL — click AI button to load", Color=Palette.Buttons[2], FontSize=16)
        AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
        if AlignmentFlag:
            lbl_onboard.widget.setAlignment(AlignmentFlag.AlignCenter)
        self.ModeStack.addWidget(lbl_onboard.widget)

        self.PanelLoaders = {
            0: ("lcars.ui.panels.bridge", "BridgePanel"),
            1: ("lcars.ui.panels.storage", "StoragePanel"),
            2: ("lcars.ui.panels.engineering", "EngineeringPanel"),
            3: ("lcars.engineering.constructor", "InterfaceConstructor"),
            4: ("lcars.ui.panels.navigation", "NavigationPanel"),
            5: ("lcars.ui.panels.communication", "CommunicationPanel"),
            6: ("lcars.ui.panels.medical", "MedicalPanel"),
            7: ("lcars.ui.panels.database", "DatabasePanel"),
            8: ("lcars.ui.panels.programs", "ProgramsPanel"),
            9: ("lcars.ui.panels.config", "ConfigurationPanel"),
            10: ("lcars.ui.onboard", "OnboardComputerDrawer"),
        }

        BodyLayout.addWidget(self.ModeStack, 4)

        # Diagnostic Feed
        diag = LCARS.Panel()
        diag.setStyleSheet("background-color: #050505; border-left: 2px solid #5599FF;")
        dlay = LCARS.Vertical(diag)
        dlay.setContentsMargins(10, 10, 10, 10)
        
        lbl_diag = LCARSLabel("◤ DIAGNOSTIC FEED", Color=Palette.Buttons[1], FontSize=14, Parent=diag)
        dlay.addWidget(lbl_diag.widget)
        
        self.feed = LCARSLabel("◤ SYSTEM: TITAN ACTIVE\n◤ NEURAL LINK: STABLE\n◤ CORE: OPTIMAL\n◤ ACCESS: AUTHORIZED", Color=Palette.Buttons[2], FontSize=14, Parent=diag)
        dlay.addWidget(self.feed.widget)
        dlay.addStretch()
        
        BodyLayout.addWidget(diag, 1)

        MainLayout.addLayout(BodyLayout, 1)

        # Eager-load Bridge
        self.EnsurePanelLoaded(0)
        self.ModeStack.setCurrentIndex(0)

        # Terminal Container
        self.TerminalContainer = LCARS.Panel()
        self.TerminalContainer.setStyleSheet("background-color: #111111; border-top: 2px solid #FF9900;")
        self.TerminalContainer.setVisible(False)
        self.TerminalContainer.setMaximumHeight(0)
        
        t_lay = LCARS.Vertical(self.TerminalContainer)
        t_lay.setContentsMargins(0, 0, 0, 0)

        notice = LCARSLabel("Embedded terminal — click CONSOLE to load", Color="#888888", FontSize=14, Parent=self.TerminalContainer)
        AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
        if AlignmentFlag:
            notice.widget.setAlignment(AlignmentFlag.AlignCenter)
        t_lay.addWidget(notice.widget)

        MainLayout.addWidget(self.TerminalContainer)

        # Footer
        footer = LCARS.Panel()
        footer.setStyleSheet("background-color: #1a1a1a;")
        footer.setMinimumHeight(35)
        flay = LCARS.Horizontal(footer)
        flay.setContentsMargins(15, 5, 15, 5)
        
        lbl_foot = LCARSLabel("◢ LCARS TITAN COMMAND // SYSTEM: ODYSSEY v4.0 // STATUS: NOMINAL", Color="#FFFFFF", FontSize=12, Parent=footer)
        flay.addWidget(lbl_foot.widget)
        flay.addStretch()
        
        MainLayout.addWidget(footer)

    def ToggleTerminal(self):
        visible = self.TerminalContainer.isVisible()
        if visible:
            self.TerminalContainer.setVisible(False)
            self.TerminalContainer.setMaximumHeight(0)
            return

        self.TerminalContainer.setVisible(True)
        avail_h = 420

        if not getattr(self, 'TerminalLoaded', False):
            Spec = importlib.util.find_spec('lcars.ui.terminal')
            if Spec is not None:
                mod = importlib.import_module('lcars.ui.terminal')
                LCARSTerminal = getattr(mod, 'LCARSTerminal', None)
                if LCARSTerminal:
                    self.Terminal = LCARSTerminal(parent=self.TerminalContainer, lite=True)
                    layout = self.TerminalContainer.layout()
                    if layout is not None:
                        while layout.count():
                            item = layout.takeAt(0)
                            w = item.widget() if hasattr(item, 'widget') else None
                            if w: w.deleteLater()
                        terminal_w = getattr(self.Terminal, 'Widget', getattr(self.Terminal, 'widget', self.Terminal))
                        layout.addWidget(terminal_w)
                    self.TerminalLoaded = True

        h = avail_h
        if hasattr(self, 'Terminal') and hasattr(self.Terminal, 'expand_to_parent'):
            h = self.Terminal.expand_to_parent(fraction=0.6, min_height=320) or avail_h
        self.TerminalContainer.setMaximumHeight(h)

        if hasattr(self, 'Terminal') and hasattr(self.Terminal, 'input_line'):
            self.Terminal.input_line.setFocus()

    def OpenSystemMenu(self):
        AccessSpec = importlib.util.find_spec('lcars.ui.views.system_access')
        if AccessSpec is not None:
            mod = importlib.import_module('lcars.ui.views.system_access')
            AccessMenu = getattr(mod, 'AccessMenu', None)
            if AccessMenu:
                if not hasattr(self, 'SystemMenuObj'):
                    self.SystemMenuObj = AccessMenu(event_bus=None, parent=self.widget)
                self.SystemMenuObj.show_menu(floating=True)
                return

        SettingsSpec = importlib.util.find_spec('lcars.ui.views.settings_overlay')
        if SettingsSpec is not None:
            mod = importlib.import_module('lcars.ui.views.settings_overlay')
            SettingsOverlay = getattr(mod, 'SettingsOverlay', None)
            if SettingsOverlay:
                dlg = SettingsOverlay(parent=self.widget)
                dlg.exec()

    def ActivateMode(self, idx: int):
        self.EnsurePanelLoaded(idx)
        self.ModeStack.setCurrentIndex(idx)

    def EnsurePanelLoaded(self, idx: int):
        if idx in self.LoadedPanels:
            return
        loader = self.PanelLoaders.get(idx)
        if not loader:
            self.LoadedPanels.add(idx)
            return

        ModuleName, ClassName = loader
        Spec = importlib.util.find_spec(ModuleName)
        if Spec is None:
            error_lbl = LCARSLabel(f"◤ ERROR: Module not found: {ModuleName}", Color=Palette.RedAlert[0], FontSize=16)
            AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
            if AlignmentFlag:
                error_lbl.widget.setAlignment(AlignmentFlag.AlignCenter)
            self.ModeStack.insertWidget(idx, error_lbl.widget)
            self.LoadedPanels.add(idx)
            return

        mod = importlib.import_module(ModuleName)
        Cls = getattr(mod, ClassName, None)
        if Cls is None:
            error_lbl = LCARSLabel(f"◤ ERROR: Class {ClassName} missing in {ModuleName}", Color=Palette.RedAlert[0], FontSize=16)
            AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
            if AlignmentFlag:
                error_lbl.widget.setAlignment(AlignmentFlag.AlignCenter)
            self.ModeStack.insertWidget(idx, error_lbl.widget)
            self.LoadedPanels.add(idx)
            return
            
        instance = None
        if "bridge" in ModuleName.lower():
            instance = Cls(Parent=self.widget, Era=getattr(self, 'era', None), Faction=getattr(self, 'faction', None))
        else:
            instance = Cls(Parent=self.widget)
            
        old = self.ModeStack.widget(idx)
        
        widget_to_insert = getattr(instance, 'widget', instance)
        if hasattr(widget_to_insert, 'Widget'):
            widget_to_insert = widget_to_insert.Widget
            
        self.ModeStack.insertWidget(idx, widget_to_insert)
        if old is not None:
            old.setParent(None)
            
        self.LoadedPanels.add(idx)
