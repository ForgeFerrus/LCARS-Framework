# ◤ SENTINEL :: LCARS АВТОНОМНИЙ ДЕМОН ОЧИЩЕННЯ ТА НАГЛЯДУ 🖖
#
# Всі системні виклики здійснюються виключно через простір імен LCARS.
# 1. Автономне миттєве видалення каталогів кешу (__pycache__, .pytest_cache, .cache) та компільованих файлів.
# 2. Перевірка дотримання архітектурних правил (заборона прямих імпортів бібліотек Qt).
# 3. Чисте алгоритмічне розгалудження через умови без використання сліпих обробників.
# 4. Повна відповідність канонічному PascalCase стилю і україномовних коментарів.

from lcars.base.type import LCARS

# Визначення кореневого каталогу проекту через LCARS.System.Path
ProjectRoot = LCARS.System.Path(__file__).resolve().parent.parent

# Каталог для системних журналів подій
LogsDir = ProjectRoot / "logs"

# Створення каталогу логів за потреби
if not LogsDir.exists():
    LogsDir.mkdir(parents=True, exist_ok=True)

# Файл журналювання подій
LogFile = LogsDir / "sentinel.log"

# Конфігурація логування через LCARS.System.Log
LCARS.System.Log.basicConfig(
    level=LCARS.System.Log.INFO,
    format="%(asctime)s [%(levelname)s] [SENTINEL] %(message)s",
    handlers=[
        LCARS.System.Log.FileHandler(LogFile, encoding="utf-8"),
        LCARS.System.Log.StreamHandler()
    ]
)
Logger = LCARS.System.Log.getLogger("Sentinel")

# Список службових директорій, які ігноруються при скануванні
IgnoredDirectories = {".git", ".venv", ".idea", ".vscode", "node_modules", "archive", "data"}

# ── 1. АЛГОРИТМІЧНЕ ОЧИЩЕННЯ КЕШУ ──────────────────────────────

# Пошук усіх кеш-директорій у просторі проекту
def FindCacheDirs(RootNode):
    CacheDirs = []
    
    if not RootNode.exists() or not RootNode.is_dir():
        return CacheDirs

    # Прохід файловим деревом через LCARS.System.Walk
    for DirPath, DirNames, _ in LCARS.System.Walk(str(RootNode)):
        PathSegments = LCARS.System.Path(DirPath).parts
        if any(IgnoredItem in PathSegments for IgnoredItem in IgnoredDirectories):
            continue

        for ItemName in list(DirNames):
            if ItemName in ("__pycache__", ".pytest_cache", ".cache"):
                TargetDirectory = LCARS.System.Path(DirPath) / ItemName
                if TargetDirectory.exists() and TargetDirectory.is_dir():
                    CacheDirs.append(TargetDirectory)
                DirNames.remove(ItemName)

    return CacheDirs

# Видалення конкретного каталогу кешу
def PurgeCacheDir(TargetDir):
    if not TargetDir.exists() or not TargetDir.is_dir():
        return None

    DirPathString = str(TargetDir)
    RelativePathString = str(TargetDir.relative_to(ProjectRoot))

    # Видалення директорії через LCARS.System.Filesystem.rmtree
    LCARS.System.Filesystem.rmtree(DirPathString, ignore_errors=True)

    # Додаткова перевірка через команду оболонки при блокуванні дескрипторів
    if TargetDir.exists():
        LCARS.System.Execute(f'rmdir /s /q "{DirPathString}" >nul 2>&1')

    if not TargetDir.exists():
        return RelativePathString

    return None

# Видалення поодиноких байткод-файлів .pyc та .pyo
def PurgeOrphanPyc(RootNode):
    DeletedCount = 0

    if not RootNode.exists() or not RootNode.is_dir():
        return 0

    for DirPath, _, FileNames in LCARS.System.Walk(str(RootNode)):
        PathSegments = LCARS.System.Path(DirPath).parts
        if any(IgnoredItem in PathSegments for IgnoredItem in IgnoredDirectories):
            continue

        for FileName in FileNames:
            if FileName.endswith(".pyc") or FileName.endswith(".pyo"):
                TargetFile = LCARS.System.Path(DirPath) / FileName
                if TargetFile.exists() and TargetFile.is_file():
                    TargetFile.unlink()
                    if not TargetFile.exists():
                        DeletedCount += 1

    return DeletedCount

