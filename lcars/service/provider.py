
import importlib
import importlib.util
import json
from typing import Any, Dict, List, Optional
from lcars.engineering.telemetry import EmitTelemetry
from lcars.system.environment import Runtime
from lcars.base.type import LCARS, Directive
from lcars.base.register import registry

requests = LCARS.Network.Request

groq = None
adapterFactory = None

# Базова форма для всіх AI бекендів.
class AIModel:
    name: str = "unknown"
    available: bool = False

    # Генерація відповіді за промптом
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "") -> str:
        return ""

    # Перевірка доступності бекенду
    def checkAvailable(self) -> bool:
        return False

    # Отримання списку доступних моделей
    def getAvailableModels(self) -> List[str]:
        return []

    # Перемикання моделі за назвою
    def switchModel(self, modelName: str) -> bool:
        return False

    # Чат з повідомленнями та інструментами
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        return None

    # Отримання інформації про бекенд
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name, 
            "available": self.available,
            "models": self.getAvailableModels()
        }

# Стандартний промпт для LCARS
PROMPT = (
    "You are the LCARS Onboard Computer, the central AI of the control system.\n\n"
    "RULES:\n"
    "- Respond concisely, technically, and professionally.\n"
    "- Use English language by default.\n"
    "- Start important messages with the symbol >\n"
    "- Use --- as section dividers.\n"
    "- You are not a chatbot, but the LCARS Framework. Format output clearly.\n"
    "- If data is missing, respond with: \"DATA UNAVAILABLE\".\n\n"
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

# Бекенд Mistral для офіційного API та HuggingFace fallback.
class Mistral(AIModel):
    name = "mistral"

    # Ініціалізація бекенду Mistral
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = model
        self.token = Runtime.get("MISTRAL_API_KEY", Runtime.get("MISTRAL API KEY", ""))
        self.available = False
        
        # Визначення URL API залежно від типу токена
        if self.token and not self.token.startswith("hf_"):
            self.apiUrl = "https://api.mistral.ai/v1/chat/completions"
            self.is_official = True
        else:
            self.apiUrl = f"https://api-inference.huggingface.co/models/{model}"
            self.is_official = False

    # Перевірка доступності бекенду Mistral
    def checkAvailable(self) -> bool:
        if not self.token or requests is None:
            self.available = False
            return False

        self.available = True
        return self.available

    # Генерація відповіді через Mistral API
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "") -> str:
        if requests is None:
            return "LCARS: MISTRAL: requests library not available"

        # Офіційний API Mistral
        if self.is_official:
            messages = []
            if systemPrompt:
                messages.append({"role": "system", "content": systemPrompt})
            if context:
                messages.append({"role": "system", "content": f"Context data:\n{context}"})
            messages.append({"role": "user", "content": prompt})
            
            # Визначення назви моделі для API
            model_name = self.model
            if "/" in model_name:
                if "codestral" in model_name.lower():
                    model_name = "codestral-latest"
                else:
                    model_name = "mistral-medium-latest"
            
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1024
            }
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            resp = requests.post(self.apiUrl, json=payload, headers=headers, timeout=30)
            result = resp.json()
            # Обробка відповіді від офіційного API
            if "choices" in result and result["choices"]:
                text = result["choices"][0]["message"]["content"].strip()
                return text if text else "LCARS: "
            return f"LCARS: MISTRAL ERROR: {result.get('error')}" if isinstance(result, dict) and "error" in result else str(result)
        else:
            # HuggingFace fallback API
            fullPrompt = (f"[INST] <<SYS>>\n{systemPrompt}\n<</SYS>>\n\nSystem data:\n{context}\n\n{ prompt} [/INST]" if context 
                           else f"[INST] <<SYS>>\n{systemPrompt}\n<</SYS>>\n\n{prompt} [/INST]")
            
            payload = {
                "inputs": fullPrompt,
                "parameters": {"max_new_tokens": 400, "temperature": 0.3, "top_p": 0.9, "return_full_text": False},
            }
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            resp = requests.post(self.apiUrl, json=payload, headers=headers, timeout=30)
            result = resp.json()
            # Обробка відповіді від HuggingFace
            if isinstance(result, list) and result:
                text = result[0].get("generated_text", "").strip()
                return text if text else "LCARS: "
            return f"LCARS: MISTRAL ERROR: {result.get('error')}" if isinstance(result, dict) and "error" in result else str(result)

    # Чат з повідомленнями через Mistral
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        if not self.available:
            return {"role": "assistant", "content": "[Mistral unavailable]"}
            
        # Офіційний API Mistral
        if self.is_official:
            model_name = self.model
            if "/" in model_name:
                if "codestral" in model_name.lower():
                    model_name = "codestral-latest"
                else:
                    model_name = "mistral-medium-latest"
                    
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 1024
            }
            if tools:
                payload["tools"] = tools
                
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            resp = requests.post(self.apiUrl, json=payload, headers=headers, timeout=30)
            result = resp.json()
            # Обробка відповіді від офіційного API
            if "choices" in result and result["choices"]:
                choice = result["choices"][0]
                msg = choice.get("message", {})
                return {
                    "role": "assistant",
                    "content": msg.get("content"),
                    "tool_calls": msg.get("tool_calls")
                }
            return {"role": "assistant", "content": f"LCARS: MISTRAL ERROR: {result.get('error', result)}"}
        else:
            # HuggingFace fallback API
            prompt = ""
            for m in messages:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role == "system":
                    prompt += f"[INST] <<SYS>>\n{content}\n<</SYS>>\n\n"
                elif role == "user":
                    prompt += f"{content} [/INST]\n"
                elif role == "assistant":
                    prompt += f"{content} </s>\n[INST] "
            
            resp = self.generate(prompt)
            if resp.startswith("LCARS: MISTRAL ERROR") or resp.startswith("LCARS: MISTRAL CONNECTION ERROR"):
                return {"role": "assistant", "content": resp}
            return {"role": "assistant", "content": resp}

    # Отримання інформації про бекенд Mistral
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "hasToken": bool(self.token),
            "models": ["mistralai/Mistral-7B-Instruct-v0.2", "mistralai/Codestral-22B-v0.1"]
        }

