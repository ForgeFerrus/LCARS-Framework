# LCARS FRAMEWORK -- Головний Десктопний Екран Зорельота
# Векторна топологія LCARS. Стандарт Titanium.
# Ідентифікатори: PascalCase, латиниця. Кирилиця -- лише в коментарях та Text= рядках.

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import Screen, Panel
from lcars.base.animation import Blink, DataStream, DiagnosticGrid
from lcars.core.signal import Transmission


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

        # NavMap: (внутрішній ключ Latin, текст кнопки Ukrainian, обробник)
        NavMap = [
            ("WORKSPACE",   "РОБОЧИЙ ПРОСТІР",  self.ActivateWorkspace),
            ("BRIDGE",      "МІСТОК",            self.ActivateBridge),
            ("SYSTEMS",     "СИСТЕМИ",           self.ActivateSystem),
            ("SUPPORT",     "ПІДТРИМКА",         self.ActivateSupport),
            ("MENU",        "МЕНЮ",              self.ActivateMenu),
            ("CONSOLE",     "КОНСОЛЬ",           self.ActivateConsole),
            ("ENGINES",     "ДВИГУНИ",           self.ActivateEngineering),
            ("SCIENCE",     "НАУКА",             self.ActivateScience),
            ("AGENT",       "АГЕНТ",             self.ActivateAgent),
            ("DESIGNER",    "КОНСТРУКТОР",       self.ActivateDesigner),
            ("COMMANDER",   "КОМАНДУВАННЯ",      self.ActivateCommander),
            ("IDE",         "РОЗРОБКА",          self.ActivateIDE),
            ("LOCK",        "БЛОКУВАННЯ",        self.TriggerLock),
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
    # СТОРІНКИ КАМЕРИ
    # -------------------------------------------------------------------------

    def BuildPages(self):
        # Реєстрація всіх векторних сторінок -- ключі Latin, тексти Ukrainian
        PageDefs = [
            ("BRIDGE",     "МІСТОК",           "ГОЛОВНИЙ ТАКТИЧНИЙ МОНІТОР"),
            ("MENU",       "МЕНЮ",             "СИСТЕМНЕ УПРАВЛІННЯ КОМП'ЮТЕРОМ"),
            ("WORKSPACE",  "РОБОЧИЙ ПРОСТІР",  "ОПЕРАТИВНА ЗОНА ОПЕРАТОРА"),
            ("SYSTEMS",    "СИСТЕМИ",          "ДІАГНОСТИКА СИСТЕМ ЗОРЕЛЬОТА"),
            ("SUPPORT",    "ПІДТРИМКА",        "ТЕХНІЧНА ДОПОМОГА ТА ОБСЛУГОВУВАННЯ"),
            ("CONSOLE",    "КОНСОЛЬ",          "ІНТЕРАКТИВНА КОМАНДНА КОНСОЛЬ"),
            ("ENGINES",    "ДВИГУНИ",          "КОНТРОЛЬ ВАРП ТА ІМПУЛЬСНИХ ДВИГУНІВ"),
            ("SCIENCE",    "НАУКА",            "НАУКОВІ ПРИЛАДИ ТА АНАЛІЗ ДАНИХ"),
            ("AGENT",      "АГЕНТ",            "АВТОНОМНИЙ АГЕНТ ЗОРЕЛЬОТА"),
            ("DESIGNER",   "КОНСТРУКТОР",      "ІНТЕРФЕЙС ДИЗАЙНУ LCARS"),
            ("COMMANDER",  "КОМАНДУВАННЯ",     "СТРАТЕГІЧНИЙ КОМАНДНИЙ ЦЕНТР"),
            ("IDE",        "РОЗРОБКА",         "ІНТЕГРОВАНЕ СЕРЕДОВИЩЕ РОЗРОБКИ"),
        ]

        for Key, Title, Subtitle in PageDefs:
            Page = Panel()
            Page.SetVertical(0, 0, 0, 0, Spacing=12)
            Page.Add(LCARSLabel(Text=Title,    FontSize=28, Align="center", Height=60))
            Page.Add(LCARSLabel(Text=Subtitle, FontSize=18, Align="center", Height=32))
            self.Pages[Key] = Page
            self.Chamber.Add(Page)
            Page.hide()

    # -------------------------------------------------------------------------
    # ПЕРЕМИКАННЯ СТОРІНОК
    # -------------------------------------------------------------------------

    def Select(self, Key):
        # Активує сторінку за Latin-ключем, приховує решту
        self.ActivePage = Key
        if self.ModeLabel is not None:
            PageNode = self.Pages.get(Key)
            Title = PageNode.Items.get("0", None) if PageNode else None
            DisplayName = Title.Text if Title and hasattr(Title, "Text") else Key
            self.ModeLabel.SetText("РЕЖИМ // " + DisplayName)
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
