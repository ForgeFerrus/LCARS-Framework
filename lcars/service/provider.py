# LCARS AI PROVIDER MANAGER & UNIFIED MODEL SUBSYSTEM
#
# ОПИС: Єдиний сервіс інтеграції AI-провайдерів через центральний Міст (Bridge) та Проксі (Proxy).
# ПРИЗНАЧЕННЯ: Маршрутизація повідомлень між викликачем та мережевим бекендом. Виключно транспортний шар.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure Classes, Proxy-Based Loading).
#
# КОНТРАКТ ПРОВАЙДЕРА:
#   Backend.Chat(Messages: List[dict], Tools=None) -> str
#   Manager.Route(Messages: List[dict], Tools=None) -> str
#   Manager.SwitchModel(Name: str) -> bool
#   Manager.GetStatus() -> dict
#
# ВІДПОВІДАЛЬНІСТЬ:
#   - Провайдер знає тільки про мережевий протокол конкретного API.
#   - Провайдер НЕ знає що таке system prompt, агент, роль чи контекст.
#   - Повідомлення (Messages) — вже сформований список {role, content} від викликача.
#   - Системні промпти, ролі та персони формуються ВИКЛЮЧНО викликачем.
#
# АРХІТЕКТУРА:
#   1. AIModel — базовий клас для всіх провайдерів
#   2. LocalQVACProvider — локальний QVAC сервер (без інтернету)
#   3. QVAC — адаптер Nova для QVAC-host
#   4. LocalLLM — локальна модель через transformers (кешується в RAM)
#   5. GROQwen — Groq cloud (ultra-fast)
#   6. Mistral — Mistral AI / Codestral
#   7. AstraProvider — Experiential Labs / GPT-6
#   8. OpenRouterProvider — мульти-модельний gateway
#   9. AIProviderManager — центральний маршрутизатор
#  10. AIProvider — статичний доступ

from __future__ import annotations
from lcars.service.bridge import Bridge
from lcars.engineering.telemetry import EmitTelemetry
from lcars.system.environment import Runtime
from lcars.base.type import LCARS, Directive
from lcars.core.signal import ODN

AbcModule = LCARS.Import("abc")
ABC = getattr(AbcModule, "ABC", None) if AbcModule else None
# =====================================================================
# 1. БАЗОВИЙ ІНТЕРФЕЙС ПРОВАЙДЕРА (TRANSPORT ADAPTER)
# Всі провайдери наслідують цей клас.
# Містить тільки транспортну логіку — мережеві запити та форматування відповідей.
# =====================================================================
class AIModel(ABC):
    BridgeKey: str = ""
    Name: str = ""
    Available: bool = False

    def CheckAvailable(self) -> bool:
        return False

    def Chat(self, Messages, Tools=None) -> str:
        return ""

    def GetInfo(self) -> dict:
        return {"name": self.Name, "available": self.CheckAvailable()}

    def NetworkRequest(self, Host, Path, Payload, Headers, Ssl=True, Timeout=30, Retries=3):
        NetworkMod = LCARS.Import("lcars.service.network")
        if NetworkMod and hasattr(NetworkMod, "NetworkService"):
            NetSvc = NetworkMod.NetworkService.GetInstance()
            if NetSvc:
                return NetSvc.Request(Host, Path, Payload, Headers, Ssl, Timeout, Retries)
        return ""


