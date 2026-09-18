# LCARS FRAMEWORK TYPES CORE LCARS OBJECTS (DNA)
# ОПИС: Фундаментальні типи та архітектурні замінники
# ПРИНЦИП: Стала база. Усі типи ініціалізуються через Реєстр
# КЛАСИФІКАЦІЯ: Системні, Геометрія, Visual, Interface, Protocol
# ─────────────────────────────────────────────────────────────────────────────
# ДНК-БУТСТРАП: єдині прямі прив'язки на завантаженні (курка-яйце Реєстру).
# Все інше в ДНК і підкласах — лише через вузли Реєстру.
from .register import registry
from .info import Version, Passport
import builtins
# =====================================================================
# ПРОСТІР ІМЕН LCARS (ЛАНЦЮГОВИЙ МАРШРУТИЗАТОР ТА ОПТИЧНИЙ ПРОВІДНИК)
# =====================================================================
class Namespace(type):
    PatternBuffer: str = ""
    Entity: object = None

    # Побудова ланцюжка та прохід углиб через крапку
    def ResolvePattern(cls, AttributeName: str):
        # Протокольні проби інтерпретатора завжди починаються з підкреслення
        if AttributeName.startswith("_"):
            return None

        ParentPath = getattr(cls, "PatternBuffer", "")
        
        # Канонічні кореневі точки входу в реєстр
        RootMap = {
            "Visual": "Base.Visual",
            "Geometry": "Base.Geometry",
            "Core": "Base.Core",
            "Interface": "Base.Interface",
            "Graphics": "Base.Graphics",
        }

        # Канонічні аліаси сегментів
        SegmentAliases = {
            "RectF": "Rect",
            "PointF": "Point",
            "SizeF": "Size",
            "LineF": "Line",
            "MarginsF": "Margins",
        }

        CleanAttrName = SegmentAliases.get(AttributeName, AttributeName)
        if not ParentPath:
            CurrentPath = RootMap.get(AttributeName, AttributeName)
        else:
            CurrentPath = f"{ParentPath}.{CleanAttrName}"

        # 1. Шукаємо запис у Реєстрі LCARS
        Resolved = LCARS.Retrieve(CurrentPath)

        # Якщо знайдено дійсний клас або функцію — віддаємо напряму
        if Resolved is not None and (callable(Resolved) or isinstance(Resolved, type)):
            return Resolved

        # 2. Якщо в Реєстрі немає окремого запису, але поточна сутність має такий атрибут:
        CurrentEntity = getattr(cls, "Entity", None)
        if Resolved is None and CurrentEntity is not None and hasattr(CurrentEntity, AttributeName):
            Resolved = getattr(CurrentEntity, AttributeName)

        # 3. Перевіряємо, чи продовжується ланцюг далі в реєстрі
        Prefix = f"{CurrentPath}."
        Branch = any(k.startswith(Prefix) for k in LCARS.Registry.keys())

        # Розгалуження триває далі (простір імен — переносій ланцюга)
        if Branch:
            return Namespace(AttributeName, (), {
                "PatternBuffer": CurrentPath,
                "Entity": Resolved,
            })

        if Resolved is not None:
            return Resolved

        return None

    # ═══ ПРОТОКОЛ ВИКЛИКУ: МАТЕРІАЛІЗАЦІЯ ЕКЗЕМПЛЯРА ЧЕРЕЗ ІНІЦІАЛІЗАТОР ═══
    def Construct(cls, *args, **kwargs):
        # Шов інтерпретатора всередині тіла: об'єкт створюється порожнім,
        # дані проходять лише через канонічний ініціалізатор Initialize.
        Instance = super().__call__()
        InitMethod = getattr(Instance, "Initialize", getattr(Instance, "Init", None))
        if callable(InitMethod) and not isinstance(InitMethod, str):
            InitMethod(*args, **kwargs)
        elif kwargs:
            for Key, Value in kwargs.items():
                setattr(Instance, Key, Value)
        return Instance

    # Прив'язка слотів протоколів без назв у коді:
    # імена слотів — дані вузла Реєстру System.Protocol.Card.
    ProtocolNodes = registry.get("System.Protocol.Card", {})
    locals()[ProtocolNodes.get("Call", "Call")] = Construct
    locals()[ProtocolNodes.get("GetAttr", "GetAttr")] = ResolvePattern
