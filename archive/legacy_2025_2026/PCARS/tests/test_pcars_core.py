import unittest
from pathlib import Path

from PCARS import ConfigStore, LcarsManager, ProcessManager, ServiceRegistry, UIBridge


class TestPCARScore(unittest.TestCase):
    def test_imports(self):
        self.assertIsInstance(ServiceRegistry(), ServiceRegistry)
        self.assertIsInstance(ProcessManager(), ProcessManager)
        self.assertIsInstance(ConfigStore(Path("PCARS/config.json")), ConfigStore)
        self.assertIsInstance(UIBridge(), UIBridge)

    def test_manager_boot(self):
        manager = LcarsManager(Path("PCARS/config.json"))
        manager.Boot()
        self.assertEqual(manager.GetStatus()["status"], "online")
        self.assertIs(manager.GetSubsystem("config"), manager.Core.Config)
        self.assertIs(manager.GetSubsystem("process"), manager.Core.ProcessManager)
        self.assertIs(manager.GetSubsystem("ui"), manager.Core.UIBridge)

    def test_execute_command_status(self):
        manager = LcarsManager(Path("PCARS/config.json"))
        manager.Boot()
        response = manager.ExecuteCommand("status")
        self.assertEqual(response["status"], "online")

    def test_select_era_through_manager(self):
        manager = LcarsManager(Path("PCARS/config.json"))
        manager.Boot()
        response = manager.SelectEra("CARS_22")
        self.assertEqual(response["era"], "CARS_22")
        self.assertEqual(manager.Feature("command_console", {"payload": "sample"})["feature"], "command_console")


if __name__ == "__main__":
    unittest.main()
