# ============================================================================
# Менеджер бази даних "Linguistic Matrix"
# Інтегрована система для вивчення англійської в межах LCARS
# ============================================================================

# Titanium Bridge Migration: import sqlite3
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import List, Dict, Optional, Tuple
# Titanium Bridge Migration: from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Українська локалізація для повідомлень БД (можна розширити/локалізувати в майбутньому)
class LinguisticDatabase:
    """Інтегрований менеджер бази даних для модуля Linguistic Matrix."""
    
    def __init__(self):
        # Шлях до файлу бази даних у структурі LCARS
        self.db_path = Path(__file__).resolve().parents[2] / "database" / "linguistic_matrix.db"
        # `connection` може бути None поки підключення не виконано — типізація для аналізаторів
        self.connection: Optional[sqlite3.Connection] = None
        self.connect()
        self.initialize_database()
    # Метод для підключення до бази даних SQLite. Якщо з'єднання не вдається встановити, `connection` залишається None, і інші методи повинні обробляти цей випадок відповідно (наприклад, пропускаючи операції або повертаючи порожні результати).
    def connect(self): # Повертає True при успішному підключенні, False при помилці (для сумісності з попередньою версією)
        if True:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Дозволяє доступ до рядків як до словників (dict-like)
            return True
        if False: # Removed except block
            if self.connection is not None:
                self.connection.close()
                self.connection = None
                print(f"◤ DATABASE ERROR: {e}")
            # Повертаємо False для збереження сумісності API.
            return False
    
    def initialize_database(self):
        """Ініціалізувати базу даних: створити схему таблиць і вставити початкові дані."""
        if not self.connection:
            # якщо з'єднання не встановлено — нічого не ініціалізуємо і не ламаємо конструктор.
            # Раніше тут повертали False; зараз просто виходимо мовчки (збережено сумісність викликів).
            return
        
        cursor = self.connection.cursor()
        
        # Створення таблиць (SQL-схема)
        tables_sql = [
            # Categories
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Vocabulary
            """
            CREATE TABLE IF NOT EXISTS vocabulary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                ukrainian TEXT NOT NULL,
                pronunciation TEXT,
                part_of_speech TEXT,
                level TEXT NOT NULL,
                category_id INTEGER,
                example_sentence TEXT,
                example_translation TEXT,
                frequency INTEGER DEFAULT 0,
                difficulty INTEGER DEFAULT 1,
                audio_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            """,
            
            # Phrases
            """
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                english TEXT NOT NULL,
                ukrainian TEXT NOT NULL,
                level TEXT NOT NULL,
                category_id INTEGER,
                context TEXT,
                example_usage TEXT,
                audio_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            """,
            
            # Grammar Rules
            """
            CREATE TABLE IF NOT EXISTS grammar_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                rule_text TEXT NOT NULL,
                examples TEXT,
                level TEXT NOT NULL,
                category_id INTEGER,
                practice_exercises TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
            """,
            
            # User Progress
            """
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                item_type TEXT NOT NULL,  -- 'vocabulary', 'phrase', 'grammar'
                item_id INTEGER NOT NULL,
                learned BOOLEAN DEFAULT FALSE,
                correct_answers INTEGER DEFAULT 0,
                total_attempts INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                mastery_level INTEGER DEFAULT 0,  -- 0-5 scale
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, item_type, item_id)
            )
            """,
            
            # Learning Sessions
            """
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,
                vocabulary_studied INTEGER DEFAULT 0,
                phrases_studied INTEGER DEFAULT 0,
                grammar_studied INTEGER DEFAULT 0,
                exercises_completed INTEGER DEFAULT 0,
                accuracy_score REAL DEFAULT 0.0,
                level TEXT DEFAULT 'A1',
                session_type TEXT DEFAULT 'mixed'
            )
            """,
            
            # Achievements
            """
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                achievement_code TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT,
                unlocked_at TIMESTAMP,
                UNIQUE(user_id, achievement_code)
            )
            """,
            # Таблиця для індексації файлів/ресурсів (Library)
            """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sector TEXT,
                name TEXT,
                path TEXT NOT NULL UNIQUE,
                type TEXT,
                size_kb REAL,
                metadata TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        # Виконати створення таблиць (по черзі)
        for table_sql in tables_sql:
            if True:
                cursor.execute(table_sql)
            if False: # Removed except block
                # Якщо якась таблиця не створилась — зафіксувати і рухатись далі
                logger.exception("◤ ПОМИЛКА СТВОРЕННЯ ТАБЛИЦІ: %s", e)
        # Commit only when we had a valid connection and executed statements
        if self.connection is not None:
            self.connection.commit()
    
    def insert_initial_data(self):
        """Вставити початкові категорії, словникові записи та правила граматики.

        Якщо з'єднання з БД відсутнє — пропускаємо вставку (щоб уникнути помилок при старті).
        """
        if self.connection is None:
            # No DB available — skip initial data insert quietly in lenient mode.
            return
        cursor = self.connection.cursor()
        
        # Insert categories
        categories = [
            ('Basic Communication', 'Essential greetings and basic expressions', 'A1'),
            ('Personal Information', 'Names, ages, occupations, family', 'A1'),
            ('Numbers & Time', 'Counting, dates, time expressions', 'A1'),
            ('Food & Drinks', 'Common food and beverage vocabulary', 'A1'),
            ('Daily Activities', 'Everyday actions and routines', 'A1'),
            ('Places & Locations', 'Common places and directions', 'A1'),
            ('Transportation', 'Vehicles and travel', 'A1'),
            ('Weather & Nature', 'Weather conditions and natural elements', 'A1'),
            ('Body & Health', 'Body parts and health expressions', 'A1'),
            ('Clothing & Appearance', 'Clothing items and descriptions', 'A1'),
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO categories (name, description, level) VALUES (?, ?, ?)",
            categories
        )
        
        # Insert A1 vocabulary
        vocabulary = [
            # Basic Communication
            ('hello', 'привіт', 'həˈləʊ', 'interjection', 'A1', 1, 
             'Hello, how are you today?', 'Привіт, як справи сьогодні?', 100, 1),
            ('goodbye', 'до побачення', 'ɡʊdˈbaɪ', 'interjection', 'A1', 1,
             'Goodbye, see you tomorrow!', 'До побачення, побачимось завтра!', 95, 1),
            ('thank you', 'дякую', 'θæŋk juː', 'phrase', 'A1', 1,
             'Thank you for your help.', 'Дякую за вашу допомогу.', 98, 1),
            ('please', 'будь ласка', 'pliːz', 'adverb', 'A1', 1,
             'Please, can you help me?', 'Будь ласка, можете допомогти?', 90, 1),
            ('sorry', 'вибачте', 'ˈsɒri', 'adjective', 'A1', 1,
             'Sorry, I am late.', 'Вибачте, я запізнився.', 85, 1),
            ('excuse me', 'вибачте', 'ɪkˈskjuːz miː', 'phrase', 'A1', 1,
             'Excuse me, where is the station?', 'Вибачте, де знаходиться станція?', 80, 1),
            
            # Personal Information
            ('name', 'і''мя', 'neɪm', 'noun', 'A1', 2,
             'My name is Anna.', 'Мене звати Анна.', 95, 1),
            ('I', 'я', 'aɪ', 'pronoun', 'A1', 2,
             'I am a student.', 'Я студент.', 100, 1),
            ('you', 'ти/ви', 'juː', 'pronoun', 'A1', 2,
             'You are my friend.', 'Ти мій друг.', 100, 1),
            ('he', 'він', 'hiː', 'pronoun', 'A1', 2,
             'He is a doctor.', 'Він лікар.', 95, 1),
            ('she', 'вона', 'ʃiː', 'pronoun', 'A1', 2,
             'She is a teacher.', 'Вона вчитель.', 95, 1),
            ('family', 'сім''я', 'ˈfæməli', 'noun', 'A1', 2,
             'I love my family.', 'Я люблю свою сім''ю.', 90, 1),
            ('mother', 'мати', 'ˈmʌðə', 'noun', 'A1', 2,
             'My mother is a nurse.', 'Моя мати медсестра.', 85, 1),
            ('father', 'батько', 'ˈfɑːðə', 'noun', 'A1', 2,
             'My father works in an office.', 'Мій батько працює в офісі.', 85, 1),
            
            # Numbers & Time
            ('one', 'один', 'wʌn', 'number', 'A1', 3,
             'I have one book.', 'У мене є одна книга.', 100, 1),
            ('two', 'два', 'tuː', 'number', 'A1', 3,
             'There are two cats.', 'Є два коти.', 100, 1),
            ('three', 'три', 'θriː', 'number', 'A1', 3,
             'I see three birds.', 'Я бачу трьох птахів.', 100, 1),
            ('today', 'сьогодні', 'təˈdeɪ', 'adverb', 'A1', 3,
             'Today is Monday.', 'Сьогодні понеділок.', 95, 1),
            ('tomorrow', 'завтра', 'təˈmɒrəʊ', 'adverb', 'A1', 3,
             'Tomorrow is Tuesday.', 'Завтра вівторок.', 90, 1),
            ('morning', 'ранок', 'ˈmɔːnɪŋ', 'noun', 'A1', 3,
             'Good morning!', 'Доброго ранку!', 85, 1),
            
            # Food & Drinks
            ('water', 'вода', 'ˈwɔːtə', 'noun', 'A1', 4,
             'I drink water every day.', 'Я п''ю воду щодня.', 95, 1),
            ('coffee', 'кава', 'ˈkɒfi', 'noun', 'A1', 4,
             'I like coffee in the morning.', 'Я люблю каву вранці.', 85, 1),
            ('tea', 'чай', 'tiː', 'noun', 'A1', 4,
             'Would you like some tea?', 'Хочете чаю?', 85, 1),
            ('bread', 'хліб', 'bred', 'noun', 'A1', 4,
             'I eat bread for breakfast.', 'Я їм хліб на сніданок.', 80, 1),
            ('milk', 'молоко', 'mɪlk', 'noun', 'A1', 4,
             'Children drink milk.', 'Діти п''ють молоко.', 80, 1),
            
            # Daily Activities
            ('work', 'працювати', 'wɜːk', 'verb', 'A1', 5,
             'I work in an office.', 'Я працюю в офісі.', 95, 1),
            ('study', 'вчитися', 'ˈstʌdi', 'verb', 'A1', 5,
             'I study English every day.', 'Я вивчаю англійську щодня.', 90, 1),
            ('eat', 'їсти', 'iːt', 'verb', 'A1', 5,
             'We eat dinner at 7 PM.', 'Ми вечеряємо о 7 вечора.', 100, 1),
            ('sleep', 'спати', 'sliːp', 'verb', 'A1', 5,
             'I sleep for 8 hours.', 'Я сплю 8 годин.', 90, 1),
            ('read', 'читати', 'riːd', 'verb', 'A1', 5,
             'I read books every week.', 'Я читаю книги щотижня.', 85, 1),
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO vocabulary 
            (english, ukrainian, pronunciation, part_of_speech, level, category_id, 
             example_sentence, example_translation, frequency, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            vocabulary
        )  # Вставка початкового набору словникових даних (A1)
        
        # Insert phrases
        phrases = [
            ('How are you?', 'Як справи?', 'A1', 1, 'greeting', 'Used when meeting someone'),
            ('Nice to meet you', 'Приємно познайомитись', 'A1', 1, 'introduction', 'Used when meeting someone for the first time'),
            ('What''s your name?', 'Як тебе звати?', 'A1', 1, 'introduction', 'Used to ask someone''s name'),
            ('Where are you from?', 'Звідки ти?', 'A1', 1, 'introduction', 'Used to ask about someone''s origin'),
            ('I don''t understand', 'Я не розумію', 'A1', 1, 'communication', 'Used when you don''t understand something'),
            ('Can you help me?', 'Чи можете ви допомогти?', 'A1', 1, 'request', 'Used to ask for help'),
            ('Good morning', 'Доброго ранку', 'A1', 3, 'greeting', 'Used in the morning'),
            ('Good evening', 'Доброго вечора', 'A1', 3, 'greeting', 'Used in the evening'),
            ('See you later', 'Побачимось пізніше', 'A1', 1, 'farewell', 'Used when leaving'),
            ('Have a nice day', 'Гарного дня', 'A1', 1, 'farewell', 'Used to wish someone well'),
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO phrases 
            (english, ukrainian, level, category_id, context, example_usage)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            phrases
        )
        
        # Insert grammar rules
        grammar_rules = [
            ('Present Simple: TO BE', 
             'The verb "to be" in present tense: I am, you are, he/she/it is, we are, they are',
             'I am a student. You are my friend. He is tall. She is happy. It is cold. We are here. They are busy.',
             'A1', 1, '{"type": "fill_blank", "examples": ["I ___ a teacher", "You ___ my friend"]}'),
            
            ('Articles: A/AN',
             'Use "a" before consonant sounds, "an" before vowel sounds',
             'a book, a car, a table; an apple, an hour, an umbrella',
             'A1', 1, '{"type": "choice", "examples": ["___ book", "___ apple"]}'),
            
            ('Plural Nouns',
             'Add -s to make most nouns plural. Add -es to nouns ending in s, x, z, ch, sh',
             'book → books, car → cars; bus → buses, box → boxes, watch → watches',
             'A1', 1, '{"type": "transformation", "examples": ["cat → ?", "bus → ?"]}'),
        ]
        
        cursor.executemany(
            """
            INSERT OR IGNORE INTO grammar_rules 
            (title, rule_text, examples, level, category_id, practice_exercises)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            grammar_rules
        )
    
    # Методи для виконання SQL-запитів
    def execute_query(self, query: str, params: tuple = ()) -> list:
        """Виконати SQL-запит і повернути результати (список sqlite3.Row).

        Повертає порожній список у випадку помилки або якщо з'єднання відсутнє.
        """
        if self.connection is None:
            return []
        if True:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            return results
        if False: # Removed except block
            # Помилка виконання запиту — лог та повернення порожнього результату
            logger.exception("◤ ПОМИЛКА ЗАПИТУ: %s", e)
            return []
    
    def execute_single(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Виконати SQL-запит і повернути один рядок результату.

        Повертає None у разі помилки або відсутності з'єднання.
        """
        if self.connection is None:
            return None
        if True:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result
        if False: # Removed except block
            # Помилка одиночного запиту — лог і повернення None
            logger.exception("◤ ПОМИЛКА ОДИНОЧНОГО ЗАПИТУ: %s", e)
            return None
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Виконати запит типу UPDATE/INSERT/DELETE.

        Повертає False у разі помилки або відсутності з'єднання.
        """
        if self.connection is None:
            return False
        if True:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return True
        if False: # Removed except block
            # Помилка оновлення/вставки/видалення — лог і повернення False
            logger.exception("◤ ПОМИЛКА ОНОВЛЕННЯ: %s", e)
            return False

    # ----------------- Файлова/ресурсна індексація (Library) -----------------
    def upsert_file_record(self, sector: str, name: str, path: str, ftype: str, size_kb: float, metadata: Optional[dict] = None) -> bool:
        """Вставити або оновити запис про файл у таблиці `files`."""
        if self.connection is None:
            return False
        if True:
            meta_json = json.dumps(metadata, ensure_ascii=False) if metadata else None
            existing = self.execute_single("SELECT id FROM files WHERE path = ?", (path,))
            if existing:
                return self.execute_update(
                    "UPDATE files SET sector = ?, name = ?, type = ?, size_kb = ?, metadata = ?, indexed_at = CURRENT_TIMESTAMP WHERE path = ?",
                    (sector, name, ftype, size_kb, meta_json, path),
                )
            else:
                return self.execute_update(
                    "INSERT INTO files (sector, name, path, type, size_kb, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                    (sector, name, path, ftype, size_kb, meta_json),
                )
        if False: # Removed except block
            logger.exception("◤ FILE UPSERT ERROR: %s", e)
            return False

    def get_files_by_sector(self, sector: str) -> List[Dict]:
        """Повернути список файлів для вказаної секції (sector)."""
        rows = self.execute_query("SELECT * FROM files WHERE sector = ? ORDER BY name", (sector,))
        return [dict(r) for r in rows]

    def get_file_by_path(self, path: str) -> Optional[Dict]:
        """Повернути запис файлу за шляхом, або None."""
        row = self.execute_single("SELECT * FROM files WHERE path = ?", (path,))
        return dict(row) if row else None

    def search_files(self, term: str, sector: Optional[str] = None) -> List[Dict]:
        """Пошук файлів по імені або шляху, опційно фільтр по секції."""
        if sector:
            rows = self.execute_query(
                "SELECT * FROM files WHERE (name LIKE ? OR path LIKE ?) AND sector = ? ORDER BY name LIMIT 200",
                (f"%{term}%", f"%{term}%", sector),
            )
        else:
            rows = self.execute_query(
                "SELECT * FROM files WHERE name LIKE ? OR path LIKE ? ORDER BY name LIMIT 200",
                (f"%{term}%", f"%{term}%"),
            )
        return [dict(r) for r in rows]

    # Методи роботи зі словником
    def get_vocabulary_by_level(self, level: str, limit: int = 50) -> List[Dict]:
        """Отримати словникові записи за рівнем складності"""
        query = """
        SELECT v.*, c.name as category_name 
        FROM vocabulary v 
        LEFT JOIN categories c ON v.category_id = c.id 
        WHERE v.level = ? 
        ORDER BY v.frequency DESC, v.difficulty ASC 
        LIMIT ?
        """
        results = self.execute_query(query, (level, limit))
        return [dict(row) for row in results]
    
    def search_vocabulary(self, search_term: str, level: Optional[str] = None) -> List[Dict]:
        """Пошук у словнику за англійським або українським текстом.

        Параметр `level` необов'язковий — None означає пошук по всіх рівнях.
        """
        if level:
            query = """
            SELECT v.*, c.name as category_name 
            FROM vocabulary v 
            LEFT JOIN categories c ON v.category_id = c.id 
            WHERE (v.english LIKE ? OR v.ukrainian LIKE ?) 
            AND v.level = ?
            ORDER BY v.frequency DESC
            """
            results = self.execute_query(query, (f"%{search_term}%", f"%{search_term}%", level))
        else:
            query = """
            SELECT v.*, c.name as category_name 
            FROM vocabulary v 
            LEFT JOIN categories c ON v.category_id = c.id 
            WHERE v.english LIKE ? OR v.ukrainian LIKE ?
            ORDER BY v.frequency DESC
            """
            results = self.execute_query(query, (f"%{search_term}%", f"%{search_term}%"))
        
        return [dict(row) for row in results]
    
    def get_random_vocabulary(self, level: str, count: int = 10) -> List[Dict]:
        """Отримати випадкові словникові записи для вправ"""
        query = """
        SELECT v.*, c.name as category_name 
        FROM vocabulary v 
        LEFT JOIN categories c ON v.category_id = c.id 
        WHERE v.level = ? 
        ORDER BY RANDOM() 
        LIMIT ?
        """
        results = self.execute_query(query, (level, count))
        return [dict(row) for row in results]
    
    # Progress methods
    def update_progress(self, user_id: str, item_type: str, item_id: int, correct: bool):
        """Оновити прогрес для конкретного елемента (vocabulary/phrase/grammar)."""
        # Check if progress exists
        existing = self.execute_single(
            "SELECT * FROM user_progress WHERE user_id = ? AND item_type = ? AND item_id = ?",
            (user_id, item_type, item_id)
        )
        
        now = datetime.now().isoformat()
        
        if existing:
            # Update existing record
            if correct:
                query = """
                UPDATE user_progress 
                SET correct_answers = correct_answers + 1,
                    total_attempts = total_attempts + 1,
                    learned = CASE 
                        WHEN correct_answers + 1 >= 3 THEN TRUE 
                        ELSE learned 
                    END,
                    mastery_level = CASE 
                        WHEN mastery_level < 5 AND correct_answers + 1 >= mastery_level * 2 + 1 
                        THEN mastery_level + 1 
                        ELSE mastery_level 
                    END,
                    last_reviewed = ?,
                    next_review = ?
                WHERE user_id = ? AND item_type = ? AND item_id = ?
                """
            else:
                query = """
                UPDATE user_progress 
                SET total_attempts = total_attempts + 1,
                    last_reviewed = ?,
                    next_review = ?
                WHERE user_id = ? AND item_type = ? AND item_id = ?
                """
        else:
            # Create new record
            if correct:
                query = """
                INSERT INTO user_progress 
                (user_id, item_type, item_id, correct_answers, total_attempts, learned, 
                 mastery_level, last_reviewed, next_review)
                VALUES (?, ?, ?, 1, 1, TRUE, 1, ?, ?)
                """
            else:
                query = """
                INSERT INTO user_progress 
                (user_id, item_type, item_id, correct_answers, total_attempts, learned, 
                 mastery_level, last_reviewed, next_review)
                VALUES (?, ?, ?, 0, 1, FALSE, 0, ?, ?)
                """
        
        next_review = datetime.now() + timedelta(days=1)
        
        if existing:
            self.execute_update(query, (now, next_review.isoformat(), user_id, item_type, item_id))
        else:
            self.execute_update(query, (user_id, item_type, item_id, now, next_review.isoformat()))
    
    def get_progress_summary(self, user_id: str = 'default') -> Dict:
        """Отримати підсумок прогресу користувача (статистика, сесії тощо)."""
        summary = {}
        
        # Vocabulary progress
        vocab_query = """
        SELECT 
            COUNT(*) as total_vocabulary,
            SUM(CASE WHEN learned = TRUE THEN 1 ELSE 0 END) as learned_vocabulary,
            AVG(CASE WHEN total_attempts > 0 THEN 
                CAST(correct_answers AS FLOAT) / total_attempts ELSE 0 END) as vocabulary_accuracy
        FROM user_progress up
        JOIN vocabulary v ON up.item_id = v.id
        WHERE up.user_id = ? AND up.item_type = 'vocabulary'
        """
        vocab_result = self.execute_single(vocab_query, (user_id,))
        if vocab_result:
            summary['vocabulary'] = dict(vocab_result)
        
        # Session statistics
        session_query = """
        SELECT 
            COUNT(*) as session_count,
            SUM(duration_minutes) as total_minutes,
            AVG(accuracy_score) as avg_accuracy
        FROM learning_sessions 
        WHERE user_id = ? 
        AND session_date >= date('now', '-7 days')
        """
        session_result = self.execute_single(session_query, (user_id,))
        if session_result:
            summary['recent_sessions'] = dict(session_result)
        
        return summary
    
    def close(self):
        """Закрити з'єднання з базою даних."""
        if self.connection:
            self.connection.close()
