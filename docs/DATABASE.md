# ◤ LCARS ISOLINEAR CHIP & DATABASE ARCHITECTURE 🖖
# =============================================================================
# ДОКУМЕНТАЦІЯ: docs/DATABASE.md
# ОПИС: Повна канонічна специфікація бази даних та ізолінійної оптичної мережі (ODN).
# СТАНДАРТ: Titanium Master (Чисті назви в одне слово, дефіси виключно для чіпів CC-NNNN).
# =============================================================================

## 1. Принцип роботи ODN (Optical Data Network)

Оптична шина даних ODN об'єднує всі ізолінійні чіпи та бази даних зорельота в єдину структуру. Кожен чіп монтується в слот стійки (Rack Slot) і містить ізольовану базу даних `.db` або YAML-карту конфігурації.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           LCARS CORE SYSTEM                             │
├─────────────────────────────────────────────────────────────────────────┤
│                             ODN BUS SYSTEM                              │
├─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────────────┤
│ 00-0000 │ 01-0000 │ 02-0000 │ 03-0000 │ 04-0000 │ 05-0000 │   06-0000   │
│ Kernel  │  Base   │Engineer │  Data   │   AI    │Security │    Comm     │
├─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────────────┤
│                       ISOLINEAR EXPANSION SLOTS                         │
│  00-0001   00-0004   00-0005   00-0020   02-0002   02-0010   02-0011    │
│  03-0001   03-0003   03-0010   03-0011   04-0020   04-0021   04-0022    │
│  05-0001   06-0002   06-0006   06-0020   07-0001   08-0001   09-0001    │
│  99-0001   99-9999                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Формат нумерації та правила назв чіпів

**Формат: `CC-NNNN`**
* `CC` — двозначний номер категорії (00–99).
* `NNNN` — чотиризначний номер слота в категорії (0000–9999).

> [!IMPORTANT]
> **Правило найменування Titanium:**
> 1. Нижнє підкреслення (`_`) **суворо заборонено** по всій системі.
> 2. Дефіс (`-`) дозволяється **виключно для серійних номерів та ідентифікаторів чіпів** (наприклад, `00-0004-odn-black-box.db`, `02-0010-telemetry.db`, `03-0010-starfleet-registry.db`).

---

## 3. Повний реєстр усіх категорій чіпів та баз даних

| Категорія | Призначення | Файли баз даних у `lcars/database/` | Системні компоненти |
|---|---|---|---|
| **00** | **System Kernel & Core** | `00/00-0001-bootstrap.db`<br>`00/00-0004-odn-black-box.db` *(Чорна скринька)*<br>`00/00-0005-system-state.db`<br>`00/00-0020-board-computer-manual.db` | `lcars/core/`, `lcars/system/` |
| **01** | **Base Framework** | `01/01-0001-signals.db`<br>`01/01-0004-types.db`<br>`01/01-0007-type-registry.db` | `lcars/base/` |
| **02** | **Engineering** | `02/02-0002-memory.db`<br>`02/02-0010-telemetry.db`<br>`02/02-0011-warp-dynamics.db` | `lcars/engineering/` |
| **03** | **Data Management & Starfleet** | `03/03-0001-shipsbook.db`<br>`03/03-0003-chronometer.db`<br>`03/03-0010-starfleet-registry.db`<br>`03/03-0011-federation-directives.db` | `lcars/database/`, `lcars/modules/` |
| **04** | **AI / Copilot Systems** | `04/04-0020-copilot-agent.db`<br>`04/04-0021-ai-providers.db`<br>`04/04-0022-agent-skills.db` | `lcars/modules/`, `lcars/skills/` |
| **05** | **Security & Access** | `05/05-0001-access-control.db`<br>`05/05-0002-encryption.db`<br>`05/05-0047-tactical-security.db` | `lcars/modules/`, `lcars/service/` |
| **06** | **Communication & Language** | `06/06-0002-learning.db`<br>`06/06-0006-english.db`<br>`06/06-0020-network-operations.db` | `lcars/modules/`, `lcars/themes/` |
| **07** | **Interface & Display** | `07/07-0001-themes.db`<br>`07/07-0002-audio.db` | `lcars/ui/`, `lcars/themes/` |
| **08** | **Storage & Virtual FS** | `08/08-0001-vfs-registry.db`<br>`08/08-0002-storage-adapters.db` | `lcars/system/environment.py` |
| **09** | **Simulation & Physics** | `09/09-0001-geant4-physics.db`<br>`09/09-0002-quantum-matrices.db` | `lcars/engineering/quantum_lab.py` |
| **10** | **IoT & Hardware Links** | Чіпи зв'язку з периферійними сенсорами | `lcars/modules/` |
| **11** | **Robotics & Android Matrix** | Позитронні нейромережі та сервоприводи | `lcars/modules/` |
| **12** | **Medical & Bio-Beds** | Біосканери та медичні картки екіпажу | `lcars/modules/` |
| **13** | **Navigation & Helm** | Зоряні карти та векторні курси польоту | `lcars/modules/` |
| **14** | **Tactical & Defenses** | Фазерні банки, торпеди та щити | `lcars/modules/` |
| **15** | **Transporters & Buffers** | Буфери квантових шаблонів матерії | `lcars/modules/` |
| **16** | **Replicators & Synthesis** | Молекулярні матриці синтезу предметів | `lcars/modules/` |
| **17** | **Holodeck Systems** | Матриці фотонного середовища | `lcars/modules/` |
| **18** | **Temporal Mechanics** | Хронометричні парадокси та часові поля | `lcars/service/chronometer.py` |
| **19** | **Stellar Cartography** | Квадранти (Alpha/Beta/Gamma/Delta) | `lcars/modules/` |
| **20** | **Tractor Beams** | Гравітонні випромінювачі | `lcars/modules/` |
| **99** | **Master BIOS & Recovery** | `99/99-9999-00-0001-bios-core.db`<br>`99/99-9999-network-operations.db` | `lcars/system/bios.py` |

