# LCARS FRAMEWORK TYPES CORE LCARS OBJECTS (DNA)
# ОПИС: Фундаментальні типи та архітектурні замінники.
# ПРИНЦИП: Стала база. Усі типи ініціалізуються через Реєстр.
# ─────────────────────────────────────────────────────────────────────────────
from typing import Any
from .register import registry
from .version import getVersion

# Складові частини типу ініціалізуються через Реєстр та LCARS.System

# =====================================================================
# METACLASS - Динамічний доступ до реєстру
class Namespace(type):
    # Повертає новий клас або об'єкт з реєстру для атрибута
    def __getattr__(cls, AttributeName: str) -> Any:
        if AttributeName.startswith("_"):
            raise AttributeError(AttributeName)

        ParentNamespace = type.__getattribute__(cls, "NamespacePath") if "NamespacePath" in cls.__dict__ else (
            type.__getattribute__(cls, "Name") if "Name" in cls.__dict__ else type.__getattribute__(cls, "__name__")
        )
        FullNamespacePath = f"{ParentNamespace}.{AttributeName}"
        ResolvedEntry = registry.Resolve(FullNamespacePath)
        if ResolvedEntry is not None:
            ModuleName, AttributeTarget = ResolvedEntry
            import importlib
            ModuleInstance = importlib.import_module(ModuleName)
            if AttributeTarget:
                for NestedAttributeName in AttributeTarget.split("."):
                    ModuleInstance = getattr(ModuleInstance, NestedAttributeName)
            return ModuleInstance

        return type(
            AttributeName, (),
            {
                "Name": FullNamespacePath,
                "NamespacePath": FullNamespacePath,
            },
        )

    # Перехоплює доступ до атрибутів і резолвить рядкові шляхи через Реєстр
    def __getattribute__(cls, AttributeName: str) -> Any:
        if AttributeName.startswith("_"):
            return super().__getattribute__(AttributeName)
        if AttributeName in {"Name", "NamespacePath"}:
            return super().__getattribute__(AttributeName)
        TargetValue = super().__getattribute__(AttributeName)
        if isinstance(TargetValue, str) and "." in TargetValue:
            ResolvedEntry = registry.Resolve(TargetValue)
            if ResolvedEntry is not None:
                ModuleName, AttributeTarget = ResolvedEntry
                import importlib
                ModuleInstance = importlib.import_module(ModuleName)
                if AttributeTarget:
                    for NestedAttributeName in AttributeTarget.split("."):
                        ModuleInstance = getattr(ModuleInstance, NestedAttributeName)
                return ModuleInstance
        return TargetValue

class SystemNamespace(metaclass=Namespace):
    NamespacePath = "System"

class CoreNamespace(metaclass=Namespace):
    NamespacePath = "Base.Core"

class VisualNamespace(metaclass=Namespace):
    NamespacePath = "Base.Visual"

class InterfaceNamespace(metaclass=Namespace):
    NamespacePath = "Base.Interface"

class ProtocolNamespace(metaclass=Namespace):
    NamespacePath = "Base.Protocol"

class GeometryNamespace(metaclass=Namespace):
    NamespacePath = "Base.Geometry"

