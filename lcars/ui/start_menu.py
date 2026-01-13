"""Start Menu prototype for LCARS OS MVP

Provides a fullscreen tile-based launcher with signals for launching
applications and basic system actions (Lock, Exit, Settings).
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal

class StartMenu(QWidget):
    launchRequested = pyqtSignal(str)
    exitRequested = pyqtSignal()
    settingsRequested = pyqtSignal()
    lockRequested = pyqtSignal()

    def __init__(self, applications=None, parent=None):
        super().__init__(parent)
        self.applications = applications or [
            {'name': 'LCARS Constructor', 'file': 'constructor.py'},
            {'name': 'Geant4 Workstation', 'file': 'lcars/ui/geant4_workstation.py'},
            {'name': 'System Monitor', 'file': 'lcars/ui/system_monitor.py'},
            {'name': 'Health Check', 'file': 'lcars/ui/health_check.py'},
        ]
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #000000; color: #FFFFFF; }
            QLabel.title { color: #FFFFFF; font-size: 32px; font-weight: bold; padding: 20px; }
            QPushButton.tile { background-color: #37A6D1; color: #000000; border-radius: 6px; font-size: 18px; padding: 18px; }
            QPushButton.tile:hover { background-color: #59c4e6; }
            QPushButton.action { background-color: #FF6753; color: #000000; border-radius: 6px; padding: 10px 16px; }
        """)

        main = QVBoxLayout(self)
        header = QHBoxLayout()
        title = QLabel("LCARS START MENU")
        title.setObjectName("title")
        title.setProperty("class", "title")
        header.addWidget(title)
        header.addStretch()

        # Control buttons
        exit_btn = QPushButton("EXIT")
        exit_btn.setProperty("class", "action")
        exit_btn.clicked.connect(lambda: self.exitRequested.emit())
        header.addWidget(exit_btn)

        settings_btn = QPushButton("SETTINGS")
        settings_btn.setProperty("class", "action")
        settings_btn.clicked.connect(lambda: self.settingsRequested.emit())
        header.addWidget(settings_btn)

        lock_btn = QPushButton("LOCK")
        lock_btn.setProperty("class", "action")
        lock_btn.clicked.connect(lambda: self.lockRequested.emit())
        header.addWidget(lock_btn)

        main.addLayout(header)

        grid = QGridLayout()
        cols = 2
        for i, app in enumerate(self.applications):
            r = i // cols
            c = i % cols

            btn = QPushButton(app['name'])
            btn.setProperty("class", "tile")
            btn.clicked.connect(lambda checked, f=app['file']: self.launchRequested.emit(f))
            grid.addWidget(btn, r, c)

        main.addLayout(grid)
        main.addStretch()

    def set_applications(self, apps):
        self.applications = apps
        # For prototype, we keep UI static; improvement: rebuild grid dynamically
