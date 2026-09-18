# ◤ TITANIUM SYSTEM BIOS & UEFI BOOT CONTROLLER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/bios.py
# ОПИС: Низькорівневий системний рівень ініціалізації, перевірки та керування
#       таблицею завантаження зорельота LCARS (BIOS / UEFI Core).
#       LCARS BIOS не є операційною системою загального призначення, а виступає
#       першим керуючим шаром LCARS після старту процесу: перевірка середовища (POST),
#       таблиця завантаження (UEFI), системні політики оболонки, перехід в аварійний контур.
# ПЕРЕВІРКИ POST (9 КРОКІВ):
# 1. PYTHON RUNTIME — перевірка версії інтерпретатора (>= 3.10).
# 2. CORE MODULE MAP — наявність фундаментальних модулів ядра.
# 3. ODN TRANSMISSION BUS — доступність шини оптичних даних та чорної скриньки.
# 4. ISOLINEAR CHIP CATALOG — каталог ізолінійних чіпів пам'яті.
# 5. REQUIRED DATA CHIPS — наявність критичних чіпів (BlackBox, BiosCore, Network, Memory, Logbook).
# 6. BIOS CONFIGURATION — перевірка валідності системних налаштувань.
# 7. UEFI BOOT POLICY — перевірка записів та цілей завантаження.
# 8. RECOVERY POLICY — політика поведінки при збоях.
# 9. BIOS CONFIG CHIP — доступність сховища конфігурації.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from lcars.base.type import LCARS, SystemComponent
from lcars.core.signal import ODN, Transmission
from lcars.base.info import Version
from lcars.modules.storage import FindChip, ListChips, ResolveChipPath
from lcars.system.software import BootEntry, BootTarget, HardwareProfile, FirmwareConfig

# Регулярні вирази для валідації JSON-типів без використання try/except
JsonNumberRegex = LCARS.System.Regex.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")
JsonBoolNullRegex = LCARS.System.Regex.compile(r"^(true|false|null)$")
JsonStringRegex = LCARS.System.Regex.compile(r'^".*"$')

def SafeJsonLoads(Text: str, Default: LCARS.Typing.Any = None) -> LCARS.Typing.Any:
    # Безпечне розкодування JSON-рядків без застосування try/except блоків.
    # Здійснює поетапний синтаксичний аналіз тексту за регулярними виразами.
    if not isinstance(Text, str) or not Text.strip():
        return Default if Default is not None else Text
    Stripped = Text.strip()
    FirstChar = Stripped[0]
    CouldBeJson = (
        FirstChar in ("{", "[", '"')
        or FirstChar.isdigit()
        or FirstChar in ("-", "t", "f", "n")
    )
    if not CouldBeJson:
        return Text
    if JsonNumberRegex.match(Stripped):
        return float(Stripped) if "." in Stripped or "e" in Stripped.lower() else int(Stripped)
    if JsonBoolNullRegex.match(Stripped):
        if Stripped == "true":
            return True
        if Stripped == "false":
            return False
        return None
    if JsonStringRegex.match(Stripped):
        return Stripped[1:-1]
    if FirstChar == "{" and not Stripped.endswith("}"):
        return Text
    if FirstChar == "[" and not Stripped.endswith("]"):
        return Text
    JsonModule = LCARS.Import("json")
    Decoder = JsonModule.JSONDecoder()
    Result, EndIdx = Decoder.raw_decode(Stripped)
    if EndIdx == len(Stripped):
        return Result
    return Text
# ═════════════════════════════════════════════════════════════════════
# 1. СИСТЕМНІ СТРУКТУРИ ТА ПАРАМЕТРИ НАЛАШТУВАНЬ BIOS
# ═════════════════════════════════════════════════════════════════════
class BiosSetting(LCARS):
    # Окремий системний параметр BIOS/UEFI з валідацією варіантів вибору
    Name: str = ""
    Value: LCARS.Typing.Any = None
    Options: LCARS.Typing.List[LCARS.Typing.Any] = LCARS.Field(default_factory=list)
    Locked: bool = False
    Section: str = "SYSTEM"
    Description: str = ""

class BiosCheck(LCARS):
    # Окремий діагностичний пункт перевірки POST
    Name: str = ""
    Status: str = ""
    Detail: str = ""
    Critical: bool = True

class BiosReport(LCARS):
    # Підсумковий звіт діагностики POST для екранів запуску, логів та чорної скриньки
    Status: str = ""
    Checks: LCARS.Typing.List[BiosCheck] = LCARS.Field(default_factory=list)
    Settings: LCARS.Typing.Dict[str, LCARS.Typing.Any] = LCARS.Field(default_factory=dict)
    Started: float = 0.0
    Finished: float = 0.0

    def Lines(self) -> LCARS.Typing.List[str]:
        # Формування текстового протоколу POST для терміналу
        Lines = [
            "LCARS BIOS CORE",
            "VERSION :: " + str(Version.Release),
            "STATUS :: " + self.Status,
        ]
        for Check in self.Checks:
            Detail = " :: " + Check.Detail if Check.Detail else ""
            Lines.append(Check.Name + " :: " + Check.Status + Detail)
        return Lines

