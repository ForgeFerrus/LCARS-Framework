# LCARS FRAMEWORK REGISTER — CENTRAL REGISTRY
# ПРИНЦИП: Єдина точка доступу до всіх системних об'єктів
from typing import Any
registry: dict[str, Any] = {
# ════════════════════════════════════════════════════════════════════════════
# 1. ГОЛОВНЕ КОМП'ЮТЕРНЕ ЯДРО ЗОРЕЛЬОТА // MAIN COMPUTER CORE (System.*)
# ОПИС: Низькорівневе обчислювальне ядро LCARS, керування процесами,
#       оптичною пам'яттю, хронометром Федерації, шиною ODN та безпекою.
# ════════════════════════════════════════════════════════════════════════════
    "System.Operating"                : ("os", None),
    "System.IO"                       : ("io", None),
    "System.Regex"                    : ("re", None),
    "System.Re"                       : ("re", None),
    "System.Math"                     : ("math", None),
    "System.Winsound"                 : ("winsound", None),
    "System.Native"                   : ("ctypes", None),
    "System.Native.Struct"            : ("ctypes", "Structure"),
    "System.Shutil"                   : ("shutil", None), # shutil    
    "System.Core"                     : ("sys", None),
    "System.String"                   : ("string", None),
    "System.Type"                     : ("typing", None),
# ────────────────────────────────────────────────────────────────────────────
# 1.1 МАТРИЦЯ СИСТЕМНИХ РЕГІСТРІВ // SYSTEM REGISTERS (System.Environment.*)
# Глобальні змінні стану зорельота, бойові режими (Condition Green/Yellow/Red)
# ────────────────────────────────────────────────────────────────────────────
    "System.Environment"              : ("os", "environ"),
    "System.Environment.Get"          : ("os.environ", "get"),
    "System.Environment.Set"          : ("os.environ", "__setitem__"),
    "System.Environment.Remove"       : ("os.environ", "pop"),
    "System.Environment.Keys"         : ("os.environ", "keys"),
    "System.Environment.Values"       : ("os.environ", "values"),
    "System.Environment.Items"        : ("os.environ", "items"),
    "System.Environment.Exists"       : ("os.environ", "__contains__"),
    "System.Environment.Count"        : ("os.environ", "__len__"),
    "System.Environment.Clear"        : ("os.environ", "clear"),
    "System.Environment.Copy"         : ("os.environ", "copy"),
# ────────────────────────────────────────────────────────────────────────────
# 1.2 ІЗОЛІНІЙНА ДИСКОВА МАТРИЦЯ // ISOLINEAR DISK MATRIX (System.Directory.*)
# Каталоги та фізичні сховища чіпів, дискові маніпуляції та переміщення
# ────────────────────────────────────────────────────────────────────────────
    "System.Directory"                : ("os", "path"),
    "System.Directory.Current"        : ("os", "getcwd"),
    "System.Directory.Change"         : ("os", "chdir"),
    "System.Directory.List"           : ("os", "listdir"),
    "System.Directory.Scan"           : ("os", "scandir"),
    "System.Directory.Make"           : ("os", "makedirs"),
    "System.Directory.Remove"         : ("os", "removedirs"),
    
    "System.Remove"                   : ("os", "remove"),
    "System.Rename"                   : ("os", "rename"),
    "System.Replace"                  : ("os", "replace"),
    "System.Walk"                     : ("os", "walk"),
    "System.PID"                      : ("os", "getpid"),
    "System.Execute"                  : ("os", "system"),
# ────────────────────────────────────────────────────────────────────────────
# 1.3 ДІАГНОСТИКА ФІЗИЧНОГО КОРПУСУ // HARDWARE PLATFORM (System.Platform.*)
# Архітектура зорельота, обчислювальні вузли, параметри комп'ютерного ядра
# ────────────────────────────────────────────────────────────────────────────
    "System.Platform" : ("platform", None),

    "System.Platform.System" : ("platform", "system"),
    "System.Platform.Node" : ("platform", "node"),
    "System.Platform.Release" : ("platform", "release"),
    "System.Platform.Version" : ("platform", "version"),

    "System.Platform.Machine" : ("platform", "machine"),
    "System.Platform.Processor" : ("platform", "processor"),
    "System.Platform.Architecture" : ("platform", "architecture"),

    "System.Platform.Python" : ("platform", "python_version"),
    "System.Platform.Compiler" : ("platform", "python_compiler"),
    "System.Platform.Build" : ("platform", "python_build"),

# ────────────────────────────────────────────────────────────────────────────
# 1.4 СИСТЕМНІ ШИНИ КОМП'ЮТЕРНОГО ЯДРА // KERNEL BUSSES (System.Core.*)
# Вхідні/вихідні термінальні канали, аргументи запуску, системні переривання
# ────────────────────────────────────────────────────────────────────────────
    "System.Core.Modules" : ("sys", "modules"),
    "System.Core.MetaPath" : ("sys", "meta_path"),
    "System.Core.PathHooks" : ("sys", "path_hooks"),
    "System.Core.PathCache" : ("sys", "path_importer_cache"),
    "System.Core.Version" : ("sys", "version"),
    "System.Core.Version.Info" : ("sys", "version_info"),
    "System.Core.StdIn" : ("sys", "stdin"),
    "System.Core.StdOut" : ("sys", "stdout"),
    "System.Core.StdErr" : ("sys", "stderr"),
    "System.Core.Arguments" : ("sys", "argv"),
    "System.Core.Exit" : ("sys", "exit"),
    "System.Core.Path" : ("sys", "path"),

    # Configuration
    "System.Core.Flags" : ("sys", "flags"),
    "System.Core.Implementation" : ("sys", "implementation"),
    "System.Core.Executable" : ("sys", "executable"),
    "System.Core.Prefix" : ("sys", "prefix"),
    "System.Core.Prefix.Base" : ("sys", "base_prefix"),
    "System.Core.Prefix.Exec" : ("sys", "exec_prefix"),
    "System.Core.BaseExecPrefix" : ("sys", "base_exec_prefix"),
    "System.Core.WarnOptions" : ("sys", "warnoptions"),
    "System.Core.Platform" : ("sys", "platform"),

    # Hooks
    "System.Core.Hook.Display" : ("sys", "displayhook"),
    "System.Core.Hook.Exception" : ("sys", "excepthook"),
    "System.Core.Hook.BreakPoint" : ("sys", "breakpointhook"),
    "System.Core.Hook.Audit" : ("sys", "addaudithook"),

# ────────────────────────────────────────────────────────────────────────────
# 1.5 ОПТИЧНІ ШЛЯХИ ТА СЕКТОРИ ПАМ'ЯТІ // OPTICAL PATHWAYS (System.Path.*)
# Об'єктно-орієнтоване зчитування, запис та адресація в ізолінійних блоках
# ────────────────────────────────────────────────────────────────────────────
    "System.Path"                    : ("pathlib", "Path"),
    "System.Path.Current"            : ("pathlib.Path", "cwd"),
    "System.Path.Home"               : ("pathlib.Path", "home"),
    "System.Path.Absolute"           : ("pathlib.Path", "absolute"),
    "System.Path.Resolve"            : ("pathlib.Path", "resolve"),
    "System.Path.Exists"             : ("pathlib.Path", "exists"),
    "System.Path.File"               : ("pathlib.Path", "is_file"),
    "System.Path.Directory"          : ("pathlib.Path", "is_dir"),
    "System.Path.Directory.Create"   : ("pathlib.Path", "mkdir"),
    "System.Path.Directory.Delete"   : ("pathlib.Path", "rmdir"),
    "System.Path.Link"               : ("pathlib.Path", "is_symlink"),
    "System.Path.Touch"              : ("pathlib.Path", "touch"),
    "System.Path.Delete"             : ("pathlib.Path", "unlink"),
    "System.Path.Rename"             : ("pathlib.Path", "rename"),
    "System.Path.Replace"            : ("pathlib.Path", "replace"),
    "System.Path.Iterate"            : ("pathlib.Path", "iterdir"),
    "System.Path.Search"             : ("pathlib.Path", "glob"),
    "System.Path.Search.Recursive"   : ("pathlib.Path", "rglob"),
    "System.Path.ReadText"           : ("pathlib.Path", "read_text"),
    "System.Path.WriteText"          : ("pathlib.Path", "write_text"),
    "System.Path.ReadBytes"          : ("pathlib.Path", "read_bytes"),
    "System.Path.WriteBytes"         : ("pathlib.Path", "write_bytes"),
# ────────────────────────────────────────────────────────────────────────────
# 1.6 АВТОНОМНІ ВИКОНАВЧІ ПІДПРОГРАМИ // EXECUTIVE SUBROUTINES (System.Process.*)
# Ізольовані підпроцеси бортових систем корабля, виклик зовнішніх команд
# ────────────────────────────────────────────────────────────────────────────
    "System.Subprocess"              : ("subprocess", None),
    "System.Process"                 : ("subprocess", "Popen"),
    "System.Process.Run"             : ("subprocess", "run"),
    "System.Process.Call"            : ("subprocess", "call"),
    "System.Process.CheckCall"       : ("subprocess", "check_call"),
    "System.Process.CheckOutput"     : ("subprocess", "check_output"),

    "System.Process.PIPE"            : ("subprocess", "PIPE"),
    "System.Process.DEVNULL"         : ("subprocess", "DEVNULL"),
    "System.Process.STDOUT"          : ("subprocess", "STDOUT"),

    "System.Process.TimeoutExpired"  : ("subprocess", "TimeoutExpired"),
    "System.Process.CalledError"     : ("subprocess", "CalledProcessError"),
# ────────────────────────────────────────────────────────────────────────────
# 1.7 ПАРАЛЕЛЬНІ ОПТИЧНІ ПОТОКИ // CONCURRENCY STREAMS (System.Thread.*)
# Багатопоточна робота підсистем зорельота, матриця синхронізації та черги
# ────────────────────────────────────────────────────────────────────────────
    "System.Thread"                  : ("threading", "Thread"),
    "System.Thread.Main"             : ("threading", "main_thread"),
    "System.Thread.Current"          : ("threading", "current_thread"),

    # Internationalization
    "System.Python.Gettext": ("gettext", None),
    # Synchronization
    "System.Thread.Lock"             : ("threading", "Lock"),
    "System.Thread.RLock"            : ("threading", "RLock"),
    "System.Thread.Event"            : ("threading", "Event"),
    "System.Thread.Condition"        : ("threading", "Condition"),
    "System.Thread.Semaphore"        : ("threading", "Semaphore"),
    "System.Thread.Barrier"          : ("threading", "Barrier"),
    # Timer Local storage
    "System.Thread.Timer"            : ("threading", "Timer"),
    "System.Thread.Local"            : ("threading", "local"),
# ────────────────────────────────────────────────────────────────────────────
# 1.8 АСИНХРОННИЙ ДИСПЕТЧЕР ПОДІЙ // ASYNC EVENT CONDUIT (System.Task.*)
# Цикл обробки подій містка, паралельні черги наказів, таймаути підпрограм
# ────────────────────────────────────────────────────────────────────────────
    "System.Task"                     : ("asyncio", None),
    # Event Loop
    "System.Task.Loop"                : ("asyncio", "get_event_loop"),
    "System.Task.RunningLoop"         : ("asyncio", "get_running_loop"),
    "System.Task.NewLoop"             : ("asyncio", "new_event_loop"),
    "System.Task.SetLoop"             : ("asyncio", "set_event_loop"),
    "System.Task.Create"              : ("asyncio", "create_task"),
    "System.Task.Current"             : ("asyncio", "current_task"),
    "System.Task.All"                 : ("asyncio", "all_tasks"),

    # Execution
    "System.Task.Run"                 : ("asyncio", "run"),
    "System.Task.Wait"                : ("asyncio", "wait"),
    "System.Task.Gather"              : ("asyncio", "gather"),
    "System.Task.AsCompleted"         : ("asyncio", "as_completed"),
    "System.Task.Shield"              : ("asyncio", "shield"),

    # Timing
    "System.Task.Sleep"               : ("asyncio", "sleep"),
    "System.Task.Timeout"             : ("asyncio", "timeout"),
    "System.Task.TimeoutAt"           : ("asyncio", "timeout_at"),

    # Synchronization
    "System.Task.Lock"                : ("asyncio", "Lock"),
    "System.Task.Event"               : ("asyncio", "Event"),
    "System.Task.Condition"           : ("asyncio", "Condition"),
    "System.Task.Semaphore"           : ("asyncio", "Semaphore"),
    "System.Task.Queue"               : ("asyncio", "Queue"),

    # Streams
    "System.Task.StreamReader"        : ("asyncio", "StreamReader"),
    "System.Task.StreamWriter"        : ("asyncio", "StreamWriter"),

    # Errors
    "System.Task.Cancelled"           : ("asyncio", "CancelledError"),
    "System.Task.TimeoutError"        : ("asyncio", "TimeoutError"),
    "System.Task.InvalidState"        : ("asyncio", "InvalidStateError"),
# ────────────────────────────────────────────────────────────────────────────
# 1.9 БІОНЕЙРОННИЙ БУФЕР ПАМ'ЯТІ // BIO-NEURAL MEMORY BUFFER (System.Memory.*)
# Збирач залишкових зарядів пам'яті, контроль оптичних посилань та об'єктів
# ────────────────────────────────────────────────────────────────────────────
    "System.Memory"                   : ("gc", None),

    # Garbage Collector
    "System.Memory.Enable"            : ("gc", "enable"),
    "System.Memory.Disable"           : ("gc", "disable"),
    "System.Memory.Enabled"           : ("gc", "isenabled"),

    "System.Memory.Collect"           : ("gc", "collect"),

    # Objects
    "System.Memory.Objects"           : ("gc", "get_objects"),
    "System.Memory.Referents"         : ("gc", "get_referents"),

    # Statistics
    "System.Memory.Count"             : ("gc", "get_count"),
    "System.Memory.Stats"             : ("gc", "get_stats"),
    "System.Memory.Threshold"         : ("gc", "get_threshold"),
    "System.Memory.SetThreshold"      : ("gc", "set_threshold"),

    # Debug
    "System.Memory.Debug"             : ("gc", "set_debug"),
    "System.DataClass"                : ("dataclasses", "dataclass"),
    "System.DataClass.Field"          : ("dataclasses", "field"),
    "System.DataClass.Module"         : ("dataclasses", None),
# ────────────────────────────────────────────────────────────────────────────
# 1.10 ДИНАМІЧНИЙ ЗАВАНТАЖУВАЧ МОДУЛІВ // SUBSYSTEM LOADER (System.Module.*)
# Гаряче підключення нових сервісів та модулів палуб без зупинки ядра
# ────────────────────────────────────────────────────────────────────────────
    "System.Module"                   : ("importlib", None),

    # Import
    "System.Module.Import"            : ("importlib", "import_module"),
    "System.Module.Reload"            : ("importlib", "reload"),

    # Specification
    "System.Module.Specification"     : ("importlib.util", "find_spec"),
    "System.Module.SpecFromFile"      : ("importlib.util", "spec_from_file_location"),
    "System.Module.FromSpec"          : ("importlib.util", "module_from_spec"),

    # Loader
    "System.Module.Loader"            : ("importlib.util", "LazyLoader"),

    # Cache
    "System.Module.InvalidateCache"   : ("importlib", "invalidate_caches"),

    # Resources
    "System.Module.Resources"         : ("importlib.resources", "files"),

    # Metadata
    "System.Module.Metadata"          : ("importlib.metadata", "metadata"),
    "System.Module.Version"           : ("importlib.metadata", "version"),

    # Utilities
    "System.Module.Util"              : ("importlib.util", None),

    # Dependency
    "System.Dependency"                 : ("importlib.metadata", None),
    "System.Dependency.Requires"        : ("importlib.metadata", "requires"),
    "System.Dependency.Distributions"   : ("importlib.metadata", "distributions"),
    # RESOURCE
    "System.Resource"                : ("importlib.resources", None),
    # Files
    "System.Resource.Files"          : ("importlib.resources", "files"),
    # ============================================================================
    # ABSTRACT
    # ============================================================================
    "System.Abstract"                : ("abc", None),
    "System.Abstract.Meta"           : ("abc", "ABCMeta"),
    "System.Abstract.Class"          : ("abc", "ABC"),
    "System.Abstract.Method"         : ("abc", "abstractmethod"),
    # ============================================================================
    # CONTEXT
    # ============================================================================
    "System.Context"                 : ("contextlib", None),

    "System.Context.Manager"         : ("contextlib", "contextmanager"),
    "System.Context.AsyncManager"    : ("contextlib", "asynccontextmanager"),

    "System.Context.ExitStack"       : ("contextlib", "ExitStack"),
    "System.Context.AsyncExitStack"  : ("contextlib", "AsyncExitStack"),

    "System.Context.Suppress"        : ("contextlib", "suppress"),

    "System.Context.RedirectStdout"  : ("contextlib", "redirect_stdout"),
    "System.Context.RedirectStderr"  : ("contextlib", "redirect_stderr"),

    "System.Context.Null"            : ("contextlib", "nullcontext"),

# ────────────────────────────────────────────────────────────────────────────
# 1.11 МАТРИЧНІ БУФЕРИ ДАНИХ // MATRIX RING BUFFERS (System.Collection.*)
# Кільцеві буфери чорної скриньки, лічильники подій сенсорів, іменовані кортежі
# ────────────────────────────────────────────────────────────────────────────
    "System.Collection"             : ("collections", None),

    "System.Collection.Deque"       : ("collections", "deque"),
    "System.Collection.Counter"     : ("collections", "Counter"),
    "System.Collection.DefaultDict" : ("collections", "defaultdict"),
    "System.Collection.OrderedDict" : ("collections", "OrderedDict"),
    "System.Collection.ChainMap"    : ("collections", "ChainMap"),

    "System.Collection.NamedTuple"  : ("collections", "namedtuple"),

# ────────────────────────────────────────────────────────────────────────────
# 1.12 КВАНТОВІ ПОСЛІДОВНОСТІ // QUANTUM SEQUENCE ENGINE (System.Iterator.*)
# Циклічне сканування фаз, перебір комбінацій частот дефлектора та щитів
# ────────────────────────────────────────────────────────────────────────────
    "System.Iterator"               : ("itertools", None),

    "System.Iterator.Count"         : ("itertools", "count"),
    "System.Iterator.Cycle"         : ("itertools", "cycle"),
    "System.Iterator.Repeat"        : ("itertools", "repeat"),

    "System.Iterator.Chain"         : ("itertools", "chain"),
    "System.Iterator.ZipLongest"    : ("itertools", "zip_longest"),

    "System.Iterator.Product"       : ("itertools", "product"),
    "System.Iterator.Permutation"   : ("itertools", "permutations"),
    "System.Iterator.Combination"   : ("itertools", "combinations"),
# ────────────────────────────────────────────────────────────────────────────
# 1.13 ЛОГІЧНІ ЗАМИКАННЯ ТА КЕШ // LOGIC CLOSURES & CACHE (System.Function.*)
# Кешування обчислень траєкторій, шаблони підпрограм швидкого реагування
# ────────────────────────────────────────────────────────────────────────────
    "System.Function"               : ("functools", None),
    "System.Function.Partial"       : ("functools", "partial"),
    "System.Function.Wraps"         : ("functools", "wraps"),
    "System.Function.Cache"         : ("functools", "cache"),
    "System.Function.LRUCache"      : ("functools", "lru_cache"),
    "System.Function.CachedProperty": ("functools", "cached_property"),
    "System.Function.Reduce"        : ("functools", "reduce"),

    # === SYSTEM BUILTIN & PROTOCOL DUNDERS ===
    "System.Method.Static"          : ("builtins", "staticmethod"),
    "System.Method.Class"           : ("builtins", "classmethod"),
    "System.Method.Property"        : ("builtins", "property"),

    "System.Protocol.Import"        : ("builtins", "__import__"),
    "System.Protocol.Init"           : ("builtins", "__init__"),
    "System.Protocol.All"            : ("builtins", "__all__"),
    "System.Protocol.Dictionary"     : ("builtins", "__dict__"),
    "System.Protocol.Directory"      : ("builtins", "__dir__"),
    "System.Protocol.Name"             : ("builtins", "__name__"),
    "System.Protocol.Doc"              : ("builtins", "__doc__"),
    "System.Protocol.File"             : ("builtins", "__file__"),
    "System.Protocol.Module"           : ("builtins", "__module__"),
    "System.Protocol.Class"            : ("builtins", "__class__"),
    "System.Protocol.Bases"            : ("builtins", "__bases__"),
    "System.Protocol.Slots"            : ("builtins", "__slots__"),
    "System.Protocol.Annotations"      : ("builtins", "__annotations__"),

    # === SYSTEM EXECUTION DUNDERS ===
    "System.Protocol.Call"           : ("builtins", "__call__"),
    "System.Protocol.Enter"          : ("builtins", "__enter__"),
    "System.Protocol.Exit"           : ("builtins", "__exit__"),
    "System.Protocol.GetAttr"        : ("builtins", "__getattr__"),
    "System.Protocol.SetAttr"        : ("builtins", "__setattr__"),
    "System.Protocol.DelAttr"        : ("builtins", "__delattr__"),
    # ============================================================================
    # SYSTEM OPERATOR DUNDERS
    "System.Operator"               : ("operator", None),
    "System.Operator.Equal"           : ("operator", "eq"),
    "System.Operator.NotEqual"        : ("operator", "ne"),
    "System.Operator.LessThan"        : ("operator", "lt"),
    "System.Operator.GreaterThan"     : ("operator", "gt"),
    "System.Operator.LessOrEqual"     : ("operator", "le"),
    "System.Operator.GreaterOrEqual"  : ("operator", "ge"),
    "System.Operator.Contains"        : ("operator", "contains"),
    "System.Operator.GetItem"         : ("operator", "getitem"),
    "System.Operator.SetItem"         : ("operator", "setitem"),
    "System.Operator.DelItem"         : ("operator", "delitem"),
    "System.Operator.Attribute"     : ("operator", "attrgetter"),
    "System.Operator.Item"          : ("operator", "itemgetter"),
    "System.Operator.Method"        : ("operator", "methodcaller"),

    # ============================================================================
    # TRACEBACK
    # ============================================================================
    "System.Traceback"              : ("traceback", None),

    "System.Traceback.Print"        : ("traceback", "print_exc"),
    "System.Traceback.Format"       : ("traceback", "format_exc"),
    "System.Traceback.Stack"        : ("traceback", "format_stack"),

    "System.Traceback.Exception"    : ("traceback", "TracebackException"),

    # ============================================================================
    # WEAK REFERENCES
    # ============================================================================
    "System.WeakReference"          : ("weakref", None),

    "System.WeakReference.Reference": ("weakref", "ref"),
    "System.WeakReference.Proxy"    : ("weakref", "proxy"),
    "System.WeakReference.Dictionary":("weakref", "WeakValueDictionary"),

    # ============================================================================
    # COPY
    # ============================================================================
    "System.Copy"                  : ("copy", None),
    "System.Copy.Deep"             : ("copy", "deepcopy"),
    "System.Copy.Shallow"           : ("copy", "copy"),

    # ============================================================================
    # TEMPORARY
    # ============================================================================
    "System.Temporary"              : ("tempfile", None),

    "System.Temporary.File"         : ("tempfile", "TemporaryFile"),
    "System.Temporary.NamedFile"    : ("tempfile", "NamedTemporaryFile"),

    "System.Temporary.Directory"    : ("tempfile", "TemporaryDirectory"),

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================
    "System.File"                   : ("shutil", None),

    "System.File.Copy"              : ("shutil", "copy"),
    "System.File.CopyTree"          : ("shutil", "copytree"),

    "System.File.Move"              : ("shutil", "move"),

    "System.File.RemoveTree"        : ("shutil", "rmtree"),

    "System.File.DiskUsage"         : ("shutil", "disk_usage"),

    "System.File.Which"             : ("shutil", "which"),

    # ────────────────────────────────────────────────────────────────────────────
    # 1.13.1 МЕРЕЖЕВІ URL ТА АДРЕСАЦІЯ // SUPSPACE ADDRESSING (Bridge.Network.URL)
    # Зворотна сумісність: канонічний шлях у Bridge.Network.URL
    # ────────────────────────────────────────────────────────────────────────────
    "System.URL"                          : ("urllib.parse", None),
    "System.URL.Parse"                    : ("urllib.parse", "urlparse"),
    "System.URL.Split"                    : ("urllib.parse", "urlsplit"),
    "System.URL.Encode"                   : ("urllib.parse", "urlencode"),
    "System.URL.Decode"                   : ("urllib.parse", "unquote"),
    "System.URL.Join"                     : ("urllib.parse", "urljoin"),
    "System.URL.Quote"                    : ("urllib.parse", "quote"),
# ────────────────────────────────────────────────────────────────────────────
# 1.14 АПАРАТНА ТЕЛЕМЕТРІЯ ЗОРЕЛЬОТА // HARDWARE TELEMETRY (System.Hardware.*)
# Низькорівневий стан заліза: процесор, пам'ять, накопичувачі, сенсори, енергія
# ────────────────────────────────────────────────────────────────────────────
    "System.Hardware"                 : ("psutil", None),
    "System.Hardware.CPU"             : ("psutil", "cpu_percent"),
    "System.Hardware.CPUCount"        : ("psutil", "cpu_count"),
    "System.Hardware.CPUFreq"         : ("psutil", "cpu_freq"),
    "System.Hardware.CPUTimes"        : ("psutil", "cpu_times_percent"),
    "System.Hardware.Memory"          : ("psutil", "virtual_memory"),
    "System.Hardware.Swap"            : ("psutil", "swap_memory"),
    "System.Hardware.Disk"            : ("psutil", "disk_usage"),
    "System.Hardware.DiskPartitions"  : ("psutil", "disk_partitions"),
    "System.Hardware.DiskIO"          : ("psutil", "disk_io_counters"),
    "System.Hardware.NetworkIO"       : ("psutil", "net_io_counters"),
    "System.Hardware.NetworkStats"    : ("psutil", "net_if_stats"),
    "System.Hardware.NetworkAddress"  : ("psutil", "net_if_addrs"),
    "System.Hardware.Battery"         : ("psutil", "sensors_battery"),
    "System.Hardware.Sensors"         : ("psutil", "sensors_temperatures"),
    "System.Hardware.Fans"            : ("psutil", "sensors_fans"),
    "System.Hardware.Processes"       : ("psutil", "process_iter"),
    "System.Hardware.Process"         : ("psutil", "Process"),
    "System.Hardware.Users"           : ("psutil", "users"),
    "System.Hardware.BootTime"        : ("psutil", "boot_time"),
# ────────────────────────────────────────────────────────────────────────────
# 1.15 ГОЛОСОВИЙ СИНТЕЗАТОР КОМП'ЮТЕРА // VOICE INTERFACE (System.Voice.*)
# Локальний синтез мови LCARS (Majel Barrett) без інтернету на будь-якій ОС
# ────────────────────────────────────────────────────────────────────────────
    "System.Voice"                    : ("pyttsx3", None),
    "System.Voice.Engine"             : ("pyttsx3", "init"),
# ────────────────────────────────────────────────────────────────────────────
# 1.16 МІЖПРОЦЕСНА ШИНА // INTER-PROCESS CONDUIT (System.IPC.*)
# Спільна оперативна пам'ять, міжпроцесні черги, низькорівневі сокети
# ────────────────────────────────────────────────────────────────────────────
    "System.IPC"                      : ("multiprocessing", None),
    "System.IPC.Process"              : ("multiprocessing", "Process"),
    "System.IPC.Queue"                : ("multiprocessing", "Queue"),
    "System.IPC.Pipe"                 : ("multiprocessing", "Pipe"),
    "System.IPC.Value"                : ("multiprocessing", "Value"),
    "System.IPC.Array"                : ("multiprocessing", "Array"),
    "System.IPC.Manager"              : ("multiprocessing", "Manager"),
    "System.IPC.SharedMemory"         : ("mmap", "mmap"),
    "System.IPC.Socket"               : ("socket", "socket"),
    "System.IPC.AF_INET"              : ("socket", "AF_INET"),
    "System.IPC.SOCK_STREAM"          : ("socket", "SOCK_STREAM"),
    "System.IPC.SOCK_DGRAM"           : ("socket", "SOCK_DGRAM"),
# ────────────────────────────────────────────────────────────────────────────
# 1.14 ХРОНОМЕТР ФЕДЕРАЦІЇ ТА ЗОРЯНИЙ ЧАС // STARFLEET CHRONOMETER (System.Time.*)
# Наносекундні такти варп-ядра, календарний час та розрахунок Stardate
# ────────────────────────────────────────────────────────────────────────────
    "System.Time"                     : ("time", None),

    # Clock
    "System.Time.Now"                 : ("time", "time"),
    "System.Time.Nanoseconds"         : ("time", "time_ns"),
    "System.Time.Monotonic"           : ("time", "monotonic"),
    "System.Time.Performance"         : ("time", "perf_counter"),
    "System.Time.Process"             : ("time", "process_time"),
    "System.Time.Thread"              : ("time", "thread_time"),

    # Sleep
    "System.Time.Sleep"               : ("time", "sleep"),

    # Local / UTC
    "System.Time.Local"               : ("time", "localtime"),
    "System.Time.UTC"                 : ("time", "gmtime"),
    "System.Time.Make"                : ("time", "mktime"),

    # Format
    "System.Time.Format"              : ("time", "strftime"),
    "System.Time.Parse"               : ("time", "strptime"),

    # Calendar & Chronometry
    "System.DateTime"                 : ("datetime", "datetime"),
    "System.Date"                     : ("datetime", "date"),
    "System.TimeDelta"                : ("datetime", "timedelta"),
    "System.Calendar"                 : ("calendar", None),
    "System.Time.DateTime"            : ("datetime", "datetime"),
    "System.Time.Date"                : ("datetime", "date"),
    "System.Time.Time"                : ("datetime", "time"),
    "System.Time.Delta"               : ("datetime", "timedelta"),
    "System.Time.TimeZone"            : ("datetime", "timezone"),

    # Constructors
    "System.Time.Today"               : ("datetime.date", "today"),
    "System.Time.NowLocal"            : ("datetime.datetime", "now"),
    "System.Time.NowUTC"              : ("datetime.datetime", "utcnow"),

    # ISO
    "System.Time.FromISO"             : ("datetime.datetime", "fromisoformat"),
    "System.Time.ToISO"               : ("datetime.datetime", "isoformat"),

    # Timestamp
    "System.Time.FromTimestamp"       : ("datetime.datetime", "fromtimestamp"),
    "System.Time.Timestamp"           : ("datetime.datetime", "timestamp"),

    # ────────────────────────────────────────────────────────────────────────────
# 1.15 ПРОТОКОЛИ БЕЗПЕКИ ЗОРЯНОГО ФЛОТУ // STARFLEET SECURITY (System.Security.*)
# Криптографічні коди доступу, підпросторові сертифікати, перевірка повноважень
# ────────────────────────────────────────────────────────────────────────────

    "System.Security"                 : ("ssl", None),

    # SSL
    "System.Security.Context"         : ("ssl", "SSLContext"),
    "System.Security.DefaultContext"  : ("ssl", "create_default_context"),
    "System.Security.Certificate"     : ("ssl", "get_server_certificate"),

    # Hash
    "System.Security.Hash"            : ("hashlib", "new"),
    "System.Security.MD5"             : ("hashlib", "md5"),
    "System.Security.SHA1"            : ("hashlib", "sha1"),
    "System.Security.SHA256"          : ("hashlib", "sha256"),
    "System.Security.SHA512"          : ("hashlib", "sha512"),

    # HMAC
    "System.Security.HMAC"            : ("hmac", "new"),
    "System.Security.HMAC.Module"     : ("hmac", None),

    # Random
    "System.Security.Random"          : ("secrets", "token_bytes"),
    "System.Security.Token"           : ("secrets", "token_hex"),
    "System.Security.URLToken"        : ("secrets", "token_urlsafe"),

    # Compare
    "System.Security.Compare"         : ("secrets", "compare_digest"),
    # ============================================================================
    # Cryptography(stdlib)
    # ============================================================================
    "System.Security.Hashlib":      ("hashlib", None),
    "System.Security.Secrets":      ("secrets", None),
    "System.Security.Base64":       ("base64", None),
    "System.Security.Binascii":     ("binascii", None),
    "System.Security.Codecs":       ("codecs", None),

# ────────────────────────────────────────────────────────────────────────────
# 1.16 ОПТИЧНА МЕРЕЖА ДАНИХ (ODN CONDUIT) // NETWORK TRANSPORT (System.Network.*)
# Магістралі передачі оптичних даних між палубами, сокети міжзоряного зв'язку
# ────────────────────────────────────────────────────────────────────────────

    "System.Network"                  : ("socket", None),
    "System.Socket"                   : ("socket", None),

    # Socket
    "System.Network.Socket"           : ("socket", "socket"),
    "System.Network.Create"           : ("socket", "create_connection"),
    "System.Network.Pair"             : ("socket", "socketpair"),

    # Address
    "System.Network.HostName"         : ("socket", "gethostname"),
    "System.Network.HostByName"       : ("socket", "gethostbyname"),
    "System.Network.HostByAddress"    : ("socket", "gethostbyaddr"),
    "System.Network.AddressInfo"      : ("socket", "getaddrinfo"),

    # Constants
    "System.Network.TCP"              : ("socket", "SOCK_STREAM"),
    "System.Network.UDP"              : ("socket", "SOCK_DGRAM"),
    "System.Network.IPv4"             : ("socket", "AF_INET"),
    "System.Network.IPv6"             : ("socket", "AF_INET6"),

    # SSL
    "System.Network.SMTP"             : ("smtplib", None),
    "System.Network.SMTP.Client"      : ("smtplib", "SMTP"),
    "System.Network.SMTP.SSL"         : ("smtplib", "SMTP_SSL"),
    "System.Network.SSL"              : ("ssl", None),

    # Async
    "System.Network.Async"            : ("asyncio", None),
    "System.Network.Async.Loop"       : ("asyncio", "get_event_loop"),
    "System.Network.Async.NewLoop"    : ("asyncio", "new_event_loop"),
    "System.Network.Async.Server"     : ("asyncio", "start_server"),
    "System.Network.Async.Run"        : ("asyncio", "run"),
    "System.Network.HTTPX"            : ("httpx", None),
    "System.Network.HTTPX.Client"     : ("httpx", "Client"),
    "System.Network.HTTPX.AsyncClient": ("httpx", "AsyncClient"),
    "System.Network.AioHTTP"          : ("aiohttp", None),
    "System.Network.AioHTTP.Client"   : ("aiohttp", "ClientSession"),
    # ============================================================================
    # Email(stdlib) 
    "System.Network.Email"            : ("email", None),
    "System.Network.Email.MIME"       : ("email.mime", None),
    "System.Network.Email.MIME.Text"  : ("email.mime.text", "MIMEText"),
# ────────────────────────────────────────────────────────────────────────────
# 1.17 БОРТОВИЙ ЖУРНАЛ КОРАБЛЯ // SHIP'S COMPUTER LOGBOOK (System.Log.*)
# Фіксація системних подій зорельота: діагностика, тривоги, звіти місій
# ────────────────────────────────────────────────────────────────────────────
    "System.Log"                    : ("logging", None),

    "System.Log.Debug"              : ("logging", "debug"),
    "System.Log.Info"               : ("logging", "info"),
    "System.Log.Warning"            : ("logging", "warning"),
    "System.Log.Error"              : ("logging", "error"),
    "System.Log.Critical"           : ("logging", "critical"),
    "System.Log.Exception"          : ("logging", "exception"),

    "System.Log.Configure"          : ("logging", "basicConfig"),

    "System.Log.Logger"             : ("logging", "getLogger"),

    "System.Log.File"               : ("logging", "FileHandler"),
    "System.Log.Stream"             : ("logging", "StreamHandler"),
    # ============================================================================
    # LOCALE
    "System.Locale"                  : ("locale", None),
    "System.Locale.Get"              : ("locale", "getlocale"),
    "System.Locale.Set"              : ("locale", "setlocale"),
    "System.Locale.Default"          : ("locale", "getdefaultlocale"),
    "System.Locale.Preferred"        : ("locale", "getpreferredencoding"),
    "System.Locale.Encoding"         : ("locale", "getencoding"),
    "System.Locale.Format"           : ("locale", "format_string"),
    "System.Locale.Currency"         : ("locale", "currency"),
    # ============================================================================
    # IDENTIFIER
    "System.Identifier"              : ("uuid", None),
    "System.Identifier.New"          : ("uuid", "uuid4"),
    "System.Uuid"                    : ("uuid", None),
    "System.UUID"                    : ("uuid", None),
    "System.Uuid.New"                : ("uuid", "uuid4"),
    "System.Uuid.UUID"               : ("uuid", "UUID"),

    "System.Identifier.UUID"         : ("uuid", "UUID"),
    "System.Identifier.UUID1"        : ("uuid", "uuid1"),
    "System.Identifier.UUID3"        : ("uuid", "uuid3"),
    "System.Identifier.UUID4"        : ("uuid", "uuid4"),
    "System.Identifier.UUID5"        : ("uuid", "uuid5"),
    # ============================================================================
    # REFLECTION
    "System.Reflection" : ("inspect", None),

    # Objects
    "System.Reflection.Module" : ("inspect", "getmodule"),
    "System.Reflection.Type" : ("inspect", "isclass"),
    "System.Reflection.Function" : ("inspect", "isfunction"),
    "System.Reflection.Method" : ("inspect", "ismethod"),
    "System.Reflection.Stack" : ("inspect", "stack"),
    "System.Reflection.CurrentFrame" : ("inspect", "currentframe"),
    # Members
    "System.Reflection.Members" : ("inspect", "getmembers"),

    # Signature
    "System.Reflection.Signature" : ("inspect", "signature"),
    "System.Reflection.Parameters" : ("inspect.Parameter", None),

    # Source
    "System.Reflection.Source"          : ("inspect", "getsource"),
    "System.Reflection.File"            : ("inspect", "getfile"),

    # Documentation
    "System.Reflection.Documentation"   : ("inspect", "getdoc"),
    # ============================================================================
    # ENUM
    # ============================================================================
    "System.Enum"               : ("enum", None),

    "System.Enum.Enum"          : ("enum", "Enum"),
    "System.Enum.IntEnum"       : ("enum", "IntEnum"),
    "System.Enum.Flag"          : ("enum", "Flag"),
    "System.Enum.IntFlag"       : ("enum", "IntFlag"),
    "System.Enum.Auto"          : ("enum", "auto"),
    # ────────────────────────────────────────────────────────────────────────────
# 1.18 КВАНТОВИЙ ГЕНЕРАТОР ЙМОВІРНОСТЕЙ // QUANTUM PROBABILITY (System.Random.*)
# Моделювання стохастичних процесів у плазмі варп-ядра та сенсорних шумах
# ────────────────────────────────────────────────────────────────────────────
    "System.Random"                  : ("random", None),
    "System.Random.Float"            : ("random", "random"),
    "System.Random.Integer"          : ("random", "randint"),
    "System.Random.Range"            : ("random", "randrange"),
    "System.Random.Choice"           : ("random", "choice"),
    # ════════════════════════════════════════════════════════════════════════════
# 2. КОНСОЛІ МІСТКА, ДИСПЛЕЇ ТА PADD // LCARS USER INTERFACE (Base.*)
# ОПИС: Графічний каркас 24-го століття, геометрія ліктів панелей (Elbow),
#       автентичні кольори, віконні протоколи безрамкового відображення PADD.
# ════════════════════════════════════════════════════════════════════════════
    "Base.Core":                    ("PyQt6.QtCore", None),
    "Base.Core.Object":             ("PyQt6.QtCore", "QObject"),
    "Base.Core.Signal":             ("PyQt6.QtCore", "pyqtSignal"),
    "Base.Core.Slot":               ("PyQt6.QtCore", "pyqtSlot"),
    "Base.Core.Property":           ("PyQt6.QtCore", "pyqtProperty"),
    "Base.Core.Application":        ("PyQt6.QtCore", "QCoreApplication"),
    "Base.Core.Event":              ("PyQt6.QtCore", "QEvent"),
    "Base.Core.Event.Loop":          ("PyQt6.QtCore", "QEventLoop"),
    "Base.Core.Event.Dispatcher":    ("PyQt6.QtCore", "QAbstractEventDispatcher"),

    # Meta
    "Base.Core.Meta.Object":         ("PyQt6.QtCore", "QMetaObject"),
    "Base.Core.Meta.Method":         ("PyQt6.QtCore", "QMetaMethod"),
    "Base.Core.Meta.Property":       ("PyQt6.QtCore", "QMetaProperty"),
    "Base.Core.Meta.Type":           ("PyQt6.QtCore", "QMetaType"),
    "Base.Core.Meta.Enum":           ("PyQt6.QtCore", "QMetaEnum"),
    # IO
    "Base.Core.IO.Device":              ("PyQt6.QtCore", "QIODevice"),
    "Base.Core.Info.Class":             ("PyQt6.QtCore", "QMetaClassInfo"),
    "Base.Core.Info.Library":           ("PyQt6.QtCore", "QLibraryInfo"),
    # ============================================================================
    # Command
    "Base.Core.Process":                ("PyQt6.QtCore", "QProcess"),
    "Base.Core.Process.Environment":    ("PyQt6.QtCore", "QProcessEnvironment"),
    "Base.Core.Resource":               ("PyQt6.QtCore", "QResource"),
    "Base.Core.Plugin.Loader":          ("PyQt6.QtCore", "QPluginLoader"),
    "Base.Core.Translator":             ("PyQt6.QtCore", "QTranslator"),
    "Base.Core.Command.Parser":         ("PyQt6.QtCore", "QCommandLineParser"),
    "Base.Core.Command.Option":         ("PyQt6.QtCore", "QCommandLineOption"),
    "Base.Core.Permission":             ("PyQt6.QtCore", "QPermission"),
    "Base.Core.Collator":               ("PyQt6.QtCore", "QCollator"),

    # Files
    "Base.Core.File": ("PyQt6.QtCore", "QFile"),
    "Base.Core.File.Info": ("PyQt6.QtCore", "QFileInfo"),
    "Base.Core.File.Device": ("PyQt6.QtCore", "QFileDevice"),
    "Base.Core.File.Storage": ("PyQt6.QtCore", "QStorageInfo"),
    "Base.Core.File.Paths": ("PyQt6.QtCore", "QStandardPaths"),
    "Base.Core.File.Watcher": ("PyQt6.QtCore", "QFileSystemWatcher"),
    "Base.Core.FileSystemWatcher": ("PyQt6.QtCore", "QFileSystemWatcher"),
    "Base.Core.FileWatcher": ("PyQt6.QtCore", "QFileSystemWatcher"),
    "Base.Core.File.Lock": ("PyQt6.QtCore", "QLockFile"),
    "Base.Core.File.Save": ("PyQt6.QtCore", "QSaveFile"),
    "Base.Core.File.Temporary": ("PyQt6.QtCore", "QTemporaryFile"),

    "Base.Core.Directory":              ("PyQt6.QtCore", "QDir"),
    "Base.Core.Directory.Iterator":     ("PyQt6.QtCore", "QDirIterator"),
    "Base.Core.Directory.Temporary":    ("PyQt6.QtCore", "QTemporaryDir"),

    "Base.Core.Library":                ("PyQt6.QtCore", "QLibrary"),
    "Base.Core.VersionNumber":          ("PyQt6.QtCore", "QVersionNumber"),
    "Base.Core.Type":               ("PyQt6.QtCore", "QTypeRevision"),

    "Base.Core.Json.Document":      ("PyQt6.QtCore", "QJsonDocument"),
    "Base.Core.Json.Object":        ("PyQt6.QtCore", "QJsonObject"),
    "Base.Core.Json.Array":         ("PyQt6.QtCore", "QJsonArray"),
    "Base.Core.Json.Value":         ("PyQt6.QtCore", "QJsonValue"),

    "Base.Core.Xml.Reader":         ("PyQt6.QtCore", "QXmlStreamReader"),
    "Base.Core.Xml.Writer":         ("PyQt6.QtCore", "QXmlStreamWriter"),
    "Base.Core.Xml.Attributes":     ("PyQt6.QtCore", "QXmlStreamAttributes"),

    # Threading
    "Base.Core.Thread":             ("PyQt6.QtCore", "QThread"),
    "Base.Core.Thread.Pool":        ("PyQt6.QtCore", "QThreadPool"),
    "Base.Core.Thread.Runnable":    ("PyQt6.QtCore", "QRunnable"),

    # Synchronization
    "Base.Core.Sync.Mutex":         ("PyQt6.QtCore", "QMutex"),
    "Base.Core.Sync.Semaphore":     ("PyQt6.QtCore", "QSemaphore"),
    "Base.Core.Sync.Wait":          ("PyQt6.QtCore", "QWaitCondition"),

    # Data
    "Base.Core.Data.ByteArray":     ("PyQt6.QtCore", "QByteArray"),
    "Base.Core.Data.BitArray":      ("PyQt6.QtCore", "QBitArray"),
    "Base.Core.Data.Buffer":        ("PyQt6.QtCore", "QBuffer"),
    "Base.Core.Data.Mime":          ("PyQt6.QtCore", "QMimeData"),
    "Base.Core.Data.Url":           ("PyQt6.QtCore", "QUrl"),
    "Base.Core.Data.Url.Query":     ("PyQt6.QtCore", "QUrlQuery"),
    "Base.Core.Data.Uuid":          ("PyQt6.QtCore", "QUuid"),

    # Streams
    "Base.Core.Stream.Binary":      ("PyQt6.QtCore", "QDataStream"),
    "Base.Core.Stream.Text":        ("PyQt6.QtCore", "QTextStream"),

    # Settings
    "Base.Core.Settings":           ("PyQt6.QtCore", "QSettings"),
    "Base.Core.Locale":             ("PyQt6.QtCore", "QLocale"),

    # Time
    "Base.Core.Time.Date":          ("PyQt6.QtCore", "QDate"),
    "Base.Core.Time.Clock":         ("PyQt6.QtCore", "QTime"),
    "Base.Core.Time.DateTime":      ("PyQt6.QtCore", "QDateTime"),
    "Base.Core.Time.Zone":          ("PyQt6.QtCore", "QTimeZone"),
    "Base.Core.Time.Timer":         ("PyQt6.QtCore", "QTimer"),
    "Base.Core.Timer":              ("PyQt6.QtCore", "QTimer"),
    "Base.Core.Time.Elapsed":       ("PyQt6.QtCore", "QElapsedTimer"),
    "Base.Core.Time.Line":          ("PyQt6.QtCore", "QTimeLine"),
    "Base.Core.Calendar":           ("PyQt6.QtCore", "QCalendar"),

    # Logging
    # ============================================================================
    "Base.Core.LogCategory":        ("PyQt6.QtCore", "QLoggingCategory"),
    "Base.Core.Message":            ("PyQt6.QtCore", "QMessageLogger"),
    # ============================================================================
    # Regex
    "Base.Core.Regex":                  ("PyQt6.QtCore", "QRegularExpression"),
    "Base.Core.Regex.Match":            ("PyQt6.QtCore", "QRegularExpressionMatch"),
    "Base.Core.Regex.Iterator":         ("PyQt6.QtCore", "QRegularExpressionMatchIterator"),
    # ============================================================================
    # Security
    "Base.Core.Hash":                   ("PyQt6.QtCore", "QCryptographicHash"),

    # Model/View
    "Base.Core.Model.Index":              ("PyQt6.QtCore", "QModelIndex"),
    "Base.Core.Model.ItemSelection":     ("PyQt6.QtCore", "QItemSelectionModel"),
    "Base.Core.Model.AbstractItem":      ("PyQt6.QtCore", "QAbstractItemModel"),
    "Base.Core.Model.AbstractList":      ("PyQt6.QtCore", "QAbstractListModel"),
    "Base.Core.Model.AbstractTable":     ("PyQt6.QtCore", "QAbstractTableModel"),
    "Base.Core.Model.SortFilter":        ("PyQt6.QtCore", "QSortFilterProxyModel"),
    "Base.Core.Model.PersistentIndex":  ("PyQt6.QtCore", "QPersistentModelIndex"),
    "Base.Core.Model.IdentityProxy":    ("PyQt6.QtCore", "QIdentityProxyModel"),
    "Base.Core.Model.AbstractProxy":            ("PyQt6.QtCore", "QAbstractProxyModel"),
    "Base.Core.Model.Concatenate":      ("PyQt6.QtCore", "QConcatenateTablesProxyModel"),
    "Base.Core.Model.Transpose":        ("PyQt6.QtCore", "QTransposeProxyModel"),

    # Geometry
    "Base.Geometry.Point": ("PyQt6.QtCore", "QPointF"),
    "Base.Geometry.Point.Int": ("PyQt6.QtCore", "QPoint"),
    "Base.Geometry.Size": ("PyQt6.QtCore", "QSizeF"),
    "Base.Geometry.Size.Int": ("PyQt6.QtCore", "QSize"),
    "Base.Geometry.Rect": ("PyQt6.QtCore", "QRectF"),
    "Base.Geometry.Rect.Int": ("PyQt6.QtCore", "QRect"),
    "Base.Geometry.Line": ("PyQt6.QtCore", "QLineF"),
    "Base.Geometry.Line.Int": ("PyQt6.QtCore", "QLine"),
    "Base.Geometry.Margins": ("PyQt6.QtCore", "QMarginsF"),
    "Base.Geometry.Margins.Int": ("PyQt6.QtCore", "QMargins"),
    "Base.Geometry.Easing": ("PyQt6.QtCore", "QEasingCurve"),
    # ============================================================================
    # 2. VISUAL — Рендеринг та графіка
    "Base.Visual":                     ("PyQt6.QtGui", None),

    # Painter
    "Base.Visual.Painter":             ("PyQt6.QtGui", "QPainter"),
    "Base.Visual.PainterPath":         ("PyQt6.QtGui", "QPainterPath"),
    "Base.Visual.Pen":                 ("PyQt6.QtGui", "QPen"),
    "Base.Visual.Brush":               ("PyQt6.QtGui", "QBrush"),
    "Base.Visual.Paint.Device":        ("PyQt6.QtGui", "QPaintDevice"),
    "Base.Visual.Paint.Engine":        ("PyQt6.QtGui", "QPaintEngine"),

    # Colors
    "Base.Visual.Color":               ("PyQt6.QtGui", "QColor"),
    "Base.Visual.Palette":             ("PyQt6.QtGui", "QPalette"),
    "Base.Visual.Color.Space":         ("PyQt6.QtGui", "QColorSpace"),

    # Gradient
    "Base.Visual.Gradient":            ("PyQt6.QtGui", None),
    "Base.Visual.Gradient.Linear":     ("PyQt6.QtGui", "QLinearGradient"),
    "Base.Visual.Gradient.Radial":     ("PyQt6.QtGui", "QRadialGradient"),
    "Base.Visual.Gradient.Conical":    ("PyQt6.QtGui", "QConicalGradient"),

    # Font
    "Base.Visual.Font":                ("PyQt6.QtGui", "QFont"),
    "Base.Visual.FontInfo":           ("PyQt6.QtGui", "QFontInfo"),
    "Base.Visual.Font.Database":       ("PyQt6.QtGui", "QFontDatabase"),
    "Base.Visual.FontDatabase":        ("PyQt6.QtGui", "QFontDatabase"),
    "Base.Visual.Font.Metrics":        ("PyQt6.QtGui", "QFontMetrics"),
    "Base.Visual.FontMetrics":         ("PyQt6.QtGui", "QFontMetrics"),
    "Base.Visual.Font.MetricsF":       ("PyQt6.QtGui", "QFontMetricsF"),
    "Base.Visual.FontMetricsF":        ("PyQt6.QtGui", "QFontMetricsF"),

    # Images
    "Base.Visual.Image":               ("PyQt6.QtGui", "QImage"),
    "Base.Visual.Image.Reader":        ("PyQt6.QtGui", "QImageReader"),
    "Base.Visual.Image.Writer":        ("PyQt6.QtGui", "QImageWriter"),
    "Base.Visual.Pixmap":              ("PyQt6.QtGui", "QPixmap"),
    "Base.Visual.Bitmap":              ("PyQt6.QtGui", "QBitmap"),
    "Base.Visual.Picture":             ("PyQt6.QtGui", "QPicture"),

    # Icons
    "Base.Visual.Icon":                ("PyQt6.QtGui", "QIcon"),
    "Base.Visual.Icon.Engine":         ("PyQt6.QtGui", "QIconEngine"),

    # Text
    "Base.Visual.Text.Document":       ("PyQt6.QtGui", "QTextDocument"),
    "Base.Visual.Text.Cursor":         ("PyQt6.QtGui", "QTextCursor"),
    "Base.Visual.Text.Layout":         ("PyQt6.QtGui", "QTextLayout"),
    "Base.Visual.Text.Option":         ("PyQt6.QtGui", "QTextOption"),
    "Base.Visual.Text.Block":          ("PyQt6.QtGui", "QTextBlock"),
    "Base.Visual.Text.BlockFormat":    ("PyQt6.QtGui", "QTextBlockFormat"),
    "Base.Visual.Text.CharFormat":     ("PyQt6.QtGui", "QTextCharFormat"),
    "Base.Visual.Text.ListFormat":     ("PyQt6.QtGui", "QTextListFormat"),
    "Base.Visual.Text.FrameFormat":    ("PyQt6.QtGui", "QTextFrameFormat"),
    "Base.Visual.Text.TableFormat":    ("PyQt6.QtGui", "QTextTableFormat"),
    "Base.Visual.Text.ImageFormat":    ("PyQt6.QtGui", "QTextImageFormat"),
    "Base.Visual.StaticText":          ("PyQt6.QtGui", "QStaticText"),
    "Base.Visual.GlyphRun":            ("PyQt6.QtGui", "QGlyphRun"),
    "Base.Visual.RawFont":             ("PyQt6.QtGui", "QRawFont"),
    # PDF
    "Base.Visual.PdfWriter":           ("PyQt6.QtGui", "QPdfWriter"),

    # Clipboard / Drag
    "Base.Visual.Clipboard":           ("PyQt6.QtGui", "QClipboard"),
    "Base.Visual.Drag":                ("PyQt6.QtGui", "QDrag"),
    "Base.Visual.Movie":                 ("PyQt6.QtGui", "QMovie"),

    # Transformations
    "Base.Visual.Polygon":             ("PyQt6.QtGui", "QPolygon"),
    "Base.Visual.PolygonF":            ("PyQt6.QtGui", "QPolygonF"),
    "Base.Visual.Region":              ("PyQt6.QtGui", "QRegion"),
    "Base.Visual.Transform":           ("PyQt6.QtGui", "QTransform"),
    "Base.Visual.Matrix4x4":           ("PyQt6.QtGui", "QMatrix4x4"),
    "Base.Visual.Quaternion":          ("PyQt6.QtGui", "QQuaternion"),
    "Base.Visual.Vector2D":            ("PyQt6.QtGui", "QVector2D"),
    "Base.Visual.Vector3D":            ("PyQt6.QtGui", "QVector3D"),
    "Base.Visual.Vector4D":            ("PyQt6.QtGui", "QVector4D"),

    # Cursor
    "Base.Visual.Cursor":              ("PyQt6.QtGui", "QCursor"),
    # Screen
    "Base.Visual.Screen":              ("PyQt6.QtGui", "QScreen"),
    "Base.Visual.Surface":               ("PyQt6.QtGui", "QSurface"),
    "Base.Visual.Surface.Format":        ("PyQt6.QtGui", "QSurfaceFormat"),
    "Base.Visual.Desktop.Services":      ("PyQt6.QtGui", "QDesktopServices"),

    # Actions
    "Base.Visual.Action":                ("PyQt6.QtGui", "QAction"),
    "Base.Visual.Action.Group":          ("PyQt6.QtGui", "QActionGroup"),
    "Base.Visual.Shortcut":              ("PyQt6.QtGui", "QShortcut"),

    # Validation
    "Base.Visual.Validator":           ("PyQt6.QtGui", "QValidator"),
    "Base.Visual.IntValidator":        ("PyQt6.QtGui", "QIntValidator"),
    "Base.Visual.DoubleValidator":     ("PyQt6.QtGui", "QDoubleValidator"),
    "Base.Visual.RegularExpression":        ("PyQt6.QtGui", "QRegularExpressionValidator"),

    # Undo
    "Base.Visual.Undo.Command":        ("PyQt6.QtGui", "QUndoCommand"),
    "Base.Visual.Undo.Stack":          ("PyQt6.QtGui", "QUndoStack"),
    "Base.Visual.Undo.Group":          ("PyQt6.QtGui", "QUndoGroup"),

    # Input
    "Base.Visual.Key.Event":           ("PyQt6.QtGui", "QKeyEvent"),
    "Base.Visual.Mouse.Event":         ("PyQt6.QtGui", "QMouseEvent"),
    "Base.Visual.Wheel.Event":         ("PyQt6.QtGui", "QWheelEvent"),
    "Base.Visual.Tablet.Event":        ("PyQt6.QtGui", "QTabletEvent"),
    "Base.Visual.Hover.Event":         ("PyQt6.QtGui", "QHoverEvent"),
    "Base.Visual.Drag.Enter":          ("PyQt6.QtGui", "QDragEnterEvent"),
    "Base.Visual.Drag.Move":           ("PyQt6.QtGui", "QDragMoveEvent"),
    "Base.Visual.Drag.Leave":          ("PyQt6.QtGui", "QDragLeaveEvent"),
    "Base.Visual.Drop.Event":          ("PyQt6.QtGui", "QDropEvent"),
    "Base.Visual.Input.Method":          ("PyQt6.QtGui", "QInputMethod"),
    "Base.Visual.Input.Method.Event":    ("PyQt6.QtGui", "QInputMethodEvent"),
    # ────────────────────────────────────────────────────────────────────────────
# 2.9 ДЕСКТОП ТА ВІКОННИЙ МЕНЕДЖЕР // DESKTOP MANAGER (Base.Desktop.*)
# Керування фізичними моніторами, вікнами оболонки ОС, системним треєм
# ────────────────────────────────────────────────────────────────────────────
    "Base.Desktop"                    : ("PyQt6.QtGui", "QGuiApplication"),
    "Base.Desktop.Screen"             : ("PyQt6.QtGui", "QScreen"),
    "Base.Desktop.Screens"            : ("PyQt6.QtGui.QGuiApplication", "screens"),
    "Base.Desktop.PrimaryScreen"      : ("PyQt6.QtGui.QGuiApplication", "primaryScreen"),
    "Base.Desktop.Display"            : ("PyQt6.QtGui", "QWindow"),
    "Base.Desktop.Cursor"             : ("PyQt6.QtGui", "QCursor"),
    "Base.Desktop.Clipboard"          : ("PyQt6.QtGui", "QClipboard"),
    "Base.Desktop.Service"            : ("PyQt6.QtGui", "QDesktopServices"),
    "Base.Desktop.Open"               : ("PyQt6.QtGui.QDesktopServices", "openUrl"),
    "Base.Desktop.Icon"               : ("PyQt6.QtWidgets", "QSystemTrayIcon"),

# ────────────────────────────────────────────────────────────────────────────
# 2.10 АУДІОМАТРИЦЯ МІСТКА // LCARS AUDIO MATRIX (Base.Audio.*)
# Миттєві біпи без затримок, ембієнти варп-ядра, тривоги
# ────────────────────────────────────────────────────────────────────────────
    "Base.Audio"                      : ("PyQt6.QtMultimedia", None),
    "Base.Audio.Effect"               : ("PyQt6.QtMultimedia", "QSoundEffect"),
    "Base.Audio.Player"               : ("PyQt6.QtMultimedia", "QMediaPlayer"),
    "Base.Audio.Output"               : ("PyQt6.QtMultimedia", "QAudioOutput"),
    "Base.Audio.Devices"              : ("PyQt6.QtMultimedia", "QMediaDevices"),

# ────────────────────────────────────────────────────────────────────────────
# 2.11 СЕНСОРНЕ ТА ЖЕСТОВЕ ВВЕДЕННЯ // TOUCH & GESTURE (Base.Input.*)
# Мультитач-панелі консолей PADD, жести збільшення та свайпи
# ────────────────────────────────────────────────────────────────────────────
    "Base.Input.Touch"                : ("PyQt6.QtGui", "QTouchEvent"),
    "Base.Input.TouchEvent"           : ("PyQt6.QtGui.QTouchEvent", "TouchPoint"),
    "Base.Input.Gesture"              : ("PyQt6.QtWidgets", "QGesture"),
    "Base.Input.Pinch"                : ("PyQt6.QtWidgets", "QPinchGesture"),
    "Base.Input.Pan"                  : ("PyQt6.QtWidgets", "QPanGesture"),
    "Base.Input.Swipe"                : ("PyQt6.QtWidgets", "QSwipeGesture"),
    "Base.Input.Recognizer"           : ("PyQt6.QtWidgets", "QGestureRecognizer"),
    # ═══════════════════════════════════════════════════════════════════════
    # 3. INTERFACE — UI компоненти
    "Base.Interface": ("PyQt6.QtWidgets", None),

    "Base.Interface.Widget": ("PyQt6.QtWidgets", "QWidget"),
    "Base.Interface.Application": ("PyQt6.QtWidgets", "QApplication"),
    "Base.Interface.Viewport": ("PyQt6.QtWidgets", "QMainWindow"),
    "Base.Interface.Dialog": ("PyQt6.QtWidgets", "QDialog"),
    "Base.Interface.Splash": ("PyQt6.QtWidgets", "QSplashScreen"),
    # Containers
    "Base.Interface.Frame": ("PyQt6.QtWidgets", "QFrame"),
    "Base.Interface.Group": ("PyQt6.QtWidgets", "QGroupBox"),
    "Base.Interface.Stack": ("PyQt6.QtWidgets", "QStackedWidget"),
    "Base.Interface.ToolBox": ("PyQt6.QtWidgets", "QToolBox"),
    "Base.Interface.Tab": ("PyQt6.QtWidgets", "QTabWidget"),
    "Base.Interface.Dock": ("PyQt6.QtWidgets", "QDockWidget"),
    "Base.Interface.Scroll": ("PyQt6.QtWidgets", "QScrollArea"),
    "Base.Interface.Splitter": ("PyQt6.QtWidgets", "QSplitter"),
    "Base.Interface.MDI": ("PyQt6.QtWidgets", "QMdiArea"),
    "Base.Interface.SubDisplay": ("PyQt6.QtWidgets", "QMdiSubWindow"),
    # ============================================================================
    # Layout
    "Base.Interface.Layout": ("PyQt6.QtWidgets", "QLayout"),
    "Base.Interface.Layout.Box": ("PyQt6.QtWidgets", "QBoxLayout"),
    "Base.Interface.Layout.Horizontal": ("PyQt6.QtWidgets", "QHBoxLayout"),
    "Base.Interface.Layout.Vertical": ("PyQt6.QtWidgets", "QVBoxLayout"),
    "Base.Interface.Layout.Grid": ("PyQt6.QtWidgets", "QGridLayout"),
    "Base.Interface.Layout.Form": ("PyQt6.QtWidgets", "QFormLayout"),
    "Base.Interface.Layout.Stacked": ("PyQt6.QtWidgets", "QStackedLayout"),
    "Base.Interface.SizePolicy":    ("PyQt6.QtWidgets", "QSizePolicy.Policy"),
    "Base.Interface.Layout.Spacer": ("PyQt6.QtWidgets", "QSpacerItem"),
    "Base.Interface.Layout.Graphics": ("PyQt6.QtWidgets", "QGraphicsLayout"),

    "Base.Interface.Graphics.Layout.Linear": ("PyQt6.QtWidgets", "QGraphicsLinearLayout"),
    "Base.Interface.Graphics.Layout.Grid": ("PyQt6.QtWidgets", "QGraphicsGridLayout"),
    "Base.Interface.Graphics.Anchor": ("PyQt6.QtWidgets", "QGraphicsAnchor"),
    "Base.Interface.Graphics.Layout.Anchor": ("PyQt6.QtWidgets", "QGraphicsAnchorLayout"),
    # ============================================================================
    # Input
    "Base.Interface.Label":               ("PyQt6.QtWidgets", "QLabel"),
    "Base.Interface.Button":              ("PyQt6.QtWidgets", "QPushButton"),
    "Base.Interface.ToolButton":          ("PyQt6.QtWidgets", "QToolButton"),
    "Base.Interface.Radio":               ("PyQt6.QtWidgets", "QRadioButton"),
    "Base.Interface.CheckBox":            ("PyQt6.QtWidgets", "QCheckBox"),
    "Base.Interface.Combo":               ("PyQt6.QtWidgets", "QComboBox"),
    "Base.Interface.LineEdit":            ("PyQt6.QtWidgets", "QLineEdit"),
    "Base.Interface.TextEdit":            ("PyQt6.QtWidgets", "QTextEdit"),
    "Base.Interface.PlainText":           ("PyQt6.QtWidgets", "QPlainTextEdit"),
    "Base.Interface.SpinBox":             ("PyQt6.QtWidgets", "QSpinBox"),
    "Base.Interface.DoubleSpinBox":       ("PyQt6.QtWidgets", "QDoubleSpinBox"),
    "Base.Interface.DateEdit":            ("PyQt6.QtWidgets", "QDateEdit"),
    "Base.Interface.TimeEdit":            ("PyQt6.QtWidgets", "QTimeEdit"),
    "Base.Interface.DateTimeEdit":        ("PyQt6.QtWidgets", "QDateTimeEdit"),
    "Base.Interface.Dial":                ("PyQt6.QtWidgets", "QDial"),
    "Base.Interface.Slider":              ("PyQt6.QtWidgets", "QSlider"),
    "Base.Interface.ScrollBar":           ("PyQt6.QtWidgets", "QScrollBar"),
    "Base.Interface.ProgressBar":         ("PyQt6.QtWidgets", "QProgressBar"),
    "Base.Interface.LCD":                 ("PyQt6.QtWidgets", "QLCDNumber"),
    # ============================================================================
    # Views
    "Base.Interface.List":                ("PyQt6.QtWidgets", "QListWidget"),
    "Base.Interface.Tree":                ("PyQt6.QtWidgets", "QTreeWidget"),
    "Base.Interface.Table":               ("PyQt6.QtWidgets", "QTableWidget"),

    "Base.Interface.View.List":           ("PyQt6.QtWidgets", "QListView"),
    "Base.Interface.View.Tree":           ("PyQt6.QtWidgets", "QTreeView"),
    "Base.Interface.View.Table":          ("PyQt6.QtWidgets", "QTableView"),
    "Base.Interface.View.Column":         ("PyQt6.QtWidgets", "QColumnView"),
    "Base.Interface.Header":              ("PyQt6.QtWidgets", "QHeaderView"),
    # ============================================================================
    # Menu
    "Base.Interface.Menu":                 ("PyQt6.QtWidgets", "QMenu"),
    "Base.Interface.MenuBar":             ("PyQt6.QtWidgets", "QMenuBar"),
    "Base.Interface.ToolBar":             ("PyQt6.QtWidgets", "QToolBar"),
    "Base.Interface.StatusBar":           ("PyQt6.QtWidgets", "QStatusBar"),

    # ============================================================================
    # Actions
    "Base.Interface.Action": ("PyQt6.QtWidgets", "QWidgetAction"),
    # Tray
    "Base.Interface.SystemTray": ("PyQt6.QtWidgets", "QSystemTrayIcon"),
    "Base.Interface.Breadcrumb": ("PyQt6.QtWidgets", "QCommandLinkButton"),
    # ============================================================================
    # Toolbar Helpers
    "Base.Interface.SizeGrip": ("PyQt6.QtWidgets", "QSizeGrip"),
    "Base.Interface.RubberBand": ("PyQt6.QtWidgets", "QRubberBand"),
    # ============================================================================
    # Dialogs
    "Base.Interface.Dialog.File": ("PyQt6.QtWidgets", "QFileDialog"),
    "Base.Interface.Dialog.Color": ("PyQt6.QtWidgets", "QColorDialog"),
    "Base.Interface.Dialog.Font": ("PyQt6.QtWidgets", "QFontDialog"),
    "Base.Interface.Dialog.Message": ("PyQt6.QtWidgets", "QMessageBox"),
    "Base.Interface.Dialog.Error": ("PyQt6.QtWidgets", "QErrorMessage"),
    "Base.Interface.Dialog.Input": ("PyQt6.QtWidgets", "QInputDialog"),
    "Base.Interface.Dialog.Progress": ("PyQt6.QtWidgets", "QProgressDialog"),
    "Base.Interface.Dialog.Wizard": ("PyQt6.QtWidgets", "QWizard"),
    "Base.Interface.Dialog.Wizard.Page": ("PyQt6.QtWidgets", "QWizardPage"),
    # ============================================================================
    # Item Widgets
    "Base.Interface.Item.List": ("PyQt6.QtWidgets", "QListWidgetItem"),
    "Base.Interface.Item.Tree": ("PyQt6.QtWidgets", "QTreeWidgetItem"),
    "Base.Interface.Item.Table": ("PyQt6.QtWidgets", "QTableWidgetItem"),
    "Base.Interface.Item.Iterator": ("PyQt6.QtWidgets", "QTreeWidgetItemIterator"),
    "Base.Interface.Graphics.Widget": ("PyQt6.QtWidgets", "QGraphicsWidget"),
    "Base.Interface.Graphics.Proxy": ("PyQt6.QtWidgets", "QGraphicsProxyWidget"),
    "Base.Interface.Graphics.Group": ("PyQt6.QtWidgets", "QGraphicsItemGroup"),

    # ============================================================================
    # Utility
    "Base.Interface.Completer": ("PyQt6.QtWidgets", "QCompleter"),
    "Base.Interface.Data.Mapper": ("PyQt6.QtWidgets", "QDataWidgetMapper"),
    "Base.Interface.Shortcut.Edit": ("PyQt6.QtWidgets", "QKeySequenceEdit"),
    # ============================================================================
    # Scene
    "Base.Graphics.Scene": ("PyQt6.QtWidgets", "QGraphicsScene"),
    "Base.Graphics.View": ("PyQt6.QtWidgets", "QGraphicsView"),
    "Base.Graphics.Item": ("PyQt6.QtWidgets", "QGraphicsItem"),
    "Base.Graphics.Object": ("PyQt6.QtWidgets", "QGraphicsObject"),
    # ============================================================================
    # Primitive
    "Base.Graphics.Line":                     ("PyQt6.QtWidgets", "QGraphicsLineItem"),
    "Base.Graphics.Rect":                     ("PyQt6.QtWidgets", "QGraphicsRectItem"),
    "Base.Graphics.Ellipse":                  ("PyQt6.QtWidgets", "QGraphicsEllipseItem"),
    "Base.Graphics.Path":                     ("PyQt6.QtWidgets", "QGraphicsPathItem"),
    "Base.Graphics.Polygon":                  ("PyQt6.QtWidgets", "QGraphicsPolygonItem"),
    "Base.Graphics.Text":                     ("PyQt6.QtWidgets", "QGraphicsTextItem"),
    "Base.Graphics.SimpleText":               ("PyQt6.QtWidgets", "QGraphicsSimpleTextItem"),
    "Base.Graphics.Image":                    ("PyQt6.QtWidgets", "QGraphicsPixmapItem"),
    # ============================================================================
    # Interactive / Effects
    "Base.Graphics.Widget":                   ("PyQt6.QtWidgets", "QGraphicsWidget"),
    "Base.Graphics.Effect":                   ("PyQt6.QtWidgets", "QGraphicsEffect"),
    "Base.Graphics.Effect.Blur":              ("PyQt6.QtWidgets", "QGraphicsBlurEffect"),
    "Base.Graphics.Effect.Colorize":          ("PyQt6.QtWidgets", "QGraphicsColorizeEffect"),
    "Base.Graphics.Effect.Shadow":        ("PyQt6.QtWidgets", "QGraphicsDropShadowEffect"),
    "Base.Graphics.Effect.Opacity":           ("PyQt6.QtWidgets", "QGraphicsOpacityEffect"),
    # ============================================================================
    # Animation
    "Base.Graphics.Animation.Item":        ("PyQt6.QtWidgets", "QGraphicsItemAnimation"),

    "Base.Animation.Abstract":            ("PyQt6.QtCore", "QAbstractAnimation"),
    "Base.Animation.Property":            ("PyQt6.QtCore", "QPropertyAnimation"),
    "Base.Animation.Variant":             ("PyQt6.QtCore", "QVariantAnimation"),

    # Timeline
    "Base.Animation.TimeLine":            ("PyQt6.QtCore", "QTimeLine"),

    # Groups
    "Base.Animation.Group":               ("PyQt6.QtCore", "QAnimationGroup"),
    "Base.Animation.Parallel":            ("PyQt6.QtCore", "QParallelAnimationGroup"),
    "Base.Animation.Sequential":          ("PyQt6.QtCore", "QSequentialAnimationGroup"),

    # Pause
    "Base.Animation.Pause":               ("PyQt6.QtCore", "QPauseAnimation"),
 
    # Scene Rendering
    "Base.Rendering":                     ("PyQt6.QtOpenGL", None),
    # Functions
    "Base.Rendering.Functions":           ("PyQt6.QtOpenGL", "QOpenGLFunctions"),
    # Buffers
    "Base.Rendering.Buffer":              ("PyQt6.QtOpenGL", "QOpenGLBuffer"),
    "Base.Rendering.VertexArray":         ("PyQt6.QtOpenGL", "QOpenGLVertexArrayObject"),
    "Base.Rendering.Framebuffer":         ("PyQt6.QtOpenGL", "QOpenGLFramebufferObject"),
    "Base.Rendering.Framebuffer.Format":  ("PyQt6.QtOpenGL", "QOpenGLFramebufferObjectFormat"),
    # Shader
    "Base.Rendering.Shader":              ("PyQt6.QtOpenGL", "QOpenGLShader"),
    "Base.Rendering.Program":             ("PyQt6.QtOpenGL", "QOpenGLShaderProgram"),
    # Texture
    "Base.Rendering.Texture":             ("PyQt6.QtOpenGL", "QOpenGLTexture"),
    # Debug
    "Base.Rendering.Debug":               ("PyQt6.QtOpenGL", "QOpenGLDebugLogger"),
    # Widget
    "Base.Rendering.View":                ("PyQt6.QtOpenGLWidgets", None),
    "Base.Rendering.ViewWidget":         ("PyQt6.QtOpenGLWidgets", "QOpenGLWidget"),
    # ============================================================================
    # Vector
    "Base.Vector":                 ("PyQt6.QtSvg", None),
    "Base.Vector.Renderer":        ("PyQt6.QtSvg", "QSvgRenderer"),
    "Base.Vector.Generator":       ("PyQt6.QtSvg", "QSvgGenerator"),
    "Base.Vector.View":            ("PyQt6.QtSvgWidgets", None),
    "Base.Vector.Widget":     ("PyQt6.QtSvgWidgets", "QSvgWidget"),
    # ============================================================================
    # Designer
    # ============================================================================
    "Base.Designer":                          ("PyQt6.QtDesigner", None),

    "Base.Designer.Form":                     ("PyQt6.QtDesigner", "QDesignerFormEditorInterface"),
    "Base.Designer.Widget.Box":               ("PyQt6.QtDesigner", "QDesignerWidgetBoxInterface"),
    "Base.Designer.Property":                 ("PyQt6.QtDesigner", "QDesignerPropertyEditorInterface"),
    "Base.Designer.Object":                   ("PyQt6.QtDesigner", "QDesignerObjectInspectorInterface"),
    "Base.Designer.Action":                   ("PyQt6.QtDesigner", "QDesignerActionEditorInterface"),
    "Base.Designer.Extension":                ("PyQt6.QtDesigner", "QExtensionFactory"),
    # Print
    "Base.Print":                             ("PyQt6.QtPrintSupport", None),
    "Base.Print.Printer":                     ("PyQt6.QtPrintSupport", "QPrinter"),
    # Preview
    "Base.Print.Preview":                     ("PyQt6.QtPrintSupport", "QPrintPreviewDialog"),
    "Base.Print.Preview.Widget":              ("PyQt6.QtPrintSupport", "QPrintPreviewWidget"),

    # ============================================================================
    # Dialogs
    "Base.Print.Dialog":                      ("PyQt6.QtPrintSupport", "QPrintDialog"),
    "Base.Print.Page.Setup":                  ("PyQt6.QtPrintSupport", "QPageSetupDialog"),

    # ═══════════════════════════════════════════════════════════════════════
    # 4. STORAGE — Сховище даних (QtSql + Python modules)
    "Base.Data":                   ("PyQt6.QtSql", None),
    "Base.Data.Connection":        ("PyQt6.QtSql", "QSqlDatabase"),
    "Base.Data.Driver":            ("PyQt6.QtSql", "QSqlDriver"),
    "Base.Data.Query":             ("PyQt6.QtSql", "QSqlQuery"),
    "Base.Data.Record":            ("PyQt6.QtSql", "QSqlRecord"),
    "Base.Data.Field":             ("PyQt6.QtSql", "QSqlField"),
    "Base.Data.Index":             ("PyQt6.QtSql", "QSqlIndex"),
    "Base.Data.Error":             ("PyQt6.QtSql", "QSqlError"),
    "Base.Data.Model":             ("PyQt6.QtSql", "QSqlQueryModel"),
    "Base.Data.Table":             ("PyQt6.QtSql", "QSqlTableModel"),
    "Base.Data.Relation":          ("PyQt6.QtSql", "QSqlRelation"),
    "Base.Data.Relational.Model": ("PyQt6.QtSql", "QSqlRelationalTableModel"),
    "Base.Data.Relational.Delegate": ("PyQt6.QtSql", "QSqlRelationalDelegate"),
    # ═══════════════════════════════════════════════════════════════════════
    "Base.PDF":                             ("PyQt6.QtPdf", None),

    "Base.PDF.Document":                    ("PyQt6.QtPdf", "QPdfDocument"),
    "Base.PDF.Page.Navigator":              ("PyQt6.QtPdf", "QPdfPageNavigator"),
    "Base.PDF.Selection":                   ("PyQt6.QtPdf", "QPdfSelection"),
    "Base.PDF.Link.Model":                  ("PyQt6.QtPdf", "QPdfLinkModel"),
    "Base.PDF.Bookmark.Model":              ("PyQt6.QtPdf", "QPdfBookmarkModel"),
    "Base.PDF.Search.Model":                ("PyQt6.QtPdf", "QPdfSearchModel"),

    "Base.PDF.View":                        ("PyQt6.QtPdfWidgets", None),
    "Base.PDF.View.Widget":                 ("PyQt6.QtPdfWidgets", "QPdfView"),

    # ============================================================================
    # DOM
    # ============================================================================
    "Base.Xml":                             ("PyQt6.QtXml", None),

    "Base.Xml.Document":                    ("PyQt6.QtXml", "QDomDocument"),
    "Base.Xml.Node":                        ("PyQt6.QtXml", "QDomNode"),
    "Base.Xml.Element":                     ("PyQt6.QtXml", "QDomElement"),
    "Base.Xml.Attribute":                   ("PyQt6.QtXml", "QDomAttr"),
    "Base.Xml.Text":                        ("PyQt6.QtXml", "QDomText"),
    "Base.Xml.Comment":                     ("PyQt6.QtXml", "QDomComment"),
    "Base.Xml.DocumentType":                ("PyQt6.QtXml", "QDomDocumentType"),
    "Base.Xml.NodeList":                    ("PyQt6.QtXml", "QDomNodeList"),
    "Base.Xml.NamedNodeMap":                ("PyQt6.QtXml", "QDomNamedNodeMap"),
    # ============================================================================
    # 5. MEDIA — Мультимедіа
    "Base.Media": ("PyQt6.QtMultimedia", None),
    "Base.Multimedia": ("PyQt6.QtMultimediaWidgets", None),

    "Base.Media.Sound":                         ("PyQt6.QtMultimedia", "QSoundEffect"),
    "Base.Media.Device":                        ("PyQt6.QtMultimedia", "QMediaDevices"),
    "Base.Media.Format":                        ("PyQt6.QtMultimedia", "QMediaFormat"),
    "Base.Media.MetaData":                      ("PyQt6.QtMultimedia", "QMediaMetaData"),
    "Base.Media.Player":                        ("PyQt6.QtMultimedia", "QMediaPlayer"),
    # ============================================================================
    # Audio
    "Base.Media.Audio.Input":                   ("PyQt6.QtMultimedia", "QAudioInput"),
    "Base.Media.Audio.Output":                  ("PyQt6.QtMultimedia", "QAudioOutput"),
    "Base.Media.Audio.Buffer":                  ("PyQt6.QtMultimedia", "QAudioBuffer"),
    "Base.Media.Audio.Decoder":                 ("PyQt6.QtMultimedia", "QAudioDecoder"),
    "Base.Media.Spatial.Listener":              ("PyQt6.QtMultimedia", "QAudioListener"),
    "Base.Media.Spatial.Room":                  ("PyQt6.QtMultimedia", "QAudioRoom"),
    # ============================================================================
    # Video
    "Base.Media.Video.Frame":                   ("PyQt6.QtMultimedia", "QVideoFrame"),
    "Base.Media.Video.Sink":                    ("PyQt6.QtMultimedia", "QVideoSink"),
    "Base.Media.Video.Widget":                  ("PyQt6.QtMultimediaWidgets", "QVideoWidget"),
    # ============================================================================
    # Camera
    "Base.Media.Camera":                        ("PyQt6.QtMultimedia", "QCamera"),
    "Base.Media.Camera.Device":                 ("PyQt6.QtMultimedia", "QCameraDevice"),
    # ============================================================================
    # Capture
    "Base.Media.Capture.Session":               ("PyQt6.QtMultimedia", "QMediaCaptureSession"),
    "Base.Media.Image.Capture":                 ("PyQt6.QtMultimedia", "QImageCapture"),
    "Base.Media.Recorder":                      ("PyQt6.QtMultimedia", "QMediaRecorder"),
    # ============================================================================
    # 6. COMMS — Комунікації
    # Serial
    "Base.Serial":                            ("PyQt6.QtSerialPort", None),
    # Port
    "Base.Serial.Port":                       ("PyQt6.QtSerialPort", "QSerialPort"),
    "Base.Serial.Port.Info":                  ("PyQt6.QtSerialPort", "QSerialPortInfo"),
    # ============================================================================
    # Base.Http
    # ============================================================================
    "Base.Http":                            ("PyQt6.QtHttpServer", None),

    "Base.Http.Server":                     ("PyQt6.QtHttpServer", "QHttpServer"),
    "Base.Http.Request":                    ("PyQt6.QtHttpServer", "QHttpServerRequest"),
    "Base.Http.Response":                   ("PyQt6.QtHttpServer", "QHttpServerResponse"),
    "Base.Http.Router":                     ("PyQt6.QtHttpServer", "QHttpServerRouter"),

    # Network
    "Base.Network":                            ("PyQt6.QtNetwork", None),
    "Base.Network.Manager":                    ("PyQt6.QtNetwork", "QNetworkAccessManager"),
    "Base.Network.Request":                    ("PyQt6.QtNetwork", "QNetworkRequest"),
    "Base.Network.Reply":                      ("PyQt6.QtNetwork", "QNetworkReply"),
    "Base.Network.Interface":                  ("PyQt6.QtNetwork", "QNetworkInterface"),
    "Base.Network.Address.Entry":              ("PyQt6.QtNetwork", "QNetworkAddressEntry"),
    # Address
    "Base.Network.Host":                       ("PyQt6.QtNetwork", "QHostAddress"),
    "Base.Network.Host.Info":                  ("PyQt6.QtNetwork", "QHostInfo"),
    "Base.Network.IPv4":                       ("PyQt6.QtNetwork", "QHostAddress"),
    "Base.Network.IPv6":                       ("PyQt6.QtNetwork", "QHostAddress"),
    # Socket
    "Base.Network.Socket":                     ("PyQt6.QtNetwork", "QAbstractSocket"),
    "Base.Network.TCP":                        ("PyQt6.QtNetwork", "QTcpSocket"),
    "Base.Network.Server":                     ("PyQt6.QtNetwork", "QTcpServer"),
    "Base.Network.UDP":                        ("PyQt6.QtNetwork", "QUdpSocket"),
    "Base.Network.Local.Socket":               ("PyQt6.QtNetwork", "QLocalSocket"),
    "Base.Network.Local.Server":               ("PyQt6.QtNetwork", "QLocalServer"),
    # SSL
    "Base.Network.SSL":                        ("PyQt6.QtNetwork", "QSslSocket"),
    "Base.Network.SSL.Certificate":            ("PyQt6.QtNetwork", "QSslCertificate"),
    "Base.Network.SSL.Configuration":          ("PyQt6.QtNetwork", "QSslConfiguration"),
    "Base.Network.SSL.Key":                    ("PyQt6.QtNetwork", "QSslKey"),
    "Base.Network.SSL.Cipher":                 ("PyQt6.QtNetwork", "QSslCipher"),
    # Proxy
    "Base.Network.Proxy":                      ("PyQt6.QtNetwork", "QNetworkProxy"),
    "Base.Network.Proxy.Factory":              ("PyQt6.QtNetwork", "QNetworkProxyFactory"),
    # DNS
    "Base.Network.DNS":                        ("PyQt6.QtNetwork", "QDnsLookup"),
    # Cookie
    "Base.Network.Cookie":                     ("PyQt6.QtNetwork", "QNetworkCookie"),
    "Base.Network.Cookie.Jar":                 ("PyQt6.QtNetwork", "QNetworkCookieJar"),
    # Cache
    "Base.Network.Cache":                      ("PyQt6.QtNetwork", "QAbstractNetworkCache"),
    "Base.Network.Disk.Cache":                 ("PyQt6.QtNetwork", "QNetworkDiskCache"),
    # Authentication
    "Base.Network.Authentication":             ("PyQt6.QtNetwork", "QAuthenticator"),
    "Base.Network.Auth":                    ("PyQt6.QtNetworkAuth", None),

    "Base.Network.Auth.OAuth2":             ("PyQt6.QtNetworkAuth", "QOAuth2AuthorizationCodeFlow"),
    "Base.Network.Auth.DeviceFlow":         ("PyQt6.QtNetworkAuth", "QOAuth2DeviceAuthorizationFlow"),
    "Base.Network.Auth.ReplyHandler":       ("PyQt6.QtNetworkAuth", "QOAuthHttpServerReplyHandler"),
    "Base.Network.Auth.PKCE":               ("PyQt6.QtNetworkAuth", "QOAuthUriSchemeReplyHandler"),
    # ============================================================================
    # Bluetooth
    "Base.Bluetooth":                         ("PyQt6.QtBluetooth", None),
    # Device
    "Base.Bluetooth.Device":                  ("PyQt6.QtBluetooth", "QBluetoothDeviceInfo"),
    "Base.Bluetooth.Address":                 ("PyQt6.QtBluetooth", "QBluetoothAddress"),
    "Base.Bluetooth.UUID":                    ("PyQt6.QtBluetooth", "QBluetoothUuid"),
    "Base.Bluetooth.Local":                   ("PyQt6.QtBluetooth", "QBluetoothLocalDevice"),
    # Discovery
    "Base.Bluetooth.Discovery":               ("PyQt6.QtBluetooth", "QBluetoothDeviceDiscoveryAgent"),
    "Base.Bluetooth.Service.Discovery":       ("PyQt6.QtBluetooth", "QBluetoothServiceDiscoveryAgent"),
    # Service
    "Base.Bluetooth.Service":                 ("PyQt6.QtBluetooth", "QBluetoothServiceInfo"),
    # ============================================================================
    # Socket
    "Base.Bluetooth.Socket":                  ("PyQt6.QtBluetooth", "QBluetoothSocket"),
    "Base.Bluetooth.Server":                  ("PyQt6.QtBluetooth", "QBluetoothServer"),
    # Transfer
    "Base.Bluetooth.Transfer.Manager":        ("PyQt6.QtBluetooth", "QBluetoothTransferManager"),
    "Base.Bluetooth.Transfer.Request":        ("PyQt6.QtBluetooth", "QBluetoothTransferRequest"),
    "Base.Bluetooth.Transfer.Reply":          ("PyQt6.QtBluetooth", "QBluetoothTransferReply"),
    # ============================================================================
    # 7. WEB — Веб (QtWebEngine)
    "Base.Web":                               ("PyQt6.QtWebChannel", None),
    # WebChannel
    "Base.Web.Channel":                       ("PyQt6.QtWebChannel", "QWebChannel"),
    # WebSockets
    "Base.Web.Socket":                        ("PyQt6.QtWebSockets", None),
    "Base.Web.Socket.Client":                 ("PyQt6.QtWebSockets", "QWebSocket"),
    "Base.Web.Socket.Server":                 ("PyQt6.QtWebSockets", "QWebSocketServer"),
    # Remote Objects
    "Base.Web.Remote":                        ("PyQt6.QtRemoteObjects", None),
    "Base.Web.Remote.Node":                   ("PyQt6.QtRemoteObjects", "QRemoteObjectNode"),
    "Base.Web.Remote.Host":                   ("PyQt6.QtRemoteObjects", "QRemoteObjectHost"),
    "Base.Web.Remote.Registry":               ("PyQt6.QtRemoteObjects", "QRemoteObjectRegistryHost"),
    "Base.Web.Remote.DynamicReplica":         ("PyQt6.QtRemoteObjects", "QRemoteObjectDynamicReplica"),
    "Base.Web.Remote.Replica":                ("PyQt6.QtRemoteObjects", "QRemoteObjectReplica"),
    # ------------------------------------------------------------------
    "Base.WebEngine":                       ("PyQt6.QtWebEngineCore", None),

    "Base.WebEngine.Page":                  ("PyQt6.QtWebEngineCore", "QWebEnginePage"),
    "Base.WebEngine.Profile":               ("PyQt6.QtWebEngineCore", "QWebEngineProfile"),
    "Base.WebEngine.Settings":              ("PyQt6.QtWebEngineCore", "QWebEngineSettings"),

    "Base.WebEngine.History":               ("PyQt6.QtWebEngineCore", "QWebEngineHistory"),
    "Base.WebEngine.History.Item":          ("PyQt6.QtWebEngineCore", "QWebEngineHistoryItem"),
    "Base.WebEngine.History.Model":         ("PyQt6.QtWebEngineCore", "QWebEngineHistoryModel"),

    "Base.WebEngine.Download":              ("PyQt6.QtWebEngineCore", "QWebEngineDownloadRequest"),

    "Base.WebEngine.Script":                ("PyQt6.QtWebEngineCore", "QWebEngineScript"),
    "Base.WebEngine.Script.Collection":     ("PyQt6.QtWebEngineCore", "QWebEngineScriptCollection"),

    "Base.WebEngine.Cookie":                ("PyQt6.QtWebEngineCore", "QWebEngineCookieStore"),

    "Base.WebEngine.Permission":            ("PyQt6.QtWebEngineCore", "QWebEnginePermission"),

    "Base.WebEngine.Find":                  ("PyQt6.QtWebEngineCore", "QWebEngineFindTextResult"),

    "Base.WebEngine.ContextMenu":           ("PyQt6.QtWebEngineCore", "QWebEngineContextMenuRequest"),

    "Base.WebEngine.FullScreen":            ("PyQt6.QtWebEngineCore", "QWebEngineFullScreenRequest"),

    "Base.WebEngine.FileSystem":            ("PyQt6.QtWebEngineCore", "QWebEngineFileSystemAccessRequest"),

    "Base.WebEngine.Notification":          ("PyQt6.QtWebEngineCore", "QWebEngineNotification"),

    "Base.WebEngine.ClientCertificate":     ("PyQt6.QtWebEngineCore", "QWebEngineClientCertificateSelection"),

    "Base.WebEngine.View":                  ("PyQt6.QtWebEngineWidgets", "QWebEngineView"),

    "Base.WebEngine.Navigation":            ("PyQt6.QtWebEngineCore", "QWebEngineNavigationRequest"),

    "Base.WebEngine.UrlRequest":            ("PyQt6.QtWebEngineCore", "QWebEngineUrlRequestInfo"),
    "Base.WebEngine.UrlInterceptor":        ("PyQt6.QtWebEngineCore", "QWebEngineUrlRequestInterceptor"),
    "Base.WebEngine.UrlScheme":             ("PyQt6.QtWebEngineCore", "QWebEngineUrlScheme"),
    "Base.WebEngine.UrlScheme.Handler":     ("PyQt6.QtWebEngineCore", "QWebEngineUrlSchemeHandler"),
    "Base.WebEngine.CertificateError":      ("PyQt6.QtWebEngineCore", "QWebEngineCertificateError"),

    # ═══════════════════════════════════════════════════════════════════════
    # 8. ANALYTICS — Діаграми та аналітика (QtCharts)
    "Base.Analytic": ("PyQt6.QtCharts", ""),
    "Base.Analytic.Chart": ("PyQt6.QtCharts", "QChart"),
    "Base.Analytic.ChartView": ("PyQt6.QtCharts", "QChartView"),
    "Base.Analytic.Series.Line": ("PyQt6.QtCharts", "QLineSeries"),
    "Base.Analytic.Series.Spline": ("PyQt6.QtCharts", "QSplineSeries"),
    "Base.Analytic.Series.Bar": ("PyQt6.QtCharts", "QBarSeries"),
    "Base.Analytic.Series.Pie": ("PyQt6.QtCharts", "QPieSeries"),
    "Base.Analytic.Series.Scatter": ("PyQt6.QtCharts", "QScatterSeries"),
    "Base.Analytic.Series.Area": ("PyQt6.QtCharts", "QAreaSeries"),
    "Base.Analytic.AxisX": ("PyQt6.QtCharts", "QValueAxis"),
    "Base.Analytic.AxisY": ("PyQt6.QtCharts", "QValueAxis"),
    "Base.Analytic.Axis.Category": ("PyQt6.QtCharts", "QBarCategoryAxis"),
    "Base.Analytic.Axis.DateTime": ("PyQt6.QtCharts", "QDateTimeAxis"),
    "Base.Analytic.Legend": ("PyQt6.QtCharts", "QLegend"),

    # Base.Position
    "Base.Position":                          ("PyQt6.QtPositioning", None),
    "Base.Position.Coordinate":               ("PyQt6.QtPositioning", "QGeoCoordinate"),
    "Base.Position.Info":                     ("PyQt6.QtPositioning", "QGeoPositionInfo"),
    "Base.Position.Source":                   ("PyQt6.QtPositioning", "QGeoPositionInfoSource"),

    # ============================================================================
    # Area
    "Base.Position.Area":                     ("PyQt6.QtPositioning", "QGeoAreaMonitorInfo"),
    "Base.Position.Area.Source":              ("PyQt6.QtPositioning", "QGeoAreaMonitorSource"),

    # ============================================================================
    # Satellite
    "Base.Position.Satellite":                ("PyQt6.QtPositioning", "QGeoSatelliteInfo"),
    "Base.Position.Satellite.Source":         ("PyQt6.QtPositioning", "QGeoSatelliteInfoSource"),
    # ============================================================================
    # Sensor
    "Base.Sensor":                            ("PyQt6.QtSensors", None),
    "Base.Sensor.Object":                     ("PyQt6.QtSensors", "QSensor"),
    "Base.Sensor.Reading":                    ("PyQt6.QtSensors", "QSensorReading"),
    "Base.Sensor.Filter":                     ("PyQt6.QtSensors", "QSensorFilter"),
    "Base.Sensor.Gesture":                    ("PyQt6.QtSensors", "QSensorGesture"),
    "Base.Sensor.Gesture.Manager":            ("PyQt6.QtSensors", "QSensorGestureManager"),
    "Base.Sensor.Gesture.Recognizer":         ("PyQt6.QtSensors", "QSensorGestureRecognizer"),
    # Accelerometer
    "Base.Sensor.Accelerometer":              ("PyQt6.QtSensors", "QAccelerometer"),
    "Base.Sensor.Accelerometer.Reading":      ("PyQt6.QtSensors", "QAccelerometerReading"),

    # Gyroscope
    "Base.Sensor.Gyroscope":                  ("PyQt6.QtSensors", "QGyroscope"),
    "Base.Sensor.Gyroscope.Reading":          ("PyQt6.QtSensors", "QGyroscopeReading"),

    # Compass
    "Base.Sensor.Compass":                    ("PyQt6.QtSensors", "QCompass"),
    "Base.Sensor.Compass.Reading":            ("PyQt6.QtSensors", "QCompassReading"),

    # Magnetometer
    "Base.Sensor.Magnetometer":               ("PyQt6.QtSensors", "QMagnetometer"),
    "Base.Sensor.Magnetometer.Reading":       ("PyQt6.QtSensors", "QMagnetometerReading"),

    # Orientation
    "Base.Sensor.Orientation":                ("PyQt6.QtSensors", "QOrientationSensor"),
    "Base.Sensor.Orientation.Reading":        ("PyQt6.QtSensors", "QOrientationReading"),

    # Rotation
    "Base.Sensor.Rotation":                   ("PyQt6.QtSensors", "QRotationSensor"),
    "Base.Sensor.Rotation.Reading":           ("PyQt6.QtSensors", "QRotationReading"),

    # Proximity
    "Base.Sensor.Proximity":                  ("PyQt6.QtSensors", "QProximitySensor"),
    "Base.Sensor.Proximity.Reading":          ("PyQt6.QtSensors", "QProximityReading"),

    # Light
    "Base.Sensor.Light":                      ("PyQt6.QtSensors", "QLightSensor"),
    "Base.Sensor.Light.Reading":              ("PyQt6.QtSensors", "QLightReading"),

    # Ambient Light
    "Base.Sensor.AmbientLight":               ("PyQt6.QtSensors", "QAmbientLightSensor"),
    "Base.Sensor.AmbientLight.Reading":       ("PyQt6.QtSensors", "QAmbientLightReading"),

    # Ambient Temperature
    "Base.Sensor.AmbientTemperature":         ("PyQt6.QtSensors", "QAmbientTemperatureSensor"),
    "Base.Sensor.AmbientTemperature.Reading": ("PyQt6.QtSensors", "QAmbientTemperatureReading"),

    # Pressure
    "Base.Sensor.Pressure":                   ("PyQt6.QtSensors", "QPressureSensor"),
    "Base.Sensor.Pressure.Reading":           ("PyQt6.QtSensors", "QPressureReading"),

    # Humidity
    "Base.Sensor.Humidity":                   ("PyQt6.QtSensors", "QHumiditySensor"),
    "Base.Sensor.Humidity.Reading":           ("PyQt6.QtSensors", "QHumidityReading"),

    # Altimeter
    "Base.Sensor.Altimeter":                  ("PyQt6.QtSensors", "QAltimeter"),
    "Base.Sensor.Altimeter.Reading":          ("PyQt6.QtSensors", "QAltimeterReading"),

    # Tilt
    "Base.Sensor.Tilt":                       ("PyQt6.QtSensors", "QTiltSensor"),
    "Base.Sensor.Tilt.Reading":               ("PyQt6.QtSensors", "QTiltReading"),

    # ============================================================================
    # Base.State
    # ============================================================================
    "Base.State":                             ("PyQt6.QtStateMachine", None),
    "Base.State.Machine":                     ("PyQt6.QtStateMachine", "QStateMachine"),
    "Base.State.State":                       ("PyQt6.QtStateMachine", "QState"),
    "Base.State.Final":                       ("PyQt6.QtStateMachine", "QFinalState"),
    "Base.State.History":                     ("PyQt6.QtStateMachine", "QHistoryState"),

    # ============================================================================
    # Transition
    "Base.State.Transition":                  ("PyQt6.QtStateMachine", "QAbstractTransition"),
    "Base.State.EventTransition":             ("PyQt6.QtStateMachine", "QEventTransition"),
    "Base.State.SignalTransition":            ("PyQt6.QtStateMachine", "QSignalTransition"),
    "Base.State.Animation":                   ("PyQt6.QtStateMachine", "QAbstractAnimation"),    
    # ============================================================================
    # Connection
    "Base.DBus":                               ("PyQt6.QtDBus", None),
    "Base.DBus.Connection":                    ("PyQt6.QtDBus", "QDBusConnection"),
    "Base.DBus.Interface":                     ("PyQt6.QtDBus", "QDBusInterface"),
    "Base.DBus.Message":                       ("PyQt6.QtDBus", "QDBusMessage"),
    "Base.DBus.Error":                         ("PyQt6.QtDBus", "QDBusError"),
    # Pending
    "Base.DBus.Pending.Call":                  ("PyQt6.QtDBus", "QDBusPendingCall"),
    "Base.DBus.Pending.Reply":                 ("PyQt6.QtDBus", "QDBusPendingReply"),
    # Object
    "Base.DBus.Object":                        ("PyQt6.QtDBus", "QDBusObjectPath"),
    "Base.DBus.Service":                       ("PyQt6.QtDBus", "QDBusServiceWatcher"),    
    # Serial
    "Base.Serial.SerialBus":                      ("PyQt6.QtSerialBus", None),

    "Base.Serial.SerialBus.CAN":                  ("PyQt6.QtSerialBus", "QCanBus"),
    "Base.Serial.SerialBus.Device":               ("PyQt6.QtSerialBus", "QCanBusDevice"),
    "Base.Serial.SerialBus.Frame":                ("PyQt6.QtSerialBus", "QCanBusFrame"),

    "Base.Serial.SerialBus.Modbus.Client":        ("PyQt6.QtSerialBus", "QModbusClient"),
    "Base.Serial.SerialBus.Modbus.Server":        ("PyQt6.QtSerialBus", "QModbusServer"),
    "Base.Serial.SerialBus.Modbus.TCP":           ("PyQt6.QtSerialBus", "QModbusTcpClient"),
    "Base.Serial.SerialBus.Modbus.RTU":           ("PyQt6.QtSerialBus", "QModbusRtuSerialClient"),
    # ============================================================================
    # MQTT
    # ============================================================================
    "Base.MQTT":                            ("PyQt6.QtMqtt", None),

    "Base.MQTT.Client":                     ("PyQt6.QtMqtt", "QMqttClient"),
    "Base.MQTT.Subscription":               ("PyQt6.QtMqtt", "QMqttSubscription"),
    "Base.MQTT.Message":                    ("PyQt6.QtMqtt", "QMqttMessage"),
    # ============================================================================
    # OPCUA
    # ============================================================================
    "Base.OPCUA":                           ("PyQt6.QtOpcUa", None),

    "Base.OPCUA.Client":                    ("PyQt6.QtOpcUa", "QOpcUaClient"),
    "Base.OPCUA.Node":                      ("PyQt6.QtOpcUa", "QOpcUaNode"),
    "Base.OPCUA.Endpoint":                  ("PyQt6.QtOpcUa", "QOpcUaEndpointDescription"),# Base.Help
    "Base.Help":                              ("PyQt6.QtHelp", None),

    "Base.Help.Engine":                       ("PyQt6.QtHelp", "QHelpEngine"),
    "Base.Help.Engine.Core":                  ("PyQt6.QtHelp", "QHelpEngineCore"),

    "Base.Help.Content":                      ("PyQt6.QtHelp", "QHelpContentModel"),
    "Base.Help.Content.Item":                 ("PyQt6.QtHelp", "QHelpContentItem"),

    "Base.Help.Index":                        ("PyQt6.QtHelp", "QHelpIndexModel"),

    "Base.Help.Search.Engine":                ("PyQt6.QtHelp", "QHelpSearchEngine"),
    "Base.Help.Search.Query":                 ("PyQt6.QtHelp", "QHelpSearchQuery"),
    "Base.Help.Search.Result":                ("PyQt6.QtHelp", "QHelpSearchResult"),
    # ============================================================================
    # Base.Test
    "Base.Test":                              ("PyQt6.QtTest", None),

    "Base.Test.Core":                         ("PyQt6.QtTest", "QTest"),
    "Base.Test.Event":                        ("PyQt6.QtTest", "QTestEventList"),  
    # ═══════════════════════════════════════════════════════════════════════
    # 9. PROTOCOL — Системні директиви (Qt)
    "Base.Protocol":                 ("PyQt6.QtCore", "Qt"),
    # ------------------------------------------------------------------
    # Mouse Buttons
    # ------------------------------------------------------------------
    "Base.Protocol.Mouse.Left":        ("PyQt6.QtCore", "Qt.MouseButton.LeftButton"),
    "Base.Protocol.Mouse.Right":       ("PyQt6.QtCore", "Qt.MouseButton.RightButton"),
    "Base.Protocol.Mouse.Middle":      ("PyQt6.QtCore", "Qt.MouseButton.MiddleButton"),
    "Base.Protocol.Mouse.Back":        ("PyQt6.QtCore", "Qt.MouseButton.BackButton"),
    "Base.Protocol.Mouse.Forward":     ("PyQt6.QtCore", "Qt.MouseButton.ForwardButton"),
    "Base.Protocol.Mouse.Task":        ("PyQt6.QtCore", "Qt.MouseButton.TaskButton"),
    "Base.Protocol.Mouse.Extra1":      ("PyQt6.QtCore", "Qt.MouseButton.ExtraButton1"),
    "Base.Protocol.Mouse.Extra2":      ("PyQt6.QtCore", "Qt.MouseButton.ExtraButton2"),
    # ------------------------------------------------------------------
    # Orientation
    # ------------------------------------------------------------------
    "Base.Protocol.Orientation.Horizontal": ("PyQt6.QtCore", "Qt.Orientation.Horizontal"),
    "Base.Protocol.Orientation.Vertical":   ("PyQt6.QtCore", "Qt.Orientation.Vertical"),
    # ------------------------------------------------------------------
    # Dock
    # ------------------------------------------------------------------
    "Base.Protocol.Dock.Left":         ("PyQt6.QtCore", "Qt.DockWidgetArea.LeftDockWidgetArea"),
    "Base.Protocol.Dock.Right":        ("PyQt6.QtCore", "Qt.DockWidgetArea.RightDockWidgetArea"),
    "Base.Protocol.Dock.Top":          ("PyQt6.QtCore", "Qt.DockWidgetArea.TopDockWidgetArea"),
    "Base.Protocol.Dock.Bottom":       ("PyQt6.QtCore", "Qt.DockWidgetArea.BottomDockWidgetArea"),
    "Base.Protocol.Dock.All":          ("PyQt6.QtCore", "Qt.DockWidgetArea.AllDockWidgetAreas"),
    "Base.Protocol.Dock.None":         ("PyQt6.QtCore", "Qt.DockWidgetArea.NoDockWidgetArea"),
    # ------------------------------------------------------------------
    # Toolbar
    # ------------------------------------------------------------------
    "Base.Protocol.Toolbar.Left":      ("PyQt6.QtCore", "Qt.ToolBarArea.LeftToolBarArea"),
    "Base.Protocol.Toolbar.Right":     ("PyQt6.QtCore", "Qt.ToolBarArea.RightToolBarArea"),
    "Base.Protocol.Toolbar.Top":       ("PyQt6.QtCore", "Qt.ToolBarArea.TopToolBarArea"),
    "Base.Protocol.Toolbar.Bottom":    ("PyQt6.QtCore", "Qt.ToolBarArea.BottomToolBarArea"),
    "Base.Protocol.Toolbar.All":       ("PyQt6.QtCore", "Qt.ToolBarArea.AllToolBarAreas"),
    # ------------------------------------------------------------------
    # Check State
    # ------------------------------------------------------------------
    "Base.Protocol.Check.Unchecked":   ("PyQt6.QtCore", "Qt.CheckState.Unchecked"),
    "Base.Protocol.Check.Partial":     ("PyQt6.QtCore", "Qt.CheckState.PartiallyChecked"),
    "Base.Protocol.Check.Checked":     ("PyQt6.QtCore", "Qt.CheckState.Checked"),
    # ------------------------------------------------------------------
    # Case Sensitivity
    # ------------------------------------------------------------------
    "Base.Protocol.Case.Sensitive":    ("PyQt6.QtCore", "Qt.CaseSensitivity.CaseSensitive"),
    "Base.Protocol.Case.Insensitive":  ("PyQt6.QtCore", "Qt.CaseSensitivity.CaseInsensitive"),
    # ------------------------------------------------------------------
    # Timer
    # ------------------------------------------------------------------
    "Base.Protocol.Timer.Precise":     ("PyQt6.QtCore", "Qt.TimerType.PreciseTimer"),
    "Base.Protocol.Timer.Coarse":      ("PyQt6.QtCore", "Qt.TimerType.CoarseTimer"),
    "Base.Protocol.Timer.VeryCoarse":  ("PyQt6.QtCore", "Qt.TimerType.VeryCoarseTimer"),
    # ------------------------------------------------------------------
    # Connection
    # ------------------------------------------------------------------
    "Base.Protocol.Connection.Auto":      ("PyQt6.QtCore", "Qt.ConnectionType.AutoConnection"),
    "Base.Protocol.Connection.Direct":    ("PyQt6.QtCore", "Qt.ConnectionType.DirectConnection"),
    "Base.Protocol.Connection.Queued":    ("PyQt6.QtCore", "Qt.ConnectionType.QueuedConnection"),
    "Base.Protocol.Connection.Blocking":  ("PyQt6.QtCore", "Qt.ConnectionType.BlockingQueuedConnection"),
    "Base.Protocol.Connection.Unique":    ("PyQt6.QtCore", "Qt.ConnectionType.UniqueConnection"),
    # ------------------------------------------------------------------
    # Date Format
    # ------------------------------------------------------------------
    "Base.Protocol.Date.Text":         ("PyQt6.QtCore", "Qt.DateFormat.TextDate"),
    "Base.Protocol.Date.ISO":          ("PyQt6.QtCore", "Qt.DateFormat.ISODate"),
    "Base.Protocol.Date.ISOWithMS":    ("PyQt6.QtCore", "Qt.DateFormat.ISODateWithMs"),
    "Base.Protocol.Date.RFC2822":      ("PyQt6.QtCore", "Qt.DateFormat.RFC2822Date"),
    # -----------------------------------------------------------------
    # Context Menu
    # ------------------------------------------------------------------
    "Base.Protocol.Context.Default":   ("PyQt6.QtCore", "Qt.ContextMenuPolicy.DefaultContextMenu"),
    "Base.Protocol.Context.Actions":   ("PyQt6.QtCore", "Qt.ContextMenuPolicy.ActionsContextMenu"),
    "Base.Protocol.Context.Custom":    ("PyQt6.QtCore", "Qt.ContextMenuPolicy.CustomContextMenu"),
    "Base.Protocol.Context.Prevent":   ("PyQt6.QtCore", "Qt.ContextMenuPolicy.PreventContextMenu"),
    "Base.Protocol.Context.None":      ("PyQt6.QtCore", "Qt.ContextMenuPolicy.NoContextMenu"),
    # ------------------------------------------------------------------
    # Drop Action
    # ------------------------------------------------------------------
    "Base.Protocol.Drop.Copy":         ("PyQt6.QtCore", "Qt.DropAction.CopyAction"),
    "Base.Protocol.Drop.Move":         ("PyQt6.QtCore", "Qt.DropAction.MoveAction"),
    "Base.Protocol.Drop.Link":         ("PyQt6.QtCore", "Qt.DropAction.LinkAction"),
    "Base.Protocol.Drop.Ignore":       ("PyQt6.QtCore", "Qt.DropAction.IgnoreAction"),
    # ------------------------------------------------------------------
    # Arrow
    # ------------------------------------------------------------------
    "Base.Protocol.Arrow.Up":          ("PyQt6.QtCore", "Qt.ArrowType.UpArrow"),
    "Base.Protocol.Arrow.Down":        ("PyQt6.QtCore", "Qt.ArrowType.DownArrow"),
    "Base.Protocol.Arrow.Left":        ("PyQt6.QtCore", "Qt.ArrowType.LeftArrow"),
    "Base.Protocol.Arrow.Right":       ("PyQt6.QtCore", "Qt.ArrowType.RightArrow"),
    "Base.Protocol.Arrow.None":        ("PyQt6.QtCore", "Qt.ArrowType.NoArrow"),    
    # ------------------------------------------------------------------
    # Alignment
    # ------------------------------------------------------------------
    "Base.Protocol.AlignmentFlag":     ("PyQt6.QtCore", "Qt.AlignmentFlag"),
    "Base.Protocol.Alignment":         ("PyQt6.QtCore", "Qt.AlignmentFlag"),
    "Base.Protocol.Align.Left":        ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignLeft"),
    "Base.Protocol.Align.Right":       ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignRight"),
    "Base.Protocol.Align.Top":         ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignTop"),
    "Base.Protocol.Align.Bottom":      ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignBottom"),
    "Base.Protocol.Align.Center":      ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignCenter"),
    "Base.Protocol.Align.HCenter":     ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignHCenter"),
    "Base.Protocol.Align.VCenter":     ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignVCenter"),
    "Base.Protocol.Align.Justify":     ("PyQt6.QtCore", "Qt.AlignmentFlag.AlignJustify"),
    # ==========================================================
    # APPLICATION
    # ==========================================================
    "Base.Protocol.Application.HighDpiPixmaps":        ("PyQt6.QtCore", "Qt.ApplicationAttribute.AA_UseHighDpiPixmaps"),
    "Base.Protocol.Application.DesktopOpenGL":     ("PyQt6.QtCore", "Qt.ApplicationAttribute.AA_UseDesktopOpenGL"),
    "Base.Protocol.Application.Contexts":    ("PyQt6.QtCore", "Qt.ApplicationAttribute.AA_ShareOpenGLContexts"),
    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------
    "Base.Protocol.Display.Widget":     ("PyQt6.QtCore", "Qt.WindowType.Widget"),
    "Base.Protocol.Display.Dialog":     ("PyQt6.QtCore", "Qt.WindowType.Dialog"),
    "Base.Protocol.Display.Popup":      ("PyQt6.QtCore", "Qt.WindowType.Popup"),
    "Base.Protocol.Display.Tool":       ("PyQt6.QtCore", "Qt.WindowType.Tool"),
    "Base.Protocol.Display.Splash":     ("PyQt6.QtCore", "Qt.WindowType.SplashScreen"),
    "Base.Protocol.Display.Sheet":      ("PyQt6.QtCore", "Qt.WindowType.Sheet"),
    "Base.Protocol.Display.Drawer":     ("PyQt6.QtCore", "Qt.WindowType.Drawer"),
    "Base.Protocol.Display.ToolTip":    ("PyQt6.QtCore", "Qt.WindowType.ToolTip"),
    "Base.Protocol.Display.Normal":     ("PyQt6.QtCore", "Qt.WindowState.WindowNoState"),
    "Base.Protocol.Display.Minimized":  ("PyQt6.QtCore", "Qt.WindowState.WindowMinimized"),
    "Base.Protocol.Display.Maximized":  ("PyQt6.QtCore", "Qt.WindowState.WindowMaximized"),
    "Base.Protocol.Display.FullScreen": ("PyQt6.QtCore", "Qt.WindowState.WindowFullScreen"),
    "Base.Protocol.Display.Active":     ("PyQt6.QtCore", "Qt.WindowState.WindowActive"),

    "Base.Protocol.DisplayFlag.Frameless":     ("PyQt6.QtCore", "Qt.WindowType.FramelessWindowHint"),
    "Base.Protocol.DisplayFlag.StayOnTop":     ("PyQt6.QtCore", "Qt.WindowType.WindowStaysOnTopHint"),
    "Base.Protocol.DisplayFlag.StayOnBottom":  ("PyQt6.QtCore", "Qt.WindowType.WindowStaysOnBottomHint"),
    "Base.Protocol.DisplayFlag.Customize":     ("PyQt6.QtCore", "Qt.WindowType.CustomizeWindowHint"),
    "Base.Protocol.DisplayFlag.CloseButton":   ("PyQt6.QtCore", "Qt.WindowType.WindowCloseButtonHint"),
    "Base.Protocol.DisplayFlag.MinimizeButton":("PyQt6.QtCore", "Qt.WindowType.WindowMinimizeButtonHint"),
    "Base.Protocol.DisplayFlag.MaximizeButton":("PyQt6.QtCore", "Qt.WindowType.WindowMaximizeButtonHint"),
    "Base.Protocol.WindowType":                ("PyQt6.QtCore", "Qt.WindowType"),
    "Base.Protocol.Align.WindowType":          ("PyQt6.QtCore", "Qt.WindowType"),
    "Base.Protocol.FramelessWindowHint":        ("PyQt6.QtCore", "Qt.WindowType.FramelessWindowHint"),
    "Base.Protocol.Align.WindowType.FramelessWindowHint": ("PyQt6.QtCore", "Qt.WindowType.FramelessWindowHint"),
    "Base.Flags.Frameless":                    ("PyQt6.QtCore", "Qt.WindowType.FramelessWindowHint"),
    "Base.Protocol.Display.Frameless":         ("PyQt6.QtCore", "Qt.WindowType.FramelessWindowHint"),
    "Base.Protocol.Display":                   ("PyQt6.QtCore", "Qt.WindowType"),
    # ==========================================================
    # WIDGET
    # ==========================================================
    "Base.Protocol.Widget.DeleteOnClose":      ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_DeleteOnClose"),
    "Base.Protocol.Widget.Transparent":        ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_TranslucentBackground"),
    "Base.Protocol.Widget.Translucent":        ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_TranslucentBackground"),
    "Base.Protocol.Widget.NoBackground":       ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_NoSystemBackground"),
    "Base.Protocol.Widget.StyledBackground":   ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_StyledBackground"),
    "Base.Protocol.Widget.Hover":              ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_Hover"),
    "Base.Protocol.Widget.Disabled":           ("PyQt6.QtCore", "Qt.WidgetAttribute.WA_Disabled"),
    # ------------------------------------------------------------------
    # Focus
    # ------------------------------------------------------------------
    "Base.Protocol.Focus.None":        ("PyQt6.QtCore", "Qt.FocusPolicy.NoFocus"),
    "Base.Protocol.Focus.Tab":         ("PyQt6.QtCore", "Qt.FocusPolicy.TabFocus"),
    "Base.Protocol.Focus.click":       ("PyQt6.QtCore", "Qt.FocusPolicy.ClickFocus"),
    "Base.Protocol.Focus.Strong":      ("PyQt6.QtCore", "Qt.FocusPolicy.StrongFocus"),
    "Base.Protocol.Focus.Wheel":       ("PyQt6.QtCore", "Qt.FocusPolicy.WheelFocus"),
    # ------------------------------------------------------------------
    # Scroll
    # ------------------------------------------------------------------
    "Base.Protocol.Scroll.AlwaysOff":  ("PyQt6.QtCore", "Qt.ScrollBarPolicy.ScrollBarAlwaysOff"),
    "Base.Protocol.Scroll.AlwaysOn":   ("PyQt6.QtCore", "Qt.ScrollBarPolicy.ScrollBarAlwaysOn"),
    "Base.Protocol.Scroll.AsNeeded":   ("PyQt6.QtCore", "Qt.ScrollBarPolicy.ScrollBarAsNeeded"),
    # ------------------------------------------------------------------
    # Cursor
    # ------------------------------------------------------------------
    "Base.Protocol.Cursor.Arrow":      ("PyQt6.QtCore", "Qt.CursorShape.ArrowCursor"),
    "Base.Protocol.Cursor.Cross":      ("PyQt6.QtCore", "Qt.CursorShape.CrossCursor"),
    "Base.Protocol.Cursor.Wait":       ("PyQt6.QtCore", "Qt.CursorShape.WaitCursor"),
    "Base.Protocol.Cursor.IBeam":      ("PyQt6.QtCore", "Qt.CursorShape.IBeamCursor"),
    "Base.Protocol.Cursor.SizeAll":    ("PyQt6.QtCore", "Qt.CursorShape.SizeAllCursor"),
    "Base.Protocol.Cursor.Pointing":   ("PyQt6.QtCore", "Qt.CursorShape.PointingHandCursor"),
    "Base.Protocol.Cursor.Forbidden":  ("PyQt6.QtCore", "Qt.CursorShape.ForbiddenCursor"),
    "Base.Protocol.Cursor.Busy":       ("PyQt6.QtCore", "Qt.CursorShape.BusyCursor"),
    # ------------------------------------------------------------------
    # Keyboard Modifier
    # ------------------------------------------------------------------
    "Base.Protocol.Keyboard.Shift":    ("PyQt6.QtCore", "Qt.KeyboardModifier.ShiftModifier"),
    "Base.Protocol.Keyboard.Control":  ("PyQt6.QtCore", "Qt.KeyboardModifier.ControlModifier"),
    "Base.Protocol.Keyboard.Alt":      ("PyQt6.QtCore", "Qt.KeyboardModifier.AltModifier"),
    "Base.Protocol.Keyboard.Meta":     ("PyQt6.QtCore", "Qt.KeyboardModifier.MetaModifier"),
    # ------------------------------------------------------------------
    # Shortcut
    # ------------------------------------------------------------------
    "Base.Protocol.Shortcut.Window":   ("PyQt6.QtCore", "Qt.ShortcutContext.WindowShortcut"),
    "Base.Protocol.Shortcut.Widget":   ("PyQt6.QtCore", "Qt.ShortcutContext.WidgetShortcut"),
    "Base.Protocol.Shortcut.Application":("PyQt6.QtCore","Qt.ShortcutContext.ApplicationShortcut"),
    # ------------------------------------------------------------------
    # Match
    # ------------------------------------------------------------------
    "Base.Protocol.Match.Exact":       ("PyQt6.QtCore", "Qt.MatchFlag.MatchExactly"),
    "Base.Protocol.Match.Contains":    ("PyQt6.QtCore", "Qt.MatchFlag.MatchContains"),
    "Base.Protocol.Match.StartsWith":  ("PyQt6.QtCore", "Qt.MatchFlag.MatchStartsWith"),
    "Base.Protocol.Match.EndsWith":    ("PyQt6.QtCore", "Qt.MatchFlag.MatchEndsWith"),
    "Base.Protocol.Match.Regex":       ("PyQt6.QtCore", "Qt.MatchFlag.MatchRegularExpression"),
    # ------------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------------
    "Base.Protocol.Sort.Ascending":    ("PyQt6.QtCore", "Qt.SortOrder.AscendingOrder"),
    "Base.Protocol.Sort.Descending":   ("PyQt6.QtCore", "Qt.SortOrder.DescendingOrder"),
    # ------------------------------------------------------------------
    # Aspect Ratio
    # ------------------------------------------------------------------
    "Base.Protocol.Aspect.Ignore":     ("PyQt6.QtCore", "Qt.AspectRatioMode.IgnoreAspectRatio"),
    "Base.Protocol.Aspect.Keep":       ("PyQt6.QtCore", "Qt.AspectRatioMode.KeepAspectRatio"),
    "Base.Protocol.Aspect.Expand":     ("PyQt6.QtCore", "Qt.AspectRatioMode.KeepAspectRatioByExpanding"),
    # ------------------------------------------------------------------
    # Transformation
    # ------------------------------------------------------------------
    "Base.Protocol.Transform.Fast":    ("PyQt6.QtCore", "Qt.TransformationMode.FastTransformation"),
    "Base.Protocol.Transform.Smooth":  ("PyQt6.QtCore", "Qt.TransformationMode.SmoothTransformation"),
    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------
    "Base.Protocol.Text.Plain":        ("PyQt6.QtCore", "Qt.TextFormat.PlainText"),
    "Base.Protocol.Text.Rich":         ("PyQt6.QtCore", "Qt.TextFormat.RichText"),
    "Base.Protocol.Text.Auto":         ("PyQt6.QtCore", "Qt.TextFormat.AutoText"),
    "Base.Protocol.Text.Markdown":     ("PyQt6.QtCore", "Qt.TextFormat.MarkdownText"),
    # ------------------------------------------------------------------
    # Layout Direction
    # ------------------------------------------------------------------
    "Base.Protocol.Layout.LeftToRight":("PyQt6.QtCore", "Qt.LayoutDirection.LeftToRight"),
    "Base.Protocol.Layout.RightToLeft":("PyQt6.QtCore", "Qt.LayoutDirection.RightToLeft"),
    # ------------------------------------------------------------------
    # Item Data Role
    # ------------------------------------------------------------------
    "Base.Protocol.Item.DataRole":      ("PyQt6.QtCore", "Qt.ItemDataRole.DisplayRole"),
    "Base.Protocol.Item.Decoration":   ("PyQt6.QtCore", "Qt.ItemDataRole.DecorationRole"),
    "Base.Protocol.Item.Edit":         ("PyQt6.QtCore", "Qt.ItemDataRole.EditRole"),
    "Base.Protocol.Item.ToolTip":      ("PyQt6.QtCore", "Qt.ItemDataRole.ToolTipRole"),
    "Base.Protocol.Item.StatusTip":    ("PyQt6.QtCore", "Qt.ItemDataRole.StatusTipRole"),
    "Base.Protocol.Item.User":         ("PyQt6.QtCore", "Qt.ItemDataRole.UserRole"),
    # ------------------------------------------------------------------
    # Item Flags
    # ------------------------------------------------------------------
    "Base.Protocol.Item.Enabled":      ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsEnabled"),
    "Base.Protocol.Item.Selectable":   ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsSelectable"),
    "Base.Protocol.Item.Editable":     ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsEditable"),
    "Base.Protocol.Item.Checkable":    ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsUserCheckable"),
    "Base.Protocol.Item.Drag":         ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsDragEnabled"),
    "Base.Protocol.Item.Drop":         ("PyQt6.QtCore", "Qt.ItemFlag.ItemIsDropEnabled"),
    # ==========================================================
    # FILL
    # ==========================================================
    "Base.Protocol.Fill.OddEven":              ("PyQt6.QtCore", "Qt.FillRule.OddEvenFill"),
    "Base.Protocol.Fill.Winding":              ("PyQt6.QtCore", "Qt.FillRule.WindingFill"),
    # ==========================================================
    # CLIP
    # ==========================================================
    "Base.Protocol.Clip.None":                 ("PyQt6.QtCore", "Qt.ClipOperation.NoClip"),
    "Base.Protocol.Clip.Replace":              ("PyQt6.QtCore", "Qt.ClipOperation.ReplaceClip"),
    "Base.Protocol.Clip.Intersect":            ("PyQt6.QtCore", "Qt.ClipOperation.IntersectClip"),
    # ------------------------------------------------------------------
    # Edge
    # ------------------------------------------------------------------
    "Base.Protocol.Edge.Left":    ("PyQt6.QtCore", "Qt.Edge.LeftEdge"),
    "Base.Protocol.Edge.Right":   ("PyQt6.QtCore", "Qt.Edge.RightEdge"),
    "Base.Protocol.Edge.Top":     ("PyQt6.QtCore", "Qt.Edge.TopEdge"),
    "Base.Protocol.Edge.Bottom":  ("PyQt6.QtCore", "Qt.Edge.BottomEdge"),
    # ------------------------------------------------------------------
    # Event
    # ------------------------------------------------------------------
    "Base.Protocol.Event.None":          ("PyQt6.QtCore", "QEvent.Type.None_"),
    "Base.Protocol.Event.Timer":         ("PyQt6.QtCore", "QEvent.Type.Timer"),
    "Base.Protocol.Event.MousePress":    ("PyQt6.QtCore", "QEvent.Type.MouseButtonPress"),
    "Base.Protocol.Event.MouseRelease":  ("PyQt6.QtCore", "QEvent.Type.MouseButtonRelease"),
    "Base.Protocol.Event.MouseMove":     ("PyQt6.QtCore", "QEvent.Type.MouseMove"),
    "Base.Protocol.Event.MouseDblClick": ("PyQt6.QtCore", "QEvent.Type.MouseButtonDblClick"),
    "Base.Protocol.Event.Wheel":         ("PyQt6.QtCore", "QEvent.Type.Wheel"),
    "Base.Protocol.Event.KeyPress":      ("PyQt6.QtCore", "QEvent.Type.KeyPress"),
    "Base.Protocol.Event.KeyRelease":    ("PyQt6.QtCore", "QEvent.Type.KeyRelease"),
    "Base.Protocol.Event.FocusIn":       ("PyQt6.QtCore", "QEvent.Type.FocusIn"),
    "Base.Protocol.Event.FocusOut":      ("PyQt6.QtCore", "QEvent.Type.FocusOut"),
    "Base.Protocol.Event.Enter":         ("PyQt6.QtCore", "QEvent.Type.Enter"),
    "Base.Protocol.Event.Leave":         ("PyQt6.QtCore", "QEvent.Type.Leave"),
    "Base.Protocol.Event.Paint":         ("PyQt6.QtCore", "QEvent.Type.Paint"),
    "Base.Protocol.Event.Move":          ("PyQt6.QtCore", "QEvent.Type.Move"),
    "Base.Protocol.Event.Resize":        ("PyQt6.QtCore", "QEvent.Type.Resize"),
    "Base.Protocol.Event.Show":          ("PyQt6.QtCore", "QEvent.Type.Show"),
    "Base.Protocol.Event.Hide":          ("PyQt6.QtCore", "QEvent.Type.Hide"),
    "Base.Protocol.Event.Close":         ("PyQt6.QtCore", "QEvent.Type.Close"),
    "Base.Protocol.Event.DragEnter":     ("PyQt6.QtCore", "QEvent.Type.DragEnter"),
    "Base.Protocol.Event.DragMove":      ("PyQt6.QtCore", "QEvent.Type.DragMove"),
    "Base.Protocol.Event.DragLeave":     ("PyQt6.QtCore", "QEvent.Type.DragLeave"),
    "Base.Protocol.Event.Drop":          ("PyQt6.QtCore", "QEvent.Type.Drop"),
    "Base.Protocol.Event.ContextMenu":   ("PyQt6.QtCore", "QEvent.Type.ContextMenu"),
    # ------------------------------------------------------------------
    # Keyboard Keys
    # ------------------------------------------------------------------
    "Base.Protocol.Key.Escape":      ("PyQt6.QtCore", "Qt.Key.Key_Escape"),
    "Base.Protocol.Key.Tab":         ("PyQt6.QtCore", "Qt.Key.Key_Tab"),
    "Base.Protocol.Key.Backtab":     ("PyQt6.QtCore", "Qt.Key.Key_Backtab"),
    "Base.Protocol.Key.Backspace":   ("PyQt6.QtCore", "Qt.Key.Key_Backspace"),
    "Base.Protocol.Key.Return":      ("PyQt6.QtCore", "Qt.Key.Key_Return"),
    "Base.Protocol.Key.Enter":       ("PyQt6.QtCore", "Qt.Key.Key_Enter"),
    "Base.Protocol.Key.Insert":      ("PyQt6.QtCore", "Qt.Key.Key_Insert"),
    "Base.Protocol.Key.Delete":      ("PyQt6.QtCore", "Qt.Key.Key_Delete"),
    "Base.Protocol.Key.Pause":       ("PyQt6.QtCore", "Qt.Key.Key_Pause"),
    "Base.Protocol.Key.Print":       ("PyQt6.QtCore", "Qt.Key.Key_Print"),
    "Base.Protocol.Key.Home":        ("PyQt6.QtCore", "Qt.Key.Key_Home"),
    "Base.Protocol.Key.End":         ("PyQt6.QtCore", "Qt.Key.Key_End"),
    "Base.Protocol.Key.Left":        ("PyQt6.QtCore", "Qt.Key.Key_Left"),
    "Base.Protocol.Key.Up":          ("PyQt6.QtCore", "Qt.Key.Key_Up"),
    "Base.Protocol.Key.Right":       ("PyQt6.QtCore", "Qt.Key.Key_Right"),
    "Base.Protocol.Key.Down":        ("PyQt6.QtCore", "Qt.Key.Key_Down"),
    "Base.Protocol.Key.PageUp":      ("PyQt6.QtCore", "Qt.Key.Key_PageUp"),
    "Base.Protocol.Key.PageDown":    ("PyQt6.QtCore", "Qt.Key.Key_PageDown"),
    "Base.Protocol.Key.Space":       ("PyQt6.QtCore", "Qt.Key.Key_Space"),
    # ═══════════════════════════════════════════════════════════════════════
    # 10. BRIDGE — Зовнішні бібліотеки
    # ═══════════════════════════════════════════════════════════════════════
    "Bridge.AI": (dict, None),
    # Providers / SDK / CLI / IDE / Runtime / Model Formats
    "Bridge.AI.Provider.OpenAI":               ("openai", None),
    "Bridge.AI.Provider.Anthropic":            ("anthropic", None),
    "Bridge.AI.Provider.Gemini":               ("google.genai", None),
    "Bridge.AI.Provider.Groq":                 ("groq", None),
    "Bridge.AI.Provider.Mistral":              ("mistralai.client", "Mistral"),
    "Bridge.AI.Provider.OpenRouter":           ("openrouter", None),
    "Bridge.AI.Provider.OpenCode":             ("opencode", None),
    "Bridge.AI.Provider.HuggingFace":          ("huggingface_hub", None),
    "Bridge.AI.Provider.Replicate":            ("replicate", None),
    "Bridge.AI.Provider.Together":             ("together", None),
    "Bridge.AI.Provider.Fireworks":            ("fireworks", None),
    "Bridge.AI.Provider.Cerebras":             ("cerebras", None),
    "Bridge.AI.Provider.Azure":                ("openai", "AzureOpenAI"),
    "Bridge.AI.Provider.Cloudflare":           ("cloudflare", None),
    "Bridge.AI.Provider.QVAC":                 ("tetherto.qvac_sdk", None),
    # ---------------------------------------------------------------------------
    # RUNTIME
    # ---------------------------------------------------------------------------
    "Bridge.AI.Runtime.QVAC":                  ("tetherto.qvac_sdk", "Client"),
    "Bridge.AI.Runtime.Ollama":                ("ollama", None),
    "Bridge.AI.Runtime.LlamaCPP":              ("llama_cpp", None),
    "Bridge.AI.Runtime.VLLM":                  ("vllm", None),
    "Bridge.AI.Runtime.LMStudio":              ("openai", None),
    "Bridge.AI.Runtime.TensorRTLLM":           ("tensorrt_llm", None),
    "Bridge.AI.Runtime.OpenVINO":              ("openvino", None),
    "Bridge.AI.Runtime.MLX":                   ("mlx", None),
    "Bridge.AI.Runtime.ExLlama":               ("exllama", None),
    "Bridge.AI.Runtime.ExLlamaV2":             ("exllamav2", None),
    "Bridge.AI.Runtime.SGLang": ("sglang", None),
    "Bridge.AI.Runtime.KTransformers": ("ktransformers", None),
    # ---------------------------------------------------------------------------
    # MODELS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Model":                         (None, None),
    "Bridge.AI.Model.Transformers":            ("transformers", None),
    "Bridge.AI.Model.Diffusers":               ("diffusers", None),
    "Bridge.AI.Model.PEFT":                    ("peft", None),
    "Bridge.AI.Model.TRL":                     ("trl", None),
    "Bridge.AI.Model.Optimum":                 ("optimum", None),
    "Bridge.AI.Model.AutoGPTQ":                ("auto_gptq", None),
    "Bridge.AI.Model.AutoAWQ":                 ("awq", None),
    # ---------------------------------------------------------------------------
    # TOKENIZERS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Tokenizer":                     ("tokenizers", None),
    "Bridge.AI.Tokenizer.SentencePiece":       ("sentencepiece", None),
    # ---------------------------------------------------------------------------
    # FORMATS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Format":                        (None, None),
    "Bridge.AI.Format.GGUF":                   ("gguf", None),
    "Bridge.AI.Format.GGML":                   ("ggml", None),
    "Bridge.AI.Format.SafeTensors":            ("safetensors", None),
    "Bridge.AI.Format.ONNX":                   ("onnx", None),
    "Bridge.AI.Format.TorchScript":            ("torch", "jit"),
    # ---------------------------------------------------------------------------
    # QUANTIZATION
    # ---------------------------------------------------------------------------
    "Bridge.AI.Quantization":                  (None, None),
    "Bridge.AI.Quantization.BitsAndBytes":     ("bitsandbytes", None),
    "Bridge.AI.Quantization.AutoGPTQ":         ("auto_gptq", None),
    "Bridge.AI.Quantization.AutoAWQ":          ("awq", None),
    "Bridge.AI.Quantization.GGUF":             ("gguf", None),
    "Bridge.AI.Quantization.GGML":             ("ggml", None),
    # ---------------------------------------------------------------------------
    # AGENTS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Agent":                          (None, None),
    "Bridge.AI.Agent.Agno":                     ("agno", None),
    "Bridge.AI.Agent.CrewAI":                   ("crewai", None),
    "Bridge.AI.Agent.AutoGen":                  ("autogen", None),
    "Bridge.AI.Agent.LangGraph":                ("langgraph", None),
    "Bridge.AI.Agent.LangChain":                ("langchain", None),
    "Bridge.AI.Agent.LlamaIndex":               ("llama_index", None),
    "Bridge.AI.Agent.PydanticAI":               ("pydantic_ai", None),
    "Bridge.AI.Agent.SemanticKernel":           ("semantic_kernel", None),
    # ---------------------------------------------------------------------------
    # EMBEDDINGS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Embedding":                      (None, None),
    "Bridge.AI.Embedding.SentenceTransformers": ("sentence_transformers", None),
    "Bridge.AI.Embedding.FlagEmbedding":        ("FlagEmbedding", None),
    "Bridge.AI.Embedding.FastEmbed":            ("fastembed", None),
    # ---------------------------------------------------------------------------
    # RERANKERS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Reranker":                       (None, None),
    "Bridge.AI.Reranker.FlagEmbedding":         ("FlagEmbedding", None),
    "Bridge.AI.Reranker.ColBERT":               ("colbert", None),
    # ---------------------------------------------------------------------------
    # VECTOR DATABASES
    # ---------------------------------------------------------------------------
    "Bridge.AI.VectorDatabase":                 (None, None),
    "Bridge.AI.VectorDatabase.FAISS":           ("faiss", None),
    "Bridge.AI.VectorDatabase.Chroma":          ("chromadb", None),
    "Bridge.AI.VectorDatabase.Qdrant":          ("qdrant_client", None),
    "Bridge.AI.VectorDatabase.Milvus":          ("pymilvus", None),
    "Bridge.AI.VectorDatabase.Weaviate":        ("weaviate", None),
    # ---------------------------------------------------------------------------
    # RAG
    # ---------------------------------------------------------------------------
    "Bridge.AI.RAG":                            (None, None),
    "Bridge.AI.RAG.LlamaIndex":                 ("llama_index", None),
    "Bridge.AI.RAG.LangChain":                  ("langchain", None),
    # ---------------------------------------------------------------------------
    # TOOLS
    # ---------------------------------------------------------------------------
    "Bridge.AI.Tool":                           (None, None),
    "Bridge.AI.Tool.MCP":                       ("mcp", None),
    "Bridge.AI.Tool.FastMCP":                   ("fastmcp", None),

    # ---------------------------------------------------------------------------
    # VISION
    # ---------------------------------------------------------------------------
    "Bridge.AI.Vision":                         (None, None),
    "Bridge.AI.Vision.OpenCV":                  ("cv2", None),
    "Bridge.AI.Vision.SAM":                     ("segment_anything", None),
    "Bridge.AI.Vision.YOLO":                    ("ultralytics", None),
    # ---------------------------------------------------------------------------
    # SPEECH
    # ---------------------------------------------------------------------------
    "Bridge.AI.Speech":                         (None, None),
    "Bridge.AI.Speech.Whisper":                 ("whisper", None),
    "Bridge.AI.Speech.FasterWhisper":           ("faster_whisper", None),
    "Bridge.AI.Speech.CoquiTTS":                ("TTS", None),
    # ---------------------------------------------------------------------------
    # EVALUATION
    # ---------------------------------------------------------------------------
    "Bridge.AI.Evaluation":                     (None, None),
    "Bridge.AI.Evaluation.Deepeval":            ("deepeval", None),
    "Bridge.AI.Evaluation.Ragas":               ("ragas", None),
    # ---------------------------------------------------------------------------
    # TRAINING
    # ---------------------------------------------------------------------------
    "Bridge.AI.Training":                       (None, None),

    "Bridge.AI.Training.Accelerate":            ("accelerate", None),
    "Bridge.AI.Training.DeepSpeed":             ("deepspeed", None),
    "Bridge.AI.Training.Lightning":             ("lightning", None),
    # ---------------------------------------------------------------------------
    # SDK
    # ---------------------------------------------------------------------------
    "Bridge.SDK":                           (None, None),
    "Bridge.SDK.OpenAI":                    ("openai", None),
    "Bridge.SDK.Anthropic":                 ("anthropic", None),
    "Bridge.SDK.GoogleGenAI":               ("google.genai", None),
    "Bridge.SDK.Cohere":                    ("cohere", None),
    "Bridge.SDK.Groq":                      ("groq", None),
    "Bridge.SDK.MistralAI":                 ("mistralai", None),
    "Bridge.SDK.Ollama":                    ("ollama", None),
    "Bridge.SDK.LiteLLM":                   ("litellm", None),
    "Bridge.SDK.Instructor":                ("instructor", None),
    # ---------------------------------------------------------------------------
    # CLI
    # ---------------------------------------------------------------------------
    "Bridge.CLI":                           (None, None),
    "Bridge.CLI.Codex":                     ("codex", None),
    "Bridge.CLI.ClaudeCode":                ("claude-code", None),
    "Bridge.CLI.Gemini":                    ("gemini", None),
    "Bridge.CLI.Qwen":                      ("qwen", None),
    "Bridge.CLI.Ollama":                    ("ollama", None),
    "Bridge.CLI.Aider":                     ("aider", None),
    "Bridge.CLI.Warp":                      ("warp", None),
    # ---------------------------------------------------------------------------
    # IDE
    # ---------------------------------------------------------------------------
    "Bridge.IDE":                           (None, None),
    "Bridge.IDE.Cursor":                    ("cursor", None),
    "Bridge.IDE.Windsurf":                  ("windsurf", None),
    "Bridge.IDE.Copilot":                   ("github_copilot", None),
    "Bridge.IDE.CodeGPT":                   ("codegpt", None),
    # ════════════════════════════════════════════════════════════════════════════
# 3. ЗОВНІШНІЙ МІСТ, ІЗОЛІНІЙНІ НОСІЇ ТА НАУКОВІ ЛАБОРАТОРІЇ (Bridge.*)
# ОПИС: Шлюз до зовнішніх форматів (JSON, YAML, SQLite, ZIP),
#       міжзоряних баз даних, наукових інструментів (Geant4) та ШІ.
# ════════════════════════════════════════════════════════════════════════════
# ────────────────────────────────────────────────────────────────────────────
# 3.1 ІЗОЛІНІЙНІ НОСІЇ ТА ФОРМАТИ // ISOLINEAR CARRIERS (Bridge.Storage.*)
# Фізичні чіпи ізолінійної пам'яті, серіалізація та пакування даних
# ────────────────────────────────────────────────────────────────────────────
    "Bridge.Storage":                  (dict, None),

    # Embedded
    "Bridge.Storage.Sqlite":           ("sqlite3", None),
    "Bridge.Storage.TinyDB":           ("tinydb", None),
    "Bridge.Storage.LMDB":             ("lmdb", None),

    # Serialization
    "Bridge.Storage.Pickle":           ("pickle", None),
    "Bridge.Storage.Dill":             ("dill", None),
    "Bridge.Storage.Joblib":           ("joblib", None),

    # Structured
    "Bridge.Storage.Json":             ("json", None),
    "Bridge.Storage.Msgpack":          ("msgpack", None),
    "Bridge.Storage.Protobuf":         ("google.protobuf", None),

    # Configuration
    "Bridge.Storage.YAML":             ("yaml", None),
    "Bridge.Storage.TOML":             ("toml", None),

    # Scientific
    "Bridge.Storage.Arrow":            ("pyarrow", None),
    "Bridge.Storage.PyArrow":          ("pyarrow", None),
    "Bridge.Storage.H5Py":             ("h5py", None),
    "Bridge.Storage.NetCDF4":          ("netCDF4", None),
    "Bridge.Storage.Zarr":             ("zarr", None),

    # Compression
    "Bridge.Storage.Zip":              ("zipfile", "ZipFile"),
    "Bridge.Storage.ZipFile":          ("zipfile", "ZipFile"),
    "Bridge.Storage.ZStandard":        ("zstandard", None),
    "Bridge.Storage.LZ4":              ("lz4", None),
    "Bridge.Storage.Snappy":           ("snappy", None),
    "Bridge.Storage.Brotli":           ("brotli", None),

    # Structured Documents (XML)
    "Bridge.Storage.XML":              ("xml.etree.ElementTree", None),
    "Bridge.Storage.XML.Parse":        ("xml.etree.ElementTree", "parse"),
    "Bridge.Storage.XML.FromString":   ("xml.etree.ElementTree", "fromstring"),
    "Bridge.Storage.XML.ToString":     ("xml.etree.ElementTree", "tostring"),
    "Bridge.Storage.XML.Element":      ("xml.etree.ElementTree", "Element"),
    "Bridge.Storage.XML.SubElement":   ("xml.etree.ElementTree", "SubElement"),
    "Bridge.Storage.XML.Tree":         ("xml.etree.ElementTree", "ElementTree"),

    # Tabular Data (CSV)
    "Bridge.Storage.CSV":              ("csv", None),
    "Bridge.Storage.CSV.Reader":       ("csv", "reader"),
    "Bridge.Storage.CSV.Writer":       ("csv", "writer"),
    "Bridge.Storage.CSV.DictReader":   ("csv", "DictReader"),
    "Bridge.Storage.CSV.DictWriter":   ("csv", "DictWriter"),

    # INI Configuration Formats
    "Bridge.Storage.INI":              ("configparser", None),
    "Bridge.Storage.Config":           ("configparser", "ConfigParser"),
    "Bridge.Storage.INI.Parser":       ("configparser", "ConfigParser"),

    # Media & Format Detection
    "Bridge.Storage.MIME":             ("mimetypes", None),
    "Bridge.Storage.MIME.Guess":       ("mimetypes", "guess_type"),
    "Bridge.Storage.MIME.Extension":   ("mimetypes", "guess_extension"),

    # Archives & Compression
    "Bridge.Storage.Tar":              ("tarfile", None),
    "Bridge.Storage.GZip":             ("gzip", None),
    "Bridge.Storage.BZ2":              ("bz2", None),
    "Bridge.Storage.LZMA":             ("lzma", None),
        
    # ────────────────────────────────────────────────────────────────────────────
    # 3.2 БАЗИ ДАНИХ ТА ЗОВНІШНІ СХОВИЩА // DATABASE BRIDGES (Bridge.Database.*)
    # Астрометричні каталоги, бази зоряних карт та реляційні сервери
    # ────────────────────────────────────────────────────────────────────────────
    "Bridge.Database":                  (dict, None),

    # SQL
    "Bridge.Database.SQLite":           ("sqlite3", None),
    "Bridge.Database.SQLAlchemy":       ("sqlalchemy", None),
    "Bridge.Database.Alembic":          ("alembic", None),

    "Bridge.Database.PostgreSQL":       ("psycopg2", None),
    "Bridge.Database.PostgreSQLAsync":  ("asyncpg", None),

    "Bridge.Database.MySQL":            ("pymysql", None),
    "Bridge.Database.MySQLClient":      ("MySQLdb", None),

    "Bridge.Database.Oracle":           ("oracledb", None),

    "Bridge.Database.MSSQL":            ("pyodbc", None),

    # NoSQL
    "Bridge.Database.MongoDB":          ("pymongo", None),
    "Bridge.Database.MongoMotor":       ("motor", None),

    "Bridge.Database.Redis":            ("redis", None),

    "Bridge.Database.Cassandra":        ("cassandra", None),

    "Bridge.Database.Neo4j":            ("neo4j", None),

    "Bridge.Database.Elasticsearch":    ("elasticsearch", None),

    "Bridge.Database.OpenSearch":       ("opensearchpy", None),

    "Bridge.Database.Supabase":         ("supabase", None),

    # Streaming
    "Bridge.Database.Kafka":            ("kafka", None),
    "Bridge.Database.ConfluentKafka":   ("confluent_kafka", None),

    # Time Series
    "Bridge.Database.InfluxDB":         ("influxdb", None),

    # ORM
    "Bridge.Database.Peewee":           ("peewee", None),
    "Bridge.Database.SQLModel":         ("sqlmodel", None),

    # Validation
    "Bridge.Database.Pydantic":         ("pydantic", None),
    # ============================================================================
    # Cloud
    # ============================================================================

    "Bridge.Cloud":                       (dict, None),

    # Amazon Web Services
    "Bridge.Cloud.AWS":                   ("boto3", None),
    "Bridge.Cloud.Botocore":              ("botocore", None),
    "Bridge.Cloud.S3":                    ("boto3.s3", None),
    "Bridge.Cloud.DynamoDB":              ("boto3.dynamodb", None),
    "Bridge.Cloud.Lambda":                ("boto3.lambda", None),

    # Microsoft Azure
    "Bridge.Cloud.Azure":                 ("azure", None),
    "Bridge.Cloud.AzureStorage":          ("azure.storage.blob", None),
    "Bridge.Cloud.AzureIdentity":         ("azure.identity", None),
    "Bridge.Cloud.AzureAI":               ("azure.ai", None),

    # Google Cloud
    "Bridge.Cloud.Google":                ("google.cloud", None),
    "Bridge.Cloud.GoogleStorage":         ("google.cloud.storage", None),
    "Bridge.Cloud.BigQuery":              ("google.cloud.bigquery", None),
    "Bridge.Cloud.VertexAI":              ("google.cloud.aiplatform", None),
    "Bridge.Cloud.Firestore":             ("google.cloud.firestore", None),
    "Bridge.Cloud.PubSub":                ("google.cloud.pubsub", None),

    # Firebase
    "Bridge.Cloud.Firebase":              ("firebase_admin", None),

    # Cloudflare
    "Bridge.Cloud.Cloudflare":            ("cloudflare", None),

    # Supabase
    "Bridge.Cloud.Supabase":              ("supabase", None),

    # MinIO
    "Bridge.Cloud.MinIO":                 ("minio", None),

    # Oracle Cloud
    "Bridge.Cloud.OCI":                   ("oci", None),

    # DigitalOcean
    "Bridge.Cloud.DigitalOcean":          ("digitalocean", None),

    # OpenStack
    "Bridge.Cloud.OpenStack":             ("openstack", None),

    # Kubernetes
    "Bridge.Cloud.Kubernetes":            ("kubernetes", None),

    # Docker
    "Bridge.Cloud.Docker":                ("docker", None),

    # Infrastructure
    "Bridge.Cloud.Terraform":             ("python_terraform", None),
    "Bridge.Cloud.Pulumi":                ("pulumi", None),
    "Bridge.Cloud.Ansible":               ("ansible", None),

    # CDN
    "Bridge.Cloud.Fastly":                ("fastly", None),

    # Monitoring
    "Bridge.Cloud.Prometheus":            ("prometheus_client", None),
    "Bridge.Cloud.Grafana":               ("grafana_api", None),

    # Error Tracking
    "Bridge.Cloud.Sentry":                ("sentry_sdk", None),

    # Analytics
    "Bridge.Cloud.Datadog":               ("datadog", None),
    "Bridge.Cloud.NewRelic":              ("newrelic", None),
    # ============================================================================
    # NET Network
    # ============================================================================
    "Bridge.Network":                    (dict, None),

    # HTTP
    "Bridge.Network.Requests":           ("requests", None),
    "Bridge.Network.HTTPX":              ("httpx", None),
    "Bridge.Network.AioHTTP":            ("aiohttp", None),
    "Bridge.Network.Urllib3":            ("urllib3", None),

    # REST
    "Bridge.Network.FastAPI":            ("fastapi", None),
    "Bridge.Network.Starlette":          ("starlette", None),
    "Bridge.Network.Flask":              ("flask", None),
    "Bridge.Network.Django":             ("django", None),
    "Bridge.Network.Sanic":              ("sanic", None),
    "Bridge.Network.Tornado":            ("tornado", None),

    # ASGI / WSGI
    "Bridge.Network.Uvicorn":            ("uvicorn", None),
    "Bridge.Network.Gunicorn":           ("gunicorn", None),
    "Bridge.Network.Hypercorn":          ("hypercorn", None),

    # WebSocket
    "Bridge.Network.WebSocket":          ("websocket", None),
    "Bridge.Network.WebSockets":         ("websockets", None),
    "Bridge.Network.SocketIO":           ("socketio", None),

    # RPC
    "Bridge.Network.GRPC":               ("grpc", None),
    "Bridge.Network.GRPCTools":          ("grpc_tools", None),

    # Messaging
    "Bridge.Network.ZeroMQ":             ("zmq", None),
    "Bridge.Network.Kafka":              ("kafka", None),
    "Bridge.Network.ConfluentKafka":     ("confluent_kafka", None),
    "Bridge.Network.Redis":              ("redis", None),

    # MQTT
    "Bridge.Network.PahoMQTT":           ("paho.mqtt.client", None),

    # AMQP
    "Bridge.Network.RabbitMQ":           ("pika", None),

    # FTP / SSH
    "Bridge.Network.Paramiko":           ("paramiko", None),
    "Bridge.Network.AsyncSSH":           ("asyncssh", None),

    # DNS
    "Bridge.Network.Dnspython":          ("dns", None),

    # GraphQL
    "Bridge.Network.GraphQL":            ("graphql", None),
    "Bridge.Network.Graphene":           ("graphene", None),

    # Clients
    "Bridge.Network.SocketClient":       ("socket", None),
    "Bridge.Network.HTTPClient":         ("http.client", None),

    # Proxy
    "Bridge.Network.SOCKS":              ("socks", None),

    # Download
    "Bridge.Network.Wget":               ("wget", None),
    "Bridge.Network.CurlCFFI":           ("curl_cffi", None),
    # ============================================================================
    # Security
    # ============================================================================
    "Bridge.Security":                    (dict, None),

    # Cryptography
    "Bridge.Security.Cryptography":       ("cryptography", None),
    "Bridge.Security.PyNaCl":             ("nacl", None),
    "Bridge.Security.PyOpenSSL":          ("OpenSSL", None),

    # Hash
    "Bridge.Security.Bcrypt":             ("bcrypt", None),
    "Bridge.Security.Argon2":             ("argon2", None),
    "Bridge.Security.Scrypt":             ("scrypt", None),
    "Bridge.Security.Passlib":            ("passlib", None),

    # JWT
    "Bridge.Security.JWT":                ("jwt", None),
    "Bridge.Security.PyJWT":              ("jwt", None),

    # OAuth
    "Bridge.Security.OAuthLib":           ("oauthlib", None),
    "Bridge.Security.RequestsOAuth":      ("requests_oauthlib", None),
    "Bridge.Security.Authlib":            ("authlib", None),

    # SAML
    "Bridge.Security.PySAML2":            ("saml2", None),

    # Certificates
    "Bridge.Security.Certifi":            ("certifi", None),
    "Bridge.Security.ACME":               ("acme", None),

    # TLS / SSL
    "Bridge.Security.SSLyze":             ("sslyze", None),

    # Secrets
    "Bridge.Security.Keyring":            ("keyring", None),

    # Signing
    "Bridge.Security.PGPy":               ("pgpy", None),

    # Scanners
    "Bridge.Security.Bandit":             ("bandit", None),
    "Bridge.Security.Safety":             ("safety", None),
    "Bridge.Security.Semgrep":            ("semgrep", None),

    # Vulnerabilities
    "Bridge.Security.Snyk":               ("snyk", None),

    # Password Policy
    "Bridge.Security.ZXCVBN":             ("zxcvbn", None),

    # Encoding
    "Bridge.Security.Base58":             ("base58", None),
    "Bridge.Security.Base91":             ("base91", None),

    # UUID
    "Bridge.Security.UUID":               ("uuid", None),
    "Bridge.Security.ShortUUID":          ("shortuuid", None),

    # Validation
    "Bridge.Security.Cerberus":           ("cerberus", None),
    # ============================================================================
    # Bridge.Optimization
    # ============================================================================

    "Bridge.Optimization":             (dict, None),

    "Bridge.Optimization.ORTools":     ("ortools", None),
    "Bridge.Optimization.PuLP":        ("pulp", None),
    "Bridge.Optimization.Pyomo":       ("pyomo", None),
    "Bridge.Optimization.CVXPY":       ("cvxpy", None),

    "Bridge.Optimization.Hyperopt":    ("hyperopt", None),
    "Bridge.Optimization.Optuna":      ("optuna", None),
    "Bridge.Optimization.ScikitOptimize": ("skopt", None),
    "Bridge.Optimization.Nevergrad":   ("nevergrad", None),
    "Bridge.Optimization.BayesianOpt": ("bayesian_optimization", None),
    "Bridge.Optimization.Ax":          ("ax", None),
    "Bridge.Optimization.BoTorch":     ("botorch", None),
    # ────────────────────────────────────────────────────────────────────────────
# 3.3 НАУКОВА ЛАБОРАТОРІЯ ТА ОБЧИСЛЕННЯ // SCIENCE LAB (Bridge.Science.*)
# Спектрометрія, тензорні поля, аналітичні обчислення фізичних законів
# ────────────────────────────────────────────────────────────────────────────
    "Bridge.Science":                  (dict, None),

    # Mathematics
    "Bridge.Science.NumPy":            ("numpy", None),
    "Bridge.Science.SciPy":            ("scipy", None),
    "Bridge.Science.SymPy":            ("sympy", None),
    "Bridge.Science.Mpmath":           ("mpmath", None),

    # Data
    "Bridge.Science.Pandas":           ("pandas", None),
    "Bridge.Science.Polars":           ("polars", None),
    "Bridge.Science.Dask":             ("dask", None),
    "Bridge.Science.PyArrow":          ("pyarrow", None),

    # Statistics
    "Bridge.Science.Statsmodels":      ("statsmodels", None),
    "Bridge.Science.Pingouin":         ("pingouin", None),
    "Bridge.Science.PyMC":             ("pymc", None),
    "Bridge.Science.ArViz":            ("arviz", None),

    # Scientific Formats
    "Bridge.Science.H5Py":             ("h5py", None),
    "Bridge.Science.NetCDF4":          ("netCDF4", None),
    "Bridge.Science.H5NetCDF":         ("h5netcdf", None),
    "Bridge.Science.Zarr":             ("zarr", None),
    "Bridge.Science.XArray":           ("xarray", None),
    "Bridge.Science.CFGRIB":           ("cfgrib", None),
    "Bridge.Science.Iris":             ("iris", None),
        
    # ============================================================================
    # Bridge.Analytics
    # ============================================================================
    "Bridge.Analytics":                 (dict, None),

    "Bridge.Analytics.Prophet":         ("prophet", None),
    "Bridge.Analytics.Sktime":          ("sktime", None),
    "Bridge.Analytics.TSFresh":         ("tsfresh", None),
    "Bridge.Analytics.STUMPY":          ("stumpy", None),
    "Bridge.Analytics.MatrixProfile":   ("matrixprofile", None),

    "Bridge.Analytics.MLflow":          ("mlflow", None),
    "Bridge.Analytics.WandB":           ("wandb", None),
    "Bridge.Analytics.TensorBoard":     ("tensorboard", None),

    "Bridge.Analytics.Segment":         ("analytics", None),
    "Bridge.Analytics.Mixpanel":        ("mixpanel", None),
    "Bridge.Analytics.Amplitude":       ("amplitude", None),
    "Bridge.Analytics.PostHog":         ("posthog", None),
    "Bridge.Analytics.RudderStack":     ("rudder_sdk_python", None),

    "Bridge.Analytics.GreatExpectations": ("great_expectations", None),
    # ============================================================================
    # Bridge.Simulation
    # ============================================================================
    "Bridge.Simulation":               (dict, None),

    "Bridge.Simulation.SimPy":         ("simpy", None),
    "Bridge.Simulation.Mesa":          ("mesa", None),
    "Bridge.Simulation.Salabim":       ("salabim", None),
    "Bridge.Simulation.AgentPy":       ("agentpy", None),

    "Bridge.Simulation.OpenMM":        ("openmm", None),
    "Bridge.Simulation.PyBullet":      ("pybullet", None),
    "Bridge.Simulation.Rebound":       ("rebound", None),

    # ============================================================================
    # Bridge.Quantum
    # ============================================================================
    "Bridge.Quantum":                  (dict, None),

    "Bridge.Quantum.Qiskit":           ("qiskit", None),
    "Bridge.Quantum.Cirq":             ("cirq", None),
    "Bridge.Quantum.PennyLane":        ("pennylane", None),
    "Bridge.Quantum.QuTiP":            ("qutip", None),
    "Bridge.Quantum.PyQuil":           ("pyquil", None),
    "Bridge.Quantum.TKET":             ("pytket", None),
    "Bridge.Quantum.Ocean":            ("dwave.system", None),
    # ────────────────────────────────────────────────────────────────────────────
# 3.4 ФІЗИЧНИЙ СИМУЛЯТОР ЧАСТИНОК ТА GEANT4 // HIGH-ENERGY PHYSICS (Bridge.Physics.*)
# Симуляція радіаційних навантажень на корпус та взаємодії матерії з антиматерією
# ────────────────────────────────────────────────────────────────────────────
    "Bridge.Physics":                  (dict, None),

    "Bridge.Physics.Astropy":          ("astropy", None),
    "Bridge.Physics.SunPy":            ("sunpy", None),
    "Bridge.Physics.SpacePy":          ("spacepy", None),
    "Bridge.Physics.Poliastro":        ("poliastro", None),
    "Bridge.Physics.PyKEP":            ("pykep", None),
    "Bridge.Physics.Skyfield":         ("skyfield", None),
    "Bridge.Physics.PyEphem":          ("ephem", None),
    "Bridge.Physics.Pint":             ("pint", None),
    "Bridge.Physics.Unyt":             ("unyt", None),
    # ============================================================================
    # Bridge.Engineering
    # ============================================================================
    "Bridge.Engineering":              (dict, None),

    # Particle Physics
    "Bridge.Engineering.Geant4":       ("geant4_pybind", None),
    "Bridge.Engineering.ROOT":         ("ROOT", None),

    # Nuclear
    "Bridge.Engineering.OpenMC":       ("openmc", None),

    # CAD
    "Bridge.Engineering.FreeCAD":      ("FreeCAD", None),
    "Bridge.Engineering.CadQuery":     ("cadquery", None),
    "Bridge.Engineering.OCC":          ("OCC", None),
    "Bridge.Engineering.Gmsh":         ("gmsh", None),

    # FEM
    "Bridge.Engineering.FEniCS":       ("fenics", None),
    "Bridge.Engineering.SfePy":        ("sfepy", None),
    "Bridge.Engineering.MFEM":         ("mfem", None),
    "Bridge.Engineering.PETSc":        ("petsc4py", None),

    # CFD
    "Bridge.Engineering.OpenFOAM":     ("PyFoam", None),

    # Optimization
    "Bridge.Engineering.NLopt":        ("nlopt", None),

    # Visualization
    "Bridge.Engineering.VTK":          ("vtk", None),
    "Bridge.Engineering.PyVista":      ("pyvista", None),
    # Accelerated Computing & GPU
    "Bridge.Engineering.CuPy":         ("cupy", None),
    "Bridge.Engineering.Numba":        ("numba", None),
    "Bridge.Engineering.PyOpenCL":     ("pyopencl", None),

    # 3D Graphics & Spatial Modeling
    "Bridge.Engineering.ModernGL":     ("moderngl", None),
    "Bridge.Engineering.VisPy":        ("vispy", None),
    "Bridge.Engineering.Open3D":       ("open3d", None),
    "Bridge.Engineering.OpenXR":       ("xr", None),
    "Bridge.Engineering.OpenVR":       ("openvr", None),
    "Bridge.Engineering.OpenUSD":      ("pxr", None),
    "Bridge.Engineering.Trimesh":      ("trimesh", None),

    # Hardware Telemetry Bridge Alias
    "Bridge.Psutil":                   ("psutil", None),
    # ── SHORTCUT ALIASES ────────────────────────────────────────────
    "Bridge.Numpy":                    ("numpy", None),
    "Bridge.Pandas":                   ("pandas", None),
    "Bridge.Matplotlib":               ("matplotlib", None),
}