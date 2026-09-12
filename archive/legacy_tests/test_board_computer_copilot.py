import unittest
from lcars.core.board_computer import get_computer
from lcars.core.kernel import EventType


class TestBoardComputerCopilotIntegration(unittest.TestCase):
    def test_open_browser_emits_event(self):
        bc = get_computer()
        # ensure copilot exists and is in fallback mode
        if not hasattr(bc, 'copilot'):
            self.skipTest('Copilot not present in BoardComputer')

        # Clear event history
        bc.kernel.event_bus.event_history.clear()

        res = bc.process_query('open browser https://example.com')
        # return value should acknowledge browser open
        self.assertIn('ВІДКРИТО БРАУЗЕР', res.upper() or res)

        # Find UI_COMPONENT_UPDATED event
        evs = [e for e in bc.kernel.event_bus.event_history if e.event_type == EventType.UI_COMPONENT_UPDATED]
        self.assertTrue(any(e.data.get('action') == 'open_browser' for e in evs))
