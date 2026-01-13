
# LCARS Framework — Enterprise Edition

## Огляд
LCARS Framework — це модульна система для керування Geant4-проєктами, аналізу даних і моніторингу, з підтримкою кількох інтерфейсів у стилі Star Trek.

**Основні компоненти:**
- `lcars/` — ядро, інтерфейси, утиліти, теми
- `plugins/` — розширення (приклад: `detector_control`)
- `config/` — налаштування (JSON/YAML)
- `docs/` — developer guide, архітектура, коротка довідка
- `tests/` — тестовий набір (unittest)
- `archive/` — усе застаріле, дублікати, службові, демо-файли

## Швидкий старт

1. Встановіть Python 3.9+
2. Встановіть залежності:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустіть:
   - **Windows:** `start_lcars.bat` — одразу відкриває графічний лаунчер вибору інтерфейсу (без консолі)
   - **Python (ручний режим):** `python start_lcars.py` — консольне меню (лише для тесту/відладки)

## Основна структура
```
lcars/
├── core/         # Ядро: event_bus, plugin_system, config_manager, ...
├── ui/           # Інтерфейси: LCARS_22nd-25th, TCARS_29th, PCARS, Romulan, Klingon
├── utils/        # Утиліти, логування
├── themes/       # Теми, палітри
plugins/
└── detector_control/  # Приклад сучасного плагіна
config/           # Конфігурації
docs/             # Developer Guide, архітектура, коротка довідка
tests/            # Тести (unittest)
archive/          # Застаріле, службове, демо
```

## Інтерфейси
- **LCARS**: 22nd, 23rd, 24th (TNG), 25th століття
- **TCARS**: 29th століття
- **PCARS**: 22nd, 23rd століття
- **Romulan, Klingon**: альтернативні стилі

## Плагіни
- Динамічна система плагінів (див. `plugins/detector_control/`)
- Приклад: `detector_control_plugin.py`, `plugin.yaml`
- Додайте власний плагін за шаблоном (див. developer guide)

## Документація
- `docs/README.md` — developer guide (розширення, плагіни, вкладки, тестування)
- `docs/ARCHITECTURE.md`, `docs/README_CONCISE.md` — архітектура, коротка довідка
- `PHASE_1_COMPLETE.py` — підсумковий звіт (успішно завершено)
- Всі застарілі/повні документи — в archive/

## Тестування
- Тести у `tests/` (unittest)
- Запуск: `python -m unittest discover tests`

## Залежності
- PyQt6, numpy, pandas, matplotlib, psutil, PyYAML, vispy, PyOpenGL, python-dotenv
- Повний список — у `requirements.txt`

## Додатково
- Логування: `logs/`
- Автозапуск: додайте ярлик `start_lcars.bat` у папку автозавантаження Windows (`shell:startup`)
- Діагностика: `health_check.bat`
- Оновлення: `pip install --upgrade -r requirements.txt`

---
**Версія:** 1.0+  
**Оновлено:** 27 листопада 2025  
*LCARS Framework — Enterprise Edition*