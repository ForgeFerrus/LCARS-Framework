# LCARS FRAMEWORK — Головний Десктопний Екран Зорельота
# Векторна топологія LCARS без залежностей від застарілих фреймворків.
# Стандарт: Titanium · Ідентифікатори PascalCase · Лише LCARS API

from lcars.base.type import LCARS
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.component import LCARSButton, LCARSBar, LCARSElbow, LCARSLabel, LCARSIndicator
from lcars.base.interface import Screen, Panel
from lcars.base.animation import Blink, DataStream, DiagnosticGrid
from lcars.core.signal import Transmission


# =============================================================================
# LCARS ДЕСКТОП — ГОЛОВНА ОПЕРАЦІЙНА ПОВЕРХНЯ ЗОРЕЛЬОТА
# =============================================================================

class LCARSDesktop(Screen):

    LockRequested = Transmission()

    def Initialize(self, Parent=None):
        super().Initialize(Parent=Parent)
        self.ActivePage = None
        self.Pages = {}
        self.NavItems = {}
        self.ModeLabel = None
        self.Build()

    # ─────────────────────────────────────────────────────────────────────────
    # ВЕКТОРНА ПОБУДОВА ПОВЕРХНІ
    # ─────────────────────────────────────────────────────────────────────────

    def Build(self):
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
        self.Select("МІСТОК")

    # ─────────────────────────────────────────────────────────────────────────
    # ЛІВА НАВІГАЦІЙНА ПАНЕЛЬ
    # ─────────────────────────────────────────────────────────────────────────

    def BuildNavigation(self):
        # Верхня арка навігаційної панелі
        TopArch = LCARSElbow(Corner="top-left", Height=85)
        self.LeftColumn.Add(TopArch)

        # Таблиця навігаційних кнопок: назва → обробник
        NavMap = [
            ("РОБОЧИЙ ПРОСТІР",  self.ActivateWorkspace),
            ("МІСТОК",           self.ActivateBridge),
            ("СИСТЕМИ",          self.ActivateSystem),
            ("ПІДТРИМКА",        self.ActivateSupport),
            ("МЕНЮ",             self.ActivateMenu),
            ("КОНСОЛЬ",          self.ActivateConsole),
            ("ДВИГУНИ",          self.ActivateEngineering),
            ("НАУКА",            self.ActivateScience),
            ("АГЕНТ",            self.ActivateAgent),
            ("КОНСТРУКТОР",      self.ActivateDesigner),
            ("КОМАНДУВАННЯ",     self.ActivateCommander),
            ("РОЗРОБКА",         self.ActivateIDE),
            ("БЛОКУВАННЯ",       self.TriggerLock),
        ]

        for Name, Handler in NavMap:
            Btn = LCARSButton(
                Text=Name,
                Form=LCARSButton.SoftLeftType,
                Height=36,
                FontSize=16,
                Handler=Handler
            )
            self.NavItems[Name] = Btn
            self.LeftColumn.Add(Btn)

        # Нижня арка навігаційної панелі
        BottomArch = LCARSElbow(Corner="bottom-left", Height=61)
        self.LeftColumn.Add(BottomArch)

    # ─────────────────────────────────────────────────────────────────────────
    # ВЕРХНЯ ЗАГОЛОВКОВА ЗОНА
    # ─────────────────────────────────────────────────────────────────────────

    def BuildHeaderZone(self):
        # Рядок загального стану системи
        TopRow = Panel()
        TopRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        self.StatusBar = LCARSIndicator(
            Text="LCARS БОРТОВИЙ КОМ'ЮТЕР // ОНЛАЙН",
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

    # ─────────────────────────────────────────────────────────────────────────
    # КАМЕРА — ОСНОВНА ЗОНА ВМІСТУ
    # ─────────────────────────────────────────────────────────────────────────

    def BuildChamber(self):
        # Центральна камера — векторний контейнер активних сторінок
        self.Chamber = Panel()
        self.Chamber.SetVertical(0, 0, 0, 0, Spacing=4)
        self.RightColumn.Add(self.Chamber, 1)

    # ─────────────────────────────────────────────────────────────────────────
    # НИЖНЯ ЗОНА СТАНУ
    # ─────────────────────────────────────────────────────────────────────────

    def BuildFooterZone(self):
        # Рядок діагностичних показників
        DiagRow = Panel()
        DiagRow.SetHorizontal(0, 0, 0, 0, Spacing=7)

        Metrics = [
            ("ТЕМПЕРАТУРА ЯДРА", "47.2 °C"),
            ("ПОТУЖНІСТЬ",       "12.4 ГВт"),
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

    # ─────────────────────────────────────────────────────────────────────────
    # СТОРІНКИ КАМЕРИ
    # ─────────────────────────────────────────────────────────────────────────

    def BuildPages(self):
        # Реєстрація всіх векторних сторінок у камері вмісту
        PageDefs = [
            ("МІСТОК",           "ГОЛОВНИЙ ТАКТИЧНИЙ МОНІТОР"),
            ("МЕНЮ",             "СИСТЕМНЕ УПРАВЛІННЯ БОРТОВИМ КОМ'ЮТЕРОМ"),
            ("РОБОЧИЙ ПРОСТІР",  "ОПЕРАТИВНА ЗОНА ОПЕРАТОРА"),
            ("СИСТЕМИ",          "ДІАГНОСТИКА ВСІХ СИСТЕМ ЗОРЕЛЬОТА"),
            ("ПІДТРИМКА",        "ТЕХНІЧНА ДОПОМОГА ТА ОБСЛУГОВУВАННЯ"),
            ("КОНСОЛЬ",          "ІНТЕРАКТИВНА КОМАНДНА КОНСОЛЬ LCARS"),
            ("ДВИГУНИ",          "КОНТРОЛЬ ВАРП ТА ІМПУЛЬСНИХ ДВИГУНІВ"),
            ("НАУКА",            "НАУКОВІ ПРИЛАДИ ТА АНАЛІЗ ДАНИХ"),
            ("АГЕНТ",            "АВТОНОМНИЙ АГЕНТ ЗОРЕЛЬОТА"),
            ("КОНСТРУКТОР",      "ІНТЕРФЕЙС ДИЗАЙНУ LCARS"),
            ("КОМАНДУВАННЯ",     "СТРАТЕГІЧНИЙ КОМАНДНИЙ ЦЕНТР"),
            ("РОЗРОБКА",         "ІНТЕГРОВАНЕ СЕРЕДОВИЩЕ РОЗРОБКИ"),
        ]

        for Title, Subtitle in PageDefs:
            Page = Panel()
            Page.SetVertical(0, 0, 0, 0, Spacing=12)
            Page.Add(LCARSLabel(Text=Title,    FontSize=28, Align="center", Height=60))
            Page.Add(LCARSLabel(Text=Subtitle, FontSize=18, Align="center", Height=32))
            self.Pages[Title] = Page
            self.Chamber.Add(Page)
            Page.hide()

    # ─────────────────────────────────────────────────────────────────────────
    # ПЕРЕМИКАННЯ СТОРІНОК
    # ─────────────────────────────────────────────────────────────────────────

    def Select(self, Name):
        self.ActivePage = Name
        if self.ModeLabel:
            self.ModeLabel.SetText("РЕЖИМ // " + Name)
        for PageName, Page in self.Pages.items():
            if PageName == Name:
                Page.show()
            else:
                Page.hide()

    # ─────────────────────────────────────────────────────────────────────────
    # ОБРОБНИКИ НАВІГАЦІЇ
    # ─────────────────────────────────────────────────────────────────────────

    def ActivateWorkspace(self):   self.Select("РОБОЧИЙ ПРОСТІР")
    def ActivateBridge(self):      self.Select("МІСТОК")
    def ActivateSystem(self):      self.Select("СИСТЕМИ")
    def ActivateSupport(self):     self.Select("ПІДТРИМКА")
    def ActivateMenu(self):        self.Select("МЕНЮ")
    def ActivateConsole(self):     self.Select("КОНСОЛЬ")
    def ActivateEngineering(self): self.Select("ДВИГУНИ")
    def ActivateScience(self):     self.Select("НАУКА")
    def ActivateAgent(self):       self.Select("АГЕНТ")
    def ActivateDesigner(self):    self.Select("КОНСТРУКТОР")
    def ActivateCommander(self):   self.Select("КОМАНДУВАННЯ")
    def ActivateIDE(self):         self.Select("РОЗРОБКА")

    def TriggerLock(self):
        # Надіслати сигнал блокування бортового комп'ютера
        self.LockRequested.Emit()