# =====================================================================
# LCARS CLASS - Головний клас з динамічною маршрутизацією
class LCARS(metaclass=Namespace):
    Name = "Library Computer Access/Retrieval System"
    System = SystemNamespace
    Core = CoreNamespace
    Visual = VisualNamespace
    Interface = InterfaceNamespace
    Protocol = ProtocolNamespace
    Geometry = GeometryNamespace
    Version = getVersion()
    Dependencies = []
    # === СИСТЕМНІ КОРЕНІ РЕЄСТРУ ===
    LCARS           = "System.LCARS"
    Regex           = "System.Regex"
    Math            = "System.Math"
    Random          = "System.Random"
    RandomInteger   = "System.Random.Integer"
    RandomChoice    = "System.Random.Choice"
    RandomFloat     = "System.Random.Float"
    RandomRange     = "System.Random.Range"
    TimeMod         = "System.Time"
    Copy            = "System.Copy"
    String          = "System.String"
    Sys             = "System.Sys"
    Typing          = "System.TypeHint"
    Module          = "System.Module"
    ModuleUtil      = "System.Module.Util"
    Import          = "System.Module.Import"
    ModuleSpec      = "System.Module.SpecFromFile"
    ModuleFromSpec  = "System.Module.FromSpec"
    ModuleLoader    = "System.Module.Loader"
    Deepcopy        = "System.Copy.Deep"
    Environment     = "System.Environment"
    Directory       = "System.Directory"
    Process         = "System.Process"
    Task            = "System.Task"
    Memory          = "System.Memory"
    Module          = "System.Module"
    Resource        = "System.Resource"
    Security        = "System.Security"
    Network         = "System.Network"
    Context         = "System.Context"
    Collection      = "System.Collection"
    Iterator        = "System.Iterator"
    Function        = "System.Function"
    Operator        = "System.Operator"
    Traceback       = "System.Traceback"
    Temporary       = "System.Temporary"
    URL             = "System.URL"
    # === ПЛАТФОРМА === 
    Release         = "System.Platform.Release"
    Machine         = "System.Platform.Machine"
    Processor       = "System.Platform.Processor"
    Architecture    = "System.Platform.Architecture"
    Node            = "System.Platform.Node"
    Compiler        = "System.Platform.Compiler"
    Build           = "System.Platform.Build"
    # === СИГНАЛИ / СЛОТИ / ВЛАСТИВОСТІ (QtCore wrappers) ===
    Object          = "Base.Core.Object"
    Signal          = "Base.Core.Signal"
    Slot            = "Base.Core.Slot"
    Property        = "Base.Core.Property"