# =====================================================================
# 2. QVAC PROVIDER — локальний QVAC сервер (два методи підключення)
# Метод 1: Через Bridge/Adapter (Nova)
# Метод 2: Пряме підключення (OpenAI-compatible)
# Запуск: qvac serve openai --model nova --port 11434
# =====================================================================
class QVAC(AIModel):
    def __init__(self, Model="gemma2-27b", Host: str = "127.0.0.1", Port: int = 11434):
        self.Name = "qvac"
        self.Model = Model
        self.Host = Host
        self.Port = Port
        self.MaxTokens = 1024
        self.BridgeKey = "AI.Provider.QVAC"
        self.Adapter = None
        self.UseAdapter = False

    def CheckAvailable(self) -> bool:
        if self.Available:
            return True

        # Спочатку пробуємо адаптер через Bridge
        BridgeInstance = Bridge.GetInstance()
        if BridgeInstance:
            Adapter = BridgeInstance.Load(self.BridgeKey)
            if Adapter:
                self.Adapter = Adapter
                self.UseAdapter = True
                self.Available = True
                return True

        # Якщо адаптер не працює - пробуємо пряме підключення
        SocketMod = LCARS.Import("socket")
        if SocketMod:
            Sock = SocketMod.socket(SocketMod.AF_INET, SocketMod.SOCK_STREAM)
            Sock.settimeout(0.4)
            Result = Sock.connect_ex((self.Host, self.Port)) == 0
            Sock.close()
            if Result:
                self.Available = True
                return True

        return False

    def Chat(self, Messages, Tools=None):
        if not self.CheckAvailable():
            return "[QVAC: not available - check QVAC server or adapter]"

        if self.UseAdapter and self.Adapter:
            if hasattr(self.Adapter, "Chat"):
                return self.Adapter.Chat(Messages, Tools)
            return "[QVAC: Chat method not found in adapter]"

        Payload = {
            "model": self.Model,
            "messages": Messages,
            "max_tokens": self.MaxTokens,
        }
        if Tools:
            Payload["tools"] = Tools
            Payload["tool_choice"] = "auto"
        Headers = {"Content-Type": "application/json"}
        Raw = self.NetworkRequest(self.Host + ":" + str(self.Port), "/v1/chat/completions", Payload, Headers, Ssl=False, Timeout=120)
        if not Raw:
            return "[QVAC: no response from server]"
        return self.ParseResponse(Raw) or "[QVAC: empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {
            "name": self.Name,
            "model": self.Model,
            "available": self.CheckAvailable(),
            "host": self.Host,
            "port": self.Port,
            "adapter": self.UseAdapter,
        }


