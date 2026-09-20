# LCARS FRAMEWORK -- Головний Десктопний Екран Зорельота (Демонстрація)
# Векторна топологія LCARS. Стандарт Titanium.
# Ідентифікатори: PascalCase, латиниця. Кирилиця -- лише в коментарях та Text= рядках.

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import Screen, Panel
from lcars.base.animation import Warp, DataStream, DiagnosticGrid, Blink
from lcars.core.signal import Transmission
import importlib.util


# =============================================================================
# LCARS DESKTOP -- головна операційна поверхня зорельота
# =============================================================================

class LCARSDesktop(Screen):

    LockRequested = Transmission()

    def Initialize(self, Parent=None):
        super().Initialize(Parent=Parent)
        self.ActivePage = ""
        self.Pages = {}
        self.NavItems = {}
        self.ModeLabel = None
        self.StatusBar = None
        self.SystemStatus = None
        self.Build()

    # -------------------------------------------------------------------------
    # ВЕКТОРНА ПОБУДОВА ПОВЕРХНІ
    # -------------------------------------------------------------------------

    def Build(self):
        # Горизонтальний розподіл: ліва панель навігації + права зона вмісту
        self.SetHorizontal(18, 18, 18, 18, Spacing=10)

        self.LeftColumn = Panel()
        self.LeftColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.Add(self.LeftColumn)

        self.RightColumn = Panel()
        self.RightColumn.SetVertical(0, 0, 0, 0, Spacing=7)
        self.Add(self.RightColumn, 1)

        self.BuildNavigation()
        self.BuildHeaderZone()
        self.BuildChamber()
        self.BuildFooterZone()
        self.BuildPages()
        self.Select("BRIDGE")

    # -------------------------------------------------------------------------
    # ЛІВА НАВІГАЦІЙНА ПАНЕЛЬ
    # -------------------------------------------------------------------------

    def BuildNavigation(self):
        # Верхня арка лівої панелі
        self.LeftColumn.Add(LCARSElbow(Corner="top-left", Height=85))

        # NavMap: (внутрішній Latin-ключ, текст кнопки, обробник)
        NavMap = [
            ("WORKSPACE",  "РОБОЧИЙ ПРОСТІР",  self.ActivateWorkspace),
            ("BRIDGE",     "МІСТОК",            self.ActivateBridge),
            ("SYSTEMS",    "СИСТЕМИ",           self.ActivateSystem),
            ("SUPPORT",    "ПІДТРИМКА",         self.ActivateSupport),
            ("MENU",       "МЕНЮ",              self.ActivateMenu),
            ("CONSOLE",    "КОНСОЛЬ",           self.ActivateConsole),
            ("ENGINES",    "ДВИГУНИ",           self.ActivateEngineering),
            ("SCIENCE",    "НАУКА",             self.ActivateScience),
            ("AGENT",      "АГЕНТ",             self.ActivateAgent),
            ("DESIGNER",   "КОНСТРУКТОР",       self.ActivateDesigner),
            ("COMMANDER",  "КОМАНДУВАННЯ",      self.ActivateCommander),
            ("IDE",        "РОЗРОБКА",          self.ActivateIDE),
            ("LOCK",       "БЛОКУВАННЯ",        self.TriggerLock),
        ]

        for Key, Label, Handler in NavMap:
            Btn = LCARSButton(
                Text=Label,
                Form=LCARSButton.SoftLeftType,
                Height=36,
                FontSize=16,
                Handler=Handler
            )
            self.NavItems[Key] = Btn
            self.LeftColumn.Add(Btn)

        # Нижня арка лівої панелі
        self.LeftColumn.Add(LCARSElbow(Corner="bottom-left", Height=61))

    # -------------------------------------------------------------------------
    # ВЕРХНЯ ЗАГОЛОВКОВА ЗОНА
    # -------------------------------------------------------------------------

    def BuildHeaderZone(self):
        # Рядок загального стану системи
        TopRow = Panel()
        TopRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.StatusBar = LCARSIndicator(
            Text="LCARS БОРТОВИЙ КОМП'ЮТЕР // ОНЛАЙН",
            Form=LCARSIndicator.RectLeftType,
            FontSize=18,
            Height=52
        )
        TopRow.Add(self.StatusBar, 1)
        TopRow.Add(LCARSBar(Form=LCARSBar.RectType, Width=72, Height=52))
        self.RightColumn.Add(TopRow)

        # Рядок поточного режиму
        ModeRow = Panel()
        ModeRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.ModeLabel = LCARSIndicator(
            Text="РЕЖИМ // МІСТОК",
            Form=LCARSIndicator.RectLeftType,
            FontSize=16,
            Height=32
        )
        ModeRow.Add(self.ModeLabel, 1)
        ModeRow.Add(LCARSBar(Form=LCARSBar.PillHalfType, Width=180, Height=32))
        self.RightColumn.Add(ModeRow)

    # -------------------------------------------------------------------------
    # КАМЕРА -- ОСНОВНА ЗОНА ВМІСТУ
    # -------------------------------------------------------------------------

    def BuildChamber(self):
        # Центральна камера -- векторний контейнер активних сторінок
        self.Chamber = Panel()
        self.Chamber.SetVertical(0, 0, 0, 0, Spacing=4)
        self.RightColumn.Add(self.Chamber, 1)

    # -------------------------------------------------------------------------
    # НИЖНЯ ЗОНА СТАНУ
    # -------------------------------------------------------------------------

    def BuildFooterZone(self):
        # Рядок діагностичних показників зорельота
        DiagRow = Panel()
        DiagRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        Metrics = [
            ("ТЕМПЕРАТУРА ЯДРА", "47.2 C"),
            ("ПОТУЖНІСТЬ",       "12.4 GW"),
            ("СУБПРОСТІР",       "НОМІНАЛ"),
            ("ЗАХИСНІ ПОЛЯ",     "ГОТОВНІСТЬ"),
            ("СЕНСОРНИЙ МАСИВ",  "АКТИВНИЙ"),
        ]

        for Caption, Reading in Metrics:
            Tile = Panel()
            Tile.SetVertical(0, 0, 0, 0, Spacing=2)
            Tile.Add(LCARSLabel(Text=Caption,  FontSize=16, Height=20))
            Tile.Add(LCARSLabel(Text=Reading,  FontSize=18, Height=24))
            DiagRow.Add(Tile, 1)

        self.RightColumn.Add(DiagRow)

        # Нижній рядок статусу з кутовою аркою
        StatusRow = Panel()
        StatusRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.SystemStatus = LCARSIndicator(
            Text="ГОЛОВНИЙ ЕКРАН ОНЛАЙН // ШТАТНИЙ РЕЖИМ",
            Form=LCARSIndicator.RectLeftType,
            FontSize=16,
            Height=36
        )
        StatusRow.Add(self.SystemStatus, 1)
        StatusRow.Add(LCARSElbow(Corner="bottom-right", Width=160, Height=36))
        self.RightColumn.Add(StatusRow)

    # -------------------------------------------------------------------------
    # ПОБУДОВА СТОРІНОК КАМЕРИ
    # -------------------------------------------------------------------------

    def BuildPages(self):
        # Сторінка BRIDGE: варп-анімація + потік даних
        self.Pages["BRIDGE"] = self.BuildBridgePage()

        # Сторінка MENU: кнопки застосунків
        self.Pages["MENU"] = self.BuildMenuPage()

        # Сторінка SYSTEMS: діагностика або заглушка
        self.Pages["SYSTEMS"] = self.BuildSystemPage()

        # Сторінка CONSOLE: термінал бортового комп'ютера
        self.Pages["CONSOLE"] = self.BuildConsolePage()

        # Сторінка SCIENCE: потік наукових даних
        self.Pages["SCIENCE"] = self.BuildSciencePage()

        # Сторінка ENGINES: контроль двигунів
        self.Pages["ENGINES"] = self.BuildEnginesPage()

        # Решта сторінок -- базові панелі
        for Key in ("WORKSPACE", "SUPPORT", "AGENT", "DESIGNER", "COMMANDER", "IDE"):
            self.Pages[Key] = self.BuildGenericPage(Key)

        # Всі сторінки додаються до камери і ховаються
        for Page in self.Pages.values():
            self.Chamber.Add(Page)
            Page.hide()

    # -------------------------------------------------------------------------
    # СТОРІНКА МІСТОК
    # -------------------------------------------------------------------------

    def BuildBridgePage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)

        # Верхній заголовок
        Page.Add(LCARSLabel(Text="МІСТОК", FontSize=28, Align="center", Height=48))

        # Тіло: варп-анімація зліва + потік даних справа
        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=16)

        Stars = Warp(
            Color="#D9E8FF",
            Width=900,
            Height=480,
            StarCount=170,
            Running=True
        )
        Body.Add(Stars, 1)

        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=10)

        Stream = DataStream(
            Color=Palette.Buttons[1],
            Width=320,
            Height=220,
            Running=True
        )
        Side.Add(Stream)
        Side.Add(LCARSLabel(Text="РОЗТАШУВАННЯ: СОЛ СИСТЕМА", FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="СТАТУС: ВСІ СИСТЕМИ НОМІНАЛ", FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="ЕКІПАЖ: АКТИВНИЙ", FontSize=16, Height=28))
        Body.Add(Side)

        Page.Add(Body, 1)

        # Кнопки управління двигунами
        Controls = Panel()
        Controls.SetHorizontal(0, 0, 0, 0, Spacing=10)

        BtnImpulse = LCARSButton(
            Text="ІМПУЛЬС",
            Form=LCARSButton.PillType,
            Height=44,
            FontSize=18,
            Handler=lambda: Stars.SetWarpSpeed(False)
        )
        BtnWarp = LCARSButton(
            Text="ВАРП",
            Form=LCARSButton.PillType,
            Height=44,
            FontSize=18,
            Handler=lambda: Stars.SetWarpSpeed(True)
        )
        Controls.Add(BtnImpulse)
        Controls.Add(BtnWarp)
        Page.Add(Controls)

        return Page

    # -------------------------------------------------------------------------
    # СТОРІНКА МЕНЮ ЗАСТОСУНКІВ
    # -------------------------------------------------------------------------

    def BuildMenuPage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        Page.Add(LCARSLabel(Text="ЗАСТОСУНКИ", FontSize=28, Align="center", Height=48))

        Grid = Panel()
        Grid.SetHorizontal(16, 16, 16, 16, Spacing=24)

        Col1 = Panel()
        Col1.SetVertical(0, 0, 0, 0, Spacing=16)
        Col2 = Panel()
        Col2.SetVertical(0, 0, 0, 0, Spacing=16)

        AppList1 = [
            ("ДВИГУНИ",    self.ActivateEngineering),
            ("НАУКА",      self.ActivateScience),
            ("КОНСОЛЬ",    self.ActivateConsole),
            ("АГЕНТ",      self.ActivateAgent),
        ]
        AppList2 = [
            ("СИСТЕМИ",      self.ActivateSystem),
            ("КОНСТРУКТОР",  self.ActivateDesigner),
            ("ЗВ'ЯЗОК",      None),
            ("БАЗА ДАНИХ",   None),
        ]

        for Index, (Label, Handler) in enumerate(AppList1):
            Col1.Add(LCARSButton(
                Text=Label,
                Form=LCARSButton.RectLeftType,
                Height=70,
                FontSize=20,
                Handler=Handler
            ))

        for Index, (Label, Handler) in enumerate(AppList2):
            Col2.Add(LCARSButton(
                Text=Label,
                Form=LCARSButton.RectLeftType,
                Height=70,
                FontSize=20,
                Handler=Handler
            ))

        Grid.Add(Col1, 1)
        Grid.Add(Col2, 1)
        Page.Add(Grid, 1)
        return Page

    # -------------------------------------------------------------------------
    # СТОРІНКА СИСТЕМ
    # -------------------------------------------------------------------------

    def BuildSystemPage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        Page.Add(LCARSLabel(Text="ДІАГНОСТИКА СИСТЕМ", FontSize=28, Align="center", Height=48))

        if importlib.util.find_spec("lcars.ui.panels.access") is not None:
            from lcars.ui.panels.access import SystemAccess
            SystemPanel = SystemAccess()
            Page.Add(SystemPanel, 1)
        else:
            Page.Add(LCARSLabel(Text="МОДУЛЬ СИСТЕМНОГО ДОСТУПУ НЕ ЗНАЙДЕНО", FontSize=18, Align="center", Height=48))
            Grid = DiagnosticGrid(Width=600, Height=300, Running=True)
            Page.Add(Grid, 1)

        return Page

    # -------------------------------------------------------------------------
    # СТОРІНКА КОНСОЛІ
    # -------------------------------------------------------------------------

    def BuildConsolePage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=8)
        Page.Add(LCARSLabel(Text="КОМАНДНА КОНСОЛЬ", FontSize=28, Align="center", Height=48))

        # Потік даних як фон консолі
        Stream = DataStream(
            Color=Palette.Buttons[3],
            Width=800,
            Height=320,
            Running=True
        )
        Page.Add(Stream, 1)

        # Рядок швидких команд
        Commands = Panel()
        Commands.SetHorizontal(0, 0, 0, 0, Spacing=8)

        for Label in ("СТАТУС", "ДОПОМОГА", "ДІАГНОСТИКА", "ПЕРЕВІРКА"):
            Commands.Add(LCARSButton(
                Text=Label,
                Form=LCARSButton.PillType,
                Height=36,
                FontSize=16
            ))

        Page.Add(Commands)
        return Page

    # -------------------------------------------------------------------------
    # СТОРІНКА НАУКИ
    # -------------------------------------------------------------------------

    def BuildSciencePage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        Page.Add(LCARSLabel(Text="НАУКОВИЙ ВІДДІЛ", FontSize=28, Align="center", Height=48))

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=16)

        Stream = DataStream(
            Color=Palette.Buttons[2],
            Width=520,
            Height=380,
            Running=True
        )
        Body.Add(Stream, 1)

        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=10)
        Side.Add(LCARSLabel(Text="СЕНСОРИ: ПАСИВНІ",    FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="СИМУЛЯЦІЯ: ОЧІКУЄ",   FontSize=16, Height=28))
        Side.Add(LCARSLabel(Text="КВАНТОВИЙ: РЕЗЕРВ",   FontSize=16, Height=28))
        Body.Add(Side)

        Page.Add(Body, 1)
        return Page

    # -------------------------------------------------------------------------
    # СТОРІНКА ДВИГУНІВ
    # -------------------------------------------------------------------------

    def BuildEnginesPage(self):
        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        Page.Add(LCARSLabel(Text="ДВИГУНИ ЗОРЕЛЬОТА", FontSize=28, Align="center", Height=48))

        Grid = DiagnosticGrid(Width=700, Height=360, Running=True)
        Page.Add(Grid, 1)

        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=10)
        Row.Add(LCARSLabel(Text="ВАРП: ГОТОВНІСТЬ",    FontSize=18, Height=32))
        Row.Add(LCARSLabel(Text="ІМПУЛЬС: АКТИВНИЙ",   FontSize=18, Height=32))
        Row.Add(LCARSLabel(Text="ДЕФЛЕКТОР: НОМІНАЛ",  FontSize=18, Height=32))
        Page.Add(Row)
        return Page

    # -------------------------------------------------------------------------
    # ЗАГАЛЬНА СТОРІНКА-ЗАГЛУШКА
    # -------------------------------------------------------------------------

    def BuildGenericPage(self, Key):
        # Відображення назви сторінки та стану готовності модуля
        Labels = {
            "WORKSPACE":  ("РОБОЧИЙ ПРОСТІР",    "ОПЕРАТИВНА ЗОНА ОПЕРАТОРА"),
            "SUPPORT":    ("ПІДТРИМКА",           "ТЕХНІЧНА ДОПОМОГА ТА ОБСЛУГОВУВАННЯ"),
            "AGENT":      ("АГЕНТ",               "АВТОНОМНИЙ АГЕНТ ЗОРЕЛЬОТА"),
            "DESIGNER":   ("КОНСТРУКТОР",         "ІНТЕРФЕЙС ДИЗАЙНУ LCARS"),
            "COMMANDER":  ("КОМАНДУВАННЯ",        "СТРАТЕГІЧНИЙ КОМАНДНИЙ ЦЕНТР"),
            "IDE":        ("РОЗРОБКА",            "ІНТЕГРОВАНЕ СЕРЕДОВИЩЕ РОЗРОБКИ"),
        }
        Title, Subtitle = Labels.get(Key, (Key, "МОДУЛЬ ІНІЦІАЛІЗУЄТЬСЯ"))

        Page = Panel()
        Page.SetVertical(0, 0, 0, 0, Spacing=12)
        Page.Add(LCARSLabel(Text=Title,    FontSize=28, Align="center", Height=60))
        Page.Add(LCARSLabel(Text=Subtitle, FontSize=18, Align="center", Height=32))
        return Page

    # -------------------------------------------------------------------------
    # ПЕРЕМИКАННЯ СТОРІНОК
    # -------------------------------------------------------------------------

    def Select(self, Key):
        # Активує сторінку за Latin-ключем, приховує решту
        self.ActivePage = Key
        if self.ModeLabel is not None and Key in self.Pages:
            Labels = {
                "BRIDGE":    "МІСТОК",
                "MENU":      "МЕНЮ",
                "WORKSPACE": "РОБОЧИЙ ПРОСТІР",
                "SYSTEMS":   "СИСТЕМИ",
                "SUPPORT":   "ПІДТРИМКА",
                "CONSOLE":   "КОНСОЛЬ",
                "ENGINES":   "ДВИГУНИ",
                "SCIENCE":   "НАУКА",
                "AGENT":     "АГЕНТ",
                "DESIGNER":  "КОНСТРУКТОР",
                "COMMANDER": "КОМАНДУВАННЯ",
                "IDE":       "РОЗРОБКА",
            }
            self.ModeLabel.SetText("РЕЖИМ // " + Labels.get(Key, Key))
        for PageKey, Page in self.Pages.items():
            if PageKey == Key:
                Page.show()
            else:
                Page.hide()

    # -------------------------------------------------------------------------
    # ОБРОБНИКИ НАВІГАЦІЇ
    # -------------------------------------------------------------------------

    def ActivateWorkspace(self):   self.Select("WORKSPACE")
    def ActivateBridge(self):      self.Select("BRIDGE")
    def ActivateSystem(self):      self.Select("SYSTEMS")
    def ActivateSupport(self):     self.Select("SUPPORT")
    def ActivateMenu(self):        self.Select("MENU")
    def ActivateConsole(self):     self.Select("CONSOLE")
    def ActivateEngineering(self): self.Select("ENGINES")
    def ActivateScience(self):     self.Select("SCIENCE")
    def ActivateAgent(self):       self.Select("AGENT")
    def ActivateDesigner(self):    self.Select("DESIGNER")
    def ActivateCommander(self):   self.Select("COMMANDER")
    def ActivateIDE(self):         self.Select("IDE")

    def TriggerLock(self):
        # Надіслати сигнал блокування бортового комп'ютера
        self.LockRequested.Emit()


# =============================================================================
# ТОЧКА ВХОДУ ДЛЯ ЗАПУСКУ ДЕМОНСТРАЦІЇ
# =============================================================================

def Build(Parent=None):
    return LCARSDesktop(Parent=Parent)


def Run():
    App = LCARS.Application
    if App is None:
        return 1
    Instance = App.instance() or App([])
    Desktop = Build()
    Desktop.ShowFullScreen()
    return Instance.exec()


if __name__ == "__main__":
    Run()
