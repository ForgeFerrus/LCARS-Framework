"""Phone/VoIP stub with contact support"""
import sys, os
# ensure programs directory is on path
prog_dir = os.path.dirname(__file__)
if prog_dir not in sys.path:
    sys.path.insert(0, prog_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel
)

from comm_base import ContactListWidget


class PhoneApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Phone")
        central = QWidget()
        self.setCentralWidget(central)
        main = QHBoxLayout(central)

        self.contacts = ContactListWidget()
        self.contacts.currentItemChanged.connect(self._fill_number)
        main.addWidget(self.contacts,1)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        main.addWidget(right,2)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        right_layout.addWidget(self.history)
        self.number = QLineEdit()
        right_layout.addWidget(self.number)
        call = QPushButton("Call")
        right_layout.addWidget(call)
        call.clicked.connect(self._call)
        self.resize(500,400)

    def _fill_number(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current:
            c=current.data(0x0100)
            if c.phone:
                self.number.setText(c.phone)

    def _call(self):
        num = self.number.text().strip()
        if num:
            self.history.append(f"Calling {num}...")
            self.number.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PhoneApp()
    win.show()
    sys.exit(app.exec())
