import sqlite3
import sys
from pathlib import Path

projectRoot = Path(__file__).resolve().parents[3]
if str(projectRoot) not in sys.path:
    sys.path.insert(0, str(projectRoot))

try:
    from programs.learning.vocabulary import VOCABULARY as vocabPack
except Exception:
    from programs.learning.seed.vocabulary import VOCABULARY as vocabPack

chipDbPath = projectRoot / "lcars" / "database" / "iso_chip_b1_plus.db"

levelRank = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
}


def allowLevel(level, maxLevel):
    return levelRank.get(level, 99) <= levelRank.get(maxLevel, 99)


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
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            english TEXT NOT NULL,
            ukrainian TEXT NOT NULL,
            category TEXT,
            level TEXT,
            context TEXT,
            example_usage TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS grammar_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            rule_text TEXT NOT NULL,
            examples TEXT,
            level TEXT,
            category TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS mini_texts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            english_text TEXT,
            translated_text TEXT,
            level TEXT
        )
        """
    )
    cur.execute(
        """
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
        """
    )
    conn.commit()


def seedVocabulary(conn, maxLevel):
    cur = conn.cursor()
    inserted = 0
    for en, ua, pos, lvl, ex, cat, diff in vocabPack:
        if not allowLevel(lvl, maxLevel):
            continue
        row = cur.execute(
            "SELECT id FROM vocabulary WHERE english = ? AND level = ?",
            (en, lvl),
        ).fetchone()
        if row:
            continue
        cur.execute(
            """
            INSERT INTO vocabulary
            (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (en, ua, pos, lvl, ex, cat, diff),
        )
        inserted += 1
    conn.commit()
    return inserted


def seedGrammar(conn):
    grammarPack = [
        (
            "Present Perfect vs Past Simple",
            "Use Present Perfect for experience and unfinished time. Use Past Simple for finished time in the past.",
            "I have visited London. | I visited London in 2019.",
            "B1",
            "tenses",
        ),
        (
            "First Conditional",
            "Use if + Present Simple, will + base verb for real future possibility.",
            "If it rains, we will stay home.",
            "B1",
            "conditionals",
        ),
        (
            "Second Conditional",
            "Use if + Past Simple, would + base verb for unreal present or future situations.",
            "If I had more time, I would learn Spanish.",
            "B1",
            "conditionals",
        ),
        (
            "Modals for Advice and Obligation",
            "Use should for advice, must or have to for obligation.",
            "You should rest. | You must wear a helmet.",
            "B1",
            "modals",
        ),
        (
            "Passive Voice Basics",
            "Use be + past participle when focus is on action or result.",
            "The report was finished yesterday.",
            "B1",
            "voice",
        ),
        (
            "Relative Clauses",
            "Use who, which, that to add information about nouns.",
            "The woman who called me is my manager.",
            "B1",
            "clauses",
        ),
        (
            "Gerund and Infinitive",
            "Some verbs take -ing, others take to + verb.",
            "I enjoy reading. | I decided to study.",
            "B1",
            "verb patterns",
        ),
        (
            "Reported Speech Basics",
            "Backshift tense in reported statements when reporting in the past.",
            "She said she was tired.",
            "B1",
            "reported speech",
        ),
    ]

    cur = conn.cursor()
    inserted = 0
    for title, ruleText, examples, level, category in grammarPack:
        row = cur.execute(
            "SELECT id FROM grammar_rules WHERE title = ? AND level = ?",
            (title, level),
        ).fetchone()
        if row:
            continue
        cur.execute(
            """
            INSERT INTO grammar_rules (title, rule_text, examples, level, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (title, ruleText, examples, level, category),
        )
        inserted += 1
    conn.commit()
    return inserted


def seedPhrases(conn):
    phrasePack = [
        ("In my opinion, this is effective.", "На мою думку, це ефективно.", "general", "B1", "discussion", "In my opinion, this is effective for beginners."),
        ("Could you clarify your point?", "Чи могли б ви уточнити вашу думку?", "work", "B1", "meeting", "Could you clarify your point about the deadline?"),
        ("I totally agree with you.", "Я повністю з вами згоден.", "general", "B1", "discussion", "I totally agree with you on this issue."),
        ("I am not sure that is correct.", "Я не впевнений, що це правильно.", "general", "B1", "discussion", "I am not sure that is correct in this context."),
        ("We should focus on priorities.", "Нам слід зосередитися на пріоритетах.", "work", "B1", "planning", "We should focus on priorities this week."),
        ("Can we postpone the meeting?", "Чи можемо перенести зустріч?", "work", "B1", "meeting", "Can we postpone the meeting until Friday?"),
        ("I have already finished this task.", "Я вже завершив це завдання.", "work", "B1", "status", "I have already finished this task today."),
        ("I am working on it right now.", "Я працюю над цим прямо зараз.", "work", "B1", "status", "I am working on it right now, give me ten minutes."),
        ("Could you send me the details?", "Чи можете надіслати мені деталі?", "work", "B1", "email", "Could you send me the details by email?"),
        ("That depends on the situation.", "Це залежить від ситуації.", "general", "B1", "conversation", "That depends on the situation and budget."),
        ("I am trying to improve my English.", "Я намагаюся покращити свою англійську.", "general", "B1", "learning", "I am trying to improve my English every day."),
        ("Could you speak a bit slower?", "Чи можете говорити трохи повільніше?", "general", "B1", "conversation", "Could you speak a bit slower, please?"),
        ("I did not catch the last part.", "Я не розчув останню частину.", "general", "B1", "conversation", "I did not catch the last part of your sentence."),
        ("This option seems more practical.", "Цей варіант здається більш практичним.", "work", "B1", "analysis", "This option seems more practical for our team."),
        ("We need to find a better solution.", "Нам потрібно знайти краще рішення.", "work", "B1", "problem solving", "We need to find a better solution before launch."),
    ]

    cur = conn.cursor()
    inserted = 0
    for en, ua, category, level, context, usage in phrasePack:
        row = cur.execute(
            "SELECT id FROM phrases WHERE english = ? AND level = ?",
            (en, level),
        ).fetchone()
        if row:
            continue
        cur.execute(
            """
            INSERT INTO phrases (english, ukrainian, category, level, context, example_usage)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (en, ua, category, level, context, usage),
        )
        inserted += 1
    conn.commit()
    return inserted


