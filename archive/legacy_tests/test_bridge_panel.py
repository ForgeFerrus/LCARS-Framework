import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# ensure project root on path
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication

from lcars.ui.panels.bridge import BridgePanel
from lcars.modules.config_manager import config_manager
from lcars.themes.palette import LCARSEra, FactionEra
from lcars.system.alert import alert_system, AlertLevel


class TestBridgePanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def setUp(self):
        # reset config and provide a mocked board computer
        config_manager.configs['app'] = {}
        self.mock_bc = MagicMock()
        self.mock_bc._system_metrics = {'cpu_percent': 5, 'mem_percent': 10}
        self.mock_bc.run_nova_workflow = MagicMock(return_value="OK")
        # patch get_computer to return our mock
        self.patcher = patch('lcars.ui.panels.bridge.get_computer', return_value=self.mock_bc)
        self.mock_get = self.patcher.start()
        # patch LCARSAgent so it doesn't require real network
        self.agent_patcher = patch('lcars.ui.panels.bridge.LCARSAgent', return_value=MagicMock())
        self.mock_agent = self.agent_patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.agent_patcher.stop()

    def test_instantiation_and_defaults(self):
        panel = BridgePanel(era=LCARSEra.LCARS_25TH, faction=FactionEra.KLINGON)
        # verify attributes set
        self.assertEqual(panel.era, LCARSEra.LCARS_25TH)
        self.assertEqual(panel.faction, FactionEra.KLINGON)
        self.assertEqual(panel.propulsion_mode, 'impulse')
        panel.close()

    def test_propulsion_toggle_updates(self):
        panel = BridgePanel()
        panel._set_propulsion_mode('warp')
        self.assertEqual(panel.propulsion_mode, 'warp')
        # warp_bar stylesheet should contain accent colour (p1 or alert)
        self.assertIn('background', panel.warp_bar.styleSheet())
        panel._set_propulsion_mode('impulse')
        self.assertEqual(panel.propulsion_mode, 'impulse')
        panel.close()

    def test_alert_changes_warp_bar(self):
        panel = BridgePanel()
        # normal level should use theme accent
        alert_system.set_level(AlertLevel.NORMAL)
        before = panel.warp_bar.styleSheet()
        alert_system.set_level(AlertLevel.RED)
        after = panel.warp_bar.styleSheet()
        self.assertNotEqual(before, after)
        panel.close()

    def test_screenshot_button_and_capture(self):
        panel = BridgePanel()
        # verify that the button exists in the layout
        found = False
        for child in panel.findChildren(LCARSButton):
            if child.text() == "SCREENSHOT":
                found = True
                # simulate click
                child.click()
                break
        self.assertTrue(found, "SCREENSHOT button should be present")
        # after clicking, label should have a pixmap set
        pix = panel.screenshot_label.pixmap()
        self.assertIsNotNone(pix)
        panel.close()

    def test_run_actions_do_not_raise(self):
        panel = BridgePanel()
        # these should execute without exception and log something
        panel._run_scan()
        panel._run_bioscan()
        panel._run_syst_lock()
        panel._run_nova()
        # nova workflow called on mock
        self.mock_bc.run_nova_workflow.assert_called_once_with('default')
        panel.close()

    def test_copilot_initialization_and_query(self):
        panel = BridgePanel()
        # copilot attribute should exist
        self.assertIsNotNone(panel.bc.copilot)
        # calling ask should trigger mock agent
        panel._ask_computer()
        # agent.ask was called in the patched object
        panel.bc.copilot.ask.assert_called()
        panel.close()


if __name__ == '__main__':
    unittest.main()
