# ◤ TITANIUM CONTACT DATABASE — СИСТЕМА КОНТАКТІВ LCARS ◢
import sqlite3
from typing import List, Optional
from dataclasses import dataclass
import uuid

@dataclass
class Contact:
    name: str
    faction: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[str] = None

class ContactDatabase:
    def __init__(self, path: str):
        self.path = path
        self.InitDb()

    def InitDb(self):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    faction TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    notes TEXT
                )
            """)
            cursor = conn.execute("SELECT COUNT(*) FROM contacts")
            if cursor.fetchone()[0] == 0:
                initial_contacts = [
                    Contact("Jean-Luc Picard", "Starfleet", "picard@enterprise.fed", "1701-D", "Bridge", "Captain", str(uuid.uuid4())),
                    Contact("William Riker", "Starfleet", "riker@enterprise.fed", "1701-D", "Bridge", "Commander", str(uuid.uuid4())),
                    Contact("Data", "Starfleet", "data@enterprise.fed", "1701-D", "Bridge", "Lt. Commander", str(uuid.uuid4()))
                ]
                for c in initial_contacts:
                    conn.execute("INSERT INTO contacts VALUES (?,?,?,?,?,?,?)",
                                 (c.id, c.name, c.faction, c.email, c.phone, c.address, c.notes))

    def search(self, query: str) -> List[Contact]:
        with sqlite3.connect(self.path) as conn:
            q = f"%{query}%"
            cursor = conn.execute("""
                SELECT id, name, faction, email, phone, address, notes FROM contacts
                WHERE name LIKE ? OR faction LIKE ? OR email LIKE ?
            """, (q, q, q))
            return [Contact(id=r[0], name=r[1], faction=r[2], email=r[3], phone=r[4], address=r[5], notes=r[6]) for r in cursor]

    def AddContact(self, c: Contact) -> str:
        cid = c.id or str(uuid.uuid4())
        with sqlite3.connect(self.path) as conn:
            conn.execute("INSERT INTO contacts VALUES (?,?,?,?,?,?,?)",
                         (cid, c.name, c.faction, c.email, c.phone, c.address, c.notes))
        return cid

    def UpdateContact(self, cid: str, name: str, faction: str, email: str, phone: str, address: str, notes: str):
        with sqlite3.connect(self.path) as conn:
            conn.execute("""
                UPDATE contacts SET name=?, faction=?, email=?, phone=?, address=?, notes=? WHERE id=?
            """, (name, faction, email, phone, address, notes, cid))

    def DeleteContact(self, cid: str):
        with sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM contacts WHERE id=?", (cid,))
