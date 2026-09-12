import sqlite3
import sys
from pathlib import Path

PROJECTRoot = Path(__file__).resolve().parents[3]
if str(PROJECTRoot) not in sys.path:
    sys.path.insert(0, str(PROJECTRoot))

try:
    from programs.learning.vocabulary import VOCABULARY as FULLVocab
except Exception:
    try:
        from programs.learning.seed.vocabulary import VOCABULARY as FULLVocab
    except Exception:
        FULLVocab = []

CHIPDb = PROJECTRoot / 'lcars' / 'database' / 'iso_chip_06_english.db'

LEVELOrder = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}


def levelAllowed(level: str, maxLevel: str = 'B2') -> bool:
    return LEVELOrder.get(level, 99) <= LEVELOrder.get(maxLevel, 99)


def ensureSchema(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("\n        CREATE TABLE IF NOT EXISTS vocabulary (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            english TEXT NOT NULL,\n            ukrainian TEXT NOT NULL,\n            part_of_speech TEXT,\n            level TEXT,\n            example_sentence TEXT,\n            pronunciation TEXT,\n            difficulty INTEGER DEFAULT 1,\n            last_reviewed DATETIME,\n            next_review DATETIME,\n            tags TEXT,\n            category TEXT DEFAULT 'general'\n        )\n    ")
    cur.execute('\n        CREATE TABLE IF NOT EXISTS phrases (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            english TEXT NOT NULL,\n            ukrainian TEXT NOT NULL,\n            category TEXT,\n            level TEXT,\n            context TEXT,\n            example_usage TEXT\n        )\n    ')
    cur.execute('\n        CREATE TABLE IF NOT EXISTS grammar_rules (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            title TEXT NOT NULL,\n            rule_text TEXT NOT NULL,\n            examples TEXT,\n            level TEXT,\n            category TEXT\n        )\n    ')
    cur.execute('\n        CREATE TABLE IF NOT EXISTS mini_texts (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            title TEXT,\n            english_text TEXT,\n            translated_text TEXT,\n            level TEXT\n        )\n    ')
    cur.execute('\n        CREATE TABLE IF NOT EXISTS tests (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            question TEXT,\n            option_a TEXT,\n            option_b TEXT,\n            option_c TEXT,\n            option_d TEXT,\n            correct_option TEXT,\n            level TEXT\n        )\n    ')
    conn.commit()


def seedVocabulary(conn: sqlite3.Connection, maxLevel: str = 'B2') -> int:
    cur = conn.cursor()
    inserted = 0
    for en, ua, pos, lvl, ex, cat, diff in FULLVocab:
        if not levelAllowed(lvl, maxLevel):
            continue
        exists = cur.execute(
            'SELECT id FROM vocabulary WHERE english = ? AND level = ?',
            (en, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            'INSERT INTO vocabulary\n               (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)\n               VALUES (?, ?, ?, ?, ?, ?, ?)',
            (en, ua, pos, lvl, ex, cat, diff),
        )
        inserted += 1
    conn.commit()
    return inserted


def seedGrammar(conn: sqlite3.Connection, maxLevel: str = 'B2') -> int:
    # Grammar is managed as DB source-of-truth; no static file seeding here.
    return 0


def seedPhrases(conn: sqlite3.Connection) -> int:
    phrasePack = [
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
    for en, ua, cat, lvl, ctx, usage in phrasePack:
        exists = cur.execute(
            'SELECT id FROM phrases WHERE english = ? AND level = ?',
            (en, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            'INSERT INTO phrases (english, ukrainian, category, level, context, example_usage)\n               VALUES (?, ?, ?, ?, ?, ?)',
            (en, ua, cat, lvl, ctx, usage),
        )
        inserted += 1
    conn.commit()
    return inserted


def seedTextsAndTests(conn: sqlite3.Connection) -> tuple[int, int]:
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
    insTexts = 0
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
        insTexts += 1

    insTests = 0
    for lvl, q, a, b, c, d, ok in tests:
        exists = cur.execute(
            'SELECT id FROM tests WHERE question = ? AND level = ?',
            (q, lvl),
        ).fetchone()
        if exists:
            continue
        cur.execute(
            'INSERT INTO tests (question, option_a, option_b, option_c, option_d, correct_option, level)\n               VALUES (?, ?, ?, ?, ?, ?, ?)',
            (q, a, b, c, d, ok, lvl),
        )
        insTests += 1

    conn.commit()
    return insTexts, insTests


def printSummary(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table in ['vocabulary', 'phrases', 'grammar_rules', 'mini_texts', 'tests']:
        total = cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        byLevel = cur.execute(
            f"SELECT level, COUNT(*) FROM {table} GROUP BY level ORDER BY level"
        ).fetchall()
        print(f'{table}: total={total}, by_level={by_level}')


def main():
    CHIPDb.parent.mkdir(parents=True, existOk=True)
    conn = sqlite3.connect(str(CHIPDb))
    ensureSchema(conn)

    iv = seedVocabulary(conn, 'B2')
    ig = seedGrammar(conn, 'B2')
    ip = seedPhrases(conn)
    it, iq = seedTextsAndTests(conn)

    print(f'inserted vocabulary={iv}, grammar={ig}, phrases={ip}, texts={it}, tests={iq}')
    printSummary(conn)
    conn.close()


if __name__ == '__main__':
    main()
