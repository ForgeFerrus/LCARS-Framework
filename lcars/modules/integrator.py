# ◤ LCARS COMPONENT INTEGRATOR 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/integrator.py
# ОПИС: Інтегратор компонентів LCARS Framework.
#       Вищий рівень над PluginManager — завантажує модулі та плагіни,
#       зв'язує їх між собою, керує залежностями та життєвим циклом.
#       РОЛЬ:
#       1. Реєстрація компонентів системи.
#       2. Розв'язання залежностей (топологічне сортування).
#       3. Запуск/зупинка компонентів у правильному порядку.
#       4. Моніторинг стану (health checks).
#       5. Перезапуск впалих компонентів.
#       6. Сповіщення про зміни стану (event system).
#       7. Валідація залежностей (циклі, відсутні компоненти).
#       8. Конфігурування компонентів.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Strict PascalCase, Pure Classes).
# =============================================================================

from typing import Any, Optional, Dict, List, Callable
from pathlib import Path
from lcars.base.type import LCARS


class ComponentNode:
    # Вузол компонента — обгортка для зберігання метаданих

    def __init__(self, Name: str, Instance: Any, Deps: List[str] = None, Config: Dict = None):
        # Ініціалізація вузла компонента
        self.Name = Name
        self.Instance = Instance
        self.Deps = Deps or []
        self.Config = Config or {}
        self.Status = "registered"
        self.Error: Optional[str] = None
        self.RestartCount = 0
        self.MaxRestarts = 3

    def Start(self) -> bool:
        # Запуск компонента
        if self.Status == "running":
            return True
        if hasattr(self.Instance, 'Start'):
            Result = self.Instance.Start()
            if Result is False:
                self.Status = "failed"
                self.Error = "Start() returned False"
                return False
        self.Status = "running"
        self.Error = None
        return True

    def Stop(self) -> bool:
        # Зупинка компонента
        if self.Status != "running":
            return True
        if hasattr(self.Instance, 'Stop'):
            Result = self.Instance.Stop()
            if Result is False:
                self.Status = "stop_failed"
                return False
        self.Status = "stopped"
        return True

    def Restart(self) -> bool:
        # Перезапуск компонента
        if self.RestartCount >= self.MaxRestarts:
            self.Status = "dead"
            self.Error = f"Max restarts ({self.MaxRestarts}) exceeded"
            return False
        self.RestartCount += 1
        self.Stop()
        return self.Start()

    def HealthCheck(self) -> bool:
        # Перевірка здоров'я компонента
        if self.Status == "dead":
            return False
        if self.Status == "registered":
            return True
        if hasattr(self.Instance, 'HealthCheck'):
            Result = self.Instance.HealthCheck()
            if Result is False:
                self.Status = "unhealthy"
                return False
        if self.Status == "unhealthy":
            self.Status = "running"
        return True


