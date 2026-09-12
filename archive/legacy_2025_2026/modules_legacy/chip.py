# ◤ PLUGIN CHIP MANAGER — v1.0
# Опис: Конвертація YAML плагінів в ізолінійні чіпи та управління ними
# Призначення: Містить PluginChipManager клас для роботи з плагінами як чіпами
# Потік: YAML → DetectFaction → CalculateCapacity → Create Chip → Insert to Slot
# Розташування: lcars/modules/ — модуль для управління плагін-чіпами

# Titanium Bridge Migration: from typing import Any, Dict, List, Optional
# Titanium Bridge Migration: from pathlib import Path

from lcars.engineering.isolinear import (
    ChipStatus, IsolinearChip, IsolinearBank
)

# Titanium Bridge Migration: import yaml
# Titanium Bridge Migration: import os


# ═════════════════════════════════════════════════════════════════════════════
# ISOLINEAR MODULE
# ═════════════════════════════════════════════════════════════════════════════
# Призначення: Функціональний модуль що реалізує логіку на базі чіпа

class IsolinearModule:
    # Модуль підключається до чіпа та розширює його функціональність

    def __init__(self, ModuleId: str, ParentChip: Any):
        self.ModuleId = ModuleId
        self.ParentChip = ParentChip
        self.Active = False
        self.EntryPoint: Optional[str] = None
        self.Instance: Any = None

    def Load(self, EntryPoint: str) -> bool:
        # Завантаження коду модуля через EntryPoint
        self.EntryPoint = EntryPoint
        if EntryPoint and ':' in EntryPoint:
            EntryModule, EntryFunc = EntryPoint.split(':')
            Parts = EntryModule.split('.')
            Module = __import__(EntryModule, fromlist=[Parts[-1]] if Parts else [])
            InitFunc = getattr(Module, EntryFunc)
            self.Instance = InitFunc()
            return True
        return False

    def Activate(self) -> bool:
        # Активація модуля
        if not self.ParentChip.Connected:
            return False
        if self.Instance is None:
            return False
        self.Active = True
        return True

    def Deactivate(self):
        # Деактивація модуля
        self.Active = False


# ═════════════════════════════════════════════════════════════════════════════
# PLUGIN CHIP MANAGER
# ═════════════════════════════════════════════════════════════════════════════
# Призначення: Розширення базової IsolinearBank специфічною логікою конвертації
#              YAML файлів плагінів в ізолінійні чіпи
# Наслідує: IsolinearBank - отримує всі базові методи управління чіпами
# Розширює: Логіка парсингу YAML, визначення фракцій, розрахунок параметрів чіпа