# Бекенд Groq для швидких віддалених відповідей.
class GROQwen(AIModel):
    name = "groqwen"

    # Ініціалізація бекенду Groq
    def __init__(self, model: str = "qwen/qwen3.6-27b"):
        self.model = model
        self.token = Runtime.get("GROQ_API_KEY", Runtime.get("GROQ API KEY", ""))
        self.available = False
        self.client = None

    # Перевірка доступності бекенду Groq
    def checkAvailable(self) -> bool:
        global groq
        if groq is None and importlib.util.find_spec("groq") is not None:
            groq = importlib.import_module("groq")

        if not self.token or groq is None:
            self.available = False
            return False
        # Ініціалізація клієнта Groq якщо ще не створений
        if self.client is None:
            self.client = groq.Groq(api_key=self.token)
        self.available = True
        return self.available

    # Генерація відповіді через Groq API
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "") -> str:
        if not self.checkAvailable() or self.client is None:
            return "[Groq unavailable]"
        
        messages = []
        if systemPrompt:
            messages.append({"role": "system", "content": systemPrompt})
        if context:
            messages.append({"role": "system", "content": f"Context data:\n{context}"})
        messages.append({"role": "user", "content": prompt})

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.3,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content

    # Чат з повідомленнями через Groq
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        if not self.client:
            self.checkAvailable()
        if not self.client:
            return {"role": "assistant", "content": "[Groq unavailable]"}
        kwargs = {
            "messages": messages,
            "model": self.model,
            "temperature": 0.3,
            "max_tokens": 1024,
        }
        # Додавання інструментів якщо вони є
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        chat_completion = self.client.chat.completions.create(**kwargs)
        return chat_completion

    # Отримання інформації про бекенд Groq
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "hasToken": bool(self.token),
            "models": [self.model, "qwen/qwen3.6-27b", "qwen/qwen3-32b"]
        }

