
import sqlite3
import json
import random
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, cast

from lcars.base.type import LCARS, Directive

import importlib.util
import importlib

# Опційний `LinguisticChip` з LCARS. Якщо модуль відсутній,
# працюємо через локальну БД.
LinguisticChip = None

# Глобальні прапори для керування поведінкою чіпа та JSON bootstrap (можна налаштувати через API)
EnableFrameworkChipFlag = False
ENABLE_JSON_BOOTSTRAP = False
ISO_CHIP_DB_PATH: Optional[str] = None

def set_enable_framework_chip_flag(value: bool) -> None:
    global EnableFrameworkChipFlag
    EnableFrameworkChipFlag = bool(value)

def set_enable_json_bootstrap(value: bool) -> None:
    global ENABLE_JSON_BOOTSTRAP
    ENABLE_JSON_BOOTSTRAP = bool(value)

def set_iso_chip_db_path(path: Optional[str]) -> None:
    global ISO_CHIP_DB_PATH
    ISO_CHIP_DB_PATH = str(path) if path is not None else None
if EnableFrameworkChipFlag:
    spec = importlib.util.find_spec('lcars.modules.linguistic_matrix')
    if spec is None:
        LinguisticChip = None
    else:
        mod = importlib.import_module('lcars.modules.linguistic_matrix')
        LinguisticChip = getattr(mod, 'LinguisticChip', None)

# Утиліта: додає CamelCase-ключі для UI, зберігаючи оригінальні case для логіки та сумісності з даними.
def CaseKey(key: str) -> str:
    parts = str(key).split('_')
    return ''.join(p.capitalize() for p in parts if p)

def Camelize(obj):
    # Створюємо обидва варіанти ключів для зворотної сумісності.
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = Camelize(v)
            out[CaseKey(k)] = Camelize(v)
        return out
    if isinstance(obj, list):
        return [Camelize(i) for i in obj]
    return obj