# =====================================================================
# LCARS TYPE & ANNOTATION (ЗАМІННИКИ ТИПІВ)
# =====================================================================
# замінники системних типів LCARS
class Type(metaclass=Namespace):
    PatternBuffer = "System.Type"
    NoneType = type(None)
    Class = type
    Any = object
    Mapping = dict
    List = list
    Tuple = tuple
    Set = set
    String = str
    Integer = int
    Float = float
    Boolean = bool
    Bytes = bytes
    Callable = callable
Annotation = Type
# =====================================================================
# ВУЗЛОВІ ФУНКЦІЇ РЕЄСТРУ LCARS (МОДУЛЬНИЙ РІВЕНЬ)
# =====================================================================
# Вузлові функції живуть поза тілом класу: так аналізатори типів не
# сприймають перший параметр як self, а доступ лишається канонічним —
# LCARS.Import / LCARS.Retrieve / LCARS.Expand.
# Замість typing використано замінники LCARS (Type.Any, Type.String).
# Канонічний замінник прямих завантажень — бутстрап усього розгортання.
# Шов інтерпретатора — всередині тіла: завантажувач береться з картки
# Реєстру (дані вузла System.Protocol.Card), хост — модуль builtins.
# Реєстр тут читається як словник напряму: через Retrieve/Expand йти
# не можна — саме це завантаження обслуговує їхнє розгортання.
def Import(ModuleName: str, fromlist=None):
    CleanName = ModuleName.strip() if isinstance(ModuleName, str) else ""
    if not CleanName:
        return None
    SlotName = registry.get("System.Protocol.Card", {}).get("Import", "")
    if not SlotName:
        return None
    BuiltinLoader = getattr(builtins, SlotName)
    if fromlist:
        return BuiltinLoader(CleanName, fromlist=fromlist)
    # Звичайне завантаження: складені шляхи розгортаємо атрибутним ланцюгом
    Mod = BuiltinLoader(CleanName)
    for Segment in CleanName.split(".")[1:]:
        Mod = getattr(Mod, Segment, Mod)
    return Mod
# Базове розгортання кортежу реєстру в живий об'єкт (Expand)
def Expand(Target: Type.Any):
    if not isinstance(Target, tuple):
        return Target
    ModName = Target[0]
    AttrName = Target[1] if len(Target) > 1 else None
    if isinstance(ModName, str):
        Obj = LCARS.Import(ModName)
        if Obj is not None and AttrName:
            for Part in str(AttrName).split("."):
                Obj = getattr(Obj, Part, None)
                if Obj is None:
                    break
            return Obj
        return Obj
    return Target[0]
# Системна функція вилучення вузла LCARS
def Retrieve(Key: str, Default=None):
    if not isinstance(LCARS.Registry, dict) or not Key:
        return Default
    Res = LCARS.Registry.get(Key)
    if Res is None:
        LowerKey = Key.lower() if isinstance(Key, str) else ""
        if LowerKey in LCARS.RegistryKeys:
            RealKey = LCARS.RegistryKeys[LowerKey]
            Res = LCARS.Registry.get(RealKey)
    if Res is None:
        return Default
    # Якщо це кортеж із реєстру — розгортаємо в живий об'єкт
    if isinstance(Res, tuple) and len(Res) == 2 and isinstance(Res[0], str):
        return LCARS.Expand(Res)
    return Res
# Розгортання запису реєстру в живий об'єкт за ключем (Materialize)
def Materialize(Key: str, Default=None):
    Entry = LCARS.Retrieve(Key)
    if Entry is not None:
        return Entry
    return Default
