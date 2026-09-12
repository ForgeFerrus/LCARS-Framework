import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from programs.learning.seed_vocab_full import VOCABULARY as FULL_VOCAB
from programs.learning.grammar_data import GRAMMAR_RULES

CHIP_DB = PROJECT_ROOT / 'lcars' / 'database' / 'iso_chip_06_english.db'

LEVEL_ORDER = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}


def level_allowed(level: str, max_level: str = 'B2') -> bool:
    return LEVEL_ORDER.get(level, 99) <= LEVEL_ORDER.get(max_level, 99)


def ensure_schema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute('''
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
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            ukrainian TEXT NOT NULL,
            category TEXT,
            level TEXT,
            context TEXT,
            example_usage TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS grammar_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            rule_text TEXT NOT NULL,
            examples TEXT,
            level TEXT,
            category TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS mini_texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            english_text TEXT,
            translated_text TEXT,
            level TEXT
        )
    ''')
    cur.execute('''
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
    ''')
    conn.commit()


def seed_vocabulary(conn: sqlite3.Connection, max_level: str = 'B2') -> int:
    cur = conn.cursor()
    inserted = 0
    for en, ua, pos, lvl, ex, cat, diff in FULL_VOCAB:
        if not level_allowed(lvl, max_level):
            continue
        exists = cur.execute(
            'SELECT id FROM vocabulary WHERE english = ? AND level = ?',
            (en, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            '''INSERT INTO vocabulary
               (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (en, ua, pos, lvl, ex, cat, diff),
        )
        inserted += 1
    conn.commit()
    return inserted


def seed_grammar(conn: sqlite3.Connection, max_level: str = 'B2') -> int:
    cur = conn.cursor()
    inserted = 0
    for rule in GRAMMAR_RULES:
        lvl = rule.get('level', 'A1')
        if not level_allowed(lvl, max_level):
            continue
        title = rule.get('title', '').strip()
        exists = cur.execute(
            'SELECT id FROM grammar_rules WHERE title = ? AND level = ?',
            (title, lvl),
        ).fetchone()
        if exists:
            continue
        examples = ' | '.join([f"{en} || {ua}" for en, ua in rule.get('examples', [])])
        cur.execute(
            '''INSERT INTO grammar_rules (title, rule_text, examples, level, category)
               VALUES (?, ?, ?, ?, ?)''',
            (title, rule.get('rule', ''), examples, lvl, 'grammar'),
        )
        inserted += 1
    conn.commit()
    return inserted


def seed_phrases(conn: sqlite3.Connection) -> int:
    phrase_pack = [
        ('How are you?', 'Як справи?', 'general', 'A1', 'greeting', 'How are you today?'),
        ('Can you help me?', 'Можете мені допомогти?', 'general', 'A1', 'request', 'Can you help me with this?'),
        ('I do not understand.', 'Я не розумію.', 'general', 'A1', 'conversation', 'Sorry, I do not understand.'),
        ('Could you repeat that, please?', 'Не могли б ви повторити, будь ласка?', 'general', 'A2', 'conversation', 'Could you repeat that, please?'),
        ('I would like to book a room.', 'Я хотів би забронювати номер.', 'travel', 'A2', 'hotel', 'I would like to book a room for two nights.'),
        ('Where is the nearest station?', 'Де найближча станція?', 'travel', 'A2', 'directions', 'Where is the nearest station from here?'),
        ('In my opinion, this is the best option.', 'На мою думку, це найкращий варіант.', 'general', 'B1', 'discussion', 'In my opinion, this is the best option.'),
        ('We need a practical solution.', 'Нам потрібне практичне рішення.', 'work', 'B1', 'meeting', 'We need a practical solution before Friday.'),
        ('I have been working on this since Monday.', 'Я працюю над цим з понеділка.', 'work', 'B1', 'status update', 'I have been working on this since Monday.'),
        ('From a broader perspective, the results are promising.', 'З ширшої перспективи результати обнадійливі.', 'general', 'B2', 'analysis', 'From a broader perspective, the results are promising.'),
        ('The proposal requires further clarification.', 'Пропозиція потребує додаткового уточнення.', 'work', 'B2', 'meeting', 'The proposal requires further clarification.'),
        ('We should mitigate the risks before deployment.', 'Нам слід зменшити ризики перед впровадженням.', 'technology', 'B2', 'planning', 'We should mitigate the risks before deployment.'),
    ]
    cur = conn.cursor()
    inserted = 0
    for en, ua, cat, lvl, ctx, usage in phrase_pack:
        exists = cur.execute(
            'SELECT id FROM phrases WHERE english = ? AND level = ?',
            (en, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            '''INSERT INTO phrases (english, ukrainian, category, level, context, example_usage)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (en, ua, cat, lvl, ctx, usage),
        )
        inserted += 1
    conn.commit()
    return inserted


def seed_texts_and_tests(conn: sqlite3.Connection) -> tuple[int, int]:
    texts = [
        ('A1', 'A Morning Routine', 'I wake up at seven, have breakfast, and go to work.', 'Я прокидаюся о сьомій, снідаю та йду на роботу.'),
        ('A2', 'A Weekend Trip', 'Last weekend we traveled to Lviv and visited museums.', 'Минулого вихідного ми подорожували до Львова та відвідали музеї.'),
        ('B1', 'The History of Tea', 'Tea is one of the most popular drinks in the world.', 'Чай — один із найпопулярніших напоїв у світі.'),
        ('B2', 'Artificial Intelligence in Modern Society', 'AI is transforming work, education, and healthcare globally.', 'ШІ трансформує роботу, освіту та медицину в усьому світі.'),
    ]
    tests = [
        ('A1', 'Choose the correct sentence:', 'She go to school every day.', 'She goes to school every day.', 'She going to school every day.', 'She gone to school every day.', 'B'),
        ('A2', "What is the past form of 'go'?", 'goed', 'gone', 'went', 'goes', 'C'),
        ('B1', 'Which sentence uses Present Perfect correctly?', 'I have saw this movie.', 'I have seen this movie.', 'I seen this movie.', 'I has seen this movie.', 'B'),
        ('B2', "What does 'to mitigate' mean?", 'To make less severe', 'To increase', 'To ignore', 'To celebrate', 'A'),
        ('B2', 'Choose the correct conditional sentence:', 'If I had known, I would have gone.', 'If I know, I would go.', 'If I knew, I will go.', 'If I had knew, I would go.', 'A'),
    ]

    cur = conn.cursor()
    ins_texts = 0
    for lvl, title, en, ua in texts:
        exists = cur.execute(
            'SELECT id FROM mini_texts WHERE title = ? AND level = ?',
            (title, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            'INSERT INTO mini_texts (title, english_text, translated_text, level) VALUES (?, ?, ?, ?)',
            (title, en, ua, lvl),
        )
        ins_texts += 1

    ins_tests = 0
    for lvl, q, a, b, c, d, ok in tests:
        exists = cur.execute(
            'SELECT id FROM tests WHERE question = ? AND level = ?',
            (q, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            '''INSERT INTO tests (question, option_a, option_b, option_c, option_d, correct_option, level)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (q, a, b, c, d, ok, lvl),
        )
        ins_tests += 1

    conn.commit()
    return ins_texts, ins_tests


def print_summary(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table in ['vocabulary', 'phrases', 'grammar_rules', 'mini_texts', 'tests']:
        total = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        by_level = cur.execute(
            f"SELECT level, COUNT(*) FROM {table} GROUP BY level ORDER BY level"
        ).fetchall()
        print(f'{table}: total={total}, by_level={by_level}')


def main():
    CHIP_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(CHIP_DB))
    ensure_schema(conn)

    iv = seed_vocabulary(conn, 'B2')
    ig = seed_grammar(conn, 'B2')
    ip = seed_phrases(conn)
    it, iq = seed_texts_and_tests(conn)

    print(f'inserted vocabulary={iv}, grammar={ig}, phrases={ip}, texts={it}, tests={iq}')
    print_summary(conn)
    conn.close()


if __name__ == '__main__':
    main()
