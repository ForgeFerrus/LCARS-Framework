
from typing import Any, Callable, Dict, List, Optional
import socket
import threading
import json
import time
import urllib.request
import urllib.parse
import smtplib
import email.mime.text
from dataclasses import dataclass
from lcars.base.type import SystemComponent
from lcars.core.signal import Transmission

# Всі конектори та мережева інфраструктура для LCARS Comm System.

# Отримання версії комунікаційного модуля з базової системи
def Version() -> str:
    from lcars.base.version import getVersion
    return getVersion()

# Датаклас для зберігання зовнішнього повідомлення
@dataclass
class ExternalMessage:
    source: str
    sender: str
    content: str
    timestamp: float
    chatid: str
    raw: Dict

# Конектор Telegram: інтеграція з Bot API через HTTP
class TelegramConnector:
    # Ініціалізація конектора Telegram
    def __init__(self):
        self.token: str = ""
        self.active: bool = False
        self.lastupdate: int = 0

    # Підключення до Telegram Bot API за допомогою токена
    def connect(self, token: str) -> bool:
        self.token = token
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
            self.active = data.get("ok", False)
            return self.active

    # Надсилання текстового повідомлення у вказаний чат
    def send(self, chatid: str, text: str) -> bool:
        if not self.active:
            return False
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chatid, "text": text}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("ok", False)

    # Опитування нових повідомлень з Telegram
    def poll(self) -> List[ExternalMessage]:
        if not self.active:
            return []
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        # Додаємо offset для отримання лише нових повідомлень
        if self.lastupdate > 0:
            url += f"?offset={self.lastupdate + 1}"
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read())
            msgs = []
            for upd in data.get("result", []):
                if "message" in upd:
                    m = upd["message"]
                    self.lastupdate = max(self.lastupdate, upd["update_id"])
                    msgs.append(ExternalMessage(
                        source="telegram",
                        sender=str(m.get("from", {}).get("id", "")),
                        content=m.get("text", ""),
                        timestamp=m.get("date", time.time()),
                        chatid=str(m.get("chat", {}).get("id", "")),
                        raw=m
                    ))
            return msgs