# Системний заповнювач-константа (канонічний маркер LCARS або вузол реєстру)
def Constant(Name: str, Default=None):
    if not Name:
        return Default
    return LCARS.Retrieve(Name, Name)
# Реєстрація нового вузла або системної сутності в системі
def Register(Key: str, Value: Type.Any, Attribute: Type.Any = None):
    if isinstance(Value, tuple):
        Entry = (Value[0], Value[1] if len(Value) > 1 else None)
    else:
        Entry = (Value, Attribute)
    LCARS.Registry[Key] = Entry
    LCARS.RegistryKeys[Key.lower()] = Key
    return Value
# Вилучення (дереєстрація) запису за ключем
def Deregister(Key: str):
    LCARS.Registry.pop(Key, None)
    LCARS.RegistryKeys.pop(Key.lower(), None)
    return LCARS
# Список зареєстрованих ключів або їхня кількість
def Catalog(Count: bool = False):
    if Count:
        return len(LCARS.Registry)
    return list(LCARS.Registry.keys())
# =====================================================================
# LCARS CLASS - ГОЛОВНИЙ КЛАС ТА ЄДИНА ТОЧКА ВХОДУ LCARS
# =====================================================================
class LCARS(metaclass=Namespace):
    # Паспортні дані та специфікація системи
    Name = "Library Computer Access/Retrieval System"
    Title = Version.Title
    Status = "Operational"
    Annotation = Annotation
    # Типи та анотації
    Typing = Type
    Passport = Passport
    Specification = Version.Specification
    Architecture = Version.Architecture
    Design = Version.Design
    Platform = Version.Platform
    Stardate = Version.Stardate
    EarthDate = Version.EarthDate
    Metadata = Version.Metadata
    Version = Version.Release

    # Канонічний ініціалізатор системного вузла LCARS
    def Initialize(self, SystemId=None, Id=None, Parent=None, **kwargs):
        self.SystemId = SystemId or Id or getattr(self, "SystemId", None) or f"Sys{id(self)}"
        self.Id = self.SystemId
        self.Parent = Parent
        self.Config = dict(getattr(self, "Config", {}))
        for Key, Value in kwargs.items():
            setattr(self, Key, Value)
        return self
    # Канонічний замінник конструктора
    Init = Initialize
    Registry = registry
    Keys = {k.lower(): k for k in registry.keys()} if isinstance(registry, dict) else {}
    # Канонічний синонім індексу (його читають Retrieve / Register)
    RegistryKeys = Keys
    # Службовий метод первинної індексації реєстру (викликається автоматично)
    def IndexRegistry(self, cls):
        if isinstance(cls.Registry, dict) and not cls.Keys:
            Index = {k.lower(): k for k in cls.Registry.keys()}
            cls.Keys = Index
            cls.RegistryKeys = Index
        return cls.Registry
    # -----------------------------------------------------------------
    # СИСТЕМНІ ІНСТРУМЕНТИ КЕРУВАННЯ РЕЄСТРОМ
    # Реалізація вузлових функцій — на рівні модуля (блок вище класу),
    # канонічна прив'язка до кореня — одразу після оголошення класу.
    # -----------------------------------------------------------------
    # Системний ідентифікатор вузла
    def Identifier(self) -> str:
        return str(getattr(self, "Id", id(self)))
    # Повний дескриптор сутності
    def Descriptor(self) -> dict:
        return {
            "id": getattr(self, "Id", None),
            "system": getattr(self, "SystemId", None),
            "status": getattr(self, "Status", "Operational"),
        }

    # Отримання канонічного екземпляра додатку через ядро
    def Launch(EntryPoint: Type.Any, *Args, **Flags) -> Type.Any:
        # 1. СПЕРШУ створюємо / отримуємо головний додаток (QApplication)
        AppClass = LCARS.Retrieve("Base.Interface.Application")
        App = AppClass.instance() if AppClass and hasattr(AppClass, "instance") else None
        if App is None and AppClass and callable(AppClass):
            App = AppClass([])

        # Якщо викликано як метод класу LCARS.Launch(EntryPoint)
        TargetEntryPoint = EntryPoint
        if TargetEntryPoint is LCARS and Args:
            TargetEntryPoint = Args[0]
            Args = Args[1:]

        # 2. ТІЛЬКИ ТЕПЕР викликаємо інтерфейс — тепер створення QWidget дозволено!
        Instance = TargetEntryPoint(*Args, **Flags) if callable(TargetEntryPoint) else TargetEntryPoint

        if hasattr(Instance, "Show"):
            Instance.Show()
        elif hasattr(Instance, "show"):
            Instance.show()

        # 3. Запускаємо головний цикл подій
        if App and hasattr(App, "exec"):
            return App.exec()
        return Instance

    # === СИСТЕМНІ ЗМАГАЛЬНІ ТА ДАНДЕР-ЗАМІННИКИ (BUILTINS & OPERATORS) ===
    # Шляхові канонії зібрано у вкладені контейнери, щоб не перекривати
    # справжні атрибути класу (Init, Name, Import, Directory тощо).
    StaticMethod = "System.Method.Static"
    ClassMethod = "System.Method.Class"
    MethodProperty = "System.Method.Property"

    # Аліас ініціалізатора визначено вище (Init = Initialize):
    # шляховий вузол System.Protocol.Init не перекриває канонічний метод.
    All = "System.Protocol.All"
    Directory = "System.Protocol.Directory"
    Doc = "System.Protocol.Doc"
    File = "System.Protocol.File"
    Annotations = "System.Protocol.Annotations"
    Call = "System.Protocol.Call"
    Enter = "System.Protocol.Enter"
    Exit = "System.Protocol.Exit"
    GetAttr = "System.Protocol.GetAttr"
    SetAttr = "System.Protocol.SetAttr"
    DelAttr = "System.Protocol.DelAttr"

    Equal = "System.Operator.Equal"
    NotEqual = "System.Operator.NotEqual"
    LessThan = "System.Operator.LessThan"
    GreaterThan = "System.Operator.GreaterThan"
    Contains = "System.Operator.Contains"
    GetItem = "System.Operator.GetItem"
    SetItem = "System.Operator.SetItem"
    DelItem = "System.Operator.DelItem"

    # === СИСТЕМНІ КОРЕНІ (ОПЕРАЦІЙНА СИСТЕМА) ===
    ABC = "System.ABC"
    Regex = "System.Regex"
    Math = "System.Math"
    Random = "System.Random"
    Integer = "System.Random.Integer"
    Choice = "System.Random.Choice"
    Float = "System.Random.Float"
    Range = "System.Random.Range"
    Time = "System.Time"
    Copy = "System.Copy"
    String = "System.String"
    Method = "System.AbstractMethod"
    Environment = "System.Environment"
    DataClass = "System.DataClass"
    Field = "System.DataClass.Field"
    Threading = "System.Threading"
    DateTime = "System.DateTime"
    Attribute = "System.Attribute"
    Module = "System.Module"
    Util = "System.Module.Util"
    Loader = "System.Module.Loader"
    Deepcopy = "System.Copy.Deep"
    Directory = "System.Directory"
    Process = "System.Process"
    Task = "System.Task"
    Memory = "System.Memory"
    Resource = "System.Resource"
    Security = "System.Security"
    Network = "System.Network"
    Context = "System.Context"
    Collection = "System.Collection"
    Iterator = "System.Iterator"
    Function = "System.Function"
    Traceback = "System.Traceback"
    Temporary = "System.Temporary"
    Uuid = "System.Identifier.UUID"
    URL = "System.URL"
    
    # === ПЛАТФОРМА ===
    Release = "System.Platform.Release"
    Machine = "System.Platform.Machine"
    Processor = "System.Platform.Processor"
    Architecture = "System.Platform.Architecture"
    Node = "System.Platform.Node"
    Compiler = "System.Platform.Compiler"
    Build = "System.Platform.Build"
    
    # === SIGNALS / SLOTS / PROPERTIES ===
    Object = "Base.Core.Object"
    Signal = "Base.Core.Signal"
    Slot = "Base.Core.Slot"
    Property = "Base.Core.Property"
    
    # === THREADS / TIMERS ===
    Application = "Base.Interface.Application"
    Thread = "Base.Core.Thread"
    Clock = "Base.Core.Timer"
    Chronometer = "Base.Core.Timer"
    Pulser = "Base.Core.Timer"
    Mutex = "Base.Core.Sync.Mutex"
    Semaphore = "Base.Core.Sync.Semaphore"
    WaitCondition = "Base.Core.Sync.Wait"
    
    # === FILE SYSTEM ===
    File = "Base.Core.File"
    Dir = "Base.Core.Directory"
    Url = "Base.Core.Data.Url"
    Uuid = "Base.Core.Data.Uuid"
    
    # === MEMORY ===
    Memory = "Base.Core.Memory"
    
    # === SETTINGS ===
    Settings = "Base.Core.Settings"
    
    # === LOCALE ===
    Locale = "Base.Core.Locale"
    # === DATA STRUCTURES ===
    ByteArray = "Base.Core.Data.ByteArray"
    MimeData = "Base.Core.Data.Mime"
    # === EVENTS / TIME ===
    Event = "Base.Core.Event"
    Date = "Base.Core.Time.Date"
    DateTime = "Base.Core.Time.DateTime"
    Time = "Base.Core.Time.Clock"
    
    # === GEOMETRY - Базові фігури (Вікна: Int, Векторне малювання: Float) ===
    Point = "Base.Geometry.Point.Int"      # QPoint
    PointF = "Base.Geometry.Point"         # QPointF
    Size = "Base.Geometry.Size.Int"        # QSize
    SizeF = "Base.Geometry.Size"           # QSizeF
    Rect = "Base.Geometry.Rect.Int"        # QRect
    RectF = "Base.Geometry.Rect"           # QRectF
    Line = "Base.Geometry.Line.Int"        # QLine
    LineF = "Base.Geometry.Line"           # QLineF
    Margins = "Base.Geometry.Margins.Int"  # QMargins
    MarginsF = "Base.Geometry.Margins"     # QMarginsF
    Easing = "Base.Geometry.Easing"        # QEasingCurve
    # === VISUAL - Векторна оптика та рендеринг ===
    Painter = "Base.Visual.Painter"        # QPainter
    PainterPath = "Base.Visual.PainterPath"# QPainterPath (головний контур!)
    Pen = "Base.Visual.Pen"                # QPen
    Brush = "Base.Visual.Brush"            # QBrush
    Color = "Base.Visual.Color"            # QColor
    Palette = "Base.Visual.Palette"        # QPalette
    Font = "Base.Visual.Font"              # QFont
    FontDatabase = "Base.Visual.FontDatabase"
    Pixmap = "Base.Visual.Pixmap"          # QPixmap
    Image = "Base.Visual.Image"            # QImage
    Bitmap = "Base.Visual.Bitmap"          # QBitmap
    Icon = "Base.Visual.Icon"              # QIcon
    Polygon = "Base.Visual.Polygon"        # QPolygon
    PolygonF = "Base.Visual.PolygonF"      # QPolygonF
    Gradient = "Base.Visual.Gradient.Linear" # QLinearGradient
    Transform = "Base.Visual.Transform"    # QTransform
    Region = "Base.Visual.Region"          # QRegion
    # === GRAPHICS SCENE & TACTICAL GRID ===
    Scene = "Base.Graphics.Scene"          # QGraphicsScene
    View = "Base.Graphics.View"            # QGraphicsView
    Item = "Base.Graphics.Item"            # QGraphicsItem
    # === TACTICAL ITEMS (Тактичні сутності зорельота) ===
    Course = "Base.Graphics.Line"          # Курс на карті
    Perimeter = "Base.Graphics.Rect"       # Зона / периметр
    Orbit = "Base.Graphics.Ellipse"        # Орбіта
    Trajectory = "Base.Graphics.Path"      # Траєкторія польоту
    Territory = "Base.Graphics.Polygon"    # Сектор / територія
    Designation = "Base.Graphics.Text"     # Бортовий напис
    SimpleText = "Base.Graphics.SimpleText" # Текстовий індикатор
    Sprite = "Base.Graphics.Image"         # Спрайт об'єкта

    # === PHOTONIC & SUBSPACE EFFECTS ===
    Cloak = "Base.Graphics.Effect.Opacity"         # Маскування / прозорість
    Glow = "Base.Graphics.Effect.DropShadow"       # Фотонне світіння

    # === LCARS SURFACE & DISPLAY TOPOLOGY ===
    Viewport = "Base.Interface.Viewport"
    Display = "Base.Interface.Widget"
    Scroll = "Base.Interface.Scroll"
    Tab = "Base.Interface.Tab"
    Stacked = "Base.Interface.Stack"
    Divider = "Base.Interface.Splitter"
    
    # === INTERACTIVE ELEMENTS ===
    Input = "Base.Interface.LineEdit"
    TextBox = "Base.Interface.TextEdit"
    Selector = "Base.Interface.Combo"
    Regulator = "Base.Interface.Slider"
    TextEdit = "Base.Interface.TextEdit"
    PlainText = "Base.Interface.PlainText"
    LineEdit = "Base.Interface.LineEdit"
    
    # === LAYOUTS ===
    Layout = "Base.Interface.Layout"
    Vertical = "Base.Interface.Layout.Vertical"
    Horizontal = "Base.Interface.Layout.Horizontal"
    Grid = "Base.Interface.Layout.Grid"
    GridLayout = "Base.Interface.Layout.Grid"
    FormLayout = "Base.Interface.Layout.Form"
    StackLayout = "Base.Interface.Layout.Stacked"
    Spacer = "Base.Interface.Layout.Spacer"

    # === PROTOCOL ENUMS ===
    AlignCenter = "Base.Protocol.Align.Center"
    AlignLeft = "Base.Protocol.Align.Left"
    AlignRight = "Base.Protocol.Align.Right"
    AlignAbove = "Base.Protocol.Align.Top"
    AlignBottom = "Base.Protocol.Align.Bottom"
    AlignHCenter = "Base.Protocol.Align.HCenter"
    AlignVCenter = "Base.Protocol.Align.VCenter"
    KeyReturn = "Base.Protocol.Key.Return"
    KeyEnter = "Base.Protocol.Key.Enter"
    KeyEscape = "Base.Protocol.Key.Escape"
    KeyBackspace = "Base.Protocol.Key.Backspace"
    KeyTab = "Base.Protocol.Key.Tab"
    KeySpace = "Base.Protocol.Key.Space"
    KeyUp = "Base.Protocol.Key.Up"
    KeyDown = "Base.Protocol.Key.Down"
    KeyLeft = "Base.Protocol.Key.Left"
    KeyRight = "Base.Protocol.Key.Right"
    KeyHome = "Base.Protocol.Key.Home"
    KeyEnd = "Base.Protocol.Key.End"
    KeyPageUp = "Base.Protocol.Key.PageUp"
    KeyPageDown = "Base.Protocol.Key.PageDown"
    Frameless = "Base.Protocol.DisplayFlag.Frameless"
    StayOnTop = "Base.Protocol.DisplayFlag.StayOnTop"
    CursorHand = "Base.Protocol.Cursor.Pointing"
    CursorWait = "Base.Protocol.Cursor.Wait"
    CursorCross = "Base.Protocol.Cursor.Cross"
    CursorIBeam = "Base.Protocol.Cursor.IBeam"
    CursorArrow = "Base.Protocol.Cursor.Arrow"
    CursorSizeAll = "Base.Protocol.Cursor.SizeAll"
    CursorForbidden = "Base.Protocol.Cursor.Forbidden"
    CursorBusy = "Base.Protocol.Cursor.Busy"
    CursorPointing = "Base.Protocol.Cursor.Pointing"
    ScrollAlwaysOff = "Base.Protocol.Scroll.AlwaysOff"
    Translucent = "Base.Protocol.Widget.Transparent"
    TextCursor = "Base.Visual.Text.Cursor"
    
    # === СТОРОННІ ТА ФАЙЛОВІ БІБЛІОТЕКИ (МІСТ / BRIDGE) ===
    Serialization = "Bridge.Storage.Json"
    Pickle = "Bridge.Storage.Pickle"
    Toml = "Bridge.Storage.Toml"
    Arrow = "Bridge.Storage.Arrow"
    Tar = "Bridge.Storage.Tar"
    GZip = "Bridge.Storage.GZip"
    # Сумісні аліаси
    JSON = "Bridge.Storage.Json"
    YAML = "Bridge.Storage.Yaml"
    SQL = "Bridge.Storage.Sqlite"
    CSV = "Bridge.Storage.Csv"
    XML = "Bridge.Storage.Xml"
    INI = "Bridge.Storage.Ini"
    MIME = "Bridge.Storage.Mime"
