# ◤ TITANIUM SCANNER ENGINE — v44.20 🖖
# LCARS Framework :: SCANNER_CORE // SYSTEM_DIAGNOSTICS // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Ядро діагностики для сканера LCARS Titanium.
# ФУНКЦІЇ: Реальна телеметрія (PSUTIL), мережевий аналіз та симуляція сенсорів.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────
import time
import psutil
import socket
import urllib.request
from typing import Dict, Any, Optional

# ГОЛОВНИЙ КЛАС ДВИГУНА СКАНУВАННЯ (SCANNER ENGINE)
class ScannerEngine:
    # Ядро сканера: Об'єднує фізичні дані системи з імітацією підпросторових сенсорів.
    def __init__(self):
        # Початковий знімок мережевих метрик Titanium
        self.LastNetworkIoMetrics = psutil.net_io_counters()
        self.LastTelemetryTimestamp = time.time()

    # Отримання метрик системи в реальному часі (CamelCase)
    def GetSystemStats(self) -> Dict[str, Any]:
        # Повертає знімок завантаження CPU, пам'яті та диска.
        try:
            CpuLoadValue = psutil.cpu_percent(interval=None)
            MemoryPercentVal = psutil.virtual_memory().percent
            DiskUsagePercentVal = psutil.disk_usage('/').percent
            
            # Розрахунок термальної синхронізації (Temperature)
            ThermalStatusStr = "N/A"
            if hasattr(psutil, "sensors_temperatures"):
                TemperatureNodesMap = psutil.sensors_temperatures()
                if TemperatureNodesMap:
                    # Вибір першого доступного температурного датчика
                    for NodeNameStr, EntryList in TemperatureNodesMap.items():
                        if EntryList:
                            ThermalStatusStr = f"{EntryList[0].current}°C"
                            break
            
            # Повернення результатів без технічних підкреслювань у ключах
            return {
                "Cpu":     CpuLoadValue,
                "Memory":  MemoryPercentVal,
                "Disk":    DiskUsagePercentVal,
                "Temp":    ThermalStatusStr,
                "Uptime":  self.CalculateUptimeValue()
            }
        except Exception as ErrorNode:
            return {"Error": str(ErrorNode)}

    # Розрахунок часу безперервної роботи вузла
    def CalculateUptimeValue(self) -> str:
        UptimeSecondsVal = time.time() - psutil.boot_time()
        HoursVal, RemainderVal = divmod(int(UptimeSecondsVal), 3600)
        MinutesVal, SecondsVal = divmod(RemainderVal, 60)
        return f"{HoursVal:02}:{MinutesVal:02}:{SecondsVal:02}"

    # Отримання мережевої інформації Titanium (GetNetworkStatusInfo)
    def GetNetworkStatusInfo(self) -> Dict[str, Any]:
        # Повертає IP-адресу, Hostname та поточну швидкість передачі.
        try:
            HostnameStr = socket.gethostname()
            LocalIpStr = socket.gethostbyname(HostnameStr)
            
            # Розрахунок пропускної здатності ODN-каналу (kB/s)
            CurrentTimeVal = time.time()
            IoCountersNode = psutil.net_io_counters()
            TimeDeltaVal = CurrentTimeVal - self.LastTelemetryTimestamp
            
            if TimeDeltaVal <= 0: TimeDeltaVal = 0.001
            
            SentSpeedVal = (IoCountersNode.bytes_sent - self.LastNetworkIoMetrics.bytes_sent) / 1024 / TimeDeltaVal
            RecvSpeedVal = (IoCountersNode.bytes_recv - self.LastNetworkIoMetrics.bytes_recv) / 1024 / TimeDeltaVal
            
            # Кешування для наступного циклу сканування
            self.LastNetworkIoMetrics = IoCountersNode
            self.LastTelemetryTimestamp = CurrentTimeVal
            
            return {
                "Hostname":    HostnameStr,
                "LocalIp":     LocalIpStr,
                "UploadRate":  round(SentSpeedVal, 1),
                "DownloadRate": round(RecvSpeedVal, 1)
            }
        except Exception:
            return {
                "Hostname": "Unknown", "LocalIp": "0.0.0.0", 
                "UploadRate": 0.0, "DownloadRate": 0.0
            }

    # Виконання фізичного тесту швидкості (ExecutePhysicalSpeedTest)
    def ExecutePhysicalSpeedTest(self, TimeoutVal: int = 5) -> Dict[str, Any]:
        # Тимчасове підключення до ретранслятора для вимірювання латентності.
        TestTargetUrlStr = "https://speed.cloudflare.com/__down?bytes=5000000" # 5MB Buffer
        StartTimeVal = time.time()
        try:
            RequestObject = urllib.request.Request(
                TestTargetUrlStr, 
                data=None, 
                headers={
                    'User-Agent': 'TITANIUM-SCANNER/v44.20 (LCARS BRIDGE ACCESS)'
                }
            )
            with urllib.request.urlopen(RequestObject, timeout=TimeoutVal) as ResponseNode:
                DataBuffer = ResponseNode.read()
                EndTimeVal = time.time()
                
            ElapsedSecondsVal = EndTimeVal - StartTimeVal
            BufferSizeMbValue = len(DataBuffer) / (1024 * 1024)
            SpeedMbpsValue = (BufferSizeMbValue * 8) / ElapsedSecondsVal if ElapsedSecondsVal > 0 else 0
            
            return {
                "Status": "success",
                "SpeedMbps": round(SpeedMbpsValue, 2),
                "LatencyMs": round(ElapsedSecondsVal * 100, 1) # Апроксимація затримки
            }
        except Exception as ErrorNode:
            return {"Status": "error", "Message": str(ErrorNode)}

    # Генерація симульованих даних підпросторової матриці
    def GetSimulatedSensorData(self, ModeStr: str = "subspace") -> Dict[str, Any]:
        import random
        if ModeStr == "subspace":
            return {
                "Subspace Band": f"{random.uniform(0.1, 9.9):.1f} THz",
                "Flux Density": f"{random.randint(100, 999)} millicochranes",
                "Variance": f"{random.uniform(0, 0.05):.4f}",
                "Harmonics": "Stable" if random.random() > 0.1 else "Fluctuating"
            }
        elif ModeStr == "bio":
            return {
                "Life Signs": random.randint(0, 5),
                "Species Id": "Humanoid" if random.random() > 0.2 else "Unknown",
                "Metabolism": f"{random.randint(60, 120)} bpm",
                "Integrity": f"{random.randint(90, 100)}%"
            }
        return {"Status": "Scanning..."}

# Експорт двигуна Titanium
__all__ = ["ScannerEngine"]

if __name__ == "__main__":
    eng = ScannerEngine()
    print("Available scanners:", eng.list_scanners())
    for name in eng.list_scanners():
        try:
            print(name, eng.scan(name))
        except Exception as e:
            print(name, "error:", e)
