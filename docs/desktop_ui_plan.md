
- **Мета:** Повноекранний безрамковий десктоп у стилі LCARS, який відкриває основні робочі процеси (операції з проєктами, аналітика, термінал, файловий менеджер, меню Пуск) і залишається стійким при частковому відновленні або відсутності опційних залежностей.
- **Основний UX-потік:** Блокування/авторизація → Mission Hub / Меню Пуск → Відкриття додатків (Operations, Analytics, Terminal, File Manager) → Системні дії (Вимкнення, Блокування, Вихід).

**Ключові компоненти**

- ✅ **Mission Hub / Welcome:** центральна панель, швидкий доступ до `Start Menu`, годинник/stardate, індикатор стану. (корпус реалізовано, кнопки працюють)
- ✅ **Start Menu:** список додатків, пошук, ярлики до `Operations`, `Analytics`, `Terminal`, `File Manager`, `Settings`. (пункт меню з робочими кнопками; плагіни підписуються)
- 🔶 **Operations Panel (`OperationsWidget`):** виявлення проєктів, автоматизація збірки/запуску, лог термінала, кнопки `REFRESH`. (механізм викликів готовий, UI є, бекенд потребує наповнення)
- 🔶 **Terminal (`LCARSTerminalWidget`):** виконання shell-команд, читач stdout у окремому потоці, робоча директорія на рівні проєкту. (ми вже маємо інтеграцію у лаунчер та десктоп, але панель не повністю сучасна)
- ⚪ **File Manager:** дерево файлів, відкрити у ОС, контекстні дії (копіювати, перемістити, показати) — у разі відсутності модулю можливий зовнішній або простий fallback. (ще не створено, план)
- ✅ **Settings & Logs:** легкий модуль налаштувань і перегляду логів для швидкого усунення проблем. (реалізовано SystemControlCenter та механізм зміни мови/епохи/фракції)

**Дизайн і принципи взаємодії**

*(реалізовано безрамковість, ера‑палітра, прогресивне покращення, клавіатурні шоти та неблокуючий I/O – основні механізми вже працюють)*

- **Безрамковий, повноекранний:** `LCARSDesktop` запускається без стандартної рамки, елементи керування — у стилі LCARS.
- **Ера-орієнтована палітра:** використовувати палітри з `lcars.themes.lcars_palette`; за потреби анімація кольорів.
- **Прогресивне поліпшення / graceful degradation:** віджети опціональні; десктоп повинен стартувати навіть при відсутності шрифтів або модулів.
- **Керування клавіатурою:** швидкі клавіші (Alt+S — Start Menu, Alt+O — Operations, Alt+T — Terminal).
- **Неблокуючий I/O:** довготривалі задачі виконуються у фонових потоках та передають вивід у UI через черги або сигнали.

**Фолбеки та відновлення**

*(увімкнений повільний graceful degradation: опціональні імпорти, повідомлення про відсутність, відмови не зупиняють старт)*

- Якщо імпорт віджета падає — показувати плейсхолдер із коротким описом, кнопкою `REFRESH` та посиланням на `docs/desktop_ui_plan.md`.
- Якщо шрифти/ресурси відсутні — використовувати системні шрифти; `get_lcars_font_style()` має забезпечити консистентні розміри.
- Обгортати опціональні імпорти в `try/except` (вже застосовано в `lcars.modules.__init__`).

**Тестування**

- ✅ Юніт‑тести для `ProjectManager.get_all_projects()` та `TaskExecutor.execute_command()` (деякі вже існують).
- ✅ Додано тести для теми/локалізації/lock screen у `tests/test_desktop_theme.py`.
- 🔶 Headless smoke‑тести: запуск `start.py` з моками – частково працюють, але інші модулі викликають помилки при відсутності залежностей.

**Наступні кроки (суто практично)**

1. ⚪ Відновити/реалізувати `FileManager` та `StartMenu` (або плейсхолдери).  
2. 🔶 Інтегрувати `TaskExecutor` з `OperationsWidget` і протестувати build/run на прикладі проєкту.  
3. ✅ Додати клавіатурні шорткати та опції доступності (базові гарячі клавіші вже працюють).  
4. ✅ Провести візуальну та функціональну перевірку; виправити залишкові імпорт/рантайм помилки (більшість вже закрито).  
5. ✅ Прибрати тимчасові шими і закомітити зміни в recovery-гілку.

