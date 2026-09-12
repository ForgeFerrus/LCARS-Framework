
# Дорожня карта внутрішніх програм

Цей документ містить перелік внутрішніх, основних застосунків, запланованих для LCARS Framework, та їхні пріоритети.

## Високий пріоритет

- Geant4 Workstation
  - Шлях: `programs/Geant4`
  - Опис: Настільний застосунок для запуску, керування та моніторингу завдань симуляції Geant4. Містить помічники для збірки, чергу завдань, переглядач результатів і гачки для візуалізації.

- Внутрішній браузер
  - Шлях: `programs/browser`
  - Опис: Вбудований браузер для внутрішніх інтерфейсів та веб-контенту (Qt WebEngine або еквівалент). Легкий, керований з плагінів.

- Файловий менеджер (у стилі Total Commander)
  - Шлях: `programs/file_manager`
  - Опис: Двопанельний файловий менеджер з копіюванням/переміщенням, архівацією та гачками для плагінів для операцій з проєктами.

## Середній пріоритет

- Notebook / Notes (`programs/notebook.py`)
- Logger / Journals (`programs/logger_app.py`)
- SMS/Chat client (`programs/sms_client.py`) **(now shows shared contact list)**
- Email client (`programs/email_client.py`) **(uses contacts for addressing)**
- Phone/VoIP (`programs/phone.py`) **(select number from contacts)**
- Social messengers: Facebook/Twitter/Telegram/Viber/WhatsApp
  (individual stubs under `programs/messenger_*.py`; all derive from the
  SMS client and share contact/conversation logic)
- Network aggregator (`programs/network_apps.py`) **(list of messengers that
  can be launched directly from the container window)**
- GPS module (`programs/gps.py`) **(positioning stub integrated with NavigationPanel)**

> **Палітра та кольори.** Усі програми не присвоюють фіксовані кольори в
> QSS. Натомість вони використовують `apply_lcars_style()` для застосування
> тільки загальних фонів/шрифтів, а конкретні кольори генеруються алгоритмами
> у `LCARSButton`/`COLOR_MANAGER` згідно з обраною ерою/фракцією. Це стандартний
> механізм: зміна ери в конфігурації впливає на всі компоненти, включаючи
> незалежні програми, без необхідності редагувати кожен стиль окремо.

- Star maps viewer (`programs/maps.py`)
- Weather viewer (`programs/weather.py`)
- Astronavigation tool (`programs/astro_nav.py`)
- Laboratory manager (`programs/lab_manager.py`)
- Physical modules interface (`programs/physical_modules.py`)
- Wi‑Fi scanner (`programs/wifi_scanner.py`)
- Cortex Agent (`programs/cortex_agent.py`) **(shows the embedded AI agent widget;
  useful for testing or as a panel component)**

> **Note:** CortexAgent is primarily a widget used within the UI (e.g. onboard
> or diagnostics panels).  A minimal standalone launcher exists above so the
> widget can be inspected independently.
- Internal browser wrapper (`programs/internal_browser.py`)


- Конструктор/дизайнер GUI
- Термінал / Шелл
- Медіапрогравач
- Нотатки / Блокнот
- Пошта / SMS-клієнт
- Інженерний калькулятор і Tricode Encoder
- Панель керування та екранна клавіатура

## Комунікації та навігація

Ключовий напрямок для розробки – повнофункціональні панелі/програми
зв'язку й навігації.  Кожна фракція повинна мати власний інтерфейс
(відповідно до її естетики та лінгвістичних особливостей):

- Мостик/панель Bridge зі статусом, тактичним оглядом, мережевою
  телеметрією (зараз реалізовано у `lcars/ui/panels/bridge.py`).
- Окрема панель Communications (`communication.py`) з логами, частотами,
  перекладом, імпульсами; планується розширити до SMS/EMail/чатів.
- Навігаційна панель (для містика та автономних скриншотів) із мапами,
  плануванням траєкторій, маркерами об’єктів та зв’язком з іншими модулями.

Потрібні внутрішні програми/толси в рамках комунікацій:

- **Записник / Бортові журнали** – зберігає текстові нотатки та логи.
- **SMS, e‑mail, внутрішня пошта** – всі тільки внутрішні, без зовнішнього
  інтернету.
- **Телефон/VoIP** – симуляція голосового зв'язку через мережу Titan.
- **Мережеві застосунки** – аналоги Facebook, Telegram, Viber, WhatsApp
  для внутрішньої соціальної мережі / чату.
- **Комунікатор** – standalone програма, повноцінний клієнт для всіх
  протоколів зв’язку; відрізняється від «додатка» тим, що має власні
  панелі та функціонал.
- **Внутрішній браузер** – вже в списку, але його слід інтегрувати з
  мережевими сервісами вище (відкривати внутрішні сайти/додатки).
- **База контактів** – спільна для всіх комунікаторів, з фільтрацією за
  фракціями/проектами.  Початковий модуль `lcars.modules.contact_db`
  вже реалізовано (SQLite), використовується в панелях Communication і
  Database, додаткові таблиці/поля можуть з’явитися пізніше.

> Примітка: більше половини згаданих програм зараз розглядаються як
> «толси» (легкі утиліти), але з часом вони мають вирости в повноцінні
> модулі з власними панелями.  Описано тут, щоб не забути план.

## Низький пріоритет / Інтеграції

- Обгортка для офісного пакету (тільки інтеграція)
- Встановлювач/інтеграція антивірусу (Avast) — лише сторонній пакет
- CI / Оркестратор збірки для важких збірок (Geant4)

## Примітки
- Усі згенеровані заготовки мінімальні й призначені як основа для розробки функціоналу.
- Реальні реалізації вимагатимуть UI-фреймворків (PyQt6/PySide6), інструментів збірки (для Geant4) та кроків для пакетування під платформи.

