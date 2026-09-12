import sqlite3
from pathlib import Path

ROOT = Path(".")

# 1. 00-0020 Board Computer Manual
p00 = ROOT / "lcars" / "database" / "00" / "00-0020-board-computer-manual.db"
p00.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(p00) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS system_manual (id TEXT PRIMARY KEY, title TEXT, section TEXT, content TEXT, stardate TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS voice_directives (keyword TEXT PRIMARY KEY, action TEXT, response_template TEXT, security_level INTEGER)")
    
    manual_entries = [
        ("DOC-01", "Ініціалізація ядра LCARS 5.0", "CORE", "Послідовність запуску: 1. Реєстр секторів -> 2. Ядро -> 3. ODN BlackBox -> 4. Ізолінійні чіпи -> 5. BIOS POST -> 6. Сервісні канали -> 7. Мережевий аплінк.", "74205.1"),
        ("DOC-02", "Протоколи тактичних тривог", "TACTICAL", "Condition Red: підняття щитів, зарядка фазерних банків, квантові торпеди в стендбай. Condition Yellow: сканування на підвищеній чутливості. Condition Normal: штатний режим.", "74205.2"),
        ("DOC-03", "Синтез інтерфейсів на чіпи", "ISOLINEAR", "Автоматичний синтез інтерфейсів генерує LCARS-панелі на чіпи 05-0047 (Tactical), 05-0048 (Engineering), 05-0049 (Science).", "74205.3"),
        ("DOC-04", "Агентний шар Copilot", "AI", "Copilot здійснює оркестрацію мислення, завантажує навички з каталогу skills/ та маршрутизує запити до AIProviderManager.", "74205.4"),
    ]
    c.executemany("INSERT OR REPLACE INTO system_manual VALUES (?,?,?,?,?)", manual_entries)
    
    directives = [
        ("red alert", "SetAlert(RED)", "LCARS COMPUTER: CONDITION RED ACTIVATED. ALL STATIONS TO TACTICAL ALERT.", 3),
        ("yellow alert", "SetAlert(YELLOW)", "LCARS COMPUTER: CONDITION YELLOW ACTIVATED.", 2),
        ("cancel alert", "SetAlert(NORMAL)", "LCARS COMPUTER: TACTICAL ALERT CANCELLED.", 1),
        ("synthesize tactical", "SynthesizeSubsystemUI(tactical, 05-0047)", "TACTICAL INTERFACE SYNTHESIZED ON CHIP 05-0047.", 2),
        ("synthesize engineering", "SynthesizeSubsystemUI(engineering, 05-0048)", "ENGINEERING INTERFACE SYNTHESIZED ON CHIP 05-0048.", 2),
        ("status", "SystemSummary()", "LCARS QUANTUM CORE NOMINAL.", 1),
    ]
    c.executemany("INSERT OR REPLACE INTO voice_directives VALUES (?,?,?,?)", directives)
    conn.commit()
print("[OK] 00-0020-board-computer-manual.db")

# 2. 04-0020 Copilot Agent DB
p04_20 = ROOT / "lcars" / "database" / "04" / "04-0020-copilot-agent.db"
p04_20.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(p04_20) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS agent_state (agent_id TEXT PRIMARY KEY, name TEXT, mode TEXT, turns INTEGER, created_at TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS agent_tools (name TEXT PRIMARY KEY, description TEXT, parameters TEXT, target_subsystem TEXT)")
    
    c.execute("INSERT OR REPLACE INTO agent_state VALUES (?,?,?,?,?)", 
              ("LCARS-AGENT-PRIMARY", "LCARS Development Copilot", "ACTIVE", 0, "2026-08-22T00:00:00Z"))
    
    tools = [
        ("set_alert", "Зміна тактичного рівня тривоги корабля", '{"level": "RED / YELLOW / NORMAL"}', "Tactical/AlertSystem"),
        ("synthesize_ui", "Синтез панелі інтерфейсу на ізолінійний чіп", '{"subsystem": "tactical / engineering / science", "chip_id": "string"}', "Engineering/Isolinear"),
        ("system_summary", "Отримання зведеного звіту стану зорельота", "{}", "BoardComputer/Diagnostics"),
        ("get_stardate", "Розрахунок поточної зоряної дати Федерації", "{}", "System/Chronology"),
        ("process_directive", "Виконання команди в ядрі комп'ютера", '{"text": "string"}', "BoardComputer/VoiceEngine"),
    ]
    c.executemany("INSERT OR REPLACE INTO agent_tools VALUES (?,?,?,?)", tools)
    conn.commit()
print("[OK] 04-0020-copilot-agent.db")

# 3. 04-0021 AI Providers DB
p04_21 = ROOT / "lcars" / "database" / "04" / "04-0021-ai-providers.db"
with sqlite3.connect(p04_21) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS ai_providers (name TEXT PRIMARY KEY, bridge_key TEXT, default_model TEXT, model_type TEXT, description TEXT)")
    providers = [
        ("qvac", "Bridge.AI.Provider.QVAC", "meta-llama/Llama-3.2-1B-Instruct", "LOCAL_NEURAL_RPC", "Власний локальний бекенд Нова/QVAC SDK"),
        ("localllm", "Bridge.AI.Model.Transformers", "Qwen/Qwen2.5-0.5B-Instruct", "LOCAL_TRANSFORMERS", "Локальні моделі Gemma/Qwen/TinyLlama на CPU/GPU"),
        ("groqwen", "Bridge.AI.Provider.Groq", "qwen-2.5-32b", "CLOUD_LPUS", "Надшвидкий Groq хмарний рушій з великими моделями Qwen"),
        ("mistral", "Bridge.AI.Provider.Mistral", "codestral-latest", "CLOUD_MISTRAL", "Спеціалізовані моделі Mistral Codestral для кодингу"),
        ("gemini-cli", "System.CLI", "gemini-cli", "CLI_FALLBACK", "Локальний агентний CLI інструментарій"),
    ]
    c.executemany("INSERT OR REPLACE INTO ai_providers VALUES (?,?,?,?,?)", providers)
    conn.commit()
print("[OK] 04-0021-ai-providers.db")

# 4. 04-0022 Agent Skills DB
p04_22 = ROOT / "lcars" / "database" / "04" / "04-0022-agent-skills.db"
with sqlite3.connect(p04_22) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS skills_registry (name TEXT PRIMARY KEY, triggers TEXT, category TEXT, file_path TEXT, description TEXT)")
    skills = [
        ("agent-builder", "/agent-builder", "DEVELOPMENT", "lcars/skills/agent-builder.md", "Створення та налаштування агентів"),
        ("code-review", "/review,/code-review", "QUALITY", "lcars/skills/code-review.md", "Автоматизоване рев'ю коду за стандартами Titanium"),
        ("default-tools", "/tools,/default-tools", "INFRASTRUCTURE", "lcars/skills/default-tools.md", "Базові інструменти та файлові операції"),
        ("security", "/sec,/security", "SECURITY", "lcars/skills/security.md", "Перевірка безпеки та дозволів доступу"),
        ("fix_test", "/fix-test,/test", "TESTING", "lcars/skills/fix_test.md", "Діагностика та виправлення тестів"),
    ]
    c.executemany("INSERT OR REPLACE INTO skills_registry VALUES (?,?,?,?,?)", skills)
    conn.commit()
print("[OK] 04-0022-agent-skills.db")

# 5. 03-0010 Starfleet Registry DB
p03_10 = ROOT / "lcars" / "database" / "03" / "03-0010-starfleet-registry.db"
p03_10.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(p03_10) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS starships (registry TEXT PRIMARY KEY, name TEXT, ship_class TEXT, status TEXT, captain TEXT, max_warp REAL, crew_complement INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS ship_classes (class_name TEXT PRIMARY KEY, role TEXT, length_meters REAL, decks INTEGER, primary_weapons TEXT)")
    
    starships = [
        ("NCC-74205", "USS Sovereign Core", "Sovereign", "ACTIVE", "Captain LCARS", 9.975, 855),
        ("NCC-1701-E", "USS Enterprise-E", "Sovereign", "ACTIVE", "Jean-Luc Picard", 9.985, 855),
        ("NX-74205", "USS Defiant", "Defiant", "ACTIVE", "Benjamin Sisko", 9.982, 50),
        ("NCC-74656", "USS Voyager", "Intrepid", "ACTIVE", "Kathryn Janeway", 9.975, 140),
        ("NCC-74913", "USS Prometheus", "Prometheus", "ACTIVE", "Classified", 9.99, 175),
    ]
    c.executemany("INSERT OR REPLACE INTO starships VALUES (?,?,?,?,?,?,?)", starships)
    
    classes = [
        ("Sovereign", "Heavy Cruiser / Flagship", 685.0, 24, "Type XII Phasers, Quantum Torpedoes"),
        ("Defiant", "Tactical Escort / Warship", 170.0, 4, "Pulse Phaser Cannons, Quantum Torpedoes"),
        ("Intrepid", "Long-Range Science Vessel", 344.0, 15, "Type X Phasers, Photon Torpedoes, Bio-neural Gel Packs"),
        ("Prometheus", "Advanced Tactical Cruiser / MVAM", 415.0, 15, "Multi-Vector Assault Mode, Regenerative Shields"),
        ("Galaxy", "Explorer / Diplomatic Heavy Cruiser", 642.0, 42, "Type X Phasers, Photon Torpedoes"),
    ]
    c.executemany("INSERT OR REPLACE INTO ship_classes VALUES (?,?,?,?,?)", classes)
    conn.commit()
print("[OK] 03-0010-starfleet-registry.db")

# 6. 03-0011 Federation Directives DB
p03_11 = ROOT / "lcars" / "database" / "03" / "03-0011-federation-directives.db"
with sqlite3.connect(p03_11) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS general_orders (order_number INTEGER PRIMARY KEY, name TEXT, summary TEXT, full_text TEXT, exception_clause TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS member_worlds (name TEXT PRIMARY KEY, sector TEXT, quadrant TEXT, species TEXT, joined_year INTEGER, status TEXT)")
    
    orders = [
        (1, "Prime Directive", "Заборона втручання у природний розвиток цивілізацій", "Жоден зореліт чи офіцер Зоряного Флоту не має права втручатися у природний соціальний або технологічний розвиток недоварпових цивілізацій.", "Немає винятків (крім збереження виду від повного вимирання за спеціальним наказом)."),
        (24, "General Order 24", "Наказ про повне знищення поверхні ворожої планети", "Наказ капітану на знищення всіх штучних об'єктів та поверхні ворожого світу при критичній загрозі Федерації.", "Виключно за прямою командою або відсутності зв'язку з Командуванням."),
        (12, "Tactical Protocol 12", "Захист комунікацій при зустрічі з невідомим ворогом", "Під час першого контакту з ворожими намірами негайно закрити субпросторові канали до захищених частот.", "Діє автоматично при Condition Yellow."),
    ]
    c.executemany("INSERT OR REPLACE INTO general_orders VALUES (?,?,?,?,?)", orders)
    
    worlds = [
        ("Earth (Terra)", "Sector 001", "Alpha", "Human", 2161, "Founding Member / Capital"),
        ("Vulcan (Ni'Var)", "Sector 004", "Alpha", "Vulcan", 2161, "Founding Member"),
        ("Andoria", "Sector 002", "Alpha", "Andorian", 2161, "Founding Member"),
        ("Tellar Prime", "Sector 003", "Alpha", "Tellarite", 2161, "Founding Member"),
        ("Bajor", "Sector Bajoran", "Alpha", "Bajoran", 2375, "Full Member"),
        ("Betazed", "Sector 079", "Beta", "Betazoid", 2273, "Member World"),
    ]
    c.executemany("INSERT OR REPLACE INTO member_worlds VALUES (?,?,?,?,?,?)", worlds)
    conn.commit()
print("[OK] 03-0011-federation-directives.db")

# 7. 06-0020 Network Operations DB
p06_20 = ROOT / "lcars" / "database" / "06" / "06-0020-network-operations.db"
p06_20.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(p06_20) as conn:
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS allowed_endpoints (domain TEXT PRIMARY KEY, protocol TEXT, purpose TEXT, tls_required BOOLEAN)")
    c.execute("CREATE TABLE IF NOT EXISTS subspace_relays (relay_id TEXT PRIMARY KEY, sector TEXT, frequency_ghz REAL, status TEXT, bandwidth_pbps REAL)")
    
    endpoints = [
        ("google.com", "HTTPS/TLS1.3", "Search and AI API Uplink", 1),
        ("startpage.com", "HTTPS/TLS1.3", "Privacy-Focused Search Gateway", 1),
        ("api.groq.com", "HTTPS/TLS1.3", "Groq Neural Hardware Cloud", 1),
        ("api.mistral.ai", "HTTPS/TLS1.3", "Mistral AI Engineering Core", 1),
        ("starfleet.federation.int", "SubspaceCarrier/ODNv3", "Starfleet Secure Relay", 1),
    ]
    c.executemany("INSERT OR REPLACE INTO allowed_endpoints VALUES (?,?,?,?)", endpoints)
    
    relays = [
        ("RELAY-001-SOL", "Sector 001", 47.85, "ONLINE", 1200.0),
        ("RELAY-047-DEEP", "Sector 047", 94.20, "ONLINE", 850.0),
        ("RELAY-104-BAJOR", "Bajoran Sector", 12.45, "ONLINE", 600.0),
    ]
    c.executemany("INSERT OR REPLACE INTO subspace_relays VALUES (?,?,?,?,?)", relays)
    conn.commit()
print("[OK] 06-0020-network-operations.db")

