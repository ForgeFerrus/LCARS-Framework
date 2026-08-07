from __future__ import annotations

import importlib.util
import json
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import Any, Dict, List

from lcars.core.signal import ODN, Transmission
from lcars.base.version import getVersion
from lcars.modules.storage import FindChip, ListChips, ResolveChipPath
from lcars.system.software import BootEntry, BootTarget, HardwareProfile, FirmwareConfig

# LCARS BIOS не замінює фізичний BIOS/UEFI комп'ютера.
# Це перший керуючий рівень LCARS після запуску Python-процесу.
# Тут живе не графіка, а системна логіка: перевірка середовища,
# таблиця запуску, політики оболонки, аварійний перехід і звіт для екранів.
Version = getVersion()
# Глобальний екземпляр BIOS, який створюється при ініціалізації системи
# Підрівень UEFI для керування таблицею запуску
# Підрівень LCARS для опису політик оболонки й recovery

# Регулярні вирази для перевірки базових JSON-типів
_JSON_NUMBER_RE = re.compile(r"^-?\d+(\.\d+)?([eE][+-]?\d+)?$")
_JSON_BOOL_NULL_RE = re.compile(r"^(true|false|null)$")
_JSON_STRING_RE = re.compile(r'^".*"$')


def SafeJsonLoads(Text: str, Default: Any = None) -> Any:
    # Безпечне завантаження JSON без використання try/except.
    # Перевіряє формат рядка перед парсингом: якщо виглядає як JSON — парсимо,
    # інакше повертаємо оригінальний рядок або значення за замовчуванням.
    if not isinstance(Text, str) or not Text.strip():
        return Default if Default is not None else Text
    Stripped = Text.strip()
    FirstChar = Stripped[0]
    # Визначення JSON-типу за першим символом
    CouldBeJson = (
        FirstChar in ("{", "[", '"')
        or FirstChar.isdigit()
        or FirstChar in ("-", "t", "f", "n")
    )
    if not CouldBeJson:
        return Text
    # Перевірка простих JSON-типів за допомогою регулярних виразів
    if _JSON_NUMBER_RE.match(Stripped):
        return float(Stripped) if "." in Stripped or "e" in Stripped.lower() else int(Stripped)
    if _JSON_BOOL_NULL_RE.match(Stripped):
        if Stripped == "true":
            return True
        if Stripped == "false":
            return False
        return None
    if _JSON_STRING_RE.match(Stripped):
        return Stripped[1:-1]
    # Перевірка завершеності структури для об'єктів і масивів
    if FirstChar == "{" and not Stripped.endswith("}"):
        return Text
    if FirstChar == "[" and not Stripped.endswith("]"):
        return Text
    # Парсинг складних JSON-структур
    Decoder = json.JSONDecoder()
    Result, EndIdx = Decoder.raw_decode(Stripped)
    # Перевірка що весь рядок було розпарсено
    if EndIdx == len(Stripped):
        return Result
    return Text


@dataclass
class BiosSetting:
    # Один параметр BIOS/UEFI. UI може його показати й змінити,
    # але перевірка значення й блокування живуть тільки тут.
    Name: str
    Value: Any
    Options: List[Any] = field(default_factory=list)
    Locked: bool = False
    Section: str = "SYSTEM"
    Description: str = ""


@dataclass
class BiosCheck:
    # Один пункт POST. Якщо Critical=True і Status не OK,
    # нормальний запуск має перейти в emergency/recovery.
    Name: str
    Status: str
    Detail: str = ""
    Critical: bool = True


@dataclass
class BiosReport:
    # Повний результат POST для boot-screen, логів, ODN black box
    # і аварійного режиму.
    Status: str
    Checks: List[BiosCheck]
    Settings: Dict[str, Any]
    Started: float
    Finished: float

    def Lines(self) -> List[str]:
        # Формування текстового звіту для консолі й логів
        Lines = [
            "LCARS BIOS CORE",
            "VERSION :: " + str(Version),
            "STATUS :: " + self.Status,
        ]
        for Check in self.Checks:
            Detail = " :: " + Check.Detail if Check.Detail else ""
            Lines.append(Check.Name + " :: " + Check.Status + Detail)
        return Lines


