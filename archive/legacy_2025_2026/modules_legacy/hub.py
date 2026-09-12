"""
LCARS Network Hub (Main Menu)
- ╨ж╨╡╨╜╤В╤А╨░╨╗╤М╨╜╨╕╨╣ ╨▓╤Г╨╖╨╛╨╗ ╨┤╨╗╤П ╨▓╨╕╨▒╨╛╤А╤Г ╤Б╤В╨░╨╜╤Ж╤Ц╤Ч/╨╝╨╛╨┤╤Г╨╗╤П (╨║╨╛╤А╨░╨▒╨╡╨╗╤М, ╤И╤В╨░╨▒-╨║╨▓╨░╤А╤В╨╕╤А╨░, ╨▒╨░╨╖╨░, ╨░╨║╨░╨┤╨╡╨╝╤Ц╤П, ╨░╤А╤Е╤Ц╨▓, ╨╝╤Г╨╖╨╡╨╣, ╨╗╨░╨▒╨╛╤А╨░╤В╨╛╤А╤Ц╤П, ╨╜╨░╤Г╨║╨╛╨▓╨░ ╤Б╤В╨░╨╜╤Ж╤Ц╤П)
- ╨Т╨╕╨▒╤Ц╤А ╨╡╨┐╨╛╤Е╨╕/╤А╨╡╨╢╨╕╨╝╤Г (24th, 25th, Klingon, Federation HQ, Starbase, Academy, ╤В╨╛╤Й╨╛)
- ╨Я╤Ц╨┤╤В╤А╨╕╨╝╨║╨░ ╤В╨╡╨╝╤Ц╨╖╨░╤Ж╤Ц╤Ч, ╤Ц╨╜╤В╨╡╨│╤А╨░╤Ж╤Ц╤Ч ╨┐╨╗╨░╨│╤Ц╨╜╤Ц╨▓, ╤Б╤Ж╨╡╨╜╨░╤А╤Ц╤Ч╨▓ ╨╖╨░╨┐╤Г╤Б╨║╤Г
- ╨Ъ╨╛╨╢╨╡╨╜ ╨▓╤Г╨╖╨╛╨╗ ╨▓╤Ц╨┤╨║╤А╨╕╨▓╨░╤Ф╤В╤М╤Б╤П ╤П╨║ ╨▓╨║╨╗╨░╨┤╨║╨░ ╨░╨▒╨╛ ╨╛╨║╤А╨╡╨╝╨╡ ╨▓╤Ц╨║╨╜╨╛
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: import sys
from lcars.ui.starship_node import StarshipNode
from lcars.ui.headquarters_node import HeadquartersNode

class StarbaseNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Starbase (╨Ч╨╛╤А╤П╨╜╨░ ╨▒╨░╨╖╨░): ╨Ы╨╛╨│╤Ц╤Б╤В╨╕╨║╨░, ╤А╨╡╨╝╨╛╨╜╤В"))

class AcademyNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Academy (╨Р╨║╨░╨┤╨╡╨╝╤Ц╤П): ╨Э╨░╨▓╤З╨░╨╜╨╜╤П, ╤В╤А╨╡╨╜╨░╨╢╨╡╤А╨╕"))

class ArchiveNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Archive (╨Р╤А╤Е╤Ц╨▓): ╨С╨░╨╖╨░ ╨╖╨╜╨░╨╜╤М, ╤Ц╤Б╤В╨╛╤А╤Ц╤П"))

class MuseumNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Museum (╨Ь╤Г╨╖╨╡╨╣): ╨Х╨║╤Б╨┐╨╛╨╖╨╕╤Ж╤Ц╤Ч, ╨┤╨╡╨╝╨╛"))

class LaboratoryNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Laboratory (╨Ы╨░╨▒╨╛╤А╨░╤В╨╛╤А╤Ц╤П): ╨Х╨║╤Б╨┐╨╡╤А╨╕╨╝╨╡╨╜╤В╨╕, sandbox"))

class ScienceStationNode(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Science Station (╨Э╨░╤Г╨║╨╛╨▓╨░ ╤Б╤В╨░╨╜╤Ж╤Ц╤П): ╨Р╨╜╨░╨╗╤Ц╨╖, ╤Б╨╕╨╝╤Г╨╗╤П╤Ж╤Ц╤Ч"))

class LCARSNetworkHub(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Network Hub - Main Menu")
        self.setMinimumSize(1200, 800)
        layout = QVBoxLayout(self)
        title = QLabel("LCARS GLOBAL NETWORK")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; color: orange; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        # ╨Ф╨╛╨┤╨░╤Ф╨╝╨╛ ╨▓╤Г╨╖╨╗╨╕ ╤П╨║ ╨▓╨║╨╗╨░╨┤╨║╨╕
        self.tabs.addTab(StarshipNode(), "╨Ъ╨╛╤А╨░╨▒╨╡╨╗╤М")
        self.tabs.addTab(HeadquartersNode(), "╨и╤В╨░╨▒-╨║╨▓╨░╤А╤В╨╕╤А╨░")
        self.tabs.addTab(StarbaseNode(), "╨Ч╨╛╤А╤П╨╜╨░ ╨▒╨░╨╖╨░")
        self.tabs.addTab(AcademyNode(), "╨Р╨║╨░╨┤╨╡╨╝╤Ц╤П")
        self.tabs.addTab(ArchiveNode(), "╨Р╤А╤Е╤Ц╨▓")
        self.tabs.addTab(MuseumNode(), "╨Ь╤Г╨╖╨╡╨╣")
        self.tabs.addTab(LaboratoryNode(), "╨Ы╨░╨▒╨╛╤А╨░╤В╨╛╤А╤Ц╤П")
        self.tabs.addTab(ScienceStationNode(), "╨Э╨░╤Г╨║╨╛╨▓╨░ ╤Б╤В╨░╨╜╤Ж╤Ц╤П")
        # TODO: ╨┤╨╛╨┤╨░╤В╨╕ ╨▓╨╕╨▒╤Ц╤А ╨╡╨┐╨╛╤Е╨╕, ╤Ц╨╜╤В╨╡╨│╤А╨░╤Ж╤Ц╤О ╨┐╨╗╨░╨│╤Ц╨╜╤Ц╨▓, ╤Б╤Ж╨╡╨╜╨░╤А╤Ц╤Ч ╨╖╨░╨┐╤Г╤Б╨║╤Г

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hub = LCARSNetworkHub()
    hub.show()
    sys.exit(app.exec())

# Backwards compatibility: some modules import `NetworkHub`
NetworkHub = LCARSNetworkHub