# ═════════════════════════════════════════════════════════════════════
# 2. ПІДСИСТЕМА UEFI ТА ПОЛІТИКИ ЗАВАНТАЖЕННЯ (BOOT POLICY)
# ═════════════════════════════════════════════════════════════════════
class UEFI(LCARS):
    # UEFI-рівень зорельота відповідає за вибір та керування записами запуску

    def Entries(self) -> LCARS.Typing.List[LCARS.Typing.Dict[str, LCARS.Typing.Any]]:
        # Повертає список доступних записів завантаження
        return self.Owner.GetBootEntries()

    def Target(self) -> str:
        # Поточна цільова підсистема запуску
        return self.Owner.Get("Target", BootTarget.DESKTOP)

    def SecureBoot(self) -> bool:
        # Перевірка чи активовано режим безпечного завантаження
        return bool(self.Owner.Get("SecureBoot", True))

    def BootOrder(self) -> LCARS.Typing.List[str]:
        # Поточний пріоритетний порядок завантаження
        Order = self.Owner.Get("BootOrder", [])
        return list(Order) if isinstance(Order, list) else []

    def SelectTarget(self, Target: str) -> bool:
        # Встановлення активної цілі завантаження
        return self.Owner.SelectBootTarget(Target)

    def AddEntry(self, Name: str, Description: str, Target: str, Secure: bool = True) -> bool:
        # Додавання нового запису в таблицю завантаження
        return self.Owner.AddBootEntry(Name, Description, Target, Secure)

    def RemoveEntry(self, Name: str) -> bool:
        # Вилучення запису завантаження
        return self.Owner.RemoveBootEntry(Name)

    def SetDefault(self, Name: str) -> bool:
        # Встановлення запису за замовчуванням
        return self.Owner.SetDefaultBootEntry(Name)

    def Firmware(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Отримання повної конфігурації низькорівневої прошивки
        return self.Owner.BuildFirmwareConfig().ToDict()

    def GetManifest(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Системний маніфест UEFI для передачі графічним панелям налаштувань
        return {
            "Target": self.Target(),
            "SecureBoot": self.SecureBoot(),
            "BootOrder": self.BootOrder(),
            "Entries": self.Entries(),
            "Firmware": self.Firmware(),
        }

    # Аліас сумісності
    Payload = GetManifest

# ═════════════════════════════════════════════════════════════════════
# 3. ПОЛІТИКИ СИСТЕМИ LCARS (LCARS POLICY)
# ═════════════════════════════════════════════════════════════════════
class LCARSPolicy(LCARS):
    # Опис глобальних системних політик інтерфейсу, мови та відновлення
    def __init__(self, Owner: "BIOS"):
        super().__init__(Id="LCARSPolicy")
        self.Owner = Owner

    def DisplayPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика параметрів дисплеїв та графічних панелей
        return {
            "Resolution": self.Owner.Get("Resolution", "1920X1080"),
            "RefreshRate": self.Owner.Get("RefreshRate", "60 HZ"),
            "Fullscreen": self.Owner.Get("Fullscreen", True),
        }

    def IdentityPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика ідентичності корабля, ери, фракції та локалізації
        return {
            "Era": self.Owner.Get("Era", "25TH CENTURY"),
            "Faction": self.Owner.Get("Faction", "STARFLEET"),
            "Language": self.Owner.Get("Language", "UKRAINIAN"),
            "Keyboard": self.Owner.Get("Keyboard", "QWERTY"),
        }

    def ServicePolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика підключення системних сервісів, звуку, анімації та ODN
        return {
            "ServiceMode": self.Owner.Get("ServiceMode", "STANDARD"),
            "Audio": self.Owner.Get("Audio", True),
            "Animations": self.Owner.Get("Animations", True),
            "ODNMode": self.Owner.Get("ODNMode", "NORMAL"),
            "BlackBox": self.Owner.Get("BlackBox", True),
        }

    def RecoveryPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика автоматичного відновлення при нештатних ситуаціях
        return self.Owner.RecoveryPolicy()

    def AutofixPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика застосування системних авто-патчів
        return self.Owner.AutofixPolicy()

    def GetManifest(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Підсумковий системний маніфест політик LCARS
        return {
            "Display": self.DisplayPolicy(),
            "Identity": self.IdentityPolicy(),
            "Services": self.ServicePolicy(),
            "Recovery": self.RecoveryPolicy(),
            "Autofix": self.AutofixPolicy(),
        }

    # Аліас сумісності
    Payload = GetManifest

# ═════════════════════════════════════════════════════════════════════
# 4. ГОЛОВНИЙ ПРОЦЕСОР BIOS // SYSTEM COMPONENT
# ═════════════════════════════════════════════════════════════════════
class BIOS(SystemComponent):
    # Головний процесор BIOS LCARS — керує POST-тестами, UEFI та SQLite-сховищем
    SystemVersion = Version.Release
    InstanceRef = None

    # Канали системних сигналів ODN / Transmission
    ConfigLoaded = Transmission(dict)
    ConfigSaved = Transmission(dict)
    PostCompleted = Transmission(dict)
    BootApproved = Transmission(dict)
    EmergencyRequired = Transmission(dict)
    BootTargetSelected = Transmission(dict)

    def __init__(self, Settings: LCARS.Typing.Optional[LCARS.Typing.Dict[str, LCARS.Typing.Any]] = None,
                 ConfigPath: LCARS.Typing.Optional[LCARS.Typing.Any] = None):
        super().__init__(SystemId="System.BIOS")
        self.Version = Version.Release
        self.Passport = Version.Passport()
        self.Settings: LCARS.Typing.Dict[str, BiosSetting] = {}
        self.BootEntries: LCARS.Typing.List[BootEntry] = []
        self.Hardware = HardwareProfile()
        self.LastReport: LCARS.Typing.Optional[BiosReport] = None
        TimeModule = LCARS.System.Time
        self.Started = TimeModule.time() if hasattr(TimeModule, "time") else 0.0
        self.ConfigPath = LCARS.System.Path(ConfigPath) if ConfigPath else self.DefaultConfigPath()
        self.UEFI = UEFI(self)
        self.LCARS = LCARSPolicy(self)
        self.LoadDefaults()
        self.LoadSaved()
        if Settings:
            self.Load(Settings)

    def DefaultConfigPath(self) -> LCARS.Typing.Any:
        # Отримання канонічного шляху до ізолінійного чіпу конфігурації BIOS
        return LCARS.System.Path(ResolveChipPath("00-0001-bios-core"))

    def LoadDefaults(self) -> None:
        # Завантаження базових параметрів та записів замовчування
        self.Settings = {
            "Resolution": BiosSetting("Resolution", "1920X1080", ["1280X720", "1920X1080", "2560X1440", "3840X2160"], False, "DISPLAY", "Розмір основного LCARS-поля для екранів і PADD."),
            "RefreshRate": BiosSetting("RefreshRate", "60 HZ", ["60 HZ", "120 HZ", "144 HZ"], False, "DISPLAY", "Цільова частота оновлення для анімацій."),
            "Fullscreen": BiosSetting("Fullscreen", True, [False, True], False, "DISPLAY", "Запускати оболонку на весь екран або як переносний PADD."),
            "Era": BiosSetting("Era", "25TH CENTURY", ["22ND CENTURY", "23RD CENTURY", "24TH CENTURY", "25TH CENTURY"], False, "IDENTITY", "Активний часовий стиль LCARS."),
            "Faction": BiosSetting("Faction", "STARFLEET", ["STARFLEET", "KLINGON", "ROMULAN", "VULCAN", "BORG"], False, "IDENTITY", "Фракція, яка задає протоколи й стиль оболонки."),
            "Language": BiosSetting("Language", "UKRAINIAN", ["UKRAINIAN", "ENGLISH"], False, "LOCALIZATION", "Мова системних екранів і службових повідомлень."),
            "Keyboard": BiosSetting("Keyboard", "QWERTY", ["QWERTY", "QWERTZ", "AZERTY"], False, "LOCALIZATION", "Підказка розкладки для полів введення."),
            "Target": BiosSetting("Target", BootTarget.DESKTOP, [BootTarget.DESKTOP, BootTarget.RECOVERY, BootTarget.BIOS, BootTarget.SHELL, BootTarget.AI_BOOT, "designer"], False, "UEFI", "Ціль запуску, яку вибирає UEFI-рівень."),
            "SecureBoot": BiosSetting("SecureBoot", True, [False, True], False, "UEFI", "Дозволяти тільки захищені записи запуску."),
            "BootOrder": BiosSetting("BootOrder", ["LCARS-MAIN", "RECOVERY", "AI-AUTONOMOUS"], [], False, "UEFI", "Порядок записів запуску."),
            "SafeMode": BiosSetting("SafeMode", False, [False, True], False, "RECOVERY", "Примусово запускати скорочений безпечний ланцюг."),
            "Diagnostics": BiosSetting("Diagnostics", True, [False, True], False, "RECOVERY", "Виконувати повну діагностику перед стартом."),
            "Autofix": BiosSetting("Autofix", False, [False, True], False, "RECOVERY", "Дозволити аварійному рівню виправляти відомі збої."),
            "RecoveryTarget": BiosSetting("RecoveryTarget", BootTarget.RECOVERY, [BootTarget.RECOVERY, BootTarget.BIOS, BootTarget.SHELL], False, "RECOVERY", "Куди переходити після критичної помилки."),
            "ODNMode": BiosSetting("ODNMode", "NORMAL", ["NORMAL", "SAFE", "DIAGNOSTIC"], False, "NETWORK", "Режим передачі каналами ODN."),
            "BlackBox": BiosSetting("BlackBox", True, [False, True], False, "NETWORK", "Записувати події запуску у чорну скриньку ODN."),
            "ServiceMode": BiosSetting("ServiceMode", "STANDARD", ["MINIMAL", "STANDARD", "FULL"], False, "SERVICES", "Який набір служб піднімати після ініціалізації."),
            "Audio": BiosSetting("Audio", True, [False, True], False, "SERVICES", "Дозволити звуковий відгук LCARS."),
            "Animations": BiosSetting("Animations", True, [False, True], False, "SERVICES", "Дозволити анімаційні протоколи LCARS."),
        }
        self.BootEntries = [
            BootEntry("LCARS-MAIN", "Головний термінал LCARS", BootTarget.DESKTOP, 1, True, True),
            BootEntry("RECOVERY", "Обслуговування й аварійний режим", BootTarget.RECOVERY, 2, False, True),
            BootEntry("BIOS-SETUP", "Екран налаштувань LCARS BIOS", BootTarget.BIOS, 3, False, True),
            BootEntry("AI-AUTONOMOUS", "Прямий запуск AI-рівня", BootTarget.AI_BOOT, 4, False, True),
            BootEntry("DESIGNER", "LCARS-конструктор інтерфейсів", "designer", 5, False, True),
        ]
        self.SyncBootOrder()

    def InitDatabase(self) -> None:
        # Створення структури таблиць у SQLite чіпі конфігурації
        if not self.ConfigPath.parent.exists():
            self.ConfigPath.parent.mkdir(parents=True)
        SqliteModule = LCARS.SQLite
        conn = SqliteModule.connect(str(self.ConfigPath))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS settings (Name TEXT PRIMARY KEY, Value TEXT, Section TEXT, Locked INTEGER, Description TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS boot_entries (Name TEXT PRIMARY KEY, Description TEXT, Target TEXT, Priority INTEGER, IsDefault INTEGER, Secure INTEGER)")
        cursor.execute("CREATE TABLE IF NOT EXISTS hardware_profile (Id INTEGER PRIMARY KEY, Cpu TEXT, MemoryTotal INTEGER, Data TEXT)")
        conn.commit()
        conn.close()

    def LoadSaved(self) -> bool:
        # Зчитування збережених параметрів зі сховища SQLite
        self.InitDatabase()
        if not self.ConfigPath.exists():
            return False
        SqliteModule = LCARS.SQLite
        ConnValid = hasattr(SqliteModule, "connect")
        if not ConnValid:
            return False
        conn = SqliteModule.connect(str(self.ConfigPath))
        if conn is None:
            return False
        cursor = conn.cursor()
        if cursor is None:
            conn.close()
            return False
        cursor.execute("SELECT Name, Value FROM settings")
        rows = cursor.fetchall()
        loaded_settings = {}
        for row in rows:
            val = SafeJsonLoads(row[1], row[1])
            loaded_settings[row[0]] = val
        if loaded_settings:
            self.Load(loaded_settings)
        cursor.execute("SELECT Name, Description, Target, Priority, IsDefault, Secure FROM boot_entries ORDER BY Priority")
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "Name": row[0], "Description": row[1], "Target": row[2],
                "Priority": row[3], "IsDefault": bool(row[4]), "Secure": bool(row[5])
            })
        if entries:
            self.LoadBootEntries(entries)
        cursor.execute("SELECT Cpu, MemoryTotal, Data FROM hardware_profile WHERE Id=1")
        hw_row = cursor.fetchone()
        if hw_row:
            hw_data = SafeJsonLoads(hw_row[2], {}) if hw_row[2] else {}
            if not isinstance(hw_data, dict):
                hw_data = {}
            hw_data["Cpu"] = hw_row[0]
            hw_data["MemoryTotal"] = hw_row[1]
            self.LoadHardware(hw_data)
        conn.close()
        StatePacket = self.ExportState()
        self.ConfigLoaded.Emit(StatePacket)
        ODN.Emit("BIOS.ConfigLoaded", StatePacket)
        return True

    def Save(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Збереження поточної конфігурації в SQLite
        self.InitDatabase()
        StatePacket = self.ExportState()
        SqliteModule = LCARS.SQLite
        JsonModule = LCARS.Import("json")
        if not hasattr(SqliteModule, "connect"):
            self.ConfigSaved.Emit(StatePacket)
            ODN.Emit("BIOS.ConfigSaved", StatePacket)
            return StatePacket
        conn = SqliteModule.connect(str(self.ConfigPath))
        if conn is None:
            self.ConfigSaved.Emit(StatePacket)
            ODN.Emit("BIOS.ConfigSaved", StatePacket)
            return StatePacket
        cursor = conn.cursor()
        if cursor is None:
            conn.close()
            self.ConfigSaved.Emit(StatePacket)
            ODN.Emit("BIOS.ConfigSaved", StatePacket)
            return StatePacket
        cursor.execute("DELETE FROM settings")
        for name, setting in self.Settings.items():
            val_str = JsonModule.dumps(setting.Value)
            cursor.execute("INSERT INTO settings (Name, Value, Section, Locked, Description) VALUES (?, ?, ?, ?, ?)",
                           (name, val_str, setting.Section, int(setting.Locked), setting.Description))
        cursor.execute("DELETE FROM boot_entries")
        for entry in self.BootEntries:
            cursor.execute("INSERT INTO boot_entries (Name, Description, Target, Priority, IsDefault, Secure) VALUES (?, ?, ?, ?, ?, ?)",
                           (entry.Name, entry.Description, entry.Target, entry.Priority, int(entry.IsDefault), int(entry.Secure)))
        cursor.execute("DELETE FROM hardware_profile")
        hw_data_str = JsonModule.dumps({"StorageDevices": self.Hardware.StorageDevices, "NetworkInterfaces": self.Hardware.NetworkInterfaces})
        cursor.execute("INSERT INTO hardware_profile (Id, Cpu, MemoryTotal, Data) VALUES (1, ?, ?, ?)",
                       (self.Hardware.Cpu, self.Hardware.MemoryTotal, hw_data_str))
        conn.commit()
        conn.close()
        self.ConfigSaved.Emit(StatePacket)
        ODN.Emit("BIOS.ConfigSaved", StatePacket)
        return StatePacket

    def ResetDefaults(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Скидання параметрів BIOS до фабричного стану
        self.LoadDefaults()
        StatePacket = self.ExportState()
        ODN.Emit("BIOS.ResetDefaults", StatePacket)
        return StatePacket

    def Load(self, Values: LCARS.Typing.Dict[str, LCARS.Typing.Any]) -> None:
        # Масове завантаження параметрів
        for Name, Value in Values.items():
            self.Set(Name, Value)

    def Export(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Експорт параметрів у словник
        return {Name: Setting.Value for Name, Setting in self.Settings.items()}

    def ExportState(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Повний системний зліпок стану BIOS
        return {
            "SystemId": self.SystemId,
            "Version": self.Version,
            "Settings": self.Export(),
            "Catalog": self.Catalog(),
            "UEFI": self.UEFI.GetManifest(),
            "LCARS": self.LCARS.GetManifest(),
            "BootEntries": self.GetBootEntries(),
            "Hardware": self.Hardware.__dict__,
            "Firmware": self.BuildFirmwareConfig().ToDict(),
            "Recovery": self.RecoveryPolicy(),
            "Autofix": self.AutofixPolicy(),
            "ConfigPath": str(self.ConfigPath),
        }

    # Аліас для сумісності з UI панелями
    ExportPayload = ExportState

    def Catalog(self) -> LCARS.Typing.Dict[str, LCARS.Typing.List[LCARS.Typing.Dict[str, LCARS.Typing.Any]]]:
        # Структурований каталог параметрів за розділами
        CatalogData = {}
        for Name, Setting in self.Settings.items():
            Section = Setting.Section
            if Section not in CatalogData:
                CatalogData[Section] = []
            CatalogData[Section].append({
                "Name": Name,
                "Value": Setting.Value,
                "Options": list(Setting.Options),
                "Locked": Setting.Locked,
                "Description": Setting.Description,
            })
        return CatalogData

    def Set(self, Name: str, Value: LCARS.Typing.Any) -> bool:
        # Безпечне оновлення значення параметра
        Setting = self.Settings.get(Name)
        if Setting is None:
            self.Settings[Name] = BiosSetting(Name, Value)
            return True
        if Setting.Locked:
            return False
        if Setting.Options and Value not in Setting.Options:
            return False
        Setting.Value = Value
        if Name == "BootOrder":
            self.ApplyBootOrder(Value)
        return True

    def Get(self, Name: str, Default: LCARS.Typing.Any = None) -> LCARS.Typing.Any:
        # Зчитування значення параметра
        Setting = self.Settings.get(Name)
        return Setting.Value if Setting else Default

    def Lock(self, Name: str) -> bool:
        # Блокування параметра від редагування
        Setting = self.Settings.get(Name)
        if Setting is None:
            return False
        Setting.Locked = True
        return True

    def Unlock(self, Name: str) -> bool:
        # Розблокування параметра
        Setting = self.Settings.get(Name)
        if Setting is None:
            return False
        Setting.Locked = False
        return True

    def LoadBootEntries(self, Entries: LCARS.Typing.List[LCARS.Typing.Dict[str, LCARS.Typing.Any]]) -> None:
        # Завантаження записів таблиці завантаження UEFI
        Loaded = []
        for Entry in Entries:
            if isinstance(Entry, dict) and Entry.get("Name") and Entry.get("Target"):
                Loaded.append(BootEntry(
                    str(Entry.get("Name")),
                    str(Entry.get("Description", "")),
                    str(Entry.get("Target")),
                    int(Entry.get("Priority", len(Loaded) + 1)),
                    bool(Entry.get("IsDefault", False)),
                    bool(Entry.get("Secure", True)),
                ))
        if Loaded:
            self.BootEntries = Loaded
            self.SyncBootOrder()

    def LoadHardware(self, Data: LCARS.Typing.Dict[str, LCARS.Typing.Any]) -> None:
        # Оновлення опису апаратного профілю
        self.Hardware.Cpu = str(Data.get("Cpu", self.Hardware.Cpu))
        self.Hardware.MemoryTotal = int(Data.get("MemoryTotal", self.Hardware.MemoryTotal))
        Storage = Data.get("StorageDevices", self.Hardware.StorageDevices)
        Network = Data.get("NetworkInterfaces", self.Hardware.NetworkInterfaces)
        self.Hardware.StorageDevices = Storage if isinstance(Storage, list) else self.Hardware.StorageDevices
        self.Hardware.NetworkInterfaces = Network if isinstance(Network, list) else self.Hardware.NetworkInterfaces

    def GetBootEntries(self) -> LCARS.Typing.List[LCARS.Typing.Dict[str, LCARS.Typing.Any]]:
        # Отримання відсортованого списку записів запуску
        Entries = sorted(self.BootEntries, key=lambda Entry: Entry.Priority)
        return [Entry.__dict__ for Entry in Entries]

    def AddBootEntry(self, Name: str, Description: str, Target: str, Secure: bool = True) -> bool:
        # Створення нового запису завантаження
        if self.FindBootEntry(Name):
            return False
        Priority = len(self.BootEntries) + 1
        self.BootEntries.append(BootEntry(Name, Description, Target, Priority, False, Secure))
        self.SyncBootOrder()
        ODN.Emit("BIOS.BootEntryAdded", {"Name": Name, "Target": Target})
        return True

    def RemoveBootEntry(self, Name: str) -> bool:
        # Видалення запису завантаження (якщо він не є дефолтним)
        Entry = self.FindBootEntry(Name)
        if Entry is None or Entry.IsDefault:
            return False
        self.BootEntries = [Item for Item in self.BootEntries if Item.Name != Name]
        self.SyncBootOrder()
        ODN.Emit("BIOS.BootEntryRemoved", {"Name": Name})
        return True

    def FindBootEntry(self, Name: str) -> BootEntry | None:
        # Пошук запису за назвою
        for Entry in self.BootEntries:
            if Entry.Name == Name:
                return Entry
        return None

    def SetBootPriority(self, Name: str, Priority: int) -> bool:
        # Встановлення пріоритету запису
        Entry = self.FindBootEntry(Name)
        if Entry is None:
            return False
        Entry.Priority = max(1, int(Priority))
        self.NormalizeBootPriorities()
        self.SyncBootOrder()
        return True

    def SetDefaultBootEntry(self, Name: str) -> bool:
        # Призначення головного запису завантаження
        Entry = self.FindBootEntry(Name)
        if Entry is None:
            return False
        for Item in self.BootEntries:
            Item.IsDefault = Item.Name == Name
        self.Set("Target", Entry.Target)
        ODN.Emit("BIOS.DefaultBootEntry", {"Name": Name, "Target": Entry.Target})
        return True

    def ApplyBootOrder(self, Order: LCARS.Typing.Any) -> None:
        # Застосування нового порядку записів за списком імен
        if not isinstance(Order, list):
            return
        Position = {str(Name): Index + 1 for Index, Name in enumerate(Order)}
        for Entry in self.BootEntries:
            if Entry.Name in Position:
                Entry.Priority = Position[Entry.Name]
        self.NormalizeBootPriorities()

    def SyncBootOrder(self) -> None:
        # Синхронізація налаштування BootOrder з масивом BootEntries
        self.NormalizeBootPriorities()
        Order = [Entry.Name for Entry in sorted(self.BootEntries, key=lambda Item: Item.Priority)]
        Setting = self.Settings.get("BootOrder")
        if Setting:
            Setting.Value = Order

    def NormalizeBootPriorities(self) -> None:
        # Нормалізація послідовності пріоритетів від 1 до N
        for Index, Entry in enumerate(sorted(self.BootEntries, key=lambda Item: Item.Priority), start=1):
            Entry.Priority = Index

    def SelectBootTarget(self, Target: str) -> bool:
        # Вибір цілі завантаження з передачею події в ODN
        Changed = self.Set("Target", Target)
        if Changed:
            self.BootTargetSelected.Emit({"Target": Target})
            ODN.Emit("BIOS.TargetSelected", {"Target": Target})
        return Changed

    def RecoveryPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Формування поточної політики аварійного відновлення
        return {
            "SafeMode": self.Get("SafeMode", False),
            "Diagnostics": self.Get("Diagnostics", True),
            "Target": self.Get("RecoveryTarget", BootTarget.RECOVERY),
            "ServiceMode": "MINIMAL" if self.Get("SafeMode", False) else self.Get("ServiceMode", "STANDARD"),
        }

    def AutofixPolicy(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Політика допустимих зон автоматичного виправлення помилок
        return {
            "Enabled": self.Get("Autofix", False),
            "AllowedStages": ["REGISTER MAP", "ODN BUS", "BIOS POST", "KERNEL MAP"],
            "RequiresBlackBox": self.Get("BlackBox", True),
        }

    def BuildFirmwareConfig(self) -> FirmwareConfig:
        # Створення об'єкта прошивки FirmwareConfig на основі BIOS налаштувань
        Config = FirmwareConfig()
        Config.Version = Version.Release
        Config.Language = self.Get("Language", "UKRAINIAN")
        Config.DefaultBoot = self.Get("Target", Config.DefaultBoot)
        Config.Hardware = self.Hardware
        Config.BootEntries = list(self.BootEntries)
        for Entry in Config.BootEntries:
            Entry.Secure = bool(self.Get("SecureBoot", True)) and Entry.Secure
        return Config

    # ─── ВИКОНАННЯ POST (POWER-ON SELF-TEST) ──────────────────────────
    def RunPost(self) -> BiosReport:
        # Головна діагностична послідовність POST зорельота LCARS
        Started = LCARS.System.DateTime.now().timestamp()
        Checks = [
            self.CheckPython(),
            self.CheckCoreModules(),
            self.CheckODN(),
            self.CheckChipCatalog(),
            self.CheckRequiredChips(),
            self.CheckSettings(),
            self.CheckFirmwarePolicy(),
            self.CheckRecoveryPolicy(),
            self.CheckConfigStorage(),
        ]
        Status = "NOMINAL"
        for Check in Checks:
            if Check.Critical and Check.Status != "OK":
                Status = "EMERGENCY"

        Report = BiosReport(Status, Checks, self.Export(), Started, LCARS.System.DateTime.now().timestamp())
        self.LastReport = Report
        ReportPacket = self.BuildReportPacket(Report)

        self.PostCompleted.Emit(ReportPacket)
        ODN.Emit("BIOS.POST", ReportPacket)
        if Status == "NOMINAL":
            self.BootApproved.Emit(ReportPacket)
            ODN.Emit("BIOS.BootApproved", ReportPacket)
        else:
            self.EmergencyRequired.Emit(ReportPacket)
            ODN.Emit("BIOS.EmergencyRequired", ReportPacket)
        return Report

    def CheckPython(self) -> BiosCheck:
        # 1/9: Перевірка версії середовища виконання Python
        SysObj = LCARS.System.Core
        VersionOk = SysObj.version_info >= (3, 10)
        Detail = str(SysObj.version_info.major) + "." + str(SysObj.version_info.minor)
        return BiosCheck("PYTHON RUNTIME", "OK" if VersionOk else "FAIL", Detail)

    def CheckCoreModules(self) -> BiosCheck:
        # 2/9: Перевірка цілісності базових системних модулів ядра
        Required = [
            "lcars.base.type",
            "lcars.core.signal",
            "lcars.modules.storage",
            "lcars.core.system",
            "lcars.system.software",
            "lcars.system.command",
        ]
        ModuleUtil = LCARS.ModuleUtil
        Missing = [Name for Name in Required if ModuleUtil.find_spec(Name) is None]
        return BiosCheck("CORE MODULE MAP", "OK" if not Missing else "FAIL", ", ".join(Missing))

    def CheckODN(self) -> BiosCheck:
        # 3/9: Перевірка працездатності шини ODN та чорної скриньки
        HasBlackBox = hasattr(ODN, "BlackBox")
        Status = ODN.BlackBox.GetStatus() if HasBlackBox else {}
        Detail = Status.get("ChipName", "BLACK BOX OFFLINE") if isinstance(Status, dict) else "BLACK BOX OFFLINE"
        return BiosCheck("ODN TRANSMISSION BUS", "OK" if HasBlackBox else "FAIL", Detail)

    def CheckChipCatalog(self) -> BiosCheck:
        # 4/9: Перевірка каталогу ізолінійних чіпів
        Chips = ListChips()
        return BiosCheck("ISOLINEAR CHIP CATALOG", "OK" if Chips else "FAIL", str(len(Chips)) + " CHIPS")

    def CheckRequiredChips(self) -> BiosCheck:
        # 5/9: Перевірка наявності критичних чіпів ядра в сховищі
        Required = [
            ("ODN Black Box", "black-box"),
            ("BIOS Core Chip", "bios-core"),
            ("Network Operations Chip", "network-operations"),
            ("Memory Matrix Chip", "memory"),
            ("Logbook Archive Chip", "shipsbook"),
        ]
        Missing = [Title for Title, Query in Required if FindChip(Query) is None]
        return BiosCheck("REQUIRED DATA CHIPS", "OK" if not Missing else "FAIL", ", ".join(Missing))

    def CheckSettings(self) -> BiosCheck:
        # 6/9: Валідація значень конфігурації BIOS
        Invalid = []
        for Name, Setting in self.Settings.items():
            if Setting.Options and Setting.Value not in Setting.Options:
                Invalid.append(Name)
        return BiosCheck("BIOS CONFIGURATION", "OK" if not Invalid else "FAIL", ", ".join(Invalid))

    def CheckFirmwarePolicy(self) -> BiosCheck:
        # 7/9: Перевірка відповідності політики завантаження записам UEFI
        Target = self.Get("Target")
        EntryNames = [Entry.Name for Entry in self.BootEntries]
        BootOrder = self.Get("BootOrder", [])
        Missing = [Name for Name in BootOrder if Name not in EntryNames]
        if Target not in self.Settings["Target"].Options:
            return BiosCheck("UEFI BOOT POLICY", "FAIL", "INVALID TARGET " + str(Target))
        if Missing:
            return BiosCheck("UEFI BOOT POLICY", "FAIL", "MISSING ENTRIES " + ", ".join(Missing))
        if self.Get("SecureBoot", True):
            Insecure = [Entry.Name for Entry in self.BootEntries if not Entry.Secure]
            if Insecure:
                return BiosCheck("UEFI BOOT POLICY", "FAIL", "INSECURE ENTRIES " + ", ".join(Insecure))
        return BiosCheck("UEFI BOOT POLICY", "OK", str(Target))

    def CheckRecoveryPolicy(self) -> BiosCheck:
        # 8/9: Перевірка recovery-політики
        Policy = self.RecoveryPolicy()
        Target = Policy.get("Target")
        if Target not in self.Settings["RecoveryTarget"].Options:
            return BiosCheck("RECOVERY POLICY", "FAIL", str(Target))
        return BiosCheck("RECOVERY POLICY", "OK", str(Target), False)

    def CheckConfigStorage(self) -> BiosCheck:
        # 9/9: Перевірка доступності файлового сховища для бази BIOS
        Parent = self.ConfigPath.parent
        Parent.mkdir(parents=True, exist_ok=True)
        return BiosCheck("BIOS CONFIG CHIP", "OK" if Parent.exists() else "FAIL", str(self.ConfigPath), False)

    def SaveAndExit(self) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Збереження налаштувань та вихід
        StatePacket = self.Save()
        ODN.Emit("BIOS.SaveAndExit", StatePacket)
        return StatePacket

    def OpenChip(self, Name: str) -> LCARS.System.Path:
        # Отримання абсолютного шляху до вказаного ізолінійного чіпу
        return LCARS.System.Path(ResolveChipPath(Name))

    def BuildReportPacket(self, Report: BiosReport | None = None) -> LCARS.Typing.Dict[str, LCARS.Typing.Any]:
        # Формування повного системного пакету діагностичного звіту
        ActiveReport = Report or self.LastReport or self.RunPost()
        Packet = self.ExportState()
        Packet.update({
            "Status": ActiveReport.Status,
            "Checks": [
                {
                    "Name": Check.Name,
                    "Status": Check.Status,
                    "Detail": Check.Detail,
                    "Critical": Check.Critical,
                }
                for Check in ActiveReport.Checks
            ],
            "Started": ActiveReport.Started,
            "Finished": ActiveReport.Finished,
        })
        return Packet

    # Аліас для сумісності
    ReportPayload = BuildReportPacket

    def Lines(self) -> LCARS.Typing.List[str]:
        # Формування масиву текстових рядків звіту
        Report = self.LastReport or self.RunPost()
        return Report.Lines()

# ═════════════════════════════════════════════════════════════════════
# 5. ТОЧКИ ЗАПУСКУ ТА ЕКСПОРТ
# ═════════════════════════════════════════════════════════════════════
def RunBios(Settings: LCARS.Typing.Dict[str, LCARS.Typing.Any] | None = None) -> BiosReport:
    # Швидкий запуск POST-тестування ядра BIOS
    return BIOS(Settings).RunPost()

__all__ = [
    "BIOS",
    "UEFI",
    "LCARS",
    "BiosSetting",
    "BiosCheck",
    "BiosReport",
    "RunBios",
]