# Повний цикл очищення кешу
def PurgeAllCaches():
    PurgedRecords = []

    for CacheDirItem in FindCacheDirs(ProjectRoot):
        PurgeResult = PurgeCacheDir(CacheDirItem)
        if PurgeResult is not None:
            PurgedRecords.append(PurgeResult)

    OrphanPycCount = PurgeOrphanPyc(ProjectRoot)
    if OrphanPycCount > 0:
        PurgedRecords.append(f"{OrphanPycCount} orphan .pyc files")

    return PurgedRecords

# ── 2. АУДИТ АРХІТЕКТУРНИХ ПРАВИЛ ──────────────────────────────

AllowedDirectQtFiles = {
    LCARS.System.Path("lcars/base/register.py"),
    LCARS.System.Path("lcars/base/dynamic.py"),
}

# Шаблон пошуку заборонених прямих імпортів через LCARS.System.Regex
QtImportPattern = LCARS.System.Regex.compile(
    r"^\s*(from|import)\s+(PyQt6|PyQt5|PySide6|PySide2|PyQt6\.QtCore|PyQt6\.QtGui|PyQt6\.QtWidgets)\b",
    LCARS.System.Regex.MULTILINE
)

# Перевірка окремого файлу
def CheckFileRules(SourceFile):
    ViolationsList = []

    if not SourceFile.exists() or not SourceFile.is_file():
        return ViolationsList

    RelativeFilePath = SourceFile.relative_to(ProjectRoot) if SourceFile.is_relative_to(ProjectRoot) else SourceFile

    if RelativeFilePath in AllowedDirectQtFiles:
        return ViolationsList

    FileContent = SourceFile.read_text(encoding="utf-8", errors="ignore")

    if QtImportPattern.search(FileContent):
        ViolationsList.append(f"RULE VIOLATION: Direct Qt import in {RelativeFilePath}. Use LCARS framework abstraction.")

    return ViolationsList

# ── 3. КЕРУВАННЯ СИСТЕМНИМ ПРОЦЕСОМ ────────────────────────────

# Фіксація ідентифікатора процесу
def WritePid():
    PidDirectory = ProjectRoot / ".lcars"
    if not PidDirectory.exists():
        PidDirectory.mkdir(parents=True, exist_ok=True)
    PidFilePath = PidDirectory / "sentinel.pid"
    PidFilePath.write_text(str(LCARS.System.PID()), encoding="utf-8")

# Видалення ідентифікатора процесу
def RemovePid():
    PidFilePath = ProjectRoot / ".lcars" / "sentinel.pid"
    if PidFilePath.exists():
        PidFilePath.unlink()

# Головний фоновий цикл Сентінела
def RunSentinel(PollInterval=0.5):
    WritePid()
    Logger.info("==========================================================")
    Logger.info("[SENTINEL] LCARS GUARDIAN DAEMON ACTIVE")
    Logger.info(f"[SENTINEL] WATCH TARGET: {ProjectRoot}")
    Logger.info(f"[SENTINEL] SCAN INTERVAL: {PollInterval}s")
    Logger.info(f"[SENTINEL] LOG FILE: {LogFile}")
    Logger.info("==========================================================")

    InitialPurgeReport = PurgeAllCaches()
    if InitialPurgeReport:
        for PurgedEntry in InitialPurgeReport:
            Logger.info(f"[PURGE] INITIAL CLEAN: {PurgedEntry}")

    CycleCounter = 0
    IsRunning = True

    while IsRunning:
        CurrentPurges = PurgeAllCaches()
        if CurrentPurges:
            for PurgedItem in CurrentPurges:
                Logger.info(f"[PURGE] AUTO-PURGED CACHE: {PurgedItem}")

        CycleCounter += 1
        if CycleCounter >= 10:
            CycleCounter = 0
            for PythonSourceFile in ProjectRoot.rglob("*.py"):
                if any(IgnoredPart in PythonSourceFile.parts for IgnoredPart in IgnoredDirectories):
                    continue
                RuleViolations = CheckFileRules(PythonSourceFile)
                for ViolationItem in RuleViolations:
                    Logger.warning(f"[RULE ALERT] {ViolationItem}")

        LCARS.System.Time.sleep(PollInterval)

    RemovePid()

if __name__ == "__main__":
    RunSentinel(0.5)
