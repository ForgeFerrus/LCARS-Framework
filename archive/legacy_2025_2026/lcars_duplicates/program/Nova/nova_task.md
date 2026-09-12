# ЗАВДАННЯ ДЛЯ GEMMA: ЗБІРКА ПРОГРАМИ NOVA

## Мета
Створити повноцінну програму Nova IDE — інтегроване три-стороннє середовище розробки (код + графіка + AI).

## Структура програми Nova

### Файл: `lcars/program/nova.py`

### Компоненти:

1. **CodeEditor** — редактор коду
   - Поле для введення Python коду
   - Нумерація рядків
   - Підсвітка синтаксису (базова)
   - Методи: `loadFile()`, `saveFile()`, `getCode()`, `setCode()`

2. **LivePreview** — графічне відображення
   - Canvas для matplotlib графіків
   - Оновлення в реальному часі
   - Методи: `plot()`, `clear()`, `update()`

3. **CopilotPanel** — інтеграція з AI
   - Чат-інтерфейс з AI копілотом
   - Використання `lcars.service.provider.getProvider()`
   - Методи: `ask()`, `getResponse()`, `clearHistory()`

4. **NovaIDE (головний клас)**
   - Ініціалізація всіх компонентів
   - Інтеграція з LCARS типами (Directive, Signal)
   - Методи: `run()`, `setup()`, `shutdown()`

### Вимоги до коду:

- **Без try/except** — тільки явні перевірки `if`
- **camelCase** для всіх імен
- **Динамічні імпорти** через `importlib` для опціональних бібліотек
- **Інтеграція з LCARS**: використовувати `lcars.base.type.LCARS`, `Directive`
- **AI інтеграція**: `from lcars.service.provider import getProvider`

### Приклад структури:

```python
class CodeEditor:
    def __init__(self):
        self.content = ""
        self.filePath = None
    
    def loadFile(self, path: str) -> bool:
        if not path:
            return False
        # ...
        return True
    
    def saveFile(self) -> bool:
        if not self.filePath:
            return False
        # ...
        return True

class LivePreview:
    def __init__(self):
        self.canvas = None
        self.figure = None
    
    def plot(self, data):
        if data is None:
            return False
        # ...
        return True

class CopilotPanel:
    def __init__(self):
        self.provider = None
        self.history = []
    
    def connectProvider(self):
        provider = getProvider()
        if provider is None:
            return False
        self.provider = provider
        return True
    
    def ask(self, question: str) -> str:
        if not self.provider:
            return "[Copilot not connected]"
        # ...
        return response

class NovaIDE:
    def __init__(self):
        self.editor = CodeEditor()
        self.preview = LivePreview()
        self.copilot = CopilotPanel()
        self.running = False
    
    def setup(self) -> bool:
        # Ініціалізація всіх компонентів
        return True
    
    def run(self):
        self.running = True
        # Головний цикл
    
    def shutdown(self):
        self.running = False
```

### Результат:

Заповнити `lcars/program/nova.py` повноцінною реалізацією всіх класів згідно цього завдання.
