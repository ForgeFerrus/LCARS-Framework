# LCARS SYSTEM METRICS - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Зчитування реальних системних показників
# СТАНДАРТ: Titanium Master (Isolated OS Access)

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import LCARS, SystemComponent, Directive


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
        DateTimeNode = getattr(LCARS.System, "DateTime", None)
        if DateTimeNode is None or not hasattr(DateTimeNode, "now"):
            return 0
        return int(DateTimeNode.now().timestamp())

    # Збір та повернення всіх метрик системи
    def GetAllMetrics(self) -> dict[str, Any]:
        DateTimeNode = getattr(LCARS.System, "DateTime", None)
        TimestampValue = ""
        if DateTimeNode is not None and hasattr(DateTimeNode, "now"):
            TimestampValue = DateTimeNode.now().isoformat()

        self.LastReadings = {
            "CPU": self.GetCPUUsage(),
            "Memory": self.GetMemoryUsage(),
            "Uptime": self.GetUptime(),
            "Timestamp": TimestampValue,
        }
        return self.LastReadings


# Експорт
SystemMetricsAdapter = SystemMetrics()

__all__ = ["SystemMetrics", "SystemMetricsAdapter"]
