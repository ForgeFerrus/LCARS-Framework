# ◤ PLUGIN CHANNEL — v1.0
# Опис: Ініціалізація ізолінійних чіпів з plugin/chips/ в систему LCARS
# Призначення: Точка входу для завантаження чіпів з епох та їх активація
# Потік: Сканування епох → Завантаження YAML → Інтеграція в ODN → Активація

from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml

# Імпорт ізолінійної системи з інженерного відсіку
# IsolinearChip, IsolinearBank, IsolinearModule - базові компоненти
# IsolinearController - контролер активації/деактивації
# IsolinearRegistry - реєстр відповідності чіп-бібліотека
# IsolinearSocket - точки інтеграції чіпів
from lcars.engineering.isolinear import (
    ChipStatus, IsolinearChip, IsolinearBank, IsolinearModule, ChipChannel, NetworkChannel
)
from lcars.engineering.controller import IsolinearController
from lcars.engineering.optical import IsolinearSocket, SocketArray, GetSocketArray

# Імпорт API плагінів для реєстрації компонентів
from lcars.service.plugin import PluginApi, AgentPlugin, BackupPlugin
from lcars.base.register import Registry

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM INITIALIZATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def InitializeODN() -> SocketArray:
    # Функція: Ініціалізація Optical Data Network (ODN) для чіпів
    # Логіка: Створення SocketArray → Додавання сокетів з пріоритетами
    # Повертає: Налаштований SocketArray з готовими сокетами

    # Отримання єдиного екземпляру масиву сокетів (singleton)
    SocketArrayRef = GetSocketArray("main")

    # Список сокетів з їх ідентифікаторами та пріоритетами
    # Пріоритет 1 - найвищий (ядро системи)
    # Пріоритет 10 - найнижчий (теми, UI)
    SocketDefinitions = [
        ('core.alpha', 1),
        ('core.beta', 1),
        ('agent.primary', 3),
        ('storage.main', 5),
        ('backup.aux', 7),
        ('detector.geant4', 9),
        ('nova.ide', 9),
        ('theme.dynamic', 10)
    ]

    # Додавання кожного сокета в масив
    for SocketId, Priority in SocketDefinitions:
        SocketArrayRef.AddSocket(SocketId, Priority)

    return SocketArrayRef


def LoadChipFromYaml(YamlPath: Path, Bank: IsolinearBank) -> Optional[IsolinearChip]:
    # Функція: Завантаження одного YAML файлу як чіпа
    # Параметри: YamlPath - шлях до файлу, Bank - банк для реєстрації
    # Повертає: IsolinearChip або None при помилці

    import os

    # Перевірка існування файлу
    if not os.path.exists(YamlPath):
        return None
    if not os.path.isfile(YamlPath):
        return None

    # Читання та парсинг YAML
    with open(YamlPath, 'r', encoding='utf-8') as F:
        Data = yaml.safe_load(F)

    if Data is None or not isinstance(Data, dict):
        return None

    # Перевірка обов'язкових полів
    if 'id' not in Data or 'name' not in Data or 'version' not in Data:
        return None

    # Створення чіпа та додавання в банк
    ChipId = Data['id'].replace('plugins.', '')
    Chip = Bank.AddChip(ChipId)

    return Chip


def LoadAllChipsFromEpochs(Bank: IsolinearBank) -> int:
    # Функція: Завантаження всіх чіпів з епох (plugin/chips/XX-XXXX/)
    # Логіка: Сканування директорій епох → Завантаження YAML → Реєстрація в банку
    # Повертає: Кількість успішно завантажених чіпів

    # Визначення шляху до директорії чіпів
    ChipsDirectory = Path(__file__).parent / 'chips'

    # Лічильник успішно завантажених чіпів
    LoadedCount = 0

    # Перевірка чи існує директорія чіпів
    if not ChipsDirectory.exists():
        return 0

    # Сканування директорій епох (формат: XX-XXXX)
    for EpochDir in ChipsDirectory.iterdir():
        if EpochDir.is_dir():
            # Сканування YAML файлів в епосі
            for YamlFile in EpochDir.glob('*.yaml'):
                Chip = LoadChipFromYaml(YamlFile, Bank)
                if Chip is not None:
                    LoadedCount += 1

    return LoadedCount


