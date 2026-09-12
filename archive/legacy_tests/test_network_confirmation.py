import threading
import time
import unittest
from unittest.mock import patch, Mock
from lcars.modules.network_manager import NetworkManager


class TestNetworkConfirmation(unittest.TestCase):
    def setUp(self):
        self.nm = NetworkManager(event_bus=None)
        self.nm.allowlist = ['example.com']
        self.nm.enable(True)
        self.nm.set_require_confirmation(True)

    @patch('lcars.modules.network_manager.requests.get')
    def test_perform_request_with_confirmation_approve(self, mock_get):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = 'OK'
        mock_get.return_value = mock_resp

        result_container = {}

        def worker():
            result_container['res'] = self.nm.perform_request('https://example.com')

        t = threading.Thread(target=worker)
        t.start()

        # wait for pending confirmation to appear
        timeout = time.time() + 2
        req_id = None
        while time.time() < timeout and not req_id:
            if self.nm._pending_confirm:
                req_id = next(iter(self.nm._pending_confirm.keys()))
                break
            time.sleep(0.05)

        self.assertIsNotNone(req_id, 'expected pending confirmation')
        # approve
        ok = self.nm.approve_request(req_id, True)
        self.assertTrue(ok)
        t.join(timeout=2)
        self.assertIn('HTTP 200', result_container.get('res',''))

    def test_perform_request_with_confirmation_deny(self):
        # no network call expected
        result_container = {}

        def worker():
            result_container['res'] = self.nm.perform_request('https://example.com')

        t = threading.Thread(target=worker)
        t.start()

        timeout = time.time() + 2
        req_id = None
        while time.time() < timeout and not req_id:
            if self.nm._pending_confirm:
                req_id = next(iter(self.nm._pending_confirm.keys()))
                break
            time.sleep(0.05)

        self.assertIsNotNone(req_id)
        ok = self.nm.approve_request(req_id, False)
        self.assertTrue(ok)
        t.join(timeout=2)
        self.assertIn('DENIED', result_container.get('res',''))
