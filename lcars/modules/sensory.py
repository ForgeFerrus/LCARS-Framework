# ◤ TITANIUM SENSORY SYSTEM
# LCARS Framework :: SENSOR_GRID // ENV_SCANNER // NO_Q PROTOCOL
# ОПИС: Агрегатор даних від усіх сенсорів (апаратних та системних).
# СТАНДАРТ: Titanium CamelCase, Zero-Except.

import psutil
from lcars.base.type import LCARS, SystemComponent, Directive
from lcars.core.signal import ODN, Transmission
from lcars.base.info import getVersion

__version__ = getVersion()

class SensorySystem(SystemComponent):
    def __init__(self, parent=None):
        super().__init__()
        self.environment_updated = Transmission("Sensory.Environment", dict)
        self.engineering_updated = Transmission("Sensory.Engineering", dict)
        self.framework_updated = Transmission("Sensory.Framework", dict)
        if parent is not None:
            getattr(self, "setParent", lambda p: None)(parent)
        TimerClass = getattr(LCARS, "Timer", None)
        if TimerClass and callable(TimerClass):
            self.update_timer = TimerClass()
            if hasattr(self.update_timer, "timeout"):
                self.update_timer.timeout.connect(self.ScanAllSensors)
                self.update_timer.start(5000)
        ODN.Transmit("Telemetry.Event", Source="Sensory", Status="Sensor grid online.")

    def GetCurrentData(self) -> dict:
        return {
            **self.GetEnvMatrix(),
            **self.GetEngMatrix(),
            **self.GetFrameworkMatrix()
        }

    def ScanAllSensors(self):
        import time
        from datetime import datetime
        NowDt = datetime.now()
        TaskId = f"SC-{NowDt.microsecond % 10000:04d}"
        EnvData = self.GetEnvMatrix()
        if hasattr(self.environment_updated, "Emit"):
            self.environment_updated.Emit(EnvData)
        EngData = self.GetEngMatrix()
        if hasattr(self.engineering_updated, "Emit"):
            self.engineering_updated.Emit(EngData)
        FrameData = self.GetFrameworkMatrix()
        if hasattr(self.framework_updated, "Emit"):
            self.framework_updated.Emit(FrameData)
        Metrics = {**EnvData, **EngData, **FrameData}
        ODN.Emit("Telemetry.Metrics", "Sensory", str(Metrics))
        if EngData.get('system_load', 0) > 90:
            ODN.Emit("Telemetry.Warn", "Sensory", f"TASK_WARN: {TaskId}. Core Overload: {EngData['system_load']}%")
        if NowDt.second < 5:
            ODN.Emit("Telemetry.Report", "Sensory", f"TASK_REPORT: {TaskId}. Matrix Balanced.")

    def GetEnvMatrix(self) -> dict:
        Temp = 0
        if hasattr(psutil, "sensors_temperatures"):
            TempSensors = psutil.sensors_temperatures()
            if TempSensors and 'coretemp' in TempSensors:
                Temp = TempSensors['coretemp'][0].current

        # Деталізований статус живлення
        Battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
        Power = Battery.percent if Battery else 100
        PowerDetails = {
            "percent": Power,
            "power_plugged": getattr(Battery, "power_plugged", True) if Battery else True,
            "secsleft": getattr(Battery, "secsleft", -1) if Battery else -1
        }

        # Усі розділи дисків
        Partitions = {}
        if hasattr(psutil, "disk_partitions") and hasattr(psutil, "disk_usage"):
            for P in psutil.disk_partitions():
                if 'cdrom' not in getattr(P, "opts", ""):
                    try:
                        Partitions[P.mountpoint] = psutil.disk_usage(P.mountpoint).percent
                    except Exception:
                        pass
        import os
        RootDisk = os.path.splitdrive(os.getcwd())[0] + "\\" if os.name == "nt" else "/"
        Disk = psutil.disk_usage(RootDisk) if hasattr(psutil, "disk_usage") else None
        IoCounters = psutil.disk_io_counters()

        # Віртуальні метрики LCARS
        EpsFlow = round(Power * 0.95, 1)
        
        import sys
        return {
            "core_temp": Temp,
            "power_level": Power,
            "eps_flow": EpsFlow,
            "os_platform": sys.platform,
            "status": "STABLE"
        }

    def GetEngMatrix(self) -> dict:
        Mem = psutil.virtual_memory()
        return {
            "system_load": psutil.cpu_percent(),
            "memory_usage": Mem.percent,
            "ram_allocated_mb": round(Mem.used / (1024**2), 1),
            "active_processes": len(psutil.pids()),
            "eps_status": "NOMINAL",
            "shield_status": "NONE"
        }

    def GetFrameworkMatrix(self) -> dict:
        import time
        NetStatus = "OFFLINE"
        if hasattr(Directive, "Network") and hasattr(Directive.Network, "is_online") and Directive.Network.is_online():
            NetStatus = "CONNECTED"
        return {
            "integrity_index": 100,
            "uptime_sec": int(time.time()),
            "network_link": NetStatus,
            "subspace_band": "Standard"
        }

Sensory = SensorySystem()

__all__ = ["SensorySystem", "Sensory"]