# =====================================================================
# 4. LOCAL LLM — CPU/GPU БЕКЕНД (TRANSFORMERS)
# Модель завантажується ОДИН раз і кешується в пам'яті.
# Наступні виклики Chat() використовують вже завантажену модель.
# Налаштування шляху до моделі: LOCAL_LLM_PATH в .env
# =====================================================================
class LocalLLM(AIModel):
    ModelInstance = None
    TokenizerInstance = None
    CachedPath = None
    LoadLock = None

    def __init__(self, Model="gemma2-27b", MaxTokens=1024):
        self.Name = "localllm"
        self.ModelKey = Model
        self.ModelId = "Gemma2-27B-Local"
        self.MaxTokens = MaxTokens
        self.Model = None
        self.Tokenizer = None
        if LocalLLM.LoadLock is None:
            ThreadingMod = LCARS.System.Thread
            if ThreadingMod and hasattr(ThreadingMod, "Lock"):
                LocalLLM.LoadLock = ThreadingMod.Lock()

    def ResolveModelPath(self):
        CustomPath = str(Runtime.get("LOCAL_LLM_PATH", "")).strip()
        if CustomPath:
            PathMod = LCARS.System.Path
            if PathMod and hasattr(PathMod, "Path"):
                PathObj = PathMod.Path(CustomPath)
                if hasattr(PathObj, "exists") and PathObj.exists():
                    return CustomPath
        DefaultPath = r"C:\Users\Forge\MyProject\Models\HuggingFace\models--google--gemma-2-27b-it"
        PathMod = LCARS.System.Path
        if PathMod and hasattr(PathMod, "Path"):
            PathObj = PathMod.Path(DefaultPath)
            if hasattr(PathObj, "exists") and PathObj.exists():
                return DefaultPath
        return ""

    def EnsureLoaded(self) -> bool:
        if LocalLLM.ModelInstance is not None and LocalLLM.TokenizerInstance is not None:
            self.Model = LocalLLM.ModelInstance
            self.Tokenizer = LocalLLM.TokenizerInstance
            return True
        ModelPath = self.ResolveModelPath()
        if not ModelPath:
            return False
        if LocalLLM.LoadLock:
            with LocalLLM.LoadLock:
                if LocalLLM.ModelInstance is not None:
                    self.Model = LocalLLM.ModelInstance
                    self.Tokenizer = LocalLLM.TokenizerInstance
                    return True
                TimeMod = LCARS.System.Time
                StartT = TimeMod.time() if TimeMod and hasattr(TimeMod, "time") else 0.0
                SysModule = LCARS.Import("sys")
                if SysModule and hasattr(SysModule, "stdout"):
                    SysModule.stdout.write(">> [NEURAL BUFFER] Loading model into RAM (first time only)...\n")
                    SysModule.stdout.flush()
                TransformersMod = LCARS.Import("transformers")
                TorchMod = LCARS.Import("torch")
                if TransformersMod is None or TorchMod is None:
                    if SysModule and hasattr(SysModule, "stdout"):
                        SysModule.stdout.write("✗ [NEURAL BUFFER] Missing dependencies: transformers or torch\n")
                        SysModule.stdout.flush()
                    return False
                AutoTokenizer = getattr(TransformersMod, "AutoTokenizer", None)
                AutoModelForCausalLM = getattr(TransformersMod, "AutoModelForCausalLM", None)
                if AutoTokenizer is None or AutoModelForCausalLM is None:
                    if SysModule and hasattr(SysModule, "stdout"):
                        SysModule.stdout.write("✗ [NEURAL BUFFER] Missing classes: AutoTokenizer or AutoModelForCausalLM\n")
                        SysModule.stdout.flush()
                    return False
                Tokenizer = AutoTokenizer.from_pretrained(ModelPath, local_files_only=True)
                Model = AutoModelForCausalLM.from_pretrained(
                    ModelPath,
                    dtype=TorchMod.float32,
                    device_map="cpu",
                    local_files_only=True
                )
                if Model is None or Tokenizer is None:
                    if SysModule and hasattr(SysModule, "stdout"):
                        SysModule.stdout.write("✗ [NEURAL BUFFER] Failed to load model or tokenizer\n")
                        SysModule.stdout.flush()
                    return False
                LocalLLM.ModelInstance = Model
                LocalLLM.TokenizerInstance = Tokenizer
                LocalLLM.CachedPath = ModelPath
                self.Model = Model
                self.Tokenizer = Tokenizer
                EndT = TimeMod.time() if TimeMod and hasattr(TimeMod, "time") else 0.0
                if SysModule and hasattr(SysModule, "stdout"):
                    SysModule.stdout.write(f"✓ [NEURAL BUFFER] Model loaded in {EndT - StartT:.2f}s\n")
                    SysModule.stdout.flush()
                return True
        return True

    def Chat(self, Messages, Tools=None):
        if not self.EnsureLoaded():
            return "[LocalLLM: Model not available — check LOCAL_LLM_PATH]"
        TimeMod = LCARS.System.Time
        StartGen = TimeMod.time() if TimeMod and hasattr(TimeMod, "time") else 0.0
        SysModule = LCARS.Import("sys")
        if SysModule and hasattr(SysModule, "stdout"):
            SysModule.stdout.write(">> [NEURAL CORE] Processing...\n")
            SysModule.stdout.flush()
        TorchMod = LCARS.Import("torch")
        if TorchMod is None:
            return "[LocalLLM: torch module not available]"
        Text = self.Tokenizer.apply_chat_template(Messages, tokenize=False, add_generation_prompt=True)
        Inputs = self.Tokenizer([Text], return_tensors="pt")
        with TorchMod.no_grad():
            Outputs = self.Model.generate(
                **Inputs,
                max_new_tokens=self.MaxTokens,
                temperature=0.3,
                do_sample=True,
            )
        NewTokens = [out[len(inp):] for inp, out in zip(Inputs.input_ids, Outputs)]
        Response = self.Tokenizer.batch_decode(NewTokens, skip_special_tokens=True)[0]
        EndGen = TimeMod.time() if TimeMod and hasattr(TimeMod, "time") else 0.0
        if SysModule and hasattr(SysModule, "stdout"):
            SysModule.stdout.write(f"✓ [NEURAL CORE] Generated {len(NewTokens[0])} tokens ({EndGen - StartGen:.2f}s)\n")
            SysModule.stdout.flush()
        return Response.strip()

    def GetInfo(self):
        return {
            "name": self.Name,
            "model": self.ModelId,
            "available": self.EnsureLoaded(),
            "path": self.ResolveModelPath(),
        }


