# ◤ LCARS EXTERNAL COMMUNICATIONS & MESSAGING CONNECTORS 🖖
# =============================================================================
# ФАЙЛ: lcars/modules/connector.py
# ОПИС: Модуль зовнішніх комунікаційних конекторів зорельота.
#       Забезпечує зв'язок LCARS PADD-станцій та служб екіпажу з зовнішніми мережами
#       та месенджерами: Telegram, WhatsApp, Viber, Meta (Facebook) та Email (SMTP).
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations

from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import VersionInfo
from lcars.core.signal import ODN, Transmission
from lcars.modules.net import NetworkManager
from lcars.service.bridge import Bridge

# LCARS External Message Structure 
class ExternalMessage(LCARS):
    def __init__(self, Source: str, Sender: str, Content: str,
                 Timestamp: float = 0.0, ChatId: str = "", Raw: dict | None = None):
        super().__init__()
        self.Source = Source
        self.Sender = Sender
        self.Content = Content
        self.Timestamp = Timestamp
        self.ChatId = ChatId
        self.Raw = Raw or {}

    def ToDict(self) -> dict:
        return {
            "Source": self.Source,
            "Sender": self.Sender,
            "Content": self.Content,
            "Timestamp": self.Timestamp,
            "ChatId": self.ChatId,
            "Raw": self.Raw,
        }


class TelegramConnector(LCARS):
    def __init__(self):
        super().__init__()
        self.Token = ""
        self.IsActive = False
        self.LastUpdateId = 0
        self.Network = NetworkManager()

    def Connect(self, TokenStr: str) -> bool:
        self.Token = TokenStr
        Url = f"https://api.telegram.org/bot{TokenStr}/getMe"
        Success, Data = self.Network.RequestJson(Url, Timeout=8)
        self.IsActive = bool(Success and Data.get("ok", False)) if isinstance(Data, dict) else False
        return self.IsActive

    def Disconnect(self) -> None:
        self.IsActive = False
        self.Token = ""
        self.LastUpdateId = 0

    def Send(self, ChatId: str, Text: str) -> bool:
        if not self.IsActive and not self.Token:
            return False
        Url = f"https://api.telegram.org/bot{self.Token}/sendMessage"
        Success, Data = self.Network.RequestJson(
            Url, "POST", Payload={"chat_id": ChatId, "text": Text}, Timeout=8
        )
        return bool(Success and isinstance(Data, dict) and Data.get("ok", False))

    def Poll(self) -> list:
        if not self.IsActive:
            return []
        Url = f"https://api.telegram.org/bot{self.Token}/getUpdates"
        if self.LastUpdateId > 0:
            Url += f"?offset={self.LastUpdateId + 1}"
        Messages = []
        Success, Data = self.Network.RequestJson(Url, Timeout=10)
        if not Success or not isinstance(Data, dict):
            return Messages
        for Upd in Data.get("result", []):
            if "message" in Upd:
                Msg = Upd["message"]
                self.LastUpdateId = max(self.LastUpdateId, Upd.get("update_id", 0))
                DateTimeModule = LCARS.Import("datetime")
                DateTimeClass = getattr(DateTimeModule, "datetime", None) if DateTimeModule else None
                Now = DateTimeClass.now().timestamp() if DateTimeClass and hasattr(DateTimeClass, "now") else 0.0
                Messages.append(ExternalMessage(
                    Source="Telegram",
                    Sender=str(Msg.get("from", {}).get("id", "")),
                    Content=Msg.get("text", ""),
                    Timestamp=float(Msg.get("date", Now)),
                    ChatId=str(Msg.get("chat", {}).get("id", "")),
                    Raw=Msg,
                ))
        return Messages


