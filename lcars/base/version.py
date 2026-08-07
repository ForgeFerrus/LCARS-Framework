# ◤ TITANIUM VERSION INFO
# Minimal LCARS base version module for package metadata.
from __future__ import annotations
# Метадані версії пакета lcars
__version__ = "0.3.0-alpha"
__title__ = "LCARS Framework"
__description__ = "Titanium Master Architecture"
# Повертає рядок версії пакета
def GetVersion():
    return __version__

getVersion = GetVersion

def GetMetadata() -> dict[str, str]:
    return {
        "title": __title__,
        "version": __version__,
        "description": __description__,
        "status": "alpha",
        "build": "2026.02.26"
    }

getMetadata = GetMetadata

__all__ = ["GetVersion", "GetMetadata", "getVersion", "getMetadata"]
