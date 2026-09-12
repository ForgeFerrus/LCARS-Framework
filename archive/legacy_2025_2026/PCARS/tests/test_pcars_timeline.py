import unittest
from pathlib import Path

from PCARS import PCARSCentral, EraTimeline


class TestPCARSTimeline(unittest.TestCase):
    def test_timeline_loads_eras(self):
        central = PCARSCentral(Path("PCARS/config.json"))
        central.Boot()
        era_list = central.Timeline.AvailableEras()
        self.assertGreaterEqual(len(era_list), 4)
        keys = [era.key for era in era_list]
        self.assertIn("CARS_22", keys)
        self.assertIn("PCARS_23", keys)
        self.assertIn("LCARS_24_25", keys)
        self.assertIn("TKARS_29_30", keys)

    def test_selects_and_runs_era_feature(self):
        central = PCARSCentral(Path("PCARS/config.json"))
        central.Boot()
        result = central.SelectEra("CARS_22")
        self.assertEqual(result["era"], "CARS_22")
        feature_result = central.Feature("command_console", {"payload": "test"})
        self.assertEqual(feature_result["feature"], "command_console")
        self.assertEqual(feature_result["era"], "CARS_22")

    def test_unknown_feature_returns_error(self):
        central = PCARSCentral(Path("PCARS/config.json"))
        central.Boot()
        central.SelectEra("PCARS_23")
        result = central.Feature("nonexistent_feature")
        self.assertEqual(result["error"], "feature_not_available")


if __name__ == "__main__":
    unittest.main()
