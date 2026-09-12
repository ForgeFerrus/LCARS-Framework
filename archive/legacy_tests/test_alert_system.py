import pytest
from lcars.system.alert import AlertSystem, AlertLevel, get_alert_system
from lcars.core.event_bus import EventBus, EventType


def test_singleton_get_alert_system():
    bus = EventBus()
    a1 = get_alert_system(bus)
    a2 = get_alert_system()
    assert a1 is a2
    assert a1.event_bus is bus


def test_cycle_and_levels():
    bus = EventBus()
    asys = AlertSystem(bus)
    assert asys.current_level == AlertLevel.GREEN
    # cycle through to yellow
    lvl = asys.cycle_level()
    assert lvl == AlertLevel.YELLOW
    assert asys.current_level == AlertLevel.YELLOW

    # raise to red and then wrap to green
    lvl = asys.cycle_level()
    assert lvl == AlertLevel.RED
    lvl = asys.cycle_level()
    assert lvl == AlertLevel.GREEN

    # manual raise/lower
    asys.set_level(AlertLevel.YELLOW)
    asys.lower_level()
    assert asys.current_level == AlertLevel.GREEN
    asys.raise_level()
    assert asys.current_level == AlertLevel.YELLOW


# режимні тести тепер виконуються окремо, AlertSystem не керує ModeManager


def test_event_bus_emission():
    bus = EventBus()
    asys = AlertSystem(bus)
    received = []

    def handler(event):
        if event.event_type == EventType.UI_COMPONENT_UPDATED:
            received.append(event)

    bus.subscribe(EventType.UI_COMPONENT_UPDATED, handler)
    asys.set_level(AlertLevel.RED)
    assert received and received[0].data['level'] == 'RED'
    # also setting by integer or name should work and not raise
    asys.set_level(0)
    asys.set_level("YELLOW")


if __name__ == "__main__":
    pytest.main([__file__])
