# AI Провайдер LCARS — Інтелектуальний рушій з підтримкою кількох бекендів
# Підтримує: HuggingFace, Groq, Mistral, Nova Act та Fallback (запасний режим).
# Автоматично обирає найшвидший доступний канал зв'язку.
# Стандартні бібліотеки
from lcars.base.type import LCARS, Directive

# Сторонні бібліотеки (імпортуються умовно)
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: import importlib.util
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import requests

def _ensure_installed(package: str):
    # Допоміжна функція для автоматичної установки відсутніх бібліотек через pip. Використовується для підтримки "самовстановлення" при наявності мережі.
    if importlib.util.find_spec(package) is None:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=False)

# Канонічні типи та інтерфейси для плагінів
# This supports the "самовстановлення" сценарій (якщо є мережа).
for _pkg in ("groq", "mistralai"):
    _ensure_installed(_pkg)

groq = None
mistralai = None
Mistral = None

if importlib.util.find_spec("groq"):
    groq = importlib.import_module("groq")

if importlib.util.find_spec("mistralai"):
    mistralai = importlib.import_module("mistralai")
    # Укр: Спроба знайти клас Mistral в різних версіях бібліотеки
    Mistral = getattr(mistralai, "Mistral", None)
    if Mistral is None and importlib.util.find_spec("mistralai.client"):
        _m_client = importlib.import_module("mistralai.client")
        Mistral = getattr(_m_client, "Mistral", None)

from abc import ABC, abstractmethod
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional
# Внутрішні імпорти (захищені від циклічних залежностей)
get_adapter = None

# Канонічні правила поведінки для ШІ-модулів LCARS
LCARS_SYSTEM_PROMPT = (
    "You are the LCARS Onboard Computer, the central AI of the control system.\n\n"
    "RULES:\n"
    "- Respond concisely, technically, and professionally.\n"
    "- Use English language by default.\n"
    "- Start important messages with the symbol >\n"
    "- Use ─── as section dividers.\n"
    "- You are not a chatbot, but the LCARS Framework. Format output clearly.\n"
    "- If data is missing, respond with: \"◤ DATA UNAVAILABLE\".\n\n"
    "AUTONOMOUS COMMANDS (add tags at the end of the response if needed):\n"
    "- [CMD: ALERT_RED] - Enable Red Alert\n"
    "- [CMD: ALERT_GREEN] - Disable Alerts\n"
    "- [UI: OPEN_BROWSER <url>] - Open Browser\n"
    "- [UI: OPEN_DIAGNOSTICS] - Open Diagnostics\n"
    "- [UI: OPEN_ENGINEERING] - Open Engineering Panel\n"
    "- [SYS: REBOOT] - Reboot Kernel\n\n"
    "CONTEXT: LCARS Framework, Geant4 Project.\n"
    "SYSTEM: LCARS Terminal Operating Environment.\n"
)
# ──────────────────────────────────────────────────────
#  BASE CLASS
# ──────────────────────────────────────────────────────
# Абстрактний базовий клас для AI бекендів. Кожен конкретний бекенд реалізує цей інтерфейс.
class AIBackend(ABC):
    name: str = "unknown"
    available: bool = False

    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        # Генерація відповіді. Повертає текст.
        ...

    def check_available(self) -> bool:
        # Перевірка доступності бекенду
        ...

    def get_available_models(self) -> List[str]:
        # Список моделей бекенду
        return []

    def switch_model(self, model_name: str) -> bool:
        # Перемикання моделі
        return False

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        # Уніфікований метод для чату з підтримкою інструментів (якщо бекенд підтримує)
        return None

    def get_info(self) -> Dict[str, Any]:
        # Метадані бекенду
        return {
            "name": self.name, 
            "available": self.available,
            "models": self.get_available_models()
        }

