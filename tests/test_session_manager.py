import unittest
from lcars.core.session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    def test_lock_unlock_persistence(self):
        sm = SessionManager()
        # Ensure start unlocked
        sm.unlock()
        self.assertFalse(sm.is_locked())

        # Lock and verify
        sm.lock()
        self.assertTrue(sm.is_locked())

        # Create new instance to check persistence
        sm2 = SessionManager()
        self.assertTrue(sm2.is_locked())

        # Cleanup: unlock
        sm2.unlock()
        self.assertFalse(sm2.is_locked())

if __name__ == '__main__':
    unittest.main()