# =====================================================================
# КАНОНІЧНА ПРИВ'ЯЗКА ВУЗЛОВИХ ФУНКЦІЙ РЕСТРУ ДО КОРЕНЯ LCARS
# =====================================================================
# Прив'язка виконується після оголошення класу: тіло класу лишається чистим,
# а доступ до вузлів — канонічний: LCARS.Import / LCARS.Retrieve / LCARS.Expand.
LCARS.Import = Import
LCARS.Expand = Expand
LCARS.Retrieve = Retrieve
LCARS.Materialize = Materialize
LCARS.Register = Register
LCARS.Deregister = Deregister
LCARS.Catalog = Catalog
LCARS.Library = Catalog
LCARS.Constant = Constant
# Обгортка в канонічний замінник static-вузла з реєстру (System.Method.Static):
# жодних декораторів у коді — лише системний вузол реєстру.
StaticNode = LCARS.Materialize(LCARS.StaticMethod)
if StaticNode is not None:
    LCARS.Import = StaticNode(Import)
    LCARS.Expand = StaticNode(Expand)
    LCARS.Retrieve = StaticNode(Retrieve)
    LCARS.Materialize = StaticNode(Materialize)
    LCARS.Register = StaticNode(Register)
    LCARS.Deregister = StaticNode(Deregister)
    CatalogNode = StaticNode(Catalog)
    LCARS.Catalog = CatalogNode
    LCARS.Library = CatalogNode
    LCARS.Constant = StaticNode(Constant)
    LCARS.Launch = StaticNode(LCARS.Launch)
