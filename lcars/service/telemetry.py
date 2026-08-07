from __future__ import annotations
import os

# Отримання вузла сенсорної системи з модуля сенсорів
def SensorySystemNode():
    from lcars.modules.sensor import SensorArray
    return SensorArray()

# Отримання глобального вузла сенсорної системи
def GetSensorySystemNode(): return SensorySystemNode()

# Головний клас телеметричної мережі для агрегації даних
class TelemetryGrid:
    TelemetryInstanceObject = None
    CallbackRegistryList    = []
    StreamListeners         = []

    def __new__(cls):
        if cls.TelemetryInstanceObject is None:
            Instance = object.__new__(cls)
            Instance.CallbackRegistryList = []
            Instance.StreamListeners      = []
            cls.TelemetryInstanceObject   = Instance
        return cls.TelemetryInstanceObject

    # Отримання глобального singleton-екземпляра
    @classmethod
    def GlobalInstance(cls):
        return cls()

    # Альтернативний метод отримання singleton-екземпляра
    @classmethod
    def GetGlobalInstance(cls): return cls.GlobalInstance()

    # Логування телеметричної події зі сповіщенням слухачів
    def LogTelemetryEvent(self, SourceStr: str, LevelStr: str, MessageStr: str):
        # Сповіщаємо всіх слухачів
        for Listener in self.StreamListeners:
            Listener(SourceStr, MessageStr, LevelStr)
        # Вивід у консоль
        if os.getenv("LCARS_TELEMETRY_CONSOLE", "1").strip() != "0":
            print(f"[{SourceStr.upper()}] [{LevelStr.upper()}]: {MessageStr}")
        # Зворотні виклики
        for CallbackFunc in self.CallbackRegistryList:
            CallbackFunc(SourceStr, MessageStr, LevelStr)

    # Підключення слухача до потоку телеметрії
    def ConnectStream(self, Listener):
        if Listener not in self.StreamListeners:
            self.StreamListeners.append(Listener)

    # Відключення слухача від потоку телеметрії
    def DisconnectStream(self, Listener):
        if Listener in self.StreamListeners:
            self.StreamListeners.remove(Listener)

    # Реєстрація callback-функції для телеметричних подій
    def RegisterTelemetryCallback(self, CallbackFunction):
        self.CallbackRegistryList.append(CallbackFunction)

    # Активація пульсу телеметрії з інтервалом синхронізації
    def ActivateTelemetryPulse(self, SyncIntervalMsVal=5000):
        SensoryNode = SensorySystemNode()
        if hasattr(SensoryNode, "UpdateTimerNode") and SensoryNode.UpdateTimerNode:
            SensoryNode.UpdateTimerNode.start(SyncIntervalMsVal)
        self.LogTelemetryEvent("Telemetry", "info", "Sensory grid synchronized. Pulse active.")

    # Деактивація пульсу телеметрії
    def DeactivateTelemetryPulse(self):
        SensoryNode = SensorySystemNode()
        if hasattr(SensoryNode, "UpdateTimerNode") and SensoryNode.UpdateTimerNode:
            SensoryNode.UpdateTimerNode.stop()
        self.LogTelemetryEvent("Telemetry", "info", "Sensory grid offline. Pulse suspended.")

    # Отримання даних сенсорів
    def SensorData(self):
        return SensorySystemNode().GetCurrentSensoryData()

    # Альтернативний метод отримання даних сенсорів
    def GetSensorData(self): return self.SensorData()

    # Отримання метрик телеметрії з фільтрацією за ключами Titanium
    def TelemetryMetrics(self) -> dict:
        RawDataMap = SensorySystemNode().GetCurrentSensoryData()
        TitaniumKeys = [
            "SystemLoad", "MemoryUsage", "IsolinearIntegrity",
            "CoreTemp", "PowerLevel", "UptimeCronon",
            "NetworkLink", "SubspaceBand", "SystemStatus",
            "EpsStatus", "ShieldStatus",
        ]
        return {Key: RawDataMap.get(Key) for Key in TitaniumKeys if Key in RawDataMap}

    # Альтернативний метод отримання метрик телеметрії
    def GetTelemetryMetrics(self): return self.TelemetryMetrics()

    # Виконання повного сканування сенсорної системи
    def ExecuteFullScan(self):
        SensorySystemNode().ExecuteFullSensorScan()

# Емісія телеметричної події в глобальний singleton
def EmitTelemetry(SourceStr: str, MessageStr: str, LevelStr: str = "info"):
    TelemetryGrid.GlobalInstance().LogTelemetryEvent(SourceStr, LevelStr, MessageStr)
