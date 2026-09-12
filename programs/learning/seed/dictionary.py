# Масовий скрипт наповнення бази даних англо-українського словника.
# Рівні: A1, A2, B1, B2, C1, C2
# Теми: general, family, work, travel, nature, technology, food
import sqlite3
import os
from pathlib import Path

DBPath = str(Path(__file__).resolve().parents[3] / "lcars" / "database" / "english_learning_v2.db")

# Format: (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)
VOCABULARY = [
    # === A1 — GENERAL ===
    ("hello", "привіт", "interjection", "A1", "Hello! How are you?", "general", 1),
    ("goodbye", "до побачення", "interjection", "A1", "Goodbye! See you tomorrow.", "general", 1),
    ("yes", "так", "adverb", "A1", "Yes, I agree.", "general", 1),
    ("no", "ні", "adverb", "A1", "No, thank you.", "general", 1),
    ("please", "будь ласка", "adverb", "A1", "Please, come in.", "general", 1),
    ("thank you", "дякую", "phrase", "A1", "Thank you for your help.", "general", 1),
    ("sorry", "вибачте", "interjection", "A1", "Sorry, I was late.", "general", 1),
    ("good", "добрий", "adjective", "A1", "This is a good book.", "general", 1),
    ("bad", "поганий", "adjective", "A1", "That was a bad idea.", "general", 1),
    ("big", "великий", "adjective", "A1", "That is a big house.", "general", 1),
    ("small", "маленький", "adjective", "A1", "She has a small dog.", "general", 1),
    ("new", "новий", "adjective", "A1", "I bought a new phone.", "general", 1),
    ("old", "старий", "adjective", "A1", "This is an old building.", "general", 1),
    ("man", "чоловік", "noun", "A1", "The man is tall.", "general", 1),
    ("woman", "жінка", "noun", "A1", "The woman is kind.", "general", 1),
    ("house", "будинок", "noun", "A1", "We live in a big house.", "general", 1),
    ("book", "книга", "noun", "A1", "This book is interesting.", "general", 1),
    ("water", "вода", "noun", "A1", "Please give me water.", "general", 1),
    ("day", "день", "noun", "A1", "Have a nice day!", "general", 1),
    ("work", "робота / працювати", "noun/verb", "A1", "I go to work every day.", "general", 1),
    # === A1 — FAMILY ===
    ("mother", "мати", "noun", "A1", "My mother is a doctor.", "family", 1),
    ("father", "батько", "noun", "A1", "My father works in a bank.", "family", 1),
    ("brother", "брат", "noun", "A1", "I have two brothers.", "family", 1),
    ("sister", "сестра", "noun", "A1", "She is my little sister.", "family", 1),
    ("son", "син", "noun", "A1", "He is my son.", "family", 1),
    ("daughter", "донька", "noun", "A1", "She is my daughter.", "family", 1),
    ("husband", "чоловік (чоловік)", "noun", "A1", "My husband is very kind.", "family", 1),
    ("wife", "дружина", "noun", "A1", "His wife is a teacher.", "family", 1),
    ("baby", "немовля", "noun", "A1", "The baby is sleeping.", "family", 1),
    ("child", "дитина", "noun", "A1", "Every child needs love.", "family", 1),
    # === A1 — FOOD ===
    ("bread", "хліб", "noun", "A1", "We eat bread every day.", "food", 1),
    ("milk", "молоко", "noun", "A1", "I drink milk in the morning.", "food", 1),
    ("apple", "яблуко", "noun", "A1", "She eats an apple every day.", "food", 1),
    ("egg", "яйце", "noun", "A1", "I like fried eggs.", "food", 1),
    ("coffee", "кава", "noun", "A1", "I drink coffee in the morning.", "food", 1),
    ("tea", "чай", "noun", "A1", "Would you like some tea?", "food", 1),
    ("meat", "м'ясо", "noun", "A1", "He doesn't eat meat.", "food", 1),
    ("fish", "риба", "noun", "A1", "We had fish for dinner.", "food", 1),
    # === A2 — GENERAL ===
    ("beautiful", "гарний/красивий", "adjective", "A2", "She is very beautiful.", "general", 2),
    ("important", "важливий", "adjective", "A2", "This meeting is important.", "general", 2),
    ("possible", "можливий", "adjective", "A2", "Is it possible to do that?", "general", 2),
    ("early", "рано", "adverb", "A2", "We arrived early.", "general", 2),
    ("late", "пізно", "adverb", "A2", "The bus was late.", "general", 2),
    ("money", "гроші", "noun", "A2", "I need more money.", "general", 2),
    ("time", "час", "noun", "A2", "There is no time to waste.", "general", 2),
    ("place", "місце", "noun", "A2", "Is this a good place to stay?", "general", 2),
    ("question", "питання", "noun", "A2", "Can I ask a question?", "general", 2),
    ("answer", "відповідь", "noun", "A2", "What is the answer?", "general", 2),
    ("problem", "проблема", "noun", "A2", "We have a big problem.", "general", 2),
    ("idea", "ідея", "noun", "A2", "That is a great idea!", "general", 2),
    ("friend", "друг", "noun", "A2", "She is my best friend.", "general", 2),
    ("city", "місто", "noun", "A2", "Kyiv is a wonderful city.", "general", 2),
    ("country", "країна", "noun", "A2", "Ukraine is a beautiful country.", "general", 2),
    # === A2 — WORK ===
    ("job", "робота", "noun", "A2", "I love my job.", "work", 2),
    ("office", "офіс", "noun", "A2", "She works in a big office.", "work", 2),
    ("meeting", "зустріч/нарада", "noun", "A2", "We have a meeting at ten.", "work", 2),
    ("boss", "керівник", "noun", "A2", "My boss is very strict.", "work", 2),
    ("salary", "зарплата", "noun", "A2", "She got a higher salary.", "work", 2),
    ("colleague", "колега", "noun", "A2", "She is my colleague.", "work", 2),
    ("deadline", "дедлайн", "noun", "A2", "The deadline is tomorrow.", "work", 2),
    # === A2 — TRAVEL ===
    ("hotel", "готель", "noun", "A2", "We stayed at a nice hotel.", "travel", 2),
    ("airport", "аеропорт", "noun", "A2", "We arrived at the airport.", "travel", 2),
    ("passport", "паспорт", "noun", "A2", "Don't forget your passport.", "travel", 2),
    ("ticket", "квиток", "noun", "A2", "I bought a train ticket.", "travel", 2),
    ("map", "карта", "noun", "A2", "Can I have a map of the city?", "travel", 2),
    ("suitcase", "валіза", "noun", "A2", "My suitcase is too heavy.", "travel", 2),
    # === B1 — GENERAL ===
    ("responsibility", "відповідальність", "noun", "B1", "It is your responsibility.", "general", 3),
    ("opportunity", "можливість", "noun", "B1", "Don't miss this opportunity.", "general", 3),
    ("relationship", "стосунки", "noun", "B1", "A good relationship is import.", "general", 3),
    ("experience", "досвід", "noun", "B1", "She has a lot of experience.", "general", 3),
    ("behavior", "поведінка", "noun", "B1", "His behavior was surprising.", "general", 3),
    ("achievement", "досягнення", "noun", "B1", "It is a great achievement.", "general", 3),
    ("argument", "суперечка", "noun", "B1", "They had a serious argument.", "general", 3),
    ("choice", "вибір", "noun", "B1", "You have to make a choice.", "general", 3),
    ("difference", "різниця", "noun", "B1", "What is the difference?", "general", 3),
    ("decision", "рішення", "noun", "B1", "That was a hard decision.", "general", 3),
    ("demand", "попит / вимога", "noun", "B1", "There is a huge demand.", "general", 3),
    # === B1 — TECHNOLOGY ===
    ("software", "програмне забезпечення", "noun", "B1", "This software is outdated.", "technology", 3),
    ("hardware", "апаратне забезпечення", "noun", "B1", "I need to upgrade my hardware.", "technology", 3),
    ("network", "мережа", "noun", "B1", "The network is down.", "technology", 3),
    ("database", "база даних", "noun", "B1", "The database has many records.", "technology", 3),
    ("download", "завантажувати", "verb", "B1", "Please download the file.", "technology", 3),
    ("upload", "вивантажувати", "verb", "B1", "Upload the photo here.", "technology", 3),
    ("password", "пароль", "noun", "B1", "Change your password often.", "technology", 3),
    ("application", "застосунок", "noun", "B1", "Install this application.", "technology", 3),
    # === B1 — NATURE ===
    ("environment", "навколишнє середовище", "noun", "B1", "Protect the environment.", "nature", 3),
    ("pollution", "забруднення", "noun", "B1", "Air pollution is a problem.", "nature", 3),
    ("climate", "клімат", "noun", "B1", "The climate is changing.", "nature", 3),
    ("energy", "енергія", "noun", "B1", "Solar energy is renewable.", "nature", 3),
    ("species", "вид (тварин)", "noun", "B1", "Many species are endangered.", "nature", 3),
    ("forest", "ліс", "noun", "B1", "Forests produce oxygen.", "nature", 3),
    # === B2 — GENERAL ===
    ("phenomenon", "феномен", "noun", "B2", "It is a fascinating phenomenon.", "general", 4),
    ("controversy", "суперечка/полеміка", "noun", "B2", "The topic caused controversy.", "general", 4),
    ("consequence", "наслідок", "noun", "B2", "Think about the consequences.", "general", 4),
    ("perspective", "точка зору", "noun", "B2", "See it from my perspective.", "general", 4),
    ("circumstance", "обставина", "noun", "B2", "Under no circumstances.", "general", 4),
    ("fundamental", "фундаментальний", "adjective", "B2", "A fundamental question.", "general", 4),
    ("inevitable", "неминучий", "adjective", "B2", "Change is inevitable.", "general", 4),
    ("significant", "значний", "adjective", "B2", "A significant improvement.", "general", 4),
    ("substantial", "суттєвий", "adjective", "B2", "A substantial amount of work.", "general", 4),
    ("consistent", "послідовний", "adjective", "B2", "Be consistent in your efforts.", "general", 4),
    # === B2 — WORK ===
    ("productivity", "продуктивність", "noun", "B2", "Boost your productivity.", "work", 4),
    ("negotiate", "вести переговори", "verb", "B2", "We need to negotiate.", "work", 4),
    ("invest", "інвестувати", "verb", "B2", "Invest in your future.", "work", 4),
    ("revenue", "дохід/виручка", "noun", "B2", "Revenue increased this year.", "work", 4),
    ("strategy", "стратегія", "noun", "B2", "We need a better strategy.", "work", 4),
    ("proposal", "пропозиція/проект", "noun", "B2", "Submit the proposal by Friday.", "work", 4),
    # === C1 — GENERAL ===
    ("alleviate", "полегшувати", "verb", "C1", "Medication can alleviate pain.", "general", 5),
    ("ambiguous", "двозначний", "adjective", "C1", "His answer was ambiguous.", "general", 5),
    ("coherent", "зв'язний/логічний", "adjective", "C1", "A coherent argument.", "general", 5),
    ("comprehensive", "всебічний", "adjective", "C1", "A comprehensive analysis.", "general", 5),
    ("contemplate", "розмірковувати", "verb", "C1", "She contemplated the decision.", "general", 5),
    ("diminish", "зменшувати", "verb", "C1", "Nothing can diminish his spirit.", "general", 5),
    ("elaborate", "детально розробляти", "verb", "C1", "Please elaborate on this idea.", "general", 5),
    ("facilitate", "сприяти/полегшувати", "verb", "C1", "Technology facilitates learning.", "general", 5),
    ("implication", "наслідок/підтекст", "noun", "C1", "The implications are serious.", "general", 5),
    ("intricate", "заплутаний/складний", "adjective", "C1", "An intricate network of roads.", "general", 5),
    # === C1 — TECHNOLOGY ===
    ("algorithm", "алгоритм", "noun", "C1", "The algorithm is efficient.", "technology", 5),
    ("infrastructure", "інфраструктура", "noun", "C1", "We need better infrastructure.", "technology", 5),
    ("cybersecurity", "кібербезпека", "noun", "C1", "Cybersecurity is critical.", "technology", 5),
    ("automation", "автоматизація", "noun", "C1", "Automation changes the economy.", "technology", 5),
    ("bandwidth", "пропускна здатність", "noun", "C1", "We need more bandwidth.", "technology", 5),
    # === C2 — GENERAL ===
    ("ubiquitous", "всюдисущий/повсюдний", "adjective", "C2", "Smartphones are ubiquitous.", "general", 6),
    ("ephemeral", "ефемерний/скороминущий", "adjective", "C2", "Fame is often ephemeral.", "general", 6),
    ("esoteric", "езотеричний/таємний", "adjective", "C2", "An esoteric philosophical view.", "general", 6),
    ("juxtaposition", "зіставлення/протиставлення", "noun", "C2", "A juxtaposition of ideas.", "general", 6),
    ("paradigm", "парадигма", "noun", "C2", "A paradigm shift in science.", "general", 6),
    ("rhetoric", "риторика", "noun", "C2", "Political rhetoric can mislead.", "general", 6),
    ("tenacious", "наполегливий/впертий", "adjective", "C2", "She is a tenacious worker.", "general", 6),
    ("pragmatic", "прагматичний", "adjective", "C2", "A pragmatic approach.", "general", 6),
    ("eloquent", "красномовний", "adjective", "C2", "An eloquent speech.", "general", 6),
    ("loquacious", "балакучий", "adjective", "C2", "A loquacious personality.", "general", 6),
    ("benevolent", "доброзичливий", "adjective", "C2", "A benevolent leader.", "general", 6),
    ("meticulous", "скрупульозний", "adjective", "C2", "Meticulous attention to detail.", "general", 6),
]

def migrateAddCategory(cursor):
    # Add category column if not present.
    cursor.execute("ALTER TABLE vocabulary ADD COLUMN category TEXT DEFAULT 'general'")
    print("  migration: added 'category' column.")

def seed():
    conn = sqlite3.connect(DBPath)
    cursor = conn.cursor()
    migrateAddCategory(cursor)
    
    inserted = 0
    skipped = 0
    for en, ua, pos, lvl, ex, cat, diff in VOCABULARY:
        exists = cursor.execute(
            "SELECT id FROM vocabulary WHERE english = ? AND level = ?", (en, lvl)
        ).fetchone()
        if exists:
            skipped += 1
            continue
        cursor.execute(
            'INSERT INTO vocabulary \n               (english, ukrainian, part_of_speech, level, example_sentence, category, difficulty)\n               VALUES (?, ?, ?, ?, ?, ?, ?)',
            (en, ua, pos, lvl, ex, cat, diff)
        )
        inserted += 1
    
    conn.commit()
    conn.close()
    print(f"Done! Inserted {inserted} words, skipped {skipped} duplicates.")
    print(f"Total vocabulary: A1, A2, B1, B2, C1, C2 — all major topics covered.")

if __name__ == "__main__":
    seed()
