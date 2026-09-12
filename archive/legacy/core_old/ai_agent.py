"""
LCARS AI Agent - Інтеграція вільного ШІ в LCARS систему
"""
import logging
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal

# Logger for this module
logger = logging.getLogger(__name__)

# Prefer using the core provider module; fallback to local mock if unavailable
try:
    from lcars.core.provider import ask_openai
except ImportError:
    logger.exception("Failed to import ask_openai from core.ai_provider; using mock fallback")
    def ask_openai(prompt: str, model: str | None = None) -> str:
        return "(AI provider unavailable)"


class LCARSAgent(QThread):
    """AI агент для LCARS системи (Free Edition)"""
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.system_prompt = """Ти - LCARS AI асистент, допомогаєш користувачеві з LCARS системою. 
Відповідай українською мовою, будь лаконічним. 
Якщо кажеш про техніку, використовуй термінологію Star Trek."""
    
    def ask_agent(self, prompt: str, callback=None):
        """Надсилає запит до AI агента.

        If `callback` is provided it will be called with the response string when
        the background thread finishes. The callback will be disconnected after
        being invoked once to avoid multiple invocations.
        """
        self.prompt = prompt
        if callback:
            # wrapper to ensure the slot is disconnected after first call
            def _once(resp):
                try:
                    callback(resp)
                finally:
                    # Disconnect the one-shot slot; allow errors to propagate
                    self.response_ready.disconnect(_once)
            self.response_ready.connect(_once)
        self.start()
    
    def run(self):
        """Виконує запит через єдиний провайдер lcars_ai"""
        # Використовуємо ask_openai, який вже налаштований на HF/Mock
        try:
            answer = ask_openai(f"{self.system_prompt}\n\nUser: {self.prompt}")
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            # Log and notify consumers; avoid silently swallowing errors
            logger.exception("AI provider error in LCARSAgent.run")
            self.error_occurred.emit(str(e))
            return
        self.response_ready.emit(answer)
    
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

_GLOBAL_AI_AGENT: Optional[LCARSAgent] = None

def get_global_ai_agent() -> LCARSAgent:
    """Lazily create and return a global `LCARSAgent` instance.

    Avoid creating QThread instances at import time so importing this
    module is safe in headless scripts and tests.
    """
    global _GLOBAL_AI_AGENT
    if _GLOBAL_AI_AGENT is None:
        _GLOBAL_AI_AGENT = LCARSAgent()
    return _GLOBAL_AI_AGENT

def ask_lcars_ai(prompt: str) -> str:
    """Blocking convenience wrapper that returns the AI response synchronously.

    Use this in scripts or tests where blocking behavior is acceptable. For UI
    usage, prefer `ai_agent.ask_agent()` which runs in a background thread and
    emits `response_ready` when finished.
    """
    return ask_openai(prompt)


import threading

def ask_lcars_ai_async(prompt: str):
    """Enqueue an async request via the global `ai_agent` (emits signals)."""
    agent = get_global_ai_agent()
    return agent.ask_agent(prompt)


def ask_lcars_ai_background(prompt: str, callback=None):
    """Run `ask_openai` in a background Python thread and call `callback(resp)`.

    This is a small compatibility helper for non-Qt contexts or for callers
    that prefer a simple Python callback rather than PyQt signals.
    """
    def _worker():
        resp = ask_openai(prompt)
        if callback:
            callback(resp)
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    return t


def get_component_help(component_name: str) -> str:
    """Blocking helper that returns component help immediately."""
    prompt = f"Розкажи про компонент '{component_name}' в LCARS системі."
    return ask_lcars_ai(prompt)


def get_design_advice(description: str) -> str:
    prompt = f"Дай поради щодо дизайну LCARS інтерфейсу: {description}."
    return ask_lcars_ai(prompt)


def get_script_help(task: str) -> str:
    prompt = f"Напиши приклад скрипта для LCARS елемента: {task}."
    return ask_lcars_ai(prompt)
