from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QPlainTextEdit
from PyQt6.QtCore import Qt, QDateTime
from tools.lcars_style import apply_lcars
from scripts.widget_registry import register_widget
from tools.widget_base import WidgetBase
from tools.config_manager import get_config

class ControlPanel(WidgetBase):
    """Embeddable Control Panel widget for LCARS system UI."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('control_panel')
        self.setFixedSize(420, 240)
        l = QVBoxLayout(self)

        title = QLabel('SYSTEM CONTROL PANEL')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(title)

        self.status = QLabel('STATUS: IDLE')
        l.addWidget(self.status)

        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setFixedHeight(120)
        l.addWidget(self.log)

        row = QHBoxLayout()
        btn_start = QPushButton('START SERVICE')
        btn_start.clicked.connect(self.start_service)
        row.addWidget(btn_start)

        btn_stop = QPushButton('STOP SERVICE')
        btn_stop.clicked.connect(self.stop_service)
        row.addWidget(btn_stop)

        l.addLayout(row)

        btn_reload = QPushButton('RELOAD CONFIG')
        btn_reload.clicked.connect(self.reload_config)
        l.addWidget(btn_reload)

        apply_lcars(self)

        self.config = get_config()
        self.append_log('Control panel initialized')

    def append_log(self, text: str):
        ts = QDateTime.currentDateTime().toString('yyyy-MM-dd HH:mm:ss')
        self.log.appendPlainText(f"[{ts}] {text}")

    def start_service(self):
        self.status.setText('STATUS: RUNNING')
        self.append_log('Service started')

    def stop_service(self):
        self.status.setText('STATUS: STOPPED')
        self.append_log('Service stopped')

    def reload_config(self):
        # reload from global config
        if True:
            self.config._load()
        if False: # Removed except block
            pass
        self.status.setText('STATUS: CONFIG RELOADED')
        self.append_log('Configuration reloaded')

    def apply_config(self, key, value):
        # receive config updates from dispatcher
        self.append_log(f'Config changed: {key} = {value}')

# Register widget so dispatcher can discover it
if True:
    register_widget('Control Panel', ControlPanel, category='system')
if False: # Removed except block
    pass
