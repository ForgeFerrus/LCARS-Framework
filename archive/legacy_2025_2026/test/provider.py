from lcars.service.provider import AIProviderManager


# Перевіряємо, чи провайдер збирає саме ті бекенди, які потрібні системі.
def test_provider_backends() -> None:
    manager = AIProviderManager()
    backendNames = [backend.name for backend in manager.backends]

    assert backendNames == ["nova", "gemma", "groqwen", "mistral"]


# Перевіряємо, чи провайдер віддає основний робочий API без зайвих деталей.
def test_provider_surface() -> None:
    manager = AIProviderManager()

    assert hasattr(manager, "chat")
    assert hasattr(manager, "ask")
    assert hasattr(manager, "getStatus")
    assert hasattr(manager, "generateWithModel")
    assert hasattr(manager, "listAvailableModels")


# Перевіряємо, чи провайдер може вибрати перший доступний бекенд і відповісти через нього.
def test_provider_selects_working_backend() -> None:
    class FakeBackend:
        def __init__(self, name: str, ready: bool, answer: str):
            self.name = name
            self.available = False
            self.ready = ready
            self.answer = answer

        def checkAvailable(self) -> bool:
            self.available = self.ready
            return self.available

        def generate(self, prompt: str, systemPrompt: str = "", context: str = "") -> str:
            return self.answer

        def chat(self, messages, tools=None):
            return {"role": "assistant", "content": self.answer}

        def getAvailableModels(self):
            return [self.name]

        def getInfo(self):
            return {"name": self.name, "available": self.available, "models": [self.name]}

    manager = AIProviderManager()
    manager.backendList = [
        FakeBackend("dead", False, "NOPE"),
        FakeBackend("nova", True, "READY"),
    ]
    manager.initialized = False
    manager.activeBackend = None

    answer = manager.ask("hello")

    assert answer == "READY"
    assert manager.activeBackend is not None
    assert manager.activeBackend.name == "nova"


# Перевіряємо, чи статус провайдера повертає очікувані поля.
def test_provider_status() -> None:
    manager = AIProviderManager()
    status = manager.getStatus()

    assert isinstance(status, dict)
    assert "active" in status
    assert "initialized" in status
    assert "is_ai" in status
    assert "backends" in status
    assert isinstance(status["backends"], list)
    assert len(status["backends"]) == 4
