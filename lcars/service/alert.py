from typing import List, TYPE_CHECKING
from lcars.core.service import Service

if TYPE_CHECKING:
    from lcars.core.kernel import Kernel

# Сервіс системи тривог для керування рівнями безпеки
class AlertService(Service):
    Name = "alert"
    Dependencies: List[str] = []

    def __init__(self):
        super().__init__(Id="svc_alert")
        self.Level = "GREEN"

    # Встановлення рівня тривоги з нормалізацією значення
    def SetLevel(self, NewLevel: str) -> None:
        Old = self.Level
        Normalized = NewLevel.upper().strip()
        if Normalized in ("RED", "YELLOW", "GREEN", "NORMAL"):
            if Normalized == "NORMAL":
                Normalized = "GREEN"
            self.Level = Normalized
            if getattr(self, 'Kernel', None) and self.Kernel.State:
                self.Kernel.State.Set("alert.level", self.Level)
            
            # Емісія через локальний ODN та Kernel Events для сумісності
            if hasattr(self, 'ODN'):
                self.ODN.Emit("alert.changed", "alert", Level=self.Level, Previous=Old)
            if getattr(self, 'Kernel', None) and self.Kernel.Events:
                self.Kernel.Events.Emit("alert.changed", "alert", Level=self.Level, Previous=Old)

    # Отримання поточного рівня тривоги
    def GetLevel(self) -> str:
        return self.Level

    # Альтернативний метод встановлення рівня
    def Set(self, NewLevel: str) -> None:
        self.SetLevel(NewLevel)

    # Альтернативний метод отримання рівня
    def Get(self) -> str:
        return self.GetLevel()

    def __repr__(self) -> str:
        return f"<Service:{self.Name}>"

Alert = AlertService
