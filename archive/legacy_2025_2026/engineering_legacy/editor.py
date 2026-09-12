# LCARS INTERFACE EDITOR - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Редагування UI елементів з повним контролем та перемиканням режимів

# Titanium Bridge Migration: from typing import Any
# Titanium Bridge Migration: from enum import Enum, auto

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

    def __init__(self):
        super().__init__()
        self.Elements: list[dict[str, Any]] = []
        self.SelectedId: str | None = None
        self.ModeManager = ModeManager()
        self.Clipboard: dict | None = None
        self.GridSize = 5
        self.IsEnabled = False

    def Enable(self) -> None:
        # Активація редактора
        self.IsEnabled = True
        self.ModeManager.EnterEditMode()
        self.ModeChanged.Emit(SystemMode.EDIT)

    def Disable(self) -> None:
        # Деактивація редактора
        self.IsEnabled = False
        self.ModeManager.ExitEditMode()
        self.ModeChanged.Emit(self.ModeManager.GetMode())

    def ToggleMode(self) -> SystemMode:
        # Перемикання режиму однією кнопкою
        if self.ModeManager.IsEditMode():
            self.Disable()
        else:
            self.Enable()
        return self.ModeManager.GetMode()

    def AddElement(self, ElementType: str, Position: tuple[int, int],
                   Properties: dict | None = None) -> dict[str, Any]:
        # Створення нового UI елемента
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

    def SelectElement(self, ElementId: str) -> dict[str, Any] | None:
        # Вибір елемента за ID
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.SelectedId = ElementId
                return El
        return None

    def UpdateElement(self, ElementId: str, Properties: dict[str, Any]) -> bool:
        # Оновлення властивостей
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

    def MoveElement(self, ElementId: str, NewPosition: tuple[int, int]) -> bool:
        # Переміщення елемента
        return self.UpdateElement(ElementId, {"Position": NewPosition})

    def ResizeElement(self, ElementId: str, NewSize: tuple[int, int]) -> bool:
        # Зміна розміру
        return self.UpdateElement(ElementId, {"Size": NewSize})

    def DeleteElement(self, ElementId: str) -> bool:
        # Видалення елемента
        for I, El in enumerate(self.Elements):
            if El["Id"] == ElementId:
                del self.Elements[I]
                if self.SelectedId == ElementId:
                    self.SelectedId = None
                self.ElementDeleted.Emit(ElementId)
                return True
        return False

    def CopyElement(self, ElementId: str) -> bool:
        # Копіювання в буфер
        for El in self.Elements:
            if El["Id"] == ElementId:
                self.Clipboard = El.copy()
                self.Clipboard["Id"] = f"{El['Id']}_copy"
                return True
        return False

    def PasteElement(self, Position: tuple[int, int] | None = None) -> dict[str, Any] | None:
        # Вставка з буфера
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

    def GetElements(self) -> list[dict[str, Any]]:
        # Отримання всіх елементів
        return self.Elements.copy()

    def Clear(self) -> None:
        # Очищення
        self.Elements.clear()
        self.SelectedId = None
        self.Clipboard = None

    def CanPerformOperation(self, Operation: EditOperation) -> bool:
        # Перевірка дозволу операції
        if not self.IsEnabled:
            return Operation in (EditOperation.VIEW, EditOperation.NAVIGATE)
        return self.ModeManager.State.Can(Operation.name.lower())

# Експорт
Editor = InterfaceEditor
EditSystem = InterfaceEditor
