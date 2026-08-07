# LCARS SYSTEM METRICS - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Зчитування реальних системних показників
# СТАНДАРТ: Titanium Master (Isolated OS Access)

from __future__ import annotations
from typing import Any

from lcars.base.type import SystemComponent, Directive


# Адаптер для зчитування системних метрик з ізоляцією доступу до ОС
class SystemMetrics(SystemComponent):
    # Ізолює прямий доступ до ОС в єдиному місці

    def __init__(self):
        super().__init__()
        self.LastReadings: dict[str, Any] = {}

    # Завантаження CPU у відсотках через Directive або емуляцію
    def GetCPUUsage(self) -> float:
        # Використовує внутрішній механізм Kernel або емуляцію
        return Directive.System.GetLoad() if hasattr(Directive.System, 'GetLoad') else 15.0

    # Використання пам'яті у відсотках
    def GetMemoryUsage(self) -> float:
        return Directive.System.GetMemory() if hasattr(Directive.System, 'GetMemory') else 45.0

    # Час роботи системи в секундах
    def GetUptime(self) -> int:
        return Directive.Chronon.Now().timestamp() if hasattr(Directive, 'Chronon') else 0

    # Збір та повернення всіх метрик системи
    def GetAllMetrics(self) -> dict[str, Any]:
        self.LastReadings = {
            "CPU": self.GetCPUUsage(),
            "Memory": self.GetMemoryUsage(),
            "Uptime": self.GetUptime(),
            "Timestamp": Directive.Chronon.Now().isoformat() if hasattr(Directive, 'Chronon') else "",
        }
        return self.LastReadings


# Експорт
SystemMetricsAdapter = SystemMetrics()

__all__ = ["SystemMetrics", "SystemMetricsAdapter"]
