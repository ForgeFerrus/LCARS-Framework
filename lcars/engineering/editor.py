# ◤ LCARS ENGINEERING :: INTERFACE ATOMIC EDITOR & DECOMPILER 🖖
# =============================================================================
# ФАЙЛ: lcars/engineering/editor.py
# ОПИС: Інженерний Редактор та Декомпілятор інтерфейсів зорельота LCARS.
#       Забезпечує часткове та атомарне розкладання будь-якого екрана/консолі
#       на базові примітиви (Button, Elbow, Bar, Label, Panel) при переході
#       у SystemMode.EDIT, маніпуляцію елементами за магнітною сіткою (5px)
#       та подвійне збереження: у вихідний файл і як образ в ізолінійний чіп (07).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.core.signal import Transmission
from lcars.modules.mode import ModeManager, SystemMode

# Операції редагування інтерфейсу зорельота
class EditOperation(LCARS):
    VIEW = "VIEW"
    INTERACT = "INTERACT"
    NAVIGATE = "NAVIGATE"
    EDIT = "EDIT"
    MOVE = "MOVE"
    RESIZE = "RESIZE"
    DELETE = "DELETE"
    CREATE = "CREATE"

# Атомарні типи примітивів LCARS
class PrimitiveType(LCARS):
    PANEL = "PANEL"
    BUTTON = "BUTTON"
    ELBOW = "ELBOW"
    BAR = "BAR"
    CAP = "CAP"
    LABEL = "LABEL"
    SENSOR = "SENSOR"
    GRID = "GRID"
    CONTAINER = "CONTAINER"

