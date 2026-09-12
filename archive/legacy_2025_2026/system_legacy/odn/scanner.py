# ◤ TITANIUM ODN SCANNER — CORE SYSTEM LAYER 🖖
# LCARS Framework :: SYSTEM_INFRASTRUCTURE // HARDWARE_COORD
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Єдиний шлюз до апаратного забезпечення та ОС вузла Titanium.
# ФУНКЦІЇ: Низькорівневий збір метрик із адаптивним розрахунком телеметрії.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань у ключах даних).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: import sys
import psutil
import random
# Titanium Bridge Migration: from datetime import datetime

# Імпорт базових типів Titanium Master
from lcars.base.type import SystemComponent

# ГОЛОВНИЙ КЛАС СКАНЕРА ОПТИЧНОЇ МЕРЕЖІ ДАНИХ (ODN SCANNER)
class ODNScanner(SystemComponent):
    # Низькорівневий аналізатор системних ресурсів вузла.
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        
        # Ініціалізація CPU моніторингу (Non-blocking Matrix)
        psutil.cpu_percent(interval=None)
        
        # Визначення початкових значень мережевої активності
        self.LastNetworkIOData = psutil.net_io_counters()
        self.LastNetworkSyncTimestamp = datetime.now().timestamp()

    # Збір основних апаратних метрик Titanium (Hardware Telemetry)
    def GetHardwareTelemetry(self) -> dict:
        # Отримання системних метрик через psutil (Pure Non-blocking)
        VirtualMemoryNode = psutil.virtual_memory()
        CpuLoadValue = psutil.cpu_percent(interval=None)
        
        # 1. ТЕМПЕРАТУРА (Адаптивний розрахунок "Термальної Емісії")
        TemperatureValue = 0.0
        if hasattr(psutil, "sensors_temperatures"):
            TemperatureSensors = psutil.sensors_temperatures()
            if TemperatureSensors and 'coretemp' in TemperatureSensors:
                TemperatureValue = TemperatureSensors['coretemp'][0].current
        
        # Емуляція термального фону для вузлів типу Redmond (Якщо заблоковано)
        if TemperatureValue <= 0:
            TemperatureValue = 35.0 + (CpuLoadValue / 2.0) + random.uniform(-1, 1)

        # 2. ЕНЕРГОЗАБЕЗПЕЧЕННЯ (Power Systems)
        PowerLevelValue = 100
        if hasattr(psutil, "sensors_battery"):
            BatteryNode = psutil.sensors_battery()
            if BatteryNode: 
                PowerLevelValue = BatteryNode.percent

        # Формування Titanium Data Map (Без підкреслювань у ключах!)
        return {
            "CpuLoad":       CpuLoadValue,
            "MemPercent":    VirtualMemoryNode.percent,
            "MemUsedMb":     VirtualMemoryNode.used // (1024**2),
            "TempCore":      round(TemperatureValue, 1),
            "PowerLevel":    PowerLevelValue,
            "ProcessCount":  len(psutil.pids()),
            "PlatformRef":   sys.platform
        }

    # Розрахунок пропускної здатності мережевих вузлів (Network IO Relay)
    def GetNetworkIO(self) -> dict:
        SyncTimestamp = datetime.now().timestamp()
        CurrentIOData = psutil.net_io_counters()
            
        DeltaTimeValue = SyncTimestamp - self.LastNetworkSyncTimestamp
        
        # Захист від нульового часового інтервалу (Zero Division Protection)
        if DeltaTimeValue <= 0.1 or not self.LastNetworkIOData: 
            return {"TransmitKbps": 0.0, "ReceiveKbps": 0.0}
        
        # Розрахунок швидкості передачі (Kbps)
        TxValue = (CurrentIOData.bytes_sent - self.LastNetworkIOData.bytes_sent) / 1024 / DeltaTimeValue
        RxValue = (CurrentIOData.bytes_recv - self.LastNetworkIOData.bytes_recv) / 1024 / DeltaTimeValue
        
        # Оновлення точок синхронізації Titanium
        self.LastNetworkIOData = CurrentIOData
        self.LastNetworkSyncTimestamp = SyncTimestamp
        
        return {
            "TransmitKbps": round(TxValue, 1), 
            "ReceiveKbps":  round(RxValue, 1)
        }

    # Побудова матриці поточних процесів вузла
    def GetProcessMatrix(self, LimitCount=10) -> list:
        ProcessMatrixArray = []
        for ProcNode in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            ProcessMatrixArray.append(ProcNode.info)
            
        # Сортування за навантаженням на ядро (Descending)
        return sorted(ProcessMatrixArray, key=lambda x: x['cpu_percent'], reverse=True)[:LimitCount]

# СИНГЛТОН ЕКЗЕМПЛЯР СКАНЕРА (TITANIUM INSTANCE)
scanner = ODNScanner()

# Експорт функціональних вузлів Titanium
__all__ = ["ODNScanner", "scanner"]
