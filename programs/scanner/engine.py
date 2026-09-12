"""ScannerEngine used by LCARS UI and CLI to access registered scanners.

This engine is intentionally lightweight: it queries the central
`ScannerRegistry` and offers a few convenience helpers expected by UI
components (system stats, network info, simulated tests, etc.).
"""
from lcars.system.scanner_system import ScannerRegistry
import psutil
import socket
import random
import time
from typing import Any, Dict


class ScannerEngine:
    def __init__(self):
        # Ensure built-in adapters are imported and registered
        try:
            import lcars.system.scanner_adapters  # noqa: F401
        except Exception:
            pass

        self.registry = ScannerRegistry

    def list_scanners(self):
        return self.registry.list_scanners()

    def scan(self, name: str, *args, **kwargs) -> Any:
        return self.registry.run_scan(name, *args, **kwargs)

    def get_system_stats(self) -> Dict[str, Any]:
        # Prefer ODN data when available
        telemetry = {}
        try:
            res = self.scan("odn")
            if isinstance(res, dict):
                telemetry = res.get("telemetry", res)
        except Exception:
            telemetry = {}

        cpu = telemetry.get("CpuLoad") or telemetry.get("cpu") or 0
        memory = telemetry.get("MemPercent") or telemetry.get("memory") or 0
        disk = telemetry.get("MemUsedMb") or telemetry.get("DiskUsedMb") or 0
        temp = telemetry.get("TempCore") or telemetry.get("Temp") or "N/A"

        # uptime
        try:
            boot = psutil.boot_time()
            uptime_seconds = int(time.time() - boot)
            hours = uptime_seconds // 3600
            mins = (uptime_seconds % 3600) // 60
            secs = uptime_seconds % 60
            uptime = f"{hours:02d}:{mins:02d}:{secs:02d}"
        except Exception:
            uptime = "00:00:00"

        return {"cpu": cpu, "memory": memory, "disk": disk, "uptime": uptime, "temp": temp}

    def get_network_info(self) -> Dict[str, Any]:
        download_kb = 0
        upload_kb = 0
        try:
            res = self.scan("odn")
            if isinstance(res, dict):
                network = res.get("network", {})
                download_kb = network.get("ReceiveKbps", network.get("ReceiveKbps", 0))
                upload_kb = network.get("TransmitKbps", network.get("TransmitKbps", 0))
        except Exception:
            pass

        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "0.0.0.0"
            hostname = "unknown"

        return {"local_ip": local_ip, "hostname": hostname, "download_kb": download_kb, "upload_kb": upload_kb}

    def get_simulation_data(self, which: str = "subspace") -> Dict[str, Any]:
        if which == "subspace":
            return {"warp": "NOMINAL", "field_strength": round(random.random(), 3), "noise": round(random.random(), 3)}
        return {}

    def run_speed_test(self) -> Dict[str, Any]:
        # Lightweight simulated speed test to keep UI responsive without external deps
        if random.random() < 0.98:
            return {"status": "success", "speed_mbps": round(random.uniform(10, 500), 2), "latency_ms": round(random.uniform(5, 150), 1)}
        return {"status": "fail", "message": "Relay unreachable"}


if __name__ == "__main__":
    eng = ScannerEngine()
    print("Available scanners:", eng.list_scanners())
    for name in eng.list_scanners():
        try:
            print(name, eng.scan(name))
        except Exception as e:
            print(name, "error:", e)
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
