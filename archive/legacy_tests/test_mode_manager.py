import pytest
from lcars.modules.mode_manager import ModeManager, AppMode
from lcars.core.kernel import EventBus, EventType


def test_set_mode_emits_event():
    bus = EventBus()
    received = []

    def on_ui(ev):
        received.append(ev)

    bus.subscribe(EventType.UI_COMPONENT_UPDATED, on_ui)

    mm = ModeManager(bus)
    mm.set_mode(AppMode.DEV)

    assert mm.current_mode == AppMode.DEV
    assert len(received) == 1
    assert received[0].source == "mode_manager"
    assert received[0].data.get("mode") == "DEV"


def test_set_mode_invalid_type_raises():
    mm = ModeManager(EventBus())
    with pytest.raises(TypeError):
        mm.set_mode("DEV")  # wrong type should raise


def test_set_mode_idempotent_no_emit_when_same():
    bus = EventBus()
    calls = []

    def on_ui(ev):
        calls.append(ev)

    bus.subscribe(EventType.UI_COMPONENT_UPDATED, on_ui)
    mm = ModeManager(bus)

    # default is NORMAL; setting NORMAL again should NOT emit
    mm.set_mode(AppMode.NORMAL)
    assert len(calls) == 0


def test_set_mode_by_name_and_invalid():
    bus = EventBus()
    events = []
    bus.subscribe(EventType.UI_COMPONENT_UPDATED, lambda e: events.append(e))

    mm = ModeManager(bus)
    mm.set_mode_by_name("dev")
    assert mm.current_mode == AppMode.DEV
    assert events and events[-1].data.get("mode") == "DEV"

    with pytest.raises(ValueError):
        mm.set_mode_by_name("not-a-mode")


def test_module_has_ukrainian_comments_present():
    import inspect
    import lcars.modules.mode_manager as mm_mod

    # Перевіряємо, що в коді є прості україномовні пояснювальні коментарі
    src = inspect.getsource(mm_mod)
    assert "# Пояснення" in src
