# LCARS FRAMEWORK TYPES CORE LCARS OBJECTS (DNA)
# ОПИС: Фундаментальні типи та архітектурні замінники
# ПРИНЦИП: Стала база. Усі типи ініціалізуються через Реєстр
# КЛАСИФІКАЦІЯ: Системні, Геометрія, Visual, Interface, Protocol
# ─────────────────────────────────────────────────────────────────────────────
from .register import registry
from .info import Version, Passport
# =====================================================================
# Простір імен LCARS (будівник ланцюжків та маршрутизація через Реєстр)
class Namespace(type):
    PatternBuffer: str = ""

    # Прямий резолвінг вузла або ланцюжка
    def Pattern(cls, Path: str):
        return registry.Retrieve(Path)

    # LCARS Буфер для побудови ланцюжка
    def ResolvePattern(cls, AttributeName: str):
        if AttributeName.startswith("_"):
            raise AttributeError(AttributeName)

        ParentPath = (
            cls.__dict__["PatternBuffer"] if "PatternBuffer" in cls.__dict__
            else cls.__dict__["NamespacePath"] if "NamespacePath" in cls.__dict__
            else cls.__dict__["Name"] if "Name" in cls.__dict__
            else cls.__name__
        )
        FullPath = f"{ParentPath}.{AttributeName}"

        # 1. Прямий резолвінг через реєстр LCARS
        DirectResolved = registry.Retrieve(FullPath)
        if DirectResolved is not None and not isinstance(DirectResolved, tuple):
            return DirectResolved

        # 2. Створення наступної ланки простору імен
        return Namespace(AttributeName, (), {
            "PatternBuffer": FullPath,
            "NamespacePath": FullPath,
        })

    # Системний аліас Python для підтримки оператора крапки
    __getattr__ = ResolvePattern

