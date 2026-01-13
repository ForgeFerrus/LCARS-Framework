# 🚀 LCARS Framework - СТАРТОВА ІНСТРУКЦІЯ

## 📌 За 5 хвилин до першого запуску

### ШАГ 1️⃣: Встановлення залежностей

Відкрийте **PowerShell** у папці `LCARS-Framework` та запустіть:

```powershell
pip install -r requirements.txt
```

або просто запустіть:

```powershell
.\run.bat
```

### ШАГ 2️⃣: Запуск програми

```powershell
python run.py
```

### ШАГ 3️⃣: Перша конфігурація

1. **Автоматично** виявляться всі проекти (ENX01-ENX09, NCC-00-NCC-02)
2. Вони з'являться в **лівій панелі**
3. Якщо Geant4 не виявлено → перейдіть на вкладку **ENVIRONMENT** та натисніть "Set Geant4 Path"

---

## 🎮 Основні операції

### Побудувати проект

1. Виберіть проект з лівої панелі
2. Перейдіть на вкладку **EXECUTION**
3. Натисніть **[Build Project]**
4. Спостерігайте вивід у консолі

### Запустити симуляцію

1. Виберіть проект
2. На вкладці **EXECUTION** натисніть **[Run Simulation]**
3. Очікуйте завершення
4. Результати будуть в папці проекту

### Аналізувати дані (NCC-02)

1. Виберіть **NCC-02** в лівій панелі
2. Перейдіть на вкладку **ANALYSIS**
3. Натисніть **[Analyze Spectra]**
4. Будуть створені графіки:
   - `spectra_pure_sample.png`
   - `spectra_reactant_sample.png`
   - `reactions_*.png`

---

## 🎨 Інтерфейс LCARS

Інтерфейс розроблений у стилі **Star Trek**:

- 🟠 **Помаранчеві** кнопки - основні дії
- 🔵 **Сині** панелі - інформація
- 🟡 **Жовтий** текст - заголовки
- 🖥️ **Зелений** текст в консолі - успіх
- 🔴 **Червоні** повідомлення - помилки

---

## ⚙️ Файли конфігурації

### `config/environment.json`
```json
{
  "GEANT4_PATH": "C:\\geant4",  ← встановіть своє значення
  "env_vars": {...}
}
```

### `.env`
```
GEANT4_PATH=C:\geant4
LOG_LEVEL=INFO
DEBUG_MODE=False
```

---

## 📋 Структура проекту

```
LCARS-Framework/
│
├── lcars/                    ← основний пакет
│   ├── core/                 ← ядро (управління Geant4)
│   ├── ui/                   ← інтерфейс
│   └── utils/                ← утиліти
│
├── config/                   ← конфігурація
├── logs/                     ← логи (auto-created)
│
├── main.py                   ← простий запуск
├── run.py                    ← запуск з перевіркою
├── run.bat                   ← для Windows
├── run.sh                    ← для Linux/Mac
│
├── examples.py               ← приклади використання
├── tests.py                  ← unit тести
├── health_check.bat          ← перевірка системи
│
└── DOCUMENTATION.md          ← повна документація
```

---

## 🔍 Перевірка встановлення

Запустіть:

```powershell
.\health_check.bat
```

Має вивести:
```
[1/5] Checking Python...           ✓ Python 3.x.x
[2/5] Checking PyQt6...            ✓ PyQt6 installed
[3/5] Checking LCARS Framework...  ✓ LCARS Framework OK
[4/5] Checking Geant4...           ✓ Geant4 Detected (або ⚠ NOT found)
[5/5] Checking Projects...         ✓ Found X projects
```

---

## 🐛 Вирішення поширених проблем

### ❌ "ModuleNotFoundError: No module named 'PyQt6'"

```powershell
pip install PyQt6
```

### ❌ "Python не знайдений"

Переінсталюйте Python з https://www.python.org/ (обов'язково додайте до PATH)

### ❌ "Geant4 не виявлено"

Розташування:
- Windows: `C:\geant4\` або `C:\Program Files\geant4\`
- Встановіть вручну в GUI (ENVIRONMENT tab)

### ❌ Програма вікупиняється

Перевірте логи:
```powershell
type logs\lcars_framework.log
```

---

## 📖 Подальша інформація

- **Повна документація**: `DOCUMENTATION.md`
- **Архітектура**: `ARCHITECTURE.md`
- **Встановлення**: `INSTALL.md`
- **Приклади**: `examples.py`
- **Швидкий старт**: `QUICKSTART.py`

---

## 💡 Поради

1. **Перший запуск може бути повільним** - це нормально, оскільки відбувається аналіз проектів
2. **Гарячі клавіші** - користуйтесь фокусом на вкладках для навігації
3. **Консоль** - показує реал-тайм вивід всіх команд
4. **Логи** - завжди перевіряйте їх при проблемах

---

## 🎯 Наступні кроки

1. ✅ Встановити залежності (`pip install -r requirements.txt`)
2. ✅ Запустити програму (`python run.py`)
3. ✅ Вибрати проект в лівій панелі
4. ✅ Виконати дію (Build/Run/Analyze)
5. ✅ Переглянути результати

---

## 🌟 Готово!

Тепер ви готові працювати з:
- 📊 **9 проектів ENX** (ENX01-ENX09)
- 📈 **3 проекти NCC** (NCC-00, NCC-01, NCC-02)
- 🔬 **Системою Geant4**

**Гарного запуску!** 🚀

*Live long and prosper with Enterprise Framework* 🖖

---

## 📞 Швидка довідка команд

```powershell
# Встановлення
pip install -r requirements.txt

# Запуск
python run.py

# Тести
python -m unittest tests.py

# Приклади
python examples.py

# Здоров'я системи
.\health_check.bat

# Переглід логів
type logs\lcars_framework.log

# Аналіз даних (NCC-02)
cd NCC-02
python ..\LCARS-Framework\lcars\core\analysis.py
```

---

## 🔐 Мінімальні вимоги

- Python 3.9+
- 512 MB вільної пам'яті
- 100 MB місця на диску
- Windows 10/11 або Linux

