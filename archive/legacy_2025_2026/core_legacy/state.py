# LCARS FRAMEWORK v0.9.0-PRE
# Сховище стану системи (State Vault)
# Просте key-value сховище з thread-safe доступом та подіями
from __future__ import annotations
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .kernel import EventBus


class StateVault:
    # Просте сховище ключ-значення
    # Генерує події при зміні даних через EventBus

    def __init__(self, Bus: 'EventBus'):
        self.Bus = Bus
        self.Data: Dict[str, Any] = {}
        self.Lock = threading.Lock()

    def Set(self, Key: str, Value: Any) -> None:
        with self.Lock:
            Old = self.Data.get(Key)
            self.Data[Key] = Value
        self.Bus.Emit("state.set", "StateVault", Key=Key, Value=Value, Old=Old)

    def Get(self, Key: str, Default: Any = None) -> Any:
        with self.Lock:
            return self.Data.get(Key, Default)

    def Has(self, Key: str) -> bool:
        with self.Lock:
            return Key in self.Data

    def Delete(self, Key: str) -> None:
        with self.Lock:
            self.Data.pop(Key, None)
        self.Bus.Emit("state.delete", "StateVault", Key=Key)

    def Keys(self) -> List[str]:
        with self.Lock:
            return list(self.Data.keys())

    def Snapshot(self) -> Dict[str, Any]:
        with self.Lock:
            return dict(self.Data)


__all__ = ["StateVault"]
