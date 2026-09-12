import unittest
from unittest.mock import patch, Mock
from lcars.core.board_computer import get_computer


class TestCopilotNetworkPermission(unittest.TestCase):
    def setUp(self):
        self.bc = get_computer()
        # Ensure network_manager exists
        assert hasattr(self.bc, 'network_manager')
        self.nm = self.bc.network_manager
        # start with disabled allowlist for deterministic tests
        self.nm.allowlist = ['localhost']
        self.nm.enable(True)
        self.nm.set_require_confirmation(False)

    def test_network_blocked_by_allowlist(self):
        r = self.bc.copilot.tools.execute('network_request', {'url': 'https://example.com'})
        self.assertIn('NETWORK BLOCKED', r)

    @patch('lcars.modules.network_manager.requests.get')
    def test_network_allowed_when_in_allowlist(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK'
        mock_get.return_value = mock_resp

        self.nm.add_allowed('example.com')
        res = self.bc.copilot.tools.execute('network_request', {'url': 'https://example.com'})
        self.assertIn('HTTP 200', res)

    def test_network_disabled_by_manager(self):
        self.nm.enable(False)
        res = self.bc.copilot.tools.execute('network_request', {'url': 'https://localhost'})
        self.assertIn('NETWORK DISABLED', res)
