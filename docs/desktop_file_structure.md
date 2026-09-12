**Структура проєкту LCARS (ключові файли та плановані)**

Нижче — повний, впорядкований скелет файлової структури проєкту (існуючі файли залишаються; решту створимо як плейсхолдери за потреби). Вкажіть правки — я потім можу автоматично згенерувати ці файли.

start.py

requirements.txt

README.md

lcars

__init__.py
launcher.py
lcars_system.py
lcars_data
core/
__init__.py
project_manager.py
task_executor.py
storage_adapter.py
tricoder.py # artifact encoder/decoder
ui/
__init__.py
desktop.py
lock_screen.py
start_menu.py
devworkbench/
__init__.py
editor.py
preview.py
terminal_panel.py
workbench_layout.py
widgets/
__init__.py
operations.py
analytics.py
terminal.py
file_manager.py
settings.py
maps_widget.py
physics_widget.py
chemistry_widget.py
astronomy_widget.py
navigation_widget.py
comms_widget.py
themes/
__init__.py
lcars_palette.py
theme_presets.yaml
modules/
__init__.py
lock_screen.py (shim/wrapper)
onboard/
__init__.py
agent.py # local agent API & attestation
agent_cli.py
agent_service.py
storage/
__init__.py
tricoder.py
object_store.py
platform/

bios/
README.md
bios-profiles/
default_bios.yaml
secure_server_bios.yaml
tools
flash_bios.bat
flash_bios.ps1
uefi/
README.md
uefi-profiles/
default_uefi.yaml
scripts
set_uefi_vars.sh
create_uefi_capsule.py
keys/
README.md
generate_keys.sh
hw/

specs/
isoline-system.md
components.md
schematics/
block_diagram.svg
rtl/
isoline_top.v
isoline_bus.v
fpga/
README.md
sim/
tb_isoline_top.v
data

projects/ # per-project folders
archive
backups/
resources

lcars_assets/ (wallpapers, ui elements, fonts, icons)
fonts/
docs

desktop_ui_plan.md
desktop_file_structure.md
security_model.md
deployment.md
testing.md
lab/
physics_guide.md
chemistry_guide.md
astronomy_guide.md
navigation_guide.md
maps_guide.md
comms_guide.md
command_control.md
README_UI.md
tests

test_project_manager.py
test_task_executor.py
test_tricoder.py
e2e/
test_edit_preview_flow.py
scripts

repair_missing.py
build_release.py
generate_assets_index.py
tools

validate_configs.py
generate_thumbs.py
plugins

<plugin_name>/
__init__.py
plugin.yaml
main.py
lcars/security/

README.md
secrets.example.env
.gitignore (for real keys)
vault/ (instructions only — DO NOT COMMIT KEYS)
ci/

pipeline.yml
rtl_sim.yml
logs

audit.log
recovery.log
archive

GLOBAL_PLAN.md
Пропозиція далі:
---

**Існуючі / Відновлені (важливі)**

- `start.py` — точка входу, `LCARSWindowManager` (boot, lock, desktop).
- `lcars/__init__.py` — пакет.
- `lcars/ui/desktop.py` — основний shell `LCARSDesktop`.
- `lcars/ui/lock_screen.py` — сумісний wrapper до `lcars.modules.lock_screen`.
- `lcars/ui/widgets/operations.py` — відновлено (OperationsWidget).
- `lcars/ui/widgets/analytics.py` — відновлено (AnalyticsWidget).
- `lcars/ui/widgets/terminal.py` — відновлено (LCARSTerminalWidget).
- `lcars/themes/lcars_palette.py` — палітри, `setup_lcars_font()`, `get_lcars_font_style()`.
- `lcars/utils/__init__.py` — стабільний інтерфейс `setup_logging` + фолбеки.
- `lcars/modules/__init__.py` — обгортки імпортів (resilient imports).
- `lcars/system/loading.py` — `LCARSBoot` (shim/реальна реалізація).
- `lcars/core/project_manager.py` — керування виявленням проєктів (очікується).
- `lcars/core/task_executor.py` — виконання зовнішніх команд/черга виводу.

**Довідкова документація**

- `docs/desktop_ui_plan.md` — план UI (вже створено).
- `archive/GLOBAL_PLAN.md` — повний план (перекладено українською).

---

**Плановані / Рекомендовані файли для створення або відновлення**