---
**Рекомендована папкова структура (детально)**
**Місії / Проєкти — дані та архіви (структура і процеси)**

- Організація: місії/проєкти зберігаються окремо від коду; кожен проєкт має метадані, файлове сховище і історію (версії/знімки).
- Файлова структура (рекомендовано):
	- `data/projects/` — робочі дані проєктів (папки per‑project)
	- `data/archive/` — заархівовані/знімкові образи проєктів
	- `lcars/db/` — БД проєктів (metadata, users, permissions, history)
	- `docs/projects/` — проєктна документація, design notes, runbooks

- Модель даних і метадані: для кожного проєкту зберігати `id`, `name`, `owner`, `tags`, `created_at`, `updated_at`, `version`, `artifacts` (список файлів з хешами), `policy` (retention/encryption)

- Збереження файлів і версій: файли мають бути версіоновані (snapshot per release) або зберігатися з хешем; великі дані можуть зберігатися на зовнішньому сховищі (S3/NAS) з посиланням у БД.

- Архівування і політики: інструменти для ingest → snapshot → archive; політики зберігання (retention), шифрування at‑rest, можливість відновлення через UI.

- Бекапи та знімки: регулярні резервні копії БД і критичних файлів; знімки проєктів для швидкого відкату/відновлення.

- Пошук і індексація: індексувати метадані та лог‑артефакти для швидкого пошуку (elastic/SQLite FTS для локальних інсталяцій).

- API та інструменти: REST/gRPC API для CRUD операцій з проєктами, експорту/імпорту, тригерів архівації та інтеграції з `TaskExecutor`.

- UI: Dashboard проєкту з переглядом метаданих, історії, знімків, логів і кнопками `Archive`, `Restore`, `Export`, `Snapshot`.

- Безпека: проектні дані мають налаштування доступу (project‑RBAC), шифрування at‑rest за потреби, audit‑лог усіх операцій із проєктом.

- Інтеграція з центральним командуванням: дозволити оркестрування задач (масові build/deploy), тригерити playbook для staged rollout або recovery через broker/agents.

 Далі: розбити роботу на конкретні підзадачі (schema design, DB implementation, storage adapters, UI components, backup jobs). Це додано у TODO як окрема група задач.

**Бортовий комп'ютер та Робоче місце розробника (Developer Workbench)**

Коротко: інтегруємо бортовий комп'ютер як внутрішній сервіс/agent у систему та будуємо повноцінний робочий стіл розробника, де код, UI і дизайн синхронізуються в реальному часі.

Ключові вимоги:
- Бортовий комп'ютер (`onboard computer`) — локальний agent/service, що надає API для апаратних інтерфейсів, журналів, телеметрії і підписаних результатів. Має RBAC, attestation та підписування важливих артефактів.
- Developer Workbench — окремий робочий стіл/панель у LCARS, що містить: файловий провідник проекту, live‑editor, constructor (visual builder), preview панель (живий UI), console/terminal, task runner і debug tools.
- Live preview: код, який ви редагуєте в `Edit` або який експортує `Constructor`, має одразу (або після швидкого reload) відображатися у preview; зміни можна зберегти як runnable‑артефакт.
- Code generation: `Edit` і `Constructor` мають експортувати чистий код (наприклад Python + PyQt6) за визначеним контрактом; зворотна інтеграція — зміни у коді мають бути відображені в дизайнері, коли це можливо.
- Безпека: будь‑яке виконання коду у середовищі розробника запускається в sandbox або в окремому процесі з обмеженими правами; апаратні дії вимагають підтвердження і перевірки attestation.
- Інтерактивність: CLI/console команд в `Terminal` викликають TaskExecutor; їхні результати логуються в бортовому журналі і Journal проекту.

Параметри реалізації (фази):
1. Skeleton: створити `lcars/onboard/agent.py` (agent API stub) та `lcars/devworkbench/` з базовими панелями (editor, preview, terminal).
2. Live preview PoC: implement hot‑reload mechanism (execute preview in subprocess, communicate via websocket/IPC, show output in preview panel).
3. Code generator: implement exporter for constructor and editor to produce runnable module and register artifact in tri‑coder.
4. Sandbox & security: run preview & tasks in sandboxed environment; add RBAC checks for hardware access.
5. Tests & CI: E2E tests for edit→preview→save flow, and agent→task→journal flow.

