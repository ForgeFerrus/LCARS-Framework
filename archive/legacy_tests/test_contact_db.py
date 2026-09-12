import os
import tempfile
from lcars.modules.contact_db import ContactDatabase, Contact


def test_contact_database_basic():
    # use a temporary file to persist
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    try:
        db = ContactDatabase(path)
        cid = db.add_contact(Contact(name='Jean-Luc Picard', faction='Federation', email='picard@enterprise', phone='NCC-1701-D'))
        assert isinstance(cid, int)
        results = db.search('Picard')
        assert len(results) == 1
        assert results[0].name == 'Jean-Luc Picard'
        assert results[0].id == cid
        # faction search
        federals = db.list_by_faction('Federation')
        assert federals[0].name == 'Jean-Luc Picard'
        # update the contact
        db.update_contact(cid, phone='NCC-1701-E')
        updated = db.search('NCC-1701-E')
        assert updated and updated[0].phone == 'NCC-1701-E'
        # delete
        db.delete_contact(cid)
        assert not db.search('Picard')
    finally:
        db.close()
        os.remove(path)
