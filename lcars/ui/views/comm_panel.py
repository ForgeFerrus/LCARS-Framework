"""
LCARS Communication Panel (PyQt6)
Unified UI for contacts, messages, and calls.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt
from lcars.modules.comm import comm_system, Contact, Message, Call

class CommPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Communication Panel")
        self.resize(800, 600)
        layout = QVBoxLayout(self)

        # Tabs (simple buttons for now)
        btn_row = QHBoxLayout()
        self.btn_contacts = QPushButton("Contacts")
        self.btn_messages = QPushButton("Messages")
        self.btn_calls = QPushButton("Calls")
        btn_row.addWidget(self.btn_contacts)
        btn_row.addWidget(self.btn_messages)
        btn_row.addWidget(self.btn_calls)
        layout.addLayout(btn_row)

        # Main area
        self.stack = QWidget()
        self.stack_layout = QVBoxLayout(self.stack)
        layout.addWidget(self.stack)

        # Contacts view
        self.contacts_list = QListWidget()
        self.contact_add = QLineEdit()
        self.contact_add.setPlaceholderText("Add contact name...")
        self.contact_add_btn = QPushButton("Add Contact")
        self.stack_layout.addWidget(QLabel("Contacts"))
        self.stack_layout.addWidget(self.contacts_list)
        self.stack_layout.addWidget(self.contact_add)
        self.stack_layout.addWidget(self.contact_add_btn)
        self.contacts_list.hide()
        self.contact_add.hide()
        self.contact_add_btn.hide()

        # Messages view
        self.messages_list = QListWidget()
        self.message_input = QTextEdit()
        self.message_send_btn = QPushButton("Send Message")
        self.stack_layout.addWidget(QLabel("Messages"))
        self.stack_layout.addWidget(self.messages_list)
        self.stack_layout.addWidget(self.message_input)
        self.stack_layout.addWidget(self.message_send_btn)
        self.messages_list.hide()
        self.message_input.hide()
        self.message_send_btn.hide()

        # Calls view
        self.calls_list = QListWidget()
        self.stack_layout.addWidget(QLabel("Calls"))
        self.stack_layout.addWidget(self.calls_list)
        self.calls_list.hide()

        # Connect buttons
        self.btn_contacts.clicked.connect(self.show_contacts)
        self.btn_messages.clicked.connect(self.show_messages)
        self.btn_calls.clicked.connect(self.show_calls)
        self.contact_add_btn.clicked.connect(self.add_contact)
        self.message_send_btn.clicked.connect(self.send_message)

        self.show_contacts()

    def show_contacts(self):
        self.contacts_list.show()
        self.contact_add.show()
        self.contact_add_btn.show()
        self.messages_list.hide()
        self.message_input.hide()
        self.message_send_btn.hide()
        self.calls_list.hide()
        self.refresh_contacts()

    def show_messages(self):
        self.contacts_list.hide()
        self.contact_add.hide()
        self.contact_add_btn.hide()
        self.messages_list.show()
        self.message_input.show()
        self.message_send_btn.show()
        self.calls_list.hide()
        self.refresh_messages()

    def show_calls(self):
        self.contacts_list.hide()
        self.contact_add.hide()
        self.contact_add_btn.hide()
        self.messages_list.hide()
        self.message_input.hide()
        self.message_send_btn.hide()
        self.calls_list.show()
        self.refresh_calls()

    def refresh_contacts(self):
        self.contacts_list.clear()
        for c in comm_system.search_contacts(""):
            self.contacts_list.addItem(f"[{c.id}] {c.name} | {c.faction} | {c.email} | {c.phone}")

    def refresh_messages(self):
        self.messages_list.clear()
        # For demo, show all messages (in real UI, filter by participant)
        for m in comm_system.get_messages(""):
            self.messages_list.addItem(f"[{m.id}] {m.timestamp:.0f} {m.sender} -> {m.recipient}: {m.content} [{m.status}]")

    def refresh_calls(self):
        self.calls_list.clear()
        for c in comm_system.get_calls(""):
            self.calls_list.addItem(f"[{c.id}] {c.timestamp:.0f} {c.caller} -> {c.callee} duration={c.duration} status={c.status}")

    def add_contact(self):
        name = self.contact_add.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Contact name required.")
            return
        contact = Contact(name=name)
        comm_system.add_contact(contact)
        self.contact_add.clear()
        self.refresh_contacts()

    def send_message(self):
        # For demo, use fixed sender/recipient
        content = self.message_input.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Input Error", "Message content required.")
            return
        comm_system.send_message("user", "recipient", content)
        self.message_input.clear()
        self.refresh_messages()
