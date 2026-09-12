"""Lightweight System Synapse shim for recovery.

Provides `SystemSynapse` with a minimal signal-like API used by
engineering modules (e.g. `data_received.emit(...)`, `emit_pulse(...)`).
"""
# Titanium Bridge Migration: from typing import Any, Callable


class SimpleSignal:
    def __init__(self):
        self.callbacks = []

    def connect(self, cb: Callable):
        self.callbacks.append(cb)

    def emit(self, *args, **kwargs):
        for cb in list(self.callbacks):
            cb(*args, **kwargs)


class SystemSynapse:
    """Minimal synapse used by engineering modules for inter-subsystem pulses."""
    def __init__(self):
        self.data_received = SimpleSignal()
        self.pulse = SimpleSignal()

    def emit_pulse(self, source: str, data: Any):
        self.pulse.emit(source, data)

    def send(self, name: str, payload: Any):
        self.data_received.emit(name, payload)


__all__ = ["SystemSynapse"]