# =====================================================================
# COMPONENT CLASS - Базовий клас для компонентів
class SystemComponent(LCARS):
    TypeName = "LCARSComponent"
    Enabled = True
    Visible = True
    Active = True
    Status = "Stopped"
    Parent = None
    Subsystem = None
    Config = {}

    def AssignModule(self, Module):
        self.Module = Module
        if Module:
            Module.Parent = self
        self.Status = "Running"
        return self

    def Configure(self, Config):
        self.Config.update(Config)
        if self.Module and hasattr(self.Module, "Configure"):
            self.Module.Configure(Config)
        return self

    # Діагностика стану живого компонента
    def Diagnostics(self) -> dict:
        return {
            "id": self.Id,
            "system": self.SystemId,
            "status": self.Status,
            "enabled": self.Enabled,
            "visible": self.Visible,
            "active": self.Active,
            "module": self.Module,
            "config": self.Config.copy(),
        }

    # === LIFECYCLE CONTRACT (DNA) ===
    def Start(self):
        self.Status = "Running"
        return self

    def Stop(self):
        self.Status = "Stopped"
        return self

    def Destroy(self):
        self.Status = "Terminated"
        return self

# =====================================================================
# ABSTRACT MATRIX TYPE
# =====================================================================
class Matrix(SystemComponent):
    TypeName = "LCARSMatrix"
    Nodes = {}
    Domains = {}
    Links = {}
    Layers = {}
    # === MATRIX ABSTRACT CONTRACT ===
    def AddNode(self, Name, Node): pass
    def ReadNode(self, Name): pass
    def RemoveNode(self, Name): pass
    def AddDomain(self, Name, Domain=None): pass
    def RemoveDomain(self, Name): pass
    def AddLayer(self, Name, Layer=None): pass
    def ReadLayer(self, Name): pass
    def RemoveLayer(self, Name): pass
    def LinkNodes(self, Source, Target): pass
    def UnlinkNodes(self, Source, Target): pass
