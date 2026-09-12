"""Common utilities for communication program stubs.

This module provides simple base classes and helpers to load the contact
database and present a contact list.  It is deliberately minimal; programs
import whatever they need and extend it for their specific UI.
"""
from pathlib import Path
from typing import List

from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from lcars.modules.contact_db import ContactDatabase, Contact


def get_shared_db_path() -> str:
    """Return the default path to the contacts database in the project root."""
    root = Path(__file__).resolve().parent.parent
    return str(root / "contacts.sqlite")


class ContactListWidget(QListWidget):
    """A convenience widget that displays contacts from the shared database."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = ContactDatabase(get_shared_db_path())
        # lazy population; call populate() after UI layout is ready if you prefer
        self.populate()

    def populate(self, faction: str = None):
        """Reload the list, optionally filtering by faction."""
        self.clear()
        if faction:
            contacts = self.db.list_by_faction(faction)
        else:
            # fetch all; simple query by empty search term
            contacts = self.db.search("")
        for c in contacts:
            item = QListWidgetItem(c.name)
            item.setData(0x0100, c)  # store Contact object in user role
            self.addItem(item)

    def selected_contact(self) -> Contact | None:
        item = self.currentItem()
        if not item:
            return None
        return item.data(0x0100)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