# === ЗАСТОСУНОК / ПОТОКИ / ТАЙМЕР ===
    Application     = "Base.Interface.Application"
    Thread          = "Base.Core.Thread"
    Timer           = "Base.Core.Timer"
    Chronometer     = "Base.Core.Timer"
    Lock            = "Base.Core.Sync.Mutex"
    Mutex           = "Base.Core.Sync.Mutex"
    Semaphore       = "Base.Core.Sync.Semaphore"
    WaitCondition   = "Base.Core.Sync.Wait"

    # === ФАЙЛОВА СИСТЕМА ===
    File            = "Base.Core.File"
    Dir             = "Base.Core.Directory"
    Url             = "Base.Core.Data.Url"
    Settings        = "Base.Core.Settings"

    # === ПОДІЇ / ЧАС ===
    Event           = "Base.Core.Event"
    Date            = "Base.Core.Time.Date"
    DateTime        = "Base.Core.Time.DateTime"
    Time            = "Base.Core.Time.Clock"

    # === ГЕОМЕТРІЯ ТА КООРДИНАТИ ===
    Size            = "Base.Geometry.Size"
    SizeF           = "Base.Geometry.Size"
    Rect            = "Base.Geometry.Rect"
    RectF           = "Base.Geometry.Rect"
    Point           = "Base.Geometry.Point"
    PointF          = "Base.Geometry.Point"
    Line            = "Base.Geometry.Line"
    Margins         = "Base.Geometry.Margins"
    Transform       = "Base.Visual.Transform"
    Region          = "Base.Visual.Region"

    # === ДАНІ ТА СТРУКТУРИ ===
    ByteArray       = "Base.Core.Data.ByteArray"
    MimeData        = "Base.Core.Data.Mime"
    Uuid            = "Base.Core.Data.Uuid"

    # === UI КОНТЕЙНЕРИ ===
    Panel           = "Base.Interface.Frame"
    Segment         = "Base.Interface.Widget"
    Buffer          = "Base.Interface.Scroll"
    Tab             = "Base.Interface.Tab"
    Stacked         = "Base.Interface.Stack"
    Divider         = "Base.Interface.Splitter"
    Dock            = "Base.Interface.Dock"
    Progress        = "Base.Interface.ProgressBar"
    Readout         = "Base.Interface.LCD"

    # === ДІАЛОГИ / МЕНЮ / TOOLBAR ===
    Dialog          = "Base.Interface.Dialog"
    Message         = "Base.Interface.Dialog.Message"
    FileDialog      = "Base.Interface.Dialog.File"
    Menu            = "Base.Interface.Menu"
    MenuBar         = "Base.Interface.MenuBar"
    ToolBar         = "Base.Interface.ToolBar"
    StatusBar       = "Base.Interface.StatusBar"
    Command         = "Base.Interface.Action"
    Beacon          = "Base.Interface.SystemTray"
    Grip            = "Base.Interface.SizeGrip"
    Policy          = "Base.Interface.SizePolicy"
    Synthesizer     = "Base.Interface.Completer"

    # === ІНТЕРАКТИВНІ ЕЛЕМЕНТИ ===
    Button          = "Base.Interface.Button"
    Label           = "Base.Interface.Label"
    Input           = "Base.Interface.LineEdit"
    Console         = "Base.Interface.TextEdit"
    Terminal        = "Base.Interface.TextEdit"
    Selector        = "Base.Interface.Combo"
    Regulator       = "Base.Interface.Slider"
    TextEdit        = "Base.Interface.TextEdit"
    PlainText       = "Base.Interface.PlainText"
    LineEdit        = "Base.Interface.LineEdit"
    ToolButton      = "Base.Interface.ToolButton"
    Radio           = "Base.Interface.Radio"
    CheckBox        = "Base.Interface.CheckBox"
    SpinBox         = "Base.Interface.SpinBox"
    DoubleSpinBox   = "Base.Interface.DoubleSpinBox"
    DateEdit        = "Base.Interface.DateEdit"
    TimeEdit        = "Base.Interface.TimeEdit"
    DateTimeEdit    = "Base.Interface.DateTimeEdit"
    Dial            = "Base.Interface.Dial"
    Slider          = "Base.Interface.Slider"
    ScrollBar       = "Base.Interface.ScrollBar"
    ProgressBar     = "Base.Interface.ProgressBar"
    LCD             = "Base.Interface.LCD"

    # === ЛІСТИНГИ ТА ТАБЛИЦІ ===
    Manifest        = "Base.Interface.List"
    Record          = "Base.Interface.Item.List"
    Hierarchy       = "Base.Interface.Tree"
    Table           = "Base.Interface.Table"
    Combo           = "Base.Interface.Combo"
    Tray            = "Base.Interface.SystemTray"
    Complete        = "Base.Interface.Completer"

    # === LAYOUTS ===
    Layout          = "Base.Interface.Layout"
    Vertical        = "Base.Interface.Layout.Vertical"
    Horizontal      = "Base.Interface.Layout.Horizontal"
    VBox            = "Base.Interface.Layout.Vertical"
    HBox            = "Base.Interface.Layout.Horizontal"
    VMatrix         = "Base.Interface.Layout.Vertical"
    HMatrix         = "Base.Interface.Layout.Horizontal"
    Grid            = "Base.Interface.Layout.Grid"
    Form            = "Base.Interface.Layout.Form"
    StackLayout     = "Base.Interface.Layout.Stacked"
    Gap             = "Base.Interface.Layout.Spacer"

    # === ГРАФІКА ТА ВІЗУАЛІЗАЦІЯ ===
    Painter         = "Base.Visual.Painter"
    PainterPath     = "Base.Visual.PainterPath"
    Pen             = "Base.Visual.Pen"
    Brush           = "Base.Visual.Brush"
    Color           = "Base.Visual.Color"
    Palette         = "Base.Visual.Palette"
    Font            = "Base.Visual.Font"
    Pixmap          = "Base.Visual.Pixmap"
    Image           = "Base.Visual.Image"
    Bitmap          = "Base.Visual.Bitmap"
    Icon            = "Base.Visual.Icon"
    Polygon         = "Base.Visual.Polygon"
    Gradient        = "Base.Visual.Gradient.Linear"

    # === ВІКНА / ДІАЛОГИ ===
    FileSelect      = "Base.Interface.Dialog.File"
    ColorPick       = "Base.Interface.Dialog.Color"
    FontPick        = "Base.Interface.Dialog.Font"
    ProgressDialog  = "Base.Interface.Dialog.Progress"
    ErrorDialog     = "Base.Interface.Dialog.Error"
    InputDialog     = "Base.Interface.Dialog.Input"
    Wizard          = "Base.Interface.Dialog.Wizard"

    # === GRAPHICS VIEW ===
    GraphicsView    = "Base.Graphics.View"
    GraphicsScene   = "Base.Graphics.Scene"
    GraphicsItem    = "Base.Graphics.Item"
    GraphicsObject  = "Base.Graphics.Object"
    GraphicsLine    = "Base.Graphics.Line"
    GraphicsRect    = "Base.Graphics.Rect"
    GraphicsEllipse = "Base.Graphics.Ellipse"
    GraphicsPath    = "Base.Graphics.Path"
    GraphicsPolygon = "Base.Graphics.Polygon"
    GraphicsText    = "Base.Graphics.Text"
    GraphicsImage   = "Base.Graphics.Image"

    # === ANIMATION ===
    Animation           = "Base.Animation"
    AnimationProperty   = "Base.Animation.Property"
    AnimationVariant    = "Base.Animation.Variant"
    AnimationTimeline   = "Base.Animation.TimeLine"
    AnimationGroup      = "Base.Animation.Group"
    AnimationParallel   = "Base.Animation.Parallel"
    AnimationSequential = "Base.Animation.Sequential"
    AnimationPause      = "Base.Animation.Pause"

    # === PROTOCOL ENUMS (однословні) ===
    AlignCenter     = "Base.Protocol.Align.Center"
    AlignLeft       = "Base.Protocol.Align.Left"
    AlignRight      = "Base.Protocol.Align.Right"
    AlignAbove     = "Base.Protocol.Align.Top"
    AlignBottom     = "Base.Protocol.Align.Bottom"
    AlignHCenter    = "Base.Protocol.Align.HCenter"
    AlignVCenter    = "Base.Protocol.Align.VCenter"
    KeyReturn       = "Base.Protocol.Key.Return"
    KeyEnter        = "Base.Protocol.Key.Enter"
    KeyEscape       = "Base.Protocol.Key.Escape"
    KeyBackspace    = "Base.Protocol.Key.Backspace"
    KeyTab          = "Base.Protocol.Key.Tab"
    KeySpace        = "Base.Protocol.Key.Space"
    KeyUp           = "Base.Protocol.Key.Up"
    KeyDown         = "Base.Protocol.Key.Down"
    KeyLeft         = "Base.Protocol.Key.Left"
    KeyRight        = "Base.Protocol.Key.Right"
    KeyHome         = "Base.Protocol.Key.Home"
    KeyEnd          = "Base.Protocol.Key.End"
    KeyPageUp       = "Base.Protocol.Key.PageUp"
    KeyPageDown     = "Base.Protocol.Key.PageDown"
    Frameless       = "Base.Protocol.DisplayFlag.Frameless"
    StayOnTop       = "Base.Protocol.DisplayFlag.StayOnTop"
    CursorHand      = "Base.Protocol.Cursor.Pointing"
    CursorWait      = "Base.Protocol.Cursor.Wait"
    CursorCross     = "Base.Protocol.Cursor.Cross"
    CursorIBeam     = "Base.Protocol.Cursor.IBeam"
    CursorArrow     = "Base.Protocol.Cursor.Arrow"
    CursorSizeAll   = "Base.Protocol.Cursor.SizeAll"
    CursorForbidden = "Base.Protocol.Cursor.Forbidden"
    CursorBusy      = "Base.Protocol.Cursor.Busy"
    CursorPointing  = "Base.Protocol.Cursor.Pointing"
    ScrollAlwaysOff = "Base.Protocol.Scroll.AlwaysOff"
    TextCursor      = "Base.Visual.Text.Cursor"

    # Реєструє клас у глобальному реєстрі за ключем
    @staticmethod
    def Register(Key, Value):
        registry.Register(Key, Value)
        return Value

    # === ШЛЯХИ ===
    # Повертає рядковий шлях з частин
    @staticmethod
    def Path(*Parts):
        PathClass = LCARS.System.Path
        return str(PathClass(*Parts))

    # Повертає об'єкт Path з частин
    @staticmethod
    def PathLib(*Parts):
        PathClass = LCARS.System.Path
        return PathClass(*Parts)

    # Повертає поточну робочу директорію
    @staticmethod
    def WorkDir():
        PathClass = LCARS.System.Path
        return str(PathClass.cwd())

    # Повертає домашню директорію користувача
    @staticmethod
    def HomeDir():
        PathClass = LCARS.System.Path
        return str(PathClass.home())

    # === КЕШУВАННЯ ===
    Cache = {}
    # Повертає інформацію для дебагу: версія, платформа, кількість зареєстрованих
    @classmethod
    def DebugInfo(cls):
        return {
            "version": cls.Version,
            "platform": cls.Platform,
            "registered": len(registry.List())
        }       
    # === ЕКЗЕМПЛЯР ===
    def __init__(self, Id=None):
        self.Id = Id or f"Sys{id(self)}"
        self.SystemId = self.Id
        self.Active = True
        self.Parent = None

    # === ДОДАТКОВІ АЛІАСИ ДЛЯ СУМІСНОСТІ (lab_manager, etc.) ===
    Visual      = "Base.Visual"
    Chassis     = "Base.Interface.Frame"
    VBoxLayout  = "Base.Interface.Layout.Vertical"
    HBoxLayout  = "Base.Interface.Layout.Horizontal"
    GridLayout  = "Base.Interface.Layout.Grid"
    Logic       = "System.Function"
    Lore        = "System.Module"
    ODN         = "System.Network"

