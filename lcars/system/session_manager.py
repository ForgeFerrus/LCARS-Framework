# LCARS FRAMEWORK SESSION MANAGER
# СТАНДАРТ: Titanium (Zero-Except, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from typing import Optional
from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import Version

class SessionManager(SystemComponent):
    Instance = None
    _Locked = False
    _CurrentUser: Optional[str] = None
    _SessionToken: Optional[str] = None

    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance = super().__new__(cls)
            cls.Instance.Initialized = True
        return cls.Instance

    def __init__(self):
        super().__init__(SystemId="System.Session")

    @classmethod
    def GetInstance(cls) -> SessionManager:
        if cls.Instance is None:
            cls.Instance = SessionManager()
        return cls.Instance

    def Lock(self) -> None:
        self.__class__._Locked = True

    def Unlock(self) -> None:
        self.__class__._Locked = False

    def IsLocked(self) -> bool:
        return self.__class__._Locked

    def GetCurrentUser(self) -> Optional[str]:
        return self.__class__._CurrentUser

    def SetCurrentUser(self, User: Optional[str]) -> None:
        self.__class__._CurrentUser = User

    def GetSessionToken(self) -> Optional[str]:
        return self.__class__._SessionToken

    def SetSessionToken(self, Token: Optional[str]) -> None:
        self.__class__._SessionToken = Token

    # Backward compatibility aliases (snake_case)
    lock = Lock
    unlock = Unlock
    is_locked = IsLocked
    get_current_user = GetCurrentUser
    set_current_user = SetCurrentUser
    get_session_token = GetSessionToken
    set_session_token = SetSessionToken

Session = SessionManager
__all__ = ["SessionManager", "Session"]