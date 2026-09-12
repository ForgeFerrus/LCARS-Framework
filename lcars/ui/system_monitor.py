from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel

class SystemMonitorWidget(QWidget):
    """Minimal system monitor stub to satisfy imports in Desktop/Central."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("System Monitor (stub)"))
