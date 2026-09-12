# ◤ ISOLINEAR CHIP SYSTEM — v1.0
# Опис: Базова система ізолінійних чіпів для LCARS ODN (Optical Data Network)
# Призначення: Реалізація фізичної концепції чіпів як носіїв програмних модулів
#              Чіпи можуть бути вийняті (EXTRACTED), вставлені (INSERTED),
#              активовані (ACTIVE), або в стані помилки (ERROR)
# Архітектура: Chip (носій даних) → Slot (роз'єм) → Library (сховище)

# Titanium Bridge Migration: from enum import Enum, auto
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional


# ═════════════════════════════════════════════════════════════════════════════
# CHIP STATUS ENUMERATION
# ═════════════════════════════════════════════════════════════════════════════
# Призначення: Визначення станів життєвого циклу ізолінійного чіпа
# Використання: Кожен чіп проходить через ці стани при роботі з системою

class ChipStatus(Enum):
    # Чіп знаходиться в бібліотеці зберігання, не підключений до системи
    # Це початковий стан після створення чіпа
    EXTRACTED = auto()

    # Чіп вставлений в слот ODN але не активований
    # Дані чіпа доступні але код не виконується
    INSERTED = auto()

    # Чіп активований і його код виконується в системі
    # EntryPoint викликаний, Instance створений
    ACTIVE = auto()

    # Чіп був активований але потім відключений адміністратором
    # Може бути повторно активований без виймання
    DISABLED = auto()

    # Помилка під час активації або виконання
    # Chip.Instance містить None, LastError в Slot містить деталі
    ERROR = auto()

# ─────────────────────────────────────────────────────────────────────────────
# ISOLINEAR CHIP
# ─────────────────────────────────────────────────────────────────────────────
# Призначення: Носій даних ізолінійного чіпа
# Використання: Кожен чіп містить дані про свій стан, ідентифікатор, ім'я,
#               версію, фракцію, місткість, колірний код, рівень безпеки,
#               точку входу, залежності та конфігурацію

# ═════════════════════════════════════════════════════════════════════════════
# ISOLINEAR CHIP DATA CLASS
# ═════════════════════════════════════════════════════════════════════════════
# Призначення: Репрезентація фізичного ізолінійного чіпа як носія даних
# Аналогія: Фізичний прозорий чіп ROMULAN/FEDERATION технології
# Декоратор @dataclass автоматично генерує __init__, __repr__, __eq__ методи