# =====================================================================
# LCARS TYPE & ANNOTATION (ТИТАНОВІ ЗАМІННИКИ ТИПІВ)
# =====================================================================
# Титанові замінники системних типів LCARS
class Type(metaclass=Namespace):
    NamespacePath = "System.Type"
    Any = object
    Dict = dict
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
# LCARS CLASS - ГОЛОВНИЙ КЛАС ТА ЄДИНА ТОЧКА ВХОДУ LCARS
# =====================================================================
class LCARS(metaclass=Namespace):
    # Паспортні дані та специфікація системи
    Name = "Library Computer Access/Retrieval System"
    Title = Version.Title
    Status = "Operational"
    Build = Version.Build
    Passport = Passport
    Specification = Version.Specification
    Architecture = Version.Architecture
    Design = Version.Design
    PlatformSpec = Version.Platform
    Stardate = Version.Stardate
    EarthDate = Version.EarthDate
    Metadata = Version.Passport
    Version = Version.Release

    # Титанові типи та анотації
    Type = Type
    Typing = Type
    Annotation = Annotation

    # Канонічні простори імен (генеруються безпосередньо через Namespace)
    System = Namespace("System", (), {"PatternBuffer": "System"})
    Platform = Namespace("Platform", (), {"PatternBuffer": "System.Platform"})

    Core = Namespace("Core", (), {"PatternBuffer": "Base.Core"})
    Geometry = Namespace("Geometry", (), {"PatternBuffer": "Base.Geometry"})
    Visual = Namespace("Visual", (), {"PatternBuffer": "Base.Visual"})
    Interface = Namespace("Interface", (), {"PatternBuffer": "Base.Interface"})
    Protocol = Namespace("Protocol", (), {"PatternBuffer": "Base.Protocol"})
    Bridge = Namespace("Bridge", (), {"PatternBuffer": "Bridge"})
    Storage = Namespace("Storage", (), {"PatternBuffer": "Bridge.Storage"})
    Runtime = Namespace("Runtime", (), {"PatternBuffer": "System.Core"})

    
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

    DataClass = "System.DataClass"
    Field = "System.DataClass.Field"
    Threading = "System.Threading"
    DateTime = "System.DateTime"
    Module = "System.Module"
    ModuleUtil = "System.Module.Util"
    Import = "System.Module.Import"
    ModuleSpec = "System.Module.SpecFromFile"
    ModuleFromSpec = "System.Module.FromSpec"
    ModuleLoader = "System.Module.Loader"
    Deepcopy = "System.Copy.Deep"
    Environment = "System.Environment"
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
    Operator = "System.Operator"
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
    Timer = "Base.Core.Timer"
    Chronometer = "Base.Core.Timer"
    Pulser = "Base.Core.Timer"
    Lock = "Base.Core.Sync.Mutex"
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
    
    # === EVENTS / TIME ===
    Event = "Base.Core.Event"
    Date = "Base.Core.Time.Date"
    DateTime = "Base.Core.Time.DateTime"
    Time = "Base.Core.Time.Clock"
    
    # === GEOMETRY - Базові фігури ===
    Size = "Base.Geometry.Size.Int"
    SizeInt = "Base.Geometry.Size.Int"
    SizeF = "Base.Geometry.Size"
    Rect = "Base.Geometry.Rect.Int"
    RectInt = "Base.Geometry.Rect.Int"
    RectF = "Base.Geometry.Rect"
    PointF = "Base.Geometry.Point"
    Line = "Base.Geometry.Line"
    Margins = "Base.Geometry.Margins"
    
    # === DATA STRUCTURES ===
    ByteArray = "Base.Core.Data.ByteArray"
    MimeData = "Base.Core.Data.Mime"
    
    # === LCARS SURFACE & DISPLAY TOPOLOGY ===
    Display = "Base.Interface.Viewport"
    Screen = "Base.Interface.Viewport"
    Viewport = "Base.Interface.Viewport"
    Widget = "Base.Interface.Widget"
    Buffer = "Base.Interface.Scroll"
    Tab = "Base.Interface.Tab"
    Stacked = "Base.Interface.Stack"
    Divider = "Base.Interface.Splitter"
    Dock = "Base.Interface.Dock"
    Progress = "Base.Interface.ProgressBar"
    Readout = "Base.Interface.LCD"
    
    # === DIALOGS / MENUS ===
    Dialog = "Base.Interface.Dialog"
    Message = "Base.Interface.Dialog.Message"
    FileDialog = "Base.Interface.Dialog.File"
    Menu = "Base.Interface.Menu"
    MenuBar = "Base.Interface.MenuBar"
    ToolBar = "Base.Interface.ToolBar"
    StatusBar = "Base.Interface.StatusBar"
    Command = "Base.Interface.Action"
    Beacon = "Base.Interface.SystemTray"
    Grip = "Base.Interface.SizeGrip"
    Policy = "Base.Interface.SizePolicy"
    Synthesizer = "Base.Interface.Completer"
    
    # === INTERACTIVE ELEMENTS ===
    Button = "Base.Interface.Button"
    Label = "Base.Interface.Label"
    Frame = "Base.Interface.Frame"
    Input = "Base.Interface.LineEdit"
    Console = "Base.Interface.TextEdit"
    Terminal = "Base.Interface.TextEdit"
    TextBox = "Base.Interface.TextEdit"
    Selector = "Base.Interface.Combo"
    Regulator = "Base.Interface.Slider"
    TextEdit = "Base.Interface.TextEdit"
    PlainText = "Base.Interface.PlainText"
    LineEdit = "Base.Interface.LineEdit"
    ToolButton = "Base.Interface.ToolButton"
    Radio = "Base.Interface.Radio"
    CheckBox = "Base.Interface.CheckBox"
    SpinBox = "Base.Interface.SpinBox"
    DoubleSpinBox = "Base.Interface.DoubleSpinBox"
    DateEdit = "Base.Interface.DateEdit"
    TimeEdit = "Base.Interface.TimeEdit"
    DateTimeEdit = "Base.Interface.DateTimeEdit"
    Dial = "Base.Interface.Dial"
    Slider = "Base.Interface.Slider"
    ScrollBar = "Base.Interface.ScrollBar"
    ProgressBar = "Base.Interface.ProgressBar"
    LCD = "Base.Interface.LCD"
    Stack = "Base.Interface.Stack"
    Chamber = "Base.Interface.Stack"
    
    # === LISTS / TABLES ===
    List = "Base.Interface.List"
    ListWidget = "Base.Interface.List"
    Manifest = "Base.Interface.List"
    Record = "Base.Interface.Item.List"
    Hierarchy = "Base.Interface.Tree"
    Table = "Base.Interface.Table"
    Combo = "Base.Interface.Combo"
    Tray = "Base.Interface.SystemTray"
    Complete = "Base.Interface.Completer"
    
    # === LAYOUTS ===
    Layout = "Base.Interface.Layout"
    Vertical = "Base.Interface.Layout.Vertical"
    Horizontal = "Base.Interface.Layout.Horizontal"
    Grid = "Base.Interface.Layout.Grid"
    GridLayout = "Base.Interface.Layout.Grid"
    Form = "Base.Interface.Layout.Form"
    FormLayout = "Base.Interface.Layout.Form"
    StackLayout = "Base.Interface.Layout.Stacked"
    Gap = "Base.Interface.Layout.Spacer"
    
    # === VISUAL - Графіка та рендеринг ===
    Painter = "Base.Visual.Painter"
    PainterPath = "Base.Visual.PainterPath"
    Pen = "Base.Visual.Pen"
    Brush = "Base.Visual.Brush"
    Color = "Base.Visual.Color"
    Palette = "Base.Visual.Palette"
    Font = "Base.Visual.Font"
    FontDatabase = "Base.Visual.FontDatabase"
    Pixmap = "Base.Visual.Pixmap"
    Image = "Base.Visual.Image"
    Bitmap = "Base.Visual.Bitmap"
    Icon = "Base.Visual.Icon"
    Polygon = "Base.Visual.Polygon"
    Gradient = "Base.Visual.Gradient.Linear"
    Transform = "Base.Visual.Transform"
    Region = "Base.Visual.Region"
    
    # === GRAPHICS VIEW ===
    View = "Base.Graphics.View"
    Scene = "Base.Graphics.Scene"
    Item = "Base.Graphics.Item"
    Line = "Base.Graphics.Line"
    Rect = "Base.Graphics.Rect"
    Ellipse = "Base.Graphics.Ellipse"
    Polygon = "Base.Graphics.Polygon"
    Text = "Base.Graphics.Text"
    GraphicObject = "Base.Graphics.Object"
    GraphicsImage = "Base.Graphics.Image"
    
    # === ANIMATION ===
    Animation = "Base.Animation"
    Property = "Base.Animation.Property"
    Variant = "Base.Animation.Variant"
    Timeline = "Base.Animation.TimeLine"
    Group = "Base.Animation.Group"
    Parallel = "Base.Animation.Parallel"
    Sequential = "Base.Animation.Sequential"
    Pause = "Base.Animation.Pause"
    
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
    
    # === МЕТОДИ ДОСТУПУ ТА РЕЗОЛВІНГУ (LCARS RETRIEVAL) ===
    # Прямий резолвінг ключа з реєстру LCARS
    @classmethod
    def Resolve(cls, Path: str):
        return registry.Retrieve(Path)

    Retrieve = Resolve

    # Каталог або кількість зареєстрованих компонентів
    @classmethod
    def Library(cls, Count: bool = False):
        return registry.Library(Count=Count)

    Catalog = Library

    # Реєстрація компонента в системному реєстрі LCARS
    @staticmethod
    def Register(Key, Value, Attribute=None):
        if isinstance(Value, tuple):
            registry.Register(Key, Value[0], Value[1] if len(Value) > 1 else None)
        else:
            registry.Register(Key, Value, Attribute)
        return Value
    
    # Діагностична інформація системи LCARS
    @classmethod
    def DebugInfo(cls):
        return {
            "Name": cls.Name,
            "Title": cls.Title,
            "Version": str(cls.Version),
            "Status": cls.Status,
            "Registered": len(registry),
            "Stardate": cls.Stardate(),
        }

    def __init__(self, SystemId=None, Id=None, **kwargs):
        self.SystemId = SystemId or Id or f"Sys{id(self)}"
        self.Id = self.SystemId

    def __repr__(self):
        return f"<LCARS Id={self.Id!r} Status={self.Status!r}>"