UI expectations:
- Developer Workbench is accessible from Start Menu and Mission Hub.
- Constructor's save/export produces code tied to project and updates project Journal with version and artifact hash.
- Alerts and Mode Manager influence workbench: Dev mode enables hot reload and debug overlays; Normal mode enforces stricter sandbox.

Наступні кроки (пропозиція):
- Я можу створити скелет `lcars/onboard/agent.py` і базові панелі `lcars/devworkbench/` (editor, preview, terminal) і додати minimal E2E test harness. Робити це зараз?
 **Бортовий журнал, changelog і версії проєкту**

 - Призначення: зберігати хронологічні записи подій проєкту — дії інженерів, оновлення артефактів, реліз‑версії, результати build/deploy, важливі помітки й інциденти.
 - Формат записів: кожен запис має `id`, `project_id`, `timestamp`, `author`, `type` (note|update|release|incident), `message`, `meta` (структуровані дані: версія, artifacts, hash, task_id).
 - Changelog/версиї: для релізів зберігати `version`, `released_by`, `released_at`, `notes`, `artifacts` (з хешами), `rollback_instructions`.
 - Зв'язок з логами та аудитом: записи журналу мають посилання на audit entries та підписи результатів агентів; важливі події повинні бути дубльовані в audit trail з підписами (integrity).
 - UI: timeline view в dashboard проєкту з фільтрами (by type, author, date, version) та кнопками `Create entry`, `Annotate`, `Export`, `Attach artifact`.
 - API: REST/gRPC endpoints для CRUD журналу, генерації автоматичного changelog (збір записів по релізу) та експорту у форматі Markdown/JSON.
 - Автоматизація: інтеграція з CI/TaskExecutor для створення автоматичних записів при успішному build/deploy (включаючи артифакти і хеші). Генерація release notes на основі записів і PR/commit metadata.
 - Безпека: журнал має project‑level RBAC (хто може читати/писати), шифрування при зберіганні за потреби, і регулярні бекапи; retention policy для старих записів.
 - Архівування: можливість snapshot→archive журналу при архівації проєкту; restore із архіву з відновленням пов'язаної історії й версій.

 Додавання: це покриває requirement "записи бортовий журнал проекту, оновлень, версій" і інтегрується з уже запланованими модулями бази даних, архіву та UI.

**Лабораторні модулі та внутрішні програми (огляд)**

Мета: додати набір внутрішніх віджетів/програм для лабораторної роботи і аналізу, які працюють як частина LCARS‑середовища. Зовнішні інструменти можна підключати лише як опції/плагіни.

Основні модулі:
- `Physics` — симуляції, експерименти, візуалізації; інтеграція з локальними симуляторами; data logger.
- `Chemistry` — експериментальні робочі процеси, керування інструментами (симулятори або драйвери), реакції/рецепти, експериментальні записи.
- `Astronomy` — зоряні карти, епхемериди, планувальник спостережень, імпорт FITS/телескопних даних.
- `Navigation` — інструменти маршрутизації, waypoints, координатні перетворення, інтеграція з maps і комунікаціями.
- `Maps` — тайловий переглядач, шари (overlays), імпорт/експорт геоданих (GeoJSON), вимірювання відстаней.
- `Comms` — внутрішні канали зв'язку, логи з'єднань, management of radio links / virtual channels; можливість підключення зовнішніх SDR або network bridges як опція.

Вимоги та принципи реалізації:
- Усі модулі — як внутрішні віджети/програми з lifecycle hooks; деякі можуть бути висувними (detachable) або pop‑out вікнами.
- За замовчуванням використовувати внутрішні/simulated backends; зовнішні драйвери повинні бути опціональними і вмикатися явно у налаштуваннях з перевіркою дозволів.
- Дані експериментів зберігаються у `data/projects/<project_id>/lab/` з версіонуванням, journal‑записами та метаданими.
- Інтеграція з `TaskExecutor`, telemetry і journal: автоматичні записи при запуску симуляцій та завершенні задач.
- Безпека: sandbox для коду/скриптів, перевірка прав доступу і ретельна валідація вхідних даних; обмеження доступу до апаратних інтерфейсів.