# =====================================================================
# 5. GROQ — ULTRA-FAST CLOUD GATEWAY
# Groq API для швидкої генерації в хмарі
# Потребує GROQ_API_KEY в .env
# =====================================================================
class GROQwen(AIModel):
    MODELS = [
        "gemma-2-27b-it",
        "gemma-2-9b-it",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]

    def __init__(self, Model="gemma-2-27b-it"):
        self.Name = "groqwen"
        self.Model = Model
        self.Host = "api.groq.com"
        self.Path = "/openai/v1/chat/completions"
        self.Token = str(Runtime.get("GROQ_API_KEY", Runtime.get("GROQ API KEY", ""))).strip()
        self.Available = False

    def CheckAvailable(self):
        if self.Token:
            self.Available = True
        return self.Available

    def Chat(self, Messages, Tools=None):
        if not self.Token:
            return "[Groq Standby: Set GROQ_API_KEY. Model: " + self.Model + "]"
        MaxTok = int(getattr(self, "MaxTokens", 600))
        Payload = {"model": self.Model, "messages": Messages, "max_tokens": MaxTok}
        if Tools:
            Payload["tools"] = Tools
            Payload["tool_choice"] = "auto"
        Headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.Token}
        Raw = self.NetworkRequest(self.Host, self.Path, Payload, Headers, Ssl=True, Timeout=45)
        if not Raw:
            return "[Groq " + self.Model + "]: No response"
        return self.ParseResponse(Raw) or "[Groq: Empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {"name": self.Name, "model": self.Model, "available": self.CheckAvailable(), "models": self.GetAvailableModels()}

    def GetAvailableModels(self):
        return self.MODELS


# =====================================================================
# 6. MISTRAL AI / CODESTRAL GATEWAY
# Mistral API для кодування та генерації тексту
# Потребує MISTRAL_API_KEY в .env
# =====================================================================
class Mistral(AIModel):
    MODELS = ["codestral-latest", "mistral-large-latest", "mistral-small-latest"]

    def __init__(self, Model="codestral-latest"):
        self.Name = "mistral"
        self.Model = Model
        self.Host = "api.mistral.ai"
        self.Path = "/v1/chat/completions"
        self.Token = str(Runtime.get("MISTRAL_API_KEY", Runtime.get("MISTRAL API KEY", ""))).strip()
        self.Available = False

    def CheckAvailable(self):
        if self.Token:
            self.Available = True
        return self.Available

    def Chat(self, Messages, Tools=None):
        if not self.Token:
            return "[Mistral Standby: Set MISTRAL_API_KEY. Model: " + self.Model + "]"
        MaxTok = int(getattr(self, "MaxTokens", 600))
        Payload = {"model": self.Model, "messages": Messages, "max_tokens": MaxTok}
        if Tools:
            Payload["tools"] = Tools
            Payload["tool_choice"] = "auto"
        Headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.Token}
        Raw = self.NetworkRequest(self.Host, self.Path, Payload, Headers, Ssl=True, Timeout=45)
        if not Raw:
            return "[Mistral " + self.Model + "]: No response"
        return self.ParseResponse(Raw) or "[Mistral: Empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {"name": self.Name, "model": self.Model, "available": self.CheckAvailable(), "models": self.GetAvailableModels()}

    def GetAvailableModels(self):
        return self.MODELS