# Головний інженерний редактор інтерфейсів корабля
class InterfaceEditor(SystemComponent):
    Instance = None

    # Оптичні сигнали шини ODN
    ModeChanged = Transmission(SystemMode)
    ElementUpdated = Transmission(str, dict)
    ElementDeleted = Transmission(str)
    ChipExported = Transmission(str, str)

    def __init__(self):
        super().__init__()
        self.Elements: list[dict] = []
        self.SelectedId: str | None = None
        self.ModeManager = ModeManager()
        self.Clipboard: dict | None = None
        self.GridSize = 5
        self.IsEnabled = False
        self.UndoStack: list[list[dict]] = []
        self.RedoStack: list[list[dict]] = []
        self.CurrentEra = "24th"

    @classmethod
    def GetInstance(cls) -> InterfaceEditor:
        if cls.Instance is None:
            cls.Instance = InterfaceEditor()
        return cls.Instance

    # ─── КЕРУВАННЯ РЕЖИМАМИ (SystemMode.EDIT) ─────────────────────────────────

    def Enable(self) -> None:
        self.SaveState()
        self.IsEnabled = True
        self.ModeManager.EnterEditMode()
        self.ModeChanged.Emit(SystemMode.EDIT)

    def Disable(self) -> None:
        self.IsEnabled = False
        self.ModeManager.ExitEditMode()
        self.SelectedId = None
        self.ModeChanged.Emit(self.ModeManager.GetMode())

    def ToggleMode(self) -> SystemMode:
        if self.ModeManager.IsEditMode():
            self.Disable()
        else:
            self.Enable()
        return self.ModeManager.GetMode()

    def CanPerformOperation(self, Operation: str) -> bool:
        if not self.IsEnabled:
            return Operation in (EditOperation.VIEW, EditOperation.NAVIGATE)
        return self.ModeManager.State.Can(Operation.lower())

    # ─── ДЕКОМПОЗИЦІЯ ІНТЕРФЕЙСУ (ЧАСТКОВА ТА АТОМАРНА) ───────────────────────

    def DecomposeInterface(self, TargetObject: any, PartialOnly: bool = False) -> list[dict]:
        self.SaveState()
        DecomposedNodes: list[dict] = []
        if TargetObject is None:
            return DecomposedNodes

        # Якщо об'єкт — словник макета або список
        if isinstance(TargetObject, dict):
            return self.DecomposeDictionary(TargetObject, PartialOnly)

        # Якщо об'єкт — віджет графічного інтерфейсу (PyQt6 / QWidget)
        if hasattr(TargetObject, "children"):
            Children = TargetObject.children()
            for Index, Child in enumerate(Children):
                if not hasattr(Child, "geometry"):
                    continue
                Geo = Child.geometry()
                TypeStr = Child.__class__.__name__.upper()

                IsAtomic = not PartialOnly and (len(Child.children()) == 0 or "BUTTON" in TypeStr or "LABEL" in TypeStr)
                NodeId = f"node_{Index}_{TypeStr.lower()}"

                NodeData = {
                    "Id": NodeId,
                    "Type": self.MapToPrimitiveType(TypeStr),
                    "OriginalClass": Child.__class__.__name__,
                    "Position": (self.Snap(Geo.x()), self.Snap(Geo.y())),
                    "Size": (self.Snap(Geo.width()), self.Snap(Geo.height())),
                    "IsPrimitive": IsAtomic,
                    "Properties": {
                        "Visible": Child.isVisible() if hasattr(Child, "isVisible") else True,
                        "Enabled": Child.isEnabled() if hasattr(Child, "isEnabled") else True,
                        "Text": Child.text() if hasattr(Child, "text") else "",
                    }
                }
                DecomposedNodes.append(NodeData)

        self.Elements = DecomposedNodes
        return self.Elements

    def DecomposeDictionary(self, DataDict: dict, PartialOnly: bool = False) -> list[dict]:
        Nodes: list[dict] = []
        RawElements = DataDict.get("elements", DataDict.get("Elements", []))
        for Index, Item in enumerate(RawElements):
            NodeId = Item.get("Id", f"elem_{Index}")
            TypeStr = Item.get("Type", "PANEL").upper()
            IsAtomic = not PartialOnly or Item.get("IsPrimitive", True)
            Pos = Item.get("Position", (0, 0))
            Sz = Item.get("Size", (100, 40))

            Node = {
                "Id": NodeId,
                "Type": self.MapToPrimitiveType(TypeStr),
                "Position": (self.Snap(Pos[0]), self.Snap(Pos[1])),
                "Size": (self.Snap(Sz[0]), self.Snap(Sz[1])),
                "IsPrimitive": IsAtomic,
                "Properties": Item.get("Properties", {}),
            }
            Nodes.append(Node)
        self.Elements = Nodes
        return self.Elements

    def MapToPrimitiveType(self, ClassOrType: str) -> str:
        Upper = ClassOrType.upper()
        if "BUTTON" in Upper:
            return PrimitiveType.BUTTON
        if "ELBOW" in Upper:
            return PrimitiveType.ELBOW
        if "BAR" in Upper:
            return PrimitiveType.BAR
        if "CAP" in Upper:
            return PrimitiveType.CAP
        if "LABEL" in Upper or "TEXT" in Upper:
            return PrimitiveType.LABEL
        if "SENSOR" in Upper or "GRID" in Upper:
            return PrimitiveType.SENSOR
        return PrimitiveType.PANEL

    # ─── МАГНІТНА СІТКА LCARS ──────────────────────────────────────────────────

    def Snap(self, Value: int) -> int:
        if self.GridSize <= 1:
            return Value
        return int(round(Value / self.GridSize) * self.GridSize)

    def SnapPosition(self, Pos: tuple[int, int]) -> tuple[int, int]:
        return (self.Snap(Pos[0]), self.Snap(Pos[1]))

    def SnapSize(self, Size: tuple[int, int]) -> tuple[int, int]:
        return (max(self.GridSize, self.Snap(Size[0])), max(self.GridSize, self.Snap(Size[1])))

    # ─── МАНІПУЛЯЦІЯ ЕЛЕМЕНТАМИ ───────────────────────────────────────────────

    def AddElement(self, ElementType: str, Position: tuple[int, int], Properties: dict | None = None) -> dict:
        self.SaveState()
        Props = Properties or {}
        ElementId = f"{ElementType.lower()}_{len(self.Elements) + 1}"
        Element = {
            "Id": ElementId,
            "Type": self.MapToPrimitiveType(ElementType),
            "Position": self.SnapPosition(Position),
            "Size": self.SnapSize(Props.get("Size", (120, 40))),
            "Color": Props.get("Color", "#FF9900"),
            "Text": Props.get("Text", "NODE"),
            "IsPrimitive": True,
            "Properties": Props,
        }
        self.Elements.append(Element)
        self.ElementUpdated.Emit(ElementId, Element)
        return Element

    def SelectElement(self, ElementId: str) -> dict | None:
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.SelectedId = ElementId
                return El
        return None

    def MoveElement(self, ElementId: str, NewPosition: tuple[int, int]) -> bool:
        self.SaveState()
        Snapped = self.SnapPosition(NewPosition)
        for El in self.Elements:
            if El["Id"] == ElementId:
                El["Position"] = Snapped
                self.ElementUpdated.Emit(ElementId, El)
                return True
        return False

    def ResizeElement(self, ElementId: str, NewSize: tuple[int, int]) -> bool:
        self.SaveState()
        Snapped = self.SnapSize(NewSize)
        for El in self.Elements:
            if El["Id"] == ElementId:
                El["Size"] = Snapped
                self.ElementUpdated.Emit(ElementId, El)
                return True
        return False

    def UpdateElement(self, ElementId: str, Properties: dict) -> bool:
        self.SaveState()
        for El in self.Elements:
            if El["Id"] == ElementId:
                El["Properties"].update(Properties)
                if "Position" in Properties:
                    El["Position"] = self.SnapPosition(Properties["Position"])
                if "Size" in Properties:
                    El["Size"] = self.SnapSize(Properties["Size"])
                if "Text" in Properties:
                    El["Text"] = Properties["Text"]
                if "Color" in Properties:
                    El["Color"] = Properties["Color"]
                self.ElementUpdated.Emit(ElementId, El)
                return True
        return False

    def DeleteElement(self, ElementId: str) -> bool:
        self.SaveState()
        for Index, El in enumerate(self.Elements):
            if El["Id"] == ElementId:
                del self.Elements[Index]
                if self.SelectedId == ElementId:
                    self.SelectedId = None
                self.ElementDeleted.Emit(ElementId)
                return True
        return False

    def CopyElement(self, ElementId: str) -> bool:
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.Clipboard = dict(El)
                self.Clipboard["Id"] = f"{El['Id']}_copy"
                return True
        return False

    def PasteElement(self, Position: tuple[int, int] | None = None) -> dict | None:
        if not self.Clipboard:
            return None
        self.SaveState()
        NewElement = dict(self.Clipboard)
        NewId = f"{self.Clipboard['Type'].lower()}_{len(self.Elements) + 1}"
        NewElement["Id"] = NewId
        if Position:
            NewElement["Position"] = self.SnapPosition(Position)
        else:
            PrevPos = NewElement.get("Position", (0, 0))
            NewElement["Position"] = self.SnapPosition((PrevPos[0] + 15, PrevPos[1] + 15))
        self.Elements.append(NewElement)
        self.ElementUpdated.Emit(NewId, NewElement)
        return NewElement

    # ─── UNDO / REDO СТАН ──────────────────────────────────────────────────────

    def SaveState(self) -> None:
        StateSnapshot = [dict(item) for item in self.Elements]
        self.UndoStack.append(StateSnapshot)
        if len(self.UndoStack) > 50:
            self.UndoStack.pop(0)
        self.RedoStack.clear()

    def Undo(self) -> bool:
        if not self.UndoStack:
            return False
        CurrentSnapshot = [dict(item) for item in self.Elements]
        self.RedoStack.append(CurrentSnapshot)
        self.Elements = self.UndoStack.pop()
        return True

    def Redo(self) -> bool:
        if not self.RedoStack:
            return False
        CurrentSnapshot = [dict(item) for item in self.Elements]
        self.UndoStack.append(CurrentSnapshot)
        self.Elements = self.RedoStack.pop()
        return True

    # ─── ПОДВІЙНЕ ЗБЕРЕЖЕННЯ (ФАЙЛ + ІЗОЛІНІЙНИЙ ЧІП 07) ───────────────────────

    def SaveToFile(self, FilePath: str) -> bool:
        Target = LCARS.System.Path(FilePath)
        Target.parent.mkdir(parents=True, exist_ok=True)
        Payload = {
            "version": VersionInfo.GetVersion(),
            "era": self.CurrentEra,
            "elements_count": len(self.Elements),
            "elements": self.Elements,
        }
        Content = LCARS.Storage.Yaml.dump(Payload, sort_keys=False)
        Target.write_text(Content, encoding="utf-8")
        return True

    def SaveToChip(
        self,
        ChipNumber: str = "07-0010",
        ChipName: str = "LCARS Custom Station Interface",
        Faction: str = "Federation",
        Era: str = "24th"
    ) -> str:
        ChipDir = LCARS.System.Path("lcars/engineering/chips/07")
        ChipDir.mkdir(parents=True, exist_ok=True)
        ChipFile = ChipDir / f"{ChipNumber}.yaml"

        DataDir = LCARS.System.Path("lcars/data/07")
        DataDir.mkdir(parents=True, exist_ok=True)
        SnapshotFile = DataDir / f"{ChipNumber}-snapshot.json"

        # Запис повного стану образу інтерфейсу
        SnapshotPayload = {
            "id": ChipNumber,
            "name": ChipName,
            "era": Era,
            "elements_count": len(self.Elements),
            "elements": self.Elements,
        }
        SnapshotJson = LCARS.Storage.Json.dumps(SnapshotPayload, indent=2)
        SnapshotFile.write_text(SnapshotJson, encoding="utf-8")

        # Запис канонічного маніфесту чіпа Категорії 07 (Interface)
        Manifest = {
            "metadata": {
                "id": ChipNumber,
                "name": ChipName,
                "category": "07",
                "version": VersionInfo.GetVersion(),
                "faction": Faction,
                "type": "interface",
                "status": "nominal",
            },
            "specs": {
                "capacity": 2048,
                "color_code": "#FF9900",
                "security_level": 2,
                "bus": "ODN-07",
                "primitives_count": len(self.Elements),
            },
            "paths": {
                "database_file": str(SnapshotFile).replace("\\", "/"),
            },
            "entrypoints": {
                "main": "lcars.engineering.editor:InterfaceEditor",
            },
            "description": f"Образ інтерфейсу зорельота ({ChipName}), скомпонований через InterfaceEditor.",
        }

        ManifestYaml = LCARS.Storage.Yaml.dump(Manifest, sort_keys=False)
        ChipFile.write_text(ManifestYaml, encoding="utf-8")

        self.ChipExported.Emit(ChipNumber, ChipName)
        return str(ChipFile)
