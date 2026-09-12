"""Compatibility wrapper for sound manager.

Some modules import `lcars.core.sound_manager` while the implementation
resides in `lcars.modules.sound_manager`. This file provides a thin forwarder
so both import paths work.
"""
from lcars.modules.sound_manager import get_sound_manager, SoundManager  # re-export

__all__ = ["get_sound_manager", "SoundManager"]
