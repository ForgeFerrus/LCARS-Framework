"""
Modern LCARS Communication Panel (PyQt6)
Multi-channel, extensible, with plugin-ready architecture.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QLineEdit, QMessageBox, QTabWidget, QComboBox
)
from PyQt6.QtCore import Qt
from lcars.modules.comm import comm_system, Contact, Message, Call

CHANNELS = [
    ("Contacts", "contacts"),
    ("Email", "email"),
    ("Internal Messenger", "internal"),
    ("Telegram", "telegram"),
    ("Facebook", "facebook"),
    ("Viber", "viber"),
    ("WhatsApp", "whatsapp"),
    ("Twitter", "twitter"),
    ("Google Drive", "gdrive"),
    ("OneDrive", "onedrive"),
    ("GitHub", "github"),
    ("Smartphone", "phone"),
]

class CommPanelModern(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Communication Center")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- Contacts Tab ---
        self.tab_contacts = QWidget()
        contacts_layout = QVBoxLayout(self.tab_contacts)
        self.contacts_list = QListWidget()
        self.contact_add = QLineEdit()
        self.contact_add.setPlaceholderText("Add contact name...")
        self.contact_add_btn = QPushButton("Add Contact")
        contacts_layout.addWidget(QLabel("Contacts"))
        contacts_layout.addWidget(self.contacts_list)
        contacts_layout.addWidget(self.contact_add)
        contacts_layout.addWidget(self.contact_add_btn)
        self.tabs.addTab(self.tab_contacts, "Contacts")
        self.contact_add_btn.clicked.connect(self.add_contact)
        self.refresh_contacts()

        # --- Email Tab ---
        self.tab_email = QWidget()
        email_layout = QVBoxLayout(self.tab_email)
        self.email_account = QLineEdit()
        self.email_account.setPlaceholderText("Email address (any)")
        self.email_connect_btn = QPushButton("Connect Email")
        self.email_inbox = QListWidget()
        self.email_compose = QTextEdit()
        self.email_send_btn = QPushButton("Send Email")
        email_layout.addWidget(QLabel("Email"))
        email_layout.addWidget(self.email_account)
        email_layout.addWidget(self.email_connect_btn)
        email_layout.addWidget(self.email_inbox)
        email_layout.addWidget(self.email_compose)
        email_layout.addWidget(self.email_send_btn)
        self.tabs.addTab(self.tab_email, "Email")
        # TODO: Connect email logic

        # --- Internal Messenger Tab ---
        self.tab_internal = QWidget()
        internal_layout = QVBoxLayout(self.tab_internal)
        self.internal_contacts = QComboBox()
        self.internal_messages = QListWidget()
        self.internal_input = QTextEdit()
        self.internal_send_btn = QPushButton("Send Message")
        internal_layout.addWidget(QLabel("Internal Messenger"))
        internal_layout.addWidget(self.internal_contacts)
        internal_layout.addWidget(self.internal_messages)
        internal_layout.addWidget(self.internal_input)
        internal_layout.addWidget(self.internal_send_btn)
        self.tabs.addTab(self.tab_internal, "Messenger")
        self.internal_send_btn.clicked.connect(self.send_internal_message)
        self.refresh_internal_contacts()
        self.refresh_internal_messages()

        # --- External Channels (placeholders) ---
        for label, key in CHANNELS[3:]:
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            tab_layout.addWidget(QLabel(f"{label} integration coming soon..."))
            self.tabs.addTab(tab, label)

    def refresh_contacts(self):
        self.contacts_list.clear()
        for c in comm_system.search_contacts(""):
            self.contacts_list.addItem(f"[{c.id}] {c.name} | {c.faction} | {c.email} | {c.phone}")

    def add_contact(self):
        name = self.contact_add.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Contact name required.")
            return
        contact = Contact(name=name)
        comm_system.add_contact(contact)
        self.contact_add.clear()
        self.refresh_contacts()
        self.refresh_internal_contacts()

    def refresh_internal_contacts(self):
        self.internal_contacts.clear()
        for c in comm_system.search_contacts(""):
            self.internal_contacts.addItem(f"{c.name}")

    def refresh_internal_messages(self):
        self.internal_messages.clear()
        # For demo, show all messages
        for m in comm_system.get_messages(""):
            self.internal_messages.addItem(f"[{m.id}] {m.timestamp:.0f} {m.sender} -> {m.recipient}: {m.content} [{m.status}]")

    def send_internal_message(self):
        sender = "user"  # TODO: Selectable sender
        recipient = self.internal_contacts.currentText()
        content = self.internal_input.toPlainText().strip()
        if not recipient or not content:
            QMessageBox.warning(self, "Input Error", "Recipient and content required.")
            return
        comm_system.send_message(sender, recipient, content)
        self.internal_input.clear()
        self.refresh_internal_messages()