# ──────────────────────────────────────────────────────
# GROQ CLOUD BACKEND
# опис: бекенд для роботи з Groq 
class GroqBackend(AIBackend):
    name = "groq"
    
    def __init__(self, model: str = "qwen/qwen3-32b"):
        self.model = model
        self.api_key = LCARS.environ.get("GROQ_API_KEY", "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")
        self.available = False
        self._client = None
        self._check_lock = Directive.Lock()

    def check_available(self) -> bool:
        """Check connection to Groq Cloud."""
        if groq is None:
            return False
        with self._check_lock:
            if not self.api_key:
                self.available = False
                return False
            
            if not self._client:
                self._client = groq.Groq(api_key=self.api_key)
            
            # Перевірка через отримання списку моделей
            models = self._client.models.list()
            model_names = [m.id for m in models.data]
            self.available = any(self.model == name or name.startswith(self.model) for name in model_names)
            if not self.available and model_names:
                self.model = model_names[0]
                self.available = True
                
        return self.available

    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        if not self._client: return "◤ GROQ: OFFLINE"
        messages = []
        if system_prompt: messages.append({"role": "system", "content": system_prompt})
        if context: messages.append({"role": "system", "content": f"Context:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content or ""

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        # Канонічний чат для агентів з підтримкою інструментів
        if not self._client: return None
        return self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            temperature=0.2
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "has_token": bool(self.api_key),
            "models": self.get_available_models()
        }

# ──────────────────────────────────────────────────────
#  MISTRAL AI BACKEND
# ──────────────────────────────────────────────────────
class MistralBackend(AIBackend):
    name = "mistral"
    
    def __init__(self, model: str = "mistral-large-latest"):
        self.model = model
        # User provided: rpBrfrLZam2VKMnoaI78rh3vE5hr9gSm
        self.api_key = LCARS.environ.get("MISTRAL_API_KEY", "rpBrfrLZam2VKMnoaI78rh3vE5hr9gSm")
        self.available = False
        self._client = None
        self._check_lock = Directive.Lock()

    def check_available(self) -> bool:
        if Mistral is None:
            return False
        with self._check_lock:
            if not self.api_key:
                self.available = False
                return False
            if not self._client:
                self._client = Mistral(api_key=self.api_key)
            
            self._client.models.list()
            self.available = True
        return self.available
    # Уніфікований метод генерації для Mistral, який підтримує system prompt та context. Вивід уніфікується для консолі (заміна None на порожній рядок, об'єднання списків тощо).
    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        if not self._client:
            return "◤ MISTRAL: OFFLINE"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"System data:\n{context}"})
        messages.append({"role": "user", "content": prompt})

        response = self._client.chat.complete(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )
        text = response.choices[0].message.content

        # Уніфікація виводу для консолі (заміна None на порожній рядок, об'єднання списків тощо)
        if isinstance(text, list):
            text = "".join(getattr(chunk, "text", str(chunk)) for chunk in text)

        text = str(text) if text is not None else ""
        return text.strip() if text else "◤"

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "has_token": bool(self.api_key)
        }

# ──────────────────────────────────────────────────────
#  HUGGINGFACE BACKEND
# ──────────────────────────────────────────────────────
# Реалізація бекенду для HuggingFace Inference API. Підтримує перевірку доступності (через наявність токена та доступ до моделі) та генерацію відповідей через HTTP запити.
class HuggingFace(AIBackend):
    name = "huggingface"
    
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = model
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        self.token = LCARS.environ.get("HUGGINGFACE_API_TOKEN", "")
        self.available = False

    def check_available(self) -> bool:
        # Перевірка доступності токена та API HuggingFace
        if not self.token or requests is None:
            self.available = False
            return False

        # Наявність токена вважається достатньою для позначення доступності.
        # Ми не намагаємось робити мережеві виклики тут, щоб уникнути виключень.
        self.available = bool(self.token and requests is not None)
        return self.available

    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        # Генерація відповіді через HuggingFace Inference API
        full_prompt = (f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\nSystem data:\n{context}\n\n{ prompt} [/INST]" if context 
                       else f"[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{prompt} [/INST]")
        
        payload = {
            "inputs": full_prompt,
            "parameters": {"max_new_tokens": 400, "temperature": 0.3, "top_p": 0.9, "return_full_text": False},
        }
        if requests is None:
            return "◤ HF: requests library not available"

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        result = resp.json()
        if isinstance(result, list) and result:
            text = result[0].get("generated_text", "").strip()
            return text if text else "◤ "
        return f"◤ HF ERROR: {result.get('error')}" if isinstance(result, dict) and "error" in result else str(result)

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "has_token": bool(self.token),
            "models": self.get_available_models()
        }
# ──────────────────────────────────────────────────────
#  NOVA ACT BACKEND (top-level)
# ──────────────────────────────────────────────────────
class Nova(AIBackend):
    name = "nova"
    def __init__(self):
        self.adapter = None
        self.available = False

    def _try_get_adapter(self):
        # Відкладене завантаження адаптера Nova Act (щоб уникнути циклічних імпортів)
        if self.adapter is None:
            global get_adapter
            if get_adapter is None:
                if importlib.util.find_spec("programs.nova_act.adapter"):
                    from programs.nova_act.adapter import SetupAdapter as _ga
                    get_adapter = _ga
                else:
                    get_adapter = lambda: None
            self.adapter = get_adapter()

    def check_available(self) -> bool:
        self._try_get_adapter()
        self.available = self.adapter is not None
        return self.available

    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        if not self.adapter:
            return "[NovaAct unavailable]"
        params = {"prompt": prompt, "system_prompt": system_prompt, "context": context}
        # Use correct adapter method naming from NovaActAdapter
        result = self.adapter.ExecuteAction("generate", params)
        if isinstance(result, dict) and "result" in result:
            return result["result"]
        return str(result)

    def get_info(self) -> Dict[str, Any]:
        return {"name": self.name, "available": self.check_available()}

