import pytest
from lcars.system.alert import AlertSystem, AlertLevel
from lcars.core.event_bus import EventBus

# we import the handler so it subscribes to bus
import lcars.engineering.alert_handler as ah


def test_alert_triggers_engineering():
    bus = EventBus()
    # override ENGINEER with a fresh instance tied to this bus
    ah.ENGINEER = ah._Engineering(bus)

    alert = AlertSystem(bus)
    alert.set_level(AlertLevel.RED)
    assert ah.ENGINEER.deflector.shield_level == 100
    assert ah.ENGINEER.drive.mode == "impulse"

    alert.set_level(AlertLevel.GREEN)
    assert ah.ENGINEER.deflector.shield_level == 0
    assert ah.ENGINEER.drive.mode == "standby"
