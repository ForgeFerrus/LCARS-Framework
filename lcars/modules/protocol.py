# ◤ TITANIUM LCARS :: PROTOCOL MANAGER // STARFLEET GENERAL ORDERS 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/protocol.py
# ОПИС: Менеджер протоколів та директив Зоряного Флоту (Starfleet Protocols).
#       Керує виконанням загальних наказів (General Orders), карантинними,
#       оборонними та аварійними процедурами зорельота.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from typing import Any, Optional

from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission, ODN

class ProtocolManager(SystemComponent):

    Instance = None
    ProtocolChanged = Transmission(str, bool)

    def __new__(cls):
        if cls.Instance is None:
            cls.Instance = super(ProtocolManager, cls).__new__(cls)
            SystemComponent.__init__(cls.Instance, SystemId="Module.ProtocolManager")
            cls.Instance.ActiveProtocols: dict[str, dict[str, Any]] = {}
            cls.Instance.RegisterCanonicalProtocols()
        return cls.Instance

    @classmethod
    def GetInstance(cls) -> "ProtocolManager":
        return cls()

    def RegisterCanonicalProtocols(self) -> None:
        """Реєстрація базових протоколів Зоряного Флоту."""
        self.KnownProtocols = {
            "GeneralOrder1": {"Name": "Prime Directive", "Priority": 1, "Active": True},
            "GeneralOrder4": {"Name": "Emergency Command Transfer", "Priority": 2, "Active": False},
            "GeneralOrder7": {"Name": "Talos IV Quarantine", "Priority": 1, "Active": True},
            "OmegaDirective": {"Name": "Omega Molecule Containment", "Priority": 0, "Active": False},
            "Quarantine": {"Name": "Bio-hazard Containment", "Priority": 3, "Active": False},
            "SilentRunning": {"Name": "Minimal EM Emission", "Priority": 4, "Active": False},
            "SelfDestruct": {"Name": "Vessel Auto-Destruct Sequence", "Priority": 0, "Active": False},
        }

    def EngageProtocol(self, ProtocolKey: str) -> bool:
        if ProtocolKey in self.KnownProtocols:
            self.KnownProtocols[ProtocolKey]["Active"] = True
            self.ProtocolChanged.Emit(ProtocolKey, True)
            ODN.Transmit("Protocol.Engaged", Protocol=ProtocolKey)
            return True
        return False

    def DisengageProtocol(self, ProtocolKey: str) -> bool:
        if ProtocolKey in self.KnownProtocols:
            self.KnownProtocols[ProtocolKey]["Active"] = False
            self.ProtocolChanged.Emit(ProtocolKey, False)
            ODN.Transmit("Protocol.Disengaged", Protocol=ProtocolKey)
            return True
        return False

    def IsActive(self, ProtocolKey: str) -> bool:
        Proto = self.KnownProtocols.get(ProtocolKey)
        return bool(Proto.get("Active", False)) if Proto else False

    def GetActiveProtocols(self) -> list[str]:
        return [Key for Key, Val in self.KnownProtocols.items() if Val.get("Active")]

    def List(self) -> list[str]:
        return list(self.KnownProtocols.keys())

    def GetStatus(self) -> dict[str, Any]:
        return {
            "ActiveCount": len(self.GetActiveProtocols()),
            "ActiveProtocols": self.GetActiveProtocols(),
            "TotalProtocols": len(self.KnownProtocols),
        }

# Глобальний синглтон
Protocols = ProtocolManager.GetInstance

__all__ = [
    "ProtocolManager",
    "Protocols",
]
