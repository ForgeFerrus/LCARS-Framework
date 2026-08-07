import re

# Завантаження коду провайдера з файлу
with open('c:/Users/Forge/MyProject/LCARS-Framework/lcars/service/provider.py', 'r', encoding='utf-8') as f:
    provider_code = f.read()

# Завантаження відсутніх класів з файлу
with open('c:/Users/Forge/MyProject/LCARS-Framework/lcars/service/missing_classes.py', 'r', encoding='utf-8') as f:
    missing_classes = f.read()

# Єдиний клас Mistral для HuggingFace API
mistral_code = """
# ──────────────────────────────────────────────────────
#  MISTRAL (via HuggingFace API or direct)
# ──────────────────────────────────────────────────────
# Клас Mistral для роботи з HuggingFace API
class Mistral(AIModel):
    name = "mistral"
    
    # Ініціалізація моделі Mistral
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = model
        self.apiUrl = f"https://api-inference.huggingface.co/models/{model}"
        self.token = LCARS.environ.get("HUGGING FACE API TOKEN", LCARS.environ.get("MISTRAL API KEY", ""))
        self.available = False

    # Перевірка доступності моделі
    def checkAvailable(self) -> bool:
        if not self.token or requests is None:
            self.available = False
            return False
        self.available = True
        return self.available

    # Генерація відповіді від моделі
    def generate(self, prompt: str, systemPrompt: str = "", context: str = "") -> str:
        # Формування повного промпту залежно від наявності контексту
        fullPrompt = (f"[INST] <<SYS>>\\n{systemPrompt}\\n<</SYS>>\\n\\nSystem data:\\n{context}\\n\\n{ prompt} [/INST]" if context 
                       else f"[INST] <<SYS>>\\n{systemPrompt}\\n<</SYS>>\\n\\n{prompt} [/INST]")
        
        # Підготовка даних для запиту
        payload = {
            "inputs": fullPrompt,
            "parameters": {"max_new_tokens": 800, "temperature": 0.3, "top_p": 0.9, "return_full_text": False},
        }
        if requests is None:
            return "◤ MISTRAL: requests library not available"

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        # Виконання запиту до API
        resp = requests.post(self.apiUrl, json=payload, headers=headers, timeout=30)
        result = resp.json()
        # Обробка результату залежно від формату відповіді
        if isinstance(result, list) and result:
            text = result[0].get("generated_text", "").strip()
            return text if text else "◤ "
        if isinstance(result, dict) and "error" in result:
            return f"◤ MISTRAL ERROR: {result.get('error')}"
        return str(result)

    # Отримання інформації про модель
    def getInfo(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "available": self.available,
            "hasToken": bool(self.token),
            "models": ["mistralai/Mistral-7B-Instruct-v0.2", "codestral-latest"]
        }
"""

# Заміна Mistral та HuggingFace у коді провайдера
provider_code = re.sub(
    r'# ──────────────────────────────────────────────────────\s*#  MISTRAL AI BACKEND.*?#  GEMMA 4 BACKEND',
    mistral_code + "\n#  GEMMA 4 BACKEND",
    provider_code,
    flags=re.DOTALL
)

# Вставка відсутніх класів перед AIProviderManager
provider_code = provider_code.replace(
    '# Очищено: Видалено Cirq, QVAC, TensorFlow, Nova як непотрібні для мовної моделі.',
    missing_classes
)

# Оновлення списку бекендів в AIProviderManager
provider_code = re.sub(
    r'self\.backends = \[.*?\]',
    '''self.backends = [
                Mistral(model=mistralModel),
                GROQwen(model=groqModel),
                GemmaSpark(model=gemmaModel),
                CirQwen(),
                TensorFlow(),
                QVAC(),
                Fallback()
            ]
            if LCARS.environ.get("ENABLE NOVA", "0").lower() in ("1", "true"):
                self.backends.insert(-1, Nova())''',
    provider_code,
    flags=re.DOTALL
)

# Видалення hfModel з коду
provider_code = provider_code.replace('hfModel = LCARS_ENV.get("HUGGINGFACE_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")', '')
provider_code = provider_code.replace('HuggingFace(model=hfModel),', '')

# Запис оновленого коду провайдера у файл
with open('c:/Users/Forge/MyProject/LCARS-Framework/lcars/service/provider.py', 'w', encoding='utf-8') as f:
    f.write(provider_code)
