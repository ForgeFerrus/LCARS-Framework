# LCARS INTERFACE EDITOR - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Редагування UI елементів з повним контролем та перемиканням режимів

from typing import Any
from enum import Enum, auto

from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission
from lcars.modules.mode import ModeManager, SystemMode

# Операції редагування UI
class EditOperation(Enum):
    VIEW = auto()       # Перегляд
    INTERACT = auto()   # Взаємодія
    NAVIGATE = auto()   # Навігація
    EDIT = auto()       # Редагування властивостей
    MOVE = auto()       # Переміщення
    RESIZE = auto()     # Зміна розміру
    DELETE = auto()     # Видалення
    CREATE = auto()     # Створення

# Редактор інтерфейсу LCARS -- Повний контроль над UI елементами
class InterfaceEditor(SystemComponent):
    # Сигнал зміни режиму
    ModeChanged = Transmission(SystemMode)
    # Сигнал оновлення елемента
    ElementUpdated = Transmission(str, dict)
    # Сигнал видалення елемента
    ElementDeleted = Transmission(str)

    # Ініціалізація редактора інтерфейсу.
    def __init__(self):
        super().__init__()
        self.Elements: list[dict[str, Any]] = []
        self.SelectedId: str | None = None
        self.ModeManager = ModeManager()
        self.Clipboard: dict | None = None
        self.GridSize = 5
        self.IsEnabled = False

    # Активація редактора.
    def Enable(self) -> None:
        self.IsEnabled = True
        self.ModeManager.EnterEditMode()
        self.ModeChanged.Emit(SystemMode.EDIT)

    # Деактивація редактора.
    def Disable(self) -> None:
        self.IsEnabled = False
        self.ModeManager.ExitEditMode()
        self.ModeChanged.Emit(self.ModeManager.GetMode())

    # Перемикання режиму однією кнопкою.
    def ToggleMode(self) -> SystemMode:
        if self.ModeManager.IsEditMode():
            self.Disable()
        else:
            self.Enable()
        return self.ModeManager.GetMode()

    # Створення нового UI елемента.
    def AddElement(self, ElementType: str, Position: tuple[int, int],
                   Properties: dict | None = None) -> dict[str, Any]:
        Properties = Properties or {}
        ElementId = f"{ElementType}_{len(self.Elements)}"
        Element = {
            "Id": ElementId,
            "Type": ElementType,
            "Position": Position,
            "Size": Properties.get("Size", (100, 50)),
            "Color": Properties.get("Color", "var(--accent)"),
            "Text": Properties.get("Text", "NODE"),
            "Properties": Properties,
        }
        self.Elements.append(Element)
        self.ElementUpdated.Emit(ElementId, Element)
        return Element

    # Вибір елемента за ID.
    def SelectElement(self, ElementId: str) -> dict[str, Any] | None:
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.SelectedId = ElementId
                return El
        return None

    # Оновлення властивостей елемента.
    def UpdateElement(self, ElementId: str, Properties: dict[str, Any]) -> bool:
        for El in self.Elements:
            if El["Id"] == ElementId:
                El["Properties"].update(Properties)
                if "Position" in Properties:
                    El["Position"] = Properties["Position"]
                if "Size" in Properties:
                    El["Size"] = Properties["Size"]
                self.ElementUpdated.Emit(ElementId, El)
                return True
        return False

    # Переміщення елемента.
    def MoveElement(self, ElementId: str, NewPosition: tuple[int, int]) -> bool:
        return self.UpdateElement(ElementId, {"Position": NewPosition})

    # Зміна розміру елемента.
    def ResizeElement(self, ElementId: str, NewSize: tuple[int, int]) -> bool:
        return self.UpdateElement(ElementId, {"Size": NewSize})

    # Видалення елемента.
    def DeleteElement(self, ElementId: str) -> bool:
        for I, El in enumerate(self.Elements):
            if El["Id"] == ElementId:
                del self.Elements[I]
                if self.SelectedId == ElementId:
                    self.SelectedId = None
                self.ElementDeleted.Emit(ElementId)
                return True
        return False

    # Копіювання елемента в буфер.
    def CopyElement(self, ElementId: str) -> bool:
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.Clipboard = El.copy()
                self.Clipboard["Id"] = f"{El['Id']}_copy"
                return True
        return False

    # Вставка елемента з буфера.
    def PasteElement(self, Position: tuple[int, int] | None = None) -> dict[str, Any] | None:
        if not self.Clipboard:
            return None
        NewElement = self.Clipboard.copy()
        NewElement["Id"] = f"{self.Clipboard['Type']}_{len(self.Elements)}"
        if Position:
            NewElement["Position"] = Position
        else:
            NewElement["Position"] = (NewElement["Position"][0] + 10,
                                      NewElement["Position"][1] + 10)
        self.Elements.append(NewElement)
        self.ElementUpdated.Emit(NewElement["Id"], NewElement)
        return NewElement

    # Отримання списку всіх елементів.
    def GetElements(self) -> list[dict[str, Any]]:
        return self.Elements.copy()

    # Очищення всіх елементів.
    def Clear(self) -> None:
        self.Elements.clear()
        self.SelectedId = None
        self.Clipboard = None

    # Перевірка дозволу операції.
    def CanPerformOperation(self, Operation: EditOperation) -> bool:
        if not self.IsEnabled:
            return Operation in (EditOperation.VIEW, EditOperation.NAVIGATE)
        return self.ModeManager.State.Can(Operation.name.lower())

# Експорт
Editor = InterfaceEditor
EditSystem = InterfaceEditor
