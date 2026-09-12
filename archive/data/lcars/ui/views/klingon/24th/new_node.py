from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
try: from lcars.ui.onboard import OnboardComputerView
except: OnboardComputerView = None

class NewNodeView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("KLINGON EMPIRE 24TH CENTURY CORE"))
    def ask_computer(self):
        if OnboardComputerView: self.c = OnboardComputerView(); self.c.show()