# =====================================================================
# ABSTRACT PROCESS TYPE
# Базовий тип процесу. Описує системний процес незалежно від його реалізації.
class Process(SystemComponent):
    TypeName = "LCARSProcess"
    Command = ""
    Inputs: dict         # Вхідні дані
    Outputs: dict        # Вихідні дані
    Stages: dict         # Іменовані етапи процесу
    Transitions: dict    # Переходи та умови між етапами
    # === PROCESS ABSTRACT CONTRACT ===
    def Validate(self): pass
    def Execute(self, Command=None): pass
    def Reset(self): pass

# Базовий тип директиви.
# Описує системну директиву незалежно від її реалізації.
class Directive(LCARS):
    TypeName = "LCARSDirective"
    Category = None
    Source = None
    Target = None
    Priority = 0
    # === DIRECTIVE ABSTRACT CONTRACT ===
    def Validate(self, Data=None): pass
    def Execute(self, Data=None): pass
    def Cancel(self): pass
    def Reset(self): pass

# Базовий тип протоколу.
# Описує формат, правила та стан протоколу.
class Protocol(LCARS):
    TypeName = "LCARSProtocol"
    Encoding = "UTF-8"
    Format = "Raw"
    Participants: dict    # Учасники взаємодії та їхні ролі
    Scope: dict           # Область застосування протоколу
    Rules: dict           # Правила взаємодії
    Operations: dict      # Допустимі операції
    Messages: dict        # Формати повідомлень і даних
    Phases: dict          # Фази взаємодії
    Transitions: dict     # Допустимі переходи між фазами
    Conditions: dict      # Умови застосування та завершення
    Constraints: dict     # Обмеження взаємодії
    Exceptions: dict      # Виняткові ситуації та правила реагування
    # === PROTOCOL ABSTRACT CONTRACT ===
    def Validate(self, Data=None): pass
    def Encode(self, Data): pass
    def Decode(self, Data): pass
    def Serialize(self, Data): pass
    def Deserialize(self, Data): pass
    def Reset(self): pass

# =====================================================================
# ABSTRACT SESSION TYPE
# =====================================================================
class Session(SystemComponent):
    TypeName = "LCARSSession"
    Token = ""
    Active = True
    User = None
    Participants: dict    # Учасники та їхні ролі
    Protocols: dict       # Застосовані протоколи
    Scope: dict           # Межі взаємодії
    Lifecycle: dict       # Умови відкриття, підтримання та завершення
# =====================================================================
# ЕКСПОРТОВАНИЙ МАНІФЕСТ ТИПІВ LCARS (DNA)
# =====================================================================
LCARS.Types = (
    "LCARS",
    "SystemComponent",
    "Matrix",
    "Directive",
    "Protocol",
    "Process",
    "Program",
    "Session",
    "Type",
    "Annotation",
)
# Аліас експорту модуля для Python імпортів (from lcars.base.type import *)
All = list(LCARS.Types)