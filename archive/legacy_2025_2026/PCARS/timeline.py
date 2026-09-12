# Era timeline manager for PCARS.

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .service_registry import ServiceRegistry
from .eras.base import BaseEra, EraRegistry, EraSpec


class EraTimeline:
    def __init__(self, services: ServiceRegistry) -> None:
        self.Services = services
        self.CurrentEra: Optional[BaseEra] = None

    def LoadEras(self) -> List[EraSpec]:
        from .eras import cars22, pcars23, lcars2425, tkars2930  # noqa: F401
        return self.AvailableEras()

    def AvailableEras(self) -> List[EraSpec]:
        return EraRegistry.Specs()

    def SelectEra(self, key: str) -> Dict[str, Any]:
        if self.CurrentEra:
            self.CurrentEra.Deactivate()
        self.CurrentEra = EraRegistry.Create(key, self.Services)
        return self.CurrentEra.Activate()

    def GetCurrentEra(self) -> Optional[BaseEra]:
        return self.CurrentEra

    def CurrentEraInfo(self) -> Optional[Dict[str, Any]]:
        if self.CurrentEra is None:
            return None
        return {
            "key": self.CurrentEra.SPEC.key,
            "display_name": self.CurrentEra.SPEC.display_name,
            "period": self.CurrentEra.SPEC.period,
            "description": self.CurrentEra.SPEC.description,
            "features": self.CurrentEra.SPEC.features,
            "active": self.CurrentEra.Active,
        }

    def ExecuteCurrentFeature(self, feature_name: str, payload: Any | None = None) -> Dict[str, Any]:
        if self.CurrentEra is None:
            return {"error": "no_active_era"}
        return self.CurrentEra.ExecuteFeature(feature_name, payload)
