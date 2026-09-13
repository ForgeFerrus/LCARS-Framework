import pytest

class MockEventBus:
    def __init__(self):
        self.events = []

    def emit(self, event_name, event_data=None):
        if hasattr(event_name, "name"):
            event_name = event_name.name
        self.events.append((str(event_name), event_data))

    Emit = emit

@pytest.fixture
def mock_event_bus():
    return MockEventBus()
