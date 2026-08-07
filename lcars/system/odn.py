from __future__ import annotations

import random
import sys
from datetime import datetime

import psutil

from lcars.base.type import SystemComponent


class ODNScanner(SystemComponent):
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        psutil.cpu_percent(interval=None)
        self.LastNetworkIOData = psutil.net_io_counters()
        self.LastNetworkSyncTimestamp = datetime.now().timestamp()

    def GetHardwareTelemetry(self) -> dict:
        VirtualMemoryNode = psutil.virtual_memory()
        CpuLoadValue = psutil.cpu_percent(interval=None)

        TemperatureValue = 0.0
        if hasattr(psutil, "sensors_temperatures"):
            TemperatureSensors = psutil.sensors_temperatures()
            if TemperatureSensors:
                CoreSensors = TemperatureSensors.get("coretemp")
                if CoreSensors:
                    TemperatureValue = CoreSensors[0].current

        if TemperatureValue <= 0:
            TemperatureValue = 35.0 + (CpuLoadValue / 2.0) + random.uniform(-1, 1)

        PowerLevelValue = 100
        if hasattr(psutil, "sensors_battery"):
            BatteryNode = psutil.sensors_battery()
            if BatteryNode:
                PowerLevelValue = BatteryNode.percent

        return {
            "CpuLoad": CpuLoadValue,
            "MemPercent": VirtualMemoryNode.percent,
            "MemUsedMb": VirtualMemoryNode.used // (1024 ** 2),
            "TempCore": round(TemperatureValue, 1),
            "PowerLevel": PowerLevelValue,
            "ProcessCount": len(psutil.pids()),
            "PlatformRef": sys.platform,
        }

    def GetNetworkIO(self) -> dict:
        SyncTimestamp = datetime.now().timestamp()
        CurrentIOData = psutil.net_io_counters()
        DeltaTimeValue = SyncTimestamp - self.LastNetworkSyncTimestamp

        if DeltaTimeValue <= 0.1 or not self.LastNetworkIOData:
            return {"TransmitKbps": 0.0, "ReceiveKbps": 0.0}

        TxValue = (CurrentIOData.bytes_sent - self.LastNetworkIOData.bytes_sent) / 1024 / DeltaTimeValue
        RxValue = (CurrentIOData.bytes_recv - self.LastNetworkIOData.bytes_recv) / 1024 / DeltaTimeValue

        self.LastNetworkIOData = CurrentIOData
        self.LastNetworkSyncTimestamp = SyncTimestamp

        return {
            "TransmitKbps": round(TxValue, 1),
            "ReceiveKbps": round(RxValue, 1),
        }

    def GetProcessMatrix(self, LimitCount=10) -> list:
        ProcessMatrixArray = []
        for ProcNode in psutil.process_iter(["pid", "name", "cpu_percent"]):
            ProcessMatrixArray.append(ProcNode.info)

        return sorted(ProcessMatrixArray, key=lambda x: x["cpu_percent"], reverse=True)[:LimitCount]


scanner = ODNScanner()

__all__ = ["ODNScanner", "scanner"]
