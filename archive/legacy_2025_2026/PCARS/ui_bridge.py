# UI bridge for PCARS.

from typing import Any


class UIBridge:
    def __init__(self) -> None:
        self.Responses: dict[str, Any] = {}

    def SendCommand(self, name: str, payload: Any) -> None:
        self.Responses[name] = payload

    def GetResponse(self, name: str) -> Any:
        return self.Responses.get(name)
