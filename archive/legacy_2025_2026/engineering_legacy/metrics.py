# LCARS SYSTEM METRICS - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Зчитування реальних системних показників
# СТАНДАРТ: Titanium Master (Isolated OS Access)

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent, Directive


class SystemMetrics(SystemComponent):
    # Адаптер для зчитування системних метрик
    # Ізолює прямий доступ до ОС в єдиному місці

    def __init__(self):
        super().__init__()
        self.LastReadings: dict[str, Any] = {}

    def GetCPUUsage(self) -> float:
        # Завантаження CPU в відсотках
        # Використовує внутрішній механізм Kernel або емуляцію
        return Directive.System.GetLoad() if hasattr(Directive.System, 'GetLoad') else 15.0

    def GetMemoryUsage(self) -> float:
        # Використання памяті в відсотках
        return Directive.System.GetMemory() if hasattr(Directive.System, 'GetMemory') else 45.0

    def GetUptime(self) -> int:
        # Час роботи системи в секундах
        return Directive.Chronon.Now().timestamp() if hasattr(Directive, 'Chronon') else 0

    def GetAllMetrics(self) -> dict[str, Any]:
        # Отримання всіх метрик
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
