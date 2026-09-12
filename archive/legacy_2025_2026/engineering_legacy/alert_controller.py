from __future__ import annotations
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from typing import Union

# AlertLevel and SystemMode imported only when required to prevent cycles

# інженерні підсистеми
from lcars.engineering.deflector import Deflector
from lcars.engineering.drive import WarpDrive
from lcars.engineering.damage_control import DamageControl


class EngineeringController:
    """Encapsulates all hardware/engineering reactions to alert or mode changes.

    Раніше код, що керував щитами і двигуном, жив у AlertSystem. Цей
    клас дозволяє винести його в окремий сервіс, щоб логіка тривоги була
    незалежною від конкретного обладнання.
    """

    def __init__(self):
        self.deflector = Deflector()
        self.drive = WarpDrive()
        self.damage_control = DamageControl(os.getcwd())

    def apply_alert_level(self, level) -> None:
        """Налаштувати інженерні підсистеми відповідно до рівня тривоги.

        Рівень може бути як членом AlertLevel, так і його числовим значенням.
        """
        from lcars.system.alert import AlertLevel

        if level == AlertLevel.RED:
            self.deflector.shield_level = 100
            self.drive.set_mode("impulse")
            self.damage_control.verify_hull_integrity()
        elif level == AlertLevel.YELLOW:
            self.deflector.shield_level = 50
            self.drive.set_mode("standby")
        elif level in (AlertLevel.GREEN, AlertLevel.BLUE, AlertLevel.BLACK):
            self.deflector.shield_level = 0
            self.drive.set_mode("standby")
        # інші рівні (додавайте за потреби)

    def apply_system_mode(self, mode) -> None:
        """Переводить інженерію в конкретний бойовий/тактичний режим.

        `mode` може бути об’єктом SystemMode або відповідним рядком.
        """
        from lcars.modules.mode_manager import SystemMode

        if mode == SystemMode.BATTLE:
            self.deflector.shield_level = 200
            self.drive.set_mode("warp")
        elif mode == SystemMode.TACTICAL:
            self.deflector.shield_level = 100
            self.drive.set_mode("impulse")
        elif mode == SystemMode.SCIENCE:
            self.deflector.shield_level = 20
            self.drive.set_mode("standby")
        elif mode == SystemMode.AUTODESTRUCT:
            self.deflector.shield_level = 0
            # додаткові дії по автознищенню можна реалізувати тут
