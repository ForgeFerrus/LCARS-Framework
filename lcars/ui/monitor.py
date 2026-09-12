# ─────────────────────────────────────────────────────────────
# LCARS UI MONITOR ADAPTER (Canonical UI module path)
# ─────────────────────────────────────────────────────────────

from programs.titan_monitor import TitanMonitor

# Ensure registration is performed
TitanMonitorClass = TitanMonitor

__all__ = ["TitanMonitor", "TitanMonitorClass"]