# =====================================================================
# 7. ASTRA PROVIDER — Experiential Labs / GPT-6
# Експериментальний провайдер для нових моделей
# Потребує ASTRA_API_KEY в .env
# =====================================================================
class Astra(AIModel):
    MODELS = ["gpt-6-preview", "gpt-6-turbo"]

    def __init__(self, Model="gpt-6-preview"):
        self.Name = "astra"
        self.Model = Model
        self.Host = "api.experiential.ai"
        self.Path = "/v1/chat/completions"
        self.Token = str(Runtime.get("ASTRA_API_KEY", Runtime.get("ASTRA API KEY", ""))).strip()
        self.Available = False

    def CheckAvailable(self):
        if self.Token:
            self.Available = True
        return self.Available

    def Chat(self, Messages, Tools=None):
        if not self.Token:
            return "[Astra Standby: Set ASTRA_API_KEY. Model: " + self.Model + "]"
        MaxTok = int(getattr(self, "MaxTokens", 600))
        Payload = {"model": self.Model, "messages": Messages, "max_tokens": MaxTok}
        if Tools:
            Payload["tools"] = Tools
            Payload["tool_choice"] = "auto"
        Headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.Token}
        Raw = self.NetworkRequest(self.Host, self.Path, Payload, Headers, Ssl=True, Timeout=60)
        if not Raw:
            return "[Astra " + self.Model + "]: No transmission"
        return self.ParseResponse(Raw) or "[Astra: Empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {"name": self.Name, "model": self.Model, "available": self.CheckAvailable(), "models": self.GetAvailableModels()}

    def GetAvailableModels(self):
        return self.MODELS


# =====================================================================
# 8. OPENROUTER PROVIDER — мульти-модельний gateway
# Підтримує багато різних моделей через один API
# Потребує OPENROUTER_API_KEY в .env
# =====================================================================
class OpenRouter(AIModel):
    MODELS = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-405b-instruct",
    ]

    def __init__(self, Model="anthropic/claude-3.5-sonnet"):
        self.Name = "openrouter"
        self.Model = Model
        self.Host = "openrouter.ai"
        self.Path = "/api/v1/chat/completions"
        self.Token = str(Runtime.get("OPENROUTER_API_KEY", Runtime.get("OPENROUTER API KEY", ""))).strip()
        self.Available = False

    def CheckAvailable(self):
        if self.Token:
            self.Available = True
        return self.Available

    def Chat(self, Messages, Tools=None):
        if not self.Token:
            return "[OpenRouter Standby: Set OPENROUTER_API_KEY. Model: " + self.Model + "]"
        MaxTok = int(getattr(self, "MaxTokens", 600))
        Payload = {"model": self.Model, "messages": Messages, "max_tokens": MaxTok}
        if Tools:
            Payload["tools"] = Tools
            Payload["tool_choice"] = "auto"
        Headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.Token,
            "HTTP-Referer": "https://lcars.starfleet",
            "X-Title": "LCARS Control Master Gateway",
        }
        Raw = self.NetworkRequest(self.Host, self.Path, Payload, Headers, Ssl=True, Timeout=60)
        if not Raw:
            return "[OpenRouter " + self.Model + "]: No transmission"
        return self.ParseResponse(Raw) or "[OpenRouter: Empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {"name": self.Name, "model": self.Model, "available": self.CheckAvailable(), "models": self.GetAvailableModels()}

    def GetAvailableModels(self):
        return self.MODELS
