# LCARS COPILOT
# Агентний шар для бортового комп'ютера.
#
# Призначення:
# - дати CLI реальний агентний контур;
# - використовувати provider, якщо він доступний;
# - інакше повертати локальну розумну відповідь від BoardComputer;
# - зберегти сумісний публічний API.
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from lcars.service.provider import getProvider


# Отримання екземпляра AI-провайдера
def getProviderInstance():
    return getProvider()


# Пам'ять агента для зберігання сесійних повідомлень
@dataclass
class AgentMemory:
    SessionId: str
    Messages: List[Dict[str, str]] = field(default_factory=list)


# Головний клас Copilot-агента для бортового комп'ютера
class Copilot:
    singletonInstance: Optional["Copilot"] = None

    def __new__(cls, *Args, **Kwargs) -> "Copilot":
        if cls.singletonInstance is None:
            cls.singletonInstance = super().__new__(cls)
        return cls.singletonInstance

    def __init__(self, projectRoot: str = None, boardComputer: Any = None):
        if getattr(self, "initialized", False):
            return
        self.projectRoot = Path(projectRoot) if projectRoot else Path(__file__).resolve().parents[2]
        self.boardComputer = boardComputer
        self.provider = None
        self.initialized = False
        self.busy = False
        self.progressCallback: Optional[Callable[[str], None]] = None
        self.memory = AgentMemory(SessionId=f"LCARS-AGENT-{id(self):x}")

    # Встановлення callback-функції для звітування про прогрес
    def setProgressCallback(self, callback: Callable[[str], None]):
        self.progressCallback = callback

    # Звітування про прогрес через callback
    def reportProgress(self, message: str):
        if self.progressCallback is not None:
            self.progressCallback(self.sanitizeOutput(message))

    # Очищення тексту від некодованих символів
    def sanitizeOutput(self, text: Any) -> str:
        return str(text).encode("utf-8", errors="replace").decode("utf-8")

    # Ініціалізація агента
    def initialize(self) -> bool:
        if self.initialized:
            return True
        self.initialized = True
        return True

    # Отримання локальної відповіді від BoardComputer
    def getLocalAnswer(self, prompt: str) -> str:
        if self.boardComputer is not None and hasattr(self.boardComputer, "LocalIntelligence"):
            return self.boardComputer.LocalIntelligence(prompt)
        return "BOARD INTELLIGENCE: REQUEST RECEIVED."

    # Отримання відповіді від зовнішнього AI-провайдера з урахуванням ролі
    def getProviderAnswer(self, prompt: str, role: str) -> str:
        if self.provider is None:
            return self.getLocalAnswer(prompt)
        systemPrompt = (
            "You are LCARS Copilot, the onboard intelligence of the LCARS Board Computer. "
            "Be concise, technical, and useful. "
            "Use the user's language. "
            "Do not act like a generic chatbot."
        )
        if role == "code":
            systemPrompt += " Focus on code review and precise fixes."
        elif role == "system":
            systemPrompt += " Focus on diagnostics and operational status."
        elif role == "science":
            systemPrompt += " Focus on analysis and structured reasoning."
        elif role == "commander":
            systemPrompt += " Focus on direct onboard computer behavior."
        if hasattr(self.provider, "generate"):
            return self.provider.generate(prompt, systemPrompt)
        if hasattr(self.provider, "ask"):
            return self.provider.ask(prompt)
        return self.getLocalAnswer(prompt)

    # Активація зовнішнього AI-провайдера
    def enableExternalAI(self) -> bool:
        if self.provider is None:
            self.provider = getProviderInstance()
            if self.provider is not None and hasattr(self.provider, "initialize"):
                self.provider.initialize()
        return self.provider is not None

    # Виконання запиту агента з автоматичним визначенням ролі
    def run(self, userRequest: str, role: str = "auto") -> str:
        if self.busy:
            return self.sanitizeOutput("\u25e7 AGENT BUSY")
        if not self.initialized:
            self.initialize()
        self.busy = True
        prompt = str(userRequest or "").strip()
        if not prompt:
            self.busy = False
            return self.sanitizeOutput("\u25e7 AGENT: EMPTY REQUEST")
        # Автоматичне визначення ролі за ключовими словами
        if role == "auto":
            lower = prompt.lower()
            if any(token in lower for token in ("status", "diagnostic", "alert", "system")):
                role = "system"
            elif any(token in lower for token in ("code", "fix", "bug", "refactor", "file", "patch")):
                role = "code"
            elif any(token in lower for token in ("science", "analy", "quantum", "data")):
                role = "science"
            else:
                role = "commander"
        if self.provider is not None:
            answer = self.getProviderAnswer(prompt, role)
        else:
            answer = self.getLocalAnswer(prompt)
        self.memory.Messages.append({"role": "user", "content": prompt})
        self.memory.Messages.append({"role": "assistant", "content": str(answer)})
        self.busy = False
        return self.sanitizeOutput(answer)

    # Отримання інформації про поточний проект
    def getProjectInfo(self) -> str:
        return "PROJECT: LCARS FRAMEWORK\nROOT: " + str(self.projectRoot)


# Отримання екземпляра Copilot-агента
def getAgent(projectRoot: str = None) -> Copilot:
    return Copilot(projectRoot)


# Ініціалізація агента та повернення статусу
def initializeAgent(projectRoot: str = None) -> bool:
    agent = getAgent(projectRoot)
    return agent.initialize()


LCARSAgent = Copilot
getLCARS = getAgent
CopilotAgent = Copilot
