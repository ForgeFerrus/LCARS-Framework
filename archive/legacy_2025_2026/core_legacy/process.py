# LCARS PROCESS SYSTEM
# Core program lifecycle and the process table used by Kernel.

from __future__ import annotations
# Titanium Bridge Migration: from typing import TYPE_CHECKING, Any, Dict, List, Optional
# Titanium Bridge Migration: from datetime import datetime
# Titanium Bridge Migration: import threading

if TYPE_CHECKING:
    from .kernel import Kernel

# ◤ LCARS APPLICATION CONTRACT ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Layer 2 Foundation. Контракт життєвого циклу програми.
# Цей контракт НЕЗМІННИЙ. Всі програми імплементують його.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Базовий клас для всіх програм LCARS.
# Програма — інтерфейс користувача що запускається на робочому столі.
# Lifecycle: Launch → OnLaunch(Kernel) → CreateUI() → [Running]
#            → OnFocus() / OnMinimize() → OnClose()
class Application:

    AppId: str = "unnamed"
    Title: str = "LCARS Application"
    Icon: str = ""
    Category: str = "general"

    # Запуск програми. Зберегти посилання на ядро.
    def OnLaunch(self, KernelRef: Kernel) -> None:
        self.Kernel = KernelRef

    # Створити та повернути головний віджет.
    def CreateUI(self) -> Any:
        return None

    # Програму виведено на передній план.
    def OnFocus(self) -> None:
        pass

    # Програму мінімізовано або сховано.
    def OnMinimize(self) -> None:
        pass

    # Програму закрито. Звільнити ресурси.
    def OnClose(self) -> None:
        pass


class ProcessEntry:
    Counter = 0
    CounterLock = threading.Lock()

    def __init__(self, App: Application):
        with ProcessEntry.CounterLock:
            ProcessEntry.Counter += 1
            self.Pid = ProcessEntry.Counter
        self.App = App
        self.Started = datetime.now()
        self.Widget = None


class ProcessTable:
    def __init__(self):
        self.Table: Dict[int, ProcessEntry] = {}

    def Add(self, App: Application) -> ProcessEntry:
        Entry = ProcessEntry(App)
        self.Table[Entry.Pid] = Entry
        return Entry

    def Get(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.get(Pid)

    def Find(self, AppId: str) -> Optional[ProcessEntry]:
        for Entry in self.Table.values():
            if Entry.App.AppId == AppId:
                return Entry
        return None

    def Remove(self, Pid: int) -> Optional[ProcessEntry]:
        return self.Table.pop(Pid, None)

    def All(self) -> List[ProcessEntry]:
        return list(self.Table.values())

    def Count(self) -> int:
        return len(self.Table)

    def KillAll(self) -> None:
        for Entry in list(self.Table.values()):
            Entry.App.OnClose()
        self.Table.clear()