# =====================================================================
# COMPONENT CLASS - Базовий клас для компонентів

class SystemComponent(LCARS):
    def __init__(self, SystemId=None, Id=None, **kwargs):
        super().__init__(SystemId=SystemId, Id=Id, **kwargs)
        self.Version = Version.Release
        self.Enabled = True
        self.Visible = True
        self.Active = True
        self.Parent = None
        self.Module = None
        self.Config = {}
        self.Status = "Stopped"

    def AssignModule(self, Module):
        self.Module = Module
        if Module:
            Module.Parent = self
        self.Status = "Running"

    def Configure(self, Config):
        self.Config.update(Config)
        if self.Module and hasattr(self.Module, "Configure"):
            self.Module.Configure(Config)

    def Diagnostics(self):
        return {
            "Id": self.SystemId,
            "Status": self.Status,
            "Module": self.Module,
            "Config": self.Config
        }

    # === LIFECYCLE CONTRACT (DNA) ===
    def Initialize(self):
        pass

    def Start(self):
        self.Status = "Running"

    def Stop(self):
        self.Status = "Stopped"

    def Destroy(self):
        pass

# =====================================================================
# ABSTRACT MATRIX TYPE
# =====================================================================
class Matrix(SystemComponent):
    TypeName = "LCARSMatrix"

    def __init__(self, Parent=None, Id=None, SystemId=None, **kwargs):
        EffectiveId = Id or SystemId or (Parent if isinstance(Parent, str) else None)
        EffectiveParent = Parent if not isinstance(Parent, str) else None
        super().__init__(SystemId=EffectiveId, Id=EffectiveId)
        self.LcarsId = self.SystemId
        self.Parent = EffectiveParent
        self.Nodes = {}
        self.Domains = {}
        self.Links = {}
        self.Layers = {}
        self.State = {}
        self.Metadata = {}

    # === MATRIX CONTRACT ===
    def AddNode(self, Name, Node):
        self.Nodes[Name] = Node
        return Node

    def ReadNode(self, Name):
        return self.Nodes.get(Name)

    def AddDomain(self, Name, Domain=None):
        self.Domains[Name] = Domain
        return Domain

    def LinkNodes(self, Source, Target):
        pass
        
    def UnlinkNodes(self, Source, Target):
        pass

