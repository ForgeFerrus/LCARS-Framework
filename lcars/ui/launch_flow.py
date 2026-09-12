from __future__ import annotations
# Titanium Bridge Migration: import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from lcars.ui.launcher_integrated import IntegratedLauncher
from lcars.ui.welcome import LCARSWelcomeScreen
from lcars.ui.desktop import LCARSDesktop

class LaunchFlow:
    def __init__(self):
        self.launcher = None
        self.welcome = None
        self.desktop = None
        ODN.Subscribe("Launcher.Launch", self.onLauncherComplete)
        ODN.Subscribe("Welcome.Dismissed", self.onWelcomeComplete)

    def start(self):
        self.launcher = IntegratedLauncher(autoLaunchDesktop=False)
        self.launcher.show()
        result = self.launcher.exec()
        if result:
            selection = self.launcher.selection()
            if selection:
                faction, era = selection
                ODN.Emit("Launcher.Launch", {"faction": faction, "era": era})

    def onLauncherComplete(self, data):
        faction = data.get("faction", "federation")
        era = data.get("era", "24th")
        self.welcome = LCARSWelcomeScreen()
        self.welcome.showFullScreen()

    def onWelcomeComplete(self, data):
        if self.welcome:
            self.welcome.close()
        if self.launcher:
            selection = self.launcher.selection()
            if selection:
                faction, era = selection
                self.desktop = LCARSDesktop(era_key=era, faction_key=faction)

    def run(self):
        self.start()

def runLaunchFlow():
    app = QApplication.instance() or QApplication(sys.argv)
    flow = LaunchFlow()
    flow.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    runLaunchFlow()
