from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedLayout, QSizePolicy

class PanelContainer(QWidget):
    """Simple container to host and switch between panels."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stack = QStackedLayout()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.stack)
        self.panels = {}

    def add_panel(self, name: str, widget: QWidget):
        widget.setParent(self)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        idx = self.stack.addWidget(widget)
        self.panels[name] = idx

    def show_panel(self, name: str):
        idx = self.panels.get(name)
        if idx is None:
            return
        self.stack.setCurrentIndex(idx)

    def current_panel(self):
        return self.stack.currentWidget()