class WhatsAppConnector(LCARS):
    ApiBase = "https://graph.facebook.com/v18.0"

    def __init__(self):
        super().__init__()
        self.Token = ""
        self.PhoneId = ""
        self.IsActive = False
        self.Network = NetworkManager()

    def Connect(self, TokenStr: str, PhoneIdStr: str) -> bool:
        self.Token = TokenStr
        self.PhoneId = PhoneIdStr
        self.IsActive = bool(TokenStr and PhoneIdStr)
        return self.IsActive

    def Disconnect(self) -> None:
        self.IsActive = False
        self.Token = ""
        self.PhoneId = ""

    def Send(self, TargetPhone: str, Text: str) -> bool:
        if not self.IsActive:
            return False
        Url = f"{self.ApiBase}/{self.PhoneId}/messages"
        Headers = {"Authorization": f"Bearer {self.Token}", "Content-Type": "application/json"}
        Payload = {
            "messaging_product": "whatsapp",
            "to": TargetPhone,
            "type": "text",
            "text": {"body": Text},
        }
        Success, Data = self.Network.RequestJson(
            Url, "POST", Headers=Headers, Payload=Payload, Timeout=8
        )
        return bool(Success and isinstance(Data, dict) and Data.get("messages") is not None)

    def Poll(self) -> list:
        if not self.IsActive:
            return []
        Url = f"{self.ApiBase}/{self.PhoneId}/messages"
        Headers = {"Authorization": f"Bearer {self.Token}"}
        Success, Data = self.Network.RequestJson(Url, "GET", Headers=Headers, Timeout=10)
        if not Success or not isinstance(Data, dict):
            return []
        Messages = []
        for Msg in Data.get("data", []):
            Messages.append(ExternalMessage(
                Source="WhatsApp",
                Sender=str(Msg.get("from", "")),
                Content=Msg.get("text", {}).get("body", ""),
                Timestamp=0.0,
                ChatId=str(Msg.get("id", "")),
                Raw=Msg,
            ))
        return Messages


class ViberConnector(LCARS):
    ApiBase = "https://chatapi.viber.com/pa"

    def __init__(self):
        super().__init__()
        self.Token = ""
        self.IsActive = False
        self.Network = NetworkManager()

    def Connect(self, TokenStr: str) -> bool:
        self.Token = TokenStr
        self.IsActive = bool(TokenStr)
        return self.IsActive

    def Disconnect(self) -> None:
        self.IsActive = False
        self.Token = ""

    def Send(self, UserId: str, Text: str) -> bool:
        if not self.IsActive:
            return False
        Url = f"{self.ApiBase}/send_message"
        Headers = {"X-Viber-Auth-Token": self.Token, "Content-Type": "application/json"}
        Payload = {"receiver": UserId, "type": "text", "text": Text}
        Success, Data = self.Network.RequestJson(
            Url, "POST", Headers=Headers, Payload=Payload, Timeout=8
        )
        return bool(Success and isinstance(Data, dict) and Data.get("status") == 0)

    def Poll(self) -> list:
        if not self.IsActive:
            return []
        Url = f"{self.ApiBase}/get_messages"
        Headers = {"X-Viber-Auth-Token": self.Token}
        Success, Data = self.Network.RequestJson(Url, "GET", Headers=Headers, Timeout=10)
        if not Success or not isinstance(Data, dict):
            return []
        Messages = []
        for Msg in Data.get("data", []):
            Messages.append(ExternalMessage(
                Source="Viber",
                Sender=str(Msg.get("sender", {}).get("id", "")),
                Content=Msg.get("text", ""),
                Timestamp=float(Msg.get("timestamp", 0.0)),
                ChatId=str(Msg.get("conversation", {}).get("id", "")),
                Raw=Msg,
            ))
        return Messages


