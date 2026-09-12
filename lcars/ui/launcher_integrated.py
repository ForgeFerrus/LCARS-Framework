from __future__ import annotations
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from typing import Sequence, Optional
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget, QWidget, QFrame
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.palette import LCARSColorGenerator, LCARSEra
from lcars.themes.theme import setup_lcars_font
from lcars.modules.sound_manager import get_sound_manager
from lcars.base.signal import ODN

DEFAULT_FACTIONS = ["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"]
DEFAULT_ERAS = ["22nd", "23rd", "23st", "24th", "24st", "25th", "29th"]

class IntegratedLauncher(QDialog):
    def __init__(self, factions: Sequence[str]=DEFAULT_FACTIONS, eras: Sequence[str]=DEFAULT_ERAS, parent=None, autoLaunchDesktop: bool = False):
        super().__init__(parent)
        setup_lcars_font()
        self.factions = factions
        self.eras = eras
        self.selectedFaction = factions[0]
        self.selectedEra = eras[0]
        self.eraEnum = LCARSEra.LCARS_25TH
        self.colorGen = LCARSColorGenerator(self.eraEnum)
        self.autoLaunchDesktop = autoLaunchDesktop
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setStyleSheet("background-color: transparent; color: white;")
        self.resize(1200, 800)
        
        main = QVBoxLayout(self)
        container = QWidget()
        container.setFixedSize(1200, 800)
        layout = QVBoxLayout(container)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        self.buildBoot()
        self.buildLogin()
        self.buildLauncher()
        self.buildDesktopPreview()
        
        main.addWidget(container)
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            x = (geom.width() - container.width()) // 2
            y = (geom.height() - container.height()) // 2
            self.move(x, y)
        
        QTimer.singleShot(400, self.startBoot)
        ODN.Subscribe("Launcher.Close", self.close)
    
    def buildBoot(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        hdr = QHBoxLayout()
        elb = QFrame()
        elb.setFixedSize(200, 70)
        elb.setStyleSheet(f"background:{self.colorGen.getColorAtIndex(0)}; border-top-left-radius: 40px; border-bottom-left-radius: 4px;")
        hdr.addWidget(elb)
        title = QLabel("◢ LCARS SYSTEM - INITIALIZATION")
        title.setStyleSheet(getLcarsFontStyle(22, 'normal'))
        hdr.addWidget(title)
        lay.addLayout(hdr)
        self.bootLog = QLabel("BOOT: STARTING")
        self.bootLog.setStyleSheet(getLcarsFontStyle(14, 'normal') + "; color: #4BBEBF;")
        lay.addWidget(self.bootLog)
        self.stack.addWidget(w)
    
    def buildLogin(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        title = QLabel("AUTHORIZATION PROTOCOL // SECURE ACCESS")
        title.setStyleSheet(getLcarsFontStyle(18, 'normal') + "; color: #FFCC33;")
        lay.addWidget(title)
        self.loginProgress = QFrame()
        self.loginProgress.setFixedWidth(50)
        self.loginProgress.setStyleSheet("background:#4BBEBF; height: 20px;")
        lay.addWidget(self.loginProgress)
        btn = QPushButton("AUTHORIZE")
        btn.clicked.connect(self.onAuthorize)
        btn.setFixedSize(200, 50)
        btn.setStyleSheet("background:#3366CC; color: white; border:none; border-radius:6px;")
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(w)
    
    def buildLauncher(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        title = QLabel("SYSTEM ACCESS // TEMPORAL ALIGNMENT")
        title.setStyleSheet(getLcarsFontStyle(20, 'normal'))
        lay.addWidget(title)
        
        self.factionBtns = {}
        for f in self.factions:
            b = QPushButton(f)
            b.clicked.connect(lambda ch, ff=f: self.selectFaction(ff))
            b.setFixedSize(250, 100)
            b.setStyleSheet(f"background:{getRandomButtonColor(self.eraEnum)}; color:black; border-radius:8px; {getLcarsFontStyle(18, 'bold')}")
            lay.addWidget(b)
            self.factionBtns[f] = b
        
        self.eraBtns = {}
        for e in self.eras:
            b = QPushButton(e.upper())
            b.clicked.connect(lambda ch, ee=e: self.selectEra(ee))
            b.setFixedSize(180, 60)
            b.setStyleSheet(f"background:{getRandomButtonColor(self.eraEnum)}; color:black; border-radius:6px; {getLcarsFontStyle(14, 'bold')}")
            lay.addWidget(b)
            self.eraBtns[e] = b
        
        launch = QPushButton("LAUNCH SYSTEM")
        launch.clicked.connect(self.onLaunch)
        launch.setFixedSize(300, 60)
        launch.setStyleSheet("background:#00FF00; color:black; border:none; border-radius:8px;")
        lay.addWidget(launch, alignment=Qt.AlignmentFlag.AlignCenter)
        self.stack.addWidget(w)
    
    def buildDesktopPreview(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lbl = QLabel("DESKTOP PREVIEW — will launch main UI")
        lbl.setStyleSheet(getLcarsFontStyle(18, 'normal'))
        lay.addWidget(lbl)
        self.stack.addWidget(w)
    
    def startBoot(self):
        self.stack.setCurrentIndex(0)
        self.bootSteps = ['ISOLINEAR CORE INIT', 'NEXUS DATA HUB ONLINE', 'INTERFACE READY']
        self.bootIndex = 0
        self.bootTimer = QTimer()
        self.bootTimer.timeout.connect(self.bootTick)
        self.bootTimer.start(600)
    
    def bootTick(self):
        if self.bootIndex < len(self.bootSteps):
            self.bootLog.setText(self.bootSteps[self.bootIndex])
            self.bootIndex += 1
        else:
            self.bootTimer.stop()
            self.stack.setCurrentIndex(1)
    
    def onAuthorize(self):
        self.stack.setCurrentIndex(2)
    
    def onLaunch(self):
        ODN.Emit("Launcher.Selection", {"faction": self.selectedFaction, "era": self.selectedEra})
        if self.autoLaunchDesktop:
            from lcars.ui.desktop import LCARSDesktop
            desktop = LCARSDesktop()
            desktop.showFullScreen()
        else:
            self.accept()
    
    def selectFaction(self, faction: str):
        self.selectedFaction = faction
        ODN.Emit("Launcher.FactionChanged", {"faction": faction})
    
    def selectEra(self, era: str):
        self.selectedEra = era
        ODN.Emit("Launcher.EraChanged", {"era": era})
    
    def selection(self) -> Optional[tuple]:
        return (self.selectedFaction, self.selectedEra)

def runLauncher():
    app = QApplication.instance() or QApplication(sys.argv)
    dlg = IntegratedLauncher()
    dlg.show()
    res = dlg.exec()
    return dlg.selection() if res == QDialog.DialogCode.Accepted else None

if __name__ == '__main__':
    sel = runLauncher()
    print('Selection:', sel)

LCARSIntegratedLauncher = IntegratedLauncher
