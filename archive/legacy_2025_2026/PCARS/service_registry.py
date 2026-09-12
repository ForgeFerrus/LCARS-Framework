# Service registry for PCARS.

from typing import Any, Dict, Optional


class ServiceRegistry:
    def __init__(self) -> None:
        self.Services: Dict[str, Any] = {}

    def Register(self, name: str, service: Any) -> None:
        self.Services[name] = service

    def Get(self, name: str) -> Optional[Any]:
        return self.Services.get(name)

    def ListServices(self) -> list[str]:
        return list(self.Services.keys())
