# Робочі панелі десктопа LCARS.
# Кожна панель оперує реальними модулями ядра. Канонічний стиль:
# периферійні пояси, матові блоки, без заголовків-капсул і без elbow.
# Без docstring і без try/except — тільки короткі коментарі.

import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel, LCARSIndicator
from lcars.base.interface import Segment, Panel, DataBlock, Header
from lcars.core.kernel import Kernel


# Базова панель робочого столу з заголовком і рядком блоків
class WorkPanel(Segment):
    # Ініціалізація панелі з заголовком та вертикальним контейнером
    def __init__(self, KernelRef, ParentChamber, Title):
        super().__init__(Parent=ParentChamber)
        self.KernelRef = KernelRef
        self.Chamber = ParentChamber
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Root = LCARS.Vertical(self.widget)
        self.Root.setContentsMargins(0, 0, 0, 0)
        self.Root.setSpacing(10)
        self.TitleBar = LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=34, Parent=self.widget)
        BarLayout = LCARS.Horizontal(self.TitleBar.widget)
        BarLayout.setContentsMargins(12, 0, 12, 0)
        self.TitleLabel = LCARSLabel(Text=Title, Color=Palette.Background, FontSize=16, Parent=self.TitleBar.widget)
        self.TitleLabel.widget.setStyleSheet("background-color: transparent; border: none;")
        BarLayout.addWidget(self.TitleLabel.widget)
        self.Root.addWidget(self.TitleBar.widget)

    # Створення горизонтального рядка з блоками даних
    def BlockRow(self, Specs):
        Grid = Segment(Parent=self.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(0, 0, 0, 0)
        GridLayout.setSpacing(10)
        Blocks = {}
        for Label, Color in Specs:
            Block = DataBlock(LabelText=Label, ValueText="--", Color=Color, Parent=Grid.widget)
            GridLayout.addWidget(Block.widget, 1)
            Blocks[Label] = Block
        self.Root.addWidget(Grid.widget)
        return Blocks

    # Додавання розтягувача для заповнення вільного простору
    def Stretch(self):
        self.Root.addStretch(1)


# ──────────────────────────────────────────────── SCIENCE
# Панель наукових сенсорів і спектрального аналізу
class SciencePanel(WorkPanel):
    # Ініціалізація панелі науки з сенсорним блоком і журналом
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "SCIENCE // SENSOR GRID")
        self.Blocks = self.BlockRow([("SENSORS", Palette.Buttons[0]), ("SPECTRAL", Palette.Buttons[2]), ("ANALYSIS", Palette.Buttons[3]), ("ARCHIVE", Palette.Buttons[4])])
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(2000)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення даних сенсорів та запис у журнал
    def Refresh(self):
        from lcars.modules.sensor import SensorArray
        Sensors = SensorArray()
        Sensors.SetupStandardGrid()
        Grid = Sensors.PollGrid()
        Count = 0
        if Grid:
            Count = len(Grid) if hasattr(Grid, "__len__") else 0
        self.Blocks["SENSORS"].SetValue(str(Count) + " ACTIVE")
        self.Blocks["SPECTRAL"].SetValue("ONLINE")
        self.Blocks["ANALYSIS"].SetValue("IDLE")
        self.Blocks["ARCHIVE"].SetValue("OPEN")
        self.Log.append("SENSOR SCAN: " + str(Count) + " channels nominal")


# ──────────────────────────────────────────────── NAVIGATION
# Панель навігації та астрометричних даних
class NavigationPanel(WorkPanel):
    # Ініціалізація навігаційної панелі з сектором, заголовком і журналом
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "NAVIGATION // ASTROMETRICS")
        self.Blocks = self.BlockRow([("SECTOR", Palette.Buttons[0]), ("HEADING", Palette.Buttons[1]), ("SPEED", Palette.Buttons[2]), ("RANGE", Palette.Buttons[3])])
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(2500)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення навігаційних даних з астрометричного сервісу
    def Refresh(self):
        Svc = self.KernelRef.Service("astrometrics")
        Status = Svc.GetStatus() if hasattr(Svc, "GetStatus") else {}
        Sector = Status.get("sector", "0-0-0") if isinstance(Status, dict) else "0-0-0"
        Heading = Status.get("heading", "000") if isinstance(Status, dict) else "000"
        self.Blocks["SECTOR"].SetValue(str(Sector))
        self.Blocks["HEADING"].SetValue(str(Heading))
        self.Blocks["SPEED"].SetValue("IMPULSE")
        self.Blocks["RANGE"].SetValue("NOMINAL")
        self.Log.append("PLOT: sector " + str(Sector) + " heading " + str(Heading))