UI/UX вимоги:
- Можливість швидкого виклику модулів з Start Menu або Mission Hub.
- Pop‑out panels для робочого простору інженера (drag/drop, resize, persist layout via Constructor).
- Alerts і priority routing: лабораторні модулі повинні отримувати і відправляти глобальні Alerts (жовтий/червоний режими показують стан і дають priority notifications), без руйнівних дій.

Документація та навчання:
- Для кожного модуля створити operator guide, safety notes, example experiments, і quick start. Ці документи — у `docs/lab/`.

Далі: розбити кожен модуль на підзадачі (API, storage, widget, backend, security) і додати у TODO‑список (виконано).

Щоб мати зрозумілу організацію для прошивок, платформених скриптів, системних налаштувань LCARS і апаратної частини (ізолінійна система чіпів), запропоную таку структуру в корені проекту (створювати під `platform/` або `lcars/system/`):
	- `bios/`
		- `README.md`  # інструкції, застереження
		- `bios-profiles/`
			- `default_bios.yaml`
			- `secure_server_bios.yaml`
		- `tools/`
			- `flash_bios.bat`
			- `flash_bios.ps1`
		- `vendor/`  # notes, vendor wrappers
	- `uefi/`
		- `README.md`
		- `uefi-profiles/`
			- `default_uefi.yaml`
			- `dev_uefi.yaml`
		- `scripts/`
			- `set_uefi_vars.sh`
			- `create_uefi_capsule.py`
		- `keys/`
			- `README.md`
			- `generate_keys.sh`

- `lcars/`
	- `system/`
		- `README.md`
		- `system.yaml`  # hostname, timezone, ntp, boot flow
		- `hardware_policy.yaml`  # TPM, virtualization, secure elements
		- `boot_flow.md`
	- `config/`
		- `ui_theme.yaml`
		- `services.yaml`  # event_bus, task_executor, plugins
	- `security/`
		- `README.md`  # policy for secrets, store examples only
		- `keys/` (ignored)  # do not commit private keys
		- `secrets.example.env`

- `hw/`  # апаратний блок (ізолінійна система чіпів)
	- `specs/`
		- `isoline-system.md`  # архітектура, цілі, інтерфейси
		- `components.md`  # Secure Enclave, Attestation, Fabric
	- `schematics/`
		- `block_diagram.svg`
		- `power_domains.svg`
	- `rtl/`
		- `isoline_top.v`  # приклад top-level Verilog
		- `isoline_bus.v`
	- `fpga/`
		- `README.md`
		- `sim/`  # testbenches, tb_isoline_top.v

- `tools/`
	- `validate_configs.py`  # YAML schema validation
	- `generate_diagram.py`  # helper для SVG/PNG

- `docs/`
	- `security_model.md`
	- `deployment.md`  # playbook: BIOS → UEFI → LCARS
	- `testing.md`  # test plans for firmware and hw

 **Стислий план реалізації (послідовно, без прикладів)**

1. Режими (основні):
	- `Lock` — екран блокування/авторизація.
	- `Normal` — звичайний десктоп, доступ до додатків.
	- `Edit` — режим правки контенту/налаштувань.
	- `Constructor` — візуальний конструктор/маппер UI (збереження/завантаження макетів).
	- `Dev` — розробницький режим з додатковими інструментами і логами.

2. Глобальні сервіси (мають бути активні з початку):
	- Глобальна система Alert (broadcast + per-widget routing).
	- Mode‑State Manager (уніфікований стан режиму, кнопка `Mode`).
	- EventBus / Command Bus для внутрішнього обміну повідомленнями.

3. UI-компоненти і життєвий цикл додатків (послідовність):
	- Start Menu / Mission Hub (швидкий доступ, виклик команд).
	- Operations, Analytics, Terminal, FileManager — кожен як окремий модуль з lifecycle hooks (init, pause, resume, shutdown).
	- Edit tool (вбудований редактор): редагування тексту/конфігів/макетів.
	- Constructor (builder): drag‑drop макети, збереження у форматі проекту.

