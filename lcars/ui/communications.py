from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class CommunicationsPanel(QWidget):
    """Stub for CommunicationsPanel used by Desktop."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Communications (stub)"))
