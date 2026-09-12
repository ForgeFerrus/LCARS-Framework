"""Email program stub with contact support"""
import sys, os
# ensure programs directory is on path
prog_dir = os.path.dirname(__file__)
if prog_dir not in sys.path:
    sys.path.insert(0, prog_dir)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel
)

from comm_base import ContactListWidget


class EmailClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Email Client")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        self.contacts = ContactListWidget()
        self.contacts.currentItemChanged.connect(self._contact_changed)
        main_layout.addWidget(self.contacts,1)

        right_widget=QWidget()
        right_layout=QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget,2)

        self.conv_label = QLabel("Select a contact to begin")
        right_layout.addWidget(self.conv_label)

        self.inbox = QListWidget()
        right_layout.addWidget(self.inbox)

        self.compose = QLineEdit()
        right_layout.addWidget(self.compose)

        send = QPushButton("Send")
        right_layout.addWidget(send)
        send.clicked.connect(self._send)

        self.resize(600,400)
        self.current_contact=None
        self.messages={}

    def _contact_changed(self,current:QListWidgetItem,previous:QListWidgetItem):
        if current:
            c=current.data(0x0100)
            self.current_contact=c
            self.conv_label.setText(f"Emailing {c.name}")
            self.inbox.clear()
            for msg in self.messages.get(c.name,[]):
                self.inbox.addItem(msg)
        else:
            self.current_contact=None
            self.conv_label.setText("Select a contact to begin")
            self.inbox.clear()

    def _send(self):
        if not self.current_contact:
            return
        body=self.compose.text().strip()
        if body:
            msg=f"To {self.current_contact.name}: {body}"
            self.inbox.addItem(msg)
            self.messages.setdefault(self.current_contact.name,[]).append(msg)
            self.compose.clear()

if __name__=="__main__":
    app=QApplication(sys.argv)
    win=EmailClient()
    win.show()
    sys.exit(app.exec())