4. Налаштування середовища розробки і теми:
	- Dev Environment selector (локально / container / remote).
	- Era chooser (theme/era selection) — впливає на палітру й шрифти.

5. Безпека, авторизація та аудит:
	- RBAC + інтеграція з PKI/TPM для критичних команд.
	- Telemetry + Audit Trail (всі команди і результати логуються, підписи там де треба).

6. Оновлення і відновлення:
	- Подпісані артефакти (firmware/updates) + staged rollout playbooks.
	- Recovery/rollback playbooks і образ for recovery USB.

7. CI, тести і верифікація:
	- Unit tests, smoke tests для `start.py` та модулів.
	- RTL sim & HW testbenches (для isoline), reproducible builds.

8. Операційні вимоги і інструменти:
	- Flash/UEFI wrappers, key management scripts, secrets manager bridge.
	- Monitoring/heartbeat і alert routing до UI (повідомлення всюди).

9. Завершальні кроки перед релізом:
	- Видалення тимчасових шимів, інтеграція ресторованих файлів.
	- End‑to‑end перевірка запуску `start.py` → Lock → Desktop → Mission Control.
	- Закріплення recovery гілки і документування процеса відновлення.

Пріоритет на першій ітерації: забезпечити Alerts повсюди + Mode‑button/Mode‑State Manager → базовий Start Menu → плейсхолдери для `FileManager` і `Constructor` → smoke‑test запуску.

**Проблеми та обмеження (важливо)**

- Заборонені небезпечні функції: проект не включатиме або не реалізовуватиме функцій, що навмисно завдають шкоди людям, майну або інфраструктурі (наприклад «система самознищення»). Такі можливості заборонені з етичних, юридичних і безпекових причин.
- Alert‑режими: жовтий/червоний режими реалізуються як візуальні й поведінкові стани (зміна палітри, прискорення анімацій, пріоритетне маршрутизування повідомлень). Вони не ініціюють руйнівних дій; критичні операції виконуються лише через захищені playbook‑процеси.
- Відлік і скасування: таймери/відліки для критичних сценаріїв повинні мати явне підтвердження (дві форми підтвердження для критичних дій), audit‑лог і можливість скасування; автоматичне виконання руйнівних дій заборонене.
- Бортовий комп'ютер / agent: agent та broker мають контракт з RBAC, attestation (TPM) та підписуванням результатів. Критичні команди потребують dual‑approval і проходять staged rollout з dry‑run та rollback.

Додавання цього розділу у план фіксує обмеження та вимагає, щоб всі критичні механізми мали механізми захисту, логування й ручного підтвердження.

`platform/bios/bios-profiles/default_bios.yaml` (поля):
- boot_order: ["NVMe0","USB","PXE"]
- secure_boot: true
- tpm_enabled: true
- virtualization:
	vt-d: true
	svm: false
- csm: false

`platform/uefi/uefi-profiles/default_uefi.yaml` (поля):
- BootOrder: ["0001","0002"]
- SecureBoot: enabled
- Keys:
	PK: keys/PK.crt
	KEK: keys/KEK.crt
	db: keys/db.crt
- NVRAM_vars:
	BootTimeout: 2

`lcars/system/system.yaml` (поля):
- hostname: lcars-desktop
- timezone: Europe/Kiev
- ntp_servers: ["time.google.com"]
- ui:
	theme: default
	scale: 1.0

`hw/specs/isoline-system.md` — розділи:
- Мета та обґрунтування
- Компоненти: Secure Enclave, Isolation Fabric, Trust Monitor, Attestation Module
- Інтерфейси: AXI/PCIe/Memory DMA з контролем доступу
- Верифікація: testbenches, fault injection

**Безпека та операційні поради**
- Не комітити приватні ключі або прошивки у репозиторій; зберігати приклади у `secrets.example.env`.
- Використовувати `sops`/Vault для захищеного зберігання секретів.
- Наявність TPM 2.0 рекомендована; мати інструменти для програмування SPI BIOS та JTAG для апаратних модулів.
- Maйти rollback-план для оновлення прошивок (recovery image на USB).

