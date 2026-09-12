"""
Global leniency toggle for LCARS — when enabled the system suppresses non-fatal checks/log warnings
and treats missing/invalid resources permissively.

Usage:
    from lcars.modules.leniency import set_lenient, LENIENT_MODE

By default LENIENT_MODE=True (per your request to remove checks everywhere).
"""
import logging

# Default: lenient mode enabled (suppress warnings/info level logging)
LENIENT_MODE: bool = True


def apply_leniency() -> None:
    """Apply global logging suppression according to LENIENT_MODE.

    - When LENIENT_MODE is True: suppress WARNING and below (keeps ERROR/CRITICAL).
    - When False: restore logging to default behaviour.
    """
    if LENIENT_MODE:
        # Suppress non-fatal logs (INFO/DEBUG/WARNING)
        logging.disable(logging.WARNING)
    else:
        # Re-enable all logging
        logging.disable(logging.NOTSET)


# Convenience helper to toggle at runtime
def set_lenient(value: bool) -> None:
    global LENIENT_MODE
    LENIENT_MODE = bool(value)
    apply_leniency()


# Apply at import time so other modules pick up the policy immediately
apply_leniency()