import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from programs.learning.logic import DatabaseManager


def main():
    manager = DatabaseManager()
    manager.SyncIsoChipData(max_level='B2')

    stats = manager.get_statistics()
    print('ISO-chip sync complete.')
    print(f"Total vocabulary in DB: {stats.get('total_words', 0)}")
    print(f"By level: {stats.get('by_level', {})}")

    chip_db = manager.ResolveIsoChipDbPath()
    print(f"Source chip DB: {chip_db}")
    print(f"Chip DB exists: {chip_db.exists()}")

    if chip_db.exists():
        con = sqlite3.connect(str(chip_db))
        cur = con.cursor()
        for table in ['vocabulary', 'phrases', 'grammar_rules', 'mini_texts', 'tests']:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"chip.{table}: {count}")
        con.close()


if __name__ == '__main__':
    main()
