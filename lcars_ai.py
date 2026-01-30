# lcars_ai.py
import os
import requests
import json
import random

class AIProvider:
    def ask(self, prompt: str) -> str:
        raise NotImplementedError

class HuggingFaceProvider(AIProvider):
    """Використовує безкоштовний Inference API від Hugging Face"""
    def __init__(self, model="mistralai/Mistral-7B-Instruct-v0.2"):
        self.model = model
        # Безкоштовний API ключ (публічний або пустий для обмежених запитів)
        self.api_url = f"https://api-inference.huggingface.co/models/{model}"
        # Read token from environment if present; otherwise run without key
        hf_token = os.environ.get("HUGGINGFACE_API_TOKEN", "")
        if hf_token:
            self.headers = {"Authorization": f"Bearer {hf_token}"}
        else:
            self.headers = {}

    def ask(self, prompt: str) -> str:
        try:
            payload = {
                "inputs": f"<s>[INST] {prompt} [/INST]",
                "parameters": {"max_new_tokens": 250, "return_full_text": False}
            }
            # Спробуємо зробити запит без ключа або з пустим ключем
            # Багато моделей на HF дозволяють базові запити до певного ліміту
            response = requests.post(self.api_url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', '').strip()
                return str(result)
            return f"HF Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"HF Provider Error: {str(e)}"

class MockComputerProvider(AIProvider):
    """Автентичний комп'ютер LCARS для роботи офлайн"""
    def __init__(self):
        self.responses = [
            "WORKING. DATA PROCESSING IN PROGRESS.",
            "COMMAND RECOGNIZED. ACCESSING SUB-PROCESSORS.",
            "SPECIFY PARAMETERS FOR SECTOR DATABASE SEARCH.",
            "INFORMATION RESTRICTED. SECURITY CLEARANCE LEVEL 4 REQUIRED.",
            "SYSTEMS OPERATING WITHIN NORMAL PARAMETERS.",
            "WAITING INPUT. COMPUTER STANDBY.",
            "UNABLE TO COMPLY. LOGIC LOOP DETECTED.",
            "RE-ROUTING POWER TO SENSORS. SCANNING..."
        ]

    def ask(self, prompt: str) -> str:
        # Для певних ключових слів даємо специфічні відповіді
        lower_prompt = prompt.lower()
        if "energy" in lower_prompt or "power" in lower_prompt:
            return "POWER LEVELS NOMINAL. ANTIMATTER CONTAINMENT STABLE."
        if "sector" in lower_prompt or "map" in lower_prompt:
            return "CHARTING NEAREST SECTORS. NO ANOMALIES DETECTED."
        if "status" in lower_prompt:
            return "ALL SYSTEMS FUNCTIONAL. LCARS CORE OPERATING AT 98.4% EFFICIENCY."
        
        return f"{random.choice(self.responses)}"

def ask_openai(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """
    Залишаємо функцію для сумісності з іншими модулями, 
    але перенаправляємо її на безкоштовний провайдер.
    """
    # Спробуємо Hugging Face (Option 2)
    # Якщо HF видасть помилку, перейдемо на Mock
    provider = HuggingFaceProvider()
    response = provider.ask(prompt)
    
    if "Error" in response or not response:
        provider = MockComputerProvider()
        return provider.ask(prompt)
        
    return response

if __name__ == "__main__":
    print(ask_openai("Status report of the Enterprise"))
