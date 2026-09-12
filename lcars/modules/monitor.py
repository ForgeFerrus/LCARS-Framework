# ◤ LCARS SYSTEM MONITOR UTILITY
# Самостійний застосунок для моніторингу системних ресурсів
# ───────────────────────────────────────────────────────────────
from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Optional, Dict
# Titanium Bridge Migration: from pathlib import Path

from lcars.base.type import Matrix, Directive, SystemComponent
from lcars.base.register import registry
from lcars.core.signal import ODN
from lcars.engineering.telemetry import EmitTelemetry
from lcars.base.info import getVersion

# УКР: Делегування версії згідно стандарту Titanium
__version__ = getVersion()

# Самостійний системний монітор з інтеграцією телеметрії
class SystemMonitorUtility(SystemComponent):    
    def __init__(self, ParentNode=None):
        super().__init__(SystemId="SystemMonitorUtility")
        
        # УКР: Збереження посилання на батьківський вузол
        self.ParentNodeRef = ParentNode
        
        # УКР: Стан моніторингу
        self.ActiveMonitoring = False
        self.PreviousNetworkIoCounters = None
        self.MonitoringIntervalMilliseconds = 2000
        
        # УКР: UI Компоненти
        self.CpuUsageDisplay = None
        self.MemoryUsageDisplay = None
        self.NetworkUsageDisplay = None
        self.UpdateIntervalControl = None
        
        # УКР: Таймер оновлення даних
        self.MonitoringTimer = None
        
        # УКР: Ініціалізація інтерфейсу
        self.InitializeInterface()
        
        # УКР: Підключення до системи телеметрії
        self.ConnectTelemetryStream()
    
    def InitializeInterface(self):
        # УКР: Створення базової структури UI
        WidgetClass = registry.Get("Interface.Widget")
        VBoxClass = registry.Get("Interface.Layout.VBox")
        LabelClass = registry.Get("Interface.Label")
        ButtonClass = registry.Get("Interface.Button")
        
        if not callable(WidgetClass) or not callable(VBoxClass):
            self.Native = None
            return

        # УКР: Головний контейнер - створюємо нове вікно якщо немає батька
        if self.ParentNodeRef is None:
            self.Native = WidgetClass()
        else:
            self.Native = self
        
        MainLayout = VBoxClass(self.Native)
        
        # УКР: Заголовок вікна
        TitleLabel = LabelClass("◤ SYSTEM RESOURCE MONITOR")
        TitleLabel.setStyleSheet("font-size: 18pt; color: #FFAA00;")
        MainLayout.addWidget(TitleLabel)
        
        # УКР: Індикатор CPU
        self.CpuUsageDisplay = LabelClass("CPU: --%")
        self.CpuUsageDisplay.setStyleSheet("font-size: 14pt; color: #6699CC;")
        MainLayout.addWidget(self.CpuUsageDisplay)
        
        # УКР: Індикатор памяті
        self.MemoryUsageDisplay = LabelClass("MEMORY: --%")
        self.MemoryUsageDisplay.setStyleSheet("font-size: 14pt; color: #CC6699;")
        MainLayout.addWidget(self.MemoryUsageDisplay)
        
        # УКР: Індикатор мережі
        self.NetworkUsageDisplay = LabelClass("NETWORK: -- KB/s")
        self.NetworkUsageDisplay.setStyleSheet("font-size: 14pt; color: #99CC66;")
        MainLayout.addWidget(self.NetworkUsageDisplay)
        
        # УКР: Кнопка ручного оновлення
        RefreshButton = ButtonClass("MANUAL REFRESH")
        RefreshButton.setStyleSheet("background: #FFAA00; color: #000; padding: 10px;")
        RefreshButton.clicked.connect(self.ExecuteMetricsScan)
        MainLayout.addWidget(RefreshButton)
        
        # УКР: Кнопка автоматичного режиму
        self.AutoModeButton = ButtonClass("START AUTO MONITOR")
        self.AutoModeButton.setStyleSheet("background: #6699CC; color: #000; padding: 10px;")
        self.AutoModeButton.clicked.connect(self.ToggleAutoMonitoring)
        MainLayout.addWidget(self.AutoModeButton)
        
        self.Native.setLayout(MainLayout)
        
        # УКР: Перший збір даних
        self.ExecuteMetricsScan()
    
    def ConnectTelemetryStream(self):
        # УКР: Підписка на події системи
        ODN.Listen("Telemetry.Update", self.ProcessTelemetryEvent)
    
    def ProcessTelemetryEvent(self, EventData: Dict[str, Any]):
        # УКР: Обробка вхідних телеметричних даних
        if "CpuLoad" in EventData:
            self.CpuUsageDisplay.setText(f"CPU: {EventData['CpuLoad']}%")
        if "MemoryPercent" in EventData:
            self.MemoryUsageDisplay.setText(f"MEMORY: {EventData['MemoryPercent']}%")
    
    def ToggleAutoMonitoring(self):
        # УКР: Перемикання автоматичного режиму моніторингу
        if self.ActiveMonitoring:
            self.StopAutoMonitoring()
        else:
            self.StartAutoMonitoring()
    
    def StartAutoMonitoring(self):
        # УКР: Запуск автоматичного збору метрик
        self.ActiveMonitoring = True
        self.AutoModeButton.setText("STOP AUTO MONITOR")
        
        TimerClass = registry.Get("Base.Timer")
        self.MonitoringTimer = TimerClass(self.Native)
        self.MonitoringTimer.timeout.connect(self.ExecuteMetricsScan)
        self.MonitoringTimer.start(self.MonitoringIntervalMilliseconds)
        
        EmitTelemetry("Monitor", "AUTO_MONITORING_ENABLED")
    
    def StopAutoMonitoring(self):
        # УКР: Зупинка автоматичного збору
        self.ActiveMonitoring = False
        self.AutoModeButton.setText("START AUTO MONITOR")
        
        if self.MonitoringTimer:
            self.MonitoringTimer.stop()
            self.MonitoringTimer = None
        
        EmitTelemetry("Monitor", "AUTO_MONITORING_DISABLED")
    
    def ExecuteMetricsScan(self):
        # УКР: Виконання сканування системних метрик
        self.UpdateCpuMetrics()
        self.UpdateMemoryMetrics()
        self.UpdateNetworkMetrics()
        
        # УКР: Відправка агрегованих даних у телеметрію
        ODN.Emit("System.Metrics", {
            "Timestamp": registry.Get("System.Time"),
            "Source": "SystemMonitorUtility"
        })
    
    def UpdateCpuMetrics(self):
        # УКР: Оновлення показників CPU через psutil
        psutilModule = registry.Get("System.psutil")
        if psutilModule is None:
            self.CpuUsageDisplay.setText("CPU: N/A")
            return
        
        CpuLoad = psutilModule.cpu_percent(interval=None)
        self.CpuUsageDisplay.setText(f"CPU: {CpuLoad}%")
        
        # УКР: Телеметрія CPU
        EmitTelemetry("Cpu", {"Load": CpuLoad})
    
    def UpdateMemoryMetrics(self):
        # УКР: Оновлення показників памяті
        psutilModule = registry.Get("System.psutil")
        if psutilModule is None:
            self.MemoryUsageDisplay.setText("MEMORY: N/A")
            return
        
        MemoryData = psutilModule.virtual_memory()
        MemoryPercent = MemoryData.percent
        self.MemoryUsageDisplay.setText(f"MEMORY: {MemoryPercent}%")
        
        # УКР: Телеметрія памяті
        EmitTelemetry("Memory", {"Percent": MemoryPercent})
    
    def UpdateNetworkMetrics(self):
        # УКР: Оновлення мережевих показників з розрахунком дельти
        psutilModule = registry.Get("System.psutil")
        if psutilModule is None:
            self.NetworkUsageDisplay.setText("NETWORK: N/A")
            return
        
        CurrentNetworkIo = psutilModule.net_io_counters()
        if CurrentNetworkIo is None:
            self.NetworkUsageDisplay.setText("NETWORK: UNAVAILABLE")
            return
        
        if self.PreviousNetworkIoCounters is None:
            self.NetworkUsageDisplay.setText("NETWORK: INITIALIZING...")
            self.PreviousNetworkIoCounters = CurrentNetworkIo
            return
        
        # УКР: Розрахунок швидкості передачі
        BytesSentDelta = CurrentNetworkIo.bytes_sent - self.PreviousNetworkIoCounters.bytes_sent
        BytesRecvDelta = CurrentNetworkIo.bytes_recv - self.PreviousNetworkIoCounters.bytes_recv
        
        KiloBytesSent = BytesSentDelta / 1024
        KiloBytesRecv = BytesRecvDelta / 1024
        
        self.NetworkUsageDisplay.setText(
            f"NETWORK: ↑{KiloBytesSent:.1f} KB/s ↓{KiloBytesRecv:.1f} KB/s"
        )
        
        # УКР: Збереження поточного стану для наступного розрахунку
        self.PreviousNetworkIoCounters = CurrentNetworkIo
        
        # УКР: Телеметрія мережі
        EmitTelemetry("Network", {
            "SentKbps": KiloBytesSent,
            "RecvKbps": KiloBytesRecv
        })
    
    def Show(self):
        # УКР: Відображення вікна монітору
        if hasattr(self.Native, 'show'):
            self.Native.show()
        
        EmitTelemetry("Monitor", "UTILITY_DISPLAY_ACTIVATED")

# СТАТИЧНИЙ ЕКЗЕМПЛЯР (Singleton Pattern)
UtilityInstance = None

def SystemMonitor() -> SystemMonitorUtility:
    # Глобальний доступ до монітору
    global UtilityInstance
    if UtilityInstance is None:
        UtilityInstance = SystemMonitorUtility()
    return UtilityInstance

def LaunchAsStandalone():
    # Запуск як самостійного застосунку
    Application = Directive.Application
    App = Application([])
    
    Monitor = SystemMonitorUtility()
    Monitor.Show()
    
    EmitTelemetry("System", "STANDALONE_MONITOR_LAUNCHED")
    return App.exec()

# ───────────────────────────────────────────────────────────────
# Експорт функціональних вузлів Titanium
__all__ = [
    "SystemMonitorUtility",
    "SystemMonitor", 
    "LaunchAsStandalone"
]

# Точка входу для самостійного запуску
if __name__ == "__main__":
    LaunchAsStandalone()
