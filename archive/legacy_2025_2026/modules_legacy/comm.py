# ◤ lcars/modules/comm.py — COMM SUBSYSTEM v44.20
# Центральна комунікаційна підсистема LCARS Framework.
# Керує контактами, повідомленнями та дзвінками через ізолінійну архітектуру.
# Підключена до ізолінійного чіпа 06-0002 через ODN Socket.
# Підтримує контекстне керування дзвінками через CallContext менеджер.
#
# Архітектура:
# - Isolinear Chip 06-0002 (Communication) → Socket ODN → CommSubsystem
# - Дані зберігаються в ізолінійній базі comm_isolinear.db
# - TCP/IP сервер для мережевої комунікації між вузлами LCARS
#
# Приклад використання:
#   from lcars.modules.comm import commsystem, Contact
#   contact = Contact(name="James Kirk", faction="Federation", email="kirk@enterprise")
#   commsystem.addcontact(contact)
#   with commsystem.call("kirk", "spock") as callid:
#       # Дзвінок автоматично логується в ізолінійній базі
#       pass
#
# Автор: LCARS Development Team
# Дата: 2025

import time
# Titanium Bridge Migration: import socket
# Titanium Bridge Migration: import threading
# Titanium Bridge Migration: from dataclasses import dataclass, field
# Titanium Bridge Migration: from typing import List, Optional, Dict, Callable, Any, Union
# Titanium Bridge Migration: from pathlib import Path
from lcars.engineering.isolinear import IsolinearChip, IsolinearSocket, ChipStatus
from lcars.modules.connector import (
    NetworkConnector, ExternalAPIManager, ExternalMessage,
    TelegramConnector, WhatsAppConnector, ViberConnector,
    MetaConnector, EmailConnector, SMSConnector, TwitterConnector
)

# Всі конектори та мережева інфраструктура для LCARS Comm System.
def Version() -> str:
    # Отримання версії комунікаційного модуля з базової системи
    from lcars.base.info import getVersion
    return getVersion()
# Клас даних: структура контакту з усіма полями для ідентифікації суб'єкта
@dataclass
class Contact:
    identifier: Optional[int] = None
    name: str = ""
    faction: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

# Клас даних: структура повідомлення для зберігання в базі даних
@dataclass
class Message:
    identifier: Optional[int] = None
    sender: str = ""
    recipient: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    content: str = ""
    status: Optional[str] = None

# Клас даних: структура дзвінка з інформацією про тривалість та статус
@dataclass
class Call:
    identifier: Optional[int] = None
    caller: str = ""
    callee: str = ""
    timestamp: float = field(default_factory=lambda: time.time())
    duration: Optional[float] = None
    status: Optional[str] = None


# Клас даних: статус присутності користувача в системі
@dataclass
class Presence:
    userid: str = ""
    status: str = "offline"
    lastseen: float = field(default_factory=lambda: time.time())
    device: str = ""
    signature: str = ""


# Клас шифрування: використовує AES через Fernet для захисту повідомлень
class Encryption:
    def __init__(self, key: bytes):
        self.key = key[:32].ljust(32, b'\0')[:32]

    def encrypt(self, plaintext: str) -> str:
        from cryptography.fernet import Fernet
        import base64
        f = Fernet(base64.urlsafe_b64encode(self.key))
        return f.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        from cryptography.fernet import Fernet
        import base64
        f = Fernet(base64.urlsafe_b64encode(self.key))
        return f.decrypt(ciphertext.encode()).decode()


