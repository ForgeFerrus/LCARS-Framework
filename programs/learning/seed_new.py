import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lcars", "data", "english_learning_v2.db")

texts = [
    ("B1", "The History of Tea", "Tea is the second most popular drink in the world, after water. It originated in China as a medicinal drink. It was introduced to Portuguese priests and merchants in Lebanon during the 16th century. Drinking tea became popular in Britain during the 17th century.", "Чай — другий за популярністю напій у світі після води. Він виник у Китаї як лікувальний напій. У 16-му столітті його завезли португальським священникам і купцям до Лівану. Розпивання чаю стало популярним у Британії в 17 столітті."),
    ("B2", "Artificial Intelligence in Modern Society", "Artificial intelligence (AI) is rapidly changing the way we live and work. While some fear that automation will lead to widespread job losses, others argue that AI will create new opportunities and industries. Regulating AI development is becoming a critical topic for governments.", "Штучний інтелект (ШІ) стрімко змінює те, як ми живемо та працюємо. Хоча дехто побоюється, що автоматизація призведе до масової втрати робочих місць, інші стверджують, що ШІ створить нові можливості та галузі. Регулювання розвитку ШІ стає критично важливою темою для урядів."),
    ("C1", "The Philosophy of Existentialism", "Existentialism explores the problem of human existence and centers on the lived experience of the thinking, feeling, acting individual. Key themes include human freedom, meaninglessness, anxiety, and authenticity. It emphasizes that existential questions are central to human life.", "Екзистенціалізм досліджує проблему людського існування та зосереджується на пережитому досвіді індивіда, який думає, відчуває та діє. Ключові теми включають людську свободу, безглуздість, тривогу та автентичність. Він наголошує, що екзистенційні питання є центральними в людському житті."),
]

tests = [
    ("B1", "What is the synonym of 'rapid'?", "Slow", "Fast", "Boring", "Sad", "B"),
    ("B1", "Choose the correct sentence:", "She don't like it.", "She doesn't likes it.", "She doesn't like it.", "She not like it.", "C"),
    ("B2", "What does 'to mitigate' mean?", "To make less severe", "To amplify", "To complain", "To discover", "A"),
    ("B2", "Select the correct third conditional sentence:", "If I had knew, I would go.", "If I will know, I would go.", "If I had known, I would have gone.", "If I knew, I would went.", "C"),
    ("C1", "Which of the following describes 'ephemeral'?", "Lasting forever", "Short-lived", "Extremely heavy", "Dangerous", "B"),
    ("C1", "Identify the correct use of subjunctive:", "I suggest he goes now.", "I suggest he go now.", "I suggest that he went.", "I suggest he going.", "B"),
]

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert new texts
    for level, title, en, ua in texts:
        cursor.execute('''
            INSERT INTO mini_texts (level, title, english_text, translated_text)
            VALUES (?, ?, ?, ?)
        ''', (level, title, en, ua))
        
    # Insert new tests
    for level, q, a, b, c, d, correct in tests:
        cursor.execute('''
            INSERT INTO tests (level, question, option_a, option_b, option_c, option_d, correct_option)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (level, q, a, b, c, d, correct))
        
    conn.commit()
    conn.close()
    print("Database seeded with B1, B2, C1 texts and tests.")

if __name__ == "__main__":
    seed()
