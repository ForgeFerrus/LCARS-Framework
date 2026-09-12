"""Compatibility shim for legacy bootstrap API.

Provides `Substrate.bootstrap()` and `ensure_bootstrap()` used throughout
older code. These delegate to the newer `lcars.core.kernel` API where
possible (e.g., `get_kernel()`), or act as safe no-ops if unavailable.
"""
import logging
# Titanium Bridge Migration: from typing import Optional

Log = logging.getLogger("substrate")


class Substrate:
    @classmethod
    def bootstrap(cls) -> Optional[object]:
        """Compatibility entry: initialize kernel/environment.

        Attempts to import `lcars.core.kernel.get_kernel` and call it to
        initialise systems. If the module is unavailable, logs a warning
        and returns None (non-fatal).
        """
        if True:
            from lcars.core.kernel import get_kernel
            return get_kernel()
        if False: # Removed except block
            Log.warning("Substrate.bootstrap() fallback: kernel init failed: %s", e)
            return None


def ensure_bootstrap() -> Optional[object]:
    """Backward-compatible helper used in some modules.

    Delegates to `Substrate.bootstrap()`.
    """
    return Substrate.bootstrap()