# =====================================================================
# Базовий тип процесу.
# Описує системний процес незалежно від його реалізації.
class Process(LCARS):

    # Ініціалізує процес з ідентифікатором та порожніми полями
    def __init__(self, Id=None):
        super().__init__(Id)

        self.Name = ""
        self.Command = ""
        self.State = "Created"
        self.Metadata = {}

    # Валідує процес, завжди повертає True
    def Validate(self):
        return True

    # Скидає стан процесу до "Created"
    def Reset(self):
        self.State = "Created"

    # Серіалізує процес у словник
    def ToDict(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "command": self.Command,
            "state": self.State,
            "metadata": self.Metadata.copy()
        }

    # Десеріалізує процес з словника
    @classmethod
    def FromDict(cls, Data):
        Obj = cls(Data.get("id"))

        Obj.Name = Data.get("name", "")
        Obj.Command = Data.get("command", "")
        Obj.State = Data.get("state", "Created")
        Obj.Metadata = Data.get("metadata", {}).copy()

        return Obj

    # Повертає рядкове представлення процесу
    def __repr__(self):
        return (
            f"<Process "
            f"Id={self.Id!r} "
            f"Name={self.Name!r} "
            f"State={self.State!r}>"
        )
# =====================================================================
class AlignMeta(type):
    def __getattr__(cls, Name: str):
        return getattr(LCARS, "AlignCenter", 0x0004) if "Center" in Name else (getattr(LCARS, "AlignRight", 0x0002) if "Right" in Name else getattr(LCARS, "AlignLeft", 0x0001))

