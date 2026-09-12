# project_mapper.py
import os
import ast
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path.cwd()
DB_FILE = PROJECT_ROOT / "project_map.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS files(
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE,
    size INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS classes(
    file TEXT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS functions(
    file TEXT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS imports(
    file TEXT,
    module TEXT
)
""")

conn.commit()

python_files = 0
total_files = 0

for root, dirs, files in os.walk(PROJECT_ROOT):

    if ".venv" in root:
        continue

    if "__pycache__" in root:
        continue

    for file in files:

        total_files += 1

        path = Path(root) / file

        try:
            size = path.stat().st_size
        except:
            size = 0

        cur.execute(
            "INSERT OR REPLACE INTO files(path,size) VALUES(?,?)",
            (str(path), size)
        )

        if not file.endswith(".py"):
            continue

        python_files += 1

        try:
            source = path.read_text(
                encoding="utf-8",
                errors="ignore"
            )

            tree = ast.parse(source)

            for node in ast.walk(tree):

                if isinstance(node, ast.ClassDef):
                    cur.execute(
                        "INSERT INTO classes VALUES(?,?)",
                        (str(path), node.name)
                    )

                elif isinstance(node, ast.FunctionDef):
                    cur.execute(
                        "INSERT INTO functions VALUES(?,?)",
                        (str(path), node.name)
                    )

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        cur.execute(
                            "INSERT INTO imports VALUES(?,?)",
                            (str(path), alias.name)
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    cur.execute(
                        "INSERT INTO imports VALUES(?,?)",
                        (str(path), module)
                    )

        except Exception:
            pass

conn.commit()

report = PROJECT_ROOT / "PROJECT_REPORT.txt"

with open(report, "w", encoding="utf-8") as f:

    f.write("LCARS PROJECT REPORT\n")
    f.write("=" * 60 + "\n\n")

    f.write(f"FILES: {total_files}\n")
    f.write(f"PYTHON FILES: {python_files}\n\n")

    f.write("TOP CLASSES\n")
    f.write("-" * 40 + "\n")

    for row in cur.execute("""
        SELECT name,file
        FROM classes
        ORDER BY name
    """):
        f.write(f"{row[0]} -> {row[1]}\n")

conn.close()

print()
print("=" * 60)
print("PROJECT SCAN COMPLETE")
print("DB :", DB_FILE)
print("TXT:", report)
print("=" * 60)