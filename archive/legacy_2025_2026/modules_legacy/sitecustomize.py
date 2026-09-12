# ◤ TITANIUM SITE CUSTOMIZE
# Налаштування системних шляхів LCARS.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.service.bridge import Bridge

class SiteConfig(LCARS):
    @staticmethod
    def InitializePath() -> None:
        Path = Bridge().Load("System.Path")
        Sys = Bridge().Load("System.Sys")
        if Path and Sys and hasattr(Sys, "path"):
            Root = Path(__file__).resolve().parents[2]
            if str(Root) not in Sys.path:
                Sys.path.insert(0, str(Root))

SiteConfig.InitializePath()

__all__ = ["SiteConfig"]
