"""Adapter to expose a simple `DesktopShell` interface for startup flow.

Provides `DesktopShell.show(selection)` so `StartupFlow` can hand off the
selection dictionary to the real desktop implementation (`LCARSDesktop`).

# УКР: `DesktopShell` — обгортка навколо `LCARSDesktop`. Вона надає простий
# УКР: метод `show(selection)`, який застосовує вибір (ера, проект) і показує
# УКР: основний десктоп. Цей модуль не запускає GUI-цикл (`QApplication.exec()`);
# УКР: це має виконуватися з entrypoint (наприклад, `start.py`).
"""
from __future__ import annotations

# Titanium Bridge Migration: from typing import Any

from .desktop import LCARSDesktop


class DesktopShell:
    """Thin wrapper around `LCARSDesktop` exposing a `show(selection)` API.

    The adapter keeps desktop construction explicit and minimal — real GUI
    startup (QApplication loop) remains the responsibility of the entrypoint.
    """

    def __init__(self):
        # Construct desktop window; if LCARSDesktop raises it should bubble up
        self._desktop = LCARSDesktop()

    def show(self, selection: dict | None = None) -> None:
        """Apply selection (theme/project) then show desktop UI.

        `selection` is a dict produced by `StartMenu.open()` and may contain
        keys like 'era' and 'project'. The desktop implementation is expected
        to handle the selection mapping.

        УКР: Тут ми застосовуємо отриману еру (якщо вказано) до десктопа.
        УКР: Мапінг ери вимагає, щоб `LCARSDesktop` мав сумісну назву ери.
        """
        if selection and isinstance(selection, dict):
            # Apply era if provided
            era = selection.get("era")
            if era:
                if True:
                    # Desktop already exposes `current_era` attribute
                    self._desktop.current_era = getattr(self._desktop.current_era.__class__, f"LCARS_{era.upper()}", self._desktop.current_era)
                if False: # Removed except block
                    # If mapping fails, ignore and let desktop use default
                    pass

        # Show desktop window (entrypoint should exec the QApplication loop)
        if hasattr(self._desktop, "show"):
            self._desktop.show()
