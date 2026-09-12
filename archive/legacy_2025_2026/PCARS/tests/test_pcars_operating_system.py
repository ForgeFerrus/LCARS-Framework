import unittest
from pathlib import Path

from PCARS import PCARSOSystem

class TestPCARSOSystem(unittest.TestCase):
    def setUp(self):
        self.system = PCARSOSystem(Path("PCARS/config.json"))

    def test_start_and_status(self):
        self.system.Start(default_era="CARS_22")
        status = self.system.Status()
        self.assertEqual(status["status"], "online")
        self.assertEqual(status["active_era"]["key"], "CARS_22")

    def test_execute_status_command(self):
        self.system.Start()
        result = self.system.Execute("status")
        self.assertEqual(result["status"], "online")

    def test_select_era(self):
        self.system.Start()
        response = self.system.SelectEra("PCARS_23")
        self.assertEqual(response["key"], "PCARS_23")
        self.assertEqual(self.system.Status()["active_era"]["key"], "PCARS_23")

    def test_shutdown(self):
        self.system.Start()
        self.assertTrue(self.system.IsOnline)
        self.system.Stop()
        self.assertFalse(self.system.IsOnline)

if __name__ == "__main__":
    unittest.main()
