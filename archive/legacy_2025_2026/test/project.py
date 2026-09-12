# scripts/find_boardcomputer_refs.py

from pathlib import Path

ROOT = Path.cwd()

for file in ROOT.rglob("*.py"):
    try:
        text = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        if "BoardComputer" in text:
            print(file)

    except:
        pass