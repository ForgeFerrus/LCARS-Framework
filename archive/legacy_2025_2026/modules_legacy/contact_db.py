#Проста база даних контактів для внутрішніх комунікацій LCARS.
# Забезпечує легке сховище контактів на основі SQLite, яке використовується
# панелями комунікації/навігації та додатками для повідомлень. Розроблено
# незалежно від UI, щоб тести могли використовувати її напряму.
#   Приклад використання::
#   from lcars.modules.contact_db import ContactDatabase, Contact
#   db = ContactDatabase('contacts.sqlite')
#   db.add_contact(Contact(name='James Kirk', faction='Federation',
#         email='kirk@starfleet', phone='NCC-1701'))
#    results = db.search('Kirk')
#Файл бази даних створюється ліниво; можна передати ``:memory:`` для
#зберігання в пам'яті (використовується в юніт-тестах).
# При використанні в UI, база даних зберігається в корені проекту як
from __future__ import annotations
# Titanium Bridge Migration: import sqlite3
# Titanium Bridge Migration: from dataclasses import dataclass, asdict
# Titanium Bridge Migration: from typing import List, Optional

@dataclass
class Contact:
    id: Optional[int] = None
    name: str = ""
    faction: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None  # freeform remarks

class ContactDatabase:
    def __init__(self, path: str = ":memory:"):
        # Ініціалізація бази даних, створення таблиці контактів
        self.path = path
        self.conn = sqlite3.connect(self.path)
        self._ensure_table()

    def _ensure_table(self):
        # Створення таблиці контактів, якщо вона ще не існує
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                faction TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                notes TEXT
            )
            """
        )
        self.conn.commit()

    def add_contact(self, contact: Contact) -> int:
        # Додавання нового контакту до бази даних
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO contacts (name, faction, email, phone, address, notes) VALUES (?,?,?,?,?,?)",
            (
                contact.name,
                contact.faction,
                contact.email,
                contact.phone,
                contact.address,
                contact.notes,
            ),
        )
        self.conn.commit()
        cid = cur.lastrowid if cur.lastrowid is not None else 0
        contact.id = cid
        return cid

    def search(self, term: str) -> List[Contact]:
        # Пошук контактів за ключовим словом у будь-якому полі
        pattern = f"%{term}%"
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id,name,faction,email,phone,address,notes FROM contacts"
            " WHERE name LIKE ? OR faction LIKE ? OR email LIKE ? OR phone LIKE ? OR address LIKE ? OR notes LIKE ?",
            (pattern, pattern, pattern, pattern, pattern, pattern),
        )
        rows = cur.fetchall()
        return [Contact(*row) for row in rows]

    def list_by_faction(self, faction: str) -> List[Contact]:
        # Повертає список контактів за фракцією
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,faction,email,phone,address,notes FROM contacts WHERE faction = ?", (faction,))
        return [Contact(*row) for row in cur.fetchall()]

    def update_contact(self, contact_id: int, **fields) -> None:
        # Оновлення полів контакту за id
        if not fields:
            return
        cols = []
        vals = []
        for k, v in fields.items():
            cols.append(f"{k} = ?")
            vals.append(v)
        vals.append(contact_id)
        cur = self.conn.cursor()
        cur.execute(f"UPDATE contacts SET {', '.join(cols)} WHERE id = ?", tuple(vals))
        self.conn.commit()

    def delete_contact(self, contact_id: int) -> None:
        # Видалення контакту за id
        cur = self.conn.cursor()
        cur.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        self.conn.commit()

    def close(self):
        # Закриває з'єднання з базою даних
        self.conn.close()
