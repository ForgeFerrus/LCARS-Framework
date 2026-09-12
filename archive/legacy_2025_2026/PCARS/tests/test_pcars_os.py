import unittest
from pathlib import Path

from PCARS import PCARSCentral
from PCARS.core import OSEventType, OSEvent


class TestPCARSOS(unittest.TestCase):
    def setUp(self):
        self.central = PCARSCentral(Path("PCARS/config.json"))
        self.central.Boot()

    def test_event_bus_is_registered(self):
        self.assertIsNotNone(self.central.GetSubsystem("event_bus"))
        self.assertTrue(hasattr(self.central, "EventBus"))

    def test_status_command(self):
        response = self.central.ExecuteCommand("status")
        self.assertEqual(response["status"], "online")
        self.assertGreaterEqual(response["event_history"], 1)

    def test_select_era_command(self):
        response = self.central.ExecuteCommand("select_era", {"era": "CARS_22"})
        self.assertEqual(response["era"], "CARS_22")
        status = self.central.ExecuteCommand("status")
        self.assertEqual(status["active_era"]["key"], "CARS_22")

    def test_event_bus_emits_on_era_change(self):
        captured = []

        def on_era_changed(event: OSEvent):
            captured.append(event.payload)

        self.central.EventBus.subscribe(OSEventType.ERA_CHANGED, on_era_changed)
        self.central.ExecuteCommand("select_era", {"era": "PCARS_23"})
        self.assertEqual(len(captured), 1)
        self.assertEqual(captured[0]["era"], "PCARS_23")

    def test_feature_execution_through_command(self):
        self.central.ExecuteCommand("select_era", {"era": "CARS_22"})
        result = self.central.ExecuteCommand("feature", {"name": "command_console", "payload": {"sample": True}})
        self.assertEqual(result["feature"], "command_console")
        self.assertEqual(result["era"], "CARS_22")


if __name__ == "__main__":
    unittest.main()