class PluginChipManager(IsolinearBank):

    def LoadFromYaml(self, YamlPath: Path) -> Optional[IsolinearChip]:
        # Метод: Завантаження плагіна з YAML файлу та конвертація в ізолінійний чіп
        # Параметр YamlPath: шлях до файлу конфігурації плагіна (*.yaml)
        # Повертає: IsolinearChip об'єкт або None при помилці
        # Логіка: Перевірка існування → Читання → Парсинг → Валідація → Створення чіпа
        # Важливо: Не використовуємо try/except, тільки розгалуження для обробки помилок

        # Крок 1: Перевірка існування файлу перед спробою читання
        # os.path.exists повертає True якщо шлях існує в файловій системі
        FileExists = os.path.exists(YamlPath)
        if not FileExists:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - File not found')
            return None

        # Крок 2: Перевірка чи це файл (не директорія)
        # os.path.isfile повертає True тільки для файлів
        IsFile = os.path.isfile(YamlPath)
        if not IsFile:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Path is not a file')
            return None

        # Крок 3: Читання вмісту файлу в рядок
        # Використовуємо open з явним вказівником кодування UTF-8
        # read() зчитує весь файл однією операцією
        FileContent = None
        FileHandle = open(YamlPath, 'r', encoding='utf-8')
        if FileHandle:
            FileContent = FileHandle.read()
            FileHandle.close()

        # Перевірка чи вдалося прочитати файл
        if FileContent is None:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Cannot read file')
            return None

        # Крок 4: Парсинг YAML вмісту в Python словник
        # yaml.safe_load конвертує YAML текст в dict
        # Перевіряємо результат на None (помилка парсингу)
        Data = yaml.safe_load(FileContent)
        if Data is None:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - YAML parse failed (empty or invalid)')
            return None

        # Перевірка чо це словник (dict), а не список чи інший тип
        IsDict = isinstance(Data, dict)
        if not IsDict:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - YAML root must be dictionary')
            return None

        # Крок 5: Валідація обов'язкових полів
        # metadata.id - унікальний ідентифікатор плагіна (обов'язковий)
        # metadata.name - відображувана назва (обов'язковий)
        # metadata.version - версія для контролю сумісності (обов'язковий)
        Metadata = Data.get('metadata', {})
        HasId = 'id' in Metadata
        HasName = 'name' in Metadata
        HasVersion = 'version' in Metadata

        if not HasId:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Missing required field: metadata.id')
            return None
        if not HasName:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Missing required field: metadata.name')
            return None
        if not HasVersion:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Missing required field: metadata.version')
            return None

        # Крок 6: Визначення фракції чіпа на основі тегів та назви
        # Фракція впливає на колір чіпа та роль в системі
        Faction = self.DetectFaction(Data)

        # Крок 7: Отримання ємності з specs або розрахунок
        Specs = Data.get('specs', {})
        Capacity = Specs.get('capacity', 100)

        # Крок 8: Визначення кольору чіпа відповідно до фракції
        ColorCode = Specs.get('color_code', self.GetFactionColor(Faction))

        # Крок 9: Отримання рівня безпеки
        SecurityLevel = Specs.get('security_level', 1)

        # Крок 10: Створення ізолінійного чіпа через банк
        # ChipId: ідентифікатор без префікса 'plugins.'
        RawId = Metadata['id']
        CleanId = RawId.replace('plugins.', '')

        # Створення чіпа через батьківський метод AddChip
        Chip = self.AddChip(CleanId, Faction)

        # Крок 11: Додавання метаданих до чіпа
        Chip.Name = Metadata['name']
        Chip.Version = Metadata['version']
        Chip.Capacity = Capacity
        Chip.ColorCode = ColorCode
        Chip.SecurityLevel = SecurityLevel
        Chip.EntryPoints = Data.get('entrypoints', {})
        Chip.Config = Data.get('config', {})
        Chip.Dependencies = Data.get('dependencies', [])
        Chip.Paths = Data.get('paths', {})
        Chip.Interfaces = Data.get('interfaces', [])
        Chip.Tags = Data.get('tags', [])

        # Повернення створеного чіпа
        return Chip

    def LoadAllFromCategory(self, CategoryPath: Path) -> int:
        # Метод: Завантаження всіх YAML чіпів з категорії (папки)
        # Параметр CategoryPath: шлях до папки з YAML файлами
        # Повертає: Кількість успішно завантажених чіпів

        LoadedCount = 0

        # Перевірка існування папки
        if not CategoryPath.exists():
            return 0
        if not CategoryPath.is_dir():
            return 0

        # Сканування всіх YAML файлів в папці
        for YamlFile in CategoryPath.glob('*.yaml'):
            Chip = self.LoadFromYaml(YamlFile)
            if Chip is not None:
                LoadedCount += 1

        return LoadedCount

    def DetectFaction(self, Data: Dict) -> str:
        # Метод: Визначення фракції чіпа на основі тегів або назви
        # Логіка: Перевірка тегів на відповідність відомим фракціям
        #         Якщо тегів немає - перевірка назви плагіна
        #         За замовчуванням - Federation (стандартна фракція системи)
        # Повертає: Рядок з назвою фракції (Federation, Klingon, Romulan, Cardassian)

        # Отримання списку тегів з даних, порожній список якщо відсутні
        Tags = Data.get('tags', [])

        # Отримання назви плагіна в нижньому регістрі для пошуку
        Metadata = Data.get('metadata', {})
        NameLower = Metadata.get('name', '').lower()

        # Мапінг ключових слів на фракції
        # Ключ - слово для пошуку, Значення - назва фракції
        FactionKeywords = {
            'klingon': 'Klingon',
            'romulan': 'Romulan',
            'cardassian': 'Cardassian',
            'borg': 'Borg',
            'bajoran': 'Bajoran',
            'dominion': 'Dominion'
        }

        # Перевірка тегів на відповідність фракціям
        # Перебір кожного тегу та порівняння з ключовими словами
        for Tag in Tags:
            TagLower = str(Tag).lower()
            if TagLower in FactionKeywords:
                return FactionKeywords[TagLower]

        # Якщо теги не вказали фракцію - перевірка назви
        for Keyword, FactionName in FactionKeywords.items():
            if Keyword in NameLower:
                return FactionName

        # За замовчуванням - Federation (базова фракція системи)
        return 'Federation'

    def GetFactionColor(self, Faction: str) -> str:
        # Метод: Отримання кольору маркування для фракції
        # Кольори відповідають канонічній палітрі LCARS
        # Federation: Помаранчевий (основний колір системи)
        # Klingon: Червоний (агресивна фракція)
        # Romulan: Зелений (прихована фракція)
        # Cardassian: Коричневий (військова фракція)
        # Borg: Зелений (колектив)
        # Bajoran: Помаранчевий (вірянська фракція)

        FactionColors = {
            'Federation': '#FF9900',
            'Klingon': '#CC0000',
            'Romulan': '#33CC33',
            'Cardassian': '#996600',
            'Borg': '#00FF00',
            'Bajoran': '#FF6600',
            'Dominion': '#9900CC'
        }

        # Повернення кольору або світло-блакитний якщо фракція невідома
        DefaultColor = '#99CCFF'
        return FactionColors.get(Faction, DefaultColor)

    def AutoInsertChips(self, Controller: Any) -> int:
        # Метод: Автоматична вставка та активація всіх завантажених чіпів
        # Параметр Controller: IsolinearController для управління активацією
        # Повертає: Кількість успішно активованих чіпів

        ActivatedCount = 0

        for ChipId, Chip in self.Chips.items():
            # Перевірка чи чіп має entrypoint для активації
            HasEntry = len(Chip.EntryPoints) > 0 if hasattr(Chip, 'EntryPoints') else False

            if HasEntry:
                # Спроба активації через контролер
                Success = Controller.ActivateChip(ChipId)
                if Success:
                    ActivatedCount += 1

        return ActivatedCount


# ═════════════════════════════════════════════════════════════════════════════
# SINGLETON MANAGER INSTANCE
# ═════════════════════════════════════════════════════════════════════════════

ManagerRef: Optional[PluginChipManager] = None


def GetManager() -> PluginChipManager:
    # Функція: Отримання єдиного екземпляру менеджера (singleton)
    # Призначення: Забезпечення доступу до одного менеджера чіпів в системі

    global ManagerRef
    if ManagerRef is None:
        ManagerRef = PluginChipManager()
    return ManagerRef


__all__ = [
    'IsolinearModule', 'PluginChipManager', 'GetManager'
]
