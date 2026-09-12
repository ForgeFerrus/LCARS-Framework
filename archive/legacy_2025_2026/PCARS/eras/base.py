# Base era abstractions for PCARS.

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type

from ..service_registry import ServiceRegistry


@dataclass
class EraSpec:
    key: str
    display_name: str
    period: str
    description: str
    features: List[str] = field(default_factory=list)


class BaseEra:
    SPEC: EraSpec

    def __init__(self, services: ServiceRegistry) -> None:
        self.Services = services
        self.Active = False

    def Activate(self) -> Dict[str, Any]:
        self.Active = True
        return {
            "era": self.SPEC.key,
            "display_name": self.SPEC.display_name,
            "status": "activated",
            "features": self.SPEC.features,
        }

    def Deactivate(self) -> Dict[str, Any]:
        self.Active = False
        return {
            "era": self.SPEC.key,
            "status": "deactivated",
        }

    def ExecuteFeature(self, feature_name: str, payload: Any | None = None) -> Dict[str, Any]:
        if feature_name not in self.SPEC.features:
            return {
                "error": "feature_not_available",
                "feature": feature_name,
                "available": self.SPEC.features,
            }
        return {
            "era": self.SPEC.key,
            "feature": feature_name,
            "result": "executed",
            "payload": payload,
        }


class EraRegistry:
    Eras: Dict[str, Type[BaseEra]] = {}

    @classmethod
    def Register(cls, era_class: Type[BaseEra]) -> Type[BaseEra]:
        if not issubclass(era_class, BaseEra):
            raise TypeError("EraRegistry can only register BaseEra subclasses")
        cls.Eras[era_class.SPEC.key] = era_class
        return era_class

    @classmethod
    def Create(cls, key: str, services: ServiceRegistry) -> BaseEra:
        era_class = cls.Eras.get(key)
        if era_class is None:
            raise KeyError(f"Era '{key}' is not registered")
        return era_class(services)

    @classmethod
    def ListKeys(cls) -> List[str]:
        return list(cls.Eras.keys())

    @classmethod
    def Specs(cls) -> List[EraSpec]:
        return [era_class.SPEC for era_class in cls.Eras.values()]

    @classmethod
    def GetSpec(cls, key: str) -> Optional[EraSpec]:
        era_class = cls.Eras.get(key)
        return era_class.SPEC if era_class is not None else None
