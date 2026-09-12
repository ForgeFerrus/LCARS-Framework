# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import datetime


def ProjectRoot() -> Path:
    # Функція: Отримання кореневої директорії проєкту
    # Призначення: Визначає шлях до кореня проєкту відносно поточного файлу
    # Логіка: <repo>/lcars/system/journal.py -> parents[2] == repo root
    return Path(".").resolve().parents[2]


def JournalDir() -> Path:
    # Функція: Отримання або створення директорії журналів
    # Призначення: Забезпечує існування папки journal в корені проєкту
    # Логіка: Створюємо директорію якщо вона не існує, повертаємо шлях
    d = ProjectRoot() / 'journal'
    d.mkdir(parents=True, exist_ok=True)
    return d


def record(entry_type: str, message: str, metadata: dict | None = None) -> Path:
    # Функція: Запис події в бортовий журнал
    # Призначення: Додає запис у щоденний markdown-файл журналу
    # Параметри:
    #   entry_type - тип події (INFO, WARNING, ERROR тощо)
    #   message - текст повідомлення
    #   metadata - додаткові дані (опціонально)
    # Повертає: шлях до файлу журналу
    ts = datetime.datetime.now()
    # Формуємо рядок дати у форматі ISO (YYYY-MM-DD)
    date_str = ts.strftime('%Y-%m-%d')
    # Формуємо рядок часу у форматі HH:MM:SS
    time_str = ts.strftime('%H:%M:%S')
    # Формуємо шлях до файлу журналу за поточною датою
    journal_path = JournalDir() / f"{date_str}.md"
    # Відкриваємо файл в режимі append ('a') для додавання запису
    with open(journal_path, 'a', encoding='utf-8') as f:
        # Записуємо рядок формату [час] [тип] повідомлення
        f.write(f"[{time_str}] [{entry_type}] {message}\n")
        # Якщо передані метадані - записуємо їх компактно
        if metadata:
            f.write(f"    metadata: {metadata}\n")
    # Повертаємо шлях до файлу для інформації викликаючого
    return journal_path


def read(date: str | None = None) -> str:
    # Функція: Читання журналу за вказану дату
    # Призначення: Повертає вміст файлу журналу для дати або сьогодні
    # Параметри:
    #   date - дата у форматі YYYY-MM-DD (None = сьогодні)
    # Повертає: текст журналу або порожній рядок якщо файлу немає
    # Якщо дата не передана - використовуємо поточну дату
    if date is None:
        date = datetime.datetime.now().strftime('%Y-%m-%d')
    # Формуємо шлях до файлу журналу за вказаною датою
    p = _journal_dir() / f"{date}.md"
    # Перевіряємо чи існує файл журналу
    if not p.exists():
        # Якщо файлу немає - повертаємо порожній рядок
        return ""
    # Читаємо та повертаємо весь текст файлу
    return p.read_text(encoding='utf-8')