# =====================================================================
# 9. OPENCODE PROVIDER — спеціалізований для коду
# =====================================================================
class OpenCode(AIModel):
    def __init__(self, Model="code-model"):
        self.Name = "opencode"
        self.Model = Model
        self.Host = "api.opencode.ai"
        self.Path = "/v1/code/completions"
        self.Token = str(Runtime.get("OPENCODE_API_KEY", Runtime.get("OPENCODE API KEY", ""))).strip()
        self.Available = False

    def CheckAvailable(self):
        if self.Token:
            self.Available = True
        return self.Available

    def Chat(self, Messages, Tools=None):
        if not self.Token:
            return "[OpenCode Standby: Set OPENCODE_API_KEY. Model: " + self.Model + "]"
        MaxTok = int(getattr(self, "MaxTokens", 600))
        Payload = {"model": self.Model, "messages": Messages, "max_tokens": MaxTok}
        Headers = {"Content-Type": "application/json", "Authorization": "Bearer " + self.Token}
        Raw = self.NetworkRequest(
            self.Host,
            self.Path,
            Payload,
            Headers,
            Ssl=True,
            Timeout=120,
            Retries=1,
        )
        if not Raw:
            return "[OpenCode: no response]"
        return self.ParseResponse(Raw) or "[OpenCode: empty response]"

    def ParseResponse(self, RawBody: str) -> str:
        JsonMod = LCARS.Import("json")
        if not RawBody or not JsonMod:
            return ""
        if RawBody.startswith("[HTTP"):
            return RawBody
        try:
            Data = JsonMod.loads(RawBody)
        except Exception:
            return RawBody
        Choices = Data.get("choices", [])
        if not Choices:
            return ""
        MsgObj = Choices[0].get("message", {})
        RawContent = MsgObj.get("content")
        Content = str(RawContent or "")
        return Content

    def GetInfo(self):
        return {
            "name": self.Name,
            "model": self.Model,
            "available": self.CheckAvailable(),
        }
# ====================================================================
# 10. AI PROVIDER MANAGER — центральний маршрутизатор
# ====================================================================
class AIProviderManager(Directive):
    Instance = None

    def __new__(cls):
        if cls.Instance is None:
            cls.Instance = super().__new__(cls)
            cls.Instance.Backends = []
            cls.Instance.ActiveBackend = None
            cls.Instance.InitializeBackends()
        return cls.Instance

    def InitializeBackends(self):
        self.Backends = [
            QVAC(),
            LocalLLM(),
            GROQwen(),
            Mistral(),
            Astra(),
            OpenRouter(),
            OpenCode(),
        ]
        for Backend in self.Backends:
            if Backend.CheckAvailable():
                self.ActiveBackend = Backend
                break
        if not self.ActiveBackend and self.Backends:
            self.ActiveBackend = self.Backends[0]

    @classmethod
    def GetInstance(cls):
        if not hasattr(cls, '_Instance') or cls._Instance is None:
            cls._Instance = cls()
        return cls._Instance

    def SwitchModel(self, Name: str) -> bool:
        for Backend in self.Backends:
            if Backend.Name == Name or Backend.Model == Name:
                self.ActiveBackend = Backend
                return True
        return False

    def GetStatus(self) -> dict:
        AvailableBackends = [b.Name for b in self.Backends if b.CheckAvailable()]
        return {
            "active": self.ActiveBackend.Name if self.ActiveBackend else "none",
            "available": AvailableBackends,
            "all": [b.Name for b in self.Backends],
        }
    
    def Initialize(self):
        self.Initialized = True

    def Route(self, Messages, Tools=None) -> str:
        if not self.ActiveBackend:
            return "[AI Provider: No active backend]"
        return self.ActiveBackend.Chat(Messages, Tools)
    
    def GetProvider(self):
        return self

# =====================================================================
# 11. AI PROVIDER — статичний доступ
# =====================================================================
def AIProvider():
    return AIProviderManager()

# Backward compatibility alias
AIProviderClass = AIProvider