class ComponentIntegrator:
    # Інтегратор компонентів системи — завантажує, зв'язує, керує

    def __init__(self):
        # Ініціалізація порожнього реєстру компонентів
        self.Components: Dict[str, ComponentNode] = {}
        self.StartOrder: List[str] = []
        self.Started: bool = False
        self.EventHandlers: Dict[str, List[Callable]] = {
            "on_start": [],
            "on_stop": [],
            "on_fail": [],
            "on_restart": [],
        }

    def Register(self, Name: str, Instance: Any, Deps: List[str] = None, Config: Dict = None):
        # Реєстрація компонента в системі
        # Name: унікальна назва компонента
        # Instance: екземпляр класу
        # Deps: список залежностей (назви інших компонентів)
        # Config: конфігурація для компонента
        Node = ComponentNode(Name, Instance, Deps, Config)
        self.Components[Name] = Node
        if Name not in self.StartOrder:
            self.StartOrder.append(Name)
        self._ApplyConfig(Name, Config)

    def _ApplyConfig(self, Name: str, Config: Dict = None):
        # Застосування конфігурації до компонента
        if not Config:
            return
        Node = self.Components.get(Name)
        if not Node:
            return
        Instance = Node.Instance
        for Key, Value in Config.items():
            if hasattr(Instance, Key):
                setattr(Instance, Key, Value)

    def Resolve(self) -> List[str]:
        # Розв'язання залежностей — повертає порядок запуску
        # Використовує топологічне сортування
        Resolved: List[str] = []
        Visited: set = set()
        InStack: set = set()

        def Visit(NodeName: str) -> bool:
            # Рекурсивний обхід графа залежностей
            if NodeName in InStack:
                return False
            if NodeName in Visited:
                return True
            InStack.add(NodeName)
            Node = self.Components.get(NodeName)
            if Node:
                for Dep in Node.Deps:
                    if Dep not in self.Components:
                        self._Emit("on_fail", NodeName, f"Missing dependency: {Dep}")
                        return False
                    if not Visit(Dep):
                        return False
            InStack.discard(NodeName)
            Visited.add(NodeName)
            Resolved.append(NodeName)
            return True

        for Name in self.StartOrder:
            if not Visit(Name):
                return []
        return Resolved

    def Validate(self) -> Dict[str, List[str]]:
        # Валідація залежностей — перевірка циклів та відсутніх компонентів
        # Повертає словник помилок: {component_name: [errors]}
        Errors: Dict[str, List[str]] = {}

        for Name, Node in self.Components.items():
            NodeErrors = []
            for Dep in Node.Deps:
                if Dep not in self.Components:
                    NodeErrors.append(f"Missing dependency: {Dep}")
            if Name in Node.Deps:
                NodeErrors.append("Self-dependency")
            if NodeErrors:
                Errors[Name] = NodeErrors

        # Перевірка циклів
        Order = self.Resolve()
        if not Order:
            for Name in self.Components:
                if Name not in Errors:
                    Errors[Name] = ["Part of dependency cycle"]

        return Errors

    def Get(self, Name: str) -> Optional[Any]:
        # Отримання компонента за назвою
        Node = self.Components.get(Name)
        return Node.Instance if Node else None

    def StartAll(self) -> bool:
        # Запуск всіх компонентів у правильному порядку
        if self.Started:
            return True
        Order = self.Resolve()
        if not Order:
            return False
        for Name in Order:
            Node = self.Components.get(Name)
            if Node:
                Success = Node.Start()
                if Success:
                    self._Emit("on_start", Name)
                else:
                    self._Emit("on_fail", Name, Node.Error)
        self.Started = True
        return True

    def StopAll(self) -> bool:
        # Зупинка всіх компонентів у зворотному порядку
        if not self.Started:
            return True
        Order = self.Resolve()
        for Name in reversed(Order):
            Node = self.Components.get(Name)
            if Node:
                Success = Node.Stop()
                if Success:
                    self._Emit("on_stop", Name)
        self.Started = False
        return True

    def Restart(self, Name: str) -> bool:
        # Перезапуск конкретного компонента
        Node = self.Components.get(Name)
        if not Node:
            return False
        Success = Node.Restart()
        if Success:
            self._Emit("on_restart", Name)
        else:
            self._Emit("on_fail", Name, Node.Error)
        return Success

    def HealthCheckAll(self) -> Dict[str, bool]:
        # Перевірка здоров'я всіх компонентів
        Results = {}
        for Name, Node in self.Components.items():
            Results[Name] = Node.HealthCheck()
        return Results

    def GetStatus(self) -> Dict[str, str]:
        # Повертає статус кожного компонента
        Status = {}
        for Name, Node in self.Components.items():
            Status[Name] = Node.Status
        return Status

    def ListComponents(self) -> List[str]:
        # Повертає список всіх зареєстрованих компонентів
        return list(self.Components.keys())

    def On(self, Event: str, Handler: Callable):
        # Підписка на подію
        # Events: "on_start", "on_stop", "on_fail", "on_restart"
        if Event in self.EventHandlers:
            self.EventHandlers[Event].append(Handler)

    def _Emit(self, Event: str, Name: str, Error: str = None):
        # Відправка події обробникам
        for Handler in self.EventHandlers.get(Event, []):
            if Error:
                Handler(Name, Error)
            else:
                Handler(Name)


ManagerRef: Optional[ComponentIntegrator] = None

def GetIntegrator() -> ComponentIntegrator:
    # Отримання єдиного екземпляру інтегратора (singleton)
    global ManagerRef
    if ManagerRef is None:
        ManagerRef = ComponentIntegrator()
    return ManagerRef


def Version() -> str:
    # Отримання версії модуля
    from lcars.base.info import getVersion
    return getVersion()


__all__ = ['ComponentIntegrator', 'GetIntegrator', 'ComponentNode']
