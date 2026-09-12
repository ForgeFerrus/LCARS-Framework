import os
from lcars.modules.library import Library


def test_index_and_db_upsert(tmp_path):
    # Підготувати тимчасову структуру секції
    sector_dir = tmp_path / "federation"
    sector_dir.mkdir(parents=True)
    # створити 2 файли
    (sector_dir / "doc1.txt").write_text("hello world", encoding="utf-8")
    (sector_dir / "img1.png").write_bytes(b"PNGDATA")

    # Простий mock DB для перевірки upsert викликів
    class MockDB:
        def __init__(self):
            self.records = []
            self.connection = True

        def upsert_file_record(self, sector, name, path, ftype, size_kb, metadata=None):
            self.records.append({
                "sector": sector,
                "name": name,
                "path": path,
                "type": ftype,
                "size_kb": size_kb,
            })
            return True

        def get_files_by_sector(self, sector):
            return [r for r in self.records if r["sector"] == sector]

    mock_db = MockDB()
    lib = Library(base_path=str(tmp_path), db=mock_db)

    # Запустити індексацію секції DOCUMENTS і перевірити, що DB отримала записи
    total = lib.index_sector("DOCUMENTS")
    assert total == 2
    assert len(mock_db.records) == 2

    # list_files має повернути DB-повернення (не файловий fallback)
    listed = lib.list_files("DOCUMENTS")
    assert isinstance(listed, list)
    assert len(listed) == 2


def test_index_handles_db_upsert_exception(tmp_path):
    # Підготувати тимчасову структуру секції з трьома файлами
    sector_dir = tmp_path / "federation"
    sector_dir.mkdir(parents=True)
    (sector_dir / "ok.txt").write_text("ok", encoding="utf-8")
    (sector_dir / "bad.txt").write_text("bad", encoding="utf-8")
    (sector_dir / "ok2.txt").write_text("ok2", encoding="utf-8")

    # Mock DB який під час upsert кидає виключення для одного файлу
    class MockDBFail:
        def __init__(self):
            self.records = []
            self.connection = True

        def upsert_file_record(self, sector, name, path, ftype, size_kb, metadata=None):
            if "bad" in name:
                raise RuntimeError("simulated DB failure")
            self.records.append(name)
            return True

        def get_files_by_sector(self, sector):
            return [ {"name": n} for n in self.records ]

    mock_db = MockDBFail()
    lib = Library(base_path=str(tmp_path), db=mock_db)

    total = lib.index_sector("FEDERATION")
    # Два успішних файли, один пропущений через помилку
    assert total == 2
    assert len(mock_db.records) == 2


def test_list_files_db_failure_fallback(tmp_path):
    sector_dir = tmp_path / "federation"
    sector_dir.mkdir(parents=True)
    (sector_dir / "file.txt").write_text("x", encoding="utf-8")

    class MockDBBroken:
        def __init__(self):
            self.connection = True

        def get_files_by_sector(self, sector):
            raise RuntimeError("simulated read error")

    lib = Library(base_path=str(tmp_path), db=MockDBBroken())
    res = lib.list_files("FEDERATION")
    # fallback до файлової системи
    assert isinstance(res, list)
    assert len(res) == 1