class MetaConnector(LCARS):
    ApiBase = "https://graph.facebook.com/v18.0"

    def __init__(self):
        super().__init__()
        self.Token = ""
        self.PageId = ""
        self.IsActive = False
        self.Network = NetworkManager()

    def Connect(self, TokenStr: str, PageIdStr: str) -> bool:
        self.Token = TokenStr
        self.PageId = PageIdStr
        self.IsActive = bool(TokenStr and PageIdStr)
        return self.IsActive

    def Disconnect(self) -> None:
        self.IsActive = False
        self.Token = ""
        self.PageId = ""

    def Send(self, Psid: str, Text: str) -> bool:
        if not self.IsActive:
            return False
        Url = f"{self.ApiBase}/{self.PageId}/messages"
        Headers = {"Authorization": f"Bearer {self.Token}", "Content-Type": "application/json"}
        Payload = {
            "recipient": {"id": Psid},
            "message": {"text": Text},
        }
        Success, Data = self.Network.RequestJson(
            Url, "POST", Headers=Headers, Payload=Payload, Timeout=8
        )
        return bool(Success and isinstance(Data, dict) and Data.get("recipient_id") is not None)

    def Poll(self) -> list:
        if not self.IsActive:
            return []
        Url = f"{self.ApiBase}/{self.PageId}/conversations?fields=messages&access_token={self.Token}"
        Success, Data = self.Network.RequestJson(Url, "GET", Timeout=10)
        if not Success or not isinstance(Data, dict):
            return []
        Messages = []
        for Msg in Data.get("data", []):
            Messages.append(ExternalMessage(
                Source="Meta",
                Sender=str(Msg.get("from", {}).get("id", "")),
                Content=Msg.get("message", {}).get("text", ""),
                Timestamp=0.0,
                ChatId=str(Msg.get("id", "")),
                Raw=Msg,
            ))
        return Messages


class EmailConnector(LCARS):
    def __init__(self):
        super().__init__()
        self.Server = ""
        self.Port = 587
        self.User = ""
        self.Password = ""
        self.IsActive = False

    def Connect(self, ServerStr: str, PortNum: int, UserStr: str, PassStr: str) -> bool:
        self.Server = ServerStr
        self.Port = PortNum
        self.User = UserStr
        self.Password = PassStr
        self.IsActive = bool(ServerStr and UserStr)
        return self.IsActive

    def Disconnect(self) -> None:
        self.IsActive = False
        self.Server = ""
        self.User = ""
        self.Password = ""

    def Send(self, RecipientEmail: str, SubjectText: str, BodyText: str) -> bool:
        if not self.IsActive or not self.Server:
            return False
        SmtpClass = Bridge.Load("System.Network.SMTP.Client")
        MimeTextClass = Bridge.Load("System.Network.Email.MIME.Text")
        if not callable(SmtpClass) or not callable(MimeTextClass):
            return False
        Message = MimeTextClass(BodyText)
        Message["Subject"] = SubjectText
        Message["From"] = self.User
        Message["To"] = RecipientEmail
        Smtp = SmtpClass(self.Server, self.Port, timeout=10)
        if Smtp is None:
            return False
        StartTlsFn = getattr(Smtp, "starttls", None)
        if callable(StartTlsFn):
            StartTlsFn()
        LoginFn = getattr(Smtp, "login", None)
        if callable(LoginFn):
            LoginFn(self.User, self.Password)
        SendFn = getattr(Smtp, "send_message", None)
        if callable(SendFn):
            SendFn(Message)
        QuitFn = getattr(Smtp, "quit", None)
        if callable(QuitFn):
            QuitFn()
        return True

    def Poll(self) -> list:
        if not self.IsActive or not self.Server:
            return []
        ImapClass = Bridge.Load("System.Network.Email.IMAP.Client")
        if not callable(ImapClass):
            return []
        Imap = ImapClass(self.Server, timeout=10)
        if Imap is None:
            return []
        LoginFn = getattr(Imap, "login", None)
        if callable(LoginFn):
            LoginFn(self.User, self.Password)
        SelectFn = getattr(Imap, "select", None)
        if callable(SelectFn):
            SelectFn("INBOX")
        SearchFn = getattr(Imap, "search", None)
        Messages = []
        if callable(SearchFn):
            Status, Data = SearchFn(None, "UNSEEN")
            if Status == "OK":
                Ids = Data[0].split() if Data and Data[0] else []
                FetchFn = getattr(Imap, "fetch", None)
                for MsgId in Ids[-10:]:
                    if callable(FetchFn):
                        MsgData = FetchFn(MsgId, "(RFC822)")
                        if MsgData and MsgData[1]:
                            Raw = str(MsgData[1][0][1])
                            Messages.append(ExternalMessage(
                                Source="Email",
                                Sender=self.User,
                                Content=Raw[:2048],
                                Timestamp=0.0,
                                ChatId=str(MsgId),
                                Raw={"id": str(MsgId)},
                            ))
        CloseFn = getattr(Imap, "close", None)
        if callable(CloseFn):
            CloseFn()
        LogoutFn = getattr(Imap, "logout", None)
        if callable(LogoutFn):
            LogoutFn()
        return Messages


