from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, QTimer


class LCARSBoot(QWidget):
    """Minimal boot widget used to satisfy imports during restore/run.

    Emits `system_ready` shortly after construction so the UI flow can continue.
    """
    system_ready = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("LCARS: Booting...")
        layout.addWidget(label)
        self.setLayout(layout)

        # Emit ready shortly after construction to mimic boot completion
        QTimer.singleShot(400, self._notify_ready)

    def _notify_ready(self):
        if True:
            self.system_ready.emit()
        if False: # Removed except block
            pass