# Бекенд Gemma для локального виконання через transformers.
class GemmaSpark(AIModel):
    name = "gemma"
    available = False

    MODEL = {
        "gemma4-4b": "google/gemma-3-1b-it",
        "gemma4-9b": "google/gemma-3-1b-it",
        "gemma4-12b": "google/gemma-3-1b-it",
        "gemma4-26b": "google/gemma-3-1b-it",
    }

    # Ініціалізація бекенду Gemma
    def __init__(self, model: str = "gemma4-4b", enableThinking: bool = False):
        self.modelKey = model
        self.modelPath = self.MODEL.get(model, self.MODEL["gemma4-4b"])
        self.enableThinking = enableThinking
        self.processor = None
        self.model = None
        self.device = None
        self.token = Runtime.get("HF_TOKEN", Runtime.get("HUGGINGFACE_TOKEN", ""))
        self.checkDeps()

    # Перевірка залежностей (transformers, torch)
    def checkDeps(self):
        tx = importlib.util.find_spec("transformers") is not None
        tc = importlib.util.find_spec("torch") is not None
        self.available = tx and tc

    # Перевірка доступності бекенду Gemma
    def checkAvailable(self) -> bool:
        if not self.available:
            self.checkDeps()
        # gemma-3 — gated модель, потрібен HF-токен; без нього докачка впаде/зависне.
        return bool(self.available) and bool(self.token)

    # Завантаження моделі Gemma
    def loadModel(self) -> bool:
        if self.model is not None:
            return True
        if not self.checkAvailable():
            return False

        torch = importlib.import_module("torch")
        transformers = importlib.import_module("transformers")

        AutoTokenizer = getattr(transformers, "AutoTokenizer")
        AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM")

        EmitTelemetry("Gemma", f"Loading model: {self.modelPath}")
        loadKwargs = {}
        if self.token:
            loadKwargs["token"] = self.token
        self.processor = AutoTokenizer.from_pretrained(
            self.modelPath,
            **loadKwargs
        )
        EmitTelemetry("Gemma", "Tokenizer loaded. Loading model weights.")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.modelPath,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            **loadKwargs
        )
        self.device = next(self.model.parameters()).device
        # Перевірка чи пристрій не meta (віртуальний)
        if "meta" in str(self.device):
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
        EmitTelemetry("Gemma", f"Model active on {self.device}")
        return True

    # Генерація відповіді через Gemma
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "", maxTokens: int = 1024) -> str:
        if not self.loadModel():
            return "[Gemma: Model not loaded]"

        messages = []
        if systemPrompt:
            messages.append({"role": "system", "content": systemPrompt})
        if context:
            prompt = f"Context: {context}\n\n{prompt}"
        messages.append({"role": "user", "content": prompt})

        if self.processor is None or self.model is None:
            return "[Gemma: Model not initialized]"

        chatTemplate = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=chatTemplate, return_tensors="pt").to(self.device)

        generateKwargs = {"max_new_tokens": maxTokens, "do_sample": True}
        # Налаштування параметрів генерації для режиму thinking
        if self.enableThinking:
            generateKwargs["temperature"] = 0.7
            generateKwargs["top_p"] = 0.9

        from transformers import TextStreamer
        streamer = TextStreamer(self.processor, skip_prompt=True, skip_special_tokens=True)
        generateKwargs["streamer"] = streamer

        outputs = self.model.generate(**inputs, **generateKwargs)
        response = self.processor.batch_decode(outputs[:, inputs["input_ids"].shape[-1]:], skip_special_tokens=True)[0]
        return response

    # Чат з повідомленнями через Gemma
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, maxTokens: int = 1024) -> Dict[str, Any]:
        if not self.loadModel():
            return {"role": "assistant", "content": "[Gemma: Model not loaded]"}

        if self.processor is None or self.model is None:
            return {"role": "assistant", "content": "[Gemma: Model not initialized]"}

        chatTemplate = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.processor(text=chatTemplate, return_tensors="pt").to(self.device)

        generateKwargs = {"max_new_tokens": maxTokens, "do_sample": True}
        # Налаштування параметрів генерації для режиму thinking
        if self.enableThinking:
            generateKwargs["temperature"] = 0.7
            generateKwargs["top_p"] = 0.9

        from transformers import TextStreamer
        streamer = TextStreamer(self.processor, skip_prompt=True, skip_special_tokens=True)
        generateKwargs["streamer"] = streamer

        outputs = self.model.generate(**inputs, **generateKwargs)
        response = self.processor.batch_decode(outputs[:, inputs["input_ids"].shape[-1]:], skip_special_tokens=True)[0]

        return {"role": "assistant", "content": response}

    # Увімкнення/вимкнення режиму thinking
    def setThinking(self, enabled: bool):
        self.enableThinking = enabled

    # Перемикання моделі Gemma
    def switchModel(self, modelName: str) -> bool:
        if modelName in self.MODEL:
            nextPath = self.MODEL[modelName]
            self.modelKey = modelName
            # Скидання моделі якщо шлях змінився
            if nextPath != self.modelPath:
                self.modelPath = nextPath
                self.model = None
                self.processor = None
            return True
        return False

    # Отримання списку доступних моделей Gemma
    def getAvailableModels(self) -> List[str]:
        return list(self.MODEL.keys())

    # Отримання інформації про бекенд Gemma
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.modelKey,
            "path": self.modelPath,
            "available": self.checkAvailable(),
            "loaded": self.model is not None,
            "thinking": self.enableThinking,
            "models": self.getAvailableModels()
        }


