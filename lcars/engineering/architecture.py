from pathlib import Path
from typing import Any

from lcars.base.version import getVersion
from lcars.engineering.controller import AlertLevel, EngineeringController
from lcars.engineering.deflector import DeflectorSystem
from lcars.engineering.maintenance import MaintenanceProtocol
from lcars.engineering.optical import InitializeOpticalNetwork
from lcars.engineering.warpdrive import WarpDrive
from lcars.engineering.collector import CollectorInstance
from lcars.modules.library import IsolinearBank

# Інженерна архітектура керує тільки інженерним шаром.
# Системна аварійка, життєзабезпечення й відновлення живуть окремо у `lcars.system.emergency`.
class EngineeringArchitecture:
    def __init__(self, Kernel: Any | None = None, WorkDir: str | None = None):
        # Базові посилання на ядро та робочий каталог.
        self.Kernel = Kernel
        self.WorkDir = WorkDir
        self.Status = "OFFLINE"
        self.Version = getVersion()
        # Реальні інженерні вузли.
        self.Deflector = DeflectorSystem()
        self.Drive = WarpDrive()
        self.Maintenance = MaintenanceProtocol(WorkDir) if WorkDir else None
        self.Isolinear = IsolinearBank()
        self.Optical = InitializeOpticalNetwork()
        self.Collector = CollectorInstance
        self.Controller = EngineeringController(
            deflector=self.Deflector,
            drive=self.Drive,
            collector=self.Collector,
        )
        # Те, що не належить інженерному шару, лишаємо порожнім.
        self.LifeSupport = None
        self.Sensors = None
        self.Transporter = None
        self.WarpCore = None
        self.Diagnostics = None

        # Реєстр підсистем для швидкого доступу.
        self.Subsystems: dict[str, Any] = {
            "Controller": self.Controller,
            "Deflector": self.Deflector,
            "Drive": self.Drive,
            "Maintenance": self.Maintenance,
            "Isolinear": self.Isolinear,
            "Optical": self.Optical,
            "Collector": self.Collector,
            "LifeSupport": self.LifeSupport,
            "Sensors": self.Sensors,
            "Transporter": self.Transporter,
            "WarpCore": self.WarpCore,
            "Diagnostics": self.Diagnostics,
        }

    def Initialize(self, WorkDir: str | None = None) -> bool:
        # Переводимо архітектуру в робочий стан і підхоплюємо ядро.
        self.Status = "BOOTING"
        if WorkDir:
            self.WorkDir = WorkDir
            if self.Maintenance is not None:
                self.Maintenance.WorkRoot = Path(WorkDir)

        # Інженерний шар стартує з нейтрального режиму.
        self.Controller.ApplyLevel(AlertLevel.GREEN)

        # Якщо ядро вже дало канал подій, підключаємося до нього.
        if self.Kernel is not None and hasattr(self.Kernel, "Events"):
            self.Controller.eventBus = self.Kernel.Events

        self.Status = "ONLINE"
        return True

    def GetSubsystem(self, Name: str) -> Any | None:
        # Доступ до підсистеми по імені.
        return self.Subsystems.get(Name)

    def RegisterSubsystem(self, Name: str, Component: Any) -> None:
        # Додаємо новий вузол в реєстр.
        self.Subsystems[Name] = Component

    def Statusof(self, Component: Any, Fallback: str = "OFFLINE") -> Any:
        # Безпечне отримання статусу від вузла.
        if Component is None:
            return Fallback
        if hasattr(Component, "GetStatus"):
            return Component.GetStatus()
        if hasattr(Component, "Status"):
            return Component.Status()
        return Fallback

    def GetStatus(self) -> dict[str, Any]:
        # Повний знімок інженерної архітектури.
        return {
            "Status": self.Status,
            "Controller": self.Statusof(self.Controller),
            "Deflector": self.Statusof(self.Deflector),
            "Drive": self.Statusof(self.Drive),
            "Maintenance": self.Statusof(self.Maintenance),
            "Isolinear": self.Statusof(self.Isolinear),
            "Optical": self.Statusof(self.Optical),
            "Collector": self.Statusof(self.Collector),
            "LifeSupport": self.Statusof(self.LifeSupport),
            "Sensors": self.Statusof(self.Sensors),
            "Transporter": self.Statusof(self.Transporter),
            "WarpCore": self.Statusof(self.WarpCore),
            "Diagnostics": self.Statusof(self.Diagnostics),
        }

    def SetAlertLevel(self, Level: AlertLevel) -> None:
        # Рівень тривоги передається контролеру.
        self.Controller.ApplyLevel(Level)
