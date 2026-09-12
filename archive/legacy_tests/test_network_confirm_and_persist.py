import threading
import time
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

from lcars.modules.network_manager import NetworkManager
from lcars.modules.config_manager import config_manager


class TestNetworkConfirmAndPersist(unittest.TestCase):
    def setUp(self):
        # Clear persisted network config
        try:
            config_manager.configs.pop('network', None)
        except Exception:
            pass
        self.nm = NetworkManager(event_bus=None, enabled=True, require_confirmation=False)

    @patch('lcars.modules.network_manager.requests.get')
    def test_perform_request_with_confirmation_and_approve(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK'
        mock_get.return_value = mock_resp

        self.nm.add_allowed('example.com')
        self.nm.set_require_confirmation(True)

        result_container = {}

        def worker():
            res = self.nm.perform_request('https://example.com')
            result_container['res'] = res

        t = threading.Thread(target=worker)
        t.start()

        # wait until pending is created
        for _ in range(50):
            if self.nm._pending_confirm:
                break
            time.sleep(0.01)
        self.assertTrue(self.nm._pending_confirm)
        req_id = next(iter(self.nm._pending_confirm.keys()))

        # Approve
        ok = self.nm.approve_request(req_id, True)
        self.assertTrue(ok)

        t.join(timeout=2)
        self.assertIn('HTTP 200', result_container.get('res', ''))

    def test_allowlist_persistence(self):
        # Initially no network config
        self.nm.add_allowed('persist.example')
        # Check global config_manager saved allowlist
        al = config_manager.get('network', 'allowlist')
        self.assertTrue(isinstance(al, list))
        self.assertIn('persist.example', al)
