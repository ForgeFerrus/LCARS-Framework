# LCARS FRAMEWORK v0.1.0-alpha
# Bootstrap module - system entry point
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional

from .kernel import Kernel
from .service import Service, ServiceRegistry, Configuration, AlertSubsystem
from ..modules.memory import MemorySubsystem


def Start(Gui: bool = True, ExtraServices: Optional[list] = None) -> Kernel:
    # Єдина точка входу в LCARS
    K = Kernel()

    # Реєструємо базові сервіси
    K.Register(Configuration())
    K.Register(AlertSubsystem())
    K.Register(MemorySubsystem())

    # Додаткові сервіси якщо передані
    if ExtraServices:
        for Svc in ExtraServices:
            K.Register(Svc)

    K.Boot()
    return K


def GetKernel() -> Kernel:
    # Отримати єдиний екземпляр Kernel
    return Kernel()
