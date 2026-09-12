# ─────────────────────────────────────────────────────────────
# LCARS UI EXPLORER ADAPTER (Canonical UI module path)
# ─────────────────────────────────────────────────────────────

from programs.titan_explorer import TitanExplorer

# Ensure registration is performed
TitanExplorerClass = TitanExplorer

__all__ = ["TitanExplorer", "TitanExplorerClass"]
