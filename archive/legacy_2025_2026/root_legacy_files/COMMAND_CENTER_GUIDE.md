# LCARS Command Center v4.0 - User Guide

## Quick Start

```bash
python start.py
```

Це запустить **Central Command Center** - універсальний хаб для управління всією системою.

---

## Interface Overview

### Main Menu (LEFT PANEL)
7 основних категорій:

1. **HOME** 🏠
   - Загальна інформація про систему
   - Системна статистика
   - Статус і час

2. **GEANT4** ⚛
   - Управління Geant4 проектами
   - Створення симуляцій
   - Налаштування детекторів
   - NCC-02 конфігурація

3. **EXPORT** 💾
   - Експорт до GDML (Geant4 формат)
   - Експорт до C++ (компільовані модулі)
   - Експорт JSON (конфігурації)
   - Побудова детекторів

4. **VISUALIZE** 📊
   - Создание траєкторій частинок
   - Загрузка CSV даних
   - Запуск 3D viewer

5. **MONITOR** 📈
   - Системний статус
   - CPU моніторинг
   - Пам'ять та диск

6. **CONFIG** ⚙
   - Зміна теми
   - Налаштування шляхів
   - Змінні оточення

7. **TOOLS** 🔧
   - Перевірка здоров'я системи
   - Перевірка залежностей
   - Запуск тестів

---

## Available Functions

### GEANT4 Module (5 buttons)

| Функція | Опис |
|---------|------|
| **Discover Projects** | Пошук Geant4 проектів на диску (ENX*, NCC-*) |
| **Create New Simulation** | Створити новий симуляційний об'єкт |
| **Load Configuration** | Завантажити конфіг з JSON файлу |
| **Configure NCC-02** | Готова конфіг для NCC-02 детектора |
| **Save Configuration** | Зберегти поточну конфіг |

**Example Workflow:**
```
1. Discover Projects → знайти мої ENX проекти
2. Configure NCC-02 → готова конфіг 
3. Save Configuration → зберегти як JSON
```

### EXPORT Module (4 buttons)

| Функція | Вихід | Використання |
|---------|-------|--------------|
| **Export to GDML** | XML формат для Geant4 | Симуляції |
| **Export to C++** | Header + Implementation | Компіляція |
| **Export JSON** | JSON конфіги | Переносимість |
| **Build NCC-02** | Готовий детектор | Тестування |

**Example Workflow:**
```
1. Configure NCC-02 → створити конфіг
2. Build NCC-02 → збудувати детектор
3. Export to GDML → отримати XML
4. Export to C++ → отримати .hh/.cc файли
```

### VISUALIZATION Module (3 buttons)

| Функція | Опис |
|---------|------|
| **Create Trajectory** | Згенерувати траєкторію електрона (test) |
| **Load CSV Data** | Завантажити дані про частинки з CSV |
| **Launch 3D Viewer** | Запустити Vispy 3D відоб

раження |

**CSV Format Expected:**
```
particle_id,particle_type,x1,y1,z1,x2,y2,z2,x3,y3,z3,energy_keV
1,electron,0,0,0,1,1,1,2,2,2,100.0
```

### MONITOR Module (4 buttons)

Реальний час моніторинг:
- CPU usage
- Memory usage
- Disk usage
- Process count

### CONFIG Module (3 buttons)

| Функція | Результат |
|---------|-----------|
| **Change Theme** | Выбір era: 22nd/23rd/24th/25th |
| **Set Geant4 Path** | Налаштувати шлях до Geant4 |
| **Environment Variables** | Переглянути і редагувати env |

### TOOLS Module (3 buttons)

| Функція | Результат |
|---------|-----------|
| **Health Check** | Перевірка всіх модулів |
| **Dependency Check** | Статус залежностей (PyQt6, NumPy, etc) |
| **Test All Features** | Запуск 10 test cases |

---

## Common Workflows

### Workflow 1: Simulating a Particle

```
1. GEANT4 → Discover Projects
2. GEANT4 → Configure NCC-02
3. EXPORT → Build NCC-02
4. GEANT4 → Save Configuration
5. VISUALIZE → Create Trajectory
6. VISUALIZE → Launch 3D Viewer
```

### Workflow 2: Exporting for Geant4 Use

```
1. GEANT4 → Configure NCC-02
2. EXPORT → Export to GDML
3. EXPORT → Export to C++
   → Files: detector.gdml, Detector.hh, DetectorConstruction.cc
```

### Workflow 3: System Health Check

```
1. TOOLS → Health Check (all modules)
2. TOOLS → Dependency Check (packages)
3. MONITOR → System Status (resources)
```

---

## Output Display

Кожна функція має:
- **Text Output Panel** (внизу) - результати операції
- **Status Indicators**
- **Error Messages** (якщо щось пішло не так)

### Text Output Examples:

**GDML Export Success:**
```
GDML Export: SUCCESS
File created in temp directory
```

**Configuration Save:**
```
Configured NCC-02:
Detector: Detector_001
Particle: electron
Physics: standard_physics
Events: 1000
Status: ready
```

---

## Keyboard Shortcuts

| Комбінація | Дія |
|-----------|-----|
| `Ctrl+Q` | Закрити додаток |
| `Ctrl+H` | Перейти на HOME |
| `Tab` | Переміщення між кнопками |
| `Enter` | Натиснути активну кнопку |

---

## Troubleshooting

### Error: "Geant4 not found"
→ Йти в CONFIG → Set Geant4 Path і указати папку

### Error: "No projects discovered"
→ Перевірити, чи є папки з префіксом ENX* або NCC-*

### Error: "PyQt6 not installed"
→ Запустити: `pip install PyQt6`

### 3D Viewer не запускається
→ Потребує графічного дисплея (не працює в SSH без X11)

---

## Technical Details

### Architecture

```
CommandCenter (Main Window)
├── Left Panel (Menu)
│   ├── 7 Category Buttons
│   └── System Info Display
│
└── Right Panel (Content)
    ├── HOME page
    ├── GEANT4 page (5 buttons + output)
    ├── EXPORT page (4 buttons + output)
    ├── VISUAL page (3 buttons + output)
    ├── MONITOR page (4 buttons + output)
    ├── CONFIG page (3 buttons + output)
    └── TOOLS page (3 buttons + output)
```

### Total Interactive Elements

- **7** main category buttons
- **22** action buttons (across all modules)
- **7** text output panels
- **1** central information display

**Everything is clickable from this single window!**

### Color Scheme (LCARS 25th Century)

- **Accent Color:** Cyan (#00FFFF)
- **Button Colors:** Multi-color palette (red, orange, green, blue, yellow)
- **Text Color:** White
- **Background:** Black
- **Hover Effect:** Bright version + white border

---

## Module Integration

All modules are connected:
- **Config** → GEANT4 (loads configurations)
- **GEANT4** → EXPORT (builds detectors)
- **EXPORT** → CONFIG (saves results)
- **MONITOR** → All (tracks resources)
- **TOOLS** → All (tests everything)

---

## File Locations

| Файл | Призначення |
|------|------------|
| `command_center.py` | Главний GUI модуль |
| `start.py` | Entry point |
| `lcars/core/*` | Логіка (geant4, export, visualization) |
| `lcars/themes/*` | LCARS palette system |
| `config/*.json` | Конфігураційні файли |

---

## Version Info

```
LCARS Framework v4.0
Command Center v4.0
Status: OPERATIONAL
Build: January 15, 2026
```

---

**Last Updated:** January 15, 2026
**Maintained by:** LCARS Development Team