# Менеджер бази даних для навчального модуля, з підтримкою ізолінійного чіпа LCARS (якщо доступний) або локального SQLite файлу.
class LearningStore:
    def __init__(self, dbPath: Optional[str] = None, preferFrameworkChip: bool = True, skipSyncIsoChip: bool = False):
        # Основне сховище — локальний SQLite.
        # Дані чіпа синхронізуються з окремого SQLite-файлу (iso chip), якщо він існує.
        self.externalChip = None
        self.preferFrameworkChip = False
        self.dbPath = dbPath
        self.connection = None
        self.skipSyncIsoChip = skipSyncIsoChip
        self.initDatabase()

    def initDatabase(self):
        # Ініціалізація підключення і таблиць.
        # Пріоритет — `LinguisticChip`, інакше локальна БД.
        if self.preferFrameworkChip and LinguisticChip is not None:
            chip = LinguisticChip()
            if getattr(chip, 'ConnectToMatrix', None) and chip.ConnectToMatrix():
                self.externalChip = chip
                self.connection = chip.MatrixConnection
                # Ensure chip schema and optionally bootstrap
                self.EnsureIsoChipSchema(self.connection)
                self.Bootstrapchipfromjsonifempty(self.connection, maxLevel='B2')
                # Ensure learning tables exist (no-op if already present)
                self.CreateTables()
                return

            # При відмові підключення до LinguisticChip переходимо на локальну БД без додаткового логування.
            self.externalChip = None

        # Fallback: локальний SQLite у директорії фреймворку.
        if not self.dbPath:
            projectRoot = Path(__file__).resolve().parents[2]
            self.dbPath = str(projectRoot / "lcars" / "database" / "english_learning_v2.db")

        Path(self.dbPath).parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.dbPath, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.CreateTables()
        # За потреби синхронізуємо локальну БД з даними чіпа.
        if not getattr(self, 'skipSyncIsoChip', False):
            self.SyncIsoChipData(maxLevel='B2')

    def _connection(self) -> sqlite3.Connection:
        if self.connection is None:
            raise RuntimeError('Database connection is not initialized')
        return self.connection

    def ResolveIsoChipDbPath(self) -> Path:
        # Primary source: SQLite isolinear chip DB.
        # Respect explicit override if caller configured an ISO chip DB path
        if ISO_CHIP_DB_PATH:
            return Path(ISO_CHIP_DB_PATH)
        projectRoot = Path(__file__).resolve().parents[2]
        return projectRoot / 'lcars' / 'database' / 'iso_chip_06_english.db'

    def EnsureIsoChipSchema(self, chipConn: sqlite3.Connection):
        cursor = chipConn.cursor()
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS vocabulary (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                english TEXT NOT NULL,\n                ukrainian TEXT NOT NULL,\n                part_of_speech TEXT,\n                level TEXT,\n                example_sentence TEXT,\n                pronunciation TEXT,\n                difficulty INTEGER DEFAULT 1,\n                last_reviewed DATETIME,\n                next_review DATETIME,\n                tags TEXT,\n                category TEXT DEFAULT 'general'\n            )\n        ")
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS phrases (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                english TEXT NOT NULL,\n                ukrainian TEXT NOT NULL,\n                category TEXT,\n                level TEXT,\n                context TEXT,\n                example_usage TEXT\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS grammar_rules (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                title TEXT NOT NULL,\n                rule_text TEXT NOT NULL,\n                examples TEXT,\n                level TEXT,\n                category TEXT\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS mini_texts (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                title TEXT,\n                english_text TEXT,\n                translated_text TEXT,\n                level TEXT\n            )\n        ')
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS tests (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                question TEXT,\n                option_a TEXT,\n                option_b TEXT,\n                option_c TEXT,\n                option_d TEXT,\n                correct_option TEXT,\n                level TEXT\n            )\n        ')
        chipConn.commit()

    def Bootstrapchipfromjsonifempty(self, chipConn: sqlite3.Connection, maxLevel: str):
        if not ENABLE_JSON_BOOTSTRAP:
            return
        cursor = chipConn.cursor()
        hasVocab = cursor.execute("SELECT COUNT(*) FROM vocabulary").fetchone()[0] > 0
        if hasVocab:
            return
        jsonPath = Path(__file__).resolve().parents[2] / "lcars" / "database" / "english_learning_bootstrap.json"
        # Безпечне читання та парсинг JSON з базовою перевіркою структури, щоб уникнути помилок при завантаженні.
        raw = jsonPath.read_text(encoding='utf-8')
        if not raw or not raw.strip():
            return
        first = raw.lstrip()[0]
        if first not in ('{', '['):
            return
        payload = json.loads(raw)

        for item in payload.get('vocabulary', []):
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            cursor.execute(
                'INSERT INTO vocabulary\n                   (english, ukrainian, part_of_speech, level, example_sentence, pronunciation, difficulty, tags, category)\n                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    item.get('english', ''),
                    item.get('ukrainian', ''),
                    item.get('part_of_speech', ''),
                    level,
                    item.get('example_sentence', ''),
                    item.get('pronunciation', ''),
                    int(item.get('difficulty', 1) or 1),
                    item.get('tags', ''),
                    item.get('category', 'general'),
                )
            )

        for item in payload.get('phrases', []):
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            cursor.execute(
                'INSERT INTO phrases\n                   (english, ukrainian, category, level, context, example_usage)\n                   VALUES (?, ?, ?, ?, ?, ?)',
                (
                    item.get('english', ''),
                    item.get('ukrainian', ''),
                    item.get('category', 'general'),
                    level,
                    item.get('context', ''),
                    item.get('example_usage', ''),
                )
            )

        for item in payload.get('grammar_rules', []):
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            cursor.execute(
                'INSERT INTO grammar_rules\n                   (title, rule_text, examples, level, category)\n                   VALUES (?, ?, ?, ?, ?)',
                (
                    item.get('title', ''),
                    item.get('rule_text', ''),
                    item.get('examples', ''),
                    level,
                    item.get('category', 'general'),
                )
            )

        for item in payload.get('mini_texts', []):
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            cursor.execute(
                'INSERT INTO mini_texts (title, english_text, translated_text, level)\n                   VALUES (?, ?, ?, ?)',
                (
                    item.get('title', ''),
                    item.get('english_text', ''),
                    item.get('translated_text', ''),
                    level,
                )
            )

        for item in payload.get('tests', []):
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            cursor.execute(
                'INSERT INTO tests\n                   (question, option_a, option_b, option_c, option_d, correct_option, level)\n                   VALUES (?, ?, ?, ?, ?, ?, ?)',
                (
                    item.get('question', ''),
                    item.get('option_a', ''),
                    item.get('option_b', ''),
                    item.get('option_c', ''),
                    item.get('option_d', ''),
                    item.get('correct_option', ''),
                    level,
                )
            )
        chipConn.commit()

    def Levelallowed(self, level: str, maxLevel: str) -> bool:
        order = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4, 'C1': 5, 'C2': 6}
        return order.get(level, 99) <= order.get(maxLevel, 99)

    def SyncIsoChipData(self, maxLevel: str = 'B1'):
        # Sync data from an isolinear chip into the learning DB if present.
        # Current mode: read from chip SQLite file path; if file is absent, skip sync.
        if hasattr(self, 'externalChip') and self.externalChip:
            chipConn = self.externalChip.MatrixConnection
            chipConn.row_factory = sqlite3.Row
            self.EnsureIsoChipSchema(chipConn)
            self.Bootstrapchipfromjsonifempty(chipConn, maxLevel)
            chipCur = chipConn.cursor()
            closeChipAfter = False
        else:
            chipPath = self.ResolveIsoChipDbPath()
            if not chipPath.exists():
                return
            chipConn = sqlite3.connect(str(chipPath))
            chipConn.row_factory = sqlite3.Row
            self.EnsureIsoChipSchema(chipConn)
            self.Bootstrapchipfromjsonifempty(chipConn, maxLevel)
            chipCur = chipConn.cursor()
            closeChipAfter = True

        cursor = self._connection().cursor()

        for row in chipCur.execute("SELECT * FROM vocabulary"):
            item = dict(row)
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            exists = cursor.execute(
                "SELECT id FROM vocabulary WHERE english = ? AND level = ?",
                (item.get('english', ''), level)
            ).fetchone()
            if exists:
                continue
            cursor.execute(
                'INSERT INTO vocabulary\n                   (english, ukrainian, part_of_speech, level, example_sentence, pronunciation, difficulty, tags, category)\n                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (
                    item.get('english', ''),
                    item.get('ukrainian', ''),
                    item.get('part_of_speech', ''),
                    level,
                    item.get('example_sentence', ''),
                    item.get('pronunciation', ''),
                    int(item.get('difficulty', 1) or 1),
                    item.get('tags', ''),
                    item.get('category', 'general'),
                )
            )

        for row in chipCur.execute("SELECT * FROM phrases"):
            item = dict(row)
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            exists = cursor.execute(
                "SELECT id FROM phrases WHERE english = ? AND level = ?",
                (item.get('english', ''), level)
            ).fetchone()
            if exists:
                continue
            cursor.execute(
                'INSERT INTO phrases\n                   (english, ukrainian, category, level, context, example_usage)\n                   VALUES (?, ?, ?, ?, ?, ?)',
                (
                    item.get('english', ''),
                    item.get('ukrainian', ''),
                    item.get('category', 'general'),
                    level,
                    item.get('context', ''),
                    item.get('example_usage', ''),
                )
            )

        for row in chipCur.execute("SELECT * FROM grammar_rules"):
            item = dict(row)
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            exists = cursor.execute(
                "SELECT id FROM grammar_rules WHERE title = ? AND level = ?",
                (item.get('title', ''), level)
            ).fetchone()
            if exists:
                continue
            cursor.execute(
                'INSERT INTO grammar_rules\n                   (title, rule_text, examples, level, category)\n                   VALUES (?, ?, ?, ?, ?)',
                (
                    item.get('title', ''),
                    item.get('rule_text', ''),
                    item.get('examples', ''),
                    level,
                    item.get('category', 'general'),
                )
            )

        for row in chipCur.execute("SELECT * FROM mini_texts"):
            item = dict(row)
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            exists = cursor.execute(
                "SELECT id FROM mini_texts WHERE title = ? AND level = ?",
                (item.get('title', ''), level)
            ).fetchone()
            if exists:
                continue
            cursor.execute(
                'INSERT INTO mini_texts (title, english_text, translated_text, level)\n                   VALUES (?, ?, ?, ?)',
                (
                    item.get('title', ''),
                    item.get('english_text', ''),
                    item.get('translated_text', ''),
                    level,
                )
            )

        for row in chipCur.execute("SELECT * FROM tests"):
            item = dict(row)
            level = item.get('level', 'A1')
            if not self.Levelallowed(level, maxLevel):
                continue
            exists = cursor.execute(
                "SELECT id FROM tests WHERE question = ? AND level = ?",
                (item.get('question', ''), level)
            ).fetchone()
            if exists:
                continue
            cursor.execute(
                'INSERT INTO tests\n                   (question, option_a, option_b, option_c, option_d, correct_option, level)\n                   VALUES (?, ?, ?, ?, ?, ?, ?)',
                (
                    item.get('question', ''),
                    item.get('option_a', ''),
                    item.get('option_b', ''),
                    item.get('option_c', ''),
                    item.get('option_d', ''),
                    item.get('correct_option', ''),
                    level,
                )
            )

        self._connection().commit()
        if closeChipAfter:
            chipConn.close()

    def CreateTables(self):
        # Create necessary tables if they don't exist
        cursor = self._connection().cursor()
        
        # Word lists
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS vocabulary (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                english TEXT NOT NULL,\n                ukrainian TEXT NOT NULL,\n                part_of_speech TEXT,\n                level TEXT,\n                example_sentence TEXT,\n                pronunciation TEXT,\n                difficulty INTEGER DEFAULT 1,\n                last_reviewed DATETIME,\n                next_review DATETIME,\n                tags TEXT,\n                category TEXT DEFAULT 'general'\n            )\n        ")

        # Phrases
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS phrases (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                english TEXT NOT NULL,\n                ukrainian TEXT NOT NULL,\n                category TEXT,\n                level TEXT,\n                context TEXT,\n                example_usage TEXT\n            )\n        ')

        # Grammar rules
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS grammar_rules (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                title TEXT NOT NULL,\n                rule_text TEXT NOT NULL,\n                examples TEXT,\n                level TEXT,\n                category TEXT\n            )\n        ')

        # User progress tracking
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS user_progress (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                user_id TEXT DEFAULT 'default',\n                item_type TEXT, -- 'vocabulary', 'phrase', 'grammar'\n                item_id INTEGER,\n                times_correct INTEGER DEFAULT 0,\n                times_incorrect INTEGER DEFAULT 0,\n                last_result INTEGER, -- 1 for correct, 0 for incorrect\n                mastery_level INTEGER DEFAULT 0,\n                last_practiced DATETIME\n            )\n        ")

        # Learning sessions
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS learning_sessions (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                user_id TEXT DEFAULT 'default',\n                session_date DATETIME,\n                duration_minutes INTEGER,\n                vocabulary_studied INTEGER,\n                phrases_studied INTEGER,\n                grammar_studied INTEGER,\n                exercises_completed INTEGER,\n                accuracy_score FLOAT,\n                level TEXT\n            )\n        ")

        # Achievements
        cursor.execute("\n            CREATE TABLE IF NOT EXISTS achievements (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                user_id TEXT DEFAULT 'default',\n                achievement_code TEXT UNIQUE,\n                achievement_name TEXT,\n                description TEXT,\n                unlocked_at DATETIME\n            )\n        ")

        # Mini texts
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS mini_texts (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                title TEXT,\n                english_text TEXT,\n                translated_text TEXT,\n                level TEXT\n            )\n        ')

        # Tests
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS tests (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                question TEXT,\n                option_a TEXT,\n                option_b TEXT,\n                option_c TEXT,\n                option_d TEXT,\n                correct_option TEXT,\n                level TEXT\n            )\n        ')

        self._connection().commit()

    def executeQuery(self, query: str, params: tuple = ()) -> List[Dict]:
        # Виконує SELECT і повертає список словників.
        cursor = self._connection().cursor()
        cursor.execute(query, params)
        return [cast(Dict[str, Any], Camelize(dict(row))) for row in cursor.fetchall()]

    def executeSingle(self, query: str, params: tuple = ()) -> Optional[Dict]:
        # Execute a query and return a single result
        results = self.executeQuery(query, params)
        return results[0] if results else None

    def executeUpdate(self, query: str, params: tuple = ()) -> int:
        # Виконує INSERT/UPDATE/DELETE та повертає `lastrowid`.
        cursor = self._connection().cursor()
        cursor.execute(query, params)
        self._connection().commit()
        return int(cursor.lastrowid or 0)

    def getRandomWords(self, level: Optional[str] = None, category: Optional[str] = None, count: int = 10) -> List[Dict]:
        conditions = []
        params = []
        if level:
            conditions.append("level = ?")
            params.append(level)
        if category:
            conditions.append("category = ?")
            params.append(category)
        query = "SELECT * FROM vocabulary"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY RANDOM() LIMIT ?"
        params.append(count)
        return self.executeQuery(query, tuple(params))
        
    def searchWords(self, searchTerm: str, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        q = f"%{searchTerm}%"
        conditions = ["(english LIKE ? OR ukrainian LIKE ?)"]
        params: List[Any] = [q, q]
        if category:
            conditions.append("category = ?")
            params.append(category)
        query = "SELECT * FROM vocabulary WHERE " + " AND ".join(conditions) + " LIMIT ?"
        params.append(limit)
        return self.executeQuery(query, tuple(params))

    def getPhrasesByLevel(self, level: str, limit: int = 50) -> List[Dict]:
        return self.executeQuery("SELECT * FROM phrases WHERE level = ? LIMIT ?", (level, limit))

    def getGrammarRulesByLevel(self, level: Optional[str] = None) -> List[Dict]:
        if level:
            return self.executeQuery("SELECT * FROM grammar_rules WHERE level = ?", (level,))
        return self.executeQuery("SELECT * FROM grammar_rules")

    def getMiniText(self, level: str) -> Optional[Dict]:
        query = "SELECT * FROM mini_texts WHERE level = ? ORDER BY RANDOM() LIMIT 1"
        return self.executeSingle(query, (level,))

    def getTestQuestions(self, level: str, count: int = 5) -> List[Dict]:
        query = "SELECT * FROM tests WHERE level = ? ORDER BY RANDOM() LIMIT ?"
        return self.executeQuery(query, (level, count))

    def updateWordProgress(self, userId: str, wordId: int, correct: bool):
        lastResult = 1 if correct else 0
        incCorrect = 1 if correct else 0
        incIncorrect = 0 if correct else 1
        
        # Check if record exists
        existing = self.executeSingle(
            "SELECT id, times_correct, times_incorrect FROM user_progress WHERE user_id = ? AND item_id = ? AND item_type = 'vocabulary'",
            (userId, wordId)
        )
        
        if existing:
            prevCorrect = int(existing.get('times_correct', 0) or 0)
            prevIncorrect = int(existing.get('times_incorrect', 0) or 0)
            newCorrect = prevCorrect + incCorrect
            newIncorrect = prevIncorrect + incIncorrect
            # Mastery grows with net successful answers and is clamped to 0..5.
            masteryLevel = max(0, min(5, newCorrect - newIncorrect))
            self.executeUpdate(
                "UPDATE user_progress SET \n                   times_correct = times_correct + ?, \n                   times_incorrect = times_incorrect + ?, \n                   mastery_level = ?, \n                   last_result = ?, \n                   last_practiced = DATETIME('now')\n                   WHERE id = ?",
                (incCorrect, incIncorrect, masteryLevel, lastResult, existing['id'])
            )
        else:
            masteryLevel = 1 if correct else 0
            self.executeUpdate(
                "INSERT INTO user_progress (user_id, item_type, item_id, times_correct, times_incorrect, mastery_level, last_result, last_practiced)\n                   VALUES (?, 'vocabulary', ?, ?, ?, ?, ?, DATETIME('now'))",
                (userId, wordId, incCorrect, incIncorrect, masteryLevel, lastResult)
            )

    def getProgressSummary(self, userId: str = 'default') -> Dict:
        # Vocabulary summary
        vocabStats = self.executeSingle("\n            SELECT \n                COUNT(*) as total_practiced,\n                SUM(times_correct) as total_correct,\n                SUM(times_incorrect) as total_incorrect,\n                CAST(SUM(times_correct) AS FLOAT) / (SUM(times_correct) + SUM(times_incorrect)) as accuracy \n            FROM user_progress \n            WHERE user_id = ? AND item_type = 'vocabulary'\n        ", (userId,))
        
        totalVocab = self.executeSingle("SELECT COUNT(*) as count FROM vocabulary")
        learnedVocab = self.executeSingle(
            "SELECT COUNT(*) as count FROM user_progress WHERE user_id = ? AND item_type = 'vocabulary' AND mastery_level >= 3",
            (userId,)
        )
        
        return {
            'vocabulary': {
                'total_practiced': vocabStats['total_practiced'] if vocabStats else 0,
                'total_vocabulary': totalVocab['count'] if totalVocab else 0,
                'learned_vocabulary': learnedVocab['count'] if learnedVocab else 0,
                'vocabulary_accuracy': vocabStats['accuracy'] if vocabStats and vocabStats['accuracy'] else 0.0
            }
        }

    def getStatistics(self) -> Dict:
        # Get database global statistics
        stats = {'total_words': 0, 'by_level': {}}
        res = self.executeSingle("SELECT COUNT(*) as count FROM vocabulary")
        if res:
            stats['total_words'] = res['count']
        
        levelsRes = self.executeQuery("SELECT level, COUNT(*) as count FROM vocabulary GROUP BY level")
        for r in levelsRes:
            stats['by_level'][r['level']] = r['count']
        return stats

    def close(self):
        if self.connection:
            self.connection.close()

# Backwards compatibility alias: preserve `DatabaseManager` symbol for imports
# Backwards compatibility aliases (Titanium zero-underscore style preferred)
LearningDatabaseManager = LearningStore
DatabaseManager = LearningStore

# --- LEARNING MODULE MANAGER ---

class LearningModuleManager:
    # Manages different learning modules and exercises
    
    def __init__(self, dbManager: DatabaseManager):
        self.db = dbManager
        self.currentExercise = None
        self.exerciseHistory = []
        self.currentLevel = 'A1'
    
    def generateVocabularyExercise(self, level: str = 'A1', exerciseType: str = 'translation') -> Dict:
        if exerciseType == 'multiple_choice':
            return self.GenerateMultipleChoiceExercise(level)
        elif exerciseType == 'spelling':
            return self.GenerateSpellingExercise(level)
        else:
            return self.GenerateTranslationExercise(level)

    def setCurrentLevel(self, level: str):
        self.currentLevel = level

    def selectExerciseType(self) -> str:
        exerciseTypes = [
            'vocabulary_translation',
            'vocabulary_multiple_choice',
            'vocabulary_spelling',
            'phrase_translation',
            'grammar_fill_blank',
        ]
        weights = [30, 25, 15, 20, 10]
        return random.choices(exerciseTypes, weights=weights)[0]

    def generateExercise(self, exerciseType: Optional[str] = None) -> Dict:
        kind = exerciseType or self.selectExerciseType()

        if kind == 'vocabulary_multiple_choice':
            return self.generateVocabularyExercise(self.currentLevel, 'multiple_choice')
        if kind == 'vocabulary_spelling':
            return self.generateVocabularyExercise(self.currentLevel, 'spelling')
        if kind == 'phrase_translation':
            return self.generatePhraseExercise(self.currentLevel)
        if kind == 'grammar_fill_blank':
            return self.generateGrammarExercise(self.currentLevel)

        return self.generateVocabularyExercise(self.currentLevel, 'translation')

    def getNextExercise(self, exerciseTypes: Optional[List[str]] = None) -> Dict:
        pool = exerciseTypes or [
            'vocabulary_translation',
            'vocabulary_multiple_choice',
            'phrase_translation',
            'grammar_fill_blank',
        ]
        return self.generateExercise(random.choice(pool))

    def GenerateTranslationExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=1)
        if not words: return {}
        word = words[0]
        exercise = {
            'type': 'translation',
            'direction': 'en_to_ua',
            'question': f"Translate to Ukrainian: {word['english']}",
            'correct_answer': word['ukrainian'],
            'word_data': word,
            'hints': [f"Part: {word.get('part_of_speech')}", f"Ex: {word.get('example_sentence')}"],
            'difficulty': word.get('difficulty', 1)
        }
        self.currentExercise = exercise
        return exercise

    def GenerateMultipleChoiceExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=5)
        if len(words) < 4:
            return {}

        correctWord = random.choice(words)
        # Robust access: support both snake_case and CamelCase keys
        correct_uk = correctWord.get('ukrainian', correctWord.get('Ukrainian', ''))
        options = [correct_uk]
        others = [w.get('ukrainian', w.get('Ukrainian', '')) for w in words if w.get('id', w.get('Id')) != correctWord.get('id', correctWord.get('Id'))][:3]
        options.extend(others)
        random.shuffle(options)
        exercise = {
            'type': 'multiple_choice',
            'question': f"Ukrainian translation of: {correctWord.get('english', correctWord.get('English', ''))}?",
            'correct_answer': correct_uk,
            'options': options,
            'correct_index': options.index(correct_uk) if correct_uk in options else 0,
            'word_data': correctWord,
            'hints': [f"Part: {correctWord.get('part_of_speech', correctWord.get('PartOfSpeech', ''))}"],
            'difficulty': correctWord.get('difficulty', 1)
        }
        self.currentExercise = exercise
        return exercise

    def GenerateSpellingExercise(self, level: str) -> Dict:
        words = self.db.getRandomWords(level, count=1)
        if not words: return {}
        word = words[0]
        en = word['english'].lower()
        scrambled = list(en)
        random.shuffle(scrambled)
        exercise = {
            'type': 'spelling',
            'question': f"Unscramble: {''.join(scrambled).upper()}",
            'correct_answer': word['english'],
            'hint': f"Meaning: {word['ukrainian']}",
            'word_data': word,
            'difficulty': word.get('difficulty', 1)
        }
        self.currentExercise = exercise
        return exercise

    def generatePhraseExercise(self, level: str = 'A1') -> Dict:
        phrases = self.db.getPhrasesByLevel(level, limit=1)
        if not phrases:
            return {}
        phrase = phrases[0]
        exercise = {
            'type': 'phrase_translation',
            'question': f"Translate this phrase: {phrase.get('english', phrase.get('English', ''))}",
            'correct_answer': phrase.get('ukrainian', phrase.get('Ukrainian', '')),
            'phrase_data': phrase,
            'difficulty': 1,
        }
        self.currentExercise = exercise
        return exercise

    def generateGrammarExercise(self, level: str = 'A1') -> Dict:
        rules = self.db.getGrammarRulesByLevel(level)
        if not rules:
            return {}
        rule = random.choice(rules)
        exercise = {
            'type': 'grammar_review',
            'question': f"Study grammar rule: {rule.get('title', rule.get('Title', ''))}",
            'correct_answer': 'studied',
            'rule_data': rule,
            'difficulty': 1,
        }
        self.currentExercise = exercise
        return exercise

    def checkAnswer(self, userAnswer: str) -> Dict:
        if not self.currentExercise:
            return {'correct': False, 'message': 'No active exercise'}
        correctAnswer = str(self.currentExercise.get('correct_answer', '')).strip().lower()
        isCorrect = userAnswer.strip().lower() == correctAnswer

        if 'word_data' in self.currentExercise:
            wd = self.currentExercise['word_data']
            wordId = wd.get('Id', wd.get('id'))
            if wordId is not None:
                self.db.updateWordProgress('default', wordId, isCorrect)

        self.exerciseHistory.append({'exercise': self.currentExercise, 'correct': isCorrect})
        return {
            'correct': isCorrect,
            'message': 'Correct!' if isCorrect else f"Incorrect. Correct: {self.currentExercise.get('correct_answer', '')}",
            'exercise_type': self.currentExercise.get('type')
        }


def SyncIsoChipIntoLearningDb(maxLevel: str = 'B2', dbPath: Optional[str] = None) -> Dict[str, Any]:
    # Unified entry point for manual ISO-chip import; kept in logic module on purpose.
    manager = LearningStore(dbPath=dbPath, skipSyncIsoChip=True)
    manager.SyncIsoChipData(maxLevel=maxLevel)
    stats = manager.getStatistics()
    chipPath = manager.ResolveIsoChipDbPath()
    result: Dict[str, Any] = {
        'chip_path': str(chipPath),
        'chip_exists': chipPath.exists(),
        'total_words': stats.get('total_words', 0),
        'by_level': stats.get('by_level', {}),
    }
    manager.close()
    return result


if __name__ == '__main__':
    summary = SyncIsoChipIntoLearningDb(maxLevel='B2')
    print('ISO-chip sync complete.')
    print(f"Source chip DB: {summary['chip_path']}")
    print(f"Chip DB exists: {summary['chip_exists']}")
    print(f"Total vocabulary in DB: {summary['total_words']}")
    print(f"By level: {summary['by_level']}")