1. `lcars/ui/widgets/file_manager.py` — `FileManagerWidget` (дерево файлів, контекстні дії).
2. `lcars/ui/start_menu.py` — `StartMenu` (пошук додатків, фаворити, ярлики).
3. `lcars/ui/widgets/settings.py` — налаштування (доступність, тема, шрифти).
4. `lcars/logs/RECOVERY_LOG.md` — журнал відновлення й змін (створити для трасування).
5. `tests/test_project_manager.py` — юніт-тести для `ProjectManager`.
6. `tests/test_task_executor.py` — тести для `TaskExecutor` (імітація команд).
7. `scripts/repair_missing.py` — утиліта для автоматичного відновлення/виявлення відсутніх файлів (за наявності бекопів).
8. `docs/README_UI.md` — короткий огляд інструкцій для дизайнерів/розробників UI.

---

**Файли/модулі, які слід перевірити чи доповнити**

- `lcars/core/__init__.py` — переконатися, що `ProjectManager` і `TaskExecutor` експортуються.
- `lcars/system/paths.py` — функції `get_project_root()` і шляхи, які використовують віджети.
- `requirements.txt` — містить `PyQt6`, `psutil`, інші залежності.

---

Рекомендація: спочатку створити/відновити `file_manager.py` і `start_menu.py` як прості плейсхолдери (інформативні сторінки з `REFRESH`), після чого зробити повний прогін `start.py` і поетапно виправляти помилки.

Файл створено для узгодження структури — якщо підтверджуєте, я реалізую плейсхолдери для `FileManager` і `StartMenu` і запущу повний прогін стартера.

---

**Структура папок — аналіз та план дій**

Нижче — детальний перелік папок у репозиторії з аналізом поточного стану та планованими діями.

- `lcars/` — основний пакет UI/логіки.
	- Статус: існує; ключові піддиректорії (`ui`, `core`, `themes`, `system`, `modules`) присутні частково.
	- План: завершити/перевірити `core` (`ProjectManager`, `TaskExecutor`), забезпечити чисті експорти у `lcars/core/__init__.py`.

- `lcars/ui/` — UI-компоненти.
	- Статус: `desktop.py`, `lock_screen.py`, `widgets/` частково відновлені.
	- План: додати `start_menu.py`, `file_manager.py`, `settings.py`; переконатися у сумісності стилів та імпортів.

- `lcars/ui/widgets/` — окремі віджети.
	- Статус: відновлено `operations.py`, `analytics.py`, `terminal.py`.
	- План: створити `file_manager.py`, `settings_widget.py`, і додати тести/приклади використання.

- `lcars/core/` — бізнес-логіка.
	- Статус: частково присутні файли (очікується `project_manager.py`, `task_executor.py`).
	- План: завершити реалізації, додати юніт-тести та mock-інтерфейси для headless-тестування.

- `lcars/themes/` — палітри та ресурси тем.
	- Статус: `lcars_palette.py` оновлено; ресурси (fonts/images) можуть бути відсутні.
	- План: перевірити наявність `resources/fonts`, додати fallback-логику та тест кольорів/контрасту.

- `lcars/system/` — системні допоміжні модулі.
	- Статус: наявний `loading.py`, `paths.py` частково.
	- План: завершити `paths.py` (єдина точка для `get_project_root()`), додати `env`/конфіг в `config/`.

- `plugins/` — плагіни.
	- Статус: існують шаблони; кілька плагінів можуть бути неповними.
	- План: документувати API плагіна, додати приклади плагінів та систему валідації `plugin.yaml`.

- `docs/` та `archive/` — документація і плани.
	- Статус: `docs/desktop_ui_plan.md`, `archive/GLOBAL_PLAN.md` перекладені.
	- План: синхронізувати `README.md`, додати короткий зміст у `docs/README_UI.md`.

- `tests/` — тести.
	- Статус: порожні або мінімальні.
	- План: додати тести для `ProjectManager` та `TaskExecutor`, CI-воркфлоу для запуску тестів.

- `scripts/` — утиліти.
	- Статус: є кілька утиліт; рекомендовано створити `repair_missing.py` і `auto_tasks.py` у `scripts/`.
	- План: написати скрипт для виявлення відсутніх файлів і відновлення з резервів або повідомлень.

---

Якщо підтверджуєте — реалізую прості плейсхолдери для `lcars/ui/start_menu.py` та `lcars/ui/widgets/file_manager.py`, потім запущу `start.py` і зафіксую список залишкових помилок для подальшої роботи.

*** End Patch
