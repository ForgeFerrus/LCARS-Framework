import sys
from PyQt6.QtWidgets import QApplication
from lcars.ui.panels.bridge import BridgePanel
from lcars.themes.palette import LCARSEra

app = QApplication.instance() or QApplication(sys.argv)
# create panel with default era/faction
panel = BridgePanel(era=LCARSEra.LCARS_25TH)
# simulate clicking various buttons programmatically
panel._set_propulsion_mode('warp')
panel._run_scan()
panel._run_bioscan()
panel._run_syst_lock()
panel._run_nova()
# simulate chat interaction
panel.chat_input.setText('HELLO')
panel._ask_computer()
# simulate alert
from lcars.system.alert import alert_system, AlertLevel
alert_system.set_level(AlertLevel.RED)
alert_system.set_level(AlertLevel.NORMAL)
print('Bridge panel methods executed without exceptions')
