import sys
import importlib
import importlib.util
from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.base.interface import Segment
from lcars.base.default import Palette

# Головна панель центру — відображає міст та діагностичний канал
class CentralPanel(Segment):
    # Ініціалізація панелі з системою, робочим столом та параметрами ери
    def __init__(self, system=None, DesktopNodeRef=None, ParentNode=None, era=None, faction=None):
        super().__init__(Parent=ParentNode)
        self.system = system
        self.DesktopNode = DesktopNodeRef
        self.LoadedPanels = set()
        
        self.widget.setStyleSheet("background-color: #000000;")
        self.Build()

    # Побудова основного інтерфейсу панелі
    def Build(self):
        MainLayout = LCARS.Vertical(self.widget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)

        # Меню заголовку видалено для чистого вигляду LCARS
        # Модулі доступні через головну ліву навігацію робочого столу або меню програм

        # Тіло панелі
        BodyLayout = LCARS.Horizontal()
        BodyLayout.setSpacing(5)

        # Динамічний імпорт мосту без використання try/except
        BridgePanel = None
        BridgeSpec = importlib.util.find_spec('lcars.ui.panels.bridge')
        if BridgeSpec is not None:
            BridgeMod = importlib.import_module('lcars.ui.panels.bridge')
            BridgePanel = getattr(BridgeMod, 'BridgePanel', None)

        if BridgePanel:
            self.BridgeView = BridgePanel(DesktopNodeRef=self.DesktopNode, ParentNode=self)
            bridge_widget = self.BridgeView.widget if hasattr(self.BridgeView, "widget") else self.BridgeView
            BodyLayout.addWidget(bridge_widget, 4)
        else:
            lbl = LCARSLabel("◤ BRIDGE FAILED TO LOAD", Color=Palette.RedAlert[0], FontSize=16)
            AlignmentFlag = getattr(LCARS.Protocol, "AlignmentFlag", None)
            if AlignmentFlag:
                lbl.widget.setAlignment(AlignmentFlag.AlignCenter)
            BodyLayout.addWidget(lbl.widget, 4)

        # Канал діагностики
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

        # Контейнер терміналу
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

        # Нижній колонтитул
        footer = LCARS.Panel()
        footer.setStyleSheet("background-color: #1a1a1a;")
        footer.setMinimumHeight(35)
        flay = LCARS.Horizontal(footer)
        flay.setContentsMargins(15, 5, 15, 5)
        
        lbl_foot = LCARSLabel("◢ LCARS TITAN COMMAND // SYSTEM: ODYSSEY v4.0 // STATUS: NOMINAL", Color="#FFFFFF", FontSize=12, Parent=footer)
        flay.addWidget(lbl_foot.widget)
        flay.addStretch()
        
        MainLayout.addWidget(footer)

    # Перемикання видимості вбудованого терміналу
    def ToggleTerminal(self):
        visible = self.TerminalContainer.isVisible()
        if visible:
            self.TerminalContainer.setVisible(False)
            self.TerminalContainer.setMaximumHeight(0)
            return

        self.TerminalContainer.setVisible(True)
        avail_h = 420

        # Динамічне завантаження терміналу при першому виклику
        if not getattr(self, 'TerminalLoaded', False):
            LCARSTerminal = None
            Spec = importlib.util.find_spec('lcars.ui.terminal')
            if Spec is not None:
                mod = importlib.import_module('lcars.ui.terminal')
                LCARSTerminal = getattr(mod, 'LCARSTerminal', None)

            if LCARSTerminal:
                self.Terminal = LCARSTerminal(parent=self.TerminalContainer, lite=True)
                layout = self.TerminalContainer.layout()
                if layout is not None:
                    # Очищення попереднього вмісту контейнера
                    while layout.count():
                        item = layout.takeAt(0)
                        w = item.widget() if hasattr(item, 'widget') else None
                        if w:
                            w.deleteLater()
                    terminal_w = getattr(self.Terminal, 'Widget', getattr(self.Terminal, 'widget', self.Terminal))
                    layout.addWidget(terminal_w)
                self.TerminalLoaded = True

        h = avail_h
        if hasattr(self, 'Terminal') and hasattr(self.Terminal, 'ExpandToParent'):
            h = self.Terminal.ExpandToParent(Fraction=0.6, MinimumHeight=320) or avail_h
        self.TerminalContainer.setMaximumHeight(h)

        if hasattr(self, 'Terminal') and hasattr(self.Terminal, 'input_line'):
            self.Terminal.input_line.setFocus()

    # Відкриття меню доступу до системи
    def OpenSystemMenu(self):
        # Динамічний імпорт меню доступу до системи
        AccessMenu = None
        AccessSpec = importlib.util.find_spec('lcars.ui.views.system_access')
        if AccessSpec is not None:
            mod = importlib.import_module('lcars.ui.views.system_access')
            AccessMenu = getattr(mod, 'AccessMenu', None)

        if AccessMenu:
            if not hasattr(self, 'SystemMenuObj'):
                self.SystemMenuObj = AccessMenu(event_bus=None, parent=self.widget)
            self.SystemMenuObj.show_menu(floating=True)
            return

        # Запасний варіант — накладання налаштувань
        SettingsOverlay = None
        SettingsSpec = importlib.util.find_spec('lcars.ui.views.settings_overlay')
        if SettingsSpec is not None:
            mod = importlib.import_module('lcars.ui.views.settings_overlay')
            SettingsOverlay = getattr(mod, 'SettingsOverlay', None)

        if SettingsOverlay:
            if not hasattr(self, 'SettingsObj'):
                self.SettingsObj = SettingsOverlay(parent=self.widget)
            self.SettingsObj.show()
