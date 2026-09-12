"""Startup flow wiring: StartMenu -> Desktop orchestration.

This module provides a non-GUI `StartupFlow` class that coordinates the
start menu selection and hand-off to the desktop. It is a skeleton that the
real UI can use when wiring the flow.

# УКР: `StartupFlow` координує сценарій запуску: відкриває StartMenu, отримує
# УКР: вибір користувача і передає його десктопу через `DesktopShell.show()`.
"""
from __future__ import annotations

# Titanium Bridge Migration: from typing import Optional

from .start_menu import StartMenu


class StartupFlow:
    def __init__(self, desktop):
        """`desktop` should be a Desktop-like object with a `show(selection)` method.

        УКР: `desktop` має реалізовувати `show(selection)` для застосування
        УКР: вибраної теми/проекту. Цей клас не виконує GUI-цикл; він лише
        УКР: координує передачу вибору між компонентами.
        """
        self.start_menu = StartMenu()
        self.desktop = desktop

    def start(self):
        """Begin the startup flow. Opens StartMenu and routes selection to Desktop.

        УКР: Метод `start()` відкриває StartMenu і одразу передає вибір до десктопу
        УКР: через колбек `on_select`. У GUI-реалізації виклик `open()` може бути
        УКР: асинхронним або модальним — тут використовується простий колбек.
        """
        def on_select(selection: dict):
            # Route selection to desktop; desktop is responsible for applying theme
            if hasattr(self.desktop, "show"):
                self.desktop.show(selection)

        self.start_menu.open(on_select)