# Бекенд Nova (QVAC SDK) вилучено: QVAC вимагає Vulkan >= 1.4 навіть для CPU-
# інференсу, чого немає на даній машині, плюс реєстр моделей QVAC недоступний.
# Вихідники адаптера та хоста збережено в archive/qvac-sdk/.

# Локальний CPU-бекенд на вже встановлених torch/transformers.
# Використовує маленьку ВІДКРИТУ інструктивну модель (без gated-токена, без Vulkan),
# тож працює офлайн на слабкому залізі. Модель докачується з HF при першому запуску.
class LocalLLM(AIModel):
    name = "localllm"
    available = False

    MODELS = {
        "qwen0.5": "Qwen/Qwen2.5-0.5B-Instruct",
        "qwen1.5": "Qwen/Qwen2.5-1.5B-Instruct",
        "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    }

    # Ініціалізація локального CPU-бекенду
    def __init__(self, model: str = "qwen0.5", maxTokens: int = 256):
        self.modelKey = model
        self.modelId = self.MODELS.get(model, self.MODELS["qwen0.5"])
        self.maxTokens = maxTokens
        self.tokenizer = None
        self.model = None
        self.checkDeps()

    # Перевірка залежностей (transformers, torch)
    def checkDeps(self):
        tx = importlib.util.find_spec("transformers") is not None
        tc = importlib.util.find_spec("torch") is not None
        self.available = tx and tc

    # Перевірка доступності локального бекенду
    def checkAvailable(self) -> bool:
        if not self.available:
            self.checkDeps()
        return bool(self.available)

    # Завантаження локальної моделі
    def loadModel(self) -> bool:
        if self.model is not None:
            return True
        if not self.checkAvailable():
            return False
        EmitTelemetry("LocalLLM", f"Loading local model: {self.modelId}")
        transformers = importlib.import_module("transformers")
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(self.modelId)
        self.model = transformers.AutoModelForCausalLM.from_pretrained(self.modelId)
        EmitTelemetry("LocalLLM", "Local model ready (CPU).")
        return True

    # Генерація відповіді через локальну модель
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "", maxTokens: int = None) -> str:
        if not self.loadModel():
            return "[LocalLLM: model not loaded]"
        maxTokens = maxTokens or self.maxTokens
        messages = []
        if systemPrompt:
            messages.append({"role": "system", "content": systemPrompt})
        if context:
            messages.append({"role": "system", "content": "Context:\n" + context})
        messages.append({"role": "user", "content": prompt})
        # Застосування chat template, якщо підтримується
        if hasattr(self.tokenizer, 'apply_chat_template'):
            text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            text = prompt
        inputs = self.tokenizer(text, return_tensors="pt")
        import torch
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=maxTokens,
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        resp = self.tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return resp.strip()

    # Отримання списку доступних моделей
    def getAvailableModels(self) -> List[str]:
        return list(self.MODELS.keys())

    # Отримання інформації про локальний бекенд
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.modelKey,
            "modelId": self.modelId,
            "available": self.checkAvailable(),
            "loaded": self.model is not None,
        }


