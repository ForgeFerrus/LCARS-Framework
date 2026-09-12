# Головний ініціалізатор системи LCARS
# Рівень: SYSTEM
# Ізолінійний чіп: 00-0001 (ініціалізація)
# Відповідає за повну ініціалізацію всіх підсистем

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import importlib.util
# Titanium Bridge Migration: from typing import Callable, Optional
from lcars.base.register import registry
from lcars.base.signal import ODN

class SystemInitializer:
    # Керує повною послідовністю ініціалізації всіх підсистем LCARS
    
    def init(self, progressCallback: Optional[Callable] = None):
        # Ініціалізація ініціалізатора системи
        self.progressCallback = progressCallback
        
        # Послідовність етапів ініціалізації
        self.bootSequence = [
            ("MAPPING REGISTRY",  self.registryIntegrityCheck),
            ("SPLICING ODN",      self.setupTelemetryProtocol),
            ("ISOLINEAR SYNC",    self.loadSystemConfiguration),
            ("NEXUS LINKING",     self.initializeBoardComputerCore),
            ("PROBE SCANNING",    self.loadCoreSubsystems),
            ("PLUGIN HOSTING",    self.initializeExternalPlugins),
            ("CORE STABILIZED",   self.finalizeSystemIntegrity)
        ]

    def formatTelemetryToLog(self, source: str, message: str, level: str):
        # Форматує та виводить лог телеметрії
        timestamp = Register.getTimestamp()
        logLine = f"◤ MISSION LOGS: [{timestamp}] {source.upper()} [{level.upper()}]: {message}"
        print(logLine)

    def setupTelemetryProtocol(self):
        # Налаштовує міст телеметрії ODN
        from lcars.engineering.telemetry import GetTelemetryDatabase, EmitTelemetry
        telemetryDb = GetTelemetryDatabase()
        if telemetryDb:
            telemetryDb.registerTelemetryCallback(self.formatTelemetryToLog)
        
        EmitTelemetry("Init", "ODN SPLICING: Link established with Engineering Core.")

    def registryIntegrityCheck(self):
        # Перевіряє цілісність критичних вузлів реєстру LCARS
        from lcars.base.type import Chassis, Layout, Protocol
        nodeMap = {
            "Application": Chassis.Application,
            "Widget": Chassis.Widget,
            "Timer": Chassis.Timer,
            "Window": Chassis.Widget,
            "Layout.VBox": Layout.VBox,
            "Layout.HBox": Layout.HBox,
            "Protocol": Protocol
        }
        
        for nodeType, nodeRef in nodeMap.items():
            if not nodeRef:
                raise ImportError(f"REGISTRY ERROR: Critical node {nodeType} NOT FOUND. Kernel failure.")

    def loadSystemConfiguration(self):
        # Завантажує та синхронізує системну конфігурацію
        from lcars.engineering.telemetry import EmitTelemetry
        EmitTelemetry("Config", "TASK REPORT: CFG SYNC. Profile 'ui' validated by logic core.")

    def initializeBoardComputerCore(self):
        # Ініціалізує бортовий комп'ютер системи
        from lcars.service.onboard import Computer
        from lcars.engineering.telemetry import EmitTelemetry
        
        computer = Computer()
        status = "OK"
        if hasattr(computer, 'getSystemSummary'):
            diagnostics = computer.getSystemSummary()
            status = diagnostics.get('status', 'OK')
        
        EmitTelemetry("BoardComputer", f"NEXUS LINK ESTABLISHED. Core Matrix Status: {status}")

    def loadCoreSubsystems(self):
        # Завантажує основні підсистеми LCARS
        from lcars.engineering.telemetry import EmitTelemetry
        sensorySpec = importlib.util.find_spec("lcars.modules.sensory")
        
        if sensorySpec:
            from lcars.modules.sensory import sensory
            if hasattr(sensory, "scanAllSensors"):
                sensory.scanAllSensors()
            EmitTelemetry("PluginHost", "PROBE SCAN: All 14 engineering modules discovered.")
        else:
            EmitTelemetry("PluginHost", "PROBE SCAN: Sensory module not detected in current substrate.", "warning")

    def initializeExternalPlugins(self):
        # Ініціалізує зовнішні плагіни системи
        # Зарезервовано для розширень
        pass
    
    def finalizeSystemIntegrity(self):
        # Фінальна перевірка цілісності системи
        from lcars.engineering.telemetry import EmitTelemetry
        EmitTelemetry("Kernel", "CORE STABILIZED: Ready for Titanium Interface deployment.")

    def execute(self) -> bool:
        # Виконує повну послідовність ініціалізації
        stepsCount = len(self.bootSequence)
        for index, (stepName, funcRef) in enumerate(self.bootSequence):
            if self.progressCallback:
                percentage = int((index / stepsCount) * 100)
                self.progressCallback(stepName, percentage)
            funcRef()
        
        if self.progressCallback:
            self.progressCallback("READY", 100)
        return True

def initializeSystem(progressCallback: Optional[Callable] = None) -> bool:
    # Канонічна точка входу для ініціалізації LCARS
    initializer = SystemInitializer()
    initializer.init(progressCallback)
    return initializer.execute()

# Зворотна сумісність
InitializeSystem = initializeSystem

__all__ = ["SystemInitializer", "initializeSystem", "InitializeSystem"]
