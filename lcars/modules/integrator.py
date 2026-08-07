# ◤ PLUGIN CHIP MANAGER
# Опис: Конвертація YAML плагінів в ізолінійні чіпи та управління ними
# Призначення: Містить ChipManager клас для роботи з плагінами як чіпами
# Потік: YAML → DetectFaction → CalculateCapacity → Create Chip → Insert to Slot
# Розташування: lcars/modules/ — модуль для управління плагін-чіпами
# ВЕРСІЯ: Делегована з lcars.base.version

from typing import Any, Dict, List, Optional
import yaml
from .library import (
    ChipStatus, IsolinearChip, IsolinearBank
)
from lcars.base.type import LCARS
# ═════════════════════════════════════════════════════════════════════════════
# ISOLINEAR MODULE
# Призначення: Функціональний модуль що реалізує логіку на базі чіпа
# Модуль підключається до чіпа та розширює його функціональність 
class IsolinearModule:
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
# PLUGIN CHIP MANAGER + AI INTEGRATOR
# Призначення: Розширення базової IsolinearBank + AI інтеграція (з GemmaIntegrator)
# Наслідує: IsolinearBank - отримує всі базові методи управління чіпами
# Розширює: AI провайдер, стани, метрики, історія розмов

class ChipManager(IsolinearBank):
    # Інтеграція з AI (GemmaIntegrator functionality)
    AIState: str = "offline"  # offline, initializing, ready, processing, error
    AIModel: str = "gemma4-9b"
    AIConversationHistory: List[Dict[str, str]] = []
    AIMetrics: Dict[str, Any] = {"requests": 0, "errors": 0, "avgResponseTime": 0.0}
    AIProviderRef: Any = None

    def LoadFromYaml(self, YamlPath: Any) -> Optional[IsolinearChip]:
        # Метод: Завантаження плагіна з YAML файлу та конвертація в ізолінійний чіп
        # Параметр YamlPath: шлях до файлу конфігурації плагіна (*.yaml)
        # Повертає: IsolinearChip об'єкт або None при помилці
        # Логіка: Перевірка існування → Читання → Парсинг → Валідація → Створення чіпа
        # Важливо: Не використовуємо try/except, тільки розгалуження для обробки помилок

        # Крок 1: Перевірка існування файлу через LCARS Directive.Path
        # LCARS.Directive.Path замінює os.path та pathlib для No-OS архітектури
        PathRef = LCARS.Directive.Path(YamlPath)
        FileExists = PathRef.exists()
        if not FileExists:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - File not found')
            return None

        # Крок 2: Перевірка чи це файл (не директорія)
        IsFile = PathRef.is_file()
        if not IsFile:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Path is not a file')
            return None

        # Крок 3: Читання вмісту файлу через LCARS інтерфейс
        # Chassis.Path.open замінює вбудовану функцію open для ізоляції від ОС
        FileContent = PathRef.read_text(encoding='utf-8')
        if FileContent is None:
            print(f'◤ CHIP LOAD ERROR: {YamlPath} - Cannot read file')
            return None

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
            'federation': 'Federation',
            'klingon': 'Klingon',
            'romulan': 'Romulan',
            'cardassian': 'Cardassian',
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

    # ◤ AI INTEGRATION METHODS (from GemmaIntegrator)
    def InitializeAI(self, Model: str = "gemma4-9b") -> bool:
        # Ініціалізація AI провайдера
        self.AIState = "initializing"
        self.AIModel = Model
        from lcars.service.provider import getProvider
        self.AIProviderRef = getProvider()
        self.AIProviderRef.initialize()
        self.AIState = "ready"
        return True

    def ProcessAIRequest(self, RequestData: Dict[str, Any]) -> Dict[str, Any]:
        # Обробка AI запиту через провайдера
        self.AIState = "processing"
        self.AIMetrics["requests"] += 1
        if self.AIProviderRef:
            Response = self.AIProviderRef.ask(str(RequestData))
            return {"success": True, "response": Response}
        return {"success": False, "error": "AI Provider not initialized"}

    def GetAISystemPrompt(self) -> str:
        # Системний промпт для AI
        return (
            "You are the LCARS Board Computer AI.\n"
            "Respond concisely and professionally.\n"
            "Use technical terminology appropriate for Starfleet systems.\n"
            "Format: [ACTION: <command>] <parameters>\n"
            "Actions: FILE_READ, FILE_WRITE, FILE_EDIT, COMMAND, ALERT, UI_OPEN\n"
        )
# ═════════════════════════════════════════════════════════════════════════════
# SINGLETON MANAGER INSTANCE
ManagerRef: Optional[ChipManager] = None
def GetManager() -> ChipManager:
    # Функція: Отримання єдиного екземпляру менеджера (singleton)
    # Призначення: Забезпечення доступу до одного менеджера чіпів в системі

    global ManagerRef
    if ManagerRef is None:
        ManagerRef = ChipManager()
    return ManagerRef

def Version() -> str:
    # Отримання версії модуля з базової системи
    from lcars.base.version import getVersion
    return getVersion()

__all__ = [
    'IsolinearModule', 'ChipManager', 'GetManager'
]
