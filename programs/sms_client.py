"""SMS/Chat client stub with contact support"""
import sys, os
# ensure programs directory is on path when run as script
prog_dir = os.path.dirname(__file__)
if prog_dir not in sys.path:
    sys.path.insert(0, prog_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
)

from comm_base import ContactListWidget


class SMSClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS SMS Client")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # contacts on left
        self.contacts = ContactListWidget()
        self.contacts.currentItemChanged.connect(self._contact_changed)
        main_layout.addWidget(self.contacts, 1)

        # conversation area on right
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget, 2)

        self.conv_label = QLabel("Select a contact to begin")
        right_layout.addWidget(self.conv_label)

        self.history = QListWidget()
        right_layout.addWidget(self.history)

        self.input = QLineEdit()
        right_layout.addWidget(self.input)

        send = QPushButton("Send")
        right_layout.addWidget(send)
        send.clicked.connect(self._send)

        self.resize(600, 400)

        self.current_contact = None
        self.conversations = {}  # name -> list of strings

    def _contact_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current:
            c = current.data(0x0100)
            self.current_contact = c
            self.conv_label.setText(f"Conversation with {c.name}")
            self.history.clear()
            for msg in self.conversations.get(c.name, []):
                self.history.addItem(msg)
        else:
            self.current_contact = None
            self.conv_label.setText("Select a contact to begin")
            self.history.clear()

    def _send(self):
        if not self.current_contact:
            return
        text = self.input.text().strip()
        if text:
            msg = f"Me: {text}"
            self.history.addItem(msg)
            self.conversations.setdefault(self.current_contact.name, []).append(msg)
            self.input.clear()


if (__name__ == "__main__"):
    app = QApplication(sys.argv)
    win = SMSClient()
    win.show()
    sys.exit(app.exec())
