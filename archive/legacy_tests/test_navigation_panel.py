import unittest
from PyQt6.QtWidgets import QApplication
from lcars.ui.panels.navigation import NavigationPanel

class NavigationPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._app = QApplication.instance() or QApplication([])

    def test_warp_controls_update_label(self):
        panel = NavigationPanel()
        # initial state
        self.assertIn("STATIONARY", panel.warp_status_lbl.text())
        # simulate warp button calls
        panel._set_warp_speed("WARP 3")
        self.assertIn("WARP 3", panel.warp_status_lbl.text())
        panel._set_warp_speed()  # stop
        self.assertIn("STATIONARY", panel.warp_status_lbl.text())
        panel.close()

if __name__ == '__main__':
    unittest.main()