**Що ще потрібно організувати**
- Вендор-утиліти для флешу BIOS
- Шаблони для UEFI capsule update
- CI для RTL симуляцій (Icarus/cocotb)
- Тестова плата (FPGA) та програматор
- Playbook оновлення прошивки та план відновлення

---

 **Desktop Overview**

- **Goal:** Provide a full-screen, frameless LCARS-style desktop shell that exposes core workflows (project operations, analytics, terminal, file manager, start menu) while remaining resilient to partial restores and missing optional dependencies.
- **Primary UX flow:** Lock/authorize → Mission Hub / Start Menu → Open apps (Operations, Analytics, Terminal, File Manager) → System actions (Shutdown, Lock, Logout).

**Core Components**

- **Mission Hub / Welcome:** central greeting, quick access to `Start Menu`, clock, stardate, status pill.
- **Start Menu:** app list, search, favorites, and shortcuts to `Operations`, `Analytics`, `Terminal`, `File Manager`, `Settings`.
- **Operations Panel (`OperationsWidget`):** project discovery, build/run automation, terminal log, `REFRESH`, `BUILD`, `RUN`, `OPEN FOLDER` actions.
- **Analytics Panel (`AnalyticsWidget`):** live system metrics (CPU, memory, I/O), visual bar-spectrum, status indicators, update timer.
- **Terminal (`LCARSTerminalWidget`):** shell command execution, threaded output reader, working directory per project.
- **File Manager:** navigable tree view, open in OS, context actions (copy, move, reveal) — can be an external system fallback if missing.
- **Settings & Logs:** lightweight settings panel and logs viewer for quick troubleshooting.

**Design & Interaction Principles**

- **Frameless, Fullscreen:** `LCARSDesktop` launches without native chrome, controls exposed via LCARS buttons.
- **Era-aware color system:** use `LCARS` era palettes from `lcars.themes.lcars_palette` and animate button colors when applicable.
- **Progressive enhancement / graceful degradation:** components should be optional; the desktop must start even if some modules or fonts are missing.
- **Keyboard-first controls:** provide shortcuts for primary actions (Alt+S = Start Menu, Alt+O = Operations, Alt+T = Terminal).
- **Non-blocking IO:** long-running tasks (build/run, shell commands) must run in background threads and push output into the UI via queues or signals.

**Fallback & Resilience Modes**

- If a widget import raises (missing file or dependency), show a placeholder page with: short explanation, `REFRESH` button, and a link to `docs/desktop_ui_plan.md` instructions for recovery.
- If fonts/resources unavailable, fall back to system fonts with `get_lcars_font_style()` providing consistent sizes.
- Wrap optional modules in `try/except` at import boundaries (already applied to `lcars.modules.__init__`).

**Accessibility & Testing**

- Ensure readable contrast ratios for each era palette; provide an accessibility settings toggle to increase font sizes.
- Produce unit tests for critical logic: `ProjectManager.get_all_projects()`, `TaskExecutor.execute_command()`, and terminal output handling.
- Visual smoke tests: run `start.py` headless with mocked widgets to verify no import-time failures; then run interactive checks for `Operations` build/run flow.

**Developer Notes & File Mapping**

- Desktop shell: `lcars/ui/desktop.py` — orchestrates layout and injection of widgets.
- Widgets: `lcars/ui/widgets/operations.py`, `analytics.py`, `terminal.py` — core app modules (restored).
- Theme helpers: `lcars/themes/lcars_palette.py` — palettes + `setup_lcars_font()` and `get_lcars_font_style()`.
- Startup: `start.py` — currently uses `LCARSWindowManager` to show lock or desktop.

**Next Steps (implementation order)**

1. Replace temporary shims with restored widget implementations (Operations, Analytics, Terminal) — DONE for core widgets.
2. Implement or restore `FileManager` and `StartMenu` (if missing), or provide graceful placeholders.
3. Integrate `TaskExecutor` output queue with `OperationsWidget` polling and test build/run with a sample project.
4. Add keyboard shortcuts and accessibility options.
5. Run visual and functional validation; fix remaining import/runtime errors.
6. Remove compatibility shims and commit the restored files to a recovery branch; prepare a cleaned history if requested.
```
File created as a working specification to guide restoration and UI polishing. Use this doc to assign implementation subtasks.