# ──────────────────────────────────────────────── TACTICAL
# Панель тактичної оборони та озброєння
class TacticalPanel(WorkPanel):
    # Ініціалізація тактичної панелі з блоками щитів і зброї
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "TACTICAL // DEFENSE GRID")
        self.Blocks = self.BlockRow([("SHIELDS", Palette.Buttons[0]), ("PHASERS", Palette.Buttons[1]), ("TORPEDOES", Palette.Buttons[2]), ("THREAT", Palette.Buttons[3])])
        self.Blocks["SHIELDS"].SetValue("100%")
        self.Blocks["PHASERS"].SetValue("ARMED")
        self.Blocks["TORPEDOES"].SetValue("READY")
        self.Blocks["THREAT"].SetValue("NONE")
        self.Stretch()


# ──────────────────────────────────────────────── COMM
# Панель зв'язку та мережевих комунікацій
class CommPanel(WorkPanel):
    # Ініціалізація панелі зв'язку з підсистемами hail і subspace
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "COMMUNICATIONS // NETWORK")
        self.Blocks = self.BlockRow([("HAILO", Palette.Buttons[0]), ("SUBSPACE", Palette.Buttons[1]), ("CHANNELS", Palette.Buttons[2]), ("ENCRYPT", Palette.Buttons[3])])
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(3000)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення стану мережі та запис у журнал
    def Refresh(self):
        Net = self.KernelRef.Module("net")
        Status = Net.GetStatus() if hasattr(Net, "GetStatus") else {}
        if isinstance(Status, dict):
            self.Blocks["HAILO"].SetValue(str(Status.get("hail", "OPEN")))
            self.Blocks["SUBSPACE"].SetValue(str(Status.get("subspace", "OPEN")))
            self.Blocks["CHANNELS"].SetValue(str(Status.get("channels", 0)))
            self.Blocks["ENCRYPT"].SetValue(str(Status.get("crypto", "ACTIVE")))
            self.Log.append("NET: " + str(Status))


# ──────────────────────────────────────────────── LIBRARY
# Панель бібліотеки комп'ютерних даних
class LibraryPanel(WorkPanel):
    # Ініціалізація панелі бібліотеки з каталогом та медіа-блоками
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "LIBRARY COMPUTER")
        self.Blocks = self.BlockRow([("CATALOG", Palette.Buttons[0]), ("INDEX", Palette.Buttons[1]), ("MEDIA", Palette.Buttons[2]), ("ACCESS", Palette.Buttons[3])])
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(3000)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення статистики бібліотеки та запис у журнал
    def Refresh(self):
        from lcars.modules.library import LibraryComputer
        Lib = LibraryComputer()
        Stats = Lib.GetStatus() if hasattr(Lib, "GetStatus") else {}
        if isinstance(Stats, dict):
            self.Blocks["CATALOG"].SetValue(str(Stats.get("catalog", 0)))
            self.Blocks["INDEX"].SetValue(str(Stats.get("index", 0)))
            self.Blocks["MEDIA"].SetValue(str(Stats.get("media", 0)))
            self.Blocks["ACCESS"].SetValue(str(Stats.get("access", "ONLINE")))
            self.Log.append("LIB: " + str(Stats))


# ──────────────────────────────────────────────── STORAGE
# Панель сховища даних та ізолінійних банків
class StoragePanel(WorkPanel):
    # Ініціалізація панелі сховища з чіпами та кешем
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "STORAGE // ISOLINEAR BANKS")
        self.Blocks = self.BlockRow([("CHIPS", Palette.Buttons[0]), ("CAPACITY", Palette.Buttons[1]), ("CACHE", Palette.Buttons[2]), ("I/O", Palette.Buttons[3])])
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(3000)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення статистики сховища та запис у журнал
    def Refresh(self):
        from lcars.modules.storage import StorageManager
        Store = StorageManager()
        Stats = Store.GetStatus() if hasattr(Store, "GetStatus") else {}
        if isinstance(Stats, dict):
            self.Blocks["CHIPS"].SetValue(str(Stats.get("chips", 0)))
            self.Blocks["CAPACITY"].SetValue(str(Stats.get("capacity", 0)))
            self.Blocks["CACHE"].SetValue(str(Stats.get("cache", "CLEAN")))
            self.Blocks["I/O"].SetValue(str(Stats.get("io", "IDLE")))
            self.Log.append("STORE: " + str(Stats))


