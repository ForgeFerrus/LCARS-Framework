import csv
import sqlite3
import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parents[3]
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

chipDbPath = projectRoot / "lcars" / "database" / "iso_chip_b1_plus.db"


def ensureSchema(conn):
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS vocabulary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            ukrainian TEXT NOT NULL,
            part_of_speech TEXT,
            level TEXT,
            example_sentence TEXT,
            pronunciation TEXT,
            difficulty INTEGER DEFAULT 1,
            last_reviewed DATETIME,
            next_review DATETIME,
            tags TEXT,
            category TEXT DEFAULT 'general'
        )
        """
    )
    conn.commit()


def toInt(value, fallback):
    text = str(value).strip()
    if text.isdigit():
        return int(text)
    return fallback


def pick(row, key, fallback=""):
    value = row.get(key, fallback)
    return str(value).strip()


def importCsv(csvPath):
    conn = sqlite3.connect(str(chipDbPath))
    ensureSchema(conn)
    cur = conn.cursor()

    inserted = 0
    updated = 0

    with open(csvPath, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            english = pick(row, "english")
            if not english:
                continue

            ukrainian = pick(row, "ukrainian")
            partOfSpeech = pick(row, "part_of_speech")
            level = pick(row, "level", "B1")
            exampleSentence = pick(row, "example_sentence")
            pronunciation = pick(row, "pronunciation")
            tags = pick(row, "tags")
            category = pick(row, "category", "general")
            difficulty = toInt(pick(row, "difficulty", "3"), 3)

            existing = cur.execute(
                "SELECT id FROM vocabulary WHERE english = ? AND level = ?",
                (english, level),
            ).fetchone()

            if existing:
                cur.execute(
                    """
                    UPDATE vocabulary
                    SET ukrainian = ?,
                        part_of_speech = ?,
                        example_sentence = ?,
                        pronunciation = ?,
                        difficulty = ?,
                        tags = ?,
                        category = ?
                    WHERE id = ?
                    """,
                    (
                        ukrainian,
                        partOfSpeech,
                        exampleSentence,
                        pronunciation,
                        difficulty,
                        tags,
                        category,
                        existing[0],
                    ),
                )
                updated += 1
            else:
                cur.execute(
                    """
                    INSERT INTO vocabulary
                    (english, ukrainian, part_of_speech, level, example_sentence, pronunciation, difficulty, tags, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        english,
                        ukrainian,
                        partOfSpeech,
                        level,
                        exampleSentence,
                        pronunciation,
                        difficulty,
                        tags,
                        category,
                    ),
                )
                inserted += 1

    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0]
    print(f"inserted={inserted} updated={updated} totalVocabulary={total}")
    conn.close()


def printTemplate(path):
    header = [
        "english",
        "ukrainian",
        "part_of_speech",
        "level",
        "example_sentence",
        "pronunciation",
        "difficulty",
        "tags",
        "category",
    ]
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerow([
            "responsibility",
            "відповідальність",
            "noun",
            "B1",
            "It is your responsibility.",
            "rɪˌspɒnsəˈbɪləti",
            "3",
            "exam,b1",
            "general",
        ])
    print(f"templateReady={path}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage:")
        print("  python programs/learning/seed/importLicensedLexicon.py <path_to_csv>")
        print("  python programs/learning/seed/importLicensedLexicon.py --template <output_csv>")
        sys.exit(1)

    if args[0] == "--template":
        outPath = args[1] if len(args) > 1 else "licensed_lexicon_template.csv"
        printTemplate(outPath)
        sys.exit(0)

    importCsv(args[0])