# LCARS PRIMITIVES (updated)
class Primitives:
    Rect = "Base.Geometry.Rect"
    RectF = "Base.Geometry.Rect"
    Point = "Base.Geometry.Point"
    Line = "Base.Geometry.Line"
    Circle = "Base.Geometry.Circle"
    Ellipse = "Base.Geometry.Ellipse"
    Polygon = "Base.Visual.Polygon"
    Triangle = "Base.Geometry.Triangle"
    Trapezoid = "Base.Geometry.Trapezoid"
    Button = "Base.Interface.Button"
    Label = "Base.Interface.Label"
    Panel = "Base.Interface.Frame"
    Painter = "Base.Visual.Painter"
    Pen = "Base.Visual.Pen"
    Brush = "Base.Visual.Brush"
    Font = "Base.Visual.Font"
    Path = "Base.Visual.PainterPath"
    RectF = "Base.Geometry.Rect"
    Point = "Base.Geometry.Point"
    VBox = "Base.Interface.Layout.Vertical"
    HBox = "Base.Interface.Layout.Horizontal"
    Antialiasing = "Base.Visual.RenderHint.Antialiasing"

# =====================================================================
# LCARS TYPE - Базовий тип даних з динамічною маршрутизацією
class Matrix(LCARS):
    TypeName = "LCARSMatrix"

    # Ініціалізує матрицю з батьківським елементом та порожніми контейнерами
    def __init__(self, Parent=None, Id=None):
        super().__init__(Id=Id)
        self.Parent = Parent
        self.Nodes = {}
        self.Domains = {}
        self.Links = {}
        self.Layers = {}
        self.State = {}
        self.Metadata = {}

    # Додає вузол до матриці за іменем
    def AddNode(self, Name, Node):
        self.Nodes[Name] = Node
        return Node

    # Повертає вузол за іменем або None
    def GetNode(self, Name):
        return self.Nodes.get(Name)

    # Додає домен до матриці
    def AddDomain(self, Name, Domain=None):
        self.Domains[Name] = Domain
        return Domain

    # Створює зв'язок між джерелом і ціллю
    def Link(self, Source, Target):
        self.Links.setdefault(Source, set()).add(Target)

    # Повертає знімок стану матриці
    def Snapshot(self):
        return {
            "Nodes": self.Nodes,
            "Domains": self.Domains,
            "Links": self.Links,
            "Layers": self.Layers,
            "State": self.State
        }

