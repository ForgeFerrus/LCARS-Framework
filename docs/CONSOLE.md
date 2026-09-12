# ◤ LCARS ONBOARD CONSOLE // ДОВІДНИК 🖖
# =============================================================================
# ФАЙЛ : docs/CONSOLE.md
# ОПИС : Повний довідник команд та принципів роботи консолі бортового комп'ютера.
# =============================================================================

## ЗАПУСК

    py start_lcars.py          # CLI — бортовий комп'ютер (за замовчуванням)
    py start_lcars.py --gui    # GUI — графічний інтерфейс LCARS Desktop

---

## АРХІТЕКТУРА

    Оператор
      ↓ текст
    start_lcars.py :: RunCliMode
      ↓
    LCARSConsole.Execute(text)        ← lcars/service/console.py
      ↓ класифікація вводу
      ├── Відома команда?        → прямий хендлер
      ├── Системна директива?   → Command().Execute()
      ├── Кирилиця / фраза?     → LocalIntelligence → BoardComputer.ProcessVoiceDirective
      ├── Shell команда?        → TryShellCommand (subprocess)
      ├── Bridge namespace?     → TryBridgeCommand
      ├── Шлях до файлу?        → HandlePath
      └── Все інше              → BoardComputer.AskNeuralCore → Groq AI

---

## КОМАНДИ

### СИСТЕМА

    help              — цей довідник (скорочена версія в CLI)
    status            — стан консолі: режим, AI-бекенд, alert, uptime
    version           — версія LCARS Framework
    bios              — стан BIOS / ядра
    diag              — діагностичний протокол рівень 3 (стандартний)
    diag 1            — повна тотальна діагностика (всі проби)
    diag 5            — автоматичний моніторинг (тільки EPS + CORE)
    alert red         — тактична тривога ЧЕРВОНА
    alert yellow      — тактична тривога ЖОВТА
    alert green       — зняти тривогу
    mode quantum      — квантовий режим процесора
    mode optical      — оптичний режим процесора
    model             — показати поточний AI-бекенд та доступні моделі
    modes             — список доступних режимів консолі
    clear / cls       — очистити екран
    exit / quit       — завершити сесію

### ФАЙЛИ ТА ДИРЕКТОРІЇ

    ls [path]         — список файлів у поточній або вказаній директорії
    dir [path]        — те саме (псевдонім ls)
    cd <path>         — змінити поточну директорію
    pwd               — показати поточну директорію

### КОМПІЛЯЦІЯ ТА ЗАПУСК

    compile <file>    — компілювати файл. Компілятор визначається автоматично
    build <file>      — псевдонім compile
    run <file>        — запустити файл (Python / .lcars / компілятор)
    source <file>     — псевдонім run
    py <file.py>      — запуск Python напряму через системний інтерпретатор
    python <file.py>  — псевдонім py

Підтримувані компілятори (auto-detect):

    .lcars                  ScriptCompiler
    .py (app)               PythonAppCompiler
    .cpp / Geant4           Geant4Compiler
    CMakeLists.txt          CMakeCompiler
    .pro (Qt)               QMakeCompiler
    .quantum                QuantumCompiler
    Android project         AndroidCompiler
    .bat / .cmd             CmdCompiler
    .ps1                    PowerShellCompiler
    .sh                     BashCompiler

### BRIDGE / SDK / ЗОВНІШНІ ПІДКЛЮЧЕННЯ

    bridge <name>     — підключитись до Bridge (AI, SDK, DATABASE, CLOUD, ...)
    connect <name>    — псевдонім bridge
    catalog [prefix]  — каталог зареєстрованих Bridge-з'єднань

Bridge Namespace: AI SDK CLI IDE DATABASE CLOUD NETWORK STORAGE
                  QUANTUM SCIENCE PHYSICS ENGINEERING SECURITY
                  OPTIMIZATION ANALYTICS SIMULATION RENDERING XR SCENE

### ДИРЕКТИВИ БОРТОВОГО КОМП'ЮТЕРА

    directive <cmd>   — виконати системну директиву напряму
    agent             — статус Copilot-агента
    agent <prompt>    — надіслати запит до Copilot

### GUI

    gui / padd / boot / desktop — запустити графічний інтерфейс LCARS (Boot → Desktop)

---

## ПРИРОДНЯ МОВА

Консоль розпізнає природні фрази (українська та англійська) і передає їх
до бортового AI (Groq / openai/gpt-oss-120b) з живим контекстом корабля:

    LCARS: які підсистеми зараз активні?
    LCARS: де знаходяться файли інтерфейсу?
    LCARS: яка архітектура проекту?
    LCARS: стан warp core?

Живий контекст що передається в AI при кожному запиті:
  - Ship class та registry (NCC-74205)
  - Timestamp
  - Список підсистем (13 online)
  - Mounted isolinear chips
  - Active interfaces
  - Runtime mode (QUANTUM / OPTICAL)

---

## КЛАСИФІКАЦІЯ ВВОДУ

    COMMAND   — зареєстрована команда або системна директива
    SHELL     — схожий на shell (dir, git, pip, powershell...)
    THINK     — фраза-роздум / природня мова
    UNKNOWN   — невизначений короткий ввід → AI

---

## ДІАГНОСТИЧНІ РІВНІ

    1 — Тотальна:       всі проби, всі підсистеми
    2 — Глибока:        критичні та важливі вузли
    3 — Аналіз:         стандарт (за замовчуванням)
    4 — Фонова:         тільки EPS + CORE
    5 — Автоматичний:   EPS + CORE (мінімум)

---

## ФАЙЛИ

    start_lcars.py              — точка входу (CLI або GUI)
    lcars/service/console.py    — сервіс консолі (LCARSConsole)
    lcars/ui/terminal.py        — UI-термінал (LCARSTerminal / PADD) для GUI
    lcars/service/diagnostic.py — діагностичний модуль (DiagnosticEngine)
    lcars/service/provider.py   — AI-провайдер (Groq / openai/gpt-oss-120b)
    lcars/core/computer.py      — бортовий комп'ютер (BoardComputer)
    lcars/system/compiler.py    — компілятори (IsolinearCompiler)
    docs/CONSOLE.md             — цей файл

---

◤ LCARS Framework // Starfleet Core // NCC-74205 🖖