# Менеджер, який вибирає доступний бекенд і тримає його як основний.
class AIProviderManager:
    # Ініціалізація менеджера провайдерів AI
    def __init__(self):
        from typing import cast
        gemmaModel = cast(str, Runtime.get("GEMMA_MODEL", "gemma4-4b"))
        groqModel = cast(str, Runtime.get("GROQ_MODEL", "qwen/qwen3.6-27b"))
        mistralModel = cast(str, Runtime.get("MISTRAL_MODEL", "mistralai/Codestral-22B-v0.1"))
        self.backendList: List[AIModel] = [
            LocalLLM(),
            GemmaSpark(model=gemmaModel),
            GROQwen(model=groqModel),
            Mistral(model=mistralModel),
        ]
        self.activeBackend: Optional[AIModel] = None
        self.manualOverride = False
        self.initialized = False
        self.systemPrompt = PROMPT
        
    # Властивість для отримання списку бекендів
    @property
    def backends(self) -> List[AIModel]:
        return self.backendList

    # Ініціалізація: пошук першого доступного бекенду
    def initialize(self):
        for backend in self.backends:
            # Перевірка доступності без використання try/except
            available = False
            if hasattr(backend, 'checkAvailable'):
                available = backend.checkAvailable()
            if available:
                self.activeBackend = backend
                self.initialized = True
                return

        self.activeBackend = self.backends[-1]
        self.initialized = True

    # Асинхронна ініціалізація в окремому потоці
    def initializeAsync(self):
        import threading
        thread = threading.Thread(target=self.initialize, daemon=True, name="ai-provider-init")
        thread.start()

    # Властивість для отримання назви активного бекенду
    @property
    def activeBackendName(self) -> str:
        if self.activeBackend:
            return self.activeBackend.name
        return "none"

    # Властивість для перевірки доступності AI
    @property
    def isAiAvailable(self) -> bool:
        return (
            self.activeBackend is not None
            and self.activeBackend.name != "fallback"
        )

    # Чат з повідомленнями через доступний бекенд
    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Any:
        if not self.initialized:
            self.initializeAsync()
            return None

        # Пошук першого бекенду з успішною відповіддю
        for backend in self.backends:
            if not backend.available:
                continue
            if hasattr(backend, 'chat'):
                response = backend.chat(messages, tools)
                
                # Перевірка чи відповідь є помилкою
                is_error = False
                if isinstance(response, dict):
                    content = response.get("content", "")
                    if "[Gemma: Model not loaded]" in content or "[Gemma: Model not initialized]" in content or "[Groq unavailable]" in content or "LCARS: GROQ ERROR" in content:
                        is_error = True
                        backend.available = False
                elif isinstance(response, str) and (response.startswith("error") or "[Model not loaded]" in response):
                    is_error = True
                    backend.available = False
                elif response is None:
                    is_error = True
                    
                if not is_error:
                    if not self.manualOverride: 
                        self.activeBackend = backend
                    return response

        # Fallback на останній бекенд
        if self.backends and hasattr(self.backends[-1], 'chat'):
            return self.backends[-1].chat(messages, tools)
        return {"role": "assistant", "content": "ALL AI SYSTEMS OFFLINE"}

    # Генерація відповіді через доступний бекенд
    def ask(self, prompt: str, context: str = "") -> str:
        if not self.initialized:
            self.initialize()

        # Якщо встановлено ручний пріоритет — використовуємо вказаний бекенд
        if self.manualOverride and self.activeBackend:
            if self.activeBackend.available or self.activeBackend.checkAvailable():
                if hasattr(self.activeBackend, 'generate'):
                    response = self.activeBackend.generate(prompt, self.systemPrompt, context)
                    if response is not None:
                        return response

        lastError = "[AI: Provider offline]"
        # Перебір усіх бекендів у порядку пріоритету
        for backend in self.backends:
            if not backend.available: continue
            if hasattr(backend, 'generate'):
                response = backend.generate(prompt=prompt, systemPrompt=self.systemPrompt, context=context)
            else:
                continue
            if response and not str(response).startswith("error"):
                if not self.manualOverride: self.activeBackend = backend
                return response
            if str(response).startswith("error"):
                lastError = str(response)

        # Fallback на останній бекенд
        if hasattr(self.backends[-1], 'generate'):
            return self.backends[-1].generate(prompt)
        return lastError

    # Отримання статусу менеджера провайдерів
    def getStatus(self) -> Dict[str, Any]:
        return {
            "active": self.activeBackendName,
            "initialized": self.initialized,
            "is_ai": self.isAiAvailable,
            "backends": [b.getInfo() for b in self.backends],
        }

    # Генерація відповіді через вказану модель
    def generateWithModel(self, prompt: str, modelName: str, systemPrompt: str = "", context: str = "") -> str:
        # Пошук бекенду за назвою або моделлю
        for backend in self.backends:
            aliases = getattr(backend, "aliases", [])
            if backend.name == modelName or modelName in aliases or modelName in backend.getAvailableModels():
                if backend.available or backend.checkAvailable():
                    return backend.generate(prompt, systemPrompt, context)
        return f"[Model {modelName} not available]"

    # Отримання списку всіх доступних моделей
    def listAvailableModels(self) -> List[str]:
        models = []
        for backend in self.backends:
            if backend.available:
                models.extend(backend.getAvailableModels())
        return models

    # Спроба переключити активний AI-бекенд або модель.
    # Параметр `modelName` може бути іменем бекенда (наприклад 'gemma', 'groqwen')
    # або ключем моделі, який розпізнає конкретний бекенд (наприклад, варіанти Gemma).
    # Повертає True при успіху, False — якщо перемикання неможливе.
    def switchModel(self, modelName: str) -> bool:
        target = str(modelName).lower()

        # Спочатку шукаємо бекенд за його канонічною назвою
        for backend in self.backends:
            name = getattr(backend, "name", "")
            if name.lower() != target:
                continue

            # Якщо бекенд не позначений як доступний, спробуємо викликати його checkAvailable(), якщо така функція є
            if not getattr(backend, "available", False) and hasattr(backend, "checkAvailable"):
                backend.checkAvailable()

            # Якщо після перевірки бекенд доступний — встановлюємо його як активний
            if getattr(backend, "available", False):
                self.activeBackend = backend
                self.manualOverride = True
                return True

            # Якщо бекенд не доступний, але підтримує перемикання моделі — спробуємо switchModel
            if hasattr(backend, "switchModel") and backend.switchModel(modelName):
                self.activeBackend = backend
                self.manualOverride = True
                return True

        # Якщо не знайдено бекенд за іменем, спробуємо знайти модель у списку доступних моделей кожного бекенду
        for backend in self.backends:
            models = []
            if hasattr(backend, "getAvailableModels"):
                models = [m.lower() for m in backend.getAvailableModels()]
            # Якщо знайдено варіант моделі у бекенді і бекенд може змінити модель — викликаємо switchModel
            if target in models and hasattr(backend, "switchModel"):
                if backend.switchModel(modelName):
                    if not getattr(backend, "available", False) and hasattr(backend, "checkAvailable"):
                        backend.checkAvailable()
                    if getattr(backend, "available", False):
                        self.activeBackend = backend
                        self.manualOverride = True
                        return True

        # Якщо не знайдено модель у списку доступних моделей, спробуємо перевірити getInfo() кожного бекенду
        for backend in self.backends:
            info = {}
            if hasattr(backend, "getInfo"):
                info = backend.getInfo() or {}
            models = [str(m).lower() for m in info.get("models", [])]
            if target in models:
                if hasattr(backend, "switchModel"):
                    backend.switchModel(modelName)
                if not getattr(backend, "available", False) and hasattr(backend, "checkAvailable"):
                    backend.checkAvailable()
                if getattr(backend, "available", False):
                    self.activeBackend = backend
                    self.manualOverride = True
                    return True

        return False

# Глобальний екземпляр менеджера провайдерів
defaultProvider = None

# Отримання або створення глобального провайдера
def getProvider() -> AIProviderManager:
    global defaultProvider
    if defaultProvider is None:
        defaultProvider = AIProviderManager()
    return defaultProvider

# Псевдонім для зворотної сумісності
get_provider = getProvider