LCARSMatrix = Matrix
# ІНШІ БАЗОВІ ТИПИ МОЖУТЬ БУТИ ДОДАНІ ТУТ
class SystemComponent(LCARS):
    # Ініціалізує системний компонент з модулем та конфігурацією
    def __init__(self, Id=None):
        super().__init__(Id)
        self.Module = None
        self.Config = {}
        self.Status = "Stopped"
        
    # Встановлює модуль компонента та оновлює статус
    def SetModule(self, Module):
        self.Module = Module
        Module.Parent = self
        self.Status = "Running"
        
    # Оновлює конфігурацію компонента та передає в модуль
    def Configure(self, Config):
        self.Config.update(Config)
        if self.Module:
            self.Module.Configure(Config)
            
    # Повертає словник з поточним статусом компонента
    def GetStatus(self):
        return {
            "id": self.SystemId,
            "status": self.Status,
            "module": self.Module,
            "config": self.Config
        }

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
# Базовий тип директиви.
# Описує системну директиву незалежно від її реалізації.
class Directive(LCARS):

    # Ініціалізує директиву з пріоритетом та станом
    def __init__(self, Id=None):
        super().__init__(Id)

        self.Name = ""
        self.Category = None
        self.Source = None
        self.Target = None

        self.Priority = 0
        self.State = "Created"
        self.Metadata = {}

    # Валідує директиву, завжди повертає True
    def Validate(self):
        return True

    # Скидає стан директиви до "Created"
    def Reset(self):
        self.State = "Created"

    # Серіалізує директиву у словник
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

    # Десеріалізує директиву з словника
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

    # Повертає рядкове представлення директиви
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
__all__ = [
    "LCARS", "SystemComponent", "Matrix", "LCARSMatrix",
    "Directive", "Protocol", "Process", "Primitives",
]
