# LCARS Framework - Installation Guide

## Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- Required Python packages (see `requirements.txt`)

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/lcars-framework.git
cd lcars-framework
```

### 2. Set Up a Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Framework
```bash
python start_lcars.py
```

## Troubleshooting
- **Missing Dependencies**: Ensure all packages in `requirements.txt` are installed.
- **Permission Issues**: Run the commands with elevated privileges if necessary.
- **Python Version**: Verify that Python 3.11+ is installed.

---
*LCARS Framework v1.0 - Installation Guide*
# INSTALLATION AND SETUP GUIDE

## 🌟 Встановлення LCARS Framework

### Вимоги перед встановленням
- Windows 10/11 (або Linux/Mac)
- Python 3.9 або новіше
- Інтернет-з'єднання (для встановлення пакетів)

### Крок 1: Перевірка Python

Відкрийте PowerShell і перевірте версію Python:

```powershell
python --version
```

Якщо Python не встановлений, завантажте його з https://www.python.org/

### Крок 2: Навігація до папки Framework

```powershell
cd "c:\Users\Forge\MyProject\Geant4\Enterprise\NCC-project\LCARS-Framework"
```

### Крок 3: Встановлення залежностей

#### Варіант A: Використання batch файлу (найпростіше)
```powershell
# Просто запустіть:
run.bat
```

#### Варіант B: Ручне встановлення
```powershell
# Встановіть всі необхідні пакети:
pip install -r requirements.txt

# Основні пакети:
pip install PyQt6>=6.0.0
pip install numpy>=1.20.0
pip install pandas>=1.3.0
pip install matplotlib>=3.4.0
```

### Крок 4: Перевірка встановлення

```powershell
python -c "import PyQt6; print('✓ PyQt6 встановлено')"
python -c "from lcars.ui.main_window import LCARSMainWindow; print('✓ LCARS Framework готовий')"
```

---

## 🚀 Запуск програми

### Метод 1: Batch файл (Windows)
```powershell
# Просто запустіть:
.\run.bat

# Або двічі клікніть на run.bat
```

### Метод 2: Python безпосередньо
```powershell
# Запуск з автоматичною перевіркою залежностей:
python run.py

# Або простий запуск (якщо залежності встановлені):
python main.py
```

### Метод 3: Прямого запуску з Python
```powershell
python -c "from lcars.ui.main_window import LCARSMainWindow; from PyQt6.QtWidgets import QApplication; import sys; app = QApplication(sys.argv); root_path = Path('.'); window = LCARSMainWindow(Path('./').parent); window.show(); sys.exit(app.exec())"
```

---

## 📋 Що буде в інтерфейсі

При першому запуску ви побачите:

```
┌──────────────────────────────────────────┐
│  ENTERPRISE LCARS FRAMEWORK               │
│  ✓ Geant4: Detected          Projects: 9 │
└──────────────────────────────────────────┘

