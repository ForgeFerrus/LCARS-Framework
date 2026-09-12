# LCARS Engineering Operations Center 🖖

Ласкаво просимо до інженерного сектору фреймворку. Цей вузол керує фізичною топологією зорельота, енергосистемою та цілісністю даних.


## 🛠 Ключові Системи

1. **[Drive](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/drive.py)**: Керує варп-ядром, імпульсними двигунами та розподілом енергії (Electro-Plasma System).
- **[Diagnostics](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/diagnostics.py)**: Регламентна перевірка всіх вузлів зорельота, Level 1-5 сканування.
- **[Transporter](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/transporter.py)**: Надійна система перенесення даних, файлів і записів між підсистемами. Відсутні try/except, всі сигнали мають fallback (NullSignal), модулі перевіряються через registry, типи параметрів суворо контролюються. Гарантована стабільність навіть при частково ініціалізованому середовищі.
- **[Turbolift](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/turbolift.py)**: Фізична навігація палубами та контроль доступу через ізолінійні вузли. Сигнали визначені через Signal, emit використовується коректно, типи параметрів перевірені. Відсутні try/except, код відповідає Titanium Standard.
3. **Telemetry (`telemetry.py`)**: Системний "Диспетчер задач". Всі інженерні дії реєструються тут.
4. **[Life Support & Autofix](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/life_support.py)**: Моніторинг стабільності ядра та автоматичний ремонт пошкоджених структур.
- **[Deflector](file:///c:/Users/Forge/MyProject/LCARS-Framework/lcars/engineering/deflector.py)**: Системна безпека, щити та антивірусний скан.

*(Сенсори як джерело даних винесено в шар модулів: `lcars/modules/sensory.py`)*

## 📊 Протокол "Задач" (Task Manager)

Відповідно до Titanium Standard, кожна інженерна операція повинна бути прозорою. Використовуйте `emit_telemetry` з відповідними префіксами:

- `PROCESS: NAME` — запуск тривалого процесу (напр. переміщення між палубами).
- `TASK: NAME` — реєстрація статичної системної задачі.
- `TASK_ID: X-000` — унікальний ідентифікатор для відстеження життєвого циклу.
- `TASK_REPORT` — проміжний звіт про виконання.
- `PROCESS_COMPLETE` — успішне завершення.
- `TASK_WARN` / `TASK_FAILED` — повідомлення про збої.

## 💾 'Журнал' (Telemetry DB)

Всі задачі зберігаються в ізолінійному чіпі `telemetry`. Це дозволяє відтворити хронологію інженерних подій навіть після системного збою.

- **Локація**: `lcars/database/iso_chip_04_telemetry.db`
- **Таблиця**: `telemetry` (timestamp, component, action, details)

## ⚖ Спадковість

Всі інженерні компоненти наслідують `SystemComponent` та використовують `Directive` для автономності від зовнішніх бібліотек (No Q Protocol).

---
*Статус інженерії: **ОПТИМАЛЬНИЙ**. Всі системи працюють на Titanium Standard.* 🇺🇦
