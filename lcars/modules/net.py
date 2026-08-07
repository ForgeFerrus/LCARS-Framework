# ◤ LCARS NETWORK MANAGER — БАЗОВИЙ МОДУЛЬ МЕРЕЖІ
# Модуль для базових мережевих операцій та конфігурації.
# НЕ містить: Service, Database, ODN.Emit — це рівень сервісу.
# ───────────────────────────────────────────────────────────────

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
import urllib.request
import urllib.error
from lcars.core.signal import Transmission
from lcars.base.type import SystemComponent
from lcars.base.version import getVersion
from lcars.engineering.telemetry import EmitTelemetry

__version__ = getVersion()


class NetworkManager(SystemComponent):
    # Базовий менеджер мережевих операцій (Module Layer)
    # Відповідає за: конфігурацію, валідацію URL, базову логіку дозволів.
    # БЕЗ прямих мережевих запитів — це делегується сервісу.

    # Ініціалізація базового менеджера мережевих операцій
    def __init__(self):
        super().__init__()
        
        # УКР: Стан мережевого зєднання
        self.Enabled = True
        self.RequireConfirmation = False
        
        # УКР: Список дозволених доменів (whitelist)
        self.Allowlist: Set[str] = {"localhost", "127.0.0.1"}
        
        # УКР: Налаштування таймаутів
        self.DefaultTimeout = 15
        self.MaxTimeout = 60
        
        # УКР: Ліміти запитів
        self.MaxRetries = 3
        self.RetryDelay = 1.0

    def IsHostAllowed(self, Url: str) -> bool:
        # УКР: Перевірка чи дозволений хост для запиту
        Host = (urlparse(Url).hostname or "").lower()
        if not Host:
            return False
        if Host in ("localhost", "127.0.0.1"):
            return True
        for Domain in self.Allowlist:
            if Host == Domain or Host.endswith("." + Domain):
                return True
        return False

    def AddToAllowlist(self, Domain: str) -> bool:
        # УКР: Додавання домену до списку дозволених
        CleanDomain = Domain.lower().strip()
        if CleanDomain:
            self.Allowlist.add(CleanDomain)
            return True
        return False

    def RemoveFromAllowlist(self, Domain: str) -> bool:
        # УКР: Видалення домену зі списку дозволених
        CleanDomain = Domain.lower().strip()
        if CleanDomain in self.Allowlist:
            self.Allowlist.remove(CleanDomain)
            return True
        return False

    def GetAllowlist(self) -> List[str]:
        # УКР: Отримання списку дозволених доменів
        return sorted(list(self.Allowlist))

    def SetEnabled(self, Status: bool):
        # УКР: Встановлення стану мережі (enabled/disabled)
        self.Enabled = Status

    def IsEnabled(self) -> bool:
        # УКР: Перевірка чи увімкнена мережа
        return self.Enabled

    def GetConfig(self) -> Dict[str, Any]:
        # УКР: Отримання поточної конфігурації
        return {
            "enabled": self.Enabled,
            "require_confirmation": self.RequireConfirmation,
            "allowlist": list(self.Allowlist),
            "default_timeout": self.DefaultTimeout,
            "max_retries": self.MaxRetries
        }

    def LoadConfig(self, Config: Dict[str, Any]):
        # УКР: Завантаження конфігурації
        self.Enabled = Config.get("enabled", True)
        self.RequireConfirmation = Config.get("require_confirmation", False)
        self.DefaultTimeout = Config.get("default_timeout", 15)
        self.MaxRetries = Config.get("max_retries", 3)
        
        # УКР: Завантаження списку дозволених
        AllowlistData = Config.get("allowlist", [])
        if AllowlistData:
            self.Allowlist = set(AllowlistData)

    def ValidateUrl(self, Url: str) -> tuple[bool, str]:
        # УКР: Валідація URL перед запитом
        if not Url:
            return False, "URL_EMPTY"
        if not Url.startswith(("http://", "https://")):
            return False, "URL_INVALID_SCHEME"
        if not self.IsHostAllowed(Url):
            return False, "HOST_BLOCKED"
        if not self.Enabled:
            return False, "NETWORK_DISABLED"
        return True, "OK"

    def CalculateBackoff(self, Attempt: int) -> float:
        # УКР: Розрахунок затримки між повторними спробами
        import math
        return min(self.RetryDelay * math.pow(2, Attempt), 30.0)

    def Ping(self, Url: str) -> bool:
        # Перевірка доступності хоста.
        valid, msg = self.ValidateUrl(Url)
        if not valid:
            EmitTelemetry("NetworkManager", f"PING REJECTED: {msg}")
            return False
            
        req = urllib.request.Request(Url, method="HEAD")
        response = urllib.request.urlopen(req, timeout=self.DefaultTimeout)
        EmitTelemetry("NetworkManager", f"PING SUCCESS: {Url} (HTTP {response.status})")
        return response.status < 400

    def FetchUrl(self, Url: str) -> Tuple[bool, str]:
        # Завантаження вмісту за URL.
        valid, msg = self.ValidateUrl(Url)
        if not valid:
            EmitTelemetry("NetworkManager", f"FETCH REJECTED: {msg}")
            return False, f"ERROR: {msg}"
            
        req = urllib.request.Request(Url, headers={'User-Agent': 'LCARS-Titanium/4.0'})
        response = urllib.request.urlopen(req, timeout=self.DefaultTimeout)
        content = response.read().decode('utf-8')
        EmitTelemetry("NetworkManager", f"FETCH SUCCESS: {Url} (Length: {len(content)})")
        return True, content

__all__ = ["NetworkManager"]
