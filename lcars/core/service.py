# ◤ LCARS SERVICE CONTRACT ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Layer 2 Foundation. Контракт життєвого циклу системного сервісу.
# Цей контракт НЕЗМІННИЙ. Всі сервіси імплементують його.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict, Optional, Set, Any

if TYPE_CHECKING:
    from .kernel import Kernel

from lcars.base.type import LCARS
# Базовий клас для всіх системних сервісів LCARS.
# Сервіс — фоновий компонент що надає функціональність системі.
# Lifecycle: Register → OnInit(Kernel) → OnStart() → [Running] → OnStop()
class Service(LCARS):
    Name: str = "unnamed"
    Dependencies: List[str] = []

    # Конструктор сервісу. Генерує Id якщо не надано.
    def __init__(self, Id: str | None = None):
        super().__init__(Id=Id or f"svc_{self.Name}")
        from lcars.core.signal import ODN
        self.ODN = ODN

    # Ядро доступне. Отримати конфігурацію та ресурси.
    def OnInit(self, KernelRef: Kernel) -> None:
        self.Kernel = KernelRef

    # Публічний метод ініціалізації.
    def Init(self, KernelRef: Kernel) -> None:
        self.OnInit(KernelRef)

    # Запуск. Почати обробку.
    def OnStart(self) -> None:
        pass

    # Публічний метод запуску.
    def Start(self) -> None:
        self.OnStart()

    # Зупинка. Звільнити всі ресурси.
    def OnStop(self) -> None:
        pass

    # Публічний метод зупинки.
    def Stop(self) -> None:
        self.OnStop()

    # Перевірка працездатності.
    def Health(self) -> bool:
        return True

    # Публічна перевірка здоров'я.
    def Check(self) -> bool:
        return self.Health()


# Реєстр сервісів. Управляє реєстрацією та життєвим циклом сервісів.
class ServiceRegistry:
    # Конструктор реєстру. Ініціалізує порожні словники.
    def __init__(self):
        self.Services: Dict[str, Service] = {}
        self.StartOrder: List[str] = []

    # Реєстрація сервісу. Перевіряє унікальність за Name.
    def Register(self, Svc: Service) -> None:
        if Svc.Name in self.Services:
            raise ValueError(f"Service already registered: {Svc.Name}")
        self.Services[Svc.Name] = Svc

    # Публічний метод реєстрації.
    def Add(self, Svc: Service) -> None:
        self.Register(Svc)

    # Отримання сервісу за іменем. Повертає None якщо не знайдено.
    def Get(self, Name: str) -> Optional[Service]:
        return self.Services.get(Name)

    # Отримання сервісу за іменем. Кидає KeyError якщо не знайдено.
    def Require(self, Name: str) -> Service:
        Svc = self.Services.get(Name)
        if Svc is None:
            raise KeyError(f"Service not found: {Name}")
        return Svc

    # Публічний метод вимоги сервісу.
    def Need(self, Name: str) -> Service:
        return self.Require(Name)

    # Перевірка здоров'я всіх сервісів.
    # Повертає словник з результатами перевірки для кожного сервісу.
    def HealthCheck(self) -> Dict[str, bool]:
        Result: Dict[str, bool] = {}
        for Name, Svc in self.Services.items():
            Result[Name] = Svc.Health()
        return Result

    # Публічна перевірка здоров'я.
    def Health(self) -> Dict[str, bool]:
        return self.HealthCheck()

    # Запуск всіх сервісів з розв'язанням залежностей.
    # Повертає список помилок (порожній якщо все успішно).
    def StartAll(self, KernelRef: Kernel) -> List[str]:
        Errors: List[str] = []
        Started: Set[str] = set()

        # Внутрішня функція розв'язання залежностей рекурсивно.
        def Resolve(Name: str, Chain: frozenset) -> bool:
            if Name in Started:
                return True
            Svc = self.Services.get(Name)
            if Svc is None:
                Errors.append(f"Unknown dependency: {Name}")
                return False
            # Перевірка на циклічну залежність.
            if Name in Chain:
                Errors.append(f"Circular dependency: {Name}")
                return False

            # Рекурсивний запуск залежностей.
            for Dep in (Svc.Dependencies or []):
                if not Resolve(Dep, Chain | {Name}):
                    Errors.append(f"Required by: {Name}")
                    return False

            Svc.OnInit(KernelRef)
            Svc.OnStart()
            Started.add(Name)
            self.StartOrder.append(Name)
            return True

        # Запуск кожного сервісу через розв'язувач залежностей.
        for Name in list(self.Services):
            Resolve(Name, frozenset())

        return Errors

    # Публічний метод запуску.
    def Start(self, KernelRef: Kernel) -> List[str]:
        return self.StartAll(KernelRef)

    # Зупинка всіх сервісів у зворотному порядку запуску.
    def StopAll(self) -> None:
        for Name in reversed(self.StartOrder):
            Svc = self.Services.get(Name)
            if Svc:
                Svc.OnStop()
        self.StartOrder.clear()

    # Публічний метод зупинки.
    def Stop(self) -> None:
        self.StopAll()

    # Повертає список імен зареєстрованих сервісів.
    def Names(self) -> List[str]:
        return list(self.Services.keys())

    # Публічний метод отримання списку сервісів.
    def List(self) -> List[str]:
        return self.Names()

__all__ = [
    "Service",
    "ServiceRegistry"
]