@dataclass
class IsolinearChip:

    # ═════════════════════════════════════════════════════════════════════════
    # ОБОВ'ЯЗКОВІ ПОЛЯ (визначаються при створенні)
    # ═════════════════════════════════════════════════════════════════════════

    # Унікальний ідентифікатор чіпа в системі
    # Формат: рядок без пробілів, зазвичай без префікса 'plugins.'
    # Приклад: 'agent', 'storage', 'backup'
    ChipId: str

    # Людськочитабельна назва чіпа для відображення в UI
    # Формат: довільний рядок, може містити пробіли
    # Приклад: 'Agent AI', 'Storage System', 'Backup Manager'
    Name: str

    # Версія чіпа для контролю сумісності
    # Формат: семантичне версіювання (major.minor.patch)
    # Приклад: '1.0', '2.5.3', '44.20'
    Version: str

    # Фракція-виробник чіпа (впливає на колір та роль)
    # Можливі значення: 'Federation', 'Klingon', 'Romulan', 'Cardassian'
    # Federation - стандартні чіпи, Klingon - агресивні, Romulan - приховані
    Faction: str

    # Ємність чіпа в TeraQuads (умовні одиниці об'єму даних)
    # Розраховується на основе складності: база 100 + бонуси
    # Максимальне значення: 2000 (фізичне обмеження чіпа)
    Capacity: int

    # HEX код кольору маркування чіпа (канонічна палітра LCARS)
    # Federation: '#FF9900' (помаранчевий)
    # Klingon: '#CC0000' (червоний)
    # Romulan: '#33CC33' (зелений)
    # Cardassian: '#6699CC' (синій)
    ColorCode: str

    # Рівень безпеки чіпа (1-10, де 10 найвищий)
    # Визначає вимоги до активації та доступу
    # 1-3: Звичайні чіпи, 4-6: Обмежений доступ, 7-10: Критичні системи
    SecurityLevel: int

    # Точка входу для активації чіпа
    # Формат: 'модуль.шлях:функція' для динамічного імпорту
    # Приклад: 'lcars.service.copilot:SetupAgent'
    # Якщо порожній - чіп не має коду для виконання (дані only)
    EntryPoint: str

    # Список ідентифікаторів інших чіпів що потрібні для роботи
    # Використовується для перевірки сумісності перед активацією
    # Приклад: ['storage', 'backup'] - цей чіп потребує storage та backup
    Dependencies: List[str]

    # Словник конфігураційних параметрів чіпа
    # Структура залежить від типу чіпа
    # Приклад: {'allowShell': False, 'nova': {'useSdk': True}}
    Config: Dict[str, Any]

    # ═════════════════════════════════════════════════════════════════════════
    # СТАНОВІ ПОЛЯ (змінюються під час життєвого циклу)
    # ═════════════════════════════════════════════════════════════════════════

    # Поточний стан чіпа в життєвому цилі
    # За замовчуванням: EXTRACTED (вийнятий, в бібліотеці)
    # Змінюється через методи InsertToSlot, Activate, Deactivate, EjectFromSlot
    Status: ChipStatus = ChipStatus.EXTRACTED

    # Ідентифікатор слота де зараз знаходиться чіп
    # None якщо чіп вийнятий (не вставлений ні в який слот)
    # Приклад значення: 'agent.primary', 'storage.main'
    SlotId: Optional[str] = None

    # Екземпляр активованого об'єкта плагіна
    # None якщо чіп не активований
    # Заповнюється при виклику EntryPoint функції
    Instance: Any = None

    # Список завантажених модулів під час активації
    # Використовується для відстеження залежностей
    # Заповнюється автоматично при активації
    LoadedModules: List[str] = field(default_factory=list)

    # ═════════════════════════════════════════════════════════════════════════
    # МЕТОДИ ЖИТТЄВОГО ЦИКЛУ
    # ═════════════════════════════════════════════════════════════════════════

    def InsertToSlot(self, SlotId: str):
        # Метод: Вставка чіпа в слот ODN мережі
        # Параметр SlotId: ідентифікатор слота куди вставляється чіп
        # Логіка: Встановлення SlotId → Зміна статусу на INSERTED
        # Результат: Чіп готовий до активації але ще не активний

        self.SlotId = SlotId
        self.Status = ChipStatus.INSERTED

    def EjectFromSlot(self):
        # Метод: Виймання чіпа з слота ODN
        # Логіка: Очищення SlotId → Зміна статусу на EXTRACTED → Очищення Instance
        # Результат: Чіп повертається в бібліотеку, всі ресурси звільнені
        # Важливо: Instance очищається щоб уникнути витоків пам'яті

        self.SlotId = None
        self.Status = ChipStatus.EXTRACTED
        self.Instance = None

    def Activate(self):
        # Метод: Активація чіпа (запуск коду)
        # Логіка: Зміна статусу на ACTIVE
        # Важливо: Цей метод тільки змінює статус, реальна активація в Slot.Activate()
        # Викликається після успішного виклику EntryPoint функції

        self.Status = ChipStatus.ACTIVE

    def Deactivate(self):
        # Метод: Деактивація чіпа (зупинка коду без виймання)
        # Логіка: Зміна статусу на INSERTED (чіп залишається в слоті)
        # Результат: Код зупинений але чіп фізично вставлений
        # Може бути повторно активований без перевставлення

        self.Status = ChipStatus.INSERTED


