"""
Minimal DB initializer for the learning module.
Creates the canonical database at `lcars/database/english_learning_v2.db` and
ensures required tables exist. Safe to run multiple times.
"""

import sqlite3
from pathlib import Path
from typing import Optional


def find_project_root() -> Path:
    p = Path(__file__).resolve()
    # Walk up parents until we find a folder that contains `lcars`
    for parent in p.parents:
        if (parent / 'lcars').exists():
            return parent
    # Fallback to three levels up (expected layout: programs/learning/seed)
    return p.parents[3]


PROJECT_ROOT = find_project_root()
DB_PATH = PROJECT_ROOT / 'lcars' / 'database' / 'english_learning_v2.db'


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    c = conn.cursor()

    # vocabulary
    c.execute("""
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
    """)

    # phrases
    c.execute("""
    CREATE TABLE IF NOT EXISTS phrases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        english TEXT NOT NULL,
        ukrainian TEXT NOT NULL,
        category TEXT,
        level TEXT,
        context TEXT,
        example_usage TEXT
    )
    """)

    # grammar rules
    c.execute("""
    CREATE TABLE IF NOT EXISTS grammar_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        rule_text TEXT NOT NULL,
        examples TEXT,
        level TEXT,
        category TEXT
    )
    """)

    # mini_texts
    c.execute("""
    CREATE TABLE IF NOT EXISTS mini_texts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        english_text TEXT,
        translated_text TEXT,
        level TEXT
    )
    """)

    # tests
    c.execute("""
    CREATE TABLE IF NOT EXISTS tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_option TEXT,
        level TEXT
    )
    """)

    # user progress
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'default',
        item_type TEXT,
        item_id INTEGER,
        times_correct INTEGER DEFAULT 0,
        times_incorrect INTEGER DEFAULT 0,
        last_result INTEGER,
        mastery_level INTEGER DEFAULT 0,
        last_practiced DATETIME
    )
    """)

    # learning sessions
    c.execute("""
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'default',
        session_date DATETIME,
        duration_minutes INTEGER,
        vocabulary_studied INTEGER,
        phrases_studied INTEGER,
        grammar_studied INTEGER,
        exercises_completed INTEGER,
        accuracy_score FLOAT,
        level TEXT
    )
    """)

    # achievements
    c.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT DEFAULT 'default',
        achievement_code TEXT UNIQUE,
        achievement_name TEXT,
        description TEXT,
        unlocked_at DATETIME
    )
    """)

    conn.commit()
    return conn


if __name__ == '__main__':
    conn = init_db()
    conn.close()
    print(f'Initialized DB: {DB_PATH}')