def seedTextsAndTests(conn):
    textPack = [
        (
            "B1",
            "Remote Work Habits",
            "Remote work can increase flexibility, but it also requires good time management. Many people create a daily routine, plan tasks in blocks, and avoid multitasking to stay productive.",
            "Віддалена робота може підвищити гнучкість, але також вимагає гарного тайм-менеджменту. Багато людей створюють щоденний розклад, планують завдання блоками та уникають багатозадачності, щоб залишатися продуктивними.",
        ),
        (
            "B1",
            "Healthy Sleep",
            "Sleep affects concentration, mood, and memory. Experts suggest going to bed at the same time every day and reducing screen use before sleep.",
            "Сон впливає на концентрацію, настрій і пам'ять. Експерти радять лягати спати щодня в один і той самий час і зменшувати використання екранів перед сном.",
        ),
        (
            "B1",
            "Learning by Doing",
            "People often learn faster when they practice in real situations. Short daily practice sessions are usually more effective than rare long sessions.",
            "Люди часто вчаться швидше, коли практикуються в реальних ситуаціях. Короткі щоденні сесії зазвичай ефективніші за рідкісні довгі сесії.",
        ),
        (
            "B1",
            "City Transport",
            "Public transport is cheaper than driving in many cities. However, crowded buses and delays can make commuting stressful during peak hours.",
            "Громадський транспорт у багатьох містах дешевший за поїздки авто. Однак переповнені автобуси та затримки можуть робити дорогу на роботу стресовою в години пік.",
        ),
        (
            "B1",
            "Digital Security",
            "Strong passwords and two-factor authentication reduce the risk of account theft. Users should also update software regularly.",
            "Надійні паролі та двофакторна автентифікація зменшують ризик крадіжки акаунтів. Користувачам також слід регулярно оновлювати програмне забезпечення.",
        ),
    ]

    testPack = [
        ("B1", "Choose the correct sentence:", "She have finished.", "She has finished.", "She finishing.", "She is finish.", "B"),
        ("B1", "If I had more time, I ...", "will study", "study", "would study", "am studying", "C"),
        ("B1", "Pick the correct modal advice:", "You must to rest.", "You should rest.", "You should to rest.", "You should resting.", "B"),
        ("B1", "Passive form of: They repaired the car.", "The car repaired.", "The car was repaired.", "The car was repair.", "The car is repaired yesterday.", "B"),
        ("B1", "Reported speech: He said: I am tired.", "He said he is tired.", "He said he was tired.", "He said I was tired.", "He said tired.", "B"),
        ("B1", "Choose the best connector:", "I was tired, because I went out.", "I was tired although I slept well.", "I was tired so I went to bed early.", "I was tired but I drank coffee and felt better, because.", "C"),
        ("B1", "Present perfect for experience:", "I have been to London.", "I was in London never.", "I am in London before.", "I have went to London.", "A"),
        ("B1", "Correct relative clause:", "The person which called me is my manager.", "The person who called me is my manager.", "The person whose called me is my manager.", "The person where called me is my manager.", "B"),
    ]

    cur = conn.cursor()
    insTexts = 0
    for level, title, enText, uaText in textPack:
        row = cur.execute(
            "SELECT id FROM mini_texts WHERE title = ? AND level = ?",
            (title, level),
        ).fetchone()
        if row:
            continue
        cur.execute(
            """
            INSERT INTO mini_texts (level, title, english_text, translated_text)
            VALUES (?, ?, ?, ?)
            """,
            (level, title, enText, uaText),
        )
        insTexts += 1

    insTests = 0
    for level, question, a, b, c, d, correct in testPack:
        row = cur.execute(
            "SELECT id FROM tests WHERE question = ? AND level = ?",
            (question, level),
        ).fetchone()
        if row:
            continue
        cur.execute(
            """
            INSERT INTO tests (level, question, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (level, question, a, b, c, d, correct),
        )
        insTests += 1

    conn.commit()
    return insTexts, insTests


def printSummary(conn):
    cur = conn.cursor()
    tables = ["vocabulary", "grammar_rules", "phrases", "mini_texts", "tests"]
    for name in tables:
        total = cur.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
        byLevel = cur.execute(
            f"SELECT level, COUNT(*) FROM {name} GROUP BY level ORDER BY level"
        ).fetchall()
        print(f"{name}: total={total} byLevel={byLevel}")


def upsertTable(srcConn, dstConn, tableName, columns):
    srcCur = srcConn.cursor()
    dstCur = dstConn.cursor()
    colsCsv = ", ".join(columns)
    marks = ", ".join(["?" for _ in columns])
    keyCols = ["english", "level"] if tableName in ["vocabulary", "phrases"] else ["title", "level"] if tableName == "grammar_rules" else ["title", "level"] if tableName == "mini_texts" else ["question", "level"]

    rows = srcCur.execute(f"SELECT {colsCsv} FROM {tableName}").fetchall()
    for row in rows:
        rowMap = dict(zip(columns, row))
        whereSql = " AND ".join([f"{k} = ?" for k in keyCols])
        whereVals = tuple(rowMap[k] for k in keyCols)
        exists = dstCur.execute(
            f"SELECT id FROM {tableName} WHERE {whereSql}",
            whereVals,
        ).fetchone()
        if exists:
            setCols = [c for c in columns if c not in keyCols]
            setSql = ", ".join([f"{c} = ?" for c in setCols])
            setVals = tuple(rowMap[c] for c in setCols)
            dstCur.execute(
                f"UPDATE {tableName} SET {setSql} WHERE id = ?",
                setVals + (exists[0],),
            )
        else:
            dstCur.execute(
                f"INSERT INTO {tableName} ({colsCsv}) VALUES ({marks})",
                row,
            )


def syncChipToMainDbs():
    targetDbPaths = [
        projectRoot / "lcars" / "database" / "english_learning_v2.db",
    ]

    srcConn = sqlite3.connect(str(chipDbPath))
    for targetPath in targetDbPaths:
        targetPath.parent.mkdir(parents=True, exist_ok=True)
        dstConn = sqlite3.connect(str(targetPath))
        ensureSchema(dstConn)

        upsertTable(srcConn, dstConn, "vocabulary", ["english", "ukrainian", "part_of_speech", "level", "example_sentence", "pronunciation", "difficulty", "tags", "category"])
        upsertTable(srcConn, dstConn, "grammar_rules", ["title", "rule_text", "examples", "level", "category"])
        upsertTable(srcConn, dstConn, "phrases", ["english", "ukrainian", "category", "level", "context", "example_usage"])
        upsertTable(srcConn, dstConn, "mini_texts", ["title", "english_text", "translated_text", "level"])
        upsertTable(srcConn, dstConn, "tests", ["question", "option_a", "option_b", "option_c", "option_d", "correct_option", "level"])

        dstConn.commit()
        dstConn.close()
        print(f"syncedTo={targetPath}")

    srcConn.close()


def buildChip(maxLevel="B1"):
    chipDbPath.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(chipDbPath))
    ensureSchema(conn)

    countVocab = seedVocabulary(conn, maxLevel)
    countGrammar = seedGrammar(conn)
    countPhrases = seedPhrases(conn)
    countTexts, countTests = seedTextsAndTests(conn)

    print(f"inserted vocabulary={countVocab}")
    print(f"inserted grammar={countGrammar}")
    print(f"inserted phrases={countPhrases}")
    print(f"inserted texts={countTexts}")
    print(f"inserted tests={countTests}")
    printSummary(conn)
    conn.close()
    syncChipToMainDbs()


if __name__ == "__main__":
    buildChip("B1")
