import unittest
from unittest.mock import patch, Mock
from lcars.modules.network_manager import NetworkManager


class TestNetworkManager(unittest.TestCase):
    def setUp(self):
        # ensure global config does not override test expectations
        try:
            from lcars.modules.config_manager import config_manager
            config_manager.configs.pop('network', None)
        except Exception:
            pass
        self.nm = NetworkManager(event_bus=None, enabled=True, require_confirmation=False)

    def test_enable_disable(self):
        self.assertTrue(self.nm.enabled)
        self.nm.enable(False)
        self.assertFalse(self.nm.enabled)
        self.nm.enable(True)
        self.assertTrue(self.nm.enabled)

    def test_allowlist(self):
        self.nm.allowlist = []
        self.assertFalse(self.nm.is_allowed('https://example.com'))
        self.nm.add_allowed('example.com')
        self.assertTrue(self.nm.is_allowed('https://sub.example.com'))

    @patch('lcars.modules.network_manager.requests.get')
    def test_perform_request_success(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK'
        mock_get.return_value = mock_resp

        self.nm.add_allowed('example.com')
        # ensure enabled
        self.nm.enable(True)
        res = self.nm.perform_request('https://example.com')
        self.assertIn('HTTP 200', res)
        self.assertIn('OK', res)

    @patch('lcars.modules.network_manager.requests.get')
    def test_perform_request_skips_confirmation_when_flagged(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK BYPASS'
        mock_get.return_value = mock_resp

        self.nm.add_allowed('example.com')
        self.nm.enable(True)
        # enable confirmation globally but bypass in the call
        self.nm.set_require_confirmation(True)
        res = self.nm.perform_request('https://example.com', skip_confirmation=True)
        self.assertIn('HTTP 200', res)
        self.assertIn('OK BYPASS', res)

    @patch('lcars.modules.network_manager.requests.get')
    def test_perform_request_unchecked_alias(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 204
        mock_resp.text = ''
        mock_get.return_value = mock_resp

        self.nm.add_allowed('example.com')
        self.nm.enable(True)
        self.nm.set_require_confirmation(True)
        res = self.nm.perform_request_unchecked('https://example.com')
        self.assertIn('HTTP 204', res)

    def test_persist_allowlist_to_config(self):
        try:
            from lcars.modules.config_manager import config_manager
        except Exception:
            config_manager = None
        self.nm.add_allowed('persist.example')
        if config_manager:
            self.assertIn('persist.example', config_manager.get('network', 'allowlist', []))

    def test_perform_request_blocked_or_disabled(self):
        self.nm.allowlist = []
        r = self.nm.perform_request('https://example.com')
        self.assertIn('NETWORK BLOCKED', r)
        self.nm.enable(False)
        r2 = self.nm.perform_request('https://localhost')
        self.assertIn('NETWORK DISABLED', r2)
