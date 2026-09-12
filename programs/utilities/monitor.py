# ◤ TITANIUM SYSTEM MONITOR — v12.5 🖖
# LCARS Framework :: HARDWARE TELEMETRY :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Стратегічний дашборд апаратної телеметрії в реальному часі.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from pathlib import Path

# Імпортуємо psutil для зчитування системних метрик
try: import psutil
except ImportError: psutil = None

# Імпортуємо основні типи Titanium (Витримуємо протокол No Q)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.default import (
    TitanPalette 
)
from lcars.base.interface import LCARSProgramPanel

# Головна програма моніторингу системи
class SystemMonitorProgram(LCARSProgramPanel):
    # Ініціалізація модуля телеметрії
    def __init__(self, Era=None, Faction=None, Parent=None, **kwargs):
        # Викликаємо базовий конструктор LCARSPanel
        super().__init__(
            title="SYSTEM_MONITOR // HARDWARE_TELEMETRY",
            era=Era,
            faction=Faction,
            accent_color="#36C", # Колір системного зв'язку
            parent=Parent
        )
        # Список основних метрик для відстеження
        self.MetricsList = ["cpu", "memory", "disk", "network"]
        # Словник для зберігання віджетів-індикаторів
        self.MetricWidgets = {}

    # Створення інтерфейсу (Використовуємо канонічний BuildUI)
    def BuildUI(self, Layout: VBoxLayout):
        # Отримуємо основні кольори поточної палітри
        Acc = self.accent_color
        Sec = self.theme.get("secondary", "#FC6")
        
        # Головний контейнер для метрик
        MonitorBox = VBoxLayout()
        MonitorBox.setSpacing(15)
        MonitorBox.setContentsMargins(25, 10, 25, 10)
        
        # Створюємо індикатори для кожної метрики
        for Index, MetricName in enumerate(self.MetricsList):
            # Вибираємо колір із палітри Titanium
            MetricColor = self.palette[Index % len(self.palette)]
            # Використовуємо Visual.Progress (Проксі для StatBar)
            ProgressWidget = Visual.Progress(MetricName.upper(), MetricColor, parent=self)
            self.MetricWidgets[MetricName] = ProgressWidget
            MonitorBox.addWidget(ProgressWidget)
            
        Layout.addLayout(MonitorBox, 1)

        # Створюємо таймер оновлення даних (Directive-based)
        self.DataTimer = Directive.Timer(self)
        self.DataTimer.timeout.connect(self.PollHardwareSubstrate)
        self.DataTimer.start(1000)

    # Отримання даних із фізичного обладнання (Без нижніх підкреслювань)
    def PollHardwareSubstrate(self):
        # Перевіряємо наявність бібліотеки psutil
        if not psutil: return
        try:
            # CPU Load
            if "cpu" in self.MetricWidgets:
                self.MetricWidgets["cpu"].update_value(f"{psutil.cpu_percent():.1f}%")
            # Memory Consumption
            if "memory" in self.MetricWidgets:
                self.MetricWidgets["memory"].update_value(f"{psutil.virtual_memory().percent:.1f}%")
            # Disk Usage
            if "disk" in self.MetricWidgets:
                DiskData = psutil.disk_usage("/")
                self.MetricWidgets["disk"].update_value(f"{(DiskData.used/DiskData.total*100):.1f}%")
            # Network Activity
            if "network" in self.MetricWidgets:
                NetData = psutil.net_io_counters()
                Activity = "ACTIVE" if (NetData.bytes_sent + NetData.bytes_recv) > 0 else "IDLE"
                self.MetricWidgets["network"].update_value(Activity)
        except Exception:
            # Відмова системного сканера (Заглушка)
            pass

# Запуск монітора в автономному режимі
if __name__ == "__main__":
    # Отримуємо об'єкт Application з реєстру
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    
    # Створюємо вікно монітора
    MonitorWin = SystemMonitorProgram()
    MonitorWin.resize(900, 600)
    MonitorWin.show()
    
    # Вихід із термінала
    sys.exit(AppInst.exec())
