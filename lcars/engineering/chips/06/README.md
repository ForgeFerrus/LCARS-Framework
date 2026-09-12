# ◤ LCARS Communication Subsystem (06-xxxx)
## Комунікаційна підсистема — категорія 06

Повна документація ізолінійної архітектури: [plugin/chips/README.md](../README.md)

---

## Структура 06-категорії

### Нумерація чіпів 06-категорії (Communication)

| Чіп | Призначення | База даних | Функціонал |
|-----|-------------|------------|------------|
| **06-0002** | Core Communication | `06-0002-comm.db` | Базові функції: контакти, внутрішні повідомлення, дзвінки, TCP сервер |
| **06-0003** | Telegram Connector | `06-0003-telegram.db` | Інтеграція з Telegram Bot API |
| **06-0004** | WhatsApp Connector | `06-0004-whatsapp.db` | Інтеграція з WhatsApp Business API |
| **06-0005** | Viber Connector | `06-0005-viber.db` | Інтеграція з Viber Public Account API |
| **06-0006** | Email & SMS Gateway | `06-0006-email.db` | SMTP, Email, SMS через Twilio |
| **06-0007** | Meta Connector | `06-0007-meta.db` | Facebook Messenger, Instagram |
| **06-0008** | Twitter/X Connector | `06-0008-twitter.db` | Twitter API v2, Direct Messages |

### Принцип роботи

Кожен чіп — окремий плагін що монтується в ODN слот:
```
ODN Slot 1: 06-0002 (Core)     — базова комунікація
ODN Slot 2: 06-0003 (Telegram) — Telegram бот
ODN Slot 3: 06-0004 (WhatsApp)  — WhatsApp Business
...
```

### Залежності

- **06-0002** — базовий, без залежностей
- **06-0003 — 06-0008** — залежать від 06-0002 (Core) для збереження контактів

### Інтеграція

```python
# Приклад використання
from lcars.modules.comm import CommSubsystem
from lcars.engineering.isolinear import IsolinearChip, IsolinearSocket

# Монтуємо Core чіп
chip02 = IsolinearChip("06-0002", "06-0002-comm.db")
socket01 = IsolinearSocket("ODN-06", 1)
comm = CommSubsystem()
comm.mountChip(chip02, socket01)

# Монтуємо Telegram чіп
chip03 = IsolinearChip("06-0003", "06-0003-telegram.db")
socket02 = IsolinearSocket("ODN-06", 2)
comm.enableTelegram("BOT_TOKEN")
```

### Структура файлів

```
lcars/
├── modules/
│   ├── comm.py              # Core (06-0002)
│   ├── comm_telegram.py     # 06-0003
│   ├── comm_whatsapp.py     # 06-0004
│   ├── comm_viber.py        # 06-0005
│   ├── comm_email.py        # 06-0006
│   ├── comm_meta.py         # 06-0007
│   └── comm_twitter.py      # 06-0008
│
plugin/chips/06-0000/
├── 06-0002.yaml  # Core Communication
├── 06-0003.yaml  # Telegram
├── 06-0004.yaml  # WhatsApp
├── 06-0005.yaml  # Viber
├── 06-0006.yaml  # Email/SMS
├── 06-0007.yaml  # Meta
├── 06-0008.yaml  # Twitter
└── README.md     # Цей файл
```

### Архітектура даних

**06-0002 (Core):**
- Таблиця `contacts` — загальна адресна книга
- Таблиця `messages` — внутрішні LCARS повідомлення
- Таблиця `calls` — лог дзвінків

**06-0003 — 06-0008:**
- Таблиця `credentials` — API токени
- Таблиця `external_messages` — кеш зовнішніх повідомлень
- Таблиця `delivery_log` — лог відправки

### ODN Мережа комунікацій

```
┌─────────────────────────────────────────┐
│           LCARS Core System             │
├─────────────────────────────────────────┤
│  ODN Bus 06 (Communication Subsystem) │
├─────────┬─────────┬─────────┬──────────┤
│ 06-0002 │ 06-0003 │ 06-0004 │ 06-0005  │
│  Core   │Telegram │WhatsApp │  Viber   │
│         │         │         │          │
│ 06-0006 │ 06-0007 │ 06-0008 │ [empty]  │
│Email/SMS│  Meta   │ Twitter │          │
└─────────┴─────────┴─────────┴──────────┘
```

---
*LCARS Communication Subsystem v44.20*
*Дата створення: 2025*
*Стандарт: Isolinear Chip Architecture*)