# Клас підсистеми комунікацій: керує ізолінійним чіпом та мережевим інтерфейсом
class CommSubsystem:
    def __init__(self, host: str = "0.0.0.0", port: int = 7777):
        # Мережеві параметри для TCP сервера
        self.host = host
        self.port = port
        self.server: Optional[socket.socket] = None
        # Словник активних клієнтських з'єднань: clientid -> socket
        self.clients: Dict[str, socket.socket] = {}
        # Обробники повідомлень за префіксом: префікс -> функція-обробник
        self.handlers: Dict[str, Callable] = {}
        # Прапорець роботи сервера для контролю циклів прийому
        self.running = False
        # Потік прослуховування вхідних з'єднань
        self.listener: Optional[threading.Thread] = None
        # Ізолінійний сокет для підключення чіпа комунікацій
        self.socket: Optional[IsolinearSocket] = None
        # Ізолінійний чіп 06-0002 з базою даних
        self.chip: Optional[IsolinearChip] = None
        # Менеджер зовнішніх API (Telegram, WhatsApp, Viber, Meta)
        self.extapi: ExternalAPIManager = ExternalAPIManager()
        # Статуси присутності користувачів: userid -> Presence
        self.presence: Dict[str, Presence] = {}
        # Шифрування (опціонально)
        self.crypto: Optional[Encryption] = None

    def mountChip(self, chip: IsolinearChip, socket: IsolinearSocket) -> bool:
        # Монтування ізолінійного чіпа 06-0002 в ODN сокет
        # Перевіряємо чи чіп може бути вставлений
        if socket.Status.name != "EMPTY":
            return False
        socket.Insert(chip.ChipId)
        socket.Activate()
        chip.Connect()
        chip.Activate()
        self.socket = socket
        self.chip = chip
        self.initStorage()
        return True

    def unmountChip(self) -> bool:
        # Демонтування чіпа
        if self.chip is None or self.socket is None:
            return False
        self.chip.Deactivate()
        self.chip.Disconnect()
        self.socket.Eject()
        self.chip = None
        self.socket = None
        return True

    def initStorage(self):
        # Ініціалізація структури бази в чіпі
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery(
            "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, faction TEXT, email TEXT, phone TEXT, address TEXT, notes TEXT)"
        )
        self.chip.ExecuteQuery(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT NOT NULL, recipient TEXT NOT NULL, timestamp REAL NOT NULL, content TEXT NOT NULL, status TEXT)"
        )
        self.chip.ExecuteQuery(
            "CREATE TABLE IF NOT EXISTS calls (id INTEGER PRIMARY KEY AUTOINCREMENT, caller TEXT NOT NULL, callee TEXT NOT NULL, timestamp REAL NOT NULL, duration REAL, status TEXT)"
        )

    def startHost(self):
        # Запуск TCP сервера
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(10)
        self.running = True
        self.listener = threading.Thread(target=self.acceptClients, daemon=True)
        self.listener.start()

    def stopHost(self):
        self.running = False
        if self.server is not None:
            self.server.close()
        for client in self.clients.values():
            client.close()
        self.clients.clear()

    def acceptClients(self):
        # Цикл прийому TCP з'єднань
        assert self.server is not None, "server not created"
        while self.running:
            conn, addr = self.server.accept()
            clientid = f"{addr[0]}:{addr[1]}"
            self.clients[clientid] = conn
            threading.Thread(target=self.handleClient, args=(conn, clientid), daemon=True).start()

    def handleClient(self, conn: socket.socket, clientid: str):
        # Обробка повідомлень від конкретного клієнта в окремому потоці
        while self.running:
            # Читаємо дані з сокета, максимум 4KB за раз
            data = conn.recv(4096)
            # Якщо даних немає, клієнт закрив з'єднання
            if not data:
                break
            # Декодуємо байти в рядок UTF-8
            message = data.decode("utf-8")
            # Маршрутизуємо повідомлення до відповідного обробника
            self.route(message, clientid)
        # Видаляємо клієнта зі словника активних
        if clientid in self.clients:
            del self.clients[clientid]
        # Закриваємо сокет з'єднання
        conn.close()

    def route(self, message: str, clientid: str):
        # Маршрутизація повідомлення за префіксом до відповідного обробника
        for prefix, handler in self.handlers.items():
            # Перевіряємо чи повідомлення починається з зареєстрованого префікса
            if message.startswith(prefix):
                # Викликаємо обробник з повідомленням та ідентифікатором клієнта
                handler(message, clientid)
                return

    def register(self, prefix: str, handler: Callable):
        self.handlers[prefix] = handler

    def send(self, clientid: str, data: str):
        # Відправка даних конкретному клієнту за його ідентифікатором
        if clientid in self.clients:
            # Кодуємо рядок в UTF-8 байти та відправляємо через сокет
            self.clients[clientid].send(data.encode("utf-8"))

    def broadcast(self, data: str):
        for clientid in list(self.clients.keys()):
            self.send(clientid, data)

    def pollExternal(self) -> List[ExternalMessage]:
        # Отримання повідомлень з усіх підключених зовнішніх API
        results = self.extapi.pollAll()
        msgs: List[ExternalMessage] = []
        for platform, platformmsgs in results.items():
            msgs.extend(platformmsgs)
        return msgs

    def sendExternal(self, platform: str, recipient: str, text: str) -> bool:
        # Відправка повідомлення через зовнішній API
        return self.extapi.send(platform, recipient, text)

    def enableTelegram(self, token: str) -> bool:
        # Активація Telegram бота
        return self.extapi.enableTelegram(token)

    def enableWhatsapp(self, token: str, phoneid: str) -> bool:
        # Активація WhatsApp Business API
        return self.extapi.enableWhatsapp(token, phoneid)

    def enableViber(self, token: str) -> bool:
        # Активація Viber Public Account
        return self.extapi.enableViber(token)

    def enableMeta(self, token: str, pageid: str) -> bool:
        # Активація Meta Messenger
        return self.extapi.enableMeta(token, pageid)

    def setEncryption(self, key: bytes):
        # Встановлення ключа шифрування
        self.crypto = Encryption(key)

    def encryptMsg(self, text: str) -> str:
        # Шифрування повідомлення
        if self.crypto is None:
            return text
        return self.crypto.encrypt(text)

    def decryptMsg(self, text: str) -> str:
        # Розшифрування повідомлення
        if self.crypto is None:
            return text
        return self.crypto.decrypt(text)

    def setPresence(self, userid: str, status: str, device: str = ""):
        # Встановлення статусу присутності
        self.presence[userid] = Presence(userid=userid, status=status, device=device)

    def getPresence(self, userid: str) -> Optional[Presence]:
        # Отримання статусу присутності
        return self.presence.get(userid)

    def sendmulti(self, platforms: List[str], recipient: str, text: str) -> Dict[str, bool]:
        # Відправка на всі вказані платформи одразу
        results = {}
        for plat in platforms:
            results[plat] = self.sendExternal(plat, recipient, text)
        return results

    def sendemail(self, smtpconfig: Dict, to: str, subject: str, body: str) -> bool:
        # Відправка Email через SMTP
        import smtplib
        import email.mime.text
        msg = email.mime.text.MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = smtpconfig['user']
        msg['To'] = to
        with smtplib.SMTP(smtpconfig['host'], smtpconfig.get('port', 587)) as s:
            s.starttls()
            s.login(smtpconfig['user'], smtpconfig['pass'])
            s.send_message(msg)
        return True

    def sendsms(self, twilioconfig: Dict, to: str, body: str) -> bool:
        # Відправка SMS через Twilio API
        import urllib.request
        import urllib.parse
        import base64
        url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(twilioconfig['sid'])
        data = urllib.parse.urlencode({'To': to, 'From': twilioconfig['from'], 'Body': body}).encode()
        auth = base64.b64encode(f"{twilioconfig['sid']}:{twilioconfig['token']}".encode()).decode()
        req = urllib.request.Request(url, data=data, headers={'Authorization': f'Basic {auth}'}, method='POST')
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 201

    def connectto(self, host: str, port: int) -> Optional[socket.socket]:
        # Встановлення з'єднання з віддаленим вузлом LCARS
        # Створюємо клієнтський сокет IPv4 TCP
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Підключаємося до вказаного хосту та порту
        conn.connect((host, port))
        return conn

    def Version() -> str:
        # Отримання версії комунікаційного модуля з базової системи
        from lcars.base.info import getVersion
        return getVersion()

    def sendMessage(self, sender: str, recipient: str, content: str) -> int:
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery(
            "INSERT INTO messages (sender, recipient, timestamp, content, status) VALUES (?, ?, ?, ?, ?)",
            (sender, recipient, time.time(), content, "sent")
        )
        rid = self.chip.ExecuteQuery("SELECT last_insert_rowid()")
        if isinstance(rid, list) and len(rid) > 0 and isinstance(rid[0], (list, tuple)) and len(rid[0]) > 0:
            return int(rid[0][0])
        return 0

    def getMessages(self, participant: str) -> List[Message]:
        assert self.chip is not None, "chip not mounted"
        result = self.chip.ExecuteQuery(
            "SELECT id, sender, recipient, timestamp, content, status FROM messages WHERE sender = ? OR recipient = ? ORDER BY timestamp DESC",
            (participant, participant)
        )
        rows: List = result if isinstance(result, list) else []
        return [Message(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]

    def updateMessageStatus(self, messageid: int, status: str):
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery("UPDATE messages SET status = ? WHERE id = ?", (status, messageid))

    def getConversation(self, usera: str, userb: str) -> List[Message]:
        assert self.chip is not None, "chip not mounted"
        result = self.chip.ExecuteQuery(
            "SELECT id, sender, recipient, timestamp, content, status FROM messages WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?) ORDER BY timestamp ASC",
            (usera, userb, userb, usera)
        )
        rows: List = result if isinstance(result, list) else []
        return [Message(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]

    def startCall(self, caller: str, callee: str) -> int:
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery(
            "INSERT INTO calls (caller, callee, timestamp, status) VALUES (?, ?, ?, ?)",
            (caller, callee, time.time(), "started")
        )
        rid = self.chip.ExecuteQuery("SELECT last_insert_rowid()")
        if isinstance(rid, list) and len(rid) > 0 and isinstance(rid[0], (list, tuple)) and len(rid[0]) > 0:
            return int(rid[0][0])
        return 0

    def endCall(self, callid: int, duration: float):
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery("UPDATE calls SET duration = ?, status = ? WHERE id = ?", (duration, "ended", callid))

    def getCalls(self, participant: str) -> List[Call]:
        assert self.chip is not None, "chip not mounted"
        result = self.chip.ExecuteQuery(
            "SELECT id, caller, callee, timestamp, duration, status FROM calls WHERE caller = ? OR callee = ? ORDER BY timestamp DESC",
            (participant, participant)
        )
        rows: List = result if isinstance(result, list) else []
        return [Call(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]

    def call(self, caller: str, callee: str):
        # Створення контекстного менеджера для автоматичного керування дзвінком
        # При вході в with-контекст: створюється запис дзвінка
        # При виході: автоматично розраховується тривалість та оновлюється запис
        return CallContext(self, caller, callee)

    def addContact(self, contact: Contact) -> int:
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery(
            "INSERT INTO contacts (name, faction, email, phone, address, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (contact.name, contact.faction, contact.email, contact.phone, contact.address, contact.notes)
        )
        rid = self.chip.ExecuteQuery("SELECT last_insert_rowid()")
        cid = 0
        if isinstance(rid, list) and len(rid) > 0 and isinstance(rid[0], (list, tuple)) and len(rid[0]) > 0:
            cid = int(rid[0][0])
        contact.identifier = cid
        return cid

    def search(self, term: str) -> List[Contact]:
        assert self.chip is not None, "chip not mounted"
        pattern = f"%{term}%"
        result = self.chip.ExecuteQuery(
            "SELECT id, name, faction, email, phone, address, notes FROM contacts WHERE name LIKE ? OR faction LIKE ? OR email LIKE ? OR phone LIKE ? OR notes LIKE ?",
            (pattern, pattern, pattern, pattern, pattern)
        )
        rows: List = result if isinstance(result, list) else []
        return [Contact(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

    def deleteContact(self, contactid: int):
        assert self.chip is not None, "chip not mounted"
        self.chip.ExecuteQuery("DELETE FROM contacts WHERE id = ?", (contactid,))

    def updateContact(self, contactid: int, **fields):
        assert self.chip is not None, "chip not mounted"
        if not fields:
            return
        cols = [f"{k} = ?" for k in fields.keys()]
        vals = list(fields.values()) + [contactid]
        self.chip.ExecuteQuery(f"UPDATE contacts SET {', '.join(cols)} WHERE id = ?", tuple(vals))


class CallContext:
    def __init__(self, comm: CommSubsystem, caller: str, callee: str):
        self.comm = comm
        self.caller = caller
        self.callee = callee
        self.callid = None
        self.starttime = None

    def enter(self):
        self.starttime = time.time()
        self.callid = self.comm.startcall(self.caller, self.callee)
        return self.callid

    def exit(self, exctype=None, excval=None, exctb=None):
        if self.callid and self.starttime:
            duration = time.time() - self.starttime
            self.comm.endcall(self.callid, duration)

    def __enter__(self):
        return self.enter()

    def __exit__(self, exctype, excval, exctb):
        self.exit(exctype, excval, exctb)


commsystem = CommSubsystem()
ContactDatabase = CommSubsystem

# Ініціалізація комунікаційної підсистеми через ізолінійний чіп 06-0002
# Викликається при завантаженні чіпа в ODN слот
# Аргументи:
#   chip: IsolinearChip 06-0002 з базою даних comm_isolinear.db
#   socket: IsolinearSocket ODN слот для підключення
# Повертає: налаштований CommSubsystem з підключеним чіпом
def InitializeCommSubsystem(chip: IsolinearChip, socket: IsolinearSocket) -> CommSubsystem:
    subsystem = CommSubsystem()
    subsystem.mountChip(chip, socket)
    return subsystem

def InitializeContacts(chip: IsolinearChip) -> bool:
    # Ініціалізація таблиці контактів в ізолінійному чіпі
    chip.ExecuteQuery(
        "CREATE TABLE IF NOT EXISTS contacts ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "name TEXT NOT NULL,"
        "faction TEXT,"
        "email TEXT,"
        "phone TEXT,"
        "address TEXT,"
        "notes TEXT)"
    )
    return True

def InitializeMessages(chip: IsolinearChip) -> bool:
    # Ініціалізація таблиці повідомлень в ізолінійному чіпі
    chip.ExecuteQuery(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "sender TEXT NOT NULL,"
        "recipient TEXT NOT NULL,"
        "timestamp REAL NOT NULL,"
        "content TEXT NOT NULL,"
        "status TEXT)"
    )
    return True

def InitializeCalls(chip: IsolinearChip) -> bool:
    # Ініціалізація таблиці дзвінків в ізолінійному чіпі
    chip.ExecuteQuery(
        "CREATE TABLE IF NOT EXISTS calls ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "caller TEXT NOT NULL,"
        "callee TEXT NOT NULL,"
        "timestamp REAL NOT NULL,"
        "duration REAL,"
        "status TEXT)"
    )
    return True

__all__ = [
    "CommSubsystem", "Contact", "Message", "Call", "CallContext", "Presence", "Encryption",
    "commsystem", "ContactDatabase", "InitializeCommSubsystem",
    "InitializeContacts", "InitializeMessages", "InitializeCalls",
    "ExternalMessage"
]

def ContactDatabase():
    return Path("lcars/database/06-0002-comm.db")