┌──────────────┐  ┌─────────────────────────┐
│ PROJECTS     │  │ PROJECT INFO / TABS     │
├──────────────┤  ├─────────────────────────┤
│ • ENX01      │  │ Tabs:                   │
│ • ENX02      │  │ • PROJECT INFO          │
│ • ENX03      │  │ • EXECUTION             │
│ • ENX04      │  │ • ANALYSIS              │
│ • ENX05      │  │ • ENVIRONMENT           │
│ • ENX06      │  │                         │
│ • ENX07      │  │ [Build Project]         │
│ • ENX08      │  │ [Run Simulation]        │
│ • ENX09      │  │ [Stop Task]             │
│ • NCC-00     │  │                         │
│ • NCC-01     │  │ CONSOLE OUTPUT:         │
│ • NCC-02     │  │ ┌─────────────────────┐ │
│              │  │ │ Output here...      │ │
│ [Refresh]    │  │ └─────────────────────┘ │
└──────────────┘  └─────────────────────────┘
```

---

## ⚙️ Налаштування після встановлення

### 1. Налаштування Geant4 (якщо необхідно)

1. Запустіть програму
2. Перейдіть на вкладку **ENVIRONMENT**
3. Натисніть кнопку **"Set Geant4 Path"**
4. Виберіть папку з встановленням Geant4
5. Подтвердіть вибір

### 2. Перевірка проектів

1. На вкладці **PROJECT INFO** виберіть проект з лівої панелі
2. Переконайтеся, що відображаються:
   - Шлях до проекту
   - Папка build
   - Виконуваний файл
   - Папка data

### 3. Налаштування змінних середовища

Створіть файл `.env` з змісту з `.env.example`:

```powershell
copy .env.example .env
```

Потім відредагуйте `.env` за необхідністю.

---

## 🔧 Налаштування Geant4 (якщо він не виявлений)

### Windows

1. Завантажте Geant4 з https://geant4.web.cern.ch/
2. Встановіть у `C:\geant4` (або інший каталог)
3. У програмі натисніть "Set Geant4 Path"
4. Виберіть цей каталог

### Перевірка встановлення

```powershell
# Перевірте наявність:
Test-Path "C:\geant4\bin\geant4-config.exe"
```

---

## 🧪 Запуск прикладів

### Запуск тестів
```powershell
python -m unittest tests.py -v
```

### Запуск прикладів використання
```powershell
python examples.py
```

### Запуск аналізу даних
```powershell
cd NCC-02
python ..\LCARS-Framework\lcars\core\analysis.py
```

---

## 🐛 Вирішення проблем

### Проблема: "ModuleNotFoundError: No module named 'PyQt6'"

**Рішення:**
```powershell
pip install PyQt6
```

### Проблема: "Python не знайдений"

**Рішення:**
1. Переконайтеся, що Python встановлений
2. Додайте Python до PATH під час встановлення
3. Перезавантажте PowerShell

### Проблема: "Порт уже використовується"

**Рішення:** Зупиніть попередній процес:
```powershell
Get-Process python | Stop-Process -Force
```

### Проблема: Програма вікупиняється при запуску

**Рішення:**
1. Перевірте логи: `type logs\lcars_framework.log`
2. Встановіть DEBUG_MODE=true в .env
3. Запустіть еще раз і перевірте помилки

### Проблема: Проекти не виявляються

**Рішення:**
1. Переконайтеся, що папки мають імена ENX* або NCC-*
2. Вони повинні бути в тій же папці, що й `LCARS-Framework`
3. Натисніть "Refresh Projects" в програмі

---

## 📞 Технічна підтримка

### Виведення логів

```powershell
# Переглянути останні 50 рядків логу:
Get-Content logs\lcars_framework.log -Tail 50

# Або відкрийте в TextEdit:
notepad logs\lcars_framework.log
```

### Перезавантаження

```powershell
# Видаліть кеш та конфіг для чистого старту:
Remove-Item config\environment.json
Remove-Item logs\* -Force

# Запустіть знову:
python run.py
```

### Оновлення залежностей

```powershell
# Оновіть всі пакети:
pip install --upgrade -r requirements.txt

# Або окремо:
pip install --upgrade PyQt6 numpy pandas matplotlib
```

---

## 📚 Додаткові ресурси

- **Документація**: `DOCUMENTATION.md`
- **Швидкий старт**: `QUICKSTART.py`
- **Приклади**: `examples.py`
- **Тести**: `tests.py`

---

## ✅ Контрольний список встановлення

- [ ] Python 3.9+ встановлений
- [ ] `pip install -r requirements.txt` виконаний
- [ ] Програма запускається без помилок
- [ ] Проекти виявляються в лівій панелі
- [ ] Вкладки EXECUTION та ANALYSIS видимі
- [ ] Логи створюються в `logs/`
- [ ] Конфіг створюється в `config/`

---

## 🎉 Готово!

Тепер ви можете:

1. **Управляти проектами** - вибирати їх з лісту
2. **Будувати проекти** - кнопка Build
3. **Запускати симуляції** - кнопка Run
4. **Аналізувати дані** - вкладка Analysis
5. **Налаштовувати середовище** - вкладка Environment

**Гарного запуску!** 🚀