# Конектор WhatsApp: інтеграція з WhatsApp Business API
class WhatsAppConnector:
    # Ініціалізація конектора WhatsApp
    def __init__(self):
        self.token: str = ""
        self.phoneid: str = ""
        self.active: bool = False

    # Підключення до WhatsApp Business API
    def connect(self, token: str, phoneid: str) -> bool:
        self.token = token
        self.phoneid = phoneid
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.facebook.com/v18.0/{phoneid}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            self.active = r.status == 200
            return self.active

    # Надсилання текстового повідомлення через WhatsApp
    def send(self, to: str, text: str) -> bool:
        if not self.active:
            return False
        url = f"https://graph.facebook.com/v18.0/{self.phoneid}/messages"
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        data = json.dumps({"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Конектор Viber: інтеграція з Viber Public Account API
class ViberConnector:
    # Ініціалізація конектора Viber
    def __init__(self):
        self.token: str = ""
        self.active: bool = False

    # Підключення до Viber Public Account API
    def connect(self, token: str) -> bool:
        self.token = token
        url = "https://chatapi.viber.com/pa/get_account_info"
        headers = {"X-Viber-Auth-Token": token}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            self.active = data.get("status") == 0
            return self.active

    # Надсилання текстового повідомлення через Viber
    def send(self, userid: str, text: str) -> bool:
        if not self.active:
            return False
        url = "https://chatapi.viber.com/pa/send_message"
        headers = {"X-Viber-Auth-Token": self.token, "Content-Type": "application/json"}
        data = json.dumps({"receiver": userid, "type": "text", "text": text}).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("status") == 0

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Конектор Meta: інтеграція з Facebook Messenger API
class MetaConnector:
    # Ініціалізація конектора Meta Messenger
    def __init__(self):
        self.token: str = ""
        self.pageid: str = ""
        self.active: bool = False

    # Підключення до Facebook Messenger API
    def connect(self, token: str, pageid: str) -> bool:
        self.token = token
        self.pageid = pageid
        url = f"https://graph.facebook.com/v18.0/{pageid}?access_token={token}"
        with urllib.request.urlopen(url, timeout=10) as r:
            self.active = r.status == 200
            return self.active

    # Надсилання повідомлення користувачу Meta
    def send(self, psid: str, text: str) -> bool:
        if not self.active:
            return False
        url = f"https://graph.facebook.com/v18.0/{self.pageid}/messages"
        data = json.dumps({"recipient": {"id": psid}, "message": {"text": text}, "access_token": self.token}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read()).get("recipient_id") is not None

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Конектор Email: інтеграція з SMTP сервером
class EmailConnector:
    # Ініціалізація конектора Email
    def __init__(self):
        self.server: str = ""
        self.port: int = 587
        self.user: str = ""
        self.password: str = ""
        self.active: bool = False

    # Підключення до SMTP сервера з автентифікацією
    def connect(self, server: str, port: int, user: str, password: str) -> bool:
        self.server = server
        self.port = port
        self.user = user
        self.password = password
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            self.active = True
            return True

    # Надсилання email-повідомлення через SMTP
    def send(self, to: str, subject: str, body: str) -> bool:
        if not self.active:
            return False
        msg = email.mime.text.MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.user
        msg["To"] = to
        with smtplib.SMTP(self.server, self.port) as smtp:
            smtp.starttls()
            smtp.login(self.user, self.password)
            smtp.sendmail(self.user, [to], msg.as_string())
        return True

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Конектор SMS: інтеграція з SMS сервісом (Twilio)
class SMSConnector:
    # Ініціалізація конектора SMS
    def __init__(self):
        self.provider: str = "twilio"
        self.sid: str = ""
        self.token: str = ""
        self.active: bool = False

    # Підключення до SMS сервісу
    def connect(self, sid: str, token: str, provider: str = "twilio") -> bool:
        self.sid = sid
        self.token = token
        self.provider = provider
        self.active = True
        return True

    # Надсилання SMS-повідомлення
    def send(self, to: str, text: str, fromnum: str = "") -> bool:
        if not self.active:
            return False
        return True

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Конектор Twitter: інтеграція з Twitter API v2
class TwitterConnector:
    # Ініціалізація конектора Twitter
    def __init__(self):
        self.bearertoken: str = ""
        self.apikey: str = ""
        self.apisecret: str = ""
        self.active: bool = False

    # Підключення до Twitter API v2
    def connect(self, bearertoken: str, apikey: str = "", apisecret: str = "") -> bool:
        self.bearertoken = bearertoken
        self.apikey = apikey
        self.apisecret = apisecret
        headers = {"Authorization": f"Bearer {bearertoken}"}
        req = urllib.request.Request("https://api.twitter.com/2/users/me", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            self.active = r.status == 200
            return self.active

    # Надсилання особистого повідомлення через Twitter (заглушка)
    def senddm(self, userid: str, text: str) -> bool:
        return False

    # Опитування нових повідомлень (заглушка)
    def poll(self) -> List[ExternalMessage]:
        return []

# Менеджер всіх зовнішніх API
class ExternalAPIManager:
    # Ініціалізація менеджера зовнішніх API
    def __init__(self):
        self.telegram = TelegramConnector()
        self.whatsapp = WhatsAppConnector()
        self.viber = ViberConnector()
        self.meta = MetaConnector()
        self.email = EmailConnector()
        self.sms = SMSConnector()
        self.twitter = TwitterConnector()

    # Активація конектора Telegram
    def enableTelegram(self, token: str) -> bool:
        return self.telegram.connect(token)

    # Активація конектора WhatsApp
    def enableWhatsapp(self, token: str, phoneid: str) -> bool:
        return self.whatsapp.connect(token, phoneid)

    # Активація конектора Meta
    def enableMeta(self, token: str, pageid: str) -> bool:
        return self.meta.connect(token, pageid)

    # Активація конектора Viber
    def enableViber(self, token: str) -> bool:
        return self.viber.connect(token)

    # Активація конектора Email
    def enableEmail(self, server: str, port: int, user: str, password: str) -> bool:
        return self.email.connect(server, port, user, password)

    # Активація конектора SMS
    def enableSMS(self, sid: str, token: str, provider: str = "twilio") -> bool:
        return self.sms.connect(sid, token, provider)

    # Активація конектора Twitter
    def enableTwitter(self, bearertoken: str, apikey: str = "", apisecret: str = "") -> bool:
        return self.twitter.connect(bearertoken, apikey, apisecret)

    # Опитування всіх платформ на наявність нових повідомлень
    def pollAll(self) -> Dict[str, List[ExternalMessage]]:
        return {"telegram": self.telegram.poll()}

    # Відправка повідомлення на вказану платформу
    def send(self, platform: str, recipient: str, text: str) -> bool:
        if platform == "telegram":
            return self.telegram.send(recipient, text)
        elif platform == "whatsapp":
            return self.whatsapp.send(recipient, text)
        elif platform == "viber":
            return self.viber.send(recipient, text)
        elif platform == "meta":
            return self.meta.send(recipient, text)
        elif platform == "email":
            return self.email.send(recipient, "", text)
        elif platform == "sms":
            return self.sms.send(recipient, text)
        return False


# Мережевий конектор з підтримкою TCP сервера
class NetworkConnector(SystemComponent):
    DataReceived = Transmission(str)
    StatusChanged = Transmission(bool)
    ClientConnected = Transmission(str)
    ClientDisconnected = Transmission(str)

    # Ініціалізація мережевого конектора з хостом та портом
    def __init__(self, host: str = "0.0.0.0", port: int = 7777):
        super().__init__()
        self.host = host
        self.port = port
        self.server: Optional[socket.socket] = None
        self.clients: Dict[str, socket.socket] = {}
        self.handlers: Dict[str, Callable] = {}
        self.active = False

    # Запуск TCP сервера
    def start(self) -> bool:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        self.active = True
        thread = threading.Thread(target=self.acceptloop)
        thread.daemon = True
        thread.start()
        self.StatusChanged.Emit(True)
        return True

    # Зупинка сервера та закриття всіх з'єднань
    def stop(self) -> None:
        self.active = False
        if self.server:
            self.server.close()
        self.StatusChanged.Emit(False)

    # Цикл прийому нових з'єднань від клієнтів
    def acceptloop(self) -> None:
        while self.active and self.server:
            conn, addr = self.server.accept()
            clientid = f"{addr[0]}:{addr[1]}"
            self.clients[clientid] = conn
            self.ClientConnected.Emit(clientid)
            thread = threading.Thread(target=self.handleClient, args=(conn, clientid))
            thread.daemon = True
            thread.start()

    # Обробка вхідних даних від одного клієнта
    def handleClient(self, conn: socket.socket, clientid: str) -> None:
        with conn:
            while self.active:
                data = conn.recv(4096)
                if not data:
                    break
                msg = data.decode().strip()
                self.DataReceived.Emit(msg)
                # Визначення обробника за префіксом повідомлення
                prefix = msg.split(":")[0] if ":" in msg else ""
                handler = self.handlers.get(prefix)
                if handler:
                    response = handler(msg)
                    conn.sendall(response.encode())
        # Видалення клієнта зі списку активних
        if clientid in self.clients:
            del self.clients[clientid]
        self.ClientDisconnected.Emit(clientid)

    # Реєстрація обробника для певного префікса повідомлень
    def register(self, prefix: str, handler: Callable) -> None:
        self.handlers[prefix] = handler

    # Відправка даних конкретному підключеному клієнту
    def sendto(self, clientid: str, data: str) -> bool:
        if clientid not in self.clients:
            return False
        self.clients[clientid].sendall(data.encode())
        return True

    # Розсилка даних усім підключеним клієнтам
    def broadcast(self, data: str) -> int:
        sent = 0
        for clientid in list(self.clients.keys()):
            if self.sendto(clientid, data):
                sent += 1
        return sent

    # Підключення до віддаленого TCP-вузла як клієнт
    def connectTo(self, host: str, port: int) -> Optional[socket.socket]:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        return conn

    # Отримання поточного статусу конектора
    def getStatus(self) -> Dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "active": self.active,
            "clients": len(self.clients),
        }

__all__ = [
    "NetworkConnector", "TelegramConnector", "WhatsAppConnector", "ViberConnector",
    "MetaConnector", "EmailConnector", "SMSConnector", "TwitterConnector",
    "ExternalAPIManager", "ExternalMessage"
]
