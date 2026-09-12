# LCARS Framework - Інструкція з встановлення

## Швидке встановлення (Windows)

### Спосіб 1: Автоматичне встановлення (Рекомендовано)

Запустіть файл `install.bat` подвійним кліком. Це автоматично:
- Створить віртуальне середовище
- Встановить всі залежності
- Створить ярлик на робочому столі
- Налаштує все необхідне

### Спосіб 2: Ручне встановлення

```batch
# 1. Створити віртуальне середовище
python -m venv .venv

# 2. Активувати віртуальне середовище
.venv\Scripts\activate

# 3. Встановити залежності
pip install -e .

# 4. Запустити LCARS
python launcher.py
```

## Система побудови

### Доступні команди

```batch
# Очистити директорії побудови
build.bat clean

# Створити віртуальне середовище
build.bat setup

# Встановити залежності
build.bat install
build.bat install --dev  # З development залежностями

# Побудувати проект
build.bat build

# Запустити тести
build.bat test

# Запустити LCARS
build.bat run

# Створити дистрибутив
build.bat package

# Перевірити статус системи
build.bat status
```

### Python система побудови

```bash
# Використання Python напряму
python build.py clean
python build.py setup
python build.py install
python build.py build
python build.py test
python build.py run
python build.py package
```

## Структура проекту

```
LCARS-Framework/
├── lcars/              # Основний код фреймворку
│   ├── ui/            # Користувацький інтерфейс
│   ├── base/          # Базові компоненти
│   ├── core/          # Ядро системи
│   ├── app/           # Додатки
│   └── engineering/   # Інженерні системи
├── scripts/           # Допоміжні скрипти
├── assets/            # Ресурси
├── config/            # Конфігурація
├── test/              # Тести
├── install.bat        # Інсталятор для Windows
├── uninstall.bat      # Деінсталятор для Windows
├── build.bat          # Скрипт побудови для Windows
├── start.bat          # Швидкий запуск
├── build.py           # Python система побудови
├── setup.py           # Конфігурація встановлення
├── pyproject.toml     # Сучасне пакування Python
└── launcher.py        # Головний лаунчер
```

## Залежності

### Основні залежності
- PyQt6 >= 6.0.0 (GUI Framework)
- numpy >= 1.20.0 (Обробка даних)
- pandas >= 1.3.0 (Аналіз даних)
- matplotlib >= 3.4.0 (Візуалізація)
- psutil >= 5.8.0 (Системні утиліти)
- python-dotenv >= 0.19.0 (Змінні середовища)
- PyYAML >= 6.0.0 (Конфігурація)

### Додаткові залежності
- scipy >= 1.7.0 (Розширений аналіз даних)
- vispy >= 0.14.0 (3D графіка з прискоренням GPU)
- PyOpenGL >= 3.1.5 (OpenGL бібліотеки)

### AI/ML залежності
- transformers >= 4.40.0 (NLP моделі)
- torch >= 2.0.0 (Deep learning)
- kagglehub >= 0.3.0 (Kaggle датасети)
- accelerate >= 0.30.0 (Прискорення моделей)

## Налаштування для розробки

```bash
# Встановити з development залежностями
pip install -e ".[dev]"

# Запустити тести
pytest test/ -v

# Форматування коду
black lcars/

# Перевірка типів
mypy lcars/
```

## Запуск LCARS

### Windows
```batch
# Подвійний клік на ярлик робочого столу
LCARS.lnk

# Або використовувати bat файли
start.bat
build.bat run

# Або напряму через Python
.venv\Scripts\python launcher.py
```

### Linux/Mac
```bash
# Активувати віртуальне середовище
source .venv/bin/activate

# Запустити LCARS
python launcher.py
```

## Виправлення проблем

### Python не знайдено
Переконайтеся, що Python 3.8+ встановлений і доданий в PATH.

### Помилка встановлення PyQt6
```batch
pip install --upgrade pip
pip install PyQt6 PyQt6-Qt6 PyQt6-sip
```

### Проблеми з віртуальним середовищем
Видаліть директорію `.venv` і запустіть встановлення знову.

### Помилки імпорту
Переконайтеся, що ви знаходитесь в кореневій директорії проекту і віртуальне середовище активовано.

## Видалення

```batch
uninstall.bat
```

Потім вручну видаліть директорію проекту, якщо потрібно.

## Системні вимоги

- Python 3.8 або вище
- Windows 10/11 (рекомендовано)
- 4GB RAM мінімум, 8GB рекомендовано
- 500MB вільного місця на диску