class UEFI:
    # UEFI-рівень LCARS відповідає за таблицю запуску.
    # Він не запускає екран напряму, а тільки описує куди система має перейти.
    def __init__(self, Owner: "BIOS"):
        self.Owner = Owner

    def Entries(self) -> List[Dict[str, Any]]:
        # Повертає список записів запуску з BIOS
        return self.Owner.GetBootEntries()

    def Target(self) -> str:
        # Поточна цільова платформа запуску
        return self.Owner.Get("Target", BootTarget.DESKTOP)

    def SecureBoot(self) -> bool:
        # Статус захищеного завантаження
        return bool(self.Owner.Get("SecureBoot", True))

    def BootOrder(self) -> List[str]:
        # Порядок записів запуску
        Order = self.Owner.Get("BootOrder", [])
        return list(Order) if isinstance(Order, list) else []

    def SelectTarget(self, Target: str) -> bool:
        # Вибір цілі запуску через BIOS
        return self.Owner.SelectBootTarget(Target)

    def AddEntry(self, Name: str, Description: str, Target: str, Secure: bool = True) -> bool:
        # Додавання нового запису запуску
        return self.Owner.AddBootEntry(Name, Description, Target, Secure)

    def RemoveEntry(self, Name: str) -> bool:
        # Видалення запису запуску за ім'ям
        return self.Owner.RemoveBootEntry(Name)

    def SetDefault(self, Name: str) -> bool:
        # Встановлення запису як цільового за замовчуванням
        return self.Owner.SetDefaultBootEntry(Name)

    def Firmware(self) -> Dict[str, Any]:
        # Повертає конфігурацію прошивки у вигляді словника
        return self.Owner.BuildFirmwareConfig().ToDict()

    def Payload(self) -> Dict[str, Any]:
        # Єдиний пакет даних UEFI для передачі на екран налаштувань
        return {
            "Target": self.Target(),
            "SecureBoot": self.SecureBoot(),
            "BootOrder": self.BootOrder(),
            "Entries": self.Entries(),
            "Firmware": self.Firmware(),
        }


class LCARS:
    # LCARS-рівень описує правила самої оболонки.
    # Тут не кнопки й не екран, а режими, мова, сервісний склад і recovery.
    def __init__(self, Owner: "BIOS"):
        self.Owner = Owner

    def DisplayPolicy(self) -> Dict[str, Any]:
        # Політика дисплея: роздільна здатність, частота оновлення, повноекранний режим
        return {
            "Resolution": self.Owner.Get("Resolution", "1920X1080"),
            "RefreshRate": self.Owner.Get("RefreshRate", "60 HZ"),
            "Fullscreen": self.Owner.Get("Fullscreen", True),
        }

    def IdentityPolicy(self) -> Dict[str, Any]:
        # Політика ідентичності: ера, фракція, мова, розкладка клавіатури
        return {
            "Era": self.Owner.Get("Era", "25TH CENTURY"),
            "Faction": self.Owner.Get("Faction", "STARFLEET"),
            "Language": self.Owner.Get("Language", "UKRAINIAN"),
            "Keyboard": self.Owner.Get("Keyboard", "QWERTY"),
        }

    def ServicePolicy(self) -> Dict[str, Any]:
        # Політика сервісів: режим обслуговування, звук, анімації, ODN, чорна скринька
        return {
            "ServiceMode": self.Owner.Get("ServiceMode", "STANDARD"),
            "Audio": self.Owner.Get("Audio", True),
            "Animations": self.Owner.Get("Animations", True),
            "ODNMode": self.Owner.Get("ODNMode", "NORMAL"),
            "BlackBox": self.Owner.Get("BlackBox", True),
        }

    def RecoveryPolicy(self) -> Dict[str, Any]:
        # Політика відновлення після збоїв
        return self.Owner.RecoveryPolicy()

    def AutofixPolicy(self) -> Dict[str, Any]:
        # Політика автоматичного виправлення помилок
        return self.Owner.AutofixPolicy()

    def Payload(self) -> Dict[str, Any]:
        # Єдиний пакет даних LCARS для передачі на екран налаштувань
        return {
            "Display": self.DisplayPolicy(),
            "Identity": self.IdentityPolicy(),
            "Services": self.ServicePolicy(),
            "Recovery": self.RecoveryPolicy(),
            "Autofix": self.AutofixPolicy(),
        }


