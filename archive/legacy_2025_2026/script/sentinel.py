# ◤ SENTINEL :: LCARS AUTOMATIC MAINTENANCE SCRIPT 🖖
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Автоматичний скрипт для очистки проекту від кешу.
# КЛАСИФІКАЦІЯ: Maintenance Script (Автоматичний сервісний скрипт).
# ПРОТОКОЛ: TITANIUM Master (Pure LCARS Shims & Zero OS Direct).
#
# ПОВНЕ ПОЯСНЕННЯ (УКРАЇНСЬКОЮ):
#   
# 1. СТРАТЕГІЯ ЛКАРС:
#    Ми ПОВНІСТЮ відмовилися від 'os', 'time' та інших прямих імпортів. 
#    Весь функціонал працює через 'Directive' та 'Technical' вузли LCARS.
#
# 2. ПОДІЙНИЙ ЦИКЛ:
#    Скрипт інтегрований у головну чергу подій ЛКАРС (EventLoop). 
#    Він не "заморожує" потік, а працює асинхронно через таймери.
#
# 3. TITANIUM CamelCase ПРАВИЛА:
#    - Жодних 'try/except'. Тільки пряма верифікація вузлів.
#    - Жодних потрійних лапок. Тільки лінійні коментарі.
#    - Використовується стиль CamelCase для всіх ідентифікаторів.
# ───────────────────────────────────────────────────────────────

import sys
import shutil
from pathlib import Path

# Bootstrap: додаємо корінь проекту до шляху
# Використовуємо стандартний Path тільки для bootstrap (необхідний мінімум)
_ProjectRoot = Path(__file__).resolve().parent.parent
if str(_ProjectRoot) not in sys.path:
    sys.path.insert(0, str(_ProjectRoot))

# Імпорт головних вузлів LCARS Titanium
from lcars.base.type import Directive, LCARS, registry

# Спрощене журналювання замість відсутнього модуля
class AutoJournal:
    def __init__(self):
        pass
    
    def log(self, message):
        print(f"◤ JOURNAL :: {message}")

class UpdateJournal:
    def __init__(self):
        pass
    
    def log(self, message):
        print(f"◤ UPDATE :: {message}")

# ◤ КЛАС: SentinelHandler (Обробник автоматичного очищення)
class SentinelHandler:
    def __init__(self, RootDirectoryNode):
        # Ініціалізація головного вузла сканування (PathDrive)
        self.RootDirectory = RootDirectoryNode
        # Системні зони виключення
        self.IgnoreNodesSet = {".venv", ".git", ".idea", ".vscode"}
        print(f"◤ UTILITY SENTINEL :: ACTIVE :: MONITORING PROMPT {self.RootDirectory}")

    # Протокол автоматичного перехоплення вузлів кешу (LCARS Matrix Scan)
    def InterceptProtocol(self):
        # Спочатку будуємо повний snapshot-список ПЕРЕД видаленням.
        # rglob — lazy generator: видалення під час ітерації ламає його на Windows.
        # parts замість str() — точна перевірка компонентів шляху без хибних збігів.
        TargetList = [
            P for P in self.RootDirectory.rglob("__pycache__")
            if not any(I in P.parts for I in self.IgnoreNodesSet)
            and P.is_dir()
        ]
        for TargetNode in TargetList:
            self.PurgeNode(TargetNode)

    def PurgeNode(self, TargetNode):
        # Алгоритмічне видалення за стандартом Titanium
        # Перевіряємо чи вузол існує перед видаленням
        if not TargetNode.exists():
            return
        # Отримуємо модуль доступу до системи через реєстр LCARS
        SystemAccessModule = registry.Get("System.Sys")
        # Перевіряємо чи є права на запис і видалення
        # Використовуємо os.access для верифікації доступу без виклику exception
        OperatingSystemModule = registry.Get("System.LCARS")
        AccessCheckResult = OperatingSystemModule.access(TargetNode, OperatingSystemModule.W_OK)
        if not AccessCheckResult:
            print(f"◤ UTILITY SENTINEL :: ACCESS DENIED: {TargetNode}")
            return
        # Видаляємо директорію та все її вміст
        # Використовуємо rmtree без обробника помилок — дотримання протоколу Zero-Except
        shutil.rmtree(TargetNode)
        # Повідомляємо про успішне видалення
        print(f"◤ UTILITY SENTINEL :: PURGED: {TargetNode.relative_to(self.RootDirectory)}")

# ◤ ФУНКЦІЯ: RunSentinelSubsystem (Запуск автоматичного циклу)
def RunSentinelSubsystem():
    SentinelNode = SentinelHandler(_ProjectRoot)

    # Негайне очищення при старті
    SentinelNode.InterceptProtocol()
    # Налаштування моніторингу файлової системи для миттєвого реагування
    # Отримуємо QFileSystemWatcher з реєстру — правильний ключ Base.FileWatcher
    FileSystemWatcherClass = registry.Get("Base.FileWatcher")
    DirectoryWatcherNode = FileSystemWatcherClass()
    
    # Додаємо корінь проекту до списку відстежуваних директорій
    DirectoryWatcherNode.addPath(str(SentinelNode.RootDirectory))
    # Підключаємо сигнал directoryChanged — викликається при створенні/видаленні папок
    DirectoryWatcherNode.directoryChanged.connect(SentinelNode.InterceptProtocol)
    
    # Зберігаємо посилання на обробник усередині вузла спостерігача
    # Це запобігає знищенню обробника збирачем сміття
    DirectoryWatcherNode.SentinelHandlerReference = SentinelNode
    
    print("◤ UTILITY SENTINEL :: OPERATIONAL :: FILESYSTEM WATCHER ACTIVE")
    print("◤ UTILITY SENTINEL :: MODE :: REALTIME — PURGE ON DETECTION")
    return DirectoryWatcherNode

if __name__ == "__main__":
    # Отримуємо клас QApplication з реєстру — правильний ключ "Interface.Application"
    AppClassNodeValue = registry.Get("Interface.Application")
    # QApplication є сінглтоном — спочатку перевіряємо instance(), інакше створюємо
    MainProcessNode = AppClassNodeValue.instance() or AppClassNodeValue(sys.argv)
    
    ActiveSentinelReference = RunSentinelSubsystem()
    MainProcessNode.exec()
    