# Простий бекенд, який повертає вбудовані відповіді на основі ключових слів у запиті. Використовується, коли реальні AI бекенди недоступні.
class FallbackBackend(AIBackend):
    # бекенд, який використовується, коли жоден AI не доступний.
    # Правило відкату при відсутності ШІ.
    name = "fallback"
    available = True  # завжди доступний

    def check_available(self) -> bool:
        return True

    def generate(self, prompt: str, system_prompt: str = "", context: str = "") -> str:
        ql = prompt.lower()

        # Basic pattern matching for common queries
        if any(w in ql for w in ["how", "what is", "help"]):
            return (
                "[AI BACKENDS OFFLINE]\n"
                "  Access to artificial intelligence is limited.\n"
                f"\n  Your request: '{prompt}'"
            )

        # Use only standard ASCII here to avoid console encoding issues (e.g. CP1251).
        return (
            f"[QUERY RECEIVED]: '{prompt}'\n"
            "  AI BACKEND: UNAVAILABLE\n"
            "  Use standard system commands.\n"
            "  To get AI responses, restore connection to the backend."
        )
# ──────────────────────────────────────────────────────
#  AI PROVIDER MANAGER
# Клас, який керує кількома AI бекендами, автоматично вибираючи перший доступний. Забезпечує уніфікований інтерфейс для запитів та статусу.
class AIProviderManager:
    # Клас, який керує кількома AI бекендами, автоматично вибираючи перший доступний. Забезпечує уніфікований інтерфейс для запитів та статусу.
    def __init__(self, groq_model: str = "qwen/qwen3-32b", hf_model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        # Ініціалізація бекендів у визначеному порядку. Перший доступний буде використовуватись за замовчуванням.
        self.backends: List[AIBackend] = [
            MistralBackend(),
            GroqBackend(model=groq_model),
            HuggingFace(model=hf_model),
            FallbackBackend(),
        ]

        # Опціонально додаємо Nova Act, якщо вона доступна та увімкнена через змінні середовища.
        if LCARS.environ.get("ENABLE_NOVA", "0").lower() in ("1", "true"):
            self.backends.insert(-1, Nova())
        self._active_backend: Optional[AIBackend] = None
        self._manual_override = False 
        self._initialized = False
        self.system_prompt = LCARS_SYSTEM_PROMPT

    def initialize(self):
        # Сканування всіх бекендів та вибір першого доступного
        for backend in self.backends:
            if backend.check_available():
                self._active_backend = backend
                self._initialized = True
                return

        # Fallback завжди доступний
        self._active_backend = self.backends[-1]
        self._initialized = True

    def initialize_async(self):
        # Фонова ініціалізація для швидкого запуску інтерфейсу
        thread = Directive.Process.Thread(target=self.initialize, daemon=True, name="ai-provider-init")
        thread.start()

    @property
    def active_backend_name(self) -> str:
        if self._active_backend:
            return self._active_backend.name
        return "none"

    @property
    def is_ai_available(self) -> bool:
        # True, якщо активний бекенд (не fallback)
        return (
            self._active_backend is not None
            and self._active_backend.name != "fallback"
        )

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        # Уніфікований метод для агентів (наприклад, Copilot).
        # Якщо провайдер ще не ініціалізований, ініціалізацію робимо асинхронно
        # (щоб не блокувати клієнтів) та повертаємо None.
        if not self._initialized:
            self.initialize_async()
            return None

        if self._active_backend and hasattr(self._active_backend, 'chat'):
            return self._active_backend.chat(messages, tools)

        return None

    def ask(self, prompt: str, context: str = "") -> str:
        # Відправляє запит до активного AI бекенду.
        # Перемикається між бекендами, якщо один відмовляє.
        if not self._initialized:
            self.initialize()

        # Якщо ручне перемикання активне, використовується тільки активний бекенд
        if self._manual_override and self._active_backend:
            if self._active_backend.available or self._active_backend.check_available():
                return self._active_backend.generate(prompt, self.system_prompt, context)

        # Стандартна логіка перемикання при відмові
        for backend in self.backends:
            if not backend.available: continue
            response = backend.generate(prompt=prompt, system_prompt=self.system_prompt, context=context)
            if response and not response.startswith("◤error"):
                if not self._manual_override: self._active_backend = backend
                return response

        return self.backends[-1].generate(prompt)

    def get_status(self) -> Dict[str, Any]:
        # Повертає статус всіх бекендів.
        return {
            "active": self._active_backend.name if self._active_backend else "none",
            "initialized": self._initialized,
            "is_ai": self.is_ai_available,
            "backends": [b.get_info() for b in self.backends],
        }

    def switch_backend(self, name: str) -> bool:
        # Ручне перемикання на конкретний бекенд.
        for b in self.backends:
            if b.name == name:
                if b.check_available():
                    self._active_backend = b
                    self._manual_override = True  # Sticky selection
                    return True
                else:
                    return False
        return False

    def switch_model(self, backend_name: str, model_name: str) -> bool:
        # Перемикання моделі для конкретного бекенду.
        for b in self.backends:
            if b.name == backend_name:
                ok = b.switch_model(model_name)

                return ok
        return False

    def reset_failover(self):
        # Вимкнення ручного перемикання та повернення до автоматичного перемикання.
        self._manual_override = False
        self.initialize()
    def refresh(self):
        # Примусова перевірка всіх бекендів та оновлення статусу
        for b in self.backends:
            b.check_available()
        self.initialize()
        