class BIOS:
    # BIOS є системним функціональним рівнем.
    # Він не створює екран, не малює UI і не запускає застосунок.
    ConfigLoaded = Transmission(dict)
    ConfigSaved = Transmission(dict)
    PostCompleted = Transmission(dict)
    BootApproved = Transmission(dict)
    EmergencyRequired = Transmission(dict)
    BootTargetSelected = Transmission(dict)

    def __init__(self, Settings: Dict[str, Any] | None = None, ConfigPath: Path | str | None = None):
        self.Settings: Dict[str, BiosSetting] = {}
        self.BootEntries: List[BootEntry] = []
        self.Hardware = HardwareProfile()
        self.LastReport: BiosReport | None = None
        self.Started = time()
        self.ConfigPath = Path(ConfigPath) if ConfigPath else self.DefaultConfigPath()
        self.UEFI = UEFI(self)
        self.LCARS = LCARS(self)
        self.LoadDefaults()
        self.LoadSaved()
        if Settings:
            self.Load(Settings)

    def DefaultConfigPath(self) -> Path:
        # Шлях до конфігураційного чіпу BIOS за замовчуванням
        return ResolveChipPath("00-0001-bios-core")

    def LoadDefaults(self) -> None:
        # Базові параметри згруповані за секціями, щоб BIOS-screen
        # міг автоматично будувати меню без хардкоду випадкових полів.
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
            "BootOrder": BiosSetting("BootOrder", ["TITANIUM-OS", "RECOVERY", "AI-AUTONOMOUS"], [], False, "UEFI", "Порядок записів запуску."),
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
            BootEntry("TITANIUM-OS", "Основний LCARS-інтерфейс", BootTarget.DESKTOP, 1, True, True),
            BootEntry("RECOVERY", "Обслуговування й аварійний режим", BootTarget.RECOVERY, 2, False, True),
            BootEntry("BIOS-SETUP", "Екран налаштувань LCARS BIOS", BootTarget.BIOS, 3, False, True),
            BootEntry("AI-AUTONOMOUS", "Прямий запуск AI-рівня", BootTarget.AI_BOOT, 4, False, True),
            BootEntry("DESIGNER", "LCARS-конструктор інтерфейсів", "designer", 5, False, True),
        ]
        self.SyncBootOrder()

    def InitDatabase(self) -> None:
        # Ініціалізація SQLite-бази даних для зберігання конфігурації BIOS
        if not self.ConfigPath.parent.exists():
            self.ConfigPath.parent.mkdir(parents=True)
        conn = sqlite3.connect(str(self.ConfigPath))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                Name TEXT PRIMARY KEY,
                Value TEXT,
                Section TEXT,
                Locked INTEGER,
                Description TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS boot_entries (
                Name TEXT PRIMARY KEY,
                Description TEXT,
                Target TEXT,
                Priority INTEGER,
                IsDefault INTEGER,
                Secure INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hardware_profile (
                Id INTEGER PRIMARY KEY,
                Cpu TEXT,
                MemoryTotal INTEGER,
                Data TEXT
            )
        """)
        conn.commit()
        conn.close()

    def LoadSaved(self) -> bool:
        # Завантаження збережених параметрів з SQLite-бази.
        # Використовує if-перевірки замість try/except для обробки даних.
        self.InitDatabase()
        if not self.ConfigPath.exists():
            return False
        # Перевірка можливості відкриття бази даних
        ConnValid = hasattr(sqlite3, "connect")
        if not ConnValid:
            return False
        conn = sqlite3.connect(str(self.ConfigPath))
        if conn is None:
            return False
        cursor = conn.cursor()
        if cursor is None:
            conn.close()
            return False
        # Завантаження параметрів налаштувань
        cursor.execute("SELECT Name, Value FROM settings")
        rows = cursor.fetchall()
        loaded_settings = {}
        for row in rows:
            # Декодування JSON або використання оригінального рядка
            val = SafeJsonLoads(row[1], row[1])
            loaded_settings[row[0]] = val
        if loaded_settings:
            self.Load(loaded_settings)
        # Завантаження записів запуску
        cursor.execute("SELECT Name, Description, Target, Priority, IsDefault, Secure FROM boot_entries ORDER BY Priority")
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "Name": row[0], "Description": row[1], "Target": row[2],
                "Priority": row[3], "IsDefault": bool(row[4]), "Secure": bool(row[5])
            })
        if entries:
            self.LoadBootEntries(entries)
        # Завантаження профілю апаратного забезпечення
        cursor.execute("SELECT Cpu, MemoryTotal, Data FROM hardware_profile WHERE Id=1")
        hw_row = cursor.fetchone()
        if hw_row:
            # Декодування JSON для даних апаратного забезпечення
            hw_data = SafeJsonLoads(hw_row[2], {}) if hw_row[2] else {}
            if not isinstance(hw_data, dict):
                hw_data = {}
            hw_data["Cpu"] = hw_row[0]
            hw_data["MemoryTotal"] = hw_row[1]
            self.LoadHardware(hw_data)
        conn.close()
        # Випромінювання події завантаження конфігурації
        self.ConfigLoaded.Emit(self.ExportPayload())
        ODN.Emit("BIOS.ConfigLoaded", self.ExportPayload())
        return True

    def Save(self) -> Dict[str, Any]:
        # Збереження поточних параметрів BIOS у SQLite-базу даних
        self.InitDatabase()
        Payload = self.ExportPayload()
        # Перевірка можливості відкриття бази даних
        if not hasattr(sqlite3, "connect"):
            self.ConfigSaved.Emit(Payload)
            ODN.Emit("BIOS.ConfigSaved", Payload)
            return Payload
        conn = sqlite3.connect(str(self.ConfigPath))
        if conn is None:
            self.ConfigSaved.Emit(Payload)
            ODN.Emit("BIOS.ConfigSaved", Payload)
            return Payload
        cursor = conn.cursor()
        if cursor is None:
            conn.close()
            self.ConfigSaved.Emit(Payload)
            ODN.Emit("BIOS.ConfigSaved", Payload)
            return Payload
        # Збереження параметрів налаштувань
        cursor.execute("DELETE FROM settings")
        for name, setting in self.Settings.items():
            val_str = json.dumps(setting.Value)
            cursor.execute("INSERT INTO settings (Name, Value, Section, Locked, Description) VALUES (?, ?, ?, ?, ?)",
                           (name, val_str, setting.Section, int(setting.Locked), setting.Description))
        # Збереження записів запуску
        cursor.execute("DELETE FROM boot_entries")
        for entry in self.BootEntries:
            cursor.execute("INSERT INTO boot_entries (Name, Description, Target, Priority, IsDefault, Secure) VALUES (?, ?, ?, ?, ?, ?)",
                           (entry.Name, entry.Description, entry.Target, entry.Priority, int(entry.IsDefault), int(entry.Secure)))
        # Збереження профілю апаратного забезпечення
        cursor.execute("DELETE FROM hardware_profile")
        hw_data_str = json.dumps({"StorageDevices": self.Hardware.StorageDevices, "NetworkInterfaces": self.Hardware.NetworkInterfaces})
        cursor.execute("INSERT INTO hardware_profile (Id, Cpu, MemoryTotal, Data) VALUES (1, ?, ?, ?)",
                       (self.Hardware.Cpu, self.Hardware.MemoryTotal, hw_data_str))
        conn.commit()
        conn.close()
        self.ConfigSaved.Emit(Payload)
        ODN.Emit("BIOS.ConfigSaved", Payload)
        return Payload

    def ResetDefaults(self) -> Dict[str, Any]:
        # Повний reset повертає BIOS до заводського LCARS-профілю.
        self.LoadDefaults()
        Payload = self.ExportPayload()
        ODN.Emit("BIOS.ResetDefaults", Payload)
        return Payload

    def Load(self, Values: Dict[str, Any]) -> None:
        # Масове завантаження settings проходить через Set,
        # тому locked/options працюють однаково для UI й системи.
        for Name, Value in Values.items():
            self.Set(Name, Value)

    def Export(self) -> Dict[str, Any]:
        # Експорт поточних значень у простий словник
        return {Name: Setting.Value for Name, Setting in self.Settings.items()}

    def ExportPayload(self) -> Dict[str, Any]:
        # Єдиний пакет для BIOS-screen, initialization і black box.
        return {
            "Version": Version,
            "Settings": self.Export(),
            "Catalog": self.Catalog(),
            "UEFI": self.UEFI.Payload(),
            "LCARS": self.LCARS.Payload(),
            "BootEntries": self.GetBootEntries(),
            "Hardware": self.Hardware.__dict__,
            "Firmware": self.BuildFirmwareConfig().ToDict(),
            "Recovery": self.RecoveryPolicy(),
            "Autofix": self.AutofixPolicy(),
            "ConfigPath": str(self.ConfigPath),
        }

    def Catalog(self) -> Dict[str, List[Dict[str, Any]]]:
        # Каталог є описом для UI: які секції існують, що можна редагувати,
        # які значення допустимі й що означає кожен параметр.
        CatalogData: Dict[str, List[Dict[str, Any]]] = {}
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

    def Set(self, Name: str, Value: Any) -> bool:
        # Значення проходить тільки якщо параметр не locked і входить в Options.
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

    def Get(self, Name: str, Default: Any = None) -> Any:
        # Отримання значення параметра за ім'ям
        Setting = self.Settings.get(Name)
        return Setting.Value if Setting else Default

    def Lock(self, Name: str) -> bool:
        # Блокування параметра від зміни
        Setting = self.Settings.get(Name)
        if Setting is None:
            return False
        Setting.Locked = True
        return True

    def Unlock(self, Name: str) -> bool:
        # Розблокування параметра для зміни
        Setting = self.Settings.get(Name)
        if Setting is None:
            return False
        Setting.Locked = False
        return True

    def LoadBootEntries(self, Entries: List[Dict[str, Any]]) -> None:
        # Boot entries є UEFI-таблицею LCARS: ім'я, опис, target, priority, default, secure.
        Loaded: List[BootEntry] = []
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

    def LoadHardware(self, Data: Dict[str, Any]) -> None:
        # HardwareProfile тут логічний, не фізичний: LCARS бачить ці вузли
        # як системний опис середовища запуску.
        self.Hardware.Cpu = str(Data.get("Cpu", self.Hardware.Cpu))
        self.Hardware.MemoryTotal = int(Data.get("MemoryTotal", self.Hardware.MemoryTotal))
        Storage = Data.get("StorageDevices", self.Hardware.StorageDevices)
        Network = Data.get("NetworkInterfaces", self.Hardware.NetworkInterfaces)
        self.Hardware.StorageDevices = Storage if isinstance(Storage, list) else self.Hardware.StorageDevices
        self.Hardware.NetworkInterfaces = Network if isinstance(Network, list) else self.Hardware.NetworkInterfaces

    def GetBootEntries(self) -> List[Dict[str, Any]]:
        # Повертає відсортований за пріоритетом список записів запуску
        Entries = sorted(self.BootEntries, key=lambda Entry: Entry.Priority)
        return [Entry.__dict__ for Entry in Entries]

    def AddBootEntry(self, Name: str, Description: str, Target: str, Secure: bool = True) -> bool:
        # Додавання нового запису запуску до UEFI-таблиці
        if self.FindBootEntry(Name):
            return False
        Priority = len(self.BootEntries) + 1
        self.BootEntries.append(BootEntry(Name, Description, Target, Priority, False, Secure))
        self.SyncBootOrder()
        ODN.Emit("BIOS.BootEntryAdded", {"Name": Name, "Target": Target})
        return True

    def RemoveBootEntry(self, Name: str) -> bool:
        # Видалення запису запуску (не можна видалити запис за замовчуванням)
        Entry = self.FindBootEntry(Name)
        if Entry is None or Entry.IsDefault:
            return False
        self.BootEntries = [Item for Item in self.BootEntries if Item.Name != Name]
        self.SyncBootOrder()
        ODN.Emit("BIOS.BootEntryRemoved", {"Name": Name})
        return True

    def FindBootEntry(self, Name: str) -> BootEntry | None:
        # Пошук запису запуску за ім'ям
        for Entry in self.BootEntries:
            if Entry.Name == Name:
                return Entry
        return None

    def SetBootPriority(self, Name: str, Priority: int) -> bool:
        # Встановлення пріоритету запису запуску
        Entry = self.FindBootEntry(Name)
        if Entry is None:
            return False
        Entry.Priority = max(1, int(Priority))
        self.NormalizeBootPriorities()
        self.SyncBootOrder()
        return True

    def SetDefaultBootEntry(self, Name: str) -> bool:
        # Встановлення запису як цільового за замовчуванням
        Entry = self.FindBootEntry(Name)
        if Entry is None:
            return False
        for Item in self.BootEntries:
            Item.IsDefault = Item.Name == Name
        self.Set("Target", Entry.Target)
        ODN.Emit("BIOS.DefaultBootEntry", {"Name": Name, "Target": Entry.Target})
        return True

    def ApplyBootOrder(self, Order: Any) -> None:
        # Застосування нового порядку записів запуску
        if not isinstance(Order, list):
            return
        Position = {str(Name): Index + 1 for Index, Name in enumerate(Order)}
        for Entry in self.BootEntries:
            if Entry.Name in Position:
                Entry.Priority = Position[Entry.Name]
        self.NormalizeBootPriorities()

    def SyncBootOrder(self) -> None:
        # Синхронізація порядку записів між BootEntries і setting BootOrder
        self.NormalizeBootPriorities()
        Order = [Entry.Name for Entry in sorted(self.BootEntries, key=lambda Item: Item.Priority)]
        Setting = self.Settings.get("BootOrder")
        if Setting:
            Setting.Value = Order

    def NormalizeBootPriorities(self) -> None:
        # Нормалізація пріоритетів: послідовні числа від 1
        for Index, Entry in enumerate(sorted(self.BootEntries, key=lambda Item: Item.Priority), start=1):
            Entry.Priority = Index

    def SelectBootTarget(self, Target: str) -> bool:
        # Вибір цілі запуску з випромінюванням події
        Changed = self.Set("Target", Target)
        if Changed:
            self.BootTargetSelected.Emit({"Target": Target})
            ODN.Emit("BIOS.TargetSelected", {"Target": Target})
        return Changed

    def RecoveryPolicy(self) -> Dict[str, Any]:
        # Recovery policy описує, що робити після критичного збою.
        return {
            "SafeMode": self.Get("SafeMode", False),
            "Diagnostics": self.Get("Diagnostics", True),
            "Target": self.Get("RecoveryTarget", BootTarget.RECOVERY),
            "ServiceMode": "MINIMAL" if self.Get("SafeMode", False) else self.Get("ServiceMode", "STANDARD"),
        }

    def AutofixPolicy(self) -> Dict[str, Any]:
        # Autofix не ремонтує тут напряму. BIOS лише визначає,
        # чи дозволений автоматичний ремонт і в якому режимі.
        return {
            "Enabled": self.Get("Autofix", False),
            "AllowedStages": ["REGISTER MAP", "ODN BUS", "BIOS POST", "KERNEL MAP"],
            "RequiresBlackBox": self.Get("BlackBox", True),
        }

    def BuildFirmwareConfig(self) -> FirmwareConfig:
        # Генерує об'єкт конфігурації для рівня Firmware на базі поточних налаштувань BIOS.
        Config = FirmwareConfig()
        Config.Version = getVersion()
        Config.Language = self.Get("Language", "UKRAINIAN")
        Config.DefaultBoot = self.Get("Target", Config.DefaultBoot)
        Config.Hardware = self.Hardware
        Config.BootEntries = list(self.BootEntries)
        for Entry in Config.BootEntries:
            Entry.Secure = bool(self.Get("SecureBoot", True)) and Entry.Secure
        return Config

    def RunPost(self) -> BiosReport:
        # POST не запускає UI. Він тільки перевіряє, чи система має право
        # продовжити ініціалізацію або має перейти в emergency.
        Started = time()
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
            # Якщо хоча б одна критична перевірка не пройдена — режим emergency
            if Check.Critical and Check.Status != "OK":
                Status = "EMERGENCY"

        Report = BiosReport(Status, Checks, self.Export(), Started, time())
        self.LastReport = Report
        Payload = self.ReportPayload(Report)

        self.PostCompleted.Emit(Payload)
        ODN.Emit("BIOS.POST", Payload)
        if Status == "NOMINAL":
            self.BootApproved.Emit(Payload)
            ODN.Emit("BIOS.BootApproved", Payload)
        else:
            self.EmergencyRequired.Emit(Payload)
            ODN.Emit("BIOS.EmergencyRequired", Payload)
        return Report

    def CheckPython(self) -> BiosCheck:
        # Перевірка версії Python runtime
        VersionOk = sys.version_info >= (3, 10)
        Detail = str(sys.version_info.major) + "." + str(sys.version_info.minor)
        return BiosCheck("PYTHON RUNTIME", "OK" if VersionOk else "FAIL", Detail)

    def CheckCoreModules(self) -> BiosCheck:
        # Перевірка наявності необхідних системних модулів LCARS
        Required = [
            "lcars.base.type",
            "lcars.core.signal",
            "lcars.modules.storage",
            "lcars.core.kernel",
            "lcars.system.emergency",
        ]
        Missing = [Name for Name in Required if importlib.util.find_spec(Name) is None]
        return BiosCheck("CORE MODULE MAP", "OK" if not Missing else "FAIL", ", ".join(Missing))

    def CheckODN(self) -> BiosCheck:
        # Перевірка стану каналу ODN та чорної скриньки
        HasBlackBox = hasattr(ODN, "BlackBox")
        Status = ODN.BlackBox.GetStatus() if HasBlackBox else {}
        Detail = Status.get("ChipName", "BLACK BOX OFFLINE") if isinstance(Status, dict) else "BLACK BOX OFFLINE"
        return BiosCheck("ODN TRANSMISSION BUS", "OK" if HasBlackBox else "FAIL", Detail)

    def CheckChipCatalog(self) -> BiosCheck:
        # Перевірка наявності чіпів у каталозі ізоліній
        Chips = ListChips()
        return BiosCheck("ISOLINEAR CHIP CATALOG", "OK" if Chips else "FAIL", str(len(Chips)) + " CHIPS")

    def CheckRequiredChips(self) -> BiosCheck:
        # Перевірка наявності всіх обов'язкових даних чіпів
        Required = [
            "ODN Black Box",
            "LCARS Primary Database",
            "LCARS System Registry",
            "Network Operations Chip",
            "Logbook Archive Chip",
        ]
        Missing = [Name for Name in Required if FindChip(Name) is None]
        return BiosCheck("REQUIRED DATA CHIPS", "OK" if not Missing else "FAIL", ", ".join(Missing))

    def CheckSettings(self) -> BiosCheck:
        # Перевірка коректності поточних налаштувань BIOS
        Invalid = []
        for Name, Setting in self.Settings.items():
            if Setting.Options and Setting.Value not in Setting.Options:
                Invalid.append(Name)
        return BiosCheck("BIOS CONFIGURATION", "OK" if not Invalid else "FAIL", ", ".join(Invalid))

    def CheckFirmwarePolicy(self) -> BiosCheck:
        # Перевірка відповідності UEFI-політики записам запуску
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
        # Перевірка коректності recovery-цілі
        Policy = self.RecoveryPolicy()
        Target = Policy.get("Target")
        if Target not in self.Settings["RecoveryTarget"].Options:
            return BiosCheck("RECOVERY POLICY", "FAIL", str(Target))
        return BiosCheck("RECOVERY POLICY", "OK", str(Target), False)

    def CheckConfigStorage(self) -> BiosCheck:
        # Перевірка доступності сховища конфігурації
        Parent = self.ConfigPath.parent
        Parent.mkdir(parents=True, exist_ok=True)
        return BiosCheck("BIOS CONFIG CHIP", "OK" if Parent.exists() else "FAIL", str(self.ConfigPath), False)

    def SaveAndExit(self) -> Dict[str, Any]:
        # Збереження конфігурації та вихід із BIOS
        Payload = self.Save()
        ODN.Emit("BIOS.SaveAndExit", Payload)
        return Payload

    def OpenChip(self, Name: str) -> Path:
        # BIOS не читає вміст бази напряму. Він лише знаходить потрібний чіп.
        return ResolveChipPath(Name)

    def ReportPayload(self, Report: BiosReport | None = None) -> Dict[str, Any]:
        # Формування повного пакету звіту для передачі на екрани
        ActiveReport = Report or self.LastReport or self.RunPost()
        Payload = self.ExportPayload()
        Payload.update({
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
        return Payload

    def Lines(self) -> List[str]:
        # Текстовий звіт BIOS для консолі
        Report = self.LastReport or self.RunPost()
        return Report.Lines()


def RunBios(Settings: Dict[str, Any] | None = None) -> BiosReport:
    # Запуск POST-перевірки BIOS
    return BIOS(Settings).RunPost()


def PerformAutofix(ErrorContext: Dict[str, Any] | None = None, ConsoleWidget: Any = None) -> None:
    # Реальний autofix живе в emergency-рівні. BIOS тільки передає політику й контекст.
    from lcars.system.emergency import PerformAutofix as EmergencyAutofix
    EmergencyAutofix(ErrorContext or {}, ConsoleWidget)


__all__ = [
    "BIOS",
    "UEFI",
    "LCARS",
    "BiosSetting",
    "BiosCheck",
    "BiosReport",
    "RunBios",
    "PerformAutofix",
]
