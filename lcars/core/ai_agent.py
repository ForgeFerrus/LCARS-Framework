"""
LCARS AI Agent - Інтеграція вільного ШІ в LCARS систему
"""
import os
from PyQt6.QtCore import QThread, pyqtSignal
from lcars_ai import ask_openai  # Використовуємо наш новий провайдер

class LCARSAIAgent(QThread):
    """AI агент для LCARS системи (Free Edition)"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.system_prompt = """Ти - LCARS AI асистент, допомогаєш користувачеві з LCARS системою. 
Відповідай українською мовою, будь лаконічним. 
Якщо кажеш про техніку, використовуй термінологію Star Trek."""
    
    def ask_agent(self, prompt: str):
        """Надсилає запит до AI агента"""
        self.prompt = prompt
        self.start()
    
    def run(self):
        """Виконує запит через єдиний провайдер lcars_ai"""
        try:
            # Використовуємо ask_openai, який вже налаштований на HF/Mock
            answer = ask_openai(f"{self.system_prompt}\n\nUser: {self.prompt}")
            self.response_ready.emit(answer)
            
        except Exception as e:
            self.error_occurred.emit(f"Помилка AI: {str(e)}")
    
    def get_component_help(self, component_name: str):
        """Отримує допомогу по конкретному компоненту"""
        prompt = f"Розкажи про компонент '{component_name}' в LCARS системі."
        self.ask_agent(prompt)
    
    def get_design_advice(self, description: str):
        """Отримує поради щодо дизайну"""
        prompt = f"Дай поради щодо дизайну LCARS інтерфейсу: {description}."
        self.ask_agent(prompt)
    
    def get_script_help(self, task: str):
        """Отримує допомогу зі скриптами"""
        prompt = f"Напиши приклад скрипта для LCARS елемента: {task}."
        self.ask_agent(prompt)

# Глобальний екземпляр AI агента
ai_agent = LCARSAIAgent()

def ask_lcars_ai(prompt: str) -> str:
    """Проста функція для запиту до LCARS AI"""
    return ai_agent.ask_agent(prompt)

def get_component_help(component_name: str) -> str:
    """Отримати допомогу по компоненту"""
    return ai_agent.get_component_help(component_name)

def get_design_advice(description: str) -> str:
    """Отримати поради щодо дизайну"""
    return ai_agent.get_design_advice(description)

def get_script_help(task: str) -> str:
    """Отримати допомогу зі скриптами"""
    return ai_agent.get_script_help(task)
