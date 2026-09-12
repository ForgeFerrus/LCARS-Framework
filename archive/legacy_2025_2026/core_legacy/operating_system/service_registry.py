# Service registry for lcars core operating system.

# Titanium Bridge Migration: from typing import Any, Dict, Optional


class ServiceRegistry:
    def __init__(self) -> None:
        self.services: Dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        self.services[name] = service

    def get(self, name: str) -> Optional[Any]:
        return self.services.get(name)

    def list_services(self) -> list[str]:
        return list(self.services.keys())
