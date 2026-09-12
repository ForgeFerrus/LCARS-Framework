# ◤ TITANIUM SYSTEM COMMAND ALIAS BRIDGE // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/command.py
# ОПИС: Канонічний шлюз експорту процесора команд lcars.system.commands.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Strict PascalCase).
# =============================================================================

from __future__ import annotations
from lcars.system.commands import Command, Commands, Directive

__all__ = [
    "Command",
    "Commands",
    "Directive",
]