class ConnectorManager(SystemComponent):
    Instance = None
    MessageTransmitted = Transmission(str, str, bool)

    def __init__(self):
        super().__init__()
        self.Telegram = TelegramConnector()
        self.WhatsApp = WhatsAppConnector()
        self.Viber = ViberConnector()
        self.Meta = MetaConnector()
        self.Email = EmailConnector()
        self.Version = VersionInfo.GetVersion()

    @classmethod
    def GetInstance(cls) -> ConnectorManager:
        if cls.Instance is None:
            cls.Instance = ConnectorManager()
        return cls.Instance

    def ConnectAll(self, Config: dict) -> dict:
        Results = {}
        TelegramToken = Config.get("telegram_token", "")
        if TelegramToken:
            Results["Telegram"] = self.Telegram.Connect(TelegramToken)
        WhatsAppToken = Config.get("whatsapp_token", "")
        WhatsAppPhone = Config.get("whatsapp_phone_id", "")
        if WhatsAppToken and WhatsAppPhone:
            Results["WhatsApp"] = self.WhatsApp.Connect(WhatsAppToken, WhatsAppPhone)
        ViberToken = Config.get("viber_token", "")
        if ViberToken:
            Results["Viber"] = self.Viber.Connect(ViberToken)
        MetaToken = Config.get("meta_token", "")
        MetaPage = Config.get("meta_page_id", "")
        if MetaToken and MetaPage:
            Results["Meta"] = self.Meta.Connect(MetaToken, MetaPage)
        EmailServer = Config.get("email_server", "")
        EmailPort = int(Config.get("email_port", 587))
        EmailUser = Config.get("email_user", "")
        EmailPass = Config.get("email_password", "")
        if EmailServer and EmailUser:
            Results["Email"] = self.Email.Connect(EmailServer, EmailPort, EmailUser, EmailPass)
        return Results

    def DisconnectAll(self) -> None:
        self.Telegram.Disconnect()
        self.WhatsApp.Disconnect()
        self.Viber.Disconnect()
        self.Meta.Disconnect()
        self.Email.Disconnect()

    def PollAll(self) -> list:
        Messages = []
        Messages.extend(self.Telegram.Poll())
        Messages.extend(self.WhatsApp.Poll())
        Messages.extend(self.Viber.Poll())
        Messages.extend(self.Meta.Poll())
        Messages.extend(self.Email.Poll())
        return Messages

    def SendExternal(self, ServiceName: str, Destination: str, Content: str) -> bool:
        Svc = ServiceName.lower()
        Success = False
        if Svc == "telegram":
            Success = self.Telegram.Send(Destination, Content)
        elif Svc == "whatsapp":
            Success = self.WhatsApp.Send(Destination, Content)
        elif Svc == "viber":
            Success = self.Viber.Send(Destination, Content)
        elif Svc in ("meta", "facebook"):
            Success = self.Meta.Send(Destination, Content)
        elif Svc == "email":
            Success = self.Email.Send(Destination, "LCARS Transmission", Content)

        self.MessageTransmitted.Emit(ServiceName, Destination, Success)
        ODN.Transmit("System.Connector.Sent", Service=ServiceName, Destination=Destination, Success=Success)
        return Success

    def GetStatus(self) -> dict:
        return {
            "TelegramActive": self.Telegram.IsActive,
            "WhatsAppActive": self.WhatsApp.IsActive,
            "ViberActive": self.Viber.IsActive,
            "MetaActive": self.Meta.IsActive,
            "EmailActive": self.Email.IsActive,
            "Version": self.Version,
        }


__all__ = [
    "ExternalMessage", "TelegramConnector", "WhatsAppConnector",
    "ViberConnector", "MetaConnector", "EmailConnector", "ConnectorManager",
]
