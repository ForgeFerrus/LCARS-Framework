"""
Modern LCARS Communication Panel (PyQt6)
Multi-channel, extensible, with plugin-ready architecture.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QLineEdit, QMessageBox, QTabWidget, QComboBox
)
from lcars.themes.theme import font_manager
from lcars.system.localization import LOCALIZATION as Language
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


class CommunicationPanelModern(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Communication Center")
        self.resize(1000, 700)
        layout = QVBoxLayout(self)

        # --- Language/Font selection ---
        lang_font_layout = QHBoxLayout()
        self.lang_combo = QComboBox()
        self.font_combo = QComboBox()
        self.lang_combo.setToolTip("Select language")
        self.font_combo.setToolTip("Select font")
        # Populate languages
        for code, name in Language.get_supported_languages().items():
            self.lang_combo.addItem(f"{name} ({code})", code)
        # Populate fonts
        for key, family in font_manager.fonts.items():
            self.font_combo.addItem(family, key)
        lang_font_layout.addWidget(QLabel("Language:"))
        lang_font_layout.addWidget(self.lang_combo)
        lang_font_layout.addWidget(QLabel("Font:"))
        lang_font_layout.addWidget(self.font_combo)
        layout.addLayout(lang_font_layout)

        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        self.font_combo.currentIndexChanged.connect(self.on_font_changed)

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

        # Apply initial font
        self.apply_selected_font()

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
    def on_language_changed(self):
        code = self.lang_combo.currentData()
        Language.set_language(code)
        self.apply_selected_font()

    def on_font_changed(self):
        self.apply_selected_font()

    def apply_selected_font(self):
        # Get selected font family
        font_key = self.font_combo.currentData()
        family = font_manager.fonts.get(font_key)
        if not family:
            family = "LCARS"
        # Apply to all relevant widgets
        font_css = f"font-family: '{family}';"
        # Contacts tab
        self.contacts_list.setStyleSheet(font_css)
        self.contact_add.setStyleSheet(font_css)
        # Email tab
        self.email_account.setStyleSheet(font_css)
        self.email_inbox.setStyleSheet(font_css)
        self.email_compose.setStyleSheet(font_css)
        # Internal messenger tab
        self.internal_contacts.setStyleSheet(font_css)
        self.internal_messages.setStyleSheet(font_css)
        self.internal_input.setStyleSheet(font_css)
        # (Optionally: set for all tabs/labels)
        # For demo, set on main widget too
        self.setStyleSheet(font_css)

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