---

## 4. Схеми основних таблиць у системних базах

### Категорія 00: Системне ядро, чорна скринька та стан
* **`00-0004-odn-black-box.db`**:
  * `odn_events (id, channel, sender, payload, stardate, timestamp)` — повний незмінний аудит-лог оптичної шини.
  * `bus_metrics (id, bandwidth_tbps, optical_latency_ps, active_conduits)` — швидкісні показники шини.
* **`00-0005-system-state.db`**:
  * `subsystem_states (id, subsystem, status, health, stardate, metadata_json)` — актуальний статус підсистем.
  * `alert_history (id, level, authorized_by, reason, stardate, timestamp)` — історія перемикання тривог.
* **`00-0020-board-computer-manual.db`**:
  * `system_manual (id, title, section, content, stardate)` — технічний посібник комп'ютера.
  * `voice_directives (keyword, action, response_template, security_level)` — голосові тригери.

### Категорія 02: Інженерні системи
* **`02-0010-telemetry.db`**:
  * `engineering_metrics (id, subsystem, parameter, value, unit, stardate, timestamp)` — телеметрія варп-ядра, EPS, дефлектора.
  * `diagnostic_logs (id, level, source, message, stardate)` — журнали діагностики.
* **`02-0011-warp-dynamics.db`**:
  * `warp_coils (coil_id, position, magnetic_confinement, status)` — параметри варп-котушок.
  * `subspace_geometries (field_shape, frequency_ghz, compression_ratio)` — геометрія поля.

### Категорія 03: Дані та Флот
* **`03-0001-shipsbook.db`**:
  * `captains_log (entry_id, stardate, officer, location, content, timestamp)` — журнал капітана.
* **`03-0003-chronometer.db`**:
  * `mission_events (id, event_type, title, stardate, earth_date, status, details)` — хронологія місії.
  * `scheduled_timers (id, name, duration_seconds, remaining_seconds, state, callback_signal)` — таймери.
* **`03-0010-starfleet-registry.db`**:
  * `starships (registry, name, ship_class, status, captain, max_warp, crew_complement)` — кораблі Федерації.
  * `ship_classes (class_name, role, length_meters, decks, primary_weapons)` — класи кораблів.
* **`03-0011-federation-directives.db`**:
  * `general_orders (order_number, name, summary, full_text, exception_clause)` — 24 директиви Зоряного Флоту.
  * `member_worlds (name, sector, quadrant, species, joined_year, status)` — світи Федерації.

---

## 5. Життєвий цикл чіпа в стійці ODN

```
[EMPTY] ──> [INSERTED] ──> [CONNECTED] ──> [ACTIVATED] ──> [RUNNING]
   ▲                                                           │
   └──────────── [EJECTED] <── [DEACTIVATED] <── [STOPPED] <───┘
```