# ──────────────────────────────────────────────── PROGRAMS
# Панель запуску програм та додатків
class ProgramsPanel(WorkPanel):
    # Ініціалізація панелі запуску з кнопками програм
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "PROGRAMS // LAUNCHER")
        Grid = Segment(Parent=self.widget)
        GridLayout = LCARS.Horizontal(Grid.widget)
        GridLayout.setContentsMargins(0, 0, 0, 0)
        GridLayout.setSpacing(10)
        for Name, Color in [("BROWSER", Palette.Buttons[0]), ("CALCULATOR", Palette.Buttons[1]), ("HOLODECK", Palette.Buttons[2]), ("MEDIA", Palette.Buttons[3])]:
            Btn = LCARSButton(Text=Name, Type="pill", Color=Color, Parent=Grid.widget)
            Btn.widget.setFixedSize(200, 56)
            Btn.Clicked.Connect(lambda Checked=False, N=Name: self.Launch(N))
            GridLayout.addWidget(Btn.widget)
        self.Root.addWidget(Grid.widget)
        self.Log = LCARS.Terminal(self.widget)
        self.Log.setReadOnly(True)
        self.Log.setStyleSheet("background-color: #000000; color: " + Palette.Panels[2] + "; border: 1px solid " + Palette.Panels[1] + "; font-family: 'LCARS', Consolas, monospace; font-size: 13px; padding: 10px;")
        self.Root.addWidget(self.Log, 1)
        self.Stretch()

    # Запуск програми через ядро та запис результату
    def Launch(self, Name):
        Proc = self.KernelRef.ProcStart(Name.lower(), Name)
        self.Log.append("LAUNCH: " + Name + " -> " + ("OK" if Proc else "BUSY"))


# ──────────────────────────────────────────────── SETTINGS
# Панель конфігурації системи та параметрів
class SettingsPanel(WorkPanel):
    # Ініціалізація панелі налаштувань з рядками параметрів
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "CONFIG // SYSTEM")
        for Label, Source in [("DISPLAY", "1920x1080"), ("LANGUAGE", "ENG"), ("ALERT STATE", "NOMINAL"), ("PHASE", KernelRef.Phase.name), ("SERVICES", str(len(KernelRef.Services.Names()))), ("MODULES", str(len(KernelRef.ModuleNames())))]:
            Row = Segment(Parent=self.widget)
            RowLayout = LCARS.Horizontal(Row.widget)
            RowLayout.setContentsMargins(0, 0, 0, 0)
            RowLayout.setSpacing(12)
            Name = LCARSLabel(Text=Label, Color=Palette.Buttons[1], FontSize=15, Parent=Row.widget)
            Name.widget.setFixedWidth(200)
            Name.widget.setStyleSheet("background-color: transparent; border: none;")
            RowLayout.addWidget(Name.widget)
            Val = LCARSLabel(Text=Source, Color=Palette.Panels[2], FontSize=15, Parent=Row.widget)
            Val.widget.setStyleSheet("background-color: transparent; border: none;")
            RowLayout.addWidget(Val.widget)
            self.Root.addWidget(Row.widget)
        self.Stretch()


# ──────────────────────────────────────────────── DATABASE
# Панель бази даних та ядра пам'яті
class DatabasePanel(WorkPanel):
    # Ініціалізація панелі БД з блоками сесій та контекстів
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "DATABASE // MEMORY CORE")
        self.Blocks = self.BlockRow([("CHIPS", Palette.Buttons[0]), ("SESSIONS", Palette.Buttons[1]), ("DIALOGS", Palette.Buttons[2]), ("CONTEXTS", Palette.Buttons[3])])
        self.Stretch()
        self.Refresh()
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.setInterval(3000)
        self.Timer.timeout.connect(self.Refresh)
        self.Timer.start()

    # Оновлення статистики пам'яті з модуля memory
    def Refresh(self):
        Mem = self.KernelRef.Module("memory")
        Stats = Mem.GetMemoryStats()
        self.Blocks["CHIPS"].SetValue(str(Stats.get("chips", "--")))
        self.Blocks["SESSIONS"].SetValue(str(Stats.get("sessions", "--")))
        self.Blocks["DIALOGS"].SetValue(str(Stats.get("dialogs", "--")))
        self.Blocks["CONTEXTS"].SetValue(str(Stats.get("contexts", "--")))


# ──────────────────────────────────────────────── MEDICAL
# Панель медичного відділення та стану екіпажу
class MedicalPanel(WorkPanel):
    # Ініціалізація медичної панелі з блоками екіпажу та медицини
    def __init__(self, KernelRef, ParentChamber):
        super().__init__(KernelRef, ParentChamber, "SICKBAY // MEDICAL")
        self.Blocks = self.BlockRow([("CREW", Palette.Buttons[0]), ("SICK", Palette.Buttons[1]), ("MEDICINE", Palette.Buttons[2]), ("GENOME", Palette.Buttons[3])])
        self.Blocks["CREW"].SetValue("1014")
        self.Blocks["SICK"].SetValue("0")
        self.Blocks["MEDICINE"].SetValue("FULL")
        self.Blocks["GENOME"].SetValue("STABLE")
        self.Stretch()