def AutoInsertChips(Sockets: SocketArray, Bank: IsolinearBank) -> int:
    # Функція: Автоматична вставка чіпів у відповідні сокети ODN
    # Логіка: Мапінг chipId → socketId → Вставка чіпа в сокет
    # Повертає: Кількість успішно вставлених чіпів

    # Мапінг ідентифікаторів чіпів на ідентифікатори сокетів
    ChipToSocketMapping = {
        'agent': 'agent.primary',
        'storage': 'storage.main',
        'backup': 'backup.aux',
        'detector': 'detector.geant4',
        'nova': 'nova.ide',
        'theme': 'theme.dynamic'
    }

    InsertedCount = 0

    for ChipId, SocketId in ChipToSocketMapping.items():
        # Перевірка чи чіп існує в банку
        if ChipId not in Bank.Chips:
            continue

        # Отримання сокета та вставка
        Socket = Sockets.GetSocket(SocketId)
        if Socket:
            Success = Socket.Insert(ChipId)
            if Success:
                InsertedCount += 1

    return InsertedCount


def GetChipSystemStatus(Bank: IsolinearBank, Sockets: SocketArray) -> Dict:
    # Функція: Отримання повної інвентаризації системи чіпів
    # Повертає: Словник з інформацією про чіпи та сокети

    return {
        'bank': Bank.ClusterStatus(),
        'sockets': Sockets.GetStatus()
    }

# ─────────────────────────────────────────────────────────────────────────────
# CHIP-AWARE SETUP FUNCTIONS (Legacy API Compatibility)
# ─────────────────────────────────────────────────────────────────────────────
# Ці функції забезпечують сумісність з існуючим кодом що очікує старий API


def SetupCopilot(Api: PluginApi, Cfg: Dict, Bank: IsolinearBank) -> Any:
    # Функція: Налаштування AI копілота через плагін
    # Логіка: Створення чіпа → Додавання в банк → Реєстрація в реєстрі → Завантаження модуля

    # Створення та додавання чіпа в банк
    Chip = Bank.AddChip('copilot')
    Chip.Faction = 'Federation'

    # Реєстрація в реєстрі
    Registry.Register('copilot', 'lcars.service.copilot', 'CopilotModule', {'config': Cfg})

    # Завантаження та активація плагіна (тимчасова заглушка до реалізації CopilotPlugin)
    # return CopilotPlugin().Load(Api, Cfg)
    return {'chip': 'copilot', 'cfg': Cfg}


def SetupBackup(Api: PluginApi, Cfg: Dict, Bank: IsolinearBank) -> Any:
    # Функція: Налаштування системи резервного копіювання
    # Логіка: Створення чіпа → Додавання в банк → Реєстрація → Завантаження

    Chip = Bank.AddChip('backup')
    Chip.Faction = 'Federation'
    Registry.Register('backup', 'lcars.core.backup', 'BackupModule', {'config': Cfg})
    return BackupPlugin().Load(Api, Cfg)


def SetupControl(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для плагіна контролю системи
    return {'chip': 'control', 'cfg': Cfg}


def SetupDetector(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для плагіна GEANT4 детекторів
    return {'chip': 'detector', 'cfg': Cfg}


def SetupNova(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для плагіна Nova Act
    return {'chip': 'nova', 'cfg': Cfg}

def SetupStorage(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для плагіна сховища
    return {'chip': 'storage', 'cfg': Cfg}

def SetupTheme(Api: PluginApi, Cfg: Dict) -> Any:
    # Функція: Налаштування теми через плагін
    # Імпорт ThemePlugin виконується тут щоб уникнути циклічних залежностей
    from lcars.service.plugin import ThemePlugin
    return ThemePlugin().Load(Api, Cfg)

def SetupUi(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для UI плагіна
    return {'chip': 'ui', 'cfg': Cfg}


def SetupMatrix(Api: PluginApi, Cfg: Dict) -> Dict:
    # Заглушка для Matrix ядра
    return {'chip': 'matrix', 'cfg': Cfg}


# ─────────────────────────────────────────────────────────────────────────────
# EXPORTS
# ─────────────────────────────────────────────────────────────────────────────

__all__ = [
    # Класи ізолінійної системи (з engineering)
    'IsolinearChip', 'IsolinearBank', 'IsolinearModule',
    'IsolinearController', 'IsolinearRegistry', 'GetIsolinearRegistry',
    'IsolinearSocket', 'SocketArray', 'GetSocketArray',
    'ChipChannel', 'NetworkChannel',
    # Функції ініціалізації
    'InitializeODN', 'LoadChipFromYaml', 'LoadAllChipsFromEpochs',
    'AutoInsertChips', 'GetChipSystemStatus',
    # Legacy setup functions
    'SetupCopilot', 'SetupBackup', 'SetupControl', 'SetupDetector', 'SetupMatrix',
    'SetupNova', 'SetupStorage', 'SetupTheme', 'SetupUi'
]