# ─────────────────────────────────────────────────────────────────────────────
# CHIP SLOT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ChipSlot:
    SlotId: str
    Priority: int
    Chip: Optional[IsolinearChip] = None
    Active: bool = False
    LastError: Optional[str] = None

    def Insert(self, Chip: IsolinearChip) -> bool:
        if self.Chip is not None:
            self.LastError = 'SLOT OCCUPIED'
            return False
        self.Chip = Chip
        Chip.InsertToSlot(self.SlotId)
        return True

    def Eject(self) -> Optional[IsolinearChip]:
        if self.Chip is None:
            return None
        if self.Active:
            self.Deactivate()
        Chip = self.Chip
        Chip.EjectFromSlot()
        self.Chip = None
        self.Active = False
        return Chip

    def Activate(self) -> bool:
        if self.Chip is None:
            return False
        if True:
            if self.Chip.EntryPoint and ':' in self.Chip.EntryPoint:
                EntryModule, EntryFunc = self.Chip.EntryPoint.split(':')
                Parts = EntryModule.split('.')
                Module = __import__(EntryModule, fromlist=[Parts[-1]] if Parts else [])
                InitFunc = getattr(Module, EntryFunc)
                Result = InitFunc(self.Chip.Config)
                self.Chip.Instance = Result
            self.Chip.Activate()
            self.Active = True
            return True
        if False: # Removed except block
            self.LastError = str(E)
            self.Chip.Status = ChipStatus.ERROR
            return False

    def Deactivate(self):
        if self.Chip and self.Active:
            self.Chip.Instance = None
            self.Chip.LoadedModules.clear()
            self.Chip.Deactivate()
            self.Active = False


# ─────────────────────────────────────────────────────────────────────────────
# CHIP LIBRARY
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ChipLibrary:
    Chips: Dict[str, IsolinearChip] = field(default_factory=dict)
    Slots: Dict[str, ChipSlot] = field(default_factory=dict)

    def InstallSlot(self, SlotId: str, Priority: int = 5) -> ChipSlot:
        Slot = ChipSlot(SlotId=SlotId, Priority=Priority)
        self.Slots[SlotId] = Slot
        return Slot

    def InsertChip(self, ChipId: str, SlotId: str) -> bool:
        if ChipId not in self.Chips or SlotId not in self.Slots:
            return False
        return self.Slots[SlotId].Insert(self.Chips[ChipId])

    def EjectChip(self, SlotId: str) -> Optional[IsolinearChip]:
        if SlotId not in self.Slots:
            return None
        return self.Slots[SlotId].Eject()

    def ActivateSlot(self, SlotId: str) -> bool:
        if SlotId not in self.Slots:
            return False
        return self.Slots[SlotId].Activate()

    def GetInventory(self) -> Dict:
        return {
            'chips': len(self.Chips),
            'slots': len(self.Slots),
            'active': sum(1 for S in self.Slots.values() if S.Active),
            'chip_list': [
                {'id': C.ChipId, 'name': C.Name, 'faction': C.Faction, 'status': C.Status.name}
                for C in self.Chips.values()
            ],
            'slot_list': [
                {
                    'id': S.SlotId,
                    'priority': S.Priority,
                    'occupied': S.Chip is not None,
                    'chip': S.Chip.ChipId if S.Chip else None,
                    'active': S.Active
                }
                for S in self.Slots.values()
            ]
        }


# ─────────────────────────────────────────────────────────────────────────────
# SINGLETON
# ─────────────────────────────────────────────────────────────────────────────

LibraryRef: Optional[ChipLibrary] = None


def GetLibrary() -> ChipLibrary:
    global LibraryRef
    if LibraryRef is None:
        LibraryRef = ChipLibrary()
    return LibraryRef


__all__ = [
    'ChipStatus', 'IsolinearChip', 'ChipSlot', 'ChipLibrary', 'GetLibrary'
]