class Align(metaclass=AlignMeta):
    AlignCenter = 0x0004
    AlignLeft = 0x0001
    AlignRight = 0x0002
    AlignTop = 0x0020
    AlignBottom = 0x0040
    AlignVCenter = 0x0080
    AlignHCenter = 0x0004

# Базовий тип директиви.
# Описує системну директиву незалежно від її реалізації.
class Directive(LCARS):
    Align = Align

    @staticmethod
    def PathDrive(*Parts):
        return LCARS.System.Path(*Parts)

    def __init__(self, Id=None):
        super().__init__(Id)

        self.Name = ""
        self.Category = None
        self.Source = None
        self.Target = None

        self.Priority = 0
        self.State = "Created"
        self.Metadata = {}

    def Validate(self):
        return True

    def Reset(self):
        self.State = "Created"

    def ToDict(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "category": self.Category,
            "source": self.Source,
            "target": self.Target,
            "priority": self.Priority,
            "state": self.State,
            "metadata": self.Metadata.copy()
        }

    @classmethod
    def FromDict(cls, Data):
        Obj = cls(Data.get("id"))

        Obj.Name = Data.get("name", "")
        Obj.Category = Data.get("category")
        Obj.Source = Data.get("source")
        Obj.Target = Data.get("target")
        Obj.Priority = Data.get("priority", 0)
        Obj.State = Data.get("state", "Created")
        Obj.Metadata = Data.get("metadata", {}).copy()

        return Obj

    def __repr__(self):
        return (
            f"<Directive "
            f"Id={self.Id!r} "
            f"Name={self.Name!r} "
            f"State={self.State!r}>"
        )

# Базовий тип протоколу.
# Описує формат, правила та стан протоколу.
class Protocol(LCARS):
    Name = "Base.Protocol"

    # Ініціалізує протокол з кодуванням та форматом
    def __init__(self, Id=None):
        super().__init__(Id)

        self.Name = ""
        self.Version = ""
        self.Category = None

        self.Encoding = None
        self.Format = None

        self.State = "Inactive"

        self.Metadata = {}

    # Валідує протокол за даними, завжди повертає True
    def Validate(self, Data=None):
        return True

    # Кодує дані відповідно до протоколу
    def Encode(self, Data):
        return Data

    # Декодує дані з протоколу
    def Decode(self, Data):
        return Data

    # Серіалізує дані протоколу
    def Serialize(self, Data):
        return Data

    # Десеріалізує дані протоколу
    def Deserialize(self, Data):
        return Data

    # Скидає стан протоколу до "Inactive"
    def Reset(self):
        self.State = "Inactive"

    # Серіалізує протокол у словник
    def ToDict(self):
        return {
            "id": self.Id,
            "name": self.Name,
            "version": self.Version,
            "category": self.Category,
            "encoding": self.Encoding,
            "format": self.Format,
            "state": self.State,
            "metadata": self.Metadata.copy()
        }

    # Десеріалізує протокол з словника
    @classmethod
    def FromDict(cls, Data):

        Obj = cls(Data.get("id"))
        Obj.Name = Data.get("name", "")
        Obj.Version = Data.get("version", "")
        Obj.Category = Data.get("category")
        Obj.Encoding = Data.get("encoding")
        Obj.Format = Data.get("format")
        Obj.State = Data.get("state", "Inactive")
        Obj.Metadata = Data.get("metadata", {}).copy()
        return Obj

    # Повертає рядкове представлення протоколу
    def __repr__(self):
        return (
            f"<Protocol "
            f"Id={self.Id!r} "
            f"Name={self.Name!r} "
            f"Version={self.Version!r} "
            f"State={self.State!r}>"
        )
        
# =====================================================================
# ЕКСПОРТОВАНІ ТИПИ БАЗОВОГО ШАРУ (DNA)
# =====================================================================
__all__ = [
    "LCARS",
    "SystemComponent",
    "Matrix",
    "Directive",
    "Protocol",
    "Process",
    "Align",
    "Type",
    "Annotation",
]



